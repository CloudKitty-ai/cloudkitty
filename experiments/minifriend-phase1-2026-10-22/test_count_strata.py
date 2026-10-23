#!/usr/bin/env python3
"""Guards for count_strata.py on the recorded L world 905001 (arc venv).

c1  per friend the all-states sample count is 4 observers × T, every
    stratum's visible count is ≤ its all count, and the strata sum to T
    per observer
c2  the mind-visible count reads the friend's PRESENT cell in the
    observer's row for that friend: it equals a hand count over the four
    observers at offset 109 + 58·row (rows = roster minus observer, by
    id), and a cell that is not the present cell gives a different count
c3  the truth paired with obs[t] is the state at t−1: the observer's own
    needs in its self block equal the aligned stream, never the same-
    index stream
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_strata as C  # noqa: E402
import strata as S  # noqa: E402

W = HERE / "results-raw/L/streams-905001.npz"


def test_c1_counts_partition():
    seed, T, per = C.count_world(W)
    assert seed == 905001 and T == 20000
    for f, d in per.items():
        assert sum(d[n]["all"] for n in S.NAMES) == 4 * T, (f, d)
        assert all(d[n]["visible"] <= d[n]["all"] for n in S.NAMES), (f, d)
    assert per["Pumpkin"]["GRAVE"]["all"] == 0   # L world 905001 has no distress tick (check_L)


def test_c2_visible_reads_the_present_cell_of_the_friends_row():
    z = np.load(W)
    obs = z["obs"]
    _, _, per = C.count_world(W)
    for j in range(5):
        hand = 0
        for k in range(5):
            if k == j:
                continue
            row = [x for x in range(5) if x != k].index(j)
            hand += int((obs[:, k, 109 + 58 * row].astype(np.float32) > 0.5).sum())
        got = sum(per[C.SEATS[j]][n]["visible"] for n in S.NAMES)
        assert got == hand, (j, got, hand)
        assert 0 < hand < 4 * obs.shape[0], (j, hand)
    # the present cell is a 0/1 cell; the bath cell beside it (offset 5) is not
    k, j = 0, 1
    col = 109 + 58 * [x for x in range(5) if x != k].index(j)
    assert set(np.unique(obs[:, k, col].astype(np.float32))) <= {0.0, 1.0}
    assert int((obs[:, k, col + 5].astype(np.float32) > 0.5).sum()) != int((obs[:, k, col].astype(np.float32) > 0.5).sum())


def test_c4_sets_filter_counts_only_the_requested_sets():
    """--sets (Phase 1b): only the named sets are counted, in split.json order; an unknown name refuses.
    Default None = every set, unchanged."""
    sets = {"L": {"eval": [1]}, "W": {"eval": [2]}, "G": {"eval": [3]}, "P1": {"eval": [4]}, "P2": {"eval": [5]}}
    assert C.select_sets(sets) == sets
    assert list(C.select_sets(sets, ["P2", "P1"])) == ["P1", "P2"]
    assert "L" not in C.select_sets(sets, ["P1", "P2", "G"]) and "G" in C.select_sets(sets, ["P1", "P2", "G"])
    try:
        C.select_sets(sets, ["P1", "P9"])
    except AssertionError:
        pass
    else:
        raise AssertionError("an unknown set name was accepted by --sets")


def test_c3_truth_is_the_state_the_view_was_built_from():
    z = np.load(W)
    needs, hap = C.truth_streams(z)
    own = z["obs"][:, :, :6].astype(np.float32) * 100
    assert np.abs(own - needs).max() < 0.06, np.abs(own - needs).max()
    assert np.abs(own - z["needs"]).max() > 0.06          # the same-index pairing is stale
    assert np.abs(z["obs"][:, :, 6].astype(np.float32) * 100 - hap).max() < 0.06


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
