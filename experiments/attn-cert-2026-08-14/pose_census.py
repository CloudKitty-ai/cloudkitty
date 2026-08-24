#!/usr/bin/env python3
"""Per-tick census of what a VIEWER sees on the served world.

`live_census.py` reads the activity event stream — the world's own record
of what happened. This reads the frames instead: it polls `/world` faster
than the 800ms tick, dedupes by tick so every served tick is counted once,
and then replicates the client's `poseFor` + `chaseDistanceFor`
(client/render.js) against the very payload the browser drew. The output
is the pose mix on screen, not a proxy for it.

Why the two disagree, and why that is the point (2026-08-23): the drawn
pose reads `last_action`, not `activity.state`. For play, eat and drink
`activity.state` is a ONE-TICK resolution flag while the action spans the
whole engagement, so the action ticks run ~2x the state ticks for all
three — that ratio is action-run length, NOT over-drawing (eat 1.99x and
drink 2.01x both exceed play's 1.88x; Client's measurement, 2026-08-23).
The pounce is simply the loudest pose that rule extends. On top of it,
`chase` inside `pounceGateTiles` draws the pounce, and chase is how a cat
TRAVELS — so approach ticks that would draw a walk draw a pounce instead.
A world whose play budget matches its certification can still look
pounce-heavy, and only this instrument can say by how much.

Sections printed (and banked to results-raw/pose-census-<start_tick>.json):

- applied action mix per seat (`last_action`),
- activity STATE mix per seat (comparable to bio_census.py's table),
- DRAWN pose mix per seat (the client replica),
- chase-gate split: chases inside the gate, outside it, or unresolved,
- chase and play TARGETS by name — bug/greeble, the partner cat, or solo.

Usage: pose_census.py [duration_s] [interval_s] — 300s at 0.45s catches
essentially every tick of a 5-minute window.
"""

import json
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402

BASE = "https://kitties.ai"
DURATION_S = int(sys.argv[1]) if len(sys.argv) > 1 else 300
INTERVAL_S = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45
HERE = Path(__file__).resolve().parent

# The client's dials and tables. The two pose tables are ACTION_POSE and
# SCENE_POSE (client/render.js), mirrored because the census is Python and
# the client is the contract — test_pose_replica.py keeps the copy honest.
#
# The GATE is not mirrored, it is READ: a hardcoded 4 went stale within a
# day of being committed (the owner shipped 3 in #303), and a census whose
# gate disagrees with the client reports a pose mix nobody is looking at.
# It is stamped into every raw, because the checkout is only the deployed
# client if the deploy is current — the number that produced a banked run
# has to be recoverable from the run.
def pounce_gate_tiles(src=None):
    src = src or (Path(__file__).resolve().parents[2] / "client" / "anim.js")
    m = re.search(r"pounceGateTiles:\s*([0-9.]+)", src.read_text())
    if not m:
        raise SystemExit(f"pounceGateTiles not found in {src} — "
                         "the dial moved or was renamed; fix this first")
    return float(m.group(1))


POUNCE_GATE = pounce_gate_tiles()
ACTION_POSE = {
    "sleep": "sleep-curl", "rest": "loaf", "groom": "grooming",
    "eat": "eating", "drink": "drinking",
}
SCENE_POSE = {
    "sleeping": "sleep-curl", "resting": "loaf", "grooming": "grooming",
    "eating": "eating", "drinking": "drinking",
}


def chase_dist(kitty, world):
    """Manhattan tiles to whatever this tick's chase named, or None.

    None means unresolvable — no chase, or quarry caught/expired this very
    tick — and the client gives None the benefit of the doubt and KEEPS the
    pounce, so the gate only ever takes it away on positive evidence.
    """
    ref = kitty.get("last_action") or {}
    if ref.get("action") != "chase":
        return None
    if ref.get("target") == "element":
        pos = next((e["pos"] for e in world.get("elements", []) or []
                    if e.get("id") == ref.get("id")), None)
    else:
        pos = next((o["pos"] for o in world.get("kitties", []) or []
                    if o.get("id") == ref.get("id")), None)
    if not pos:
        return None
    return abs(kitty["pos"]["x"] - pos["x"]) + abs(kitty["pos"]["y"] - pos["y"])


def pose_for(kitty, moved, cd, gate=POUNCE_GATE):
    """render.js `poseFor`: action first, then scene, then movement."""
    action = (kitty.get("last_action") or {}).get("action")
    if action == "groom":
        return ("grooming-other"
                if kitty["last_action"].get("target") is not None
                else "grooming")
    if action in ACTION_POSE:
        return ACTION_POSE[action]
    # Play is never gated: a targeted play is adjacent by lawfulness, and
    # solo play has no target at all.
    if action == "play":
        return "pouncing"
    if action == "chase" and (cd is None or cd <= gate):
        return "pouncing"
    scene = SCENE_POSE.get((kitty.get("activity") or {}).get("state"))
    if scene:
        return scene
    return "walking" if moved else "idle"


