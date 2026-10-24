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
D = R.D
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
    out = {"eval_sets": sets, "n_samples": idx["n"], "seeds": list(SEEDS), "sd_runs": SD_RUNS, "probes": PROBES,
           "R1d_spread": FS.read_all(), "R2d_calibration": heads,
           "R2d_decision": decide(sd, heads["NF-h24+p"]), "R2d_professor_P2": score_p2(heads["NF-h24+p"]),
           "R2d_runs": runs_block(), "provenance": prov}
    out.update(read_addendum(idx))
    pin_committed(out)
    return out


PINNED = ("R1d_spread", "R2d_calibration", "R2d_decision", "R2d_professor_P2", "R2d_runs", "provenance")


def pin_committed(out, path=HERE / "phase1d-read.json"):
    """§Addendum: the gated blocks of the committed read are unchanged by the addendum's reads."""
    if not path.exists():
        return
    ref = json.loads(path.read_text())
    for k in PINNED:
        assert json.loads(json.dumps(out[k], default=float)) == ref[k], k


# ---------------------------------------------------------------- §Addendum: R3d which need, R4d latency

MIN_N = R.MIN_N                       # 200, Phase 1's fail-closed floor
THRESHOLDS = (0.2, 0.5)               # P(grave) operating points read
MEAN_RULE = S.NEED_DISTRESS           # the mean-reading consumer: max over needs of the mean ≥ 90
NEEDS = ("eat", "drink", "sleep", "play", "cuddle")


def grave_needs(idx):
    """(N, 5) bool: the hidden need is at or over the grave edge on the true state."""
    return idx["true"][:, :5] >= S.NEED_DISTRESS


def which_need(idx, score5, sel):
    """R3d for one head: over the samples in `sel` with at least one grave need, is the
    argmax of the five scores one of the grave needs? Pooled and per true grave need
    (fail-closed under MIN_N), top-2, the confusion (true grave need × named need)."""
    g = grave_needs(idx)
    has = g.any(1) & sel
    n = int(has.sum())
    rows = np.arange(idx["n"])
    named = np.argmax(np.asarray(score5, np.float64), axis=1)
    correct = g[rows, named] & has
    top2 = np.argsort(-np.asarray(score5, np.float64), axis=1)[:, :2]
    correct2 = g[rows[:, None], top2].any(1) & has
    per = {}
    for i, nm in enumerate(NEEDS):
        m = g[:, i] & has
        ni = int(m.sum())
        per[nm] = {"n": ni, "accuracy": float(correct[m].mean()) if ni >= MIN_N else None}
    conf = [[int((g[:, i] & has & (named == j)).sum()) for j in range(5)] for i in range(5)]
    return {"n": n, "n_multi": int((g.sum(1) >= 2)[has].sum()),
            "accuracy": float(correct.sum() / n) if n >= MIN_N else None,
            "top2_accuracy": float(correct2.sum() / n) if n >= MIN_N else None,
            "per_need": per, "confusion_true_x_named": conf}


def marginal_need(roles):
    """The most frequent grave need on the TRAINING worlds' truth streams (the which-need baseline)."""
    counts = np.zeros(5, np.int64)
    for nm, r in roles.items():
        for s in r["train"]:
            w = D.load_world(nm, s)
            counts += (w["needs"][:, :, :5] >= S.NEED_DISTRESS).sum((0, 1))
    return int(np.argmax(counts)), counts.tolist()


def baseline_which_need(idx, sel, need):
    g = grave_needs(idx)
    has = g.any(1) & sel
    n = int(has.sum())
    return {"named": NEEDS[need], "n": n, "accuracy": float(g[has, need].mean()) if n >= MIN_N else None}


def episodes(idx):
    """Maximal runs of stratum GRAVE within each (world, observer, friend) slice: list of [onset, end)."""
    code = idx["code"]
    out = []
    for _n, _s, _k, _j, a, b in idx["slices"]:
        g = (code[a:b] == S.GRAVE).astype(np.int8)
        d = np.diff(np.concatenate([[0], g, [0]]))
        for st, en in zip(np.where(d == 1)[0], np.where(d == -1)[0]):
            out.append((a + int(st), a + int(en)))
    return out


