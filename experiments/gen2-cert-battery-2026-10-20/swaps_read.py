#!/usr/bin/env python3
"""Swaps digest reader (SWAPS-DECLARATION.md §Read; report-only, nothing
gates): every `results-raw/swaps/g2-rot2-swap<k>-<net>/legs/size20/` leg
against the certified rot2 20×20 leg on the same 30 worlds (paired by
seed): team-happiness delta (mean ± SD, sign count), the swapped seat's
own happiness delta, worst distress streak mean/max, F-053 line events
and aborts, and the holding account beside rot2's. Per alternate, the
five seats side by side; pooled over every leg read, the mean paired
delta of a one-seat swap.

    swaps_read.py --out swaps-read.json --md
"""
import argparse
import json
import re
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROT2 = HERE / "results-raw/g2-rot2/legs/size20/g2-rot2-g2cmp-30x20000.jsonl"
SWAPS = HERE / "results-raw/swaps"
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
F053 = 1000
NAME = re.compile(r"^g2-rot2-swap(\d)-(s\d+)$")


def by_seed(p):
    lines = p.read_text().splitlines()
    return json.loads(lines[0]), {r["seed"]: r for r in (json.loads(l) for l in lines[1:])}


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def msd(xs):
    sd = st.stdev(xs) if len(xs) > 1 else None
    return {"n": len(xs), "mean": st.mean(xs), "sd": sd}


def holding(X, seeds):
    h = [X[w]["holding"] for w in seeds]
    return {"held_share_max_cat": max(max(x["held_share"]) for x in h),
            "held_longest_max": max(max(x["held_longest"]) for x in h),
            "shared_hold_longest_max": max(x["shared_hold_longest"] for x in h),
            "worlds_with_shared_hold": sum(x["shared_hold_ticks"] > 0 for x in h)}


def welfare(X, seeds):
    mda = [X[w].get("max_distress_age", 0) for w in seeds]
    return {"worst_streak_mean": sum(mda) / len(mda), "worst_streak_max": max(mda),
            "f053_events": sum(m >= F053 for m in mda),
            "aborts": sum("aborted_streak" in X[w] for w in seeds)}


def seat_of(seating):
    m = NAME.match(seating)
    assert m, seating
    return int(m.group(1)), m.group(2)


def read_leg(seating, R, seeds):
    k, net = seat_of(seating)
    head, S = by_seed(SWAPS / seating / "legs/size20" / f"{seating}-g2cmp-30x20000.jsonl")
    assert set(S) == set(seeds) and len(S) == 30, (seating, len(S))
    assert head["seats"][k] == f"g2:trunk-{net}", (seating, head["seats"])
    assert [s for i, s in enumerate(head["seats"]) if i != k] == \
           [s for i, s in enumerate(R[seeds[0]]["seats"]) if i != k], (seating, head["seats"])
    delta = [team(S[w]) - team(R[w]) for w in seeds]
    seat_delta = [S[w]["mean_happiness"][k] - R[w]["mean_happiness"][k] for w in seeds]
    return {"seating": seating, "seat": k, "seat_name": SEATS[k], "alternate": net,
            "team": msd([team(S[w]) for w in seeds]),
            "delta": dict(msd(delta), positive=sum(d > 0 for d in delta)),
            "seat_delta": dict(msd(seat_delta), positive=sum(d > 0 for d in seat_delta)),
            "welfare": welfare(S, seeds), "holding": holding(S, seeds),
            "per_world_delta": delta, "config_sha256": head["provenance"]["config_sha256"]}


def read():
    rhead, R = by_seed(ROT2)
    seeds = sorted(R)
    legs = []
    for d in sorted(SWAPS.glob("g2-rot2-swap*-s*")):
        f = d / "legs/size20" / f"{d.name}-g2cmp-30x20000.jsonl"
        if f.exists():
            legs.append(read_leg(d.name, R, seeds))
    legs.sort(key=lambda l: (l["alternate"], l["seat"]))
    out = {"rot2": {"team": msd([team(R[w]) for w in seeds]), "welfare": welfare(R, seeds),
                    "holding": holding(R, seeds), "config_sha256": rhead["provenance"]["config_sha256"]},
           "legs": legs, "alternates": {}}
    for net in sorted({l["alternate"] for l in legs}):
        mine = [l for l in legs if l["alternate"] == net]
        out["alternates"][net] = {"legs": len(mine), "seats_read": [l["seat"] for l in mine],
                                  "mean_delta_over_legs": st.mean(l["delta"]["mean"] for l in mine),
                                  "worst_streak_max": max(l["welfare"]["worst_streak_max"] for l in mine),
                                  "aborts": sum(l["welfare"]["aborts"] for l in mine)}
    out["pooled"] = {"legs": len(legs),
                     "mean_delta": st.mean(l["delta"]["mean"] for l in legs) if legs else None,
                     "all_per_world_deltas": msd([d for l in legs for d in l["per_world_delta"]]) if legs else None}
    return out


def md(out):
    r = out["rot2"]
    L = [f"rot2 20×20: team {r['team']['mean']:.3f} ± {r['team']['sd']:.3f}; worst streak {r['welfare']['worst_streak_mean']:.1f} / "
         f"{r['welfare']['worst_streak_max']}; F-053 events {r['welfare']['f053_events']}; held share max {r['holding']['held_share_max_cat']:.3f}, "
         f"held longest {r['holding']['held_longest_max']}, shared hold longest {r['holding']['shared_hold_longest_max']}",
         "", "| swap | seat | team | Δ team (sd) | +/30 | Δ seat | worst streak mean / max | ≥ line | aborts | held max / longest / shared |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for l in out["legs"]:
        w, h = l["welfare"], l["holding"]
        L.append(f"| {l['alternate']} | {l['seat']} {l['seat_name']} | {l['team']['mean']:.3f} | {l['delta']['mean']:+.3f} ({l['delta']['sd']:.3f}) | "
                 f"{l['delta']['positive']} | {l['seat_delta']['mean']:+.3f} | {w['worst_streak_mean']:.1f} / {w['worst_streak_max']} | "
                 f"{w['f053_events']} | {w['aborts']} | {h['held_share_max_cat']:.3f} / {h['held_longest_max']} / {h['shared_hold_longest_max']} |")
    for net, a in out["alternates"].items():
        L.append(f"\n{net}: {a['legs']} legs, mean Δ over legs {a['mean_delta_over_legs']:+.3f}, worst streak {a['worst_streak_max']}, aborts {a['aborts']}")
    p = out["pooled"]
    if p["legs"]:
        L.append(f"pooled over {p['legs']} legs: mean Δ {p['mean_delta']:+.3f}; all per-world deltas {p['all_per_world_deltas']['mean']:+.3f} ± {p['all_per_world_deltas']['sd']:.3f}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "swaps-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
