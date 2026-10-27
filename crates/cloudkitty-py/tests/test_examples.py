"""The examples run on the committed engine.

Spec 014's quickstart §3 cites examples/bench.py as the SC-003
reproduction, and the tag-time checks do not exercise examples; this is
the CI guard (the python-surface job runs this directory). bench.py
drifted once already: scalar actions and a hard-coded Idle row from a
menu that no longer exists (found 2026-10-26, spec 028 pairs required).
"""

import importlib.util
from pathlib import Path

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
