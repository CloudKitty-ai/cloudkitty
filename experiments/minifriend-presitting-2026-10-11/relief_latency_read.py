#!/usr/bin/env python3
"""Relief-latency tail-quantile power at scripted collection density.

Pre-sitting read 2 for the banked relief-latency discriminator
(Professor relay 2026-10-10): at realistic stratum sizes, is a declared
TAIL quantile of relief latency readable per stratum, and at what n
does it discriminate a degradation? Episodes are runs of need >=
threshold per (kitty, need) in the bc-corpus state channel; latency =
run length in ticks (onset to first tick back below); runs still open
at rollout end are censored and reported separately, never pooled.

Power, two reads per stratum (need kind x threshold; 90 = the engine
distress line, 70 = a read-time choice):
- bootstrap relative CI half-width of p90 at the observed n and on a
  subsample curve n in {20, 50, 100, 200, 500};
- power to detect a +25% latency shift at p90 against the null
  bootstrap reference (a 1.25x-scaled resample vs the null's 95th
  percentile, alpha 0.05 one-sided, 1000 trials; the baseline is
  treated as known, so powers are optimistic vs a true two-sample
  read).

    relief_latency_read.py [--out OUT.json]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "experiments/fog-gen1-shakeout/results-raw/bc-corpus"
PK = 32
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
THRESHOLDS = [0.70, 0.90]
SUBSAMPLE_NS = [20, 50, 100, 200, 500]
BOOT = 1000
RNG = np.random.default_rng(20261011)


def runs(mask):
    """(start, length, censored) for each True-run in a 1-D bool array."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    starts = np.nonzero(d == 1)[0]
    ends = np.nonzero(d == -1)[0]
    return [(int(s), int(e - s), bool(e == len(mask))) for s, e in zip(starts, ends)]


def boot_q(lat, q, n=None):
    """Bootstrap distribution of the q-quantile at sample size n."""
    n = n or len(lat)
    idx = RNG.integers(0, len(lat), size=(BOOT, n))
    return np.quantile(lat[idx], q, axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    rollouts = sorted({p.parent.resolve() for p in CORPUS.rglob("label_msg.npy")})
    lats = defaultdict(list)
    censored = defaultdict(int)
    per_kitty_n = defaultdict(lambda: defaultdict(int))
    total_ticks = 0
    for rd in rollouts:
        meta = json.load(open(rd / "meta.json"))
        assert meta["observation_schema"] == 5
        total_ticks += meta["ticks"]
        state = np.load(rd / "state.npy")
        roster = len(meta["experts"])
        for bi in range(roster):
            needs = state[:, bi * PK : bi * PK + 6]
            for ni, need in enumerate(NEEDS):
                for thr in THRESHOLDS:
                    key = (need, thr)
                    for _, length, cens in runs(needs[:, ni] >= thr):
                        if cens:
                            censored[key] += 1
                        else:
                            lats[key].append(length)
                            per_kitty_n[key][bi] += 1

    out = {
        "rollouts": len(rollouts),
        "total_world_ticks": total_ticks,
        "thresholds": THRESHOLDS,
        "bootstrap_draws": BOOT,
        "shift_tested_pct": 25,
        "strata": {},
    }
    for (need, thr), lat in sorted(lats.items()):
        lat = np.array(lat, float)
        n = len(lat)
        entry = {
            "episodes": n,
            "censored": censored[(need, thr)],
            "per_kitty_episodes": dict(sorted(per_kitty_n[(need, thr)].items())),
            "median": float(np.median(lat)),
            "p90": float(np.quantile(lat, 0.90)),
            "p95": float(np.quantile(lat, 0.95)),
        }
        if n >= 10:
            q = boot_q(lat, 0.90)
            p90 = entry["p90"]
            entry["p90_boot_rel_ci_halfwidth_pct"] = round(
                100 * (np.quantile(q, 0.975) - np.quantile(q, 0.025)) / 2 / p90, 1
            )
            curve = {}
            for sn in SUBSAMPLE_NS:
                if sn > n:
                    break
                qs = boot_q(lat, 0.90, sn)
                crit = np.quantile(boot_q(lat, 0.90, sn), 0.95)
                shifted = 1.25 * lat
                idx = RNG.integers(0, n, size=(BOOT, sn))
                qsh = np.quantile(shifted[idx], 0.90, axis=1)
                curve[str(sn)] = {
                    "rel_ci_halfwidth_pct": round(
                        100 * (np.quantile(qs, 0.975) - np.quantile(qs, 0.025)) / 2 / p90, 1
                    ),
                    "power_detect_25pct_shift": round(float((qsh > crit).mean()), 2),
                }
            entry["subsample_curve"] = curve
        out["strata"][f"{need}@{thr}"] = entry
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
