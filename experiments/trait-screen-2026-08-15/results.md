# Trait exchange rates, stage 1: scripted marginal cost curves

**2026-08-15** (ROADMAP v2 phase 0). 6 needs × factors {0.5, 0.75,
1.5, 2.0}× default, Miso carrying, trait-flat base (Pumpkin's
override removed), all-scripted, 10 paired seeds × 20k vs control.
Raw: `results-raw/screen.json`. Control: carrier 90.96, team 90.91.

## Carrier happiness delta vs trait-flat (the cost curves)

| need (default) | 0.5× | 0.75× | 1.5× | 2× | ~cost/unit-rate (raising) |
|---|---|---|---|---|---|
| cuddle (0.4) | **+0.76** | +0.29 | −0.58 | **−1.20** | **~3.0 — priciest** |
| eat (0.4) | +0.71 | +0.28 | −0.50 | −1.03 | ~2.6 |
| sleep (0.3) | +0.62 | +0.23 | −0.49 | −0.85 | ~2.8 |
| play (0.4) | +0.55 | +0.24 | −0.46 | −0.79 | ~2.0 |
| drink (0.4) | +0.58 | +0.21 | −0.36 | −0.75 | ~1.9 |
| bath (0.2) | +0.32 | +0.15 | −0.31 | −0.53 | ~2.6 |

Team deltas ≈ carrier/4 throughout (dilution + mild contention
externality on eat). **Zero distress in every cell** — the whole
[0.5×, 2×] envelope is constitution-safe scripted-side. Curves are
mildly convex (buying down gains more per unit than raising costs).

## The surprise: cuddle is the priciest axis (scripted company)

Not eat. Cuddle relief requires a willing adjacent partner, and
scripted company cosleeps rarely (7.5% of sleep) — a high-cuddle cat
among scripted cats waits for service that seldom comes. **This is
exactly the rate stage 2 will move most**: the deployed world
cosleeps 87% of sleep, so cuddle-rise should be far cheaper in
policy company. Clementine's design (cuddle 0.7) MUST wait for the
stage-2 bracket — the scripted number would over-compensate her.

## Provisional balanced vectors (stage-1 rates; verify directly, and
re-derive after stage 2)

- **Pumpkin rebalance**: eat 0.8 (−1.03) + sleep 0.15 (+0.62) +
  bath 0.10 (+0.32) ≈ net −0.09 — "snacky, naps light, always
  tidy." Inside the parity band pending direct verification.
- **Clementine sketch** (stage-1 rates only): cuddle 0.7 (≈ −0.88
  interpolated) + play 0.2 (+0.55) + drink 0.3 (+0.21) ≈ −0.12 —
  "affectionate, mellow, light drinker." EXPECTED TO CHANGE at
  stage 2 (see above).

Next: stage 2 (same sweep bracketed under current policies — cuddle
and bath are the axes to watch), then direct verification of chosen
vectors (additivity is a hypothesis), then the exchange table
freezes into the phase-1 design inputs. Scope stamps: engine
412d00e2…, served 20×20 geometry, scripted company; all rates mortal
on any of those moving.

## Stage 2 (same day): the policy bracket — the price order INVERTS

Same grid under the deployed roster B (greedy; Miso's cuddler
carrying — rates are carrier-conditional, stamped). Control: carrier
95.49, team 95.18. Raw: `results-raw-policy/screen.json`. Zero
distress in all 250 runs again.

| need | 2× cost, scripted | 2× cost, policy | shift |
|---|---|---|---|
| eat | −1.03 | **−1.07** | unchanged — physics |
| drink | −0.75 | **−0.87** | slightly pricier (contested water) |
| sleep | −0.85 | −0.56 | −35% |
| cuddle | **−1.20 (priciest)** | −0.51 | **−58%** |
| play | −0.79 | −0.38 | −51% |
| bath | −0.53 | −0.35 | −34% |

**Trait prices are social prices.** In company that reciprocates,
the social needs (cuddle, play) cost roughly half; the consumable
needs (eat, drink) cost the same or more — resource physics does not
adapt, affection economics does. Scripted's priciest trait (cuddle)
is policy's second-cheapest; eat takes the crown it was always
assumed to hold. Discounts also BUY less under policy (adapted cats
are already efficient — less slack to harvest: sleep 0.5× buys
+0.62 scripted but only +0.28 policy).

Revised provisional vectors (policy rates; direct verification still
required before any pin):

- **Clementine** cuddle 0.7 ≈ −0.37 (vs −0.88 scripted-derived —
  the over-compensation stage 1 warned about). Balanced candidate:
  cuddle 0.7 + play 0.3 (+0.13) + bath 0.10 (+0.28) ≈ +0.04.
  "Affectionate, mellow at play, always tidy."
- **Pumpkin**: the stage-1 vector UNDER-compensates under policy
  rates (sleep/bath discounts shrink): eat 0.8 + sleep 0.15 + bath
  0.10 nets ≈ −0.51. Either widen the compensation basket (add play
  and/or drink discounts) or accept partial compensation under
  seat-paired accounting — a phase-1 design choice, not made here.

Stamps: engine 412d00e2…, served geometry, roster-B company,
cuddler-carrier. Stage 3 (re-derive under the spread-trained
generation) remains registered in the roadmap.

