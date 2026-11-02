#!/usr/bin/env python3
"""The probe-rise read (DECLARATION.md; owner "Ok, let's try it", 2026-11-01,
to recommendation 1 of the mini-model assessment). Zero collection: the
needy set's raws and the frozen NF-h24+p, three probe seeds, as step 7
read them.

The question: is the climb the needy set saw in the probe's logit (R3: a
rise of 1.6 to 2.5 logits over the 100 ticks before a late crossing, from
a level near -8) usable as an alarm, where the level rule at her pick
(P(grave) >= 0.05, B = 2) catches 0.42-0.60 of the late crossings?

The detector family (one, declared): on each observer slice's logit
series l_t = logit(clip(P_t, 1e-6, 1 - 1e-6)), the step statistic

    s_t = mean(l[t-w+1 .. t]) - mean(l[t-2w+1 .. t-w]),   t >= 2w - 1

(undefined before 2w - 1 and wherever either window holds a missing
value: no alarm there). Three families of alarm per (w, k):
  rise      s_t >= k
  rise+f    s_t >= k  and  P_t >= 0.01            (a floor under the level)
  rise|L    s_t >= k  or   the level pick's alarm  (the consumer rule)
Grid w in {10, 25, 50, 100} x k in {0.5, 1.0, 1.5, 2.0, 3.0}: 60 cells,
beside the level cells L:t0.05-B2 (her pick) and L:t0.10-B0 (the
registered point), computed by the same accounting.

Accounting: the needy set's section 4, as ladder.py applies it (detection,
latency, anticipation = a run STARTING inside [mask onset, crossing), lead,
false alarms per class per 10,000 observer-ticks, anticipation runs
excluded, runs starting at the slice's first alarmable tick counted
apart: B for a level cell, 2w - 1 for a rise cell, B for rise|L). The
first episode per world, primary strata T-H0, E-H1, N-H2/H3/H4, every
other (arm, stratum) printed apart. Seed mean +- SD over probe seeds 1-3.

Halves: the grid on the TUNING half (every world passes refuse_unless);
then ONE rise cell S chosen by the declared rule (among pure `rise` cells
whose arm N covered-friend and scripted-from-first-mask false-alarm rates
on the tuning half are each at or under the level pick's there, the one
with the highest mean detection over N-H2, N-H3, N-H4; ties to the
smaller w, then the smaller k); then S, S|L and L:t0.05-B2 on the
CONFIRMING half, where the predictions P12-P15 are scored. No stop, no
pass bar; the pick after this read is hers.

    rise.py plan                      # worlds per half and arm; the cells
    rise.py read --out F [--md]       # the grid, the selection, the confirming read; about 3 min
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NEEDY = HERE.parent / "needy-set-2026-10-28"
sys.path.insert(0, str(NEEDY))
import needy_read as R  # noqa: E402
import set_run as SR  # noqa: E402
import ladder as L  # noqa: E402

W_GRID = (10, 25, 50, 100)
K_GRID = (0.5, 1.0, 1.5, 2.0, 3.0)
FLOOR = 0.01
EPS = 1e-6
LEVEL = {"L:t0.05-B2": (0.05, 2), "L:t0.10-B0": (0.10, 0)}
PICK = "L:t0.05-B2"
FAMILIES = ("rise", "rise+f", "rise|L")
PRIMARY = ("T-H0", "E-H1", "N-H2", "N-H3", "N-H4")
N_STRATA = ("N-H2", "N-H3", "N-H4")
STEP7 = NEEDY / "reads" / "step7.json"
# Registered predictions (DECLARATION.md section 6), scored on the confirming half, S|L against L:t0.05-B2
PRED = {
    "P12": {"strata": N_STRATA, "mean_gain": 0.10},         # above the pick in each N stratum; mean gain >= 0.10
    "P13": {"E-H1_tol": 0.05, "T-H0": 1.0},                  # E-H1 within 0.05 of the pick; T-H0 stays 1.000
    "P14": {"fa_covered_N_max": 1.5},                        # S|L's arm N covered-friend false alarms <= 1.5 per 10,000
    "P15": {"strata": N_STRATA, "antic_gain_max": 0.10},    # anticipation past the first frame: gain < 0.10 in every N stratum
}
# R5's confirming figures at the pick (needy set RESULTS step 7), re-derived here and asserted to 3 decimals
R5_PICK = {"T-H0": 1.000, "E-H1": 0.489, "N-H2": 0.596, "N-H3": 0.444, "N-H4": 0.421}


# ---- cells ------------------------------------------------------------------

def cell_name(w, k, fam):
    base = f"w{w}-k{k:.1f}"
    return {"rise": base, "rise+f": base + "+f", "rise|L": base + "|L"}[fam]


def rise_cells(fam=None):
    fams = FAMILIES if fam is None else (fam,)
    return [cell_name(w, k, f) for f in fams for w in W_GRID for k in K_GRID]


def all_cells():
    return list(LEVEL) + rise_cells()


def parse_cell(name):
    """-> (w, k, fam) for a rise cell."""
    fam = "rise|L" if name.endswith("|L") else "rise+f" if name.endswith("+f") else "rise"
    base = name.split("|")[0].split("+")[0]
    w, k = base.split("-")
    return int(w[1:]), float(k[1:]), fam


# ---- worlds -----------------------------------------------------------------

def worlds(half):
    """[(arm, k, seed, ticks, path)] of one half in the set's burn order;
    each passes refuse_unless before it is loaded."""
    out = []
    for arm, k, _cfg, seed, ticks, path in SR.worlds():
        if R.half_of(arm, k, seed) == half:
            R.refuse_unless(arm, k, seed, half)
            out.append((arm, k, seed, ticks, path))
    return out


def plan():
    out = {"cells": {"level": list(LEVEL), "rise": len(rise_cells()), "w": W_GRID, "k": K_GRID, "floor": FLOOR},
           "halves": {}}
    for half in ("tuning", "confirming"):
        ws = worlds(half)
        out["halves"][half] = {arm: sum(1 for w in ws if w[0] == arm) for arm in ("T", "E", "N")}
        out["halves"][half]["worlds"] = len(ws)
    out["probe_seeds"] = R.PROBE_SEEDS
    return out


# ---- the detector -----------------------------------------------------------

def logit(P):
    with np.errstate(invalid="ignore", divide="ignore"):
        p = np.clip(P, EPS, 1 - EPS)
        return np.log(p / (1 - p))


def step_stat(l, w):
    """s_t = mean(l[t-w+1..t]) - mean(l[t-2w+1..t-w]) along axis 0; NaN
    before t = 2w - 1 and wherever either window holds a NaN."""
    T = l.shape[0]
    s = np.full(l.shape, np.nan, dtype=np.float64)
    if T < 2 * w:
        return s
    nan = np.isnan(l)
    ln = np.where(nan, 0.0, l).astype(np.float64)
    z = np.zeros((1,) + l.shape[1:])
    cs = np.concatenate([z, np.cumsum(ln, 0)])
    cn = np.concatenate([z, np.cumsum(nan, 0)])
    t = np.arange(2 * w - 1, T)
    recent = (cs[t + 1] - cs[t - w + 1]) / w
    prior = (cs[t - w + 1] - cs[t - 2 * w + 1]) / w
    val = recent - prior
    val[(cn[t + 1] - cn[t - 2 * w + 1]) > 0] = np.nan
    s[2 * w - 1:] = val
    return s


def alarms(P):
    """{cell: (alarm (T, R, R) bool, first alarmable tick)} for one probe
    seed's P(grave) (T, R, R); NaN = no pair runs there, never an alarm."""
    P0 = np.nan_to_num(P, nan=-1.0)
    out = {}
    for name, (th, b) in LEVEL.items():
        a = P0 >= th
        a[:b] = False
        out[name] = (a, b)
    lvl, b_pick = out[PICK]
    l = logit(P)
    with np.errstate(invalid="ignore"):
        for w in W_GRID:
            s = step_stat(l, w)
            for k in K_GRID:
                r = s >= k                                   # False at NaN
                out[cell_name(w, k, "rise")] = (r, 2 * w - 1)
                out[cell_name(w, k, "rise+f")] = (r & (P0 >= FLOOR), 2 * w - 1)
                out[cell_name(w, k, "rise|L")] = (r | lvl, b_pick)
    return out


