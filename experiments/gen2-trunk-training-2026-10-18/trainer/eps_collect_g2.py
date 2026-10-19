#!/usr/bin/env python3
"""Rung (iv) collector (MITIGATION.md §Iteration, owner-ruled
2026-10-19): ε-mixture trajectories on the trunk config — the BC
clone's greedy legal action with probability 1−ε, random-legal with ε
— saved as state/reward bundles the critic trainer's --extension-dirs
loader consumes (states and rewards only; one continuous episode per
rollout, horizon = ticks+1, same geometry as the probes).

Seeds are EXACT: each rollout runs its own one-world runner at
seed_base = that seed, so rollout k's world seed is --seed-base + k
with no 1e6 world stride. The §Iteration allocation: ε 0.1 at
1095201–1095220, ε 0.3 at 1095221–1095240. Covered-mind seats (the
clone); standing stops armed; ε capped at 0.3.

    eps_collect_g2.py --epsilon 0.1 --seed-base 1095201 --rollouts 20
        [--ticks 4000] [--out ../results-raw-extension-iter/eps01]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from critic_probe_g2 import TRUNK_TOML, masked_argmax, rand_legal  # noqa: E402
from obs_layout_v6 import N_LOGITS  # noqa: E402


def collect_one(ticks, seed, epsilon, clone):
    from ppo_env_g2 import TrunkVecRunner
    runner = TrunkVecRunner(str(TRUNK_TOML), 1, seed, horizon=ticks + 1)
    obs_dim, mask_dim = runner.dims
    assert mask_dim == N_LOGITS
    rng = np.random.default_rng(seed)
    states, rewards = [], []
    for _ in range(ticks):
        states.append(runner.states()[0])
        obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
        flat = torch.as_tensor(obs[valid])
        with torch.no_grad():
            logits = clone(flat).numpy()
        actions = np.zeros((1, mask.shape[1], 2), np.int64)
        row = 0
        for j in range(mask.shape[1]):
            if valid[0, j]:
                if rng.random() >= epsilon:
                    actions[0, j] = masked_argmax(logits[row], mask[0, j])
                else:
                    actions[0, j] = rand_legal(mask[0, j], rng)
                row += 1
        rew, trunc, _f = runner.step(actions)
        assert not trunc.any(), "rung (iv) world truncated mid-stream"
        rewards.append(rew[0])
    return (np.stack(states).astype(np.float32),
            np.asarray(rewards, np.float32))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epsilon", type=float, required=True)
    ap.add_argument("--seed-base", type=int, required=True)
    ap.add_argument("--rollouts", type=int, default=20)
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--clone", type=Path,
                    default=ARC / "artifacts/trunk-clone/trunk-clone.pt")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    assert 0.0 < args.epsilon <= 0.3, "epsilon capped at 0.3 (welfare line)"

    from model_v6 import EntityPolicyV6
    ck = torch.load(args.clone, map_location="cpu", weights_only=True)
    clone = EntityPolicyV6(**ck["hyper"])
    clone.load_state_dict(ck["state_dict"])
    clone.eval()

    for k in range(args.rollouts):
        seed = args.seed_base + k
        d = args.out / f"config-00-rollout-{k:02d}"
        d.mkdir(parents=True, exist_ok=True)
        state, reward = collect_one(args.ticks, seed, args.epsilon, clone)
        np.save(d / "state.npy", state)
        np.save(d / "reward.npy", reward)
        (d / "meta.json").write_text(json.dumps(
            {"seed": seed, "epsilon": args.epsilon, "ticks": args.ticks,
             "clone": str(args.clone), "rung": "iv"}) + "\n")
        print(f"rollout {k:02d} seed {seed}: reward mean "
              f"{reward.mean():.4f}", flush=True)
    print("rung (iv) collection done", flush=True)


if __name__ == "__main__":
    main()
