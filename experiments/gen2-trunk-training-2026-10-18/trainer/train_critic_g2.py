#!/usr/bin/env python3
"""Gen 2 critic pretrain: the attn-critic recipe on the trunk corpus
(frozen prereg §5: γ = 0.998 carried verbatim; CTDE declared — the
critic is training-only, the deployed behavior API never sees the
global state).

train_critic6's recipe (exp-002 censored MC returns, min_future 1500,
full realized future, normalized targets with mean/std saved for the
PPO loop, plateau patience 5) at the v2 surface: EntityCriticV2 +
tokens_v2 (state 237, kitty blocks 40), the data_g2 loader (same val
split the clone uses). Gen 2 trains on the served roster only, so
states are 237 wide with no padding; the trunk critic sees every
seat's identity dials (spec 058 FR-009).

  .venv/bin/python train_critic_g2.py --data-root <collection dir> \
      --consent-rows <consent_rows.py JSON> \
      [--extension-manifest <extension-manifest.json>] \
      [--extension-dirs <dir> ...]

(The consent swap moves activity labels only; the critic reads states
and rewards. The loader still takes the JSON so its integrity asserts
run once, identically, for every consumer of the corpus.)

EXTENSION (MITIGATION.md, deviations entry 2): --extension-manifest
adds the rung (i) harvest rollouts (the manifest's included entries,
re-verified by sha256 at load) and --extension-dirs adds collection
dirs holding config-*-rollout-* bundles (the degradation suite).
Extension data is TRAIN-ONLY — states and rewards, no labels — and
the val split stays the ORIGINAL corpus val rollouts, so the
acceptance no-regression band reads the same quantity before and
after the mix.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data_g2 import load_dataset  # noqa: E402
from model_attn_v2 import EntityCriticV2  # noqa: E402
from tokens_v2 import STATE_DIM, tokenize  # noqa: E402


def load_extension(manifest: Path | None, dirs):
    """Extension rollouts as (name, state, reward) rows, train-only."""
    exp = HERE.parents[1]
    rows = []
    if manifest is not None:
        man = json.loads(manifest.read_text())
        for r in man["rollouts"]:
            if not r["included"]:
                continue
            d = exp / r["path"]
            state = np.load(d / "state.npy", mmap_mode="r")
            digest = hashlib.sha256(
                np.ascontiguousarray(state)).hexdigest()
            assert digest == r["sha256"], \
                f"{r['path']}: harvest rollout changed since assembly"
            rows.append(SimpleNamespace(
                name=f"ext:{r['path']}", state=state,
                reward=np.asarray(np.load(d / "reward.npy"), np.float32)))
    for root in dirs or ():
        found = sorted(Path(root).glob("**/config-*-rollout-*"))
        assert found, f"no rollout dirs under {root}"
        for d in found:
            rows.append(SimpleNamespace(
                name=f"ext:{d}", state=np.load(d / "state.npy",
                                               mmap_mode="r"),
                reward=np.asarray(np.load(d / "reward.npy"), np.float32)))
    for r in rows:
        assert r.state.shape[1] == STATE_DIM, (r.name, r.state.shape)
        assert r.state.shape[0] == r.reward.shape[0], r.name
    return rows


def critic_arrays(rollouts, gamma: float, min_future: int = 1500):
    """(states, MC returns), censored per exp-001 deviation 27c: keep
    only states with >= min_future realized ticks; the return sums the
    FULL realized future."""
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
        assert r.state.shape[1] == STATE_DIM, (r.name, r.state.shape)
        xs.append(np.asarray(r.state[:keep], dtype=np.float32))
        ys.append(g[:keep].astype(np.float32))
    return np.concatenate(xs), np.concatenate(ys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--consent-rows", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path,
                    default=HERE.parent / "artifacts/critic-g2")
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--min-future", type=int, default=1500)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261018)
    ap.add_argument("--limit-rollouts", type=int, default=None)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--extension-manifest", type=Path, default=None)
    ap.add_argument("--extension-dirs", type=Path, nargs="*", default=None)
    args = ap.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_r, val_r, dims = load_dataset(args.data_root, args.consent_rows,
                                        args.limit_rollouts)
    ext = load_extension(args.extension_manifest, args.extension_dirs)
    train_r = list(train_r) + ext
    print(f"dims: {dims}; rollouts {len(train_r)} train "
          f"({len(ext)} extension, train-only) / {len(val_r)} val",
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

    model = EntityCriticV2()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"EntityCriticV2 params: {n_params}", flush=True)
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
               args.out_dir / f"critic-g2-{tag}.pt")
    stats = {"gamma": args.gamma, "target_mean": mean, "target_std": std,
             "min_future": args.min_future, "params": n_params,
             "train_states": int(k_tr.shape[0]),
             "extension_rollouts": len(ext),
             "val_states": int(k_va.shape[0]),
             "best_epoch": best["epoch"], "best_val_mse": best["mse"],
             "best_val_ev": best["ev"], "history": history,
             "hyperparams": {k: str(v) if isinstance(v, Path) else v
                             for k, v in vars(args).items()}}
    (args.out_dir / f"critic-g2-{tag}-stats.json").write_text(
        json.dumps(stats, indent=2) + "\n")
    print(f"  best epoch {best['epoch']}: val MSE {best['mse']:.4f}, "
          f"val EV {best['ev']:.4f} -> critic-g2-{tag}.pt", flush=True)


if __name__ == "__main__":
    main()
