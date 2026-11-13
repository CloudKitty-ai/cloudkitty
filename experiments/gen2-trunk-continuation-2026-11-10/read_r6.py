#!/usr/bin/env python3
"""R-6, the checkpoint ladder (DECLARATION.md §6 R-6, §7 P54; gen2-deviations.md entry 34: 2M rungs on cont-s1, P56;
guards g18–g21). Two lineages from trunk seed 1, every rung a 40×40 battery leg (30 worlds × 20k ticks, g2cmp)
paired PER WORLD ID with the recorded trunk rows g2-s1 and with the rung before it:
  nohead-s1  trunk -> p2-nohead-s1r at ckpt-u1302 / u2604 / u3906 -> its recorded final (p2u-nohead-s1)
  cont-s1    trunk -> cont-s1 at ckpt-u3255 / u3906 / u4557 / u5208 / u5859 -> its final (R-1's 40×40 leg)
Reported per rung: the Δ-to-trunk; per lineage (when every rung is present): the rung of the maximum and the earliest
rung within the 0.325 edge of it; per step between consecutive rungs: the paired gain with its 95% half-width, read
against two candidate lines of the welfare rule (entry 32) — flat 0.10 points per 2M ticks, and 1% of the remaining
shortfall (100 minus the earlier rung's team happiness) per 2M ticks, each scaled linearly to the step's length. A gain
counts only if it also reaches the half-width. Descriptive: no selector, no stop. A rung leg whose header does not
name the rung's own checkpoint by sha256 is never read.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_r6.py --out reads/r6.json [--md]     (seconds; A = Phase 2's arc)
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_r1_cont as R1C  # noqa: E402  (puts Phase 2's arc and the harness on sys.path)
import cert_harness_fog as H  # noqa: E402
C, RP, R1, RAW, P2 = R1C.C, R1C.RP, R1C.R1, R1C.RAW, R1C.P2

SIZE, EDGE, N, T975 = 40, 0.325, 30, 2.045                 # t(0.975, 29): every leg is 30 worlds
TPU = 256 * 12
STEP, FLAT, SHARE = 2_000_000, 0.10, 0.01                  # the candidate lines, per 2M ticks
TRUNK_TICKS = 2_605 * TPU
# lineage -> the trunk's ticks on that lineage's clock, then (seating, legs root, ticks) per rung, the final last.
# The no-head arm counts its own further ticks from 0; the continuation counts the lineage's.
LADDERS = {
    "nohead-s1": (0, [(f"r6-nohead-s1-u{u}", RAW, (u + 1) * TPU) for u in (1302, 2604, 3906)] + [("p2u-nohead-s1", None, 15_000_576)]),
    "cont-s1": (TRUNK_TICKS, [(f"r6-cont-s1-u{u}", RAW, (u + 1) * TPU) for u in (3255, 3906, 4557, 5208, 5859)] + [("cont-s1", RAW, 6_510 * TPU)]),
}


def leg_file(seating, root):
    return RP.legs_dir(seating, SIZE, root) / f"{seating}-g2cmp-{N}x20000.jsonl"


def rung_rows(seating, root, artifact=None):
    """A rung's rows and its checkpoint's sha256; refused unless the leg's header seats the seating's own spec in all
    five seats and names `artifact` (default: the file that spec resolves to today) by sha256."""
    rows, header = RP.leg_rows(seating, SIZE, root)
    spec = H.SEATINGS[seating][0]
    sha = hashlib.sha256(Path(artifact or H.artifact_path(spec)).read_bytes()).hexdigest()
    got = (header["seats"], header["provenance"]["artifacts"])
    assert got == (H.SEATINGS[seating], {spec: sha}), f"{seating}: the leg seats {got[0][0]} at {got[1]}, the rung's checkpoint is {sha}"
    return rows, sha


def step(rows, prev, ticks):
    """One step of a lineage: the paired gain over the rung before, its 95% half-width, the two lines scaled to the
    step's length, and whether the gain reaches each line and the half-width."""
    assert set(rows) == set(prev) and len(rows) == N, f"world sets differ or are not {N}: {len(rows)} against {len(prev)}"
    d = np.asarray([R1.team(rows[s]) - R1.team(prev[s]) for s in sorted(rows)])
    level = float(np.mean([R1.team(prev[s]) for s in prev]))
    hw = float(T975 * d.std(ddof=1) / np.sqrt(N))
    lines = {"flat": FLAT * ticks / STEP, "share": SHARE * (100 - level) * ticks / STEP}
    return {"ticks": ticks, "gain": float(d.mean()), "sd": float(d.std(ddof=1)), "half_width": hw, "prev_team": level, "lines": lines,
            "clears": {k: bool(d.mean() >= max(v, hw)) for k, v in lines.items()}}


def summit(deltas, edge=EDGE):
    """(index of the largest Δ-to-trunk, index of the earliest rung within the edge of it, the largest rung before
    the final minus the final). The final is the last entry."""
    top = int(np.argmax(deltas))
    return top, next(i for i, v in enumerate(deltas) if v >= deltas[top] - edge), max(deltas[:-1]) - deltas[-1]


