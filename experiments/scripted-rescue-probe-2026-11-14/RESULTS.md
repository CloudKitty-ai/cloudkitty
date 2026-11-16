# The scripted-rescue probe: RESULTS (one policy seed, one hand-written rule; the primary pair unscored)

Declared in `DECLARATION.md` (§3–§9 frozen at be911e33); the record is
`experiments/gen2-deviations.md` entries 39 and 40. No training: a
hand-written rule laid over the no-head arm's seed-1 final at
evaluation. Every consequence in §8 of the declaration is hers.

## What ran

- **The overlays.** T (a free cat walks to a lost friend and takes a
  partner act, on the engine's facts), P (the same triggers, an equal
  walk away) and O (the rescue on the cat's own observation), each
  over `p2:p2-nohead-s1r` in all five seats.
- **The legs** (30 worlds × 20,000 ticks, g2cmp 905001–905030, the
  1,000-tick abort armed, a 3-world scout before each), run
  2026-11-15T08:09–08:16Z: T at 100×100, T at 40×40 and P at 40×40 at
  HEAD c876745e, O at 100×100 at 85ad65ca (between the two commits
  only the reader and its guards were added). All four ran whole, no
  abort.
- **The placebo leg at 100×100 did not run.** Its scout aborted (world
  905003 at tick 15,186) and the leg went to her. Ruled 2026-11-16,
  "As recommended" (entry 40, ruling 5): **not run**. S1, S2 and S4
  and §8's grammar stand UNSCORED, not failed.
- **Baselines.** The recorded `p2u-nohead-s1` legs at 100×100 and
  40×40. The 100×100 baseline lost world 905009 to the abort at tick
  16,940, so every pair at 100×100 holds 29 worlds.
- **Covered cost.** Four legs, 12.0M cat-ticks; four whole scouts,
  1.2M; the P scout at 100×100, under 0.3M (two whole worlds and
  15,186 ticks of the third). About 13.5M against the 16.5M declared.
  The guards' and pilots' short runs (about 0.1M, entry 39) are
  outside that line.

## R-1: welfare (team happiness, paired by world; `reads/rescue.md`)

| pair | worlds | up | down | paired mean | 95% interval |
|---|---|---|---|---|---|
| T − base, 100×100 | 29 | 17 | 12 | −0.019 | −0.138 to +0.093 |
| O − base, 100×100 | 29 | 11 | 18 | −0.172 | −0.307 to −0.049 |
| T − P, 40×40 | 30 | 7 | 3 | +0.014 | −0.003 to +0.033 |
| T − base, 40×40 | 30 | 8 | 2 | +0.014 | +0.004 to +0.027 |
| P − base, 40×40 | 30 | 5 | 5 | +0.000 | −0.016 to +0.016 |

The primary pair, T − P at 100×100, does not exist. T − base and
O − base at 100×100 are **uncontrolled comparisons**: nothing at that
size separates walking to a friend from walking at all.

At 40×40, 20 of the 30 worlds are ties in T − P: no mission opened in
them.

## R-2: the tail (`reads/rescue.md`)

| leg | lost cat-ticks | worlds with a 300+ streak | worst streak | aborts |
|---|---|---|---|---|
| T, 100×100 | 5,377 | 5 | 557 | none |
| O, 100×100 | 7,309 | 8 | 906 | none |
| baseline, 100×100 | 18,444 | 13 | 1,000 | 905009 at tick 16,940 |
| T, 40×40 | 235 | 0 | 67 | none |
| P, 40×40 | 916 | 0 | 296 | none |
| baseline, 40×40 | 1,081 | 0 | 294 | none |

Lost = cuddle need at 90 or more, unpartnered, no friend in sight.
Over the 29 worlds whole in both legs at 100×100: T 5,140 against the
baseline's 17,226 (a 70% cut); O 6,609 (a 62% cut). At 40×40: T 235
against 1,081 (78%); P 916 against 1,081 (15%).

## R-3: the missions (`reads/rescue.md`)

| leg | missions | a world | median / mean length | ending in a partner act | rule set the act | rescuer's happiness against the baseline | rescuer's highest need against the baseline |
|---|---|---|---|---|---|---|---|
| T, 100×100 | 253 | 8.4 | 22 / 26.8 | 0.937 | 0.0022 | −7.170 | +9.311 |
| T, 40×40 | 14 | 0.5 | 22 / 22.9 | 1.000 | 0.0001 | −4.382 | +4.442 |
| P, 40×40 | 15 | 0.5 | 32 / 65.5 | 0.000 | 0.0002 | −15.407 | +24.898 |
| O, 100×100 | 1,052 | 35.1 | 24 / 26.9 | 0.285 | 0.0092 | −7.136 | +7.175 |

The rescuer columns compare the same seat over the same ticks of the
baseline world. Every one of T's 253 missions at 100×100 closed with
the target partnered. Of O's 1,052, 751 closed partnered, 298 when the
call left the window and 3 on the rescuer's own need.

## Predictions scored (DECLARATION §7)

- **S1** (T cuts lost cat-ticks by at least 30% against P at
  100×100): UNSCORED. There is no P leg at 100×100.
- **S2** (T − P positive on at least 20 worlds at 100×100, mean under
  0.5): UNSCORED.
- **S3** (at 40×40, T − P inside ±0.15 with 10–20 worlds positive):
  **NOT MET** by its letter. The mean is +0.014, inside ±0.15, but 7
  worlds are positive, not 10–20; 20 worlds are ties.
- **S4** (P − base zero or negative at both sizes): UNSCORED. At
  40×40 alone P − base is +0.000 (5 up, 5 down).
- **S5** (O − base has T − base's sign at 100×100 and at least half
  its size): met by its letter only. Both are negative (−0.172 and
  −0.019). The prediction expected O to carry half of a gain; there is
  no gain to carry.

## Decision rules, applied (DECLARATION §8)

§8 reads T − P at 100×100. That pair was not run, on her ruling:
**the grammar is UNSCORED**. It is not scored from T − base as a
stand-in.

## What this says, and what it does not

- **The rule removes most lost time.** Against the baseline, T cuts
  lost cat-ticks by 70% at 100×100 and 78% at 40×40, and at 100×100
  leaves 5 worlds with a 300+ streak where the baseline has 13 and no
  abort where the baseline has one. At 100×100 this is uncontrolled.
- **At 40×40 the direction of the walk does the work.** With the
  same triggers, walking away cuts lost cat-ticks by 15%; walking to
  the friend cuts them by 78%.
- **The cat's own observation carries most of the tail cut.** O,
  which reads no hidden fact, cuts lost cat-ticks by 62% at 100×100
  where T cuts them by 70%. It opens four times T's missions (1,052
  against 253); 751 of them close with the friend partnered and 0.285
  end in the rescuer's own partner act. It reads −0.172 on team
  happiness with an interval that excludes zero. Uncontrolled.
