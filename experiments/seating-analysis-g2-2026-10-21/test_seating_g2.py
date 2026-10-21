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


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
