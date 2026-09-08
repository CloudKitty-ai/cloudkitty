#!/usr/bin/env python3
"""Guard for floor_screen.py (plain asserts, no pytest).

    test_floor_screen.py

Synthetic snapshots with recent_meows shaped like the recorded trace
payloads (intensity/kind/kitty_id/pos/reply/tick) exercise: window
deduplication, the heard (listener-floor) cut, informativeness,
reply attribution (matching kind, reply=true, other kitty, strictly
inside the window), ambient vs reply here-words, per-kind blocks, the
welfare pass-through, and read_rollout's wiring plus its --trace
refusal.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import floor_screen as fs  # noqa: E402

FLOOR, WINDOW = 0.15, 10
N = 20  # snapshots; per-1k factor 50


def meow(kitty_id, kind, tick, intensity=0.0, reply=False):
    return {"intensity": intensity, "kind": kind, "kitty_id": kitty_id,
            "pos": {"x": 0, "y": 0}, "reply": reply, "tick": tick}


MEOWS = [
    meow(1, "want_eat", 2, 0.60),          # A: heard, informative, answered
    meow(2, "here_food", 5, reply=True),   # answers A
    meow(1, "want_drink", 3, 0.20),        # B: heard, not informative
    meow(1, "here_water", 6, reply=True),  # same kitty: no answer
    meow(2, "here_water", 7),              # ambient: no answer
    meow(2, "here_water", 13, reply=True),  # dt=10, outside window: no answer
    meow(2, "want_sleep", 4, 0.10),        # C: under the floor
    meow(1, "want_cuddle", 6, 0.80),       # D: heard, no here-word kind
    meow(2, "want_play", 8, 0.55),         # E: heard, answered
    meow(1, "here_critter", 9, reply=True),  # answers E
]


def snapshots():
    for t in range(N):
        eat = 95.0 if t < 5 else 10.0  # one 5-tick episode, one crossing
        yield {
            "kitties": [
                {"id": 1, "pos": {"x": 0, "y": 0},
                 "needs": {"eat": eat, "drink": 0.0}, "memory": [None] * 5},
                {"id": 2, "pos": {"x": 10, "y": 10},
                 "needs": {"eat": 0.0, "drink": 0.0}, "memory": [None] * 5},
            ],
            "elements": [],
            # a meow persists in recent_meows for the audible window
            "recent_meows": [m for m in MEOWS if m["tick"] <= t < m["tick"] + WINDOW],
        }


tap = fs.CommsTap(snapshots())
welfare = fs.screen(iter(tap), 3, 90, 75, 15)
c = fs.comms(tap, FLOOR, WINDOW, welfare["ticks"])

assert welfare["ticks"] == N, "tap: every snapshot passed through"
assert welfare["distress_episodes_per_1k"] == 50.0, \
    "welfare through the tap: one episode"
assert welfare["safeguard_crossings_per_1k"]["eat"] == 50.0, \
    "welfare through the tap: one crossing"
assert c["wants_per_1k"] == 250.0, \
    f"wants deduplicated across window persistence, got {c['wants_per_1k']}"
assert c["heard_share"] == 0.8, f"heard: 4 of 5 at the floor, got {c['heard_share']}"
assert c["informative_heard"] == 0.75, \
    f"informativeness: 3 of 4 heard at 0.5, got {c['informative_heard']}"
assert c["answerable_heard"] == 3, \
    f"answerable: eat, drink, play heard, got {c['answerable_heard']}"
assert abs(c["reply_rate"] - 2 / 3) < 1e-12, \
    f"reply: A and E answered, B is not (same kitty / ambient / window edge), got {c['reply_rate']}"
assert c["here_reply_per_1k"] == 200.0, f"here replies: 4, got {c['here_reply_per_1k']}"
assert c["here_ambient_per_1k"] == 50.0, f"here ambient: 1, got {c['here_ambient_per_1k']}"
k = c["want_kinds"]
assert k["want_eat"] == {"per_1k": 50.0, "heard_share": 1.0,
                         "informative_heard": 1.0}, "per-kind block: want_eat"
assert k["want_drink"]["informative_heard"] == 0.0, "per-kind: drink not informative"
assert k["want_sleep"]["heard_share"] == 0.0, "per-kind: sleep under the floor"

# --- read_rollout wiring and the --trace refusal ---------------------------
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    cfg = td / "cfg.toml"
    cfg.write_text("[thresholds]\ndistress = 90\nsafeguard = 75\n"
                   "[meow]\nannounce_threshold = 15\nrecent_window_ticks = 10\n"
                   "[behavior]\nreply_intensity_floor = 0.15\n")
    roll = td / "roll"
    roll.mkdir()
    with open(roll / "trace.jsonl", "w") as f:
        for t, s in enumerate(snapshots()):
            f.write(json.dumps({"tick": t, "snapshot": s}) + "\n")
    meta = {"trace": True, "vision_radius": 4, "world_seed": 5,
            "config": str(cfg), "config_sha256": "x"}
    (roll / "meta.json").write_text(json.dumps(meta))
    res = fs.read_rollout(roll)
    assert res["floor"] == 15 and res["ticks"] == N, "read_rollout: trace read"
    assert res["comms"]["listener_floor"] == 0.15, "read_rollout: floor from config"
    assert abs(res["comms"]["reply_rate"] - 2 / 3) < 1e-12, \
        "read_rollout: comms carried through"
    (roll / "meta.json").write_text(json.dumps({**meta, "trace": False}))
    try:
        fs.read_rollout(roll)
        raise SystemExit("read_rollout: a traceless rollout must be refused")
    except AssertionError:
        pass

print("test_floor_screen: PASS")
