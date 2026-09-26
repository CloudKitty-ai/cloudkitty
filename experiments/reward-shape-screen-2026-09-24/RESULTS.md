# Reward-shape screen — results

Trained 2026-09-25 (six arms, plateau stops at 8–9M ticks; launch
05:0x, finals by evening) under the declaration frozen 2026-09-24
(`PREREG.md` + `prereg-deviations.md`); batteries collected
2026-09-26T00:59–02:42Z (36 legs: five swap seats + all-arm per arm,
30 × 20k, eval band 870001, package world, served clock; artifacts
under this screen's root, base gen1-A artifacts linked in). Raws in
`results-raw/` (uncommitted, gitignored per the 2026-09-25 ruling).

## The table (rs-read.md, from `results-raw/rs-read.json`)

| arm | own-seat placement (pooled) | all-arm placement | all-arm happiness | vs gen1-A paired | worse/30 | dist ticks | mda | low-need start share |
|---|---|---|---|---|---|---|---|---|
| hard-s1 | 0.920 | 0.922 | 90.337 | -1.983 | 30/30 | 4737 | 156 | 0.172 |
| hard-s2 | 0.937 | 0.932 | 90.755 | -1.565 | 30/30 | 187 | 50 | 0.216 |
| cvx-s1 | 0.768 | 0.746 | 90.914 | -1.406 | 30/30 | 728 | 119 | 0.303 |
| cvx-s2 | 0.767 | 0.754 | 90.902 | -1.419 | 30/30 | 1902 | 195 | 0.249 |
| lam-s1 | 0.516 | 0.488 | 91.572 | -0.749 | 30/30 | 2636 | 358 | 0.211 |
| lam-s2 | 0.496 | 0.451 | 91.199 | -1.121 | 30/30 | 3527 | 308 | 0.250 |

Comparators: gen1-A on the package world 92.320 team happiness (the
recorded tier 1 cell, same band and seeds); the floor-0 null — the
same clone under plain PPO — ended at all-arm placement 0.062 /
0.033 (tier 2's pkg arms, recorded).

## The headline: objective-side pressure substitutes for the world floor

All three shapes restore beam-seeking on the floor-0 world where the
identical PPO recipe without shaping lost it: pooled own-seat
placement 0.920 / 0.937 (hard), 0.768 / 0.767 (cvx), 0.516 / 0.496
(lam) against the null's 0.033–0.062 — every arm at least 8× the
declared 0.15 bar. And the shapes dose behavior: placement orders
hard > cvx > lam while happiness orders the reverse (90.3–90.8 <
90.9 < 91.2–91.6), so stronger pressure buys more of the target
behavior at more welfare cost. Every shaped arm pays against the
unshaped gen1-A baseline (−0.75 to −1.98, worse on 30 of 30 seeds):
the term is not welfare, and the doctrine's rule-1 stance now has its
measured price on both sides — shaping works, and shaping costs.

## Predictions, scored

1. **Holds on the declared bar** (the probe-series clause is
   unscoreable — this trainer's probes never measured placement;
   `prereg-deviations.md` 2026-09-26): hard placement 0.920 / 0.937,
   both far past 0.15, against the 0.033–0.062 null.
2. **Fails on placement, holds on happiness, as declared.** The
   cvx-vs-hard placement gap is 0.160 against a two-seed band of
   0.017 — the smooth shape sits measurably lower — while the
   happiness gap (0.362) is inside its band (0.418). Curvature does
   not reproduce the fine's behavior; it reproduces its welfare at a
   lower behavioral dose.
3. **Holds in full.** Both priced arms clear the placement bar
   (0.516 / 0.496); λ settles interior at 0.119 / 0.117 against a
   clamp of 5, last-quarter stability 8.1% / 10.1% against the 20%
   line, and final occupancy sits within 0.02 of the target
   (last-quarter mean cf 0.057 / 0.054 against d = 0.06, down from
   the 0.126 violator baseline). The learned price of the
   counterfactual state is about 0.12 in team-reward units.
4. **Watched, no farming signature.** Low-need nap-start shares run
   0.172–0.303 against the floor arms' 0.22–0.33 and the floor-0
   frozen roster's 0.28; distress stays screen-scale (max streak 358,
   the priced arms' largest; no cell near the 1,000-tick line).

## Decision rules, applied

- The declared branch is the middle one: **P1 passes, P2 fails, P3
  passes → which mechanism is load-bearing, and the λ readout, go to
  the Gen 3 design; the rule-1 question goes to the owner as
  structural.** The honest characterisation of P2's failure: not
  evidence that the discontinuity is required — all three shapes
  clear the bar — but that pressure shape doses behavior, so the
  choice among them is a welfare-per-behavior trade, not a
  works-or-not fork.
- Experiments' recommendation for that fork: **the cost channel.** It
  achieved the declared comfort standard at the least happiness cost
  (−0.75 / −1.12), the least behavioral distortion, and the only
  readable price — and a free-time constraint ("free-time share at
  least X") is the same machinery verbatim. The convex drive is the
  runner-up where a one-signal recipe is worth more than
  interpretability. The fork is the owner's.
- Nothing deploys; the served reward is untouched; adoption anywhere
  goes through the doctrine amendment path (rules 1 and 2), the
  owner's ruling.
- **Recorded as F-054** (same commit).

## Regeneration

### Collect

Training: `launch_arms.sh` (six arms, logs
`results-raw/train-logs/<slot>.log`, plateau stops; ~14 h wall).
Batteries: `arms_battery.sh` (36 legs, 1 h 43 m,
`results-raw/battery.log` stamps 00:59:23 to 02:42:55). Never run by
the gate.

### Read

Runtime: under 30 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/reward-shape-screen-2026-09-24/rs_read.py \
  --out experiments/reward-shape-screen-2026-09-24/results-raw/rs-read.json \
  --md experiments/reward-shape-screen-2026-09-24/results-raw/rs-read.md
```
