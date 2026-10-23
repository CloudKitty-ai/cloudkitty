#!/usr/bin/env python3
"""Phase 1 heads (DECLARATION.md: belief-state GRU(24) ≤ 8,445 params;
NF vs DR; three seeds, the pair sharing its seed; step-4 pins).

    train_heads.py --head NF --seed 1 [--epochs 200 --patience 10]
    train_heads.py --head DR --seed 1 --smoke        # 1 epoch, 2 chunks/set
    train_heads.py --head NF --seed 1 --hidden 12    # Phase 1b size sweep: run named NF-h12-s1
    train_heads.py --head NF --seed 1 --hidden 48 --over-cap   # 22,519 params: a probe ABOVE the
                                                     # 8,445 cap, refused without the flag

Arc root: split.json, results-raw/ and the output root come from
MINIFRIEND_ARC when set (Phase 1b), else from this directory.

Model: Linear(167 → 24) → GRU(24) → Linear(24 → 7); hidden state zero
at each world's start, carried (detached) across 500-tick chunks.
Loss per sample: w · (MSE over the five hidden needs + MSE happiness +
BATH_WEIGHT · MSE bath), targets in [0, 1]; NF w = 1, DR w = the
stratum weight from phase1_data.dr_weights on the TRAIN samples. Bath
is DOWNWEIGHTED (prereg §8 item 3 "EXCLUDED/downweighted from the
estimate loss"; declaration §What the head predicts): it is fitted at
0.1 so the seventh output is reportable (R5, the pipeline-noise bound)
without driving the shared state. The first training pass (2026-10-23
03:32Z, kept under results-raw/heads-pass1/, never read) fitted it at
1.0; deviations entry 10 records the slip. Early stop: the head's
own loss on the VALIDATION worlds (carved from the train worlds),
1e-4 margin, patience 10, cap 200 epochs (the clone trainer's rule).
Adam lr 1e-3. Writes results-raw/heads/<HEAD>-s<seed>/: run-manifest.json
(declared before the first epoch), metrics.jsonl, head-best.pt, and the
evaluation worlds' predictions pred-<set>-<seed>.npz with
pred (T, 5, 5, 7) [observer, friend] (NaN on the diagonal).
"""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

import phase1_data as D

HERE = Path(__file__).resolve().parent
ARC = Path(os.environ.get("MINIFRIEND_ARC", HERE)).resolve()
OUT_ROOT = ARC / "results-raw" / "heads"
PARAM_CAP = 8445          # 10% of the trunk's 84,450 (declaration §Capacity)
CHUNK = 500
H = 24                    # the Phase 1 width; --hidden overrides it (Phase 1b)
BATH_WEIGHT = 0.1         # bath downweighted in the loss (prereg §8 item 3); the five needs and happiness at 1


class BeliefHead(nn.Module):
    def __init__(self, x_dim=D.X_DIM, h=H, y_dim=D.Y_DIM):
        super().__init__()
        self.proj = nn.Linear(x_dim, h)
        self.gru = nn.GRU(h, h)
        self.out = nn.Linear(h, y_dim)

    def forward(self, x, h0=None):          # x (T, B, 167)
        z, hn = self.gru(torch.relu(self.proj(x)), h0)
        return self.out(z), hn


def n_params(m):
    return sum(p.numel() for p in m.parameters())


def check_cap(n, over_cap=False):
    """The cap rule: a head over PARAM_CAP trains only as a declared
    over-cap probe (--over-cap; Phase 1b's 48-wide head), never silently."""
    if n > PARAM_CAP and not over_cap:
        raise SystemExit(f"{n} params exceed the cap {PARAM_CAP}; pass --over-cap for a declared probe")
    return n > PARAM_CAP


def sample_loss(pred, y, w):
    """pred, y (T, B, 7); w (T, B). Returns the weighted mean of
    (mse5 + mse_hap + BATH_WEIGHT · mse_bath) and the three weighted
    terms (the bath term unscaled)."""
    mse5 = ((pred[..., D.HIDDEN] - y[..., D.HIDDEN]) ** 2).mean(-1)
    mh = (pred[..., D.HAP] - y[..., D.HAP]) ** 2
    mb = (pred[..., D.BATH] - y[..., D.BATH]) ** 2
    ws = w.sum()
    terms = [(t * w).sum() / ws for t in (mse5, mh, mb)]
    return terms[0] + terms[1] + BATH_WEIGHT * terms[2], terms


def train_weights(train):
    """DR stratum weights from the TRAIN worlds' samples only (declaration
    guard: an evaluation world's rows never move them)."""
    return D.dr_weights([D.load_world(n, s)["codes"] for n, s in train])


def build(name_seeds, head, weights):
    """Sequences for a role: list of dicts {x (T,167) f16, y (T,7), w (T,) f32}."""
    seqs = []
    for name, seed in name_seeds:
        w = D.load_world(name, seed)
        for k, j in D.pairs(w):
            x, y, _vis, code = D.pair_arrays(w, k, j)
            ww = np.ones(len(code), np.float32) if head == "NF" else weights[code].astype(np.float32)
            seqs.append({"set": name, "x": x, "y": y, "w": ww})
    return seqs


