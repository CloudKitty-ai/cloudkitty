#!/usr/bin/env python3
"""R-1 — the welfare rule's read (DECLARATION.md §6 R-1, §8.1; guard g6). Imports the cert battery's reader
(gate_read: rows, team, the comparator files and pins) and pairs this arc's legs with the recorded trunk rows.

    read_r1.py --out reads/r1.json [--md] [--sizes 20,40,100] [--arms act15,act10,nohead]

Per arm × size × seating shape: the arm's team happiness per seed, the paired Δ against the trunk row on the same
world (uniform: g2-s_k; roster-shaped: g2-rot2) and against the scripted comparator (sign count, range), worst streak
mean / max, aborts, F-053 events, dispersion. The EDGE STATISTIC per size is recomputed from the recorded trunk rows
(uniform: the mean of the three pairwise |g2-s1 − g2-s2|, |g2-s1 − g2-s4|, |g2-s2 − g2-s4| team means; roster, 20×20
only: the same over rot2 and the two permuted trunk legs g2-rot2-perm1 / perm2 of this arc). The welfare rule (§8.1)
is then applied at 20×20: B15 DEMOTED iff act10's team happiness exceeds act15's by more than the edge statistic of
the seating shape, the same sign in all three paired seeds, AND (left to the write-up) the consumer reads do not
favour act15 — a null keeps B15; a 40×40 / 100×100 roster clearance never demotes (descriptive). P38 / P39 / P40
scored on the uniform 20×20 read.
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
sys.path.insert(0, str(C.BATTERY))
import gate_read as GR  # noqa: E402  (rows, team, CMP_FILE, PINNED)

ARMS = ("act15", "act10", "nohead")
SEEDS = (1, 2, 4)
SIZES = (20, 40, 100)
EDGE_DECLARED = {20: 0.326, 40: 0.325}          # DECLARATION §2, recomputed here (g6)
F053 = 1_000


def team(r):
    return GR.team(r)


def edge_statistic(means):
    """The prereg's EDGE STATISTIC: the mean of the pairwise absolute differences of the given team means."""
    return float(np.mean([abs(a - b) for a, b in itertools.combinations(means, 2)]))


def trunk_uniform_rows(size):
    return {k: C.battery_rows(f"g2-s{k}", size) for k in SEEDS}


def trunk_roster_rows(size):
    return C.battery_rows("g2-rot2", size)


def comparator_rows(size):
    rs = GR.rows(GR.CMP_FILE[size])
    return {r["seed"]: r for r in rs}


def leg_summary(rows, trunk_rows, cmp_rows):
    """One leg (30 rows) paired per world with the trunk rows and the comparator rows."""
    seeds = sorted(rows)
    assert set(seeds) == set(trunk_rows) == set(cmp_rows), (len(seeds), len(trunk_rows), len(cmp_rows))
    tm = [team(rows[s]) for s in seeds]
    d_tr = [team(rows[s]) - team(trunk_rows[s]) for s in seeds]
    d_cmp = [team(rows[s]) - team(cmp_rows[s]) for s in seeds]
    mda = [rows[s]["max_distress_age"] for s in seeds]
    return {"n": len(seeds), "team_mean": float(np.mean(tm)), "team_sd": float(np.std(tm, ddof=1)),
            "paired_delta_trunk": {"mean": float(np.mean(d_tr)), "positive": int(sum(v > 0 for v in d_tr)),
                                   "range": [float(min(d_tr)), float(max(d_tr))]},
            "paired_delta_comparator": {"mean": float(np.mean(d_cmp)), "positive": int(sum(v > 0 for v in d_cmp)),
                                        "range": [float(min(d_cmp)), float(max(d_cmp))]},
            "trunk_team_mean": float(np.mean([team(trunk_rows[s]) for s in seeds])),
            "worst_streak_mean": float(np.mean(mda)), "worst_streak_max": int(max(mda)),
            "aborted_seeds": sorted(s for s in seeds if "aborted_streak" in rows[s]),
            "f053_events": sorted(s for s in seeds if rows[s]["max_distress_age"] >= F053),
            "trunk_worst_streak_max": int(max(trunk_rows[s]["max_distress_age"] for s in seeds)),
            "dispersion_together_mean": float(np.mean([np.mean(rows[s]["dispersion"]["together_share"]) for s in seeds]))
            if all("dispersion" in rows[s] for s in seeds) else None}


