#!/usr/bin/env python3
"""Guards for radius_read.py (DECLARATION.md §Instrument), on the real
recorded rows. Plain asserts: `python3 -B test_radius.py`.

g1  the radius-5 paired gap reproduces the certificate's +4.594 at 40×40
g2  the difference of gaps is per-world arithmetic (its SD, not only its
    mean, equals the SD of the per-world differences — a reader that
    pairs in the wrong seed order keeps the mean and loses the SD)
g3  R4's identity check compares per world: a cyclically permuted copy
    of the scripted rows must FAIL it
"""
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import radius_read as rr  # noqa: E402

CERT_GAP_40 = 4.594   # gen2-cert-battery-2026-10-20/RESULTS.md §Phase C, 40×40


def test_g1_radius5_gap_reproduces_the_certificate():
    out = rr.read()
    assert round(out["r1"]["gap_radius5"]["mean"], 3) == CERT_GAP_40, out["r1"]["gap_radius5"]["mean"]


def test_g2_gap_difference_is_per_world_arithmetic():
    out = rr.read()
    pw = out["r1"]["per_world"]
    hand = [a - b for a, b in zip(pw["gap_radius4"], pw["gap_radius5"])]
    got = out["r1"]["gap_difference_4_minus_5"]
    assert abs(got["mean"] - st.mean(hand)) < 1e-9
    assert abs(got["sd"] - st.stdev(hand)) < 1e-9, (got["sd"], st.stdev(hand))
    # and the per-world gaps themselves are seed-paired
    _, S = rr.by_seed(rr.ROWS["S4"])
    _, R = rr.by_seed(rr.ROWS["R4"])
    w = out["seeds"][7]
    assert abs(pw["gap_radius4"][7] - (rr.team(R[w]) - rr.team(S[w]))) < 1e-12


def test_g3_identity_check_is_per_world():
    _, S = rr.by_seed(rr.ROWS["S4"])
    seeds = sorted(S)
    assert rr.identity(S, S, seeds)["identical"]
    rolled = {seeds[(i + 1) % len(seeds)]: S[w] for i, w in enumerate(seeds)}
    v = rr.identity(S, rolled, seeds)
    assert not v["identical"] and len(v["mismatches"]) >= 25, v


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