def _runs(mask):
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def latency(idx, signal, thresh, eps):
    """R4d for one head × threshold: per episode the first tick at or over `thresh`, as a
    latency from onset (0 = at onset; MISSED when never); split by the friend's visibility to
    the observer at onset; false alarms = above-threshold runs containing no grave tick."""
    above = np.asarray(signal, np.float64) >= thresh
    grave = idx["code"] == S.GRAVE
    rows = []
    for st, en in eps:
        hit = np.where(above[st:en])[0]
        lat = int(hit[0]) if len(hit) else None
        antic = bool(lat == 0 and st > 0 and above[st - 1] and not grave[st - 1])
        rows.append({"onset_visible": bool(idx["vis"][st]), "latency": lat, "length": en - st, "anticipated": antic})

    def stats(rs):
        n = len(rs)
        det = [r["latency"] for r in rs if r["latency"] is not None]
        return {"episodes": n, "detected_frac": len(det) / n if n else None,
                "median_latency": float(np.median(det)) if det else None,
                "p90_latency": float(np.percentile(det, 90)) if det else None,
                "within_10_frac": sum(l <= 10 for l in det) / n if n else None,
                "anticipated_frac": sum(r["anticipated"] for r in rs) / n if n else None,
                "length_median": float(np.median([r["length"] for r in rs])) if n else None,
                "length_p90": float(np.percentile([r["length"] for r in rs], 90)) if n else None}
    out = {"all": stats(rows), "onset_visible": stats([r for r in rows if r["onset_visible"]]),
           "onset_fog": stats([r for r in rows if not r["onset_visible"]])}
    fa = []
    for _n, _s, _k, _j, a, b in idx["slices"]:
        for st, en in _runs(above[a:b]):
            if not grave[a + st:a + en].any():
                fa.append(int(en - st))
    out["false_alarms"] = {"runs": len(fa), "per_10k_ticks": len(fa) / idx["n"] * 1e4,
                           "run_median_length": float(np.median(fa)) if fa else None}
    return out


def msd_tree(per_seed):
    """mean ± SD over seeds of every numeric leaf of structurally identical dicts (None leaves skipped by R.msd)."""
    first = per_seed[0]
    if isinstance(first, dict):
        return {k: msd_tree([p[k] for p in per_seed]) for k in first}
    if isinstance(first, (int, float)) or first is None:
        return R.msd([p for p in per_seed])
    return first


def read_addendum(idx):
    roles = D.roles()
    need, counts = marginal_need(roles)
    sd_mass = [C.load_field(run, idx, "grave").astype(np.float64) for run in SD_RUNS]
    sd_mean = [R.load_pred(run, idx)[:, :5] for run in SD_RUNS]
    nf_mean = [R.load_pred(f"NF-h24-s{s}", idx)[:, :5] for s in SEEDS]
    dr_mean = [R.load_pred(f"DR-h24-s{s}", idx)[:, :5] for s in SEEDS]
    scores = {"SD-w16 grave mass": sd_mass, "SD-w16 mean": sd_mean, "NF-h24 mean": nf_mean, "DR-h24 mean": dr_mean}
    r3 = {"baseline_need": NEEDS[need], "train_grave_need_counts": dict(zip(NEEDS, counts)), "heads": {}, "baseline": {}}
    for v in VERSIONS:
        sel = sel_for(idx, v)
        r3["baseline"][v] = baseline_which_need(idx, sel, need)
        for h, sc in scores.items():
            per = [which_need(idx, s5, sel) for s5 in sc]
            r3["heads"].setdefault(h, {})[v] = {"per_seed": per, **msd_tree([{k: p[k] for k in ("n", "n_multi", "accuracy", "top2_accuracy")} for p in per]),
                                                "per_need": msd_tree([p["per_need"] for p in per])}
    eps = episodes(idx)
    probs = {"SD-w16 P": [C.grave_probability(m) for m in sd_mass],
             "NF-h24+p": [load_p(run, idx) for run in PROBES["NF"]], "DR-h24+p": [load_p(run, idx) for run in PROBES["DR"]]}
    means = {"SD-w16 mean ≥ 90": sd_mean, "NF-h24 mean ≥ 90": nf_mean, "DR-h24 mean ≥ 90": dr_mean}
    r4 = {"episodes_total": len(eps), "heads": {}}
    for h, ps in probs.items():
        for t in THRESHOLDS:
            per = [latency(idx, p, t, eps) for p in ps]
            r4["heads"][f"{h} ≥ {t}"] = {"per_seed": per, **msd_tree(per)}
    for h, ms in means.items():
        per = [latency(idx, m.max(1), MEAN_RULE, eps) for m in ms]
        r4["heads"][h] = {"per_seed": per, **msd_tree(per)}
    nf = r3["heads"]["NF-h24 mean"]["visible"]
    cells = [c["accuracy"]["mean"] for c in nf["per_need"].values() if c["n"]["mean"] >= MIN_N and c["accuracy"] is not None]
    rule_i = bool(nf["accuracy"]["mean"] >= 0.80 and all(c > 0.60 for c in cells))
    lat = r4["heads"]["NF-h24+p ≥ 0.2"]["onset_visible"]
    rule_ii = bool(lat["detected_frac"]["mean"] >= 0.90 and lat["median_latency"]["mean"] <= 10)
    mean_rule = r4["heads"]["NF-h24 mean ≥ 90"]["onset_visible"]["detected_frac"]["mean"]
    rules = {"i_which_need": {"accuracy": nf["accuracy"]["mean"], "per_need_min": min(cells) if cells else None, "holds": rule_i},
             "ii_latency": {"detected_frac": lat["detected_frac"]["mean"], "median_latency": lat["median_latency"]["mean"], "holds": rule_ii},
             "prediction_mean_rule_under_half": {"detected_frac": mean_rule, "holds": bool(mean_rule < 0.5)},
             "verdict": "enough for detection and naming, on this evidence" if rule_i and rule_ii else ("partial" if rule_i or rule_ii else "not ready as read")}
    return {"R3d_which_need": r3, "R4d_latency": r4, "addendum_rules": rules}


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
    if "R3d_which_need" in out:
        L += md_addendum(out)
    return "\n".join(L)


