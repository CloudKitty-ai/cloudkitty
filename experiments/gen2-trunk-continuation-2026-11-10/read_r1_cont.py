#!/usr/bin/env python3
"""R-1 for the trunk continuation (DECLARATION.md §6 R-1, §7 P48 / P49, §8.1; guard g6): each continued seed's
uniform leg paired PER WORLD ID with (i) the recorded trunk rows g2-s<k>, (ii) the recorded no-head rows
p2u-nohead-s<k> (s1's seat is the s1r rerun), (iii) the scripted comparator. Phase 2's own summary and edges are
imported, never copied. A leg whose header does not name this arc's continued final by sha256 is never read.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_r1_cont.py --out reads/r1.json [--md]
(A = experiments/minifriend-phase2-2026-11-06.) A leg not yet run reads "not run"; predictions score only when every
declared leg is present.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import read_r1 as R1  # noqa: E402

RAW = HERE / "results-raw"
SIZES = {1: (20, 40, 100), 2: (20, 40), 4: (20, 40)}
EDGE = {20: 0.326, 40: 0.325, 100: 0.726}                  # Phase 2's measured edge statistics (DECLARATION §6 R-1)


def paired(rows, other):
    """The arm's team happiness minus the other table's, world by world ID; a world set that differs raises."""
    assert set(rows) == set(other), f"world sets differ: {len(rows)} rows against {len(other)}"
    d = [R1.team(rows[s]) - R1.team(other[s]) for s in sorted(rows)]
    return {"mean": float(np.mean(d)), "positive": int(sum(v > 0 for v in d)), "n": len(d), "range": [float(min(d)), float(max(d))]}


def leg(k, size, root=RAW, final=None):
    rows, header = RP.leg_rows(f"cont-s{k}", size, root)
    final = Path(final or HERE / "artifacts" / f"cont-s{k}" / "policy-final.pt")
    sha = hashlib.sha256(final.read_bytes()).hexdigest()
    assert header["seats"] == [f"g2:cont-s{k}"] * 5 and header["provenance"]["artifacts"] == {f"g2:cont-s{k}": sha}, \
        f"cont-s{k} {size}: the leg seats {header['seats'][0]} at {header['provenance']['artifacts']}, the continued final is {sha}"
    out = R1.leg_summary(rows, C.battery_rows(f"g2-s{k}", size), R1.comparator_rows(size))
    out["paired_delta_nohead"] = paired(rows, RP.leg_rows(f"p2u-nohead-s{k}", size, None)[0])
    out["artifact_sha256"] = sha
    return out


def read(root=RAW):
    out = {"edge": {str(z): e for z, e in EDGE.items()}, "legs": {}, "missing": []}
    for k, sizes in SIZES.items():
        for size in sizes:
            if (RP.legs_dir(f"cont-s{k}", size, root) / f"cont-s{k}-g2cmp-30x20000.jsonl").exists():
                out["legs"][f"cont-s{k}/{size}"] = leg(k, size, root)          # a leg without its final raises here
            else:
                out["missing"].append(f"cont-s{k}/{size}")
    if out["missing"]:
        return out
    L = out["legs"]
    tr = {z: {k: L[f"cont-s{k}/{z}"]["paired_delta_trunk"] for k in SIZES} for z in (20, 40)}
    nh = {z: {k: L[f"cont-s{k}/{z}"]["paired_delta_nohead"] for k in SIZES} for z in (20, 40)}
    mean = lambda d: float(np.mean([v["mean"] for v in d.values()]))
    out["P48"] = {"positive_30_of_30": {str(k): v["positive"] == v["n"] == 30 for k, v in tr[20].items()},
                  "beyond_edge": {str(k): v["mean"] > EDGE[20] for k, v in tr[20].items()}}
    out["P48"]["met"] = all(out["P48"]["positive_30_of_30"].values()) and sum(out["P48"]["beyond_edge"].values()) >= 2
    out["P49"] = {str(z): {"nohead_minus_cont_seed_mean": -mean(nh[z]), "same_sign_all_three": all(v["mean"] < 0 for v in nh[z].values()),
                           "beyond_edge": -mean(nh[z]) > EDGE[z]} for z in (20, 40)}
    out["P49"]["met"] = all(v["same_sign_all_three"] and v["beyond_edge"] for v in (out["P49"]["20"], out["P49"]["40"]))
    above_trunk = all(mean(tr[z]) > EDGE[z] for z in (20, 40))
    near_trunk = all(abs(mean(tr[z])) <= EDGE[z] for z in (20, 40))
    near_nohead = all(abs(mean(nh[z])) <= EDGE[z] for z in (20, 40))
    below_nohead = all(-mean(nh[z]) > EDGE[z] for z in (20, 40))
    above_nohead = all(mean(nh[z]) > EDGE[z] for z in (20, 40))
    out["grammar"] = {"seed_mean_delta_trunk": {str(z): mean(tr[z]) for z in (20, 40)}, "seed_mean_delta_nohead": {str(z): mean(nh[z]) for z in (20, 40)},
                      "reading": ("LONGER" if near_nohead and above_trunk else "BOTH" if above_trunk and below_nohead else
                                  "DIFFERENT" if near_trunk and below_nohead else "UNEXPECTED" if above_nohead else "UNDECIDABLE")}
    return out


def md(out):
    L = ["# R-1 — the continuation's welfare read (uniform legs, 30 worlds × 20k ticks, paired per world id)", "",
         "| leg | team mean | Δ vs trunk (mean, positive, range) | Δ vs no-head (mean, positive, range) | Δ vs scripted | worst streak mean / max | aborted | edge |",
         "|---|---|---|---|---|---|---|---|"]
    p = lambda d: f"{d['mean']:+.3f}, {d['positive']}/{d.get('n', 30)}, [{d['range'][0]:+.3f}, {d['range'][1]:+.3f}]"
    for name, v in out["legs"].items():
        L.append(f"| {name} | {v['team_mean']:.3f} | {p(v['paired_delta_trunk'])} | {p(v['paired_delta_nohead'])} | {v['paired_delta_comparator']['mean']:+.3f} | "
                 f"{v['worst_streak_mean']:.1f} / {v['worst_streak_max']} | {v['aborted_seeds'] or '—'} | {out['edge'][name.split('/')[1]]} |")
    L += ["", "Not run: " + (", ".join(out["missing"]) or "none") + "."]
    if "grammar" in out:
        g = out["grammar"]
        L += ["", f"**P48 {'MET' if out['P48']['met'] else 'NOT MET'}** (30 of 30 positive at 20×20: {out['P48']['positive_30_of_30']}; beyond the edge: {out['P48']['beyond_edge']}). "
              f"**P49 {'MET' if out['P49']['met'] else 'NOT MET'}** ({json.dumps({z: out['P49'][z] for z in ('20', '40')})}). "
              f"**§8.1 reads {g['reading']}** (seed-mean Δ vs trunk {g['seed_mean_delta_trunk']}, vs no-head {g['seed_mean_delta_nohead']})."]
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
    print(json.dumps({k: out[k] for k in ("missing", "P48", "P49", "grammar") if k in out}, indent=1))
