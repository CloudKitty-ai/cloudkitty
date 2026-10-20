#!/usr/bin/env python3
"""Diagnosis read 4 (RESULTS.md declaration 2026-10-19): the
remaining-horizon ramp's share of target variance, and the detrended
per-world rank. R_t = (1 - gamma^(T - t)) / (1 - gamma) is the
deterministic censoring ramp; both prediction and target are
residualized on [1, R_t] by least squares before the Spearman.
Diagnosis only — no bars.

    detrend_check_g2.py [--out ../artifacts/diag-detrend.json]
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

from critic_probe_g2 import collect, spearman  # noqa: E402

LEGS = [("random", "round3-random.json", 870031, 1.0),
        ("eps01", "round3-eps01.json", 870034, 0.1)]
TICKS, WORLDS, GAMMA = 4000, 10, 0.998


def resid(x, basis):
    coef, *_ = np.linalg.lstsq(basis, x, rcond=None)
    return x - basis @ coef


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/diag-detrend.json")
    args = ap.parse_args()

    from model_attn_v2 import EntityCriticV2
    from model_v6 import EntityPolicyV6
    from tokens_v2 import tokenize
    from train_critic_g2 import critic_arrays

    art = torch.load(ARC / "artifacts/critic-g2-ext2/critic-g2-0p998.pt",
                     map_location="cpu", weights_only=True)
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()
    ck = torch.load(ARC / "artifacts/trunk-clone/trunk-clone.pt",
                    map_location="cpu", weights_only=True)
    clone = EntityPolicyV6(**ck["hyper"])
    clone.load_state_dict(ck["state_dict"])
    clone.eval()

    keep = TICKS - 1500 + 1
    t = np.arange(keep, dtype=float)
    ramp = (1.0 - GAMMA ** (TICKS - t)) / (1.0 - GAMMA)
    basis = np.stack([np.ones(keep), ramp], axis=1)

    out = {"gamma": GAMMA, "ramp_range_raw": float(ramp.max() - ramp.min()),
           "legs": {}}
    for leg, rec_name, base, eps in LEGS:
        rec = json.loads(
            (ARC / "artifacts/critic-g2-ext2" / rec_name).read_text())
        rollouts = collect(TICKS, WORLDS, base, eps,
                           clone if eps < 1.0 else None)
        x, y = critic_arrays(rollouts, gamma=GAMMA, min_future=1500)
        k, e, g, p = tokenize(x)
        with torch.no_grad():
            pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                    g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                              for i in range(0, k.shape[0], 4096)]).numpy()
        pred_raw = pred * art["target_std"] + art["target_mean"]
        worlds = []
        for w in range(WORLDS):
            yw = np.asarray(y[w * keep:(w + 1) * keep], float)
            pw = np.asarray(pred_raw[w * keep:(w + 1) * keep], float)
            rho = spearman(pw, yw)
            assert abs(rho - rec["per_world"][w]["rho"]) < 1e-6, \
                f"{leg} w{w}: regeneration does not reproduce recorded rho"
            ry, rp = resid(yw, basis), resid(pw, basis)
            ramp_r2 = 1.0 - float(ry.var() / yw.var())
            worlds.append({
                "rho": rec["per_world"][w]["rho"],
                "ramp_r2_target": ramp_r2,
                "target_std": float(yw.std()),
                "resid_std": float(ry.std()),
                "rho_detrended": spearman(rp, ry)})
            print(f"  {leg} w{w}: rho {rho:+.3f} ramp_r2 {ramp_r2:.3f} "
                  f"std {yw.std():.1f}->{ry.std():.1f} "
                  f"rho~ {worlds[-1]['rho_detrended']:+.3f}", flush=True)
        out["legs"][leg] = {"seed_base": base, "epsilon": eps,
                            "per_world": worlds}

    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print("read 4 done", flush=True)


if __name__ == "__main__":
    main()