# ---- accounting (section 4, as ladder.world_cells applies it) -------------------

def cells_from_alarms(w, arm, fe, alarms_by_seed, keep):
    """Per probe seed and cell: the first episode's per-observer latency,
    anticipation lead (and the lead from the first run not at the first
    alarmable tick), and the false-alarm runs per class."""
    T = w["ticks"]
    f = fe["friend"]
    obs = R.observers(w)
    assert len(obs) == 4 and f not in obs
    grave_of = {j: (w["codes"][:, j] == R.S.GRAVE) for j in range(R.ROSTER)}
    antic = L.anticipation_windows(w, fe)
    first_onset = fe["windows"][0][0] if fe["windows"] else None
    vis = {k: R.pair_x(w, k, f)[1] for k in obs}
    out = {"sight_at_crossing": None, "cells": {}}
    if fe["crossing"] is not None:
        out["sight_at_crossing"] = {str(k): bool(vis[k][fe["crossing"]]) for k in obs}
    ticks = {"scripted_before_first_mask": 4 * (first_onset if first_onset is not None else 0),
             "scripted_from_first_mask": 4 * (T - first_onset) if first_onset is not None else 4 * T,
             "covered_friends": 12 * T}
    if arm == "T":
        ticks = {"scripted_before_first_mask": 0, "scripted_from_first_mask": 4 * T, "covered_friends": 12 * T}
    out["observer_ticks"] = ticks
    for s, by_cell in alarms_by_seed.items():
        for name in keep:
            above, b = by_cell[name]
            cell = {"latency": {}, "lead": {}, "lead_not_at_offset_B": {}, "fa": {c: 0 for c in L.FA_CLASSES},
                    "fa_at_offset_B": {c: 0 for c in L.FA_CLASSES}, "fa_run_ticks": {c: 0 for c in L.FA_CLASSES},
                    "first_alarmable": b}
            for k in obs:
                for j in range(R.ROSTER):
                    if j == k:
                        continue
                    a = above[:, k, j]
                    if j == f:
                        rs = L.runs(a)
                        if fe["crossing"] is not None:
                            c, e = fe["crossing"], fe["end"]
                            hit = np.flatnonzero(a[c:e])
                            cell["latency"][str(k)] = int(hit[0]) if len(hit) else None
                            if fe["onset"] is not None:
                                starts = [st for st, _en in rs if fe["onset"] <= st < c]
                                cell["lead"][str(k)] = int(c - starts[0]) if starts else None
                                later = [st for st in starts if st != b]
                                cell["lead_not_at_offset_B"][str(k)] = int(c - later[0]) if later else None
                        for st, en in rs:
                            if grave_of[j][st:en].any() or any(on <= st < c for on, c in antic):
                                continue
                            cls = "scripted_before_first_mask" if first_onset is not None and st < first_onset else "scripted_from_first_mask"
                            cell["fa"][cls] += 1
                            cell["fa_run_ticks"][cls] += en - st
                            cell["fa_at_offset_B"][cls] += st == b
                    else:
                        for st, en in L.runs(a):
                            if grave_of[j][st:en].any():
                                continue
                            cell["fa"]["covered_friends"] += 1
                            cell["fa_run_ticks"]["covered_friends"] += en - st
                            cell["fa_at_offset_B"]["covered_friends"] += st == b
            out["cells"].setdefault(str(s), {})[name] = cell
    return out


