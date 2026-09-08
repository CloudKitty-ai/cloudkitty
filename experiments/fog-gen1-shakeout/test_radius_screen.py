#!/usr/bin/env python3
"""Guard for radius_screen.py (plain asserts, no pytest).

    test_radius_screen.py

Synthetic snapshots exercise every measure: distress episodes and the
watchdog cut (including a run still open at trace end), safeguard upward
crossings (a crossing, not a tick count), need maxima, blind-hungry /
blind-thirsty flags against memory, stocking and the disc, span
bookkeeping, friend-in-view, dispersion pass-through, per-1k scaling,
and read_rollout's meta wiring plus its --trace refusal.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import radius_screen as rs  # noqa: E402

DISTRESS, SAFEGUARD, ANNOUNCE = 90, 75, 30


def kitty(kid, x, y, eat=0.0, drink=0.0, memory=None):
    return {"id": kid, "pos": {"x": x, "y": y},
            "needs": {"eat": eat, "drink": drink},
            "memory": memory if memory is not None else [None] * 5}


def snap(kitties, elements=()):
    return {"kitties": kitties, "elements": list(elements)}


# --- spans -----------------------------------------------------------------
assert rs.spans([True, True, False, True]) == [2, 1], "spans: run splitting"
assert rs.spans([]) == [], "spans: empty"
assert rs.spans([False, False]) == [], "spans: all false"
assert rs.spans([True]) == [1], "spans: trailing open run flushed"

# --- blind() against memory, stocking and the disc -------------------------
me = kitty("a", 0, 0, eat=50)
chow_near = {"kind": "chow", "pos": {"x": 2, "y": 0}, "servings": 2}
chow_empty = {"kind": "chow", "pos": {"x": 2, "y": 0}, "servings": 0}
chow_far = {"kind": "chow", "pos": {"x": 5, "y": 0}, "servings": 2}
water_near = {"kind": "water", "pos": {"x": 2, "y": 0}}
water_far = {"kind": "water", "pos": {"x": 5, "y": 0}}
assert not rs.blind(me, snap([me], [chow_near]), 3, "chow"), \
    "blind: stocked chow in the disc is not blind"
assert rs.blind(me, snap([me], [chow_empty]), 3, "chow"), \
    "blind: unstocked chow does not count"
assert rs.blind(me, snap([me], [chow_far]), 3, "chow"), \
    "blind: chow outside the disc does not count"
remembers = kitty("a", 0, 0, eat=50)
remembers["memory"][rs.ELEMENT_KINDS.index("chow")] = \
    {"last_seen": 1, "pos": {"x": 9, "y": 9}}
assert not rs.blind(remembers, snap([remembers]), 3, "chow"), \
    "blind: a chow memory clears blindness"
assert not rs.blind(me, snap([me], [water_near]), 3, "water"), \
    "blind: water in the disc is not blind"
assert rs.blind(me, snap([me], [water_far]), 3, "water"), \
    "blind: water outside the disc does not count"

# --- screen(): episodes, watchdog, safeguard, blind spans, scaling ---------
# Kitty "a" runs eat through three high blocks; "b" idles far away so
# nn_stats has pairs but nothing else fires.
#   ticks   0-159  eat 95   (160 ticks: watchdog-length episode)
#   ticks 160-169  eat 10
#   ticks 170-172  eat 95   (3 ticks: short episode)
#   ticks 173-194  eat 10
#   ticks 195-199  eat 95   (5 ticks: still open at trace end)
eat_by_tick = [95.0] * 160 + [10.0] * 10 + [95.0] * 3 + [10.0] * 22 + [95.0] * 5
assert len(eat_by_tick) == 200
snaps = [snap([kitty("a", 0, 0, eat=e), kitty("b", 10, 10)])
         for e in eat_by_tick]
out = rs.screen(iter(snaps), 3, DISTRESS, SAFEGUARD, ANNOUNCE)
assert out["ticks"] == 200 and out["radius"] == 3, "screen: header fields"
assert out["watchdog_entries"] == 1, \
    f"watchdog: exactly the 160-tick episode, got {out['watchdog_entries']}"
assert out["watchdog_entries_per_1k"] == 5.0, "watchdog per-1k scaling"
assert out["distress_episodes_per_1k"] == 15.0, \
    f"episodes: three including the open run, got {out['distress_episodes_per_1k']}"
assert out["max_distress_age"] == 160, "episodes: max age"
assert out["need_max"] == {"drink": 0.0, "eat": 95.0}, "need maxima"
assert out["safeguard_crossings_per_1k"] == {"drink": 0.0, "eat": 15.0}, \
    f"safeguard: three upward crossings only, got {out['safeguard_crossings_per_1k']}"
assert out["friend_in_view_share"] == 0.0, "friend: nobody inside r=3"
b = out["blind_eat"]
assert b["spans"] == 3 and b["span_max"] == 160, \
    f"blind-eat spans mirror the high blocks, got {b}"
assert b["cat_ticks_per_1k"] == 840.0, \
    f"blind-eat: 168 cat-ticks over 200 ticks, got {b['cat_ticks_per_1k']}"
assert b["span_mean"] == 56.0, "blind-eat span mean"
assert out["blind_drink"]["spans"] == 0 and \
    out["blind_drink"]["cat_ticks_per_1k"] == 0.0, "blind-drink stays quiet"
assert round(out["dispersion"]["euc_median"], 2) == 14.14, \
    "dispersion: nn pass-through"

# --- screen(): friend share and dispersion on moving pairs -----------------
pair = [snap([kitty("a", 0, 0), kitty("b", 2, 0)])] * 2 + \
       [snap([kitty("a", 0, 0), kitty("b", 5, 0)])] * 2
out2 = rs.screen(iter(pair), 3, DISTRESS, SAFEGUARD, ANNOUNCE)
assert out2["friend_in_view_share"] == 0.5, \
    f"friend: half the cat-ticks see a friend, got {out2['friend_in_view_share']}"
assert out2["dispersion"]["euc_median"] == 3.5, "dispersion: euc median 3.5"
assert out2["dispersion"]["contact_share"] == 0.0, "dispersion: no contact"
assert out2["distress_episodes_per_1k"] == 0.0, "quiet needs: no episodes"

# --- read_rollout(): meta wiring and the --trace refusal -------------------
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    cfg = td / "cfg.toml"
    cfg.write_text("[thresholds]\ndistress = 90\nsafeguard = 75\n"
                   "[meow]\nannounce_threshold = 30\n")
    roll = td / "roll"
    roll.mkdir()
    with open(roll / "trace.jsonl", "w") as f:
        for s in pair:
            f.write(json.dumps({"tick": 0, "snapshot": s}) + "\n")
    meta = {"trace": True, "vision_radius": 3, "world_seed": 123,
            "config": str(cfg), "config_sha256": "deadbeef"}
    (roll / "meta.json").write_text(json.dumps(meta))
    res = rs.read_rollout(roll)
    assert res["ticks"] == 4 and res["radius"] == 3, "read_rollout: trace read"
    assert res["world_seed"] == 123 and res["config_sha256"] == "deadbeef", \
        "read_rollout: meta stamped through"
    (roll / "meta.json").write_text(json.dumps({**meta, "trace": False}))
    try:
        rs.read_rollout(roll)
        raise SystemExit("read_rollout: a traceless rollout must be refused")
    except AssertionError:
        pass

print("test_radius_screen: PASS")
