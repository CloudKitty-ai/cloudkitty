#!/usr/bin/env python3
"""Act-head parameter ladder (DECLARATION.md): two more sizes, B5 and B15, trained by the act arc's trainer verbatim and read
beside B10 / B20 / B30 by the act arc's accuracy reader and the calibration arc's reliability reader; then the curve.

    ladder_act.py train --arm B5|B15 --seed k [--smoke]        # train_act.main with the ladder arms registered; heads land in the act arc's heads store
    ladder_act.py accuracy    --out reads/accuracy.json    [--md] # read_act.read_accuracy over the five B arms (tuning half + lived worlds)
    ladder_act.py fit         --out reads/temperature.json [--md] # calib_act.read_fit over the five arms (reported only: T = 1 is ruled)
    ladder_act.py reliability --out reads/reliability.json [--md] # calib_act.read_reliability over the five arms; the 0.05 trigger read at T = 1
    ladder_act.py curve       --out reads/curve.json       [--md] # log-loss and top-1 against parameter count; marginal gain per 1,000 params; P33

The act arc's modules are imported, not copied; this file only registers the two arms and points the readers at this arc's reads/.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ACT = HERE.parent / "minifriend-act-2026-11-03"
CALIB = HERE.parent / "minifriend-act-calib-2026-11-04"
sys.path.insert(0, str(ACT))
sys.path.insert(0, str(CALIB))
import train_act as TA  # noqa: E402
import read_act as R  # noqa: E402
import calib_act as CA  # noqa: E402

READS = HERE / "reads"
TRUNK = TA.TRUNK_PARAMS
NEW = {"B5": (14, 0.05, 3942), "B15": (32, 0.15, 12438)}            # arm -> (GRU width, nominal cap, declared trained params)
LADDER = ("B5", "B10", "B15", "B20", "B30")                            # the five B arms in parameter order; arm A is not on the ladder
ECE_TRIGGER = 0.05                                                     # her ruling (calib DECLARATION §9): a temperature only above this


def params_for_width(h):
    """Trained parameters of ActHead(h): Linear(167->h)+ReLU, GRU(h), two Linear(h->11)."""
    return 6 * h * h + 196 * h + 22


def register():
    """Register B5 and B15 in the act arc's tables and point every reader at the five-arm ladder. Idempotent."""
    for arm, (h, cap, n) in NEW.items():
        TA.WIDTH[arm] = h
        TA.BUDGET[arm] = cap
        TA.DECLARED_PARAMS[arm] = n
    TA.ARMS = tuple(dict.fromkeys(tuple(TA.ARMS) + tuple(NEW)))
    R.ARMS = LADDER
    CA.HEADS = LADDER
    CA.REGISTERED = tuple((h, "y0", r) for h in LADDER for r in ("seen", "heard"))
    CA.READS = READS
    return LADDER


def train(argv):
    register()
    sys.argv = ["train_act.py"] + argv
    TA.main()


def read_accuracy(progress=True):
    register()
    out = R.read_accuracy(progress)
    out["ladder"] = list(LADDER)
    out["note"] = "the act arc's read_accuracy over the five B arms; arm A is not on the ladder (F-074 settled it)"
    return out


def read_fit(progress=True):
    register()
    out = CA.read_fit(progress)
    out["ruling"] = "T = 1 for every act head (calib DECLARATION §9); fits reported, not applied"
    return out


def read_reliability(progress=True):
    register()
    out = CA.read_reliability(progress)
    trig = {}
    for h in LADDER:
        for rg in ("seen", "heard"):
            e = out["summary"][h]["y0"][rg]["ece"]["T1"]
            trig[f"{h}/{rg}"] = {"ece_T1": None if e is None else e["mean"], "over_trigger": (e is not None and e["mean"] > ECE_TRIGGER)}
    out["trigger"] = {"bar": ECE_TRIGGER, "cells": trig, "any": any(v["over_trigger"] for v in trig.values())}
    return out


def marginal(points):
    """[(arm, params, value)] sorted by params -> [(from, to, d_params, d_value, d_value_per_1000)]."""
    out = []
    for (a0, p0, v0), (a1, p1, v1) in zip(points, points[1:]):
        out.append({"from": a0, "to": a1, "d_params": p1 - p0, "d_value": v1 - v0, "per_1000": (v1 - v0) / (p1 - p0) * 1000.0})
    return out


