#!/usr/bin/env python3
"""F-032: where `Idle` lands, and what it costs the seat that earns it.

`last_action` on the served surface is the ENFORCED action, not the
proposal (`world.rs:338`), and `action::validate` maps every illegal
proposal to `Action::Idle` (`action.rs:340`). So an `idle` has two
indistinguishable preimages -- a policy that chose it, and a policy that
was refused. This tool measures the pattern that tells them apart from
outside: WHERE idle lands relative to a scene ending, and whether the
critter field explains it.

Two sources, because the finding's first evidence was a client raw that
never commits:

  idle_seam.py [duration_s] [interval_s]   sample /world directly
  idle_seam.py path/to/pose-census.jsonl   re-cut a client pose census

The jsonl form reads Client's flat shape (`state`, `last_action` per
kitty, plus `elements`); the sampled form reads the endpoint's nested
shape. Both are handled here on purpose -- the shape belongs to the
ARTIFACT, not the endpoint, and assuming otherwise is how the 08-25
reader bug happened.
"""

import json
import statistics as st
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from census_provenance import served, stamp  # noqa: E402

BASE = "https://kitties.ai"
CRITTERS = {"bug", "greeble"}
SCENE = ("play", "chase")


def manhattan(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def sample(duration_s, interval_s):
    """Poll /world, keeping one row per distinct tick."""
    rows, seen = [], set()
    deadline = time.time() + duration_s
    while time.time() < deadline:
        try:
            w = json.load(urllib.request.urlopen(f"{BASE}/world", timeout=15))
        except Exception as e:
            print(f"poll: {e}", file=sys.stderr)
            time.sleep(interval_s)
            continue
        if w["tick"] not in seen:
            seen.add(w["tick"])
            rows.append({
                "tick": w["tick"],
                "kitties": [{
                    "name": k["name"],
                    "pos": k["pos"],
                    # nested here; flattened in a pose-census jsonl
                    "state": (k.get("activity") or {}).get("state"),
                    "last_action": k.get("last_action"),
                } for k in w["kitties"]],
                "elements": [{"kind": e["kind"], "pos": e["pos"]} for e in w["elements"]],
            })
        time.sleep(interval_s)
    return rows


def load(path):
    return [json.loads(line) for line in open(path)]


def analyse(rows):
    names = [k["name"] for k in rows[0]["kitties"]]
    out = {}
    for name in names:
        acts, dmin = [], []
        moved_while_idle = 0
        prev_pos = None
        prev_target = []
        for r in rows:
            k = next(x for x in r["kitties"] if x["name"] == name)
            la = k.get("last_action") or {}
            a = la.get("action")
            acts.append(a)
            prev_target.append((la.get("target"), la.get("id")))
            crits = [e for e in r["elements"] if e["kind"] in CRITTERS]
            dmin.append(min((manhattan(k["pos"], e["pos"]) for e in crits), default=None))
            pos = (k["pos"]["x"], k["pos"]["y"])
            if a == "idle" and prev_pos is not None and pos != prev_pos:
                moved_while_idle += 1
            prev_pos = pos

        # the discriminator: idle on the tick after a scene ends
        ends = [i + 1 for i, (x, y) in enumerate(zip(acts, acts[1:]))
                if x in SCENE and y not in SCENE]
        idle_after_end = sum(1 for i in ends if acts[i] == "idle")

        # what the refused ask was aimed at, one tick earlier
        preimage = Counter()
        for i, a in enumerate(acts):
            if a != "idle" or i == 0:
                continue
            if acts[i - 1] not in SCENE:
                preimage[f"prev {acts[i - 1]}"] += 1
            else:
                preimage["prev target KITTY (duet)" if prev_target[i - 1][0] == "kitty"
                         else "prev target element/none"] += 1

        # run lengths
        runs, cur = [], 0
        for a in acts:
            if a == "idle":
                cur += 1
            elif cur:
                runs.append(cur); cur = 0
        if cur:
            runs.append(cur)

        by_action = defaultdict(list)
        for a, d in zip(acts, dmin):
            if d is not None:
                by_action[a].append(d)

        out[name] = {
            "ticks": len(rows),
            "idle_ticks": sum(1 for a in acts if a == "idle"),
            "scene_endings": len(ends),
            "idle_after_ending": idle_after_end,
            "idle_after_ending_pct": round(100 * idle_after_end / len(ends), 1) if ends else None,
            "moved_while_idle": moved_while_idle,
            "idle_runs": dict(Counter(runs)),
            "idle_preimage": dict(preimage.most_common()),
            "nearest_critter_median": {
                a: round(st.median(v), 1) for a, v in sorted(by_action.items()) if v
            },
            "action_mix": dict(Counter(a for a in acts if a).most_common()),
        }
    return out


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "180"
    if not arg.replace(".", "").isdigit():
        rows, src = load(arg), arg
    else:
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        rows, src = sample(float(arg), interval), f"{BASE}/world"
    if len(rows) < 2:
        sys.exit("not enough ticks sampled")

    result = {
        "instrument": "idle_seam.py (F-032)",
        "provenance": stamp(__file__),
        "served": served(BASE),
        "source": src,
        "tick_range": [rows[0]["tick"], rows[-1]["tick"]],
        "seats": analyse(rows),
    }
    print(f"ticks {result['tick_range'][0]}-{result['tick_range'][1]}, {len(rows)} rows, source {src}\n")
    hdr = "%-12s %6s %6s %9s %8s  %s"
    print(hdr % ("seat", "ticks", "idle", "endings", "idle@end", "runs"))
    for n, s in result["seats"].items():
        print(hdr % (n, s["ticks"], s["idle_ticks"], s["scene_endings"],
                     f"{s['idle_after_ending_pct']}%", s["idle_runs"]))
    print()
    for n, s in result["seats"].items():
        if s["idle_ticks"]:
            print(f"{n} idle preimage: {s['idle_preimage']}")
            print(f"{n} nearest critter (median, by action): {s['nearest_critter_median']}")
            print(f"{n} moved while idle: {s['moved_while_idle']}/{s['idle_ticks']}")
    out = Path(__file__).resolve().parent / "results-raw" / f"idle-seam-{rows[0]['tick']}.json"
    out.write_text(json.dumps(result, indent=1))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
