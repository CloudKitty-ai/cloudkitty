#!/usr/bin/env python3
"""Guard for critic_probe.py (plain asserts, no pytest).

    test_critic_probe.py

Covers the pure pieces: rand_legal never picks an illegal head and
covers all legal ones; spearman on known orderings (perfect, inverted,
ties); verdict's three bars each able to fail alone (non-finite,
out-of-band, low rank correlation).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import critic_probe as cp  # noqa: E402

# --- rand_legal ------------------------------------------------------------
rng = np.random.default_rng(7)
mask = np.zeros(55, bool)
mask[[0, 5, 38]] = True          # legal activities
mask[39 + np.array([0, 4])] = True  # legal messages (Silent + one)
acts, msgs = set(), set()
for _ in range(200):
    a, m = cp.rand_legal(mask, rng)
    assert mask[a] and mask[cp.N_ACT + m], "rand_legal: an illegal head"
    acts.add(a)
    msgs.add(m)
assert acts == {0, 5, 38} and msgs == {0, 4}, \
    f"rand_legal covers every legal head, got {acts} {msgs}"

# --- spearman --------------------------------------------------------------
assert cp.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0, "spearman: perfect"
assert cp.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0, "spearman: inverted"
assert abs(cp.spearman([1, 2, 3, 4, 5], [1, 3, 2, 5, 4]) - 0.8) < 1e-12, \
    "spearman: known 0.8 case"
assert cp.spearman([1, 1, 2, 2], [1, 1, 2, 2]) == 1.0, "spearman: ties"

# --- verdict ---------------------------------------------------------------
t = np.linspace(300, 500, 100)
good = t + np.random.default_rng(0).normal(0, 5, 100)
v = cp.verdict(good, t, 423.0)
assert v["verdict"] == "PASS" and v["spearman"] > 0.9, f"verdict: clean pass, got {v}"
v = cp.verdict(np.append(good[:-1], np.nan), t, 423.0)
assert v["verdict"] == "FAIL" and not v["finite"], "verdict: NaN must fail"
v = cp.verdict(np.append(good[:-1], 900.0), t, 423.0)
assert v["verdict"] == "FAIL" and not v["in_band"], \
    "verdict: out-of-band (900 > 2x423) must fail"
v = cp.verdict(good[::-1].copy(), t, 423.0)
assert v["verdict"] == "FAIL" and v["spearman"] < 0, \
    "verdict: inverted ranking must fail"
flat = np.full(100, 423.0)
v = cp.verdict(flat, t, 423.0)
assert v["verdict"] == "FAIL", "verdict: a constant predictor must fail the rho bar"

print("test_critic_probe: PASS")
