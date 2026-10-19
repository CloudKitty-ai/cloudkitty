#!/usr/bin/env python3
"""Critic feature-sensitivity read (investigation read 1 on the failed
#365 probe; Professor advisory 2026-10-18, owner "Run the investigation
reads").

Question: do the welfare features bind at all? Degrade distress /
happiness / needs on REAL corpus val states and read the prediction
delta. Insensitive (deltas tiny against the corpus-to-probe return gap
of ~174 raw units) = the features never bound — cause (a) confirmed,
(c) dissolved. Sensitive = the critic reads welfare and mis-ranks for
another reason.

    critic_sensitivity_g2.py --data-root ... --consent-rows ...
        [--sample 20000] [--seed 20261018] [--limit-rollouts N] [--out F]

Global-state v2 kitty block (global_state.rs; tokens_v2 docstring):
needs /100 at 0..5, happiness /100 at 6, distress flags 0/1 at 20..25,
identity at 26..39; 5 kitties x 40, elements + globals after 200.
Perturbations (applied to every kitty block): distress flags -> 1;
needs -> 0.20 (well under the distress lines); happiness -> 0.20; all
three combined. The layout is asserted in-run on the raw sample
(distress columns strictly 0/1, needs+happiness in [0,1], happiness
nonzero on live rows) so a shifted offset fails loudly, never reads
the wrong column silently. Run from the repo root, exp-006 venv.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
sys.path.insert(0, str(HERE))

from data_g2 import load_dataset  # noqa: E402
from model_attn_v2 import EntityCriticV2  # noqa: E402
from tokens_v2 import KITTY_F, N_KITTY, STATE_DIM, tokenize  # noqa: E402

CRITIC = ARC / "artifacts/critic-g2/critic-g2-0p998.pt"
NEEDS = np.arange(0, 6)
HAPPY = np.array([6])
DISTRESS = np.arange(20, 26)


def kitty_cols(offsets):
    """The flat state columns for per-kitty offsets, all 5 blocks."""
    return np.concatenate([k * KITTY_F + np.asarray(offsets)
                           for k in range(N_KITTY)])


def check_layout(states):
    """Assert the documented block layout on raw data before perturbing."""
    d = states[:, kitty_cols(DISTRESS)]
    assert np.isin(d, (0.0, 1.0)).all(), "distress columns are not 0/1"
    nh = states[:, kitty_cols(np.concatenate([NEEDS, HAPPY]))]
    assert (nh >= 0.0).all() and (nh <= 1.0).all(), \
        "needs/happiness outside [0,1]"
    assert (states[:, kitty_cols(HAPPY)] > 0.0).all(), \
        "a live kitty has zero happiness"


def perturbed(base, cols, value):
    out = base.copy()
    out[:, cols] = value
    return out


def predict(model, states, mean, std):
    k, e, g, p = tokenize(states)
    with torch.no_grad():
        pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                          for i in range(0, k.shape[0], 4096)]).numpy()
    return pred * std + mean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--consent-rows", type=Path, required=True)
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261018)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    _train, val, _dims = load_dataset(args.data_root, args.consent_rows,
                                      args.limit_rollouts)
    states = np.concatenate([np.asarray(r.state, dtype=np.float32)
                             for r in val])
    assert states.shape[1] == STATE_DIM, states.shape
    rng = np.random.default_rng(args.seed)
    idx = rng.choice(states.shape[0], size=min(args.sample, states.shape[0]),
                     replace=False)
    base = states[idx]
    check_layout(base)

    art = torch.load(CRITIC, map_location="cpu", weights_only=True)
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()
    mean, std = art["target_mean"], art["target_std"]

    variants = {
        "distress_on": (kitty_cols(DISTRESS), 1.0),
        "needs_floor": (kitty_cols(NEEDS), 0.20),
        "happy_floor": (kitty_cols(HAPPY), 0.20),
    }
    p0 = predict(model, base, mean, std)
    report = {"states_sampled": int(base.shape[0]),
              "val_rollouts": [r.name for r in val],
              "baseline_mean": float(p0.mean()),
              "corpus_target_mean": float(mean),
              "probe_target_mean_ref": 243.1,  # critic-probe.json
              "seed": args.seed, "variants": {}}
    combined = base
    for name, (cols, value) in variants.items():
        pert = perturbed(base, cols, value)
        changed = pert != base
        assert changed.any(), f"{name}: perturbation is a no-op"
        assert not np.delete(changed, cols, axis=1).any(), \
            f"{name}: perturbation touched unintended columns"
        d = predict(model, pert, mean, std) - p0
        report["variants"][name] = {
            "delta_mean": float(d.mean()),
            "delta_p5": float(np.percentile(d, 5)),
            "delta_p95": float(np.percentile(d, 95))}
        combined = perturbed(combined, cols, value)
    d = predict(model, combined, mean, std) - p0
    report["variants"]["all_degraded"] = {
        "delta_mean": float(d.mean()),
        "delta_p5": float(np.percentile(d, 5)),
        "delta_p95": float(np.percentile(d, 95))}

    print(json.dumps(report, indent=1))
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
