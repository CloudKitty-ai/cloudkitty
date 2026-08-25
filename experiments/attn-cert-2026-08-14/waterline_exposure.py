#!/usr/bin/env python3
"""How often would a waterline pairing rule bind on the served world?

Owner's framing (2026-08-24): it is a PARTNERED-ACTIVITY rule, not a
grooming or sleeping rule. Two adjacent cats both on land may pair; both
on water may pair; one on each side may not. So the measurement is over
every paired activity — duet, co-sleep, cuddle, groom-a-friend — and the
first cut anyone reaches for (per-cat activity state while adjacent) is
the wrong one twice over: it drops duets if the reader only enumerates
the activities the proposal happened to name, and it weights by scene
length, so a long activity looks more exposed than a short one at equal
frequency.

This counts two different things, because they answer two different
questions and the rule does both:

  - **opportunity denied**: cross-waterline ADJACENCY. A pairing that
    could have formed and now cannot.
  - **pairing broken**: an ACTIVE cross-waterline pairing, counted once
    per unordered pair per tick. Something the rule would end, since the
    friend helpers are consulted by `validate` every tick, not only at
    formation.

Report both. If they disagree, that disagreement is the finding.

NOT a substitute for the scripted-anchor probe: this measures the served
world under the CURRENT rules, so it says how often the rule would bite,
never what the world does once cats can adapt to it. A scripted anchor
re-derivation answers that, and F-016 §3 warns that even that will not
proxy learned policies on the grooming-on-water channel.
"""

import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402

BASE = "https://kitties.ai"
DURATION_S = int(sys.argv[1]) if len(sys.argv) > 1 else 300
INTERVAL_S = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45
HERE = Path(__file__).resolve().parent
KINDS = ("duet", "cosleep", "cuddle", "groom")


def partner_of(kitty):
    """(friend id, kind) if this cat is PAIRED right now, else None.

    Paired means the activity names another kitty. Element play and solo
    play are not pairings and a waterline rule never touches them; chase
    and meow are not activities at all.
    """
    a = kitty.get("activity") or {}
    state = a.get("state")
    if state == "playing":
        t = a.get("target")
        if isinstance(t, dict) and t.get("target") == "kitty":
            return t.get("id"), "duet"
    elif state in ("resting", "sleeping") and a.get("with_friend") is not None:
        return a["with_friend"], "cuddle" if state == "resting" else "cosleep"
    elif state == "grooming" and isinstance(a.get("target"), int):
        return a["target"], "groom"
    return None


def main():
    seen = {}
    stop = time.time() + DURATION_S
    while time.time() < stop:
        try:
            with urllib.request.urlopen(f"{BASE}/world", timeout=10) as r:
                w = json.load(r)
            seen.setdefault(w["tick"], w)
        except Exception as exc:
            print(f"poll: {exc}", file=sys.stderr)
        time.sleep(INTERVAL_S)
    if not seen:
        sys.exit("no ticks collected")

    ticks = sorted(seen)
    names = {k["id"]: k["name"] for k in seen[ticks[0]]["kitties"]}
    c = Counter()
    active = Counter()
    active_pairs = Counter()
    adjacency_pairs = Counter()

    for t in ticks:
        w = seen[t]
        water = {(e["pos"]["x"], e["pos"]["y"])
                 for e in w.get("elements", []) or []
                 if e.get("kind") == "water"}
        ks = {k["id"]: k for k in w["kitties"]}
        on = {i: (k["pos"]["x"], k["pos"]["y"]) in water for i, k in ks.items()}
        counted = set()
        for i, k in ks.items():
            c["cat_ticks"] += 1
            c["on_water"] += on[i]
            pr = partner_of(k)
            if pr and pr[0] in ks:
                j, kind = pr
                key = (min(i, j), max(i, j), kind)
                if key not in counted:      # once per unordered pair per tick
                    counted.add(key)
                    active[kind] += 1
                    if on[i] != on[j]:
                        active[f"cross_{kind}"] += 1
                        active_pairs[(kind, tuple(sorted(
                            (names[i], names[j]))))] += 1
            for j, o in ks.items():
                if j <= i:
                    continue
                p, q = k["pos"], o["pos"]
                if abs(p["x"] - q["x"]) + abs(p["y"] - q["y"]) == 1:
                    c["adjacent_pair_ticks"] += 1
                    if on[i] != on[j]:
                        c["cross_adjacent"] += 1
                        adjacency_pairs[tuple(sorted(
                            (names[i], names[j])))] += 1

    out = {
        "instrument": "waterline_exposure.py",
        "provenance": stamp(__file__),
        "served": served(BASE),
        "tick_range": [ticks[0], ticks[-1]], "ticks_seen": len(ticks),
        "cat_ticks": c["cat_ticks"],
        "on_water_share": round(c["on_water"] / max(1, c["cat_ticks"]), 4),
        "adjacent_pair_ticks": c["adjacent_pair_ticks"],
        "cross_adjacent_pair_ticks": c["cross_adjacent"],
        "active_pairings": {k: active[k] for k in KINDS},
        "cross_pairings": {k: active[f"cross_{k}"] for k in KINDS},
        "cross_pairings_by_pair": {f"{k[0]}:{'+'.join(k[1])}": v
                                   for k, v in active_pairs.items()},
        "cross_adjacency_by_pair": {"+".join(k): v
                                    for k, v in adjacency_pairs.items()},
    }
    raw = HERE / "results-raw" / f"waterline-exposure-{ticks[0]}.json"
    raw.write_text(json.dumps(out, indent=1) + "\n")

    print(f"ticks {len(ticks)} ({ticks[0]}-{ticks[-1]})")
    print(f"on-water share of cat-ticks: {100 * out['on_water_share']:.2f}%")
    print(f"cross-waterline adjacency: {c['cross_adjacent']} of "
          f"{c['adjacent_pair_ticks']} adjacent pair-ticks "
          f"({100 * c['cross_adjacent'] / max(1, c['adjacent_pair_ticks']):.2f}%)")
    print("\npaired activity     pair-ticks   cross   rate")
    for k in KINDS:
        tot, cr = active[k], active[f"cross_{k}"]
        rate = f"{100 * cr / tot:5.1f}%" if tot else "    —"
        print(f"  {k:16} {tot:8}   {cr:5}  {rate}")
    print(f"\ncross pairings by pair: {out['cross_pairings_by_pair']}")
    print(f"cross adjacency by pair: {out['cross_adjacency_by_pair']}")
    print(f"-> {raw}")


if __name__ == "__main__":
    main()
