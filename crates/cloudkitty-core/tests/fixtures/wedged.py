#!/usr/bin/env python3
"""The silent wedge: reads each request, never answers, keeps stdout open.

The nastiest failure shape — no reply, no exit, no EOF. The exchange
deadline (exchange_timeout_ms) is the only thing that can contain it.
"""
import sys
import time

for line in sys.stdin:
    time.sleep(3600)
