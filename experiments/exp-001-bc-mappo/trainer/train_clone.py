"""BC clone training (exp-001 Arm 1, prereg §7.2).

Masked cross-entropy to plateau on masked val top-1 accuracy; label
smoothing per §5 so entropy > 0 at convergence. Split is by rollout
(data.py). Saves clone.pt (best-epoch weights) + clone-metrics.json.

Run from the repo root:
  trainer/.venv/bin/python experiments/exp-001-bc-mappo/trainer/train_clone.py
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from bc_loss import NEG_INF, bc_loss_and_metrics
from data import ACTION_GROUPS, ACTION_NAMES, load_dataset, stack_decisions
from model import MLP

HIDDEN = [256, 256]  # prereg §4: 182 -> 256 -> 256 -> 40


def evaluate(model, obs, mask, label, eps, batch_size, n_actions):
    """Full-split metrics + per-class counts, batched, no grad."""
    losses, entropies = [], []
    correct = np.zeros(n_actions, dtype=np.int64)
    counts = np.zeros(n_actions, dtype=np.int64)
    hits = 0
    with torch.no_grad():
        for i in range(0, obs.shape[0], batch_size):
            sl = slice(i, i + batch_size)
            loss, m = bc_loss_and_metrics(model(obs[sl]), mask[sl], label[sl], eps)
            n = obs[sl].shape[0]
            losses.append(loss.item() * n)
            entropies.append(m["entropy"] * n)
            lab = label[sl].numpy()
            ok = (m["pred"] == label[sl]).numpy()
            hits += int(ok.sum())
            np.add.at(counts, lab, 1)
            np.add.at(correct, lab, ok.astype(np.int64))
    total = obs.shape[0]
    return {
        "loss": sum(losses) / total,
        "entropy": sum(entropies) / total,
        "top1": hits / total,
        "class_counts": counts,
        "class_correct": correct,
    }


def class_table(counts, correct):
    table = []
    for i, name in enumerate(ACTION_NAMES):
        table.append({
            "index": i,
            "name": name,
            "count": int(counts[i]),
            "correct": int(correct[i]),
            "accuracy": float(correct[i] / counts[i]) if counts[i] else None,
        })
    groups = {}
    for gname, idxs in ACTION_GROUPS.items():
        c = int(counts[list(idxs)].sum())
        k = int(correct[list(idxs)].sum())
        groups[gname] = {"count": c, "correct": k,
                         "accuracy": float(k / c) if c else None}
    return table, groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/raw/bc-v1"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("experiments/exp-001-bc-mappo/artifacts/clone"))
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--smoothing", type=float, default=0.05)
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260729)
    ap.add_argument("--limit-rollouts", type=int, default=None,
                    help="smoke runs: load only the first N rollout dirs")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.set_num_threads(max(1, torch.get_num_threads()))

    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    print(f"dims: {dims}")
    print(f"rollouts: {len(train_r)} train / {len(val_r)} val "
          f"(val = {[r.name for r in val_r][:3]}{'...' if len(val_r) > 3 else ''})")

    tr = [torch.from_numpy(a) for a in stack_decisions(train_r)]
    va = [torch.from_numpy(a) for a in stack_decisions(val_r)]
    tr[1], va[1] = tr[1].bool(), va[1].bool()
    print(f"decisions: {tr[0].shape[0]} train / {va[0].shape[0]} val")

    model = MLP([dims["obs_dim"], *HIDDEN, dims["n_actions"]])
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    history, best = [], {"top1": -1.0, "epoch": -1, "state": None}
    patience = args.patience
    n_train = tr[0].shape[0]
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n_train)
        train_loss, seen = 0.0, 0
        for i in range(0, n_train, args.batch_size):
            idx = perm[i:i + args.batch_size]
            loss, _ = bc_loss_and_metrics(
                model(tr[0][idx]), tr[1][idx], tr[2][idx], args.smoothing)
            opt.zero_grad()
            loss.backward()
            opt.step()
            train_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]

        model.eval()
        ev = evaluate(model, va[0], va[1], va[2], args.smoothing,
                      args.batch_size, dims["n_actions"])
        row = {"epoch": epoch, "train_loss": train_loss / seen,
               "val_loss": ev["loss"], "val_top1": ev["top1"],
               "val_entropy": ev["entropy"], "seconds": time.time() - t0}
        history.append(row)
        print(f"epoch {epoch:2d}  train_loss {row['train_loss']:.4f}  "
              f"val_loss {row['val_loss']:.4f}  val_top1 {row['val_top1']:.4f}  "
              f"val_entropy {row['val_entropy']:.4f}  ({row['seconds']:.1f}s)")

        if ev["top1"] > best["top1"] + 1e-4:
            best = {"top1": ev["top1"], "epoch": epoch,
                    "state": {k: v.clone() for k, v in model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1
            if patience == 0:
                print(f"plateau: no val top-1 gain for {args.patience} epochs")
                break

    model.load_state_dict(best["state"])
    model.eval()
    ev = evaluate(model, va[0], va[1], va[2], args.smoothing,
                  args.batch_size, dims["n_actions"])
    table, groups = class_table(ev["class_counts"], ev["class_correct"])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"dims": model.dims, "state_dict": model.state_dict(),
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "best_epoch": best["epoch"]},
               args.out_dir / "clone.pt")
    metrics = {
        "dims": dims,
        "train_rollouts": [r.name for r in train_r],
        "val_rollouts": [r.name for r in val_r],
        "train_rows": int(tr[0].shape[0]),
        "val_rows": int(va[0].shape[0]),
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
        "history": history,
        "best_epoch": best["epoch"],
        "val_at_best": {"loss": ev["loss"], "top1": ev["top1"],
                        "entropy": ev["entropy"]},
        "per_class": table,
        "groups": groups,
    }
    (args.out_dir / "clone-metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n")

    print(f"\nbest epoch {best['epoch']}: val top1 {ev['top1']:.4f}, "
          f"entropy {ev['entropy']:.4f} (must be > 0)")
    print("group accuracy:")
    for g, s in groups.items():
        acc = "n/a" if s["accuracy"] is None else f"{s['accuracy']:.4f}"
        print(f"  {g:18s} n={s['count']:8d}  acc={acc}")
    assert ev["entropy"] > 0.0, "converged entropy must be > 0 (prereg §11)"
    print(f"saved {args.out_dir}/clone.pt + clone-metrics.json")


if __name__ == "__main__":
    main()
