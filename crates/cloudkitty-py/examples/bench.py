"""Throughput measurement (spec 014 SC-003).

Method (printed alongside the numbers, as the contract requires):
- Single-threaded: one ParallelEnv on the default 32x32 4-kitty world,
  stepped with the constant idle action for every agent; steps/s =
  steps / wall time, wall time by time.perf_counter around the step loop
  only (reset excluded). Idle actions keep the measurement about the
  environment pipeline (tick + observations + masks + global state), not
  about any policy.
- Vectorized: a VectorEnv of N independent worlds with one worker thread
  per world; environment steps/s = (steps x N) / wall time. Scaling is
  vectorized steps/s divided by single-threaded steps/s.
"""

import argparse
import time

import cloudkitty

IDLE = 39


def bench_single(steps):
    env = cloudkitty.ParallelEnv(horizon=steps + 1)
    env.reset(seed=1)
    agents = env.possible_agents
    actions = {a: IDLE for a in agents}
    start = time.perf_counter()
    for _ in range(steps):
        env.step(actions)
    elapsed = time.perf_counter() - start
    return steps / elapsed


def bench_vector(steps, worlds):
    env = cloudkitty.VectorEnv(worlds, horizon=steps + 1, workers=worlds)
    env.reset()
    agents = env.possible_agents
    actions = {a: [IDLE] * worlds for a in agents}
    start = time.perf_counter()
    for _ in range(steps):
        env.step(actions)
    elapsed = time.perf_counter() - start
    return steps * worlds / elapsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--worlds", type=int, default=8)
    args = parser.parse_args()

    print(__doc__)
    single = bench_single(args.steps)
    print(f"single-threaded: {single:,.0f} env steps/s  (target: >= 5,000)")
    vector = bench_vector(args.steps, args.worlds)
    print(f"vectorized x{args.worlds}:  {vector:,.0f} env steps/s")
    print(f"scaling:         {vector / single:.2f}x over single-threaded")


if __name__ == "__main__":
    main()
