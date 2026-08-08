"""Needs data for the meow announce-threshold decision (exp-004 §5).

Reads dataset v3 (1.9M scripted kitty-tick rows, obs[0:6] = needs /100)
and reports, per need:
  1. occupancy: share of kitty-ticks with need >= T
  2. dynamics at T: episodes per 1k ticks, mean/median dwell above T,
     and expected meow emits per 1k ticks under cooldown 10
     (emits = sum(ceil(dwell/10)))
  3. decision-conditioning: the need's value at the moment scripted cats
     choose the matching self-relief action (where self-help kicks in)
Split by expert behavior (needs_driven vs playful).
"""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/exp-003-water-schema/raw/bc-v3")
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
THRESHOLDS = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.90]
COOLDOWN = 10

# label -> (need index, tag) for decision-conditioning
DECISION_MAP = {}
DECISION_MAP[16] = (0, "eat@Eat")
DECISION_MAP[17] = (1, "drink@Drink")
DECISION_MAP[8] = (2, "sleep@SleepSolo")
for l in (9, 10, 11):
    DECISION_MAP[l] = (2, "sleep@SleepWith")
for l in (5, 6, 7):
    DECISION_MAP[l] = (4, "cuddle@RestWith")
DECISION_MAP[12] = (5, "bath@GroomSelf")

occ = {b: np.zeros((6, len(THRESHOLDS)), np.int64) for b in ("needs_driven", "playful")}
rows = {b: 0 for b in ("needs_driven", "playful")}
# dynamics accumulators: per behavior, need, threshold -> [episodes, dwell_ticks, emits, trace_ticks, dwells list capped]
dyn = {b: defaultdict(lambda: dict(ep=0, dwell=0, emits=0, ticks=0, dwells=[]))
       for b in ("needs_driven", "playful")}
dec = {b: defaultdict(list) for b in ("needs_driven", "playful")}

for d in sorted(ROOT.iterdir()):
    if not d.is_dir():
        continue
    meta = json.load(open(d / "meta.json"))
    experts = {int(k): v for k, v in meta["experts"].items()}
    obs = np.load(d / "obs.npy", mmap_mode="r")
    label = np.load(d / "label.npy", mmap_mode="r")
    kitty = np.load(d / "kitty.npy", mmap_mode="r")
    tick = np.load(d / "tick.npy", mmap_mode="r")
    needs = np.asarray(obs[:, 0:6], np.float32)
    kitty = np.asarray(kitty)
    label = np.asarray(label)
    tick = np.asarray(tick)

    for kid, beh in experts.items():
        sel = kitty == kid
        nv = needs[sel]
        lb = label[sel]
        tk = tick[sel]
        order = np.argsort(tk, kind="stable")
        nv, lb, tk = nv[order], lb[order], tk[order]
        rows[beh] += len(nv)
        for j in range(6):
            col = nv[:, j]
            for ti, t in enumerate(THRESHOLDS):
                occ[beh][j, ti] += int((col >= t).sum())
            # dynamics per threshold: run lengths of consecutive rows above t
            for t in (0.30, 0.40, 0.50, 0.60, 0.75):
                above = col >= t
                if not above.any():
                    dyn[beh][(j, t)]["ticks"] += len(col)
                    continue
                # boundaries of runs
                diff = np.diff(above.astype(np.int8))
                starts = list(np.where(diff == 1)[0] + 1)
                ends = list(np.where(diff == -1)[0] + 1)
                if above[0]:
                    starts = [0] + starts
                if above[-1]:
                    ends = ends + [len(above)]
                a = dyn[beh][(j, t)]
                for s, e in zip(starts, ends):
                    dw = e - s
                    a["ep"] += 1
                    a["dwell"] += dw
                    a["emits"] += math.ceil(dw / COOLDOWN)
                    if len(a["dwells"]) < 200000:
                        a["dwells"].append(dw)
                a["ticks"] += len(col)
        # decision conditioning
        for l, (j, tag) in DECISION_MAP.items():
            v = nv[lb == l, j]
            if len(v):
                dec[beh][tag].append(v)

print("rows:", rows)
print()
print("=== 1. OCCUPANCY: share of kitty-ticks with need >= T (%) ===")
for beh in ("needs_driven", "playful"):
    print(f"-- {beh} ({rows[beh]} rows)")
    print("  need   " + "".join(f"{int(t*100):>7}" for t in THRESHOLDS))
    for j, n in enumerate(NEEDS):
        print(f"  {n:6} " + "".join(f"{occ[beh][j, ti]/rows[beh]*100:>6.2f} "
                                    for ti in range(len(THRESHOLDS))))
print()
print("=== 2. DYNAMICS above T (needs_driven): eps/1k ticks, mean dwell, median dwell, emits/1k @cooldown10 ===")
for j, n in enumerate(NEEDS):
    line = f"  {n:6}"
    for t in (0.30, 0.40, 0.50, 0.60, 0.75):
        a = dyn["needs_driven"][(j, t)]
        if a["ep"] == 0:
            line += f" | T{int(t*100)}: -"
            continue
        dws = np.array(a["dwells"])
        line += (f" | T{int(t*100)}: {a['ep']/a['ticks']*1000:.1f}ep "
                 f"dw{a['dwell']/a['ep']:.0f}/{int(np.median(dws))} "
                 f"em{a['emits']/a['ticks']*1000:.1f}")
    print(line)
print()
print("=== 3. NEED VALUE AT SELF-RELIEF DECISIONS (x100) ===")
for beh in ("needs_driven", "playful"):
    print(f"-- {beh}")
    for tag, chunks in sorted(dec[beh].items()):
        v = np.concatenate(chunks) * 100
        print(f"  {tag:ekw20}" if False else f"  {tag:20} n={len(v):7}  "
              f"mean={v.mean():5.1f}  p10={np.percentile(v,10):5.1f}  "
              f"median={np.percentile(v,50):5.1f}  p90={np.percentile(v,90):5.1f}")
