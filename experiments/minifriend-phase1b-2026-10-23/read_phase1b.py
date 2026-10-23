#!/usr/bin/env python3
"""Phase 1b reads R1b–R6b (DECLARATION.md §Reads; descriptive). Runs the
Phase 1 reader (../minifriend-phase1-2026-10-22/read_phase1.py, every
Phase 1 cell, pin and baseline unchanged) once per head WIDTH and per
evaluation GROUP — P = the per-cat grave worlds P1..P5, G = Phase 1's
all-grave worlds — then adds the size and group contrasts. Nothing here
gates.

    MINIFRIEND_ARC=$PWD read_phase1b.py --out phase1b-read.json --md

Contrasts (all on the pooled cells over covered friends, mean over the
three seeds, SD between seeds):
  size ratio    r(h) = loss(h) / loss(24) per head × class × version,
                SD by first-order propagation, r · sqrt(cv_h² + cv_24²);
                a size effect is READ when |r − 1| exceeds that SD
                (descriptive; no bar)
  group ratio   q(h, head) = GRAVE loss on G / GRAVE loss on P, same SD
                rule (the all-grave confound: q > 1 + SD means the
                all-grave worlds were HARDER, q < 1 − SD easier)
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(PHASE1))
import read_phase1 as R  # noqa: E402

SIZES = (12, 24, 48)
REF = 24
HEADS = ("NF", "DR")
GROUPS = {"P": ["P1", "P2", "P3", "P4", "P5"], "G": ["G"]}
CLASSES = ("GRAVE", "DA", "COMMON")


def runs_for(h):
    return [(head, f"{head}-h{h}-s{s}") for head in HEADS for s in (1, 2, 3)]


def ratio(num, den):
    """num/den as {mean, sd} dicts → {ratio, sd, read} (first-order SD); None if either is uncovered."""
    if num is None or den is None or not den["mean"]:
        return None
    r = num["mean"] / den["mean"]
    sn, sdn = (num["sd"] or 0.0), (den["sd"] or 0.0)        # a single-seed cell has sd None → 0
    sd = r * math.sqrt((sn / num["mean"]) ** 2 + (sdn / den["mean"]) ** 2) if num["mean"] else 0.0
    return {"ratio": r, "sd": sd, "read": abs(r - 1.0) > sd}


def pooled(read, head, v, cls, field="mse5"):
    return read["heads"][head][field][v][cls]["pooled"]


def size_effect(reads_by_size, group):
    """R2b: per head × version × class, loss per width and its ratio to REF."""
    out = {}
    for head in HEADS:
        out[head] = {}
        for v in R.VERSIONS:
            out[head][v] = {}
            for cls in CLASSES:
                cells = {h: pooled(reads_by_size[h][group], head, v, cls) for h in reads_by_size}
                out[head][v][cls] = {"loss": cells,
                                     "ratio_to_ref": {h: ratio(cells[h], cells[REF]) for h in cells if h != REF}}
    return out


def group_contrast(reads_by_size, a="G", b="P", cls="GRAVE"):
    """R5b: per width × head × version, GRAVE loss on group a over group b."""
    return {h: {head: {v: ratio(pooled(reads_by_size[h][a], head, v, cls), pooled(reads_by_size[h][b], head, v, cls))
                       for v in R.VERSIONS} for head in HEADS} for h in reads_by_size}


def read_all(runs_by_size, groups=GROUPS):
    reads = {h: {g: R.read(runs, sets) for g, sets in groups.items()} for h, runs in runs_by_size.items()}
    out = {"sizes": sorted(reads), "ref": REF, "groups": groups, "reads": reads,
           "R2b_size_effect": {g: size_effect(reads, g) for g in groups},
           "R3b_dissolution": {h: {g: reads[h][g]["R2"] for g in groups} for h in reads},
           "R4b_ostrich": {h: {g: reads[h][g]["R4"] for g in groups} for h in reads},
           "R6b_runs": {h: reads[h][next(iter(groups))]["runs"] for h in reads}}
    if "G" in groups and "P" in groups:
        out["R5b_group_contrast"] = group_contrast(reads)
    return out


def fmt(m, d=2):
    if m is None:
        return "—"
    if isinstance(m, dict) and "mean" in m:
        return f"{m['mean']:.{d}f}" + (f" ± {m['sd']:.{d}f}" if m.get("sd") is not None else "")
    return f"{m:.{d}f}"


def fmt_r(r):
    return "—" if r is None else f"{r['ratio']:.3f} ± {r['sd']:.3f}" + (" READ" if r["read"] else "")


def md(out):
    L = ["## Phase 1b read (derived columns)"]
    for g in out["groups"]:
        L.append(f"\n### R1b/R2b pooled mind-visible loss by width, group {g} ({', '.join(out['groups'][g])} eval worlds)")
        L.append("| head | class | " + " | ".join(f"w{h}" for h in out["sizes"]) + " | " + " | ".join(f"r({h}/{out['ref']})" for h in out["sizes"] if h != out["ref"]) + " |")
        L.append("|---|---|" + "---|" * (2 * len(out["sizes"]) - 1))
        se = out["R2b_size_effect"][g]
        for head in HEADS:
            for cls in CLASSES:
                row = se[head]["visible"][cls]
                L.append(f"| {head} | {cls} | " + " | ".join(fmt(row["loss"][h]) for h in out["sizes"]) + " | "
                         + " | ".join(fmt_r(row["ratio_to_ref"][h]) for h in out["sizes"] if h != out["ref"]) + " |")
        cov = out["reads"][out["sizes"][0]][g]["coverage"]["visible"]["GRAVE"]
        L.append("coverage GRAVE mind-visible: " + ", ".join(f"{f} {n}" for f, n in cov.items()))
        if g != "P":
            continue
        r0 = out["reads"][out["sizes"][0]][g]
        L.append(f"\n#### group {g}: samples, worlds, coverage")
        L.append(f"n_samples {r0['n_samples']}; eval worlds {r0['eval_worlds']}")
        for v in R.VERSIONS:
            L.append(f"coverage {v}: " + "; ".join(f"{cls} " + ", ".join(f"{f} {n}" for f, n in r0["coverage"][v][cls].items()) for cls in CLASSES))
        for h in out["sizes"]:
            rd = out["reads"][h][g]
            for v in R.VERSIONS:
                L.append(f"\n#### R1b w{h} {v}: MSE on the five hidden needs per friend (mean ± SD over seeds)")
                L.append("| friend | " + " | ".join(f"{head} {cls}" for head in HEADS for cls in ("COMMON", "DA", "GRAVE")) + " |")
                L.append("|---|" + "---|" * 6)
                for f in list(cov) + ["pooled"]:
                    L.append(f"| {f} | " + " | ".join(fmt(rd["heads"][head]["mse5"][v][cls].get(f)) for head in HEADS for cls in ("COMMON", "DA", "GRAVE")) + " |")
            d = out["R3b_dissolution"][h][g]
            if d and d.get("readable"):
                L.append(f"\n#### R3b w{h}: floor {d['floor_dr_grave']:.2f}, NF pooled {d['nf_grave']:.2f}, ratio {d['ratio']:.3f}, pooled_ok {d['pooled_ok']}, friends_ok {d['friends_ok']} → dissolves {d['dissolves']}")
                L.append("| friend | NF grave | DR grave | excess over 1.10 × DR | NF SD | clause |")
                L.append("|---|---|---|---|---|---|")
                for f, pf in d["per_friend"].items():
                    L.append(f"| {f} | {pf['nf']:.2f} | {pf['dr']:.2f} | {pf['excess']:+.2f} | {pf['nf_sd']:.2f} | {'ok' if pf['ok'] else 'EXCEEDS'} |"
                             if pf.get("covered") else f"| {f} | insufficient | insufficient | — | — | not read |")
            else:
                L.append(f"\n#### R3b w{h}: unreadable ({(d or {}).get('reason', 'no read')})")
            for v in R.VERSIONS:
                L.append(f"\n#### R4b w{h} {v}: bias (pred − true, need points) grave / common / gap, SIG = signature")
                L.append("| friend | NF | DR |")
                L.append("|---|---|---|")
                for f in list(cov) + ["pooled"]:
                    cells = []
                    for head in HEADS:
                        o = out["R4b_ostrich"][h][g][head][v].get(f)
                        cells.append("insufficient" if not o or not o.get("covered", True) else
                                     f"{o['grave_bias']:+.2f} / {o['common_bias']:+.2f} / {o['gap']:+.2f}" + (" SIG" if o["signature"] else ""))
                    L.append(f"| {f} | " + " | ".join(cells) + " |")
        b = r0["baselines"]
        L.append(f"\n#### R1b baselines on group {g} (pooled, mind-visible / all-states; training-split statistics, width-independent)")
        for cls in ("COMMON", "DA", "GRAVE"):
            L.append(f"{cls}: marginal {fmt(b['marginal']['mse5']['visible'][cls]['pooled'])} / {fmt(b['marginal']['mse5']['all'][cls]['pooled'])}; "
                     f"proxy {fmt(b['persistence']['mse5']['visible'][cls]['pooled'])} / {fmt(b['persistence']['mse5']['all'][cls]['pooled'])}")
    if "R5b_group_contrast" in out:
        L.append("\n### R5b GRAVE loss, G over P (mind-visible)")
        for h in out["sizes"]:
            L.append(f"w{h}: " + ", ".join(f"{head} {fmt_r(out['R5b_group_contrast'][h][head]['visible'])}" for head in HEADS))
    L.append("\n### R6b runs")
    for h in out["sizes"]:
        L.append(f"w{h}: " + "; ".join(f"{r} params {d['params']} best {d['best_epoch']}/{d['epochs_run']}" for r, d in out["R6b_runs"][h].items()))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1b-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read_all({h: runs_for(h) for h in SIZES})
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)      # stdout under --md is the markdown alone (the Read fence redirects it)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
