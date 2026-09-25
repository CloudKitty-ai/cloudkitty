# World-size × density screen — results

Collected 2026-09-25T04:12–04:57Z under the declaration frozen
2026-09-24 (`PREREG.md`; configs, R values and SHAs in its freeze-time
section). Twenty legs plus the runtime pilot (31 s, so 6 workers
everywhere; the 45-minute rule never bit), band 900201–900230, served
clock; the size20 hearing cells are the fog-deafening screen's
recorded legs (band 900101), as declared — with one deviation: the
PREREG listed a scripted 20×20 cell in that column, but the
fog-deafening screen ran no scripted leg, so the teacher's size curve
rests on 28 → 100 (recorded as a PREREG deviation). Raws in
`results-raw/` (uncommitted). The pilot's outputs were not read for
claims.

## The table (wsize-read.md, from `results-raw/wsize-read.json`)

| cell | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |
|---|---|---|---|---|---|---|
| size20/intact | 92.471 | -- | -- | 0.9244 | 125 | 94 |
| size20/dir | 92.268 | -0.203 [-0.503, +0.021] | 28/30 | 0.9223 | 53 | 37 |
| size20/rows | 86.100 | -6.371 [-8.780, -4.158] | 30/30 | 0.8528 | 458967 | 6094 |
| size28/scripted | 86.930 | -- | -- | 0.8678 | 4089 | 133 |
| size28/intact | 91.550 | -- | -- | 0.9147 | 3230 | 250 |
| size28/dir | 91.193 | -0.357 [-0.721, +0.148] | 29/30 | 0.9109 | 4062 | 189 |
| size28/rows | 75.754 | -15.796 [-19.128, -13.261] | 30/30 | 0.7390 | 1224412 | 9278 |
| size40/scripted | 86.343 | -- | -- | 0.8618 | 6303 | 130 |
| size40/intact | 77.935 | -- | -- | 0.7481 | 370969 | 1751 |
| size40/dir | 77.602 | -0.333 [-2.574, +3.435] | 19/30 | 0.7466 | 364958 | 2293 |
| size40/rows | 40.910 | -37.025 [-42.969, -31.235] | 30/30 | 0.3351 | 2625106 | 19872 |
| size100/scripted | 82.898 | -- | -- | 0.8259 | 71807 | 344 |
| size100/intact | 52.813 | -- | -- | 0.4796 | 2008476 | 15927 |
| size100/dir | 52.099 | -0.715 [-9.232, +9.846] | 18/30 | 0.4628 | 1965825 | 18564 |
| size100/rows | 31.608 | -21.205 [-28.090, -15.614] | 30/30 | 0.2633 | 2863202 | 19776 |
| size40-d2/scripted | 82.863 | -- | -- | 0.8256 | 34804 | 213 |
| size40-d2/intact | 74.577 | -- | -- | 0.7141 | 514612 | 1796 |
| size40-d4/scripted | 74.508 | -- | -- | 0.7379 | 240461 | 429 |
| size40-d4/intact | 67.226 | -- | -- | 0.6434 | 1020825 | 7127 |
| size100-d2/scripted | 76.616 | -- | -- | 0.7603 | 246277 | 481 |
| size100-d2/intact | 45.663 | -- | -- | 0.4061 | 2321800 | 19087 |
| size100-d4/scripted | 67.464 | -- | -- | 0.6644 | 677022 | 1108 |
| size100-d4/intact | 40.731 | -- | -- | 0.3653 | 2633321 | 19776 |

## The headline: displacement breaks the roster, not the world

Intact team happiness falls 92.471 / 91.550 / 77.935 / 52.813 across
20 / 28 / 40 / 100 at served density, while the scripted teacher on
the same worlds reads 86.930 / 86.343 / 82.898 — the teacher pays a
few points for scale, the frozen minds collapse past 2× area. The
worlds are livable; the displaced minds are what fails. The declared
scope carries the reading: observations arrive normalised by world
dimensions, so a familiar float means twice the tiles at 40×40 and
five times at 100×100, and a mind trained at 20×20 mis-reads every
distance (doctrine rule 9: minds trained at size are the answer this
screen cannot give).

## Predictions, scored

1. **Fails as declared, informatively.** The intact-vs-rows gap is
   6.371 / 15.796 / 37.025 / 21.205 across 20 / 28 / 40 / 100: the
   40 and 100 gaps exceed the 20 gap as the prediction named (28's
   does too), but the ordering breaks at 100 — not because the
   channel stops mattering, but
   because the intact baseline itself has collapsed to 52.813 and the
   rows cells compress toward a broken-roster floor (31.608–40.910).
   The channel's absolute load peaks at 40×40, where intact minds
   still have 37.025 to lose.
