#!/usr/bin/env python3
"""Live-world census for the purrsonality deployed-world entry.

Samples the box's REST surface (no ws, no load): /world for the tick,
/kitties for per-seat state + positions, /events/activity for the
rolling 1000-event window. Polls every INTERVAL seconds for DURATION
minutes, dedupes activity events by (kitty_id, started, state), and
aggregates:

- activity budget per seat (share of ended activities by state),
- the directed grooming graph (groomer -> groomee, from activity
  target ids; reader rule: `id` present = element kind, else kitty),
- cosleep observations (sleeping cats adjacent to another sleeper at
  poll time, Manhattan <= 1 — the pile),
- proximity fabric (mean nearest-neighbor distance per seat,
  share of polls within 2 tiles of a neighbor),
- per-seat happiness over the sampling window.

Writes results-raw/live-census-<start_tick>.json (raw polls + the
aggregation) and prints the summary table. The register's lab numbers
are priors; this is the live truth at the deployed seats.
"""

import json
import statistics as st
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

BASE = "https://kitties.ai"
# Overridable: live_census.py [duration_min] [interval_s] — the defaults
# reproduce the 08-18 baseline's window.
INTERVAL_S = int(sys.argv[2]) if len(sys.argv) > 2 else 60
DURATION_MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 25
HERE = Path(__file__).resolve().parent


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
        return json.load(r)


def main():
    polls, events = [], {}
    n_polls = max(1, (DURATION_MIN * 60) // INTERVAL_S)
    start_tick = None
    for i in range(n_polls):
        try:
            world = get("/world")
            kitties = get("/kitties")
            acts = get("/events/activity")
        except Exception as e:  # transient box hiccup: skip the poll
            print(f"poll {i}: {e}", file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        tick = world.get("tick")
        start_tick = start_tick if start_tick is not None else tick
        polls.append({"tick": tick, "kitties": [
            {"id": k["id"], "name": k["name"], "pos": k["pos"],
             "happiness": k["happiness"],
             "activity": k["activity"]} for k in kitties]})
        evs = acts if isinstance(acts, list) else acts.get("events", [])
        for e in evs:
            key = (e["kitty_id"], e["started"],
                   json.dumps(e["activity"], sort_keys=True))
            events[key] = e
        if i < n_polls - 1:
            time.sleep(INTERVAL_S)

    names = {k["id"]: k["name"] for k in polls[0]["kitties"]}
    budget = defaultdict(Counter)
    groom = Counter()
    play = defaultdict(Counter)
    for e in events.values():
        act = e["activity"]
        state = act.get("state", "?")
        budget[e["kitty_id"]][state] += 1
        if state == "grooming":
            tgt = act.get("target")
            # id-present => element kind; bare int/None => kitty id
            if isinstance(tgt, int):
                groom[(e["kitty_id"], tgt)] += 1
        elif state == "playing":
            # Reader rule (specs/001 contracts): `id` present => `target`
            # is the element KIND; bare target => kitty id; neither =>
            # solo. Added 2026-08-18 (owner ask): the bug-play baseline
            # for the post-seating Biscuit-2.0 comparison.
            tgt = act.get("target")
            if act.get("id") is not None:
                play[e["kitty_id"]][str(tgt)] += 1
            elif tgt is not None:
                play[e["kitty_id"]]["kitty"] += 1
            else:
                play[e["kitty_id"]]["solo"] += 1

    cosleep = Counter()
    near = defaultdict(list)
    hap = defaultdict(list)
    for p in polls:
        ks = p["kitties"]
        for k in ks:
            hap[k["id"]].append(k["happiness"])
            others = [o for o in ks if o["id"] != k["id"]]
            d = min(abs(k["pos"]["x"] - o["pos"]["x"])
                    + abs(k["pos"]["y"] - o["pos"]["y"]) for o in others)
            near[k["id"]].append(d)
            if k["activity"].get("state") == "sleeping":
                for o in others:
                    if (o["activity"].get("state") == "sleeping"
                            and abs(k["pos"]["x"] - o["pos"]["x"])
                            + abs(k["pos"]["y"] - o["pos"]["y"]) <= 1):
                        cosleep[tuple(sorted((k["id"], o["id"])))] += 1

    out = {
        "instrument": "live_census.py",
        "base": BASE, "interval_s": INTERVAL_S,
        "polls": len(polls),
        "tick_range": [polls[0]["tick"], polls[-1]["tick"]],
        "unique_activity_events": len(events),
        "activity_budget": {names[k]: dict(c) for k, c in budget.items()},
        "play_targets": {names[k]: dict(c) for k, c in play.items()},
        "grooming_graph": {f"{names[a]}->{names[b]}": n
                           for (a, b), n in groom.items()},
        "cosleep_pair_polls": {f"{names[a]}+{names[b]}": n
                               for (a, b), n in cosleep.items()},
        "mean_nearest": {names[k]: round(st.mean(v), 2)
                         for k, v in near.items()},
        "share_within_2": {names[k]:
                           round(sum(d <= 2 for d in v) / len(v), 2)
                           for k, v in near.items()},
        "happiness": {names[k]: {"mean": round(st.mean(v), 2),
                                 "min": round(min(v), 2),
                                 "max": round(max(v), 2)}
                      for k, v in hap.items()},
        "raw_polls": polls,
    }
    raw_dir = HERE / "results-raw"
    raw_dir.mkdir(exist_ok=True)
    path = raw_dir / f"live-census-{out['tick_range'][0]}.json"
    path.write_text(json.dumps(out, indent=1) + "\n")

    print(f"census: ticks {out['tick_range'][0]}-{out['tick_range'][1]}, "
          f"{len(polls)} polls, {len(events)} unique activity events")
    for section in ("activity_budget", "play_targets", "grooming_graph",
                    "cosleep_pair_polls", "mean_nearest",
                    "share_within_2", "happiness"):
        print(f"{section}: {json.dumps(out[section])}")
    print(f"-> {path}")


if __name__ == "__main__":
    main()
