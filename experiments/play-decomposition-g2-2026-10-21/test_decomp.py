#!/usr/bin/env python3
"""Guards for decomp_read.py (plain asserts, lab venv; DECLARATION.md
§Instrument g1–g3). They read recorded streams in the native checkout."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decomp_read as D  # noqa: E402

C2 = np.load(HERE / "results-raw/C2/streams-905001.npz")
N2 = np.load(D.CELLS["N2"] / "streams-905001.npz")
C1 = np.load(D.CELLS["C1"] / "streams-905001.npz")


def test_g1_play_share_equals_an_independent_count():
    # red: PLAY pointed at another activity -> the shares differ on every cat
    w = D.world_read(C2, False)
    flag, ap = C2["activity"], C2["applied"]
    T, R = flag.shape
    play_idx = D.APPLIED_NAMES.index("play")
    for k in range(R):
        n = 0
        for t in range(T):
            if flag[t, k] == 5 or (flag[t, k] == 0 and ap[t, k] == play_idx):
                n += 1
        assert abs(w["share"][k] - n / T) < 1e-12, (k, w["share"][k], n / T)


def test_g2_onset_needs_are_read_one_tick_earlier():
    # red: the onset read on tick t instead of t-1 -> differs from needs[start-1]
    play, _kitty, _act, _part = D.play_masks(C2)
    starts = np.array([s for s in D.starts_of(play[:, 0]) if s >= 1])
    pn, on = D.onsets(C2, play, 0)
    assert len(pn) == len(starts) > 100
    assert np.array_equal(pn, C2["needs"][starts - 1, 0, D.PLAY_NEED])
    assert not np.array_equal(pn, C2["needs"][starts, 0, D.PLAY_NEED])
    others = np.delete(C2["needs"][starts - 1, 0], D.PLAY_NEED, axis=1).max(1)
    assert np.array_equal(on, others)


def test_g3_happiness_weights_and_scale_match_the_engine():
    # red: one weight moved (eat 0.20 -> 0.15) -> the derived happiness leaves
    # the recorded hap stream (no clamp binds on rot2 905001: hap > 5 everywhere)
    for z in (N2, C1):
        assert (z["hap"] > 5.0).all()
        wts = np.array([D.WEIGHTS[n] for n in D.NEED_NAMES])
        derived = 100.0 - z["needs"] @ wts
        assert abs(derived.mean() - z["hap"].mean()) < 0.01, (derived.mean(), z["hap"].mean())
        assert np.abs(derived - z["hap"]).max() < 0.05


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
