"""Spec 068 (World Branch API) on the Python surface: snapshot / restore /
fork / override / tick_records on ParallelEnv and VectorEnv. The engine-side
guards live in crates/cloudkitty-rl/tests/branch.rs; these check the wrapper's
contract (specs/068-world-branch/contracts/python-api.md). Every test here was
seen red through scripts/mutate.sh before being cited green (tasks.md lists
the mutant per test).
"""

import time

import numpy as np
import pytest

import cloudkitty

MENU = 35  # menu v2 at the default kitty_slots 4, critter_slots 2 (pinned like test_parallel_env.py)
IDLE = MENU - 1  # Idle is the last menu row
SCRIPTED = "kitty_2"  # a builtin seat in the control map below
CONTROL = {SCRIPTED: "needs_driven"}


def make_env(horizon=5000):
    return cloudkitty.ParallelEnv(horizon=horizon, control=CONTROL)


def make_venv(n=2, horizon=5000, **kw):
    return cloudkitty.VectorEnv(n, horizon=horizon, control=CONTROL, **kw)


def legal_actions(infos, turn):
    """A deterministic legal [activity, Silent] per agent, rotated over the mask."""
    actions = {}
    for agent, info in infos.items():
        legal = np.flatnonzero(np.asarray(info["mask"][:MENU]))
        actions[agent] = [int(legal[(turn * 7) % legal.size]), 0]
    return actions


def batched_actions(infos, agents, turn, n=2):
    acts = {}
    for agent in agents:
        rows = []
        for w in range(n):
            legal = np.flatnonzero(np.asarray(infos[agent]["mask"][w][:MENU]))
            rows.append([int(legal[(turn * 7) % legal.size]), 0])
        acts[agent] = rows
    return acts


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


def roster_of(env):
    """Every roster kitty's agent name: the external seats plus the scripted one."""
    return set(env.possible_agents) | {SCRIPTED}


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
    assert twin.agents == env.agents, "the restored twin is live"


def test_snapshot_before_reset_is_refused():
    env = make_env()
    with pytest.raises(ValueError, match="reset first"):
        env.snapshot()
    with pytest.raises(ValueError, match="reset first"):
        env.fork()


def test_fork_continues_identically():
    env = make_env()
    _, infos = env.reset(seed=11)
    infos, _ = run(env, infos, 50)
    fork = env.fork()
    assert isinstance(fork, cloudkitty.ParallelEnv)
    assert fork.possible_agents == env.possible_agents
    assert fork.agents == env.agents, "the fork is live"
    assert fork.snapshot() == env.snapshot(), "the fork holds the same state"
    _, trace_a = run(env, infos, 30, start=50)
    _, trace_b = run(fork, infos, 30, start=50)
    same_trace(trace_a, trace_b)


def test_restore_after_truncation_and_a_truncated_snapshot_restores_truncated():
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
    with pytest.raises(ValueError, match="reset first"):
        env.override(SCRIPTED, action=IDLE)


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
    _, _, _, _, infos = env.step(legal_actions(infos, 22))
    rec = env.tick_records()[SCRIPTED]
    assert rec["provenance"] == "overridden_message"
    assert rec["proposed_message"] == "want_eat", "head index 1 is want_eat"

    env.override(2, action=IDLE, message=0)  # the int id is accepted too
    env.step(legal_actions(infos, 23))
    rec = env.tick_records()[SCRIPTED]
    assert rec["provenance"] == "overridden_both"
    assert rec["proposed_action_name"] == "idle"
    assert rec["proposed_message"] is None, "message index 0 is Silent"


