#!/usr/bin/env python3
"""R2d — a grave probability from the FROZEN Phase 1b states
(DECLARATION.md §Read 2).

    grave_probe.py --base NF-h24-s1 [--threads 3] [--smoke]

Loads the base run's `head-best.pt` (Phase 1's BeliefHead), freezes it,
walks every world exactly as `train_heads.predict_world` does (hidden
state zero at the world's start, carried across CHUNK ticks) and keeps
the GRU output z (T, h) per (observer, friend) pair. Fits
Linear(h → 1) + sigmoid by natural-frequency BCE on "the friend's true
stratum is GRAVE" over the TRAINING worlds, early-stopped on the
VALIDATION worlds' BCE with a RELATIVE margin (new best when
val < best × (1 − REL_MARGIN)), patience 10, cap 200 epochs; probe seed
= the base run's seed. Writes results-raw/probe/<base>+p/:
run-manifest.json, metrics.jsonl, probe.pt, pgrave-<set>-<seed>.npz
(p (T, 5, 5) [observer, friend], NaN on the diagonal) for every
evaluation world, done.json. The base head is never updated; the first
evaluation world's 1b prediction file is reproduced from the extracted
states before anything is written (the guard of construction).
"""
import argparse
import hashlib
import json
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
import strata as S  # noqa: E402
import train_heads as T  # noqa: E402  (BeliefHead, CHUNK)

OUT_ROOT = HERE / "results-raw" / "probe"
BASES = [f"{h}-h24-s{s}" for h in ("NF", "DR") for s in (1, 2, 3)]
LR = 1e-2
BATCH = 65536
REL_MARGIN = 1e-3
PATIENCE = 10
EPOCHS = 200
PRED_TOL = 1e-4                       # /100 scale: the frozen head's own output over the extracted states vs 1b's file


