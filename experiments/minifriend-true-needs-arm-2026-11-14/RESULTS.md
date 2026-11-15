# Mini-friend Phase 2c, the true-needs arm: RESULTS (one seed)

Declared in `DECLARATION.md` (§3–§9 frozen at e4a3c22c); the record is
`experiments/gen2-deviations.md` entry 37. One seed clears nothing; the
consequences in §8 of the declaration are hers. The arm's networks act
on facts no cat under fog has: a measurement, never seated, served or
used as a teacher.

## What ran

- **The arm.** `p2-truth-s1`: the needs-only arm with one thing
  changed. The nine cells on each friend's row hold her true five
  hidden needs, happiness, bath and grave flag (the engine's
  start-of-tick state) in place of the needs head's estimates. Grafted
  from trunk seed 1, run index 124. Launched 2026-11-15T05:42:23Z at
  HEAD defb9b0e.
- **Its end.** The plateau rule, at 15,000,576 ticks (update 4,882
  inclusive), no harm stop. `policy-final.pt` sha256 begins
  e33b7698b270375b; the 12M checkpoint `ckpt-u3906.pt` begins
  5f444f574b95a4a1. 97 probes, one every 50 updates: the worst
  distress streak is 199 ticks against the line of 300, the next two
  134 and 116.
- **The legs** (30 worlds × 20,000 ticks, g2cmp 905001–905030, the
  1,000-tick abort armed, a 3-world scout before each 40×40 leg):

| seating | size | verdict |
|---|---|---|
| `p2u-truth-s1-u3906` (the 12M checkpoint) | 20×20 leg | clean, worst streak 9 |
| | 40×40 scout, leg | clean, 67; clean, 95 |
| | 100×100 scout (905001–905003, tail read only) | streaks 751 and 576; 905003 aborted at tick 18,498 |
| `r6-nohead-s1-u3906` (the no-head 12M checkpoint, call 5) | 20×20 leg | **stopped: world 905029 aborted at tick 1,299**; 29 worlds whole, streak 0 |
| `p2u-truth-s1` (the final) | 20×20 leg | clean, worst streak 134 |
| | 40×40 scout, leg | clean, 110; clean, 478 |

