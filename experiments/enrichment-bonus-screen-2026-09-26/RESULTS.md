# Enrichment-bonus screen — results

Trained 2026-09-26 (four arms, plateau stops; launched 07:10Z, arms
done 13:11Z, batteries done 13:19Z) under the declaration frozen
2026-09-26 (`PREREG.md`, 61d7fc8). Batteries: five legs (four all-arm
+ one fresh gen1-A comparator), 30 × 20,000, eval band 870001, package
world, served clock, every leg under `--abort-streak 1000`; no leg
aborted. Raws in `results-raw/` (gitignored).

## The table (enrich-read.md, from `results-raw/enrich-read.json`)

| arm | play share | closed-gate start share | tm-dist starts | happiness | vs recorded paired | worse/30 | sleep share | low-need starts | dist ticks | mda |
|---|---|---|---|---|---|---|---|---|---|---|
| bonus-s1 | 0.0775 | 0.1172 | 351 | 91.591 | -0.729 | 30/30 | 0.1174 | 0.132 | 1124 | 131 |
| bonus-s2 | 0.0885 | 0.1801 | 560 | 91.481 | -0.839 | 30/30 | 0.1282 | 0.205 | 2286 | 492 |
| bonus-lo-s1 | 0.0858 | 0.1318 | 217 | 92.069 | -0.251 | 30/30 | 0.1261 | 0.229 | 665 | 132 |
| bonus-lo-s2 | 0.0833 | 0.1678 | 84 | 91.939 | -0.381 | 29/30 | 0.1374 | 0.273 | 199 | 175 |

Comparators: the recorded gen1-A tier 1 cell 92.320 team happiness,
sleep share 0.1354, low-need nap-start share 0.284; the FRESH gen1-A
leg (same seeds, the play-block instrument) 92.320 happiness — the
shared fields reproduce the recorded cell exactly, the instrument
cross-check — with pooled play share 0.0749, closed-gate start share
0.0843, 69 teammate-distressed starts of 222,436 (share 0.0003), 360
distress ticks.

## The headline: the impact gate leaked, consistent with glow banking

The screen FAILED its bars, and the failure is specific enough to
redesign from. Three findings — the measurements are exact; the
causal readings are this screen's diagnosis, with no control arm to
prove them:

1. **A saturated stock is a level shift, not an incentive.** The
   traces show the glow pinned near its cap (last-quarter mean E
   0.917–0.921) with the gate partly open (mean g 0.637–0.646,
   last-quarter per-update range 0.51–0.76), so the channel paid a roughly steady
   ~58% of β per tick (term 0.0086–0.0175): at the frozen pins (gain
   0.25, half-life ~139 ticks) baseline-rate play alone keeps E near
   1, so playing MORE buys almost nothing at the margin — the
   plausible reason the bar was missed (no non-saturating control
   ran, and bonus-s2 still lifted play 18%, so the flattening was
   partial). Play share under-ran the 0.10 bar on both full arms:
   0.0775 (+3.5% relative to the comparator's 0.0749) and 0.0885
   (+18%).
2. **A persistent stock lets cats bank the glow through the gate.**
   The gate prices the bonus at cash-out time, not at play time: a
   cat that plays while needy still holds the glow when its needs
   are later met, so the act escapes the gate. A shift consistent
   with exactly that happened: closed-gate play starts (worst gate
   need ≥ 25) rose from the comparator's 0.0843 share to
   0.1172–0.1801 across the arms. (Consistent with, not proven: the
   data cannot separate banking from needs generally running closer
   to the edge — the two are entangled, and the accrual-gate
   redesign removes both.) This is the banking dodge the design discussion dismissed,
   on its stated grounds that playing with a low need already pays
   nothing — grounds that miss the bank: the glow outlives the need
   dip. The owner's
   original mechanism — gating the accrual itself, her proposal
   verbatim: "Maybe it can only relieve when the other needs (of all
   cats) are all fulfilled beyond a certain threshold" — is what
   this failure calls for (this session's recommendation: applied
   per cat rather than roster-wide, as the design doc argues).
3. **The residual pressure cost welfare without buying behavior.**
   Full-β arms pay −0.729 / −0.839 paired happiness (worse on 30/30
   seeds; the −0.50 bar fails), with distress ticks at 1,124 / 2,286
   against the fresh comparator's 360 and teammate-distressed play
   starts at 351 / 560 against 69 (shares 0.0016 / 0.0021 vs
   0.0003). Everything stays screen-scale — max streak 492 against
   the 1,000-tick abort line, zero aborts — but the direction is
   uniform on happiness and the closed-gate shift. The dose arms cut
   the happiness price to 0.34× / 0.45× of the full arms' (−0.251 /
   −0.381; bonus-lo-s2's distress counts sit at baseline scale, 199
   ticks against the comparator's 360), so the cost tracks β while
   the behavior does not: pressure without traction.

