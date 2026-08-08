"""Initiation-conditioned decision values + playful dynamics."""
import json, math
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/exp-003-water-schema/raw/bc-v3")
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
COOLDOWN = 10
GROUPS = {"eat": ([16], 0), "drink": ([17], 1), "sleep_solo": ([8], 2),
          "sleep_with": ([9,10,11], 2), "cuddle_rest": ([5,6,7], 4),
          "bath_groomself": ([12], 5)}
dec = {b: defaultdict(list) for b in ("needs_driven", "playful")}
dyn = {b: defaultdict(lambda: dict(ep=0, dwell=0, emits=0, ticks=0))
       for b in ("needs_driven", "playful")}

for d in sorted(ROOT.iterdir()):
    if not d.is_dir(): continue
    meta = json.load(open(d / "meta.json"))
    experts = {int(k): v for k, v in meta["experts"].items()}
    needs = np.asarray(np.load(d / "obs.npy", mmap_mode="r")[:, 0:6], np.float32)
    label = np.asarray(np.load(d / "label.npy", mmap_mode="r"))
    kitty = np.asarray(np.load(d / "kitty.npy", mmap_mode="r"))
    tick = np.asarray(np.load(d / "tick.npy", mmap_mode="r"))
    for kid, beh in experts.items():
        sel = kitty == kid
        nv, lb, tk = needs[sel], label[sel], tick[sel]
        o = np.argsort(tk, kind="stable"); nv, lb, tk = nv[o], lb[o], tk[o]
        starts = np.ones(len(lb), bool); starts[1:] = lb[1:] != lb[:-1]
        for tag, (labels, j) in GROUPS.items():
            m = np.isin(lb, labels) & starts
            if m.any(): dec[beh][tag].append(nv[m, j])
        for j in range(6):
            col = nv[:, j]
            for t in (0.30, 0.40, 0.50, 0.60):
                above = col >= t
                a = dyn[beh][(j, t)]; a["ticks"] += len(col)
                if not above.any(): continue
                diff = np.diff(above.astype(np.int8))
                s = list(np.where(diff == 1)[0] + 1); e = list(np.where(diff == -1)[0] + 1)
                if above[0]: s = [0] + s
                if above[-1]: e = e + [len(above)]
                for si, ei in zip(s, e):
                    dw = ei - si
                    a["ep"] += 1; a["dwell"] += dw; a["emits"] += math.ceil(dw / COOLDOWN)

print("=== NEED AT ACTION *INITIATION* (x100) ===")
for beh in ("needs_driven", "playful"):
    print(f"-- {beh}")
    for tag, chunks in sorted(dec[beh].items()):
        v = np.concatenate(chunks) * 100
        print(f"  {tag:16} n={len(v):6}  mean={v.mean():5.1f}  p10={np.percentile(v,10):5.1f}  "
              f"med={np.percentile(v,50):5.1f}  p90={np.percentile(v,90):5.1f}  p99={np.percentile(v,99):5.1f}")
print()
print("=== DYNAMICS: eps/1k, mean dwell, emits/1k @cooldown10 ===")
for beh in ("needs_driven", "playful"):
    print(f"-- {beh}")
    for j, n in enumerate(NEEDS):
        line = f"  {n:6}"
        for t in (0.30, 0.40, 0.50, 0.60):
            a = dyn[beh][(j, t)]
            if a["ep"] == 0: line += f" | T{int(t*100)}: -        "; continue
            line += (f" | T{int(t*100)}: {a['ep']/a['ticks']*1000:4.1f}ep dw{a['dwell']/a['ep']:4.0f} em{a['emits']/a['ticks']*1000:5.1f}")
        print(line)
