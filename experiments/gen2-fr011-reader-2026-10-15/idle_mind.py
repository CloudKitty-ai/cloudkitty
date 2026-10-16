#!/usr/bin/env python3
"""An always-idle mind seat — the FR-011 fire rig's plugin brain.

Declared `class = "mind"` so wrap_mind_seats puts it behind the
StuckGuard (scripted seats are never tracked, FR-003/SC-005). It
proposes idle every tick, so its kitty stays confined while its needs
rise past the armed line — the cheapest real stuck condition a served
world can produce. Protocol per docs/plugins.md: one request line in,
one reply line out, tick/kitty_id echoed.
"""
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    reply = {
        "tick": request["tick"],
        "kitty_id": request["kitty_id"],
        "proposal": {"action": "idle"},
    }
    print(json.dumps(reply), flush=True)
