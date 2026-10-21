#!/usr/bin/env python3
"""Group-holding read for battery leg files (ROSTER-DECLARATION.md
§Amendment 2026-10-21). Per file: worlds, mean share of cat-ticks in a
3+ group, the largest per-cat held share, the longest per-cat held
stretch, the longest shared hold (two or more cats held at once), and
the worlds with any shared hold. Rows written before the harness
carried the account read as n/a, never as zero.

    holding_read.py LEG.jsonl [LEG.jsonl ...] [--out holding-read.json]
"""
import argparse
import json
from pathlib import Path


def read(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines()[1:]]
    if not all("holding" in r for r in rows):
        return {"file": str(path), "worlds": len(rows), "holding": "n/a (pre-account rows)"}
    h = [r["holding"] for r in rows]
    return {
        "file": str(path), "worlds": len(rows),
        "group3_share_mean": round(sum(sum(x["group3_share"]) / len(x["group3_share"]) for x in h) / len(h), 4),
        "held_share_max_cat": max(max(x["held_share"]) for x in h),
        "held_longest_max": max(max(x["held_longest"]) for x in h),
        "shared_hold_longest_max": max(x["shared_hold_longest"] for x in h),
        "worlds_with_shared_hold": sum(x["shared_hold_ticks"] > 0 for x in h),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    out = [read(f) for f in a.files]
    for r in out:
        print(json.dumps(r))
    if a.out:
        a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
