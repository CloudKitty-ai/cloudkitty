#!/usr/bin/env python3
"""Collect the partner_absent split window off kitties.ai (PREREG.md).

Two polls on independent cadences:
- /world every WORLD_INTERVAL_S: a tick's kitty positions are recorded
  the first time that tick is seen (the snapshot labeled T carries the
  start-of-tick positions for tick T -- PREREG.md "Join rule").
- /events/refusal every RING_INTERVAL_S: rows deduped on
  (kitty_id, tick, proposed-json); a poll whose oldest row is newer
  than the previous poll's newest row is a ring rollover and is
  flagged (the F-029 hole, as in the refusal baseline collector).

Writes results-raw/partner-absent-split-<start_tick>.json with the raw
rows, the per-tick positions, the stored /config, the poll log and
both provenance halves. The read lives in split_read.py; this script
computes nothing.

Usage: collect_split.py [window_ticks]
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402

BASE = "https://kitties.ai"
WINDOW_TICKS = int(sys.argv[1]) if len(sys.argv) > 1 else 7_500
WORLD_INTERVAL_S = 0.55
RING_INTERVAL_S = 60
WALL_CAP_MIN = 150
HERE = Path(__file__).resolve().parent


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
        return json.load(r)


def row_key(e):
    return (e["kitty_id"], e["tick"],
            json.dumps(e["proposed"], sort_keys=True))


def main():
    rows, polls, gaps = {}, [], []
    positions = {}  # str(tick) -> {str(kitty_id): [x, y]}
    start_tick, last_max = None, None
    names, provenance, config = None, None, None
    last_ring_poll = 0.0
    t_wall = time.time()
    tick = None
    while time.time() - t_wall < WALL_CAP_MIN * 60:
        try:
            world = get("/world")
        except Exception as e:  # transient box hiccup: skip the poll
            print(f"world poll: {e}", file=sys.stderr)
            time.sleep(WORLD_INTERVAL_S)
            continue
        tick = world["tick"]
        if start_tick is None:
            start_tick = tick
            names = {k["id"]: k["name"] for k in world["kitties"]}
            provenance = {"instrument": stamp(__file__),
                          "served": served(BASE)}
            config = get("/config")
        key = str(tick)
        if key not in positions:
            positions[key] = {str(k["id"]): [k["pos"]["x"], k["pos"]["y"]]
                              for k in world["kitties"]}
        now = time.time()
        if now - last_ring_poll >= RING_INTERVAL_S:
            last_ring_poll = now
            try:
                ring = get("/events/refusal")
            except Exception as e:
                print(f"ring poll: {e}", file=sys.stderr)
                ring = None
            if ring is not None:
                ev = ring["events"]
                if ev and last_max is not None and ev[0]["tick"] > last_max + 1:
                    gaps.append({"tick": tick, "ring_oldest": ev[0]["tick"],
                                 "prev_newest": last_max})
                for e in ev:
                    rows[row_key(e)] = e
                if ev:
                    last_max = max(e["tick"] for e in ev)
                polls.append({"tick": tick, "ring_rows": len(ev),
                              "kept": len(rows),
                              "ticks_captured": len(positions)})
                print(f"tick {tick} (+{tick - start_tick}/{WINDOW_TICKS}): "
                      f"rows {len(rows)}, ticks captured {len(positions)}",
                      flush=True)
        if tick >= start_tick + WINDOW_TICKS:
            break
        time.sleep(WORLD_INTERVAL_S)

    # One final ring sweep so the tail of the window is in the rows.
    try:
        for e in get("/events/refusal")["events"]:
            rows[row_key(e)] = e
    except Exception as e:
        print(f"final ring poll: {e}", file=sys.stderr)

    out = {
        "window": {"start_tick": start_tick, "end_tick": tick},
        "names": names,
        "events": list(rows.values()),
        "positions": positions,
        "config": config,
        "provenance": provenance,
        "polls": polls,
        "gaps": gaps,
    }
    dest = HERE / "results-raw"
    dest.mkdir(exist_ok=True)
    path = dest / f"partner-absent-split-{start_tick}.json"
    path.write_text(json.dumps(out))
    print(f"wrote {path} ({len(rows)} rows, {len(positions)} ticks, "
          f"{len(gaps)} gaps)")


if __name__ == "__main__":
    main()
