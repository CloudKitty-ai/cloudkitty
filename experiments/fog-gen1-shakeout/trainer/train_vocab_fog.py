#!/usr/bin/env python3
"""Fog Gen 1 vocabulary lesson, option B (owner ruled 2026-09-08, #347):
the here-words arrive late, on a trunk that never had gradient from them.

  --stage strip   stage 1: train_clone_fog's recipe on the corpus with
                  every here-word label rewritten to Silent (Silent is
                  always legal). Output = a clone that acts like slot 1's
                  and never says a here-word.
  --stage teach   stage 2: load the stage-1 clone, freeze everything but
                  `msg_head`, train the message head alone (message CE,
                  same eps / Adam / batch / plateau rule, patience 10) on
                  the here-rows, then save the whole model as the
                  `init_vocab` artifact for readout_fog.py.

"Here-rows" (`--rows`, default `legal`): rows where at least one
here-word is legal in mask_msg, so the lesson carries the source's own
silences and want-over-here choices on those rows; `said` restricts to
rows where the source said a here-word (positives only, the head then
learns nothing about when NOT to speak). Reversible assumption noted to
the owner 2026-09-08.

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
sys.path.insert(1, str(EXPERIMENTS / "exp-006-character-gen" / "trainer"))
sys.path.insert(2, str(EXPERIMENTS / "attn-oracle-2026-08-15"))
sys.path.insert(3, str(EXPERIMENTS / "exp-004-meow-channel" / "trainer"))

import data_fog  # noqa: E402
import train_clone_fog  # noqa: E402
from bc_loss2 import bc_loss_and_metrics  # noqa: E402
from data_fog import HERE_MSG, MSG_NAMES, stack_decisions  # noqa: E402
from model_v5 import EntityPolicyV5  # noqa: E402
from obs_layout_v5 import N_ACT  # noqa: E402

HERE_IDX = sorted(HERE_MSG)
SILENT = MSG_NAMES.index("silent")


def strip_here(rollouts):
    """Rewrite every here-word label to Silent, in place."""
    for r in rollouts:
        here = np.isin(r.label_msg, HERE_IDX)
        assert r.mask_msg[here, SILENT].all(), "Silent must be legal"
        r.label_msg = np.where(here, SILENT, r.label_msg)
    return rollouts


def stripped_load_dataset(root, limit_rollouts=None):
    train, val, dims = data_fog.load_dataset(root, limit_rollouts)
    return strip_here(train), strip_here(val), dims


def here_rows(arrs, rows):
    """Select the lesson rows from a stacked (obs, mask, label, mask_msg,
    label_msg) tuple."""
    mask_msg, label_msg = arrs[3], arrs[4]
    if rows == "legal":
        sel = mask_msg[:, HERE_IDX].any(1)
    elif rows == "said":
        sel = np.isin(label_msg, HERE_IDX)
    else:
        raise ValueError(rows)
    return tuple(a[sel] for a in arrs)


def freeze_but_msg_head(model):
    for name, p in model.named_parameters():
        p.requires_grad = name.startswith("msg_head.")
    return [p for p in model.parameters() if p.requires_grad]


def msg_eval(model, arrs, eps, batch):
    obs, _, _, mask_msg, label_msg = arrs
    tot, loss_sum, hits = obs.shape[0], 0.0, 0
    here = np.isin(label_msg.numpy(), HERE_IDX)
    here_hits = 0
    with torch.no_grad():
        for i in range(0, tot, batch):
            sl = slice(i, i + batch)
            logits = model(obs[sl])[:, N_ACT:]
            loss, m = bc_loss_and_metrics(logits, mask_msg[sl], label_msg[sl], eps)
            loss_sum += loss.item() * obs[sl].shape[0]
            ok = (m["pred"] == label_msg[sl]).numpy()
            hits += int(ok.sum())
            here_hits += int(ok[here[sl]].sum())
    return {"loss": loss_sum / tot, "msg_top1": hits / tot,
            "msg_top1_here": here_hits / max(int(here.sum()), 1),
            "here_rows": int(here.sum())}


def teach(args):
    out_dir = args.out_dir or (HERE.parent / "artifacts" / args.name)
    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_r, val_r, _ = data_fog.load_dataset(args.data_root, args.limit_rollouts)
    tr = here_rows(stack_decisions(train_r), args.rows)
    va = here_rows(stack_decisions(val_r), args.rows)
    tr = tuple(torch.from_numpy(a) for a in tr)
    va = tuple(torch.from_numpy(a) for a in va)
    print(f"[{args.name}] lesson rows ({args.rows}): {tr[0].shape[0]} train "
          f"/ {va[0].shape[0]} val", flush=True)

    ck = torch.load(args.init, weights_only=False)
    model = EntityPolicyV5(**ck["hyper"])
    model.load_state_dict(ck["state_dict"])
    frozen = {k: v.clone() for k, v in model.state_dict().items()
              if not k.startswith("msg_head.")}
    params = freeze_but_msg_head(model)
    print(f"[{args.name}] trainable params: {sum(p.numel() for p in params)} "
          f"(msg_head only) from {args.init}", flush=True)
    opt = torch.optim.Adam(params, lr=args.lr)

    model.eval()
    ev0 = msg_eval(model, va, args.eps, args.batch_size)
    print(f"[{args.name}] epoch   0  val {ev0['loss']:.4f}  msg@1 {ev0['msg_top1']:.4f}"
          f"  msg@1|here {ev0['msg_top1_here']:.4f}", flush=True)
    history = [{"epoch": 0, **ev0}]
    best = {"loss": ev0["loss"], "epoch": 0,
            "state": {k: v.clone() for k, v in model.state_dict().items()}}
    patience = args.patience
    n = tr[0].shape[0]
    obs, _, _, mask_msg, label_msg = tr
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        perm = torch.randperm(n)
        run_loss, seen = 0.0, 0
        for i in range(0, n, args.batch_size):
            idx = perm[i:i + args.batch_size]
            loss, _ = bc_loss_and_metrics(model(obs[idx])[:, N_ACT:],
                                          mask_msg[idx], label_msg[idx], args.eps)
            opt.zero_grad()
            loss.backward()
            opt.step()
            run_loss += loss.item() * idx.shape[0]
            seen += idx.shape[0]
        model.eval()
        ev = msg_eval(model, va, args.eps, args.batch_size)
        history.append({"epoch": epoch, "train_loss": run_loss / seen, **ev,
                        "seconds": time.time() - t0})
        print(f"[{args.name}] epoch {epoch:3d}  train {run_loss / seen:.4f}  "
              f"val {ev['loss']:.4f}  msg@1 {ev['msg_top1']:.4f}  "
              f"msg@1|here {ev['msg_top1_here']:.4f}  ({time.time() - t0:.0f}s)",
              flush=True)
        if ev["loss"] < best["loss"] - 1e-4:
            best = {"loss": ev["loss"], "epoch": epoch,
                    "state": {k: v.clone() for k, v in model.state_dict().items()}}
            patience = args.patience
        else:
            patience -= 1
        if patience == 0:
            print(f"[{args.name}] plateau: no val message loss gain for "
                  f"{args.patience} epochs", flush=True)
            break
    else:
        print(f"[{args.name}] WARNING: epoch cap {args.epochs} reached before "
              "the plateau rule fired", flush=True)

    model.load_state_dict(best["state"])
    for k, v in frozen.items():
        assert torch.equal(model.state_dict()[k], v), f"{k} moved under the freeze"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"hyper": model.hyper, "state_dict": model.state_dict(),
                "best_epoch": best["epoch"], "stage1": str(args.init),
                "lesson_rows": args.rows}, out_dir / f"{args.name}.pt")
    ev = msg_eval(model, va, args.eps, args.batch_size)
    metrics = {"stage1": str(args.init), "lesson_rows": args.rows,
               "best_epoch": best["epoch"],
               "stopped_by": "plateau" if patience == 0 else "epoch_cap",
               "val_rollouts": [r.name for r in val_r], "val": ev,
               "history": history,
               "hyperparams": {k: str(v) if isinstance(v, Path) else v
                               for k, v in vars(args).items()}}
    (out_dir / f"{args.name}-metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"[{args.name}] best epoch {best['epoch']}: val {best['loss']:.4f}, "
          f"msg@1 {ev['msg_top1']:.4f}, msg@1|here {ev['msg_top1_here']:.4f} "
          f"-> {args.name}.pt", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("strip", "teach"), required=True)
    ap.add_argument("--init", type=Path, help="teach: the stage-1 clone .pt")
    ap.add_argument("--rows", choices=("legal", "said"), default="legal")
    args, rest = ap.parse_known_args(argv)
    if args.stage == "strip":
        train_clone_fog.load_dataset = stripped_load_dataset
        sys.argv = [sys.argv[0]] + rest
        return train_clone_fog.main()
    assert args.init, "--init required for --stage teach"
    ap2 = argparse.ArgumentParser()
    ap2.add_argument("--name", required=True)
    ap2.add_argument("--data-root", type=Path, required=True)
    ap2.add_argument("--out-dir", type=Path, default=None)
    ap2.add_argument("--epochs", type=int, default=2000,
                     help="cap only; seven batches per epoch on the here-rows")
    ap2.add_argument("--batch-size", type=int, default=4096)
    ap2.add_argument("--lr", type=float, default=3e-4)
    ap2.add_argument("--eps", type=float, default=0.05)
    ap2.add_argument("--patience", type=int, default=10)
    ap2.add_argument("--seed", type=int, default=20260818)
    ap2.add_argument("--limit-rollouts", type=int, default=None)
    ap2.add_argument("--threads", type=int, default=None)
    a2 = ap2.parse_args(rest)
    a2.init, a2.rows, a2.stage = args.init, args.rows, args.stage
    teach(a2)


if __name__ == "__main__":
    main()
