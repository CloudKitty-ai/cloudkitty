#!/usr/bin/env python3
"""Extension-ramp check (RESULTS.md declaration 2026-10-19, owner
"Agreed on both"): (1) ramp contamination of the extension TRAINING
targets by source rung — each rollout scored against its own length's
ramp curve; (2) prediction drift across the three on-disk checkpoints
on the same regenerated round-3 probe series. Diagnosis only.

    ext_ramp_check_g2.py [--out ../artifacts/ext-ramp-check.json]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
EXP = HERE.parents[1]
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(EXP / "attn-oracle-2026-08-15"))

from critic_probe_g2 import collect, spearman  # noqa: E402

GAMMA, MIN_FUTURE = 0.998, 1500
CKPTS = [("round0-noext", "critic-g2"),
         ("ext200", "critic-g2-ext"),
         ("ext290", "critic-g2-ext2")]
LEGS = [("random", 870031, 1.0), ("eps01", 870034, 0.1)]


def targets_of(rew):
    rew = np.asarray(rew, np.float64).ravel()
    g = np.empty(rew.size)
    acc = 0.0
    for t in range(rew.size - 1, -1, -1):
        acc = rew[t] + GAMMA * acc
        g[t] = acc
    keep = rew.size - MIN_FUTURE + 1
    assert keep > 0
    return g[:keep], rew.size


def ramp_stats(y, total_len):
    t = np.arange(len(y), dtype=float)
    ramp = (1.0 - GAMMA ** (total_len - t)) / (1.0 - GAMMA)
    basis = np.stack([np.ones(len(y)), ramp], axis=1)
    coef, *_ = np.linalg.lstsq(basis, y, rcond=None)
    ry = y - basis @ coef
    return (1.0 - float(ry.var() / y.var()) if y.var() > 0 else 0.0,
            spearman(y, t))


def rung_of(path_str):
    for tag in ("results-raw-extension-iter/eps01",
                "results-raw-extension-iter/eps03",
                "results-raw-extension-iter/IN-wide",
                "results-raw-extension-iter/IN-grave"):
        if tag in path_str:
            return tag.split("/")[-1]
    if "results-raw-extension/" in path_str:
        return "suite:" + path_str.split("results-raw-extension/")[1].split("/")[0]
    return "harvest"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/ext-ramp-check.json")
    args = ap.parse_args()

    # part 1: training-target contamination by rung
    rows = []
    man = json.loads((ARC / "artifacts/extension-manifest.json").read_text())
    for r in man["rollouts"]:
        if r["included"]:
            rows.append(("harvest", EXP / r["path"]))
    for root in (ARC / "results-raw-extension",
                 ARC / "results-raw-extension-iter"):
        for d in sorted(root.glob("**/config-*-rollout-*")):
            rows.append((rung_of(str(d)), d))
    agg = defaultdict(lambda: {"n": 0, "r2": [], "ct": [], "len": []})
    for rung, d in rows:
        y, total = targets_of(np.load(d / "reward.npy"))
        r2, ct = ramp_stats(y, total)
        a = agg[rung]
        a["n"] += 1
        a["r2"].append(r2)
        a["ct"].append(ct)
        a["len"].append(total)
    part1 = {}
    for rung, a in sorted(agg.items()):
        part1[rung] = {"n": a["n"],
                       "mean_len": float(np.mean(a["len"])),
                       "mean_ramp_r2": float(np.mean(a["r2"])),
                       "mean_corr_t": float(np.mean(a["ct"]))}
        print(f"  {rung:14s} n {a['n']:3d} len {np.mean(a['len']):7.0f} "
              f"ramp_r2 {np.mean(a['r2']):.3f} corr_t {np.mean(a['ct']):+.3f}",
              flush=True)

    # part 2: prediction drift across checkpoints on shared probe series
    from model_attn_v2 import EntityCriticV2
    from model_v6 import EntityPolicyV6
    from tokens_v2 import tokenize
    from train_critic_g2 import critic_arrays
    ck = torch.load(ARC / "artifacts/trunk-clone/trunk-clone.pt",
                    map_location="cpu", weights_only=True)
    clone = EntityPolicyV6(**ck["hyper"])
    clone.load_state_dict(ck["state_dict"])
    clone.eval()
    critics = {}
    for name, d in CKPTS:
        art = torch.load(ARC / f"artifacts/{d}/critic-g2-0p998.pt",
                         map_location="cpu", weights_only=True)
        m = EntityCriticV2(**art["hyper"])
        m.load_state_dict(art["state_dict"])
        m.eval()
        critics[name] = (m, art["target_std"], art["target_mean"])
    part2 = {}
    keep = 4000 - MIN_FUTURE + 1
    for leg, base, eps in LEGS:
        rollouts = collect(4000, 10, base, eps, clone if eps < 1.0 else None)
        x, _y = critic_arrays(rollouts, gamma=GAMMA, min_future=MIN_FUTURE)
        k, e, g, p = tokenize(x)
        part2[leg] = {}
        t = np.arange(keep, dtype=float)
        for name, (m, std, mean) in critics.items():
            with torch.no_grad():
                pred = torch.cat([m(k[i:i + 4096], e[i:i + 4096],
                                    g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                                  for i in range(0, k.shape[0], 4096)]).numpy()
            cts = [spearman(pred[w * keep:(w + 1) * keep], t)
                   for w in range(10)]
            part2[leg][name] = {
                "corr_t_pred": [float(c) for c in cts],
                "mean_abs": float(np.mean(np.abs(cts))),
                "mean": float(np.mean(cts))}
            print(f"  {leg} {name:13s} mean|ct_p| "
                  f"{part2[leg][name]['mean_abs']:.3f} "
                  f"mean {part2[leg][name]['mean']:+.3f}", flush=True)

    args.out.write_text(json.dumps(
        {"part1_by_rung": part1, "part2_drift": part2}, indent=1) + "\n")
    print("ext-ramp check done", flush=True)


if __name__ == "__main__":
    main()
