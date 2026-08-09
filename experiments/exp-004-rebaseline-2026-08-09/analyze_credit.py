#!/usr/bin/env python3
"""F-015 re-verify + F-004 world-count re-derivation on the 028 engine.

Class-conditioned twin-probe credit, the 2026-08-03 recipe on the v5
family base: 1,000 samples/class, 150 worlds/batch, 1,200-tick traces,
probe-seed 42. Analysis is the F-004 reference implementation imported
from world-search/search.py (channel_metrics — cluster-robust by world),
never re-derived here.

Batches: A-{all,gsr,ed,pc} on worlds 840001–840150; B-ed/C-ed are the
F-004 replication batches on disjoint 150-world bands (840151–840300,
840301–840450).
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "tools" / "world-search"))
from search import channel_metrics  # noqa: E402  (the F-004 reference)

out = {}
for f in sorted((HERE / "raw" / "class-credit").glob("*.jsonl")):
    traces, worlds, density = [], [], None
    for line in open(f):
        row = json.loads(line)
        if "dr" in row:
            traces.append(row["dr"])
            worlds.append(row["world_seed"])
        elif "decision_point_density" in row:
            density = row["decision_point_density"]
    m = channel_metrics(traces, worlds)
    m["n_samples"] = len(traces)
    m["n_worlds"] = len(set(worlds))
    m["decision_point_density"] = density
    out[f.stem] = m
    keep = {
        k: m.get(k)
        for k in (
            "significant_ticks",
            "band_ticks",
            "expected_fp",
            "S_0.998",
            "S_0.998_le600",
            "peak_k",
            "peak_amp",
            "mass_le_400",
            "last_band_end",
            "decision_point_density",
        )
    }
    print(f.stem, json.dumps(keep))

json.dump(out, open(HERE / "class-credit.json", "w"), indent=1)
