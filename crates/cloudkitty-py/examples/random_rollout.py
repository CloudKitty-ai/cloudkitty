"""A random-policy rollout (spec 014 quickstart scenario 3).

Usage: python examples/random_rollout.py --seed 7 [--steps 200]

Samples uniformly among masked-in menu entries each step and prints the
rollout summary. Deterministic given the seed: the same seed reproduces
the same rollout bit for bit (SC-002).
"""

import argparse

import numpy as np

import cloudkitty


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=200)
    args = parser.parse_args()

    env = cloudkitty.ParallelEnv(horizon=max(args.steps, 1))
    obs, infos = env.reset(seed=args.seed)
    agents = env.possible_agents
    rng = np.random.default_rng(args.seed)

    total_reward = 0.0
    survived = 0
    decisions = 0
    for _ in range(args.steps):
        actions = {}
        for agent in agents:
            legal = np.flatnonzero(infos[agent]["mask"])
            actions[agent] = int(rng.choice(legal))
        obs, rewards, terminations, truncations, infos = env.step(actions)
        assert not any(terminations.values()), "terminations are always False"
        total_reward += rewards[agents[0]]
        for agent in agents:
            decisions += 1
            if infos[agent]["survived"]:
                survived += 1
        if all(truncations.values()):
            break

    print(f"seed:            {args.seed}")
    print(f"steps:           {args.steps}")
    print(f"agents:          {agents}")
    print(f"mean reward:     {total_reward / max(args.steps, 1):.6f}")
    print(f"survived:        {survived}/{decisions} proposals passed validation")
    print(f"state size:      {env.state().shape[0]}")


if __name__ == "__main__":
    main()
