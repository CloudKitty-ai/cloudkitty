#!/usr/bin/env python3
"""exp-006 BC clones: the v4 battery clone recipe at the 225 surface.

Same recipe as train_attn_clone.py (two masked CEs summed, legal-only
smoothing eps=0.05, Adam 3e-4, batch 4096, patience-3 on summed val
loss) with the model swapped for EntityPolicyV4 (30 tokens, head 16)
and the loader swapped for data6. One invocation per clone:

  --name probe-pinned --data-root raw/v5-pinned     (price probe, cell A)
  --name probe-spread --data-root raw/v5-spread     (price probe, cell B)
  --name clone-anchor --data-root raw/anchor-playful (L-arm BC init)

Run from the repo root with the exp-006 venv.
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
sys.path.insert(1, str(EXPERIMENTS / "attn-oracle-2026-08-15"))
sys.path.insert(2, str(EXPERIMENTS / "exp-004-meow-channel" / "trainer"))

from bc_loss2 import two_head_loss  # noqa: E402
from data6 import (ACTION_GROUPS, ACTION_NAMES, MSG_NAMES,  # noqa: E402
                   load_dataset, stack_decisions)
from model_v4 import EntityPolicyV4  # noqa: E402


def evaluate(model, arrs, eps, batch_size, n_actions, n_msgs):
    obs, mask, label, mask_msg, label_msg = arrs
    tot = obs.shape[0]
    sums = {"loss": 0.0, "act_loss": 0.0, "msg_loss": 0.0,
            "act_entropy": 0.0, "msg_entropy": 0.0}
    act_counts = np.zeros(n_actions, np.int64)
    act_correct = np.zeros(n_actions, np.int64)
    msg_counts = np.zeros(n_msgs, np.int64)
    msg_correct = np.zeros(n_msgs, np.int64)
    act_hits = msg_hits = 0
    with torch.no_grad():
        for i in range(0, tot, batch_size):
            sl = slice(i, i + batch_size)
            loss, m = two_head_loss(model(obs[sl]), n_actions, mask[sl],
                                    label[sl], mask_msg[sl], label_msg[sl],
                                    eps)
            n = obs[sl].shape[0]
            sums["loss"] += loss.item() * n
            for k in ("act_loss", "msg_loss", "act_entropy", "msg_entropy"):
                sums[k] += m[k] * n
            la, lm = label[sl].numpy(), label_msg[sl].numpy()
            oka = (m["act_pred"] == label[sl]).numpy()
            okm = (m["msg_pred"] == label_msg[sl]).numpy()
            act_hits += int(oka.sum())
            msg_hits += int(okm.sum())
            np.add.at(act_counts, la, 1)
            np.add.at(act_correct, la, oka.astype(np.int64))
            np.add.at(msg_counts, lm, 1)
            np.add.at(msg_correct, lm, okm.astype(np.int64))
    out = {k: v / tot for k, v in sums.items()}
    out.update(act_top1=act_hits / tot, msg_top1=msg_hits / tot,
               act_counts=act_counts, act_correct=act_correct,
               msg_counts=msg_counts, msg_correct=msg_correct)
    return out


def tables(ev):
    act = [{"index": i, "name": n, "count": int(ev["act_counts"][i]),
            "accuracy": float(ev["act_correct"][i] / ev["act_counts"][i])
            if ev["act_counts"][i] else None}
           for i, n in enumerate(ACTION_NAMES)]
    groups = {}
    for g, idxs in ACTION_GROUPS.items():
        c = int(ev["act_counts"][list(idxs)].sum())
        k = int(ev["act_correct"][list(idxs)].sum())
        groups[g] = {"count": c, "accuracy": float(k / c) if c else None}
    msg = [{"index": i, "name": n, "count": int(ev["msg_counts"][i]),
            "accuracy": float(ev["msg_correct"][i] / ev["msg_counts"][i])
            if ev["msg_counts"][i] else None}
           for i, n in enumerate(MSG_NAMES)]
    return act, groups, msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--eps", type=float, default=0.05)
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260818)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--threads", type=int, default=None)
    args = ap.parse_args()
    out_dir = args.out_dir or (HERE.parent / "artifacts" / args.name)

    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    n_actions, n_msgs = dims["n_actions"], dims["n_msgs"]
    print(f"[{args.name}] dims {dims}; rollouts {len(train_r)} train "
          f"/ {len(val_r)} val", flush=True)

    tr = tuple(torch.from_numpy(a) for a in stack_decisions(train_r))
    va = tuple(torch.from_numpy(a) for a in stack_decisions(val_r))
    print(f"[{args.name}] {tr[0].shape[0]} train / {va[0].shape[0]} val rows",
          flush=True)

    model = EntityPolicyV4()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[{args.name}] EntityPolicyV4 params: {n_params}", flush=True)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = out_dir / "ckpt.pt"
    start, history = 1, []
    best = {"loss": float("inf"), "epoch": -1, "state": None}
    patience = args.patience
    if args.resume and ckpt_path.exists():
        ck = torch.load(ckpt_path, weights_only=False)
        model.load_state_dict(ck["state_dict"])
        opt.load_state_dict(ck["opt"])
        start, history, best = ck["epoch"] + 1, ck["history"], ck["best"]
        patience = ck["patience"]
        torch.set_rng_state(ck["rng"])
        print(f"[{args.name}] resumed at epoch {start}", flush=True)

    n = tr[0].shape[0]
    obs, mask, label, mask_msg, label_msg = tr
    for epoch in range(start, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n)
        run_loss, seen = 0.0, 0
        for i in range(0, n, args.batch_size):
            idx = perm[i:i + args.batch_size]
            loss, _ = two_head_loss(model(obs[idx]), n_actions, mask[idx],
                                    label[idx], mask_msg[idx],
                                    label_msg[idx], args.eps)
            opt.zero_grad()
            loss.backward()
            opt.step()
            run_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]

        model.eval()
        ev = evaluate(model, va, args.eps, args.batch_size, n_actions, n_msgs)
        row = {"epoch": epoch, "train_loss": run_loss / seen,
               "val_loss": ev["loss"], "act_top1": ev["act_top1"],
               "msg_top1": ev["msg_top1"], "act_entropy": ev["act_entropy"],
               "msg_entropy": ev["msg_entropy"],
               "seconds": time.time() - t0}
        history.append(row)
        print(f"[{args.name}] epoch {epoch:2d}  train {row['train_loss']:.4f}"
              f"  val {ev['loss']:.4f}  act@1 {ev['act_top1']:.4f}  "
              f"msg@1 {ev['msg_top1']:.4f}  H(act) {ev['act_entropy']:.3f}  "
              f"({row['seconds']:.0f}s)", flush=True)

        if ev["loss"] < best["loss"] - 1e-4:
            best = {"loss": ev["loss"], "epoch": epoch,
                    "state": {k: v.clone()
                              for k, v in model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1
        torch.save({"epoch": epoch, "state_dict": model.state_dict(),
                    "opt": opt.state_dict(), "history": history,
                    "best": best, "patience": patience,
                    "rng": torch.get_rng_state(), "hyper": model.hyper},
                   ckpt_path)
        if patience == 0:
            print(f"[{args.name}] plateau: no summed val loss gain for "
                  f"{args.patience} epochs", flush=True)
            break

    model.load_state_dict(best["state"])
    ev = evaluate(model, va, args.eps, args.batch_size, n_actions, n_msgs)
    act, groups, msg = tables(ev)
    torch.save({"hyper": model.hyper, "state_dict": model.state_dict(),
                "best_epoch": best["epoch"]}, out_dir / f"{args.name}.pt")
    metrics = {"params": n_params, "best_epoch": best["epoch"],
               "val": {k: ev[k] for k in ("loss", "act_loss", "msg_loss",
                                          "act_top1", "msg_top1",
                                          "act_entropy", "msg_entropy")},
               "activity_classes": act, "activity_groups": groups,
               "message_classes": msg, "history": history,
               "hyperparams": {k: str(v) if isinstance(v, Path) else v
                               for k, v in vars(args).items()}}
    (out_dir / f"{args.name}-metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n")
    print(f"[{args.name}] best epoch {best['epoch']}: val {best['loss']:.4f}"
          f", act@1 {ev['act_top1']:.4f}, msg@1 {ev['msg_top1']:.4f} "
          f"-> {args.name}.pt", flush=True)


if __name__ == "__main__":
    main()