The F-054 sleep dodge splits by training seed: bonus-s2 stays inside
the declared ±0.015 band (0.1282 vs 0.1354), while bonus-s1 breaks
it (0.1174) — a milder form of the suppression F-054's arms showed
(0.086–0.114). Low-need nap starts fell (0.132–0.273 vs 0.284),
which does not discriminate from F-054: 5 of its 6 arms fell too.
So part of bonus-s1's cost plausibly rides the old dodge; the split
of the remainder is unmeasured — what rose alongside it, on both
arms: needs nearer the edge and distress-adjacent play.

## Predictions, scored

1. **FAILED.** Full-β pooled play share 0.0775 / 0.0885 against the
   0.10 bar (comparator 0.0749). Dose arms reported: 0.0858 / 0.0833
   — inside the full arms' 0.0775–0.0885 range. Within the tested
   0.015–0.03 (two training seeds per β) halving β did not lower the
   play band, so β did not bind there; larger β was not tested.
2. **FAILED.** Closed-gate start shares 0.1172–0.1801 against the
   declared ceiling 0.1143 (comparator 0.0843 + 0.03), every arm
   over. The lift in play starts landed disproportionately in the
   closed-gate bin (e.g. bonus-s2: 47,002 of 261,019 starts vs the
   comparator's 18,748 of 222,436).
3. **FAILED on the count bar** (≤ 74): 351 / 560 / 217 / 84. The
   remaining P3 conjuncts hold: no leg aborted, every max streak
   < 1,000 (largest 492). Shares for scale (not a declared
   quantity): 0.0003–0.0021.
4. **FAILED on the full-β bar** (≥ −0.50): −0.729 / −0.839, worse on
   30 of 30. Sleep-share clause: bonus-s1 outside the ±0.015 band
   (0.1174), bonus-s2 inside (0.1282). Low-need clause holds (all
   below the recorded 0.284).
5. **FAILED** (the declared bar needs ≥ 4 of 5 seats positive on
   BOTH full-β arms). Biscuit stays the top play seat in all four
   arms and bonus-s2 lifted 4 of 5 seats vs the fresh comparator,
   but bonus-s1 lifted 1 of 5 — its lift concentrated in Biscuit.

## Decision rules, applied

- **P1 failed, so the declared P1-fail branch fires**: the channel is
  too weak at the calibrated β or the gate too tight; reported here
  with the dose-arm readout (within the tested 0.015–0.03, two seeds
  per β, halving β left the play band unchanged — β did not bind
  there; larger β untested); **the fork is the owner's**.
- **P4 failed, so its branch fires too**: the channel is not
  welfare-free, and the measured cost (−0.729 / −0.839 full,
  −0.251 / −0.381 dose) goes to the owner exactly as F-054's did.
- This session's RECOMMENDATION at that fork (not a declared branch;
  the redesign is an input to the Gen 3 design, not a new
  declaration): (a) **gate the accrual** — the glow only rises while
  the gate is open, the per-cat form of the owner's original
  proposal quoted above — which removes the bank; (b) **de-saturate
  the stock** — dynamics where marginal play carries marginal value
  (lower cap-approach rate, faster decay, or per-bout caps), so the
  channel is a gradient, not a level shift. Both precede any engine
  work if she takes the branch at all.
- Welfare-practice accounting: the screen's cost was four trained
  arms and batteries at screen-scale distress (largest streak 492;
  1,124 / 2,286 / 665 / 199 distress ticks per arm-leg vs 360
  baseline), bought the finding that impact-only gating failed with
  this persistent stock — before any engine work was built on it.
- Nothing deploys; the served reward and the engine are untouched;
  doctrine rule 1 stays unamended.
- **Recorded as F-055** (same commit).

## Regeneration

### Collect

Training + batteries: `overnight.sh` (four arms parallel with
`--futility-bar 0.80 --futility-probes 5`, then five battery legs
with `--abort-streak 1000`; log `results-raw/overnight.log`, markers
`== arms` 07:10:34Z → `== overnight done` 13:19:15Z). Never run by
the gate.

### Read

Runtime: under 30 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/enrichment-bonus-screen-2026-09-26/enrich_read.py \
  --out experiments/enrichment-bonus-screen-2026-09-26/results-raw/enrich-read.json \
  --md experiments/enrichment-bonus-screen-2026-09-26/results-raw/enrich-read.md
```

Gate: **PASS** 2026-09-26 (seven rounds — every number reproduced
from round 1; the six failing rounds were all prose: rewritten
decision branches, a paraphrase in quote marks, an unrun statistical
test, an F-054-dodge claim the PREREG's own band definition
contradicted, hedges and recommendation labels that did not survive
copying into the F-entry and the shelf, an unscoped β claim) ·
claims: 44 table cells + ~86 prose arithmetic, 9 thresholds all
PREREG-sourced, ~22 characterisations (1 non-failing WEAK, 1 hedged
UNDECIDABLE), ~12 provenance clean, 1 ROUNDING (~139 vs computed
138.28, the PREREG pin as printed) · raws e1bd84c48c2c.