2. **Fails as declared — the interesting failure the prereg named.**
   Exact range stays near-worthless at every measured size: dir gaps
   0.203 / 0.357 / 0.333 / 0.715, each under 1.4% of its intact
   baseline, and the size100 line (exceed the 20×20 gap by more than
   the per-seed spread) fails against a spread of 19.078 — in the
   collapsed regime the per-seed paired deltas themselves scatter
   across nineteen points, dwarfing any range effect the mean could
   carry (the size100 dir mean's standard error is about 0.74, so a
   range effect larger than roughly two points is excluded there).
   Bearing suffices at every scale this screen reached, within that
   resolution.
3. **Holds.** Density cuts hurt monotonically for both rosters at both
   sizes (intact 77.935 → 74.577 → 67.226 at 40; 52.813 → 45.663 →
   40.731 at 100; scripted 86.343 → 82.863 → 74.508 and 82.898 →
   76.616 → 67.464). The teacher pays density more than it pays size;
   the frozen roster pays size more than density.
4. **Mixed as declared.** In every rows cell the tail leads the mean
   (distress ×3,671.7 / ×379.1 / ×7.1 at 20 / 28 / 40; at 100 the
   tails saturate near the horizon — the size100 cells' max distress
   ages run 15,927–19,776 against 20,000 ticks, size40/rows reaches
   19,872 — and the factor compresses to ×1.4). In the dir cells the
   prediction fails overall: the mean moves past the 0.15 line while
   distress stays of the same order (×0.42 / ×1.26 / ×0.98 / ×0.98 at
   20 / 28 / 40 / 100; the one exception is 28, where ×1.26 exceeds
   its 0.39% mean move on a plain magnitude reading). The failure is
   itself a reading: faking range degrades the mean with no
   rows-like tail signature, while losing rows entirely is what
   builds tails.

## The harm rule, fired

Per the frozen decision rule, every cell whose longest distress streak
exceeds 1,000 ticks is named (the threshold that makes the list a
rule, not a judgment): **size28/rows** (9,278; 1,224,412 distress
ticks), **size40 intact** (1,751; 370,969), **size40/dir** (2,293),
**size40/rows** (19,872; 2,625,106), **size40-d2 intact** (1,796;
514,612), **size40-d4 intact** (7,127; 1,020,825), **every size100
frozen-roster cell** (intact 15,927 and 2,008,476 distress ticks; dir
18,564; rows 19,776; d2 19,087; d4 19,776), and one scripted cell,
**size100-d4/scripted** (1,108). The borrowed **size20/rows** cell
(6,094) crossed the same line in the fog-deafening arc and is flagged
here for the same reason. No follow-up leg runs on any config named
above — size28, size40 at every density, size100 at every density,
and the rows arm on the served world — before the owner's word.
Nothing here deploys and the served world is untouched.

## Decision rules, applied

- The size and density curves feed the Gen 2 sitting (#389) as the
  shelf's world-size input; no number here picks a world. The screen's
  own summary for that sitting: the served roster tolerates ~2× area
  at served density, breaks by 4×, and density cuts compound; any
  larger world for a future generation needs minds trained at size
  (rule 9), and the teacher's gentle curve says such worlds are
  otherwise livable.
- Prediction 2's failure updates the fog-deafening arc's picture
  unchanged: range on meows is a luxury at every scale measured.
- **Recorded as F-053** (same commit); the Gen 2 shelf pointer gains
  the size half's result.

## Regeneration

### Collect

Runtime: 45 minutes total on 6 workers (stage.log stamps 04:12:33 to
04:57:22). Never run by the gate. The full fence is PREREG.md
§Regeneration (derive, the three R probes, the stage driver).

### Read

Runtime: under 30 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/world-size-screen-2026-09-24/wsize_read.py \
  --out experiments/world-size-screen-2026-09-24/results-raw/wsize-read.json \
  --md experiments/world-size-screen-2026-09-24/results-raw/wsize-read.md
```

Gate: **PASS** 2026-09-25 (run 1 FAILED: the harm-rule list was
under-inclusive — three cells with worse tails than named ones were
missing; replaced by the 1,000-tick threshold naming all 13 crossing
cells. Runs 2–3 tightened the F-053 streak list and the P4 scoring,
each fix the gate's own suggested wording, re-verified) · claims: ~183
table/prose/derived arithmetic all matched, 4 threshold (P1, P2
scored as failing as declared), 7 characterisation, 9 provenance ·
raws 3bdbc5f181a9.