def test_tick_records_keys_are_the_documented_contract():
    env = make_env()
    _, infos = env.reset(seed=3)
    records = env.tick_records()
    assert set(records) == roster_of(env), "every roster kitty, scripted seats included"
    for agent, rec in records.items():
        assert set(rec) == RECORD_KEYS, agent
        assert all(v is None for v in rec.values()), f"{agent}: nothing happened at reset"
    env.step(legal_actions(infos, 0))
    records = env.tick_records()
    assert set(records) == roster_of(env)
    assert records[SCRIPTED]["provenance"] == "policy"
    assert records[SCRIPTED]["applied_action_name"] is not None
    assert isinstance(records[SCRIPTED]["decision_seed"], int)
    external = env.possible_agents[0]
    assert records[external]["provenance"] == "policy"
    assert records[external]["survived"] in (True, False)


def test_override_refusals_raise_the_documented_classes():
    env = make_env()
    external = env.possible_agents[0]
    with pytest.raises(ValueError, match="reset first"):
        env.override(SCRIPTED, action=IDLE)
    _, infos = env.reset(seed=1)
    snap = env.snapshot()
    with pytest.raises(ValueError, match="externally controlled"):
        env.override(external, action=IDLE)
    with pytest.raises(ValueError, match="roster"):
        env.override("kitty_999", action=IDLE)
    with pytest.raises(ValueError, match="name an action, a message, or both"):
        env.override(SCRIPTED)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, action=MENU)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, message=16)
    with pytest.raises(IndexError):
        env.override(SCRIPTED, action=-1)
    env.override(SCRIPTED, action=IDLE)
    with pytest.raises(ValueError, match="already has a pending override"):
        env.override(SCRIPTED, action=IDLE)
    assert env.snapshot() == snap, "no refusal touched the environment"
    env.step(legal_actions(infos, 0))
    assert env.tick_records()[SCRIPTED]["provenance"] == "overridden_act"


# --- US4 --------------------------------------------------------------------


def test_vector_env_restores_one_world_by_index():
    venv = make_venv(workers=None)  # one worker per world: routing exercised
    obs, infos = venv.reset(seeds=[100, 200])
    agents = venv.possible_agents
    for turn in range(30):
        obs, _, _, _, infos = venv.step(batched_actions(infos, agents, turn))
    snap0 = venv.snapshot(0)
    for turn in range(30, 40):
        obs, _, _, _, infos = venv.step(batched_actions(infos, agents, turn))
    world1_before = venv.tick_records(1)
    obs0, infos0 = venv.restore(0, snap0)
    assert set(obs0) == set(agents) and set(infos0) == set(agents)
    assert venv.tick_records(1) == world1_before, "world 1's record is untouched by world 0's restore"
    assert all(v is None for v in venv.tick_records(0)[SCRIPTED].values()), "world 0's record is cleared"
    with pytest.raises(IndexError):
        venv.snapshot(2)
    with pytest.raises(IndexError):
        venv.snapshot(-1)
    venv.override(0, SCRIPTED, action=IDLE)
    for agent in agents:  # world 0's masks are the restored tick's now
        infos[agent]["mask"][0] = infos0[agent]["mask"]
    venv.step(batched_actions(infos, agents, 40))
    assert venv.tick_records(0)[SCRIPTED]["provenance"] == "overridden_act"
    assert venv.tick_records(1)[SCRIPTED]["provenance"] == "policy"


def test_vector_env_refuses_like_the_single_world_env():
    venv = make_venv()
    with pytest.raises(ValueError, match="reset first"):
        venv.snapshot(0)
    with pytest.raises(ValueError, match="reset first"):
        venv.override(0, SCRIPTED, action=IDLE)
    # restore(i) before the first reset establishes THAT world only.
    donor = make_env()
    _, infos_d = donor.reset(seed=4)
    venv.restore(1, donor.snapshot())
    assert isinstance(venv.snapshot(1), bytes)
    with pytest.raises(ValueError, match="reset first"):
        venv.snapshot(0)
    venv.override(1, SCRIPTED, action=IDLE)  # world 1 has a decision window
    with pytest.raises(RuntimeError, match="reset"):
        venv.step({a: [[IDLE, 0], [IDLE, 0]] for a in venv.possible_agents})
    # After truncation the world's decision window is closed, like ParallelEnv.
    short = make_venv(horizon=3)
    obs, infos = short.reset(seeds=[1, 2])
    agents = short.possible_agents
    for turn in range(3):
        short.step(batched_actions(infos, agents, turn))
    with pytest.raises(ValueError, match="reset first"):
        short.override(0, SCRIPTED, action=IDLE)
    assert isinstance(short.snapshot(0), bytes), "a truncated world can still be snapshotted"


