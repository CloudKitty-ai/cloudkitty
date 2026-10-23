#!/usr/bin/env python3
"""Phase 1 reads R1–R6 (DECLARATION.md §Reads; descriptive, rule 10),
from the saved evaluation-world predictions of the six head runs and
the recorded raws. Nothing here gates.

    read_phase1.py --out phase1-read.json --md
    read_phase1.py --runs NF=NF-s1 NF=NF-s2 ... DR=DR-s1 ...   # explicit run dirs
    read_phase1.py --eval-sets P1 P2 P3 P4 P5 ...               # cells on these sets' eval worlds only (Phase 1b)

Arc root: split.json, results-raw/ and the default --out come from
MINIFRIEND_ARC when set (Phase 1b), else from this directory. Without
--eval-sets every set's evaluation worlds are pooled, as Phase 1 read.

Cells: friend × version (mind-visible / all-states) × stratum class
(COMMON; DA = GRAVE ∪ ADJACENT, the prereg's distress-adjacent column;
GRAVE alone). A cell with fewer than MIN_N samples is INSUFFICIENT
COVERAGE: None, fail-closed. "Pooled" is sample-weighted over the
friends whose cell is covered, naming them. Errors are in need points
(/100 scale): MSE5 = mean over the five hidden needs of (pred − true)²;
bias = mean over the five of (pred − true), negative = the friend
predicted LESS needy than she is (the ostrich direction).
"""
import argparse
import json
import os
import statistics as st
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARC = Path(os.environ.get("MINIFRIEND_ARC", HERE)).resolve()
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
import phase1_data as D  # noqa: E402
import strata as S  # noqa: E402

MIN_N = 200
TOL = 1.10            # the declared 10% relative equivalence tolerance (R2)
LIFT = 1.5            # the ostrich signature's grave-over-benign lift (R4)
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
CLASSES = {"COMMON": (S.COMMON,), "DA": (S.GRAVE, S.ADJACENT), "GRAVE": (S.GRAVE,)}
VERSIONS = ("visible", "all")
DEFAULT_RUNS = [(h, f"{h}-s{s}") for h in ("NF", "DR") for s in (1, 2, 3)]
ROW_ACT, ROW_PARTNER = 6, 13       # inside a kitty row: activity one-hot 6..12, partner bit 13


# ---------------------------------------------------------------- data

def eval_index(sets=None):
    """Flat sample arrays over every evaluation world (of `sets` only, when
    given): true (N,7) in points, code (N,), vis (N,), friend (N,), key
    (N,) for the persistence proxy, plus per-run prediction loaders'
    slice map."""
    roles = D.roles()
    if sets is not None:
        missing = [n for n in sets if n not in roles]
        assert not missing, f"--eval-sets not in split.json: {missing}"
    worlds = [(n, s) for n, r in roles.items() if sets is None or n in sets for s in r["eval"]]
    assert worlds, "no evaluation world selected"
    parts, keys, slices, pos = [], [], [], 0
    for n, s in worlds:
        w = D.load_world(n, s)
        for k, j in D.pairs(w):
            x, y, vis, code = D.pair_arrays(w, k, j)
            T = len(code)
            parts.append((y * 100.0, code, vis, np.full(T, j, np.int8)))
            keys.append(proxy_key(x))
            slices.append((n, s, k, j, pos, pos + T))
            pos += T
    true = np.concatenate([p[0] for p in parts])
    code = np.concatenate([p[1] for p in parts])
    vis = np.concatenate([p[2] for p in parts])
    friend = np.concatenate([p[3] for p in parts])
    return {"worlds": worlds, "sets": sorted({n for n, _ in worlds}), "true": true, "code": code, "vis": vis,
            "friend": friend, "key": np.concatenate(keys), "slices": slices, "n": pos}


def proxy_key(x):
    """The persistence baseline's lookup key from the friend's row: present
    bit, activity one-hot argmax (7), partner bit → 1 + act·2 + partner in
    1..14, or 0 = not present (15 possible keys, held in a 28-slot table)."""
    row = x[:, D.SELF_BLOCK:].astype(np.float32)
    present = row[:, 0] > 0.5
    act = row[:, ROW_ACT:ROW_ACT + 7].argmax(1)
    partner = row[:, ROW_PARTNER] > 0.5
    return np.where(present, 1 + act * 2 + partner.astype(np.int64), 0)


