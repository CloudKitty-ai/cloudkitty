#!/usr/bin/env python3
"""The tails beside seeds 2 and 4 of the re-anchor arm (deviations entry 41; a dump, it scores nothing): per seed,
the worst streak, the worlds with a streak of 300+ and the aborts of the arm's legs and of the recorded legs it is
read beside (trunk seed k, the no-head arm's 2M checkpoint and its final); for the arm's 40×40 leg the 30 worlds'
worst streaks in order, and each aborted world's row (ticks, the streak by seat, the streak's need and shape).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_tails_seeds.py --out reads/tails-seeds.json     (seconds)
"""
import argparse
import json
import statistics
from pathlib import Path

import read_reanchor as RR

C, K = RR.C, RR.K


def tail(rows):
    t = RR.tail(rows)
    return {"worlds": len(rows), "worst_streak": t["worst_streak"], "worlds_300": t["worlds_300"], "aborts": t["aborts"], "team_mean": round(t["team_mean"], 3)}


def read():
    out = {}
    for k in (2, 4):
        arm40 = RR.leg(f"reanchor-s{k}", 40, RR.RAW_SEEDS)
        streaks = sorted(r["max_distress_age"] for r in arm40.values())
        out[str(k)] = {
            "trunk@20": tail(C.battery_rows(f"g2-s{k}", 20)), "trunk@40": tail(C.battery_rows(f"g2-s{k}", 40)),
            "nohead_final@40": tail(RR.leg(f"p2u-nohead-s{k}", 40, C.RAW)), "nohead_2M@40": tail(RR.leg(f"r6-nohead-s{k}-u651", 40, K / "results-raw")),
            "reanchor@20": tail(RR.leg(f"reanchor-s{k}", 20, RR.RAW_SEEDS)), "reanchor@40": tail(arm40),
            "reanchor@40_streaks": streaks, "reanchor@40_streak_median": statistics.median(streaks),
            "reanchor@40_aborted": {str(s): {"ticks": r["ticks"], "streak_by_seat": r["max_distress_age_seat"],
                                             "shape": [x for x in r["streak_shape"] if x["length"] >= 1000]} for s, r in arm40.items() if "aborted_streak" in r}}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for k, v in out.items():
        print(f"seed {k}")
        for name, t in v.items():
            print(f"  {name}: {json.dumps(t)}")
