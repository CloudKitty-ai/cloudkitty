#!/usr/bin/env python3
"""Phase 1c reads R1c–R8c (DECLARATION.md §Reads; descriptive). Runs the
Phase 1 reader (../minifriend-phase1-2026-10-22/read_phase1.py, every
cell, pin and baseline unchanged) on the width-24 comparators (NF-h24,
DR-h24, Phase 1b's runs symlinked here) and on the SD runs, per
evaluation GROUP — P = the per-cat grave worlds P1..P5, G = Phase 1's
all-grave worlds — then adds the contrasts and the belief reads.
Nothing here gates.

    MINIFRIEND_ARC=$PWD read_phase1c.py --out phase1c-read.json --md > phase1c-read.md

Provenance pin: the comparators' pooled mind-visible GRAVE cells on P
must equal Phase 1b's gated read at width 24 (asserted; guard t6).
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
PHASE1B = HERE.parent / "minifriend-phase1b-2026-10-23"
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(PHASE1B))
sys.path.insert(0, str(PHASE1))
import read_phase1 as R  # noqa: E402
from read_phase1b import ratio  # noqa: E402  (the first-order-SD ratio with 1b's READ rule)
import strata as S  # noqa: E402

D = R.D
SEEDS = (1, 2, 3)
sys.path.insert(0, str(HERE))
from sd_head import WIDTHS, run_name  # noqa: E402  (§Addendum: widths 8 / 16 / 32 and their run names)

DECLARED = 16                                                              # the declared head; the criteria read here
RUNS_SD = {h: [("SD", run_name(h, s)) for s in SEEDS] for h in WIDTHS}     # per width
RUNS_CMP = [(h, f"{h}-h24-s{s}") for h in ("NF", "DR") for s in SEEDS]
GROUPS = {"P": ["P1", "P2", "P3", "P4", "P5"], "G": ["G"]}
CLASSES = ("GRAVE", "DA", "COMMON")
GRAVE_POINTS = S.NEED_DISTRESS            # 90
N_REL_BINS = 10
NORES_TOL = 2.0                            # R6c reading rule: structure carries the fit if nores GRAVE loss ≤ 2× full


# ---------------------------------------------------------------- sample-level loaders

def load_field(run, idx, key, file="belief"):
    """(N, 5) float32 of `key` from results-raw/heads/<run>/<file>-<set>-<seed>.npz over the eval index."""
    out = np.empty((idx["n"], 5), np.float32)
    cache = {}
    for n, s, k, j, a, b in idx["slices"]:
        if (n, s) not in cache:
            cache[(n, s)] = np.load(R.ARC / "results-raw/heads" / run / f"{file}-{n}-{s}.npz")[key]
        out[a:b] = cache[(n, s)][:, k, j]
    return out


def relief_truth(idx):
    """(N, 5) {0,1}: the need fell since the previous tick of the same (world, observer, friend) sequence; 0 at t = 0."""
    rel = np.zeros((idx["n"], 5), np.float32)
    t = idx["true"]
    for _n, _s, _k, _j, a, b in idx["slices"]:
        rel[a + 1:b] = t[a + 1:b, :5] < t[a:b - 1, :5] - 1e-4
    return rel


# ---------------------------------------------------------------- belief arithmetic

def grave_probability(mass):
    """P(any need ≥ 90) from per-need grave masses (N, 5), needs independent: 1 − ∏(1 − m)."""
    return 1.0 - np.prod(1.0 - np.asarray(mass, np.float64), axis=-1)


def reliability(p, g, n_bins=N_REL_BINS):
    """Reliability table over equal-width probability bins: count, mean p, realised grave fraction per bin."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    which = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for i in range(n_bins):
        m = which == i
        n = int(m.sum())
        rows.append({"lo": float(edges[i]), "hi": float(edges[i + 1]), "n": n,
                     "mean_p": float(p[m].mean()) if n else None, "frac_grave": float(g[m].mean()) if n else None})
    assert sum(r["n"] for r in rows) == len(p)
    return rows


