#!/usr/bin/env python3
"""Guard for detector.py on synthetic global-state arrays (prereg.md
§Guard). Pins derived by hand from W=200, D=200: a lock of length L
puts the trailing share over 0.5 from tick s+100 through s+L+98, a run
of L-1 ticks, so a 500-tick lock at s=100 fires at 100+100+199 = 399
with episode 499; a 150-tick lock never reaches D. Each pin shown red
in-run before commit.

Run: python3 test_collapse_detector.py
"""
import numpy as np

from detector import (ACTIVITIES, OFF_ACT, OFF_PFLAG, OFF_PIDX, PER_KITTY,
                      detect)

ROSTER, T = 3, 1200


def world():
    """Three idle, unpartnered cats; needs zero."""
    return np.zeros((T, ROSTER * PER_KITTY), np.float32)


def set_act(st, k, t0, t1, activity, partner=None):
    b = k * PER_KITTY
    st[t0:t1, b + OFF_ACT:b + OFF_ACT + 7] = 0
    st[t0:t1, b + OFF_ACT + ACTIVITIES.index(activity)] = 1
    if partner is not None:
        st[t0:t1, b + OFF_PFLAG] = 1
        st[t0:t1, b + OFF_PIDX] = partner / (ROSTER - 1)


def test_mutual_lock_fires_both_signals_at_the_predicted_tick():
    st = world()
    # Pair (1, 2), not (0, 1): index 0 encodes as 0.0 under any decode,
    # so only a nonzero pair pins the (roster-1) scaling.
    set_act(st, 1, 100, 600, "sleeping", partner=2)
    set_act(st, 2, 100, 600, "sleeping", partner=1)
    r = detect(st, ROSTER)
    assert r["verdict"] == "FIRE"
    a = [f for f in r["fires"] if f["signal"] == "a"]
    b = [f for f in r["fires"] if f["signal"] == "b"]
    # v0.2: (a)'s bar is 0.55, so the trailing share crosses it 0.05*W = 10
    # ticks later on the way in and 10 ticks earlier on the way out: first
    # fire 399 -> 409, episode 499 -> 479. (b) keeps v0's 0.50 numbers.
    assert [(f["seat"], f["family"], f["tick"], f["episode"]) for f in a] == \
        [("k1", "sleeping", 409, 479), ("k2", "sleeping", 409, 479)], a
    assert [(f["pair"], f["tick"], f["episode"]) for f in b] == [(["k1", "k2"], 399, 499)], b
    assert r["first_fire_tick"] == 399


def test_five_on_five_off_sits_at_the_bar_and_stays_silent():
    # Period 10 divides W=200, so every full window holds exactly 100
    # partnered ticks: share == 0.5 at every tick, never over the strict bar.
    st = world()
    for s in range(100, 1100, 10):
        set_act(st, 0, s, s + 5, "sleeping", partner=1)
        set_act(st, 1, s, s + 5, "sleeping", partner=0)
    r = detect(st, ROSTER)
    assert r["verdict"] == "silent", r["fires"]
    assert abs(r["max_share"]["a"] - 0.5) < 1e-9 and abs(r["max_share"]["b"] - 0.5) < 1e-9, r["max_share"]


def test_short_lock_stays_silent_under_d():
    st = world()
    set_act(st, 0, 100, 250, "sleeping", partner=1)
    set_act(st, 1, 100, 250, "sleeping", partner=0)
    r = detect(st, ROSTER)
    assert r["verdict"] == "silent", r["fires"]
    assert r["max_share"]["a"] > 0.7      # the lock was seen, just not sustained


def test_one_sided_partnering_fires_a_not_b():
    st = world()
    set_act(st, 2, 100, 600, "grooming", partner=0)     # k2 grooms k0; k0 never names k2
    r = detect(st, ROSTER)
    assert [f["signal"] for f in r["fires"]] == ["a"], r["fires"]
    assert r["fires"][0]["seat"] == "k2" and r["fires"][0]["family"] == "grooming"
    assert r["max_share"]["b"] == 0.0




def test_eleven_on_nine_off_one_sided_sits_at_the_v02_bar_and_stays_silent():
    # Period 20 divides W=200: k0 partnered on k1 for 11 of every 20 ticks,
    # k1 never reciprocates, so (a) == 0.55 exactly and (b) == 0.
    st = world()
    for s in range(100, 1100, 20):
        set_act(st, 0, s, s + 11, "sleeping", partner=1)
    r = detect(st, ROSTER)
    assert r["verdict"] == "silent", r["fires"]
    assert abs(r["max_share"]["a"] - 0.55) < 1e-9 and r["max_share"]["b"] == 0.0, r["max_share"]


def test_fifty_three_percent_one_sided_partnering_is_silent_under_v02():
    # 53-on/47-off (period 100 divides W), one-sided: (a) == 0.53 for the
    # whole run. Fired under v0's 0.50 bar (a healthy-Biscuit false
    # positive); silent under 0.55.
    st = world()
    for s in range(100, 1100, 100):
        set_act(st, 0, s, s + 53, "sleeping", partner=1)
    r = detect(st, ROSTER)
    assert r["verdict"] == "silent", r["fires"]
    assert abs(r["max_share"]["a"] - 0.53) < 1e-9, r["max_share"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