- **Team happiness cannot see this mechanism, in either direction.**
  The baseline's lost share at 100×100 is 17,226 of 2,900,000
  cat-ticks (0.59%). T saves 12,086 of them (0.42%), so the mean moves
  by 0.0042 times the per-tick happiness gap between a lost cat and a
  rescued one. Reaching the interval's half-width (about 0.115) would
  take a gap of about 28 points. The rescuers' side is as small: 253
  missions of mean length 26.8 ticks at 7.17 below is about 48,600
  point-ticks, under 0.02 on a 3,000,000 cat-tick mean. T − base at
  −0.019 is what every reading predicts. It is cited neither for nor
  against the rescue.
- **Not shown:** that acting on a friend's need pays at 100×100 (the
  placebo-controlled pair is missing), what a rescued cat gains, or
  anything about a trained policy. One policy seed, one hand-written
  rule.

## What the placebo cost, and what its scout shows

P's function is to walk a cat away from a friend in need. Its cost on
record: at 40×40 its 15 missions run a median 32 ticks (mean 65.5)
with the rescuer's happiness 15.4 below the baseline's over those
ticks and its highest need 24.9 above; in the build's 600-tick pilot
at 100×100 its rescuers were held away for 90–140 ticks with a worst
streak of 165 (entry 39).

