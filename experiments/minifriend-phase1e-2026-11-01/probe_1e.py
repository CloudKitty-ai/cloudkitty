#!/usr/bin/env python3
"""Phase 1e — the 25-parameter grave probe refit on the retrained head's
states (DECLARATION.md §4), grave_probe's recipe verbatim.

    probe_1e.py --seed 1 [--threads 3] [--smoke]

Loads results-raw/heads/NF1e-h24-s<seed>/head-best.pt, freezes it,
walks every training and validation world of this arc's split as
train_heads.predict_world does (state zero at the world's start,
carried across 500-tick chunks; data_1e's observers) and keeps the
GRU output z per pair tick. Fits Linear(24 → 1) + sigmoid by
natural-frequency BCE on "the friend's true stratum is GRAVE" over the
training worlds (grave_probe.fit: Adam 1e-2, batch 65,536, relative
margin 1e-3, patience 10, cap 200; probe seed = the head's), early
stopped on the validation worlds. Before anything is written the
frozen head's output layer over the extracted states must reproduce
the head's own pred file on the first 1b evaluation world (the guard
of construction, grave_probe.PRED_TOL). Writes
results-raw/probe/NF1e-h24-s<seed>+p/: run-manifest.json,
metrics.jsonl, probe.pt, done.json. No pgrave file: the reads run the
head and probe over their own worlds.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(HERE))
import data_1e as E  # noqa: E402  (pins MINIFRIEND_ARC before grave_probe imports phase1_data)
sys.path.insert(0, str(EXPTS / "minifriend-phase1d-2026-10-24"))
import grave_probe as GP  # noqa: E402
import train_heads as T  # noqa: E402
import train_1e as TR  # noqa: E402

OUT_ROOT = HERE / "results-raw" / "probe"


def head_dir(seed, smoke=False):
    return HERE / "results-raw" / "heads" / TR.run_name(seed, smoke)


def load_head(seed, smoke=False):
    ck = torch.load(head_dir(seed, smoke) / "head-best.pt", map_location="cpu", weights_only=False)
    model = T.BeliefHead(h=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, ck


def states_world(model, w, ticks=None):
    """The world's pairs (data_1e.pairs) as one batch: pairs, z (T, n, h)."""
    pairs = list(E.pairs(w))
    x = torch.from_numpy(np.stack([E.pair_arrays(w, k, j)[0] for k, j in pairs], 1))
    Tn = w["ticks"] if ticks is None else ticks
    out, h = [], None
    with torch.no_grad():
        for c in range(0, Tn, T.CHUNK):
            z, h = model.gru(torch.relu(model.proj(x[c:min(c + T.CHUNK, Tn)].float())), h)
            out.append(z)
    return pairs, torch.cat(out)


def check_reproduces(model, seed, w, pairs, z, smoke=False):
    ref = np.load(head_dir(seed, smoke) / f"pred-{w['set']}-{w['seed']}.npz")["pred"]
    with torch.no_grad():
        mine = model.out(z).numpy()
    worst = max(float(np.abs(mine[:, i] - ref[:len(mine), k, j]).max()) for i, (k, j) in enumerate(pairs))
    assert worst < GP.PRED_TOL, (seed, w["set"], w["seed"], worst)
    return worst


def collect(model, worlds, ticks=None):
    Z, y = [], []
    for n, s in worlds:
        w = E.load_world(n, s)
        pairs, z = states_world(model, w, ticks)
        Tn = z.shape[0]
        for i, (k, j) in enumerate(pairs):
            Z.append(z[:, i])
            y.append((w["codes"][:Tn, j] == E.S.GRAVE).astype(np.float32))
    return torch.cat(Z), torch.from_numpy(np.concatenate(y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    model, ck = load_head(a.seed, a.smoke)
    base_sha = GP.sha256(head_dir(a.seed, a.smoke) / "head-best.pt")
    name = TR.run_name(a.seed, a.smoke) + "+p"
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)
    train, val, ev = E.role_lists(a.smoke)
    ticks = 2 * T.CHUNK if a.smoke else None
    if a.smoke:
        train, val = train[:4], val[:2]

    w0 = E.load_world(*ev[0])
    worst = check_reproduces(model, a.seed, w0, *states_world(model, w0, ticks), smoke=a.smoke)
    probe_params = ck["manifest"]["hidden"] + 1
    manifest = {"probe": name, "base": TR.run_name(a.seed, a.smoke), "base_sha256": base_sha, "base_params": ck["manifest"]["params"],
                "params": probe_params, "hybrid_params": ck["manifest"]["params"] + probe_params, "param_cap": T.PARAM_CAP,
                "arch": f"frozen {ck['manifest']['arch']} -> Linear({ck['manifest']['hidden']}->1)+sigmoid on the GRU output",
                "target": "strata.stratum(true state) == GRAVE", "loss": "BCE, natural frequency", "lr": GP.LR,
                "batch_samples": GP.BATCH, "rel_margin": GP.REL_MARGIN, "patience": GP.PATIENCE, "epoch_cap": GP.EPOCHS,
                "seed": a.seed, "chunk": T.CHUNK, "train_worlds": len(train), "val_worlds": len(val),
                "reproduces_head_pred_max_abs": worst, "pred_tol": GP.PRED_TOL, "recipe": "grave_probe.py (Phase 1d) verbatim; data_1e for the worlds",
                "torch": torch.__version__, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "smoke": a.smoke}
    (out / "run-manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"[{name}] head reproduces its prediction on {ev[0]} to {worst:.2e}; probe {probe_params} params "
          f"(hybrid {manifest['hybrid_params']} ≤ {T.PARAM_CAP}); train {len(train)} / val {len(val)} worlds", flush=True)

    t0 = time.time()
    Z, y = collect(model, train, ticks)
    Zv, yv = collect(model, val, ticks)
    freq = float(y.mean())
    print(f"[{name}] states: train {len(Z)} samples (GRAVE {freq:.5f}) / val {len(Zv)} ({time.time() - t0:.0f}s)", flush=True)
    log = out / "metrics.jsonl"
    log.write_text("")
    probe, best, epochs_run = GP.fit(Z, y, Zv, yv, a.seed, log, epochs=2 if a.smoke else GP.EPOCHS)
    print(f"[{name}] fit: best epoch {best['epoch']}/{epochs_run} val BCE {best['loss']:.6f}", flush=True)
    torch.save({"state_dict": probe.state_dict(), "best_epoch": best["epoch"], "best_val_bce": best["loss"], "manifest": manifest},
               out / "probe.pt")
    assert GP.sha256(head_dir(a.seed, a.smoke) / "head-best.pt") == base_sha
    done = {"best_epoch": best["epoch"], "best_val_bce": best["loss"], "epochs_run": epochs_run, "train_grave_freq": freq,
            "n_train": len(Z), "n_val": len(Zv), "base_sha256_after": base_sha,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "probe_sha256": GP.sha256(out / "probe.pt")}
    (out / "done.json").write_text(json.dumps(done, indent=1))
    print(f"[{name}] done ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
