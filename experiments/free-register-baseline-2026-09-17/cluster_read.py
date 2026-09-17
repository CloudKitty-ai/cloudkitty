#!/usr/bin/env python3
"""Question 2 of PREREG.md: are mews and chirps clustered in time (and
space) beyond chance, and does the clustering survive shared state?

    cluster_read.py lab  TRACE_NPZ  [--draws 200] [--out JSON]
    cluster_read.py live POLL_JSONL [--draws 200] [--out JSON]

Coincidences = pairs (S says a word of the set at t, L != S says one at
t + l, 1 <= l <= k). Null A: each cat's series circularly shifted by a
random offset. Null B: each cat's emissions re-drawn among its own
ticks of the same activity class, counts per class kept. Ratio =
observed / null mean; pct = share of null draws at or above observed.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
import free_register_read as R  # noqa: E402

SETS = {"mew": ["mew"], "chirp": ["chirp"], "mew+chirp": ["mew", "chirp"], "purr": ["purr"]}
LAGS = (1, 3, 10)
STATES = {"idle": 0, "resting": 1, "sleeping": 2, "eating": 3, "drinking": 4, "playing": 5, "grooming": 6}


def coincidences(E, k):
    """Cross-cat pairs within lag <= k. E[T,K] bool."""
    n = 0
    for lag in range(1, k + 1):
        a, b = E[:-lag].astype(int), E[lag:].astype(int)
        n += int((a.sum(1) * b.sum(1) - (a & b).sum(1)).sum())
    return n


def pair_distance(E, pos, k):
    """Mean Manhattan distance between the two cats of each coincident
    pair, measured at the second emission; None without pairs."""
    ds = []
    for lag in range(1, k + 1):
        t, s = np.nonzero(E[:-lag])
        for ti, si in zip(t, s):
            for li in np.nonzero(E[ti + lag])[0]:
                if li != si:
                    ds.append(abs(pos[ti + lag, si] - pos[ti + lag, li]).sum())
    return float(np.mean(ds)) if ds else None, len(ds)


def null_a(E, rng):
    out = np.empty_like(E)
    T = E.shape[0]
    for i in range(E.shape[1]):
        out[:, i] = np.roll(E[:, i], int(rng.integers(T)))
    return out


def null_b(E, actcls, rng):
    out = np.zeros_like(E)
    for i in range(E.shape[1]):
        for c in np.unique(actcls[:, i]):
            idx = np.nonzero(actcls[:, i] == c)[0]
            n = int(E[idx, i].sum())
            if n:
                out[rng.choice(idx, n, replace=False), i] = True
    return out


def read(series, draws, seed=0):
    """series: list of (E_words[T,K] by set name, actcls[T,K], pos[T,K,2]) per seed."""
    rng = np.random.default_rng(seed)
    res = {}
    for name in SETS:
        res[name] = {"n_emissions": int(sum(s[0][name].sum() for s in series))}
        for k in LAGS:
            obs = sum(coincidences(s[0][name], k) for s in series)
            na = np.array([sum(coincidences(null_a(s[0][name], rng), k) for s in series) for _ in range(draws)])
            nb = np.array([sum(coincidences(null_b(s[0][name], s[1], rng), k) for s in series) for _ in range(draws)])
            cell = {"observed": obs,
                    "null_a_mean": float(na.mean()), "ratio_a": obs / na.mean() if na.mean() else None, "pct_a": float((na >= obs).mean()),
                    "null_b_mean": float(nb.mean()), "ratio_b": obs / nb.mean() if nb.mean() else None, "pct_b": float((nb >= obs).mean())}
            if k == 10:
                d_obs = [pair_distance(s[0][name], s[2], k) for s in series]
                d_null = [pair_distance(null_a(s[0][name], rng), s[2], k) for s in series for _ in range(5)]
                w = lambda ds: (sum(d * n for d, n in ds if d is not None) / max(1, sum(n for d, n in ds if d is not None))) if any(d is not None for d, n in ds) else None  # noqa: E731
                cell["pair_distance"] = w(d_obs)
                cell["pair_distance_null_a"] = w(d_null)
            res[name][f"k{k}"] = cell
    return res


def lab_series(path):
    z = np.load(path)
    out = []
    for rows in R.rows_by_seed(z).values():
        ids, pos, said, actcls, present, target, top = R.per_tick(rows)
        E = {name: np.isin(said, [R.head_index(w) for w in words]) for name, words in SETS.items()}
        out.append((E, actcls, pos))
    return out


def live_series(path):
    polls = [json.loads(l) for l in open(path) if '"tick"' in l]
    meows = {(m["kitty_id"], m["kind"], m["tick"]) for p in polls for m in p["meows"]}
    ids = sorted({k["id"] for p in polls for k in p["kitties"]})
    kix = {k: n for n, k in enumerate(ids)}
    t0, t1 = min(m[2] for m in meows), max(p["tick"] for p in polls)
    T, K = t1 - t0 + 1, len(ids)
    said = np.full((T, K), "", dtype=object)
    for kid, kind, tick in meows:
        said[tick - t0, kix[kid]] = kind  # one live row per (cat, kind, tick); a cat can say one word a tick
    E = {name: np.isin(said, words) for name, words in SETS.items()}
    # state and position from the nearest poll (polls every ~10 ticks)
    ptick = np.array([p["tick"] for p in polls])
    actcls = np.zeros((T, K), int)
    pos = np.zeros((T, K, 2))
    for t in range(T):
        p = polls[int(np.argmin(np.abs(ptick - (t + t0))))]
        for k in p["kitties"]:
            actcls[t, kix[k["id"]]] = STATES.get(k["state"], 0)
            pos[t, kix[k["id"]]] = (k["pos"]["x"], k["pos"]["y"])
    return [(E, actcls, pos)], {"ticks": T, "first_tick": t0, "last_tick": t1, "polls": len(polls), "meow_rows": len(meows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("lab", "live"))
    ap.add_argument("path", type=Path)
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    meta = {}
    series = lab_series(a.path) if a.mode == "lab" else None
    if a.mode == "live":
        series, meta = live_series(a.path)
    res = read(series, a.draws)
    res["_meta"] = {"mode": a.mode, "path": str(a.path), "draws": a.draws, **meta}
    print(f"== {a.mode} {meta}")
    print(f"{'set':10s} {'n':>6s}  k   obs   nullA  ratioA pctA   nullB  ratioB pctB   dist/null")
    for name in SETS:
        for k in LAGS:
            c = res[name][f"k{k}"]
            d = f"{c['pair_distance']:.1f}/{c['pair_distance_null_a']:.1f}" if k == 10 and c.get("pair_distance") is not None else ""
            print(f"{name:10s} {res[name]['n_emissions']:6d} {k:2d} {c['observed']:6d} {c['null_a_mean']:7.1f} {c['ratio_a'] or 0:6.2f} {c['pct_a']:.3f} {c['null_b_mean']:7.1f} {c['ratio_b'] or 0:6.2f} {c['pct_b']:.3f}   {d}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
        print("wrote", a.out)


if __name__ == "__main__":
    main()
