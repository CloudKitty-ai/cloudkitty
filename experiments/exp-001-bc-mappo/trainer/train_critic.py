"""Critic pretrain on Monte-Carlo returns (prereg §7.3, deviation 27c).

One critic per gamma in the sweep. Targets are discounted MC returns of
the BC rollouts' team reward, censored to states with >= 1,500 ticks of
realized future, normalized on TRAIN statistics (mean/std recorded — the
PPO trainer must denormalize with these exact values).

Run from the repo root:
  trainer/.venv/bin/python experiments/exp-001-bc-mappo/trainer/train_critic.py
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from data import critic_arrays, load_dataset
from model import MLP

HIDDEN = [256, 256]


def train_one(gamma, train_r, val_r, dims, args):
    x_tr, y_tr = critic_arrays(train_r, gamma, args.min_future)
    x_va, y_va = critic_arrays(val_r, gamma, args.min_future)
    mean, std = float(y_tr.mean()), float(y_tr.std())
    assert std > 0
    yn_tr = torch.from_numpy((y_tr - mean) / std)
    yn_va = torch.from_numpy((y_va - mean) / std)
    x_tr, x_va = torch.from_numpy(x_tr), torch.from_numpy(x_va)
    print(f"γ={gamma}: {x_tr.shape[0]} train / {x_va.shape[0]} val states, "
          f"target mean {mean:.2f} std {std:.2f}")

    model = MLP([dims["state_dim"], *HIDDEN, 1])
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = torch.nn.MSELoss()

    history, best = [], {"mse": float("inf"), "epoch": -1, "state": None}
    patience = args.patience
    n = x_tr.shape[0]
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n)
        tr_loss, seen = 0.0, 0
        for i in range(0, n, args.batch_size):
            idx = perm[i:i + args.batch_size]
            loss = loss_fn(model(x_tr[idx]).squeeze(-1), yn_tr[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            tr_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]

        model.eval()
        with torch.no_grad():
            pred = torch.cat([model(x_va[i:i + args.batch_size]).squeeze(-1)
                              for i in range(0, x_va.shape[0], args.batch_size)])
            val_mse = float(((pred - yn_va) ** 2).mean())
            # Explained variance on val — THE make-or-break diagnostic:
            # cooperative credit is critic-carried (F-003/F-005/F-006).
            ev = 1.0 - val_mse / float(yn_va.var())
        row = {"epoch": epoch, "train_mse": tr_loss / seen,
               "val_mse": val_mse, "val_ev": ev, "seconds": time.time() - t0}
        history.append(row)
        print(f"  epoch {epoch:2d}  train_mse {row['train_mse']:.4f}  "
              f"val_mse {val_mse:.4f}  val_EV {ev:.4f}  ({row['seconds']:.1f}s)")

        if val_mse < best["mse"] - 1e-5:
            best = {"mse": val_mse, "epoch": epoch, "ev": ev,
                    "state": {k: v.clone() for k, v in model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1
            if patience == 0:
                print(f"  plateau: no val MSE gain for {args.patience} epochs")
                break

    model.load_state_dict(best["state"])
    tag = f"{gamma}".replace("0.", "0p")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"dims": model.dims, "state_dict": model.state_dict(),
                "gamma": gamma, "target_mean": mean, "target_std": std,
                "min_future": args.min_future, "best_epoch": best["epoch"]},
               args.out_dir / f"critic-{tag}.pt")
    stats = {"gamma": gamma, "target_mean": mean, "target_std": std,
             "min_future": args.min_future,
             "train_states": int(x_tr.shape[0]), "val_states": int(x_va.shape[0]),
             "best_epoch": best["epoch"], "best_val_mse": best["mse"],
             "best_val_ev": best["ev"], "history": history,
             "hyperparams": {k: str(v) if isinstance(v, Path) else v
                             for k, v in vars(args).items()}}
    (args.out_dir / f"critic-{tag}-stats.json").write_text(
        json.dumps(stats, indent=2) + "\n")
    print(f"  best epoch {best['epoch']}: val MSE {best['mse']:.4f}, "
          f"val EV {best['ev']:.4f} -> critic-{tag}.pt")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/raw/bc-v1"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone"))
    ap.add_argument("--gammas", type=str, default="0.995,0.998")
    ap.add_argument("--min-future", type=int, default=1500)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260729)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    print(f"dims: {dims}; rollouts {len(train_r)} train / {len(val_r)} val")
    for gamma in [float(g) for g in args.gammas.split(",")]:
        train_one(gamma, train_r, val_r, dims, args)


if __name__ == "__main__":
    main()
