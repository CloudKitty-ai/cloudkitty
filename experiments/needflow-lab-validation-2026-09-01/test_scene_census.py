#!/usr/bin/env python3
"""Guard for scene_census.py, on a RECORDED /events/activity payload
(fixtures/events-activity-canon-20260901-boot.json: canon arm, seed
20260901, ticks 0–1265 of a fresh lab boot, 768 events). Every pin below
was derived independently of the module (plain comprehensions over the
JSON, 2026-09-01) and each was shown red in-run before this file was
committed — see prereg.md §Guard.

Run: python3 test_scene_census.py
"""
import json
from pathlib import Path

from scene_census import classify, span, summarize

HERE = Path(__file__).resolve().parent
EV = json.loads((HERE / "fixtures/events-activity-canon-20260901-boot.json").read_text())
assert len(EV) == 768, len(EV)


def test_partnered_rest_reads_tiers_not_end_state():
    # 183 resting events; only 101 still name a friend at the END, yet
    # every one of them counted at least one tier tick — the partner
    # wandered off before the scene closed (action.rs Resting arm drops
    # with_friend to None, clock untouched). End-state alone under-counts
    # rest by 45%.
    resting = [e for e in EV if e["activity"]["state"] == "resting"]
    assert len(resting) == 183
    assert sum(1 for e in resting if "with_friend" in e["activity"]) == 101
    assert sum(1 for e in resting if classify(e) == "rest") == 183
    assert sum(1 for e in resting if classify(e) == "rest-solo") == 0


def test_sleep_classes_and_the_rest_of_the_map():
    c = {}
    for e in EV:
        c[classify(e)] = c.get(classify(e), 0) + 1
    assert c["cosleep"] == 19 and c["sleep-solo"] == 81, c
    assert c["groom-self"] == 121 and c["groom-other"] == 6, c
    assert c["play-duet"] == 100 and c["play-elem"] == 48, c
    assert c.get("play-solo", 0) == 0, c
    assert c["eat"] == 108 and c["drink"] == 102, c
    assert not [k for k in c if k.startswith("other:")], c


def test_span_is_inclusive():
    # Config windows: groom-solo min 4, duet 2 (F-031's validation set).
    e = next(e for e in EV if e["started"] == 13 and e["kitty_id"] == 5)
    assert (e["started"], e["ended"]) == (13, 18) and span(e) == 6
    s = summarize(EV, [], 0, 1265, 5)
    assert s["mean_span"]["groom-self"] == 4.0, s["mean_span"]
    assert s["mean_span"]["play-duet"] == 2.0, s["mean_span"]


def test_window_filter_uses_ended_and_the_per_1k_math():
    s = summarize(EV, [], 0, 1265, 5)
    assert s["cat_ticks"] == 1266 * 5 and s["events_in_window"] == 768
    assert abs(s["per_1k_cat_ticks"]["rest"] - 1000 * 183 / 6330) < 1e-9
    assert s["rest_tiers"] == {"mutual_emitting": 96, "drip_emitting": 136,
                               "rest_events": 183}
    assert s["cosleep_to_solo"] == 19 / 81
    # The rest scene 13..18 straddles t1 = 17: a started-based filter
    # would count it (1), the ended-based one must not (0).
    assert summarize(EV, [], 0, 17, 5)["counts"].get("rest", 0) == 0
    assert summarize(EV, [], 0, 18, 5)["counts"].get("rest", 0) == 1


def test_polls_feed_time_means():
    polls = [{"tick": 5, "kitties": [{"needs": {n: 10.0 for n in
              ("eat", "drink", "sleep", "play", "cuddle", "bath")}, "happiness": 90.0}]},
             {"tick": 9999, "kitties": [{"needs": {n: 99.0 for n in
              ("eat", "drink", "sleep", "play", "cuddle", "bath")}, "happiness": 0.0}]}]
    s = summarize(EV, polls, 0, 1265, 5)
    assert s["polls_in_window"] == 1 and s["happiness_mean"] == 90.0
    assert s["need_means"]["cuddle"] == 10.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
