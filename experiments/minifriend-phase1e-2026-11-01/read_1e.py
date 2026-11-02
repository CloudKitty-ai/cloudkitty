#!/usr/bin/env python3
"""Phase 1e — the reads (DECLARATION.md §5), one subcommand each, every
figure the seed mean ± SD over the three retrained heads (NF1e-h24-s1..3
with their probes) beside the frozen NF-h24+p by the SAME reader on the
SAME worlds.

    read_1e.py tuning     --out reads/tuning.json     [--md]   # R-A1: the grid on the needy set's TUNING half; the declared selection -> S
    read_1e.py confirming --out reads/confirming.json [--md]   # R-A2: the CONFIRMING half at S, the pick and the registered point; P16, P17
    read_1e.py splice     --out reads/splice.json     [--md]   # R-B: F-069/F-070's splice with the junction control; the clock read on L; P18
    read_1e.py lived      --out reads/lived.json      [--md]   # R-C: the lived evaluation worlds' false runs and reset detection; P19
    read_1e.py estimate   --out reads/estimate.json   [--md]   # R-D: Phase 1's estimate cells on the 1b evaluation worlds; P20
    read_1e.py score      --out reads/score.json      [--md]   # P16-P20 gathered from the five files

Arc roots: `tuning` / `confirming` run under the needy set's reader
(MINIFRIEND_ARC = Phase 1b, needy_read's default), `splice` / `lived`
under Phase 1d's (history_read's default), `estimate` under Phase 1b's
(read_phase1 on 1b's split). Nothing here imports data_1e. The
confirming half is loaded only by `confirming`, after `tuning` has
written S; every world passes needy_read.refuse_unless for its half.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
PHASE1 = EXPTS / "minifriend-phase1-2026-10-22"
PHASE1B = EXPTS / "minifriend-phase1b-2026-10-23"
PHASE1D = EXPTS / "minifriend-phase1d-2026-10-24"
NEEDY = EXPTS / "needy-set-2026-10-28"
RISE = EXPTS / "probe-rise-2026-11-01"
READS = HERE / "reads"

SEEDS = (1, 2, 3)
THRESHOLDS = (0.02, 0.05, 0.10, 0.20, 0.30, 0.50)
BURNINS = (0, 2)
PICK, REG = "t0.05-B2", "t0.10-B0"                       # her pick (needy set, 2026-11-01) and the registered point of F-071's rows
PRIMARY = ("T-H0", "E-H1", "N-H2", "N-H3", "N-H4")
N_STRATA = ("N-H2", "N-H3", "N-H4")
HISTORIES = (0, 1, 2, 5, 10, 20, 50, 100, 500, 2000)
SPLICE_THRESH = 0.10                                      # the ruling's amendment 2 is written at 0.10 (F-069 / F-070's rows)
R5_PICK = {"T-H0": 1.000, "E-H1": 0.489, "N-H2": 0.596, "N-H3": 0.444, "N-H4": 0.421}   # the frozen probe, confirming half, R5
PRED = {"P16": {"mean_gain": 0.15}, "P17": {"E-H1_drop": 0.05, "T-H0_min": 0.95},
        "P18": {"H100_min_exclusive": 0.358, "H0_min": 0.95, "control_max": 0.05, "control_from_H": 2},
        "P19": {"fa_ratio_max": 2.0}, "P20": {"ratio_max": 1.10}}
GROUP_P = ["P1", "P2", "P3", "P4", "P5"]
GROUP_LWG = ["L", "W", "G"]


def cell_name(th, b):
    return f"t{th:.2f}-B{b}"


def parse_cell(c):
    th, b = c[1:].split("-B")
    return float(th), int(b)


CELLS = [cell_name(th, b) for th in THRESHOLDS for b in BURNINS]


# ---- the heads ------------------------------------------------------------------

def head_e_paths(seed):
    return (HERE / "results-raw" / "heads" / f"NF1e-h24-s{seed}" / "head-best.pt",
            HERE / "results-raw" / "probe" / f"NF1e-h24-s{seed}+p" / "probe.pt")


def load_head_e(seed):
    """(frozen retrained head, frozen probe) for NF1e-h24-s<seed>+p; train_heads must already be importable."""
    import torch
    import train_heads as T
    hp, pp = head_e_paths(seed)
    ck = torch.load(hp, map_location="cpu", weights_only=False)
    model = T.BeliefHead(h=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    pk = torch.load(pp, map_location="cpu", weights_only=False)
    probe = torch.nn.Linear(ck["manifest"]["hidden"], 1)
    probe.load_state_dict(pk["state_dict"])
    for m in (model, probe):
        m.eval()
        for p in m.parameters():
            p.requires_grad_(False)
    return model, probe


def heads_e():
    return {s: load_head_e(s) for s in SEEDS}


def _needy_modules():
    sys.path.insert(0, str(RISE))
    import rise  # noqa: F401  (needy_read, set_run, ladder on the path; MINIFRIEND_ARC = Phase 1b)
    return rise, rise.R, rise.L


# ---- R-A: the needy set (level alarms through the ladder's accounting) ------------------

def level_alarms(P, cells=CELLS):
    """{cell: (bool (T, R, R), first alarmable tick)} — P(grave) >= threshold with the slice's first B ticks forced off."""
    P = np.nan_to_num(P, nan=-1.0)
    out = {}
    for c in cells:
        th, b = parse_cell(c)
        above = P >= th
        above[:b] = False
        out[c] = (above, b)
    return out


