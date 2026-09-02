#!/usr/bin/env python3
"""Guards for score_refusal.py against a recorded /events/refusal payload.

fixtures/ring-sample-2026-09-02.json is the live ring as served at tick
1,295,652 on 2026-09-02 (261 rows, ticks 1,295,021..1,295,652, no
duplicate rows). The pins below were counted off the file with a
separate one-liner, not with the scorer.
"""

import json
from pathlib import Path

from score_refusal import proposal_label, score

HERE = Path(__file__).resolve().parent
EV = json.load(open(HERE / "fixtures/ring-sample-2026-09-02.json"))["events"]


def approx(a, b):
    return abs(a - b) < 1e-9


# Whole fixture, inclusive window of 632 ticks.
sc = score(EV, 1295021, 1295652, {2: "Biscuit"})
assert sc["window"]["ticks"] == 632, sc["window"]
assert sc["rows"] == 261 and sc["taxed_rows"] == 93 and sc["absorbed_rows"] == 168, sc
b = sc["seats"]["2"]
assert b["name"] == "Biscuit"
assert b["taxed"] == 45 and b["absorbed"] == 58, b
assert approx(b["taxed_share"], 45 / 632), b["taxed_share"]
assert sc["seats"]["1"]["taxed"] == 5 and sc["seats"]["5"]["absorbed"] == 30
assert b["taxed_by_action"] == {"play:kitty": 43, "eat": 1, "groom:kitty": 1}, b["taxed_by_action"]
assert approx(sc["combined_density"], 261 / 632)
assert sc["retention_floor_15k"] == 6195, sc["retention_floor_15k"]  # 6194.6 rounds up

# Duplicate rows (a ring row seen on two polls) count once.
sc2 = score(EV + EV[:50], 1295021, 1295652)
assert sc2["rows"] == 261 and sc2["seats"]["2"]["taxed"] == 45, sc2["rows"]

# Window clipping: rows past end_tick are dropped, denominator follows.
sc3 = score(EV, 1295021, 1295300)
assert sc3["window"]["ticks"] == 280 and sc3["rows"] == 125, sc3
assert sc3["seats"]["2"]["taxed"] == 21, sc3["seats"]["2"]

# Proposal labels: target kind for kitty/element targets, `with`, bare.
assert proposal_label({"action": "play", "target": "kitty", "id": 4}) == "play:kitty"
assert proposal_label({"action": "play", "target": "bug"}) == "play:bug"
assert proposal_label({"action": "groom", "with": 2}) == "groom:with"
assert proposal_label({"action": "sleep"}) == "sleep"
assert proposal_label({"action": "move", "direction": "n"}) == "move"

print("test_score_refusal: 9 pins ok")
