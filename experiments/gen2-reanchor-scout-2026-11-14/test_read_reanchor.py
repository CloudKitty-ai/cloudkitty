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


def u4():
    """A2 on a new seed (entry 41) is the trunk clause alone: 25 worlds and a mean beyond the edge."""
    vs = lambda pos, mean: {"positive": pos, "mean": mean, "n": 30}      # noqa: E731
    got = [RR.a2_seed(vs(25, 0.33)), RR.a2_seed(vs(24, 0.40)), RR.a2_seed(vs(30, 0.325)), RR.a2_seed(vs(30, 0.3251))]
    assert got == [True, False, False, True], f"A2 on a new seed scores its four cases as {got}"


def u5():
    """Each seed's word, and the cross-seed line: only REPLICATES replicates."""
    got = [RR.word(True, True, True, True), RR.word(True, False, True, True), RR.word(False, True, True, True), RR.word(False, False, True, True),
           RR.word(True, True, False, True), RR.word(None, None, True, False)]
    assert got == ["REPLICATES", "RETURN ONLY", "WELFARE ONLY", "NEITHER", "STOPPED", "UNSCORED"], f"the seed's word reads {got}"
    pairs = [("REPLICATES", "REPLICATES"), ("REPLICATES", "RETURN ONLY"), ("STOPPED", "REPLICATES"), ("RETURN ONLY", "WELFARE ONLY"), ("UNSCORED", "NEITHER")]
    lines = [RR.cross(p).split(":")[0] for p in pairs]
    want = ["both replicate", "one replicates (two of three)", "one replicates (two of three)", "neither replicates (seed 1 alone)", "neither replicates (seed 1 alone)"]
    assert lines == want, f"the cross-seed grammar reads {list(zip(pairs, lines))}"


def u6():
    """Aborted worlds, on recorded rows: the continued final's 40×40 leg (world 905007 aborted) standing where an
    arm's leg would, against trunk seed 1's. As the arm: the world counts as not above and leaves the mean. As the
    comparator: the world is unpaired."""
    arm, _h = RR.RP.leg_rows("cont-s1", 40, RR.K / "results-raw")
    trunk = RR.C.battery_rows("g2-s1", 40)
    assert "aborted_streak" in arm[905007] and len(arm) == 30
    team = RR.R1C.R1.team
    d = [team(arm[s]) - team(trunk[s]) for s in sorted(arm) if s != 905007]
    got = RR.paired_seed(arm, trunk)
    assert (got["n"], got["arm_aborted"], got["unpaired"]) == (29, 1, 0) and abs(got["mean"] - sum(d) / 29) < 1e-9 and got["positive"] == sum(v > 0 for v in d), \
        f"an aborted world entered the mean: {got} against {sum(d) / 29:.6f} over 29"
    back = RR.paired_seed(trunk, arm)
    assert (back["n"], back["arm_aborted"], back["unpaired"]) == (29, 0, 1), f"a comparator's aborted world was paired: {back}"


def u7():
    """A run reads as ended only if its final records the declared end: the scout's does; the continued final (the
    trainer's own cap) and a missing file do not."""
    assert RR.ended(RR.ARM / "policy-final.pt"), "the scout's final does not read as ended"
    assert not RR.ended(RR.K / "artifacts" / "cont-s1" / "policy-final.pt") and not RR.ended(RR.ARM / "no-such.pt"), \
        "a run that did not reach the declared end reads as ended"


GUARDS = {"u1": u1, "u2": u2, "u3": u3, "u4": u4, "u5": u5, "u6": u6, "u7": u7}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
