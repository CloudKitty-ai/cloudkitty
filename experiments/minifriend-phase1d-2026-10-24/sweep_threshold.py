#!/usr/bin/env python3
"""Phase 1d §Addendum 2 — R5d, the operating-point sweep (read-only on the
six probe runs' saved P(grave)).

R4d's `latency` instrument, unchanged, at THRESHOLDS for NF-h24+p and
DR-h24+p, on group P and on the held-out evaluation worlds of L, W and G
(SETS); seeds 1–3, mean ± SD. The 0.20 and 0.50 rows on group P must
equal the committed R4d rows (asserted before writing). Derived column:
mid-world false-alarm runs per 100 detected mid-world episodes. Post-read
columns (DECLARATION §Addendum 2 additions): non-grave ticks at or over
the threshold per 10k; where the mid-world false-alarm runs start
(offset 1, ≤ EARLY, after EARLY per 10k). Descriptive — no reading rule;
the pick is the owner's.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(HERE))
import read_phase1d as P  # noqa: E402

THRESHOLDS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
SETS = {"P": P.C.GROUPS["P"], "LWG": ["L", "W", "G"]}
PINNED_ROWS = {"0.20": "NF-h24+p ≥ 0.2", "0.50": "NF-h24+p ≥ 0.5"}


def derived(row):
    """Mid-world false-alarm runs per 100 detected mid-world episodes, from the row's own counts."""
    det = 0.0
    for k in ("midworld_visible", "midworld_fog"):
        if row[k]["detected_frac"] is not None:
            det += row[k]["detected_frac"] * row[k]["episodes"]
    fa = row["false_alarms"]["midworld_runs"]
    return {"midworld_detected": det, "midworld_fa_per_100_detected": 100.0 * fa / det if det else None}


def nongrave_above(idx, signal, thresh):
    """Post-read addition: non-grave ticks at or over the threshold, per 10,000 observer-ticks —
    monotone in the threshold by construction (a tick count, not a run count); it includes the
    ticks just before an onset and after an episode's end, so it is not a false-alarm rate."""
    above = np.asarray(signal, np.float64) >= thresh
    return float((above & (idx["code"] != P.S.GRAVE)).sum() / idx["n"] * 1e4)


EARLY = 100   # a false-alarm run starting within the slice's first EARLY ticks (offset ≤ EARLY) is "early"


def fa_detail(idx, signal, thresh):
    """Post-read addition (gate round 1): where the mid-world false-alarm runs start. Over the
    runs that `latency` counts as mid-world false alarms (over the threshold, no grave tick, not
    starting at the slice's first tick): the count starting at offset 1 (the world-start run with
    its first tick under the threshold), the fraction starting at offset ≤ EARLY, and the runs
    starting after EARLY per 10,000 observer-ticks (the false-alarm rate a burn-in of EARLY ticks
    would leave)."""
    above = np.asarray(signal, np.float64) >= thresh
    grave = idx["code"] == P.S.GRAVE
    starts = []
    for _n, _s, _k, _j, a, b in idx["slices"]:
        for st, en in P._runs(above[a:b]):
            if st != 0 and not grave[a + st:a + en].any():
                starts.append(int(st))
    n = len(starts)
    late = sum(st > EARLY for st in starts)
    return {"midworld_runs": n, "start_at_1": sum(st == 1 for st in starts),
            "frac_start_le_early": (n - late) / n if n else None,
            "late_runs_per_10k": late / idx["n"] * 1e4, "early": EARLY}


def composition(idx, eps):
    """Episodes per evaluation set name: reset and mid-world counts."""
    start = {a: n for n, _s, _k, _j, a, _b in idx["slices"]}
    out = {}
    for st, _en, a in eps:
        c = out.setdefault(start[a], {"reset": 0, "midworld": 0})
        c["reset" if st == a else "midworld"] += 1
    return out


