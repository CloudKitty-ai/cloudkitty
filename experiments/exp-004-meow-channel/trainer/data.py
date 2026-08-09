"""Loader for BC dataset v4 (exp-004; two-channel bc-collect output).

v4 rows carry BOTH heads: the v1-lineage arrays (obs/mask/label) plus
mask_msg.npy (N x 9 u1) and label_msg.npy (N u2, 0 = Silent). The critic
view (padded 5-kitty state, MC-return censoring) is exp-002's, imported
rather than copied so a fix there reaches here.

**Split (prereg §5, frozen)**: four rollouts per config (`00`-`03`),
val = `rollout-03` of every variant — 15 of 60, every world variant in
both halves on disjoint seeds, split partitions directories never rows
(F-004).

Menu tables mirror ActionCodec::v2 / MessageCodec (kitty_slots 3,
critter_slots 4) and are length-asserted against the data at load.
"""

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_EXPERIMENTS = Path(__file__).resolve().parents[2]  # experiments/
_EXP2 = _EXPERIMENTS / "exp-002-mixed-population" / "trainer"
_spec = importlib.util.spec_from_file_location("exp002_data", _EXP2 / "data.py")
_v2 = importlib.util.module_from_spec(_spec)
sys.modules["exp002_data"] = _v2
_spec.loader.exec_module(_v2)

# Critic-view pieces, unchanged from v2 (state layout survived 028:
# per-kitty 32 + tail 37, padded to the 5-kitty 197).
PER_KITTY = _v2.PER_KITTY
TAIL = _v2.TAIL
TARGET_ROSTER = _v2.TARGET_ROSTER
PADDED_STATE_DIM = _v2.PADDED_STATE_DIM
pad_states = _v2.pad_states
roster_of = _v2.roster_of

VAL_ROLLOUT = 3
EXPECTED_TRAIN, EXPECTED_VAL = 45, 15

# ActionCodec::v2 order (codec.rs), verified 34-long against mask width.
ACTION_NAMES = [
    "MoveN", "MoveE", "MoveS", "MoveW",
    "RestSolo", "RestWithKitty0", "RestWithKitty1", "RestWithKitty2",
    "SleepSolo", "SleepWithKitty0", "SleepWithKitty1", "SleepWithKitty2",
    "GroomSelf", "GroomKitty0", "GroomKitty1", "GroomKitty2",
    "Eat", "Drink",
    "ChaseCritter0", "ChaseCritter1", "ChaseCritter2", "ChaseCritter3",
    "ChaseKitty0", "ChaseKitty1", "ChaseKitty2",
    "PlaySolo",
    "PlayCritter0", "PlayCritter1", "PlayCritter2", "PlayCritter3",
    "PlayKitty0", "PlayKitty1", "PlayKitty2",
    "Idle",
]

ACTION_GROUPS = {
    "move": range(0, 4),
    "rest/sleep": range(4, 12),
    "groom-self": range(12, 13),
    "groom-kitty": range(13, 16),  # classes dead in v3 — the H2 watch
    "eat/drink": range(16, 18),
    "play/chase": range(18, 33),
    "idle": range(33, 34),
}

# MessageCodec order: index 0 Silent, then HEAD_KINDS (observe.rs).
MSG_NAMES = [
    "Silent", "WantEat", "WantDrink", "FollowMe", "WantPlay",
    "WantCuddle", "Purr", "WantBath", "WantSleep",
]


@dataclass
class Rollout:
    name: str
    obs: np.ndarray        # (N, obs_dim) f4, mmap
    mask: np.ndarray       # (N, n_actions) u1
    label: np.ndarray      # (N,) u2
    mask_msg: np.ndarray   # (N, n_msgs) u1
    label_msg: np.ndarray  # (N,) u2
    tick: np.ndarray       # (N,) u4
    reward: np.ndarray     # (T,) f4
    state: np.ndarray      # (T, state_dim) f4, mmap
    meta: dict


def load_rollout(d: Path) -> Rollout:
    obs = np.load(d / "obs.npy", mmap_mode="r")
    mask = np.load(d / "mask.npy")
    label = np.load(d / "label.npy")
    mask_msg = np.load(d / "mask_msg.npy")
    label_msg = np.load(d / "label_msg.npy")
    tick = np.load(d / "tick.npy")
    reward = np.load(d / "reward.npy")
    state = np.load(d / "state.npy", mmap_mode="r")
    meta = json.loads((d / "meta.json").read_text())

    n = obs.shape[0]
    assert meta["decisions"] == n, d
    assert label.shape == label_msg.shape == (n,), d
    assert mask.shape[0] == mask_msg.shape[0] == n, d
    assert reward.shape[0] == state.shape[0] == meta["ticks"], d
    # Both-head legality: the dataset on disk must be the one collected.
    rows = np.arange(n)
    assert mask[rows, label].all(), f"{d.name}: illegal activity label"
    assert mask_msg[rows, label_msg].all(), f"{d.name}: illegal message label"
    assert mask_msg[:, 0].all(), f"{d.name}: Silent masked somewhere"
    return Rollout(d.name, obs, mask, label, mask_msg, label_msg,
                   tick, reward, state, meta)


def _is_val(name: str) -> bool:
    return name.endswith(f"rollout-{VAL_ROLLOUT:02}")


def load_dataset(root: Path, limit_rollouts: int | None = None):
    dirs = sorted(p for p in root.iterdir() if (p / "meta.json").exists())
    assert dirs, f"no rollout directories under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]
    rollouts = [load_rollout(d) for d in dirs]

    dims = {
        "obs_dim": rollouts[0].obs.shape[1],
        "n_actions": rollouts[0].mask.shape[1],
        "n_msgs": rollouts[0].mask_msg.shape[1],
        "state_dim": PADDED_STATE_DIM,
    }
    for r in rollouts:
        assert (r.obs.shape[1], r.mask.shape[1], r.mask_msg.shape[1]) == (
            dims["obs_dim"], dims["n_actions"], dims["n_msgs"]), r.name
        roster_of(r)
    assert dims["n_actions"] == len(ACTION_NAMES), "menu moved; update tables"
    assert dims["n_msgs"] == len(MSG_NAMES), "message head moved; update tables"

    val = [r for r in rollouts if _is_val(r.name)]
    train = [r for r in rollouts if not _is_val(r.name)]
    if not val:  # smoke prefix: hold out the last dir
        train, val = rollouts[:-1], rollouts[-1:]
    if limit_rollouts is None:
        assert (len(train), len(val)) == (EXPECTED_TRAIN, EXPECTED_VAL), (
            f"{len(train)}/{len(val)} vs registered "
            f"{EXPECTED_TRAIN}/{EXPECTED_VAL}"
        )
        assert not ({r.name for r in train} & {r.name for r in val})
    return train, val, dims


def stack_decisions(rollouts):
    """(obs, mask, label, mask_msg, label_msg) stacked across rollouts."""
    return (
        np.concatenate([np.asarray(r.obs, dtype=np.float32) for r in rollouts]),
        np.concatenate([r.mask for r in rollouts]).astype(bool),
        np.concatenate([r.label.astype(np.int64) for r in rollouts]),
        np.concatenate([r.mask_msg for r in rollouts]).astype(bool),
        np.concatenate([r.label_msg.astype(np.int64) for r in rollouts]),
    )


def critic_arrays(rollouts, gamma: float, min_future: int = 1500):
    """exp-002's censored MC targets over v4 rollouts (duck-typed)."""
    return _v2.critic_arrays(rollouts, gamma, min_future)
