#!/usr/bin/env python3
"""Act predictor Phase 1 — the trainer (DECLARATION.md §4), one arm and seed per run.

    train_act.py --arm A|B10|B20|B30 --seed 1 [--threads 3] [--smoke]

Arm A: NF1e-h24-s<seed>'s Linear(167->24)+GRU(24) FROZEN, its state concatenated with the friend's 58-cell row,
Linear(82->64)+ReLU, two Linear(64->11) (y0, y10). Arms B: Linear(167->h)+ReLU, GRU(h), two Linear(h->11) at
h = 24 / 39 / 50. Loss = CE(y0) + CE(y10, masked), natural frequency; Adam 1e-3, batch 128 sequences, 500-tick
chunks with the state carried detached, early stop on the validation loss (1e-4 margin, patience 10, cap 200).
Writes results-raw/heads/<arm>-s<seed>/{run-manifest.json, metrics.jsonl, head-best.pt, done.json}.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_act as D  # noqa: E402  (pins MINIFRIEND_ARC to Phase 1e's arc before train_heads imports phase1_data)
sys.path.insert(0, str(D.P1E))
import read_1e as R1  # noqa: E402  (load_head_e: the frozen NF1e heads)

OUT_ROOT = HERE / "results-raw" / "heads"
CHUNK = 500
TRUNK_PARAMS = 84450
WIDTH = {"B10": 24, "B20": 39, "B30": 50}
BUDGET = {"B10": 0.10, "B20": 0.20, "B30": 0.30}
DECLARED_PARAMS = {"A": 6742, "B10": 8182, "B20": 16792, "B30": 24822}      # §4; guard a3
X_DIM, ROW = 167, 58
A_HIDDEN = 64
ARMS = ("A", "B10", "B20", "B30")


class ActHead(nn.Module):
    """Arm B: its own recurrent state."""
    def __init__(self, h):
        super().__init__()
        self.proj = nn.Linear(X_DIM, h)
        self.gru = nn.GRU(h, h)
        self.out0 = nn.Linear(h, D.N_ACTS)
        self.out10 = nn.Linear(h, D.N_ACTS)

    def forward(self, x, h0=None):                       # x (T, B, 167) float
        z, hn = self.gru(torch.relu(self.proj(x)), h0)
        return self.out0(z), self.out10(z), hn


class ActOnBelief(nn.Module):
    """Arm A: the frozen needs head's state z_t ++ the friend row -> MLP -> two softmax heads."""
    def __init__(self, belief, hidden=A_HIDDEN):
        super().__init__()
        self.belief = belief
        for p in self.belief.parameters():
            p.requires_grad_(False)
        self.belief.eval()
        self.fc = nn.Linear(self.belief.gru.hidden_size + ROW, hidden)
        self.out0 = nn.Linear(hidden, D.N_ACTS)
        self.out10 = nn.Linear(hidden, D.N_ACTS)

    def train(self, mode=True):
        super().train(mode)
        self.belief.eval()                                # the frozen part never leaves eval
        return self

    def forward(self, x, h0=None):
        with torch.no_grad():
            z, hn = self.belief.gru(torch.relu(self.belief.proj(x)), h0)
        u = torch.relu(self.fc(torch.cat([z, x[..., D.SELF_BLOCK:D.SELF_BLOCK + ROW]], -1)))
        return self.out0(u), self.out10(u), hn


def make_model(arm, seed):
    if arm == "A":
        belief, _probe = R1.load_head_e(seed)
        return ActOnBelief(belief)
    return ActHead(WIDTH[arm])


