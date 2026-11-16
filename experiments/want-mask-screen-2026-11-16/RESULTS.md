# The want-mask screen: RESULTS (frozen minds, one seed a mind, 40×40)

Declared in `DECLARATION.md` (§3–§9 frozen at 401746fd); the record is
`experiments/gen2-deviations.md` entry 42, on her "As recommended"
(entry 40, ruling 6). Nothing here trains, seats or serves. Every
consequence in §8 of the declaration is hers.

## What ran

- **The mask.** In the observation handed to the policy, the six
  want-intensity cells of each of the four kitty rows are zeroed (24
  cells of 399): the need a friend's freshest want-call stamped. The
  call's kind, recency, rate and place stay. Hearer-side, evaluation
  only.
- **The minds.** The no-head final (`p2:p2-nohead-s1r`) and the
  true-needs final (`p2:p2-truth-s1`), both at 15.0M ticks on trunk
  seed 1, each in all five seats.
- **R-0 first** (replays of the two recorded unmasked 40×40 legs,
  nothing covered): the mask changes the greedy act on 0.0227 of the
  no-head final's 3,000,000 decision rows and 0.0236 of the truth
  final's. §4's stop (both under 0.001) did not fire.
- **The legs** (30 worlds × 20,000 ticks, g2cmp 905001–905030, the
  1,000-tick abort armed, a 3-world scout before each), run
  2026-11-16T06:49–06:52Z: `wantmask-nohead-s1` (scout worst streak
  88, leg 106) and `wantmask-truth-s1` (scout 402, leg 509). All
  clean, no abort.
- **Comparators** (recorded, no new burn): `p2u-nohead-s1` and
  `p2u-truth-s1` at 40×40, both whole.
- **Covered cost.** Two legs, 6.0M cat-ticks; two scouts, 0.6M; the
  guards' 300-tick runs, under 0.03M. About 6.6M, as declared.

## R-0: the mask's reach (`reads/reach.md`)

| mind | decision rows | rows whose greedy act changes | share |
|---|---|---|---|
| no-head final | 3,000,000 | 68,217 | 0.0227 |
| truth final | 3,000,000 | 70,924 | 0.0236 |

Nearly every row holds a live want-intensity cell (2,992,799 and
2,990,519 of 3,000,000), so splitting on live rows adds nothing.

## R-1: welfare (masked minus unmasked, paired by world; `reads/screen.md`)

| | worlds | mean | up | down | 95% interval |
|---|---|---|---|---|---|
| Δ_nohead | 30 | −0.117 | 1 | 29 | −0.145 to −0.089 |
| Δ_truth | 30 | −0.098 | 5 | 25 | −0.141 to −0.058 |
| D = Δ_truth − Δ_nohead | 30 | +0.018 | 16 | 14 | −0.033 to +0.069 |

Team happiness: the no-head final 89.007 unmasked, 88.891 masked; the
truth final 88.735 unmasked, 88.637 masked. The edge at 40×40 is
0.325.

## R-2: substitution inside the truth mind (`reads/screen.md`)

Zeroing the truth cells (0–7) changes 0.0469 of the truth final's
greedy acts on its unmasked leg (140,808 of 3,000,000 rows) and
0.0477 on its masked leg (143,009), a ratio of 1.02.

## R-3: the tail (replays; scores nothing; `reads/screen.md`)

| leg | lost cat-ticks | friends' moves while a cat is lost | closing on it | worlds with a 300+ streak | worst streak |
|---|---|---|---|---|---|
| no-head, unmasked | 1,081 | 1,344 | 0.519 | 0 | 294 |
| no-head, masked | 389 | 452 | 0.566 | 0 | 106 |
| truth, unmasked | 3,877 | 4,979 | 0.623 | 1 | 478 |
| truth, masked | 5,153 | 5,914 | 0.568 | 5 | 509 |

Lost = cuddle need at 90 or more, unpartnered, no friend in sight.

## Predictions scored (DECLARATION §7)