def sweep(idx, ps, thresholds=THRESHOLDS):
    eps = P.episodes(idx)
    out = {"episodes_total": len(eps), "episodes_reset": sum(st == a for st, _en, a in eps),
           "episodes_midworld_visible": sum(st != a and bool(idx["vis"][st]) for st, _en, a in eps),
           "episodes_midworld_fog": sum(st != a and not idx["vis"][st] for st, _en, a in eps),
           "friend_episodes": P.friend_episode_count(idx, eps), "n_ticks": idx["n"],
           "composition": composition(idx, eps), "rows": {}}
    for t in thresholds:
        per = [P.latency(idx, p, t, eps) for p in ps]
        for r, p in zip(per, ps):
            r["derived"] = derived(r)
            r["nongrave_above_per_10k"] = nongrave_above(idx, p, t)
            r["fa_detail"] = fa_detail(idx, p, t)
            assert r["fa_detail"]["midworld_runs"] == r["false_alarms"]["midworld_runs"]
        out["rows"][f"{t:.2f}"] = {"per_seed": per, **P.msd_tree(per)}
    return out


def pin_r4d(sweep_p_nf, path=HERE / "phase1d-read.json"):
    """Group P, NF-h24+p: the 0.20 and 0.50 rows equal the committed R4d rows (minus the derived column)."""
    ref = json.loads(path.read_text())["R4d_latency"]["heads"]
    for t, name in PINNED_ROWS.items():
        got = json.loads(json.dumps(sweep_p_nf["rows"][t], default=float))
        for r in got["per_seed"] + [got]:
            r.pop("derived")
            r.pop("nongrave_above_per_10k")
            r.pop("fa_detail")
        assert got == ref[name], (t, name)


def read_all():
    out = {"thresholds": list(THRESHOLDS), "sets": SETS, "seeds": list(P.SEEDS), "probes": P.PROBES, "by_set": {}}
    for sname, sets in SETS.items():
        idx = P.R.eval_index(sets)
        heads = {}
        for b, runs in P.PROBES.items():
            heads[f"{b}-h24+p"] = sweep(idx, [P.load_p(run, idx) for run in runs])
        out["by_set"][sname] = {"eval_sets": sets, "n_samples": idx["n"], "heads": heads}
    pin_r4d(out["by_set"]["P"]["heads"]["NF-h24+p"])
    return out


def fmt(m, d=3):
    return P.fmt(m, d)


def md(out):
    L = ["# Phase 1d §Addendum 2 — R5d operating-point sweep (mean ± SD over seeds 1–3)", ""]
    for sname, blk in out["by_set"].items():
        for h, sw in blk["heads"].items():
            L.append(f"## {sname} ({', '.join(blk['eval_sets'])}; {blk['n_samples']:,} observer-ticks) — {h}")
            L.append(f"episodes {sw['episodes_total']} ({sw['friend_episodes']} friend-episodes): reset {sw['episodes_reset']}, "
                     f"mid-world in sight {sw['episodes_midworld_visible']}, mid-world under fog {sw['episodes_midworld_fog']}")
            L.append("per set: " + "; ".join(f"{n} reset {c['reset']} / mid-world {c['midworld']}" for n, c in sw["composition"].items())
                     + "".join(f"; {n} 0 / 0" for n in blk["eval_sets"] if n not in sw["composition"]))
            L.append("")
            L.append("| P ≥ | mw-sight det | antic | p90 lat | mw-fog det | antic | p90 lat | reset det | reset med lat | mw FA /10k | mw FA len | all FA /10k | mw FA per 100 det | non-grave ticks ≥ t /10k | mw FA start ≤ 100 | mw FA at tick 1 | late FA /10k (start > 100) |")
            L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for t, r in sw["rows"].items():
                mv, mf, rs, fa, dv = r["midworld_visible"], r["midworld_fog"], r["reset"], r["false_alarms"], r["derived"]
                L.append(f"| {t} | {fmt(mv['detected_frac'])} | {fmt(mv['anticipated_frac'])} | {fmt(mv['p90_latency'], 1)} "
                         f"| {fmt(mf['detected_frac'])} | {fmt(mf['anticipated_frac'])} | {fmt(mf['p90_latency'], 1)} "
                         f"| {fmt(rs['detected_frac'])} | {fmt(rs['median_latency'], 1)} "
                         f"| {fmt(fa['midworld_per_10k_ticks'])} | {fmt(fa['midworld_run_median_length'], 1)} | {fmt(fa['per_10k_ticks'])} "
                         f"| {fmt(dv['midworld_fa_per_100_detected'], 1)} | {fmt(r['nongrave_above_per_10k'], 2)} "
                         f"| {fmt(r['fa_detail']['frac_start_le_early'])} | {fmt(r['fa_detail']['start_at_1'], 1)} | {fmt(r['fa_detail']['late_runs_per_10k'])} |")
            L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1d-sweep.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
