#!/usr/bin/env python3
"""Phase 1e — the natural-frequency head retrained with late-history
graves in its training data (DECLARATION.md §4).

    train_1e.py --seed 1 [--threads 3] [--epochs 200 --patience 10] [--smoke]

The recipe is Phase 1's, verbatim, imported from train_heads: the
BeliefHead at width 24 (Linear(167 → 24) + ReLU, GRU(24), Linear(24 →
7); 7,807 params under the 8,445 cap), 500-tick chunks with the hidden
state carried detached, loss w · (mse5 + mse_hap + 0.1 · mse_bath)
with w = 1 (NF), Adam 1e-3, batch 128 sequences, early stop on the
validation worlds' loss (1e-4 margin, patience 10, cap 200). What
differs is the data: this arc's split (data_1e) — 1b's L / W / G / P
training worlds and the ten late-grave training sets TN1..5 / TE1..5,
validation carved per set by Phase 1's rule. Writes
results-raw/heads/NF1e-h24-s<seed>/: run-manifest.json (before the
first epoch), metrics.jsonl, head-best.pt, pred-<set>-<seed>.npz for
every 1b evaluation world (the frozen head's format: pred (T, 5, 5, 7)
[observer, friend], NaN on the diagonal), done.json.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_1e as E  # noqa: E402  (pins MINIFRIEND_ARC to this arc before train_heads imports phase1_data)
import train_heads as T  # noqa: E402

OUT_ROOT = HERE / "results-raw" / "heads"
HEAD = "NF1e"
H = 24


def run_name(seed, smoke=False):
    return f"{HEAD}-h{H}-s{seed}" + ("-smoke" if smoke else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true", help="2 train / 1 val world per set, 2 chunks, 2 epochs, one eval world")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    name = run_name(a.seed, a.smoke)
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)

    train, val, ev = E.role_lists(a.smoke)
    missing = [ws for ws in train + val + ev if not E.world_path(*ws).exists()]
    assert not missing, f"{len(missing)} worlds missing, first {missing[:3]}: collect the training set first (collect_1e.py run)"

    model = T.BeliefHead(h=H)
    np_ = T.n_params(model)
    over = T.check_cap(np_)
    roles = E.roles()
    manifest = {"head": HEAD, "seed": a.seed, "params": np_, "param_cap": T.PARAM_CAP, "over_cap": over, "hidden": H,
                "arch": f"Linear(167->{H})+ReLU, GRU({H}), Linear({H}->7)", "chunk": T.CHUNK,
                "loss": "w*(mse5 + mse_hap + BATH_WEIGHT*mse_bath)", "bath_weight": T.BATH_WEIGHT, "weights_used": False,
                "lr": a.lr, "batch_sequences": a.batch, "patience": a.patience, "epoch_cap": a.epochs, "margin": 1e-4,
                "recipe": "train_heads.py (Phase 1, gated c0360c1d) verbatim; data_1e for the worlds",
                "split": "split.json (1b's sets verbatim + TN1..5, TE1..5)", "roles": roles,
                "train_worlds": {"old": sum(1 for n, _s in train if n in E.OLD_SETS), "new": sum(1 for n, _s in train if n in E.NEW_SETS)},
                "val_worlds": {"old": sum(1 for n, _s in val if n in E.OLD_SETS), "new": sum(1 for n, _s in val if n in E.NEW_SETS)},
                "eval_worlds": len(ev), "torch": torch.__version__,
                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "smoke": a.smoke}
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"[{name}] params {np_} ≤ {T.PARAM_CAP}; train {len(train)} / val {len(val)} / eval {len(ev)} worlds "
          f"(new sets: train {manifest['train_worlds']['new']}, val {manifest['val_worlds']['new']})", flush=True)

    t0 = time.time()
    tr_seqs = E.build(train)
    va_seqs = E.build(val)
    n_tr = sum(len(s["y"]) for s in tr_seqs)
    print(f"[{name}] {len(tr_seqs)} train / {len(va_seqs)} val sequences, {n_tr:,} train samples ({time.time() - t0:.0f}s)", flush=True)

    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    best = {"loss": float("inf"), "epoch": -1, "state": None}
    patience = a.patience
    hist = out / "metrics.jsonl"
    hist.write_text("")
    epoch = 0
    for epoch in range(1, (2 if a.smoke else a.epochs) + 1):
        t1 = time.time()
        model.train()
        tr = T.run_epoch(model, tr_seqs, opt, rng, a.batch, a.smoke)
        model.eval()
        va = T.run_epoch(model, va_seqs, None, rng, a.batch, a.smoke)
        row = {"epoch": epoch, "train_loss": tr, "val_loss": va, "seconds": time.time() - t1}
        with hist.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(f"[{name}] epoch {epoch:3d} train {tr:.6f} val {va:.6f} ({row['seconds']:.0f}s)", flush=True)
        if va < best["loss"] - 1e-4:
            best = {"loss": va, "epoch": epoch, "state": {k: v.clone() for k, v in model.state_dict().items()}}
            patience = a.patience
        else:
            patience -= 1
        if patience == 0:
            print(f"[{name}] plateau: no val gain over {a.patience} epochs", flush=True)
            break
    else:
        if not a.smoke:
            print(f"[{name}] WARNING: epoch cap {a.epochs} reached before the plateau rule fired", flush=True)

    model.load_state_dict(best["state"])
    torch.save({"state_dict": model.state_dict(), "best_epoch": best["epoch"], "best_val": best["loss"], "manifest": manifest},
               out / "head-best.pt")
    for n, s in ev:
        w = E.load_world(n, s)
        assert w["observers"] == list(range(E.ROSTER)), (n, s)          # the 1b evaluation worlds: every seat an observer
        np.savez_compressed(out / f"pred-{n}-{s}.npz", pred=T.predict_world(model, w))
    done = {"best_epoch": best["epoch"], "best_val": best["loss"], "epochs_run": epoch,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head_sha256": hashlib.sha256((out / "head-best.pt").read_bytes()).hexdigest()}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done: best epoch {best['epoch']} val {best['loss']:.6f}; predictions for {len(ev)} eval worlds "
          f"({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