The scout's abort at 100×100 (world 905003, seat 0 at the 1,000-tick
line at tick 15,186): seat 0 was never a rescuer in that world, and
it was the placebo's **target** in 8 of the world's 10 missions.
Seven of those ran back to back from tick 14,187 to the abort, each
walking a free cat away from it; six closed when the rescuer's own
need reached 90 and the seventh was open at the abort. In the
recorded baseline the same world ran whole and seat 0's worst streak
was 10 ticks. The two runs part ways at the overlay's first act, so
this is not proof that the placebo caused the abort; it is what the
placebo doing its declared job to one cat looks like, and it is the
welfare ground for not running the leg.

## Guards and reds

The overlay's six guards (s1–s6, eleven mutants; a twelfth red on
record is Phase 2's g10, re-run on the changed harness) and the
reader's five (t1–t5), every red as predicted, are in entry 39, with
two slips recorded there as they happened: the first leg start failed
before any tick on the hook's own assert (the guards had not built
the job as the command line does; fixed, all twelve reds re-run), and
the
reader's predictions were fixed only as `--expect` arguments, not
written to the entry, before their mutants ran.

## Limitations

- The primary comparison is missing by ruling; nothing here is
  scored against a placebo at the size where the tail lives.
- One policy seed (the no-head final on trunk seed 1), one rule.
- Uniform five-copy seatings are stress reads (F-017, F-044, F-060).
- The rescued cat's own gain is not read. A replay-only paired read
  of it was offered by the Professor thread's review and is not ruled
  (entry 40).
- If the rescue line goes on to training-side work, the control
  question returns with a redesigned placebo and its own declaration
  (entry 40, ruling 5).

## Regeneration

### Collect (her word per step; never run by the gate)

```
/Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh rescue-T 100
/Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh rescue-P 100
/Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh rescue-T 40
/Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh rescue-P 40
/Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh rescue-O 100
```

### Read (fresh outputs to the gate's scratchpad `$OUT`, never over `reads/`; env inline; runtime declared)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/scripted-rescue-probe-2026-11-14
# about 5 minutes
OMP_NUM_THREADS=1 VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B read_rescue.py --out $OUT/rescue.json --md
# seconds: every scout's worlds, ticks run and aborts; every leg's run-log header lines
python3 -c "import json,glob; [print(f.split('legs/',1)[1], [(r['seed'], r.get('ticks'), r.get('aborted_streak')) for r in map(json.loads, list(open(f))[1:])]) for f in sorted(glob.glob('results-raw/legs/*/scouts/size*/*.jsonl'))]" > $OUT/scouts.txt
grep -h "^== rescue" results-raw/legs/*/run.log > $OUT/runlog.txt
# seconds: the P scout's aborted world (its missions, worst streak by seat) beside the same world of the recorded baseline
python3 -c "import json; row = lambda f, s: [x for x in map(json.loads, list(open(f))[1:]) if x['seed'] == s][0]; p = row('results-raw/legs/rescue-P/scouts/size100/rescue-P-g2cmp-3x20000.jsonl', 905003); b = row('../minifriend-phase2-2026-11-06/results-raw/legs/p2u-nohead-s1/legs/size100/p2u-nohead-s1-g2cmp-30x20000.jsonl', 905003); print('P scout 905003', p['ticks'], p['aborted_streak'], p['max_distress_age_seat']); [print(' mission', {k: m[k] for k in ('rescuer', 'target', 'open', 'close', 'why')}) for m in p['overlay']['missions']]; print('baseline 905003', b['ticks'], 'aborted_streak' in b, b['max_distress_age_seat'])" > $OUT/p-scout-905003.txt
```

Accuracy gate stamp: **PASS**, 2026-11-16 (round 2 of 2, fresh
subagents; round 1 FAILED on two provenance misses: the O leg's HEAD
and the overlay guards' mutant count, both fixed here). Claims: about
151 arithmetic, 9 threshold, 16 characterisation (15 supported, 1 WEAK
and reported), 1 undecidable ("the two runs part ways at the overlay's
first act" has no tick-level read behind it), 20 provenance. The WEAK
sentence, left as gated: "Team happiness cannot see this mechanism, in
either direction" rests on arithmetic and on the per-tick gap being
implausibly large; the gap itself is not measured. Round 1 also
reported the placebo scout's target account, now in "What the placebo
cost". Raw-dir hash (`scripts/rawdir-hash.sh
experiments/scripted-rescue-probe-2026-11-14/results-raw`): v1:30f8458327ec7069.
