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

## Regeneration

```
cd experiments/cuddle-economy-model
python3 needflow.py            # scenario tables
python3 test_needflow.py       # guard; every assertion shown red in-run
```