def welfare_rule(act15_by_seed, act10_by_seed, edge, shape):
    """§8.1 arithmetic on seed team means {seed: team}: demotion iff act10 − act15 > edge in seed mean AND the same
    sign (act10 > act15) in all three paired seeds; the 20 / 30 conditional iff act15 − act10 > edge with the same
    sign in all three. A null keeps B15. `shape` names the seating shape; only 20×20 reads enter the clause."""
    diffs = {k: act10_by_seed[k] - act15_by_seed[k] for k in SEEDS}
    mean_d = float(np.mean(list(diffs.values())))
    all_act10 = all(v > 0 for v in diffs.values())
    all_act15 = all(v < 0 for v in diffs.values())
    demote = bool(mean_d > edge and all_act10)
    extend = bool(-mean_d > edge and all_act15)
    return {"shape": shape, "edge": edge, "act10_minus_act15": diffs, "seed_mean_diff": mean_d,
            "same_sign_all_three": all_act10 or all_act15,
            "verdict": ("DEMOTION FINDING (pending the consumer reads)" if demote else
                        "act15 beats act10 beyond the edge (her 20 / 30 conditional, pending both shapes)" if extend else
                        "null: B15 stands"),
            "demote": demote, "extend_conditional": extend}


def score_predictions(uni20, edge):
    """P38–P40 on the uniform 20×20 read (seed means over the three paired seeds). act10 may be ABSENT (deviations
    entry 29 (C), 2026-11-08: the arm dropped from the battery): P38 then reads UNDECIDABLE (met None, reason), P39 is
    act10-free and scores, P40's act15 half scores and its act10 half is UNDECIDABLE — the conjunction is NOT MET
    when the act15 half fails on its own, UNDECIDABLE when it holds (the act10 half could still fail)."""
    a15 = uni20["act15"]["seed_mean_team"]
    a10 = uni20["act10"]["seed_mean_team"] if "act10" in uni20 else None
    nh = uni20["nohead"]
    if a10 is None:
        out = {"P38": {"value": None, "bar": edge, "met": None, "reason": "act10 absent (entry 29 (C)): no comparator",
                       "text": "|act15 − act10| ≤ the edge statistic (a null)"}}
    else:
        out = {"P38": {"value": abs(a15 - a10), "bar": edge, "met": abs(a15 - a10) <= edge,
                       "text": "|act15 − act10| ≤ the edge statistic (a null)"}}
    inside = [abs(nh["per_seed"][k]["paired_delta_trunk"]["mean"]) <= edge for k in map(str, SEEDS)]
    out["P39"] = {"per_seed_inside": dict(zip(map(str, SEEDS), inside)), "met": sum(inside) >= 2,
                  "text": "the no-head arm's paired gain over its trunk seed inside the envelope in ≥ 2 of 3 seeds"}
    g15 = a15 - nh["seed_mean_team"]
    half15 = bool(g15 > 0 and g15 <= edge)
    if a10 is None:
        out["P40"] = {"act15_minus_nohead": g15, "act10_minus_nohead": None, "act15_half_met": half15,
                      "met": (None if half15 else False),
                      "reason": "act10 absent (entry 29 (C)): the act10 half is UNDECIDABLE" + ("" if half15 else "; the act15 half fails on its own"),
                      "text": "each act arm's gain over the no-head arm positive in mean but inside the envelope"}
    else:
        g10 = a10 - nh["seed_mean_team"]
        out["P40"] = {"act15_minus_nohead": g15, "act10_minus_nohead": g10, "act15_half_met": half15,
                      "met": (half15 and g10 > 0 and g10 <= edge),
                      "text": "each act arm's gain over the no-head arm positive in mean but inside the envelope"}
    return out