def target_label(ref, kitty_names, el_kind):
    """Name what a chase or play points at: a critter kind, a cat, or solo."""
    if ref.get("target") == "element":
        return el_kind.get(ref.get("id"), "element(gone)")
    if ref.get("target") == "kitty":
        return kitty_names.get(ref.get("id"), f"kitty{ref.get('id')}")
    if ref.get("target") is None and "id" not in ref:
        return "solo"
    return f"unknown:{ref.get('target')}"


def collect():
    seen = {}
    stop = time.time() + DURATION_S
    while time.time() < stop:
        try:
            with urllib.request.urlopen(f"{BASE}/world", timeout=10) as r:
                world = json.load(r)
        except Exception as exc:  # transient box hiccup: skip the poll
            print(f"poll: {exc}", file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        seen.setdefault(world["tick"], world)
        time.sleep(INTERVAL_S)
    return seen


def main():
    seen = collect()
    if not seen:
        sys.exit("no ticks collected")
    ticks = sorted(seen)
    names = {k["id"]: k["name"] for k in seen[ticks[0]]["kitties"]}
    act = defaultdict(Counter)
    state = defaultdict(Counter)
    pose = defaultdict(Counter)
    gate_split = defaultdict(Counter)
    chase_at = defaultdict(Counter)
    play_at = defaultdict(Counter)
    prev = None
    consecutive = 0

    for t in ticks:
        world = seen[t]
        el_kind = {e["id"]: e.get("kind", "?")
                   for e in world.get("elements", []) or []}
        # A pose needs the PREVIOUS tick to know whether the cat moved, so
        # only consecutive pairs contribute to the pose mix; the action and
        # state mixes take every tick.
        adjacent = prev is not None and t == prev + 1
        consecutive += adjacent
        for k in world["kitties"]:
            ref = k.get("last_action") or {}
            action = ref.get("action", "?")
            act[k["id"]][action] += 1
            state[k["id"]][(k.get("activity") or {}).get("state", "?")] += 1
            if action in ("chase", "play"):
                bucket = chase_at if action == "chase" else play_at
                bucket[k["id"]][target_label(ref, names, el_kind)] += 1
            if not adjacent:
                continue
            was = next((x for x in seen[prev]["kitties"]
                        if x["id"] == k["id"]), None)
            moved = bool(was) and was["pos"] != k["pos"]
            cd = chase_dist(k, world)
            pose[k["id"]][pose_for(k, moved, cd)] += 1
            if action == "chase":
                gate_split[k["id"]]["unresolved" if cd is None else
                                    (f"<={POUNCE_GATE}" if cd <= POUNCE_GATE
                                     else f">{POUNCE_GATE}")] += 1
        prev = t

    def pct(counter):
        n = sum(counter.values()) or 1
        return " ".join(f"{k}:{100 * v / n:.1f}%"
                        for k, v in counter.most_common())

    print(f"pose census: ticks {ticks[0]}-{ticks[-1]}, {len(ticks)} seen of "
          f"span {ticks[-1] - ticks[0] + 1}, {consecutive} consecutive pairs")
    for title, table in (("applied action mix (last_action)", act),
                         ("activity STATE mix (bio_census comparable)", state),
                         ("DRAWN pose mix (client poseFor replica)", pose)):
        print(f"\n== {title} ==")
        for kid in sorted(table):
            print(f"{names[kid]:11} {pct(table[kid])}")
    print("\n== chase gate split / targets ==")
    for kid in sorted(names):
        print(f"{names[kid]:11} gate {dict(gate_split[kid])}")
        print(f"{'':11} chase {dict(chase_at[kid].most_common())}")
        print(f"{'':11} play  {dict(play_at[kid].most_common())}")

    out = {
        "instrument": "pose_census.py",
        # F-028's header. The gate below is part of it: this census
        # replicates a CLIENT rule, so the dial it replicated is as
        # load-bearing as the commit it ran from.
        "provenance": stamp(__file__),
        "served": served(BASE),
        "base": BASE, "interval_s": INTERVAL_S,
        "pounce_gate_tiles": POUNCE_GATE,
        "tick_range": [ticks[0], ticks[-1]],
        "ticks_seen": len(ticks), "consecutive_pairs": consecutive,
        "action_mix": {names[k]: dict(v) for k, v in act.items()},
        "state_mix": {names[k]: dict(v) for k, v in state.items()},
        "pose_mix": {names[k]: dict(v) for k, v in pose.items()},
        "chase_gate_split": {names[k]: dict(v) for k, v in gate_split.items()},
        "chase_targets": {names[k]: dict(v) for k, v in chase_at.items()},
        "play_targets": {names[k]: dict(v) for k, v in play_at.items()},
    }
    raw_dir = HERE / "results-raw"
    raw_dir.mkdir(exist_ok=True)
    path = raw_dir / f"pose-census-{ticks[0]}.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(f"\n-> {path}")


if __name__ == "__main__":
    main()
