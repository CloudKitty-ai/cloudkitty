#!/usr/bin/env python3
"""Act predictor Phase 1 — the reads (DECLARATION.md §5), one subcommand each; every figure the seed mean ± SD over
three heads per arm, the baselines F / V / R beside, by the same reader on the same worlds.

    read_act.py accuracy   --out reads/accuracy.json   [--md]            # R-A: four arms on the lived evaluation worlds and the needy TUNING half
    read_act.py ladder     --out reads/ladder.json     [--md] [--margin m --words "..."]   # R-B from accuracy.json; P25, P27, P28; P26 once m is ruled
    read_act.py confirming --out reads/confirming.json [--md]            # R-C: the chosen arm on the needy CONFIRMING half, once
    read_act.py score      --out reads/score.json      [--md]

Covered friends only in every scored cell; the scripted friend's rows apart. Every needy-set world passes
needy_read.refuse_unless for the half its read is declared on.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_act as D  # noqa: E402
import train_act as TA  # noqa: E402
import read_1e as R1  # noqa: E402  (on the path via train_act)

READS = HERE / "reads"
SEEDS = (1, 2, 3)
ARMS = TA.ARMS
HORIZONS = ("y0", "y10")
STATES = ("all", "seen", "heard", "silent")
CLASSES = ("covered", "scripted")
GROUP_P = ("P1", "P2", "P3", "P4", "P5")
GROUP_LWG = ("L", "W", "G")
PRIMARY = {"group": "needy-tuning", "horizon": "y0", "state": "all", "cls": "covered", "metric": "top1"}
FOG = dict(PRIMARY, state="silent")
PRED = {"P25": {"fog_gain_over_F_min": 0.05}, "P26": {"margin_recommended": 0.02}, "P27": {"ladder_gain_max": 0.02}}
MODE_SOURCE = ("B10", 1)                                   # the F baseline's class frequencies: every arm trained on the same data


def mods():
    return R1._needy_modules()


# ---- metrics --------------------------------------------------------------------------------

class Acc:
    """One cell's accumulator: n, top-1 correct, log-loss sum, confusion (true x predicted)."""
    def __init__(self):
        self.n, self.correct, self.nll = 0, 0, 0.0
        self.conf = np.zeros((D.N_ACTS, D.N_ACTS), np.int64)

    def add(self, y, pred, nll=None):
        if len(y) == 0:
            return
        self.n += len(y)
        self.correct += int((pred == y).sum())
        if nll is not None:
            self.nll += float(nll.sum())
        np.add.at(self.conf, (y, pred), 1)

    def row(self, live):
        if self.n == 0:
            return {"n": 0}
        rec = {}
        for c in live:
            s = self.conf[c].sum()
            if s > 0:
                rec[D.ACT_NAMES[c]] = float(self.conf[c, c] / s)
        return {"n": int(self.n), "top1": self.correct / self.n, "logloss": (self.nll / self.n) if self.nll else None,
                "macro_recall": float(np.mean(list(rec.values()))) if rec else None, "recall": rec,
                "support": {D.ACT_NAMES[c]: int(self.conf[c].sum()) for c in live}}


def metrics_hand(y, pred, p=None, live=None):
    """The textbook values on arrays (guard a4): top-1, mean log-loss of p[y], macro recall over `live`."""
    a = Acc()
    nll = None if p is None else -np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1))
    a.add(np.asarray(y), np.asarray(pred), nll)
    return a.row(live if live is not None else range(D.N_ACTS))


# ---- worlds ---------------------------------------------------------------------------------

def lived_worlds():
    """[(group, set, seed)] — the 1b evaluation worlds."""
    r = D.roles()
    out = []
    for n in GROUP_P:
        out += [("lived-P", n, s) for s in r[n]["eval"]]
    for n in GROUP_LWG:
        out += [("lived-LWG", n, s) for s in r[n]["eval"]]
    return out


def needy_worlds(half):
    rise, _R, _L = mods()
    return rise.worlds(half)


