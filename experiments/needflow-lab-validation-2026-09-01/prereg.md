# Needflow lab validation — preregistration
## (2026-09-01, Experiments; fog timeline step 2 primary: "scripted needs-driven lab worlds vs the needflow model's predicted bands"; bars pinned HERE, before collection)

Engine: main @ 055dc5b (same crate tree as dfa4b6b: 041 economy, 044/045
inert, contagion shelved). Debug build, headless local servers, tick_ms
40. Model under test: `../cuddle-economy-model/needflow.py`, tables in
its RESULTS.md (canonical baseline row and the serving-bump 2.0 row).

## Two deliverables, in order of importance

1. **Step 5's reference bands.** The measured scene mix of scripted
   `needs_driven` seats on the served world at the canonical 041 economy
   (`groom_cuddle_relief` 0.5). Whatever the model says, this is what
   the shakeout's INVESTIGATE line ("activity mix outside step-2 bands
   by modest factors") compares against. Reported as pooled rate with
   per-seed range, per class.
2. **Model validation.** needflow's own disclosure: "comparative mixes
   across scenarios are the deliverable; absolute rates are
   indicative." So the model is scored on its COMPARATIVE predictions
   between two economies it has priced (canonical 0.5 vs serving bump
   2.0), plus the emit/shape claims the timeline names. Absolute
   lab/model ratios are reported per class with no bar; a class off by
   more than 3× is recorded as a model gap in needflow's RESULTS.md
   "known misses", not as a failure of the economy.

## Arms and configs

`gen_configs.py` (committed beside this file) rewrites the served
`cloudkitty.toml` textually: all five seats `needs_driven`, tick_ms 40,
per-run seed/port/snapshot, no `[water]` block.

| arm | groom_cuddle_relief | needflow row |
|---|---|---|
| canon | 0.5 | canonical baseline (rest 12.8, cosleep 16.7, sleep-solo 3.0, groom self/other 4.3/15.8, play solo/duet 13.2/27.0, mean cuddle 7.6, mean bath 5.23, happiness 95.4) |
| serve | 2.0 (served today) | bump table 2.0 row (groom other/self 27.77/1.62, rest 5.72, cosleep 17.23, mean cuddle 6.71, mean bath 3.45, happiness 95.83) |

Three paired seeds per arm (20260901/02/03), six runs, sequential.

## Protocol (per run)

Fresh world (`--fresh --no-backup`); discard ticks < 1,500 (warmup);
measure **20,000 ticks** (100k cat-ticks) via `scene_census.py` polling
`/events/activity` + `/world` every 0.5 s (~12 ticks; retention 1,000
events, so nothing is lost). Archive final `/world` + `/welfare` and
the boot log. Raws → `results-raw/` (uncommitted, house rule).

Instrument rules (F-031): scenes off `/events/activity`, span
inclusive (+1), never `activity.state`. Classification reads the EVENT,
not the end-state: a partnered rest/cosleep whose partner wandered off
closes with `with_friend` absent but its tier counters intact, so
"partnered" = friend named at the end OR any `mutual_ticks`/`drip_ticks`.
On the recorded boot fixture this moved rest from 101 → 183 events
(end-state alone under-counts 45%). Guard: `test_scene_census.py`, five
literal pins on a recorded payload, each shown red in-run before
commit (end-state-only classification; dropped +1; started-based
window filter; duet/element swap; unfiltered polls).

## Validity gates (per run)

- `polls_in_window` ≥ 1,000 (0.5 s over ≥ 800 s wall).
- Watchdog quiet in the final `/welfare` (an alarm is reported, and
  the run's happiness is read with that in view; not a re-run trigger,
  since the economy under test is the served one).

## Pinned bars

**Emit gates (F-029; canon arm, EVERY seed)**
- E1 rest ≥ 1 scene in each of the four 5,000-tick sub-windows
  (sustained, not a startup transient).
- E2 both rest tiers emit: `mutual_emitting` ≥ 1 and `drip_emitting` ≥ 1.
- E3 nonzero: cosleep, sleep-solo, groom-self, groom-other, play-duet.

**Shape bars (canon arm, pooled)**
- S1 rest ≥ 1.0 / 1k cat-ticks.
- S2 cosleep : sleep-solo ≥ 3 : 1 (model 5.6 : 1; the timeline's "~6:1").

**Comparative model bars (canon vs serve; pooled, AND the same sign in
every seed pair)** — the model's predicted directions for the bump:
- M1 groom-other: serve > canon (model +76%).
- M2 groom-self: serve < canon (model −62%).
- M3 rest: serve < canon (model −55%).
- M4 mean bath: serve < canon (model −34%).
- M5 cosleep flat: |serve − canon| ≤ 0.25 × canon (model +3%).
- M6 play corridor flat: |Δ play total (duet+elem+solo)| ≤ max(2 / 1k,
  0.10 × canon). needflow has no critter hunting, so the lab's
  play-elem is outside its model; the corridor claim is about the
  total.

**Report, no bar**: mean cuddle (model −12%, likely within noise),
happiness (model +0.5), all absolute lab/model ratios, mean spans per
class (F-031: every mean should land on its config minimum; grooming
is the exception), rest-solo (posture-only rest — the fixture showed
zero, so a nonzero count here is itself a note), eat/drink rates.

## Verdicts

- Deliverable 1 stands whatever happens; the bands are the measured
  canon numbers.
- Model VALIDATED for step-2 purposes iff E1–E3, S1–S2, M1–M6 all
  hold. Any miss is named with its size; a directional miss (M1–M4
  reversed in pooled OR in any seed pair) is a model gap recorded in
  needflow's RESULTS.md; a flatness miss (M5/M6) says the bump moves
  a corridor the model called untouched, which is a step-3 note for
  the owner (the bump reverts at Gen 1 reseating either way).
- An emit-gate miss (E1–E3) is the one outcome that is about the
  ECONOMY, not the model: 041's rest niche not emitting under scripted
  seats would be a HALT-class question for the owner before step 5.

## What this is not

Not a measurement of the frozen served roster (policies re-decide
nothing when relief dials move); the post-041 census
(`../post041-census-2026-08-31.md`) covers that. Not a fog measurement;
step 5 re-derives bands on the locked fog config (step 6, second and
final re-baseline).
