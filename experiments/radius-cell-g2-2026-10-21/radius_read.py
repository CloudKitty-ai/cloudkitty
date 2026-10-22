#!/usr/bin/env python3
"""Reads R1–R4 of the displaced-size radius cell (DECLARATION.md): the
2 × 2 at 40×40 — {scripted, rot2} × {radius 5 (law, recorded rows),
radius 4 (this cell)} — on the same 30 g2cmp worlds, paired by seed.

    radius_read.py --out radius-read.json --md
"""
import argparse
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
CMP = HERE.parent / "gen2-comparator-legs-2026-10-14/results-raw"
BAT = HERE.parent / "gen2-cert-battery-2026-10-20"
ROWS = {
    "S5": CMP / "vision5-40/legs/size40/scripted-g2cmp-30x20000.jsonl",
    "R5": BAT / "results-raw/g2-rot2/legs/size40/g2-rot2-g2cmp-30x20000.jsonl",
    "S4": HERE / "results-raw/scripted/legs/size40/scripted-g2cmp-30x20000.jsonl",
    "R4": HERE / "results-raw/g2-rot2/legs/size40/g2-rot2-g2cmp-30x20000.jsonl",
    # the pre-law v4 scripted row (radius 4, vocabulary unarmed): R4's
    # instrument check, never the pair
    "V4": CMP / "legs/size40/scripted-g2cmp-30x20000.jsonl",
    # the comparator arc's vocab-armed re-run of the law row (config
    # f45a5183, binding e3bcc79a: R5's config and binding); S5's check
    "A5": CMP / "vocab-armed-rerun/legs/size40/scripted-g2cmp-30x20000.jsonl",
}
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
CONTEXT_20 = BAT / "dispersion-read.json"   # the 20×20 cert gap, printed beside
F053 = 1000


def by_seed(p):
    lines = p.read_text().splitlines()
    head = json.loads(lines[0])
    rows = {r["seed"]: r for r in (json.loads(l) for l in lines[1:])}
    return head, rows


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def msd(xs):
    sd = st.stdev(xs) if len(xs) > 1 else None
    return {"n": len(xs), "mean": st.mean(xs), "sd": sd,
            "se": (sd / len(xs) ** 0.5) if sd is not None else None}


def paired(A, B, seeds, f=team):
    """Per-world f(A) − f(B), in seed order."""
    return [f(A[w]) - f(B[w]) for w in seeds]


def welfare(X, seeds):
    mda = [X[w].get("max_distress_age", 0) for w in seeds]
    return {"worst_streak_mean": sum(mda) / len(mda), "worst_streak_max": max(mda),
            "at_or_over_line": sum(m >= F053 for m in mda),
            "aborts": sum("aborted_streak" in X[w] for w in seeds)}


def identity(A, B, seeds, places=3):
    """R4: per-world team happiness equal at the printed precision, and
    whether every seat's mean happiness is byte-equal as recorded."""
    bad = [w for w in seeds if round(team(A[w]), places) != round(team(B[w]), places)]
    exact = all(A[w]["mean_happiness"] == B[w]["mean_happiness"] for w in seeds)
    return {"worlds_compared": len(seeds), "mismatches": bad, "identical": not bad,
            "mean_happiness_exact": exact}


