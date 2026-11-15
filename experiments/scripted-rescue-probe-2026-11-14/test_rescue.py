#!/usr/bin/env python3
"""Guards s1–s6 of DECLARATION.md §9 (deviations entry 39); each red on record via scripts/mutate.sh --expect before a
leg runs. Two kinds of world:
  - BUILT states (s2's assignment, s5): a v2 global-state vector written here, handed to the rule; no engine, no mind.
  - one RECORDED world moment (s1, s2's mission, s3, s4, s6): g2cmp 905002 at 100×100, where the no-head final's
    recorded leg has its first lost cat at tick 129 (cat 4, a 22-tile walk from cat 1). The harness runs the first
    260 ticks under each overlay into a scratch directory (five copies of the no-head final decide: 1,300 covered
    cat-ticks a run) and the test reads the run back by replaying its recorded acts.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_rescue.py [s1 s2 ...]      (A = ../minifriend-phase2-2026-11-06)
"""
import functools
import os
import sys
import tempfile
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rescue as RS  # noqa: E402
C, RP, L = RS.C, RS.RP, RS.L
import cert_harness_fog as H  # noqa: E402  (p2_common put the harness on the path)

SIZE, SEED, TICKS = 100, 905002, 260
CFG = tomllib.loads(Path(C.LEG_TOML[SIZE]).read_text())
RADIUS = CFG["vision"]["radius"]
BASELINE = C.RAW / "legs" / "p2u-nohead-s1" / "legs" / f"size{SIZE}" / "acts" / f"acts-{SEED}.npz"
SCRATCH = Path(os.environ.get("RESCUE_SCRATCH", "/tmp/rescue-scratch"))
R = C.ROSTER


