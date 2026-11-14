#!/usr/bin/env python3
"""Guards of the needs-only arm's readers (DECLARATION.md §9: each reader's extension lands with its own red before
its first read). Recorded legs only; nothing is served.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_needs_reads.py [guard ...]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def n1():
    """R-1's reader refuses a leg whose header names another file than the arm's final: the scout's recorded 20×20
    leg reads under its own final, and raises when the final asked for is the dual-head arm's."""
    import read_r1_needs as R
    R.leg(1, 20)
    try:
        R.leg(1, 20, final=R.P2 / "artifacts" / "p2-both-s1" / "policy-final.pt")
    except AssertionError:
        return
    raise AssertionError("the needs leg was read as the dual-head final: the header's artifact sha256 is not compared")


def n2():
    """The two-by-two's recorded cell is both − act15 on the same seed: it reproduces the declared +0.233 / +0.379 /
    +0.591 (DECLARATION §6) at 20 / 40 / 100."""
    import read_r1_needs as R
    got = [round(R.recorded_cell(1, z)["mean"], 3) for z in (20, 40, 100)]
    assert got == [0.233, 0.379, 0.591], f"both − act15 reads {got}"


def n3():
    """The scoring on the scout's recorded legs: N1 needs the paired mean inside the edge at BOTH sizes, N2 at least
    25 of 30 worlds at both, §8's cases need the edge crossed at both sizes; nothing scores with a leg missing."""
    import read_r1_needs as R
    out = R.read(1)
    got = (out["N1"]["inside_edge"], out["N1"]["met"], out["N2"]["positive_worlds"], out["N2"]["met"], out["reading"])
    assert got == ({"20": True, "40": False}, False, {"20": 14, "40": 11}, False, "NOT COVERED"), f"R-1 scores {got}"
    short = R.score({n: v for n, v in out["legs"].items() if n != "s1/40"}, 1)
    assert short == {}, f"with the 40×40 leg absent R-1 scores {sorted(short)}"


def n4():
    """The block read replays one world of the scout's recorded 20×20 leg under both fences (the recorded act is a
    maximiser of the replayed masked logits; all cells zeroed equals the trainer's own cells-in-use count) and its
    blocks partition the arm's 9 cells with the needs cells at offset 0."""
    import read_blocks_needs as B
    assert B.BLOCKS == {"needs": (0, 8), "tsl": (8, 9), "all": (0, 9)} and B.PG == 7, f"blocks {B.BLOCKS}, P(grave) cell {B.PG}"
    w = B.leg(20, [905001])["worlds"][0]
    assert w["rows"] == 100_000 and w["zero"]["all"]["changed"] == w["trainer_changed"] > 0, f"world 905001 reads {w}"


def n5():
    """A partial leg is never scored: a one-world leg file in a scratch directory raises at the score."""
    import json
    import tempfile
    import read_blocks_needs as B
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / f"{B.SEATING}-20.json").write_text(json.dumps(B.leg(20, [905001])))
        try:
            B.score(Path(td))
        except AssertionError:
            return
    raise AssertionError("a partial leg was scored")


GUARDS = {"n1": n1, "n2": n2, "n3": n3, "n4": n4, "n5": n5}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