- **Covered cost.** Training 75.0M cat-ticks (4,883 updates × 3,072
  ticks × 5 seats), probes 2.9M (97 × 3 worlds × 2,000 ticks × 5),
  the checkpoint's legs and two scouts 6.6M, the final's legs 6.0M and
  their scout 0.3M (the scout is not in the declaration's table), call
  5's leg 2.9M: about 93.7M. The declared line is about 69–91M
  expected plus 3.0M for call 5, about 117M at the cap.

## R-1: welfare (paired per world; `reads/r1.md`)

Pairs are the worlds whole in both legs. Edges: 0.326 at 20×20, 0.325
at 40×40.

| leg | team happiness | vs trunk s1 (mean, worlds up) | worlds with a 300+ streak | worst streak |
|---|---|---|---|---|
| truth 12M, 20×20 | 89.848 | +2.534, 30/30 | 0 | 9 |
| truth final, 20×20 | 89.885 | +2.572, 30/30 | 0 | 134 |
| needs final (12.0M), 20×20 | 89.778 | +2.465, 30/30 | 0 | 201 |
| dual-head final (12.0M), 20×20 | 90.021 | +2.708, 30/30 | 0 | 89 |
| no-head 12M, 20×20 | 89.322 | +2.323, 29/29 | 1 | 1000 (aborted) |
| no-head final, 20×20 | 90.013 | +2.700, 30/30 | 0 | 113 |
| truth 12M, 40×40 | 88.437 | +2.295, 30/30 | 0 | 95 |
| truth final, 40×40 | 88.735 | +2.594, 30/30 | 1 | 478 |
| needs final (12.0M), 40×40 | 88.566 | +2.424, 30/30 | 3 | 908 |
| dual-head final (12.0M), 40×40 | 89.033 | +2.892, 30/30 | 0 | 288 |
| no-head 12M, 40×40 | 88.534 | +2.392, 30/30 | 0 | 187 |
| no-head final, 40×40 | 89.007 | +2.866, 30/30 | 0 | 294 |

The no-head 12M row at 20×20 averages 30 worlds, one of them cut at
tick 1,299; its paired column holds the 29 whole worlds.

**Equal length: the arm's 12M checkpoint minus each 12.0M comparator**
(mean, worlds up):

| size | − needs final | − dual-head final | − no-head 12M checkpoint |
|---|---|---|---|
| 20×20 | +0.069, 22/30 | −0.174, 1/30 | +0.212, 27/29 |
| 40×40 | −0.129, 7/30 | −0.597, 0/30 | −0.097, 3/30 |

**The arm's final.** It stopped at 15,000,576 ticks, the no-head
final's own length, so the read the declaration labels unequal is an
equal-length one against no-head.

| size | − no-head final | − its own 12M checkpoint |
|---|---|---|
| 20×20 | −0.128, 1/30 | +0.038, 19/30 |
| 40×40 | −0.272, 0/30 | +0.299, 30/30 |

## The block read (`reads/blocks/score.md`)

The share of the 12M checkpoint's decision rows whose act changes when
the truth cells are zeroed. Grave rows: some friend is grave by the
engine's state.

| size | all rows | grave rows | other rows | grave rows in the leg |
|---|---|---|---|---|
| 20×20 | 0.0383 | not scored (under the reader's 200-row minimum) | 0.0383 | 84, of which 19 change |
| 40×40 | 0.0422 | 0.1045 | 0.0420 | 7,514 |

The time-since-live cell alone changes no act at either size.

## The tail read (`reads/tail.md`)

The 12M checkpoint's 40×40 leg and 100×100 scout, the needs scout's
same worlds beside it. A cat is lost when its cuddle need is at least
90, it is unpartnered and no friend is in sight.

| arm / size | worlds | streaks of 300+ | lost cat-ticks | unpartnered friends' moves while a cat is lost | share closing on it |
|---|---|---|---|---|---|
| truth 12M, 40×40 | 30 | 0 | 1,529 | 1,889 | 0.557 |
| truth 12M, 100×100 | 3 | 7 | 8,772 | 13,005 | 0.532 |
| needs, 40×40 | 30 | 3 | 7,256 | 9,488 | 0.610 |
| needs, 100×100 | 3 | 8 | 8,405 | 10,883 | 0.575 |

At 100×100 one of the truth scout's three worlds was cut by the abort
(18,498 ticks) and two of the needs scout's (7,423 and 17,421), so the
100×100 rows cover unequal ticks.

## Predictions scored (DECLARATION §7)

- **T1 MET.** Line: truth − needs at equal length inside the edge at
  both sizes. Read: +0.069 and −0.129.
- **T2 MET.** Line: truth − no-head at equal length inside the edge at
  40×40. Read: −0.097.
- **T3: first half met; second half met at 40×40, not scored at
  20×20.** Line: the truth cells drive at least 0.025 of acts at both
  sizes, and more on grave rows than on others. Read: 0.0383 and
  0.0422; at 40×40 0.1045 on grave rows against 0.0420. At 20×20 the
  leg holds 84 grave rows, under the reader's 200-row minimum (a
  convention of the block reader, not a line of the declaration); 19
  of the 84 change.
- **T4 MET.** Line: unpartnered friends' moves close on a lost cat on
  under 0.70 of them, at a size with 500+ such moves. Read: 0.557 and
  0.532.
- **The unscored expectation did not hold at 40×40.** Expected: no
  change in the count of 300+ streaks against the needs scout on the
  same worlds. Read: no world against three at 40×40.

## Decision rules, applied (DECLARATION §8)

Truth − needs at equal length is inside the edge at both sizes. The
declaration's line for that case, verbatim: "**LEVEL** (inside the edge
at both sizes): true needs buy nothing measurable as an input in this
world at this budget. The limit is not the head's quality. Put to her:
close the needs-head line for Gen 2's world (Phase 1f, the held
dual-head seeds), spend on the tail."

## What this says, and what it does not

- Given each friend's true needs, the arm reads level with the arm
  given a head's estimates, and level with the no-head arm at 40×40,
  at equal training length.
- The cells are read: zeroing them changes about 4% of acts.
- Friends told a lost cat's true needs close on it on 0.557 and 0.532
  of their moves.
- The dual-head seed reads above the truth arm at equal length, by
  more than the edge at 40×40 (−0.597, 0 of 30 worlds).
- Against the no-head final at the same length the arm's final reads
  −0.128 and −0.272, inside the edge at both sizes, with 1 and 0 of 30
  worlds up.
- The 12M checkpoint's 40×40 leg has no world with a 300+ streak where
  the needs scout has three; the no-head 12M checkpoint's 40×40 leg
  also has none.
- It does not say that seeds 2 and 4 would read the same, that a head
  could reach this ceiling, or anything about welfare at 100×100, where
  three worlds were read for the tail only.

## The stopped comparator leg

`r6-nohead-s1-u3906` at 20×20, world 905029: seat 3's distress streak
reached 1,000 ticks at tick 1,299, its need drink, with no drink tick
in the world for that seat; seat 0 held a 909-tick drink streak. The
leg was that seating's only one in this arc. The stop is owner-routed.
The same network's final has no 300+ streak on its 20×20 leg (worst
113).

## Guards and reds

- Instruments g14a–g14e and g10: eight reds as predicted (entry 37,
  commit defb9b0e).
- Readers w1–w8 (`test_truth_reads.py`): eight reds as predicted
  (commits e934f88e, eab751f5).
- Found by w8 before any read: `diag_lost.py` scored a move that left
  the walk equal by float noise. Fixed; the needs arc's recorded
  lost-cat read moved in two cells by 0.001.