def world_record(arm, k, seed, ticks, path, half, probes, keep):
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None and w["ticks"] == ticks and w["scripted"] == [k - 1], (arm, k, seed)
    fe = L.first_episode(w, arm)
    by_seed = {s: alarms(R.probe_world(m, p, w)) for s, (m, p) in probes.items()}
    cells = cells_from_alarms(w, arm, fe, by_seed, keep)
    return {"arm": arm, "block": k, "seed": seed, "half": half, "ticks": ticks, "friend": fe["friend"], "status": fe["status"],
            "crossing": fe["crossing"], "end": None if fe["crossing"] is None else fe["end"],
            "length": None if fe["crossing"] is None else fe["end"] - fe["crossing"],
            "onset": fe["onset"], "stratum": fe["stratum"], "m": fe["m"], "masked": fe["masked"], "edge": fe["edge"],
            "windows": [list(x) for x in fe["windows"]], "episodes": [list(x) for x in fe["episodes"]],
            "sight_at_crossing": cells["sight_at_crossing"], "observer_ticks": cells["observer_ticks"], "cells": cells["cells"]}


# ---- tables -------------------------------------------------------------------

def table(recs, cells):
    """Per (arm, stratum) group and per cell: ladder.stratum_cell; per arm and
    cell: ladder.false_alarm_cell."""
    groups = {}
    for r in recs:
        if r["stratum"] is not None:
            groups.setdefault(f'{r["arm"]}-{r["stratum"]}', []).append(r)
    status = {}
    for r in recs:
        status.setdefault(r["arm"], {}).setdefault(r["status"], 0)
        status[r["arm"]][r["status"]] += 1
    out = {"worlds": {arm: sum(1 for r in recs if r["arm"] == arm) for arm in ("T", "E", "N")},
           "first_episode_status": status, "groups": {}, "false_alarms": {}}
    for name, rs in sorted(groups.items()):
        arm = name[0]
        out["groups"][name] = {"arm": arm, "stratum": name[2:], "primary": name in PRIMARY, "friend_episodes": len(rs),
                               "observer_episodes": 4 * len(rs),
                               "in_sight_at_crossing": sum(sum(r["sight_at_crossing"].values()) for r in rs),
                               "cells": {c: L.stratum_cell(rs, c, with_sight=arm != "T") for c in cells}}
    for arm in ("T", "E", "N"):
        rs = [r for r in recs if r["arm"] == arm]
        out["false_alarms"][arm] = {c: L.false_alarm_cell(rs, c) for c in cells}
    return out


