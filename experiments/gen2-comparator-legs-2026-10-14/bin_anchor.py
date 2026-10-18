#!/usr/bin/env python3
"""Bin-anchor read (owner, freeze sitting 2026-10-17, "Agreed"): record
the Gen 2 SEMANTIC ANCHOR of the doctrine bin edges (happiness 45/70 +
the need-90 distress edge) before the freeze, so the banked Gen 3
re-anchor obligation has a committed Gen 2 reference to bridge against.

For each leg size, replays the band's first seeds (the scout seeds)
with bc-collect --trace on the law config, streams the per-tick
snapshots, and derives per kitty-tick:

- bin occupancy: happiness < 45 / 45-70 / > 70;
- the engine's own distress flags (`in_distress`, edge list at
  thresholds.distress = 90 -- ground truth, never re-derived from
  needs) and the happiness distribution conditioned on flagged vs
  unflagged ticks;
- per-need flag tick counts;
- the discrimination pair P(flag | hap < 45) vs P(flag | hap > 70).

Traces land in a scratch dir (regenerable: the capture is
deterministic from seed + config + binary) and only the derived JSON
is kept, one file per size in results-raw/bin-anchor/.

    python3 -B bin_anchor.py --scratch DIR [--sizes 20,40,100]
        [--seeds 905001,905002,905003] [--ticks 20000]

Hard checks: trace row count == ticks, roster == 5 every tick,
happiness/needs present on every kitty.
"""
import argparse
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BC = HERE.parents[1] / "experiments/tools/bc-collect/target/release/bc-collect"
ROSTER = 5
NEED_KINDS = ("eat", "drink", "sleep", "cuddle", "bath", "play")


def capture(config, seed, ticks, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(BC), "--config", str(config), "--rollouts", "1",
                        "--ticks", str(ticks), "--seed-base", str(seed),
                        "--out-dir", str(out_dir), "--trace"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"bc-collect seed {seed} failed:\n{r.stderr[-400:]}")
    return out_dir / "config-00-rollout-00" / "trace.jsonl"


def read_trace(trace_path, ticks, acc):
    n = 0
    with open(trace_path) as f:
        for line in f:
            row = json.loads(line)
            kitties = row["snapshot"]["kitties"]
            assert len(kitties) == ROSTER, (trace_path, row["tick"])
            for k in kitties:
                hap = k["happiness"]
                flagged = bool(k["in_distress"])
                acc["kitty_ticks"] += 1
                bin_ = "lt45" if hap < 45 else ("b45_70" if hap < 70 else "gt70")
                acc["occ"][bin_] += 1
                side = "flag" if flagged else "noflag"
                acc[side]["n"] += 1
                acc[side]["hap"].append(hap)
                if flagged:
                    for need in k["in_distress"]:
                        acc["flag_by_need"][need] += 1
                acc["joint"][(bin_, side)] += 1
            n += 1
    assert n == ticks, (trace_path, n, ticks)


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, round(q * (len(sorted_vals) - 1))))
    return sorted_vals[i]


def summarize(acc, sizes_meta):
    out = dict(sizes_meta)
    kt = acc["kitty_ticks"]
    out["kitty_ticks"] = kt
    out["occupancy_share"] = {b: acc["occ"][b] / kt for b in acc["occ"]}
    for side in ("flag", "noflag"):
        vals = sorted(acc[side]["hap"])
        n = acc[side]["n"]
        out[side] = {
            "n": n, "share": n / kt,
            "hap_median": quantile(vals, 0.5),
            "hap_p10": quantile(vals, 0.10),
            "hap_p90": quantile(vals, 0.90),
            "share_lt45": (sum(v < 45 for v in vals) / n) if n else None,
            "share_lt70": (sum(v < 70 for v in vals) / n) if n else None,
        }
    out["flag_ticks_by_need"] = dict(sorted(acc["flag_by_need"].items()))
    lt45 = acc["occ"]["lt45"]
    gt70 = acc["occ"]["gt70"]
    out["p_flag_given_lt45"] = acc["joint"][("lt45", "flag")] / lt45 if lt45 else None
    out["p_flag_given_gt70"] = acc["joint"][("gt70", "flag")] / gt70 if gt70 else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--sizes", default="20,40,100")
    ap.add_argument("--seeds", default="905001,905002,905003")
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--out-dir", type=Path, default=HERE / "results-raw/bin-anchor")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")]
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for size in (int(s) for s in a.sizes.split(",")):
        config = HERE / f"g2leg-{size}.toml"
        acc = {"kitty_ticks": 0,
               "occ": {"lt45": 0, "b45_70": 0, "gt70": 0},
               "flag": {"n": 0, "hap": []}, "noflag": {"n": 0, "hap": []},
               "flag_by_need": {k: 0 for k in NEED_KINDS},
               "joint": {(b, s): 0 for b in ("lt45", "b45_70", "gt70")
                         for s in ("flag", "noflag")}}
        for seed in seeds:
            trace = capture(config, seed, a.ticks,
                            a.scratch / f"size{size}-seed{seed}")
            read_trace(trace, a.ticks, acc)
            print(f"size{size} seed {seed}: read", flush=True)
        meta = {"config": config.name, "seeds": seeds, "ticks": a.ticks,
                "distress_edge": 90.0, "happiness_edges": [45.0, 70.0]}
        summary = summarize(acc, meta)
        p = a.out_dir / f"anchor-{size}.json"
        p.write_text(json.dumps(summary, indent=1))
        print(f"wrote {p}", flush=True)


if __name__ == "__main__":
    main()
