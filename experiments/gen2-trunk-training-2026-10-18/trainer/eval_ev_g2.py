#!/usr/bin/env python3
"""Val-EV evaluator (MITIGATION.md §Round 4 (3)): computes a critic
checkpoint's explained variance on the ORIGINAL full-100 val split at
an arbitrary censoring floor. Used once to re-derive the no-regression
baseline (round-0 critic at min_future 3500) and for every round-4
no-regression read. Raw-space EV = 1 − MSE/var, affine-invariant, so
it equals the train-time normalized EV at matched censoring.

    eval_ev_g2.py --critic <ckpt> --min-future 3500 [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data_g2 import load_dataset  # noqa: E402
from model_attn_v2 import EntityCriticV2  # noqa: E402
from tokens_v2 import tokenize  # noqa: E402
from train_critic_g2 import critic_arrays  # noqa: E402

ROOT = HERE.parents[1] / "gen2-collection-driver-2026-10-14/results-raw"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--critic", type=Path, required=True)
    ap.add_argument("--min-future", type=int, required=True)
    ap.add_argument("--data-root", type=Path, default=ROOT / "full-100")
    ap.add_argument("--consent-rows", type=Path,
                    default=ROOT / "consent-rows-full-100.json")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    _train, val_r, _dims = load_dataset(args.data_root, args.consent_rows)
    x, y = critic_arrays(val_r, gamma=0.998, min_future=args.min_future)
    art = torch.load(args.critic, map_location="cpu", weights_only=True)
    assert art["gamma"] == 0.998
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()
    k, e, g, p = tokenize(x)
    with torch.no_grad():
        pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                          for i in range(0, k.shape[0], 4096)]).numpy()
    pred_raw = pred * art["target_std"] + art["target_mean"]
    ev = 1.0 - float(((pred_raw - y) ** 2).mean() / y.var())
    out = {"critic": str(args.critic), "min_future": args.min_future,
           "val_states": int(len(y)), "val_ev": ev,
           "trained_min_future": art["min_future"]}
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