def test_a_snapshot_is_portable_between_env_objects():
    env = make_env()
    _, infos = env.reset(seed=9)
    infos, _ = run(env, infos, 40)
    snap = env.snapshot()
    venv = make_venv()
    venv.reset(seeds=[1, 2])
    obs0, infos0 = venv.restore(1, snap)
    for agent in env.possible_agents:
        assert infos0[agent]["decision_seed"] == infos[agent]["decision_seed"]
    back = venv.snapshot(1)
    twin = make_env()
    obs_t, infos_t = twin.restore(back)
    for agent in env.possible_agents:
        assert infos_t[agent]["decision_seed"] == infos[agent]["decision_seed"]
    assert twin.snapshot() == env.snapshot(), "the round trip is byte-identical"


# --- US5 --------------------------------------------------------------------


def test_restore_mismatch_errors_name_the_component():
    env = make_env()
    _, infos = env.reset(seed=4)
    snap = env.snapshot()
    other = cloudkitty.ParallelEnv(horizon=5000, control={SCRIPTED: "external"})
    other.reset(seed=4)
    other_snap = other.snapshot()
    with pytest.raises(ValueError, match="control differs: snapshot kitty_2=needs_driven, this environment kitty_2=external"):
        other.restore(snap)
    assert other.snapshot() == other_snap, "the refused environment is untouched"
    shorter = cloudkitty.ParallelEnv(horizon=4000, control=CONTROL)
    with pytest.raises(ValueError, match="config_digest differs"):
        shorter.restore(snap)
    tampered = snap.replace(cloudkitty.ENGINE_COMMIT.encode(), b"deadbeef", 1)
    with pytest.raises(ValueError, match="engine_commit differs"):
        env.restore(tampered)
    with pytest.raises(ValueError, match="not a snapshot"):
        env.restore(b"not a snapshot")
    assert env.snapshot() == snap, "untouched by the refusals"
    assert env.agents == env.possible_agents
    env.step(legal_actions(infos, 0))


# --- Polish -----------------------------------------------------------------


def test_branch_docstrings_carry_the_welfare_line():
    for cls, names in (
        (cloudkitty.ParallelEnv, ("snapshot", "restore", "fork", "override")),
        (cloudkitty.VectorEnv, ("snapshot", "restore", "override")),
    ):
        for name in names:
            doc = getattr(cls, name).__doc__ or ""
            assert "k > 1" in doc and "WELFARE-STANDING" in doc, f"{cls.__name__}.{name}"
    for cls in (cloudkitty.ParallelEnv, cloudkitty.VectorEnv):
        assert "transient token" in cls.snapshot.__doc__, cls.__name__


def test_restore_plus_one_step_is_far_cheaper_than_replay():
    env = make_env(horizon=20000)
    _, infos = env.reset(seed=1)
    acts = {a: [IDLE, 0] for a in env.possible_agents}
    t0 = time.perf_counter()
    for _ in range(10_000):
        env.step(acts)
    replay = time.perf_counter() - t0
    snap = env.snapshot()
    branch = min(_timed_restore_step(env, snap, acts) for _ in range(5))
    ratio = branch / replay
    assert ratio < 0.1, f"restore+step/replay ratio {ratio:.4f} (replay {replay:.3f}s, branch {branch*1e3:.2f}ms)"


def _timed_restore_step(env, snap, acts):
    t0 = time.perf_counter()
    env.restore(snap)
    env.step(acts)
    return time.perf_counter() - t0
