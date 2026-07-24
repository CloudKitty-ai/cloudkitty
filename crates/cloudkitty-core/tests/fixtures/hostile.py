#!/usr/bin/env python3
"""A hostile CloudKitty plugin: malformed output every decision, cycling
through the failure modes that must not kill the process (spec 016 SC-003) --
non-JSON, an unknown action kind, an extra unknown field."""
import json
import sys

for i, line in enumerate(sys.stdin):
    req = json.loads(line)
    tick, kitty = req["tick"], req["kitty_id"]
    mode = i % 3
    if mode == 0:
        print("meow meow garbage {not json", flush=True)
    elif mode == 1:
        print(json.dumps({"tick": tick, "kitty_id": kitty,
                          "proposal": {"action": "levitate"}}), flush=True)
    else:
        print(json.dumps({"tick": tick, "kitty_id": kitty,
                          "proposal": {"action": "move", "direction": "north",
                                       "speed": 9}}), flush=True)