def world_record(rise, R, L, arm, k, seed, ticks, path, half, probes, cells):
    R.refuse_unless(arm, k, seed, half)
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None and w["ticks"] == ticks and w["scripted"] == [k - 1], (arm, k, seed)
    fe = L.first_episode(w, arm)
    by_seed = {s: level_alarms(R.probe_world(m, p, w), cells) for s, (m, p) in probes.items()}
    c = rise.cells_from_alarms(w, arm, fe, by_seed, cells)
    return {"arm": arm, "block": k, "seed": seed, "half": half, "ticks": ticks, "friend": fe["friend"], "status": fe["status"],
            "crossing": fe["crossing"], "end": None if fe["crossing"] is None else fe["end"],
            "length": None if fe["crossing"] is None else fe["end"] - fe["crossing"],
            "onset": fe["onset"], "stratum": fe["stratum"], "m": fe["m"], "masked": fe["masked"], "edge": fe["edge"],
            "sight_at_crossing": c["sight_at_crossing"], "observer_ticks": c["observer_ticks"], "cells": c["cells"]}


def records(rise, R, L, half, probes, cells, progress=True):
    ws = rise.worlds(half)
    recs, t0 = [], time.time()
    for i, (arm, k, seed, ticks, path) in enumerate(ws):
        recs.append(world_record(rise, R, L, arm, k, seed, ticks, path, half, probes, cells))
        if progress and (i + 1) % 30 == 0:
            print(f"  {half}: {i + 1}/{len(ws)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    return recs


def _m(x):
    return None if x is None else x["mean"]


def bound_from_ladder():
    """The frozen pick's tuning false-run rates (the needy set's ladder.json): the selection's bound."""
    lad = json.loads((NEEDY / "reads" / "ladder.json").read_text())
    fa = lad["false_alarms"]["N"][PICK]
    return {"fa_cov": fa["covered_friends"]["per_10k_ticks"]["mean"], "fa_scr": fa["scripted_from_first_mask"]["per_10k_ticks"]["mean"]}


def selection_rows(tab, cells=CELLS):
    def fa(cell, cls):
        return _m(tab["false_alarms"]["N"][cell][cls]["per_10k_ticks"])
    rows = {}
    for c in cells:
        th, b = parse_cell(c)
        dets = [tab["groups"][g]["cells"][c]["detected"]["mean"] for g in N_STRATA if g in tab["groups"]]
        rows[c] = {"th": th, "b": b, "det_N": float(np.mean(dets)) if dets else None,
                   "fa_cov": fa(c, "covered_friends"), "fa_scr": fa(c, "scripted_from_first_mask")}
    return rows


def select_from(rows, bound):
    """The declared rule (§5 R-A1): candidates = cells whose arm N covered-friend AND scripted-from-first-mask
    false-run rates are at or under the frozen pick's tuning rates; chosen = the highest mean N-stratum
    detection, ties to the HIGHER threshold then the SMALLER burn-in; None when no cell qualifies."""
    cands = [c for c, r in rows.items()
             if r["det_N"] is not None and r["fa_cov"] is not None and r["fa_scr"] is not None
             and r["fa_cov"] <= bound["fa_cov"] and r["fa_scr"] <= bound["fa_scr"]]
    if not cands:
        return {"bound": bound, "candidates": [], "chosen": None}
    best = sorted(cands, key=lambda c: (-rows[c]["det_N"], -rows[c]["th"], rows[c]["b"]))[0]
    return {"bound": bound, "candidates": sorted(cands), "chosen": best}


def read_tuning(progress=True):
    rise, R, L = _needy_modules()
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    probes = heads_e()
    recs = records(rise, R, L, "tuning", probes, CELLS, progress)
    tab = rise.table(recs, CELLS)
    rows = selection_rows(tab)
    sel = select_from(rows, bound_from_ladder())
    return {"half": "tuning", "head": "NF1e-h24+p", "seeds": list(SEEDS), "cells": CELLS, "table": tab,
            "selection_rows": rows, "selection": sel, "S": sel["chosen"], "records": recs, "seconds": round(time.time() - t0)}


def read_confirming(progress=True):
    rise, R, L = _needy_modules()
    import torch
    torch.set_num_threads(1)
    tun = json.loads((READS / "tuning.json").read_text())
    S = tun["S"]
    cells = [c for c in dict.fromkeys([S, PICK, REG]) if c is not None]
    t0 = time.time()
    new = records(rise, R, L, "confirming", heads_e(), cells, progress)
    frozen = records(rise, R, L, "confirming", {s: R.load_probe(s)[:2] for s in R.PROBE_SEEDS}, cells, progress)
    tab_new, tab_frozen = rise.table(new, cells), rise.table(frozen, cells)
    out = {"half": "confirming", "S": S, "cells": cells, "new": tab_new, "frozen": tab_frozen,
           "records": {"new": new, "frozen": frozen}, "seconds": round(time.time() - t0)}
    out["score"] = score_confirming(tab_new, tab_frozen, S)
    return out


def score_confirming(tab_new, tab_frozen, S):
    def det(tab, cell, g):
        return tab["groups"][g]["cells"][cell]["detected"]["mean"] if g in tab["groups"] else None
    pick = {g: det(tab_frozen, PICK, g) for g in PRIMARY}
    for g, v in R5_PICK.items():
        assert pick[g] is not None and round(pick[g], 3) == v, ("the frozen probe at the pick on the confirming half must reproduce R5", g, pick[g], v)
    out = {"S": S, "frozen_pick": pick}
    if S is None:
        out["P16"] = {"met": False, "reason": "no cell inside the frozen pick's false-run bound on the tuning half"}
        out["P17"] = {"met": False, "reason": "no S"}
        return out
    new_S = {g: det(tab_new, S, g) for g in PRIMARY}
    gains = {g: new_S[g] - pick[g] for g in N_STRATA}
    mg = float(np.mean(list(gains.values())))
    out["P16"] = {"detected_S": {g: new_S[g] for g in N_STRATA}, "detected_frozen_pick": {g: pick[g] for g in N_STRATA},
                  "gain": gains, "mean_gain": mg, "clause_1_each_above": all(v > 0 for v in gains.values()),
                  "clause_2_mean_gain": mg >= PRED["P16"]["mean_gain"]}
    out["P16"]["met"] = out["P16"]["clause_1_each_above"] and out["P16"]["clause_2_mean_gain"]
    out["P17"] = {"E-H1_S": new_S["E-H1"], "E-H1_frozen_pick": pick["E-H1"], "T-H0_S": new_S["T-H0"],
                  "met": new_S["E-H1"] >= pick["E-H1"] - PRED["P17"]["E-H1_drop"] and new_S["T-H0"] >= PRED["P17"]["T-H0_min"]}
    fa = lambda tab, cell: _m(tab["false_alarms"]["N"][cell]["covered_friends"]["per_10k_ticks"])
    out["false_runs_covered_N"] = {"new_S": fa(tab_new, S), "frozen_pick": fa(tab_frozen, PICK), "new_pick": fa(tab_new, PICK)}
    return out


# ---- R-B: the splice and the clock read (Phase 1d's reader) ------------------------------

def _hist_modules():
    os.environ.setdefault("MINIFRIEND_ARC", str(PHASE1D))
    sys.path.insert(0, str(PHASE1D))
    import history_read as HR
    return HR


def committed_splice():
    """The frozen head's committed rows at 0.10: H = 1 … 50 from the knee read, 0r / 100 / 500 / 2000 from the history read."""
    hist = json.loads((PHASE1D / "phase1d-history.json").read_text())["splice"]["NF-h24+p"]
    knee = json.loads((PHASE1D / "phase1d-knee.json").read_text())
    out = {}
    for H in ("0r", "100", "500", "2000"):
        r = hist[H]["0.10"]                                # the seed-mean tree (msd_tree): every leaf {mean, sd, seeds}
        out["0" if H == "0r" else H] = {"detected": r["all"]["detected_frac"]["mean"], "control_fired": r["control_fired"]["mean"]}
    for H, r in knee["splice"]["NF-h24+p"].items():
        if H not in out:                                   # 1, 2, 5, 10, 20, 50 (the knee's 100 re-run equals the history's)
            out[H] = {"detected": r["0.10"]["all"]["detected_frac"]["mean"], "control_fired": r["0.10"]["control_fired"]["mean"]}
    return out


def splice_one(HR, model, probe, donors, recips, thresholds):
    rows = {}
    for H in HISTORIES:
        r = HR.splice_rows_nf(model, probe, donors, recips, H, thresholds=thresholds)
        rows[str(H)] = {f"{t:.2f}": {"detected": r[f"{t:.2f}"]["all"]["detected_frac"], "median_latency": r[f"{t:.2f}"]["all"]["median_latency"],
                                     "control_fired": r[f"{t:.2f}"]["control_fired"], "grave_fired": r[f"{t:.2f}"]["grave_fired"]}
                        for t in thresholds}
    return rows


def read_splice(progress=True):
    HR = _hist_modules()
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    S = json.loads((READS / "tuning.json").read_text())["S"]
    thresholds = tuple(dict.fromkeys([SPLICE_THRESH] + ([parse_cell(S)[0]] if S else [])))
    idx_p = HR.P.R.eval_index(HR.C.GROUPS["P"])
    idx_l = HR.P.R.eval_index([HR.L_SET])
    donors, recips = HR.donor_list(idx_p), HR.recipient_list(idx_l)
    out = {"thresholds": list(thresholds), "histories": list(HISTORIES), "donors": len(donors), "recipients": len(recips),
           "per_seed": {}, "clock": {"per_seed": {}}, "committed_frozen_0.10": committed_splice()}
    for s in SEEDS:
        model, probe = load_head_e(s)
        out["per_seed"][str(s)] = splice_one(HR, model, probe, donors, recips, thresholds)
        _p, hs = HR.signal_over_index(model, probe, idx_l, keep_h=True)
        cv = HR.convergence(list(hs.values()))
        out["clock"]["per_seed"][str(s)] = {k: cv[k] for k in ("logit_profile", "slope_per_1000", "within_slice_sd", "drift_to_scatter")}
        if progress:
            print(f"  splice seed {s} done, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    out["mean_sd"] = {str(H): {f"{t:.2f}": {k: msd([out["per_seed"][str(s)][str(H)][f"{t:.2f}"][k] for s in SEEDS])
                                            for k in ("detected", "median_latency", "control_fired")} for t in thresholds} for H in HISTORIES}
    out["clock"]["logit_profile_mean"] = {k: float(np.mean([out["clock"]["per_seed"][str(s)]["logit_profile"][k] for s in SEEDS]))
                                          for k in out["clock"]["per_seed"]["1"]["logit_profile"]}
    out["clock"]["slope_per_1000_mean"] = float(np.mean([out["clock"]["per_seed"][str(s)]["slope_per_1000"]["mean"] for s in SEEDS]))
    out["score"] = score_splice(out)
    out["seconds"] = round(time.time() - t0)
    return out


