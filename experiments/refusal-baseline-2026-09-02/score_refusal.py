#!/usr/bin/env python3
"""Score a refusal-ring collection: the live refusal baseline (spec 046).

Input: a list of `/events/refusal` rows (deduped by the collector) and
the tick window [start, end] they cover. Every seat is present on every
tick, so a seat's denominator is the window's tick count.

Per seat and roster-wide:
- taxed share   = rows with absorbed == false / window ticks   (the
  step-5 pin currency: INVESTIGATE at >10% of a seat's ticks)
- absorbed share = rows with absorbed == true / window ticks
- combined density = all rows / window ticks (the retention sizing input:
  FR-004 wants >= 15,000 ticks of ring; retention floor = density * 15000)
- taxed rows by proposed action (and target kind when the action names one)

Usage: score_refusal.py results-raw/refusal-baseline-<tick>.json
"""

import json
import sys
from collections import Counter, defaultdict

WINDOW_TICKS = 15_000  # FR-004's ring window


def row_key(e):
    return (e["kitty_id"], e["tick"],
            json.dumps(e["proposed"], sort_keys=True))


def proposal_label(p):
    a = p["action"]
    if "target" in p:
        t = p["target"]
        return f"{a}:{t if isinstance(t, str) else 'kitty'}"
    if "with" in p:
        return f"{a}:with"
    return a


def score(rows, start_tick, end_tick, names=None):
    names = names or {}
    ticks = end_tick - start_tick + 1  # inclusive, F-031 rule
    assert ticks > 0, (start_tick, end_tick)
    seen = set()
    rows = [e for e in rows
            if start_tick <= e["tick"] <= end_tick
            and not (row_key(e) in seen or seen.add(row_key(e)))]
    per = defaultdict(lambda: {"taxed": 0, "absorbed": 0,
                               "taxed_by_action": Counter(),
                               "absorbed_by_action": Counter()})
    for e in rows:
        s = per[e["kitty_id"]]
        bucket = "absorbed" if e["absorbed"] else "taxed"
        s[bucket] += 1
        s[bucket + "_by_action"][proposal_label(e["proposed"])] += 1
    seats = {}
    for kid in sorted(per):
        s = per[kid]
        seats[str(kid)] = {
            "name": names.get(kid),
            "taxed": s["taxed"],
            "absorbed": s["absorbed"],
            "taxed_share": s["taxed"] / ticks,
            "absorbed_share": s["absorbed"] / ticks,
            "taxed_by_action": dict(s["taxed_by_action"].most_common()),
            "absorbed_by_action": dict(s["absorbed_by_action"].most_common()),
        }
    taxed = sum(v["taxed"] for v in seats.values())
    absorbed = sum(v["absorbed"] for v in seats.values())
    density = len(rows) / ticks
    return {
        "window": {"start_tick": start_tick, "end_tick": end_tick,
                   "ticks": ticks},
        "rows": len(rows),
        "taxed_rows": taxed,
        "absorbed_rows": absorbed,
        "taxed_density": taxed / ticks,
        "combined_density": density,
        "retention_floor_15k": int(density * WINDOW_TICKS + 0.5),
        "seats": seats,
    }


def render(sc):
    w = sc["window"]
    out = [f"window ticks {w['start_tick']}..{w['end_tick']} "
           f"({w['ticks']} ticks), rows {sc['rows']} "
           f"(taxed {sc['taxed_rows']}, absorbed {sc['absorbed_rows']})",
           f"combined density {sc['combined_density']:.3f}/tick "
           f"(taxed {sc['taxed_density']:.3f}); "
           f"retention floor for 15k ticks = {sc['retention_floor_15k']}",
           f"{'seat':<14}{'taxed%':>8}{'absorbed%':>11}  top taxed actions"]
    for kid, s in sc["seats"].items():
        top = ", ".join(f"{k} {v}" for k, v in
                        list(s["taxed_by_action"].items())[:3])
        label = f"{kid} {s['name'] or ''}"
        out.append(f"{label:<14}{100*s['taxed_share']:>7.2f}%"
                   f"{100*s['absorbed_share']:>10.2f}%  {top}")
    return "\n".join(out)


if __name__ == "__main__":
    raw = json.load(open(sys.argv[1]))
    names = {int(k): v for k, v in raw["names"].items()}
    sc = score(raw["rows"], raw["start_tick"], raw["end_tick"], names)
    print(render(sc))
    if "--write" in sys.argv:
        raw["score"] = sc
        json.dump(raw, open(sys.argv[1], "w"), indent=1)
