"""Loader for BC dataset v3 (exp-003; bc-collect against the v4 family).

Same public API as exp-001's and exp-002's `data.py`, so exp-001's
training loops run unchanged — the shims in this directory put this
module first on `sys.path` under the name `data`.

v3 is v2's loader with one difference this module owns: **the split.**
Everything else — the padded 5-kitty critic view, the roster-layout
assertion, the MC-return censoring — is v2's and is imported rather than
copied, so a fix there reaches here.

**Split (recorded in results/dataset-v3-2026-08-06.md)**: four rollouts
per config (`00`–`03`), val = **`rollout-03`** of every variant, 15 of
60. Every world variant appears in both halves on disjoint seeds, and
splits partition directories, never rows (F-004).

v2 also held out `s6-rollout-00` of three configs so that policy-like
states and channel rows appeared in val. **v3 cannot**: the schema bump
means no generation-2 policy exists yet to generate rollouts from, so
the dataset is scripted-only and `VAL_S6_CONFIGS` is empty. That is the
generation wall, not an oversight — see the dataset record.
"""

import importlib.util
import sys
from pathlib import Path

_EXPERIMENTS = Path(__file__).resolve().parents[2]  # experiments/
_EXP2 = _EXPERIMENTS / "exp-002-mixed-population" / "trainer"
_spec = importlib.util.spec_from_file_location("exp002_data", _EXP2 / "data.py")
_v2 = importlib.util.module_from_spec(_spec)
sys.modules["exp002_data"] = _v2
_spec.loader.exec_module(_v2)

# v2's `_is_val` reads these at call time, so setting them here
# reconfigures its split without duplicating the loader. This mutates the
# imported module object, which is private to this process — exp-002's
# own scripts load their own copy and are unaffected. The assertion in
# `load_dataset` below is what actually holds the split to the record;
# these two lines are the mechanism, not the guarantee.
_v2.VAL_SCRIPTED_ROLLOUT = 3
_v2.VAL_S6_CONFIGS = ()

VAL_ROLLOUT = 3
EXPECTED_TRAIN, EXPECTED_VAL = 45, 15

# Unchanged pieces, re-exported so exp-001's training scripts and
# exp-002's `ppo_env` (which imports PER_KITTY/TAIL/TARGET_ROSTER/
# pad_states for its padded critic view) run against this module
# unmodified. A missing name here is an ImportError, not a silent
# fallback — which is why the list is explicit rather than a star import.
ACTION_NAMES = _v2.ACTION_NAMES
ACTION_GROUPS = _v2.ACTION_GROUPS
load_rollout = _v2.load_rollout
stack_decisions = _v2.stack_decisions
critic_arrays = _v2.critic_arrays
pad_states = _v2.pad_states
roster_of = _v2.roster_of
PER_KITTY = _v2.PER_KITTY
TAIL = _v2.TAIL
TARGET_ROSTER = _v2.TARGET_ROSTER
PADDED_STATE_DIM = _v2.PADDED_STATE_DIM


def load_dataset(root: Path, limit_rollouts: int | None = None):
    """v2's loader, with the registered split asserted rather than trusted.

    A split is the one thing in this pipeline that fails silently and
    expensively: nothing downstream complains if val quietly becomes the
    wrong rollouts, or empty, or overlapping — the numbers just come out
    optimistic. So the shape recorded in the dataset document is checked
    here on every full load.
    """
    train, val, dims = _v2.load_dataset(root, limit_rollouts)
    if limit_rollouts is None:
        assert (len(train), len(val)) == (EXPECTED_TRAIN, EXPECTED_VAL), (
            f"split is {len(train)} train / {len(val)} val, but the record "
            f"registers {EXPECTED_TRAIN}/{EXPECTED_VAL} — the dataset shape "
            f"changed, or the rollout count did"
        )
        assert all(r.name.endswith(f"rollout-{VAL_ROLLOUT:02}") for r in val), (
            f"val holds {[r.name for r in val][:3]}…, not rollout-"
            f"{VAL_ROLLOUT:02} of every variant"
        )
        assert not ({r.name for r in train} & {r.name for r in val}), (
            "train and val share a rollout"
        )
    return train, val, dims
