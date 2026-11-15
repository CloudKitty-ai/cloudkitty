#!/usr/bin/env python3
"""R-D, search when foodless (DECLARATION.md §6; scores nothing). `diag_abort.world`'s search table, called and not
copied, on every recorded world of three 40×40 legs: this arm's, the no-head arm's final and the continued final's.
Replays of recorded acts: nothing covered decides. Pooled per leg: cat-ticks with no chow in sight or memory and eat
need at 50 or more / 90 or more, the share of them where a move was legal, the share of those where one was proposed;
the longest run without chow in sight or memory (the worst seat of the worst world, and the median over worlds).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_rd.py --out reads/rd.json [--md]     (about 6 minutes, 7 GB a worker)
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
K = HERE.parent / "gen2-trunk-continuation-2026-11-10"
sys.path.insert(0, str(K))
import diag_abort as DA  # noqa: E402

LEGS = {"reanchor-s1": HERE / "results-raw", "p2u-nohead-s1": None, "cont-s1": K / "results-raw"}


def job(a):
    seating, seed = a
    w = DA.world(seating, "legs", LEGS[seating], seed)
    return seating, seed, {"ticks": w["ticks"], "search": w["search"], "longest_foodless_run": w["longest_foodless_run"]}


def read(workers=3):
    jobs = [(s, int(p.stem.split("-")[1])) for s, root in LEGS.items()
            for p in sorted(((root or DA.C.RAW) / "legs" / s / "legs" / f"size{DA.SIZE}" / "acts").glob("acts-*.npz"))]
    per = {s: {} for s in LEGS}
    with ProcessPoolExecutor(workers, max_tasks_per_child=1) as ex:
        for s, seed, w in ex.map(job, jobs):
            per[s][seed] = w
    out = {}
    for s, worlds in per.items():
        row = {"worlds": len(worlds), "short_worlds": {str(k): v["ticks"] for k, v in worlds.items() if v["ticks"] < 20_000}}
        for lab in ("foodless_eat50", "foodless_eat90"):
            n = sum(v["search"][lab]["cat_ticks"] for v in worlds.values())
            legal = sum(v["search"][lab]["cat_ticks"] * (v["search"][lab]["move_legal_share"] or 0) for v in worlds.values())
            prop = sum(v["search"][lab]["cat_ticks"] * (v["search"][lab]["move_legal_share"] or 0) * (v["search"][lab]["move_proposed_when_legal"] or 0) for v in worlds.values())
            row[lab] = {"cat_ticks": n, "move_legal_share": legal / n if n else None, "move_proposed_when_legal": prop / legal if legal else None}
        runs = [max(v["longest_foodless_run"]) for v in worlds.values()]
        row["longest_foodless_run"] = {"max": int(max(runs)), "median_world": float(np.median(runs))}
        out[s] = row
    return out


def md(out):
    f = lambda x: "n/a" if x is None else f"{x:.3f}"      # noqa: E731
    L = ["# R-D: search when foodless (40×40 legs, replays; scores nothing)", "",
         "| leg | worlds | foodless, eat ≥ 50: cat-ticks | move legal | move proposed when legal | foodless, eat ≥ 90: cat-ticks | move legal | proposed when legal | longest foodless run (max / median world) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for s, r in out.items():
        a, b = r["foodless_eat50"], r["foodless_eat90"]
        L.append(f"| {s} | {r['worlds']} | {a['cat_ticks']} | {f(a['move_legal_share'])} | {f(a['move_proposed_when_legal'])} | {b['cat_ticks']} | {f(b['move_legal_share'])} | "
                 f"{f(b['move_proposed_when_legal'])} | {r['longest_foodless_run']['max']} / {r['longest_foodless_run']['median_world']:.0f} |")
    short = {s: r["short_worlds"] for s, r in out.items() if r["short_worlds"]}
    return "\n".join(L + (["", f"Worlds cut short by the armed abort (world: ticks): {short}."] if short else [])) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(md(out))
