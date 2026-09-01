# Need-flow model: predicted behavior mixes for the cuddle repricing
## (2026-08-26, `needflow.py`, guard `test_needflow.py`)

A ~200-line simulator of the engine's economy — `[needs]` rise rates,
clamped relief, min/max durations, early termination, conscription vs
availability, tiered payloads — under a greedy weighted-relief chooser
(a proxy for what Nash training rewards, not any particular policy).
Dials read from `cloudkitty.toml`; scenarios override in memory.

## Validation before prediction

Calibration (`EPS=0.3, TRAVEL=2, P_ADJ=0.3, ADJ_SPELL=30`) was frozen
against the measured world *before* any scenario ran:

| check | measured | model baseline |
|---|---|---|
| rest scenes | 0 in 869 + 605 ticks | 0.19/1k ≈ 0.9 expected in the owner's window — consistent with 0 |
| solo sleep | minimal, nonzero | 1.6 vs cosleep 26.1 |
| groom mix | both modes common | self 2.9 / other 19.8 |
| play venues | both | solo 11.5 / duet 29.4 |
| mean sleep · cuddle · bath | 5.0 · 5.1 · 4.8 | 4.7 · 3.2 · 4.4 |

Known misses, disclosed: eat mean 3.0 vs measured 8.6 (no Pumpkin
rise-override, bowls always full); play mean low (no critter hunting —
policy skill, out of scope); no refusal tax (conscription always
succeeds instantly, so the model *understates* the sibling variant's
advantage over conscripted rest — the tax is exactly what F-033
measured and what availability legality removes). **Comparative mixes
across scenarios are the deliverable; absolute rates are indicative.**

The adjacency model matters: per-tick resampling (a friend always one
tick away) erased solo sleep and self-groom entirely. Solo niches are
created by *persistent* separation. That is itself a finding about the
economy: diversity comes from state heterogeneity, and any world change
that shortens far-spells (smaller maps, higher density) will eat the
solo niches before any relief dial does.

## Predicted mixes (scenes / 1k cat-ticks, 30k-tick runs)

| scenario | rest | cosleep | solo sleep | groom self/other | play solo/duet | mean cuddle | happiness |
|---|---|---|---|---|---|---|---|
| baseline (served) | 0.2 | 26.1 | 1.6 | 2.9 / 19.8 | 11.5 / 29.4 | 3.2 | 96.6 |
| A+B: play drip on conscripted rest, riders saturating | **0.3** | 26.0 | 1.6 | 3.0 / 19.7 | 11.5 / 29.2 | 3.1 | 96.6 |
| C+D: riders partial (0.25/0.6, groom rider 0.5), rest conscript | **12.6** | 17.7 | 2.7 | 4.3 / 15.0 | 12.4 / 27.3 | 5.6 | 95.7 |
| sibling: riders partial + rest availability two-tier | **12.8** | 16.7 | 3.0 | 4.3 / 15.8 | 13.2 / 27.0 | 7.6 | 95.4 |
| sibling + play drip 0.25 | 13.3 | 16.7 | 2.9 | 3.9 / 16.2 | 12.5 / 26.7 | 7.3 | 95.4 |

## Readings

1. **The Small package (A+B) is confirmed dead**: 0.2 → 0.3 rest scenes
   per 1k. A play drip cannot buy a niche while three riders saturate
   cuddle. The doc's "probably won't clear non-zero" was right, and the
   mechanism is now identified: it patched *value* when the deficit was
   *demand*.
2. **Riders-partial alone is the load-bearing move**: rest jumps to
   ~12.5/1k — comparable to today's groom_other — with or without the
   legality change. Demand restoration is the whole game.
3. **The play drip adds ~0.5 rest scenes/1k. Drop lever B.** Play's mix
   moves by ~2/1k across every repricing scenario — the corridor is
   untouched, which was the owner's constraint.
4. **The diversity dividend lands where wanted**: solo sleep roughly
   doubles (1.6 → 2.7–3.0) while co-sleep stays dominant ~6:1; self-groom
   rises ~50% as the partial groom rider trims groom_other's edge.
5. **The cost is ~1 happiness point** (96.6 → 95.4–95.7): standing cuddle
   demand now exists (mean 3.2 → 5.6–7.6). Certification anchors would
   re-derive under any of these — SC-005-style re-baseline, as gated.
6. Conscript-vs-sibling barely differ *in this model* because the model
   has no refusal tax; the sibling's case rests on F-033's live
   measurement, not on these tables.

## Post-041 re-baseline + waterline contagion pricing (2026-08-30)

Spec 041 merged the sibling economy into the served config and retired
`cuddle_relief`, so `econ_from_config` now reads the 041 dial names and
the model's baseline IS the sibling row above: the migrated baseline
reproduces it exactly (rest_avail 12.8, cosleep 16.7, happiness 95.4),
and the retired pre-041 economy is kept as a scenario that reproduces
the old baseline row (rest 0.19, cosleep 26.1, happiness 96.6). The
guard's rest claim flipped with it: baseline rest must now be nonzero,
and rider saturation is the red arm.