## Limitations

- One seed, one checkpoint an arm. A result inside the edge
  establishes nothing until replicated; an effect smaller than about
  0.33 is invisible here.
- The truth is given for friends out of sight and hearing: LEVEL says
  no head of this kind can do better as an input under this graft at
  this budget; it does not price a different use of the information.
- Uniform five-copy seatings are stress reads. The paired contrast
  holds; the level does not transfer to a mixed roster.
- Battery worlds hold few grave events at 20×20 (84 rows of 3,000,000).

## Regeneration

### Collect (her word per step; never run by the gate)

```
/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/run_arm.sh p2-truth-s1
/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-true-needs-arm-2026-11-14/run_legs_truth.sh p2u-truth-s1-u3906
/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-true-needs-arm-2026-11-14/run_legs_truth.sh p2u-truth-s1-u3906 scout100
/Users/elizabethkelly/ai/cloudkitty/experiments/gen2-trunk-continuation-2026-11-10/run_legs_cont.sh r6-nohead-s1-u3906 --only 20
/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-true-needs-arm-2026-11-14/run_legs_truth.sh p2u-truth-s1
```

### Read (fresh outputs to the gate's scratchpad `$OUT`, never over `reads/`; env inline; runtime declared)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-true-needs-arm-2026-11-14
# seconds
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_r1_truth.py --out $OUT/r1.json --md
# about 4 minutes each, six workers
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_blocks_truth.py leg 20 --out $OUT/blocks/p2u-truth-s1-u3906-20.json
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_blocks_truth.py leg 40 --out $OUT/blocks/p2u-truth-s1-u3906-40.json
# seconds
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_blocks_truth.py score --dir $OUT/blocks --out $OUT/blocks/score.json --md
# about 2 minutes, six workers
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_tail_truth.py --out $OUT/tail.json --md
# seconds: the training record (probes, end line, the two files' sha256) and the legs' verdicts
grep "probe u" ../minifriend-phase2-2026-11-06/artifacts/p2-truth-s1.log > $OUT/probes.txt; grep "^PLATEAU:" ../minifriend-phase2-2026-11-06/artifacts/p2-truth-s1.log > $OUT/end.txt; shasum -a 256 ../minifriend-phase2-2026-11-06/artifacts/p2-truth-s1/policy-final.pt ../minifriend-phase2-2026-11-06/artifacts/p2-truth-s1/ckpt-u3906.pt > $OUT/sha.txt
grep -h "verdict" results-raw/legs/p2u-truth-s1-u3906/run.log results-raw/legs/p2u-truth-s1/run.log > $OUT/verdicts.txt; grep "verdict" ../gen2-trunk-continuation-2026-11-10/results-raw/legs/r6-nohead-s1-u3906/run.log | tail -1 >> $OUT/verdicts.txt
# seconds: the 100×100 scout's three rows and the stopped world's row
python3 -c "import json,sys; [print(r['seed'], r['ticks'], r['max_distress_age'], r.get('aborted_streak')) for r in map(json.loads, open(sys.argv[1]).read().splitlines()[1:])]" results-raw/legs/p2u-truth-s1-u3906/scouts/size100/p2u-truth-s1-u3906-g2cmp-3x20000.jsonl > $OUT/scout100.txt
python3 -c "import json,sys; R=[r for r in map(json.loads, open(sys.argv[1]).read().splitlines()[1:])]; r=[x for x in R if x['seed']==905029][0]; print(r['aborted_streak'], r['streak_shape'], r['needs']['drink_ticks'], sorted(x['max_distress_age'] for x in R))" ../gen2-trunk-continuation-2026-11-10/results-raw/legs/r6-nohead-s1-u3906/legs/size20/r6-nohead-s1-u3906-g2cmp-30x20000.jsonl > $OUT/stopped.txt
```

Accuracy gate stamp: **PASS**, 2026-11-15 (one round, a fresh
subagent, the Read fence only; fresh outputs identical to the recorded
reads). Claims: about 135 arithmetic, 12 threshold, 27 characterisation
(26 supported, 1 WEAK and reported), 0 undecidable, 24 provenance. The
WEAK sentence, left as gated: "The nine cells on each friend's row hold
her true five hidden needs, happiness, bath and grave flag" in What ran
names eight values for nine cells; the ninth is ticks-since-live, the
cat's own and unchanged from the needs arm (DECLARATION §3). Gate
notes: the cap figure of about 117M is the declaration's total without
call 5's 3.0M; the block-read legs ran in about 2 minutes each, not 4;
the tail replay counts a 984-tick streak on the needs scout's 40×40
world 905012 where the harness row reads 908 (two instruments, the
streak counts agree; not a claim of this document). Raw-dir hash
(`scripts/rawdir-hash.sh
experiments/minifriend-true-needs-arm-2026-11-14/results-raw`):
v1:73ea859f9a835ed2.
