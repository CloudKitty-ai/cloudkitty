"""R-2, the curves (DECLARATION §6 R-2, §7 P50 / P51; guard g8). Zero cost: recorded `metrics.jsonl` only.
Per lineage (trunk seed s1 / s2 / s4): the trunk's 1M-tick bins, then — aligned at the trunk's stop — the
continuation's bins (when it has run), the Phase 2 no-head arm's and the act15 arm's. Per bin: mean return and
anchor-KL (the trainer's own `bin_closed` values), and the bin means of `ev` and policy entropy over the update rows.
Per post-trunk run: the STEP (its first bin's return minus the trunk's last bin's), the SLOPE (least-squares return per
bin over the bins after the first), the tick and reason of its stop.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_curves.py --out reads/r2/curves.json [--md]
(A = experiments/minifriend-phase2-2026-11-06; torch is needed only to read a final's stop_reason.)
"""
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
TRUNK = EXPTS / "gen2-trunk-training-2026-10-18" / "artifacts"
P2 = EXPTS / "minifriend-phase2-2026-11-06" / "artifacts"
CONT = HERE / "artifacts"
# s1's no-head arm is the s1r rerun (deviations entry 25), as R-1 paired it
LINEAGES = {k: {"trunk": TRUNK / f"ppo-g2-trunk-s{k}", "cont": CONT / f"cont-s{k}",
                "nohead": P2 / ("p2-nohead-s1r" if k == 1 else f"p2-nohead-s{k}"), "act15": P2 / f"p2-act15-s{k}"} for k in (1, 2, 4)}
ARMS = ("cont", "nohead", "act15")


def series(run_dir):
    """The run's closed bins in order: ticks, ret, kl (the trainer's `bin_closed`), ev and entropy (bin means over
    the update rows that closed in the bin), the recorded flat flag and streak."""
    bins, acc = [], []
    for line in (run_dir / "metrics.jsonl").open():
        r = json.loads(line)
        if "kl_anchor" not in r:
            continue
        acc.append(r)
        if r.get("bin_closed"):
            b = r["bin_closed"]
            bins.append({"ticks": b["ticks"], "ret": b["ret"], "kl": b["kl"], "ev": float(np.mean([x["ev"] for x in acc])),
                         "entropy": float(np.mean([x["entropy"] for x in acc])), "flat": b["flat"], "flat_streak": r["flat_streak"]})
            acc = []
    return bins


def stop(run_dir):
    """(last training tick, stop_reason from the final) — reason None when no final exists."""
    last = None
    for line in (run_dir / "metrics.jsonl").open():
        r = json.loads(line)
        if "kl_anchor" in r:
            last = r["ticks"]
    final = run_dir / "policy-final.pt"
    if not final.exists():
        return last, None
    import torch
    return last, torch.load(final, map_location="cpu", weights_only=False).get("stop_reason")


def step(first_bins, trunk_bins):
    """The STEP: the run's FIRST closed bin's return minus the trunk's LAST closed bin's."""
    return first_bins[0]["ret"] - trunk_bins[-1]["ret"]


def slope(bins):
    """The SLOPE: least-squares return per bin over the bins after the first (None under three bins)."""
    y = [b["ret"] for b in bins[1:]]
    return float(np.polyfit(np.arange(len(y)), y, 1)[0]) if len(y) >= 2 else None


def read():
    out = {}
    for k, runs in LINEAGES.items():
        tb = series(runs["trunk"])
        t_ticks, t_reason = stop(runs["trunk"])
        row = {"trunk": {"bins": tb, "stop_ticks": t_ticks, "stop_reason": t_reason,
                         "slope_last4": float(np.polyfit(np.arange(4), [b["ret"] for b in tb[-4:]], 1)[0])}}
        for arm in ARMS:
            if not (runs[arm] / "metrics.jsonl").exists():
                row[arm] = None
                continue
            ab = series(runs[arm])
            a_ticks, a_reason = stop(runs[arm])
            row[arm] = {"run": runs[arm].name, "bins": ab, "step": step(ab, tb), "slope": slope(ab), "stop_ticks": a_ticks,
                        "stop_reason": a_reason, "kl_first_bin": ab[0]["kl"], "kl_last_bin": ab[-1]["kl"]}
        out[f"s{k}"] = row
    return out


def md(out):
    L = ["# R-2 — the curves (per-1M-bin return and anchor-KL; recorded metrics only)", "",
         "STEP = the run's first bin return minus the trunk's last bin return; SLOPE = least-squares return per bin over the bins after the first.", "",
         "| lineage | run | bins | first bin return | STEP | SLOPE / bin | last bin return | KL first / last bin | stop ticks | stop reason |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s, row in out.items():
        t = row["trunk"]
        L.append(f"| {s} | trunk | {len(t['bins'])} | {t['bins'][0]['ret']:.4f} | — | {t['slope_last4']:+.4f} (last 4 bins) | {t['bins'][-1]['ret']:.4f} | "
                 f"{t['bins'][0]['kl']:.3f} / {t['bins'][-1]['kl']:.3f} | {t['stop_ticks']:,} | {t['stop_reason']} |")
        for arm in ARMS:
            a = row[arm]
            if a is None:
                L.append(f"| {s} | {arm} | not run | — | — | — | — | — | — | — |")
                continue
            L.append(f"| {s} | {a['run']} | {len(a['bins'])} | {a['bins'][0]['ret']:.4f} | {a['step']:+.4f} | {a['slope']:+.4f} | {a['bins'][-1]['ret']:.4f} | "
                     f"{a['kl_first_bin']:.3f} / {a['kl_last_bin']:.3f} | {a['stop_ticks']:,} | {a['stop_reason']} |")
    for s, row in out.items():
        L += ["", f"## {s}: per-bin return / KL / ev / entropy", "", "| run | " + " | ".join(str(i) for i in range(1, 21)) + " |", "|---|" + "---|" * 20]
        for name in ("trunk",) + ARMS:
            a = row[name]
            if a is None:
                continue
            cells = [f"{b['ret']:.4f} / {b['kl']:.3f} / {b['ev']:.2f} / {b['entropy']:.3f}" for b in a["bins"]]
            L.append(f"| {name} | " + " | ".join(cells + [""] * (20 - len(cells))) + " |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    res = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(res))
    for s, row in res.items():
        print(s, {arm: (None if row[arm] is None else {"step": round(row[arm]["step"], 4), "slope": round(row[arm]["slope"], 4)}) for arm in ARMS})
