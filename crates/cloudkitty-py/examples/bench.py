"""Throughput measurement (spec 014 SC-003).

Method (printed alongside the numbers, as the contract requires):
- Single-threaded: one ParallelEnv on the default world, stepped with the
  constant no-op pair for every agent; steps/s = steps / wall time, wall
  time by time.perf_counter around the step loop only (reset excluded).
  No-op actions keep the measurement about the environment pipeline
  (tick + observations + masks + global state), not about any policy.
- The action is spec 028's [activity, message] pair: Idle (the activity
  menu's LAST row, menu_len - 1; the row index depends on the world's
  kitty and critter slots, so it is read from the environment, never
  hard-coded) and Silent (message 0, spec 033).
- Vectorized: a VectorEnv of N independent worlds with one worker thread
  per world; environment steps/s = (steps x N) / wall time. Scaling is
  vectorized steps/s divided by single-threaded steps/s.
"""

import argparse
import time

import cloudkitty

SILENT = 0


def idle_action(env):
    """The no-op [Idle, Silent] pair for this environment. Idle is the activity
    menu's last row (codec.rs builds the menu with Idle pushed last)."""
    return [env.menu_len - 1, SILENT]


def bench_single(steps):
    env = cloudkitty.ParallelEnv(horizon=steps + 1)
    env.reset(seed=1)
    idle = idle_action(env)
    actions = {a: idle for a in env.possible_agents}
    start = time.perf_counter()
    for _ in range(steps):
        env.step(actions)
    elapsed = time.perf_counter() - start
    return steps / elapsed


def bench_vector(steps, worlds):
    env = cloudkitty.VectorEnv(worlds, horizon=steps + 1, workers=worlds)
    env.reset()
    idle = idle_action(env)
    actions = {a: [idle] * worlds for a in env.possible_agents}
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