def concave(gains):
    """P33: every successive per-1,000 gain is smaller in magnitude than the one before it (ties within 1e-9 are not shrinking)."""
    mags = [abs(g["per_1000"]) for g in gains]
    return all(b < a - 1e-9 for a, b in zip(mags, mags[1:]))


def read_curve():
    register()
    acc = json.loads((READS / "accuracy.json").read_text())
    S = acc["summary"]
    cell = lambda arm, m: S[arm]["needy-tuning"]["y0"]["all"]["covered"][m]["mean"]            # noqa: E731
    params = {arm: TA.DECLARED_PARAMS[arm] for arm in LADDER}
    pts_ll = sorted([(arm, params[arm], cell(arm, "logloss")) for arm in LADDER], key=lambda t: t[1])
    pts_t1 = sorted([(arm, params[arm], cell(arm, "top1")) for arm in LADDER], key=lambda t: t[1])
    g_ll, g_t1 = marginal(pts_ll), marginal(pts_t1)
    rows = [{"arm": arm, "width": TA.WIDTH[arm], "params": params[arm], "share": round(params[arm] / TRUNK, 4),
             "top1": cell(arm, "top1"), "logloss": cell(arm, "logloss"), "macro_recall": cell(arm, "macro_recall"),
             "seen_top1": S[arm]["needy-tuning"]["y0"]["seen"]["covered"]["top1"]["mean"],
             "heard_top1": S[arm]["needy-tuning"]["y0"]["heard"]["covered"]["top1"]["mean"],
             "y10_top1": S[arm]["needy-tuning"]["y10"]["all"]["covered"]["top1"]["mean"]} for arm in LADDER]
    return {"ladder": list(LADDER), "trunk_params": TRUNK, "rows": rows, "marginal_logloss": g_ll, "marginal_top1": g_t1,
            "P33": {"concave_logloss": concave(g_ll), "concave_top1": concave(g_t1), "met": concave(g_ll)},
            "owner_call": "the Phase 2 act head: hers after this curve (DECLARATION §6); no selector here"}


def _f(v, d=3):
    return "—" if v is None else f"{v:.{d}f}"


def md(cmd, out):
    if cmd == "accuracy":
        return R.md("accuracy", out)
    if cmd in ("fit", "reliability"):
        s = CA.md(cmd, out)
        if cmd == "reliability":
            t = out["trigger"]
            s += f"\n### The 0.05 trigger at T = 1 (any over: {t['any']})\n\n| cell | ECE T = 1 | over 0.05 |\n|---|---|---|\n"
            s += "".join(f"| {k} | {_f(v['ece_T1'], 4)} | {v['over_trigger']} |\n" for k, v in t["cells"].items())
        return s
    L = ["# Act-head ladder read: the curve", "", "Needy tuning half, covered friends, y0 unless named; seed means over three heads per arm.", "",
         "| arm | width | params | share of trunk | top-1 | log-loss | macro recall | seen top-1 | heard top-1 | y10 top-1 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        L.append(f"| {r['arm']} | {r['width']} | {r['params']:,} | {r['share']:.4f} | {_f(r['top1'])} | {_f(r['logloss'])} | {_f(r['macro_recall'])} | "
                 f"{_f(r['seen_top1'])} | {_f(r['heard_top1'])} | {_f(r['y10_top1'])} |")
    for name, key in (("log-loss", "marginal_logloss"), ("top-1", "marginal_top1")):
        L += ["", f"### Marginal {name} per added parameter", "", "| step | Δ params | Δ value | per 1,000 params |", "|---|---|---|---|"]
        for g in out[key]:
            L.append(f"| {g['from']} → {g['to']} | {g['d_params']:,} | {g['d_value']:+.4f} | {g['per_1000']:+.5f} |")
    L += ["", f"P33 (log-loss gains shrink at every step): {'MET' if out['P33']['met'] else 'NOT MET'}; top-1 concave: {out['P33']['concave_top1']}.",
          "", out["owner_call"]]
    return "\n".join(L) + "\n"


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train(sys.argv[2:])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["accuracy", "fit", "reliability", "curve"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    fn = {"accuracy": lambda: read_accuracy(not a.quiet), "fit": lambda: read_fit(not a.quiet),
          "reliability": lambda: read_reliability(not a.quiet), "curve": read_curve}[a.cmd]
    out = fn()
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k not in ("tables", "detail", "manifests")}, indent=1))


if __name__ == "__main__":
    main()
