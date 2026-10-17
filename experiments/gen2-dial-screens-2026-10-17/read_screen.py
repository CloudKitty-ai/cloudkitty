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
    k_happy = {}
    k_act = {}
    k_part = {}
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
                a = k["activity"]
                state = a["state"]
                activity[state] = activity.get(state, 0) + 1
                kid = k["id"]
                k_happy[kid] = k_happy.get(kid, 0.0) + k["happiness"]
                k_act.setdefault(kid, {})
                k_act[kid][state] = k_act[kid].get(state, 0) + 1
                # Partnered variant: Resting/Sleeping carry with_friend,
                # Playing/Grooming carry target, when the scene has one.
                if a.get("with_friend") is not None or a.get("target") is not None:
                    k_part.setdefault(kid, {})
                    k_part[kid][state] = k_part[kid].get(state, 0) + 1
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
        "kitty_happiness": {kid: s / ticks for kid, s in sorted(k_happy.items())},
        "kitty_activity_share": {kid: {s: n / ticks for s, n in sorted(d.items())}
                                 for kid, d in sorted(k_act.items())},
        "kitty_partnered_share": {kid: {s: n / ticks for s, n in sorted(d.items())}
                                  for kid, d in sorted(k_part.items())},
    }


SCALARS = ["mean_happiness", "distress_ticks", "max_distress_streak"]

# Favourite screen (owner kickoff 2026-10-17): the stand-in assignment
# (screen_dials.FAVOURITES; deployed assignment is her freeze call) and
# each favourite's expressing trace signature. Cuddle = PARTNERED
# resting (with_friend set); bath = grooming (self-groom is the cat's
# own bath relief); Pumpkin (id 3) carries no favourite, the control.
KITTY_NAMES = {1: "Miso", 2: "Biscuit", 3: "Pumpkin",
               4: "Kittybear", 5: "Clementine"}
FAV_EXPRESSION = {
    1: ("cuddle", "kitty_partnered_share", "resting"),
    2: ("play", "kitty_activity_share", "playing"),
    4: ("bath", "kitty_activity_share", "grooming"),
    5: ("sleep", "kitty_activity_share", "sleeping"),
}


def _stats(rows, anchor_rows):
    deltas = [r - a for r, a in zip(rows, anchor_rows)]
    return {"per_seed": rows, "mean": sum(rows) / len(rows),
            "delta_mean": sum(deltas) / len(deltas),
            "delta_range": [min(deltas), max(deltas)]}


def fav_view(values, anchor):
    """Per value: each favourite kitty's expression-state share and every
    seat's happiness, seed-paired against the anchor like the main table."""
    def expr(run, kid):
        _, table, state = FAV_EXPRESSION[kid]
        return run[table].get(kid, {}).get(state, 0.0)
    anchor_runs = values[anchor]
    out = {}
    for value, runs in values.items():
        expression = {}
        for kid, (kind, _, state) in sorted(FAV_EXPRESSION.items()):
            label = f"{KITTY_NAMES[kid]} {kind} ({state})"
            expression[label] = _stats([expr(r, kid) for r in runs],
                                       [expr(r, kid) for r in anchor_runs])
        seat = {}
        for kid, name in sorted(KITTY_NAMES.items()):
            seat[name] = _stats([r["kitty_happiness"][kid] for r in runs],
                                [r["kitty_happiness"][kid] for r in anchor_runs])
        out[value] = {"expression": expression, "seat_happiness": seat}
    return out


def run_scalars(run):
    row = {m: run[m] for m in SCALARS}
    row["play_share"] = run["activity_share"].get("playing", 0.0)
    row["consent_refusals"] = run["refusals"].get("consent_declined", 0)
    return row


def sweep(sweep_dir, anchor, fav=False):
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
    result = {"anchor": anchor, "values": table}
    if fav:
        result["fav"] = fav_view(values, anchor)
    return result


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


def markdown_fav(result):
    fav = result["fav"]
    labels = sorted(next(iter(fav.values()))["expression"])
    lines = ["| value | " + " | ".join(labels) + " |",
             "|" + "---|" * (len(labels) + 1)]
    for value in sorted(fav):
        cells = [f"{fav[value]['expression'][l]['mean']:.3f} "
                 f"({fav[value]['expression'][l]['delta_mean']:+.3f})"
                 for l in labels]
        tag = " (anchor)" if value == result["anchor"] else ""
        lines.append(f"| {value}{tag} | " + " | ".join(cells) + " |")
    names = sorted(next(iter(fav.values()))["seat_happiness"])
    lines += ["", "| value | " + " | ".join(f"{n} happiness" for n in names) + " |",
              "|" + "---|" * (len(names) + 1)]
    for value in sorted(fav):
        cells = [f"{fav[value]['seat_happiness'][n]['mean']:.3f} "
                 f"({fav[value]['seat_happiness'][n]['delta_mean']:+.3f})"
                 for n in names]
        tag = " (anchor)" if value == result["anchor"] else ""
        lines.append(f"| {value}{tag} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep_dir")
    ap.add_argument("--anchor", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--fav", action="store_true",
                    help="add the favourite expression + per-seat view")
    a = ap.parse_args()
    result = sweep(a.sweep_dir, a.anchor, fav=a.fav)
    pathlib.Path(a.out).write_text(json.dumps(result, indent=1))
    if a.md:
        print(markdown(result))
        if a.fav:
            print()
            print(markdown_fav(result))


if __name__ == "__main__":
    main()
