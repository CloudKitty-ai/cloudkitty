# Enrichment-decay sweep — preregistration (stage A)

Drafted and FROZEN 2026-09-26 on the owner's word in the Experiments
session. Her design, verbatim: "Let's do a larger sweep. We have quite
a few variables to test here: E, B, and g has been replaced with a
curve representing min/max decay values (0.25%, 0.5%, 1% min, 2.5%,
5%, 10% max maybe?), and the need levels that bracket those min/max
decay values (10,15 min, 20,25,30 max). It would be helpful to
identity the point at which banking stops occurring, as well as
figuring out what levels produce optimal free time behavior (your
point about over-tending is well-taken, and not a behavior I want to
see)." Her architecture ruling: "Impact gate is good. It should be
minimal on top of a well designed decay curve, but having it as a
backstop doesn't cost anything […] So keep+add. Let's run this. We
can always sweep B and E before gen 3." The staging (corners first,
brackets second, β and gain held) was proposed by this session and
covered by "Let's run this"; stage B freezes separately once stage A
names its winner. Deviations, if any, go in `prereg-deviations.md`.

## Question

F-055 killed the impact-only bonus channel: the glow saturated into a
level shift and the persistent stock leaked through the gate,
consistent with banking. The owner's fix is a need-proportional decay
curve on the glow — no decay while needs are met, harsh decay while
needy — with the impact gate kept as a backstop. Stage A asks, at the
decay-space corners: (1) where does banking stop, (2) does the
channel gain traction (the floor decay is what restores marginal
value to play), (3) does the protect-your-glow incentive produce
over-tending, the behavior the owner has said she does not want.

Findings relied on: F-055 (the failure this redesigns from, and the
exposure basis for the welfare-cost line), F-054 (welfare-cost
comparator for shaped objectives), F-047 (structure over constants —
the named bet holding β and gain fixed), F-004/F-009/F-012.

## The channel (pins)

As the enrichment-bonus screen (its PREREG §The channel: obs-side
read, W_nash recomposition, β = 0.03, gain = 0.25, cap 1, impact gate
g = clamp((0.25 − W)/0.10, 0, 1)) with two changes, guarded by
`test_enrich2_term.py` (terms AND the banked-payout split full-tick
against an independent reference; 3 mutate reds + the needs-block
red):

- **Decay curve replaces the flat 0.5%**: d(W) = D_MIN +
  clamp((W − 0.15)/0.10, 0, 1)·(D_MAX − D_MIN) per non-playing tick,
  applied to the glow. Stage A pins the decay brackets to the gate's
  15→25 (the calibrated p50/~p90); stage B moves them.
- **The glow is split** into open-earned and closed-earned parts
  (E = E_open + E_closed, gains attributed by whether the gate was
  open at the earning tick, both decaying identically) so the trace
  reads banking directly: `banked_payout_share` = the closed-earned
  share of all bonus actually paid.

## Arms (stage A)

The four decay corners × two seeds, run indices 69–76 (episode band
1,480,000,000–1,639,999,999):

| slot | D_MIN /tick | D_MAX /tick |
|---|---|---|
| d25-250 | 0.25% | 2.5% |
| d25-1000 | 0.25% | 10% |
| d100-250 | 1% | 2.5% |
| d100-1000 | 1% | 10% |

Recipe otherwise F-055's, unchanged (clone init, package.toml, 20M
cap, plateau stop, probes every 50, `--futility-bar 0.80
--futility-probes 5`). **Pre-declared contingent pair**: if P2 passes
at 10% max and fails at 2.5% max (the transition bracketed), the
midpoint corner (0.5%, 5%) × two seeds runs under this same
declaration and bars, run indices 77–78 (band through
1,679,999,999). Nothing else launches without a new freeze.

Saturation arithmetic behind the corner choice (calibration play
rates): equilibrium glow at a comfortable cat's baseline play is
~0.84 at the 0.25% floor but ~0.57 at the 1% floor — the 1% floor is
the corner where marginal play should carry real value again.

## Instrument (F-009 dimensions)