def load_pred(run, idx):
    out = np.empty((idx["n"], D.Y_DIM), np.float32)
    cache = {}
    for n, s, k, j, a, b in idx["slices"]:
        if (n, s) not in cache:
            cache[(n, s)] = np.load(ARC / "results-raw/heads" / run / f"pred-{n}-{s}.npz")["pred"]
        out[a:b] = cache[(n, s)][:, k, j]
    return out * 100.0


def train_stats():
    """R3's tables from the TRAIN worlds' samples: marginal mean per hidden
    need, and the mean per proxy key (friend's visible activity + partner)."""
    roles = D.roles()
    sums = np.zeros((28, 5)); cnt = np.zeros(28)
    for n, r in roles.items():
        for s in r["train"]:
            w = D.load_world(n, s)
            for k, j in D.pairs(w):
                x, y, _v, _c = D.pair_arrays(w, k, j)
                key = proxy_key(x)
                np.add.at(sums, key, y[:, :5] * 100.0)
                np.add.at(cnt, key, 1)
    marginal = sums.sum(0) / cnt.sum()
    table = np.where(cnt[:, None] > 0, sums / np.maximum(cnt, 1)[:, None], marginal[None])
    return {"marginal": marginal, "table": table, "key_counts": cnt}


# ---------------------------------------------------------------- cells

def cell_mask(idx, friend, version, cls):
    m = (idx["friend"] == friend) & np.isin(idx["code"], CLASSES[cls])
    if version == "visible":
        m &= idx["vis"]
    return m


def errors(pred, true):
    pred, true = pred.astype(np.float64), true.astype(np.float64)   # float64: pooled == per-friend recombination
    d = pred[:, :5] - true[:, :5]
    return {"mse5": float((d ** 2).mean()), "bias": float(d.mean()),
            "mse_hap": float(((pred[:, 5] - true[:, 5]) ** 2).mean()),
            "mse_bath": float(((pred[:, 6] - true[:, 6]) ** 2).mean())}


def cells_for(pred, idx):
    """{version: {cls: {friend: {n, mse5, bias, mse_hap, mse_bath} | insufficient}}} plus pooled."""
    out = {}
    for v in VERSIONS:
        out[v] = {}
        for cls in CLASSES:
            per, masks = {}, {}
            for j, name in enumerate(SEATS):
                m = cell_mask(idx, j, v, cls)
                n = int(m.sum())
                if n < MIN_N:
                    per[name] = {"n": n, "insufficient": True}
                else:
                    per[name] = dict(n=n, **errors(pred[m], idx["true"][m]))
                    masks[name] = m
            if masks:
                mm = np.logical_or.reduce(list(masks.values()))
                pooled = dict(n=int(mm.sum()), friends=sorted(masks), **errors(pred[mm], idx["true"][mm]))
            else:
                pooled = {"n": 0, "friends": [], "insufficient": True}
            out[v][cls] = {"per_friend": per, "pooled": pooled}
    return out


def baseline_preds(idx, stats, kind):
    n = idx["n"]
    p = np.zeros((n, D.Y_DIM), np.float32)
    if kind == "marginal":
        p[:, :5] = stats["marginal"]
    else:
        p[:, :5] = stats["table"][idx["key"]]
    p[:, 5] = idx["true"][:, 5]      # happiness / bath are not the baselines' subject; copy truth so only mse5 reads
    p[:, 6] = idx["true"][:, 6]
    return p


# ---------------------------------------------------------------- across seeds

def msd(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"mean": st.mean(xs), "sd": st.stdev(xs) if len(xs) > 1 else None, "seeds": len(xs)}


def get(cells, v, cls, friend, field):
    c = cells[v][cls]["pooled"] if friend == "pooled" else cells[v][cls]["per_friend"][friend]
    return None if c.get("insufficient") else c[field]


def across_seeds(runs_cells, field):
    """{version: {cls: {friend|pooled: msd}}} over a head's seeds."""
    out = {}
    for v in VERSIONS:
        out[v] = {}
        for cls in CLASSES:
            out[v][cls] = {}
            for f in SEATS + ["pooled"]:
                out[v][cls][f] = msd([get(c, v, cls, f, field) for c in runs_cells])
    return out


