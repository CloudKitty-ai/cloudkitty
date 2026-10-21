#!/usr/bin/env python3
"""Guards for the Gen 2 seating-analysis port (plain asserts, lab venv).

The collector is held EQUAL to the certified harness (cert_harness_fog
run_one, the battery's own loop) on the same world: any stride, loop or
observation-tampering error shows as a different world. Group holding
is checked on a recorded payload (the s2 905008 replay trace: normal
grouping before the lock, the lock after) and its tending exclusion on
analytic literals, as v1 checks its math helpers.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import seating_collect_g2 as C  # noqa: E402
import seating_read_g2 as R  # noqa: E402

SEED, TICKS = 905001, 300
TRACE = EXPTS / "gen2-cert-battery-2026-10-20" / "diag-s2-905008.npz"
_cache = {}


def _pair(seating):
    if seating not in _cache:
        arrays, meta = C.collect(seating, SEED, TICKS, 1000)
        ref = H.run_one((seating, SEED, TICKS, str(C.CONFIG), None, None,
                         "served", None, None, 1000))
        _cache[seating] = (arrays, meta, ref)
    return _cache[seating]


def _assert_same_world(arrays, ref):
    hap = arrays["hap"].astype(np.float64).mean(0)
    assert np.allclose(hap, ref["mean_happiness"], atol=1e-3), \
        (hap.round(4).tolist(), ref["mean_happiness"])
    eat = (arrays["activity"] == 3).sum(0).tolist()
    drink = (arrays["activity"] == 4).sum(0).tolist()
    assert (eat, drink) == (ref["needs"]["eat_ticks"], ref["needs"]["drink_ticks"]), \
        (eat, drink, ref["needs"]["eat_ticks"], ref["needs"]["drink_ticks"])


def test_collector_matches_the_certified_harness_policy_roster():
    # red: v1's stride (32) or any observation tampering (a clock write)
    arrays, meta, ref = _pair("g2-s1")
    _assert_same_world(arrays, ref)
    for k in range(5):
        got = np.bincount(arrays["msg"][:, k], minlength=16).tolist()
        assert got == ref["msg"][f"kitty_{k + 1}"], (k, got, ref["msg"][f"kitty_{k + 1}"])


def test_collector_matches_the_certified_harness_scripted_roster():
    arrays, meta, ref = _pair("scripted")
    _assert_same_world(arrays, ref)
    assert meta["speech_recorded"] == [False] * 5 and (arrays["act"] == -1).all()


def test_rotation_is_a_latin_square_over_the_five_networks():
    nets = {f"g2:trunk-{n}" for n in ("s1", "s2", "s4", "s6", "s7")}
    rots = [H.SEATINGS[f"g2-rot{r}"] for r in range(1, 6)]
    for r in rots:
        assert set(r) == nets, r
    for k in range(5):
        assert {r[k] for r in rots} == nets, ("seat", k, [r[k] for r in rots])


def test_play_share_counts_partner_play_proposals_only():
    # red: the proposal set widened past PlayKitty (solo or critter play)
    arrays, _meta, _ref = _pair("g2-s1")
    ref = [float(np.mean([R.ACTION_NAMES[x].startswith("PlayKitty")
                          for x in arrays["act"][:, k]])) for k in range(5)]
    assert R.play_share(arrays["act"]) == ref, (R.play_share(arrays["act"]), ref)
    assert max(ref) > 0
    assert R.play_share(_pair("scripted")[0]["act"]) == [None] * 5


def test_group_holding_separates_normal_grouping_from_the_s2_lock():
    # red: holding without the need condition reads normal grouping as held
    z = np.load(TRACE)
    t, pos, needs, act = z["tick"], z["pos"].astype(np.int16), z["needs"] * 100.0, z["act_state"]
    normal, lock = t < 17400, t >= 17950
    hn = R.group_holding(pos[normal], needs[normal], act[normal])
    hl = R.group_holding(pos[lock], needs[lock], act[lock])
    assert np.mean(hn["group3_share"]) > 0.15, hn["group3_share"]   # grouping happened
    assert max(hn["held_share"]) == 0.0, hn["held_share"]           # and was never held
    assert min(hl["held_share"]) > 0.8, hl["held_share"]
    assert hl["shared_hold_longest"] >= 100, hl["shared_hold_longest"]


def test_group_holding_does_not_count_a_cat_that_is_eating():
    # red: the tending exclusion dropped (analytic literals: three cats on
    # adjacent tiles, cat 0 at eat 90; eating -> not held, idle -> held)
    pos = np.array([[[5, 5], [5, 6], [6, 6], [15, 15], [0, 0]]] * 2, np.int16)
    needs = np.zeros((2, 5, 6), np.float32)
    needs[:, 0, 0] = 90.0
    act = np.zeros((2, 5), np.int8)
    act[0, 0] = 3          # tick 0: Eat
    h = R.group_holding(pos, needs, act)
    assert h["group3_share"][:3] == [1.0, 1.0, 1.0] and h["group3_share"][3] == 0.0
    assert h["held_share"][0] == 0.5, h["held_share"]                # idle tick only


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