def n_trained(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def n_frozen(model):
    return sum(p.numel() for p in model.parameters() if not p.requires_grad)


def check_budget(arm, n):
    assert n == DECLARED_PARAMS[arm], f"{arm}: {n} trained parameters, declared {DECLARED_PARAMS[arm]}"
    if arm in BUDGET:
        assert n <= BUDGET[arm] * TRUNK_PARAMS, f"{arm} exceeds {int(BUDGET[arm] * 100)}% of the trunk"
    return n


def sample_loss(o0, o10, y):
    """Sum over samples of CE(y0) + CE(y10 where defined); returns (loss_sum, n_samples_y0)."""
    y0, y10 = y[..., 0], y[..., 1]
    l0 = F.cross_entropy(o0.reshape(-1, D.N_ACTS), y0.reshape(-1), reduction="sum")
    m = y10.reshape(-1) >= 0
    l10 = F.cross_entropy(o10.reshape(-1, D.N_ACTS)[m], y10.reshape(-1)[m], reduction="sum") if m.any() else o0.sum() * 0
    return l0 + l10, int(y0.numel())


def run_epoch(model, seqs, opt, rng, batch, smoke=False):
    """One pass (train_heads.run_epoch's shape): sequences batched within a set, 500-tick chunks in order, the
    recurrent state carried detached. Returns the mean per-sample loss."""
    tot, n_tot = 0.0, 0
    by_set = {}
    for i, s in enumerate(seqs):
        by_set.setdefault(s["set"], []).append(i)
    order = list(by_set)
    rng.shuffle(order)
    for name in order:
        idx = np.array(by_set[name])
        rng.shuffle(idx)
        for b0 in range(0, len(idx), batch):
            bi = idx[b0:b0 + batch]
            T = seqs[bi[0]]["x"].shape[0]
            x = torch.from_numpy(np.stack([seqs[i]["x"] for i in bi], 1))      # (T, B, 167) f16
            y = torch.from_numpy(np.stack([seqs[i]["y"] for i in bi], 1))      # (T, B, 2) int64
            h = None
            n_chunks = T // CHUNK if not smoke else 2
            for c in range(n_chunks):
                sl = slice(c * CHUNK, (c + 1) * CHUNK)
                xc = x[sl].float()
                if opt is not None:
                    o0, o10, h = model(xc, h)
                    loss, n = sample_loss(o0, o10, y[sl])
                    opt.zero_grad()
                    (loss / n).backward()
                    opt.step()
                    h = h.detach()
                else:
                    with torch.no_grad():
                        o0, o10, h = model(xc, h)
                        loss, n = sample_loss(o0, o10, y[sl])
                tot += loss.item()
                n_tot += n
    return tot / n_tot


def probs_from_x(model, x):
    """(T, n, 2, 11) probabilities from a stacked pair input x (T, n, 167) float16 numpy, the state carried across
    CHUNK ticks from zero at the world's start."""
    xt = torch.from_numpy(np.ascontiguousarray(x))
    T = xt.shape[0]
    out, h = [], None
    with torch.no_grad():
        for c in range(0, T, CHUNK):
            o0, o10, h = model(xt[c:min(c + CHUNK, T)].float(), h)
            out.append(torch.stack([torch.softmax(o0, -1), torch.softmax(o10, -1)], 2))
    return torch.cat(out).numpy()


def probs_world(model, w, pairs=None):
    """(T, n_pairs, 2, 11) over the world's pairs (data_act.pairs) and the pairs."""
    pairs = list(D.pairs(w)) if pairs is None else pairs
    return probs_from_x(model, np.stack([D.pair_x(w, k, j) for k, j in pairs], 1)), pairs


def run_name(arm, seed, smoke=False):
    return f"{arm}-s{seed}" + ("-smoke" if smoke else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=ARMS, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true", help="2 train / 1 val world per set, 2 chunks, 2 epochs")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    name = run_name(a.arm, a.seed, a.smoke)
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)

    train, val, _ev = D.role_lists(a.smoke)
    missing = [ws for ws in train + val if not D.world_path(*ws).exists()]
    assert not missing, f"{len(missing)} worlds missing, first {missing[:3]}"

    model = make_model(a.arm, a.seed)
    n_tr = check_budget(a.arm, n_trained(model))
    manifest = {"arm": a.arm, "seed": a.seed, "trained_params": n_tr, "frozen_params": n_frozen(model), "trunk_params": TRUNK_PARAMS,
                "share_of_trunk": round(n_tr / TRUNK_PARAMS, 4), "budget": BUDGET.get(a.arm), "width": WIDTH.get(a.arm, A_HIDDEN if a.arm == "A" else None),
                "arch": ("NF1e-h24-s%d frozen Linear(167->24)+GRU(24); Linear(82->64)+ReLU; 2x Linear(64->11)" % a.seed) if a.arm == "A"
                        else f"Linear(167->{WIDTH[a.arm]})+ReLU, GRU({WIDTH[a.arm]}), 2x Linear({WIDTH[a.arm]}->11)",
                "targets": ["applied[t]", f"applied[t+{D.H10}]"], "loss": "CE(y0) + CE(y10 masked), natural frequency", "chunk": CHUNK,
                "lr": a.lr, "batch_sequences": a.batch, "patience": a.patience, "epoch_cap": a.epochs, "margin": 1e-4,
                "split": "minifriend-phase1e-2026-11-01/split.json via data_1e", "roles": D.roles(),
                "train_worlds": len(train), "val_worlds": len(val), "torch": torch.__version__,
                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "smoke": a.smoke}
    t0 = time.time()
    tr_seqs = D.build(train)
    va_seqs = D.build(val)
    cf = D.class_freq(tr_seqs)
    manifest["class_freq_train_y0"] = cf.tolist()
    manifest["mode_train_y0"] = int(cf.argmax())
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    n_samples = sum(len(s["y"]) for s in tr_seqs)
    print(f"[{name}] trained params {n_tr} ({manifest['share_of_trunk']:.3f} of trunk); {len(tr_seqs)} train / {len(va_seqs)} val sequences, "
          f"{n_samples:,} train samples ({time.time() - t0:.0f}s); mode {D.ACT_NAMES[cf.argmax()]}", flush=True)

    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=a.lr)
    best = {"loss": float("inf"), "epoch": -1, "state": None}
    patience = a.patience
    hist = out / "metrics.jsonl"
    hist.write_text("")
    epoch = 0
    for epoch in range(1, (2 if a.smoke else a.epochs) + 1):
        t1 = time.time()
        model.train()
        tr = run_epoch(model, tr_seqs, opt, rng, a.batch, a.smoke)
        model.eval()
        va = run_epoch(model, va_seqs, None, rng, a.batch, a.smoke)
        row = {"epoch": epoch, "train_loss": tr, "val_loss": va, "seconds": time.time() - t1}
        with hist.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(f"[{name}] epoch {epoch:3d} train {tr:.5f} val {va:.5f} ({row['seconds']:.0f}s)", flush=True)
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
    torch.save({"state_dict": {k: v for k, v in model.state_dict().items() if not k.startswith("belief.")},
                "best_epoch": best["epoch"], "best_val": best["loss"], "manifest": manifest}, out / "head-best.pt")
    done = {"best_epoch": best["epoch"], "best_val": best["loss"], "epochs_run": epoch,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head_sha256": hashlib.sha256((out / "head-best.pt").read_bytes()).hexdigest()}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done: best epoch {best['epoch']} val {best['loss']:.5f} ({time.time() - t0:.0f}s)", flush=True)


def load_act(arm, seed, smoke=False):
    """The trained head of one arm and seed, frozen, eval; arm A rebuilt around NF1e-h24-s<seed>."""
    ck = torch.load(OUT_ROOT / run_name(arm, seed, smoke) / "head-best.pt", map_location="cpu", weights_only=False)
    model = make_model(arm, seed)
    model.load_state_dict(ck["state_dict"], strict=False)
    missing = [k for k in model.state_dict() if not k.startswith("belief.") and k not in ck["state_dict"]]
    assert not missing, missing
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, ck["manifest"]


if __name__ == "__main__":
    main()
