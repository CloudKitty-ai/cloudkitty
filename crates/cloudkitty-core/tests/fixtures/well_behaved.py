#!/usr/bin/env python3
"""A well-behaved CloudKitty plugin: correlated envelopes, always-legal
proposals. With --die-after N it exits after N replies, playing the part of
an advisor that dies mid-run (spec 016 SC-005)."""
import json
import sys

die_after = None
if len(sys.argv) == 3 and sys.argv[1] == "--die-after":
    die_after = int(sys.argv[2])

replies = 0
for line in sys.stdin:
    req = json.loads(line)
    tick, kitty = req["tick"], req["kitty_id"]
    # Idle and solo play are legal in every world state.
    proposal = {"action": "idle"} if tick % 2 == 0 else {"action": "play"}
    print(json.dumps({"tick": tick, "kitty_id": kitty, "proposal": proposal}), flush=True)
    replies += 1
    if die_after is not None and replies >= die_after:
        sys.exit(0)
