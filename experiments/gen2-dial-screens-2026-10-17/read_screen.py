#!/usr/bin/env python3
"""Reader: per-run metrics and the seed-paired sweep table for the Gen 2
dial screens (screen_dials.py's output).

Per run (one trace.jsonl, the full-world per-tick WorldSnapshot):
  mean_happiness      mean over kitty-ticks
  distress_ticks      kitty-ticks with in_distress
  max_distress_streak longest consecutive in_distress run of any kitty
  activity_share      state -> share of kitty-ticks
  refusals            reason -> count (engine refusal records; consent
                      refusals are reason == "consent_declined")

Per sweep value: per-seed metrics, their mean, and the seed-paired
delta against the sweep's ANCHOR value (consent 30 / slack 0) — paired
within seed per the weigh-it practice; a between-value read without
the pairing confounds seed draw with dial effect.

Usage: read_screen.py <sweep-dir> --anchor N --out out.json [--md]
<sweep-dir> is results-raw/<dial> holding v<NN>/config-00-rollout-*/trace.jsonl.
"""
import argparse
import json
import pathlib
import sys


def read_run(trace_path):
    ticks = 0
    kitty_ticks = 0
    happiness_sum = 0.0
    distress_ticks = 0
    streaks = {}
    max_streak = 0
    activity = {}
    refusals = {}
    with open(trace_path) as f:
        for line in f:
            rec = json.loads(line)
            ticks += 1
            for ref in rec["refusals"]:
                reason = ref["reason"]
                refusals[reason] = refusals.get(reason, 0) + 1
            for k in rec["snapshot"]["kitties"]:
                kitty_ticks += 1
                happiness_sum += k["happiness"]
                state = k["activity"]["state"]
                activity[state] = activity.get(state, 0) + 1
                kid = k["id"]
                if k["in_distress"]:
                    distress_ticks += 1
                    streaks[kid] = streaks.get(kid, 0) + 1
                    max_streak = max(max_streak, streaks[kid])
                else:
                    streaks[kid] = 0
    assert ticks > 0, f"empty trace: {trace_path}"
    return {
        "ticks": ticks,
        "kitties": kitty_ticks // ticks,
        "mean_happiness": happiness_sum / kitty_ticks,
        "distress_ticks": distress_ticks,
        "max_distress_streak": max_streak,
        "activity_share": {s: n / kitty_ticks for s, n in sorted(activity.items())},
        "refusals": dict(sorted(refusals.items())),
    }


SCALARS = ["mean_happiness", "distress_ticks", "max_distress_streak"]


def run_scalars(run):
    row = {m: run[m] for m in SCALARS}
    row["play_share"] = run["activity_share"].get("playing", 0.0)
    row["consent_refusals"] = run["refusals"].get("consent_declined", 0)
    return row


def sweep(sweep_dir, anchor):
    sweep_dir = pathlib.Path(sweep_dir)
    values = {}
    for vdir in sorted(sweep_dir.glob("v*")):
        traces = sorted(vdir.glob("config-00-rollout-*/trace.jsonl"))
        assert traces, f"no traces under {vdir}"
        values[int(vdir.name[1:])] = [read_run(t) for t in traces]
    assert anchor in values, f"anchor v{anchor:02d} missing from {sweep_dir}"
    counts = {v: len(runs) for v, runs in values.items()}
    assert len(set(counts.values())) == 1, f"unequal seed counts: {counts}"

    table = {}
    anchor_rows = [run_scalars(r) for r in values[anchor]]
    for value, runs in values.items():
        rows = [run_scalars(r) for r in runs]
        mean = {m: sum(r[m] for r in rows) / len(rows) for m in rows[0]}
        deltas = {m: [r[m] - a[m] for r, a in zip(rows, anchor_rows)]
                  for m in rows[0]}
        table[value] = {
            "seeds": len(rows),
            "per_seed": rows,
            "mean": mean,
            "paired_delta_mean": {m: sum(d) / len(d) for m, d in deltas.items()},
            "paired_delta_range": {m: [min(d), max(d)] for m, d in deltas.items()},
        }
    return {"anchor": anchor, "values": table}


def markdown(result):
    cols = ["mean_happiness", "play_share", "consent_refusals",
            "distress_ticks", "max_distress_streak"]
    lines = ["| value | " + " | ".join(cols) + " | Δhappiness vs anchor (paired) |",
             "|" + "---|" * (len(cols) + 2)]
    for value in sorted(result["values"]):
        row = result["values"][value]
        cells = [f"{row['mean'][c]:.3f}" if c in ("mean_happiness", "play_share")
                 else f"{row['mean'][c]:.1f}" for c in cols]
        d = row["paired_delta_mean"]["mean_happiness"]
        lo, hi = row["paired_delta_range"]["mean_happiness"]
        tag = " (anchor)" if value == result["anchor"] else ""
        lines.append(f"| {value}{tag} | " + " | ".join(cells)
                     + f" | {d:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep_dir")
    ap.add_argument("--anchor", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    result = sweep(a.sweep_dir, a.anchor)
    pathlib.Path(a.out).write_text(json.dumps(result, indent=1))
    if a.md:
        print(markdown(result))


if __name__ == "__main__":
    main()