def world_inputs(w, observers, scripted):
    """For every (observer, friend) pair: x (T, 167) f16, y (T, 2), row states, cls; stacked x for the forward."""
    _rise, R, _L = mods()
    pairs, xs, ys, states, cls = [], [], [], [], []
    for k in observers:
        for j in range(D.ROSTER):
            if j == k:
                continue
            x = (D.pair_x(w, k, j) if "observers" in w else R.pair_x(w, k, j)[0])
            pairs.append((k, j))
            xs.append(x)
            ys.append(D.targets(w["applied"], j))
            states.append(D.row_state(x))
            cls.append("scripted" if j == scripted else "covered")
    return pairs, np.stack(xs, 1), ys, states, cls


def load_needy(path, arm, k, seed, half):
    _rise, R, _L = mods()
    R.refuse_unless(arm, k, seed, half)
    w = R.load_world(path)
    assert w["meta"]["aborted_at"] is None, path
    w["applied"] = D.applied_of(path)
    return w, R.observers(w), w["scripted"][0]


def load_lived(name, seed):
    w = D.load_world(name, seed)
    assert w["observers"] == list(range(D.ROSTER)), (name, seed)
    return w, w["observers"], None


def mode_and_live():
    man = json.loads((TA.OUT_ROOT / TA.run_name(*MODE_SOURCE) / "run-manifest.json").read_text())
    cf = np.asarray(man["class_freq_train_y0"], np.int64)
    return int(cf.argmax()), cf / cf.sum(), [c for c in range(D.N_ACTS) if cf[c] > 0]


# ---- the core read --------------------------------------------------------------------------

