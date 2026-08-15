"""exp-005 loader: the playful-Biscuit dataset (raw/bc-playful, 100
rollouts), filtered to the demonstrator's rows (kitty id 2). Val =
every 10th rollout (10 of 100). Duck-types exp-004's loader surface
for train_attn_clone's fork.
"""
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_EXPERIMENTS = Path(__file__).resolve().parents[2]
_E4 = _EXPERIMENTS / "exp-004-meow-channel" / "trainer"
_spec = importlib.util.spec_from_file_location("exp004_data", _E4 / "data.py")
_v4 = importlib.util.module_from_spec(_spec)
sys.modules["exp004_data"] = _v4
_spec.loader.exec_module(_v4)

ACTION_NAMES = _v4.ACTION_NAMES
ACTION_GROUPS = _v4.ACTION_GROUPS
MSG_NAMES = _v4.MSG_NAMES

SUBJECT_KITTY = 2  # Biscuit: the playful demonstrator's seat


@dataclass
class Rollout:
    name: str
    obs: np.ndarray
    mask: np.ndarray
    label: np.ndarray
    mask_msg: np.ndarray
    label_msg: np.ndarray
    kitty: np.ndarray
    meta: dict


def load_rollout(d: Path) -> Rollout:
    r = Rollout(
        d.name,
        np.load(d / "obs.npy", mmap_mode="r"),
        np.load(d / "mask.npy"),
        np.load(d / "label.npy"),
        np.load(d / "mask_msg.npy"),
        np.load(d / "label_msg.npy"),
        np.load(d / "kitty.npy"),
        json.loads((d / "meta.json").read_text()),
    )
    n = r.obs.shape[0]
    assert r.meta["decisions"] == n
    rows = np.arange(n)
    assert r.mask[rows, r.label].all(), f"{d.name}: illegal activity label"
    assert r.mask_msg[rows, r.label_msg].all(), f"{d.name}: illegal msg label"
    return r


def load_dataset(root: Path, limit_rollouts=None):
    dirs = sorted(p for p in root.iterdir() if (p / "meta.json").exists())
    assert dirs, f"no rollouts under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]
    rollouts = [load_rollout(d) for d in dirs]
    dims = {"obs_dim": rollouts[0].obs.shape[1],
            "n_actions": rollouts[0].mask.shape[1],
            "n_msgs": rollouts[0].mask_msg.shape[1]}
    assert dims["n_actions"] == len(ACTION_NAMES)
    assert dims["n_msgs"] == len(MSG_NAMES)
    val = [r for i, r in enumerate(rollouts) if i % 10 == 9]
    train = [r for i, r in enumerate(rollouts) if i % 10 != 9]
    if not val:
        train, val = rollouts[:-1], rollouts[-1:]
    return train, val, dims


def stack_decisions(rollouts):
    """Subject rows only (the playful seat)."""
    def sel(r):
        return r.kitty == SUBJECT_KITTY
    return (
        np.concatenate([np.asarray(r.obs, np.float32)[sel(r)]
                        for r in rollouts]),
        np.concatenate([r.mask[sel(r)] for r in rollouts]).astype(bool),
        np.concatenate([r.label[sel(r)].astype(np.int64)
                        for r in rollouts]),
        np.concatenate([r.mask_msg[sel(r)] for r in rollouts]).astype(bool),
        np.concatenate([r.label_msg[sel(r)].astype(np.int64)
                        for r in rollouts]),
    )
