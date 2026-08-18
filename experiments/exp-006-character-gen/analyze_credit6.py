#!/usr/bin/env python3
"""Class-credit re-baseline + F-004 bar re-derivation, post-wall stamp.

Prereg §9 rider (F-013/F-014/F-015 fired triggers): the 2026-08-09
recipe verbatim on the phase-1 collection base
(`collect-config.toml`) — 1,000 samples/class, 150 worlds/batch,
1,200-tick traces, t in [100, 1100), probe-seed 42, twin-probe at the
post-wall stamp. Analysis is the F-004 reference implementation
imported from world-search/search.py (channel_metrics,
cluster-robust by world), never re-derived here.

Batches: A-{all,groom-sleep-rest,eat-drink,play-chase} on worlds
875001-875150; B/C eat-drink replications on 875151-875300 /
875301-875450 (disjoint; the 840k band belongs to the 028-era
re-baseline, 870k to the trait screen).
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS / "tools" / "world-search"))
from search import channel_metrics  # noqa: E402  (the F-004 reference)

KEEP = ("significant_ticks", "band_ticks", "expected_fp", "S_0.998",
        "S_0.998_le600", "peak_k", "peak_amp", "mass_le_400",
        "last_band_end", "decision_point_density")

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
    keep = {k: m.get(k) for k in KEEP}
    print(f.stem, json.dumps(keep))

(HERE / "results-raw").mkdir(exist_ok=True)
p = HERE / "results-raw" / "class-credit.json"
p.write_text(json.dumps(out, indent=1, default=float) + "\n")
print(f"-> {p}")
