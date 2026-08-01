# Pre-wet-fur water baseline (2026-08-01)

The now-or-never measurement from the wet-fur handover: how the served
world uses water on the **current engine, before the bath cost lands**.
Once wet-fur merges this becomes unregenerable (the post-022
dead-baselines lesson applied prospectively) — which is why it exists.
Descriptive replay; evaluate-once does not apply.

- **Engine**: main @ `c6050f5` (includes the pyo3 `elements()`
  accessor, PR #89 — dynamics identical to the pair-screen engine).
- **Config**: served `cloudkitty.toml`, sha256 `37b282cd978e6e62…`
  (24×24, Seating B: Miso=s6, Biscuit playful, Pumpkin needs_driven,
  Kittybear=s3). 8 water tiles in every seed's world.
- **Recipe**: `trainer/water_baseline.py` — seeds 1–10 × 20,000 ticks,
  pin-clock deploy semantics, the exact pair-screen replay recipe.
  **Checksum: mean Nash 0.8977**, matching
  [pair-screen-2026-07-31.md](pair-screen-2026-07-31.md) Seating B
  exactly — these are the registered trajectories, not a new
  evaluation. Per-seed JSONs in
  [water-baseline-2026-08-01/](water-baseline-2026-08-01/).

## Headline: the policies are water-indifferent, the scripted cats are not

Aggregate over 200,000 ticks (10 seeds × 20k):

| Kitty | On-water ticks | Occupancy | Entries | Mean dwell (ticks) |
|---|---|---|---|---|
| Miso (s6) | 16,563 | **8.28%** | 2,545 | 6.5 |
| Kittybear (s3) | 15,745 | **7.87%** | 1,935 | 8.1 |
| Pumpkin (needs_driven) | 3,473 | 1.74% | 1,497 | 2.3 |
| Biscuit (playful) | 2,809 | 1.40% | 799 | 3.5 |

The agents stand on water **5–6× as much** as the scripted cats, and
linger (dwell 6.5–8.1 ticks per entry vs 2.3–3.5). The scripted cats'
low numbers are `water_step_cost = 4.0` doing its job — they cross
briskly and drink from the bank; the policies never saw a reason to
care. This is the motivating observation of the BACKLOG wet-fur entry,
now quantified.

## What they do while standing on water

| Activity | Miso | Kittybear | Pumpkin | Biscuit |
|---|---|---|---|---|
| Idle (incl. transit) | 7,482 | 6,667 | 2,382 | 2,028 |
| **Sleeping** | 3,319 | 3,275 | 250 | 53 |
| **Grooming** | 2,359 | 2,781 | 240 | 6 |
| Drinking | 2,247 | 1,852 | 197 | 15 |
| Playing | 913 | 978 | 191 | 572 |
| Resting | 120 | 75 | 160 | 125 |
| Eating | 123 | 117 | 53 | 10 |

The agents don't just wade through — they **sleep and groom in the
pond** (~3.3k sleeping + ~2.4–2.8k grooming ticks each). Grooming
while sitting in water is the exact absurdity the wet-fur change is
aimed at. Post-change success signature: Idle-transit survives
(crossings are legitimate), Sleeping/Grooming-on-water collapses
toward the scripted cats' levels, Drinking unharmed.

## Drinking geometry (Article I exposure)

Drinking ticks by Manhattan distance to the nearest water tile:

| Kitty | Drinking on-tile (d=0) | Drinking beside (d=1) | On-tile share |
|---|---|---|---|
| Miso | 2,247 | 7,097 | **24.0%** |
| Kittybear | 1,852 | 7,047 | **20.8%** |
| Pumpkin | 197 | 3,877 | 4.8% |
| Biscuit | 15 | 1,582 | 0.9% |

Article I keeps water free as a *drinking destination* (routing), but
an occupancy-based bath gain will still touch a drinker **standing on**
the tile. Today that's ~21–24% of agent drinking (vs ~1–5% scripted).
Under the batch design this is benign — the bath<50 clamp means no
drink can end in distress — and mildly pedagogical (it teaches
drink-from-the-bank, which is what the scripted cats already do). Noted
for Product so the spec treats it as intended behavior, not a surprise;
and for the calibration probe, which should count drink-on-tile ticks
separately from wading when converting the dial into welfare delta.

## Per-seed on-water ticks (spread check)

| Seed | Miso | Biscuit | Pumpkin | Kittybear |
|---|---|---|---|---|
| 1 | 1,760 | 132 | 304 | 1,446 |
| 2 | 1,565 | 233 | 293 | 1,558 |
| 3 | 1,648 | 314 | 367 | 1,715 |
| 4 | 1,582 | 253 | 322 | 1,964 |
| 5 | 1,656 | 251 | 348 | 1,318 |
| 6 | 1,392 | 373 | 354 | 1,724 |
| 7 | 1,680 | 234 | 379 | 1,574 |
| 8 | 2,008 | 278 | 406 | 1,416 |
| 9 | 1,546 | 362 | 352 | 1,656 |
| 10 | 1,726 | 379 | 348 | 1,374 |

Stable across seeds — no burstiness caveat here (contrast F-012's
FollowMe correction): every seed shows the same agent/scripted split.

## Regeneration (valid only until wet-fur merges)

```
cd experiments/exp-001-bc-mappo/trainer
./.venv/bin/python water_baseline.py          # seeds 1-10
```

After the wet-fur batch lands, rerunning produces the *post*-change
numbers on new trajectories — the comparison IS the calibration probe
(register §2b), with this document as its frozen "before" side.
