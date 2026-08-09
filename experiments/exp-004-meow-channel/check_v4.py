#!/usr/bin/env python3
"""Dataset v4 collection acceptance (prereg §11, frozen 2026-08-09).

Checks, over every rollout in raw/bc-v4/:
- widths from the engine (197/34/9, schemas 3/2/2) via meta.json;
- label-legality invariant on BOTH heads (mask[label] == 1 row-wise);
- Silent never masked (mask_msg[:,0] all-ones, structural);
- no meow-turn rows (the v2 menu has no meow activity; dropped_by is
  checked for a 'meow' entry as a belt-and-braces read);
- channel composition: label_msg distribution by head index;
- THE two-channel FR acceptance check: activity-class distribution
  conditioned on message != Silent vs unconditioned — announcing cats
  must be mid-errand; a skew toward Idle voids the collection.
"""

import json
from collections import Counter
from pathlib import Path

import numpy as np

RAW = Path(__file__).parent / "raw" / "bc-v4"
dirs = sorted(RAW.glob("config-*-rollout-*"))
assert len(dirs) == 60, len(dirs)

tot = Counter()
act_all = Counter()
act_talk = Counter()
per_behavior = {"needs_driven": [Counter(), Counter()], "playful": [Counter(), Counter()]}
msg_dist = Counter()
widths = set()
for d in dirs:
    meta = json.load(open(d / "meta.json"))
    widths.add(
        (
            meta["obs_width"],
            meta["mask_width"],
            meta["msg_mask_width"],
            meta["observation_schema"],
            meta["action_schema"],
            meta["mask_schema"],
        )
    )
    assert "meow" not in meta["dropped_by_action"], d
    label = np.load(d / "label.npy")
    mask = np.load(d / "mask.npy")
    lmsg = np.load(d / "label_msg.npy")
    mmsg = np.load(d / "mask_msg.npy")
    n = len(label)
    assert mask[np.arange(n), label].all(), d
    assert mmsg[np.arange(n), lmsg].all(), d
    assert mmsg[:, 0].all(), d
    assert label.max() < meta["mask_width"] and lmsg.max() < meta["msg_mask_width"]
    tot["rows"] += n
    tot["talk"] += int((lmsg != 0).sum())
    msg_dist.update(Counter(lmsg.tolist()))
    act_all.update(Counter(label.tolist()))
    act_talk.update(Counter(label[lmsg != 0].tolist()))
    kit = np.load(d / "kitty.npy")
    beh = {int(k): v for k, v in meta["experts"].items()}
    for b, (c_all, c_talk) in per_behavior.items():
        ids = [k for k, v in beh.items() if v == b]
        sel = np.isin(kit, ids)
        c_all.update(Counter(label[sel].tolist()))
        c_talk.update(Counter(label[sel & (lmsg != 0)].tolist()))

assert widths == {(197, 34, 9, 3, 2, 2)}, widths

rows, talk = tot["rows"], tot["talk"]
print(f"rows {rows}  channel rows {talk} ({100*talk/rows:.2f}%)  widths OK  legality OK")
print("msg head dist:", dict(sorted(msg_dist.items())))

# The FR check: compare activity-CLASS shares. Menu v2 (ActionCodec::v2,
# kitty_slots=3, critter_slots=4, 34 entries): Move 0-3, RestSolo 4,
# RestWith 5-7, SleepSolo 8, SleepWith 9-11, GroomSelf 12, GroomKitty
# 13-15, Eat 16, Drink 17, ChaseCritter 18-21, ChaseKitty 22-24,
# PlaySolo 25, PlayCritter 26-29, PlayKitty 30-32, Idle 33.
# (Correction 2026-08-09: the first cut of this file bucketed with
# speculative slot counts; Idle's index was right, so the FR verdict is
# unaffected — the descriptive table shifts. See the results doc note.)
IDLE = 33


def classes(c):
    total = sum(c.values()) or 1
    buckets = Counter()
    for ix, n in c.items():
        if ix <= 3:
            b = "move"
        elif ix <= 7:
            b = "rest"
        elif ix <= 11:
            b = "sleep"
        elif ix <= 15:
            b = "groom"
        elif ix == 16:
            b = "eat"
        elif ix == 17:
            b = "drink"
        elif ix < IDLE:
            b = "play/chase"
        else:
            b = "idle"
        buckets[b] += n
    return {b: n / total for b, n in sorted(buckets.items())}


ca, ct = classes(act_all), classes(act_talk)
tv = 0.5 * sum(abs(ca.get(b, 0) - ct.get(b, 0)) for b in set(ca) | set(ct))
print("\npooled composition read (NOT the FR verdict — announcing rows")
print("over-represent playful cats ~12:1, so pooled conditioning mixes")
print(f"behavior composition): TV {tv:.4f}, Idle {ca.get('idle',0):.4f} -> {ct.get('idle',0):.4f}")

# THE registered FR verdict is WITHIN-BEHAVIOR: the check is about the
# decider (does announcing distort what a cat does), so behavior
# composition must be held fixed.
ok = True
for b, (all_c, talk_c) in per_behavior.items():
    cb, tb = classes(all_c), classes(talk_c)
    tvb = 0.5 * sum(abs(cb.get(k, 0) - tb.get(k, 0)) for k in set(cb) | set(tb))
    idle_skew = tb.get("idle", 0) - cb.get("idle", 0)
    verdict = "PASS" if idle_skew <= 0.02 else "VOID (Idle skew)"
    ok &= idle_skew <= 0.02
    print(f"{b}: TV {tvb:.4f}, Idle {cb.get('idle',0):.4f} -> "
          f"{tb.get('idle',0):.4f} ({idle_skew:+.4f}) -> {verdict}")
print("FR acceptance:", "PASS" if ok else "VOID")
