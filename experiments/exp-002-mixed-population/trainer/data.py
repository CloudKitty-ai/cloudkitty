"""Loaders for BC dataset v2 (exp-002; bc-collect + collect_s6_rollouts).

Same public API as exp-001's trainer/data.py (load_dataset,
stack_decisions, critic_arrays, ACTION_* tables) so exp-001's training
scripts run unchanged on v2 — the shims in this directory put this
module first on sys.path under the name `data`. v2 differs in two ways
this module owns:

  - Mixed rosters (3-5 kitties), so state.npy width varies per rollout
    (roster*32 + 37 — cloudkitty_rl::global_state: per-kitty blocks in
    stable id order, then the element/clock tail). The critic view pads
    every state to the 5-kitty layout (prereg §4): real blocks first,
    zero blocks for absent kitties, tail at its fixed offset 160. Real
    blocks are never all-zero (the activity one-hot), so the zero
    pattern encodes roster size.
  - Split (prereg §5, fixed at freeze): val = rollout-02 of every
    variant (one held-out world seed per config, scripted) plus
    s6-rollout-00 of configs 12/13/14 (one per roster size, so
    policy-like states and channel rows appear in val). Splits
    partition directories, never rows (F-004).
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np

_EXPERIMENTS = Path(__file__).resolve().parents[2]  # experiments/
_EXP1 = _EXPERIMENTS / "exp-001-bc-mappo" / "trainer"
_spec = importlib.util.spec_from_file_location("exp001_data", _EXP1 / "data.py")
_v1 = importlib.util.module_from_spec(_spec)
sys.modules["exp001_data"] = _v1
_spec.loader.exec_module(_v1)

# Unchanged pieces, re-exported for the exp-001 training scripts.
ACTION_NAMES = _v1.ACTION_NAMES
ACTION_GROUPS = _v1.ACTION_GROUPS
load_rollout = _v1.load_rollout
stack_decisions = _v1.stack_decisions

PER_KITTY = 32
TAIL = 37
TARGET_ROSTER = 5
PADDED_STATE_DIM = TARGET_ROSTER * PER_KITTY + TAIL  # 197

VAL_SCRIPTED_ROLLOUT = 2
VAL_S6_CONFIGS = (12, 13, 14)  # rosters 3/4/5 — one of each in val


def roster_of(rollout):
    roster, rem = divmod(rollout.state.shape[1] - TAIL, PER_KITTY)
    assert rem == 0 and 3 <= roster <= TARGET_ROSTER, (
        f"{rollout.name}: state width {rollout.state.shape[1]} is not a "
        f"3-5 kitty layout"
    )
    return roster


def pad_states(states, roster):
    """(N, roster*32+37) -> (N, 197): zero blocks for absent kitties."""
    s = np.asarray(states, dtype=np.float32)
    if roster == TARGET_ROSTER:
        return s
    zeros = np.zeros((s.shape[0], (TARGET_ROSTER - roster) * PER_KITTY),
                     np.float32)
    cut = roster * PER_KITTY
    return np.concatenate([s[:, :cut], zeros, s[:, cut:]], axis=1)


def _is_val(name):
    if name.endswith(f"rollout-{VAL_SCRIPTED_ROLLOUT:02}") and "s6" not in name:
        return True
    return any(name == f"config-{ci:02}-s6-rollout-00" for ci in VAL_S6_CONFIGS)


def load_dataset(root: Path, limit_rollouts: int | None = None):
    """Returns (train, val, dims). Obs/action dims are strict-equal
    across rollouts; state_dim is the PADDED width (what the critic
    consumes) — raw widths vary with roster and are validated by
    roster_of()."""
    dirs = sorted(p for p in root.iterdir() if (p / "meta.json").exists())
    assert dirs, f"no rollout directories under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]
    rollouts = [load_rollout(d) for d in dirs]

    dims = {
        "obs_dim": rollouts[0].obs.shape[1],
        "n_actions": rollouts[0].mask.shape[1],
        "state_dim": PADDED_STATE_DIM,
    }
    for r in rollouts:
        assert (r.obs.shape[1], r.mask.shape[1]) == (
            dims["obs_dim"], dims["n_actions"]), f"inconsistent dims in {r.name}"
        roster_of(r)  # asserts the state width is a lawful roster layout
    assert dims["n_actions"] == len(ACTION_NAMES), (
        f"menu has {dims['n_actions']} actions but ACTION_NAMES lists "
        f"{len(ACTION_NAMES)} — codec changed, update the table"
    )

    val = [r for r in rollouts if _is_val(r.name)]
    train = [r for r in rollouts if not _is_val(r.name)]
    if not val:  # smoke runs on a tiny prefix: hold out the last dir
        train, val = rollouts[:-1], rollouts[-1:]
    return train, val, dims


def critic_arrays(rollouts, gamma: float, min_future: int = 1500):
    """(padded states, MC returns), censored per exp-001 deviation 27c:
    keep only states with >= min_future realized ticks; the return sums
    the FULL realized future."""
    xs, ys = [], []
    for r in rollouts:
        t_total = r.reward.shape[0]
        g = np.empty(t_total, dtype=np.float64)
        acc = 0.0
        rew = r.reward.astype(np.float64)
        for t in range(t_total - 1, -1, -1):
            acc = rew[t] + gamma * acc
            g[t] = acc
        keep = t_total - min_future + 1
        assert keep > 0, f"{r.name}: rollout shorter than min_future"
        xs.append(pad_states(r.state[:keep], roster_of(r)))
        ys.append(g[:keep].astype(np.float32))
    return np.concatenate(xs), np.concatenate(ys)
