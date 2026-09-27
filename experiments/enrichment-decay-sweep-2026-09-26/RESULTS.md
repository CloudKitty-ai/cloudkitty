# Enrichment-decay sweep, stage A — results

Trained 2026-09-26/27 (eight arms in two waves, all ending in
plateau stops; no §10 welfare stop and no futility stop fired; wave
1 18:23:03Z→00:44:06Z, wave 2 →06:58:47Z; batteries done 07:12:36Z)
under the declaration frozen 2026-09-26 (`PREREG.md`, 7f6fab9).
Nine battery legs (eight all-arm + the fresh gen1-A comparator),
30 × 20,000, eval band 870001, package world, served clock, every
leg `--abort-streak 1000`; zero aborts and zero short rows. Raws in
`results-raw/` (gitignored). Trace anomaly, no effect at printed
precision: the d25-250-s1 trace carries a duplicated `update 1` row.

## The table (enrich2-read.md, from `results-raw/enrich2-read.json`)

| arm | play | closed-gate | banked (trace) | E lastq | happiness | vs recorded | worse/30 | sleep | bin0 | eat+drink | dist ticks | mda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d25-250-s1 | 0.0855 | 0.1972 | 0.0990 | 0.808 | 91.685 | -0.636 | 30/30 | 0.1220 | 0.151 | 0.0439 | 479 | 74 |
| d25-250-s2 | 0.0860 | 0.1649 | 0.0949 | 0.810 | 91.735 | -0.585 | 30/30 | 0.1203 | 0.142 | 0.0471 | 557 | 86 |
| d25-1000-s1 | 0.0791 | 0.1279 | 0.0419 | 0.524 | 91.971 | -0.349 | 30/30 | 0.1266 | 0.180 | 0.0460 | 170 | 31 |
| d25-1000-s2 | 0.0817 | 0.1452 | 0.0421 | 0.520 | 91.601 | -0.719 | 30/30 | 0.1188 | 0.150 | 0.0455 | 317 | 132 |
| d100-250-s1 | 0.0784 | 0.1580 | 0.0774 | 0.750 | 91.540 | -0.780 | 30/30 | 0.1251 | 0.151 | 0.0500 | 940 | 86 |
| d100-250-s2 | 0.0828 | 0.1413 | 0.0764 | 0.737 | 91.782 | -0.538 | 30/30 | 0.1307 | 0.154 | 0.0450 | 235 | 66 |
| d100-1000-s1 | 0.0770 | 0.1003 | 0.0384 | 0.479 | 92.189 | -0.131 | 23/30 | 0.1353 | 0.201 | 0.0494 | 546 | 212 |
| d100-1000-s2 | 0.0776 | 0.0990 | 0.0380 | 0.479 | 91.975 | -0.346 | 27/30 | 0.1275 | 0.180 | 0.0508 | 4108 | 270 |

Comparators: recorded gen1-A 92.320 happiness, sleep 0.1354; fresh
gen1-A leg — play 0.0749, closed-gate start share 0.0843, bin0
(worst need < 10) share 0.161, eat+drink share 0.0499,
teammate-distressed start share 0.0003, 360 distress ticks.
Teammate-distressed start shares per arm: 0.0006 / 0.0009 / 0.0002 /
0.0004 / 0.0013 / 0.0003 / 0.0006 / 0.0056 (table order).

## The headline: the structural fixes landed; the traction question stays open, and the arc halts on its declared branch

The mechanism that ran is the banking THROTTLE (need-proportional
decay over the kept impact gate), not the accrual gating the owner
originally proposed — the accrual-gate arm remains stage B's, as
the stage-B inputs record. What stage A established:

