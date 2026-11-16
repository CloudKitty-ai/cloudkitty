# Gen 2 re-anchor arm, seeds 2 and 4: RESULTS (the scout's replication)

Declared as an extension of `DECLARATION.md` (§3–§9 frozen at
f652ec8d) in `experiments/gen2-deviations.md` entry 41, on her "As
recommended" of 2026-11-16 (entry 40, ruling 3). The scout, seed 1, is
`RESULTS.md` (gated) and is the read prior here, not pooled. Every
consequence is hers.

## What ran

- **The arms.** `reanchor-s2` and `reanchor-s4`: trunk seed k's own
  run resumed from its checkpoint at update 2,605 as `cont-s<k>` was,
  the KL anchor moved to trunk seed k's final policy. Run indices 126
  and 127. Launched side by side 2026-11-16T06:38Z at HEAD 2499a8a5.
- **Their end.** Both at update 3,255 inclusive, 10,002,432 lineage
  ticks, no harm stop. Finals' sha256 begin c830d891b0decbbc (seed 2)
  and 1f7c739f73099fe2 (seed 4). Thirteen probes a seed: twelve with
  a distress streak of 0 and one of 171 (seed 2) or 110 (seed 4).
- **The legs** (30 worlds × 20,000 ticks, g2cmp 905001–905030, the
  1,000-tick abort armed, a 3-world scout before each 40×40 leg), run
  2026-11-16T07:36–07:39Z at HEAD 9b3a8f20: each arm at 20×20 and
  40×40, and the no-head arm's 2M checkpoint on the same trunk seed
  (`r6-nohead-s<k>-u651`) at 40×40.
- **One leg stopped.** `reanchor-s4` at 40×40: its scout was clean
  (worst streak 728); in the leg, world 905004 aborted at tick 3,913
  and world 905010 at tick 1,128. The other 28 worlds ran whole. It
  was that seating's last leg. Every other leg and scout ran clean.
- **Covered cost.** Training, 2 × 1,999,872 ticks × 5 seats, 20.0M
  cat-ticks. Probes, 0.39M a seed by the scout's own figure
  (`RESULTS.md`), 0.78M. Legs and scouts, 9.6M a seed less the two
  aborted worlds' unrun ticks (0.17M), 19.0M. About 39.8M against
  the 40M declared. The guards' one-update runs (3,072 ticks a run)
  are outside that line.

## R-A: the step (training bins; `reads/seeds.md`)

| seed | run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |
|---|---|---|---|---|---|---|
| 2 | re-anchored | 0.8911 | 0.2479 | 0.8941 | 0.2972 | +0.0122 |
| 2 | continued | 0.8758 | 0.5037 | 0.8773 | 0.5212 | −0.0031 |
| 2 | no-head | 0.8901 | 0.2106 | 0.8930 | 0.3006 | +0.0112 |
| 4 | re-anchored | 0.8966 | 0.2465 | 0.9013 | 0.3135 | +0.0162 |
| 4 | continued | 0.8826 | 0.5491 | 0.8796 | 0.5265 | +0.0023 |
| 4 | no-head | 0.8957 | 0.2024 | 0.8990 | 0.3152 | +0.0153 |

Trunk seed 2's last bin reads 0.8789; trunk seed 4's, 0.8803.

## R-B: welfare (paired by world against trunk seed k; `reads/seeds.md`)

| leg | team happiness | against trunk seed k | worlds up, of worlds in the mean |
|---|---|---|---|
| seed 2, re-anchored, 20×20 | 89.338 | +1.997 | 29 of 29 |
| seed 2, re-anchored, 40×40 | 88.346 | +2.334 | 30 of 30 |
| seed 2, no-head 2M, 40×40 | 88.112 | +2.100 | 30 of 30 |
| seed 4, re-anchored, 20×20 | 89.974 | +2.227 | 30 of 30 |
| seed 4, re-anchored, 40×40 | 88.418 | +2.093 | 28 of 28 |
| seed 4, no-head 2M, 40×40 | 89.018 | +2.519 | 30 of 30 |

Seed 2 at 20×20 holds 29 pairs: trunk seed 2's own leg lost world
905008 to the abort and that world is unpaired. Seed 4 at 40×40
holds 28 worlds in the mean: the arm's two aborted worlds count as
not above the trunk and are left out of the mean (entry 41).