@functools.lru_cache(None)
def run(seating):
    """One harness run of `seating` on the recorded world: (the row, the acts file's arrays, the replayed ticks)."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=f"{seating}-", dir=SCRATCH))
    row = H.run_one((seating, SEED, TICKS, str(C.LEG_TOML[SIZE]), None, None, "served", None, None, None, str(out)))
    z = dict(np.load(out / f"acts-{SEED}.npz"))
    return row, z, list(RP.replay(out / f"acts-{SEED}.npz", C.LEG_TOML[SIZE], want_obs=True))


def facts(rec):
    """(needs x100, happiness x100, tile, partnered) at the start of a replayed tick, read here and not by the rule."""
    needs, hap, pos, _a, partnered, _p, _d = rec["pre"]
    return needs, hap, np.rint(pos * SIZE).astype(int), partnered


def walk(a, b):
    return int(np.abs(np.asarray(a) - np.asarray(b)).sum())


def applied(rec, k):
    v = rec["recs"][rec["names"][k]]
    return v["proposed_action_name"] == v["applied_action_name"]


def built(cats):
    """A v2 global-state vector for five cats: each (tile, {need: level}, partnered); happiness 80 unless given."""
    st = np.zeros((R, RP.PK), np.float32)
    for k, (tile, needs, partnered) in enumerate(cats):
        st[k, RP.POS0:RP.POS0 + 2] = np.asarray(tile) / SIZE
        st[k, RP.HAP] = needs.get("happiness", 80) / 100
        for n, v in needs.items():
            if n != "happiness":
                st[k, L.NEED_KINDS.index(n)] = v / 100
        st[k, RP.PARTNER_PRESENT] = float(partnered)
    return st.reshape(-1)


def moves_only():
    mk = np.zeros((R, 51), bool)
    mk[:, RS.MOVES] = True
    return mk


LOST_WORLD = [((10, 10), {"cuddle": 95}, False),      # lost: alone, cuddle 95
              ((40, 10), {}, False),                  # free, a 30-tile walk
              ((10, 60), {}, False),                  # free, a 50-tile walk
              ((50, 50), {"eat": 80}, False),         # not free: hungry
              ((60, 60), {}, True)]                   # not free: partnered
IDLE = np.full(R, RS.MENU.index("idle"))


def s1():
    """With no overlay the harness reproduces the recorded baseline world's acts tick for tick; so does an overlay
    seating until its first mission opens."""
    base = np.load(BASELINE)["acts"][:TICKS]
    _row, z, _ = run("p2u-nohead-s1")
    d = np.nonzero((z["acts"] != base).any((1, 2)))[0]
    assert not len(d), f"the bare harness differs from the recorded leg (seating p2u-nohead-s1, first at tick {d[0]})"
    row, z, _ = run("rescue-T")
    opened = [m["open"] for m in row["overlay"]["missions"]]
    t0 = min(opened, default=TICKS)
    d = np.nonzero((z["acts"][:t0] != base[:t0]).any((1, 2)))[0]
    assert not len(d), f"the bare harness differs from the recorded leg (overlay T with no mission open, first at tick {d[0]}; its first mission opens at {t0})"
    assert 0 < t0 < TICKS, f"no mission opened inside the window: {opened}"


def s2():
    """T assigns the nearest free cat; every mission move shortens the walk; the partner act is taken when legal; the
    mission ends on release."""
    ov = RS.Overlay("T", SIZE, SIZE, RADIUS, 4)
    out = ov.act(built(LOST_WORLD), None, moves_only(), IDLE)
    got = {k: m["target"] for k, m in ov.open.items()}
    assert got == {1: 0}, f"the rescuer is not the nearest free cat (built world: missions {got}, the 30-tile cat is seat 1)"
    assert RS.MENU[out[1]] == "move_west" and (np.delete(out, 1) == np.delete(IDLE, 1)).all(), [RS.MENU[a] for a in out]

    row, z, ticks = run("rescue-T")
    m = row["overlay"]["missions"][0]
    k, j, t0, t1 = m["rescuer"], m["target"], m["open"], m["close"]
    needs, hap, tile, partnered = facts(ticks[t0])
    free = [c for c in range(R) if c != j and not partnered[c] and needs[c, :5].max() < 70 and hap[c] >= 70]
    assert len(free) >= 2, f"the recorded moment has {len(free)} free cats: the nearest-cat line would be vacuous"
    nearest = min(free, key=lambda c: (walk(tile[c], tile[j]), c))
    assert k == nearest, f"the rescuer is not the nearest free cat (tick {t0}: seat {k} sent, seat {nearest} is nearest of {free})"
    assert t1 is not None and z["rule_set"][t0:t1, k].sum() >= 5, f"the mission never closed or set too few acts: {m}"
    row_j = RS.friend_row(k, j)
    released = lambda f: bool(f[3][j] or f[0][j, RS.CUD] < 50 or f[0][k, :5].max() >= 90)   # noqa: E731
    for t in range(t0, t1):
        needs, hap, tile, partnered = f = facts(ticks[t])
        assert not released(f), f"the mission did not end on its release (a release line held at tick {t}, it closed at {t1})"
        act, mk = int(z["acts"][t, k, 0]), ticks[t]["mask"][k]
        legal = [a[row_j] for a in RS.PARTNER if mk[a[row_j]]]
        if legal:
            assert z["rule_set"][t, k] and act == legal[0], f"a legal partner act was not taken at tick {t}: {RS.MENU[act]}"
        elif z["rule_set"][t, k]:
            after = np.rint(ticks[t]["post"][2][k] * SIZE).astype(int)
            assert act in RS.MOVES and (not applied(ticks[t], k) or walk(after, tile[j]) == walk(tile[k], tile[j]) - 1), \
                f"a mission move did not shorten the walk at tick {t}: {RS.MENU[act]}"
    assert released(facts(ticks[t1])), f"the mission did not end on its release (none held at its close, tick {t1})"


def s3():
    """Every overridden act is legal by the tick's mask, and the message half is the policy's."""
    _row, z, ticks = run("rescue-T")
    set_ = np.argwhere(z["rule_set"])
    assert len(set_) >= 5, len(set_)
    for t, k in set_:
        assert ticks[t]["mask"][k, z["acts"][t, k, 0]], f"an overridden act is illegal (tick {t}, seat {k}: {RS.MENU[z['acts'][t, k, 0]]})"
    fwd = H.load_model(H.SEATINGS["rescue-T"][0])
    spoke = 0
    for t, rec in enumerate(ticks):
        lg = np.asarray(fwd(rec["obs"], rec["mask"]), np.float32)
        own = np.where(rec["mask"][:, 35:], lg[:, 35:], -np.inf).argmax(1)
        assert (own == z["acts"][t, :, 1]).all(), f"the message half is not the policy's (tick {t}: sent {z['acts'][t, :, 1].tolist()}, the policy's {own.tolist()})"
        spoke += int((own > 0).sum())
    assert spoke > 0, "the policy never spoke in the window: the message line would be vacuous"


def s4():
    """On one stream of states P opens and closes its missions on the ticks T does; in its own run it takes no partner
    act and every act the rule sets walks away from the lost cat."""
    _rowT, zT, ticks = run("rescue-T")
    logs = {}
    for kind in ("T", "P"):
        ov = RS.Overlay(kind, SIZE, SIZE, RADIUS, TICKS)
        for t, rec in enumerate(ticks):
            ov.act(rec["state"], rec["obs"], rec["mask"], zT["policy_acts"][t])
        logs[kind] = [(m["rescuer"], m["target"], m["open"], m["close"], m["why"]) for m in ov.report()["missions"]]
    assert logs["T"] and logs["P"] == logs["T"], f"the placebo's missions differ from the rescue's on one stream: {logs}"

    row, z, ticks = run("rescue-P")
    m = row["overlay"]["missions"][0]
    k, j, t0 = m["rescuer"], m["target"], m["open"]
    assert (k, j, t0) == logs["T"][0][:3], f"the placebo's first mission differs from the rescue's: {m} vs {logs['T'][0]}"
    lost_at = facts(ticks[t0])[2][j]
    t1 = m["close"] if m["close"] is not None else TICKS
    moved = 0
    for t in range(t0, t1):
        if not z["rule_set"][t, k]:
            continue
        act = int(z["acts"][t, k, 0])
        before, after = facts(ticks[t])[2][k], np.rint(ticks[t]["post"][2][k] * SIZE).astype(int)
        away = act in RS.MOVES and walk(after, lost_at) >= walk(before, lost_at) and (not applied(ticks[t], k) or walk(after, lost_at) == walk(before, lost_at) + 1)
        assert away, f"the placebo walked to the lost cat (tick {t}: {RS.MENU[act]}, walk {walk(before, lost_at)} -> {walk(after, lost_at)})"
        moved += applied(ticks[t], k)
    assert moved >= 5, f"the placebo's rescuer made {moved} moves: the walk line would be vacuous"


def s5():
    """A rescuer whose own hidden need reaches 90 is released that tick."""
    ov = RS.Overlay("T", SIZE, SIZE, RADIUS, 4)
    ov.act(built(LOST_WORLD), None, moves_only(), IDLE)
    assert list(ov.open) == [1], ov.open
    hungry = [c if i != 1 else (c[0], {"eat": 92}, False) for i, c in enumerate(LOST_WORLD)]
    out = ov.act(built(hungry), None, moves_only(), IDLE)
    closed = [m for m in ov.missions if m["rescuer"] == 1]
    assert 1 not in ov.open and closed and closed[0]["why"] == "rescuer_need" and out[1] == IDLE[1] and not ov.rule[1, 1], \
        f"a rescuer in distress stayed on its mission (open {ov.open}, closed {ov.missions})"


def s6():
    """O reads the observation only: the harness withholds the engine's state from it (the rule refuses one), and the
    place it walks to is the one its own row carries."""
    row, _z, ticks = run("rescue-O")                      # the rule raises if the harness hands it the state
    missions = row["overlay"]["missions"]
    assert missions and row["overlay"]["kind"] == "O", missions
    for m in missions:
        k, j, t0 = m["rescuer"], m["target"], m["open"]
        o = ticks[t0]["obs"][k][L.BLOCKS[RS.friend_row(k, j)][0]:][:L.KITTY_W]
        assert o[L.ROW_PRESENT] <= 0.5 and o[L.ROW_INTENSITY + L.WANT_KINDS.index("want_cuddle")] >= np.float32(0.9), f"mission {m} opened on a row that is not calling"
        place = np.rint(o[1:3] * np.expm1(o[4] * np.log1p(400.0))).astype(int).tolist()
        assert m["place"] == place, f"the observation rule's call place is not the row's (tick {t0}, seat {k}: {m['place']} against the row's {place})"
    ov = RS.Overlay("O", SIZE, SIZE, RADIUS, 2)
    try:
        ov.act(ticks[0]["state"], ticks[0]["obs"], ticks[0]["mask"], IDLE)
    except AssertionError:
        return
    raise AssertionError("the observation rule took the engine state without refusing")


GUARDS = {"s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s6": s6}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
