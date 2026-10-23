#!/usr/bin/env python3
"""Data for the Phase 1 heads (DECLARATION.md §What the head predicts,
§Strata, §Data; the step-4 pins in §Run order).

A SAMPLE is (world, observer k, friend j ≠ k, tick t):
  x[t]  = the observer's self block (109) ++ the friend's permanent row
          (58) from the observer's saved start-of-tick observation,
          167 cells (float16 as recorded);
  y[t]  = the friend's TRUE state the view was built from (needs[t−1],
          needs0 at t = 0): five hidden needs, happiness, bath, all /100
          → 7 targets in [0, 1];
  vis   = the row's present cell (mind-visible);
  code  = strata.stratum on that true state (GRAVE 0 / ADJACENT 1 / COMMON 2).

Splits come from split.json (by world). The VALIDATION worlds for early
stopping are carved from each set's TRAIN worlds with the same
SPLIT_SEED (round(0.2·n_train) of them); the evaluation worlds touch
nothing until the reads.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
import strata as S  # noqa: E402
from count_strata import SELF_BLOCK, KITTY_SLOT, ROSTER, friend_row, truth_streams  # noqa: E402

SPLIT = json.loads((HERE / "split.json").read_text())
VAL_SHARE = 0.2
X_DIM = SELF_BLOCK + KITTY_SLOT      # 167
Y_DIM = 7                            # eat, drink, sleep, play, cuddle, happiness, bath
HIDDEN = slice(0, 5)
HAP, BATH = 5, 6


def roles():
    """{set: {"train": [...], "val": [...], "eval": [...]}} — val carved from train."""
    rng = np.random.default_rng(SPLIT["split_seed"])
    out = {}
    for name, s in SPLIT["sets"].items():
        tr = sorted(s["train"])
        perm = [tr[i] for i in rng.permutation(len(tr))]
        n_val = round(VAL_SHARE * len(tr))
        val = sorted(perm[:n_val])
        out[name] = {"train": [w for w in tr if w not in val], "val": val, "eval": sorted(s["eval"])}
    return out


def world_path(name, seed):
    return HERE / "results-raw" / name / f"streams-{seed}.npz"


def load_world(name, seed):
    z = np.load(world_path(name, seed))
    meta = json.loads(str(z["meta"]))
    assert meta["obs_recorded"] == [True] * ROSTER
    needs, hap = truth_streams(z)                 # aligned to obs[t]
    return {"set": name, "seed": seed, "ticks": meta["ticks"], "obs": z["obs"],
            "needs": needs, "hap": hap, "codes": S.stratum(needs, hap)}


def pair_arrays(w, k, j):
    """x (T, 167) float16, y (T, 7) float32, vis (T,) bool, code (T,) int8 for observer k, friend j."""
    off = SELF_BLOCK + KITTY_SLOT * friend_row(k, j)
    obs = w["obs"]
    x = np.concatenate([obs[:, k, :SELF_BLOCK], obs[:, k, off:off + KITTY_SLOT]], axis=1)
    y = np.concatenate([w["needs"][:, j, :5], w["hap"][:, j, None], w["needs"][:, j, 5:6]], axis=1) / 100.0
    vis = obs[:, k, off].astype(np.float32) > 0.5
    return x, y.astype(np.float32), vis, w["codes"][:, j]


def pairs(w):
    for k in range(ROSTER):
        for j in range(ROSTER):
            if j != k:
                yield k, j


def dr_weights(train_codes, cap=50.0):
    """Distress-reweighting (declaration §Two heads): per-stratum weight =
    inverse frequency on the TRAINING samples, capped at `cap` × the
    COMMON stratum's weight, renormalised so the mean training weight is
    1. Returns weight per stratum code [GRAVE, ADJACENT, COMMON] and the
    frequencies. Pure function of the training codes."""
    codes = np.concatenate([np.asarray(c).ravel() for c in train_codes])
    n = codes.size
    freq = np.array([(codes == i).sum() for i in range(3)], np.float64) / n
    assert (freq > 0).all(), freq
    w = 1.0 / freq
    w = np.minimum(w, cap * w[S.COMMON])
    w = w / float((w[codes]).mean())          # mean 1 over the training samples
    return w, freq
