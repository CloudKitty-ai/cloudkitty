#!/usr/bin/env python3
"""Act-head calibration — the reads (DECLARATION.md §5): B10 and B30, seeds 1–3, y0 and y10; zero collection.

    calib_act.py fit         --out reads/temperature.json [--md]   # C3a: Phase 1e VALIDATION worlds, covered friends, every 10th tick — a temperature per (head, horizon, regime) and a global one
    calib_act.py reliability --out reads/reliability.json [--md]   # C1 / C2 / C3b: the needy TUNING half's covered friends — top-prob reliability by regime at T = 1 / global / per-regime, accuracy by entropy, AUROC
    calib_act.py score       --out reads/score.json [--md]         # P29–P32 and the tempering rule from the two files above

Every head is read by the act arc's own loader and forward (train_act.load_act / probs_from_x); every tuning world passes
needy_read.refuse_unless for the tuning half (read_act.load_needy). Nothing here trains, collects or writes a weight.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ACT = HERE.parent / "minifriend-act-2026-11-03"
sys.path.insert(0, str(ACT))
import data_act as D  # noqa: E402
import train_act as TA  # noqa: E402
import read_act as R  # noqa: E402
import read_1e as R1  # noqa: E402  (on the path via train_act)

READS = HERE / "reads"
HEADS = ("B10", "B30")
SEEDS = (1, 2, 3)
HORIZONS = ("y0", "y10")
REGIMES = ("all", "seen", "heard", "silent")
CONF_EDGES = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)         # top-prob bins; 11 classes put the floor at 1/11
ENT_EDGES = tuple(round(0.1 * i, 1) for i in range(11))                 # normalised-entropy bins
FINE = 400                                                              # histogram resolution of the AUROC
T_GRID = np.round(np.arange(0.50, 3.0001, 0.01), 2)                     # the temperature grid; argmin of the validation NLL
FIT_STRIDE = 10                                                         # every 10th tick of each validation pair enters the fit (after the forward)
FLOOR_CELL = 10_000                                                     # a registered cell under this count is UNDECIDABLE (Professor's sharpening 3)
FLOOR_BIN = 1_000                                                       # a bin under this count is printed thin
REGISTERED = tuple((h, "y0", r) for h in HEADS for r in ("seen", "heard"))
PRED = {"P29": {"conf_gap_min": 0.10}, "P30": {"auroc_min": 0.70}, "P31": {"auroc_gap_max": 0.02}, "P32": {"temp_gap_min": 0.10}}
TEMPERINGS = ("T1", "global", "regime")


# ---- the quantities --------------------------------------------------------------------------

def entropy_norm(p):
    """(n,) Shannon entropy of each row of p (n, 11) over log(11): 0 for a one-hot, 1 for the uniform."""
    q = np.clip(np.asarray(p, np.float64), 1e-12, 1.0)
    return -(q * np.log(q)).sum(-1) / np.log(D.N_ACTS)


def bin_index(v, edges):
    """Bin of each value: 0 .. len(edges) - 2; the last bin closed at edges[-1]."""
    return np.clip(np.digitize(v, edges[1:-1], right=False), 0, len(edges) - 2)


def temper(p, T):
    """softmax(log p / T) along the last axis; T a scalar or one per row. T = 1 returns p (to the clip)."""
    T = np.asarray(T, np.float64)
    if np.all(T == 1.0):
        return np.asarray(p, np.float64)
    z = np.log(np.clip(np.asarray(p, np.float64), 1e-12, 1.0)) / (T[:, None] if T.ndim else T)
    z -= z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


def ece_from_bins(n, sconf, ncorr):
    """Expected calibration error on the top label from per-bin counts, confidence sums and correct counts."""
    N = n.sum()
    if N == 0:
        return None
    m = n > 0
    return float((n[m] * np.abs(sconf[m] / n[m] - ncorr[m] / n[m])).sum() / N)


def auroc_from_hist(pos, neg):
    """P(score of a correct tick > score of an incorrect tick), ties half, from per-score-bin counts (pos = correct)."""
    P, Nn = pos.sum(), neg.sum()
    if P == 0 or Nn == 0:
        return None
    below = np.concatenate([[0.0], np.cumsum(neg)[:-1]])
    return float((pos * (below + 0.5 * neg)).sum() / (P * Nn))


def nll_grid(p, y):
    """(len(T_GRID),) summed negative log-likelihood of y under temper(p, T) for every T on the grid."""
    logp = np.log(np.clip(np.asarray(p, np.float64), 1e-12, 1.0))
    ly = logp[np.arange(len(y)), y]
    out = np.empty(len(T_GRID))
    for i, T in enumerate(T_GRID):
        z = logp / T
        m = z.max(-1)
        lse = m + np.log(np.exp(z - m[:, None]).sum(-1))
        out[i] = float((lse - ly / T).sum())
    return out


def fit_temperature(grid):
    return float(T_GRID[int(np.argmin(grid))])


# ---- accumulators ---------------------------------------------------------------------------

class Cal:
    """One cell's accumulator: counts, log-loss, top-prob reliability bins at three temperings, entropy bins, the
    fine histograms behind the AUROCs."""
    def __init__(self):
        nb = len(CONF_EDGES) - 1
        self.n, self.correct, self.nll, self.sum_ent, self.sum_conf = 0, 0, 0.0, 0.0, 0.0
        self.conf = {t: np.zeros((3, nb)) for t in TEMPERINGS}      # n, sum conf, n correct
        self.ent = np.zeros((2, len(ENT_EDGES) - 1))                 # n, n correct (T = 1)
        self.fine_ent = np.zeros((2, FINE))                          # correct / incorrect by score 1 - entropy
        self.fine_conf = np.zeros((2, FINE))                         # correct / incorrect by top-prob

    def add(self, p, y, T_global, T_rows):
        """p (n, 11) at T = 1; y (n,); T_global a scalar; T_rows (n,) each row's regime temperature."""
        if len(y) == 0:
            return
        p = np.asarray(p, np.float64)
        pred = p.argmax(1)
        ok = (pred == y).astype(np.float64)
        self.n += len(y)
        self.correct += int(ok.sum())
        self.nll += float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)).sum())
        for t in TEMPERINGS:
            q = p if t == "T1" else temper(p, T_global if t == "global" else T_rows)
            c = q.max(1)
            b = bin_index(c, CONF_EDGES)
            np.add.at(self.conf[t][0], b, 1.0)
            np.add.at(self.conf[t][1], b, c)
            np.add.at(self.conf[t][2], b, ok)
            if t == "T1":
                self.sum_conf += float(c.sum())
                s2 = np.clip((c * FINE).astype(int), 0, FINE - 1)
                np.add.at(self.fine_conf[0], s2, ok)
                np.add.at(self.fine_conf[1], s2, 1.0 - ok)
        h = entropy_norm(p)
        self.sum_ent += float(h.sum())
        eb = bin_index(h, ENT_EDGES)
        np.add.at(self.ent[0], eb, 1.0)
        np.add.at(self.ent[1], eb, ok)
        s = np.clip(((1.0 - h) * FINE).astype(int), 0, FINE - 1)
        np.add.at(self.fine_ent[0], s, ok)
        np.add.at(self.fine_ent[1], s, 1.0 - ok)

    def row(self):
        if self.n == 0:
            return {"n": 0}
        bins = {}
        for t in TEMPERINGS:
            n, sc, nc = self.conf[t]
            bins[t] = [{"bin": f"[{CONF_EDGES[i]:g}, {CONF_EDGES[i + 1]:g}{']' if i == len(CONF_EDGES) - 2 else ')'}", "n": int(n[i]),
                        "conf": (float(sc[i] / n[i]) if n[i] else None), "acc": (float(nc[i] / n[i]) if n[i] else None), "thin": bool(n[i] < FLOOR_BIN)}
                       for i in range(len(n))]
        ent_bins = [{"bin": f"[{ENT_EDGES[i]:g}, {ENT_EDGES[i + 1]:g}{']' if i == len(ENT_EDGES) - 2 else ')'}", "n": int(self.ent[0][i]),
                     "acc": (float(self.ent[1][i] / self.ent[0][i]) if self.ent[0][i] else None), "thin": bool(self.ent[0][i] < FLOOR_BIN)}
                    for i in range(len(ENT_EDGES) - 1)]
        return {"n": int(self.n), "top1": self.correct / self.n, "logloss": self.nll / self.n, "mean_conf": self.sum_conf / self.n,
                "mean_entropy": self.sum_ent / self.n, "ece": {t: ece_from_bins(*self.conf[t]) for t in TEMPERINGS},
                "auroc_entropy": auroc_from_hist(*self.fine_ent), "auroc_conf": auroc_from_hist(*self.fine_conf),
                "undecidable": bool(self.n < FLOOR_CELL), "bins": bins, "entropy_bins": ent_bins}


