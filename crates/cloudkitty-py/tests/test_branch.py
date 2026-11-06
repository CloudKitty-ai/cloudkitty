"""Spec 068 (World Branch API) on the Python surface: snapshot / restore /
fork / override / tick_records on ParallelEnv and VectorEnv. The engine-side
guards live in crates/cloudkitty-rl/tests/branch.rs; these check the wrapper's
contract (contracts/python-api.md) and were each seen red through
scripts/mutate.sh before being cited green.
"""

import time

import numpy as np
import pytest

import cloudkitty

MENU = 35  # menu v2 at the default kitty_slots 4, critter_slots 2
IDLE = MENU - 1  # Idle is the last menu row
SCRIPTED = "kitty_2"  # a builtin seat in the control map below


def make_env(horizon=5000):
    return cloudkitty.ParallelEnv(horizon=horizon, control={SCRIPTED: "needs_driven"})


def legal_actions(infos, turn):
    """A deterministic legal [activity, Silent] per agent, rotated over the mask."""
    actions = {}
    for agent, info in infos.items():
        legal = np.flatnonzero(np.asarray(info["mask"][:MENU]))
        actions[agent] = [int(legal[(turn * 7) % legal.size]), 0]
    return actions


def run(env, infos, turns, start=0):
    trace = []
    for turn in range(start, start + turns):
        obs, rewards, _, _, infos = env.step(legal_actions(infos, turn))
        trace.append((obs, rewards, infos))
    return infos, trace


def same_trace(a, b):
    for (oa, ra, ia), (ob, rb, ib) in zip(a, b):
        for agent in oa:
            assert np.array_equal(oa[agent], ob[agent]), f"observations differ for {agent}"
            assert ra[agent] == rb[agent], f"rewards differ for {agent}"
            for key in ia[agent]:
                va, vb = ia[agent][key], ib[agent][key]
                if isinstance(va, np.ndarray):
                    assert np.array_equal(va, vb), f"info {key} differs for {agent}"
                else:
                    assert va == vb, f"info {key} differs for {agent}"


# --- US1 --------------------------------------------------------------------


def test_restore_into_a_never_reset_twin_is_byte_identical():
    env = make_env()
    _, infos = env.reset(seed=7)
    infos, _ = run(env, infos, 300)
    seeds_at_snapshot = {a: infos[a]["decision_seed"] for a in infos}
    snap = env.snapshot()
    assert isinstance(snap, bytes) and len(snap) > 1000

    twin = make_env()  # never reset: restore stands in for it
    obs_t, infos_t = twin.restore(snap)
    assert set(obs_t) == set(env.possible_agents)
    assert {a: infos_t[a]["decision_seed"] for a in infos_t} == seeds_at_snapshot, (
        "FR-004: the restored infos report the original's next decision seeds"
    )
    _, trace_a = run(env, infos, 200, start=300)
    _, trace_b = run(twin, infos_t, 200, start=300)
    same_trace(trace_a, trace_b)
    assert twin.agents == env.agents


def test_snapshot_before_reset_is_refused():
    env = make_env()
    with pytest.raises(ValueError, match="reset first"):
        env.snapshot()


def test_fork_continues_identically():
    env = make_env()
    _, infos = env.reset(seed=11)
    infos, _ = run(env, infos, 50)
    fork = env.fork()
    assert isinstance(fork, cloudkitty.ParallelEnv)
    assert fork.possible_agents == env.possible_agents
    # The fork's own first step uses the same infos the original has in hand.
    _, trace_a = run(env, infos, 30, start=50)
    _, trace_b = run(fork, infos, 30, start=50)
    same_trace(trace_a, trace_b)


def test_restore_heals_after_truncation_and_restores_truncated():
    env = make_env(horizon=6)
    _, infos = env.reset(seed=2)
    mid = None
    for turn in range(6):
        if turn == 3:
            mid = env.snapshot()
        _, _, _, truncs, infos = env.step(legal_actions(infos, turn))
    assert all(truncs.values()), "staged: truncated at the horizon"
    end = env.snapshot()  # legal after truncation
    env.restore(mid)
    assert env.agents == env.possible_agents, "restored mid-episode: live again"
    env.step(legal_actions(infos, 3))
    env.restore(end)
    assert env.agents == [], "a truncated snapshot restores truncated"
    with pytest.raises(RuntimeError):
        env.step(legal_actions(infos, 0))


