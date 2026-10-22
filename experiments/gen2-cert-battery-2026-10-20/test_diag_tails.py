#!/usr/bin/env python3
"""Guards for diag_tails.py's two new pieces (the replay and read_run are
the s7 investigation's, already guarded). Plain asserts:
`python3 -B test_diag_tails.py` from the lab venv.

t1  shape() places a run by the declared thresholds (moving >= 0.5 ->
    searching; Drink-while-sated >= half the window and moving <= 0.2
    -> parked), re-derived from the recorded reads' own numbers
t2  drink_while_sated() counts Drink chosen with thirst under 10, on a
    recorded rot2 stream, against an independent per-tick count
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_tails as dt  # noqa: E402

EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "gen2-trunk-training-2026-10-18" / "trainer"))


def test_t1_shape_follows_the_declared_thresholds():
    runs = [r for c in json.load(open(HERE / "diag-tails.json")) for r in c["runs"]]
    by = {(r["seat"], r["need"], r["recorded_longest"]): r for r in runs}
    cl = by[("Clementine", "cuddle", 687)]       # moving 0.60, Drink 22 of 100
    assert cl["moving_share"] >= 0.5 and dt.shape(cl) == "searching", cl["moving_share"]
    pk = by[("Pumpkin", "eat", 641)]             # Drink 100 of 100, still
    assert pk["drink_while_sated"] == pk["length"] and pk["moving_share"] == 0.0
    assert dt.shape(pk) == "parked"
    bi = by[("Biscuit", "cuddle", 602)]          # Drink 47 of 100, moving 0.24
    assert dt.shape(bi) == "other", (bi["drink_while_sated"], bi["moving_share"])
    # the parked rule needs BOTH halves: still but not drinking is not parked
    still = dict(pk, drink_while_sated=0)
    assert dt.shape(still) == "other"


def test_t2_drink_while_sated_counts_drink_under_thirst_10():
    from data_g2 import ACTION_NAMES
    z = np.load(EXPTS / "seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905001.npz")
    drink = ACTION_NAMES.index("Drink")
    T = z["act"].shape[0]
    for k in range(5):
        hand = 0
        for t in range(T):
            if z["act"][t, k] == drink and z["needs"][t, k, 1] < 10:
                hand += 1
        got = dt.drink_while_sated(z, k, 0, T - 1)
        assert got == hand, (k, got, hand)
    assert sum(dt.drink_while_sated(z, k, 0, T - 1) for k in range(5)) > 0, "fixture carries no sated drinking"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
