#!/usr/bin/env python3
"""Paired play read (MITIGATION §Round 4 amendment (4), decision
structure declared pre-read): within each held-out play near-pair on
the round-4 random worlds whose BOTH midpoints sit in the censored
window, the per-pair edge = realized censored return at the flagged
midpoint − at the unflagged midpoint. Sign test at p99. Pure data —
no model anywhere in this read.

    play_edge_read_g2.py [--out ../artifacts/play-edge-read.json]
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from contrast_gate_g2 import log_binom_sf, select_pairs  # noqa: E402
from critic_probe_g2 import collect  # noqa: E402

TICKS, WORLDS, MIN_FUTURE, GAMMA = 6000, 10, 3500, 0.998
SEED_BASE = 870040


def censored_targets(rew):
    rew = np.asarray(rew, np.float64).ravel()
    g = np.empty(rew.size)
    acc = 0.0
    for t in range(rew.size - 1, -1, -1):
        acc = rew[t] + GAMMA * acc
        g[t] = acc
    return g[:rew.size - MIN_FUTURE + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/play-edge-read.json")
    args = ap.parse_args()

    rollouts = collect(TICKS, WORLDS, SEED_BASE, 1.0, None)
    keep = TICKS - MIN_FUTURE + 1
    edges = []
    total_play_pairs, in_window = 0, 0
    for r in rollouts:
        y = censored_targets(r.reward)
        for kind, fa, ua in select_pairs(r.state):
            if kind != "play":
                continue
            total_play_pairs += 1
            if fa < keep and ua < keep:
                in_window += 1
                edges.append(float(y[fa] - y[ua]))
    edges = np.asarray(edges)
    n = len(edges)
    lower = int((edges < 0).sum())
    # significantly lower = P(X >= lower | p=.5) < 0.01, X = #lower
    p_lower = 1.0 - math.exp(log_binom_sf(lower - 1, n, 0.5)) if n else 1.0
    branch = ("binding_defect_candidate" if p_lower < 0.01
              else "critic_right_gate_direction_defect")
    out = {"seed_base": SEED_BASE, "worlds": WORLDS, "ticks": TICKS,
           "min_future": MIN_FUTURE,
           "play_pairs_total": total_play_pairs,
           "pairs_in_window": in_window, "n_edges": n,
           "flagged_lower": lower,
           "frac_lower": lower / n if n else None,
           "p_significantly_lower": p_lower,
           "median_edge": float(np.median(edges)) if n else None,
           "mean_edge": float(edges.mean()) if n else None,
           "branch": branch}
    print(json.dumps(out, indent=1))
    args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
