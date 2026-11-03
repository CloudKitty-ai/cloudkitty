#!/usr/bin/env python3
"""Phase 1e diagnostics — five zero-collection reads (DECLARATION.md §5), one
subcommand each; every figure the seed mean ± SD over the three retrained
heads (NF1e-h24-s1..3+p) beside the frozen NF-h24+p by the SAME reader on
the SAME worlds, at her operating point S (Phase 1e's reads/S.json).

    diag_1e.py content     --out reads/content.json     [--md]   # D1: the covered-friend false runs partitioned (confirming); P21
    diag_1e.py covered     --out reads/covered.json     [--md]   # D2: covered friends' natural crossings (confirming; the 35 validation worlds apart); P22
    diag_1e.py persistence --out reads/persistence.json [--md]   # D3: run lengths and the persistence ladder over k (tuning); P23
    diag_1e.py means       --out reads/means.json       [--md]   # D4: the need-means filter ladder over lambda (tuning); P24
    diag_1e.py reliability --out reads/reliability.json [--md]   # D5: reliability bins per head (confirming); reported
    diag_1e.py score       --out reads/score.json       [--md]   # P21-P24 gathered

The accounting is the ladder's (rise.cells_from_alarms / rise.table), fed
transformed alarm arrays for D3 / D4; D1, D2 and D5 are new accountings of
the same P(grave) at S. Nothing here trains, selects, or writes outside
--out. Every needy-set world passes needy_read.refuse_unless for the half
its read is declared on (§3).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
P1E = EXPTS / "minifriend-phase1e-2026-11-01"
NEEDY = EXPTS / "needy-set-2026-10-28"
READS = HERE / "reads"
sys.path.insert(0, str(P1E))
import read_1e as R1  # noqa: E402  (load_head_e, level_alarms, _needy_modules, msd, price_rows, PICK, REG, SEEDS)

SEEDS = R1.SEEDS
N_STRATA = R1.N_STRATA
PRIMARY = R1.PRIMARY
S = json.loads((P1E / "reads" / "S.json").read_text())["S"]          # her operating point, t0.05-B2 (amendment 1)
REG = R1.REG
HALF = {"content": "confirming", "covered": "confirming", "reliability": "confirming", "persistence": "tuning", "means": "tuning"}
W_WINDOW, W_SENS = 50, (20, 100)                                       # §4: the window after a false run's start (median lead 43-50)
DELTA = 10.0                                                           # §4: "approach" = the worst hidden need within 10 of the 90 edge
RISE_LAG = 20                                                          # §4: rising at start = worst need at t0 minus at t0 - 20 > 0
NEAR_BANDS = ((0, 5), (5, 10), (10, 20), (20, 40), (40, 1e9))
K_GRID = (1, 2, 3, 5, 10, 20, 30, 50)
LAMBDA_GRID = (0, 50, 60, 70, 80, 90)
LEN_BANDS = ((1, 2), (2, 5), (5, 10), (10, 20), (20, 50), (50, 100), (100, 1e9))
BIN_EDGES = (0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0)
PICK_BIN = 3                                                           # [0.05, 0.10)
HORIZONS = (10, 50)
MIN_EPISODES = 20                                                      # §4: a printed covered-crossing rate needs 20 observer-episodes
PRED = {"P21": {"share_min": 0.5}, "P22": {"min_episodes": MIN_EPISODES}, "P23": {"removed_min": 0.5, "det_loss_max": 0.05},
        "P24": {"removed_min": 0.5, "det_loss_max": 0.05}}
# Phase 1e's validation carve (data_1e.roles(): 5 TN + 2 TE per block), held out of the gradient, chose the stopping epoch; guard g7
VALIDATION = {"TN1": [1096653, 1096660, 1096661, 1096662, 1096669], "TN2": [1096699, 1096702, 1096703, 1096708, 1096709],
              "TN3": [1096737, 1096741, 1096742, 1096745, 1096753], "TN4": [1096773, 1096781, 1096789, 1096790, 1096792],
              "TN5": [1096811, 1096816, 1096821, 1096829, 1096833], "TE1": [1096853, 1096856], "TE2": [1096894, 1096897],
              "TE3": [1096931, 1096932], "TE4": [1096974, 1096978], "TE5": [1097011, 1097017]}

_MODS = None


def mods():
    """(rise, needy_read, ladder) — imported once; MINIFRIEND_ARC = Phase 1b under needy_read's default."""
    global _MODS
    if _MODS is None:
        _MODS = R1._needy_modules()
    return _MODS


def heads(which):
    """{seed: (model, probe)} — 'new' = NF1e-h24-s<seed>+p, 'frozen' = NF-h24-s<seed>+p."""
    _rise, R, _L = mods()
    if which == "new":
        return {s: R1.load_head_e(s) for s in SEEDS}
    return {s: R.load_probe(s)[:2] for s in R.PROBE_SEEDS}


# ---- the shared forward: one pass, P(grave) and the five need means ------------------------

def signals(model, probe, w, pairs=None):
    """P (T, R, R) = sigmoid(probe(z)) and M (T, R, R, 5) = out(z)[:5] x 100 over the covered observer
    pairs, the GRU state zero at the world's start and carried across CHUNK ticks (needy_read.probe_world);
    NaN where no pair runs. Guard g5: P equals probe_world's to 0.0, M reproduces the head's pred file."""
    import torch
    _rise, R, _L = mods()
    pairs = R.observer_pairs(w) if pairs is None else pairs
    x = torch.from_numpy(np.stack([R.pair_x(w, k, j)[0] for k, j in pairs], 1))
    Tn = w["ticks"]
    ps, ms, h = [], [], None
    with torch.no_grad():
        for c in range(0, Tn, R.CHUNK):
            z, h = model.gru(torch.relu(model.proj(x[c:min(c + R.CHUNK, Tn)].float())), h)
            ps.append(torch.sigmoid(probe(z).squeeze(-1)))
            ms.append(model.out(z)[..., :5] * 100.0)
    p, m = torch.cat(ps).numpy(), torch.cat(ms).numpy()
    P = np.full((Tn, R.ROSTER, R.ROSTER), np.nan, np.float32)
    M = np.full((Tn, R.ROSTER, R.ROSTER, 5), np.nan, np.float32)
    for i, (k, j) in enumerate(pairs):
        P[:, k, j] = p[:, i]
        M[:, k, j] = m[:, i]
    return P, M


def alarm_S(P, cell=None):
    """(above (T, R, R) bool, B) at S (or `cell`): P >= threshold with the slice's first B ticks forced off."""
    cell = S if cell is None else cell
    return R1.level_alarms(P, [cell])[cell]


# ---- §4 definitions ---------------------------------------------------------------------

def persist(above, k):
    """alarm_k[t] = alarm[t - k + 1 .. t] all true; k = 1 is the identity. Applied AFTER the burn-in."""
    out = above.copy()
    for d in range(1, k):
        out[d:] &= above[:-d]
        out[:d] = False
    return out


