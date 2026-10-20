#!/usr/bin/env python3
"""Step-8 gate read, exactly as DECLARATION.md §Gates pins it: per
seating x size, the 30 paired per-seed deltas (trained - scripted team
happiness, same seed, team = mean over the five seats' mean
happiness), mean / sign count / range; gate = paired mean delta >= 0
AND trained mean >= pinned comparator mean (20, 40 only; 100 is
characterize-only). Worst-streak mean/max and abort counts beside.
Aborted rows are scored on the ticks they ran and FLAGGED; the gate
verdict is printed with and without them, never silently mixed.

    gate_read.py [--out gate-read.json]
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_RAW = HERE.parent / "gen2-comparator-legs-2026-10-14/results-raw"
# The vision-law comparators (prereg §7 pins); results-raw/legs/size{40,100}
# hold the superseded vision-4 record and must never be paired against.
CMP_FILE = {20: _RAW / "legs/size20/scripted-g2cmp-30x20000.jsonl",
            40: _RAW / "vision5-40/legs/size40/scripted-g2cmp-30x20000.jsonl",
            100: _RAW / "vision-law-100/legs/size100/scripted-g2cmp-30x20000.jsonl"}
PINNED = {20: 81.921, 40: 81.634, 100: 76.623}
SEATINGS = ("g2-s1", "g2-s2", "g2-s4")


def rows(p):
    return [json.loads(l) for l in open(p)][1:]


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "gate-read.json")
    a = ap.parse_args()
    cmp = {}
    for size in (20, 40, 100):
        rs = rows(CMP_FILE[size])
        assert len(rs) == 30
        cmp[size] = {r["seed"]: team(r) for r in rs}
        m = sum(cmp[size].values()) / 30
        assert round(m, 3) == PINNED[size], (size, m)  # pinned baseline reproduces
    out = {}
    for s in SEATINGS:
        for size in (20, 40, 100):
            rs = rows(HERE / f"results-raw/{s}/legs/size{size}/{s}-g2cmp-30x20000.jsonl")
            assert len(rs) == 30 and {r["seed"] for r in rs} == set(cmp[size])
            ab = sorted(r["seed"] for r in rs if "aborted_streak" in r)
            d = {r["seed"]: team(r) - cmp[size][r["seed"]] for r in rs}
            tm = sum(team(r) for r in rs) / 30
            md = sum(d.values()) / 30
            clean = [v for k, v in d.items() if k not in ab]
            mda = [r["max_distress_age"] for r in rs]
            row = {"trained_mean": round(tm, 3), "paired_mean_delta": round(md, 3),
                   "positive": sum(v > 0 for v in d.values()),
                   "delta_range": [round(min(d.values()), 3), round(max(d.values()), 3)],
                   "aborted_seeds": ab,
                   "clean_only_delta": round(sum(clean) / len(clean), 3) if clean else None,
                   "worst_streak_mean": round(sum(mda) / 30, 1), "worst_streak_max": max(mda)}
            if size in (20, 40):
                row["gate"] = "PASS" if (md >= 0 and tm >= PINNED[size]) else "MISS"
            else:
                row["gate"] = "characterize-only"
            out[f"{s}/{size}"] = row
            print(f"{s} {size:>3}: trained {tm:.3f} delta {md:+.3f} ({row['positive']}/30 +) "
                  f"range {row['delta_range']} streak {row['worst_streak_mean']}/{row['worst_streak_max']} "
                  f"aborts {len(ab)} -> {row['gate']}")
    a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
