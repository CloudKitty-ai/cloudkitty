"""bc-collect rollout loader at schema 6 for the Gen 2 trunk (frozen
prereg `gen2-prereg-2026-10-17.md` §4/§5).

data_fog's shape at the Gen 2 wall: obs 399 / activity menu 35 /
message head 16, schemas (observation 6, action 3, mask 3), dims from
obs_layout_v6 and checked against every meta.json. The corpus layout is
the collection driver's (`results-raw/full-100/rNN/config-00-rollout-00`);
a rollout is named by its rNN parent, and the held-out split carries
exp-006's rule on that name: every rollout index ending in 3 is val
(r03, r13, ..., r93 -> 10%).

CONSENT SWAP (frozen §4, pinned with the trainer config): the trunk
trainer consumes PROPOSED-where-consent-refused, applied everywhere
else — imitate the teacher's DECISION; the refusal is physics the
student experiences, not a demonstration. The swap rows come from
consent_rows.py's extraction JSON (traced deterministic re-runs of the
enrichment rollouts; served/traits run consent base 0, gate off, and
the loader asserts no swap row lands outside an enrichment rollout).

A swapped label must be solo-mask legal (masked cross-entropy cannot
train on an off-menu target). In the full-100 corpus 389 of 137,088
refusal rows (0.284%) carry a proposed label the recorded mask
forbids — all proposed PlayKittyN absorbed to RestSolo, rows where
play is not on the student's menu — so the loader swaps where the
proposed label is mask-legal and keeps the applied label at the
residual, counting both (`gen2-deviations.md` entry 1, 2026-10-18).
"""
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1]
sys.path.insert(1, str(EXPERIMENTS / "attn-oracle-2026-08-15"))

from obs_layout_v6 import N_ACT, N_HEAD, OBS_DIM  # noqa: E402

SCHEMAS = (6, 3, 3)          # observation, action, mask (meta.json keys)
KITTY_SLOTS, CRITTER_SLOTS = 4, 2
VAL_ROLLOUT_SUFFIX = "3"     # rNN ends in 3 -> val (exp-006 rule)


def menu_names(k=KITTY_SLOTS, c=CRITTER_SLOTS):
    """ActionCodec::v2 order (codec.rs) at the configured slot counts."""
    return (["MoveN", "MoveE", "MoveS", "MoveW"]
            + ["RestSolo"] + [f"RestWithKitty{i}" for i in range(k)]
            + ["SleepSolo"] + [f"SleepWithKitty{i}" for i in range(k)]
            + ["GroomSelf"] + [f"GroomKitty{i}" for i in range(k)]
            + ["Eat", "Drink"]
            + [f"ChaseCritter{i}" for i in range(c)]
            + [f"ChaseKitty{i}" for i in range(k)]
            + ["PlaySolo"]
            + [f"PlayCritter{i}" for i in range(c)]
            + [f"PlayKitty{i}" for i in range(k)]
            + ["Idle"])


ACTION_NAMES = menu_names()
assert len(ACTION_NAMES) == N_ACT, (len(ACTION_NAMES), N_ACT)

ACTION_GROUPS = {
    "move": range(0, 4),
    "rest/sleep": range(4, 14),
    "groom-self": range(14, 15),
    "groom-kitty": range(15, 19),
    "eat/drink": range(19, 21),
    "play/chase": range(21, 34),
    "idle": range(34, 35),
}
assert [ACTION_NAMES[r[0]] for r in ACTION_GROUPS.values()] == \
    ["MoveN", "RestSolo", "GroomSelf", "GroomKitty0", "Eat", "ChaseCritter0", "Idle"]

# MessageCodec order: index 0 Silent, then HEAD_KINDS (observe.rs,
# frozen through the fog era).
MSG_NAMES = [
    "Silent", "WantEat", "WantDrink", "Mew", "WantPlay", "WantCuddle",
    "Purr", "WantBath", "WantSleep", "HereFood", "HereWater",
    "HereCritter", "HereSunbeam", "Chirp", "Trill", "Ekekek",
]
assert len(MSG_NAMES) == N_HEAD


@dataclass
class Rollout:
    name: str                # rNN (the collection index)
    cls: str                 # served / enrichment / traits
    obs: np.ndarray
    mask: np.ndarray
    label: np.ndarray        # post-swap training label
    mask_msg: np.ndarray
    label_msg: np.ndarray
    tick: np.ndarray
    reward: np.ndarray
    state: np.ndarray
    meta: dict
    swapped: int             # consent-swap rows applied
    unswappable: int         # refusal rows whose proposed label is off-menu


