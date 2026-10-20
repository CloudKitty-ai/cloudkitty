#!/usr/bin/env python3
"""Per-kind realized-ordering derivation + gate re-score (MITIGATION
§Round 4 amendment (4), the declared benign-branch consequence): for
every need kind, the realized per-pair edge distribution on the
held-out round-4 random worlds (both midpoints in the censored
window), a p99 sign test each way, and the DERIVED expected direction:
LOWER / HIGHER / NONE (descriptive only). The contrast gate re-scores
from its own recorded per-kind counts under the derived directions —
beside the original, never overwriting.

    kind_edges_read_g2.py [--out ../artifacts/kind-edges.json]
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

from contrast_gate_g2 import (MIN_PAIRS, cp_lower, log_binom_sf,  # noqa: E402
                              select_pairs)
from contrast_pairs_g2 import KINDS  # noqa: E402
from critic_probe_g2 import collect  # noqa: E402
from play_edge_read_g2 import censored_targets  # noqa: E402

TICKS, WORLDS, MIN_FUTURE, SEED_BASE = 6000, 10, 3500, 870040


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ARC / "artifacts/kind-edges.json")
    args = ap.parse_args()

    rollouts = collect(TICKS, WORLDS, SEED_BASE, 1.0, None)
    keep = TICKS - MIN_FUTURE + 1
    edges = {k: [] for k in KINDS}
    for r in rollouts:
        y = censored_targets(r.reward)
        for kind, fa, ua in select_pairs(r.state):
            if fa < keep and ua < keep:
                edges[kind].append(float(y[fa] - y[ua]))

    derived = {}
    for kind in KINDS:
        e = np.asarray(edges[kind])
        n = len(e)
        lower = int((e < 0).sum())
        if n == 0:
            derived[kind] = {"n": 0, "direction": "NONE"}
            continue
        p_low = 1.0 - math.exp(log_binom_sf(lower - 1, n, 0.5))
        p_high = math.exp(log_binom_sf(lower, n, 0.5))
        direction = ("LOWER" if p_low < 0.01
                     else "HIGHER" if p_high < 0.01 else "NONE")
        derived[kind] = {"n": n, "flagged_lower": lower,
                         "frac_lower": lower / n,
                         "p_lower": p_low, "p_higher": p_high,
                         "median_edge": float(np.median(e)),
                         "direction": direction}
        print(f"  {kind:7s} n {n:4d} frac_lower "
              f"{lower / n:.3f} direction {direction}", flush=True)

    # gate re-score from the recorded per-kind counts
    g = json.loads((ARC / "artifacts/contrast-gate.json").read_text())
    inc_correct, inc_total, included = 0, 0, []
    bad = []
    for kind in KINDS:
        row = g["per_kind"][kind]
        if row["pairs"] < MIN_PAIRS or derived[kind]["direction"] == "NONE":
            continue
        included.append(kind)
        n, x = row["pairs"], row["correct"]
        if derived[kind]["direction"] == "HIGHER":
            x = n - x  # the critic is correct when it values flagged HIGHER
        inc_correct += x
        inc_total += n
        if math.exp(log_binom_sf(x, n, 0.5)) < 0.01:
            bad.append(kind)
    lower_bound = cp_lower(inc_correct, inc_total) if inc_total else 0.0
    rescore = {"included_kinds": included,
               "pooled_pairs": inc_total, "pooled_correct": inc_correct,
               "pooled_fraction": inc_correct / inc_total if inc_total else None,
               "cp99_lower": lower_bound, "kinds_below": bad,
               "pass": bool(inc_total and lower_bound > 0.5 and not bad)}
    out = {"seed_base": SEED_BASE, "derived_directions": derived,
           "gate_rescored": rescore,
           "source_gate": "artifacts/contrast-gate.json"}
    print(json.dumps(rescore, indent=1))
    args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
