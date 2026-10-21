#!/usr/bin/env python3
"""Guards for the Gen 2 seating-analysis port (plain asserts, lab venv).

The collector is held EQUAL to the certified harness (cert_harness_fog
run_one, the battery's own loop) on the same world: any stride, loop or
observation-tampering error shows as a different world. (Group holding
moved to the certification harness on the owner's word, 2026-10-21; its
guards live in gen2-cert-battery-2026-10-20/test_g2_battery.py.)
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
_cache, _streams = {}, {}


def _collect(seating):
    if seating not in _streams:
        _streams[seating] = C.collect(seating, SEED, TICKS, 1000)
    return _streams[seating]


def _pair(seating):
    if seating not in _cache:
        arrays, meta = _collect(seating)
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


def test_applied_stream_carries_every_relief_tick():
    # red: the applied action written one row off. A tick that lowered a
    # cat's eat (drink) need is a tick the cat applied eat (drink): only
    # those effects lower it. Both windows hold relief ticks the
    # end-of-tick flag hides, so a flag-derived stream fails too.
    for seating in ("g2-s1", "scripted"):
        arrays, meta = _collect(seating)
        names, ap = meta["applied_names"], arrays["applied"]
        for need, name, code in ((0, "eat", 3), (1, "drink", 4)):
            drop = np.zeros(ap.shape, bool)
            drop[1:] = np.diff(arrays["needs"][:, :, need], axis=0) < -1e-3
            assert (drop & (arrays["activity"] != code)).any(), (seating, name)
            got = {names[x] for x in ap[drop]}
            assert got == {name}, (seating, name, got)


def test_applied_partner_matches_the_flag_inside_a_scene():
    # red: a partner decoded from the wrong field (groom's target). Where
    # the end-of-tick flag names a partner and the cat's applied action
    # carries that scene, the applied action names the same partner. (A
    # cat invited into a duet after its own turn applied something else;
    # g2-s1 has two such ticks here.)
    carries = {"rest": 1, "sleep": 2, "eat": 3, "drink": 4, "play": 5, "groom": 6}
    for seating in ("g2-s1", "scripted"):
        arrays, meta = _collect(seating)
        names = meta["applied_names"]
        fp, aw, flag = arrays["partner"], arrays["applied_with"], arrays["activity"]
        same = np.vectorize(lambda x: carries.get(names[x], 0))(arrays["applied"]) == flag
        m = (fp[:, :, 0] == 1) & same
        assert m.sum() > 0 and (flag[m] == 6).any(), seating
        assert (aw[m] == fp[:, :, 1][m]).all(), seating


def test_collector_records_every_element_on_a_bigger_world():
    # red: a fixed 64-slot element table (40x40 carries 92 elements)
    import cloudkitty
    cfg = EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-40.toml"
    arrays, _meta = C.collect("scripted", SEED, 5, None, config=cfg)
    env = cloudkitty.ParallelEnv(str(cfg), control={f"kitty_{i}": "teacher" for i in range(1, 6)}, horizon=5)
    env.reset(seed=SEED)
    for t in range(5):
        env.step({})
        assert (arrays["elements"][t, :, 0] >= 0).sum() == len(env.elements()) > 64


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