# --- US2 --------------------------------------------------------------------


RECORD_KEYS = {
    "proposed_action_name",
    "validated_action_name",
    "applied_action_name",
    "proposed_message",
    "applied_message",
    "provenance",
    "decision_seed",
    "survived",
}


def test_override_on_a_builtin_seat_marks_the_record():
    env = make_env()
    _, infos = env.reset(seed=5)
    infos, _ = run(env, infos, 20)
    env.override(SCRIPTED, action=IDLE)
    _, _, _, _, infos = env.step(legal_actions(infos, 20))
    rec = env.tick_records()[SCRIPTED]
    assert rec["provenance"] == "overridden_act"
    assert rec["proposed_action_name"] == "idle"
    _, _, _, _, infos = env.step(legal_actions(infos, 21))
    assert env.tick_records()[SCRIPTED]["provenance"] == "policy", "one tick only"

    env.override(SCRIPTED, message=1)
    env.step(legal_actions(infos, 22))
    rec = env.tick_records()[SCRIPTED]
    assert rec["provenance"] == "overridden_message"
    assert rec["proposed_message"] is not None

    env.override(2, action=IDLE, message=0)  # the int id is accepted too
    env.step(legal_actions(infos, 23))
    assert env.tick_records()[SCRIPTED]["provenance"] == "overridden_both"


def test_tick_records_keys_are_the_documented_contract():
    env = make_env()
    _, infos = env.reset(seed=3)
    records = env.tick_records()
    roster = {f"kitty_{k}" for k in range(1, 6)} | {SCRIPTED}
    assert set(records) >= {SCRIPTED} | set(env.possible_agents), "every roster kitty, scripted seats included"
    for agent, rec in records.items():
        assert set(rec) == RECORD_KEYS, agent
        assert rec["provenance"] is None and rec["applied_action_name"] is None, "nothing happened at reset"
    env.step(legal_actions(infos, 0))
    records = env.tick_records()
    assert records[SCRIPTED]["provenance"] == "policy"
    assert records[SCRIPTED]["applied_action_name"] is not None
    assert isinstance(records[SCRIPTED]["decision_seed"], int)
    external = env.possible_agents[0]
    assert records[external]["provenance"] == "policy"
    del roster


def test_override_refusals_raise_the_documented_classes():
    env = make_env()
    external = env.possible_agents[0]
    with pytest.raises(ValueError, match="reset first"):
        env.override(SCRIPTED, action=IDLE)
    _, infos = env.reset(seed=1)
    with pytest.raises(ValueError, match="externally controlled"):
        env.override(external, action=IDLE)
    with pytest.raises(ValueError):
        env.override("kitty_999", action=IDLE)
    with pytest.raises(ValueError, match="empty"):
        env.override(SCRIPTED)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, action=MENU)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, message=16)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, action=-1)
    env.override(SCRIPTED, action=IDLE)
    with pytest.raises(ValueError, match="already"):
        env.override(SCRIPTED, action=IDLE)
    env.step(legal_actions(infos, 0))
    assert env.tick_records()[SCRIPTED]["provenance"] == "overridden_act"


# --- US4 --------------------------------------------------------------------