This section prices the waterline contagion (ROADMAP, pre-fog
schema-break bundle): a dry cat in a partnered scene with an in-water
partner pays the wet-fur charge, `factor x bath_gain` (engine default
3.5, no `[water]` table in the served config), below the ceiling (60).
Exposure per scene-tick uses the two measured cross-waterline windows
from `waterline-pairing-rule-2026-08-24.md`, carried separately because
magnitude swings 3x between them: low = groom 9.0% / cosleep 6.4% /
duet 0%, high = groom 25.0% / cosleep 8.6% / duet 6.9%; rest_avail
borrows co-sleep's share (rest emitted no scenes pre-041, so it has no
window). Contagion draws ride their own rng stream, so arm-vs-baseline
differences are treatment, not stream divergence.

| arm (factor x window) | groom self/other | cosleep | rest | play solo/duet | mean bath | happiness |
|---|---|---|---|---|---|---|
| baseline (0) | 4.3 / 15.8 | 16.7 | 12.8 | 13.2 / 27.0 | 5.23 | 95.36 |
| 0.25 x low | 4.6 / 16.6 | 16.9 | 12.9 | 13.5 / 26.6 | 5.18 | 95.41 |
| 0.5 x low | 5.2 / 17.0 | 16.9 | 12.8 | 13.4 / 26.6 | 5.20 | 95.40 |
| 1.0 x low | 6.0 / 18.2 | 16.7 | 12.6 | 13.7 / 26.3 | 5.14 | 95.37 |
| 0.25 x high | 4.8 / 17.3 | 16.6 | 12.5 | 13.5 / 26.6 | 5.18 | 95.37 |
| 0.5 x high | 5.4 / 18.9 | 16.7 | 12.5 | 13.5 / 26.4 | 5.19 | 95.35 |
| 1.0 x high | 7.2 / 21.2 | 16.6 | 12.0 | 13.9 / 25.8 | 5.09 | 95.33 |

Readings:

1. **Grooming absorbs the whole charge.** Worst case (factor 1.0, high
   window): groom_other 15.8 -> 21.2/1k (+34%), groom_self 4.3 -> 7.2
   (+68%). Every other niche moves by at most ~1/1k.
2. **Welfare cost is nil at any factor tried.** Happiness spans
   95.33-95.41 across all seven arms, within one seed's resolution.
   Mean bath drifts slightly DOWN under the tax (5.23 -> 5.09): the
   charge lumps bath demand onto one cat, which gets serviced sooner,
   so the standing level falls even as inflow rises.
3. **The play corridor and the rest niche hold**: duet 27.0 -> 25.8,
   rest 12.8 -> 12.0, both only at the worst case.
4. This is F-016's shape, priced as intended: grooming rises, and under
   the contagion redesign that is the mechanism working (damp cleaning
   someone), not a loop feeding itself. For the owner's factor call the
   model says even 1.0 is welfare-benign at bath_gain 3.5; the visible
   consequence is a grooming-heavier mix, scaled by exposure.

Disclosed limits, beyond the model's standing gaps: the chooser is
charge-blind (incumbents never priced it; whether the scripted ladder
should weigh it is the banked anchor-probe's question); the wet
member's own occupancy charge is unmodeled, as is all water occupancy
in the baseline; `bath_ratio` is 1 under global rates, while real seats
span 0.5-2.0x, so the per-tick charge on the box would span 1.75-7.0
by seat. The scripted-anchor probe, not this table, prices per-seat
tails.

## Regeneration

```
cd experiments/cuddle-economy-model
python3 needflow.py            # scenario tables
python3 test_needflow.py       # guard; every assertion shown red in-run
```

## Serving-world groom bump pricing (2026-08-31)

Context: `041-cuddle-investigation-2026-08-31.md` — Clementine's
frozen e004 policy runs groom-for-cuddle at 56% of high-cuddle ticks,
but 041's `groom_cuddle_relief` 0.5 sits below her 0.7 rise (a futile
loop). Candidates re-arm the habit on the SERVING config only,
reverted at the Gen 1 retrain. 30k ticks, seed 7, served dials
otherwise.

| groom_cuddle_relief | groom_other | groom_self | rest_avail | cosleep | mean cuddle | mean bath | happiness |
|---|---|---|---|---|---|---|---|
| 0.5 (served) | 15.77 | 4.28 | 12.81 | 16.66 | 7.61 | 5.23 | 95.36 |
| 1.5 | 22.52 | 2.18 | 8.97 | 17.08 | 7.08 | 3.98 | 95.67 |
| 2.0 | 27.77 | 1.62 | 5.72 | 17.23 | 6.71 | 3.45 | 95.83 |

Readings:
- **Welfare-benign, slightly positive** at both candidates
  (95.36 → 95.67 / 95.83); every mean need improves or holds.
- **Grooming displaces rest in the scripted mix** — rest_avail
  −30% at 1.5, −55% at 2.0. This is a greedy-chooser artifact and
  does NOT transfer to the frozen serving roster (policies change no
  decisions when relief dials move), but it measures how far each
  value leans against 041's specialist design in scripted reference
  worlds. Step-2 validation bands use canonical configs, not the
  serving bump, so no conflict.
- Bath improves as a side effect (more grooming = more bath relief
  delivered); groom_self is crowded out by groom_other's better EV.
- For Clementine specifically: at 1.5 her net while grooming is
  +0.8/tick against the 0.7 rise (holds, barely); at 2.0 it is
  +1.3/tick and a 4-tick scene delivers 8.0 — one old-lifeline
  scene. **Lean: 2.0** — the margin at 1.5 is thin against her rise,
  and the displacement artifact does not apply to frozen seats.

Limits: scripted greedy chooser (comparative, not a forecast of the
frozen roster); bath_ratio 1; charge-blind chooser as disclosed in
the post-041 section.