## Direct verification (2026-08-15, policy company, 10 paired seeds)

| vector | predicted (marginal sum) | measured d-carrier | verdict |
|---|---|---|---|
| pumpkin-balanced (eat .8, sleep .15, bath .1) | ≈ −0.51 | −0.42 | under-compensates, as stage 2 predicted |
| **pumpkin-widened** (+ play .2, drink .3) | ≈ 0 | **−0.01** | **balanced** |
| **clementine-sketch** (cuddle .7, play .3, bath .1) | ≈ +0.04 | **−0.07** | **balanced** (parity band) |

**Additivity holds** at these magnitudes: all three vectors land
within ~0.1 happiness of their marginal-sum predictions — the
derive-then-verify loop closes on its first pass, and the exchange
table is usable as a design tool. Two production-ready balanced
vectors now exist for the phase-1 wall (Pumpkin's five-axis widened
basket, or the narrow one with its −0.42 residual absorbed by
seat-paired accounting — an owner taste call; and Clementine's
sketch, to be re-verified on her actual seat in the roster-5 world).
Zero distress in all verification cells.

## Owner's ≥0.5× floor rule + the eat-0.6 candidates (2026-08-15)

**Standing design rule (owner)**: compensating discounts never go
below 0.5× the default — which is also the measured envelope's lower
edge (below it = unscreened territory; an F-009 validity rule, not
just taste) and protects character coherence (a barely-sleeping cat
is its own distortion). Consequence: with 3 dials at the floor, the
compensation budget caps at ≈ +0.56 (policy rates) — so narrow
full-balance is achievable only for eat ≤ ~0.75; the old 0.8's
residual was structural.

Verified (policy company, 10 paired seeds):

| vector | d-carrier | note |
|---|---|---|
| eat .6 / sleep .15 / bath .1 ("06-floor") | **−0.02** | perfectly balanced; both discounts AT the floor |
| eat .6 / sleep .225 / bath .1 ("06-light") | −0.14 | in-band; sleep only 0.75×, gentler character cost |
| eat .7 / sleep .15 / bath .1 ("07-narrow") | −0.27 | snackier; residual on seat-paired accounting |

All three are certified-adjacent choices; the trade is snackiness
(+50% / +50% / +75% hunger) vs balance quality vs discount depth.
Owner picks at the plan review.

## OWNER'S PICK (2026-08-15): Pumpkin = eat 0.6 / sleep 0.2 / bath 0.1

Verified directly: **−0.11** vs trait-flat under policy company
(prediction −0.06; zero distress) — inside the parity-adjacent band,
sleep above the floor at ⅔× base. Owner's note recorded with it:
these rates are re-derived in the new world/next generation
regardless (stage-3 mortality) — this pin is for the phase-1
config-rider PR. Additivity now 5-for-5 within 0.1.

## First-pass trait sheets for the flat seats (2026-08-15, owner's
question "before we proceed"; verified, for her review)

| seat | character | vector | verified |
|---|---|---|---|
| Miso | "the deep sleeper" | sleep .6 / drink .2 / play .3 | +0.07 |
| Biscuit | "the playful one, restored" | play .8 / **eat .3 / drink .3** (owner's revision: the bowl needs are stationary — discounting them frees chase time, the pair REINFORCES the signature) | **+0.21** |
| Kittybear | "the immaculate" | bath .4 / drink .3 / play .3 | +0.06 |

All balanced-or-better, zero distress; additivity 8-for-8. Ecology
rationale recorded in the review thread: sleep-demand feeds cosleep
(the cuddler's economy), play-demand pre-builds the social-play
market for the Biscuit-2.0 lineage (its exact fingerprint),
bath-demand gives the doter kin pair a service axis. Instrument
caveat: measured with the cuddler carrying (the screen's carrier
seat); seat-true re-verification is one cell per adopted vector.
Bodies-layer status if adopted: 5/5 seats charactered — the deep
sleeper, the playful one, the snacky one, the immaculate one, the
affectionate one. Owner decides at the plan review.

**Owner's Biscuit revision (2026-08-15, late)**: discounts moved to
eat+drink — "the most stationary needs; play benefits from chasing."
Verified +0.21 (slight structural sunniness: the bowl pair over-funds
play-0.8, which cannot rise further — envelope edge; accepted under
the ceiling-as-anchor rule). Design principle extracted for the
register: **discounts can REINFORCE the signature, not just fund
it** — choose the pair that frees time for the character, when the
budget allows. Kittybear's play-discount confirmed by the owner on
the same logic (bath time). Miso confirmed as sketched. Roster sheet
final for the plan review: Miso +0.07 · Biscuit +0.21 · Pumpkin
−0.11 · Kittybear +0.06 · Clementine −0.07.

**Canonical body names (owner, 2026-08-15 — the client-facing
summaries): Miso = SLEEPY · Biscuit = PLAYFUL · Pumpkin = HUNGRY ·
Kittybear = FASTIDIOUS · Clementine = CUDDLY.** Bodies are adjectives,
minds are epithets — a served cat is both (deployed Miso today: the
sleepy cuddler; Kittybear: the fastidious doter). Display/config
naming mechanics are a wall-time Client/Product detail; these five
words are the source of truth.
