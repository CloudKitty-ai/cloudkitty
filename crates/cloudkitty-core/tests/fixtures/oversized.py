#!/usr/bin/env python3
"""Replies with one enormous line: the reply_max_bytes bound must fail the
proposal and kill the process (spec 016 FR-010)."""
import sys

for line in sys.stdin:
    print("x" * 200000, flush=True)