def means_gate(above, M, lam):
    """alarm_lambda[t] = alarm[t] and max of the five need means (x 100) >= lambda; NaN means never pass (lambda > 0)."""
    if lam <= 0:
        return above.copy()
    with np.errstate(invalid="ignore"):
        top = np.nanmax(np.where(np.isnan(M), -np.inf, M), axis=-1)
    return above & (top >= lam)


def classify(needs5, hap, codes, t0, W=W_WINDOW, delta=DELTA):
    """One false run's partition by the friend's truth over [t0, t0 + W) (end exclusive, clipped to the world):
    'grave_after' (a grave tick inside), 'approach' (the worst hidden need within delta of 90, or happiness
    under 70 at any tick), else 'no_approach'; with the nearest approach (90 - worst need, min over the window)
    and the happiness distance (hap - 45, min)."""
    _rise, R, _L = mods()
    T = len(hap)
    win = slice(t0, min(T, t0 + W))
    worst = np.asarray(needs5[win], np.float64).max(1)
    dist = float((R.S.NEED_DISTRESS - worst).min())
    hdist = float((np.asarray(hap[win], np.float64) - R.S.HAP_GRAVE).min())
    if (np.asarray(codes[win]) == R.S.GRAVE).any():
        cls = "grave_after"
    elif dist <= delta or (np.asarray(hap[win]) < R.S.HAP_ADJACENT).any():
        cls = "approach"
    else:
        cls = "no_approach"
    return cls, dist, hdist


def rising(needs5, t0, lag=RISE_LAG):
    if t0 < lag:
        return None
    worst = np.asarray(needs5, np.float64).max(1)
    return bool(worst[t0] - worst[t0 - lag] > 0)


def within(g, h):
    """(T,) bool: a grave tick at any t' in [t, t + h], inclusive, clipped to the world's end."""
    T = len(g)
    nxt = np.full(T, 1 << 40, np.int64)                       # no grave ahead: never within any h
    last = 1 << 40
    for t in range(T - 1, -1, -1):
        if g[t]:
            last = t
        nxt[t] = last
    return (nxt - np.arange(T)) <= h


def bin_index(p):
    """Bin of each P(grave): 0 .. len(BIN_EDGES) - 2; the last bin closed at 1."""
    return np.clip(np.digitize(p, BIN_EDGES[1:-1], right=False), 0, len(BIN_EDGES) - 2)


def seeds_in(recs, key):
    """The head seeds present in the records (the full three in a read; one in a guard)."""
    return sorted({s for r in recs for s in r[key]}) or [str(s) for s in SEEDS]


def band_of(x, bands):
    for i, (lo, hi) in enumerate(bands):
        if lo <= x < hi:
            return i
    return len(bands) - 1


def band_names(bands):
    return [f"[{lo:g}, {hi:g})" if hi < 1e8 else f"{lo:g}+" for lo, hi in bands]


# ---- worlds --------------------------------------------------------------------------------

def worlds_for(cmd):
    """[(arm, k, seed, ticks, path)] of the half §3 declares for `cmd`; each passes refuse_unless."""
    rise, _R, _L = mods()
    return rise.worlds(HALF[cmd])


def validation_worlds():
    """[(set, seed, path)] — Phase 1e's 35 validation worlds."""
    return [(n, s, P1E / "results-raw" / n / f"streams-{s}.npz") for n in VALIDATION for s in VALIDATION[n]]


def load(path, arm, k, seed, half=None):
    _rise, R, _L = mods()
    if half is not None:
        R.refuse_unless(arm, k, seed, half)
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None, path
    return w


