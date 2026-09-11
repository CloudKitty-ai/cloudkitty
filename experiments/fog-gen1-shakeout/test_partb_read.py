#!/usr/bin/env python3
"""Guard for partb_read.py (plain asserts, no pytest).

    test_partb_read.py ANCHOR_ROLLOUT_DIR

The load-bearing check is EQUIVALENCE on a recorded anchor rollout:
radius_screen.screen over partb_read's obs-derived snapshots must
reproduce screen over the trace's true snapshots (same 12-red-verified
accumulator both sides, so any disagreement is the adapter's). need_max
is compared clamped: obs needs saturate at 100. Synthetic cases cover
the censuses.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
import partb_read as pb  # noqa: E402
import schema_check as sc  # noqa: E402
from radius_screen import screen, stream_snapshots  # noqa: E402

# --- synthetic censuses ----------------------------------------------------
obs = np.zeros((4, L.OBS_DIM), np.float32)
obs[0, L.SELF_ACTIVITY + 2] = 1
obs[1, L.SELF_ACTIVITY + 2] = 1
obs[2, L.SELF_ACTIVITY + 5] = 1
obs[3, L.SELF_ACTIVITY + 2] = 1
rows = {"obs": obs, "tick": np.array([0, 1, 2, 3]),
        "kitty": np.zeros(4, np.int64),
        "act": np.array([3, 3, 7, 3]), "msg": np.array([0, 0, 4, 0]),
        "mask": np.zeros((4, 55), bool)}
rows["mask"][:, [3, 7, 11]] = True
c = pb.act7_census(rows)
assert c[0]["max_share"] == 0.75 and c[0]["argmax"] == 2, \
    f"act7 domination: 3 of 4 ticks in class 2, got {c[0]}"
m = pb.menu_census(rows)
assert m["chosen"][3] == 3 and m["chosen"][7] == 1, "menu census counts"
assert [d["menu_index"] for d in m["hard_zero_legal"]] == [11], \
    f"hard-zero: menu 11 legal on every row, never chosen; got {m['hard_zero_legal']}"
assert pb.msg_census(rows)[4] == 1 and pb.msg_census(rows)[0] == 3, "msg census"

# scene starts: a FLAT consecutive age is not a start (only a strict
# drop is), so ages 0,0 then climb then reset -> exactly one start
obs2 = np.zeros((4, L.OBS_DIM), np.float32)
obs2[:, L.SELF_SCENE_AGE] = [0.0, 0.0, 0.1, 0.0]
obs2[0:2, L.SELF_ACTIVITY + 1] = 1
obs2[2:4, L.SELF_ACTIVITY + 5] = 1
rows2 = dict(rows, obs=obs2)
s = pb.scene_starts(rows2)
assert s[5] == 1 and sum(s) == 1, \
    f"scene starts: one reset, classed 5 at the start tick, got {s}"

# --- equivalence on a recorded anchor rollout ------------------------------
trace_dir = Path(sys.argv[1])
tr = sc.load_trace(trace_dir, None)
n_seats = len(tr.lines[0]["snapshot"]["kitties"])
ticks = np.repeat(np.arange(len(tr.lines)), n_seats)
kitties = np.concatenate([[k["id"] for k in line["snapshot"]["kitties"]]
                          for line in tr.lines]).astype(np.int64)
arows = {"obs": tr.obs, "tick": ticks, "kitty": kitties}
import json
import tomllib
meta = json.loads((trace_dir / "meta.json").read_text())
with open(meta["config"], "rb") as f:
    cfg = tomllib.load(f)
r = int(meta["vision_radius"])
args = (cfg["thresholds"]["distress"], cfg["thresholds"]["safeguard"],
        cfg["meow"]["announce_threshold"])
true = screen(stream_snapshots(trace_dir), r, *args)
derived = screen(pb.snapshots_from_obs(arows), r, *args)

assert derived["watchdog_entries"] == true["watchdog_entries"], \
    f"equivalence: watchdog {derived['watchdog_entries']} != {true['watchdog_entries']}"
assert derived["distress_episodes_per_1k"] == true["distress_episodes_per_1k"], \
    "equivalence: distress episode count differs from the true snapshots"
assert derived["max_distress_age"] == true["max_distress_age"], \
    "equivalence: max distress age differs"
assert derived["safeguard_crossings_per_1k"] == true["safeguard_crossings_per_1k"], \
    "equivalence: safeguard crossings differ"
assert derived["friend_in_view_share"] == true["friend_in_view_share"], \
    f"equivalence: friend-in-view {derived['friend_in_view_share']:.4f} != " \
    f"{true['friend_in_view_share']:.4f}"
assert derived["dispersion"]["euc_median"] == true["dispersion"]["euc_median"], \
    "equivalence: NN euclidean median differs (position reconstruction)"
for need in ("eat", "drink"):
    d, t = derived[f"blind_{need}"], true[f"blind_{need}"]
    assert d["cat_ticks_per_1k"] == t["cat_ticks_per_1k"] and \
        d["span_max"] == t["span_max"], \
        f"equivalence: blind_{need} differs {d} vs {t}"
for k, v in true["need_max"].items():
    assert abs(min(v, 100.0) - derived["need_max"][k]) <= 0.51, \
        f"equivalence: clamped need_max[{k}] {derived['need_max'][k]} vs true {v}"

print("test_partb_read: PASS")
