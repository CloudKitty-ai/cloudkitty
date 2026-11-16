#!/usr/bin/env python3
"""Guards m4–m7 of DECLARATION.md §9 (deviations entry 42): the reader's, each red on record before its first read.
m7 runs one 300-tick harness run of `wantmask-nohead-s1` (test_want_mask.run: 1,500 covered cat-ticks); the others
read recorded legs.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_read_wantmask.py [m4 ...]      (A = ../minifriend-phase2-2026-11-06)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_wantmask as W  # noqa: E402


def m4():
    """A leg whose rows are another seating's is refused: the no-head final's recorded unmasked leg reads as itself
    and is refused as the masked leg (both seat the same file); a leg seating another mind is refused."""
    assert len(W.load("nohead", "plain")) == 30
    for mind, path in (("nohead", W.leg_file("nohead", "plain")), ("truth", W.leg_file("nohead", "plain"))):
        try:
            W.load(mind, "masked", path)
        except AssertionError:
            continue
        raise AssertionError(f"the reader took the unmasked no-head leg as the masked {mind} leg")


def m5():
    """§8's four cells by (Δ_nohead, D), a value at the edge inside it; §4's stop needs BOTH shares under 0.001."""
    cases = [(-0.325, 0.0), (0.0, 5.0), (-0.326, 0.326), (-0.4, 0.325), (-0.4, -0.325), (-0.4, -0.326), (0.5, -1.0)]
    got = [W.grammar(*c) for c in cases]
    want = ["NOT LOAD-BEARING", "NOT LOAD-BEARING", "SUPPORTS REDUNDANCY", "UNINFORMATIVE", "UNINFORMATIVE", "REVERSED", "NOT LOAD-BEARING"]
    assert got == want, f"the grammar reads {list(zip(cases, got))}"
    stops = [W.stop(0.0009, 0.0009), W.stop(0.001, 0.0009), W.stop(0.0009, 0.001), W.stop(0.01, 0.0)]
    assert stops == [True, False, False, False], f"the grammar reads the stop as {stops}"


def m6():
    """A world aborted in any of the legs enters no pair: with the continued final's recorded 40×40 leg (world 905007
    aborted at tick 13,594) standing where a masked leg would, the pairs hold 29 worlds and not that one."""
    stand_in = W.RP.leg_rows("cont-s1", 40, W.EXPTS / "gen2-trunk-continuation-2026-11-10" / "results-raw")[0]
    assert "aborted_streak" in stand_in[905007] and len(stand_in) == 30
    plain = W.load("nohead", "plain")
    seeds = W.common([plain, stand_in, W.load("truth", "plain")])
    assert 905007 not in seeds and len(seeds) == 29, f"an aborted world entered a pair ({len(seeds)} worlds)"
    assert W.delta(stand_in, plain, seeds)["worlds"] == 29


def m7():
    """The replay fence holds on the observation the leg's policy was handed: a short masked harness run replays
    clean as a masked leg (every recorded act a maximiser on the masked observation)."""
    import test_want_mask as TM
    TM.run(TM.MASKED)
    path = sorted(TM.SCRATCH.glob(f"{TM.MASKED}-*/acts-{TM.SEED}.npz"), key=lambda p: p.stat().st_mtime)[-1]
    w = W.world(("nohead", "masked", TM.SEED, path))
    assert w["rows"] == TM.TICKS * W.C.ROSTER and w["live_rows"] > 0 and w["reach"] == 0, w


GUARDS = {"m4": m4, "m5": m5, "m6": m6, "m7": m7}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
