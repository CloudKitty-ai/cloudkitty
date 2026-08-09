"""BC clone v4 (exp-004 prereg §5): the two-head clone.

One trunk obs -> 256 -> 256 -> 43 (34 activity + 9 message, split by
convention); loss = two masked CEs SUMMED, legal-only smoothing eps per
head; plateau stop on the SUMMED masked val loss; per-head val top-1
reported. Split by rollout (data.py, val = rollout-03 x 15).

Checkpoints every epoch (clone-ckpt.pt) and resumes with --resume, so
long runs can be driven in bounded foreground chunks.

Run from the repo root with exp-001's venv:
  experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
    experiments/exp-004-meow-channel/trainer/train_clone_v4.py
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from bc_loss2 import two_head_loss
from data import (ACTION_GROUPS, ACTION_NAMES, MSG_NAMES, load_dataset,
                  stack_decisions)
from model import MLP

HIDDEN = [256, 256]


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
                                    label[sl], mask_msg[sl], label_msg[sl], eps)
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
    ap.add_argument("--data-root", type=Path,
                    default=Path("experiments/exp-004-meow-channel/raw/bc-v4"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone"))
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--smoothing", type=float, default=0.05)
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260809)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    ap.add_argument("--max-epochs-this-run", type=int, default=None,
                    help="chunked driving: stop after N epochs this process")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    train_r, val_r, dims = load_dataset(args.data_root, args.limit_rollouts)
    n_actions, n_msgs = dims["n_actions"], dims["n_msgs"]
    print(f"dims {dims}; rollouts {len(train_r)}/{len(val_r)}")

    tr = [torch.from_numpy(a) for a in stack_decisions(train_r)]
    va = [torch.from_numpy(a) for a in stack_decisions(val_r)]
    print(f"decisions: {tr[0].shape[0]} train / {va[0].shape[0]} val")

    model = MLP([dims["obs_dim"], *HIDDEN, n_actions + n_msgs])
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    ckpt_path = args.out_dir / "clone-ckpt.pt"
    history, best, start_epoch = [], {"loss": float("inf"), "epoch": -1,
                                      "state": None}, 1
    patience = args.patience
    if args.resume and ckpt_path.exists():
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["opt"])
        history, best, patience = ck["history"], ck["best"], ck["patience"]
        start_epoch = ck["epoch"] + 1
        torch.set_rng_state(ck["torch_rng"])
        print(f"resumed at epoch {start_epoch} "
              f"(best val loss {best['loss']:.4f} @ {best['epoch']})")

    n_train = tr[0].shape[0]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ran = 0
    finished = False
    for epoch in range(start_epoch, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n_train)
        train_loss, seen = 0.0, 0
        for i in range(0, n_train, args.batch_size):
            idx = perm[i:i + args.batch_size]
            loss, _ = two_head_loss(model(tr[0][idx]), n_actions, tr[1][idx],
                                    tr[2][idx], tr[3][idx], tr[4][idx],
                                    args.smoothing)
            opt.zero_grad()
            loss.backward()
            opt.step()
            train_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]

        model.eval()
        ev = evaluate(model, va, args.smoothing, args.batch_size,
                      n_actions, n_msgs)
        row = {"epoch": epoch, "train_loss": train_loss / seen,
               "val_loss": ev["loss"], "val_act_top1": ev["act_top1"],
               "val_msg_top1": ev["msg_top1"],
               "val_act_entropy": ev["act_entropy"],
               "val_msg_entropy": ev["msg_entropy"],
               "seconds": time.time() - t0}
        history.append(row)
        print(f"epoch {epoch:2d}  train {row['train_loss']:.4f}  "
              f"val {row['val_loss']:.4f}  act@1 {row['val_act_top1']:.4f}  "
              f"msg@1 {row['val_msg_top1']:.4f}  "
              f"H(act) {row['val_act_entropy']:.3f} H(msg) "
              f"{row['val_msg_entropy']:.3f}  ({row['seconds']:.0f}s)")

        if ev["loss"] < best["loss"] - 1e-4:
            best = {"loss": ev["loss"], "epoch": epoch,
                    "state": {k: v.clone() for k, v in
                              model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1

        torch.save({"model": model.state_dict(), "opt": opt.state_dict(),
                    "history": history, "best": best, "patience": patience,
                    "epoch": epoch, "torch_rng": torch.get_rng_state()},
                   ckpt_path)

        if patience == 0:
            print(f"plateau: summed val loss flat for {args.patience} epochs")
            finished = True
            break
        ran += 1
        if args.max_epochs_this_run and ran >= args.max_epochs_this_run:
            print(f"chunk done ({ran} epochs this run); resume to continue")
            return
    else:
        finished = True

    assert finished
    model.load_state_dict(best["state"])
    model.eval()
    ev = evaluate(model, va, args.smoothing, args.batch_size, n_actions, n_msgs)
    act_table, groups, msg_table = tables(ev)

    torch.save({"dims": model.dims, "state_dict": model.state_dict(),
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "best_epoch": best["epoch"]},
               args.out_dir / "clone.pt")
    metrics = {
        "dims": dims,
        "train_rollouts": [r.name for r in train_r],
        "val_rollouts": [r.name for r in val_r],
        "train_rows": int(tr[0].shape[0]), "val_rows": int(va[0].shape[0]),
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
        "history": history, "best_epoch": best["epoch"],
        "val_at_best": {"loss": ev["loss"], "act_loss": ev["act_loss"],
                        "msg_loss": ev["msg_loss"],
                        "act_top1": ev["act_top1"],
                        "msg_top1": ev["msg_top1"],
                        "act_entropy": ev["act_entropy"],
                        "msg_entropy": ev["msg_entropy"]},
        "per_class_activity": act_table, "groups": groups,
        "per_kind_message": msg_table,
    }
    (args.out_dir / "clone-metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n")

    print(f"\nbest epoch {best['epoch']}: val {ev['loss']:.4f}  "
          f"act@1 {ev['act_top1']:.4f}  msg@1 {ev['msg_top1']:.4f}")
    print("message head per kind:")
    for row in msg_table:
        acc = "n/a" if row["accuracy"] is None else f"{row['accuracy']:.4f}"
        print(f"  {row['name']:11s} n={row['count']:8d}  acc={acc}")
    print("activity groups:")
    for g, s in groups.items():
        acc = "n/a" if s["accuracy"] is None else f"{s['accuracy']:.4f}"
        print(f"  {g:12s} n={s['count']:8d}  acc={acc}")
    assert ev["act_entropy"] > 0.0 and ev["msg_entropy"] > 0.0, \
        "converged entropy must be > 0 on BOTH heads (prereg §11)"
    print(f"saved {args.out_dir}/clone.pt + clone-metrics.json")


if __name__ == "__main__":
    main()