`cert_harness_fog.py` (play block; the needs block added 2026-09-26,
kept-green byte-identical, guarded): package world, 30 × 20,000, eval
band 870001, served clock, greedy, all-arm composition, every leg
`--abort-streak 1000`. One all-arm leg per arm plus ONE fresh gen1-A
comparator leg carrying the needs block (the F-055 comparator predates
it); happiness pairing stays against the recorded tier 1 cell
(`beam-world-screen-2026-09-19/results-raw/battery/s3-b7-t3000-n6/
gen1-A-c0-eval-30x20000.jsonl`). No swap legs, as F-055 declared and
for the same reason.

## Predictions

1. **Traction rides the floor decay**: both d100 (1% floor) arms
   reach pooled all-arm play share ≥ 0.10 (F-055's bar; comparator
   ~0.0749). The d25 arms are reported (expected lower — the 0.25%
   floor may still saturate).
2. **Banking stops at the harsh ceiling**: both d*-1000 (10% max)
   arms hold closed-gate play-start share ≤ the fresh comparator's
   share + 0.02, AND their last-quarter trace `banked_payout_share`
   < 0.05. The 2.5%-max arms are reported either way — they locate
   the transition (F-055's effective ceiling was 0.5%, the known-bad
   end).
3. **No over-tending**: on every arm, the share of cat-ticks in the
   lowest worst-need bin (worst < 10) does not exceed the fresh
   comparator's share + 0.05, and pooled eat+drink tick share does
   not exceed the comparator's + 0.02.
4. **Welfare non-inferiority**: every arm's paired all-arm
   team-happiness delta vs the recorded cell ≥ −0.50 (F-055 full
   arms: −0.729/−0.839; the redesign should cost less). Watched
   alongside, as declared in F-055: sleep share within ±0.015 of the
   recorded 0.1354; teammate-distressed play-start share ≤ 0.001; no
   leg aborts; every max streak < 1,000.
5. **Seat structure survives**: Biscuit remains the top play seat in
   every arm.

## Decision rules

- A corner passing P1–P4 is stage B's carrier: the bracket sweep
  (lower {10, 15} × upper {20, 25, 30} on the decay ramp, gate
  fixed) freezes separately on its own declaration.
- P2 split across the ceiling (pass at 10%, fail at 2.5%) fires the
  pre-declared midpoint pair; the transition point is the sweep's
  first deliverable either way.
- P1 failing on both floors, or P3/P4 failing everywhere, halts the
  arc: report with the trace readout; the fork is the owner's.
- β and gain stay fixed by her word ("We can always sweep B and E
  before gen 3"); a result contradicting the F-047 bet (e.g. P1
  failing with traces showing unsaturated glow) is reported as that
  bet failing, not patched in-flight.
- Nothing deploys; the served reward and the engine are untouched;
  doctrine rule 1 stays unamended.

## Welfare practice (the five parts)

1. **Stops**: per arm — plateau, 20M cap, §10 welfare stop, futility
   `--futility-bar 0.80 --futility-probes 5`. Asymmetric; no
   early-success stop.
2. **Scout**: not a new world config (package.toml; F-055 and its
   line of priors). Standing numbers: recorded gen1-A 92.320; fresh
   comparator kept-green legs nash 0.9244, mda 0.
3. **Welfare cost**: expected distress exposure at or below F-055's
   (its worst arm: 2,286 distress ticks, max streak 492, all
   screen-scale) — the decay curve weakens the incentive to hold
   needs at the edge, so exposure should fall. What the run buys:
   the banking-stop point and the over-tending read, before any
   engine work.
4. **Measurement aborts**: every leg `--abort-streak 1000`; the
   trainer futility stop armed (both mechanised and red-verified
   2026-09-26).
5. **Fences**: untouched — package world only.

## Seed bands (SEED-BANDS.md)

Guards/probes 900401–900430 (the term-guard leg at 900401);
batteries on eval 870001; training run indices 69–76 (+ contingent
77–78) = 1,480,000,000–1,679,999,999.

## Reads

`enrich2_read.py` (written before the battery is read; the write-up
gates before commit): per arm — pooled/per-seat play share,
closed-gate start share, teammate-distressed start share, paired
happiness, sleep share, worst-need bin shares (the over-tending
read), eat+drink share, dist ticks and max streak, trace summary
(last-quarter E, g, term, banked_payout_share); P1–P5 scored against
the bars above.
