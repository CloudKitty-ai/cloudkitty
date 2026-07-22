"""Optional PettingZoo API conformance (spec 014 T032, research.md R10):
runs only when the pettingzoo package is installed; skips cleanly when not.
The convention is duck-typed — this check is a bonus, never a requirement.
"""

import pytest

pettingzoo = pytest.importorskip("pettingzoo")

import cloudkitty


def test_parallel_api_conformance():
    from pettingzoo.test import parallel_api_test

    env = cloudkitty.ParallelEnv(horizon=50)
    parallel_api_test(env, num_cycles=120)
