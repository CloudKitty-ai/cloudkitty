#!/usr/bin/env python3
"""Gen 2 critic sanity probe (Gen 1 practice #365, owner 2026-09-10
"Probe then accept"; forked from fog-gen1-shakeout/critic_probe.py
with the Gen 2 surface deltas only).

A random-legal policy tanks welfare fast, so returns actually vary;
the probe asks whether the trunk critic behaves sanely on those
off-distribution states. It is not recipe validation; it tests the
artifact for the one failure mode that would flip the accept —
pathological extrapolation — and proves the state → target → model
wiring on data with signal. Acceptance stays the owner's word.

    critic_probe_g2.py [--ticks 4000] [--worlds 3] [--seed-base 870004]
                       [--critic PATH] [--out FILE]

Bars (the #365 trio, declared before collection, carried verbatim):
every prediction finite; every raw-unit prediction inside
[0, 2 x target_mean]; Spearman rho(prediction, realized censored
return) >= 0.3 pooled. Targets are built by train_critic_g2's
critic_arrays, the trainer's own recipe (gamma 0.998, min-future
1500). World = the trunk config (g2leg-20.toml, randomized starts);
seed-base 870004 in the shared battery eval band (870001+), the Gen 1
probe's seed carried verbatim — the runner strides worlds by 1e6, so
the realized world seeds are recorded in the output JSON. Run from
the repo root with the exp-006 venv.
"""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent               # trainer/
ARC = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from obs_layout_v6 import N_ACT, N_LOGITS  # noqa: E402

CRITIC = ARC / "artifacts/critic-g2/critic-g2-0p998.pt"
TRUNK_TOML = HERE.parents[1] / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
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
    from ppo_env_g2 import TrunkVecRunner
    # horizon override: the rl config default truncates at 2,000 ticks;
    # the probe needs one continuous episode per world so censored
    # returns never span a reset (the Gen 1 probe crossed resets
    # silently; here the stream is asserted unbroken).
    runner = TrunkVecRunner(str(TRUNK_TOML), n_worlds, seed_base,
                            horizon=ticks + 1)
    obs_dim, mask_dim = runner.dims
    assert mask_dim == N_LOGITS, (mask_dim, N_LOGITS)
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
        _rew, trunc, _final = runner.step(actions)
        assert not trunc.any(), "probe world truncated mid-stream"
        for w in range(n_worlds):
            states[w].append(st[w])
            rewards[w].append(_rew[w])
    return [SimpleNamespace(name=f"probe-w{w}",
                            state=np.stack(states[w]).astype(np.float32),
                            reward=np.asarray(rewards[w], np.float32))
            for w in range(n_worlds)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--worlds", type=int, default=3)
    ap.add_argument("--seed-base", type=int, default=870004)
    ap.add_argument("--critic", type=Path, default=CRITIC)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    from model_attn_v2 import EntityCriticV2
    from tokens_v2 import tokenize
    from train_critic_g2 import critic_arrays

    rollouts = collect(args.ticks, args.worlds, args.seed_base)
    for r in rollouts:
        assert np.isfinite(r.reward).all() and np.isfinite(r.state).all()
        print(f"{r.name}: mean reward {r.reward.mean():.4f}", flush=True)
    x, y = critic_arrays(rollouts, gamma=0.998, min_future=1500)

    art = torch.load(args.critic, map_location="cpu", weights_only=True)
    assert art["gamma"] == 0.998 and art["min_future"] == 1500
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()
    k, e, g, p = tokenize(x)
    with torch.no_grad():
        pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                          for i in range(0, k.shape[0], 4096)]).numpy()
    pred_raw = pred * art["target_std"] + art["target_mean"]
    v = verdict(pred_raw, y, art["target_mean"])
    # per-world slices (equal keeps: ticks - min_future + 1 each), so a
    # pooled rho washed out by world-level offsets stays diagnosable
    keep = args.ticks - 1500 + 1
    assert len(y) == keep * args.worlds, (len(y), keep, args.worlds)
    v["per_world"] = [
        {"name": r.name,
         "rho": spearman(pred_raw[w * keep:(w + 1) * keep],
                         y[w * keep:(w + 1) * keep]),
         "pred_range": [float(pred_raw[w * keep:(w + 1) * keep].min()),
                        float(pred_raw[w * keep:(w + 1) * keep].max())],
         "target_range": [float(y[w * keep:(w + 1) * keep].min()),
                          float(y[w * keep:(w + 1) * keep].max())]}
        for w, r in enumerate(rollouts)]
    v.update({"states": int(len(y)),
              "target_min": float(y.min()), "target_max": float(y.max()),
              "target_mean_probe": float(y.mean()),
              "target_mean_corpus": float(art["target_mean"]),
              "ticks": args.ticks, "worlds": args.worlds,
              "seed_base": args.seed_base,
              "world_seeds": [args.seed_base + w * 1_000_000
                              for w in range(args.worlds)],
              "critic": str(args.critic)})
    print(json.dumps(v, indent=1))
    if args.out:
        args.out.write_text(json.dumps(v, indent=1) + "\n")
    print(f"critic probe: {v['verdict']}")


if __name__ == "__main__":
    main()