def read(sizes=SIZES, arms=ARMS, root=None):
    out = {"edge": {}, "uniform": {}, "roster": {}, "rule": {}, "notes": []}
    # edge statistics
    gate_json = json.loads((C.BATTERY / "gate-read.json").read_text())
    for size in sizes:
        tr = trunk_uniform_rows(size)
        raw_means = [float(np.mean([team(r) for r in tr[k].values()])) for k in SEEDS]
        # the DECLARED recipe (§2): the battery's printed trained means (gate-read.json, 3 dp) -> 0.326 / 0.325; the
        # same statistic from the unrounded rows is reported beside (0.327 at 20×20: a 0.001 rounding artifact)
        printed = [gate_json[f"g2-s{k}/{size}"]["trained_mean"] for k in SEEDS]
        for k, m in zip(SEEDS, raw_means):
            assert round(m, 3) == gate_json[f"g2-s{k}/{size}"]["trained_mean"], (size, k, m)
        out["edge"][f"uniform/{size}"] = {"trunk_team_means_printed": dict(zip(map(str, SEEDS), printed)),
                                          "edge": edge_statistic(printed), "edge_from_unrounded_rows": edge_statistic(raw_means),
                                          "status": "recorded trunk rows (declared recipe: printed means)"}
        if size in EDGE_DECLARED:
            assert round(edge_statistic(printed), 3) == EDGE_DECLARED[size], (size, edge_statistic(printed))
    rot2 = {size: trunk_roster_rows(size) for size in sizes}
    perm = {}
    for name in ("g2-rot2-perm1", "g2-rot2-perm2"):
        try:
            perm[name], _h = RP.leg_rows(name, 20, root)
        except FileNotFoundError:
            perm[name] = None
    if all(v is not None for v in perm.values()):
        means = [float(np.mean([team(r) for r in rot2[20].values()]))] + [float(np.mean([team(r) for r in perm[n].values()])) for n in perm]
        out["edge"]["roster/20"] = {"team_means": {"g2-rot2": means[0], "g2-rot2-perm1": means[1], "g2-rot2-perm2": means[2]},
                                    "edge": edge_statistic(means), "status": "MEASURED"}
    else:
        out["edge"]["roster/20"] = {"edge": None, "status": "NOT MEASURED (perm legs absent): roster verdicts descriptive"}
    for size in sizes:
        if size != 20:
            out["edge"][f"roster/{size}"] = {"edge": out["edge"][f"uniform/{size}"]["edge"], "status": "BORROWED (descriptive)"}
    # legs
    for size in sizes:
        cmp_rows = comparator_rows(size)
        tr = trunk_uniform_rows(size)
        uni = {}
        for arm in arms:
            per_seed = {}
            for k in SEEDS:
                try:
                    rows, _h = RP.leg_rows(f"p2u-{arm}-s{k}", size, root)
                except FileNotFoundError:
                    continue
                per_seed[str(k)] = leg_summary(rows, tr[k], cmp_rows)
            if per_seed:
                uni[arm] = {"per_seed": per_seed, "seed_mean_team": float(np.mean([v["team_mean"] for v in per_seed.values()])),
                            "seed_mean_delta_trunk": float(np.mean([v["paired_delta_trunk"]["mean"] for v in per_seed.values()])),
                            "complete": len(per_seed) == 3}
        out["uniform"][str(size)] = uni
        ros = {}
        for arm in arms:
            try:
                rows, _h = RP.leg_rows(f"p2r-{arm}", size, root)
            except FileNotFoundError:
                continue
            ros[arm] = leg_summary(rows, rot2[size], cmp_rows)
        out["roster"][str(size)] = ros
    # the rule at 20×20
    u20 = out["uniform"].get("20", {})
    if all(a in u20 and u20[a]["complete"] for a in ("act15", "act10")):
        out["rule"]["uniform/20"] = welfare_rule({k: u20["act15"]["per_seed"][str(k)]["team_mean"] for k in SEEDS},
                                                 {k: u20["act10"]["per_seed"][str(k)]["team_mean"] for k in SEEDS},
                                                 out["edge"]["uniform/20"]["edge"], "uniform")
    elif "act15" in u20 and u20["act15"]["complete"]:
        out["rule"]["uniform/20"] = {"shape": "uniform", "verdict": "UNDECIDABLE", "demote": None, "extend_conditional": None,
                                     "reason": "act10 incomplete or absent (deviations entry 29 (C), 2026-11-08): the §8.1 clause has no comparator; "
                                               "B15 stands undemoted for want of one, not on evidence"}
    if all(a in u20 and u20[a]["complete"] for a in ("act15", "nohead")):
        out["predictions"] = score_predictions({a: u20[a] for a in ("act15", "act10", "nohead") if a in u20 and u20[a]["complete"]},
                                               out["edge"]["uniform/20"]["edge"])
    r20 = out["roster"].get("20", {})
    if all(a in r20 for a in ("act15", "act10")) and out["edge"]["roster/20"]["edge"] is not None:
        # the roster-shaped legs seat the three arm seeds together: one leg per arm, its 30-world mean per seat
        # triple is not seed-paired; the clause reads the roster legs' team means with the measured roster edge,
        # the replication valve read on the three ARM SEATS' own mean happiness (Miso s2, Biscuit s4, Clementine s1).
        def seat_means(arm):
            rows, _h = RP.leg_rows(f"p2r-{arm}", 20, root)
            m = np.mean([rows[s]["mean_happiness"] for s in sorted(rows)], 0)
            return {2: float(m[0]), 4: float(m[1]), 1: float(m[4])}
        out["rule"]["roster/20"] = welfare_rule(seat_means("act15"), seat_means("act10"), out["edge"]["roster/20"]["edge"], "roster")
        out["notes"].append("roster/20 rule: the three-seed valve reads the arm seats' own mean happiness (Miso = s2, Biscuit = s4, Clementine = s1) in the one roster leg per arm")
    return out


