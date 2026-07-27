#!/usr/bin/env python3
"""Probe-guided training-world search (exp-001; see FINDINGS.md F-003).

For each named candidate: patch the base config (family-gen), measure the
credit signal (twin-probe) and the scripted-baseline welfare (kitty-eval),
and emit one JSON row. The quantity being maximized is the ABSOLUTE
discounted significant team-reward signal

    S(gamma) = sum over significant k of |mean dr_k| * gamma^k

— amplitude and timing in one scalar (the retention *fractions* in
analyze.py deliberately normalize amplitude away; here amplitude is the
point). Constraint: needs_driven stays welfare-passing with margin
(team welfare >= 0.78 on every seed) — the training world must stress
cats, not break the constitution's welfare expectations.

Methodology matches analyze.py: significance = |across-sample mean| > 2*SE
per tick; contiguous bands are the signal, isolated blips are judged
against the 5% base rate.

Usage: search.py [--candidates a,b,c] [--samples 600] [--list]
Rows append to <workdir>/results.jsonl (one line per candidate, rerun
overwrites the row by re-append; last row wins downstream).
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORKDIR = REPO / "experiments" / "exp-001-bc-mappo" / "raw" / "world-search"
FAMILY_GEN = REPO / "experiments" / "tools" / "family-gen" / "target" / "release" / "family-gen"
TWIN_PROBE = REPO / "experiments" / "tools" / "twin-probe" / "target" / "release" / "twin-probe"
KITTY_EVAL = REPO / "target" / "release" / "kitty-eval"
BASE = REPO / "training.toml"

# 100 worlds, ~10 samples each: samples within one world share long-lived
# state, so the effective N for slow common-mode signal is the number of
# WORLDS, not the number of samples. 20 worlds produced a failed
# replication (rates150 S995 0.188 on seeds 101-120 vs 0.037 on 201-220);
# the statistics below cluster by world for the same reason.
DEFAULT_SEED_START = 1001  # replication batches pass a disjoint start
EVAL_SEEDS = "1,2,3"
EVAL_TICKS = 20_000
TRACE_LEN = 1200
GAMMAS = (0.995, 0.998)
WELFARE_FLOOR = 0.78

# Rate patches are multiples of the engine DEFAULT rates (eat/drink 0.4,
# sleep 0.28, play/cuddle 0.4, bath 0.2); the base training.toml is x1.25.
def rates(mult):
    return [
        f"needs.eat={0.4 * mult}",
        f"needs.drink={0.4 * mult}",
        f"needs.sleep={0.28 * mult}",
        f"needs.play={0.4 * mult}",
        f"needs.cuddle={0.4 * mult}",
        f"needs.bath={0.2 * mult}",
    ]

SCARCITY_1 = [
    "elements.water.min=3", "elements.water.max=4",
    "elements.chow.min=3", "elements.chow.max=4",
    "elements.sunbeam.min=2", "elements.sunbeam.max=2",
]
SCARCITY_2 = [
    "elements.water.min=2", "elements.water.max=3",
    "elements.chow.min=2", "elements.chow.max=3",
    "elements.sunbeam.min=1", "elements.sunbeam.max=2",
]
GRID_20 = ["world.width=20", "world.height=20"]

CANDIDATES = {
    # The current training.toml, measured under identical search settings
    # so every S value in the table is apples-to-apples.
    "base": [],
    # One factor at a time.
    "scarcity1": SCARCITY_1,
    "scarcity2": SCARCITY_2,
    "rates150": rates(1.5),
    "grid20": GRID_20,
    # Combinations of the plausible winners.
    "scarcity1-rates150": SCARCITY_1 + rates(1.5),
    "scarcity1-grid20": SCARCITY_1 + GRID_20,
    "scarcity1-rates150-grid20": SCARCITY_1 + rates(1.5) + GRID_20,
    # Adaptive round 2 (after round 1: tempo dominates, scarcity dilutes).
    "rates175": rates(1.75),
    "rates150-grid20": rates(1.5) + GRID_20,
}


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, capture_output=True, text=True, **kw)


def mean_se(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def contiguous(ks):
    runs, start, prev = [], None, None
    for k in ks:
        if start is None:
            start = prev = k
        elif k == prev + 1:
            prev = k
        else:
            runs.append((start, prev))
            start = prev = k
    if start is not None:
        runs.append((start, prev))
    return runs


def channel_metrics(traces, world_seeds):
    """Cluster-robust significance: samples from the same world are
    correlated, so each tick's mean/SE is computed over per-world means
    (cluster = world seed), not over raw samples."""
    k_len = len(traces[0])
    by_world = {}
    for tr, ws in zip(traces, world_seeds):
        by_world.setdefault(ws, []).append(tr)
    world_means = [
        [sum(tr[k] for tr in trs) / len(trs) for k in range(k_len)]
        for trs in by_world.values()
    ]
    stats = [mean_se([wm[k] for wm in world_means]) for k in range(k_len)]
    absm = {k: abs(m) for k, (m, se) in enumerate(stats) if abs(m) > 2 * se}
    if not absm:
        return {"significant_ticks": 0}
    total = sum(absm.values())
    bands = contiguous(sorted(absm))
    # Bands of length >= 3 are the signal, per the prereg's contiguous-band
    # reading; isolated significant ticks at late k carry diffusion-scale
    # amplitudes and are dominated by the 5% false-positive base rate, so S
    # and the peak are computed over band ticks ONLY — otherwise the noise
    # floor rises with trace length and inflates every candidate's score.
    real_bands = [b for b in bands if b[1] - b[0] >= 2]
    band_ticks = {k: absm[k] for lo, hi in real_bands for k in range(lo, hi + 1) if k in absm}
    scored = band_ticks or absm
    peak_k = max(scored, key=scored.get)
    return {
        "significant_ticks": len(absm),
        "band_ticks": len(band_ticks),
        "expected_fp": round(0.05 * k_len),
        "bands": real_bands[:12],
        "peak_k": peak_k,
        "peak_amp": scored[peak_k],
        "last_band_end": real_bands[-1][1] if real_bands else bands[-1][1],
        "mass_le_200": sum(v for k, v in absm.items() if k <= 200) / total,
        "mass_le_400": sum(v for k, v in absm.items() if k <= 400) / total,
        **{
            f"S_{g}": sum(v * g**k for k, v in scored.items())
            for g in GAMMAS
        },
        # Late-truncated variant: at gamma=0.998 even k~600 retains 30%, so
        # late correlated-diffusion bands can sway the score; k<=600 keeps
        # the comparison on the part of the horizon a critic can plausibly
        # exploit and the probe measures well.
        **{
            f"S_{g}_le600": sum(v * g**k for k, v in scored.items() if k <= 600)
            for g in GAMMAS
        },
    }


def welfare_metrics(eval_json):
    d = json.loads(Path(eval_json).read_text())
    team = [r["aggregates"]["team_welfare"] for r in d["runs"]]
    bounds_ok = all(
        all(
            k["mean_happiness"] >= 70
            and k["max_low_streak"] <= 20
            and k["low_share"] <= 0.01
            and k["floor_touches"] == 0
            for k in r["report"]["kitties"]
        )
        and r["report"]["max_distress_age"] <= 150
        and all(p["streak"] <= 25 for p in r["report"]["pinned"])
        and r["fallback_count"] == 0
        for r in d["runs"]
    )
    return {
        "team_welfare_min": min(team),
        "team_welfare_mean": sum(team) / len(team),
        "least_happy_min": min(r["aggregates"]["least_happy_mean"] for r in d["runs"]),
        "bounds_pass": bounds_ok,
    }


def evaluate(name, patches, samples, seed_start):
    WORKDIR.mkdir(parents=True, exist_ok=True)
    tag = "" if seed_start == DEFAULT_SEED_START else f".w{seed_start}"
    probe_seeds = ",".join(str(s) for s in range(seed_start, seed_start + 100))
    cfg = WORKDIR / f"{name}.toml"
    jsonl = WORKDIR / f"{name}{tag}.probe.jsonl"
    evalj = WORKDIR / f"{name}.eval.json"

    if patches:
        gen = [FAMILY_GEN, "--base", BASE, "--out", cfg]
        for p in patches:
            gen += ["--set", p]
        run(gen)
    else:
        cfg = BASE

    run([
        TWIN_PROBE, "--config", cfg, "--samples", samples, "--trace-len", TRACE_LEN,
        "--seeds", probe_seeds, "--probe-seed", 42, "--quiet", "--out", jsonl,
    ])
    run([
        KITTY_EVAL, "--brain", "needs_driven", "--config", cfg,
        "--seeds", EVAL_SEEDS, "--ticks", EVAL_TICKS, "--json", evalj,
    ])

    recs = [json.loads(line) for line in open(jsonl)]
    seeds = [r["world_seed"] for r in recs]
    dr = channel_metrics([r["dr"] for r in recs], seeds)
    spill_traces = []
    for r in recs:
        kid = str(r["kitty_id"])
        rest = [tr for k_id, tr in r["dh"].items() if k_id != kid]
        spill_traces.append([sum(vals) / len(vals) for vals in zip(*rest)])
    spill = channel_metrics(spill_traces, seeds)

    row = {
        "name": name,
        "patches": patches,
        "samples": len(recs),
        "seed_start": seed_start,
        "dr": dr,
        "spillover": spill,
        "welfare": welfare_metrics(evalj),
    }
    row["feasible"] = (
        row["welfare"]["bounds_pass"]
        and row["welfare"]["team_welfare_min"] >= WELFARE_FLOOR
    )
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=None, help="comma-separated subset")
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--seed-start", type=int, default=DEFAULT_SEED_START)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for name, patches in CANDIDATES.items():
            print(f"{name}: {patches}")
        return

    names = args.candidates.split(",") if args.candidates else list(CANDIDATES)
    results_path = WORKDIR / "results.jsonl"
    for name in names:
        if name not in CANDIDATES:
            sys.exit(f"unknown candidate {name!r}; --list shows the menu")
        row = evaluate(name, CANDIDATES[name], args.samples, args.seed_start)
        WORKDIR.mkdir(parents=True, exist_ok=True)
        with open(results_path, "a") as f:
            f.write(json.dumps(row) + "\n")
        w, dr = row["welfare"], row["dr"]
        print(
            f"{name}: S(.995)={dr.get('S_0.995', 0):.2e} S(.998)={dr.get('S_0.998', 0):.2e} "
            f"peak_k={dr.get('peak_k')} band_end={dr.get('last_band_end')} "
            f"welfare_min={w['team_welfare_min']:.3f} bounds={'PASS' if w['bounds_pass'] else 'FAIL'} "
            f"feasible={row['feasible']}"
        )


if __name__ == "__main__":
    main()
