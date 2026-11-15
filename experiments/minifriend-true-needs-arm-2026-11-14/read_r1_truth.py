#!/usr/bin/env python3
"""R-1 for the true-needs arm (DECLARATION.md §6 R-1; §7 T1 / T2 scored; §8's grammar; deviations entry 37).
  equal length   the arm's 12M checkpoint (`p2u-truth-s1-u3906`) on uniform legs at 20×20 and 40×40, paired per world
                 against the needs scout's final (12.0M), the dual-head seed's final (12.0M), the no-head arm's 12M
                 checkpoint and trunk seed 1
  the final      `p2u-truth-s1` against the no-head final and against the arm's own 12M checkpoint
A leg is read only if its header seats the seating's own spec in all five seats and names that spec's file by sha256
(the re-anchor reader's `leg`, imported). A leg that has not run is left out and named; T1, T2 and §8 score only on
both sizes. Pairs are
the worlds whole in both legs (an aborted world is named in its leg's row and never paired).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_r1_truth.py --out reads/r1.json [--md]     (seconds)
    (A = ../minifriend-phase2-2026-11-06.)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "gen2-reanchor-scout-2026-11-14"))
import read_reanchor as RR  # noqa: E402  (leg: the header fence; tail; puts the continuation's and Phase 2's arcs on the path)
R1C, C, RP, K = RR.R1C, RR.C, RR.RP, RR.K

RAW = HERE / "results-raw"
EDGE = R1C.EDGE
CKPT, FINAL = "p2u-truth-s1-u3906", "p2u-truth-s1"
EQUAL = {"needs": ("p2u-needs-s1", None), "both": ("p2u-both-s1", None), "nohead_12M": ("r6-nohead-s1-u3906", K / "results-raw")}
NOHEAD_FINAL = ("p2u-nohead-s1", None)
SIZES = (20, 40)


def have(seating, size, root):
    return (RP.legs_dir(seating, size, root) / f"{seating}-g2cmp-30x20000.jsonl").exists()


def inside(mean, size):
    return bool(abs(mean) <= EDGE[size])


def grammar(m20, m40):
    """§8 on truth − needs at equal length: one of its five cases."""
    beyond = [not inside(m20, 20), not inside(m40, 40)]
    if not any(beyond):
        return "LEVEL"
    if (m20 > 0) != (m40 > 0):
        return "UNDECIDABLE"
    if all(beyond):
        return "ABOVE" if m20 > 0 else "BELOW"
    return "ONE SIZE"


def whole(rows):
    return {s: r for s, r in rows.items() if "aborted_streak" not in r}


def pair(a, b):
    """The world-id pairing on the worlds WHOLE in both legs: an aborted world's mean covers fewer ticks and is never paired."""
    a, b = whole(a), whole(b)
    both = set(a) & set(b)
    return R1C.paired({s: a[s] for s in both}, {s: b[s] for s in both})


def read(raw=RAW):
    out = {"edge": {str(z): EDGE[z] for z in SIZES}, "legs": {}, "equal_length": {}, "final": {}, "missing": [], "predictions": {}}
    for size in SIZES:
        trunk = C.battery_rows("g2-s1", size)
        mine = {}
        for name, seating in (("truth_12M", CKPT), ("truth_final", FINAL)):
            if have(seating, size, raw):
                mine[name] = RR.leg(seating, size, raw)
                out["legs"][f"{name}@{size}"] = {**RR.tail(mine[name]), "vs_trunk": pair(mine[name], trunk)}
            else:
                out["missing"].append(f"{seating}@{size}")
        other = {}
        for name, (seating, root) in {**EQUAL, "nohead_final": NOHEAD_FINAL}.items():
            if have(seating, size, root):
                other[name] = RR.leg(seating, size, root)
                out["legs"][f"{name}@{size}"] = {**RR.tail(other[name]), "vs_trunk": pair(other[name], trunk)}
            else:
                out["missing"].append(f"{seating}@{size}")
        if "truth_12M" in mine:
            out["equal_length"][str(size)] = {name: pair(mine["truth_12M"], other[name]) for name in EQUAL if name in other}
        if "truth_final" in mine:
            out["final"][str(size)] = {name: pair(mine["truth_final"], rows) for name, rows in
                                       (("nohead_final", other.get("nohead_final")), ("truth_12M", mine.get("truth_12M"))) if rows is not None}
    eq = out["equal_length"]
    if all(str(z) in eq and "needs" in eq[str(z)] for z in SIZES):
        m = {z: eq[str(z)]["needs"]["mean"] for z in SIZES}
        out["predictions"]["T1"] = {"truth_minus_needs": {str(z): m[z] for z in SIZES}, "met": all(inside(m[z], z) for z in SIZES)}
        out["grammar"] = grammar(m[20], m[40])
    if "40" in eq and "nohead_12M" in eq["40"]:
        out["predictions"]["T2"] = {"truth_minus_nohead_12M_at_40": eq["40"]["nohead_12M"]["mean"], "met": inside(eq["40"]["nohead_12M"]["mean"], 40)}
    return out


def md(out):
    p = lambda d: f"{d['mean']:+.3f}, {d['positive']}/{d['n']}, [{d['range'][0]:+.3f}, {d['range'][1]:+.3f}]"   # noqa: E731
    L = ["# True-needs arm: R-1 (uniform legs, 30 worlds × 20k ticks, paired per world)", "", f"Missing: {', '.join(out['missing']) or 'none'}.", "",
         "| leg | team happiness | vs trunk s1 (mean, worlds up, range) | worlds with a 300+ streak | worst streak | aborts |", "|---|---|---|---|---|---|"]
    for name, r in out["legs"].items():
        L.append(f"| {name} | {r['team_mean']:.3f} | {p(r['vs_trunk'])} | {r['worlds_300']} | {r['worst_streak']} | {', '.join(f'{k}: {v}' for k, v in r['aborts'].items()) or 'none'} |")
    L += ["", "## Equal length: the arm's 12M checkpoint minus each 12.0M comparator (mean, worlds up, range)", "", "| size | edge | − needs final | − dual-head final | − no-head 12M checkpoint |", "|---|---|---|---|---|"]
    for z, v in out["equal_length"].items():
        L.append(f"| {z}×{z} | {out['edge'][z]} | " + " | ".join(p(v[n]) if n in v else "not run" for n in EQUAL) + " |")
    L += ["", "## The arm's final (15,000,576 ticks, the no-head final's own length)", "", "| size | − no-head final | − its own 12M checkpoint |", "|---|---|---|"]
    for z, v in out["final"].items():
        L.append(f"| {z}×{z} | " + " | ".join(p(v[n]) if n in v else "not run" for n in ("nohead_final", "truth_12M")) + " |")
    L += ["", "## Predictions and grammar", ""]
    for k, v in out["predictions"].items():
        L.append(f"- {k}: {'MET' if v['met'] else 'NOT MET'} ({json.dumps({a: b for a, b in v.items() if a != 'met'})})")
    L.append(f"- §8 (truth − needs at equal length): **{out['grammar']}**" if "grammar" in out else "- §8 does not score until both sizes exist.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(md(out))
