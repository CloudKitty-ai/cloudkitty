#!/usr/bin/env python3
"""Guard for contrast_gate_g2.py (plain asserts, no pytest): the
Clopper-Pearson lower bound on knowns, the below-chance kind test, and
the correctness direction (flagged member must be valued LOWER).
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import contrast_gate_g2 as cg  # noqa: E402

# --- Clopper-Pearson lower bound --------------------------------------------
# x = n (all correct): lower bound is (1-conf)^(1/n) = 0.01^(1/10) ~ 0.631
assert abs(cg.cp_lower(10, 10) - 0.01 ** 0.1) < 1e-6, "CP all-correct known"
# chance-level counts must NOT clear 0.5
assert cg.cp_lower(5, 10) < 0.5, "CP at chance must sit below 0.5"
assert cg.cp_lower(0, 10) == 0.0, "CP at zero successes is 0"
# a strong majority at n=400 clears 0.5 (the gate's working regime)
assert cg.cp_lower(260, 400) > 0.5, "260/400 must clear 0.5 at 99%"
assert cg.cp_lower(220, 400) < 0.5, "220/400 must not clear 0.5 at 99%"
# monotone in x
assert cg.cp_lower(300, 400) > cg.cp_lower(260, 400), "CP monotone in x"

# --- below-chance test -------------------------------------------------------
# P(X <= 130 | n=400, p=.5) is far below 0.01; P(X <= 195) is not
assert math.exp(cg.log_binom_sf(130, 400, 0.5)) < 0.01, "130/400 is below chance"
assert math.exp(cg.log_binom_sf(195, 400, 0.5)) > 0.01, "195/400 is not"

# --- pair selection + direction ---------------------------------------------
# synthetic rollout: one kitty flagged on 'eat' for 5 ticks at t=100,
# clean elsewhere; state col k0 flag offset 20
state = np.zeros((1000, 237), np.float32)
state[100:105, 20] = 1.0
rows = cg.select_pairs(state)
assert len(rows) == 1 and rows[0][0] == "eat", f"one eat pair: {rows}"
kind, fa, ua = rows[0]
assert 100 <= fa < 105, "flagged member inside the run"
assert not (100 <= ua < 105), "unflagged member outside the run"
assert abs(ua - 100) <= cg.NEAR + 5, "unflagged member within the near window"
# direction, through the gate's own scoring path
c, t = cg.score_pairs(rows, {fa: 10.0, ua: 20.0})
assert c["eat"] == 1 and t["eat"] == 1, \
    "flagged valued lower must count correct"
c, t = cg.score_pairs(rows, {fa: 20.0, ua: 10.0})
assert c["eat"] == 0 and t["eat"] == 1, \
    "flagged valued HIGHER must not count correct"

# runs shorter than MIN_RUN never pair
state2 = np.zeros((1000, 237), np.float32)
state2[100:102, 20] = 1.0
assert cg.select_pairs(state2) == [], "a 2-tick run must not pair"

print("test_contrast_gate_g2: PASS")
