#!/usr/bin/env python3
"""Guards of DECLARATION.md §9 (g7, g8 here; g1–g6 land with the driver, after deviations entry 32 is ruled); each
red on record via scripts/mutate.sh --expect before any seed trains.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_cont.py [g7 g8 ...]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_curves as RC  # noqa: E402


def g7():
    """R-3's frozen rule reproduces every recorded stop (the asserts live in read_plateau.read, which raises): the
    seven trunk plateau stops sit at their last bin — 8,002,560 ticks on six seeds, 9,000,960 on s7 — and the Phase 2
    plateau stops at theirs; a run halted by a welfare stop shows no plateau stop."""
    import read_plateau as RP
    out = RP.read()
    trunk = {n: r for n, r in out.items() if n.startswith("ppo-g2-trunk")}
    assert len(trunk) == 11 and sum(r["stop_reason"] == "plateau" for r in trunk.values()) == 7, {n: r["stop_reason"] for n, r in trunk.items()}
    for n, r in trunk.items():
        if r["stop_reason"] == "plateau":
            assert r["rules"]["frozen"]["ticks"] == r["stop_ticks"] == (9_000_960 if n.endswith("s7") else 8_002_560), (n, r["rules"]["frozen"], r["stop_ticks"])
    assert len([n for n in out if n.startswith("p2-")]) == 12


def g8():
    """R-2's STEP on the no-head arms reproduces DECLARATION §2.2: +0.0112 / +0.0112 / +0.0154 on s1r / s2 / s4.
    §2.2's figures are printed-cell arithmetic (each bin return at four decimals, then subtracted), so the STEP is
    taken here over the bin returns rounded to four decimals; the reader itself reports the raw STEP, which on s4 is
    +0.0153 (0.01534; deviations entry 32 (3))."""
    got = []
    for k in (1, 2, 4):
        runs = RC.LINEAGES[k]
        r4 = lambda bins: [{"ret": round(b["ret"], 4)} for b in bins]
        got.append(round(RC.step(r4(RC.series(runs["nohead"])), r4(RC.series(runs["trunk"]))), 4))
    assert got == [0.0112, 0.0112, 0.0154], f"the no-head STEP on s1r / s2 / s4 reads {got}, DECLARATION §2.2 records [0.0112, 0.0112, 0.0154]"


GUARDS = {"g7": g7, "g8": g8}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
