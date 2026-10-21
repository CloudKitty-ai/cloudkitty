#!/usr/bin/env python3
"""Streak-shape read for battery leg files (ROSTER-DECLARATION.md
§Amendment 2): every seat-world whose longest distress run is at least
--min ticks, with its shape (tending / parked / idle / moving / other
shares) and the dominant kind; then counts by dominant kind. Rows
written before the harness carried the account read as n/a.

    shape_read.py LEG.jsonl [LEG.jsonl ...] [--min 100] [--out shape-read.json]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
KINDS = ("tending", "parked", "idle", "moving", "other")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--min", type=int, default=100)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    out = []
    for f in a.files:
        rows = [json.loads(l) for l in Path(f).read_text().splitlines()[1:]]
        if not all("streak_shape" in r for r in rows):
            out.append({"file": f, "shape": "n/a (pre-account rows)"})
            continue
        streaks = []
        for r in rows:
            for k, s in enumerate(r["streak_shape"]):
                if s["length"] >= a.min:
                    dom = max(KINDS, key=lambda c: s[c])
                    streaks.append({"seed": r["seed"], "seat": CATS[k], **s, "dominant": dom})
        streaks.sort(key=lambda s: -s["length"])
        out.append({"file": f, "streaks": streaks,
                     "by_dominant": dict(Counter(s["dominant"] for s in streaks))})
    for o in out:
        print(json.dumps({k: v for k, v in o.items() if k != "streaks"}))
        for s in o.get("streaks", []):
            print("   ", json.dumps(s))
    if a.out:
        a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
