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


def test_vector_env_constructor_seeds_run_verbatim():
    # Spec 014 second review: VectorEnv(n, seeds=[...]) + bare reset() must
    # run exactly those seeds (once), matching an explicit reset(seeds=...);
    # only subsequent unseeded resets advance the fresh-seed chains.
    agent_bytes = lambda obs, agents: {a: obs[a].tobytes() for a in agents}

    a = cloudkitty.VectorEnv(2, seeds=[5, 6], horizon=10, workers=2)
    obs_a, _ = a.reset()
    b = cloudkitty.VectorEnv(2, horizon=10, workers=2)
    obs_b, _ = b.reset(seeds=[5, 6])
    agents = a.possible_agents
    assert agent_bytes(obs_a, agents) == agent_bytes(obs_b, agents), (
        "constructor seeds must run verbatim on the first unseeded reset"
    )

    # The second unseeded reset advances the chains — and identically on
    # both environments (the chain is owned by each episode).
    obs_a2, _ = a.reset()
    obs_b2, _ = b.reset()
    assert agent_bytes(obs_a2, agents) != agent_bytes(obs_a, agents)
    assert agent_bytes(obs_a2, agents) == agent_bytes(obs_b2, agents)


def test_vector_env_refuses_step_before_reset():
    # Spec 014 third review: a fresh VectorEnv holds N config-seed clones
    # of one world — stepping them as "independent" worlds would silently
    # violate the contract, so step refuses until reset deals real seeds.
    env = cloudkitty.VectorEnv(2, seeds=[5, 6], horizon=10, workers=2)
    agents = env.possible_agents
    with pytest.raises(RuntimeError, match="reset"):
        env.step({a: [39, 39] for a in agents})

    # The refused step did not consume the constructor seeds: the first
    # unseeded reset still runs them verbatim.
    obs_a, _ = env.reset()
    b = cloudkitty.VectorEnv(2, horizon=10, workers=2)
    obs_b, _ = b.reset(seeds=[5, 6])
    assert all(obs_a[a].tobytes() == obs_b[a].tobytes() for a in agents)
    env.step({a: [39, 39] for a in agents})


def test_vector_env_rejects_unknown_and_scripted_agent_actions():
    # Spec 014 third review: VectorEnv applies the same guard ParallelEnv
    # does — an action for a scripted or out-of-roster agent raises rather
    # than being silently dropped (a typo must never corrupt training).
    env = cloudkitty.VectorEnv(2, horizon=10, workers=2)
    env.reset(seeds=[1, 2])
    agents = env.possible_agents
    scripted = cloudkitty.VectorEnv(
        2, horizon=10, workers=2, control={agents[0]: "needs_driven"}
    )
    scripted.reset(seeds=[1, 2])

    with pytest.raises(ValueError, match="not externally controlled"):
        env.step({**{a: [39, 39] for a in agents}, "kitty_999": [0, 0]})
    with pytest.raises(ValueError, match="not externally controlled"):
        scripted.step({a: [39, 39] for a in agents})


def test_omitted_action_reports_survived_none():
    # Spec 014 second review (contract: tri-state survived): an agent whose
    # action is lawfully omitted gets idle substituted and survived=None —
    # neither a pass nor a failure verdict.
    env = make_env()
    env.reset(seed=8)
    agents = env.possible_agents
    actions = {a: 39 for a in agents[1:]}  # agents[0] omitted
    obs, rewards, terminations, truncations, infos = env.step(actions)
    assert infos[agents[0]]["survived"] is None
    assert infos[agents[0]]["provenance"] == "substituted_idle"
    for agent in agents[1:]:
        assert infos[agent]["survived"] in (True, False)


def test_vector_batch_matches_parallel_solo_streams():
    # Round-one review: the contract promises a VectorEnv batch is N fully
    # independent worlds, and the Rust layer tests that against solo
    # Episodes -- but nothing at this surface compared the batch stream
    # against ParallelEnv stepping the same seeds solo. Observations,
    # rewards, truncations, and masks must match bit-for-bit.
    seeds = [11, 12]
    horizon = 15
    batch = cloudkitty.VectorEnv(len(seeds), horizon=horizon, workers=2)
    batch_obs, batch_infos = batch.reset(seeds=seeds)
    agents = batch.possible_agents

    solos = []
    for world, seed in enumerate(seeds):
        env = cloudkitty.ParallelEnv(horizon=horizon)
        obs, infos = env.reset(seed=seed)
        for agent in agents:
            assert obs[agent].tobytes() == batch_obs[agent][world].tobytes(), (
                f"world {world} diverged from its solo run at reset ({agent})"
            )
        solos.append(env)

    for step_index in range(horizon):
        actions = {a: (step_index + i) % 40 for i, a in enumerate(agents)}
        batch_actions = {a: [actions[a]] * len(seeds) for a in agents}
        b_obs, b_rew, b_term, b_trunc, b_infos = batch.step(batch_actions)
        for world, env in enumerate(solos):
            s_obs, s_rew, s_term, s_trunc, s_infos = env.step(actions)
            for agent in agents:
                assert s_obs[agent].tobytes() == b_obs[agent][world].tobytes(), (
                    f"world {world} observations diverged at step {step_index}"
                )
                assert s_rew[agent] == b_rew[agent][world], (
                    f"world {world} rewards diverged at step {step_index}"
                )
                assert s_trunc[agent] == b_trunc[agent][world], (
                    f"world {world} truncations diverged at step {step_index}"
                )
                assert (
                    s_infos[agent]["mask"].tobytes()
                    == b_infos[agent]["mask"][world].tobytes()
                ), f"world {world} masks diverged at step {step_index}"


def test_elements_positions_types_and_determinism():
    env = make_env()
    env.reset(seed=7)
    elems = env.elements()
    assert len(elems) > 0

    known = {"Water", "Chow", "Bug", "Greeble", "Sunbeam"}
    ids = [eid for eid, _, _, _ in elems]
    assert len(ids) == len(set(ids)), "element ids are unique"
    for eid, kind, x, y in elems:
        assert isinstance(eid, int) and eid >= 0
        assert kind in known
        assert isinstance(x, int) and x >= 0
        assert isinstance(y, int) and y >= 0
    kinds = {kind for _, kind, _, _ in elems}
    assert "Water" in kinds, "water minimums guarantee at least one"
    assert "Greeble" in kinds, "greebles are never filtered from an API"

    # Same call twice without stepping: identical (no hidden advance).
    assert env.elements() == elems

    # Same seed, fresh env: identical spawn (the deterministic fishbowl).
    twin = make_env()
    twin.reset(seed=7)
    assert twin.elements() == elems

    # The surface is live, not a reset snapshot: greebles wander every
    # tick, so a few steps must move at least one element.
    rng = np.random.default_rng(0)
    infos = env.reset(seed=7)[1]
    agents = env.possible_agents
    for _ in range(10):
        actions = {a: masked_choice(infos[a]["mask"], rng) for a in agents}
        infos = env.step(actions)[4]
    after = {eid: (x, y) for eid, _, x, y in env.elements()}
    before = {eid: (x, y) for eid, _, x, y in elems}
    moved = [eid for eid in before if eid in after and after[eid] != before[eid]]
    assert moved, "ten ticks of greebles never moving would be a frozen world"
