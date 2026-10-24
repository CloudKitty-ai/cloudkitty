#!/usr/bin/env python3
"""Phase 1d reads R1d and R2d (DECLARATION.md; descriptive, plus the
declared decision rule A / B / C and the scoring of the Professor's
prediction P2). R1d imports filter_spread; R2d reads the probe runs'
`pgrave-*.npz` on group P through Phase 1c's R4c instrument
(`calibration_p`) beside SD width 16 re-read from 1c's belief files
and pinned to 1c's committed read.

    MINIFRIEND_ARC=$PWD read_phase1d.py --out phase1d-read.json --md > phase1d-read.md
"""
import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
PHASE1B = HERE.parent / "minifriend-phase1b-2026-10-23"
PHASE1C = HERE.parent / "minifriend-phase1c-2026-10-23"
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(PHASE1C))
sys.path.insert(0, str(PHASE1B))
sys.path.insert(0, str(PHASE1))
sys.path.insert(0, str(HERE))
import read_phase1c as C  # noqa: E402  (calibration_p, calibration_block, load_field, auroc, GROUPS, run_name, R)
import filter_spread as FS  # noqa: E402
import strata as S  # noqa: E402

R = C.R
SEEDS = (1, 2, 3)
SD_WIDTH = 16
SD_RUNS = [C.run_name(SD_WIDTH, s) for s in SEEDS]
PROBES = {b: [f"{b}-h24-s{s}+p" for s in SEEDS] for b in ("NF", "DR")}
HEADS = ("SD-w16", "NF-h24+p", "DR-h24+p")
VERSIONS = ("visible", "fog", "all")
GAP_LO = 0.7
P2 = {"mean_p_on_GRAVE_min": 0.40, "mean_p_on_COMMON_max": 0.002}      # the Professor's registered prediction, in sight, NF-h24+p


def load_p(run, idx):
    """(N,) float64 probe probability over the eval index."""
    out = np.empty(idx["n"], np.float64)
    cache = {}
    for n, s, k, j, a, b in idx["slices"]:
        if (n, s) not in cache:
            cache[(n, s)] = np.load(HERE / "results-raw/probe" / run / f"pgrave-{n}-{s}.npz")["p"]
        out[a:b] = cache[(n, s)][:, k, j]
    return out


def sel_for(idx, version):
    if version == "visible":
        return idx["vis"]
    if version == "fog":
        return ~idx["vis"]
    return np.ones(idx["n"], bool)


def gap_above(rows, lo=GAP_LO):
    """The above-0.7 gap: mean over the reliability bins with lower edge ≥ lo of |seed-mean p − seed-mean realised fraction|."""
    gaps = [abs(r["mean_p"]["mean"] - r["frac_grave"]["mean"]) for r in rows
            if r["lo"] >= lo - 1e-9 and r["mean_p"] is not None and r["frac_grave"] is not None]
    return float(np.mean(gaps)) if gaps else None


def head_read(ps, idx):
    """Per version: 1c's calibration block over seeds + the above-0.7 gap, mean p on happiness-only GRAVE, AUROC."""
    grave = idx["code"] == S.GRAVE
    hap_only = grave & (idx["true"][:, :5].max(1) < S.NEED_DISTRESS)
    out = {}
    for v in VERSIONS:
        sel = sel_for(idx, v)
        cals = [C.calibration_p(idx, p, sel) for p in ps]
        blk = C.calibration_block(cals)
        blk["above_0.7_gap"] = gap_above(blk["reliability_seed_mean"])
        blk["mean_p_on_GRAVE_happiness_only"] = R.msd([float(p[sel & hap_only].mean()) if (sel & hap_only).any() else None for p in ps])
        blk["auroc"] = R.msd([C.auroc(p[sel], grave[sel]) for p in ps])
        out[v] = blk
    return out


def decide(sd, nf):
    """The declared rule on the in-sight read: A within the spread, B SD clearly better, C otherwise."""
    m_sd, m_nf = sd["visible"]["mean_p_on_GRAVE"], nf["visible"]["mean_p_on_GRAVE"]
    g_sd, g_nf = sd["visible"]["above_0.7_gap"], nf["visible"]["above_0.7_gap"]
    delta = m_sd["mean"] - m_nf["mean"]
    s = math.sqrt(m_sd["sd"] ** 2 + m_nf["sd"] ** 2)
    if abs(delta) <= s:
        outcome = "A"
    elif delta > s and g_sd < g_nf:
        outcome = "B"
    else:
        outcome = "C"
    return {"m_SD": m_sd, "m_NF": m_nf, "delta": delta, "s": s, "gap_SD": g_sd, "gap_NF": g_nf, "outcome": outcome,
            "text": {"A": "within the spread: the histogram bought nothing the consumer needs; the hybrid is the candidate shape; the SD line closes",
                     "B": "SD clearly better calibrated: one loop-fixed, diffusion-fixed SD run at the cap would be justified (her word)",
                     "C": "mixed or reversed: reported as such; the shape question is hers"}[outcome]}