# ---- worlds ----------------------------------------------------------------------------------

def fit_worlds():
    """The temperature fit's worlds: Phase 1e's VALIDATION split, nothing else (guard c7)."""
    return list(D.role_lists()[1])


def covered_pairs(w):
    return [(k, j) for k, j in D.pairs(w) if j not in w["scripted"]]


def load_heads():
    import torch
    torch.set_num_threads(1)
    return {(h, s): TA.load_act(h, s)[0] for h in HEADS for s in SEEDS}


def head_name(h, s):
    return f"{h}-s{s}"


# ---- C3a: the fit ----------------------------------------------------------------------------

def read_fit(progress=True):
    t0 = time.time()
    heads = load_heads()
    grids, counts = {}, {}
    worlds = fit_worlds()
    for i, (name, seed) in enumerate(worlds):
        w = D.load_world(name, seed)
        pairs = covered_pairs(w)
        X = np.stack([D.pair_x(w, k, j) for k, j in pairs], 1)
        Y = [D.targets(w["applied"], j) for _k, j in pairs]
        ST = [D.row_state(X[:, pi]) for pi in range(len(pairs))]
        for (h, s), m in heads.items():
            P = TA.probs_from_x(m, X)
            hn = head_name(h, s)
            for pi in range(len(pairs)):
                for hi, hz in enumerate(HORIZONS):
                    yy, st, pp = Y[pi][::FIT_STRIDE, hi], ST[pi][::FIT_STRIDE], P[::FIT_STRIDE, pi, hi]
                    ok = yy >= 0
                    for rg in REGIMES:
                        sel = ok if rg == "all" else ok & (st == D.STATE_NAMES.index(rg))
                        if not sel.any():
                            continue
                        key = (hn, hz, rg)
                        grids[key] = grids.get(key, 0.0) + nll_grid(pp[sel], yy[sel])
                        counts[key] = counts.get(key, 0) + int(sel.sum())
        if progress and ((i + 1) % 10 == 0 or i + 1 == len(worlds)):
            print(f"  fit: {i + 1}/{len(worlds)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    fits, detail = {}, {}
    for (hn, hz, rg), g in grids.items():
        T = fit_temperature(g)
        n = counts[(hn, hz, rg)]
        i1 = int(np.argmin(np.abs(T_GRID - 1.0)))
        detail.setdefault(hn, {}).setdefault(hz, {})[rg] = {"T_fit": T, "n": n, "nll_T1": float(g[i1] / n), "nll_fit": float(g.min() / n),
                                                            "undecidable": bool(n < FLOOR_CELL)}
    for hn in detail:
        for hz in detail[hn]:
            d = detail[hn][hz]
            fits.setdefault(hn, {})[hz] = {rg: (d[rg]["T_fit"] if (rg in d and not d[rg]["undecidable"]) else d["all"]["T_fit"]) for rg in REGIMES}
    return {"split": "phase1e-validation", "worlds": len(worlds), "stride": FIT_STRIDE, "grid": [float(T_GRID[0]), float(T_GRID[-1]), 0.01],
            "heads": [head_name(h, s) for h in HEADS for s in SEEDS], "floor_cell": FLOOR_CELL,
            "note": "a regime under the floor takes the global (all) temperature; fits[...] is what the reliability read applies",
            "fits": fits, "detail": detail, "seconds": round(time.time() - t0)}


# ---- C1 / C2 / C3b: the reliability read ------------------------------------------------------

def read_reliability(progress=True):
    t0 = time.time()
    temps = json.loads((READS / "temperature.json").read_text())["fits"]
    heads = load_heads()
    cells = {}
    worlds = R.needy_worlds("tuning")
    for i, (arm, k, seed, _ticks, path) in enumerate(worlds):
        w, observers, scripted = R.load_needy(path, arm, k, seed, "tuning")
        pairs, X, ys, states, cls = R.world_inputs(w, observers, scripted)
        for (h, s), m in heads.items():
            P = TA.probs_from_x(m, X)
            hn = head_name(h, s)
            for pi in range(len(pairs)):
                if cls[pi] != "covered":
                    continue
                st = states[pi]
                for hi, hz in enumerate(HORIZONS):
                    yy = ys[pi][:, hi]
                    ok = yy >= 0
                    tf = temps[hn][hz]
                    T_rows = np.array([tf[D.STATE_NAMES[int(v)]] for v in range(3)], np.float64)[st]
                    for rg in REGIMES:
                        sel = ok if rg == "all" else ok & (st == D.STATE_NAMES.index(rg))
                        if not sel.any():
                            continue
                        cells.setdefault((hn, hz, rg), Cal()).add(P[sel, pi, hi], yy[sel], tf["all"], T_rows[sel])
        if progress and ((i + 1) % 20 == 0 or i + 1 == len(worlds)):
            print(f"  reliability: {i + 1}/{len(worlds)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    tables = {}
    for (hn, hz, rg), c in cells.items():
        tables.setdefault(hn, {}).setdefault(hz, {})[rg] = c.row()
    return {"half": "tuning", "cls": "covered", "heads": sorted(tables), "temperings": list(TEMPERINGS), "conf_edges": list(CONF_EDGES),
            "ent_edges": list(ENT_EDGES), "fine": FINE, "floor_cell": FLOOR_CELL, "floor_bin": FLOOR_BIN,
            "summary": summarise(tables), "tables": tables, "seconds": round(time.time() - t0)}


def seed_mean(tables, h, hz, rg, metric, sub=None):
    vals = []
    for s in SEEDS:
        t = tables.get(head_name(h, s), {}).get(hz, {}).get(rg)
        if t and t.get("n"):
            v = t[metric] if sub is None else t[metric][sub]
            if v is not None:
                vals.append(v)
    return R1.msd(vals) if vals else None


def summarise(tables):
    out = {}
    for h in HEADS:
        for hz in HORIZONS:
            for rg in REGIMES:
                cell = {m: seed_mean(tables, h, hz, rg, m) for m in ("top1", "logloss", "mean_conf", "mean_entropy", "auroc_entropy", "auroc_conf")}
                cell["ece"] = {t: seed_mean(tables, h, hz, rg, "ece", t) for t in TEMPERINGS}
                cell["n"] = min((tables[head_name(h, s)][hz][rg]["n"] for s in SEEDS if head_name(h, s) in tables and rg in tables[head_name(h, s)].get(hz, {})), default=0)
                out.setdefault(h, {}).setdefault(hz, {})[rg] = cell
    return out


# ---- the score -------------------------------------------------------------------------------

def read_score():
    rel = json.loads((READS / "reliability.json").read_text())
    fit = json.loads((READS / "temperature.json").read_text())
    S = rel["summary"]
    m = lambda h, hz, rg, k: S[h][hz][rg][k]["mean"]        # noqa: E731
    gap29 = m("B10", "y0", "seen", "mean_conf") - m("B10", "y0", "heard", "mean_conf")
    au30 = m("B10", "y0", "seen", "auroc_entropy")
    gaps31 = {rg: m("B30", "y0", rg, "auroc_entropy") - m("B10", "y0", rg, "auroc_entropy") for rg in ("seen", "heard")}
    tgaps = [abs(fit["detail"][head_name("B10", s)]["y0"]["seen"]["T_fit"] - fit["detail"][head_name("B10", s)]["y0"]["heard"]["T_fit"]) for s in SEEDS]
    gap32 = float(np.mean(tgaps))
    score = {"P29": {"gap": gap29, "bar": PRED["P29"]["conf_gap_min"], "met": bool(gap29 >= PRED["P29"]["conf_gap_min"])},
             "P30": {"auroc": au30, "bar": PRED["P30"]["auroc_min"], "met": bool(au30 >= PRED["P30"]["auroc_min"])},
             "P31": {"gaps": gaps31, "bar": PRED["P31"]["auroc_gap_max"], "met": bool(all(g < PRED["P31"]["auroc_gap_max"] for g in gaps31.values()))},
             "P32": {"gap": gap32, "per_seed": tgaps, "bar": PRED["P32"]["temp_gap_min"], "met": bool(gap32 >= PRED["P32"]["temp_gap_min"])}}
    undecidable = [(h, hz, rg) for h, hz, rg in REGISTERED if S[h][hz][rg]["n"] < FLOOR_CELL]
    # the tempering rule (DECLARATION §6): per-regime if P32 met, else global; dropped to T = 1 for A HEAD whose registered cell it
    # worsens — a head is one trained seed (B10-s1 .. B30-s3), so the rule is applied per head; the arm view (seed means) is kept beside
    adopted = "regime" if score["P32"]["met"] else "global"
    tempering, arm_view = {}, {}
    for h in HEADS:
        for s in SEEDS:
            hn = head_name(h, s)
            t = rel["tables"][hn]["y0"]
            worse = [rg for rg in ("seen", "heard") if t[rg]["ece"][adopted] > t[rg]["ece"]["T1"]]
            tf = fit["fits"][hn]["y0"]
            frozen = (1.0 if worse else (tf["all"] if adopted == "global" else None))
            tempering[hn] = {"adopted": ("T1" if worse else adopted), "worsened_cells": worse,
                             "T_frozen": (frozen if adopted == "global" or worse else {rg: tf[rg] for rg in REGIMES}),
                             "ece": {rg: {k: t[rg]["ece"][k] for k in TEMPERINGS} for rg in ("seen", "heard")}}
        worse = [rg for rg in ("seen", "heard") if S[h]["y0"][rg]["ece"][adopted]["mean"] > S[h]["y0"][rg]["ece"]["T1"]["mean"]]
        arm_view[h] = {"adopted_if_read_per_arm": ("T1" if worse else adopted), "worsened_cells": worse,
                       "ece": {rg: {k: S[h]["y0"][rg]["ece"][k]["mean"] for k in TEMPERINGS} for rg in ("seen", "heard")}}
    b20 = "not registered in Phase 2 (P31 met; the rule as declared — RESULTS reports on its rationale)" if score["P31"]["met"] else \
          "registered in Phase 2 as its own welfare prediction if the block can afford the ablation (her call)"
    return {"score": score, "met": {p: score[p]["met"] for p in score}, "undecidable_registered_cells": undecidable, "tempering_rule": adopted,
            "tempering": tempering, "arm_view": arm_view, "b20": b20, "registered": [list(r) for r in REGISTERED]}


# ---- md --------------------------------------------------------------------------------------

def _f(v, d=3):
    if v is None:
        return "—"
    if isinstance(v, dict):
        return R1._f(v, d)
    return f"{v:.{d}f}"


def md(cmd, out):
    L = [f"# Act-head calibration read: {cmd}", ""]
    if cmd == "fit":
        L += [f"Phase 1e validation split, {out['worlds']} worlds, covered friends, every {out['stride']}th tick; grid {out['grid']}.", "",
              "| head | horizon | regime | n | T fit | NLL at T = 1 | NLL at fit | applied |", "|---|---|---|---|---|---|---|---|"]
        for hn in out["detail"]:
            for hz in HORIZONS:
                for rg in REGIMES:
                    d = out["detail"][hn][hz].get(rg)
                    if d:
                        L.append(f"| {hn} | {hz} | {rg} | {d['n']:,} | {d['T_fit']:.2f} | {d['nll_T1']:.4f} | {d['nll_fit']:.4f} | {out['fits'][hn][hz][rg]:.2f}{' (floor)' if d['undecidable'] else ''} |")
    elif cmd == "reliability":
        S = out["summary"]
        L += ["Needy tuning half, covered friends; seed mean ± SD over three heads per arm.", "",
              "| head | horizon | regime | n (min seed) | top-1 | log-loss | mean top-prob | mean entropy | ECE T=1 | ECE global | ECE regime | AUROC 1−entropy | AUROC top-prob |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for h in HEADS:
            for hz in HORIZONS:
                for rg in REGIMES:
                    c = S[h][hz][rg]
                    L.append(f"| {h} | {hz} | {rg} | {c['n']:,} | {_f(c['top1'])} | {_f(c['logloss'])} | {_f(c['mean_conf'])} | {_f(c['mean_entropy'])} | "
                             f"{_f(c['ece']['T1'], 4)} | {_f(c['ece']['global'], 4)} | {_f(c['ece']['regime'], 4)} | {_f(c['auroc_entropy'])} | {_f(c['auroc_conf'])} |")
        for h in HEADS:
            for rg in ("seen", "heard"):
                t = out["tables"][head_name(h, 1)]["y0"][rg]
                L += ["", f"### {h}-s1, y0, {rg}: top-prob reliability (T = 1) and accuracy by entropy", "",
                      "| top-prob bin | n | mean conf | accuracy | | entropy bin | n | accuracy |", "|---|---|---|---|---|---|---|---|"]
                for b, e in zip(t["bins"]["T1"], t["entropy_bins"]):
                    L.append(f"| {b['bin']} | {b['n']:,}{' thin' if b['thin'] else ''} | {_f(b['conf'])} | {_f(b['acc'])} | | {e['bin']} | {e['n']:,}{' thin' if e['thin'] else ''} | {_f(e['acc'])} |")
    else:
        L += ["```", json.dumps(out, indent=1), "```"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit", "reliability", "score"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.cmd == "fit":
        out = read_fit(progress=not a.quiet)
    elif a.cmd == "reliability":
        out = read_reliability(progress=not a.quiet)
    else:
        out = read_score()
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k not in ("tables", "detail")}, indent=1))


if __name__ == "__main__":
    main()