def score_splice(out):
    t = f"{SPLICE_THRESH:.2f}"
    ms = out["mean_sd"]
    h100, h0 = ms["100"][t]["detected"]["mean"], ms["0"][t]["detected"]["mean"]
    ctl = {str(H): ms[str(H)][t]["control_fired"]["mean"] for H in HISTORIES if H >= PRED["P18"]["control_from_H"]}
    return {"P18": {"H100_detected": h100, "H100_bar_exclusive": PRED["P18"]["H100_min_exclusive"], "H0_detected": h0, "H0_min": PRED["P18"]["H0_min"],
                    "control_fired_from_H2": ctl, "control_max": PRED["P18"]["control_max"],
                    "clause_H100": h100 > PRED["P18"]["H100_min_exclusive"], "clause_H0": h0 >= PRED["P18"]["H0_min"],
                    "clause_control": all(v <= PRED["P18"]["control_max"] for v in ctl.values()),
                    "met": h100 > PRED["P18"]["H100_min_exclusive"] and h0 >= PRED["P18"]["H0_min"] and all(v <= PRED["P18"]["control_max"] for v in ctl.values())}}


# ---- R-C: the lived evaluation worlds (Phase 1d's R4d reader) -----------------------------

def burn(sig, idx, b):
    s = np.array(sig, copy=True)
    if b:
        for _n, _s, _k, _j, a, _bb in idx["slices"]:
            s[a:a + b] = 0.0
    return s