Beside these, unscored: against the continued final at 20×20 (20M
lineage ticks, twice the arm's), the arm reads +2.098 on seed 2 and
+1.964 on seed 4, 30 of 30 worlds each. Against the no-head 2M
checkpoint at 40×40 the arm reads +0.234 on seed 2 (29 of 30 worlds
up) and −0.426 on seed 4 (0 of 28).

## The tail (`reads/tails-seeds.json`; scores nothing)

| leg at 40×40 | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|
| seed 2, trunk | 0 | 120 | none |
| seed 2, no-head 2M | 0 | 281 | none |
| seed 2, no-head final | 0 | 141 | none |
| seed 2, re-anchored | 1 | 398 | none |
| seed 4, trunk | 3 | 687 | none |
| seed 4, no-head 2M | 9 | 719 | none |
| seed 4, no-head final | 0 | 158 | none |
| seed 4, re-anchored | 24 | 1,000 | 905004 at tick 3,913; 905010 at tick 1,128 |

On seed 4's re-anchored leg every world's worst streak is at least
110 ticks; the median world's is 410. On seed 2's, 19 of the 30
worlds have no streak at all. Both of seed 4's aborts are one cat's
cuddle streak (seat 3 in 905004, seat 4 in 905010), with no tending
tick in the streak. At 20×20 the re-anchored legs read a worst streak
of 0 (seed 2) and 503 (seed 4, one world at 300+).

## R-C: distance from the clone (dump-only, scores nothing; `reads/rc-s2.md`, `reads/rc-s4.md`)

On the recorded observations of the no-head arm's seed k 20×20 leg
(150,000 rows a seed):

| seed | policy | KL to the BC clone | KL to trunk seed k's final | top act differs from the clone's |
|---|---|---|---|---|
| 2 | trunk final | 0.4820 | 0.0000 | 0.136 |
| 2 | no-head final | 1.1204 | 0.4647 | 0.257 |
| 2 | continued final | 0.3690 | 0.3377 | 0.112 |
| 2 | re-anchored final | 0.9998 | 0.3487 | 0.231 |
| 4 | trunk final | 0.4864 | 0.0000 | 0.116 |
| 4 | no-head final | 1.1251 | 0.3981 | 0.243 |
| 4 | continued final | 0.4409 | 0.2818 | 0.117 |
| 4 | re-anchored final | 1.0791 | 0.3673 | 0.237 |

## R-D: search when foodless (replays of 40×40 legs, scores nothing; `reads/rd-s2.md`, `reads/rd-s4.md`)

With no chow in sight or memory:

| leg | eat need ≥ 50: cat-ticks | a move legal | a move proposed when legal | eat need ≥ 90: cat-ticks | a move legal | proposed when legal | longest foodless run (worst / median world) |
|---|---|---|---|---|---|---|---|
| seed 2, re-anchored | 4,023 | 0.926 | 0.934 | 781 | 0.962 | 0.956 | 570 / 146 |
| seed 2, no-head final | 1,592 | 0.925 | 0.921 | 33 | 1.000 | 1.000 | 183 / 136 |
| seed 4, re-anchored | 9,985 | 0.857 | 0.791 | 2,755 | 0.954 | 0.855 | 459 / 220 |
| seed 4, no-head final | 5,166 | 0.846 | 0.860 | 365 | 0.682 | 0.566 | 279 / 155 |

The continued finals of seeds 2 and 4 ran no 40×40 leg and are not in
this read. Seed 4's re-anchored leg includes its two aborted worlds
up to their abort ticks. `diag_abort.py` was changed for this read:
its shared-streak window is skipped when the 300+ streaks of a world
never overlap, which it first met on seed 4's leg.

## Predictions scored (entry 41; DECLARATION §7 per seed)

- **Seed 2.** A1 MET (step +0.0122, at least 0.005; KL at bin 1
  0.2479, inside 0.10–0.30). A2 MET (30 worlds above the trunk, at
  least 25; mean +2.334, beyond 0.325). A3 MET (+2.334 is at least
  half of the no-head 2M checkpoint's +2.100).
- **Seed 4.** A1 MET (step +0.0162; KL 0.2465). A2 MET (28 worlds
  above the trunk; mean +2.093 over the 28 whole worlds). A3 MET
  (+2.093 is at least half of +2.519).
- **The session's registered prediction** (both seeds REPLICATE, A3
  met on both): held.
- **Unscored expectation** (no harm stop in training; no world at the
  1,000-tick line on the legs): held in training on both seeds and on
  seed 2's legs; **did not hold on seed 4**, where two worlds of the
  40×40 leg reached the line.

## Decision rules, applied (entry 41)

Seed 2: A1 and A2 met, the run ended as declared, its 40×40 leg ran:
**REPLICATES**. Seed 4: A1 and A2 met, the run ended as declared, its
40×40 leg ran with two worlds aborted, which entry 41 counts as not
above the trunk: **REPLICATES**. Across seeds: **both replicate
(three of three)**. Entry 41 puts to her, on this cell: re-anchoring
at a plateau as a recipe candidate with R-C per seed beside it, and
the second-restart scout under its own declaration. The stopped leg
on seed 4 is owner-routed. No recipe text changes without her word.

## What this says, and what it does not

- **The mean gain replicates.** Moving the anchor alone lifts all
  three trunk seeds by about two points of team happiness at both
  sizes within two million ticks (seed 1: +1.841 at 40×40), and
  carries the no-head restart's gain at equal ticks or most of it.
- **The tail does not replicate.** On seed 4 the gain arrived with
  24 of 30 worlds holding a streak of 300 or more and two worlds at
  the abort line, far beyond trunk seed 4 (3 worlds) and beyond the
  no-head restart at the same ticks (9). Seed 2 has one such world,
  seed 1 had none. Entry 41's grammar has a cell for a training stop
  and for a scout abort and none for a finished leg that aborted, so
  the declared word is REPLICATES; the tail is reported beside it and
  is not folded into the word.
- **Not shown:** whether seed 4's tail fades with further training.
  On the same trunk seed the no-head arm holds 9 such worlds at 2M
  ticks and none at its 15M final, but that arm also reset its
  entropy schedule and optimiser, which this one does not.
- **Distance from the clone roughly doubles in one move.** KL to the
  BC clone goes from 0.48 and 0.49 (trunk finals) to 1.00 and 1.08
  after two million re-anchored ticks, near the no-head finals' 1.12
  and 1.13 at fifteen million.
- **Not shown:** where a re-anchored policy would plateau, what a
  second re-anchor does, or anything about seating.

## Guards and reds

Six driver guards (a1–a6) re-run per seed with six mutants and four
reader guards (u4–u7), every red as predicted, are in entry 41. The
scout's own read reproduces `reads/reanchor.json` value for value
after the reader's extension, and `read_rc.py` reproduces
`reads/rc.md` byte for byte after it took a seed.

## Limitations

- Two bins read the step and the tail two million ticks after the
  move, not where either settles.
- The continuation's 10M rung was not run on these seeds: A2's
  second clause is scored on seed 1 only.
- Seed 1 was read before these were declared; it is a prior.
- The arms' episode seeds differ from `cont-s<k>`'s (fresh stripes).
- Uniform five-copy seatings are stress reads (F-017, F-044, F-060).
- R-D reads the food lock of the declaration's §2.4; seed 4's aborts
  are cuddle streaks, which it does not read.

## Regeneration

### Collect (her word per step; never run by the gate)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv caffeinate -s nohup /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B train_ppo_reanchor.py --seed 2 > artifacts/reanchor-s2.log 2>&1 &
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv caffeinate -s nohup /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B train_ppo_reanchor.py --seed 4 > artifacts/reanchor-s4.log 2>&1 &
REANCHOR_SEED=2 /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14/run_legs_reanchor.sh
REANCHOR_SEED=4 /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14/run_legs_reanchor.sh
/Users/elizabethkelly/ai/cloudkitty/experiments/gen2-trunk-continuation-2026-11-10/run_legs_cont.sh r6-nohead-s2-u651 --only 40
/Users/elizabethkelly/ai/cloudkitty/experiments/gen2-trunk-continuation-2026-11-10/run_legs_cont.sh r6-nohead-s4-u651 --only 40
```

### Read (fresh outputs to the gate's scratchpad `$OUT`, never over `reads/`; env inline; runtime declared)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14
# seconds
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_reanchor.py --seeds --out $OUT/seeds.json --md
# seconds
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_tails_seeds.py --out $OUT/tails-seeds.json
# about 1 minute each
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rc.py --seed 2 --out $OUT/rc-s2.json --md
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rc.py --seed 4 --out $OUT/rc-s4.json --md
# about 4 minutes each, three workers at about 7 GB each
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rd.py --seed 2 --out $OUT/rd-s2.json --md
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rd.py --seed 4 --out $OUT/rd-s4.json --md
# seconds: the training record (probes, end lines, finals' sha256, manifests) and the legs' run-log lines
grep "probe u" artifacts/reanchor-s2.log > $OUT/probes-s2.txt; grep "probe u" artifacts/reanchor-s4.log > $OUT/probes-s4.txt; grep -h "^END:" artifacts/reanchor-s2.log artifacts/reanchor-s4.log > $OUT/end.txt; shasum -a 256 artifacts/reanchor-s2/policy-final.pt artifacts/reanchor-s4/policy-final.pt > $OUT/final-sha.txt; cat artifacts/reanchor-s2/reanchor-manifest.json artifacts/reanchor-s4/reanchor-manifest.json > $OUT/manifests.txt
grep -H "^== " results-raw-seeds/legs/reanchor-s2/run.log results-raw-seeds/legs/reanchor-s4/run.log ../gen2-trunk-continuation-2026-11-10/results-raw/legs/r6-nohead-s2-u651/run.log ../gen2-trunk-continuation-2026-11-10/results-raw/legs/r6-nohead-s4-u651/run.log > $OUT/runlog.txt
```

Accuracy gate stamp: **PASS**, 2026-11-16 (one round, a fresh
subagent). Claims: about 185 arithmetic, 12 threshold, 16
characterisation (all supported), 1 undecidable ("`read_rc.py`
reproduces `reads/rc.md` byte for byte after it took a seed": the
seed-1 read is outside this Read block), about 30 provenance. Gate
notes: the scout's `RESULTS.md` prints the probes as "about 0.4M";
0.39M is its own recipe worked out (13 probes × 3 worlds × 2,000
ticks × 5 seats). Two step cells sit one unit off what the printed
bins subtract to (seed 4: +0.0162 and +0.0153 are the reader's raw
values). Raw-dir hash (`scripts/rawdir-hash.sh
experiments/gen2-reanchor-scout-2026-11-14/results-raw-seeds`): v1:dbc32b1cbdd036a6.
The two no-head 2M legs this document reads sit under the
continuation's `results-raw`, which carries no stamp yet.
