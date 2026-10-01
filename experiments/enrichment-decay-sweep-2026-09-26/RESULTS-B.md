# Enrichment-decay sweep, stage B — results

Ran under `PREREG-B.md` (frozen ddd2301, 2026-09-27, on the owner's
words). Eleven arms on the d100-1000 corner — β {0.06, 0.10, 0.14}
× 3 seeds (throttle) + ag10 × 2 (accrual gate) — run indices 79–89,
episode band 1,680,000,000–1,899,999,999. Launched
2026-09-27T20:56:24Z, `== overnight3 done` 2026-09-28T18:38:29Z.
Stops: plateau or the 20M cap per recipe (updates 2,605–3,907 per
arm; plateau lines in the train logs, e.g. b06-s2 at 8.0M ticks,
b10-s3 at 12.0M); NO futility stop fired (0 of 11 logs), no welfare
stop. Deviations: none (`prereg-b-deviations.md` was never needed).

Battery: 11 all-arm legs × 30 seeds × 20,000 ticks, eval band
870001, `--abort-streak 1000`. **All 330 rows complete: zero
aborts, zero short legs — read from the rows, not the driver
markers.** Trace β and accrual-gate flags asserted per arm by the
reader before any pooling.

## The read (reader output, verbatim)

```
| arm | play (greedy) | play (trace lastq) | closed-gate | banked | at-cap | E p50 | happiness | vs recorded | worse/30 | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b06-s1 | 0.0857 | 0.0890 | 0.1248 | 0.0381 | 0.097 | 0.463 | 91.901 | -0.420 | 30/30 | 0.1285 | 0.147 | 0.0478 | 0.0001 | 69 | 15 |
| b06-s2 | 0.0883 | 0.0907 | 0.2111 | 0.0399 | 0.099 | 0.473 | 91.324 | -0.997 | 30/30 | 0.1263 | 0.147 | 0.0448 | 0.0014 | 1256 | 97 |
| b06-s3 | 0.0802 | 0.0873 | 0.1606 | 0.0368 | 0.093 | 0.449 | 91.319 | -1.001 | 30/30 | 0.1205 | 0.123 | 0.0467 | 0.0016 | 1058 | 321 |
| b10-s1 | 0.0902 | 0.0906 | 0.1472 | 0.0367 | 0.101 | 0.471 | 92.103 | -0.218 | 29/30 | 0.1504 | 0.170 | 0.0460 | 0.0004 | 298 | 75 |
| b10-s2 | 0.0898 | 0.0892 | 0.1622 | 0.0353 | 0.099 | 0.471 | 91.715 | -0.605 | 30/30 | 0.1256 | 0.170 | 0.0460 | 0.0022 | 1563 | 256 |
| b10-s3 | 0.0837 | 0.0913 | 0.1573 | 0.0377 | 0.099 | 0.473 | 91.752 | -0.568 | 30/30 | 0.1272 | 0.159 | 0.0453 | 0.0002 | 158 | 64 |
| b14-s1 | 0.0869 | 0.0917 | 0.1129 | 0.0363 | 0.102 | 0.473 | 92.164 | -0.156 | 23/30 | 0.1298 | 0.174 | 0.0466 | 0.0008 | 574 | 190 |
| b14-s2 | 0.0955 | 0.0964 | 0.2540 | 0.0364 | 0.116 | 0.512 | 91.368 | -0.953 | 30/30 | 0.1166 | 0.128 | 0.0432 | 0.0011 | 897 | 105 |
| b14-s3 | 0.0829 | 0.0933 | 0.1998 | 0.0383 | 0.105 | 0.487 | 91.615 | -0.706 | 30/30 | 0.1269 | 0.170 | 0.0467 | 0.0005 | 588 | 110 |
| ag10-s1 | 0.0837 | 0.0887 | 0.1458 | 0.0000 | 0.091 | 0.436 | 91.743 | -0.577 | 30/30 | 0.1208 | 0.155 | 0.0458 | 0.0004 | 280 | 65 |
| ag10-s2 | 0.0780 | 0.0897 | 0.1087 | 0.0000 | 0.093 | 0.436 | 91.759 | -0.561 | 30/30 | 0.1213 | 0.140 | 0.0470 | 0.0004 | 280 | 69 |

| family | greedy play mean (per-seed) | trace play | closed-gate | banked | at-cap | delta | bin0 |
|---|---|---|---|---|---|---|---|
| b06 | 0.0848 (0.0857, 0.0883, 0.0802) | 0.0890 | 0.1655 | 0.0383 | 0.097 | -0.806 | 0.139 |
| b10 | 0.0879 (0.0902, 0.0898, 0.0837) | 0.0904 | 0.1556 | 0.0365 | 0.099 | -0.464 | 0.166 |
| b14 | 0.0885 (0.0869, 0.0955, 0.0829) | 0.0938 | 0.1889 | 0.0370 | 0.108 | -0.605 | 0.157 |
| ag10 | 0.0808 (0.0837, 0.0780) | 0.0892 | 0.1273 | 0.0000 | 0.092 | -0.569 | 0.147 |

Curve (beta 0.03 -> 0.06 -> 0.10 -> 0.14): 0.0773 -> 0.0848 -> 0.0879 -> 0.0885
```