def dissolution(nf, dr, tol=TOL):
    """R2, procedure frozen in the declaration. nf, dr: across_seeds mse5
    tables. Floor = DR pooled mind-visible GRAVE mean. NF dissolves the
    tension iff NF_grave ≤ tol × DR_grave on the pooled mind-visible read
    AND no covered friend's NF_grave exceeds tol × its DR_grave by more
    than NF's between-seed SD for that friend."""
    floor = dr["visible"]["GRAVE"]["pooled"]
    nfp = nf["visible"]["GRAVE"]["pooled"]
    if floor is None or nfp is None:
        return {"readable": False, "reason": "pooled mind-visible GRAVE unreadable"}
    pooled_ok = nfp["mean"] <= tol * floor["mean"]
    per = {}
    for f in SEATS:
        a, b = nf["visible"]["GRAVE"][f], dr["visible"]["GRAVE"][f]
        if a is None or b is None:
            per[f] = {"covered": False}
            continue
        sd = a["sd"] or 0.0
        per[f] = {"covered": True, "nf": a["mean"], "dr": b["mean"], "excess": a["mean"] - tol * b["mean"],
                  "nf_sd": sd, "ok": a["mean"] - tol * b["mean"] <= sd}
    friends_ok = all(p["ok"] for p in per.values() if p["covered"])
    return {"readable": True, "floor_dr_grave": floor["mean"], "nf_grave": nfp["mean"],
            "ratio": nfp["mean"] / floor["mean"], "tolerance": tol, "pooled_ok": pooled_ok,
            "per_friend": per, "friends_ok": friends_ok, "dissolves": bool(pooled_ok and friends_ok),
            "pooled_friends": [f for f, p in per.items() if p["covered"]]}


def ostrich(bias_tbl):
    """R4 from an across-seeds bias table: gap = GRAVE bias − COMMON bias
    per friend × version (and pooled); signature = |GRAVE| ≥ LIFT × |COMMON|
    with GRAVE bias negative (optimism)."""
    out = {}
    for v in VERSIONS:
        out[v] = {}
        for f in SEATS + ["pooled"]:
            g, c = bias_tbl[v]["GRAVE"][f], bias_tbl[v]["COMMON"][f]
            if g is None or c is None:
                out[v][f] = {"covered": False}
                continue
            lift = abs(g["mean"]) / abs(c["mean"]) if c["mean"] != 0 else float("inf")
            out[v][f] = {"covered": True, "grave_bias": g["mean"], "common_bias": c["mean"],
                         "gap": g["mean"] - c["mean"], "lift": lift,
                         "signature": bool(lift >= LIFT and g["mean"] < 0)}
    return out


# ---------------------------------------------------------------- main

def read(runs, sets=None):
    idx = eval_index(sets)
    stats = train_stats()
    per_run = {}
    for head, run in runs:
        pred = load_pred(run, idx)
        man = json.loads((ARC / "results-raw/heads" / run / "run-manifest.json").read_text())
        done = json.loads((ARC / "results-raw/heads" / run / "done.json").read_text())
        per_run[run] = {"head": head, "cells": cells_for(pred, idx), "params": man["params"],
                        "best_epoch": done["best_epoch"], "epochs_run": done["epochs_run"], "best_val": done["best_val"],
                        "dr_weights": man["dr_weights_GRAVE_ADJACENT_COMMON"], "seed": man["seed"]}
    heads = {}
    for head in ("NF", "DR"):
        cells = [per_run[r]["cells"] for h, r in runs if h == head]
        heads[head] = {"runs": [r for h, r in runs if h == head],
                       "mse5": across_seeds(cells, "mse5"), "bias": across_seeds(cells, "bias"),
                       "mse_bath": across_seeds(cells, "mse_bath"), "mse_hap": across_seeds(cells, "mse_hap")}
    base = {}
    for kind in ("marginal", "persistence"):
        c = cells_for(baseline_preds(idx, stats, kind), idx)
        base[kind] = {"mse5": across_seeds([c], "mse5"), "bias": across_seeds([c], "bias")}
    coverage = {v: {cls: {f: cells_for_counts(idx, j, v, cls) for j, f in enumerate(SEATS)} for cls in CLASSES} for v in VERSIONS}
    return {"min_n": MIN_N, "n_samples": idx["n"], "eval_worlds": idx["worlds"], "eval_sets": idx["sets"], "coverage": coverage,
            "runs": {r: {k: v for k, v in d.items() if k != "cells"} for r, d in per_run.items()},
            "per_run_cells": {r: d["cells"] for r, d in per_run.items()},
            "heads": heads, "baselines": base,
            "R2": dissolution(heads["NF"]["mse5"], heads["DR"]["mse5"]) if heads["NF"]["runs"] and heads["DR"]["runs"] else None,
            "R4": {h: ostrich(heads[h]["bias"]) for h in heads if heads[h]["runs"]},
            "R3_marginal": stats["marginal"].tolist(), "R3_key_counts": stats["key_counts"].tolist()}


