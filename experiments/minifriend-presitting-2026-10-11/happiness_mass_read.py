#!/usr/bin/env python3
"""Happiness mass at the ruled semantic edges, scripted density.

Pre-sitting read 3 (owner ask 2026-10-12, the bins discussion): how
much lived mass sits below the ruled happiness edges 45 and 70
(welfare.rs LOW_HAPPINESS / MIN_MEAN_HAPPINESS) at scripted
collection density — the occupancy input to the one-fixed-set
recommendation. Happiness is state-channel ground truth (global-state
v1 block offset 6, scale /100).

    happiness_mass_read.py [--out OUT.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "experiments/fog-gen1-shakeout/results-raw/bc-corpus"
PK = 32


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    rollouts = sorted({p.parent.resolve() for p in CORPUS.rglob("label_msg.npy")})
    hap = []
    for rd in rollouts:
        meta = json.load(open(rd / "meta.json"))
        assert meta["observation_schema"] == 5
        state = np.load(rd / "state.npy")
        for i in range(len(meta["experts"])):
            hap.append(state[:, i * PK + 6])
    h = np.concatenate(hap) * 100.0

    out = {
        "rollouts": len(rollouts),
        "kitty_ticks": int(h.size),
        "mean": round(float(h.mean()), 2),
        "p5": round(float(np.percentile(h, 5)), 1),
        "p50": round(float(np.percentile(h, 50)), 1),
        "p95": round(float(np.percentile(h, 95)), 1),
        "min": round(float(h.min()), 1),
        "pct_below_45": round(100 * float((h < 45).mean()), 4),
        "pct_45_to_70": round(100 * float(((h >= 45) & (h < 70)).mean()), 3),
        "pct_at_least_70": round(100 * float((h >= 70).mean()), 3),
    }
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
