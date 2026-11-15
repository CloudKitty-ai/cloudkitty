#!/usr/bin/env python3
"""Guards of read_reanchor.py (deviations entry 38), each red on record before the first read. No mind decides here.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_read_reanchor.py [u1 ...]      (A = ../minifriend-phase2-2026-11-06)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_reanchor as RR  # noqa: E402


def u1():
    """A leg whose header names another file is refused: the recorded 10M rung leg of cont-s1 reads under its own
    checkpoint and is refused when the seating's file is said to be cont-s1's final."""
    seating, root = RR.OTHERS["cont_10M"]
    assert len(RR.leg(seating, 40, root)) == 30
    try:
        RR.leg(seating, 40, root, artifact=RR.K / "artifacts" / "cont-s1" / "policy-final.pt")
    except AssertionError:
        return
    raise AssertionError("the reader took a leg whose header names another file")


def u2():
    """A1: the first bin at least 0.005 above the trunk's last, its KL to the anchor between 0.10 and 0.30."""
    got = [RR.a1(0.005, 0.20), RR.a1(0.0049, 0.20), RR.a1(0.01, 0.31), RR.a1(0.01, 0.09)]
    assert got == [True, False, False, False], f"A1 scores (0.005, 0.20) / (0.0049, 0.20) / (0.01, 0.31) / (0.01, 0.09) as {got}"


def u3():
    """A2: above the trunk in at least 25 of 30 worlds with the mean beyond the edge, and beyond the edge over cont-s1's rung."""
    vs = lambda pos, mean: {"positive": pos, "mean": mean, "n": 30}      # noqa: E731
    got = [RR.a2(vs(25, 0.33), vs(20, 0.33)), RR.a2(vs(24, 0.40), vs(30, 0.40)), RR.a2(vs(30, 0.32), vs(30, 0.40)), RR.a2(vs(30, 0.40), vs(30, 0.32))]
    assert got == [True, False, False, False], f"A2 scores its four cases as {got}"
    assert [RR.a3(vs(30, 0.5), vs(30, 1.0)), RR.a3(vs(30, 0.49), vs(30, 1.0))] == [True, False], "A3 does not read half of the no-head gain"


GUARDS = {"u1": u1, "u2": u2, "u3": u3}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