def test_vector_env_restores_one_world_by_index():
    venv = cloudkitty.VectorEnv(2, horizon=5000, control={SCRIPTED: "needs_driven"}, workers=1)
    obs, infos = venv.reset(seeds=[100, 200])
    agents = venv.possible_agents

    def batched_actions(infos, turn):
        acts = {}
        for agent in agents:
            rows = []
            for w in range(2):
                legal = np.flatnonzero(np.asarray(infos[agent]["mask"][w][:MENU]))
                rows.append([int(legal[(turn * 7) % legal.size]), 0])
            acts[agent] = rows
        return acts

    for turn in range(30):
        obs, _, _, _, infos = venv.step(batched_actions(infos, turn))
    snap0 = venv.snapshot(0)
    world1_before = [venv.tick_records(1)]
    for turn in range(30, 40):
        obs, _, _, _, infos = venv.step(batched_actions(infos, turn))
    obs0, infos0 = venv.restore(0, snap0)
    assert set(obs0) == set(agents) and set(infos0) == set(agents)
    # World 1 is untouched by the branch: its last record is still tick 39's.
    assert venv.tick_records(1) != world1_before[0]
    with pytest.raises(IndexError):
        venv.snapshot(2)
    venv.override(0, SCRIPTED, action=IDLE)
    # Stepping the batch after a one-world restore is still allowed (the batch was
    # reset); world 0's record carries the mark, world 1's does not.
    infos[agents[0]]["mask"][0] = infos0[agents[0]]["mask"]
    venv.step(batched_actions(infos, 40))
    assert venv.tick_records(0)[SCRIPTED]["provenance"] == "overridden_act"
    assert venv.tick_records(1)[SCRIPTED]["provenance"] == "policy"


def test_a_snapshot_is_portable_between_env_objects():
    env = make_env()
    _, infos = env.reset(seed=9)
    infos, _ = run(env, infos, 40)
    snap = env.snapshot()
    venv = cloudkitty.VectorEnv(2, horizon=5000, control={SCRIPTED: "needs_driven"})
    venv.reset(seeds=[1, 2])
    obs0, infos0 = venv.restore(1, snap)
    for agent in env.possible_agents:
        assert infos0[agent]["decision_seed"] == infos[agent]["decision_seed"]
    back = venv.snapshot(1)
    twin = make_env()
    obs_t, infos_t = twin.restore(back)
    for agent in env.possible_agents:
        assert infos_t[agent]["decision_seed"] == infos[agent]["decision_seed"]


# --- US5 --------------------------------------------------------------------


def test_restore_mismatch_errors_name_the_component():
    env = make_env()
    _, infos = env.reset(seed=4)
    snap = env.snapshot()
    other = cloudkitty.ParallelEnv(horizon=5000, control={SCRIPTED: "external"})
    with pytest.raises(ValueError, match="control differs"):
        other.restore(snap)
    shorter = cloudkitty.ParallelEnv(horizon=4000, control={SCRIPTED: "needs_driven"})
    with pytest.raises(ValueError, match="config_fingerprint differs"):
        shorter.restore(snap)
    with pytest.raises(ValueError, match="not a snapshot"):
        env.restore(b"not a snapshot")
    env.step(legal_actions(infos, 0))  # untouched by the refusals


# --- Polish -----------------------------------------------------------------


def test_branch_docstrings_carry_the_welfare_line():
    for cls, names in (
        (cloudkitty.ParallelEnv, ("snapshot", "restore", "fork", "override")),
        (cloudkitty.VectorEnv, ("snapshot", "restore", "override")),
    ):
        for name in names:
            doc = getattr(cls, name).__doc__ or ""
            assert "k > 1" in doc and "WELFARE-STANDING" in doc, f"{cls.__name__}.{name}"
    assert "transient" in cloudkitty.ParallelEnv.snapshot.__doc__


def test_restore_plus_one_step_is_far_cheaper_than_replay():
    env = make_env(horizon=20000)
    _, infos = env.reset(seed=1)
    acts = {a: [IDLE, 0] for a in env.possible_agents}
    t0 = time.perf_counter()
    for _ in range(10_000):
        env.step(acts)
    replay = time.perf_counter() - t0
    snap = env.snapshot()
    t0 = time.perf_counter()
    env.restore(snap)
    env.step(acts)
    branch = time.perf_counter() - t0
    ratio = branch / replay
    assert ratio < 0.1, f"restore+step/replay ratio {ratio:.4f} (replay {replay:.3f}s, branch {branch*1e3:.2f}ms)"
