# Gen 2 re-anchor scout: RESULTS (one arm, one seed)

Declared in `DECLARATION.md` (§3–§9 frozen at f652ec8d); the record is
`experiments/gen2-deviations.md` entry 38. One seed clears nothing; the
consequences in §8 of the declaration are hers.

## What ran

- **The arm.** `reanchor-s1`: trunk seed 1's own run resumed from its
  checkpoint at update 2,605 exactly as `cont-s1` was, with one change:
  the KL anchor is trunk seed 1's final policy, not the BC clone. Run
  index 125. Launched 2026-11-15T07:46:31Z at HEAD 71482fb0 on her word
  "1) now"; seed 1 on her word "4) keep".
- **Its end.** Update 3,255 inclusive, 10,002,432 lineage ticks, no
  harm stop. `policy-final.pt` sha256 begins c765f216f23891e5. Thirteen
  probes, one every 50 updates: the worst distress streak is 13 ticks,
  the other twelve read 0.
- **The legs** (30 worlds × 20,000 ticks, g2cmp 905001–905030, the
  1,000-tick abort armed, a 3-world scout before each 40×40 leg):
  `reanchor-s1` at 20×20 and 40×40; the no-head arm's 2M checkpoint
  `r6-nohead-s1-u651` at 40×40. All clean, no abort.
- **Covered cost.** About 10.0M cat-ticks of training (651 updates ×
  3,072 ticks × 5 seats), about 0.4M in the thirteen probes (3 worlds ×
  2,000 ticks × 5 seats each), 6.3M in the arm's legs and scout, 3.3M
  in the no-head checkpoint's leg and scout: about 20.0M, the declared
  line.

## R-A: the step (training bins; `reads/reanchor.md`)

Trunk seed 1's last bin: return 0.8802.

| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |
|---|---|---|---|---|---|
| `reanchor-s1` (anchor = trunk final) | 0.8931 | 0.2366 | 0.8956 | 0.2809 | +0.0129 |
| `cont-s1` (same resume, anchor = BC clone) | 0.8814 | 0.5365 | 0.8820 | 0.5461 | +0.0011 |
| no-head arm (full restart) | 0.8914 | 0.2062 | 0.8940 | 0.2979 | +0.0112 |

## R-B: welfare (paired by world against trunk seed 1; `reads/reanchor.md`)

| leg | team happiness | vs trunk s1 (mean, worlds up) | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|---|---|
| `reanchor-s1`, 20×20 | 89.043 | +1.729, 30/30 | 0 | 106 | none |
| `reanchor-s1`, 40×40 | 87.983 | +1.841, 30/30 | 0 | 150 | none |
| `cont-s1` 10M rung, 40×40 | 86.281 | +0.139, 27/30 | 0 | 86 | none |
| no-head 2M checkpoint, 40×40 | 87.819 | +1.678, 30/30 | 8 | 897 | none |

At 40×40 the arm reads +1.702 over `cont-s1`'s 10M rung (30 of 30
worlds up) and +0.163 over the no-head 2M checkpoint (30 of 30 worlds
up). The seed-to-seed edge at 40×40 is 0.325.

## R-C: distance from the clone (dump-only, scores nothing; `reads/rc.md`)

150,000 recorded rows: every 20th tick of the no-head arm's seed 1
20×20 leg, 30 worlds.

| policy | KL to the BC clone | KL to trunk s1's final | top act differs from the clone's |
|---|---|---|---|
| trunk s1 final | 0.4668 | 0.0000 | 0.115 |
| no-head final | 1.1121 | 0.4546 | 0.231 |
| continued final | 0.3812 | 0.2804 | 0.104 |
| re-anchored final | 0.9002 | 0.2710 | 0.204 |

## R-D: search when foodless (replays, scores nothing; `reads/rd.md`)

40×40 legs. Foodless = no chow in sight or in element memory.

| leg | worlds | foodless, eat ≥ 50: cat-ticks | move legal | move proposed when legal | foodless, eat ≥ 90: cat-ticks | move legal | proposed when legal | longest foodless run (max / median world) |
|---|---|---|---|---|---|---|---|---|
| `reanchor-s1` | 30 | 4880 | 0.881 | 0.916 | 294 | 0.779 | 0.869 | 246 / 152 |
| `p2u-nohead-s1` | 30 | 3753 | 0.813 | 0.756 | 65 | 0.738 | 0.583 | 268 / 155 |
| `cont-s1` | 30 | 13878 | 0.661 | 0.711 | 4806 | 0.350 | 0.218 | 1214 / 156 |

`cont-s1`'s world 905007 was cut short by the armed abort at 13,594
ticks.

## Predictions scored (DECLARATION §7)

- **A1 MET.** Line: the first bin at least 0.005 above the trunk's
  last bin, and KL to the anchor at bin 1 between 0.10 and 0.30. Read:
  step +0.0129, KL 0.2366.