def lived_rows(P, idx, eps, sig, cells):
    out = {}
    for c in cells:
        th, b = parse_cell(c)
        r = P.latency(idx, burn(sig, idx, b), th, eps)
        out[c] = {"reset_detected": r["reset"]["detected_frac"], "reset_episodes": r["reset"]["episodes"],
                  "fa_per_10k": r["false_alarms"]["per_10k_ticks"], "fa_midworld_per_10k": r["false_alarms"]["midworld_per_10k_ticks"],
                  "fa_runs": r["false_alarms"]["runs"]}
    return out


def read_lived(progress=True):
    HR = _hist_modules()
    P = HR.P
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    S = json.loads((READS / "tuning.json").read_text())["S"]
    cells = [c for c in dict.fromkeys([S, PICK, REG]) if c is not None]
    out = {"S": S, "cells": cells, "groups": {}}
    for gname, sets in (("P", HR.C.GROUPS["P"]), ("LWG", GROUP_LWG)):
        idx = P.R.eval_index(sets)
        eps = P.episodes(idx)
        g = {"observer_ticks": idx["n"], "new": {"per_seed": {}}, "frozen": {"per_seed": {}}}
        for s in SEEDS:
            model, probe = load_head_e(s)
            g["new"]["per_seed"][str(s)] = lived_rows(P, idx, eps, HR.signal_over_index(model, probe, idx), cells)
            g["frozen"]["per_seed"][str(s)] = lived_rows(P, idx, eps, P.load_p(f"NF-h24-s{s}+p", idx), cells)
        for head in ("new", "frozen"):
            g[head]["mean_sd"] = {c: {k: msd([g[head]["per_seed"][str(s)][c][k] for s in SEEDS]) for k in ("reset_detected", "fa_per_10k", "fa_midworld_per_10k")}
                                  for c in cells}
        out["groups"][gname] = g
        if progress:
            print(f"  lived {gname} done, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    out["score"] = score_lived(out)
    out["seconds"] = round(time.time() - t0)
    return out


def score_lived(out):
    S = out["S"]
    if S is None:
        return {"P19": {"met": False, "reason": "no S"}}
    r = {}
    for gname, g in out["groups"].items():
        r[gname] = {"new_S": g["new"]["mean_sd"][S]["fa_per_10k"]["mean"], "frozen_pick": g["frozen"]["mean_sd"][PICK]["fa_per_10k"]["mean"]}
        r[gname]["ratio"] = r[gname]["new_S"] / r[gname]["frozen_pick"] if r[gname]["frozen_pick"] else None
    ok = all(v["ratio"] is not None and v["ratio"] <= PRED["P19"]["fa_ratio_max"] for v in r.values())
    return {"P19": {"groups": r, "ratio_max": PRED["P19"]["fa_ratio_max"], "met": ok,
                    "reset_detected_P": {"new_S": out["groups"]["P"]["new"]["mean_sd"][S]["reset_detected"]["mean"],
                                         "frozen_pick": out["groups"]["P"]["frozen"]["mean_sd"][PICK]["reset_detected"]["mean"]}}}


# ---- R-D: the estimate (Phase 1's reader on the 1b evaluation worlds) ----------------------

def _phase1_reader():
    os.environ["MINIFRIEND_ARC"] = str(PHASE1B)
    sys.path.insert(0, str(PHASE1))
    import read_phase1 as RP
    return RP


def load_pred_dir(run_dir, idx, y_dim=7):
    out = np.empty((idx["n"], y_dim), np.float32)
    cache = {}
    for n, s, k, j, a, b in idx["slices"]:
        if (n, s) not in cache:
            cache[(n, s)] = np.load(Path(run_dir) / f"pred-{n}-{s}.npz")["pred"]
        out[a:b] = cache[(n, s)][:, k, j]
    return out * 100.0


def estimate_cells(RP, pred, idx):
    c = RP.cells_for(pred, idx)
    return {v: {cls: {"n": c[v][cls]["pooled"]["n"], "mse5": c[v][cls]["pooled"].get("mse5"), "mse_hap": c[v][cls]["pooled"].get("mse_hap"),
                      "insufficient": bool(c[v][cls]["pooled"].get("insufficient", False))}
                for cls in RP.CLASSES} for v in RP.VERSIONS}


def read_estimate(progress=True):
    RP = _phase1_reader()
    t0 = time.time()
    out = {"groups": {}}
    for gname, sets in (("P", GROUP_P), ("LWG", GROUP_LWG)):
        idx = RP.eval_index(sets)
        g = {"samples": idx["n"], "new": {"per_seed": {}}, "frozen": {"per_seed": {}}}
        for s in SEEDS:
            g["new"]["per_seed"][str(s)] = estimate_cells(RP, load_pred_dir(HERE / "results-raw" / "heads" / f"NF1e-h24-s{s}", idx), idx)
            g["frozen"]["per_seed"][str(s)] = estimate_cells(RP, RP.load_pred(f"NF-h24-s{s}", idx), idx)
        for head in ("new", "frozen"):
            g[head]["mean_sd"] = {v: {cls: {k: msd([g[head]["per_seed"][str(s)][v][cls][k] for s in SEEDS]) for k in ("mse5", "mse_hap")}
                                      for cls in RP.CLASSES} for v in RP.VERSIONS}
        g["ratio_new_over_frozen"] = {v: {cls: (g["new"]["mean_sd"][v][cls]["mse5"]["mean"] / g["frozen"]["mean_sd"][v][cls]["mse5"]["mean"]
                                               if g["new"]["mean_sd"][v][cls]["mse5"] and g["frozen"]["mean_sd"][v][cls]["mse5"] else None)
                                          for cls in RP.CLASSES} for v in RP.VERSIONS}
        out["groups"][gname] = g
        if progress:
            print(f"  estimate {gname} done, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    out["score"] = score_estimate(out)
    out["seconds"] = round(time.time() - t0)
    return out


def score_estimate(out):
    g = out["groups"]
    grave = g["P"]["ratio_new_over_frozen"]["visible"]["GRAVE"]
    common = g["LWG"]["ratio_new_over_frozen"]["visible"]["COMMON"]
    return {"P20": {"P_visible_GRAVE_mse5_ratio": grave, "LWG_visible_COMMON_mse5_ratio": common, "ratio_max": PRED["P20"]["ratio_max"],
                    "P_visible_GRAVE_mse5": {"new": g["P"]["new"]["mean_sd"]["visible"]["GRAVE"]["mse5"], "frozen": g["P"]["frozen"]["mean_sd"]["visible"]["GRAVE"]["mse5"]},
                    "met": grave is not None and common is not None and grave <= PRED["P20"]["ratio_max"] and common <= PRED["P20"]["ratio_max"]}}


# ---- score ------------------------------------------------------------------------------

def read_score():
    files = {n: json.loads((READS / f"{n}.json").read_text()) for n in ("tuning", "confirming", "splice", "lived", "estimate")}
    out = {"S": files["tuning"]["S"], "selection": files["tuning"]["selection"],
           "P16": files["confirming"]["score"]["P16"], "P17": files["confirming"]["score"]["P17"],
           "P18": files["splice"]["score"]["P18"], "P19": files["lived"]["score"]["P19"], "P20": files["estimate"]["score"]["P20"]}
    out["met"] = {p: out[p]["met"] for p in ("P16", "P17", "P18", "P19", "P20")}
    return out


# ---- helpers / md -----------------------------------------------------------------------

def msd(xs):
    a = np.asarray([x for x in xs if x is not None], float)
    if len(a) == 0:
        return None
    return {"mean": round(float(a.mean()), 4), "sd": round(float(a.std(ddof=1)), 4) if len(a) > 1 else None, "n_seeds": int(len(a))}


def _f(m, d=3):
    if m is None:
        return "-"
    if isinstance(m, dict):
        return f"{m['mean']:.{d}f}" + (f" ± {m['sd']:.{d}f}" if m.get("sd") is not None else "")
    return f"{m:.{d}f}"


def md_table(tab, cells, title):
    g = tab["groups"]
    lines = [f"### {title}", "", "| cell | " + " | ".join(f"{p} det" for p in PRIMARY) + " | N-H2 antic | N-H3 antic | N-H4 antic | FA covered N /10k | FA scripted-from-mask N /10k |",
             "|---" * (len(PRIMARY) + 6) + "|"]
    for c in cells:
        det = [_f(g[p]["cells"][c]["detected"]) if p in g else "-" for p in PRIMARY]
        ant = [_f(g[p]["cells"][c].get("anticipated_run_not_at_offset_B")) if p in g else "-" for p in N_STRATA]
        fa = tab["false_alarms"]["N"][c]
        lines.append(f"| {c} | " + " | ".join(det + ant) + f" | {_f(fa['covered_friends']['per_10k_ticks'], 4)} | {_f(fa['scripted_from_first_mask']['per_10k_ticks'], 4)} |")
    return lines


def md(cmd, out):
    lines = [f"# Phase 1e read: {cmd}", ""]
    if cmd == "tuning":
        lines += md_table(out["table"], CELLS, "NF1e-h24+p on the tuning half (seed mean ± SD over the three retrained heads)")
        sel = out["selection"]
        lines += ["", f"Selection bound (the frozen pick's tuning rates): covered {sel['bound']['fa_cov']:.4f}, scripted-from-mask {sel['bound']['fa_scr']:.4f} per 10k. "
                      f"Candidates: {sel['candidates']}. **S = {sel['chosen']}**.",
                  "", "| cell | mean N det | FA covered | FA scripted-from-mask |", "|---|---|---|---|"]
        for c, r in out["selection_rows"].items():
            lines.append(f"| {c} | {_f(r['det_N'])} | {_f(r['fa_cov'], 4)} | {_f(r['fa_scr'], 4)} |")
    elif cmd == "confirming":
        lines += md_table(out["new"], out["cells"], "NF1e-h24+p on the confirming half")
        lines += [""] + md_table(out["frozen"], out["cells"], "the frozen NF-h24+p on the confirming half (same reader)")
        lines += ["", "```", json.dumps(out["score"], indent=1), "```"]
    elif cmd == "splice":
        t = f"{SPLICE_THRESH:.2f}"
        lines += ["| H | new detected | new control fired | new median latency | frozen committed detected | frozen committed control |", "|---|---|---|---|---|---|"]
        cm = out["committed_frozen_0.10"]
        for H in HISTORIES:
            r = out["mean_sd"][str(H)][t]
            c = cm.get(str(H), {})
            lines.append(f"| {H} | {_f(r['detected'])} | {_f(r['control_fired'])} | {_f(r['median_latency'], 1)} | {_f(c.get('detected'))} | {_f(c.get('control_fired'))} |")
        lines += ["", f"at {t}; the second threshold's rows (S) are in the JSON. Clock read on L's clean slices: mean logit at ticks "
                      + ", ".join(f"{k}: {v:.2f}" for k, v in out["clock"]["logit_profile_mean"].items())
                      + f"; slope {out['clock']['slope_per_1000_mean']:.3f} logits per 1,000 ticks.", "", "```", json.dumps(out["score"], indent=1), "```"]
    elif cmd == "lived":
        lines += ["| group | cell | head | reset detected (P) | FA per 10k (all runs) | FA per 10k (mid-world) |", "|---|---|---|---|---|---|"]
        for gname, g in out["groups"].items():
            for c in out["cells"]:
                for head in ("new", "frozen"):
                    r = g[head]["mean_sd"][c]
                    lines.append(f"| {gname} | {c} | {head} | {_f(r['reset_detected'])} | {_f(r['fa_per_10k'])} | {_f(r['fa_midworld_per_10k'])} |")
        lines += ["", "```", json.dumps(out["score"], indent=1), "```"]
    elif cmd == "estimate":
        lines += ["| group | version | class | new mse5 | frozen mse5 | ratio |", "|---|---|---|---|---|---|"]
        for gname, g in out["groups"].items():
            for v in g["ratio_new_over_frozen"]:
                for cls, ratio in g["ratio_new_over_frozen"][v].items():
                    lines.append(f"| {gname} | {v} | {cls} | {_f(g['new']['mean_sd'][v][cls]['mse5'], 2)} | {_f(g['frozen']['mean_sd'][v][cls]['mse5'], 2)} | {_f(ratio)} |")
        lines += ["", "```", json.dumps(out["score"], indent=1), "```"]
    else:
        lines += ["```", json.dumps(out, indent=1), "```"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["tuning", "confirming", "splice", "lived", "estimate", "score"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    fn = {"tuning": read_tuning, "confirming": read_confirming, "splice": read_splice, "lived": read_lived, "estimate": read_estimate}
    out = read_score() if a.cmd == "score" else fn[a.cmd](progress=not a.quiet)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))


if __name__ == "__main__":
    main()