def score_p2(nf):
    v = nf["visible"]
    g, c = v["mean_p_on_GRAVE"]["mean"], v["mean_p_on_COMMON"]["mean"]
    return {"prediction": "NF-h24+p: mean P(grave) on GRAVE ≥ 0.40 and ≤ 0.002 on COMMON, in sight (Professor, review §3)",
            "mean_p_on_GRAVE": g, "mean_p_on_COMMON": c, "bars": P2,
            "met": bool(g >= P2["mean_p_on_GRAVE_min"] and c <= P2["mean_p_on_COMMON_max"])}


def provenance(sd):
    """SD width 16 re-read here equals 1c's committed R4c (in sight and all); the base heads are the files 1b finished with."""
    ref = json.loads((PHASE1C / "phase1c-read.json").read_text())["reads"][str(SD_WIDTH)]["P"]["R4c_calibration"]
    for v in ("visible", "all"):
        for f in ("brier", "mean_p_on_GRAVE", "mean_p_on_COMMON"):
            a, b = sd[v][f], ref[v][f]
            assert abs(a["mean"] - b["mean"]) < 1e-9 and abs(a["sd"] - b["sd"]) < 1e-9, (v, f, a, b)
    bases = {}
    for b, runs in PROBES.items():
        for run in runs:
            base = run[:-2]
            done = json.loads((HERE / "results-raw/heads" / base / "done.json").read_text())
            sha = hashlib.sha256((HERE / "results-raw/heads" / base / "head-best.pt").read_bytes()).hexdigest()
            man = json.loads((HERE / "results-raw/probe" / run / "run-manifest.json").read_text())
            assert sha == done["head_sha256"] == man["base_sha256"], (base, sha, done["head_sha256"], man["base_sha256"])
            bases[base] = sha
    return {"sd_checked_against": str(PHASE1C / "phase1c-read.json"), "sd_width": SD_WIDTH,
            "sd_cells": "R4c brier, mean p on GRAVE, mean p on COMMON; in sight and all", "base_head_sha256": bases}


def runs_block():
    out = {}
    for b, runs in PROBES.items():
        for run in runs:
            man = json.loads((HERE / "results-raw/probe" / run / "run-manifest.json").read_text())
            done = json.loads((HERE / "results-raw/probe" / run / "done.json").read_text())
            assert not man["smoke"] and done["base_sha256_after"] == man["base_sha256"]
            out[run] = {"base": man["base"], "params": man["params"], "hybrid_params": man["hybrid_params"], "param_cap": man["param_cap"],
                        "best_epoch": done["best_epoch"], "epochs_run": done["epochs_run"], "best_val_bce": done["best_val_bce"],
                        "train_grave_freq": done["train_grave_freq"], "n_train": done["n_train"],
                        "reproduces_1b_pred_max_abs": man["reproduces_1b_pred_max_abs"], "rel_margin": man["rel_margin"]}
    return out


def read_all():
    sets = C.GROUPS["P"]
    idx = R.eval_index(sets)
    sd = head_read([C.grave_probability(C.load_field(run, idx, "grave")) for run in SD_RUNS], idx)
    heads = {"SD-w16": sd}
    for b, runs in PROBES.items():
        heads[f"{b}-h24+p"] = head_read([load_p(run, idx) for run in runs], idx)
    prov = provenance(sd)
    return {"eval_sets": sets, "n_samples": idx["n"], "seeds": list(SEEDS), "sd_runs": SD_RUNS, "probes": PROBES,
            "R1d_spread": FS.read_all(), "R2d_calibration": heads,
            "R2d_decision": decide(sd, heads["NF-h24+p"]), "R2d_professor_P2": score_p2(heads["NF-h24+p"]),
            "R2d_runs": runs_block(), "provenance": prov}


# ---------------------------------------------------------------- printer

def fmt(m, d=3):
    return C.fmt(m, d)


