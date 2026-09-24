# World-size × density screen, with the meow-range axis — prereg DRAFT, 2026-09-24

**DRAFT — not frozen.** Freezes on the owner's word; nothing collects
before that. Her words (Experiments session, 2026-09-24): "I'd like to
see what happens on substantially larger worlds, with and without
distance on meows", then "Let's add 100x100 as well, with similar
element density, and a sweep of lower densities to get an idea of
sensitive to both size and density", then "draft". Fills the Gen 2
shelf's standing pointer (`GEN2-INPUTS.md` §Also standing: "World-size
× radius screen") on the size half; the radius axis stays pinned at 4
and open for a later leg.

**Pins the freeze confirms**: the seed band 900201–900230; the element
count table below (rounding: nearest, ties up); the per-size dir R
values (measured at freeze by the declared probes); the pilot rule.

## The questions

1. Do the served Gen 1 minds survive substantially larger worlds, and
   is their cost the world's or theirs (the scripted teacher pays the
   same world)?
2. Does exact range on meows start to matter when the world is big?
   At 20×20 it is worth at most 0.203 (F-052 third collection).
3. Does the channel's total load (intact vs rows) grow as the visible
   fraction shrinks? Vision radius 4 covers 41 tiles: 10% of 20×20,
   2.6% of 40×40, 0.41% of 100×100.
4. How does welfare move with element density at fixed size, for both
   rosters?

## Worlds (seven derived configs; nothing served changes)

All derived from `fog-gen1-cert/anchor-b3.toml` (20×20, floor 0, the
five served kitties) by a derive script with a guard asserting that
ONLY `world.width`, `world.height` and the five element `min`/`max`
pairs move; every config is loaded once in `ParallelEnv` at derivation
(the key-validity check) and its SHA-256 appended here. Density d =
the served per-tile counts scaled by (area/400) × d; served min/max:
water 7/9, chow 6/8, bug 3/7, greeble 1/3, sunbeam 4/5. TTLs,
servings, tethers and everything else stay byte-identical.

| config | size | d | water | chow | bug | greeble | sunbeam |
|---|---|---|---|---|---|---|---|
| size28.toml | 28×28 | 1 | 14/18 | 12/16 | 6/14 | 2/6 | 8/10 |
| size40.toml | 40×40 | 1 | 28/36 | 24/32 | 12/28 | 4/12 | 16/20 |
| size100.toml | 100×100 | 1 | 175/225 | 150/200 | 75/175 | 25/75 | 100/125 |
| size40-d2.toml | 40×40 | 1/2 | 14/18 | 12/16 | 6/14 | 2/6 | 8/10 |
| size40-d4.toml | 40×40 | 1/4 | 7/9 | 6/8 | 3/7 | 1/3 | 4/5 |
| size100-d2.toml | 100×100 | 1/2 | 88/113 | 75/100 | 38/88 | 13/38 | 50/63 |
| size100-d4.toml | 100×100 | 1/4 | 44/56 | 38/50 | 19/44 | 6/19 | 25/31 |

Two cells are worth naming: size40-d4 is the served counts on 4× the
area (the pure stretch), and size40-d2 duplicates size28's counts at
a different geometry.

## Legs (twenty, plus probes and a pilot)

All 30 × 20,000 on the served clock, `cert_harness_fog.py`, band
900201–900230, the same 30 seeds in every leg (paired within each
world config; across configs the seed names pair the draws, not the
worlds).

- **Set A — size × hearing at d = 1** (sizes 28, 40, 100; the 20×20
  column is the fog-deafening screen's recorded intact / dir16 / rows
  / scripted legs): per size, `scripted`, intact, `--deaf dir --dir-r
  <R_size>`, `--deaf rows`. Twelve legs.
- **Set B — density at intact hearing** (size40-d2, size40-d4,
  size100-d2, size100-d4): per config, `scripted` and intact. Eight
  legs.

**Per-size R** (Set A): the median heard-caller Manhattan distance on
that size's own intact world, measured at freeze by `dir_r_probe.py`
extended with `--config` and `--seed0 900201` (3 seeds × 5,000 ticks,
recorded to `results-raw/r-probe-<size>.json`); the values land here
before any dir leg runs. The 20×20 value on its own band was 16.

**Pilot rule**: before the full battery, one seed × 20,000 at
size100.toml intact, for runtime only; its outputs are not read for
claims. If a size100 leg exceeds 45 minutes, the size100 legs drop to
`--workers 3` overnight and the fact is recorded here as a deviation.

**Displaced minds, on the label**: observations normalise positions by
world dimensions, so the frozen minds read rescaled geometry — this
screen measures Gen 1 minds displaced to larger, sparser worlds, not
what a mind trained there would learn (doctrine rule 9); a world-size
choice for any future generation needs arms retrained at size. The
teacher's wants are sight-and-memory-gated the same way, which is what
makes the paired scripted leg the world's-own-cost control.

## Measures

The harness's recorded set per leg: mean happiness per seat,
nash_state, low_share, floor_touches, dist_ticks, max_distress_age
(and by seat), sleep and beam accounting with start-need bins, message
counts per kind. Encounter or travel rates are not instrumented and
not promised. Reads are paired per seed within a config; across
configs the quantities compared are per-config paired deltas and
roster-vs-teacher gaps.

## Predictions

1. **The channel's load grows with size**: the intact-vs-rows paired
   gap at 40×40 and at 100×100 each exceed the 20×20 gap (6.371), and
   the ordering 20 < 40 < 100 holds on the paired means.
2. **Range starts to pay**: the intact-vs-dir paired gap at 100×100
   exceeds the 20×20 gap (0.203) by more than the 100×100 pair's
   per-seed spread. The interesting failure is a flat gap: bearing
   suffices at any scale.
3. **Density bites monotonically**: at fixed size, intact-roster team
   happiness falls as d drops 1 → 1/2 → 1/4, and the scripted teacher's
   falls too; whether the roster's fall is steeper than the teacher's
   is reported, not predicted.
4. **The tail leads the mean** (the deafening arc's motif): in every
   cell where the mean moves past 0.15, dist_ticks moves by a larger
   factor. Crossings by name; any seat-shaped or Clementine-shaped
   concentration reported (F-043: the tail is a roster property).

## Decision rules

- The results land in this directory's RESULTS.md under the
  accuracy-gate contract (### Collect / ### Read fences, full paths,
  the reader shipping --out and --md) and gate before commit.
- The size and density curves feed the Gen 2 sitting (#389) as the
  shelf's world-size input; no number here picks a world — that is
  the sitting's ruling on the owner's word.
- A prediction-1 or -2 failure is a finding (bearing or the channel
  scale-invariant), not a rerun trigger. Any cell whose distress tail
  looks like harm at collection scale (a seat pinned in distress for
  thousands of ticks, the all-deaf signature) is reported to the owner
  with the cell named before any follow-up runs on that config.
- Nothing deploys; the served world keeps 20×20 and its density.

## Not in this screen

The radius axis (pinned 4; the shelf keeps world-size × radius open);
hearing arms crossed with density (a follow-up only where Set B shows
sensitivity); retraining at size (rule 9's answer, a later screen);
roster-size changes (five cats everywhere; the owner's density caveat
names roster a separate knob).

## Regeneration (filled at freeze)

### Collect

The derive step, the three R probes, the pilot, then the twenty legs
(exact commands with full paths land here at freeze, before any leg
runs). Never run by the gate.

### Read

The reader for this screen ships `--out` and `--md` and prints every
derived column its write-up uses; its command lands here at freeze.
