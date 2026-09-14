#!/usr/bin/env python3
"""Guard for groom_cells.py (plain asserts, no pytest).

Synthetic five-cat rows in the by-id row convention (A15). Covers: the
groom index names the observer's k-th other id; a cell's opportunity
needs present AND bath at the threshold AND GroomKitty legal, each
alone insufficient; the visible count ignores dirt; own-dirty share
reads the self bath cell; the by-row totals fold observer cells onto
their row index.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
import groom_cells as gc  # noqa: E402

KB, KW = gc.KB, gc.KW


def rows(n):
    return (np.zeros((n, L.OBS_DIM), np.float32), np.zeros(n, int),
            np.full(n, 38, int), np.zeros((n, 39), np.uint8))


def put(obs, mask, r, k, present=1.0, bath=0.0, legal=1):
    b = KB + k * KW
    obs[r, b + L.ROW_PRESENT] = present
    obs[r, b + L.ROW_NEEDS + 5] = bath
    mask[r, 15 + k] = legal


# Observer Miso (1): row 0 = Biscuit (2), row 2 = Kittybear (4).
obs, kitty, act, mask = rows(6)
kitty[:] = 1
put(obs, mask, 0, 0, bath=0.25)            # dirty, visible, legal
act[0] = 15                                # grooms row 0 = Biscuit
put(obs, mask, 1, 0, bath=0.25)            # opportunity, no groom
put(obs, mask, 2, 0, bath=0.19)            # clean: no opportunity
put(obs, mask, 3, 0, present=0.0, bath=0.25)  # unseen: no opportunity
put(obs, mask, 4, 0, bath=0.25, legal=0)   # illegal: dirty-visible, not legal
put(obs, mask, 5, 2, bath=0.20)            # Kittybear at the threshold
act[5] = 17                                # grooms row 2 = Kittybear
c = gc.cells(obs, kitty, act, mask)
assert c[(1, 2)] == [1, 3, 2, 4], c[(1, 2)]   # grooms, dirty-visible, +legal, visible
assert c[(1, 4)] == [1, 1, 1, 1], c[(1, 4)]
assert c[(1, 3)] == [0, 0, 0, 0] and c[(1, 5)] == [0, 0, 0, 0]

# Observer Clem (5): row 1 = Biscuit (2); the same index 16 must NOT
# count as Biscuit for Miso, whose row 1 is Pumpkin (3).
obs, kitty, act, mask = rows(2)
kitty[:] = [5, 1]
put(obs, mask, 0, 1, bath=0.3); act[0] = 16
put(obs, mask, 1, 1, bath=0.3); act[1] = 16
c = gc.cells(obs, kitty, act, mask)
assert c[(5, 2)][0] == 1 and c[(1, 3)][0] == 1 and c[(1, 2)][0] == 0, c

# Own-dirty share reads the self bath cell, not a row's.
obs, kitty, act, mask = rows(4)
kitty[:] = [2, 2, 3, 3]
obs[0, L.SELF_NEEDS + 5] = 0.5
obs[2, KB + L.ROW_NEEDS + 5] = 0.5           # a row's bath must not count
ds = gc.dirty_share(obs, kitty)
assert ds[2] == 0.5 and ds[3] == 0.0, ds

# add() accumulates cell-wise.
a = gc.add({(1, 2): [1, 2, 3, 4]}, {(1, 2): [1, 1, 1, 1], (1, 3): [0, 0, 0, 1]})
assert a == {(1, 2): [2, 3, 4, 5], (1, 3): [0, 0, 0, 1]}, a
print("test_groom_cells: ok")