def read(rows=ROWS):
    heads, R = {}, {}
    for k, p in rows.items():
        heads[k], R[k] = by_seed(p)
    seeds = sorted(R["R5"])
    for k in R:
        assert set(R[k]) == set(seeds) and len(seeds) == 30, (k, len(R[k]))
    out = {"seeds": seeds, "config_sha256": {k: heads[k]["provenance"]["config_sha256"] for k in heads},
           "team": {k: msd([team(R[k][w]) for w in seeds]) for k in ("S5", "R5", "S4", "R4")}}
    gap5 = paired(R["R5"], R["S5"], seeds)
    gap4 = paired(R["R4"], R["S4"], seeds)
    dd = [a - b for a, b in zip(gap4, gap5)]
    out["r1"] = {
        "gap_radius5": dict(msd(gap5), positive=sum(g > 0 for g in gap5)),
        "gap_radius4": dict(msd(gap4), positive=sum(g > 0 for g in gap4)),
        "radius_effect_scripted": msd(paired(R["S4"], R["S5"], seeds)),
        "radius_effect_rot2": msd(paired(R["R4"], R["R5"], seeds)),
        "gap_difference_4_minus_5": dict(msd(dd), positive=sum(d > 0 for d in dd)),
        "per_world": {"gap_radius5": gap5, "gap_radius4": gap4, "difference": dd},
    }
    ctx = json.loads(CONTEXT_20.read_text())["gap_by_size"]["20"]
    out["r1"]["context_20x20_gap"] = {"mean": ctx["mean"], "sd": ctx["sd"], "source": str(CONTEXT_20.relative_to(HERE.parent))}
    out["r2"] = {}
    for i, name in enumerate(SEATS):
        f = lambda r, i=i: r["mean_happiness"][i]
        out["r2"][name] = {
            "team": {k: st.mean(f(R[k][w]) for w in seeds) for k in ("S5", "R5", "S4", "R4")},
            "gap_radius5": msd(paired(R["R5"], R["S5"], seeds, f)),
            "gap_radius4": msd(paired(R["R4"], R["S4"], seeds, f)),
            "difference": msd([a - b for a, b in zip(paired(R["R4"], R["S4"], seeds, f),
                                                      paired(R["R5"], R["S5"], seeds, f))])}
    out["r3"] = {k: welfare(R[k], seeds) for k in ("S5", "R5", "S4", "R4")}
    out["r4"] = identity(R["S4"], R["V4"], seeds)
    out["r4_s5_vs_armed_rerun"] = identity(R["S5"], R["A5"], seeds)
    out["binding_sha256"] = {k: heads[k]["provenance"]["binding_artifacts"][0]["sha256"] for k in heads}
    return out


def md(out):
    r1 = out["r1"]
    L = ["| cell | team happiness | sd |", "|---|---|---|"]
    for k, lab in (("S5", "scripted, radius 5"), ("R5", "rot2, radius 5"),
                   ("S4", "scripted, radius 4"), ("R4", "rot2, radius 4")):
        t = out["team"][k]
        L.append(f"| {lab} | {t['mean']:.3f} | {t['sd']:.3f} |")
    L += ["", "| paired quantity (30 worlds) | mean | sd | se | positive/30 |", "|---|---|---|---|---|"]
    for k, lab in (("gap_radius5", "gap rot2 − scripted, radius 5 (law)"),
                   ("gap_radius4", "gap rot2 − scripted, radius 4"),
                   ("radius_effect_scripted", "radius 4 − 5, scripted"),
                   ("radius_effect_rot2", "radius 4 − 5, rot2"),
                   ("gap_difference_4_minus_5", "gap at 4 − gap at 5")):
        m = r1[k]
        L.append(f"| {lab} | {m['mean']:+.3f} | {m['sd']:.3f} | {m['se']:.3f} | {m.get('positive', '—')} |")
    c = r1["context_20x20_gap"]
    L.append(f"\n20×20 cert-leg gap, printed beside (not recomputed): {c['mean']:+.3f} ± {c['sd']:.3f}.")
    L += ["", "| seat | scripted r5 | rot2 r5 | scripted r4 | rot2 r4 | gap r5 | gap r4 | gap r4 − r5 (sd) |", "|---|---|---|---|---|---|---|---|"]
    for name, s in out["r2"].items():
        t = s["team"]
        L.append(f"| {name} | {t['S5']:.3f} | {t['R5']:.3f} | {t['S4']:.3f} | {t['R4']:.3f} | "
                 f"{s['gap_radius5']['mean']:+.3f} | {s['gap_radius4']['mean']:+.3f} | "
                 f"{s['difference']['mean']:+.3f} ({s['difference']['sd']:.3f}) |")
    L += ["", "| cell | worst streak mean | max | ≥ line | aborts |", "|---|---|---|---|---|"]
    for k, w in out["r3"].items():
        L.append(f"| {k} | {w['worst_streak_mean']:.1f} | {w['worst_streak_max']} | {w['at_or_over_line']} | {w['aborts']} |")
    i = out["r4"]
    L.append(f"\nR4 identity check, new scripted radius-4 row vs the pre-law v4 row: "
             f"{i['worlds_compared']} worlds, mismatches {i['mismatches']}, identical={i['identical']}, "
             f"mean_happiness exact={i['mean_happiness_exact']}.")
    j = out["r4_s5_vs_armed_rerun"]
    L.append(f"S5 law row vs the comparator's vocab-armed re-run: identical={j['identical']}, "
             f"mean_happiness exact={j['mean_happiness_exact']}.")
    L.append("config / binding sha256 per row: " + ", ".join(
        f"{k} {out['config_sha256'][k][:8]}/{out['binding_sha256'][k][:8]}" for k in out["config_sha256"]))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "radius-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