- **W0** (the mask changes 0.005–0.05 of the no-head final's acts,
  and a smaller share of the truth final's): **NOT MET**. The no-head
  share, 0.0227, is inside the band; the truth final's, 0.0236, is
  not smaller.
- **W1** (Δ_nohead inside the edge): **MET**, −0.117.
- **W2** (Δ_truth inside the edge): **MET**, −0.098.
- **W3** (the truth-cell share is higher on the masked leg, by less
  than a factor of two): **MET** by its letter, 0.0477 against 0.0469.
- Unscored expectation (lost cat-ticks rise under the mask on the
  no-head final and rise less on the truth final; no scout aborts):
  did not hold. Lost cat-ticks fell on the no-head final (1,081 to
  389) and rose on the truth final (3,877 to 5,153). No scout
  aborted.

## Decision rules, applied (DECLARATION §8)

Δ_nohead is −0.117, which is not below −0.325: **NOT LOAD-BEARING**.
Neither Δ is above +0.325 and Δ_truth is not below −0.325, so
nothing is outside expectation. R-2, read beside it: the truth-cell
share is 0.0469 unmasked and 0.0477 masked.

## What this says, and what it does not

- **Both minds use the stamped need a little, and equally.** The mask
  changes about 2.3% of each mind's acts and costs each about a tenth
  of a point of team happiness, a third of the edge. The cost is
  steady: 29 of 30 worlds down for the no-head final, 25 of 30 for
  the truth final.
- **Holding the true needs does not replace it.** The truth final
  loses as much as the no-head final (D +0.018, interval −0.033 to
  +0.069), and its reliance on its truth cells does not move when the
  calls' need is masked (0.0469 to 0.0477). The truth cells and the
  stamped need are not substitutes inside this trained policy.
- **So "the calls already carry the need" is not supported as the
  explanation of entry 37's LEVEL, as far as these six cells go.**
  What stays open: that knowing a friend's need does not convert to
  acting on it (entry 37, T4), and redundancy with the call's
  existence, kind and place, which the mask leaves in.
- **The tail moved in opposite directions.** Under the mask the
  no-head final's lost cat-ticks fell by 64% and its worst streak
  fell from 294 to 106, while the truth final's lost cat-ticks rose
  by 33% and its worlds with a 300+ streak went from 1 to 5. This
  read scores nothing and has no declared account; it is reported.
- **Not shown:** anything about minds trained without the stamped
  need (these were trained with it), about 100×100, or about the
  want-words themselves (F-052's re-verify clause is not discharged:
  this masks six cells, not the calls).

## Guards and reds

Seven guards, every red as predicted (entry 42): m1–m3 on the mask
and its place in the harness, m4–m7 on the reader. m4's first
mutation cycle was a no-op (the mutation command matched nothing) and
was re-run from a mutation file.

## Limitations

- Frozen minds off their training distribution: a loss is dependence
  or disorientation, and this screen cannot tell them apart beyond
  the differential and R-2.
- The mask removes the need's level, not the call.
- One seed a mind; 40×40 only.
- Uniform five-copy seatings are stress reads (F-017, F-044, F-060):
  the contrast holds, the level does not.
- Hearer-side only: speakers call as they were trained to.

## Regeneration

### Collect (her word per step; never run by the gate)

```
/Users/elizabethkelly/ai/cloudkitty/experiments/want-mask-screen-2026-11-16/run_legs_wantmask.sh wantmask-nohead-s1
/Users/elizabethkelly/ai/cloudkitty/experiments/want-mask-screen-2026-11-16/run_legs_wantmask.sh wantmask-truth-s1
```

### Read (fresh outputs to the gate's scratchpad `$OUT`, never over `reads/`; env inline; runtime declared)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/want-mask-screen-2026-11-16
# about 3 minutes, 8 workers
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_wantmask.py reach --out $OUT/reach.json --md
# about 4 minutes, 8 workers; reads $OUT/reach.json written by the line above
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_wantmask.py screen --out $OUT/screen.json --md
# seconds: the scouts' and legs' verdict lines and run headers
grep -h "^== " results-raw/legs/*/run.log > $OUT/runlog.txt
```

Accuracy gate stamp: **PASS**, 2026-11-16 (one round, a fresh
subagent). Claims: about 86 arithmetic, 10 threshold, 17
characterisation (15 supported, 2 WEAK and reported), 0 undecidable,
14 provenance. The two WEAK sentences, left as gated, both in "What
this says": "its reliance on its truth cells does not move when the
calls' need is masked (0.0469 to 0.0477)" and "The truth cells and the
stamped need are not substitutes inside this trained policy". The
share rose by 2,201 rows (1.6% relative) between two different legs
with no noise band read, so "does not move" is a judgment and not a
measured null, on one seed a mind. Gate notes: D and Δ_nohead are the
raw paired means and sit one unit off what the printed cells subtract
to; "the contrast holds" in Limitations is the declaration's sentence
(doctrine rule 7), not something the F-numbers beside it establish.
Raw-dir hash (`scripts/rawdir-hash.sh
experiments/want-mask-screen-2026-11-16/results-raw`): v1:07b15bb45990372c.
