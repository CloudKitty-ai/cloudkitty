#!/usr/bin/env python3
"""Collect the live refusal baseline off kitties.ai (spec 046, FR-004).

Polls /events/refusal and /world every INTERVAL_S seconds until the world
has advanced WINDOW_TICKS ticks past the first poll (or WALL_CAP_MIN
elapses). Rows are deduped on (kitty_id, tick, proposed); a poll whose
oldest row is newer than the previous poll's newest row is a ring
rollover between polls and is flagged (the F-029 hole: a window with a
gap undercounts at exactly the density it measures).

Writes results-raw/refusal-baseline-<start_tick>.json with the raw rows,
the poll log, both provenance halves (census_provenance.stamp + served),
and the score; prints the score table.

Usage: refusal_baseline.py [window_ticks] [interval_s]
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402
from score_refusal import render, row_key, score  # noqa: E402

BASE = "https://kitties.ai"
WINDOW_TICKS = int(sys.argv[1]) if len(sys.argv) > 1 else 15_000
INTERVAL_S = int(sys.argv[2]) if len(sys.argv) > 2 else 120
WALL_CAP_MIN = 360
HERE = Path(__file__).resolve().parent


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
        return json.load(r)


def main():
    rows, polls, gaps = {}, [], []
    start_tick, end_tick, last_max = None, None, None
    names = None
    t_wall = time.time()
    while time.time() - t_wall < WALL_CAP_MIN * 60:
        try:
            world = get("/world")
            ring = get("/events/refusal")
        except Exception as e:  # transient box hiccup: skip the poll
            print(f"poll {len(polls)}: {e}", file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        tick = world["tick"]
        if start_tick is None:
            start_tick = tick
            names = {k["id"]: k["name"] for k in world["kitties"]}
            provenance = {"instrument": stamp(__file__),
                          "served": served(BASE)}
        ev = ring["events"]
        if ev and last_max is not None and ev[0]["tick"] > last_max + 1:
            gaps.append({"poll": len(polls), "prev_max": last_max,
                         "oldest_seen": ev[0]["tick"]})
        for e in ev:
            rows.setdefault(row_key(e), e)
        if ev:
            last_max = max(last_max or 0, ev[-1]["tick"])
        polls.append({"tick": tick, "ring_rows": len(ev),
                      "capacity": ring.get("capacity"),
                      "unique_rows": len(rows), "utc": time.time()})
        end_tick = tick
        print(f"poll {len(polls)} tick {tick} (+{tick - start_tick}) "
              f"ring {len(ev)} unique {len(rows)} gaps {len(gaps)}",
              flush=True)
        if tick - start_tick >= WINDOW_TICKS:
            break
        time.sleep(INTERVAL_S)

    # Window ends at the last polled tick; rows past it are not yet
    # complete for every seat and are dropped by score().
    raw = {"start_tick": start_tick, "end_tick": end_tick,
           "names": {str(k): v for k, v in names.items()},
           "polls": polls, "gaps": gaps, "rows": list(rows.values()),
           "provenance": provenance}
    raw["score"] = score(raw["rows"], start_tick, end_tick, names)
    out = HERE / "results-raw" / f"refusal-baseline-{start_tick}.json"
    out.parent.mkdir(exist_ok=True)
    json.dump(raw, open(out, "w"), indent=1)
    print(render(raw["score"]))
    print(f"gaps: {len(gaps)}  wrote {out}")


if __name__ == "__main__":
    main()