def _progress(i, n, t0, label):
    if (i + 1) % 30 == 0 or i + 1 == n:
        print(f"  {label}: {i + 1}/{n} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)


# ---- D1: the false runs' content --------------------------------------------------------------

def false_runs_world(w, arm, fe, above, b):
    """[(class, observer, friend, start, length)] — the ladder's false runs of one alarm array: covered friends,
    and the scripted friend's from its first mask (anticipation runs and runs touching a grave tick excluded)."""
    _rise, R, L = mods()
    f = fe["friend"]
    grave_of = {j: (w["codes"][:, j] == R.S.GRAVE) for j in range(R.ROSTER)}
    antic = L.anticipation_windows(w, fe)
    first_onset = fe["windows"][0][0] if fe["windows"] else None
    out = []
    for k in R.observers(w):
        for j in range(R.ROSTER):
            if j == k:
                continue
            for st, en in L.runs(above[:, k, j]):
                if grave_of[j][st:en].any():
                    continue
                if j == f:
                    if any(on <= st < c for on, c in antic):
                        continue
                    if first_onset is not None and st < first_onset:
                        continue
                    out.append(("scripted_from_first_mask", k, j, st, en - st))
                else:
                    out.append(("covered_friends", k, j, st, en - st))
    return out


def content_world(w, arm, k_block, seed, half, probes):
    _rise, R, L = mods()
    fe = L.first_episode(w, arm)
    vis = {}
    rec = {"arm": arm, "block": k_block, "seed": seed, "half": half, "ticks": w["ticks"],
           "observer_ticks": {"covered_friends": 12 * w["ticks"],
                              "scripted_from_first_mask": 4 * (w["ticks"] - (fe["windows"][0][0] if fe["windows"] else 0)) if arm != "T" else 4 * w["ticks"]},
           "runs": {}}
    for s, (m, p) in probes.items():
        P, _M = signals(m, p, w)
        above, b = alarm_S(P)
        rows = []
        for cls, k, j, st, ln in false_runs_world(w, arm, fe, above, b):
            if (k, j) not in vis:
                vis[(k, j)] = R.pair_x(w, k, j)[1]
            c, dist, hdist = classify(w["needs"][:, j, :5], w["hap"][:, j], w["codes"][:, j], st)
            sens = {str(W): classify(w["needs"][:, j, :5], w["hap"][:, j], w["codes"][:, j], st, W=W)[0] for W in W_SENS}
            rows.append({"cls": cls, "k": k, "j": j, "start": int(st), "length": int(ln), "part": c, "nearest": dist, "hap_dist": hdist,
                         "rising": rising(w["needs"][:, j, :5], st), "in_sight": bool(vis[(k, j)][st]), "sens": sens})
        rec["runs"][str(s)] = rows
    return rec


PARTS = ("grave_after", "approach", "no_approach")


def content_table(recs, arm):
    """Per class and partition: runs, share of runs, share of ticks under alarm, per 10k observer-ticks, per
    observer per 1,000 ticks; the histograms; rising / in-sight shares; seed mean ± SD."""
    rs = [r for r in recs if r["arm"] == arm]
    per_obs = {"covered_friends": 3, "scripted_from_first_mask": 1}
    out = {"worlds": len(rs)}
    seeds = seeds_in(rs, "runs")
    for cls in per_obs:
        ticks = sum(r["observer_ticks"][cls] for r in rs)
        per_seed = {}
        for s in seeds:
            runs = [x for r in rs for x in r["runs"][s] if x["cls"] == cls]
            n, tk = len(runs), sum(x["length"] for x in runs)
            row = {"runs": n, "ticks_under_alarm": tk, "per_10k": n / ticks * 1e4 if ticks else None,
                   "mean_run_length": tk / n if n else None, "parts": {}, "sens": {}, "near_hist": {}, "hap_hist": {}}
            for part in PARTS:
                sub = [x for x in runs if x["part"] == part]
                ns, ts = len(sub), sum(x["length"] for x in sub)
                known = [x["rising"] for x in sub if x["rising"] is not None]
                row["parts"][part] = {"runs": ns, "share_runs": ns / n if n else None, "share_ticks": ts / tk if tk else None,
                                      "per_10k": ns / ticks * 1e4 if ticks else None,
                                      "per_observer_per_1000": ns / ticks * 1e4 * per_obs[cls] / 10.0 if ticks else None,
                                      "mean_run_length": ts / ns if ns else None,
                                      "rising_share": sum(known) / len(known) if known else None, "rising_known": len(known),
                                      "in_sight_share": sum(x["in_sight"] for x in sub) / ns if ns else None}
            row["approach_or_grave_share_runs"] = (row["parts"]["grave_after"]["share_runs"] or 0) + (row["parts"]["approach"]["share_runs"] or 0) if n else None
            appr = [x for x in runs if x["part"] == "approach"]
            row["approach_by_need_edge_share_runs"] = sum(x["nearest"] <= DELTA for x in appr) / n if n else None      # approach via the worst need within delta (hap may also be under 70)
            row["approach_by_happiness_only_share_runs"] = sum(x["nearest"] > DELTA for x in appr) / n if n else None  # approach via happiness under 70 alone
            for W in W_SENS:
                row["sens"][str(W)] = {part: sum(1 for x in runs if x["sens"][str(W)] == part) / n if n else None for part in PARTS}
            for name_, key, bands in (("near_hist", "nearest", NEAR_BANDS), ("hap_hist", "hap_dist", NEAR_BANDS)):
                counts = [0] * len(bands)
                for x in runs:
                    counts[band_of(x[key], bands)] += 1
                row[name_] = dict(zip(band_names(bands), counts))
            per_seed[s] = row
        agg = {"observer_ticks": ticks, "per_seed": per_seed,
               "runs": R1.msd([per_seed[s]["runs"] for s in per_seed]), "per_10k": R1.msd([per_seed[s]["per_10k"] for s in per_seed]),
               "mean_run_length": R1.msd([per_seed[s]["mean_run_length"] for s in per_seed]),
               "approach_or_grave_share_runs": R1.msd([per_seed[s]["approach_or_grave_share_runs"] for s in per_seed]),
               "approach_by_need_edge_share_runs": R1.msd([per_seed[s]["approach_by_need_edge_share_runs"] for s in per_seed]),
               "approach_by_happiness_only_share_runs": R1.msd([per_seed[s]["approach_by_happiness_only_share_runs"] for s in per_seed]),
               "parts": {part: {key: R1.msd([per_seed[s]["parts"][part][key] for s in per_seed])
                                for key in ("runs", "share_runs", "share_ticks", "per_10k", "per_observer_per_1000", "mean_run_length", "rising_share", "in_sight_share")}
                         for part in PARTS},
               "sens": {str(W): {part: R1.msd([per_seed[s]["sens"][str(W)][part] for s in per_seed]) for part in PARTS} for W in W_SENS},
               "near_hist_total": {b: sum(per_seed[s]["near_hist"][b] for s in per_seed) for b in band_names(NEAR_BANDS)},
               "hap_hist_total": {b: sum(per_seed[s]["hap_hist"][b] for s in per_seed) for b in band_names(NEAR_BANDS)}}
        out[cls] = agg
    return out


def read_content(progress=True):
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    ws = worlds_for("content")
    out = {"half": HALF["content"], "S": S, "W": W_WINDOW, "W_sens": list(W_SENS), "delta": DELTA, "rise_lag": RISE_LAG, "tables": {}, "records": {}}
    for which in ("new", "frozen"):
        probes = heads(which)
        recs = []
        for i, (arm, k, seed, ticks, path) in enumerate(ws):
            w = load(path, arm, k, seed, HALF["content"])
            assert w["ticks"] == ticks
            recs.append(content_world(w, arm, k, seed, HALF["content"], probes))
            if progress:
                _progress(i, len(ws), t0, f"content {which}")
        out["tables"][which] = {arm: content_table(recs, arm) for arm in ("N", "E", "T")}
        out["records"][which] = recs
    out["score"] = score_content(out)
    out["seconds"] = round(time.time() - t0)
    return out


def score_content(out):
    new = out["tables"]["new"]["N"]["covered_friends"]["approach_or_grave_share_runs"]
    frz = out["tables"]["frozen"]["N"]["covered_friends"]["approach_or_grave_share_runs"]
    sn, sf = (new or {}).get("mean"), (frz or {}).get("mean")
    return {"P21": {"share_new": sn, "share_frozen": sf, "share_min": PRED["P21"]["share_min"],
                    "clause_half": sn is not None and sn >= PRED["P21"]["share_min"], "clause_above_frozen": sn is not None and sf is not None and sn > sf,
                    "met": sn is not None and sf is not None and sn >= PRED["P21"]["share_min"] and sn > sf,
                    "per_10k_new": out["tables"]["new"]["N"]["covered_friends"]["per_10k"], "per_10k_frozen": out["tables"]["frozen"]["N"]["covered_friends"]["per_10k"]}}


# ---- D1 context (post-hoc, reported, not scored): the partition's null over every window start -----------

def window_any(flag, W):
    """(T,) bool: flag true at any tick of [t, t + W) clipped to the world (a forward-looking rolling any)."""
    T = len(flag)
    c = np.concatenate([[0], np.cumsum(flag.astype(np.int64))])
    end = np.minimum(np.arange(T) + W, T)
    return (c[end] - c[:T]) > 0


def null_partition_world(w, fe, W=W_WINDOW, delta=DELTA):
    """Per class (covered friends; the scripted friend from its first mask): over EVERY tick t as a window start, the
    share of windows [t, t + W) that would class grave_after / approach / no_approach, plus the per-tick base rates of
    GRAVE, ADJACENT and the worst need within delta. The null the D1 partition is read against."""
    _rise, R, _L = mods()
    f = fe["friend"]
    first_onset = fe["windows"][0][0] if fe["windows"] else None
    out = {}
    for cls, friends, start in (("covered_friends", [j for j in range(R.ROSTER) if j != f], 0),
                                ("scripted_from_first_mask", [f], first_onset if first_onset is not None else 0)):
        acc = {"windows": 0, "grave_after": 0, "approach": 0, "no_approach": 0, "ticks": 0, "grave": 0, "adjacent": 0, "need_within_delta": 0}
        for j in friends:
            codes = np.asarray(w["codes"][:, j])
            worst = np.asarray(w["needs"][:, j, :5], np.float64).max(1)
            near = (R.S.NEED_DISTRESS - worst) <= delta
            adj = np.asarray(w["hap"][:, j], np.float64) < R.S.HAP_ADJACENT
            grave = codes == R.S.GRAVE
            g_w, a_w = window_any(grave, W)[start:], window_any(near | adj, W)[start:]
            acc["windows"] += len(g_w)
            acc["grave_after"] += int(g_w.sum())
            acc["approach"] += int((~g_w & a_w).sum())
            acc["no_approach"] += int((~g_w & ~a_w).sum())
            acc["ticks"] += len(codes) - start
            acc["grave"] += int(grave[start:].sum())
            acc["adjacent"] += int((adj & ~grave)[start:].sum())
            acc["need_within_delta"] += int((near & ~grave)[start:].sum())
        out[cls] = acc
    return out


def read_context(progress=True):
    _rise, _R, L = mods()
    t0 = time.time()
    ws = worlds_for("content")
    acc = {}
    for i, (arm, k, seed, ticks, path) in enumerate(ws):
        w = load(path, arm, k, seed, HALF["content"])
        a = null_partition_world(w, L.first_episode(w, arm))
        for cls, d in a.items():
            tgt = acc.setdefault(arm, {}).setdefault(cls, {key: 0 for key in d})
            for key, v in d.items():
                tgt[key] += v
        if progress:
            _progress(i, len(ws), t0, "context")
    out = {"half": HALF["content"], "W": W_WINDOW, "delta": DELTA, "note": "post-hoc control, not in the declaration: the partition applied to every window start",
           "tables": {}}
    for arm, by_cls in acc.items():
        out["tables"][arm] = {}
        for cls, d in by_cls.items():
            n, tk = d["windows"], d["ticks"]
            out["tables"][arm][cls] = {"windows": n, "null_share": {p: d[p] / n if n else None for p in PARTS},
                                       "tick_base_rate": {"grave": d["grave"] / tk if tk else None, "adjacent": d["adjacent"] / tk if tk else None,
                                                          "need_within_delta": d["need_within_delta"] / tk if tk else None}}
    out["seconds"] = round(time.time() - t0)
    return out


# ---- D2: covered friends' natural crossings --------------------------------------------------------

def covered_episodes(w):
    """{friend: [(crossing, end)]} on every COVERED seat's truth stream; the scripted seat yields none."""
    _rise, R, _L = mods()
    return {j: R.grave_episodes(w["codes"][:, j]) for j in R.observers(w)}


def covered_world(w, label, seed, probes, cells):
    """Per covered episode and observer (the other covered seats), per head seed and cell: latency, lead, in sight."""
    _rise, R, L = mods()
    obs = R.observers(w)
    eps = covered_episodes(w)
    vis = {(k, j): R.pair_x(w, k, j)[1] for j in eps for k in obs if k != j}
    sig = {s: signals(m, p, w)[0] for s, (m, p) in probes.items()}
    rows = []
    for j, es in eps.items():
        for c, e in es:
            over = [n for n, v in zip(R.NEED_NAMES[:5], w["needs"][c, j, :5]) if v >= R.S.NEED_DISTRESS]
            row = {"friend": j, "crossing": int(c), "end": int(e), "length": int(e - c), "stratum": R.stratum_of(c),
                   "edge": "need" if over else "happiness", "observers": {}}
            for k in obs:
                if k == j:
                    continue
                o = {"in_sight": bool(vis[(k, j)][c]), "cells": {}}
                for s, P in sig.items():
                    o["cells"][str(s)] = {}
                    for cell in cells:
                        above, _b = alarm_S(P, cell)
                        a = above[:, k, j]
                        hit = np.flatnonzero(a[c:e])
                        lat = int(hit[0]) if len(hit) else None
                        lead = None
                        if lat is not None:
                            st = c + lat
                            while st > 0 and a[st - 1]:
                                st -= 1
                            if st < c:
                                lead = int(c - st)
                        o["cells"][str(s)][cell] = {"latency": lat, "lead": lead}
                row["observers"][str(k)] = o
            rows.append(row)
    return {"label": label, "seed": seed, "ticks": w["ticks"], "n_covered_episodes": sum(len(v) for v in eps.values()), "episodes": rows}


def covered_table(recs, cell, strata=None):
    """One group's figures over observer-episodes: n, in sight, detected, median / p90 latency, anticipated, median lead,
    edge counts; per head seed then mean ± SD; rates only at MIN_EPISODES or more."""
    eps = [(r, e) for r in recs for e in r["episodes"] if strata is None or e["stratum"] in strata]
    n = sum(len(e["observers"]) for _r, e in eps)
    out = {"friend_episodes": len(eps), "observer_episodes": n, "in_sight_at_crossing": sum(o["in_sight"] for _r, e in eps for o in e["observers"].values()),
           "edge": {ed: sum(1 for _r, e in eps if e["edge"] == ed) for ed in ("need", "happiness")},
           "H": None if not eps else {"min": min(e["crossing"] for _r, e in eps), "median": float(np.median([e["crossing"] for _r, e in eps])), "max": max(e["crossing"] for _r, e in eps)},
           "length_median": None if not eps else float(np.median([e["length"] for _r, e in eps])), "per_seed": {}}
    seeds = sorted({s for _r, e in eps for o in e["observers"].values() for s in o["cells"]}) or [str(s) for s in SEEDS]
    for s in seeds:
        lats = [o["cells"][s][cell]["latency"] for _r, e in eps for o in e["observers"].values()]
        leads = [o["cells"][s][cell]["lead"] for _r, e in eps for o in e["observers"].values()]
        det = [l for l in lats if l is not None]
        sight = [(o["in_sight"], o["cells"][s][cell]["latency"]) for _r, e in eps for o in e["observers"].values()]
        row = {"detected": len(det) / n if n >= MIN_EPISODES else None, "detected_count": len(det),
               "median_latency": float(np.median(det)) if det and n >= MIN_EPISODES else None,
               "p90_latency": float(np.percentile(det, 90)) if det and n >= MIN_EPISODES else None,
               "anticipated": sum(l is not None for l in leads) / n if n >= MIN_EPISODES else None,
               "median_lead": float(np.median([l for l in leads if l is not None])) if any(l is not None for l in leads) and n >= MIN_EPISODES else None,
               "detected_in_sight": (sum(l is not None for v, l in sight if v) / sum(1 for v, _l in sight if v)) if sum(1 for v, _l in sight if v) >= MIN_EPISODES else None,
               "detected_under_fog": (sum(l is not None for v, l in sight if not v) / sum(1 for v, _l in sight if not v)) if sum(1 for v, _l in sight if not v) >= MIN_EPISODES else None}
        out["per_seed"][s] = row
    for key in ("detected", "median_latency", "p90_latency", "anticipated", "median_lead", "detected_in_sight", "detected_under_fog"):
        out[key] = R1.msd([out["per_seed"][s][key] for s in out["per_seed"]])
    return out


def p22_bar():
    """The midpoint between the splice at H = 100 at 0.05 (Phase 1e reads/splice.json, seed mean) and the retrained
    head's mean N-H2 / H3 / H4 scripted detection at S (reads/confirming.json), both committed."""
    sp = json.loads((P1E / "reads" / "splice.json").read_text())
    cf = json.loads((P1E / "reads" / "confirming.json").read_text())
    th = f"{R1.parse_cell(S)[0]:.2f}"
    splice = sp["mean_sd"]["100"][th]["detected"]["mean"]
    scripted = float(np.mean([cf["new"]["groups"][g]["cells"][S]["detected"]["mean"] for g in N_STRATA]))
    return {"splice_H100_at_S_threshold": splice, "scripted_N_mean_at_S": scripted, "bar": (splice + scripted) / 2.0}


def read_covered(progress=True):
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    cells = [S, REG]
    out = {"half": HALF["covered"], "S": S, "cells": cells, "min_episodes": MIN_EPISODES, "bar": p22_bar(), "confirming": {}, "validation": {}, "records": {}}
    ws = worlds_for("covered")
    for which in ("new", "frozen"):
        probes = heads(which)
        recs = []
        for i, (arm, k, seed, ticks, path) in enumerate(ws):
            w = load(path, arm, k, seed, HALF["covered"])
            r = covered_world(w, arm, seed, probes, cells)
            r["arm"] = arm
            recs.append(r)
            if progress:
                _progress(i, len(ws), t0, f"covered {which}")
        tab = {"worlds_with_a_covered_episode": sum(1 for r in recs if r["n_covered_episodes"]), "groups": {}}
        for arm in ("T", "E", "N"):
            rs = [r for r in recs if r["arm"] == arm]
            for st in ("H0", "H1", "H2", "H3", "H4"):
                tab["groups"][f"{arm}-{st}"] = {cell: covered_table(rs, cell, (st,)) for cell in cells}
            tab["groups"][f"{arm}-H>=100"] = {cell: covered_table(rs, cell, N_STRATA_H) for cell in cells}
        tab["groups"]["all-H>=100"] = {cell: covered_table(recs, cell, N_STRATA_H) for cell in cells}
        tab["groups"]["all-H<100"] = {cell: covered_table(recs, cell, ("H0", "H1")) for cell in cells}
        out["confirming"][which] = tab
        out["records"][f"confirming_{which}"] = recs
        vrecs = []
        for n, seed, path in validation_worlds():
            w = load(path, n, None, seed, None)
            r = covered_world(w, n, seed, probes, [S])
            r["arm"] = n[:2]
            vrecs.append(r)
        vt = {"caveat": "Phase 1e's validation worlds chose the stopping epoch; a second reading, never pooled with the confirming half",
              "worlds": len(vrecs), "worlds_with_a_covered_episode": sum(1 for r in vrecs if r["n_covered_episodes"]), "groups": {}}
        for arm in ("TN", "TE"):
            rs = [r for r in vrecs if r["arm"] == arm]
            for st in ("H0", "H1", "H2", "H3", "H4"):
                vt["groups"][f"{arm}-{st}"] = {S: covered_table(rs, S, (st,))}
            vt["groups"][f"{arm}-H>=100"] = {S: covered_table(rs, S, N_STRATA_H)}
        vt["groups"]["all-H>=100"] = {S: covered_table(vrecs, S, N_STRATA_H)}
        out["validation"][which] = vt
        out["records"][f"validation_{which}"] = vrecs
    out["score"] = score_covered(out)
    out["seconds"] = round(time.time() - t0)
    return out


N_STRATA_H = ("H2", "H3", "H4")


def score_covered(out):
    g = out["confirming"]["new"]["groups"]["all-H>=100"][S]
    n, det = g["observer_episodes"], (g["detected"] or {}).get("mean") if g["detected"] else None
    bar = out["bar"]["bar"]
    und = n < PRED["P22"]["min_episodes"]
    return {"P22": {"observer_episodes": n, "friend_episodes": g["friend_episodes"], "detected": det, "bar": bar, "bar_inputs": out["bar"],
                    "frozen_detected": (out["confirming"]["frozen"]["groups"]["all-H>=100"][S]["detected"] or {}).get("mean"),
                    "validation_observer_episodes": out["validation"]["new"]["groups"]["all-H>=100"][S]["observer_episodes"],
                    "undecidable": und, "met": (not und) and det is not None and det > bar}}


# ---- D3 / D4: filter ladders through the ladder's accounting ---------------------------------------

def ladder_cells(kind):
    if kind == "persistence":
        return [f"{S}-k{k}" for k in K_GRID]
    return [f"{S}-m{lam}" for lam in LAMBDA_GRID]


def transformed_alarms(P, M, kind):
    """{cell: (above, B)} — S's alarm transformed per §4, the burn-in first."""
    above, b = alarm_S(P)
    if kind == "persistence":
        return {f"{S}-k{k}": (persist(above, k), b) for k in K_GRID}
    return {f"{S}-m{lam}": (means_gate(above, M, lam), b) for lam in LAMBDA_GRID}


def ladder_world(w, arm, k_block, seed, half, probes, kind):
    rise, R, L = mods()
    fe = L.first_episode(w, arm)
    sig = {s: signals(m, p, w) for s, (m, p) in probes.items()}
    by_seed = {s: transformed_alarms(P, M, kind) for s, (P, M) in sig.items()}
    cells = ladder_cells(kind)
    c = rise.cells_from_alarms(w, arm, fe, by_seed, cells)
    rec = {"arm": arm, "block": k_block, "seed": seed, "half": half, "ticks": w["ticks"], "friend": fe["friend"], "status": fe["status"],
           "crossing": fe["crossing"], "end": None if fe["crossing"] is None else fe["end"],
           "length": None if fe["crossing"] is None else fe["end"] - fe["crossing"],
           "onset": fe["onset"], "stratum": fe["stratum"], "m": fe["m"], "masked": fe["masked"], "edge": fe["edge"],
           "sight_at_crossing": c["sight_at_crossing"], "observer_ticks": c["observer_ticks"], "cells": c["cells"]}
    if kind == "persistence":
        rec["lengths"] = {str(s): run_lengths(w, arm, fe, by_seed[s][f"{S}-k1"][0]) for s in sig}
    else:
        rec["naming"] = {str(s): naming_at_crossing(w, fe, M) for s, (_P, M) in sig.items()}
    return rec


def run_lengths(w, arm, fe, above):
    """At k = 1: the lengths of the false runs per class and of the anticipation runs on the scripted friend's first
    episode (lead = crossing - start, and the whole run)."""
    _rise, R, L = mods()
    out = {"covered_friends": [], "scripted_from_first_mask": [], "anticipation_lead": [], "anticipation_run": []}
    for cls, _k, _j, _st, ln in false_runs_world(w, arm, fe, above, None):
        out[cls].append(int(ln))
    if fe["crossing"] is not None and fe["onset"] is not None:
        c = fe["crossing"]
        for k in R.observers(w):
            for st, en in L.runs(above[:, k, fe["friend"]]):
                if fe["onset"] <= st < c:
                    out["anticipation_lead"].append(int(c - st))
                    out["anticipation_run"].append(int(en - st))
    return out


def naming_at_crossing(w, fe, M):
    """Per observer at the scripted friend's crossing: the named need (argmax of the five means) equals the truth's
    worst need, when the edge crossed is a need."""
    _rise, R, _L = mods()
    if fe["crossing"] is None or fe["edge"] != "need":
        return None
    c, f = fe["crossing"], fe["friend"]
    truth = int(np.argmax(w["needs"][c, f, :5]))
    return {str(k): bool(int(np.nanargmax(M[c, k, f])) == truth) for k in R.observers(w)}


def length_hist(recs, arm):
    rs = [r for r in recs if r["arm"] == arm]
    out = {}
    for key in ("covered_friends", "scripted_from_first_mask", "anticipation_lead", "anticipation_run"):
        per_seed = {}
        for s in seeds_in(rs, "lengths"):
            xs = [x for r in rs for x in r["lengths"][s][key]]
            counts = [0] * len(LEN_BANDS)
            for x in xs:
                counts[band_of(x, LEN_BANDS)] += 1
            per_seed[s] = {"n": len(xs), "median": float(np.median(xs)) if xs else None, "mean": float(np.mean(xs)) if xs else None,
                           "p90": float(np.percentile(xs, 90)) if xs else None, "hist": dict(zip(band_names(LEN_BANDS), counts))}
        out[key] = {"per_seed": per_seed, "n": sum(per_seed[s]["n"] for s in per_seed),
                    "median": R1.msd([per_seed[s]["median"] for s in per_seed]), "mean": R1.msd([per_seed[s]["mean"] for s in per_seed]),
                    "p90": R1.msd([per_seed[s]["p90"] for s in per_seed]),
                    "hist_total": {b: sum(per_seed[s]["hist"][b] for s in per_seed) for b in band_names(LEN_BANDS)}}
    return out


def naming_table(recs, arm):
    rs = [r for r in recs if r["arm"] == arm and r["stratum"] is not None]
    out = {}
    for st in sorted({r["stratum"] for r in rs}):
        per_seed = {}
        for s in seeds_in(rs, "naming"):
            vals = [v for r in rs if r["stratum"] == st and r["naming"][s] for v in r["naming"][s].values()]
            per_seed[s] = {"n": len(vals), "agree": sum(vals) / len(vals) if vals else None}
        out[f"{arm}-{st}"] = {"per_seed": per_seed, "n": next(iter(per_seed.values()))["n"], "agree": R1.msd([per_seed[s]["agree"] for s in per_seed])}
    return out


def trade_rows(tab, cells, base):
    """Per cell against the base cell (arm N): covered-friend false runs removed (fraction and per 10k), ticks under false
    alarm removed per 10k, N-stratum mean detection and its loss, median lead and its loss, scripted-from-mask removed."""
    def fa(cell, cls, key="per_10k_ticks"):
        v = tab["false_alarms"]["N"][cell][cls][key]
        return None if v is None else v["mean"]
    def detN(cell):
        d = [tab["groups"][g]["cells"][cell]["detected"]["mean"] for g in N_STRATA if g in tab["groups"]]
        return float(np.mean(d)) if d else None
    def leadN(cell):
        d = [tab["groups"][g]["cells"][cell]["median_lead_run_not_at_offset_B"] for g in N_STRATA if g in tab["groups"]]
        d = [x["mean"] for x in d if x]
        return float(np.mean(d)) if d else None
    def latN(cell):
        d = [tab["groups"][g]["cells"][cell]["median_latency"] for g in N_STRATA if g in tab["groups"]]
        d = [x["mean"] for x in d if x]
        return float(np.mean(d)) if d else None
    def ticks(cell, cls):
        r, ln = fa(cell, cls), fa(cell, cls, "mean_run_length")
        return None if r is None or ln is None else r * ln
    b_fa, b_det, b_lead, b_lat = fa(base, "covered_friends"), detN(base), leadN(base), latN(base)
    rows = {}
    for c in cells:
        r = {"fa_cov_per_10k": fa(c, "covered_friends"), "fa_scr_per_10k": fa(c, "scripted_from_first_mask"),
             "ticks_under_fa_cov_per_10k": ticks(c, "covered_friends"), "det_N_mean": detN(c), "median_lead_N_mean": leadN(c), "median_latency_N_mean": latN(c)}
        r["fa_cov_removed_frac"] = None if b_fa in (None, 0) or r["fa_cov_per_10k"] is None else 1 - r["fa_cov_per_10k"] / b_fa
        r["fa_cov_removed_per_10k"] = None if b_fa is None or r["fa_cov_per_10k"] is None else b_fa - r["fa_cov_per_10k"]
        r["ticks_under_fa_cov_removed_per_10k"] = None if ticks(base, "covered_friends") is None or r["ticks_under_fa_cov_per_10k"] is None else ticks(base, "covered_friends") - r["ticks_under_fa_cov_per_10k"]
        r["det_N_loss"] = None if b_det is None or r["det_N_mean"] is None else b_det - r["det_N_mean"]
        r["median_lead_N_loss"] = None if b_lead is None or r["median_lead_N_mean"] is None else b_lead - r["median_lead_N_mean"]
        r["median_latency_N_gain"] = None if b_lat is None or r["median_latency_N_mean"] is None else r["median_latency_N_mean"] - b_lat
        rows[c] = r
    return rows


def read_ladder(kind, progress=True):
    rise, _R, _L = mods()
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    cells = ladder_cells(kind)
    base = cells[0]
    ws = worlds_for(kind)
    out = {"half": HALF[kind], "S": S, "kind": kind, "cells": cells, "grid": list(K_GRID if kind == "persistence" else LAMBDA_GRID),
           "tables": {}, "price": {}, "trade": {}, "records": {}}
    for which in ("new", "frozen"):
        probes = heads(which)
        recs = []
        for i, (arm, k, seed, ticks, path) in enumerate(ws):
            w = load(path, arm, k, seed, HALF[kind])
            assert w["ticks"] == ticks
            recs.append(ladder_world(w, arm, k, seed, HALF[kind], probes, kind))
            if progress:
                _progress(i, len(ws), t0, f"{kind} {which}")
        tab = rise.table(recs, cells)
        out["tables"][which] = tab
        out["price"][which] = R1.price_rows(tab, cells)
        out["trade"][which] = trade_rows(tab, cells, base)
        if kind == "persistence":
            out.setdefault("lengths", {})[which] = {arm: length_hist(recs, arm) for arm in ("N", "E", "T")}
        else:
            out.setdefault("naming", {})[which] = {arm: naming_table(recs, arm) for arm in ("N", "E")}
        out["records"][which] = recs
    out["score"] = score_ladder(out, kind)
    out["seconds"] = round(time.time() - t0)
    return out


def score_ladder(out, kind):
    p = "P23" if kind == "persistence" else "P24"
    tr = out["trade"]["new"]
    rows = {c: {"removed": r["fa_cov_removed_frac"], "det_loss": r["det_N_loss"],
                "qualifies": r["fa_cov_removed_frac"] is not None and r["det_N_loss"] is not None
                and r["fa_cov_removed_frac"] >= PRED[p]["removed_min"] and r["det_N_loss"] < PRED[p]["det_loss_max"]}
            for c, r in tr.items() if c != out["cells"][0]}
    return {p: {"removed_min": PRED[p]["removed_min"], "det_loss_max": PRED[p]["det_loss_max"], "cells": rows,
                "qualifying": [c for c, r in rows.items() if r["qualifies"]], "met": any(r["qualifies"] for r in rows.values())}}


# ---- D5: reliability ---------------------------------------------------------------------------

def reliability_world(w, fe, P, b):
    """Per class (covered friends; the scripted friend): per bin the count, sum of p, grave-now count and grave-within-h
    counts over every (observer, friend, tick >= B) of the covered observer slices."""
    _rise, R, _L = mods()
    f = fe["friend"]
    nb = len(BIN_EDGES) - 1
    acc = {cls: {"n": np.zeros(nb, np.int64), "p": np.zeros(nb), "now": np.zeros(nb, np.int64), **{f"w{h}": np.zeros(nb, np.int64) for h in HORIZONS}}
           for cls in ("covered_friends", "scripted")}
    grave = {j: (w["codes"][:, j] == R.S.GRAVE) for j in range(R.ROSTER)}
    win = {j: {h: within(grave[j], h) for h in HORIZONS} for j in range(R.ROSTER)}
    for k in R.observers(w):
        for j in range(R.ROSTER):
            if j == k:
                continue
            p = P[b:, k, j]
            idx = bin_index(p)
            a = acc["scripted" if j == f else "covered_friends"]
            a["n"] += np.bincount(idx, minlength=nb)
            a["p"] += np.bincount(idx, weights=p, minlength=nb)
            a["now"] += np.bincount(idx, weights=grave[j][b:], minlength=nb).astype(np.int64)
            for h in HORIZONS:
                a[f"w{h}"] += np.bincount(idx, weights=win[j][h][b:], minlength=nb).astype(np.int64)
    return {cls: {key: v.tolist() for key, v in d.items()} for cls, d in acc.items()}


def reliability_table(accs):
    """Sum the per-world accumulators of one head seed; rates per bin; ECE on grave-now."""
    names = [f"[{BIN_EDGES[i]:g}, {BIN_EDGES[i + 1]:g}{']' if i == len(BIN_EDGES) - 2 else ')'}" for i in range(len(BIN_EDGES) - 1)]
    out = {}
    for cls in ("covered_friends", "scripted"):
        tot = {key: np.sum([np.asarray(a[cls][key]) for a in accs], axis=0) for key in accs[0][cls]}
        n = tot["n"].astype(np.float64)
        with np.errstate(invalid="ignore", divide="ignore"):
            rows = {names[i]: {"n": int(tot["n"][i]), "mean_p": float(tot["p"][i] / n[i]) if n[i] else None,
                               "realised_now": float(tot["now"][i] / n[i]) if n[i] else None,
                               **{f"realised_within_{h}": float(tot[f"w{h}"][i] / n[i]) if n[i] else None for h in HORIZONS}}
                    for i in range(len(names))}
        N = n.sum()
        ece = float(sum(n[i] * abs(tot["p"][i] / n[i] - tot["now"][i] / n[i]) for i in range(len(names)) if n[i]) / N) if N else None
        out[cls] = {"bins": rows, "ece_now": ece, "base_rate_now": float(tot["now"].sum() / N) if N else None, "n": int(N), "pick_bin": names[PICK_BIN]}
    return out


def read_reliability(progress=True):
    _rise, _R, L = mods()
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    ws = worlds_for("reliability")
    out = {"half": HALF["reliability"], "S": S, "bin_edges": list(BIN_EDGES), "horizons": list(HORIZONS), "burn_in": R1.parse_cell(S)[1], "tables": {}}
    for which in ("new", "frozen"):
        probes = heads(which)
        accs = {arm: {str(s): [] for s in SEEDS} for arm in ("N", "E", "T", "all")}
        for i, (arm, k, seed, ticks, path) in enumerate(ws):
            w = load(path, arm, k, seed, HALF["reliability"])
            fe = L.first_episode(w, arm)
            for s, (m, p) in probes.items():
                P, _M = signals(m, p, w)
                _above, b = alarm_S(P)
                a = reliability_world(w, fe, P, b)
                accs[arm][str(s)].append(a)
                accs["all"][str(s)].append(a)
            if progress:
                _progress(i, len(ws), t0, f"reliability {which}")
        tabs = {}
        for arm, by_seed in accs.items():
            per_seed = {s: reliability_table(lst) for s, lst in by_seed.items()}
            agg = {"per_seed": per_seed}
            for cls in ("covered_friends", "scripted"):
                names = list(per_seed["1"][cls]["bins"])
                agg[cls] = {"n": sum(per_seed[s][cls]["n"] for s in per_seed) // len(per_seed), "ece_now": R1.msd([per_seed[s][cls]["ece_now"] for s in per_seed]),
                            "base_rate_now": R1.msd([per_seed[s][cls]["base_rate_now"] for s in per_seed]), "pick_bin": names[PICK_BIN],
                            "bins": {nm: {"n": R1.msd([per_seed[s][cls]["bins"][nm]["n"] for s in per_seed]),
                                          **{key: R1.msd([per_seed[s][cls]["bins"][nm][key] for s in per_seed])
                                             for key in ("mean_p", "realised_now", *[f"realised_within_{h}" for h in HORIZONS])}} for nm in names}}
            tabs[arm] = agg
        out["tables"][which] = tabs
    out["pick_bin_summary"] = {which: {arm: {cls: out["tables"][which][arm][cls]["bins"][out["tables"][which][arm][cls]["pick_bin"]]
                                             for cls in ("covered_friends", "scripted")} for arm in ("N", "E", "T", "all")} for which in ("new", "frozen")}
    out["seconds"] = round(time.time() - t0)
    return out


# ---- score / md ---------------------------------------------------------------------------------

def read_score():
    f = {n: json.loads((READS / f"{n}.json").read_text()) for n in ("content", "covered", "persistence", "means")}
    out = {"S": S, "P21": f["content"]["score"]["P21"], "P22": f["covered"]["score"]["P22"], "P23": f["persistence"]["score"]["P23"], "P24": f["means"]["score"]["P24"]}
    out["met"] = {p: out[p]["met"] for p in ("P21", "P22", "P23", "P24")}
    out["undecidable"] = {"P22": out["P22"]["undecidable"]}
    return out


def _f(m, d=3):
    return R1._f(m, d)


def md(cmd, out):
    lines = [f"# Phase 1e diagnostics read: {cmd}", ""]
    if cmd == "content":
        for which in ("new", "frozen"):
            for arm in ("N", "E", "T"):
                for cls in ("covered_friends", "scripted_from_first_mask"):
                    t = out["tables"][which][arm][cls]
                    lines += [f"### {which} head, arm {arm}, {cls} (W = {out['W']}, delta = {out['delta']}; {out['tables'][which][arm]['worlds']} worlds)", "",
                              f"runs per 10k observer-ticks {_f(t['per_10k'], 4)}, mean run length {_f(t['mean_run_length'], 1)}, approach-or-grave share of runs {_f(t['approach_or_grave_share_runs'])}", "",
                              "| partition | runs | share of runs | share of ticks | per 10k | per observer per 1,000 | mean run length | rising at start | in sight at start |", "|---|---|---|---|---|---|---|---|---|"]
                    for part in PARTS:
                        p = t["parts"][part]
                        lines.append(f"| {part} | {_f(p['runs'], 1)} | {_f(p['share_runs'])} | {_f(p['share_ticks'])} | {_f(p['per_10k'], 4)} | {_f(p['per_observer_per_1000'], 4)} | {_f(p['mean_run_length'], 1)} | {_f(p['rising_share'])} | {_f(p['in_sight_share'])} |")
                    lines += ["", f"approach split (share of all runs): by the worst need within delta {_f(t['approach_by_need_edge_share_runs'])}, by happiness under 70 alone {_f(t['approach_by_happiness_only_share_runs'])}",
                              "", "sensitivity (share of runs): " + "; ".join(f"W = {W}: " + ", ".join(f"{part} {_f(t['sens'][W][part])}" for part in PARTS) for W in t["sens"]),
                              "", "nearest approach of the worst need to 90 (runs, all seeds): " + ", ".join(f"{b}: {n}" for b, n in t["near_hist_total"].items()),
                              "", "happiness distance to 45 (runs, all seeds): " + ", ".join(f"{b}: {n}" for b, n in t["hap_hist_total"].items()), ""]
        lines += ["```", json.dumps(out["score"], indent=1), "```"]
    elif cmd == "context":
        lines += [out["note"], "", "| arm | class | window starts | null grave_after | null approach | null no_approach | tick rate GRAVE | tick rate ADJACENT | tick rate need within delta |", "|---" * 9 + "|"]
        for arm, by_cls in out["tables"].items():
            for cls, r in by_cls.items():
                ns, tb = r["null_share"], r["tick_base_rate"]
                lines.append(f"| {arm} | {cls} | {r['windows']} | {_f(ns['grave_after'])} | {_f(ns['approach'])} | {_f(ns['no_approach'])} | {_f(tb['grave'], 4)} | {_f(tb['adjacent'], 4)} | {_f(tb['need_within_delta'], 4)} |")
    elif cmd == "covered":
        lines += [f"P22 bar: {json.dumps(out['bar'])}", ""]
        for block in ("confirming", "validation"):
            for which in ("new", "frozen"):
                t = out[block][which]
                lines += [f"### {block}, {which} head" + (f" — {t['caveat']}" if "caveat" in t else ""), "",
                          f"worlds with a covered episode: {t['worlds_with_a_covered_episode']}", "",
                          "| group | cell | friend episodes | observer-episodes | in sight | H min/median/max | detected | median latency | p90 latency | anticipated | median lead | in sight det | fog det | edge need/hap |", "|---" * 14 + "|"]
                for g, cells in t["groups"].items():
                    for cell, r in cells.items():
                        if r["friend_episodes"] == 0:
                            continue
                        H = r["H"]
                        lines.append(f"| {g} | {cell} | {r['friend_episodes']} | {r['observer_episodes']} | {r['in_sight_at_crossing']} | {H['min']}/{H['median']:.0f}/{H['max']} | {_f(r['detected'])} | {_f(r['median_latency'], 1)} | {_f(r['p90_latency'], 1)} | {_f(r['anticipated'])} | {_f(r['median_lead'], 1)} | {_f(r['detected_in_sight'])} | {_f(r['detected_under_fog'])} | {r['edge']['need']}/{r['edge']['happiness']} |")
                lines.append("")
        lines += ["```", json.dumps(out["score"], indent=1), "```"]
    elif cmd in ("persistence", "means"):
        for which in ("new", "frozen"):
            tab, tr, pr = out["tables"][which], out["trade"][which], out["price"][which]
            lines += [f"### {which} head, arm N (tuning half), the ladder over {'k' if cmd == 'persistence' else 'lambda'}", "",
                      "| cell | " + " | ".join(f"{p} det" for p in PRIMARY) + " | N mean det | det loss | N median latency | N median lead | lead loss | FA covered /10k | removed frac | ticks under FA /10k | FA scripted-from-mask /10k | runs per observer per 1,000 (covered) |",
                      "|---" * (len(PRIMARY) + 12) + "|"]
            for c in out["cells"]:
                det = [_f(tab["groups"][p]["cells"][c]["detected"]) if p in tab["groups"] else "-" for p in PRIMARY]
                r = tr[c]
                lines.append(f"| {c} | " + " | ".join(det) + f" | {_f(r['det_N_mean'])} | {_f(r['det_N_loss'])} | {_f(r['median_latency_N_mean'], 1)} | {_f(r['median_lead_N_mean'], 1)} | {_f(r['median_lead_N_loss'], 1)} | {_f(r['fa_cov_per_10k'], 4)} | {_f(r['fa_cov_removed_frac'])} | {_f(r['ticks_under_fa_cov_per_10k'], 1)} | {_f(r['fa_scr_per_10k'], 4)} | {_f(pr[c]['covered_friends']['runs_per_observer_per_1000_ticks'], 4)} |")
            lines.append("")
            if cmd == "persistence":
                for arm in ("N", "E"):
                    lh = out["lengths"][which][arm]
                    lines += [f"run lengths at k = 1, {which} head, arm {arm}:", "", "| kind | n (all seeds) | median | mean | p90 | " + " | ".join(band_names(LEN_BANDS)) + " |", "|---" * (5 + len(LEN_BANDS)) + "|"]
                    for key, r in lh.items():
                        lines.append(f"| {key} | {r['n']} | {_f(r['median'], 1)} | {_f(r['mean'], 1)} | {_f(r['p90'], 1)} | " + " | ".join(str(v) for v in r["hist_total"].values()) + " |")
                    lines.append("")
            else:
                for arm in ("N", "E"):
                    lines += [f"naming at the crossing (need edge), {which} head, arm {arm}: " + "; ".join(f"{g}: {_f(r['agree'])} (n {r['n']})" for g, r in out["naming"][which][arm].items()), ""]
        lines += ["```", json.dumps(out["score"], indent=1), "```"]
    elif cmd == "reliability":
        for which in ("new", "frozen"):
            for arm in ("N", "E", "T", "all"):
                for cls in ("covered_friends", "scripted"):
                    t = out["tables"][which][arm][cls]
                    lines += [f"### {which} head, arm {arm}, {cls}: n {t['n']} per seed, base rate now {_f(t['base_rate_now'], 5)}, ECE now {_f(t['ece_now'], 5)}, pick bin {t['pick_bin']}", "",
                              "| bin | n | mean p | realised now | " + " | ".join(f"within {h}" for h in HORIZONS) + " |", "|---" * (4 + len(HORIZONS)) + "|"]
                    for nm, r in t["bins"].items():
                        lines.append(f"| {nm} | {_f(r['n'], 0)} | {_f(r['mean_p'], 4)} | {_f(r['realised_now'], 4)} | " + " | ".join(_f(r[f"realised_within_{h}"], 4) for h in HORIZONS) + " |")
                    lines.append("")
    else:
        lines += ["```", json.dumps(out, indent=1), "```"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["content", "context", "covered", "persistence", "means", "reliability", "score"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    fn = {"content": read_content, "context": read_context, "covered": read_covered, "persistence": lambda progress: read_ladder("persistence", progress),
          "means": lambda progress: read_ladder("means", progress), "reliability": read_reliability}
    out = read_score() if a.cmd == "score" else fn[a.cmd](progress=not a.quiet)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))


if __name__ == "__main__":
    main()
