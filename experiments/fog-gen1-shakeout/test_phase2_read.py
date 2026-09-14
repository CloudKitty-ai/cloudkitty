#!/usr/bin/env python3
"""Guard for phase2_read.py (plain asserts, no pytest).

Synthetic three-cat fixtures built in partb_read's row convention
(kitty rows ascending-id excluding self, per A15). Covers: the
unseen-speaker exclusion, the >= 2 approach bar, the settled+beam
conjunction, and the own-sleep arming gate.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
import phase2_read as p2  # noqa: E402

KB, KW = p2.KITTY_BASE, p2.KITTY_W


def fixture(T, K=3):
    n = T * K
    return {"obs": np.zeros((n, L.OBS_DIM), np.float32),
            "tick": np.repeat(np.arange(T), K),
            "kitty": np.tile(np.arange(K), T),
            "msg": np.zeros(n, np.int64)}


def set_row(rows, t, i, pos, sees=(), settled_beam=(), sleep=0.0, say=0):
    K = 3
    r = t * K + i
    o = rows["obs"][r]
    o[L.SELF_POS:L.SELF_POS + 2] = np.array(pos) / p2.W
    o[L.SELF_NEEDS + 2] = sleep / 100
    rows["msg"][r] = say
    others = [k for k in range(K) if k != i]
    for slot, oid in enumerate(others):
        b = KB + slot * KW
        if oid in sees:
            o[b + L.ROW_PRESENT] = 1
        if oid in settled_beam:
            o[b + L.ROW_PRESENT] = 1
            o[b + L.ROW_ACTIVITY + 2] = 1        # sleeping
            o[b + p2.ROW_SUNBEAM] = 1


# --- responder approach ----------------------------------------------------
# cat 2 says want_cuddle at t0, unseen by cat 0 (far), seen by cat 1.
# cat 0 walks 3 closer within the window -> 1 event, 1 approach for the
# unseen listener; the seen listener is excluded.
rows = fixture(4)
for t in range(4):
    set_row(rows, t, 2, (10, 10), say=p2.MSG_WANT_CUDDLE if t == 0 else 0)
    set_row(rows, t, 1, (11, 10), sees=(2,))
    set_row(rows, t, 0, (10 - 8 + 3 * min(t, 1), 10))   # 8 away, then 5
ids, pos, present, beamset, said, sleep = p2.per_tick(rows)
ev, ap = p2.approach_events(pos, present, said, 10, p2.MSG_WANT_CUDDLE)
assert ev == 1, f"approach: exactly the unseen listener is an event, got {ev}"
assert ap == 1, f"approach: closing 3 >= 2 counts, got {ap}"

# same but cat 0 closes only 1 -> event without approach
rows = fixture(4)
for t in range(4):
    set_row(rows, t, 2, (10, 10), say=p2.MSG_WANT_CUDDLE if t == 0 else 0)
    set_row(rows, t, 1, (11, 10), sees=(2,))
    set_row(rows, t, 0, (10 - 8 + min(t, 1), 10))
_, pos, present, _, said, _ = p2.per_tick(rows)
ev, ap = p2.approach_events(pos, present, said, 10, p2.MSG_WANT_CUDDLE)
assert (ev, ap) == (1, 0), f"approach: closing 1 < 2 is no approach, got {(ev, ap)}"

# --- cosleep ---------------------------------------------------------------
# cat 1 settled on a beam, Seen by cat 0 whose sleep is armed (25 >= 20);
# cat 0 closes 2 at t1 then holds -> three opportunity ticks, of which
# only t0 sees a further >= 1 close. cat 2's sleep is 5 -> never an
# opportunity even though it sees the same friend.
rows = fixture(4)
for t in range(4):
    set_row(rows, t, 1, (10, 10))
    set_row(rows, t, 0, (14 - 2 * min(t, 1), 10), settled_beam=(1,), sleep=25)
    set_row(rows, t, 2, (16, 10), settled_beam=(1,), sleep=5)
_, pos, present, beamset, _, sleep = p2.per_tick(rows)
opps, closed = p2.cosleep_approach(pos, present, beamset, sleep, 20.0, 10)
assert opps == 3, f"cosleep: armed seat only, one opportunity per tick, got {opps}"
assert closed == 1, f"cosleep: only the t0 opportunity still closes >= 1, got {closed}"

# unarmed everywhere -> zero opportunities
opps2, _ = p2.cosleep_approach(pos, present, beamset, sleep * 0, 20.0, 10)
assert opps2 == 0, "cosleep: no armed sleep, no opportunities"

# settled friend NOT on a beam must not create opportunities
rows = fixture(3)
for t in range(3):
    set_row(rows, t, 1, (10, 10))
    set_row(rows, t, 0, (14, 10), sees=(1,), sleep=25)
    set_row(rows, t, 2, (16, 10))
_, pos, present, beamset, _, sleep = p2.per_tick(rows)
opps3, _ = p2.cosleep_approach(pos, present, beamset, sleep, 20.0, 10)
assert opps3 == 0, "cosleep: a Seen friend off-beam is not an opportunity"

print("test_phase2_read: PASS")
