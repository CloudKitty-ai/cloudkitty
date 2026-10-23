#!/usr/bin/env python3
"""Guards for strata.py (plain asserts; any venv with numpy).

t1  hand cases at each ruled edge: 44.99/45 on happiness (grave edge),
    69.99/70 (adjacent edge), 89.99/90 on a hidden need (grave edge);
    bath at 100 never bins
t2  on a recorded rot2 stream the three bins partition every cat-tick,
    and the GRAVE count equals a hand count from the raw arrays
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import strata as S  # noqa: E402

ROT2 = HERE.parent / "seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905001.npz"


def test_t1_edges_are_the_ruled_ones():
    # red: an edge flipped from < to <= (or >= to >)
    def one(hap, **need):
        n = np.zeros(6)
        for k, v in need.items():
            n[{"eat": 0, "drink": 1, "sleep": 2, "play": 3, "cuddle": 4, "bath": 5}[k]] = v
        return int(S.stratum(n, hap))

    assert one(44.99) == S.GRAVE
    assert one(45.0) == S.ADJACENT
    assert one(69.99) == S.ADJACENT
    assert one(70.0) == S.COMMON
    assert one(80.0, play=89.99) == S.COMMON
    assert one(80.0, play=90.0) == S.GRAVE
    assert one(60.0, cuddle=90.0) == S.GRAVE      # need edge beats the adjacent band
    assert one(80.0, bath=100.0) == S.COMMON      # bath is visible, never bins
    assert one(50.0, bath=100.0) == S.ADJACENT


def test_t2_bins_partition_a_recorded_stream():
    assert ROT2.exists(), ROT2
    z = np.load(ROT2)
    meta = json.loads(str(z["meta"]))
    needs, hap = z["needs"], z["hap"]              # (T, 5, 6), (T, 5) on /100
    assert meta["seating"] == "g2-rot2" and needs.shape[0] == meta["ticks"]
    codes = S.stratum(needs, hap)
    assert codes.shape == hap.shape
    c = S.counts(codes)
    assert sum(c.values()) == hap.size, (c, hap.size)
    hand_grave = int(((needs[:, :, :5] >= 90).any(-1) | (hap < 45)).sum())
    assert c["GRAVE"] == hand_grave, (c, hand_grave)
    assert c["COMMON"] > c["ADJACENT"] >= 0 and c["GRAVE"] >= 0
    # the per-cat GRAVE counts are the distress-tick counts plus any
    # happiness<45 ticks (none expected on rot2's lived worlds)
    per_cat = [int((codes[:, k] == S.GRAVE).sum()) for k in range(5)]
    assert per_cat == [int(((needs[:, k, :5] >= 90).any(-1) | (hap[:, k] < 45)).sum()) for k in range(5)]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
