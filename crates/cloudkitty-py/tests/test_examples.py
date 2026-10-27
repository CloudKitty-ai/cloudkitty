"""The examples run on the committed engine.

Spec 014's quickstart §3 cites bench.py as the SC-003 reproduction and
random_rollout.py as the SC-002 one; the tag-time smoke runs only the
rollout, and CI ran neither. This is the CI guard (the python-surface job
runs this directory). Both drifted once already: scalar actions where
spec 028 requires [activity, message] pairs, and the bench's hard-coded
Idle row from a menu that no longer exists (found 2026-10-26).
"""

import importlib.util
from pathlib import Path

import numpy as np

import cloudkitty

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def load_example(name):
    spec = importlib.util.spec_from_file_location(name, EXAMPLES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bench_sends_the_idle_silent_pair_the_engine_accepts():
    bench = load_example("bench")
    env = cloudkitty.ParallelEnv(horizon=3)
    env.reset(seed=1)
    idle = bench.idle_action(env)
    # spec 028: one [activity, message] pair; Idle is the menu's last row, Silent is 0
    assert idle == [env.menu_len - 1, 0], "bench must send the [Idle, Silent] pair (spec 028)"
    assert 0 <= idle[0] < env.menu_len and 0 <= idle[1] < env.head_len
    obs, rewards, terminations, truncations, infos = env.step({a: idle for a in env.possible_agents})
    assert set(obs) == set(env.possible_agents)
    assert not any(terminations.values()) and not any(truncations.values())


def test_bench_runs_end_to_end_at_small_scale():
    bench = load_example("bench")
    assert bench.bench_single(steps=20) > 0
    assert bench.bench_vector(steps=10, worlds=2) > 0


def test_random_rollout_samples_legal_pairs_and_reproduces():
    rr = load_example("random_rollout")
    env = cloudkitty.ParallelEnv(horizon=3)
    _, infos = env.reset(seed=7)
    rng = np.random.default_rng(0)
    mask = np.asarray(infos[env.possible_agents[0]]["mask"], dtype=np.uint8)
    for _ in range(20):
        pair = rr.legal_pair(mask, env.menu_len, rng)
        # one [activity, message] pair, each half drawn from its own half of the mask (spec 028)
        assert isinstance(pair, list) and len(pair) == 2, "rollout must send a legal [activity, message] pair (spec 028)"
        a, m = pair
        assert a < env.menu_len and mask[a] == 1 and mask[env.menu_len + m] == 1, \
            "rollout must send a legal [activity, message] pair (spec 028)"
    first, second = rr.rollout(seed=7, steps=15), rr.rollout(seed=7, steps=15)
    assert first == second and first["decisions"] > 0 and first["steps"] == 15
