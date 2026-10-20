#!/usr/bin/env python3
"""Guard for critic_probe_g2.py (plain asserts, no pytest; forked from
fog-gen1-shakeout/test_critic_probe.py at the Gen 2 head widths).

    test_critic_probe_g2.py

Covers the pure pieces: rand_legal never picks an illegal head and
covers all legal ones (35 + 16 split); spearman on known orderings
(perfect, inverted, ties); verdict's three bars each able to fail
alone (non-finite, out-of-band, low rank correlation).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import critic_probe_g2 as cp  # noqa: E402

assert cp.N_ACT == 35, cp.N_ACT

# --- rand_legal ------------------------------------------------------------
rng = np.random.default_rng(7)
mask = np.zeros(51, bool)
mask[[0, 5, 34]] = True              # legal activities (Idle = 34)
mask[35 + np.array([0, 4])] = True   # legal messages (Silent + one)
acts, msgs = set(), set()
for _ in range(200):
    a, m = cp.rand_legal(mask, rng)
    assert mask[a] and mask[cp.N_ACT + m], "rand_legal: an illegal head"
    acts.add(a)
    msgs.add(m)
assert acts == {0, 5, 34} and msgs == {0, 4}, \
    f"rand_legal covers every legal head, got {acts} {msgs}"

# --- masked_argmax ---------------------------------------------------------
rng2 = np.random.default_rng(11)
for _ in range(200):
    logits = rng2.normal(0, 3, 51)
    m = rng2.random(51) < 0.3
    m[4] = True          # a legal activity always exists (RestSolo)
    m[35] = True         # Silent always legal
    a, g = cp.masked_argmax(logits, m)
    assert m[a] and m[35 + g], "masked_argmax: illegal head"
    legal_a = np.flatnonzero(m[:35])
    legal_g = np.flatnonzero(m[35:])
    assert logits[a] == logits[legal_a].max(), "masked_argmax: not the max act"
    assert logits[35 + g] == logits[35:][legal_g].max(), \
        "masked_argmax: not the max msg"

# --- spearman --------------------------------------------------------------
assert cp.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0, "spearman: perfect"
assert cp.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0, "spearman: inverted"
assert abs(cp.spearman([1, 2, 3, 4, 5], [1, 3, 2, 5, 4]) - 0.8) < 1e-12, \
    "spearman: known 0.8 case"
assert cp.spearman([1, 1, 2, 2], [1, 1, 2, 2]) == 1.0, "spearman: ties"
assert cp.spearman([1, 2, 3, 4], [1, 10, 100, 1000]) == 1.0, \
    "spearman: rank-based, monotone nonlinear must be exactly 1 (Pearson is not)"

# --- block_null (amended epsilon instrument) --------------------------------
rng3 = np.random.default_rng(3)
keep, nw = 2000, 3
t = np.concatenate([np.cumsum(rng3.normal(0, 1, keep)) for _ in range(nw)])
offsets = np.repeat([50.0, -40.0, 0.0], keep)
# a within-world ranker under ANTI-ALIGNED world offsets (the measured
# defect geometry) must pass: standardization kills the offsets
ranker = t + rng3.normal(0, 0.5, keep * nw) - 3 * offsets
r = cp.block_null(ranker, t, keep, nw, n_perm=200, seed=7)
assert r["pass"], f"within-world ranker with anti-aligned offsets must pass: {r}"
# an offset-only predictor (no within-world signal) must fail
r = cp.block_null(offsets.copy(), t, keep, nw, n_perm=200, seed=7)
assert not r["pass"], f"offset-only predictor must fail: {r}"
# independent noise must fail
r = cp.block_null(rng3.normal(0, 1, keep * nw), t, keep, nw,
                  n_perm=200, seed=7)
assert not r["pass"], f"independent noise must fail the null: {r}"

# --- world_null (round-3 n_eff instrument) -----------------------------------
rng4 = np.random.default_rng(13)
n = 2501
# white-noise target: shifts decorrelate fully, null stays tight, and a
# true ranker's observed rho clears it — the read is INFORMATIVE
wn = rng4.normal(0, 1, n)
ranker = wn + rng4.normal(0, 0.5, n)
r = cp.world_null(ranker, wn, n_perm=200, seed=5)
assert r["informative"] and r["null_p99"] < 0.1, \
    f"white-noise target must give a tight null: {r}"
assert r["observed"] > r["null_p99"], f"true ranker must clear the null: {r}"
assert r["n_eff"] > 500, f"tight null means large n_eff: {r}"
# heavily autocorrelated target (slow random walk): circular shifts keep
# the smoothness, the null is WIDE, and the read must label itself
# UNINFORMATIVE — the round-2 defect geometry (p99 0.412 gated nothing)
walk = np.sin(np.linspace(0, 4 * np.pi, n)) + rng4.normal(0, 0.05, n)
# two slow cycles across the window: some legal shifts re-align the
# phase almost perfectly, so the null's p99 must blow past the ceiling
r = cp.world_null(walk + rng4.normal(0, 0.1 * walk.std(), n), walk,
                  n_perm=200, seed=5)
assert not r["informative"] and r["null_p99"] > cp.NULL_CEILING, \
    f"slow-walk target must give a wide null and label UNINFORMATIVE: {r}"
# n_eff is the declared inversion of the measured p99, exactly
r_known = cp.world_null(ranker, wn, n_perm=200, seed=5)
assert abs(r_known["n_eff"] - (2.33 / r_known["null_p99"]) ** 2) < 1e-9, \
    "n_eff must be (2.33/p99)^2 of this run's own p99"

# --- amended_verdict ---------------------------------------------------------
pw = [{"rho": 0.5, "target_std": 9.0}, {"rho": 0.4, "target_std": 7.0},
      {"rho": 0.31, "target_std": 6.0}]
base = {"finite": True, "in_band": True, "per_world": pw}
assert cp.amended_verdict(base, 1.0)["pass"], "random leg: all >= 0.3 passes"
low = {**base, "per_world": [dict(pw[0]), dict(pw[1]),
                             {"rho": 0.29, "target_std": 6.0}]}
assert not cp.amended_verdict(low, 1.0)["pass"], \
    "random leg: one world at 0.29 must fail"
eps_ok = {**base, "block_null": {"pass": True}}
assert cp.amended_verdict(eps_ok, 0.1)["pass"], "eps leg: null pass passes"
thin = {**base, "per_world": [{"rho": 0.9, "target_std": 9.0},
                              {"rho": 0.9, "target_std": 2.0},
                              {"rho": 0.9, "target_std": 1.0}],
        "block_null": {"pass": True}}
v = cp.amended_verdict(thin, 0.1)
assert not v["pass"] and v["uninformative"], \
    "eps leg: one qualifying world is uninformative, never a pass"

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

print("test_critic_probe_g2: PASS")
