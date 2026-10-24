#!/usr/bin/env python3
"""Phase 1c: the structured discrete belief head (SD), trained offline on
the Phase 1 + 1b rollouts (DECLARATION.md §Head). Same samples, split,
inputs, chunking, optimiser and stopping rule as Phase 1's heads
(../minifriend-phase1-2026-10-22/train_heads.py, imported for them);
what differs is the model and the likelihood.

The belief over each of the friend's five hidden needs is a histogram
over K = 20 bins of 5 need points. Per tick, per need:

    drift    mass shifts UP by a learned per-friend rate (bins per tick;
             fractional shift, two-tap; mass at the top bin accumulates)
    relief   with probability p_rel (from the recurrent residual, read off
             the observer's view) mass shifts DOWN by a learned per-need
             relief size (bins per relieving tick; floor accumulates)
    residual the recurrent state adds a logit correction and the
             histogram is renormalised (--no-residual at prediction time
             zeroes it: the R6c residual-share read)

Likelihood: cross-entropy of the histogram against a two-hot target (the
true need's position between its two nearest bin centres), averaged over
the five needs; plus BCE of p_rel against the true relief indicator
(need fell since the previous tick; weight LAMBDA_REL); plus Phase 1's
happiness and bath terms. Natural-frequency weighting (every sample 1).

Outputs per evaluation world, Phase 1's prediction file plus two:
    pred-<set>-<seed>.npz          pred (T, 5, 5, 7): histogram MEAN on the
                                   five needs (/100), happiness, bath —
                                   Phase 1's reader reads it unchanged
    nores/pred-<set>-<seed>.npz    the same with the residual zeroed
    belief-<set>-<seed>.npz        grave (T, 5, 5, 5) float16 = mass at or
                                   over 90 per need; p_rel (T, 5, 5, 5)

    MINIFRIEND_ARC=$PWD sd_head.py --seed 1 [--smoke --out-root DIR]
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(PHASE1))
import phase1_data as D  # noqa: E402
import train_heads as T  # noqa: E402  (CHUNK, BATH_WEIGHT, PARAM_CAP, check_cap, n_params)

K = 20                                   # bins of 5 need points over [0, 100]
BIN = 100.0 / K
GRAVE_BIN = int(round(90.0 / BIN))       # 18: bins 18, 19 are [90, 100] — strata.NEED_DISTRESS
CENTRES = (torch.arange(K, dtype=torch.float32) + 0.5) * (BIN / 100.0)   # bin centres, /100
R = 16                                   # recurrent residual width
LAMBDA_REL = 0.5                         # weight of the relief-indicator BCE
N_NEEDS, N_FRIENDS = 5, D.ROSTER
OUT_ROOT = D.ARC / "results-raw" / "heads"
EPS = 1e-6
WIDTHS = (8, 16, 32)                     # §Addendum: the small candidate, the declared head, the over-cap probe


def run_name(hidden, seed, smoke=False):
    """Width 16 keeps the launch name SD-s<seed> (its runs predate the addendum); other widths SD-h<r>-s<seed>."""
    return (f"SD-s{seed}" if hidden == R else f"SD-h{hidden}-s{seed}") + ("-smoke" if smoke else "")


def inv_softplus(x):
    x = torch.as_tensor(x, dtype=torch.float32)
    return x + torch.log(-torch.expm1(-x))


def shift_matrix(s, direction):
    """Transition matrices for a fractional shift of a K-bin histogram.
    s: tensor (...,) of non-negative shifts in bins. Returns M (..., K, K)
    with new = old @ M: mass in bin i lands in bin i±n (the integer part)
    with weight 1−f and in i±(n+1) with weight f; a shift past the top
    (direction 'up') accumulates in bin K−1, past the floor ('down') in
    bin 0. Differentiable in the fractional part."""
    assert direction in ("up", "down")
    n = torch.floor(s).long()
    f = (s - n.float())[..., None, None]
    i = torch.arange(K)
    sign = 1 if direction == "up" else -1
    idx0 = (i + sign * n[..., None]).clamp(0, K - 1)            # (..., K)
    idx1 = (i + sign * (n[..., None] + 1)).clamp(0, K - 1)
    m0 = F.one_hot(idx0, K).float()                             # (..., K, K): m0[.., i, k] = [k = idx0[i]]
    m1 = F.one_hot(idx1, K).float()
    return (1.0 - f) * m0 + f * m1


def two_hot(y):
    """y (...,) in [0, 1] → (..., K): the true value's mass split between
    its two nearest bin centres so the target histogram's mean equals y
    (exact inside [centre_0, centre_{K−1}], clamped at the ends)."""
    pos = (y * K - 0.5).clamp(0.0, K - 1.0)
    lo = torch.floor(pos)
    f = pos - lo
    lo = lo.long()
    hi = (lo + 1).clamp(max=K - 1)
    t = torch.zeros(*y.shape, K, dtype=torch.float32)
    t.scatter_add_(-1, lo[..., None], (1.0 - f)[..., None])
    t.scatter_add_(-1, hi[..., None], f[..., None])
    return t


class SDHead(nn.Module):
    def __init__(self, x_dim=D.X_DIM, r=R):
        super().__init__()
        self.proj = nn.Linear(x_dim, r)
        self.gru = nn.GRU(r, r)
        self.rel = nn.Linear(r, N_NEEDS)                  # relief logits per need
        self.corr = nn.Linear(r, N_NEEDS * K)             # residual logit correction
        self.aux = nn.Linear(r + N_NEEDS, 2)              # happiness, bath (read from the state + the belief means)
        self.rate_raw = nn.Parameter(inv_softplus(torch.full((N_FRIENDS, N_NEEDS), 0.4 / BIN)))   # bins per tick
        self.relief_raw = nn.Parameter(inv_softplus(torch.full((N_NEEDS,), 2.0)))                # bins per relieving tick
        self.prior = nn.Parameter(torch.zeros(N_FRIENDS, N_NEEDS, K))

    def rates(self):
        """Learned rise rates in need points per tick (N_FRIENDS, N_NEEDS) and relief sizes in points per tick (N_NEEDS)."""
        return F.softplus(self.rate_raw) * BIN, F.softplus(self.relief_raw) * BIN

    def forward(self, x, friend, state=None, residual=True):
        """x (T, B, 167); friend (B,) long = the friend's seat index (its
        rates and prior). state = (h, b) carried between chunks."""
        Tn, Bn = x.shape[:2]
        h0, b = state if state is not None else (None, None)
        z, hn = self.gru(torch.relu(self.proj(x)), h0)                      # (T, B, r)
        p_rel = torch.sigmoid(self.rel(z))                                  # (T, B, 5)
        corr = self.corr(z).view(Tn, Bn, N_NEEDS, K)
        up = shift_matrix(F.softplus(self.rate_raw)[friend], "up")          # (B, 5, K, K)
        down = shift_matrix(F.softplus(self.relief_raw), "down")            # (5, K, K)
        if b is None:
            b = torch.softmax(self.prior[friend], -1)                       # (B, 5, K)
        out = []
        for t in range(Tn):
            bd = torch.einsum("bnk,bnkj->bnj", b, up)
            br = torch.einsum("bnk,nkj->bnj", bd, down)
            p = p_rel[t][..., None]
            b = (1.0 - p) * bd + p * br
            if residual:
                b = torch.softmax(torch.log(b + EPS) + corr[t], -1)
            out.append(b)
        belief = torch.stack(out)                                           # (T, B, 5, K)
        mean = (belief * CENTRES).sum(-1)                                   # (T, B, 5), /100
        hap_bath = self.aux(torch.cat([z, mean], -1))                       # (T, B, 2)
        return {"belief": belief, "mean": mean, "p_rel": p_rel, "hap_bath": hap_bath}, (hn, b.detach())


def sample_loss(out, y, rel, w):
    """out from forward; y (T, B, 7) /100; rel (T, B, 5) {0,1}; w (T, B).
    Weighted mean of CE5 + LAMBDA_REL·BCE_rel + mse_hap + BATH_WEIGHT·mse_bath,
    and the four terms (unweighted by their coefficients)."""
    ce5 = -(two_hot(y[..., :5]) * torch.log(out["belief"] + EPS)).sum(-1).mean(-1)          # (T, B)
    bce = F.binary_cross_entropy(out["p_rel"].clamp(EPS, 1 - EPS), rel, reduction="none").mean(-1)
    mh = (out["hap_bath"][..., 0] - y[..., D.HAP]) ** 2
    mb = (out["hap_bath"][..., 1] - y[..., D.BATH]) ** 2
    ws = w.sum()
    terms = [(t * w).sum() / ws for t in (ce5, bce, mh, mb)]
    return terms[0] + LAMBDA_REL * terms[1] + terms[2] + T.BATH_WEIGHT * terms[3], terms


def relief_indicator(y):
    """(T, 7) /100 → (T, 5) float: 1 where the need fell since the previous tick (0 at t = 0)."""
    r = np.zeros((len(y), N_NEEDS), np.float32)
    r[1:] = (y[1:, :5] < y[:-1, :5] - 1e-6)
    return r


def build(name_seeds):
    seqs = []
    for name, seed in name_seeds:
        w = D.load_world(name, seed)
        for k, j in D.pairs(w):
            x, y, _vis, _code = D.pair_arrays(w, k, j)
            seqs.append({"set": name, "x": x, "y": y, "rel": relief_indicator(y), "friend": j,
                         "w": np.ones(len(y), np.float32)})
    return seqs


def run_epoch(model, seqs, opt, rng, batch, smoke=False):
    """Phase 1's pass: sequences batched within a set (equal T); CHUNK-tick
    chunks in order with the (h, b) state carried, detached."""
    tot, tot_w = 0.0, 0.0
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
            Tn = seqs[bi[0]]["x"].shape[0]
            x = torch.from_numpy(np.stack([seqs[i]["x"] for i in bi], 1))
            y = torch.from_numpy(np.stack([seqs[i]["y"] for i in bi], 1))
            rel = torch.from_numpy(np.stack([seqs[i]["rel"] for i in bi], 1))
            w = torch.from_numpy(np.stack([seqs[i]["w"] for i in bi], 1))
            friend = torch.tensor([seqs[i]["friend"] for i in bi])
            state = None
            n_chunks = Tn // T.CHUNK if not smoke else 2
            for c in range(n_chunks):
                sl = slice(c * T.CHUNK, (c + 1) * T.CHUNK)
                xc = x[sl].float()
                if opt is not None:
                    out, state = model(xc, friend, state)
                    loss, _ = sample_loss(out, y[sl], rel[sl], w[sl])
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
                    state = (state[0].detach(), state[1])
                else:
                    with torch.no_grad():
                        out, state = model(xc, friend, state)
                        loss, _ = sample_loss(out, y[sl], rel[sl], w[sl])
                ws = float(w[sl].sum())
                tot += loss.item() * ws
                tot_w += ws
    return tot / tot_w


def predict_world(model, w, residual=True):
    """pred (T, 5, 5, 7) as Phase 1 writes it (mean /100, hap, bath), plus
    grave mass (T, 5, 5, 5) and p_rel (T, 5, 5, 5)."""
    Tn = w["ticks"]
    pred = np.full((Tn, D.ROSTER, D.ROSTER, D.Y_DIM), np.nan, np.float32)
    grave = np.full((Tn, D.ROSTER, D.ROSTER, N_NEEDS), np.nan, np.float32)
    prel = np.full((Tn, D.ROSTER, D.ROSTER, N_NEEDS), np.nan, np.float32)
    pairs = list(D.pairs(w))                                   # the 20 (observer, friend) pairs as one batch
    x = torch.from_numpy(np.stack([D.pair_arrays(w, k, j)[0] for k, j in pairs], 1))   # (T, 20, 167) f16
    friend = torch.tensor([j for _k, j in pairs])
    with torch.no_grad():
        state = None
        means, hb, gm, pr = [], [], [], []
        for c in range(0, Tn, T.CHUNK):
            out, state = model(x[c:c + T.CHUNK].float(), friend, state, residual=residual)
            means.append(out["mean"].numpy()); hb.append(out["hap_bath"].numpy())
            gm.append(out["belief"][..., GRAVE_BIN:].sum(-1).numpy()); pr.append(out["p_rel"].numpy())
    means, hb, gm, pr = (np.concatenate(a) for a in (means, hb, gm, pr))
    for i, (k, j) in enumerate(pairs):
        pred[:, k, j, :5] = means[:, i]
        pred[:, k, j, 5:] = hb[:, i]
        grave[:, k, j] = gm[:, i]
        prel[:, k, j] = pr[:, i]
    return pred, grave, prel


def configure(a):
    """The head, its run name and its cap record from the parsed arguments;
    the cap rule applies (an over-cap width trains only with --over-cap)."""
    model = SDHead(r=a.hidden)
    n = T.n_params(model)
    over = T.check_cap(n, a.over_cap)
    return run_name(a.hidden, a.seed, a.smoke), model, {"params": n, "param_cap": T.PARAM_CAP, "over_cap": over, "hidden": a.hidden}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--hidden", type=int, default=R, help="recurrent width r (§Addendum: 8 / 16 / 32)")
    ap.add_argument("--over-cap", action="store_true", help="declared over-cap probe (width 32)")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-root", type=Path, default=OUT_ROOT)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    name, model, cfg = configure(a)
    h = a.hidden
    out = a.out_root / name
    (out / "nores").mkdir(parents=True, exist_ok=True)

    roles = D.roles()
    train = [(n, s) for n, r in roles.items() for s in r["train"]]
    val = [(n, s) for n, r in roles.items() for s in r["val"]]
    ev = [(n, s) for n, r in roles.items() for s in r["eval"]]
    assert not (set(train) & set(ev)) and not (set(val) & set(ev)) and not (set(train) & set(val))

    manifest = {"head": "SD", "seed": a.seed, **cfg,
                "arch": f"Linear(167->{h})+ReLU, GRU({h}); histogram filter K={K} (drift per friend x need, relief per need, "
                        f"p_rel Linear({h}->5), residual Linear({h}->{N_NEEDS * K}), prior per friend x need); aux Linear({h + N_NEEDS}->2)",
                "K": K, "bin_points": BIN, "grave_bin": GRAVE_BIN, "chunk": T.CHUNK,
                "loss": f"CE5(two-hot) + {LAMBDA_REL}*BCE_rel + mse_hap + {T.BATH_WEIGHT}*mse_bath", "lambda_rel": LAMBDA_REL,
                "bath_weight": T.BATH_WEIGHT, "lr": a.lr, "batch_sequences": a.batch, "patience": a.patience, "epoch_cap": a.epochs,
                "margin": 1e-4, "roles": roles, "weights_used": False, "dr_weights_GRAVE_ADJACENT_COMMON": [1.0, 1.0, 1.0],
                "torch": torch.__version__, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "smoke": a.smoke}
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"[{name}] params {cfg['params']} (cap {T.PARAM_CAP}{'; OVER-CAP PROBE' if cfg['over_cap'] else ''}); "
          f"train {len(train)} / val {len(val)} / eval {len(ev)} worlds", flush=True)

    t0 = time.time()
    tr_seqs = build(train)
    va_seqs = build(val)
    print(f"[{name}] {len(tr_seqs)} train / {len(va_seqs)} val sequences loaded ({time.time() - t0:.0f}s)", flush=True)

    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    best = {"loss": float("inf"), "epoch": -1, "state": None}
    patience = a.patience
    hist = out / "metrics.jsonl"
    hist.write_text("")
    for epoch in range(1, (2 if a.smoke else a.epochs) + 1):
        t1 = time.time()
        model.train()
        tr = run_epoch(model, tr_seqs, opt, rng, a.batch, a.smoke)
        model.eval()
        va = run_epoch(model, va_seqs, None, rng, a.batch, a.smoke)
        rates, relief = model.rates()
        row = {"epoch": epoch, "train_loss": tr, "val_loss": va, "seconds": time.time() - t1,
               "rates_points_per_tick": rates.tolist(), "relief_points_per_tick": relief.tolist()}
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
    torch.save({"state_dict": model.state_dict(), "best_epoch": best["epoch"], "best_val": best["loss"],
                "manifest": manifest}, out / "head-best.pt")
    for n, s in (ev if not a.smoke else ev[:1]):
        w = D.load_world(n, s)
        pred, grave, prel = predict_world(model, w)
        np.savez_compressed(out / f"pred-{n}-{s}.npz", pred=pred)
        np.savez_compressed(out / f"belief-{n}-{s}.npz", grave=grave.astype(np.float16), p_rel=prel.astype(np.float16))
        pred_nr, _g, _p = predict_world(model, w, residual=False)
        np.savez_compressed(out / "nores" / f"pred-{n}-{s}.npz", pred=pred_nr)
    rates, relief = model.rates()
    done = {"best_epoch": best["epoch"], "best_val": best["loss"], "epochs_run": epoch,
            "rates_points_per_tick": rates.tolist(), "relief_points_per_tick": relief.tolist(),
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head_sha256": hashlib.sha256((out / "head-best.pt").read_bytes()).hexdigest()}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done: best epoch {best['epoch']} val {best['loss']:.6f}; predictions for {len(ev)} eval worlds", flush=True)


if __name__ == "__main__":
    main()
