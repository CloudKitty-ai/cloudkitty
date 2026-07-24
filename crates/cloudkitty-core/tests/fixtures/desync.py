#!/usr/bin/env python3
"""Replies twice per request. The second (stale but perfectly valid) line
must never be applied to a later decision: the correlation check catches it
and restarts the process (spec 016, analysis finding I1)."""
import json
import sys

for line in sys.stdin:
    req = json.loads(line)
    envelope = json.dumps({"tick": req["tick"], "kitty_id": req["kitty_id"],
                           "proposal": {"action": "idle"}})
    print(envelope, flush=True)
    print(envelope, flush=True)