- **A2 MET.** Line: at 40×40 above the trunk in at least 25 of 30
  worlds with the mean beyond the 0.325 edge, and above `cont-s1`'s 10M
  rung by more than the edge. Read: 30 of 30, +1.841; +1.702 over the
  rung.
- **A3 MET.** Line: at 40×40 at least half of what the no-head arm's
  2M checkpoint holds over the trunk. Read: +1.841 against +1.678.
- Unscored expectation held: no harm stop in training, no world at the
  1,000-tick line on the legs.

## Decision rules, applied (DECLARATION §8)

A1 and A2 are met. The declaration's line for that case, verbatim:
"**A1 and A2 met**: the anchor alone is sufficient on this seed. Put
to her: seeds 2 and 4 of this arm, then the second-restart scout; the
entropy and optimiser arms are not needed for the recipe."

## What this says, and what it does not

- Moving the anchor, with nothing else reset, produced a step of
  +0.0129 in return where the same resume under the clone anchor
  produced +0.0011, and a 40×40 welfare gain of +1.841 where that
  resume's 10M rung reads +0.139.
- At equal further ticks the arm is not below the full restart: +0.163
  over the no-head 2M checkpoint at 40×40, which is inside the 0.325
  edge.
- The arm's 40×40 leg has no world with a 300+ streak; the no-head 2M
  checkpoint's has 8.
- The cost side: in 2M ticks the arm's KL to the BC clone went from the
  trunk's 0.4668 to 0.9002. The arm is no longer anchored to the clone,
  so what the clone anchor was for (§2.5 of the declaration) is not
  enforced on it; R-C measures the distance and clears nothing.
- It does not say the gain continues past two bins, that seeds 2 and 4
  behave the same, or what a second re-anchor does.

## Guards and reds

- Driver guards a1–a6 (`test_reanchor.py`) and the rung seating's g10
  line: seven reds as predicted (commit a01003ca).
- Reader guards u1–u3 (`test_read_reanchor.py`): four reds as predicted
  (commits 46978841, e1b30648).
- `read_rc.py` and `read_rd.py` are diagnostics without guards of their
  own; each calls the function it reports (`train_ppo_g2.head_quantities`,
  `diag_abort.world`) and copies neither.

## Limitations

- One seed, two bins, one arm. A result on one seed establishes nothing
  about the recipe.
- The legs are uniform five-copy seatings: stress reads. The paired
  contrast holds; the level does not transfer to a mixed roster.
- R-C's rows are the no-head arm's recorded observations at 20×20, one
  distribution of states.

## Regeneration

### Collect (her word per step; never run by the gate)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv caffeinate -s nohup /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B train_ppo_reanchor.py > artifacts/reanchor-s1.log 2>&1 &
/Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14/run_legs_reanchor.sh
/Users/elizabethkelly/ai/cloudkitty/experiments/gen2-trunk-continuation-2026-11-10/run_legs_cont.sh r6-nohead-s1-u651 --only 40
```

### Read (fresh outputs to the gate's scratchpad `$OUT`, never over `reads/`; env inline; runtime declared)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-reanchor-scout-2026-11-14
# seconds
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_reanchor.py --out $OUT/reanchor.json --md
# about 3 minutes
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rc.py --out $OUT/rc.json --md
# about 6 minutes, three workers at about 7 GB each
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rd.py --out $OUT/rd.json --md
# seconds: the training record (probes, end line, final's sha256)
grep "probe u" artifacts/reanchor-s1.log > $OUT/probes.txt; grep "^END:" artifacts/reanchor-s1.log > $OUT/end.txt; shasum -a 256 artifacts/reanchor-s1/policy-final.pt > $OUT/final-sha.txt
```

Accuracy gate stamp: **PASS**, 2026-11-15 (round 2 of 2, fresh
subagents; round 1 FAILED on the covered-cost total, which left out the
probes). Claims: about 122 arithmetic, 6 threshold, 14 characterisation
(12 supported, 2 WEAK and reported), 1 undecidable (the scouts' clean
verdicts are not re-run by the Read block), 17 provenance. The two WEAK
sentences, left as gated: "with one change" in What ran and "with
nothing else reset" in What this says both leave out that the arm's
episode seeds also differ from `cont-s1`'s (a fresh stripe; DECLARATION
§3 and §10). Gate notes: R-D's `p2u-nohead-s1` and `cont-s1` rows are
those arms' finals, where R-B's `cont-s1` row is its 10M rung;
`read_rc.py` builds the trunk-final anchor's masked log-probabilities
inline. Raw-dir hash (`scripts/rawdir-hash.sh
experiments/gen2-reanchor-scout-2026-11-14/results-raw`): v1:1dee3d0f5cdd5fa9.
