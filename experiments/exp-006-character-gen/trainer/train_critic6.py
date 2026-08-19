#!/usr/bin/env python3
"""exp-006 critic pretrain: the attn-critic recipe on dataset v5.

EntityCritic + tokenize import UNCHANGED from attn-critic-2026-08-12
(the global-state layout survived the wall: per-kitty 32 + tail 37,
padded to 197 — only raw widths vary by roster stratum). Weights
retrain because the world moved: spread traits, rosters 3/4/5, the
Here* surface. Targets are exp-002's censored MC returns (min_future
1500, full realized future), gamma 0.998, normalized with mean/std
saved for the PPO loop — the same recipe attn-critic ran, on the same
loader split the clones use (val = rollout index ending in 3).

  .venv/bin/python trainer/train_critic6.py --data-root raw/v5-spread
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(EXPERIMENTS / "attn-critic-2026-08-12"))

from data6 import load_dataset  # noqa: E402
from model_attn import EntityCritic  # noqa: E402
from ppo_env6 import PER_KITTY, TAIL, pad_states  # noqa: E402
from tokens import STATE_DIM, tokenize  # noqa: E402


def roster_of(rollout):
    roster, rem = divmod(rollout.state.shape[1] - TAIL, PER_KITTY)
    assert rem == 0 and 3 <= roster <= 5, (
        f"{rollout.name}: state width {rollout.state.shape[1]} is not a "
        f"3-5 kitty layout")
    return roster


def critic_arrays(rollouts, gamma: float, min_future: int = 1500):
    """(padded states, MC returns), censored per exp-001 deviation 27c:
    keep only states with >= min_future realized ticks; the return sums
    the FULL realized future."""
    xs, ys = [], []
    for r in rollouts:
        t_total = r.reward.shape[0]
        g = np.empty(t_total, dtype=np.float64)
        acc = 0.0
        rew = r.reward.astype(np.float64)
        for t in range(t_total - 1, -1, -1):
            acc = rew[t] + gamma * acc
            g[t] = acc
        keep = t_total - min_future + 1
        assert keep > 0, f"{r.name}: rollout shorter than min_future"
        xs.append(pad_states(r.state[:keep], roster_of(r)))
        ys.append(g[:keep].astype(np.float32))
    return np.concatenate(xs), np.concatenate(ys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=HERE.parent / "raw/v5-spread")
    ap.add_argument("--out-dir", type=Path,
                    default=HERE.parent / "artifacts/critic6")
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--min-future", type=int, default=1500)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260818)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    ap.add_argument("--threads", type=int, default=None)
    args = ap.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    print(f"dims: {dims}; rollouts {len(train_r)} train / {len(val_r)} val",
          flush=True)

    x_tr, y_tr = critic_arrays(train_r, args.gamma, args.min_future)
    x_va, y_va = critic_arrays(val_r, args.gamma, args.min_future)
    assert x_tr.shape[1] == STATE_DIM, x_tr.shape
    mean, std = float(y_tr.mean()), float(y_tr.std())
    assert std > 0
    yn_tr = torch.from_numpy((y_tr - mean) / std)
    yn_va = torch.from_numpy((y_va - mean) / std)
    k_tr, e_tr, g_tr, p_tr = tokenize(x_tr)
    k_va, e_va, g_va, p_va = tokenize(x_va)
    print(f"γ={args.gamma}: {k_tr.shape[0]} train / {k_va.shape[0]} val "
          f"states, target mean {mean:.2f} std {std:.2f}", flush=True)

    model = EntityCritic()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"EntityCritic params: {n_params}", flush=True)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = torch.nn.MSELoss()

    history, best = [], {"mse": float("inf"), "epoch": -1, "state": None}
    patience = args.patience
    n = k_tr.shape[0]
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n)
        tr_loss, seen = 0.0, 0
        for i in range(0, n, args.batch_size):
            idx = perm[i:i + args.batch_size]
            pred = model(k_tr[idx], e_tr[idx], g_tr[idx], p_tr[idx])
            loss = loss_fn(pred.squeeze(-1), yn_tr[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            tr_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]

        model.eval()
        with torch.no_grad():
            pred = torch.cat([
                model(k_va[i:i + args.batch_size],
                      e_va[i:i + args.batch_size],
                      g_va[i:i + args.batch_size],
                      p_va[i:i + args.batch_size]).squeeze(-1)
                for i in range(0, k_va.shape[0], args.batch_size)])
            val_mse = float(((pred - yn_va) ** 2).mean())
            ev = 1.0 - val_mse / float(yn_va.var())
        row = {"epoch": epoch, "train_mse": tr_loss / seen,
               "val_mse": val_mse, "val_ev": ev,
               "seconds": time.time() - t0}
        history.append(row)
        print(f"  epoch {epoch:2d}  train_mse {row['train_mse']:.4f}  "
              f"val_mse {val_mse:.4f}  val_EV {ev:.4f}  "
              f"({row['seconds']:.1f}s)", flush=True)

        if val_mse < best["mse"] - 1e-5:
            best = {"mse": val_mse, "epoch": epoch, "ev": ev,
                    "state": {k: v.clone()
                              for k, v in model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1
            if patience == 0:
                print(f"  plateau: no val MSE gain for {args.patience} "
                      f"epochs", flush=True)
                break

    model.load_state_dict(best["state"])
    tag = f"{args.gamma}".replace("0.", "0p")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"hyper": model.hyper, "state_dict": model.state_dict(),
                "gamma": args.gamma, "target_mean": mean, "target_std": std,
                "min_future": args.min_future, "best_epoch": best["epoch"]},
               args.out_dir / f"critic6-{tag}.pt")
    stats = {"gamma": args.gamma, "target_mean": mean, "target_std": std,
             "min_future": args.min_future, "params": n_params,
             "train_states": int(k_tr.shape[0]),
             "val_states": int(k_va.shape[0]),
             "best_epoch": best["epoch"], "best_val_mse": best["mse"],
             "best_val_ev": best["ev"], "history": history,
             "hyperparams": {k: str(v) if isinstance(v, Path) else v
                             for k, v in vars(args).items()}}
    (args.out_dir / f"critic6-{tag}-stats.json").write_text(
        json.dumps(stats, indent=2) + "\n")
    print(f"  best epoch {best['epoch']}: val MSE {best['mse']:.4f}, "
          f"val EV {best['ev']:.4f} -> critic6-{tag}.pt", flush=True)


if __name__ == "__main__":
    main()
