#!/usr/bin/env python3
"""Seating-analysis reader, Gen 2 port (DECLARATION.md beside this file).

Per leg: v1's read_leg verbatim (the 11 declared families; one home for
the metric math, ../seating-analysis-2026-09-28/seating_read.py), plus
the Gen 2 additions: play-proposal share (chosen PlayKitty actions,
policy seats only) and the per-cat distress streak. Group holding is a
CERTIFICATION read, not part of this analysis (owner 2026-10-21); it
lives in cert_harness_fog. Speech fields
are nulled for engine-driven seats (their message heads are not
recorded). Then the rotation rollup: per roster, per network x seat,
per network, with the scripted reference beside.

    seating_read_g2.py --raws results-raw/*/streams-*.npz --out read.json [--md]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
sys.path.insert(0, str(EXPTS / "gen2-trunk-training-2026-10-18" / "trainer"))
sys.path.insert(1, str(EXPTS / "attn-oracle-2026-08-15"))
import seating_read as v1  # noqa: E402
from data_g2 import ACTION_NAMES  # noqa: E402

PLAY_IDS = np.array([i for i, n in enumerate(ACTION_NAMES) if n.startswith("PlayKitty")])


def play_share(act):
    """Per-seat share of ticks whose chosen action is a PlayKitty
    proposal; None for engine-driven seats (act == -1 throughout)."""
    out = []
    for k in range(act.shape[1]):
        a = act[:, k]
        out.append(None if (a < 0).all() else float(np.isin(a, PLAY_IDS).mean()))
    return out


def read_leg_g2(z):
    leg, _heats, _all, meta = v1.read_leg(z)
    spoken = meta["speech_recorded"]
    for k, c in enumerate(leg["cats"]):
        if not spoken[k]:
            c["msg_share"], c["speak_rate_by_need_bin"] = None, None
    leg["play_share"] = play_share(z["act"])
    leg["seating"], leg["seats"] = meta["seating"], meta["seats"]
    leg["distress_streak_max"] = distress_streak_max(z["distress"])
    return leg


def distress_streak_max(distress):
    """Per-cat longest per-(cat, need) distress-flag streak, the battery's
    max_distress_age convention, from the 6-flag little-endian bitmask."""
    flags = np.unpackbits(distress[:, :, None].astype(np.uint8), axis=2,
                          bitorder="little")[:, :, :6].astype(bool)
    return [int(max((v1.runs_of(flags[:, k, j]).max() if flags[:, k, j].any() else 0)
                    for j in range(6))) for k in range(flags.shape[1])]


def rollup(legs):
    by = {}
    for l in legs:
        by.setdefault(l["seating"], []).append(l)
    rosters = {}
    for s, ls in sorted(by.items()):
        hap_mean = [np.mean([c["hap"]["mean"] for c in l["cats"]]) for l in ls]
        worst_p5 = [min(c["hap"]["p5"] for c in l["cats"]) for l in ls]
        rosters[s] = {
            "seeds": [l["seed"] for l in ls], "seats": ls[0]["seats"],
            "aborted": [l["seed"] for l in ls if l["aborted_at"]],
            "team_hap": {"mean": float(np.mean(hap_mean)), "sd": float(np.std(hap_mean, ddof=1)) if len(ls) > 1 else None},
            "worst_cat_p5": {"mean": float(np.mean(worst_p5)), "sd": float(np.std(worst_p5, ddof=1)) if len(ls) > 1 else None},
            "gap_mean": float(np.mean([l["welfare"]["gap"]["mean"] for l in ls])),
            "distress_streak_max": max(max(l["distress_streak_max"]) for l in ls),
        }
    cells = {}
    for s, ls in by.items():
        for k, spec in enumerate(ls[0]["seats"]):
            net = spec.split(":")[-1] if spec != "scripted" else "scripted"
            cells[f"{net}@{v1.CATS[k]}"] = {
                "roster": s,
                "hap_mean": float(np.mean([l["cats"][k]["hap"]["mean"] for l in ls])),
                "hap_p5": float(np.mean([l["cats"][k]["hap"]["p5"] for l in ls])),
                "play_share": (None if ls[0]["play_share"][k] is None
                               else float(np.mean([l["play_share"][k] for l in ls]))),
                "contact": float(np.mean([l["cats"][k]["grouped"]["contact"] for l in ls])),
                "home_range": float(np.mean([l["cats"][k]["home_range_tiles"] for l in ls])),
            }
    return rosters, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raws", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    legs = [read_leg_g2(np.load(p)) for p in sorted(a.raws)]
    rosters, cells = rollup(legs)
    Path(a.out).write_text(json.dumps({"legs": legs, "rosters": rosters, "cells": cells}, indent=1))
    print("wrote", a.out)
    if a.md:
        print("\n| roster | seats | team hap (sd) | worst-cat p5 (sd) | gap | worst distress streak | aborted |")
        print("|---|---|---|---|---|---|---|")
        for s, r in rosters.items():
            seats = " ".join(x.split("-")[-1] if x != "scripted" else "scr" for x in r["seats"])
            sd = lambda v: "" if v is None else f" ({v:.2f})"  # noqa: E731
            print(f"| {s} | {seats} | {r['team_hap']['mean']:.3f}{sd(r['team_hap']['sd'])} | "
                  f"{r['worst_cat_p5']['mean']:.2f}{sd(r['worst_cat_p5']['sd'])} | {r['gap_mean']:.2f} | "
                  f"{r['distress_streak_max']} | {r['aborted'] or 'none'} |")


if __name__ == "__main__":
    main()