def _m(x):
    return None if x is None else x["mean"]


def selection_rows(tab):
    """{cell: {w, k, det_N (mean over N-H2/H3/H4 seed-mean detection),
    fa_cov, fa_scr}} for the pure rise cells, and the pick's bound."""
    def fa(cell, cls):
        return _m(tab["false_alarms"]["N"][cell][cls]["per_10k_ticks"])
    rows = {}
    for c in rise_cells("rise"):
        w, k, _f = parse_cell(c)
        dets = [tab["groups"][g]["cells"][c]["detected"]["mean"] for g in N_STRATA if g in tab["groups"]]
        rows[c] = {"w": w, "k": k, "det_N": float(np.mean(dets)) if dets else None,
                   "fa_cov": fa(c, "covered_friends"), "fa_scr": fa(c, "scripted_from_first_mask")}
    bound = {"fa_cov": fa(PICK, "covered_friends"), "fa_scr": fa(PICK, "scripted_from_first_mask")}
    return rows, bound


def select_from(rows, bound):
    """The declared rule: candidates = pure rise cells with fa_cov <= bound
    and fa_scr <= bound; chosen = the highest det_N, ties to the smaller w
    then the smaller k. None when no cell qualifies."""
    cands = [c for c, r in rows.items()
             if r["det_N"] is not None and r["fa_cov"] is not None and r["fa_scr"] is not None
             and r["fa_cov"] <= bound["fa_cov"] and r["fa_scr"] <= bound["fa_scr"]]
    if not cands:
        return {"bound": bound, "candidates": [], "chosen": None}
    best = sorted(cands, key=lambda c: (-rows[c]["det_N"], rows[c]["w"], rows[c]["k"]))[0]
    return {"bound": bound, "candidates": sorted(cands), "chosen": best}


# ---- predictions ------------------------------------------------------------------

def score(conf, S):
    """P12-P15 on the confirming table, S|L against the level pick."""
    SL = cell_name(*parse_cell(S)[:2], "rise|L")
    g = conf["groups"]
    def det(cell, name):
        return g[name]["cells"][cell]["detected"]["mean"] if name in g else None
    def ant(cell, name):
        return _m(g[name]["cells"][cell].get("anticipated_run_not_at_offset_B")) if name in g else None
    pick_det = {n: det(PICK, n) for n in PRIMARY}
    for n, v in R5_PICK.items():
        assert pick_det[n] is not None and round(pick_det[n], 3) == v, ("the pick on the confirming half must reproduce R5", n, pick_det[n], v)
    out = {"S": S, "S|L": SL, "pick": PICK}
    gains = {n: det(SL, n) - pick_det[n] for n in N_STRATA}
    out["P12"] = {"detected_S|L": {n: det(SL, n) for n in N_STRATA}, "detected_pick": {n: pick_det[n] for n in N_STRATA},
                  "gain": gains, "mean_gain": float(np.mean(list(gains.values()))),
                  "clause_1_each_above": all(v > 0 for v in gains.values()),
                  "clause_2_mean_gain": float(np.mean(list(gains.values()))) >= PRED["P12"]["mean_gain"]}
    out["P12"]["met"] = out["P12"]["clause_1_each_above"] and out["P12"]["clause_2_mean_gain"]
    e1 = det(SL, "E-H1") - pick_det["E-H1"]
    out["P13"] = {"E-H1_S|L": det(SL, "E-H1"), "E-H1_pick": pick_det["E-H1"], "E-H1_gain": e1,
                  "T-H0_S|L": det(SL, "T-H0"),
                  "met": abs(e1) <= PRED["P13"]["E-H1_tol"] and det(SL, "T-H0") == PRED["P13"]["T-H0"]}
    fa = _m(conf["false_alarms"]["N"][SL]["covered_friends"]["per_10k_ticks"])
    fa_pick = _m(conf["false_alarms"]["N"][PICK]["covered_friends"]["per_10k_ticks"])
    out["P14"] = {"fa_covered_N_S|L": fa, "fa_covered_N_pick": fa_pick, "met": fa <= PRED["P14"]["fa_covered_N_max"]}
    ag = {n: ant(SL, n) - ant(PICK, n) for n in N_STRATA}
    out["P15"] = {"anticipated_S|L": {n: ant(SL, n) for n in N_STRATA}, "anticipated_pick": {n: ant(PICK, n) for n in N_STRATA},
                  "gain": ag, "met": all(v < PRED["P15"]["antic_gain_max"] for v in ag.values())}
    return out


