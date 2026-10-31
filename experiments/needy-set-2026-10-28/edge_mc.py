#!/usr/bin/env python3
"""Top-edge Monte Carlo on the pooled arm N scout (100 worlds, real payloads).

Model per world: onset drawn as the engine draws it (weighted level, log-uniform
tick in [lo, hi)); the first crossing is onset + the real first-window offset
(crossing H - onset) sampled from the 100 worlds' first windows (bath-only
masks and already-grave-at-onset worlds give no crossing, kept as their real
outcome); an onset past 6,000 opens nothing. The engine law is
crates/cloudkitty-core/src/needy.rs tick_within (log-uniform, floor, clamp).
"""
import json, math, random, sys
from pathlib import Path

A = Path("/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28")
d = json.load(open(A / "reads/scout-N.json"))
recs = d["records"]
TICKS = 6000
LEVELS = [0, 2, 10, 50, 200, 20000]
WEIGHTS = [0.1, 0.1, 0.1, 0.1, 0.6]
STRATA = [("H0", 0, 2), ("H1", 2, 100), ("H2", 100, 300), ("H3", 300, 1250), ("H4", 1250, 6000)]

# the real first-window outcomes: offset of the first crossing from the onset, or None
offsets = []
for r in recs:
    f = r["first"]
    if f is None:
        continue  # no onset before 6,000 in the real world: no offset to learn from
    c = f.get("crossing")
    if c is None:
        offsets.append(None)
    elif c["H"] < f["onset"]:
        offsets.append(("pre", None))  # already grave at onset (an unmasked crossing earlier)
    else:
        offsets.append(c["H"] - f["onset"])
n_none_real = sum(1 for r in recs if r["first"] is None)
print(f"records {len(recs)}; real first windows {len(offsets)}; no onset {n_none_real}; "
      f"no-crossing windows {sum(1 for o in offsets if o is None)}; pre-grave {sum(1 for o in offsets if isinstance(o, tuple))}")

def tick_within(rng, lo, hi):
    u = rng.random()
    lo_p = max(lo, 1)
    hi_f = max(hi, lo + 1)
    t = math.floor(math.exp(math.log(lo_p) + u * (math.log(hi_f) - math.log(lo_p))))
    return min(max(t, lo), max(hi - 1, lo))

def level(rng):
    u = rng.random(); c = 0.0
    for i, w in enumerate(WEIGHTS):
        c += w
        if w > 0 and c > u:
            return i
    return 4

def stratum(H):
    for name, lo, hi in STRATA:
        if lo <= H < hi:
            return name
    return "none"

def sim(top, n=200000, seed=1):
    rng = random.Random(seed)
    lv = LEVELS[:-1] + [top]
    counts = {k: 0 for k in ["H0", "H1", "H2", "H3", "H4", "none", "nocross"]}
    for _ in range(n):
        L = level(rng)
        onset = tick_within(rng, lv[L], lv[L + 1])
        if onset >= TICKS:
            counts["none"] += 1; continue
        off = rng.choice(offsets)
        if off is None:
            counts["nocross"] += 1; continue
        if isinstance(off, tuple):
            counts["nocross"] += 1; continue  # pre-grave: not a masked first crossing
        H = onset + off
        counts[stratum(H) if H < TICKS else "none"] += 1
    return {k: v / n for k, v in counts.items()}

def size(shares):
    s = min(shares["H2"], shares["H3"], shares["H4"])
    w = 2
    while 5 * w * s < 50:
        w += 2
    total = 800000 + 480000 + 64000 + 10000 + 5 * w * 6000 * 4 + 5 * 16 * 800 * 4
    return s, w, total

tops = [int(x) for x in sys.argv[1:]] or [20000, 6000, 5000, 4500, 4000, 3500, 3000]
print(f"{'top':>6} {'H2':>6} {'H3':>6} {'H4':>6} {'none':>6} {'nocr':>6} {'min':>6} {'w':>4} {'total':>11}")
for top in tops:
    sh = sim(top)
    s, w, total = size(sh)
    print(f"{top:>6} {sh['H2']:6.3f} {sh['H3']:6.3f} {sh['H4']:6.3f} {sh['none']:6.3f} {sh['nocross']:6.3f} {s:6.3f} {w:>4} {total:>11,}")
