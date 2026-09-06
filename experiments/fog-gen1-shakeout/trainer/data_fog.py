"""bc-collect rollout loader at schema 5 for the fog Gen 1 clones.

data6's shape with the Gen 1 constants: obs 408 / activity menu 39 /
message head 16, schemas (observation 5, action 3, mask 3), dims read
from the arrays and checked against every meta.json. Rollout reading and
row stacking are data6's own (imported); only the dims, the names and
the schema pin are this file's.

Held-out split carried from exp-006 (owner 2026-09-05): every rollout
index ending in 3 is val (03, 13, ..., 93 -> 10%); a smoke prefix with no
such index holds out its last rollout. state.npy is 197 wide on the
served roster (5 x 32 + 37); the critic reads it, nothing here does.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1]
sys.path.insert(1, str(EXPERIMENTS / "exp-006-character-gen" / "trainer"))
sys.path.insert(1, str(EXPERIMENTS / "attn-oracle-2026-08-15"))

from data6 import (VAL_ROLLOUT_SUFFIX, Rollout, _is_val,  # noqa: E402,F401
                   load_rollout, stack_decisions)
from obs_layout_v5 import HEAD_KINDS, N_ACT, N_HEAD, OBS_DIM  # noqa: E402

SCHEMAS = (5, 3, 3)          # observation, action, mask (meta.json keys)
KITTY_SLOTS, CRITTER_SLOTS = 4, 4


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
    "play/chase": range(21, 38),
    "idle": range(38, 39),
}
assert [ACTION_NAMES[r[0]] for r in ACTION_GROUPS.values()] == \
    ["MoveN", "RestSolo", "GroomSelf", "GroomKitty0", "Eat", "ChaseCritter0", "Idle"]

# MessageCodec order: index 0 Silent, then HEAD_KINDS (serde snake_case).
MSG_NAMES = ["silent"] + HEAD_KINDS
assert len(MSG_NAMES) == N_HEAD

WANT = [MSG_NAMES.index(k) for k in
        ("want_eat", "want_drink", "want_play", "want_cuddle", "want_bath", "want_sleep")]
HERE_MSG = {MSG_NAMES.index(k): k for k in
            ("here_food", "here_water", "here_critter", "here_sunbeam")}


def load_dataset(root, limit_rollouts=None):
    root = Path(root)
    dirs = sorted(p for p in root.iterdir() if (p / "meta.json").exists())
    assert dirs, f"no rollout directories under {root}"
    if limit_rollouts is not None:
        dirs = dirs[:limit_rollouts]
    rollouts = [load_rollout(d) for d in dirs]

    dims = {"obs_dim": OBS_DIM, "n_actions": N_ACT, "n_msgs": N_HEAD}
    for r in rollouts:
        got = (r.obs.shape[1], r.mask.shape[1], r.mask_msg.shape[1])
        assert got == (OBS_DIM, N_ACT, N_HEAD), (r.name, got)
        schemas = (r.meta["observation_schema"], r.meta["action_schema"],
                   r.meta["mask_schema"])
        assert schemas == SCHEMAS, (r.name, schemas)

    val = [r for r in rollouts if _is_val(r.name)]
    train = [r for r in rollouts if not _is_val(r.name)]
    if not val:  # smoke prefix: hold out the last dir
        train, val = rollouts[:-1], rollouts[-1:]
    assert train and val, "need at least two rollouts"
    assert not ({r.name for r in train} & {r.name for r in val})
    return train, val, dims