def md(out):
    L = ["# R-1 — the welfare rule's read", ""]
    L += ["| edge | value | status |", "|---|---|---|"]
    for k, v in out["edge"].items():
        L.append(f"| {k} | {v['edge'] if v['edge'] is None else round(v['edge'], 3)} | {v.get('status', 'recorded trunk rows')} |")
    for shape in ("uniform", "roster"):
        L += ["", f"## {shape}", "", "| size | arm | seed | team | Δ trunk (mean, +/30, range) | Δ comparator | worst streak mean / max | aborts | F-053 |", "|---|---|---|---|---|---|---|---|---|"]
        for size, arms in out[shape].items():
            for arm, v in arms.items():
                rows = v["per_seed"].items() if shape == "uniform" else [("rot2", v)]
                for k, s in rows:
                    dt, dc = s["paired_delta_trunk"], s["paired_delta_comparator"]
                    L.append(f"| {size} | {arm} | {k} | {s['team_mean']:.3f} | {dt['mean']:+.3f}, {dt['positive']}/30, [{dt['range'][0]:+.3f}, {dt['range'][1]:+.3f}] | {dc['mean']:+.3f} | {s['worst_streak_mean']:.1f} / {s['worst_streak_max']} | {len(s['aborted_seeds'])} | {len(s['f053_events'])} |")
    L += ["", "## the rule (§8.1)", ""]
    for k, r in out.get("rule", {}).items():
        if "act10_minus_act15" not in r:
            L.append(f"- {k}: **{r['verdict']}** — {r['reason']}")
            continue
        L.append(f"- {k}: act10 − act15 per seed {json.dumps({str(a): round(b, 3) for a, b in r['act10_minus_act15'].items()})}, seed mean {r['seed_mean_diff']:+.3f} vs edge {r['edge']:.3f} → **{r['verdict']}**")
    if "predictions" in out:
        L += ["", "## predictions", ""]
        for p, v in out["predictions"].items():
            label = "UNDECIDABLE" if v["met"] is None else ("MET" if v["met"] else "NOT MET")
            L.append(f"- {p}: {label} — {v['text']} ({json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ('text', 'met')})})")
    for n in out["notes"]:
        L.append(f"- note: {n}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "r1.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--sizes", default="20,40,100")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--root", type=Path, default=None, help="results-raw root (default this arc's)")
    a = ap.parse_args()
    out = read(tuple(int(s) for s in a.sizes.split(",")), tuple(a.arms.split(",")), a.root)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(json.dumps({k: out[k] for k in ("edge", "rule")}, indent=1))


if __name__ == "__main__":
    main()