def run_epoch(model, seqs, opt, rng, batch, smoke=False):
    """One pass. Sequences batched within a set (equal T); chunks of CHUNK
    ticks in order with the hidden state carried, detached."""
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
            T = seqs[bi[0]]["x"].shape[0]
            x = torch.from_numpy(np.stack([seqs[i]["x"] for i in bi], 1))   # (T, B, 167) f16
            y = torch.from_numpy(np.stack([seqs[i]["y"] for i in bi], 1))
            w = torch.from_numpy(np.stack([seqs[i]["w"] for i in bi], 1))
            h = None
            n_chunks = T // CHUNK if not smoke else 2
            for c in range(n_chunks):
                sl = slice(c * CHUNK, (c + 1) * CHUNK)
                xc = x[sl].float()
                if opt is not None:
                    pred, h = model(xc, h)
                    loss, _ = sample_loss(pred, y[sl], w[sl])
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
                    h = h.detach()
                else:
                    with torch.no_grad():
                        pred, h = model(xc, h)
                        loss, _ = sample_loss(pred, y[sl], w[sl])
                ws = float(w[sl].sum())
                tot += loss.item() * ws
                tot_w += ws
    return tot / tot_w


def predict_world(model, w):
    T = w["ticks"]
    pred = np.full((T, D.ROSTER, D.ROSTER, D.Y_DIM), np.nan, np.float32)
    with torch.no_grad():
        for k, j in D.pairs(w):
            x, _y, _v, _c = D.pair_arrays(w, k, j)
            out = []
            h = None
            for c in range(0, T, CHUNK):
                p, h = model(torch.from_numpy(x[c:c + CHUNK]).float()[:, None], h)
                out.append(p[:, 0].numpy())
            pred[:, k, j] = np.concatenate(out)
    return pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", choices=("NF", "DR"), required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--hidden", type=int, default=None, help=f"GRU width (default {H}; given, the run is named HEAD-h<width>-s<seed>)")
    ap.add_argument("--over-cap", action="store_true", help="allow a head above PARAM_CAP as a declared probe")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    h = H if a.hidden is None else a.hidden
    name = f"{a.head}-" + (f"h{h}-" if a.hidden is not None else "") + f"s{a.seed}" + ("-smoke" if a.smoke else "")
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)

    roles = D.roles()
    train = [(n, s) for n, r in roles.items() for s in r["train"]]
    val = [(n, s) for n, r in roles.items() for s in r["val"]]
    ev = [(n, s) for n, r in roles.items() for s in r["eval"]]
    assert not (set(train) & set(ev)) and not (set(val) & set(ev)) and not (set(train) & set(val))

    weights, freq = train_weights(train)      # TRAIN samples only (declaration guard)

    model = BeliefHead(h=h)
    np_ = n_params(model)
    over = check_cap(np_, a.over_cap)
    manifest = {"head": a.head, "seed": a.seed, "params": np_, "param_cap": PARAM_CAP, "over_cap": over, "hidden": h,
                "arch": f"Linear(167->{h})+ReLU, GRU({h}), Linear({h}->7)", "chunk": CHUNK,
                "loss": "w*(mse5 + mse_hap + BATH_WEIGHT*mse_bath)", "bath_weight": BATH_WEIGHT,
                "lr": a.lr, "batch_sequences": a.batch, "patience": a.patience, "epoch_cap": a.epochs,
                "margin": 1e-4, "roles": roles, "train_stratum_freq": freq.tolist(),
                "dr_weights_GRAVE_ADJACENT_COMMON": weights.tolist(), "weights_used": a.head == "DR",
                "torch": torch.__version__, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "smoke": a.smoke}
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"[{name}] params {np_} {'OVER' if over else '≤'} {PARAM_CAP}; train {len(train)} / val {len(val)} / eval {len(ev)} worlds; "
          f"freq {np.round(freq, 5).tolist()} weights {np.round(weights, 3).tolist()}", flush=True)

    t0 = time.time()
    tr_seqs = build(train, a.head, weights)
    va_seqs = build(val, a.head, weights)
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
    torch.save({"state_dict": model.state_dict(), "best_epoch": best["epoch"], "best_val": best["loss"],
                "manifest": manifest}, out / "head-best.pt")
    for n, s in ev:
        w = D.load_world(n, s)
        np.savez_compressed(out / f"pred-{n}-{s}.npz", pred=predict_world(model, w))
    done = {"best_epoch": best["epoch"], "best_val": best["loss"], "epochs_run": epoch,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head_sha256": hashlib.sha256((out / "head-best.pt").read_bytes()).hexdigest()}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done: best epoch {best['epoch']} val {best['loss']:.6f}; predictions for {len(ev)} eval worlds", flush=True)


if __name__ == "__main__":
    main()
