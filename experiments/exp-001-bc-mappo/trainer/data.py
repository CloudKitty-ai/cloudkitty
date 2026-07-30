"""Loaders for BC dataset v1 (`bc-collect` output).

Layout: one directory per rollout (`config-{ci:02}-rollout-{r:02}`), each
holding per-decision arrays (obs/mask/label/kitty/tick) plus per-tick
reward.npy and state.npy. Rows align to ticks only via tick.npy — rows are
dropped (inexpressible actions, joint-resolution mismatches), so a
(T, 5, ...) reshape is impossible.

Rollout boundaries exist only as directories. Splits MUST partition
directories, never rows: rows within a rollout share one long-lived world
(F-004), so a row-level split would leak the val set into train.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# rollout-04 of every config is validation: all 9 world variants appear in
# both splits, but no world seed is shared (seed = base + ci*1000 + r).
VAL_ROLLOUT_INDEX = 4

# Menu index -> name, mirroring ActionCodec::v1 (crates/cloudkitty-rl/src/
# codec.rs). Verified against n_actions read from mask.npy at load time.
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
    "MeowWantEat", "MeowWantDrink", "MeowFollowMe", "MeowWantPlay",
    "MeowWantCuddle", "MeowPurr",
    "Idle",
]

# Report groups; play/chase (18-32) is the strongest cooperative lever
# (frozen-world addendum §1) and gets called out in the clone review.
ACTION_GROUPS = {
    "move": range(0, 4),
    "rest/sleep/groom": range(4, 16),
    "eat/drink": range(16, 18),
    "play/chase": range(18, 33),
    "meow": range(33, 39),
    "idle": range(39, 40),
}


@dataclass
class Rollout:
    name: str
    obs: np.ndarray     # (N, obs_dim) f4, mmap
    mask: np.ndarray    # (N, n_actions) u1
    label: np.ndarray   # (N,) u2
    tick: np.ndarray    # (N,) u4
    reward: np.ndarray  # (T,) f4, post-tick team reward
    state: np.ndarray   # (T, state_dim) f4, pre-tick global state, mmap
    meta: dict


def load_rollout(d: Path) -> Rollout:
    obs = np.load(d / "obs.npy", mmap_mode="r")
    mask = np.load(d / "mask.npy")
    label = np.load(d / "label.npy")
    tick = np.load(d / "tick.npy")
    reward = np.load(d / "reward.npy")
    state = np.load(d / "state.npy", mmap_mode="r")
    meta = json.loads((d / "meta.json").read_text())

    n = obs.shape[0]
    assert label.shape == (n,) and tick.shape == (n,) and mask.shape[0] == n, d
    assert meta["decisions"] == n, f"{d.name}: meta says {meta['decisions']} rows, files have {n}"
    assert reward.shape[0] == state.shape[0] == meta["ticks"], d
    # Collection guarantees every label is legal under its own mask; a
    # violation here means the dataset on disk is not the one collected.
    assert mask[np.arange(n), label].all(), f"illegal label in {d.name}"
    return Rollout(d.name, obs, mask, label, tick, reward, state, meta)


def load_dataset(root: Path, limit_rollouts: int | None = None):
    """Returns (train, val, dims). Dims are read from the files, never
    hardcoded — obs/state widths are config-derived (roster, slots)."""
    dirs = sorted(p for p in root.iterdir() if (p / "meta.json").exists())
    assert dirs, f"no rollout directories under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]
    rollouts = [load_rollout(d) for d in dirs]

    dims = {
        "obs_dim": rollouts[0].obs.shape[1],
        "n_actions": rollouts[0].mask.shape[1],
        "state_dim": rollouts[0].state.shape[1],
    }
    for r in rollouts:
        assert (r.obs.shape[1], r.mask.shape[1], r.state.shape[1]) == (
            dims["obs_dim"], dims["n_actions"], dims["state_dim"]
        ), f"inconsistent dims in {r.name}"
    assert dims["n_actions"] == len(ACTION_NAMES), (
        f"menu has {dims['n_actions']} actions but ACTION_NAMES lists "
        f"{len(ACTION_NAMES)} — codec changed, update the table"
    )

    val = [r for r in rollouts if r.name.endswith(f"rollout-{VAL_ROLLOUT_INDEX:02}")]
    train = [r for r in rollouts if r not in val]
    if not val:  # smoke runs with few rollouts: hold out the last one
        train, val = rollouts[:-1], rollouts[-1:]
    return train, val, dims


def stack_decisions(rollouts):
    """Concatenate per-decision arrays for the BC classifier.
    Materializes in RAM (~1.3 GB obs for the full set)."""
    obs = np.concatenate([np.asarray(r.obs, dtype=np.float32) for r in rollouts])
    mask = np.concatenate([r.mask for r in rollouts]).astype(bool)
    label = np.concatenate([r.label for r in rollouts]).astype(np.int64)
    return obs, mask, label


def critic_arrays(rollouts, gamma: float, min_future: int = 1500):
    """(states, MC returns) for the critic, censored per prereg deviation
    27c: Monte-Carlo targets have no bootstrap, so a state near the rollout
    cut misses tail return — keep only states with >= min_future realized
    ticks. The return itself sums the FULL realized future.
    """
    xs, ys = [], []
    for r in rollouts:
        t_total = r.reward.shape[0]
        g = np.empty(t_total, dtype=np.float64)
        acc = 0.0
        rew = r.reward.astype(np.float64)
        for t in range(t_total - 1, -1, -1):
            acc = rew[t] + gamma * acc
            g[t] = acc
        keep = t_total - min_future + 1  # ticks 0 .. t_total - min_future
        assert keep > 0, f"{r.name}: rollout shorter than min_future"
        xs.append(np.asarray(r.state[:keep], dtype=np.float32))
        ys.append(g[:keep].astype(np.float32))
    return np.concatenate(xs), np.concatenate(ys)
