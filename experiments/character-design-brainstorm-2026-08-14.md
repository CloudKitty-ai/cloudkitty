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
