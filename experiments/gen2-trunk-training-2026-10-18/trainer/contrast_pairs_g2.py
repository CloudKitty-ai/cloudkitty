#!/usr/bin/env python3
"""Contrast-pair accounting (MITIGATION.md target 3; deviations entry 2).

A PAIR, per need kind: a flagged passage (maximal run of >= 3 ticks
where one kitty's distress flag for that kind is 1) that has an
unflagged window of the same length for the SAME kitty in the SAME
world within +/-500 ticks (flag 0 throughout the window). Pairing
within world+kitty is the point — it gives the flag covariance that
survives world-level return offsets.

Flag columns: kitty block offset 20+j, j in NeedKind::ALL order
(eat, drink, sleep, play, cuddle, bath — needs.rs). Counts stream per
rollout dir; the bar is >= 200 pairs per kind over the counted set.

    contrast_pairs_g2.py <rollout-root>... [--out F]

Each root is globbed for config-*-rollout-* bundles (a root that IS a
bundle counts as itself). Run from trainer/, exp-006 venv.
"""
import argparse
import json
from pathlib import Path

import numpy as np

KINDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
MIN_RUN, NEAR = 3, 500
N_KITTY, KITTY_F, FLAG_OFF = 5, 40, 20


def runs_of_ones(x):
    """(start, length) of each maximal run of 1s in a 0/1 vector."""
    d = np.diff(np.concatenate([[0], x.astype(np.int8), [0]]))
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return list(zip(starts, ends - starts))


def pairs_in_rollout(state):
    """Per-kind pair count for one rollout's state array."""
    out = dict.fromkeys(KINDS, 0)
    t_total = state.shape[0]
    for k in range(N_KITTY):
        flags = np.asarray(state[:, k * KITTY_F + FLAG_OFF:
                                 k * KITTY_F + FLAG_OFF + 6], np.int8)
        assert ((flags == 0) | (flags == 1)).all(), "flag column not 0/1"
        for j, kind in enumerate(KINDS):
            f = flags[:, j]
            # zero-run presence per position, for O(1) window checks:
            # prefix sums of f; window [a, a+L) is unflagged iff sum == 0
            cs = np.concatenate([[0], np.cumsum(f)])
            for start, length in runs_of_ones(f):
                if length < MIN_RUN:
                    continue
                lo = max(0, start - NEAR)
                hi = min(t_total - length, start + length + NEAR)
                a = np.arange(lo, hi + 1)
                if len(a) and (cs[a + length] - cs[a] == 0).any():
                    out[kind] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    totals = dict.fromkeys(KINDS, 0)
    n = 0
    for root in args.roots:
        dirs = ([root] if (root / "state.npy").exists()
                else sorted(root.glob("**/config-*-rollout-*")))
        assert dirs, f"no rollouts under {root}"
        for d in dirs:
            state = np.load(d / "state.npy", mmap_mode="r")
            for kind, c in pairs_in_rollout(state).items():
                totals[kind] += c
            n += 1
    report = {"rollouts": n, "min_run": MIN_RUN, "near": NEAR,
              "pairs": totals,
              "met": {k: v >= 200 for k, v in totals.items()}}
    print(json.dumps(report, indent=1))
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
