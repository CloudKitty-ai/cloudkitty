#!/usr/bin/env python3
"""Guards m1–m3 of DECLARATION.md §9 (deviations entry 42): the mask itself and its place in the harness. Each red on
record via scripts/mutate.sh --expect before a covered leg runs.
  m1  on the replayed observations of a recorded world (the no-head final's 40×40 leg, g2cmp 905001, its first 3,000
      ticks) the mask zeroes the 24 want-intensity cells and changes no other cell; the cells it zeroes are the ones
      that hold a friend's need (read here off the engine's state, the columns counted here from the row contract)
  m2  a short harness run of `wantmask-nohead-s1` (300 ticks: five copies of the no-head final decide, 1,500 covered
      cat-ticks) records the policy's greedy acts on the MASKED observation, not on the unmasked one
  m3  a seating that is not a wantmask seating is untouched: `p2u-nohead-s1`'s short run reproduces its recorded leg

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_want_mask.py [m1 ...]      (A = ../minifriend-phase2-2026-11-06; about a minute)
"""
import functools
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "minifriend-phase2-2026-11-06"))
import p2_common as C  # noqa: E402  (puts the harness on the path)
import replay as RP  # noqa: E402
import cert_harness_fog as H  # noqa: E402

SIZE, SEED, TICKS, M1_TICKS = 40, 905001, 300, 3000
BASE, MASKED, SPEC = "p2u-nohead-s1", "wantmask-nohead-s1", "p2:p2-nohead-s1r"
SCRATCH = Path(os.environ.get("WANTMASK_SCRATCH", "/tmp/wantmask-scratch"))
R, N_ACT = C.ROSTER, 35
# The row contract (contracts/observation-v6.md), counted here and not read from the layout module the mask uses:
# four kitty rows of 58 cells from cell 109; in each, the last four cells are the answers-me bits and the six before
# them the want intensities, in the order eat, drink, play, cuddle, bath, sleep.
WANT_COLS = np.asarray([109 + 58 * i + 48 + j for i in range(4) for j in range(6)])
EAT, CUDDLE = 0, 3                                          # columns of a row's six; needs (eat, drink, sleep, play, cuddle, bath)
NEED_OF = {EAT: 0, CUDDLE: 4}


def greedy(fwd, ob, mk):
    lg = np.asarray(fwd(ob, mk), np.float32)
    return np.where(mk[:, :N_ACT], lg[:, :N_ACT], H.NEG_INF).argmax(1)


@functools.lru_cache(None)
def run(seating):
    """One 300-tick harness run of `seating` on the world: (its recorded acts (T, R, 2), its replayed ticks)."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=f"{seating}-", dir=SCRATCH))
    H.run_one((seating, SEED, TICKS, str(C.LEG_TOML[SIZE]), list(H.SEATINGS[seating]), None, "served", None, None, 1000, str(out)))
    p = out / f"acts-{SEED}.npz"
    return np.load(p)["acts"], list(RP.replay(p, C.LEG_TOML[SIZE], want_obs=True))


def m1():
    obs, need = [], []
    for rec in RP.replay(RP.acts_path(BASE, SIZE, SEED), C.LEG_TOML[SIZE], want_obs=True):
        if rec["tick"] >= M1_TICKS:
            break
        obs.append(rec["obs"]); need.append(rec["pre"][0])
    obs, need = np.stack(obs), np.stack(need)               # (T, R, 399), (T, R, 6) x100
    flat = obs.reshape(-1, obs.shape[-1])
    masked = H.mask_want_intensity(flat.copy())
    other = np.setdiff1d(np.arange(flat.shape[1]), WANT_COLS)
    outside, live = int((masked[:, other] != flat[:, other]).sum()), int((masked[:, WANT_COLS] != 0).sum())
    assert outside == 0 and live == 0, f"the mask changed cells outside the want-intensity block or left one live: {outside} outside, {live} live"
    was = int((flat[:, WANT_COLS] > 0).sum())
    assert was > 1000, f"only {was} want-intensity cells are live on the world: the guard sees nothing"
    # the cells are the friend's need: where a friend's eat or cuddle need is 50+ and its cell is live, the cell is that need
    n = close = 0
    for k in range(R):
        for i, j in enumerate([j for j in range(R) if j != k]):
            for col, ni in NEED_OF.items():
                cell = obs[:, k, 109 + 58 * i + 48 + col] * 100
                rows = (need[:, j, ni] >= 50) & (cell > 0)
                n += int(rows.sum()); close += int((np.abs(cell[rows] - need[rows, j, ni]) <= 10).sum())
    assert n >= 200 and close >= 0.9 * n, f"the cells the mask zeroes do not hold the friend's need: {close} of {n} within 10 points"


def m2():
    acts, recs = run(MASKED)
    fwd = H.load_model(SPEC)
    wrong = changed = 0
    for t, rec in enumerate(recs):
        ob, mk = rec["obs"].astype(np.float32), rec["mask"].astype(bool)
        on = greedy(fwd, H.mask_want_intensity(ob.copy()), mk)
        wrong += int((acts[t, :, 0] != on).sum()); changed += int((on != greedy(fwd, ob, mk)).sum())
    assert wrong == 0, f"a recorded act is not the masked policy's: {wrong} of {len(recs) * R} rows"
    assert changed > 0, "the mask changed no greedy act in the run: the guard sees nothing"


def m3():
    acts, _recs = run(BASE)
    rec = np.load(RP.acts_path(BASE, SIZE, SEED))["acts"][:TICKS]
    assert acts.shape == rec.shape and (acts == rec).all(), f"the unmasked seating's acts differ from its recorded leg: {int((acts != rec).sum())} cells"
    assert H.SEATINGS[MASKED] == H.SEATINGS[BASE] and H.SEATINGS["wantmask-truth-s1"] == H.SEATINGS["p2u-truth-s1"], "a wantmask seating seats another mind"


GUARDS = {"m1": m1, "m2": m2, "m3": m3}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
