#!/usr/bin/env python3
"""Critic sanity probe (#365, owner 2026-09-10: "Probe then accept").

A random-legal policy tanks welfare fast, so returns actually vary;
the probe asks whether the fog critic behaves sanely on those
off-distribution states. It cannot rescue the held-out EV and is not
recipe validation; it tests the artifact for the one failure mode that
would flip the accept — pathological extrapolation — and proves the
state → target → model wiring on data with signal.

    critic_probe.py [--ticks 4000] [--worlds 3] [--seed-base 870004]
                    [--out FILE]

Bars (posted to #365 before collection): every prediction finite;
every raw-unit prediction inside [0, 2 x target_mean]; Spearman
rho(prediction, realized censored return) >= 0.3 pooled. Targets are
built by train_critic6.critic_arrays, the trainer's own recipe
(gamma 0.998, min-future 1500). Run from the repo root with the
exp-006 venv.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
sys.path.insert(1, str(HERE.parents[0] / "exp-006-character-gen" / "trainer"))
sys.path.insert(2, str(HERE.parents[0] / "attn-critic-2026-08-12"))

CRITIC = HERE / "results-raw" / "clones" / "critic-fog" / "critic6-0p998.pt"
ANCHOR = HERE / "anchor.toml"
N_ACT = 39
RHO_BAR = 0.3


def rand_legal(mask, rng):
    """One uniformly random legal (activity, message) pair per seat."""
    act = rng.choice(np.flatnonzero(mask[:N_ACT]))
    msg = rng.choice(np.flatnonzero(mask[N_ACT:]))
    return int(act), int(msg)


def spearman(a, b):
    """Spearman rank correlation, average ranks for ties."""
    def ranks(x):
        order = np.argsort(x, kind="mergesort")
        r = np.empty(len(x))
        r[order] = np.arange(len(x), dtype=float)
        # average tied ranks
        vals, inv, counts = np.unique(x, return_inverse=True,
                                      return_counts=True)
        sums = np.zeros(len(vals))
        np.add.at(sums, inv, r)
        return sums[inv] / counts[inv]
    ra, rb = ranks(np.asarray(a, float)), ranks(np.asarray(b, float))
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom else 0.0


def verdict(pred_raw, targets, target_mean):
    """The three declared bars over pooled probe states."""
    finite = bool(np.isfinite(pred_raw).all())
    lo, hi = 0.0, 2.0 * target_mean
    in_band = bool(finite and (pred_raw >= lo).all() and (pred_raw <= hi).all())
    rho = spearman(pred_raw, targets) if finite else float("nan")
    ok = finite and in_band and rho >= RHO_BAR
    return {"finite": finite, "band": [lo, hi],
            "pred_min": float(np.min(pred_raw)) if finite else None,
            "pred_max": float(np.max(pred_raw)) if finite else None,
            "in_band": in_band, "spearman": rho, "rho_bar": RHO_BAR,
            "verdict": "PASS" if ok else "FAIL"}


def collect(ticks, n_worlds, seed_base):
    from ppo_env6 import MixedVecRunner, Variant
    with open(ANCHOR, "rb") as f:
        cfg = tomllib.load(f)
    variant = Variant(path=str(ANCHOR),
                      kitty_ids=[k["id"] for k in cfg["kitty"]],
                      behaviors={k["id"]: k["behavior"] for k in cfg["kitty"]})
    runner = MixedVecRunner([variant], 0.0, n_worlds, seed_base)
    obs_dim, mask_dim = runner.dims
    rng = np.random.default_rng(seed_base)
    states = [[] for _ in range(n_worlds)]
    rewards = [[] for _ in range(n_worlds)]
    for _ in range(ticks):
        st = runner.states()
        _obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
        actions = np.zeros((n_worlds, mask.shape[1], 2), np.int64)
        for w in range(n_worlds):
            for j in range(mask.shape[1]):
                if valid[w, j]:
                    actions[w, j] = rand_legal(mask[w, j], rng)
        rew, _trunc, _final = runner.step(actions)
        for w in range(n_worlds):
            states[w].append(st[w])
            rewards[w].append(rew[w])
    return [SimpleNamespace(name=f"probe-w{w}",
                            state=np.stack(states[w]).astype(np.float32),
                            reward=np.asarray(rewards[w], np.float32))
            for w in range(n_worlds)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--worlds", type=int, default=3)
    ap.add_argument("--seed-base", type=int, default=870004)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    from model_attn import EntityCritic
    from tokens import tokenize
    from train_critic6 import critic_arrays

    rollouts = collect(args.ticks, args.worlds, args.seed_base)
    for r in rollouts:
        assert np.isfinite(r.reward).all() and np.isfinite(r.state).all()
        print(f"{r.name}: mean reward {r.reward.mean():.4f} "
              f"(anchor corpus ~0.845)")
    x, y = critic_arrays(rollouts, gamma=0.998, min_future=1500)

    art = torch.load(CRITIC, map_location="cpu", weights_only=False)
    model = EntityCritic()
    model.load_state_dict(art["state_dict"])
    model.eval()
    k, e, g, p = tokenize(x)
    with torch.no_grad():
        pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                          for i in range(0, k.shape[0], 4096)]).numpy()
    pred_raw = pred * art["target_std"] + art["target_mean"]
    v = verdict(pred_raw, y, art["target_mean"])
    v.update({"states": int(len(y)),
              "target_min": float(y.min()), "target_max": float(y.max()),
              "target_mean_probe": float(y.mean()),
              "target_mean_corpus": float(art["target_mean"]),
              "ticks": args.ticks, "worlds": args.worlds,
              "seed_base": args.seed_base})
    print(json.dumps(v, indent=1))
    if args.out:
        args.out.write_text(json.dumps(v, indent=1) + "\n")
    print(f"critic probe: {v['verdict']}")


if __name__ == "__main__":
    main()
