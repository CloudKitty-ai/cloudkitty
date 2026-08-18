"""Dataset v5 loader (post-wall surface) for the exp-006 clones.

The v4 loader's shape with the spec-033 constants: obs 225 / activity
menu 34 / message head 16, dims read from the arrays and checked
against every meta.json. Split per the v4 battery recipe: val =
rollout-03 of each config. The anchor set (one config x 100 rollouts)
generalizes the same rule: every rollout index ending in 3 is val
(03, 13, ..., 93 -> 10%).

state.npy width VARIES by roster stratum (133/165/197 = roster x 32 +
37) — nothing here may assume 197 (dataset-v5 QA finding).
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ActionCodec::v2 order (codec.rs) — unchanged at the wall; the schema
# bump is the message head widening.
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
    "groom-kitty": range(13, 16),
    "eat/drink": range(16, 18),
    "play/chase": range(18, 33),
    "idle": range(33, 34),
}

# MessageCodec order: index 0 Silent, then HEAD_KINDS (observe.rs,
# frozen through the fog era).
MSG_NAMES = [
    "Silent", "WantEat", "WantDrink", "Mew", "WantPlay", "WantCuddle",
    "Purr", "WantBath", "WantSleep", "HereFood", "HereWater",
    "HereCritter", "HereSunbeam", "Chirp", "Trill", "Ekekek",
]

VAL_ROLLOUT_SUFFIX = "3"  # rollout index ends in 3 -> val


@dataclass
class Rollout:
    name: str
    obs: np.ndarray
    mask: np.ndarray
    label: np.ndarray
    mask_msg: np.ndarray
    label_msg: np.ndarray
    tick: np.ndarray
    reward: np.ndarray
    state: np.ndarray
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
    assert state.shape[1] == meta["state_width"], d
    rows = np.arange(n)
    assert mask[rows, label].all(), f"{d.name}: illegal activity label"
    assert mask_msg[rows, label_msg].all(), f"{d.name}: illegal message label"
    assert mask_msg[:, 0].all(), f"{d.name}: Silent masked somewhere"
    return Rollout(d.name, obs, mask, label, mask_msg, label_msg,
                   tick, reward, state, meta)


def _is_val(name: str) -> bool:
    return name.split("rollout-")[-1].endswith(VAL_ROLLOUT_SUFFIX)


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
    }
    assert dims["obs_dim"] == 225 and dims["n_actions"] == 34 \
        and dims["n_msgs"] == 16, dims
    for r in rollouts:
        assert (r.obs.shape[1], r.mask.shape[1], r.mask_msg.shape[1]) == (
            dims["obs_dim"], dims["n_actions"], dims["n_msgs"]), r.name
        assert (r.meta["observation_schema"], r.meta["action_schema"],
                r.meta["mask_schema"]) == (4, 3, 3), r.name

    val = [r for r in rollouts if _is_val(r.name)]
    train = [r for r in rollouts if not _is_val(r.name)]
    if not val:  # smoke prefix: hold out the last dir
        train, val = rollouts[:-1], rollouts[-1:]
    assert not ({r.name for r in train} & {r.name for r in val})
    return train, val, dims


def stack_decisions(rollouts):
    return (
        np.concatenate([np.asarray(r.obs, dtype=np.float32)
                        for r in rollouts]),
        np.concatenate([r.mask for r in rollouts]).astype(bool),
        np.concatenate([r.label.astype(np.int64) for r in rollouts]),
        np.concatenate([r.mask_msg for r in rollouts]).astype(bool),
        np.concatenate([r.label_msg.astype(np.int64) for r in rollouts]),
    )
