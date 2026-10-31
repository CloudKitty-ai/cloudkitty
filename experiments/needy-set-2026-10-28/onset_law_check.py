#!/usr/bin/env python3
"""Onset-law check (0 covered): 200 all-scripted N1 worlds, 200 ticks each,
count first onsets inside the first 200 ticks (levels 0-3, expected 0.4
under onset_weights [0.1, 0.1, 0.1, 0.1, 0.6]) and the per-level counts.
Seeds 2001-2200: outside every SEED-BANDS claim (1-1000 is the nearest).
Nothing is written to results-raw; the counts print to stdout."""
import json, sys
from pathlib import Path
import numpy as np

A = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28")
sys.path.insert(0, str(A))
sys.path.insert(0, str(A.parent / "seating-analysis-g2-2026-10-21"))
import needy_read as R  # noqa: E402
import seating_collect_g2 as C  # noqa: E402

TICKS = 200
LEVELS = [0, 2, 10, 50, 200]
seeds = list(range(2001, 2201))
onsets = []
for seed in seeds:
    arrays, meta = C.collect("scripted", seed, TICKS, 1000, config=A / "g2leg-20-N1.toml", abort_covered_only=True)
    held = np.flatnonzero(arrays["needy_phase"] == R.PHASES.index("held"))
    onsets.append(int(held[0]) if len(held) else None)
    print(seed, onsets[-1], flush=True)
opened = [o for o in onsets if o is not None]
print(json.dumps({"worlds": len(seeds), "ticks": TICKS, "opened_recorded_index": len(opened),
                  "opened_engine_tick_under_200": sum(1 for o in opened if o + 1 < 200),
                  "by_level_engine_tick": {f"[{LEVELS[i]},{LEVELS[i+1]})": sum(1 for o in opened if LEVELS[i] <= o + 1 < LEVELS[i + 1]) for i in range(4)},
                  "onsets": onsets}))