def cells_for_counts(idx, j, v, cls):
    return int(cell_mask(idx, j, v, cls).sum())


def fmt(m, d=2):
    if m is None:
        return "insuff."
    return f"{m['mean']:.{d}f}" + (f" ± {m['sd']:.{d}f}" if m.get("sd") is not None else "")


def md(out):
    L = [f"samples {out['n_samples']} over {len(out['eval_worlds'])} eval worlds; min-n {out['min_n']}", ""]
    L.append("Coverage (n per friend; visible / all): " + "; ".join(
        f"{f} GRAVE {out['coverage']['visible']['GRAVE'][f]}/{out['coverage']['all']['GRAVE'][f]}, DA {out['coverage']['visible']['DA'][f]}/{out['coverage']['all']['DA'][f]}"
        for f in SEATS))
    for v in VERSIONS:
        L.append(f"\n### R1 MSE5 (need points²), {v}\n")
        L.append("| friend | " + " | ".join(f"{h} {c}" for h in ("NF", "DR") for c in CLASSES) + " | marg GRAVE | persist GRAVE |")
        L.append("|---|" + "---|" * 8)
        for f in SEATS + ["pooled"]:
            L.append(f"| {f} | " + " | ".join(fmt(out["heads"][h]["mse5"][v][c][f]) for h in ("NF", "DR") for c in CLASSES)
                     + f" | {fmt(out['baselines']['marginal']['mse5'][v]['GRAVE'][f])} | {fmt(out['baselines']['persistence']['mse5'][v]['GRAVE'][f])} |")
    r2 = out["R2"]
    if r2 and r2["readable"]:
        L.append(f"\n### R2 dissolution: floor (DR pooled mind-visible GRAVE) {r2['floor_dr_grave']:.2f}; NF {r2['nf_grave']:.2f}; "
                 f"ratio {r2['ratio']:.3f} vs {r2['tolerance']}; pooled {'OK' if r2['pooled_ok'] else 'FAILS'}; "
                 f"friends {'OK' if r2['friends_ok'] else 'FAIL'} → {'DISSOLVES' if r2['dissolves'] else 'TENSION STANDS'}")
        for f, p in r2["per_friend"].items():
            L.append(f"  {f}: " + (f"NF {p['nf']:.2f} DR {p['dr']:.2f} excess {p['excess']:+.2f} vs sd {p['nf_sd']:.2f} {'ok' if p['ok'] else 'EXCEEDS'}" if p["covered"] else "insufficient coverage"))
    for v in VERSIONS:
        L.append(f"\n### R4 ostrich ({v}; bias in need points, gap = GRAVE − COMMON)\n")
        L.append("| friend | " + " | ".join(f"{h} grave / common / gap / lift" for h in out["R4"]) + " |")
        L.append("|---|" + "---|" * len(out["R4"]))
        for f in SEATS + ["pooled"]:
            cols = []
            for h, t in out["R4"].items():
                c = t[v][f]
                cols.append(f"{c['grave_bias']:+.2f} / {c['common_bias']:+.2f} / {c['gap']:+.2f} / {c['lift']:.2f}{' SIG' if c['signature'] else ''}" if c["covered"] else "insuff.")
            L.append(f"| {f} | " + " | ".join(cols) + " |")
    L.append("\n### R5 bath MSE (pipeline bound), pooled: " + "; ".join(
        f"{h} {v} {c} {fmt(out['heads'][h]['mse_bath'][v][c]['pooled'])}" for h in ("NF", "DR") for v in VERSIONS for c in ("COMMON", "GRAVE")))
    L.append("\n### R6 runs: " + "; ".join(f"{r} params {d['params']} best epoch {d['best_epoch']}/{d['epochs_run']} val {d['best_val']:.5f}" for r, d in out["runs"].items()))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ARC / "phase1-read.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--runs", nargs="*", help="HEAD=run-dir overrides (default NF-s1..3, DR-s1..3)")
    ap.add_argument("--eval-sets", nargs="*", help="read the cells on these sets' evaluation worlds only (default: all sets)")
    a = ap.parse_args()
    runs = [tuple(r.split("=", 1)) for r in a.runs] if a.runs else DEFAULT_RUNS
    out = read(runs, a.eval_sets)
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}")
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