1. **De-saturation improved, firmly at the harsh corners.**
   Last-quarter mean glow runs 0.479–0.810 by corner against
   F-055's pinned 0.917–0.921. The traces carry per-update MEANS
   only (the reader's declared limitation — no at-cap fraction),
   and the gentlest corner's 0.808–0.810 sits near the ~0.84
   still-saturating equilibrium the PREREG computed. The mean glow
   sits well off the cap at the 10%-ceiling corners (E ≈ 0.48–0.52;
   a bimodal at-cap population cannot be excluded from means) and
   only partly off it at the 2.5% ones.
2. **The banking shift is inside the declared band only at the
   (1%, 10%) corner — the transition is two-dimensional.**
   Closed-gate start share falls toward the comparator's 0.0843 as
   decay hardens, reaching 0.1003/0.0990 (≤ the declared 0.1043)
   only on the d100-1000 pair; d25-1000 misses (0.1279/0.1452)
   although its trace banked share is nearly the same (0.042 vs
   0.038). A floor effect on cash-out — glow surviving the open
   region longer pays banked earnings out more fully — is
   CONSISTENT with this but unmeasured (the near-equal banked
   shares do not separate it). The PREREG's midpoint contingency
   ("if P2 passes at 10% max and fails at 2.5% max") therefore
   does not fire: P2 as declared did not pass at 10% (d25-1000
   missed), and the halt branch below governs.
3. **Over-tending is absent everywhere** (P3 passes both clauses:
   bin0 shares 0.142–0.201 against the 0.211 line; eat+drink
   0.0439–0.0508 against 0.0699).
4. **Traction never reached the bar — and play ORDERED WITH
   RETAINED PRIZE.** Pooled play runs 0.0770–0.0860 against the
   0.10 bar (baseline 0.0749), and the gentle-floor d25 arms play
   more than the d100 arms in 14 of 16 cross-pairings and in all
   eight same-ceiling cross-pairs: the harsher floors came with
   less play (an ordering on two training seeds per cell; a
   ceiling-stratified permutation test gives one-sided p ≈ 1/36 —
   suggestive, not settled). The PREREG declared this reading in advance: "a
   result contradicting the F-047 bet (e.g. P1 failing with traces
   showing unsaturated glow) is reported as that bet failing, not
   patched in-flight" — and so it is reported. Whether the binding
   constraint is magnitude is exactly what the owner-ruled β family
   adjudicates and is NOT settled here; what stage A adds is that
   play tracked the size of the retained prize across corners
   (more decay, smaller stream, less play), which is consistent
   with the magnitude explanation the Professor memo's arithmetic
   proposed (one marginal play tick's discounted stream ≈ 0.08
   team-reward units against ~0.92/tick engine reward) — consistent
   with, not proof of.

**Welfare, reported in full per the practice.** The corner with the
banking band pass is also the cheapest on happiness — d100-1000-s1
pays −0.131 (23/30 worse) with sleep share 0.1353 against the
recorded 0.1354, the smallest happiness cost of any bonus arm to
date — but its seed-2 twin carries 4,108 distress ticks, the
LARGEST of any bonus leg and 1.8× F-055's worst (2,286), which
BREAKS the PREREG welfare-cost expectation ("expected distress
exposure at or below F-055's"). Max streak 270, zero aborts, no
stop lines crossed; the breach is one of scale-expectation, not of
any declared stop, and it is the owner's to weigh.

## Predictions, scored

1. **FAILED** (both floors): no arm reaches 0.10. The premise
   behind the d100 bar also inverted: the d100 arms (0.0770–0.0828)
   sit BELOW the d25 arms (0.0791–0.0860) in 14 of 16 pairings and
   all eight same-ceiling cross-pairs — the opposite ordering from
   the prediction's premise, on two training seeds per cell
   (ceiling-stratified permutation one-sided p ≈ 1/36; marginal
   value itself was never measured).
2. **FAILED as declared, transition located.** Banked trace share
   < 0.05 on all four 10%-ceiling arms (0.038–0.042) ✓; the
   closed-gate clause holds only on the d100-1000 pair
   (0.1003/0.0990 ≤ 0.1043); d25-1000 misses (0.1279/0.1452). The
   banking boundary runs between (0.25%, 10%) and (1%, 10%): a
   floor-and-ceiling property, not a ceiling property.
3. **PASSED**, both clauses, every arm.
4. **FAILED on the declared bar**: five of eight arms pay past
   −0.50 — d100-250-s1 −0.780, d25-1000-s2 −0.719, d25-250-s1
   −0.636, d25-250-s2 −0.585, d100-250-s2 −0.538 — with
   d100-1000 at −0.131/−0.346 and d25-1000-s1 at −0.349 inside it.
   The watched-alongside items (PREREG's wording): sleep band
   ±0.015 broken by two arms (d25-1000-s2 at 0.1188, 0.0166 under;
   d25-250-s2 at 0.1203, 0.0151 under); teammate-distressed start
   share ≤ 0.001 broken by two arms (d100-250-s1 0.0013,
   d100-1000-s2 0.0056); no aborts; every streak < 1,000 (largest
   270).
5. **PASSED**: Biscuit is the top play seat in all eight arms.

## Decision rules, applied

- **P1 failed on both floors, so the declared halt branch fires**:
  the arc halts here; this report with the trace readout is the
  deliverable; **the fork is the owner's.**
- The midpoint contingency does not launch (its declared condition
  is unmet — headline item 2 — and the halt branch governs).
- This session's RECOMMENDATION at her fork (not a declared
  branch): stage B as already ruled — the β response curve {0.06,
  0.10, 0.14} × three seeds — on the **d100-1000 corner**: it is
  the only corner inside the declared banking band, over-tending is
  absent there, and its happiness cost is the smallest measured
  (−0.131 on s1) — while its s2 carries the sweep's worst distress
  load, which the corner choice must weigh and stage B's three
  seeds would resolve as seed noise or corner property. The β
  family is the owner-ruled adjudicator of the open
  magnitude-vs-structure question; stage A's dose-ordering makes
  magnitude the live hypothesis, not the verdict. The accrual-gate
  arm and the bracket sweep ride behind it on the same corner.
- Welfare-practice accounting: eight arms and nine legs; distress
  170–4,108 ticks per leg against the 360 baseline, largest streak
  270, zero aborts, no §10 or futility stops — WITH the
  d100-1000-s2 leg exceeding the PREREG's expected-exposure line
  (4,108 > 2,286), reported above. Bought: the banking transition's
  location and dimensionality, the over-tending null, the
  play-orders-with-prize observation, and the on-record failure of
  the structure bet.
- Nothing deploys; the served reward and the engine are untouched;
  doctrine rule 1 stays unamended.

## Regeneration

### Collect

`overnight2.sh` (two waves of four arms with `--futility-bar 0.80
--futility-probes 5`, then nine battery legs with `--abort-streak
1000`; log `results-raw/overnight2.log`, markers `== wave1`
18:23:03Z → `== overnight2 done` 07:12:36Z). Never run by the gate.

### Read

Runtime: under 60 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/enrichment-decay-sweep-2026-09-26/enrich2_read.py \
  --out experiments/enrichment-decay-sweep-2026-09-26/results-raw/enrich2-read.json \
  --md experiments/enrichment-decay-sweep-2026-09-26/results-raw/enrich2-read.md
```

Gate: **PASS** 2026-09-27 (three rounds — numbers clean throughout;
round 1 caught an inverted play-ordering claim, three omitted
−0.50-bar breaches, an unreported welfare-expectation breach, and a
wrong PREREG hash; round 2 a phantom "seed-matched" pairing and an
unhedged causal claim on two-seed data; round 3 clean with
advisories) · claims: ~42 arithmetic, ~13 sourced thresholds, ~18
characterisations (1 non-failing WEAK), ~8 provenance, 0
UNDECIDABLE · advisories carried to STAGE-B-INPUTS: the play
orderings are greedy-eval (training-trace play orders the other
way); the recommended corner has the highest bin0 read (0.201/0.180
vs 0.161, inside the 0.211 bar); the at-cap glow fraction is still
unread pending the stage-B trace extension · raws d1065bb8f485.