Comparators (stage A's, same instrument): fresh gen1-A play 0.0749,
closed-gate 0.0843, bin0 0.161, eat+drink 0.0499, tm-dist 0.0003,
sleep 0.1354, dist ticks 360; recorded gen1-A happiness 92.320;
stage-A β 0.03 on this corner 0.0770/0.0776 (curve point 0.0773 =
their mean).

## Predictions, scored (bars from PREREG-B, sources inline)

- **P1 — the response curve rises: FAILED at the bar.** The curve
  is monotone (0.0773 < 0.0848 < 0.0879 < 0.0885) but saturating
  (per-step gains 0.0075, 0.0031, 0.0006): 4.7× the β buys +0.011
  pooled greedy play (+14%), and the b10 (0.0879) and b14 (0.0885)
  family means are both under the 0.10 standing bar, with the b10
  and b14 per-seed spreads overlapping fully. Glow is off the cap
  on every arm (last-quarter at-cap share 0.091–0.116, E p50
  0.436–0.512, the Professor condition — reported here before any
  β conclusion). Trace play runs higher than greedy on 10 of 11
  arms (ag10 gaps up to 0.0117, larger than the whole b06→b14
  rise), but the throttle-family ordering agrees and no arm
  crosses 0.10 on either read — the stage-A greedy-vs-training
  advisory did not bind on the adjudication.
- **P2 — banking stays dead under bigger prizes: SPLIT, and the
  bar-carrying half FAILED.** Trace banking is dead: last-quarter
  banked share 0.0353–0.0399 on every throttle arm (< 0.05), and
  structurally 0.0000 on both ag10 arms (guard-proven zeroing,
  confirmed in the trace). But the closed-gate START share
  (≥ 25 worst-need starts) exceeds the 0.1043 stage-A band on
  EVERY arm — 0.1087 (ag10-s2) to 0.2540 (b14-s2), against the
  comparator's 0.0843. The prereg's adjudicator ("the accrual-gate
  arm's P2 behavior decides whether mechanism or corner is at
  fault"): the ag10 arms also exceed the band (0.1458, 0.1087)
  despite closed-gate play earning structurally nothing, so the
  fault is the CORNER, not the mechanism. Observation beyond that
  binary (hedged, not an adjudication): the ag10 shares sit below
  their b10 twins seed-for-seed (0.1458 ≤ 0.1472, 0.1087 ≤
  0.1622), so payment pressure contributes to the share — but
  removing it structurally still leaves both ag arms over the
  band.
- **P3 — over-tending stays inside the bars: HELD everywhere,
  with the opposite sign.** bin0 max 0.174 ≤ 0.211; eat+drink max
  0.0478 ≤ 0.0699 — and every arm's eat+drink sits BELOW the
  comparator's 0.0499. The over-tending ceiling was never
  approached; the drift is toward under-tending, visible in the
  closed-gate shares above.
- **P4 — welfare prices the curve: MIXED; b06 breached.** Family
  paired deltas: b06 −0.806 (breaches its −0.50 bar), b10 −0.464
  (holds), b14 −0.605 (holds its −1.00). The cost curve is
  non-monotone in β — b06 is the most expensive family, driven by
  b06-s2/-s3 at ≈ −1.0. Watched values: sleep out of the 0.1354 ±
  0.015 band on two arms (b10-s1 0.1504 high, b14-s2 0.1166 low);
  teammate-distressed start share above the 0.001 watch line on
  four arms (b06-s2 0.0014, b06-s3 0.0016, b10-s2 0.0022, b14-s2
  0.0011; comparator 0.0003); zero aborts; max streak 321 < 1,000.
- **P5 — mechanism comparison at equal β (ag10 vs b10)**: banked 0
  vs 0.0365 (structural, as declared); greedy play 0.0808 vs
  0.0879; closed-gate 0.1273 vs 0.1556; welfare −0.569 vs −0.464.
  The accrual gate buys structurally-zero banking and a lower
  closed-gate share at slightly less play and slightly more
  welfare cost. Neither mechanism reaches traction, so no stage-C
  carrier recommendation is issued (see Decision below).
- **P6 — seat structure survives: HELD.** Biscuit is the top play
  seat in all 11 arms.

## Welfare accounting (declaration §Welfare practice)

Declared expectation: ≤ 2× stage A's worst per leg (≤ ~8,200), the
1,000-tick abort line standing, b14 named the likely maximum. A
"leg" here, as in PREREG-B and stage A's 170–4,108 figures, is one
30-seed battery leg. Measured: worst LEG 1,563 distress ticks
(b10-s2, pooled over its 30 seeds); worst single-seed episode
inside any leg 675 (b10-s2); max distress age 321; zero aborts on
330 rows. The expectation held with ~5× to spare (8,216 / 1,563),
and the named-maximum guess was wrong: b10-s2 and the b06 family,
not b14, carried the worst welfare readings.

## Decision rules, applied

P1 failed across the whole curve with glow off the cap. That is the
prereg's ruled branch: "the channel is dead as designed ('channel
dead' branch of the ruled adjudication); report; the fork is the
owner's." P2 is adjudicated by its own prereg bullet: "P2 failing
at any β → banking revives under prize pressure; the accrual-gate
arm's P2 behavior decides whether mechanism or corner is at fault;
report; her fork" — the ag10 arms fail the band too, so the
CORNER, not the mechanism, is at fault under that rule (and the
trace shows the "banking revives" clause did not literally occur:
banked payout stayed under 0.04 everywhere; what rose is the
closed-gate start share). Stage C's premise (brackets on the β
winner) has no winner; nothing freezes, and no cell proposal
accompanies this report. Nothing deploys; the served reward and
engine untouched; rule 1 unamended. The fork is the owner's.

F-055 anticipated this stage in its Invalidated-by clause ("an
accrual-gated or non-saturating variant failing the same way
(which would indict the channel, not the gate)"). Stage B's
variants failed the traction bar, but NOT with F-055's signature —
its glow was saturated; stage B's is off the cap — so the clause's
channel-indicting arm fires while F-055's measured facts stand;
F-055 carries a dated note to that effect rather than a status
change.

What the curve's shape says (reading, not a ruling): between β 0.03
and 0.14 the reward-side dose moved play by +14% while the
Professor dominance arithmetic (STAGE-B-INPUTS) predicted the
play-dominance onset moving from under p5 to ~p65 of worst-need
occupancy — the constraint that binds is not the prize size.
Together with P3's under-tending sign, the stage-B picture is a
policy whose play level is set somewhere other than the enrichment
channel's magnitude — consistent in direction with the queued
two-channel item (`two-channel-reward-inputs-2026-09-24.md`) and
with the Gen 3 free-time brainstorm's leading refinement (dedicated
recreation actions, recorded there as "leading direction pending
her confirmation"; `gen3-free-time-inputs-2026-09-26.md`) — but
stage B does not adjudicate those; it only closes the β lever.

## Regeneration

### Collect

`overnight3.sh` (waves B1–B3 + the battery block). Never run by the
gate.

### Read

Runtime: under 30 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26
../exp-006-character-gen/.venv/bin/python enrich2b_read.py \
  --out <scratch>/enrich2b-read-fresh.json --md <scratch>/enrich2b-read-fresh.md
```

The doc's verbatim block is the `--md` output's two tables and
curve line; the recorded copy is `results-raw/enrich2b-read.json`
(+ `.md`).

GATE: PASS round 3 of 3, 2026-09-29 — round 1: 2 CONTRADICTED (a
"leg" unit mislabel in the welfare accounting; the Professor
percentile pairing), 3 WEAK on ruling lines, 4 copy-check misses;
round 2 clean except one inverted phrase in F-056 ("past the
traction bar" for "missed"); round 3 clean, no undecidables.
Raw hash dc9219517f403fb4 (battery jsonls + enrich2b traces).
F-entry F-056 + the F-055 dated note copy-checked in the same
package.

## Addendum 2026-09-30 — per-seat play lift (the Professor review's free read, owner-ordered)

The Professor's stage-B review (memo
`~/ai/professor/reviews/2026-09-29-stage-b-review.md`, relayed
2026-09-30) offered this as its zero-training discriminator: "If
Biscuit (anchor play dial 0.8) moved and the other four seats
moved ~0, the anchor sets the ceiling." The owner ordered the read
("Add the biscuit-lift read"). Reader mode `--seat-lift` (opt-in;
the gated default fence above stays byte-identical). Output,
verbatim:

```
PER-SEAT PLAY LIFT over fresh gen1-A baseline (family means)
baseline: Miso 0.0344 Biscuit 0.2283 Pumpkin 0.0428 Kittybear 0.0366 Clementine 0.0322
| family | Miso | Biscuit | Pumpkin | Kittybear | Clementine | lift ex-Biscuit (sum) | Biscuit lift |
|---|---|---|---|---|---|---|
| b06 | -0.0014 | +0.0591 | -0.0023 | -0.0044 | -0.0015 | -0.0096 | +0.0591 |
| b10 | +0.0015 | +0.0609 | +0.0003 | -0.0001 | +0.0025 | +0.0043 | +0.0609 |
| b14 | +0.0011 | +0.0696 | -0.0015 | -0.0020 | +0.0008 | -0.0016 | +0.0696 |
| ag10 | -0.0024 | +0.0439 | -0.0057 | -0.0048 | -0.0011 | -0.0139 | +0.0439 |
```

Reading: the whole family-level rise is Biscuit — its contribution
is 94–147% of each family's pooled rise. Its lift is +0.0439 to
+0.0696 while the other four seats' summed lift sits between
−0.0139 and +0.0043: for the throttle families the per-seed sums
straddle zero (no declared noise line exists to test them
against); ag10 is the one consistent mover — summed lift negative
on both seeds (−0.0061, −0.0218), all four seats negative at the
family mean, 7 of 8 seat-seed cells (−0.0139 pooled, ≈ −9.5% of
those seats' combined 0.146 baseline). So the four seats whose
corpus is nearly play-free (the memo's premise) show family-mean
summed gains of at most +0.0043 at any prize, and under the
accrual gate they drifted down. That is the memo's discriminator
outcome in direction — the anchor sets the ceiling — and the
motivating evidence for the dead-or-held probe (declared
separately, PREREG-C.md). It does not change stage B's scored
predictions (P6's Biscuit-top-seat check is the one per-seat
verdict, re-verified unchanged) or the channel-dead branch; it
narrows WHERE the non-response lives.

### Read (seat-lift addendum)

Runtime: under 30 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26
../exp-006-character-gen/.venv/bin/python enrich2b_read.py \
  --out <scratch>/enrich2b-read-fresh.json --seat-lift
```

GATE (seat-lift addendum): PASS scoped round 3, 2026-10-01 —
arithmetic 40, characterisation 7, provenance 6 (2 undecidable:
the owner quote's verbatimness — it is verbatim, typed in this
session — and the relay date), mechanical 3; block byte-identical,
default fence unchanged from the r3 stamp. Round 1: a memo
paraphrase inside quotation marks ("predicted" for the memo's
"discriminator"). Round 2: the tightened rewrite minted a new
false universal ("all four seats negative on both seeds" — 7 of 8
cells). Round 3 clean.