def md_addendum(out):
    L = []
    r3 = out["R3d_which_need"]
    L.append(f"\n## Addendum\n\n### R3d: which need — argmax of the five per-need scores is a grave need (need-grave samples; mean ± SD over seeds; None = under {MIN_N})")
    L.append(f"baseline: always name {r3['baseline_need']} (training-world grave-need counts " + ", ".join(f"{k} {v}" for k, v in r3["train_grave_need_counts"].items()) + ")")
    for v in VERSIONS:
        b = r3["baseline"][v]
        L.append(f"\n#### R3d {v}: n {b['n']}; baseline ({b['named']}) {fmt(b['accuracy'])}")
        L.append("| head | accuracy | top-2 | " + " | ".join(f"{n} (n)" for n in NEEDS) + " | n multi-grave |")
        L.append("|---|---|---|" + "---|" * 5 + "---|")
        for h, hv in r3["heads"].items():
            c = hv[v]
            L.append(f"| {h} | {fmt(c['accuracy'])} | {fmt(c['top2_accuracy'])} | "
                     + " | ".join(f"{fmt(c['per_need'][n]['accuracy'])} ({c['per_need'][n]['n']['mean']:.0f})" for n in NEEDS) + f" | {c['n_multi']['mean']:.0f} |")
    nf = r3["heads"]["NF-h24 mean"]["visible"]["per_seed"]
    L.append("\n#### R3d confusion, NF-h24 mean in sight (true grave need × named need; counts summed over seeds)")
    L.append("| true \\ named | " + " | ".join(NEEDS) + " |")
    L.append("|---|" + "---|" * 5)
    conf = np.sum([p["confusion_true_x_named"] for p in nf], axis=0)
    for i, n in enumerate(NEEDS):
        L.append(f"| {n} | " + " | ".join(str(int(x)) for x in conf[i]) + " |")
    r4 = out["R4d_latency"]
    L.append(f"\n### R4d: latency — {r4['episodes_total']} grave episodes (per observer); detected fraction, median / p90 latency in ticks among detected, within 10 ticks of onset, anticipated (already above at onset), false-alarm runs per 10,000 observer-ticks (median run length)")
    for split in ("onset_visible", "onset_fog", "all"):
        L.append(f"\n#### R4d {split}")
        L.append("| head | episodes | detected | median lat | p90 lat | within 10 | anticipated | length median / p90 | FA / 10k (len) |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for h, hv in r4["heads"].items():
            c = hv[split]
            fa = hv["false_alarms"]
            L.append(f"| {h} | {c['episodes']['mean']:.0f} | {fmt(c['detected_frac'])} | {fmt(c['median_latency'], 1)} | {fmt(c['p90_latency'], 1)} | "
                     f"{fmt(c['within_10_frac'])} | {fmt(c['anticipated_frac'])} | {fmt(c['length_median'], 0)} / {fmt(c['length_p90'], 0)} | "
                     f"{fmt(fa['per_10k_ticks'], 2)} ({fmt(fa['run_median_length'], 1)}) |")
    r = out["addendum_rules"]
    L.append(f"\n### Addendum reading rules: (i) NF-h24 mean which-need in sight {r['i_which_need']['accuracy']:.3f} (per-need min {fmt(r['i_which_need']['per_need_min'])}) → holds {r['i_which_need']['holds']}; "
             f"(ii) NF-h24+p ≥ 0.2, onset in sight: detected {r['ii_latency']['detected_frac']:.3f}, median latency {r['ii_latency']['median_latency']:.1f} → holds {r['ii_latency']['holds']}; "
             f"mean ≥ 90 rule detects {r['prediction_mean_rule_under_half']['detected_frac']:.3f} (prediction: under half → {r['prediction_mean_rule_under_half']['holds']}); verdict: {r['verdict']}")
    return L


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
