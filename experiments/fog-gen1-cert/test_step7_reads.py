#!/usr/bin/env python3
"""Guard for step7_reads.py (plain asserts, no pytest).

Synthetic five-cat fixtures in the probe-row convention (kitty rows by
id ascending excluding self, A15), the shape test_phase2_read.py uses.
Covers: sleeping-only for the beam share; duet start de-duplication and
the t-1 need read; conscription = play not the member's top need; the
strict > consent line; groom spell latency, censoring and the spell
break at a tick gap; the E1 gap sign.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import step7_reads as S  # noqa: E402
L = S.L
K = 5


def fixture(T):
    n = T * K
    return {"obs": np.zeros((n, L.OBS_DIM), np.float32), "mask": np.zeros((n, L.N_ACT), bool),
            "tick": np.repeat(np.arange(T), K), "kitty": np.tile(np.array(S.IDS), T),
            "act": np.zeros(n, np.int64), "seed": np.zeros(n, np.int64)}


def r(rows, t, i):
    return t * K + S.IDS.index(i)


def set_self(rows, t, i, activity=0, partnered=False, in_beam=False, needs=None, target=None):
    o = rows["obs"][r(rows, t, i)]
    o[L.SELF_ACTIVITY + activity] = 1.0
    o[L.SELF_PARTNERED] = float(partnered)
    o[L.SELF_IN_SUNBEAM] = float(in_beam)
    if needs is not None:
        o[L.SELF_NEEDS:L.SELF_NEEDS + 6] = np.array(needs) / 100
    if target is not None:
        slot = [j for j in S.IDS if j != i].index(target)
        b = S.KB + slot * S.KW
        o[b + L.ROW_PRESENT] = 1.0
        o[b + L.ROW_IS_TARGET] = 1.0


def set_friend(rows, t, i, j, present=True, bath=0.0, legal=False):
    slot = [x for x in S.IDS if x != i].index(j)
    b = S.KB + slot * S.KW
    o = rows["obs"][r(rows, t, i)]
    o[b + L.ROW_PRESENT] = float(present)
    o[b + L.ROW_NEEDS + 5] = bath / 100
    rows["mask"][r(rows, t, i), S.GROOM_MENU + slot] = legal


def test_beam_share_counts_sleeping_ticks_only():
    rows = fixture(4)
    set_self(rows, 0, 1, activity=S.ACT_SLEEP, in_beam=True)
    set_self(rows, 1, 1, activity=S.ACT_SLEEP, in_beam=False)
    set_self(rows, 2, 1, activity=1, in_beam=True)   # resting on the beam: not a sleep tick
    set_self(rows, 3, 1, activity=S.ACT_SLEEP, in_beam=True)
    b = S.beam_sleep_share(rows)
    assert b["Miso"] == {"sleep_ticks": 3, "in_beam_share": 2 / 3}, b["Miso"]
    assert b["Biscuit"]["in_beam_share"] is None and b["pooled"]["sleep_ticks"] == 3


def test_duet_starts_dedupe_and_read_needs_at_t_minus_1():
    rows = fixture(5)
    # Miso (1) and Biscuit (2) idle at t0 with needs, duet t1..t3, Miso re-starts with Pumpkin (3) at t4
    set_self(rows, 0, 1, needs=[10, 10, 10, 50, 10, 10])          # Miso: play top
    set_self(rows, 0, 2, needs=[45, 10, 10, 20, 10, 10])          # Biscuit: eat 45 top -> conscripted
    for t in (1, 2, 3):
        set_self(rows, t, 1, activity=S.ACT_PLAY, partnered=True, target=2, needs=[10, 10, 10, 50, 10, 10])
        set_self(rows, t, 2, activity=S.ACT_PLAY, partnered=True, target=1, needs=[60, 10, 10, 20, 10, 10])  # post-apply: risen
    set_self(rows, 4, 1, activity=S.ACT_PLAY, partnered=True, target=3, needs=[10, 10, 10, 50, 10, 10])
    set_self(rows, 4, 3, activity=S.ACT_PLAY, partnered=True, target=1, needs=[10, 10, 10, 50, 10, 10])
    starts = S.duet_starts(rows)
    assert sorted(starts) == [(0, 1, 1, 2), (0, 4, 1, 3)], sorted(starts)
    assert starts[(0, 1, 1, 2)] == {1: 0.0, 2: float(np.float32(0.45))}, starts[(0, 1, 1, 2)]  # t-1 need (f32), conscripted member only
    d = S.duets(rows)
    assert d["duets"] == 2 and d["consent_breaches"] == 1 and d["needy_member"] == {"Biscuit": 1}
    assert d["duets_per_1k_ticks"] == 1000 * 2 / 5


def test_consent_line_is_strict_and_proposer_needs_do_not_count():
    rows = fixture(2)
    # exactly at the line: not a breach (spec 047 STRICT >)
    set_self(rows, 0, 1, needs=[10, 10, 10, 50, 10, 10])
    set_self(rows, 0, 2, needs=[30, 10, 10, 20, 10, 10])
    set_self(rows, 1, 1, activity=S.ACT_PLAY, partnered=True, target=2)
    set_self(rows, 1, 2, activity=S.ACT_PLAY, partnered=True, target=1)
    assert S.duets(rows)["consent_breaches"] == 0
    # proposer (play top) with a high side need: not conscripted
    rows = fixture(2)
    set_self(rows, 0, 1, needs=[40, 10, 10, 50, 10, 10])
    set_self(rows, 0, 2, needs=[10, 10, 10, 20, 10, 10])
    set_self(rows, 1, 1, activity=S.ACT_PLAY, partnered=True, target=2)
    set_self(rows, 1, 2, activity=S.ACT_PLAY, partnered=True, target=1)
    assert S.duets(rows)["consent_breaches"] == 0
    # conscripted member one step over the line: a breach
    rows = fixture(2)
    set_self(rows, 0, 1, needs=[10, 10, 10, 50, 10, 10])
    set_self(rows, 0, 2, needs=[31, 10, 10, 20, 10, 10])
    set_self(rows, 1, 1, activity=S.ACT_PLAY, partnered=True, target=2)
    set_self(rows, 1, 2, activity=S.ACT_PLAY, partnered=True, target=1)
    assert S.duets(rows)["consent_breaches"] == 1


def test_groom_latency_spells_censoring_and_gap_break():
    rows = fixture(8)
    # Miso sees dirty Biscuit t0..t3, grooms at t2 (latency 2); spell ends by clean at t4
    for t in (0, 1, 2, 3):
        set_friend(rows, t, 1, 2, bath=25, legal=(t >= 1))
    rows["act"][r(rows, 2, 1)] = S.GROOM_MENU + 0   # Biscuit is Miso's row 0
    # a second spell t5..t7 never groomed -> censored at the end
    for t in (5, 6, 7):
        set_friend(rows, t, 1, 2, bath=25)
    g = S.groom_latency(rows)
    assert g["spells"] == 2 and g["groomed"] == 1 and g["censored"] == 1, g
    assert g["latency_median"] == 2.0 and g["dirty_visible_rows"] == 7
    assert g["legal_share_of_dirty_visible"] == 3 / 7
    # a clean tick breaks a spell (t2), and so does a gap in the tick numbers (t3 -> t10)
    rows = fixture(6)
    for t in (0, 1, 3, 4):
        set_friend(rows, t, 1, 2, bath=25)
    rows["tick"][rows["tick"] == 4] = 10
    assert S.groom_latency(rows)["spells"] == 3  # {0,1}, {3}, {10}


def test_e1_gap_is_biscuit_minus_roster():
    rows = fixture(2)
    for t in (0, 1):
        set_self(rows, t, 2, needs=[35, 0, 0, 0, 0, 0])
        for j in (1, 3, 4, 5):
            set_self(rows, t, j, needs=[35 if (t == 0 and j == 1) else 0, 0, 0, 0, 0, 0])
    e = S.e1(rows)
    assert e["eat"] == {"biscuit": 1.0, "roster": 1 / 8, "gap": 1.0 - 1 / 8}, e["eat"]
    assert e["cuddle"]["gap"] == 0.0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok ", t.__name__)
    print(f"{len(tests)}/{len(tests)} green")
