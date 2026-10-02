# Dead-or-held probe — results

Ran under `PREREG-C.md` (frozen d5bf7fca, 2026-09-30, on the
owner's word). Four arms at β 0.14 on the d100-1000 corner: l14
(leash 0.01) × 2, o14 (E visible in the obs clock slot, leash 0.04)
× 2, run indices 90–93. All four stopped on plateau at 8–9M ticks
(no futility, no cap). Deviations: 1 on record
(`prereg-c-deviations.md`: the beta_probe pin-plumbing crash before
any l14 training step; fix guarded, arms relaunched) + 1 erratum
(note 2 there: the frozen prereg's F-019 paraphrase). Provenance
note: the driver's batteryC step crashed at 09:30:08Z on l14-s1's
final, which landed at 09:30:45Z — 37 seconds later; the zero-row
stub is set aside as `CRASHED-EMPTY-0930Z.jsonl.aside`, and the l14
legs ran by hand with the identical invocation.

Battery: l14 on the stage-B instrument verbatim; o14 on the
declared `probe_eval_o14.py` (E fed at eval as trained). 4 × 30 ×
20,000, eval band 870001, abort line 1,000 every leg.

**WELFARE EVENT — the abort line fired**: o14-s2 seed 870011
reached a 1,000-tick distress streak and that seed's episode
stopped at tick 1,224, cutting 18,776 ticks of further exposure in
it (the mechanism's second firing in anger; the row carries
`aborted_streak`; the leg's other 29 seeds ran full). One
near-miss: l14-s1 seed 870013, max streak 952, no abort. All other
118 rows complete at 20,000 ticks — read from the rows.

## The read (reader output, verbatim)

```
| arm | play (greedy) | play (trace lastq) | ex-Biscuit lift | Biscuit lift | closed-gate | at-cap | E p50 | happiness | vs recorded | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| l14-s1 | 0.0722 | 0.0824 | +0.0479 | -0.0612 | 0.0424 | 0.132 | 0.555 | 92.544 | +0.224 | 0.1551 | 0.195 | 0.0654 | 0.0039 | 3262 | 952 |
| l14-s2 | 0.0867 | 0.0831 | +0.0893 | -0.0300 | 0.0305 | 0.132 | 0.552 | 92.761 | +0.441 | 0.1372 | 0.171 | 0.0573 | 0.0013 | 1238 | 238 |
| o14-s1 | 0.0823 | 0.0931 | -0.0106 | +0.0478 | 0.1199 | 0.103 | 0.489 | 92.072 | -0.248 | 0.1374 | 0.178 | 0.0475 | 0.0002 | 329 | 83 |
| o14-s2 | 0.0915 | 0.0920 | +0.0206 | +0.0627 | 0.1500 | 0.102 | 0.488 | 91.434 | -0.887 | 0.1234 | 0.144 | 0.0441 | 0.0032 | 2973 | 1000 |

Comparators: b14 greedy 0.0885 (per-seed 0.0869, 0.0955, 0.0829); b14 trace 0.0938; baseline play 0.0749.
```

(The ex-Biscuit / Biscuit lift columns are against the stage-B
fresh gen1-A per-seat baseline, as the seat-lift addendum's.)

## Predictions, scored (PREREG-C; the one fixed reference is 0.10)

- **P1 (if the leash binds) — FAILED as declared, and its second
  clause is the probe's finding.** Declared test: l14 pooled greedy
  play > b14's 0.0885 AND ex-Biscuit lift > 0 on both seeds. The
  totals failed (0.0722, 0.0867); the composition clause PASSED
  decisively — ex-Biscuit lift +0.0479 and +0.0893, the first
  non-Biscuit movement in the entire arc, while Biscuit's own lift
  went NEGATIVE (−0.0612, −0.0300). Releasing the leash
  redistributed play across seats without raising the total.
- **P2 (if observability binds) — FAILED.** o14 trace 0.0931/0.0920
  vs b14's 0.0938; greedy 0.0823/0.0915 straddles 0.0885;
  ex-Biscuit mixed (−0.0106, +0.0206). Making the stock visible
  moved neither the total nor the composition.
- **P3 (both flat) — NOT cleanly satisfied either**: l14-s1
  (0.0722) sits below b14's per-seed range (0.0829–0.0955) and
  o14-s1 (0.0823) marginally below. Totals are flat-to-lower, not
  flat.
- **0.10 bar: no arm reaches it** (max 0.0915).
- **Watches**: bin0 and eat+drink inside bars on all four arms
  (l14-s1 closest: 0.195 vs 0.211, 0.0654 vs 0.0699 — the
  loosened leash drifts TOWARD the tending bars, opposite the
  stage-B direction); sleep out of band on l14-s1 (0.1551 high);
  tm-dist over the 0.001 watch on three arms (l14-s1 0.0039, the
  probe's worst — stage A's d100-1000-s2 ran 0.0056; l14-s2
  0.0013; o14-s2 0.0032); at-cap 0.102–0.132 (reported before
  conclusions; off the cap).

## The composition finding (what the probe actually separated)

The leash sets WHO plays, not how much. At leash 0.01 the four
corpus-non-players finally move (+0.048/+0.089 summed lift) and
Biscuit gives play back; closed-gate start share COLLAPSES to
0.0305–0.0424 — a third to a half of the 0.0843 baseline and a
fifth of b14's family mean — so the unleashed policy starts play
almost exclusively with the gate open (96–97% of starts below
worst-need 25; the 15–25 interior still carries ~0.3 of them),
exactly the free-time shape the channel was designed to teach. But
the total stays under the bar, and under b14's mean on 3 of 4
arms. With E visible and the leash standard (o14), the declared
tests move nothing: composition mixed-sign, closed-gate share and
totals at b14-like values (not literally seed-for-seed: o14-s2's
ex-Biscuit +0.0206 tops every stage-B seed — stage-B per-seed
ex-Biscuit ran −0.0315 (b14-s3) to +0.0160 (b14-s2)). Observability
released nothing here — though the declared confound means an
E-helps / clock-removal-hurts cancellation cannot be excluded from
a null — the leash is a constraint on composition, and the
channel's magnitude cannot raise the total even with both its
suspected jailers removed one at a time.

Welfare splits by arm, and it is the probe's sharpest result. The
l14 arms post the enrichment arc's first positive paired happiness
deltas (+0.224, +0.441 vs recorded gen1-A; the bonus screen, stage
A, and stage B arms were all negative — the cross-world floor-15
reads posted positives earlier against a different comparator).
That is F-019's own direction — loosening the leash buys mean
welfare and costs personality, visible here as Biscuit's play
fingerprint eroding (−0.0612, −0.0300) — plus an observation
F-019 did not measure: the distress tail widened (l14-s1: 3,262
dist ticks, streak 952, tm-dist 0.0039, the probe's worst arm).
The o14 arms moved the other way on the mean (−0.248, −0.887) and
carried the abort. Mean and tail move separately; any Gen 3 use of
a lower leash buys the mean and the composition while owning the
tail, which the abort line polices.

## Welfare accounting

Declared: o14 ≤ ~3,200 per 30-seed leg; l14 ≤ ~8,200; abort line
hard. Measured legs: l14-s1 3,262 (inside its line), l14-s2 1,238,
o14-s1 329, o14-s2 2,973 — inside its 3,200 line by 227 ticks,
with the abort having cut seed 870011's episode at tick 1,224
(18,776 ticks of that episode unrun; whether the uncut episode
would have crossed the line is unmeasured). The abort did the job
the declaration gave it. Worst single-seed dist ticks 1,809
(o14-s2), 1,043 (l14-s1).

## Decision rules, applied

- "Any arm clearing 0.10 … the channel is HELD, not dead": did not
  occur.
- "l14 moves but o14 does not (or vice versa)": on the DECLARED
  total-play tests, neither moved, so the named-constraint branch
  does not fire as written. What the probe separated instead is
  composition: l14 moved the seat distribution decisively, o14
  moved nothing. Reported as the composition finding above; per
  the prereg, report; her fork.
- "Both flat: F-056 stands on the narrower test" — no branch's
  condition is met AS WRITTEN: P3's "flat" means inside the b14
  per-seed range, and two arms sit BELOW it. This report reads the
  nearest branch because the departure is downward — a weaker
  total is not a revived channel — so F-056's channel-dead verdict
  survives both releases at the total level, and the branch's
  stated consequence applies: "the Gen 3 free-time design proceeds
  on the recreation-actions direction with the reward-channel
  branch closed twice" — now carrying the composition finding as
  its rider. The clock-zero control for o14 (the declared
  confound) is moot for a null o14 result: nothing moved to
  attribute.
- Nothing deploys; rule 1 unamended; stage C (brackets) stays
  premise-dead.

## Regeneration

### Collect

`overnight4.sh` wave + the manual batteryC block (l14) +
`probe_eval_o14.py` legs (o14). Never run by the gate.

### Read

Runtime: under 10 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26
../exp-006-character-gen/.venv/bin/python enrich2c_read.py \
  --out <scratch>/enrich2c-read-fresh.json --md
```

The doc's verbatim block is the `--md` table and comparator line;
the recorded copy is `results-raw/enrich2c-read.json`.

GATE: PASS round 2 of 2, 2026-10-01 — arithmetic ~100, threshold
9, characterisation 18 (1 minor note: the probe's longest streak
is o14-s2's 1,000, l14-s1 is worst on dist ticks and tm-dist),
provenance 15, undecidable 1 (the manual l14 invocation's argv is
unrecorded; headers match on seats/band/seed0/artifact sha).
Round 1: 3 CONTRADICTED ("the arc's worst" tm-dist — stage A ran
0.0056; the "leg" unit mislabel again, two spots; "whole program"
for what cross-world's floor-15 reads already did) + 2 failing
WEAKs (the F-019 direction, inherited from the frozen prereg's
erratum — deviations file note 2; the Both-flat branch applied
without saying it was an extension). Raw hash b07c4ace83a1dedf
(sha256 over the sorted `shasum -a 256` output lines of the four
battery jsonls, `.aside` excluded, + the four traces, paths
relative to this dir, first 16 hex).