def load_rollout(d: Path, name, cls, swap_rows=()):
    obs = np.load(d / "obs.npy", mmap_mode="r")
    mask = np.load(d / "mask.npy")
    label = np.load(d / "label.npy").astype(np.int64)
    label_proposed = np.load(d / "label_proposed.npy").astype(np.int64)
    mask_msg = np.load(d / "mask_msg.npy")
    label_msg = np.load(d / "label_msg.npy")
    tick = np.load(d / "tick.npy")
    reward = np.load(d / "reward.npy")
    state = np.load(d / "state.npy", mmap_mode="r")
    meta = json.loads((d / "meta.json").read_text())

    n = obs.shape[0]
    assert meta["decisions"] == n, d
    assert label.shape == label_msg.shape == label_proposed.shape == (n,), d
    assert mask.shape[0] == mask_msg.shape[0] == n, d
    assert reward.shape[0] == state.shape[0] == meta["ticks"], d
    assert state.shape[1] == meta["state_width"], d
    rows = np.arange(n)
    assert mask[rows, label].all(), f"{name}: illegal activity label"
    assert mask_msg[rows, label_msg].all(), f"{name}: illegal message label"
    assert mask_msg[:, 0].all(), f"{name}: Silent masked somewhere"

    swapped = unswappable = 0
    if len(swap_rows):
        assert cls == "enrichment", \
            f"{name}: consent-swap rows on a {cls} rollout"
        idx = np.asarray(sorted(swap_rows), dtype=np.int64)
        assert (idx >= 0).all() and (idx < n).all(), name
        legal = mask[idx, label_proposed[idx]].astype(bool)
        label[idx[legal]] = label_proposed[idx[legal]]
        swapped = int(legal.sum())
        unswappable = int((~legal).sum())
        assert mask[rows, label].all(), \
            f"{name}: post-swap label is solo-mask illegal"
    return Rollout(name, cls, obs, mask, label, mask_msg, label_msg,
                   tick, reward, state, meta, swapped, unswappable)


def _is_val(name: str) -> bool:
    return name.endswith(VAL_ROLLOUT_SUFFIX)


def load_dataset(root, consent_rows=None, limit_rollouts=None):
    """root = a collection dir with manifest.json + rNN/ rollout dirs.
    consent_rows = consent_rows.py output JSON (required when the
    manifest has enrichment rollouts; pass an explicit None only for
    smoke slices that exclude them)."""
    root = Path(root)
    man = json.loads((root / "manifest.json").read_text())
    cls = {r["rollout"]: r["class"] for r in man["rollouts"]}
    dirs = sorted(root.glob("r*/config-00-rollout-00"))
    assert dirs, f"no rollout directories under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]

    swaps = {}
    if consent_rows is not None:
        cj = json.loads(Path(consent_rows).read_text())
        for r in cj["rollouts"]:
            swaps[f"r{r['rollout']:02d}"] = [
                x["row"] for x in r["refused"] if x["row"] is not None]
    rollouts = []
    for d in dirs:
        name = d.parent.name
        c = cls[int(name[1:])]
        if c == "enrichment" and name not in swaps:
            raise SystemExit(
                f"{name} is enrichment but has no consent-rows entry "
                "(frozen §4 pins the proposed-where-consent-refused swap; "
                "a refusal-free rollout still gets an empty entry)")
        rollouts.append(load_rollout(d, name, c, swaps.get(name, ())))

    dims = {"obs_dim": OBS_DIM, "n_actions": N_ACT, "n_msgs": N_HEAD}
    for r in rollouts:
        got = (r.obs.shape[1], r.mask.shape[1], r.mask_msg.shape[1])
        assert got == (OBS_DIM, N_ACT, N_HEAD), (r.name, got)
        schemas = (r.meta["observation_schema"], r.meta["action_schema"],
                   r.meta["mask_schema"])
        assert schemas == SCHEMAS, (r.name, schemas)

    val = [r for r in rollouts if _is_val(r.name)]
    train = [r for r in rollouts if not _is_val(r.name)]
    if not val:  # smoke prefix with no index ending in 3
        train, val = rollouts[:-1], rollouts[-1:]
    assert not ({r.name for r in train} & {r.name for r in val})
    return train, val, dims


def refuse_non_teaching_world(meta: dict, name) -> None:
    """The learning step's refusal (owner's observer-stream ruling,
    2026-10-27, B: nothing that acts learns from a needy world).
    bc-collect names a world's non-teaching seats in meta.json
    `teachers_refused` and then records no demonstration row from any
    seat, but it still writes that world's state and reward. A rollout
    naming any such seat is never training data for a policy or a
    critic; readers may still load it, trainers call this on everything
    they train on."""
    refused = meta.get("teachers_refused") or []
    if refused:
        raise SystemExit(
            f"{name}: refusing to train on a world that seats a "
            f"non-teaching behaviour (seats {refused}; owner ruling "
            "2026-10-27, observer streams B)")


def load_training_dataset(root, consent_rows=None, limit_rollouts=None):
    """load_dataset for a learning step: every rollout passes
    refuse_non_teaching_world first."""
    train, val, dims = load_dataset(root, consent_rows, limit_rollouts)
    for r in train + val:
        refuse_non_teaching_world(r.meta, r.name)
    return train, val, dims


def stack_decisions(rollouts):
    return (
        np.concatenate([np.asarray(r.obs, dtype=np.float32)
                        for r in rollouts]),
        np.concatenate([r.mask for r in rollouts]).astype(bool),
        np.concatenate([r.label for r in rollouts]),
        np.concatenate([r.mask_msg for r in rollouts]).astype(bool),
        np.concatenate([r.label_msg.astype(np.int64) for r in rollouts]),
    )
