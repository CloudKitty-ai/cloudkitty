#!/usr/bin/env python3
"""Round-3 n_eff measurement (MITIGATION.md §Round 3 (1), owner-ruled
2026-10-19 "Ruled as recommended by Professor"): per-world block nulls
on every probe leg to date — zero NEW collection; the probe JSONs
persist stats, not series, so each leg's series is REGENERATED
seed-exactly (same seeds, same critic, same clone) and every world's
recorded ρ must reproduce before any null is read.

Writes artifacts/neff-measurement.json: per leg, the per-world
{observed, null_p99, n_eff, informative} plus the pooled block null
re-read with the §Round 3 ceiling label (random legs never had one).

    neff_measure_g2.py [--n-perm 1000] [--out ../artifacts/neff-measurement.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from critic_probe_g2 import (NULL_CEILING, block_null, collect,  # noqa: E402
                             spearman, world_null)

# (leg, artifact dir, recorded JSON, seed base, epsilon)
LEGS = [
    ("r1-random", "critic-g2-ext", "reprobe-random.json", 870013, 1.0),
    ("r1-eps01", "critic-g2-ext", "reprobe-eps01.json", 870016, 0.1),
    ("r1-eps03", "critic-g2-ext", "reprobe-eps03.json", 870019, 0.3),
    ("r2-random", "critic-g2-ext2", "reprobe-random.json", 870022, 1.0),
    ("r2-eps01", "critic-g2-ext2", "reprobe-eps01.json", 870025, 0.1),
    ("r2-eps03", "critic-g2-ext2", "reprobe-eps03.json", 870028, 0.3),
]
TICKS, WORLDS = 4000, 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/neff-measurement.json")
    args = ap.parse_args()

    from model_attn_v2 import EntityCriticV2
    from model_v6 import EntityPolicyV6
    from tokens_v2 import tokenize
    from train_critic_g2 import critic_arrays

    ck = torch.load(ARC / "artifacts/trunk-clone/trunk-clone.pt",
                    map_location="cpu", weights_only=True)
    clone = EntityPolicyV6(**ck["hyper"])
    clone.load_state_dict(ck["state_dict"])
    clone.eval()

    out = {"ceiling": NULL_CEILING, "n_perm": args.n_perm,
           "ticks": TICKS, "worlds": WORLDS, "legs": {}}
    for leg, adir, rec_name, base, eps in LEGS:
        rec = json.loads((ARC / "artifacts" / adir / rec_name).read_text())
        art = torch.load(ARC / "artifacts" / adir / "critic-g2-0p998.pt",
                         map_location="cpu", weights_only=True)
        model = EntityCriticV2(**art["hyper"])
        model.load_state_dict(art["state_dict"])
        model.eval()
        rollouts = collect(TICKS, WORLDS, base, eps,
                           clone if eps < 1.0 else None)
        x, y = critic_arrays(rollouts, gamma=0.998, min_future=1500)
        k, e, g, p = tokenize(x)
        with torch.no_grad():
            pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                    g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                              for i in range(0, k.shape[0], 4096)]).numpy()
        pred_raw = pred * art["target_std"] + art["target_mean"]
        keep = TICKS - 1500 + 1
        assert len(y) == keep * WORLDS

        worlds = []
        for w in range(WORLDS):
            pw, yw = pred_raw[w * keep:(w + 1) * keep], y[w * keep:(w + 1) * keep]
            rho = spearman(pw, yw)
            drec = abs(rho - rec["per_world"][w]["rho"])
            assert drec < 1e-6, \
                f"{leg} w{w}: regenerated rho {rho} != recorded " \
                f"{rec['per_world'][w]['rho']} (leg not reproduced)"
            wn = world_null(pw, yw, n_perm=args.n_perm, seed=base + w)
            worlds.append({"name": rec["per_world"][w]["name"], **wn})
        pooled = block_null(pred_raw, y, keep, WORLDS,
                            n_perm=args.n_perm, seed=base)
        if "block_null" in rec:
            assert abs(pooled["observed"] - rec["block_null"]["observed"]) \
                < 1e-6, f"{leg}: pooled observed not reproduced"
        pooled["informative"] = bool(pooled["null_p99"] <= NULL_CEILING)
        pooled["n_eff"] = float((2.33 / pooled["null_p99"]) ** 2) \
            if pooled["null_p99"] > 0 else float("inf")
        out["legs"][leg] = {"seed_base": base, "epsilon": eps,
                            "critic_dir": adir, "per_world": worlds,
                            "pooled": pooled}
        print(f"{leg}: pooled p99 {pooled['null_p99']:.3f} "
              f"n_eff {pooled['n_eff']:.0f} "
              f"informative {pooled['informative']}; per-world p99 "
              f"{[round(w['null_p99'], 3) for w in worlds]}", flush=True)

    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print("n_eff measurement done", flush=True)


if __name__ == "__main__":
    main()
