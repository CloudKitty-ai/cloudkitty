#!/usr/bin/env python3
"""A complete, working CloudKitty behavior plugin -- the worked example for
docs/plugins.md.

The professor wanders the meadow, pounces at nothing when the mood strikes,
and asks for cuddles when lonely. Not a clever cat -- the point is the
plumbing:

  * read ONE request line from stdin, write ONE reply line to stdout;
  * echo the request's tick and kitty_id in the reply envelope
    (a mismatched echo makes CloudKitty restart this process);
  * propose exactly one action from the documented wire
    (docs/plugins.md -- anything malformed just costs the turn);
  * break symmetry with the request's seed, never with a fixed rule two
    kitties could compute identically (the livelock warning).

Run it via cloudkitty.toml:

    [plugins.professor_whiskers]
    command = "docs/examples/demo_plugin.py"
"""
import json
import sys

DIRECTIONS = ["north", "east", "south", "west"]

for line in sys.stdin:
    request = json.loads(line)
    tick = request["tick"]
    kitty_id = request["kitty_id"]
    me = request["me"]
    # The kitty's own per-tick randomness: deterministic to the world,
    # never synchronized with any other kitty. THE tie-breaker.
    seed = request["seed"]

    needs = me.get("needs", {})
    if needs.get("cuddle", 0) > 70:
        # Lonely: say so. (A meow on cooldown is legal -- just silent.)
        proposal = {"action": "meow", "message": "want_cuddle"}
    elif needs.get("sleep", 0) > 80:
        proposal = {"action": "sleep"}
    elif seed % 5 == 0:
        # Pounce at nothing. Solo play is always legal.
        proposal = {"action": "play"}
    else:
        # Wander. The seed picks the direction, so two professors meeting
        # head-on in a corridor will not mirror each other forever.
        proposal = {"action": "move", "direction": DIRECTIONS[seed % 4]}

    reply = {"tick": tick, "kitty_id": kitty_id, "proposal": proposal}
    print(json.dumps(reply), flush=True)

    # Diagnostics belong on stderr -- stdout is only for replies.
    if tick % 100 == 0:
        print(f"professor: tick {tick}, still professing", file=sys.stderr)
