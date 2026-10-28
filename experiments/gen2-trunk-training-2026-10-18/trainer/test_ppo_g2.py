#!/usr/bin/env python3
"""Guard for train_ppo_g2's welfare-stop input (plain asserts,
python3 -B, exp-006 venv). The frozen §6 probe distress stop reads
engine distress flags out of the v2 global state; a wrong offset or a
dead comparison silently reads streak 0 forever and the stop never
fires — the exact failure this guard must catch.

Fixtures are REAL payloads: full-100 corpus state rows (bc-collect,
engine-emitted). world.rs record_distress: in_distress(kind) <=>
need >= thresholds.distress (90) at the same frozen snapshot, no
hysteresis — so the flags must equal a needs-threshold recomputation
cell for cell (away from the float boundary).
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ppo_env_g2  # noqa: E402
import train_ppo_g2 as tp  # noqa: E402

CORPUS = HERE.parents[1] / \
    "gen2-collection-driver-2026-10-14/results-raw/full-100"
STATE = np.load(CORPUS / "r00/config-00-rollout-00/state.npy",
                mmap_mode="r")


def test_distress_flags_match_engine_truth():
    # red: DISTRESS_OFF off by one, or the 0.5 comparison broken
    st = np.asarray(STATE, np.float32)              # (20000, 237)
    n = st.shape[0]
    k = st[:, :5 * tp.PER_KITTY].reshape(n, 5, tp.PER_KITTY)
    needs = k[:, :, :6]                              # NeedKind::ALL order
    flags = np.stack([tp.kitty_distress_flags(row) for row in st])
    want_any = (needs >= 0.9).any(axis=2)
    # exclude float-boundary rows (need within 1e-4 of 0.9 on any kind)
    clear = (np.abs(needs - 0.9) > 1e-4).all(axis=2)
    agree = (flags == want_any) | ~clear
    assert agree.all(), f"{(~agree).sum()} kitty-ticks disagree"
    # non-vacuous: the real rollout must contain both states
    assert flags.any() and not flags.all(), (int(flags.sum()), flags.size)


def test_max_streak_matches_run_length_reference():
    # red: the streak recurrence dropped or the flags inverted
    st = np.asarray(STATE, np.float32)
    flags = np.stack([tp.kitty_distress_flags(row) for row in st])  # (T, 5)
    streak = np.zeros(5, np.int64)
    worst = np.zeros(5, np.int64)
    for t in range(flags.shape[0]):                 # the probe's recurrence
        streak = np.where(flags[t], streak + 1, 0)
        worst = np.maximum(worst, streak)
    # independent reference: run lengths per kitty off the flag columns
    ref = []
    for j in range(5):
        col = flags[:, j].astype(int)
        best = cur = 0
        for v in col:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        ref.append(best)
    assert worst.tolist() == ref, (worst.tolist(), ref)
    assert max(ref) > 0, "rollout has no distress run at all (vacuous)"
    print(f"  (r00 max engine-distress streak per kitty: {ref})")


def test_every_slot_stripe_is_disjoint_and_claimed():
    # red: a slot whose seed stripe overlaps another run's, or a slot
    # whose stripe lies outside every claimed SEED-BANDS.md row
    import re
    rows = []
    for line in (HERE.parents[1] / "SEED-BANDS.md").read_text().splitlines():
        m = re.match(r"\|\s*(\d+)\s*[–-]\s*(\d+)\s*\|", line)
        if m:
            rows.append((int(m.group(1)), int(m.group(2))))
    assert len({seed for seed, _ in tp.SLOTS.values()}) == len(tp.SLOTS)
    stripes = sorted(tp.seed_stripe(idx) for _seed, idx in tp.SLOTS.values())
    for (a0, a1), (b0, _b1) in zip(stripes, stripes[1:]):
        assert a1 < b0, ("overlapping stripes", (a0, a1), b0)
    for s0, s1 in stripes:
        assert any(r0 <= s0 and s1 <= r1 for r0, r1 in rows), \
            ("unclaimed stripe", s0, s1)


def _needy_trunk_config(tmp: Path) -> str:
    """The trunk world with Miso on needy and its acknowledgement, the
    transform the needy fixtures in fixtures/ were recorded with."""
    src = Path(tp.TRUNK_TOML).read_text()
    line = 'behavior = "teacher"'
    i = src.index(line, src.index('name = "Miso"'))  # Miso's own line
    out = (src[:i] + 'behavior = "needy"' + src[i + len(line):]
           + '\n[welfare_hazard]\nacknowledged = ["needy"]\n')
    path = tmp / "needy-trunk.toml"
    path.write_text(out)
    return str(path)


def _needy_binding():
    import cloudkitty
    if hasattr(cloudkitty.ParallelEnv, "needy"):
        return True
    print("  (skip: this binding predates spec 067; run in the needy-set "
          "venv, experiments/needy-set-2026-10-28/BINDING.md)")
    return False


def test_ppo_runner_refuses_a_needy_world():
    # red: the runner's needy check removed; the roster-size assert then
    # fires instead, unnamed, and only because the seat count changed
    # (owner's observer-stream ruling 2026-10-27, B)
    if not _needy_binding():
        return
    with tempfile.TemporaryDirectory() as t:
        cfg = _needy_trunk_config(Path(t))
        try:
            ppo_env_g2.TrunkVecRunner(cfg, 1, 900001)
        except SystemExit as e:
            assert "refusing PPO rollouts beside needy seat(s) [1]" \
                in str(e), e
        else:
            raise AssertionError("PPO gathered rollouts beside a needy seat")


def test_frozen_rollouts_beside_a_needy_seat_still_run():
    # kept (the ruling refuses the update step, never the env): the
    # environment seats a needy world and steps its four external seats
    if not _needy_binding():
        return
    import cloudkitty
    with tempfile.TemporaryDirectory() as t:
        env = cloudkitty.ParallelEnv(_needy_trunk_config(Path(t)))
        obs, infos = env.reset(seed=900001)
        assert len(env.possible_agents) == 4, env.possible_agents
        for _ in range(3):
            acts = {a: [int(np.flatnonzero(np.asarray(infos[a]["mask"][:35]))[0]), 0]
                    for a in obs}
            obs, _rew, _term, _trunc, infos = env.step(acts)
        ((kitty, _masked, _ordinal, phase),) = env.needy()
        assert kitty == 1 and phase in ("resting", "held"), env.needy()


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            passed += 1
    print(f"{passed} passed")
