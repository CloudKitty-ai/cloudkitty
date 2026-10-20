#!/usr/bin/env python3
"""World-heterogeneity diagnosis (RESULTS.md declaration 2026-10-19,
owner "run it"): regenerate the round-3 random and ε0.1 legs
seed-exactly, assert every recorded per-world ρ reproduces, then emit
the three declared reads per world — outcome profile, temporal
structure, identity composition — plus across-world Spearman of
ρ_world against every scalar. Diagnosis only: no bars, no verdicts.

    diag_hetero_g2.py [--out ../artifacts/diag-hetero.json]
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
TICKS, WORLDS = 4000, 10
KITTIES, BLOCK = 5, 40
H_OFF, FLAG_OFF, ID_OFF = 6, 20, 26
N_FLAGS, N_ID = 6, 14
NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")


def check_layout(states):
    """In-run layout asserts (critic_sensitivity_g2's pattern)."""
    h = states[:, [k * BLOCK + H_OFF for k in range(KITTIES)]]
    assert np.all(h > 0) and np.all(h <= 1), "happiness out of (0,1]"
    for j in range(N_FLAGS):
        f = states[:, [k * BLOCK + FLAG_OFF + j for k in range(KITTIES)]]
        assert set(np.unique(f)) <= {0.0, 1.0}, f"flag col {j} not 0/1"


def world_reads(states, y_w, pred_w, rho_rec):
    check_layout(states)
    t = np.arange(len(y_w), dtype=float)
    h = states[:len(y_w), [k * BLOCK + H_OFF for k in range(KITTIES)]]
    flags = {NEEDS[j]: float(np.mean(
        states[:len(y_w), [k * BLOCK + FLAG_OFF + j
                           for k in range(KITTIES)]]))
        for j in range(N_FLAGS)}
    ident = [float(np.mean(
        states[:len(y_w), [k * BLOCK + ID_OFF + c for k in range(KITTIES)]]))
        for c in range(N_ID)]
    return {
        "rho": rho_rec,
        "target_mean": float(y_w.mean()), "target_std": float(y_w.std()),
        "target_min": float(y_w.min()), "target_max": float(y_w.max()),
        "pred_mean": float(pred_w.mean()), "pred_std": float(pred_w.std()),
        "occ_b45": float(np.mean(h < 0.45)),
        "occ_4570": float(np.mean((h >= 0.45) & (h < 0.70))),
        "flag_rates": flags,
        "corr_t_target": spearman(y_w, t),
        "corr_t_pred": spearman(pred_w, t),
        "identity_means": ident,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ARC / "artifacts/diag-hetero.json")
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

    out = {"groups": {"ranking": ">=0.3", "anti": "<=-0.1", "mid": "rest"},
           "legs": {}}
    for leg, rec_name, base, eps in LEGS:
        rec = json.loads(
            (ARC / "artifacts/critic-g2-ext2" / rec_name).read_text())
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
        worlds = []
        for w in range(WORLDS):
            yw = y[w * keep:(w + 1) * keep]
            pw = pred_raw[w * keep:(w + 1) * keep]
            rho = spearman(pw, yw)
            assert abs(rho - rec["per_world"][w]["rho"]) < 1e-6, \
                f"{leg} w{w}: regeneration does not reproduce recorded rho"
            r = world_reads(rollouts[w].state, yw, pw,
                            rec["per_world"][w]["rho"])
            r["group"] = ("ranking" if r["rho"] >= 0.3
                          else "anti" if r["rho"] <= -0.1 else "mid")
            worlds.append(r)
        rhos = [r["rho"] for r in worlds]
        scalars = {}
        for key in ("target_mean", "target_std", "occ_b45", "occ_4570",
                    "corr_t_target", "corr_t_pred"):
            scalars[key] = spearman(rhos, [r[key] for r in worlds])
        for nm in NEEDS:
            scalars[f"flag_{nm}"] = spearman(
                rhos, [r["flag_rates"][nm] for r in worlds])
        for c in range(N_ID):
            scalars[f"id_{c}"] = spearman(
                rhos, [r["identity_means"][c] for r in worlds])
        out["legs"][leg] = {"seed_base": base, "epsilon": eps,
                            "per_world": worlds,
                            "rho_vs_scalar": scalars}
        print(f"== {leg}: rho-vs-scalar", {k2: round(v, 3)
              for k2, v in scalars.items()
              if abs(v) > 0.5 or k2.startswith("corr")}, flush=True)
        for r in worlds:
            print(f"  {r['group']:7s} rho {r['rho']:+.3f} tmean "
                  f"{r['target_mean']:.1f} tstd {r['target_std']:.1f} "
                  f"b45 {r['occ_b45']:.4f} ct_t {r['corr_t_target']:+.2f} "
                  f"ct_p {r['corr_t_pred']:+.2f}", flush=True)

    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print("diagnosis reads done", flush=True)


if __name__ == "__main__":
    main()
