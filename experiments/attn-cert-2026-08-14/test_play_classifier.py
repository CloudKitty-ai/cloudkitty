"""F-029 guard: the census play classifier must separate element play
from kitty duets on the ACTIVITY shape. Run with OLD=1 to see it red
(the shipped-until-2026-08-22 rule), unset for the fixed rule.
"""
import os
from collections import Counter, defaultdict

OLD = os.environ.get("OLD") == "1"
EL_KIND = {11449: "bug", 900: "greeble"}

EVENTS = [  # (kitty, activity)
    (2, {"state": "playing", "target": {"target": "element", "id": 11449}}),
    (2, {"state": "playing", "target": {"target": "element", "id": 11449}}),
    (2, {"state": "playing", "target": {"target": "element", "id": 900}}),
    (2, {"state": "playing", "target": {"target": "element", "id": 77}}),
    (2, {"state": "playing", "target": {"target": "kitty", "id": 3}}),
    (2, {"state": "playing"}),
]
EXPECT = {"bug": 2, "greeble": 1, "element(expired)": 1, "kitty": 1,
          "solo": 1}

play = defaultdict(Counter)
for kid, act in EVENTS:
    tgt = act.get("target")
    if OLD:
        if act.get("id") is not None:
            play[kid][str(tgt)] += 1
        elif tgt is not None:
            play[kid]["kitty"] += 1
        else:
            play[kid]["solo"] += 1
    else:
        if isinstance(tgt, dict) and tgt.get("target") == "element":
            play[kid][EL_KIND.get(tgt.get("id"), "element(expired)")] += 1
        elif isinstance(tgt, dict) and tgt.get("target") == "kitty":
            play[kid]["kitty"] += 1
        elif tgt is None:
            play[kid]["solo"] += 1
        else:
            play[kid][f"unknown:{tgt}"] += 1

got = dict(play[2])
print(("OLD" if OLD else "FIXED"), "->", got)
assert got == EXPECT, f"expected {EXPECT}, got {got}"
print("classifier OK")
