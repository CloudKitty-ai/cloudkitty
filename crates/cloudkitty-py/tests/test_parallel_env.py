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


def test_unseeded_reset_gives_fresh_reproducible_episodes():
    # Spec 014 review: reset(seed=s) then bare reset() must give a NEW
    # episode (not replay s forever), and the whole sequence must replay
    # from the same starting seed.
    def rollout(env):
        obs, infos = env.reset()
        return {a: obs[a].tobytes() for a in env.possible_agents}

    a = cloudkitty.ParallelEnv(horizon=20)
    first_obs, _ = a.reset(seed=7)
    first = {k: v.tobytes() for k, v in first_obs.items()}
    second = rollout(a)
    third = rollout(a)
    assert second != first, "bare reset() must not replay the seeded episode"
    assert third != second, "each bare reset() advances again"

    b = cloudkitty.ParallelEnv(horizon=20)
    b.reset(seed=7)
    second_again = rollout(b)
    assert second_again == second, "the fresh-seed chain replays exactly"

    # Explicit seeds still reproduce exactly.
    c = cloudkitty.ParallelEnv(horizon=20)
    c_obs, _ = c.reset(seed=7)
    assert {k: v.tobytes() for k, v in c_obs.items()} == first


def test_non_canonical_agent_names_are_rejected():
    # Spec 014 review: "kitty_01" must not silently alias "kitty_1".
    env = make_env()
    env.reset(seed=2)
    agents = env.possible_agents
    actions = {a: 39 for a in agents[1:]}
    actions["kitty_01"] = 39
    with pytest.raises(ValueError):
        env.step(actions)


def test_vector_env_bad_index_leaves_the_batch_in_sync():
    # Spec 014 review: an out-of-range index raises BEFORE any world steps,
    # so a caught exception cannot desynchronize the batch.
    env = cloudkitty.VectorEnv(2, horizon=10, workers=2)
    env.reset(seeds=[1, 2])
    agents = env.possible_agents

    bad = {a: [39, 39] for a in agents}
    bad[agents[0]] = [40, 39]
    with pytest.raises(IndexError):
        env.step(bad)

    # All worlds still in lockstep: truncations flip together at horizon.
    good = {a: [39, 39] for a in agents}
    for step_index in range(10):
        obs, rewards, terminations, truncations, infos = env.step(good)
        flags = set(truncations[a].tolist()[i] for a in agents for i in range(2))
        assert flags == ({True} if step_index == 9 else {False}), (
            f"batch desynced at step {step_index}: {truncations}"
        )


def test_vector_env_unseeded_reset_advances_every_world():
    env = cloudkitty.VectorEnv(2, horizon=10, workers=2)
    obs1, infos1 = env.reset(seeds=[5, 6])
    obs2, infos2 = env.reset()
    agent = env.possible_agents[0]
    assert obs1[agent].tobytes() != obs2[agent].tobytes()
    # And the stacked info schema carries the full field set.
    info = infos2[agent]
    assert set(info) == {
        "mask",
        "decision_seed",
        "survived",
        "applied_action",
        "applied_action_name",
        "provenance",
    }
    assert info["survived"].tolist() == [-1, -1], "no proposal at reset"