def md(out):
    L = ["## Phase 1d read (derived columns)"]
    sp = out["R1d_spread"]
    L.append(f"\n### R1d: the filter's spread under pure drift — a delta at bin {sp['start_bin']}, sd in bins (closed form √(n f (1 − f)); 'clamp' = mass at the top bin)")
    L.append("| rate (pts/tick) | " + " | ".join(f"n={n}" for n in sp["ticks"]) + " |")
    L.append("|---|" + "---|" * len(sp["ticks"]))

    def cells(rows):
        return " | ".join(f"{r['sd_bins']:.3f} (cf {r['closed_form_bins']:.3f}{', clamp' if r['clamped'] else ''})" for r in rows)
    L.append(f"| initial 0.40 (every run) | {cells(sp['initial_rate'])} |")
    for run, d in sp["runs"].items():
        for k in ("median", "max", "min"):
            L.append(f"| {run} w{d['width']} {k} cell {d['cells'][k]:.3f} | {cells(d['spread'][k])} |")
    L.append("relief step (one down-shift from bin {}): ".format(sp["relief_start_bin"]) + "; ".join(
        f"{run} " + ", ".join(f"{s['size_points']:.1f}pt→sd {s['sd_bins']:.2f}" for s in d["relief_step"]) for run, d in sp["runs"].items()))
    r = sp["rule"]
    L.append(f"rule: max |sd − closed form| over {r['n_unclamped']} unclamped rows {r['max_abs_diff_bins']:.2e} bins; initial-rate sd after 100 ticks "
             f"{r['init_sd_100_bins']:.3f} bins against the Professor's {r['professor_figure_bins']} → mechanism stands: {r['mechanism_stands']}")
    for v in VERSIONS:
        L.append(f"\n### R2d(a) {v}: grave probability on group P (mean ± SD over seeds)")
        L.append("| head | Brier | mean p GRAVE | mean p COMMON | mean p ADJACENT | mean p happiness-only GRAVE | above-0.7 gap | AUROC | n GRAVE (hap-only) |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for h in HEADS:
            c = out["R2d_calibration"][h][v]
            adj = R.msd([s["mean_p_on_ADJACENT"] for s in c["per_seed"]])
            L.append(f"| {h} | {fmt(c['brier'], 5)} | {fmt(c['mean_p_on_GRAVE'])} | {fmt(c['mean_p_on_COMMON'], 4)} | {fmt(adj)} | "
                     f"{fmt(c['mean_p_on_GRAVE_happiness_only'])} | {fmt(c['above_0.7_gap'])} | {fmt(c['auroc'])} | {c['n_grave']} ({c['n_grave_happiness_only']}) |")
        for h in HEADS:
            c = out["R2d_calibration"][h][v]
            L.append(f"\n#### reliability {v}, {h}")
            L.append("| p bin | n per seed | mean p (seed mean) | realised grave fraction (mean over seeds with samples) |")
            L.append("|---|---|---|---|")
            for rr in c["reliability_seed_mean"]:
                L.append(f"| [{rr['lo']:.1f}, {rr['hi']:.1f}) | {' / '.join(str(n) for n in rr['n'])} | {fmt(rr['mean_p'])} | {fmt(rr['frac_grave'])} |")
    d = out["R2d_decision"]
    L.append(f"\n### R2d decision (in sight, group P): m_SD {fmt(d['m_SD'])}, m_NF {fmt(d['m_NF'])}, Δ {d['delta']:+.3f}, s {d['s']:.3f}; "
             f"above-0.7 gap SD {d['gap_SD']:.3f} / NF+p {d['gap_NF']:.3f} → **{d['outcome']}**: {d['text']}")
    p2 = out["R2d_professor_P2"]
    L.append(f"\n### Professor's P2: {p2['prediction']} — read {p2['mean_p_on_GRAVE']:.3f} / {p2['mean_p_on_COMMON']:.4f} → met: {p2['met']}")
    L.append("\n### R2d(b) runs")
    for run, r in out["R2d_runs"].items():
        L.append(f"{run}: probe {r['params']} params (hybrid {r['hybrid_params']} ≤ {r['param_cap']}); best {r['best_epoch']}/{r['epochs_run']} "
                 f"val BCE {r['best_val_bce']:.6f}; train GRAVE freq {r['train_grave_freq']:.5f} of {r['n_train']}; reproduces 1b's prediction to {r['reproduces_1b_pred_max_abs']:.1e}")
    p = out["provenance"]
    L.append(f"\nprovenance: SD width {p['sd_width']} re-read here equals 1c's committed read on {p['sd_cells']}; base heads "
             + ", ".join(f"{b} {s[:12]}" for b, s in p["base_head_sha256"].items()))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1d-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
