#!/usr/bin/env python3
"""Trained-seat below-45 happiness tail, from the committed cert raws.

Pre-sitting read 3 addendum (2026-10-12): the certified gen1-A
battery scorecards already carry `low_share` — the welfare
accumulator's share of ticks below happiness 45 (LOW_HAPPINESS),
per seat per seed — so the trained tail needs no new rollout.
Summarizes both bands of the certified roster beside the SAME-WORLD
all-scripted legs (same config_sha256, same seed0; same harness file,
though the trained-eval leg's tool sha was stamped mid-edit), so the
trained-vs-scripted tail comparison is paired, not cross-corpus.

    trained_tail_read.py [--out OUT.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BATTERY = ROOT / "experiments/fog-gen1-cert/results-raw/battery"
FILES = {
    "eval": {
        "trained": BATTERY / "gen1-A-eval-30x20000.jsonl",
        "scripted": BATTERY / "scripted-eval-30x20000.jsonl",
    },
    "stress": {
        "trained": BATTERY / "gen1-A-stress-30x20000.jsonl",
        "scripted": BATTERY / "scripted-stress-30x20000.jsonl",
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    def leg(path):
        rows = [json.loads(l) for l in open(path) if l.strip()]
        keyed = [r for r in rows if "low_share" in r]
        ticks = {r["ticks"] for r in keyed}
        assert ticks == {20000}, ticks
        ls = np.array([r["low_share"] for r in keyed])
        mh = np.array([r["mean_happiness"] for r in keyed])
        return {
            "file": str(path.relative_to(ROOT)),
            "seeds": int(ls.shape[0]),
            "seats": int(ls.shape[1]),
            "low_ticks_total": int(round(float(ls.sum()) * 20000)),
            "kitty_ticks_total": int(ls.size * 20000),
            "low_share_pooled_pct": round(100 * float(ls.mean()), 5),
            "low_share_per_seat_mean": [float(x) for x in ls.mean(axis=0).round(8)],
            "low_share_worst_cell": float(ls.max()),
            "cells_at_zero": int((ls == 0).sum()),
            "cells_total": int(ls.size),
            "mean_happiness_per_seat": [float(x) for x in mh.mean(axis=0).round(2)],
        }

    out = {}
    pooled = {"trained": 0, "scripted": 0}
    for band, paths in FILES.items():
        out[band] = {k: leg(p) for k, p in paths.items()}
        for k in pooled:
            pooled[k] += out[band][k]["low_ticks_total"]
        t, s = out[band]["trained"], out[band]["scripted"]
        out[band]["trained_vs_scripted_low_tick_ratio"] = (
            round(s["low_ticks_total"] / t["low_ticks_total"], 1)
            if t["low_ticks_total"]
            else None
        )
    out["pooled_low_ticks"] = pooled
    out["pooled_ratio_scripted_over_trained"] = (
        round(pooled["scripted"] / pooled["trained"], 1) if pooled["trained"] else None
    )
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
