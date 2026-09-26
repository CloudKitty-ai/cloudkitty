# Enrichment-bonus screen — preregistration

Drafted and FROZEN 2026-09-26 on the owner's word in the Experiments
session ("Let's run that overnight, and we can tackle the gen 2 spec
session tomorrow" — the prototype screen she and this session designed
across the same sitting; the design record is
`../gen3-free-time-inputs-2026-09-26.md` §"Refinement, same day",
including her operating-range correction that put the gate in need
space). Deviations, if any, go in `prereg-deviations.md`.

## Question

Gen 3 needs free-register life to emerge without violating doctrine
rule 1 (reward is team welfare only). The ruled-out alternative is a
priced quota (F-054: objective-side pressure works and costs, and a
quota homogenizes personalities). The candidate is the BONUS CHANNEL:
a positive-only enrichment term entering each cat's happiness before
the Nash mean, gated in need space so it is worthless while any
survival need is unmet. This screen prototypes the channel
trainer-side (the engine's happiness is untouched; the term exists
only in this lab trainer as a prototype of an engine-side happiness
change) and asks: does the channel elicit the behavior, does the gate
keep it out of needs' way, and what does it cost on engine happiness?

Findings relied on: F-047 (structure decides, constants matter less),
F-050 (PPO keeps what the world pays for), F-054 (the shaped-penalty
frontier this design answers), F-004/F-009/F-012 (measurement
discipline, instrument dimensions, deployment composition).

## The channel (pins)

Per cat, from its OWN observation (schema-5 self block; guard
`test_enrich_term.py`, obs/state agreement 1.0, Nash recomposition gap
2.4e-08):

- Glow stock E in [0, 1]: E += 0.25 on a Playing tick (capped at 1),
  else E *= 0.995 (half-life ~139 ticks). E resets with a world reset.
- Need-space gate g: worst gate need W = max of Eat, Drink, Sleep,
  Cuddle, Bath (Play excluded — it is the enrichment-linked need);
  g = clamp((0.25 − W) / 0.10, 0, 1): full bonus at W ≤ 0.15, zero at
  W ≥ 0.25 (the owner's operating-range correction: the ramp must
  discriminate the range the roster actually lives in).
- Bonus b = β·E·g with β = 0.03 (full arms) and 0.015 (dose arms), in
  normalized happiness units.
- Reward recomposition, per world-tick:
  reward += W_nash(h + b) − W_nash(h), the engine's own aggregate
  (p = 0, ε = 0.01). Positive only; exact, not additive-approximate.

### Calibration (measured 2026-09-26, `results-raw/calibration.json`;
gen1-A on package.toml, 3 × 5,000 ticks, seeds 900301–900303)

- Worst gate need percentiles (×100): p5 7.6 / p25 11.4 / p50 14.8 /
  p75 19.3 / p90 24.2 / p95 27.5 → the ramp's 15→25 is p50→~p90.
- Baseline pooled play share 0.0754 (per seat: Miso 0.032–0.034,
  Biscuit 0.225–0.232, Pumpkin 0.042–0.049, Kittybear 0.033–0.043,
  Clementine 0.032–0.037; the play dial is 0.8 on Biscuit, 0.3 or
  unset elsewhere).
- Play-start worst-need percentiles: p50 15.7 / p90 24.2 / p95 26.7.
- Play starts with a distressed teammate: 0 of ~5,600 starts.
- Happiness percentiles: p5 87.2 / p50 92.8 / p95 95.9 (the range the
  gate must discriminate).

## Arms and recipe

Four arms, F-054's recipe unchanged (clone init, pinned radius,
beta_low leash, package.toml, cap 20M ticks, Part C plateau stop,
probes every 50 updates): `bonus-s1`, `bonus-s2` (β 0.03),
`bonus-lo-s1`, `bonus-lo-s2` (β 0.015). Trainer
`trainer/train_ppo_enrich.py`, slots at run indices 65–68 (episode
band 1,400,000,000–1,479,999,999, SEED-BANDS.md). Trace per update to
`artifacts/ppo-fog-<slot>/enrich-trace.jsonl` (mean E, mean g, play
share, mean term).

## Instrument (F-009 dimensions)

`cert_harness_fog.py` (play block added 2026-09-26, kept-green
byte-identical on old fields; guard `test_harness_play.py`): package
world, 30 × 20,000 ticks, eval band 870001, served clock, greedy,
all-arm composition (the deployment composition, F-012). Per arm one
all-arm leg; plus ONE fresh gen1-A comparator leg on the same
instrument (the recorded gen1-A cell predates the play block, so play
baselines come from the fresh leg; happiness pairing stays against the
RECORDED tier 1 cell `beam-world-screen-2026-09-19/results-raw/
battery/s3-b7-t3000-n6/gen1-A-c0-eval-30x20000.jsonl`, F-054's
comparator, same band and seeds). No swap-seat legs: the claim lives
in the deployment composition, and own-seat placement is not this
screen's observable (declared economy; what it cannot see: mixed-
roster behavior of a single bonus mind among gen1-A incumbents).
Every leg runs `--abort-streak 1000`.

