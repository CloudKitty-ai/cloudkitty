#!/usr/bin/env python3
"""A well-behaved CloudKitty plugin: correlated envelopes, always-legal
proposals. With --die-after N it exits after N replies, playing the part of
an advisor that dies mid-run (spec 016 SC-005).

Well-behaved also means (spec 049 FR-048 / SC-013): it refuses a wire
version it does not understand (exit 3 -- the engine falls back, safely),
and it checks the world it is handed is the fogged one the version
promises: every kitty and element inside the deciding cat's vision disc
(dx^2 + dy^2 <= r^2 from `me`), its own memory and heading on `me`, and
`pos` / `reply` on every meow (exit 4 on any leak)."""
import json
import sys

WIRE_VERSION = 3

die_after = None
if len(sys.argv) == 3 and sys.argv[1] == "--die-after":
    die_after = int(sys.argv[2])


def check_fogged(req):
    me = req["me"]
    r = req["config"]["vision"]["radius"]
    ox, oy = me["pos"]["x"], me["pos"]["y"]
    if "memory" not in me or "explore_waypoint" not in me:
        return False
    for entity in req["world"]["kitties"] + req["world"]["elements"]:
        dx, dy = entity["pos"]["x"] - ox, entity["pos"]["y"] - oy
        if dx * dx + dy * dy > r * r:
            return False
    return all("pos" in m and "reply" in m for m in req["world"]["recent_meows"])


replies = 0
for line in sys.stdin:
    req = json.loads(line)
    if req.get("v") != WIRE_VERSION:
        sys.exit(3)
    if not check_fogged(req):
        sys.exit(4)
    tick, kitty = req["tick"], req["kitty_id"]
    # Idle and solo play are legal in every world state.
    proposal = {"action": "idle"} if tick % 2 == 0 else {"action": "play"}
    print(json.dumps({"tick": tick, "kitty_id": kitty, "proposal": proposal}), flush=True)
    replies += 1
    if die_after is not None and replies >= die_after:
        sys.exit(0)