# ---- the read ----------------------------------------------------------------------

def _records(half, probes, keep, progress):
    ws = worlds(half)
    recs, t0 = [], time.time()
    for i, (arm, k, seed, ticks, path) in enumerate(ws):
        recs.append(world_record(arm, k, seed, ticks, path, half, probes, keep))
        if progress and (i + 1) % 30 == 0:
            print(f"  {half}: {i + 1}/{len(ws)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    return recs


def read(progress=True):
    import torch
    torch.set_num_threads(1)
    probes = {s: R.load_probe(s)[:2] for s in R.PROBE_SEEDS}
    t0 = time.time()
    cells = all_cells()
    tun = _records("tuning", probes, cells, progress)
    grid = table(tun, cells)
    rows, bound = selection_rows(grid)
    sel = select_from(rows, bound)
    sel["rows"] = rows
    out = {"plan": plan(), "pred": PRED, "r5_pick": R5_PICK, "covered_cat_ticks": 0,
           "grid": grid, "selection": sel, "confirming": None, "predictions": None}
    if sel["chosen"] is not None:
        S = sel["chosen"]
        keep = [S, cell_name(*parse_cell(S)[:2], "rise|L"), PICK]
        con = _records("confirming", probes, keep, progress)
        out["confirming"] = table(con, keep)
        out["confirming"]["cells_read"] = keep
        out["predictions"] = score(out["confirming"], S)
        out["records_confirming"] = con
    out["seconds"] = round(time.time() - t0)
    out["records_tuning"] = tun
    return out


# ---- markdown -----------------------------------------------------------------------

def _f(m, d=3):
    if m is None:
        return "-"
    if isinstance(m, dict):
        return "-" if m.get("mean") is None else f'{m["mean"]:.{d}f} ± {m["sd"]:.{d}f}' if m.get("sd") is not None else f'{m["mean"]:.{d}f}'
    return f"{m:.{d}f}"


def _row(tab, c):
    g = tab["groups"]
    cols = []
    for n in PRIMARY:
        cols.append(_f(g[n]["cells"][c]["detected"]) if n in g else "-")
    for n in N_STRATA:
        cols.append(_f(g[n]["cells"][c].get("anticipated_run_not_at_offset_B")) if n in g else "-")
    for n in N_STRATA:
        cols.append(_f(g[n]["cells"][c].get("median_latency"), 1) if n in g else "-")
    fa = tab["false_alarms"]["N"][c]
    cols += [_f(fa["covered_friends"]["per_10k_ticks"], 2), _f(fa["scripted_from_first_mask"]["per_10k_ticks"], 2)]
    return cols


HEAD = ("| cell | T-H0 det | E-H1 det | N-H2 det | N-H3 det | N-H4 det | N-H2 antic | N-H3 antic | N-H4 antic "
        "| N-H2 med lat | N-H3 med lat | N-H4 med lat | FA covered /10k (N) | FA scripted from mask /10k (N) |")
SEP = "|---" * 14 + "|"


def md(out):
    o = []
    p = out["plan"]
    o.append(f"## The probe-rise read (tuning half: {p['halves']['tuning']}; confirming half: {p['halves']['confirming']}; "
             f"probe seeds {list(p['probe_seeds'])}; seed mean ± SD; detected = share of observer-episodes; "
             f"antic = share with an alarm run starting in [onset, crossing) not at the first alarmable tick; "
             f"false alarms per 10,000 observer-ticks in arm N, anticipation runs excluded)")
    grid = out["grid"]
    o.append("")
    o.append("Friend episodes per group (tuning): " + ", ".join(f"{n} {grid['groups'][n]['friend_episodes']}" for n in grid["groups"]))
    o.append("First-episode status per arm (tuning): " + json.dumps(grid["first_episode_status"]))
    for fam, title in (("level", "### Level cells (reference, same accounting)"), ("rise", "### rise: s_t ≥ k"),
                       ("rise+f", "### rise+f: s_t ≥ k and P ≥ 0.01"), ("rise|L", "### rise|L: s_t ≥ k or the level pick (0.05 / B = 2)")):
        o += ["", title, "", HEAD, SEP]
        cells = list(LEVEL) if fam == "level" else rise_cells(fam)
        for c in cells:
            o.append("| " + c + " | " + " | ".join(_row(grid, c)) + " |")
    sel = out["selection"]
    o += ["", "### Selection (declared rule: pure rise cells with arm N covered-friend and scripted-from-first-mask false alarms at or under the pick's on the tuning half; highest mean detection over N-H2/H3/H4; ties to the smaller w, then k)", ""]
    o.append(f"Bound (the pick on tuning): covered {sel['bound']['fa_cov']:.4f}, scripted from first mask {sel['bound']['fa_scr']:.4f} per 10,000.")
    o.append(f"Candidates: {sel['candidates'] or 'none'}. Chosen S: **{sel['chosen']}**.")
    if sel["chosen"]:
        r = sel["rows"][sel["chosen"]]
        o.append(f"S on tuning: mean N detection {r['det_N']:.3f}, FA covered {r['fa_cov']:.4f}, FA scripted from mask {r['fa_scr']:.4f}.")
    con = out["confirming"]
    if con:
        o += ["", f"### Confirming half: S, S|L and the pick ({con['worlds']}; friend episodes " +
              ", ".join(f"{n} {con['groups'][n]['friend_episodes']}" for n in con["groups"]) + ")", "", HEAD, SEP]
        for c in con["cells_read"]:
            o.append("| " + c + " | " + " | ".join(_row(con, c)) + " |")
        pr = out["predictions"]
        o += ["", "### Predictions scored (section 6; S|L against the pick on the confirming half)", ""]
        o.append(f"- P12: S|L detected {pr['P12']['detected_S|L']} vs pick {pr['P12']['detected_pick']}; gains {pr['P12']['gain']}; "
                 f"mean gain {pr['P12']['mean_gain']:.3f} (bar {PRED['P12']['mean_gain']}); each above {pr['P12']['clause_1_each_above']}; **{'MET' if pr['P12']['met'] else 'NOT MET'}**")
        o.append(f"- P13: E-H1 S|L {pr['P13']['E-H1_S|L']:.3f} vs pick {pr['P13']['E-H1_pick']:.3f} (gain {pr['P13']['E-H1_gain']:+.3f}, tol ±{PRED['P13']['E-H1_tol']}); "
                 f"T-H0 S|L {pr['P13']['T-H0_S|L']:.3f}; **{'MET' if pr['P13']['met'] else 'NOT MET'}**")
        o.append(f"- P14: arm N covered-friend false alarms S|L {pr['P14']['fa_covered_N_S|L']:.3f} per 10,000 (pick {pr['P14']['fa_covered_N_pick']:.3f}; bar ≤ {PRED['P14']['fa_covered_N_max']}); **{'MET' if pr['P14']['met'] else 'NOT MET'}**")
        o.append(f"- P15: anticipation past the first frame S|L {pr['P15']['anticipated_S|L']} vs pick {pr['P15']['anticipated_pick']}; gains {pr['P15']['gain']} (each < {PRED['P15']['antic_gain_max']}); **{'MET' if pr['P15']['met'] else 'NOT MET'}**")
    else:
        o += ["", "No rise cell qualified under the declared rule; no confirming read; P12-P15 unscorable (reported)."]
    o.append("")
    o.append(f"Covered cat-ticks: {out['covered_cat_ticks']}. Run time {out['seconds']} s.")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("plan", "read"))
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(), indent=1))
        return
    out = read()
    if a.out:
        Path(a.out).write_text(json.dumps(out, separators=(",", ":")))
    if a.md:
        print(md(out))
    else:
        print(json.dumps(out["predictions"], indent=1))


if __name__ == "__main__":
    main()
