# Brainstorm: the character system (owner design session, 2026-08-14)

**Status: brainstorm-grade design inputs — NOT a spec request, NOT a
prereg.** Captured so the threads survive until their work opens.
Frozen preregs outrank this doc. Context: the attention-roster
certification (D-002/D-003, seat-paired accounting) and the Pumpkin
diagnosis exposed how far the world has drifted from the
scripted-era personality design; the owner called the step-back.

## The three-layer character architecture

- **Bodies** (per-seat trait overrides): the only personality that
  survives a mind swap (Biscuit's playful *behavior* died at the 4×
  seating; Pumpkin's snacky *trait* sailed through). Persistent,
  viewer-legible, situation-generating — but traits modulate
  PRESSURES, not styles: no trait creates a grooming economy.
- **Discovery** (the seed lottery + purrsonality register): where
  styles come from today — cheap, real (cuddler/loner/doter), but
  unreproducible and untargetable. Demote to talent scout, never the
  supply chain.
- **Lineages** (clone-and-leash + fingerprint gates): the mechanism
  that makes a style durable — clone demonstrations (from retired
  scripted behaviors OR from lottery winners: the doter is a frozen
  artifact, its demonstrations regenerable forever), then
  welfare-finetune with the KL leash annealed-but-NEVER-zero.
  Durability across generations is a PROCESS property (keep the
  anchor, re-leash each generation, fingerprint-gate every
  candidate), not a one-shot training property.

## Evidence audit for the leash (owner's challenge, answered honestly)

Strong in-house: clones inherit personality (v4 per-class fidelity,
dead classes revived, channel behavior visibly the demonstrators').
Strong in-house, cautionary: UNLEASHED welfare-RL erodes whatever
doesn't pay — sunbeam-seeking (demonstrated → 0.15% residual) and
want-words (104/1k cloned → ~1/1k on-policy) both died under the
annealed-to-zero leash; grooming survived in one seed of three
(lottery, not design). **Zero in-house evidence for the never-zero
leash** — strongest external analogy is RLHF (SFT + KL-to-reference,
the most battle-tested recipe in ML). The real technical risk: **KL
binds decisions on visited states, not state visitation** —
personality lives in trajectories, so a leashed cat can keep
P(chase|bug nearby) while RL steers it away from bugs entirely.
**Buy the evidence: the leash dose-response experiment** — clone
scripted playful-Biscuit, PPO arms differing only in FINAL KL weight
β∞ ∈ {0, small, medium}, fingerprint metrics registered pre-training
(roadmap's play share / bug-over-meal / duet initiation PLUS a
trajectory-level metric — time-near-critters — aimed exactly at the
state-visitation failure mode).

**F-011 guard (standing)**: NO per-seat reward surgery for
personality — any per-kitty reward term voids the channel-honesty
economics. Team-level potential shaping (exp-004 A1 pattern) is the
only sanctioned reward-side tool. Personality lives in the
CONSTRAINT (leash), never the objective.

## Fair-trade traits (point-buy) and the iso-welfare methodology

Budget-balanced trait vectors (snackier ⇒ e.g. less sleepy) fix the
diversity-tax at the SOURCE: no seat tax, no institutional pressure
toward trait-flatness. Exchange rates are MEASURED, never assumed:

1. Stage 1 — scripted marginal cost curves per need (sweep one rise
   rate, one seat, paired seeds vs trait-flat; sunbeam-screen
   machinery). Expect unequal + nonlinear rates (relief pricing:
   sleep free anywhere, eat travel-priced + contention-convex,
   cuddle partner-priced and company-dependent per F-012).
2. Stage 2 — same under current frozen policies (brackets
   adaptation; the diagnosis measured adaptation spread already:
   same trait costs doter 0.96 / cuddler 1.1 / loner 1.25).
3. Derive candidate vectors from marginal RATIOS, then **verify each
   vector directly** (additivity is a hypothesis, not a fact; needs
   couple through time-budget and geography). Target = TEAM-iso
   (traits export contention, F-017), operational iso = |ΔW| ≤ 0.002
   (the parity band); seat-paired accounting (D-003 norm) absorbs
   residuals.
4. Stage 3 — re-derive under the spread-trained generation (the
   binding table; adaptation shrinks costs). Exchange rates are
   MORTAL: world geometry, engine stamp, company all stamped.

**Trait design = economy design**: the choice of WHICH needs rise
creates the markets personalities live in (bath pressure = demand for
the doter's grooming; cuddle pressure = demand for piles).
Mind×body fit generalizes to mind×ecology fit. Clementine (cuddle
0.7, planned) is demand-creation for the cuddler — design her
balanced from the exchange table on day one.

## The serving-time personality dial (the payoff)

Traits are already an OBSERVED input (self block carries own rise
rates; neighbors' are NOT visible — inference only). Today the
feature is wasted (families pin traits → extrapolation elsewhere).
**Trait-SPREAD training** (never searched, F-014-style data-thinning
cost priced) teaches π(a|s, traits) across a region — the trait
vector becomes the cat's system prompt, spread-training is the
instruction-tuning. Then the serving config is a personality dial:
same artifact, different trait = visibly different character
intensity. Two dial classes: self-dials (own pressures) and
ecology-dials (neighbors' demand for your style). Governance:
**certified trait envelope** — §9 battery at envelope corners,
config validation refuses out-of-envelope traits, the iso-welfare
budget surface is the welfare-safe rail the dial slides along.
Limits, stated: only trait-routed expression dials (dialects and
purr deixis are training-dynamics, unreachable by config); envelope
is a hard boundary (outside = the extrapolation cliff); a trait edit
is still a config change (stamp, restart, soak reset — no
retraining/recert if in-envelope).

## Sequencing rules extracted

1. **Anchors after trait redesign** — demonstrations embed their
   trait ecology; leashing to old-trait anchors pulls toward a
   vanished world. (No urgency to collect: frozen artifacts replay
   forever.) Collect in the composition where the personality is
   HEALTHY (F-012), or you clone the pathology.
2. **Seat the certified roster under current traits** — trait
   changes void certifications (F-013); the rebalance rides the next
   generation's re-baseline with the other riders (sunbeam 7,
   dataset v5, Clementine).
3. Renames: s3's category is **"the doter"** (owner, 2026-08-14).

## Feeds the roadmap revision (same day)

Candidate objectives: seat+soak the certified roster; trait
exchange-rate screen (stages 1–2); leash dose-response (exp-005 /
Biscuit 2.0 proving run); the Clementine/estimator generation; the
fog generation; the standing riders. Sequencing question put by the
owner: personality before or after fog + theory of mind.

## Addendum 2026-08-15: the 3-dial balancing procedure (owner's
standing rule)

A trait character = ONE raised signature trait + TWO discounts.
Procedure, in order:
1. Choose the signature trait and the two discount traits —
   character decisions, made before any arithmetic.
2. Discount depths respect the ≥0.5× floor (the measured envelope's
   edge; owner rule, same day).
3. Budget B = the two discounts' combined measured welfare gain
   (current bracket's exchange table).
4. The signature trait's CEILING = where its measured cost curve
   equals B. The ceiling is an ANCHOR, not a wall (owner
   clarification, same day): a LITTLE above is fine — welfare need
   not balance perfectly; small measured residuals are carried by
   seat-paired accounting (07-narrow's −0.27 is the calibration
   example of acceptable). The hard outer line stays the seat-paired
   gate budget, and every residual is measured and recorded, never
   estimated.
5. Direct verification of the pinned vector, always (additivity is
   4-for-4 across verified vectors but remains a hypothesis, not a
   law).
6. All rates are bracket- and generation-mortal (stage-3 re-derive).

Worked reference (policy bracket, 2026-08-15): sleep+bath floor pair
budgets +0.56 → eat ceiling ≈ 0.6 (verified: 06-floor balances to
−0.02). The PAIR sets the ceiling: drink+bath would budget +0.85 →
eat ceiling ≈ 0.72. Choosing the pair IS choosing the character.

## Addendum 2026-08-15 (late): the need-structure taxonomy (owner's,
verified against the engine)

Classify needs STRUCTURALLY so design survives rate re-derivation:

- **Travel needs — eat, drink** (solo, consumable, travel-priced).
  Asymmetry = SOURCE DYNAMICS, verified: water is permanent + fixed
  (no drain/ttl; spec-027 lake) → position-optimizable but
  contention-CONCENTRATING (explains stage-2 drink getting pricier
  under heavy-drinking policy company); chow churns (drains →
  despawns → respawns) → travel cost position-IRREDUCIBLE but
  contention-spreading. Hence eat discounts free more stationarity
  than drink (owner's call, both brackets agree: eat pricier).
- **Pack needs — cuddle > bath > sleep** (relief optimally social;
  gradation): cuddle strictly-pack (partner required by law); bath
  pack-optimal (gift economy — received grooming is free relief;
  empirical: doter recipients cut self-groom 25%); sleep pack-optimal
  ONLY since spec 031's shared warmth (owner's own rule made the
  sunny pile the best sleep).
- **Chase need — play** (hybrid): solo floor, MOBILE targets
  (critters churn/roam), social option, target-graded relief
  (spec 025). Half-pack by price behavior (−51% scripted→policy).

**The payoff — volatility forecasting**: pack-need rates are
SOCIETY-mortal (moved 35–58% between brackets; will move each
generation); travel-need rates are PHYSICS-stable (eat unchanged;
drink moves only via contention). Re-measure pack rows first at each
re-derive; travel rows and all PAIRINGS carry.

**Pairing rule, rate-free**: match discount structure to signature
structure — mobile signature → discount stationary needs (Biscuit:
play up, bowls down); stationary signature → discount travel needs,
eat before drink (Miso v2); pack signature → discount solo/mobile
needs (Clementine). Rates set values; structure sets pairs.

**FINAL FIVE SHEETS (owner-locked 2026-08-15)**: Miso SLEEPY sleep
.6/eat .3/play .3 (−0.13) · Biscuit PLAYFUL play .8/eat .3/drink .3
(+0.21) · Pumpkin HUNGRY eat .6/sleep .2/bath .1 (−0.11) · Kittybear
FASTIDIOUS bath .4/drink .3/play .3 (+0.06) · Clementine CUDDLY
cuddle .7/play .3/bath .1 (−0.07). Roster ecology audited: drink
−10% (v2 fix), play concentrated at Biscuit, bath concentrated at
the doter seat, eat contention net down.