def probe_name(base):
    return f"{base}+p"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_base(base):
    ck = torch.load(HERE / "results-raw/heads" / base / "head-best.pt", map_location="cpu", weights_only=False)
    model = T.BeliefHead(h=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, ck


def states_world(model, w, ticks=None):
    """The 20 pairs of a world as one batch: pairs [(k, j)], z (T, 20, h) —
    hidden state zero at the start, carried across CHUNK ticks."""
    pairs = list(D.pairs(w))
    x = torch.from_numpy(np.stack([D.pair_arrays(w, k, j)[0] for k, j in pairs], 1))      # (T, 20, 167) f16
    Tn = w["ticks"] if ticks is None else ticks
    out, h = [], None
    with torch.no_grad():
        for c in range(0, Tn, T.CHUNK):
            z, h = model.gru(torch.relu(model.proj(x[c:min(c + T.CHUNK, Tn)].float())), h)
            out.append(z)
    return pairs, torch.cat(out)


def check_reproduces(model, base, w, pairs, z):
    """The frozen head's output layer over z equals 1b's committed prediction for this world."""
    ref = np.load(HERE / "results-raw/heads" / base / f"pred-{w['set']}-{w['seed']}.npz")["pred"]
    with torch.no_grad():
        mine = model.out(z).numpy()                                                        # (T, 20, 7)
    worst = max(float(np.abs(mine[:, i] - ref[:len(mine), k, j]).max()) for i, (k, j) in enumerate(pairs))
    assert worst < PRED_TOL, (base, w["set"], w["seed"], worst)
    return worst


def collect(model, worlds, ticks=None):
    """Z (N, h) f32, y (N,) f32 GRAVE indicator, vis (N,) bool, code (N,) int8, hap_only (N,) bool, over every pair tick."""
    Z, code, vis, hap_only = [], [], [], []
    for n, s in worlds:
        w = D.load_world(n, s)
        pairs, z = states_world(model, w, ticks)
        Tn = z.shape[0]
        for i, (k, j) in enumerate(pairs):
            _x, y, v, c = D.pair_arrays(w, k, j)
            Z.append(z[:, i])
            code.append(c[:Tn])
            vis.append(v[:Tn])
            hap_only.append((c[:Tn] == S.GRAVE) & (y[:Tn, :5].max(1) * 100.0 < S.NEED_DISTRESS))
    code = np.concatenate(code)
    return (torch.cat(Z), torch.from_numpy((code == S.GRAVE).astype(np.float32)),
            np.concatenate(vis), code, np.concatenate(hap_only))


def mean_bce(probe, Z, y, batch=1 << 18):
    tot = 0.0
    with torch.no_grad():
        for i in range(0, len(Z), batch):
            tot += F.binary_cross_entropy_with_logits(probe(Z[i:i + batch]).squeeze(-1), y[i:i + batch], reduction="sum").item()
    return tot / len(Z)


def fit(Z, y, Zv, yv, seed, log=None, epochs=EPOCHS, patience=PATIENCE):
    """Linear(h → 1) by Adam on minibatch BCE; early stop on the validation BCE with the RELATIVE margin."""
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    probe = nn.Linear(Z.shape[1], 1)
    opt = torch.optim.Adam(probe.parameters(), lr=LR)
    best = {"loss": float("inf"), "epoch": -1, "state": None}
    pat = patience
    epoch = 0
    for epoch in range(1, epochs + 1):
        t1 = time.time()
        perm = torch.randperm(len(Z), generator=g)
        for i in range(0, len(Z), BATCH):
            bi = perm[i:i + BATCH]
            loss = F.binary_cross_entropy_with_logits(probe(Z[bi]).squeeze(-1), y[bi])
            opt.zero_grad()
            loss.backward()
            opt.step()
        tr, va = mean_bce(probe, Z, y), mean_bce(probe, Zv, yv)
        row = {"epoch": epoch, "train_bce": tr, "val_bce": va, "seconds": time.time() - t1}
        if log is not None:
            with log.open("a") as f:
                f.write(json.dumps(row) + "\n")
        if va < best["loss"] * (1.0 - REL_MARGIN):
            best = {"loss": va, "epoch": epoch, "state": {k: v.clone() for k, v in probe.state_dict().items()}}
            pat = patience
        else:
            pat -= 1
        if pat == 0:
            break
    probe.load_state_dict(best["state"])
    return probe, best, epoch


def predict_world_p(model, probe, w):
    pairs, z = states_world(model, w)
    with torch.no_grad():
        p = torch.sigmoid(probe(z).squeeze(-1)).numpy()                                     # (T, 20)
    out = np.full((w["ticks"], D.ROSTER, D.ROSTER), np.nan, np.float32)
    for i, (k, j) in enumerate(pairs):
        out[:, k, j] = p[:, i]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", choices=BASES, required=True)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true", help="2 train / 1 val / 1 eval world, 2 chunks each, 2 epochs")
    ap.add_argument("--out-root", type=Path, default=OUT_ROOT)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    model, ck = load_base(a.base)
    base_sha = sha256(HERE / "results-raw/heads" / a.base / "head-best.pt")
    seed = ck["manifest"]["seed"]
    name = probe_name(a.base) + ("-smoke" if a.smoke else "")
    out = a.out_root / name
    out.mkdir(parents=True, exist_ok=True)

    roles = D.roles()
    train = [(n, s) for n, r in roles.items() for s in r["train"]]
    val = [(n, s) for n, r in roles.items() for s in r["val"]]
    ev = [(n, s) for n, r in roles.items() for s in r["eval"]]
    assert not (set(train) & set(ev)) and not (set(val) & set(ev)) and not (set(train) & set(val))
    ticks = None
    if a.smoke:
        train, val, ev, ticks = train[:2], val[:1], ev[:1], 2 * T.CHUNK

    w0 = D.load_world(*ev[0])
    worst = check_reproduces(model, a.base, w0, *states_world(model, w0, ticks))         # the guard of construction
    probe_params = ck["manifest"]["hidden"] + 1
    manifest = {"probe": name, "base": a.base, "base_sha256": base_sha, "base_params": ck["manifest"]["params"],
                "params": probe_params, "hybrid_params": ck["manifest"]["params"] + probe_params, "param_cap": T.PARAM_CAP,
                "arch": f"frozen {ck['manifest']['arch']} -> Linear({ck['manifest']['hidden']}->1)+sigmoid on the GRU output",
                "target": "strata.stratum(true state) == GRAVE", "loss": "BCE, natural frequency", "lr": LR,
                "batch_samples": BATCH, "rel_margin": REL_MARGIN, "patience": PATIENCE, "epoch_cap": EPOCHS, "seed": seed,
                "chunk": T.CHUNK, "roles": roles, "reproduces_1b_pred_max_abs": worst, "pred_tol": PRED_TOL,
                "torch": torch.__version__, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "smoke": a.smoke}
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"[{name}] base {a.base} reproduces 1b's prediction on {ev[0]} to {worst:.2e}; probe {probe_params} params "
          f"(hybrid {manifest['hybrid_params']} ≤ {T.PARAM_CAP}); train {len(train)} / val {len(val)} / eval {len(ev)} worlds", flush=True)

    t0 = time.time()
    Z, y, _v, _c, _h = collect(model, train, ticks)
    Zv, yv, _v, _c, _h = collect(model, val, ticks)
    freq = float(y.mean())
    print(f"[{name}] states: train {len(Z)} samples (GRAVE {freq:.5f}) / val {len(Zv)} ({time.time() - t0:.0f}s)", flush=True)

    log = out / "metrics.jsonl"
    log.write_text("")
    probe, best, epochs_run = fit(Z, y, Zv, yv, seed, log, epochs=2 if a.smoke else EPOCHS)
    print(f"[{name}] fit: best epoch {best['epoch']}/{epochs_run} val BCE {best['loss']:.6f}", flush=True)
    torch.save({"state_dict": probe.state_dict(), "best_epoch": best["epoch"], "best_val_bce": best["loss"], "manifest": manifest},
               out / "probe.pt")
    for n, s in ev:
        np.savez_compressed(out / f"pgrave-{n}-{s}.npz", p=predict_world_p(model, probe, D.load_world(n, s)))
    base_after = sha256(HERE / "results-raw/heads" / a.base / "head-best.pt")
    assert base_after == base_sha
    done = {"best_epoch": best["epoch"], "best_val_bce": best["loss"], "epochs_run": epochs_run, "train_grave_freq": freq,
            "n_train": len(Z), "n_val": len(Zv), "base_sha256_after": base_after,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "probe_sha256": sha256(out / "probe.pt")}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done: predictions for {len(ev)} eval worlds ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
