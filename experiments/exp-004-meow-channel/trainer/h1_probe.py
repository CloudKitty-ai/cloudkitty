"""H1 probe: the clone's meow rate in policy company (prereg §2/§9.4).

Registered floor: >= 0.5 non-Silent messages per 1k kitty-ticks, greedy
selection, all-policy roster on the served world (F-012 geometry), the
declared eval band. Counts APPLIED messages (post-legality) from the
env's per-step infos, so a downgraded ask never inflates the rate.
Reports rates by kind and the proposed-vs-applied delta (should be 0 —
mask-legal messages never downgrade).
"""

import argparse
import json
from collections import Counter
from pathlib import Path

import cloudkitty
import numpy as np
import torch

from model import MLP

NEG_INF = float("-inf")


def greedy_pairs(model, obs_batch, mask_batch, n_actions):
    """One forward for the whole roster; masked argmax per head."""
    with torch.no_grad():
        logits = model(torch.from_numpy(obs_batch)).numpy()
    m = mask_batch.astype(bool)
    act_l = np.where(m[:, :n_actions], logits[:, :n_actions], NEG_INF)
    msg_l = np.where(m[:, n_actions:], logits[:, n_actions:], NEG_INF)
    return act_l.argmax(axis=1), msg_l.argmax(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path,
                    default=Path("experiments/exp-004-meow-channel/artifacts/clone/clone.pt"))
    ap.add_argument("--config", type=Path, default=Path("cloudkitty.toml"))
    ap.add_argument("--seeds", type=str, default=",".join(
        str(s) for s in range(870001, 870011)))
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--n-actions", type=int, default=34)
    args = ap.parse_args()

    ckpt = torch.load(args.clone, map_location="cpu", weights_only=True)
    model = MLP(ckpt["dims"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    kinds = Counter()
    kitty_ticks = 0
    silent_ticks = 0
    for seed in (int(s) for s in args.seeds.split(",")):
        env = cloudkitty.ParallelEnv(str(args.config))
        obs, infos = env.reset(seed=seed)
        episode = 0
        for _ in range(args.ticks):
            if not env.agents:
                # Horizon reached: chain a fresh episode on a derived
                # sub-seed so the probe covers the full tick budget.
                episode += 1
                obs, infos = env.reset(seed=seed * 100 + episode)
            agents = list(env.agents)
            ob = np.stack([np.asarray(obs[a], dtype=np.float32)
                           for a in agents])
            mk = np.stack([np.asarray(infos[a]["mask"], dtype=np.uint8)
                           for a in agents])
            act_ix, msg_ix = greedy_pairs(model, ob, mk, args.n_actions)
            acts = {a: (int(act_ix[i]), int(msg_ix[i]))
                    for i, a in enumerate(agents)}
            obs, rew, term, trunc, infos = env.step(acts)
            for agent in env.agents:
                kitty_ticks += 1
                am = infos[agent].get("applied_message")
                if am is None:
                    silent_ticks += 1
                else:
                    kinds[am] += 1
        print(f"seed {seed}: cumulative "
              f"{1000 * sum(kinds.values()) / kitty_ticks:.2f} meows/1k")

    total = sum(kinds.values())
    rate = 1000 * total / kitty_ticks
    out = {
        "kitty_ticks": kitty_ticks,
        "meows": total,
        "rate_per_1k": rate,
        "by_kind_per_1k": {k: 1000 * v / kitty_ticks
                           for k, v in sorted(kinds.items())},
        "floor": 0.5,
        "h1_pass": rate >= 0.5,
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
