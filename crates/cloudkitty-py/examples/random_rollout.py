"""A random-policy rollout (spec 014 quickstart scenario 3).

Usage: python examples/random_rollout.py --seed 7 [--steps 200]

Samples each step a uniformly random legal [activity, message] pair (spec
028: the mask is [activity menu_len | message head_len], each half sampled
on its own) and prints the rollout summary. Deterministic given the seed:
the same seed reproduces the same rollout bit for bit (SC-002).
"""

import argparse

import numpy as np

import cloudkitty


def legal_pair(mask, menu_len, rng):
    """A random legal [activity, message] pair from the two halves of the mask."""
    mask = np.asarray(mask, dtype=np.uint8)
    activities = np.flatnonzero(mask[:menu_len])
    messages = np.flatnonzero(mask[menu_len:])
    return [int(rng.choice(activities)), int(rng.choice(messages))]


def rollout(seed, steps):
    """One seeded random-policy rollout; returns the summary main() prints."""
    env = cloudkitty.ParallelEnv(horizon=max(steps, 1))
    obs, infos = env.reset(seed=seed)
    agents = env.possible_agents
    rng = np.random.default_rng(seed)

    total_reward = 0.0
    survived = 0
    decisions = 0
    for _ in range(steps):
        actions = {agent: legal_pair(infos[agent]["mask"], env.menu_len, rng) for agent in agents}
        obs, rewards, terminations, truncations, infos = env.step(actions)
        assert not any(terminations.values()), "terminations are always False"
        total_reward += rewards[agents[0]]
        for agent in agents:
            # survived is tri-state: True/False is a validation verdict on a
            # real proposal; None means no proposal was made (the engine
            # substituted idle for an omitted action) and counts as neither.
            verdict = infos[agent]["survived"]
            if verdict is not None:
                decisions += 1
                if verdict:
                    survived += 1
        if all(truncations.values()):
            break
    return {
        "seed": seed,
        "steps": steps,
        "agents": agents,
        "mean_reward": total_reward / max(steps, 1),
        "survived": survived,
        "decisions": decisions,
        "state_size": int(env.state().shape[0]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=200)
    args = parser.parse_args()
    r = rollout(args.seed, args.steps)

    print(f"seed:            {r['seed']}")
    print(f"steps:           {r['steps']}")
    print(f"agents:          {r['agents']}")
    print(f"mean reward:     {r['mean_reward']:.6f}")
    print(f"survived:        {r['survived']}/{r['decisions']} proposals passed validation")
    print(f"state size:      {r['state_size']}")


if __name__ == "__main__":
    main()
