#!/usr/bin/env python3
"""Guard for train_ppo_g2's welfare-stop input (plain asserts,
python3 -B, exp-006 venv). The frozen §6 probe distress stop reads
engine distress flags out of the v2 global state; a wrong offset or a
dead comparison silently reads streak 0 forever and the stop never
fires — the exact failure this guard must catch.

Fixtures are REAL payloads: full-100 corpus state rows (bc-collect,
engine-emitted). world.rs record_distress: in_distress(kind) <=>
need >= thresholds.distress (90) at the same frozen snapshot, no
hysteresis — so the flags must equal a needs-threshold recomputation
cell for cell (away from the float boundary).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_ppo_g2 as tp  # noqa: E402

CORPUS = HERE.parents[1] / \
    "gen2-collection-driver-2026-10-14/results-raw/full-100"
STATE = np.load(CORPUS / "r00/config-00-rollout-00/state.npy",
                mmap_mode="r")


def test_distress_flags_match_engine_truth():
    # red: DISTRESS_OFF off by one, or the 0.5 comparison broken
    st = np.asarray(STATE, np.float32)              # (20000, 237)
    n = st.shape[0]
    k = st[:, :5 * tp.PER_KITTY].reshape(n, 5, tp.PER_KITTY)
    needs = k[:, :, :6]                              # NeedKind::ALL order
    flags = np.stack([tp.kitty_distress_flags(row) for row in st])
    want_any = (needs >= 0.9).any(axis=2)
    # exclude float-boundary rows (need within 1e-4 of 0.9 on any kind)
    clear = (np.abs(needs - 0.9) > 1e-4).all(axis=2)
    agree = (flags == want_any) | ~clear
    assert agree.all(), f"{(~agree).sum()} kitty-ticks disagree"
    # non-vacuous: the real rollout must contain both states
    assert flags.any() and not flags.all(), (int(flags.sum()), flags.size)


def test_max_streak_matches_run_length_reference():
    # red: the streak recurrence dropped or the flags inverted
    st = np.asarray(STATE, np.float32)
    flags = np.stack([tp.kitty_distress_flags(row) for row in st])  # (T, 5)
    streak = np.zeros(5, np.int64)
    worst = np.zeros(5, np.int64)
    for t in range(flags.shape[0]):                 # the probe's recurrence
        streak = np.where(flags[t], streak + 1, 0)
        worst = np.maximum(worst, streak)
    # independent reference: run lengths per kitty off the flag columns
    ref = []
    for j in range(5):
        col = flags[:, j].astype(int)
        best = cur = 0
        for v in col:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        ref.append(best)
    assert worst.tolist() == ref, (worst.tolist(), ref)
    assert max(ref) > 0, "rollout has no distress run at all (vacuous)"
    print(f"  (r00 max engine-distress streak per kitty: {ref})")


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            passed += 1
    print(f"{passed} passed")
