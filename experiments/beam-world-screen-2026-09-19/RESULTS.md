# Beam-world screen — results, 2026-09-19

Prereg `PREREG.md` (a920ad8, committed before the first leg). 25 configs
× 2 seatings × 30 seeds × 20,000 ticks, served clock, all 50 legs
complete (`results-raw/run.log`, about 45 minutes). Reader
`screen_read.py` → `results-raw/screen-read.json`; the full 50-row
table is `screen_read.py results-raw/battery --md`. Raws uncommitted.

## The short version

- **Beam count sets where the teacher sleeps; lifetime adds a little;
  the relief numbers add nothing.** Share of the scripted teacher's
  naps that begin on a beam: 4 beams 0.31, 5 → 0.38, 6 → 0.44, 7 →
  0.48 at lifetime 300, each about 0.02 higher at 3,000. Off-beam
  relief 3 vs 5 and beam relief 7 vs 10 move that share by at most
  0.01. The reach gate in numbers.
- **Floor 3 lengthens off-beam naps, so the tick-weighted in-beam
  share falls by 0.07–0.08** even though placement is identical. The
  prereg's headline measure was the tick share, so prediction 1 fails
  as written and the package corner misses the 0.40 bar on that
  measure (0.365); on placement it clears (0.458). Which measure the
  corpus bar is read on is the owner's call (below).
- **The frozen Gen 1 minds follow count at one sixth the level and
  ignore lifetime and relief**: naps starting on a beam 0.046 (anchor)
  → 0.057 / 0.068 / 0.077 at 5 / 6 / 7 beams, the same at 300 and
  3,000 ticks, the same at every relief pair. Rule 9 in numbers.
- **Floor 3 costs the frozen roster under 0.1 happiness and crosses
  no line. More beams at the served relief do cross it**: seven of the
  twelve relief-5 variants put one seed of thirty over distress age
  150 (Biscuit four times, Kittybear three, worst 236), where the
  anchor reads 49 and every floor-3 variant reads under 150.
- **No farming.** Sleep need at nap start moves up under the slower
  floor, not down, on both seatings.

## Teacher (scripted roster): placement and tick share

Pooled over five seats and 30 seeds. Placement = share of sleep starts
on a beam tile; tick share = share of sleeping ticks on a beam (the
declared headline). Beam relief 7 shown; beam relief 10 sits within
0.01 of every cell.

| beams | lifetime | placement, floor 5 | placement, floor 3 | tick share, floor 5 | tick share, floor 3 |
|---|---|---|---|---|---|
| 4 (anchor) | 300 | 0.313 | | 0.299 | |
| 5 | 300 | 0.380 | 0.380 | 0.363 | 0.294 |
| 5 | 3000 | 0.406 | 0.407 | 0.391 | 0.319 |
| 6 | 300 | 0.437 | 0.435 | 0.419 | 0.343 |
| 6 | 3000 | 0.453 | 0.458 | 0.438 | 0.365 |
| 7 | 300 | 0.480 | 0.480 | 0.460 | 0.382 |
| 7 | 3000 | 0.508 | 0.505 | 0.492 | 0.408 |

Per seat at the package corner (s3-b7-t3000-n6, tick share): Miso
0.34, Biscuit 0.29, Pumpkin 0.44, Kittybear 0.40, Clementine 0.39;
anchor 0.29–0.31 at every seat. Conducted sleep (asleep off-beam beside
a direct partner on a beam) rises with count, 0.031 → 0.047 at six
beams. Sleep share of cat-ticks: 0.077 at the anchor, 0.074 at floor 5
with more beams, 0.086–0.088 at floor 3 (×1.17).

Why the tick share falls under floor 3 while placement does not: a nap
begun off-beam takes 13 ticks instead of 8 to clear the same need and a
nap on a beam still takes 6, so the off-beam naps carry more of the
sleeping ticks. The teacher never chose differently.

## Frozen Gen 1 roster (gen1-A)

| beams | lifetime | placement, floor 5 | placement, floor 3 | tick share, floor 5 | tick share, floor 3 | happiness, floor 5 → 3 | max distress age, floor 5 / 3 |
|---|---|---|---|---|---|---|---|
| 4 (anchor) | 300 | 0.046 | | 0.046 | | 92.49 | 49 |
| 5 | 300 | 0.057 | 0.058 | 0.057 | 0.053 | 92.45 → 92.35 | 21 / 40 |
| 5 | 3000 | 0.058 | 0.056 | 0.058 | 0.052 | 92.43 → 92.36 | **183** / 40 |
| 6 | 300 | 0.068 | 0.068 | 0.068 | 0.063 | 92.41 → 92.33 | 76 / 93 |
| 6 | 3000 | 0.067 | 0.068 | 0.067 | 0.063 | 92.40 → 92.32 | **162** / 133 |
| 7 | 300 | 0.076 | 0.074 | 0.076 | 0.068 | 92.40 → 92.31 | **181** / 66 |
| 7 | 3000 | 0.078 | 0.075 | 0.078 | 0.070 | 92.39 → 92.31 | **236** / 67 |

