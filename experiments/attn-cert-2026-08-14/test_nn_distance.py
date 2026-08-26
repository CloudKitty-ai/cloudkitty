#!/usr/bin/env python3
"""Guard for nn_distance.py. Synthetic positions with hand-computed answers;
the classic self-inclusion bug is demonstrated red in the same run."""
from nn_distance import stats

# (0,0)-(3,4): cheb 4, euc 5.  (3,4)-(10,10): cheb 7, euc ~9.22.
# NN cheb per cat: [4, 4, 7] -> median 4, contact_share 0.
snap = [[(0, 0), (3, 4), (10, 10)]]
s = stats(snap)
assert s["cheb_median"] == 4, s
assert s["euc_median"] == 5, s
assert s["contact_share"] == 0.0, s

# Red: include self as its own neighbour and every distance is 0 -- the
# bug this guard exists to catch, shown catchable.
b = stats(snap, include_self=True)
assert b["cheb_median"] == 0 and b["contact_share"] == 1.0, b

# Two adjacent cats: contact registers.
s2 = stats([[(5, 5), (6, 5)]])
assert s2["cheb_median"] == 1 and s2["contact_share"] == 1.0, s2

print("nn_distance guard: green (self-inclusion bug shown red)")
