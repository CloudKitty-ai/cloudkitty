"""Smoke tests for the PettingZoo-parallel surface (spec 014 T029):
shapes, bounds, bookkeeping — terminations always false, truncation
exactly at the horizon, one broadcast team scalar, documented info keys.
"""

import numpy as np
import pytest

import cloudkitty


def make_env(horizon=25):
    return cloudkitty.ParallelEnv(horizon=horizon)


def masked_choice(mask, rng):
    legal = np.flatnonzero(np.asarray(mask, dtype=np.uint8))
    assert legal.size > 0, "the mask is never all-zero"
    return int(rng.choice(legal))


def test_reset_shapes_and_bounds():
    env = make_env()
    obs, infos = env.reset(seed=7)
    agents = env.possible_agents
    assert agents == sorted(agents)
    assert set(obs) == set(agents)
    for agent in agents:
        vec = obs[agent]
        assert vec.dtype == np.float32
        assert vec.ndim == 1 and vec.size > 100
        assert np.isfinite(vec).all()
        assert vec.min() >= -1.0 and vec.max() <= 4.0
        info = infos[agent]
        assert set(info) == {
            "applied_action",
            "applied_action_name",
            "survived",
            "mask",
            "decision_seed",
            "provenance",
        }
        mask = info["mask"]
        assert mask.dtype == np.uint8 and mask.shape == (40,)
        assert mask.any(), "never all-zero"
        assert info["applied_action"] is None, "nothing applied at reset"
        assert isinstance(info["decision_seed"], int)


def test_step_bookkeeping_and_truncation_exactly_at_horizon():
    horizon = 12
    env = make_env(horizon=horizon)
    obs, infos = env.reset(seed=3)
    rng = np.random.default_rng(0)
    agents = env.possible_agents

    for step_index in range(horizon):
        actions = {a: masked_choice(infos[a]["mask"], rng) for a in agents}
        obs, rewards, terminations, truncations, infos = env.step(actions)
        expect_truncated = step_index == horizon - 1

        # One broadcast team scalar.
        values = {rewards[a] for a in agents}
        assert len(values) == 1
        assert all(np.isfinite(v) for v in values)

        for agent in agents:
            assert terminations[agent] is False, "kitties cannot die (Article II)"
            assert truncations[agent] is expect_truncated
            info = infos[agent]
            assert info["survived"] in (True, False)
            assert info["provenance"] in ("policy", "fallback", "substituted_idle")
            assert info["mask"].any()

    # Stepping past truncation is an error; reset rearms.
    with pytest.raises(RuntimeError):
        env.step({a: 39 for a in agents})
    assert env.agents == []
    obs, infos = env.reset(seed=4)
    assert env.agents == env.possible_agents


def test_out_of_range_raises_vacant_slots_do_not():
    env = make_env()
    _, infos = env.reset(seed=5)
    agents = env.possible_agents

    with pytest.raises(IndexError):
        env.step({agents[0]: 40, **{a: 39 for a in agents[1:]}})

    # Rest-with-kitty-slot-2 is vacant on the default roster (2 others):
    # decodes and lawfully resolves to idle — never a raise.
    env.reset(seed=5)
    obs, rewards, terminations, truncations, infos = env.step(
        {agents[0]: 7, **{a: 39 for a in agents[1:]}}
    )
    assert infos[agents[0]]["survived"] is False


def test_state_is_fixed_size_and_deterministic():
    env = make_env()
    env.reset(seed=9)
    s1 = env.state()
    s2 = env.state()
    assert s1.dtype == np.float32
    assert s1.shape == s2.shape
    assert (s1 == s2).all()


def test_mixed_control_and_full_roster_reward():
    env = cloudkitty.ParallelEnv(horizon=30, control={1: "needs_driven"})
    obs, infos = env.reset(seed=11)
    agents = env.possible_agents
    assert "kitty_1" not in agents, "scripted kitties are not agents"
    assert len(agents) >= 2

    obs, rewards, *_ = env.step({a: 39 for a in agents})
    values = {rewards[a] for a in agents}
    assert len(values) == 1


def test_spaces_are_described():
    env = make_env()
    agent = env.possible_agents[0]
    obs_space = env.observation_space(agent)
    act_space = env.action_space(agent)
    # gymnasium objects when available, plain dicts otherwise (duck-typed).
    try:
        import gymnasium

        assert act_space.n == 40
        assert obs_space.shape[0] > 100
    except ImportError:
        assert act_space["n"] == 40
        assert obs_space["shape"][0] > 100
