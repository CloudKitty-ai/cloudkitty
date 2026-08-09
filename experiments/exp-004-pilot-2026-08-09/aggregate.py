#!/usr/bin/env python3
"""Aggregates the 30-cell dial-pricing pilot (prereg §6).

Per cell, across the 10 paired seeds: welfare (with per-seed paired delta
vs the d15-mon-c15 control), cosleep volume and contact durations,
mutual-vs-passive share, announce-legal cuddle share (above-30 mark),
rest-duet volume and durations, groom-trade ticks and wage delivered,
and the F-016 water check. Emits summary.json + a markdown table.
"""

import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).parent
CENSUS = ROOT / "census"
CONTROL = "d15-mon-c15"
SEEDS = list(range(820001, 820011))
TICKS = 20_000
MUTUAL_IDX = (1, 2)  # partner Resting, Sleeping


def cell_relief(cell: str) -> float:
    return float(cell.split("-c")[1])


def load(cell: str, seed: int) -> dict:
    return json.load(open(CENSUS / cell / f"seed-{seed}.json"))


def seed_metrics(d: dict, relief: float) -> dict:
    ks = d["kitties"].values()
    kitty_ticks = len(d["kitties"]) * TICKS
    serviced = sum(k["cosleep_serviced"] for k in ks)
    runs = [
        r
        for k in ks
        for ep in k["cosleep_episodes"]
        for r in ep["contact_runs"]
    ]
    pact = [sum(k["partner_activity_on_serviced"][i] for k in ks) for i in range(7)]
    pact_total = sum(pact) or 1
    duet_lens = [x for k in ks for x in k["rest_duet_lens"]]
    groom_ticks = sum(k["groom_actor_ticks"] for k in ks)
    return {
        "welfare": d["mean_team_reward"],
        "cosleep_serviced_per_1k": 1000 * serviced / kitty_ticks,
        "contact_run_mean": st.mean(runs) if runs else 0.0,
        "mutual_share": sum(pact[i] for i in MUTUAL_IDX) / pact_total,
        "above30_share": sum(k["cuddle_above"][0] for k in ks) / kitty_ticks,
        "duet_ticks_per_1k": 1000 * sum(k["rest_duet_ticks"] for k in ks) / kitty_ticks,
        "duet_len_mean": st.mean(duet_lens) if duet_lens else 0.0,
        "groom_ticks_per_1k": 1000 * groom_ticks / kitty_ticks,
        "groom_wage_per_1k": 1000 * groom_ticks * relief / kitty_ticks,
        "water_tiles": d["mean_water_tiles"],
    }


cells = sorted(p.name for p in CENSUS.iterdir())
per_cell = {}
for cell in cells:
    relief = cell_relief(cell)
    rows = [seed_metrics(load(cell, s), relief) for s in SEEDS]
    agg = {k: st.mean(r[k] for r in rows) for k in rows[0]}
    agg["welfare_sd"] = st.stdev(r["welfare"] for r in rows)
    per_cell[cell] = {"seeds": rows, "mean": agg}

ctrl = per_cell[CONTROL]["seeds"]
for cell in cells:
    deltas = [
        r["welfare"] - c["welfare"]
        for r, c in zip(per_cell[cell]["seeds"], ctrl)
    ]
    per_cell[cell]["mean"]["welfare_delta_vs_control"] = st.mean(deltas)
    per_cell[cell]["mean"]["welfare_delta_sd"] = (
        st.stdev(deltas) if cell != CONTROL else 0.0
    )

json.dump(
    {c: v["mean"] for c, v in per_cell.items()},
    open(ROOT / "summary.json", "w"),
    indent=1,
)

hdr = (
    "| cell | welfare Δ (±sd) | cosleep/1k | contact len | mutual % | "
    "≥30 % | duet/1k | duet len | groom/1k | wage/1k | water |"
)
print(hdr)
print("|" + "---|" * 11)
for cell in cells:
    m = per_cell[cell]["mean"]
    print(
        f"| {cell} | {m['welfare_delta_vs_control']:+.4f} "
        f"(±{m['welfare_delta_sd']:.4f}) | {m['cosleep_serviced_per_1k']:.2f} "
        f"| {m['contact_run_mean']:.2f} | {100 * m['mutual_share']:.1f} "
        f"| {100 * m['above30_share']:.2f} | {m['duet_ticks_per_1k']:.1f} "
        f"| {m['duet_len_mean']:.2f} | {m['groom_ticks_per_1k']:.2f} "
        f"| {m['groom_wage_per_1k']:.1f} | {m['water_tiles']:.2f} |"
    )
