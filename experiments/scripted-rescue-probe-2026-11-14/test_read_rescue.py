#!/usr/bin/env python3
"""Guards of read_rescue.py (deviations entry 39), each red on record before the first read. No mind decides here:
built rows, and a replay of the recorded no-head baseline (g2cmp 905002 at 100×100, its first 600 ticks).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_read_rescue.py [t1 ...]      (A = ../minifriend-phase2-2026-11-06)
"""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_rescue as RR  # noqa: E402
C, RP = RR.C, RR.RP

BASE_100 = RR.leg_dir("base", 100) / f"p2u-nohead-s1-g2cmp-30x{RR.TICKS}.jsonl"


def rows(deltas, aborted=()):
    """Two built legs over the battery's first worlds: b at 80.0 in every seat, a above it by `deltas`."""
    seeds = RR.SEEDS[:len(deltas)]
    a = {s: {"seed": s, "mean_happiness": [80.0 + d] * 5, "ticks": RR.TICKS} for s, d in zip(seeds, deltas)}
    b = {s: {"seed": s, "mean_happiness": [80.0] * 5, "ticks": RR.TICKS} for s in seeds}
    for s in aborted:
        b[s] = {"seed": s, "mean_happiness": [10.0] * 5, "ticks": 5_000, "aborted_streak": {"limit": 1000, "at_tick": 5_000}}
    return a, b


def t1():
    """Only worlds run whole in both members enter a pair."""
    a, b = rows([0.5] * 10, aborted=RR.SEEDS[:1])
    p = RR.paired(a, b)
    assert RR.SEEDS[0] not in p["seeds"] and p["worlds"] == 9 and abs(p["mean"] - 0.5) < 1e-9 and p["left_out"] == [RR.SEEDS[0]], \
        f"an aborted world entered a pair ({p['worlds']} worlds, mean {p['mean']})"


def t2():
    """Lost cat-ticks: the reader's two counts equal counts made here from the engine's state alone (sight as the
    vision disc dx² + dy² <= r², the reader's from each cat's own kitty rows)."""
    size, r = 100, RR.radius(100)
    acts = RR.leg_dir("base", size) / "acts" / "acts-905002.npz"
    sight, manh, hap, need = RR.lost_counts(itertools.islice(RP.replay(acts, C.LEG_TOML[size], want_obs=True), 600), size, r)
    mine_sight = mine_manh = 0
    for rec in itertools.islice(RP.replay(acts, C.LEG_TOML[size]), 600):
        needs, _h, pos, _a, partnered, _p, _d = rec["pre"]
        tile = np.rint(pos * size).astype(int)
        for j in range(5):
            if needs[j, 4] >= 90 and not partnered[j]:
                d = [tile[k] - tile[j] for k in range(5) if k != j]
                mine_sight += all(int(v @ v) > r * r for v in d)
                mine_manh += all(int(np.abs(v).sum()) > r for v in d)
    assert mine_manh > 0 and (int(sight.sum()), int(manh.sum())) == (mine_sight, mine_manh) and hap.shape == need.shape == (600, 5), \
        f"the reader's lost cat-ticks differ from the count made here: {int(sight.sum())} / {int(manh.sum())} against {mine_sight} / {mine_manh}"


def t3():
    """§8's welfare half is the sign test at the level of 21 of 30."""
    def verdict(up, s1, sign=1.0):
        return RR.grammar(RR.paired(*rows([0.2 * sign] * up + [-0.2 * sign] * (30 - up))), s1)
    got = [verdict(21, True), verdict(20, True), verdict(20, False), verdict(21, True, -1.0), verdict(21, False)]
    assert got[:4] == ["PAYS", "TAIL ONLY", "LEVEL", "COSTS"] and got[4].startswith("OUTSIDE"), f"the grammar reads 21 / 20 of 30 as {got}"


def t4():
    """A leg file of another seating is refused."""
    try:
        RR.load("T", 100, BASE_100)
    except AssertionError:
        return
    raise AssertionError("the reader took the baseline's file as the rescue's")


def t5():
    """A leg file of another size is refused."""
    try:
        RR.load("base", 40, BASE_100)
    except AssertionError:
        return
    raise AssertionError("the reader took a 100x100 leg as a 40x40 one")


GUARDS = {"t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