def auroc(score, label):
    """Mann–Whitney AUROC with average ranks for ties; None if one class is empty."""
    score = np.asarray(score, np.float64).ravel()
    label = np.asarray(label).ravel() > 0.5
    n1, n0 = int(label.sum()), int((~label).sum())
    if n1 == 0 or n0 == 0:
        return None
    _u, inverse, counts = np.unique(score, return_inverse=True, return_counts=True)
    # np.unique sorts: tie group g occupies sorted positions start_g … start_g + counts_g − 1 (0-based),
    # 1-based ranks start_g + 1 … start_g + counts_g, average start_g + (counts_g + 1) / 2
    start = np.cumsum(counts) - counts
    avg = start.astype(np.float64) + (counts + 1) / 2.0
    ranks = avg[inverse]
    r1 = ranks[label].sum()
    return float((r1 - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def calibration(idx, mass, version):
    """R4c for one run: per version, Brier, separation, reliability, and the happiness-only grave count."""
    sel = idx["vis"] if version == "visible" else np.ones(idx["n"], bool)
    p = grave_probability(mass[sel])
    code = idx["code"][sel]
    g = (code == S.GRAVE).astype(np.float64)
    hap_only = int(((code == S.GRAVE) & (idx["true"][sel][:, :5].max(1) < GRAVE_POINTS)).sum())
    return {"n": int(sel.sum()), "n_grave": int(g.sum()), "n_grave_happiness_only": hap_only,
            "brier": float(((p - g) ** 2).mean()),
            "mean_p_on_GRAVE": float(p[g > 0.5].mean()) if g.any() else None,
            "mean_p_on_COMMON": float(p[code == S.COMMON].mean()),
            "mean_p_on_ADJACENT": float(p[code == S.ADJACENT].mean()) if (code == S.ADJACENT).any() else None,
            "reliability": reliability(p, g)}


def empirical_rates(roles):
    """R5c's descriptor: per friend × hidden need, the median positive one-tick change on the TRAINING worlds' truth streams."""
    pos = [[[] for _ in range(5)] for _ in range(D.ROSTER)]
    for n, r in roles.items():
        for s in r["train"]:
            w = D.load_world(n, s)
            d = np.diff(w["needs"][:, :, :5], axis=0)              # (T−1, 5 kitties, 5 needs), points
            for j in range(D.ROSTER):
                for i in range(5):
                    x = d[:, j, i]
                    pos[j][i].append(x[x > 0])
    return [[float(np.median(np.concatenate(pos[j][i]))) for i in range(5)] for j in range(D.ROSTER)]


# ---------------------------------------------------------------- the read

def head_block(runs, idx, sub=""):
    cells = [R.cells_for(R.load_pred(run + sub, idx), idx) for _h, run in runs]
    return {"runs": [run + sub for _h, run in runs], "cells": cells,
            **{f: R.across_seeds(cells, f) for f in ("mse5", "bias", "mse_hap", "mse_bath")}}


_GROUP_CACHE = {}


def group_base(sets):
    """The comparator read, the sample index and the relief truth of a group, computed once and shared by the widths."""
    key = tuple(sets)
    if key not in _GROUP_CACHE:
        idx = R.eval_index(sets)
        _GROUP_CACHE[key] = (R.read(RUNS_CMP, sets), idx, relief_truth(idx))      # NF / DR cells, baselines, coverage, R2, R4
    return _GROUP_CACHE[key]


def read_group(sets, runs, full=True):
    base, idx, rel = group_base(sets)
    sd = head_block(runs, idx)
    nores = head_block(runs, idx, "/nores")
    heads = {"NF": base["heads"]["NF"], "DR": base["heads"]["DR"],
             "SD": {k: v for k, v in sd.items() if k != "cells"}, "SD_nores": {k: v for k, v in nores.items() if k != "cells"}}
    out = {"eval_sets": base["eval_sets"], "eval_worlds": base["eval_worlds"], "n_samples": base["n_samples"],
           "coverage": base["coverage"], "baselines": base["baselines"], "heads": heads,
           "R2c_contrast": {cmp: {v: {cls: ratio(heads["SD"]["mse5"][v][cls]["pooled"], heads[cmp]["mse5"][v][cls]["pooled"])
                                       for cls in CLASSES} for v in R.VERSIONS} for cmp in ("NF", "DR")},
           "R3c_ostrich": {h: R.ostrich(heads[h]["bias"]) for h in ("SD", "NF", "DR")},
           "R6c_residual_share": {v: {cls: ratio(heads["SD_nores"]["mse5"][v][cls]["pooled"], heads["SD"]["mse5"][v][cls]["pooled"])
                                      for cls in CLASSES} for v in R.VERSIONS}}
    out["R6c_structure_carries"] = {v: (out["R6c_residual_share"][v]["GRAVE"] is not None
                                        and out["R6c_residual_share"][v]["GRAVE"]["ratio"] <= NORES_TOL) for v in R.VERSIONS}
    if not full:
        return out
    cal, aur = {v: [] for v in R.VERSIONS}, {v: [] for v in R.VERSIONS}
    for _h, run in runs:
        mass = load_field(run, idx, "grave")
        prel = load_field(run, idx, "p_rel")
        for v in R.VERSIONS:
            cal[v].append(calibration(idx, mass, v))
            sel = idx["vis"] if v == "visible" else np.ones(idx["n"], bool)
            aur[v].append(auroc(prel[sel], rel[sel]))
        fog = ~idx["vis"]
        aur.setdefault("fog", []).append(auroc(prel[fog], rel[fog]))
    out["R4c_calibration"] = {v: {"per_seed": cal[v],
                                  "brier": R.msd([c["brier"] for c in cal[v]]),
                                  "mean_p_on_GRAVE": R.msd([c["mean_p_on_GRAVE"] for c in cal[v]]),
                                  "mean_p_on_COMMON": R.msd([c["mean_p_on_COMMON"] for c in cal[v]]),
                                  "n_grave_happiness_only": cal[v][0]["n_grave_happiness_only"], "n_grave": cal[v][0]["n_grave"],
                                  "reliability_seed_mean": [{"lo": r0["lo"], "hi": r0["hi"], "n": r0["n"],
                                                             "mean_p": R.msd([c["reliability"][i]["mean_p"] for c in cal[v]]),
                                                             "frac_grave": R.msd([c["reliability"][i]["frac_grave"] for c in cal[v]])}
                                                            for i, r0 in enumerate(cal[v][0]["reliability"])]}
                              for v in R.VERSIONS}
    out["R6c_prel_auroc"] = {k: R.msd(vals) for k, vals in aur.items()}
    out["R7c_floors"] = {"SD_vs_DR": R.dissolution(heads["SD"]["mse5"], heads["DR"]["mse5"]),
                         "SD_vs_NF": R.dissolution(heads["SD"]["mse5"], heads["NF"]["mse5"]),
                         "NF_vs_DR": base["R2"]}
    return out


def provenance(readP):
    """The comparators re-read here equal Phase 1b's gated width-24 read on group P (pooled mind-visible GRAVE)."""
    ref = json.loads((PHASE1B / "phase1b-read.json").read_text())["reads"]["24"]["P"]["heads"]
    for h in ("NF", "DR"):
        for f in ("mse5", "bias"):
            a, b = readP["heads"][h][f]["visible"]["GRAVE"]["pooled"], ref[h][f]["visible"]["GRAVE"]["pooled"]
            assert abs(a["mean"] - b["mean"]) < 1e-6 and abs(a["sd"] - b["sd"]) < 1e-6, (h, f, a, b)
    return {"checked_against": str(PHASE1B / "phase1b-read.json"), "width": 24, "cells": "pooled mind-visible GRAVE mse5 + bias, NF and DR"}


def runs_block():
    out = {}
    for h in WIDTHS:
        for _h, run in RUNS_SD[h]:
            man = json.loads((R.ARC / "results-raw/heads" / run / "run-manifest.json").read_text())
            done = json.loads((R.ARC / "results-raw/heads" / run / "done.json").read_text())
            assert man["hidden"] == h and man["over_cap"] == (man["params"] > man["param_cap"]), (run, man["hidden"], man["over_cap"])
            out[run] = {"width": h, "params": man["params"], "param_cap": man["param_cap"], "over_cap": man["over_cap"],
                        "best_epoch": done["best_epoch"], "epochs_run": done["epochs_run"], "best_val": done["best_val"],
                        "rates_points_per_tick": done["rates_points_per_tick"], "relief_points_per_tick": done["relief_points_per_tick"]}
    return out


def size_effect(reads):
    """R9c: 1b's R2b rule on SD — pooled loss at width h over the loss at the declared width, per group × version × class."""
    return {g: {str(h): {v: {cls: ratio(reads[str(h)][g]["heads"]["SD"]["mse5"][v][cls]["pooled"],
                                   reads[str(DECLARED)][g]["heads"]["SD"]["mse5"][v][cls]["pooled"])
                             for cls in CLASSES} for v in R.VERSIONS}
                for h in WIDTHS if h != DECLARED} for g in GROUPS}


def read_all():
    reads = {str(h): {"P": read_group(GROUPS["P"], RUNS_SD[h], full=True), "G": read_group(GROUPS["G"], RUNS_SD[h], full=False)}
             for h in WIDTHS}
    prov = provenance(reads[str(DECLARED)]["P"])
    runs = runs_block()
    emp = empirical_rates(D.roles())
    r5 = {"empirical_median_positive_step": emp}
    for h in WIDTHS:
        rates = np.array([runs[r]["rates_points_per_tick"] for _h, r in RUNS_SD[h]])          # (seeds, 5 friends, 5 needs)
        relief = np.array([runs[r]["relief_points_per_tick"] for _h, r in RUNS_SD[h]])
        r5[str(h)] = {"learned_mean": rates.mean(0).tolist(), "learned_sd": rates.std(0, ddof=1).tolist(),
                      "relief_learned_mean": relief.mean(0).tolist(), "relief_learned_sd": relief.std(0, ddof=1).tolist()}
    return {"groups": GROUPS, "seeds": list(SEEDS), "widths": list(WIDTHS), "declared_width": DECLARED,
            "comparators": [r for _h, r in RUNS_CMP], "reads": reads, "provenance": prov,
            "R5c_rates": r5, "R8c_runs": runs, "R9c_size": size_effect(reads)}


# ---------------------------------------------------------------- printer

def fmt(m, d=2):
    if m is None:
        return "—"
    if isinstance(m, dict) and "mean" in m:
        return f"{m['mean']:.{d}f}" + (f" ± {m['sd']:.{d}f}" if m.get("sd") is not None else "")
    return f"{m:.{d}f}"


def fmt_r(r):
    return "—" if r is None else f"{r['ratio']:.3f} ± {r['sd']:.3f}" + (" READ" if r["read"] else "")


NEEDS = ("eat", "drink", "sleep", "play", "cuddle")


ROLE = {8: "the small candidate", 16: "the declared head", 32: "the over-cap probe"}


def md(out):
    L = ["## Phase 1c read (derived columns)"]
    for w in out["widths"]:                                   # `w`, not `h`: the per-head loops below bind h to "SD" / "NF" / "DR"
      for g, rd in out["reads"][str(w)].items():
        L.append(f"\n### Width {w} ({ROLE[w]}), group {g} ({', '.join(out['groups'][g])} eval worlds): n_samples {rd['n_samples']}")
        cov = rd["coverage"]["visible"]["GRAVE"]
        L.append("coverage GRAVE mind-visible: " + ", ".join(f"{f} {n}" for f, n in cov.items()))
        for v in R.VERSIONS:
            L.append(f"\n#### R1c {v}: pooled mse5 on the five hidden needs (mean ± SD over seeds) and pooled bias")
            L.append("| head | " + " | ".join(f"{cls} mse5" for cls in CLASSES) + " | " + " | ".join(f"{cls} bias" for cls in CLASSES) + " |")
            L.append("|---|" + "---|" * 6)
            for h in ("SD", "NF", "DR", "SD_nores"):
                hd = rd["heads"][h]
                L.append(f"| {h} | " + " | ".join(fmt(hd["mse5"][v][cls]["pooled"]) for cls in CLASSES) + " | "
                         + " | ".join(fmt(hd["bias"][v][cls]["pooled"]) for cls in CLASSES) + " |")
            b = rd["baselines"]
            L.append("baselines mse5 (marginal / proxy): " + "; ".join(
                f"{cls} {fmt(b['marginal']['mse5'][v][cls]['pooled'])} / {fmt(b['persistence']['mse5'][v][cls]['pooled'])}" for cls in CLASSES))
            L.append(f"\n#### R1c {v} per friend: mse5 GRAVE / COMMON per head")
            L.append("| friend | SD GRAVE | NF GRAVE | DR GRAVE | SD COMMON | NF COMMON | DR COMMON |")
            L.append("|---|---|---|---|---|---|---|")
            for f in list(cov) + ["pooled"]:
                L.append(f"| {f} | " + " | ".join(fmt(rd["heads"][h]["mse5"][v][cls].get(f)) for cls in ("GRAVE", "COMMON") for h in ("SD", "NF", "DR")) + " |")
            L.append(f"\n#### R2c {v}: SD loss over the comparator's, per class (READ when |r − 1| > SD)")
            L.append("| comparator | " + " | ".join(CLASSES) + " |")
            L.append("|---|---|---|---|")
            for cmp in ("NF", "DR"):
                L.append(f"| SD / {cmp} | " + " | ".join(fmt_r(rd["R2c_contrast"][cmp][v][cls]) for cls in CLASSES) + " |")
            L.append(f"\n#### R3c {v}: bias grave / common / gap (need points), SIG = signature, per head")
            L.append("| friend | SD | NF | DR |")
            L.append("|---|---|---|---|")
            for f in list(cov) + ["pooled"]:
                cells = []
                for h in ("SD", "NF", "DR"):
                    o = rd["R3c_ostrich"][h][v].get(f)
                    cells.append("insufficient" if not o or not o.get("covered", True) else
                                 f"{o['grave_bias']:+.2f} / {o['common_bias']:+.2f} / {o['gap']:+.2f}" + (" SIG" if o["signature"] else ""))
                L.append(f"| {f} | " + " | ".join(cells) + " |")
            L.append(f"\n#### R6c(a) {v}: residual share — SD with the residual zeroed over the full head, per class: "
                     + ", ".join(f"{cls} {fmt_r(rd['R6c_residual_share'][v][cls])}" for cls in CLASSES)
                     + f" → structure carries the fit (GRAVE ≤ {NORES_TOL}×): {rd['R6c_structure_carries'][v]}")
        if "R4c_calibration" not in rd:
            continue
        for v in R.VERSIONS:
            c = rd["R4c_calibration"][v]
            L.append(f"\n#### R4c {v}: grave probability 1 − ∏(1 − m): Brier {fmt(c['brier'], 4)}; mean p on GRAVE {fmt(c['mean_p_on_GRAVE'], 3)}, "
                     f"on COMMON {fmt(c['mean_p_on_COMMON'], 3)}; GRAVE samples {c['n_grave']}, of which happiness-only {c['n_grave_happiness_only']}")
            L.append("| p bin | n | mean p | realised grave fraction |")
            L.append("|---|---|---|---|")
            for r in c["reliability_seed_mean"]:
                L.append(f"| [{r['lo']:.1f}, {r['hi']:.1f}) | {r['n']} | {fmt(r['mean_p'], 3)} | {fmt(r['frac_grave'], 3)} |")
        a = rd["R6c_prel_auroc"]
        L.append(f"\n#### R6c(b): p_rel AUROC against the true relief indicator — in sight {fmt(a['visible'], 3)}, under fog {fmt(a['fog'], 3)}, all {fmt(a['all'], 3)}")
        for key, label in (("SD_vs_DR", "SD against the DR floor"), ("SD_vs_NF", "SD against NF"), ("NF_vs_DR", "NF against the DR floor (1b's R3b at width 24)")):
            d = rd["R7c_floors"][key]
            if d and d.get("readable"):
                L.append(f"\n#### R7c {label}: floor {d['floor_dr_grave']:.2f}, candidate pooled {d['nf_grave']:.2f}, ratio {d['ratio']:.3f}, "
                         f"pooled_ok {d['pooled_ok']}, friends_ok {d['friends_ok']} → clears {d['dissolves']}")
                L.append("| friend | candidate grave | floor grave | excess over 1.10 × floor | candidate SD | clause |")
                L.append("|---|---|---|---|---|---|")
                for f, pf in d["per_friend"].items():
                    L.append(f"| {f} | {pf['nf']:.2f} | {pf['dr']:.2f} | {pf['excess']:+.2f} | {pf['nf_sd']:.2f} | {'ok' if pf['ok'] else 'EXCEEDS'} |"
                             if pf.get("covered") else f"| {f} | insufficient | insufficient | — | — | not read |")
    L.append(f"\n### R9c: size effect — SD pooled mse5 at width h over width {out['declared_width']} (first-order SD; READ when |r − 1| > SD)")
    L.append("| group | version | " + " | ".join(f"w{h} {cls}" for h in out["widths"] if h != out["declared_width"] for cls in CLASSES) + " |")
    L.append("|---|---|" + "---|" * (3 * (len(out["widths"]) - 1)))
    for g, byw in out["R9c_size"].items():
        for v in R.VERSIONS:
            L.append(f"| {g} | {v} | " + " | ".join(fmt_r(byw[str(h)][v][cls]) for h in out["widths"] if h != out["declared_width"] for cls in CLASSES) + " |")
    emp = out["R5c_rates"]["empirical_median_positive_step"]
    for h in out["widths"]:
        r5 = out["R5c_rates"][str(h)]
        L.append(f"\n### R5c width {h}: learned rise rates (points per tick, mean ± SD over seeds) against the training worlds' median positive step")
        L.append("| friend | " + " | ".join(f"{n} learned / empirical" for n in NEEDS) + " |")
        L.append("|---|" + "---|" * 5)
        for j, f in enumerate(R.SEATS):
            L.append(f"| {f} | " + " | ".join(f"{r5['learned_mean'][j][i]:.2f} ± {r5['learned_sd'][j][i]:.2f} / {emp[j][i]:.2f}" for i in range(5)) + " |")
        L.append("relief sizes learned (points per relieving tick): " + ", ".join(f"{n} {r5['relief_learned_mean'][i]:.2f} ± {r5['relief_learned_sd'][i]:.2f}" for i, n in enumerate(NEEDS)))
    L.append("\n### R8c runs")
    for r, d in out["R8c_runs"].items():
        L.append(f"{r}: width {d['width']} params {d['params']} (cap {d['param_cap']}{', OVER-CAP PROBE' if d['over_cap'] else ''}) "
                 f"best {d['best_epoch']}/{d['epochs_run']} val {d['best_val']:.4f}")
    p = out["provenance"]
    L.append(f"\nprovenance: comparators {', '.join(out['comparators'])} re-read here equal {p['checked_against']} at width {p['width']} on {p['cells']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1c-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
