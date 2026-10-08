#!/usr/bin/env python3
"""Score a partner_absent split collection (PREREG.md).

Joins each partner_absent refusal row to the captured start-of-tick
positions (equal-tick join -- PREREG.md "Join rule") and buckets it:

  race  target at Manhattan <= 1 of the caller (the proposal was legal
        against the snapshot the mind decided on; the partner moved
        earlier in the same tick's turn order)
  seen  not adjacent, but dx^2 + dy^2 <= r^2 (the engine's vision
        disc), r = the collection's stored /config vision.radius
  fog   outside the disc

Rows whose tick has no captured snapshot are dropped and counted,
never guessed from neighbouring ticks.

Usage: split_read.py <raw.json> [--out <json>] [--md <md>]
"""

import json
import sys
from collections import Counter, defaultdict

BUCKETS = ("race", "seen", "fog")


def target_id(proposed):
    """The partnered target, from the three real payload shapes
    (PREREG.md): sleep/rest carry `with`, groom carries an integer
    `target`, play carries `target: "kitty"` plus `id`."""
    if "with" in proposed:
        return proposed["with"]
    t = proposed.get("target")
    if isinstance(t, int):
        return t
    if t == "kitty" and isinstance(proposed.get("id"), int):
        return proposed["id"]
    return None


def proposal_label(p):
    a = p["action"]
    if "target" in p:
        t = p["target"]
        return f"{a}:{t if isinstance(t, str) else 'kitty'}"
    if "with" in p:
        return f"{a}:with"
    return a


def bucket(caller_pos, target_pos, radius):
    dx = caller_pos[0] - target_pos[0]
    dy = caller_pos[1] - target_pos[1]
    if abs(dx) + abs(dy) <= 1:
        return "race"
    if dx * dx + dy * dy <= radius * radius:
        return "seen"
    return "fog"


def score(raw):
    radius = raw["config"]["vision"]["radius"]
    window = raw["window"]
    start, end = window["start_tick"], window["end_tick"]
    positions = raw["positions"]
    rows = [e for e in raw["events"]
            if e["reason"] == "partner_absent"
            and start <= e["tick"] <= end]
    joined, dropped, unparsed = [], 0, 0
    for e in rows:
        snap = positions.get(str(e["tick"]))
        if snap is None:
            dropped += 1
            continue
        tid = target_id(e["proposed"])
        caller = snap.get(str(e["kitty_id"]))
        target = snap.get(str(tid)) if tid is not None else None
        if caller is None or target is None:
            unparsed += 1
            continue
        joined.append((e, bucket(caller, target, radius)))

    per_bucket = {b: {"rows": 0, "absorbed": 0, "by_action": Counter()}
                  for b in BUCKETS}
    per_seat = defaultdict(lambda: Counter())
    for e, b in joined:
        s = per_bucket[b]
        s["rows"] += 1
        s["absorbed"] += 1 if e["absorbed"] else 0
        s["by_action"][proposal_label(e["proposed"])] += 1
        per_seat[e["kitty_id"]][b] += 1

    n = len(joined)
    buckets = {}
    for b in BUCKETS:
        s = per_bucket[b]
        buckets[b] = {
            "rows": s["rows"],
            "share": s["rows"] / n if n else None,
            "absorbed": s["absorbed"],
            "absorbed_share": s["absorbed"] / s["rows"] if s["rows"] else None,
            "by_action": dict(s["by_action"].most_common()),
        }
    names = {int(k): v for k, v in (raw.get("names") or {}).items()}
    seats = {}
    for kid in sorted(per_seat):
        c = per_seat[kid]
        seats[str(kid)] = {"name": names.get(kid),
                           **{b: c[b] for b in BUCKETS},
                           "rows": sum(c.values())}
    return {
        "window": {"start_tick": start, "end_tick": end,
                   "ticks": end - start + 1},
        "radius": radius,
        "tick_coverage": len(positions) / (end - start + 1),
        "partner_absent_rows": len(rows),
        "joined": n,
        "dropped_no_snapshot": dropped,
        "dropped_unparsed": unparsed,
        "buckets": buckets,
        "seats": seats,
    }


def render(sc):
    w = sc["window"]
    out = [f"window ticks {w['start_tick']}..{w['end_tick']} "
           f"({w['ticks']} ticks), tick coverage {sc['tick_coverage']:.3f}, "
           f"radius {sc['radius']}",
           f"partner_absent rows {sc['partner_absent_rows']}: "
           f"joined {sc['joined']}, dropped {sc['dropped_no_snapshot']} "
           f"(no snapshot) + {sc['dropped_unparsed']} (unparsed)",
           "",
           "| bucket | rows | share | absorbed share | top proposals |",
           "|---|---|---|---|---|"]
    for b in BUCKETS:
        s = sc["buckets"][b]
        share = f"{s['share']:.3f}" if s["share"] is not None else "--"
        ab = (f"{s['absorbed_share']:.3f}"
              if s["absorbed_share"] is not None else "--")
        top = ", ".join(f"{k} {v}" for k, v in
                        list(s["by_action"].items())[:3]) or "--"
        out.append(f"| {b} | {s['rows']} | {share} | {ab} | {top} |")
    out.append("")
    out.append("| seat | race | seen | fog | rows |")
    out.append("|---|---|---|---|---|")
    for kid, s in sc["seats"].items():
        out.append(f"| {s['name'] or kid} | {s['race']} | {s['seen']} "
                   f"| {s['fog']} | {s['rows']} |")
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    out_path = md_path = None
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        del args[i:i + 2]
    if "--md" in args:
        i = args.index("--md")
        md_path = args[i + 1]
        del args[i:i + 2]
    raw = json.load(open(args[0]))
    sc = score(raw)
    table = render(sc)
    print(table)
    if out_path:
        with open(out_path, "w") as f:
            json.dump(sc, f, indent=1)
    if md_path:
        with open(md_path, "w") as f:
            f.write(table + "\n")


if __name__ == "__main__":
    main()