Beam relief 10 reads the same within 0.01 on every column; its own
crossings are s5-b10-t300-n7 (207), s5-b10-t3000-n5 (183),
s5-b10-t3000-n6 (151). Nash 0.923–0.925 everywhere. Per seat the
placement is Miso's: 0.09 at the anchor to 0.12 at six or seven beams,
Clementine 0.06 → 0.09, Kittybear 0.04 → 0.07, Biscuit and Pumpkin
under 0.02 throughout.

**The crossings.** Seven variants, one seed each, every one at the
served relief (floor 5): seed 870022 Kittybear at 183 twice (both
five-beam, 3,000-tick variants), 870019 Kittybear 236, 870004 /
870006 / 870014 / 870025 Biscuit at 181 / 162 / 151 / 207. None of the
twelve floor-3 variants crosses (max 133). The anchor on these seeds
reads 49 (the battery's served-clock read was 47). This is F-043's
roster tail moved by a world change: more or longer beams at the
served relief put the Biscuit and Kittybear seats over the line on
about one seed in thirty, which is the swap legs' rate (1.8% of runs).
Not a Gen 2 reading (the minds are frozen), but a deploy reading: the
served Gen 1 roster under a beam-count change alone is not the roster
the battery certified.

## Farming (rule 4)

Sleep need at a nap start, share under 5 / mean: teacher 0.08 / 15.9 at
the anchor, 0.04–0.06 / 16.4–17.8 on the floor-3 and more-beam
variants (beam relief 10 lifts the under-5 share to 0.10–0.11, +0.03);
gen1-A 0.42 / 6.8 at the anchor, 0.28 / 8.8 under floor 3. Nothing is
flagged (the rule was +0.10 on the under-5 share or ±5 on the mean).
The slower floor moves need at start up, which is the opposite of
farming; the frozen minds nap early by habit (42% of their naps begin
under need 5) and that habit does not change with the world.

## Predictions

1. **Fails as written.** Lifetime and count moved the teacher's tick
   share up in every one of the 20 declared contrasts, but the relief
   contrast is 0.07–0.08, not under 0.03. The cause is nap length, not
   placement; on placement the relief contrast is ≤ 0.01 and the
   prediction's intent holds. The measure was the wrong one for the
   claim, and that is on the prereg, not the world.
2. **Not cleared on the declared measure.** s3-b7-t3000-n6 reads 0.365
   in tick share (0.458 in placement). By the decision rule, count 7
   clears it (0.408) and lifetime past 3,000 would not (300 → 3,000
   bought 0.02).
3. **Holds.** gen1-A's tick share never exceeds 0.078; relief
   contrasts ≤ 0.009.
4. **Half holds.** Happiness under floor 3 drops 0.06–0.10 (predicted
   under 1.5); the sleep share rises ×1.06 (predicted about ×1.5 on
   off-beam naps; the naps lengthen but the frozen minds' nap count
   falls with it). The no-crossing clause fails, on the floor-5
   variants rather than the floor-3 ones (above).
5. **Holds.** No farming shift on either seating.

## Decision rules, applied

- **The corpus bar at count 6.** On the declared tick share the package
  corner is under 0.40, so the rule says count 7 or a longer lifetime,
  and the table says count 7. On placement, the share of the teacher's
  naps that begin on a beam, count 6 is at 0.458 and clears. Placement
  is what a clone has to imitate (the walk and the lie-down); the
  sleeping-on-a-beam rows are its consequence, and floor 3 changes
  their weight without changing a decision. Experiments' recommendation
  is to pin the bar on placement and keep the count the owner's visual
  call; the declared measure said otherwise, so this goes to her.
- **Distress crossings.** Reported by name above; no variant is dropped.
- **Nothing here changes the served world.**

## What this settles for the Gen 2 collection

The teacher's beam-seeking under the package is count-driven: about
0.06 of placement per extra beam, 0.02 for the long lifetime, nothing
from relief. Whatever count the owner picks, the corpus will carry
that share of beam-started naps, and the F-047 re-verify on the clone
reads against it. Floor 3 does its work on the clone's side of the
reward, not in the corpus, exactly as the mechanism note in the prereg
said; whether the clone answers it is tier 2.

## Regeneration

```
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/derive_configs.py \
  experiments/beam-world-screen-2026-09-19/results-raw/configs --sha experiments/beam-world-screen-2026-09-19/results-raw/configs/sha256.json
cp experiments/fog-gen1-cert/anchor-b3.toml experiments/beam-world-screen-2026-09-19/results-raw/configs/s5-b7-t300-n4.toml
nohup bash experiments/beam-world-screen-2026-09-19/run_screen.sh \
  experiments/beam-world-screen-2026-09-19/results-raw/configs experiments/beam-world-screen-2026-09-19/results-raw/battery 6 \
  > experiments/beam-world-screen-2026-09-19/results-raw/run.log 2>&1 &
experiments/exp-006-character-gen/.venv/bin/python experiments/beam-world-screen-2026-09-19/screen_read.py \
  experiments/beam-world-screen-2026-09-19/results-raw/battery --md --out experiments/beam-world-screen-2026-09-19/results-raw/screen-read.json
```
