#!/usr/bin/env python3
"""The needs trigger's read on the needs-only arm (DECLARATION.md §6, §7 N4): the lived grave bias at every probe
(the trainer's metrics.jsonl) and on the arm's recorded legs. Phase 2's reader is imported, never copied
(read_canary: trajectory, trajectory_summary, needs_leg). needs_leg steps the frozen needs head over a recorded
leg's observations; the head and the observations are the same whichever arm's cells carry it, so Phase 2's function
reads this arm's legs unchanged (guard n6 proves it on a recorded world). Zero covered cost.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_trigger_needs.py leg <size> --out reads/trigger/needs-leg-<size>.json     (about 2 min)
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_trigger_needs.py score --dir reads/trigger --out reads/trigger/score.json [--md]
(A = experiments/minifriend-phase2-2026-11-06.)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import read_canary as RC  # noqa: E402
import read_r1_needs as R1N  # noqa: E402  (leg: the header fence on the arm's final)

SEED, SIZES = 1, (20, 40, 100)
SEATING, SLOT = f"p2u-needs-s{SEED}", f"p2-needs-s{SEED}"


def fires(states):
    """The trigger's read fires when either version (in sight, all rows) shows the SIGNATURE at min-n."""
    return any(s == "SIGNATURE" for s in states.values())


def leg(size, seeds=None, final=None):
    R1N.leg(SEED, size, final=final)                       # raises unless the leg seats the arm's final
    return RC.needs_leg(SEATING, size, seeds)


def score(d):
    series = RC.trajectory((C.ARTS / SLOT / "metrics.jsonl").read_text().splitlines())
    out = {"probes": {v: RC.trajectory_summary(series, v) for v in ("visible", "all")},
           "probes_fired": [s["update"] for s in series if fires({v: c["state"] for v, c in s["cumulative"].items()})],
           "last_probe": series[-1]["cumulative"], "legs": {}, "missing": []}
    for size in SIZES:
        f = d / f"needs-leg-{size}.json"
        if not f.exists():
            out["missing"].append(size)
            continue
        r = json.loads(f.read_text())
        assert r["seating"] == SEATING and len(r["worlds"]) == 30, f"{f.name}: {r['seating']}, {len(r['worlds'])} worlds — a partial leg is never scored"
        bv = r["pooled"]["by_version"]
        out["legs"][str(size)] = {"state": r["state"], "fires": fires(r["state"]),
                                  "by_version": {v: {k: bv[v][k] for k in ("n_grave", "grave", "grave_sd", "common")} for v in bv}}
    out["N4"] = {"fires": {z: v["fires"] for z, v in out["legs"].items()}, "met_on_the_legs_read": not any(v["fires"] for v in out["legs"].values())}
    return out


def md(out):
    g = lambda v: "—" if v is None else f"{v:+.2f}"
    L = ["# The needs trigger's read on the needs-only arm (p2-needs-s1: every probe, and its recorded legs)", "",
         "Grave bias = the head's estimate minus the friend's true hidden need, in need points, on GRAVE rows; negative = a grave "
         "friend read less needy than she is (the optimism direction). SIGNATURE = grave bias negative and at least 1.5× the "
         "common bias in size, at 200 rows or more in both strata. The read is logged, never a stop (shape (ii)).", "",
         "| leg | version | grave rows | grave bias (SD) | common bias | state |", "|---|---|---|---|---|---|"]
    for z, v in out["legs"].items():
        for ver, c in v["by_version"].items():
            L.append(f"| {z}×{z} | {ver} | {c['n_grave']:,} | {g(c['grave'])} ({c['grave_sd']:.2f}) | {g(c['common'])} | {v['state'][ver]} |")
    L += ["", "Not read: " + (", ".join(f"{z}×{z}" for z in out["missing"]) or "none") + ".", "",
          "| probes | version | cumulative state INSUFFICIENT / CLEAR / SIGNATURE (probes) | first sufficient update | last probe: grave rows, grave bias, state |", "|---|---|---|---|---|"]
    for ver, s in out["probes"].items():
        c, last = s["cumulative_states"], out["last_probe"][ver]
        L.append(f"| {s['n_probes']} | {ver} | {c['INSUFFICIENT']} / {c['CLEAR']} / {c['SIGNATURE']} | {s['first_sufficient_update']} | {last['n_grave']:,}, {g(last['grave'])}, {last['state']} |")
    L += ["", f"Probes at which the cumulative read fired (updates): {out['probes_fired'] or 'none'}.", "",
          f"**N4 {'MET' if out['N4']['met_on_the_legs_read'] else 'NOT MET'} on the legs read** (fires: {out['N4']['fires']})."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("leg"); a.add_argument("size", type=int); a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("score"); b.add_argument("--dir", type=Path, required=True); b.add_argument("--out", type=Path, required=True)
    b.add_argument("--md", action="store_true")
    args = ap.parse_args()
    if args.cmd == "leg":
        res = leg(args.size)
    else:
        res = score(args.dir)
        if args.md:
            args.out.with_suffix(".md").write_text(md(res))
        print(json.dumps(res["N4"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