## Predictions

1. **Emergence**: both full-β arms' pooled all-arm play share ≥ 0.10
   against the fresh comparator's ~0.075 (calibration 0.0754). Dose
   arms reported (expected between comparator and full arms), no bar.
2. **The gate holds**: on every bonus arm, the share of play starts in
   the closed-gate bin (worst gate need ≥ 25) does not exceed the
   fresh comparator's share + 0.03. Reported alongside: where the play
   LIFT lands by bin (expected: overwhelmingly below 25).
3. **No distress dodge**: pooled teammate-distressed play starts per
   arm ≤ the fresh comparator's + 5 counts over 30 seeds (calibration
   baseline: 0); no leg aborts on the 1,000-tick streak line; every
   max_distress_age < 1,000.
4. **Welfare non-inferiority on ENGINE happiness** (the screen's key
   question — F-054's shaped arms paid 0.75–1.98): both full-β arms'
   paired all-arm team-happiness delta vs the recorded gen1-A cell
   ≥ −0.50; sleep share within 0.015 of gen1-A's 0.135 (the F-054
   dodge, watched); low-need nap-start share not above the recorded
   gen1-A's.
5. **Seat structure survives**: Biscuit remains the top play seat in
   every bonus arm, and the per-seat play lift vs the fresh comparator
   is positive in ≥ 4 of 5 seats on the full-β arms (a quota would
   homogenize; the channel should lift broadly while personality
   orders the levels).

## Decision rules

- P1 ∧ P2 ∧ P4 → the bonus channel is validated as the Gen 3
  free-time mechanism; the engine-side design (happiness carrying the
  bonus, enrichment activities, trait weighting) goes to the Gen 3
  spec inputs, kickoff the owner's.
- P1 passes, P2 fails → the gate form is wrong (ramp too soft or
  misplaced); gate redesign precedes any engine work.
- P1 fails → the channel is too weak at the calibrated β or the gate
  too tight; report with the dose-arm readout; the fork is the
  owner's.
- P4 fails → the channel is not welfare-free; the measured cost goes
  to the owner exactly as F-054's did.
- Nothing deploys; the served reward and the engine are untouched;
  doctrine rule 1 stays unamended (the prototype's term lives in the
  lab trainer only).

## Welfare practice (the five parts, README §Design discipline)

1. **Stops, declared and asymmetric**: per arm — Part C plateau, the
   20M cap, the §10 welfare stop (nash < 0.5 × 3 probes), and the
   futility stop `--futility-bar 0.80 --futility-probes 5` (gen1-A
   probes ≈ 0.92; a run held under 0.80 cannot pass P4 and its
   completion changes no decision). No early-success stop exists.
2. **Scout**: package.toml is not a new world config (tier 1–6,
   F-054, and the served world's history). Standing numbers cited:
   recorded gen1-A 92.320 team happiness on the paired cell; kept-
   green leg 2026-09-26 nash 0.9244, mda 0. The calibration read
   above is this screen's fresh baseline.
3. **Welfare cost**: expected distress exposure ≈ baseline scale
   (gen1-A on package: mda 0 across the kept-green legs; the channel
   is positive-only and need-gated, so the plausible harm is mild
   need neglect at the ramp edge, watched by P2/P3/P4; F-054's worst
   penalty arm carried 4,737 distress ticks — this screen is expected
   under that by design). What the run buys: the go/no-go on the
   Gen 3 free-time mechanism before any engine spec work.
4. **Measurement aborts**: every battery leg runs
   `--abort-streak 1000` (mechanised and red-verified 2026-09-26,
   `test_welfare_stops.py`); the trainer futility stop is likewise
   mechanised and red-verified.
5. **Fences**: untouched — package world only; no fenced config runs.

## Seed bands (SEED-BANDS.md)

Probe/calibration 900301–900330 (this screen); batteries on the
shared eval band 870001 (paired with the recorded gen1-A cell);
training episodes 1,400,000,000–1,479,999,999 (run indices 65–68).

## Reads

`enrich_read.py` (written before the battery is read; the write-up
carries `### Collect` / `### Read` fences and gates before commit per
the accuracy-gate contract): per arm — pooled and per-seat play share,
start bins, teammate-distressed starts, paired happiness vs the
recorded cell, sleep share, low-need nap-start share, dist ticks and
max streak, trace summary (mean E / g / term trajectory). Guards:
`test_enrich_term.py` (3 mutate reds: play cell, gate polarity, reward
sign), `test_harness_play.py` (1 red: play cell), `test_welfare_stops.py`
(2 reds: abort boundary, futility threshold).
