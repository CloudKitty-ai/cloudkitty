#!/usr/bin/env python3
"""Arm E under the edge-4500 configs: the first scout seed of each of the 15 E
configs re-collected (800 ticks, all scripted, 0 covered) and every array
compared with the recorded edge-20000 world. Arm E draws its first onset
from level 0 ([0, 2)), which never reads the top edge, so the worlds must be
identical."""
import json, sys
from pathlib import Path
import numpy as np

A = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28")
sys.path.insert(0, str(A)); sys.path.insert(0, str(A.parent / "seating-analysis-g2-2026-10-21"))
import scout as SC  # noqa: E402
import seating_collect_g2 as C  # noqa: E402

seen, out = set(), []
for group, config, seed, ticks in SC.worlds("E"):
    if group in seen:
        continue
    seen.add(group)
    arrays, meta = C.collect("scripted", seed, ticks, SC.S1_STREAK, config=config, abort_covered_only=True)
    z = np.load(SC.paths(group, seed)[0], allow_pickle=False)
    keys = sorted(k for k in z.files if k != "meta")
    same = {k: bool(np.array_equal(z[k], arrays[k])) for k in keys}
    out.append({"group": group, "seed": seed, "arrays": len(keys), "all_equal": all(same.values()),
                "unequal": [k for k, v in same.items() if not v]})
    print(out[-1], flush=True)
print(json.dumps({"worlds": len(out), "all_equal": all(o["all_equal"] for o in out), "per_world": out}))