def p56(deltas, edge=EDGE):
    """P56 (entry 34) on cont-s1's Δ-to-trunk per rung, the final last: (a) positive at every rung, (b) the first
    rung holds under half of the final's (gradual, no step at the resume), (c) no rung over the final by more than the edge."""
    out = {"a_positive_every_rung": all(v > 0 for v in deltas), "b_first_rung_under_half_of_final": deltas[0] < 0.5 * deltas[-1],
           "c_no_peak_over_final": summit(deltas, edge)[2] <= edge, "first_rung": deltas[0], "final": deltas[-1]}
    out["met"] = out["a_positive_every_rung"] and out["b_first_rung_under_half_of_final"] and out["c_no_peak_over_final"]
    return out


def ladder(name):
    t0, rungs = LADDERS[name]
    trunk = C.battery_rows("g2-s1", SIZE)
    out = {"rungs": [], "missing": []}
    prev, prev_t = trunk, t0
    for seating, root, ticks in rungs:
        if not leg_file(seating, root).exists():
            out["missing"].append(seating)
            prev = None                                        # a step is never bridged across a rung not run
            continue
        rows, sha = rung_rows(seating, root)                   # a leg without its checkpoint raises here
        r = {"seating": seating, "ticks": ticks, "team": float(np.mean([R1.team(v) for v in rows.values()])), "delta_trunk": R1C.paired(rows, trunk),
             "worst_streak_max": int(max(v["max_distress_age"] for v in rows.values())), "artifact_sha256": sha}
        if prev is not None:
            r["step"] = step(rows, prev, ticks - prev_t)
        out["rungs"].append(r)
        prev, prev_t = rows, ticks
    if not out["missing"]:
        deltas = [r["delta_trunk"]["mean"] for r in out["rungs"]]
        top, first, peak = summit(deltas)
        out["summit"] = {"max_rung": out["rungs"][top]["seating"], "earliest_within_edge": out["rungs"][first]["seating"], "peak_over_final": peak}
    return out


def read():
    out = {"edge": EDGE, "lines_per_2M": {"flat": FLAT, "share_of_shortfall": SHARE}, "ladders": {n: ladder(n) for n in LADDERS}}
    nh, ct = out["ladders"]["nohead-s1"], out["ladders"]["cont-s1"]
    if "summit" in nh:                                         # P54: no recorded peak before the stop
        out["P54"] = {"peak_over_final": nh["summit"]["peak_over_final"], "met": nh["summit"]["peak_over_final"] <= EDGE}
    if "summit" in ct:                                         # P56 (entry 34): positive throughout, gradual, no peak
        out["P56"] = p56([r["delta_trunk"]["mean"] for r in ct["rungs"]])
    return out


def md(out):
    L = ["# R-6 — the checkpoint ladder (40×40, 30 worlds × 20k ticks, paired per world id against trunk s1 and the rung before)", ""]
    p = lambda d: f"{d['mean']:+.3f}, {d['positive']}/{d['n']}, [{d['range'][0]:+.3f}, {d['range'][1]:+.3f}]"
    for name, lad in out["ladders"].items():
        L += [f"## {name}", "", "| rung | ticks | team | Δ vs trunk (mean, positive, range) | worst streak max | step: ticks | gain ± half-width | flat line | 1% line | reaches flat / 1% |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in lad["rungs"]:
            s = r.get("step")
            tail = (f"{s['ticks']:,} | {s['gain']:+.3f} ± {s['half_width']:.3f} | {s['lines']['flat']:.3f} | {s['lines']['share']:.3f} | "
                    f"{'yes' if s['clears']['flat'] else 'no'} / {'yes' if s['clears']['share'] else 'no'}") if s else "— | — | — | — | —"
            L.append(f"| {r['seating']} | {r['ticks']:,} | {r['team']:.3f} | {p(r['delta_trunk'])} | {r['worst_streak_max']} | {tail} |")
        L += ["", "Not run: " + (", ".join(lad["missing"]) or "none") + "."]
        if "summit" in lad:
            s = lad["summit"]
            L += [f"Largest Δ-to-trunk at {s['max_rung']}; earliest rung within the {out['edge']} edge of it: {s['earliest_within_edge']}; "
                  f"largest rung over the final: {s['peak_over_final']:+.3f}."]
        L.append("")
    for k in ("P54", "P56"):
        if k in out:
            L.append(f"**{k} {'MET' if out[k]['met'] else 'NOT MET'}** ({json.dumps({a: b for a, b in out[k].items() if a != 'met'})}).")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(json.dumps({n: {"missing": lad["missing"], **({"summit": lad["summit"]} if "summit" in lad else {})} for n, lad in out["ladders"].items()}
                     | {k: out[k] for k in ("P54", "P56") if k in out}, indent=1))