def evaluate(worlds, heads, progress=True, label=""):
    """worlds: [(group, loader_fn)]; heads: {(arm, seed): model}. Returns the nested cell tables for every head and
    the baselines, each cell an Acc.row."""
    mode, freq, live = mode_and_live()
    cells = {}            # (who, group, horizon, state, cls) -> Acc
    def acc(*key):
        return cells.setdefault(key, Acc())
    t0 = time.time()
    for i, (group, loader) in enumerate(worlds):
        w, observers, scripted = loader()
        pairs, X, ys, states, cls = world_inputs(w, observers, scripted)
        probs = {key: TA.probs_from_x(m, X) for key, m in heads.items()}       # (T, n, 2, 11)
        for pi, (k, j) in enumerate(pairs):
            y, st, c = ys[pi], states[pi], cls[pi]
            v = D.baseline_V(X[:, pi], mode)
            r = D.baseline_R(w["applied"][:, j], mode)
            for hi, hname in enumerate(HORIZONS):
                yy = y[:, hi]
                ok = yy >= 0
                for sname in STATES:
                    sel = ok if sname == "all" else ok & (st == D.STATE_NAMES.index(sname))
                    if not sel.any():
                        continue
                    yt = yy[sel]
                    for key, p in probs.items():
                        pp = p[sel, pi, hi]
                        acc(key, group, hname, sname, c).add(yt, pp.argmax(1), -np.log(np.clip(pp[np.arange(len(yt)), yt], 1e-12, 1)))
                    acc(("F",), group, hname, sname, c).add(yt, np.full(len(yt), mode), -np.log(np.clip(freq[yt], 1e-12, 1)))
                    acc(("V",), group, hname, sname, c).add(yt, v[sel])
                    acc(("R",), group, hname, sname, c).add(yt, r[sel])
        if progress and ((i + 1) % 20 == 0 or i + 1 == len(worlds)):
            print(f"  {label}: {i + 1}/{len(worlds)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    out = {}
    for (who, group, h, s, c), a in cells.items():
        name = who[0] if len(who) == 1 else f"{who[0]}-s{who[1]}"
        out.setdefault(name, {}).setdefault(group, {}).setdefault(h, {}).setdefault(s, {})[c] = a.row(live)
    return out, {"mode": mode, "mode_name": D.ACT_NAMES[mode], "freq": freq.tolist(), "live": [D.ACT_NAMES[c] for c in live]}


def seed_mean(tables, arm, group, h, s, c, metric):
    vals = [tables[f"{arm}-s{seed}"][group][h][s][c].get(metric) for seed in SEEDS
            if f"{arm}-s{seed}" in tables and group in tables[f"{arm}-s{seed}"] and h in tables[f"{arm}-s{seed}"][group]
            and s in tables[f"{arm}-s{seed}"][group][h] and c in tables[f"{arm}-s{seed}"][group][h][s]]
    return R1.msd([v for v in vals if v is not None])


def summarise(tables, arms):
    """Seed mean ± SD per arm and cell for top1 / logloss / macro_recall; the baselines' single values."""
    out = {}
    groups = sorted({g for t in tables.values() for g in t})
    for arm in arms:
        out[arm] = {g: {h: {s: {c: {m: seed_mean(tables, arm, g, h, s, c, m) for m in ("top1", "logloss", "macro_recall")}
                                 for c in CLASSES} for s in STATES} for h in HORIZONS} for g in groups}
    for b in ("F", "V", "R"):
        if b in tables:
            out[b] = tables[b]
    return out


def read_accuracy(progress=True):
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    heads = {(arm, s): TA.load_act(arm, s)[0] for arm in ARMS for s in SEEDS}
    worlds = [(g, (lambda n=n, s=s: load_lived(n, s))) for g, n, s in lived_worlds()]
    for arm, k, seed, _ticks, path in needy_worlds("tuning"):
        worlds.append(("needy-tuning", (lambda p=path, a=arm, kk=k, sd=seed: load_needy(p, a, kk, sd, "tuning"))))
        if arm == "N":
            pass
    tables, base = evaluate(worlds, heads, progress, "accuracy")
    # arm N apart on the tuning half: re-key from the records is not possible after pooling, so run the N worlds again as their own group
    worlds_n = [("needy-tuning-N", (lambda p=path, a=arm, kk=k, sd=seed: load_needy(p, a, kk, sd, "tuning")))
                for arm, k, seed, _ticks, path in needy_worlds("tuning") if arm == "N"]
    tables_n, _ = evaluate(worlds_n, heads, progress, "accuracy N")
    for who, t in tables_n.items():
        tables.setdefault(who, {}).update(t)
    out = {"half": "tuning", "arms": list(ARMS), "seeds": list(SEEDS), "baseline": base, "manifests": {f"{a}-s{s}": TA.load_act(a, s)[1] for a in ARMS for s in SEEDS},
           "summary": summarise(tables, ARMS), "tables": tables, "seconds": round(time.time() - t0)}
    for k_, v in out["manifests"].items():
        v.pop("roles", None)
    return out


def cell(summary, arm, spec, metric="top1"):
    v = summary[arm][spec["group"]][spec["horizon"]][spec["state"]][spec["cls"]][metric]
    return None if v is None else v["mean"]


def base_cell(summary, b, spec):
    return summary[b][spec["group"]][spec["horizon"]][spec["state"]][spec["cls"]].get("top1")


def read_ladder(margin=None, words=None):
    acc = json.loads((READS / "accuracy.json").read_text())
    S = acc["summary"]
    if margin is not None:
        READS.mkdir(exist_ok=True)
        (READS / "margin.json").write_text(json.dumps({"m": margin, "owner_words": words, "source": "DECLARATION §12 call 1"}, indent=1) + "\n")
    m = json.loads((READS / "margin.json").read_text())["m"] if (READS / "margin.json").exists() else None
    out = {"primary": PRIMARY, "fog": FOG, "margin": m, "cells": {}, "gains": {}}
    for spec_name, spec in (("primary", PRIMARY), ("fog", FOG)):
        row = {arm: cell(S, arm, spec) for arm in ARMS}
        row.update({b: base_cell(S, b, spec) for b in ("F", "V", "R")})
        out["cells"][spec_name] = row
        bs = {a: row[a] for a in ("B10", "B20", "B30") if row[a] is not None}
        best = max(bs, key=bs.get) if bs else None
        out["gains"][spec_name] = {"B_best": best, "B_best_value": bs.get(best), "B20_minus_B10": None if None in (row["B20"], row["B10"]) else row["B20"] - row["B10"],
                                   "B30_minus_B20": None if None in (row["B30"], row["B20"]) else row["B30"] - row["B20"],
                                   "B30_minus_B10": None if None in (row["B30"], row["B10"]) else row["B30"] - row["B10"],
                                   "A_minus_B_best": None if best is None or row["A"] is None else row["A"] - bs[best]}
    fog, prim = out["cells"]["fog"], out["cells"]["primary"]
    out["score"] = {
        "P25": {"B10_fog": fog["B10"], "F_fog": fog["F"], "gain": None if None in (fog["B10"], fog["F"]) else fog["B10"] - fog["F"],
                "bar": PRED["P25"]["fog_gain_over_F_min"], "met": fog["B10"] is not None and fog["F"] is not None and fog["B10"] - fog["F"] >= PRED["P25"]["fog_gain_over_F_min"]},
        "P27": {"primary_B30_minus_B10": out["gains"]["primary"]["B30_minus_B10"], "fog_B30_minus_B10": out["gains"]["fog"]["B30_minus_B10"], "bar": PRED["P27"]["ladder_gain_max"],
                "met": all(v is not None and v < PRED["P27"]["ladder_gain_max"] for v in (out["gains"]["primary"]["B30_minus_B10"], out["gains"]["fog"]["B30_minus_B10"]))},
        "P28": {"seen_cell": {arm: cell(S, arm, dict(PRIMARY, state="seen")) for arm in ARMS}, "V_seen": base_cell(S, "V", dict(PRIMARY, state="seen"))},
    }
    vs = out["score"]["P28"]["V_seen"]
    out["score"]["P28"]["unfit"] = [a for a, v in out["score"]["P28"]["seen_cell"].items() if v is None or vs is None or v < vs]
    out["score"]["P28"]["met"] = not out["score"]["P28"]["unfit"]
    if m is None:
        out["score"]["P26"] = {"met": None, "status": "pending her call on the margin (DECLARATION §12)"}
        out["chosen"] = None
    else:
        ok = all(out["gains"][k]["A_minus_B_best"] is not None and out["gains"][k]["A_minus_B_best"] >= -m for k in ("primary", "fog"))
        out["score"]["P26"] = {"margin": m, "A_minus_B_best_primary": out["gains"]["primary"]["A_minus_B_best"], "A_minus_B_best_fog": out["gains"]["fog"]["A_minus_B_best"], "met": ok}
        if ok:
            out["chosen"] = "A"
        else:
            bb = out["gains"]["primary"]["B_best_value"]
            out["chosen"] = next(a for a in ("B10", "B20", "B30") if prim[a] is not None and prim[a] >= bb - m)
        out["chosen_rule"] = "P26 met -> A; else the smallest B within m of B_best on the primary cell (DECLARATION §6)"
    return out


def read_confirming(progress=True):
    import torch
    torch.set_num_threads(1)
    lad = json.loads((READS / "ladder.json").read_text())
    assert lad.get("chosen"), "no chosen arm: the margin is not ruled (ladder.json)"
    arm = lad["chosen"]
    t0 = time.time()
    heads = {(arm, s): TA.load_act(arm, s)[0] for s in SEEDS}
    worlds = [("needy-confirming", (lambda p=path, a=a_, kk=k, sd=seed: load_needy(p, a, kk, sd, "confirming"))) for a_, k, seed, _t, path in needy_worlds("confirming")]
    tables, base = evaluate(worlds, heads, progress, "confirming")
    worlds_n = [("needy-confirming-N", (lambda p=path, a=a_, kk=k, sd=seed: load_needy(p, a, kk, sd, "confirming"))) for a_, k, seed, _t, path in needy_worlds("confirming") if a_ == "N"]
    tables_n, _ = evaluate(worlds_n, heads, progress, "confirming N")
    for who, t in tables_n.items():
        tables.setdefault(who, {}).update(t)
    return {"half": "confirming", "chosen": arm, "chosen_rule": lad.get("chosen_rule"), "baseline": base, "summary": summarise(tables, (arm,)), "tables": tables,
            "note": "the confirming half's covered friends, read once for the chosen arm; this half's fourth touch (DECLARATION §3)", "seconds": round(time.time() - t0)}


def read_score():
    lad = json.loads((READS / "ladder.json").read_text())
    out = {"P25": lad["score"]["P25"], "P26": lad["score"]["P26"], "P27": lad["score"]["P27"], "P28": lad["score"]["P28"], "chosen": lad.get("chosen")}
    f = READS / "confirming.json"
    if f.exists():
        c = json.loads(f.read_text())
        out["confirming"] = {"chosen": c["chosen"], "primary_cell": c["summary"][c["chosen"]]["needy-confirming"]["y0"]["all"]["covered"],
                             "fog_cell": c["summary"][c["chosen"]]["needy-confirming"]["y0"]["silent"]["covered"]}
    out["met"] = {p: out[p]["met"] for p in ("P25", "P26", "P27", "P28")}
    return out


# ---- md -------------------------------------------------------------------------------------

def _f(m, d=3):
    return R1._f(m, d)


def md(cmd, out):
    lines = [f"# Act predictor read: {cmd}", ""]
    if cmd in ("accuracy", "confirming"):
        S = out["summary"]
        arms = [a for a in S if a in ARMS]
        lines += [f"baseline F mode: {out['baseline']['mode_name']}; live classes: {', '.join(out['baseline']['live'])}", ""]
        groups = sorted({g for a in arms for g in S[a]})
        for g in groups:
            for c in CLASSES:
                lines += [f"### {g}, {c} friends", "", "| arm | horizon | state | n | top-1 | log-loss | macro recall |", "|---|---|---|---|---|---|---|"]
                for h in HORIZONS:
                    for s in STATES:
                        n = None
                        for a in arms:
                            r = S[a][g][h][s][c]
                            n = out["tables"][f"{a}-s1"].get(g, {}).get(h, {}).get(s, {}).get(c, {}).get("n") if n is None else n
                            lines.append(f"| {a} | {h} | {s} | {n if n is not None else '-'} | {_f(r['top1'])} | {_f(r['logloss'])} | {_f(r['macro_recall'])} |")
                        for b in ("F", "V", "R"):
                            r = S.get(b, {}).get(g, {}).get(h, {}).get(s, {}).get(c)
                            if r and r.get("n"):
                                lines.append(f"| {b} | {h} | {s} | {r['n']} | {_f(r.get('top1'))} | {_f(r.get('logloss'))} | {_f(r.get('macro_recall'))} |")
                lines.append("")
    elif cmd == "ladder":
        for spec in ("primary", "fog"):
            lines += [f"### {spec} cell ({json.dumps(out[spec])})", "", "| arm / baseline | top-1 |", "|---|---|"]
            for a, v in out["cells"][spec].items():
                lines.append(f"| {a} | {_f(v)} |")
            lines += ["", f"gains: {json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out['gains'][spec].items()})}", ""]
        lines += [f"chosen: {out.get('chosen')} ({out.get('chosen_rule')})", "", "```", json.dumps(out["score"], indent=1), "```"]
    else:
        lines += ["```", json.dumps(out, indent=1), "```"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["accuracy", "ladder", "confirming", "score"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--margin", type=float, default=None, help="ladder: the ruled margin m (DECLARATION §12), written to reads/margin.json")
    ap.add_argument("--words", default=None, help="ladder: her words ruling the margin, verbatim")
    a = ap.parse_args()
    if a.cmd == "accuracy":
        out = read_accuracy(progress=not a.quiet)
    elif a.cmd == "ladder":
        out = read_ladder(a.margin, a.words)
    elif a.cmd == "confirming":
        out = read_confirming(progress=not a.quiet)
    else:
        out = read_score()
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k != "tables"}, indent=1))


if __name__ == "__main__":
    main()
