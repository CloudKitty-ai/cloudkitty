# Phase-1 design inputs — trait spreads in the training family

**Status: WORKING NOTES, not a design.** Drafted 2026-08-15 while the
exp-005 PPO arms run. Nothing here is registered, decided, or costed.
When the phase-1 prereg is written, each item is adopted (and cited),
consciously rejected, or deferred — nothing silently dropped.
Precedent: [exp-004-design-inputs.md](exp-004-design-inputs.md).

Owner input wanted on §3 (the five spread decisions). §1–§2 are
restatements of pinned facts; §4 is mechanical work that needs no
decision.

---

## 1. What is already pinned (no decisions here)

- **Substrate** (ROADMAP Phase 1, the wall, spec 033 + rider PR
  #228): roster 5, the five locked trait sheets (served
  `cloudkitty.toml` is the source of truth for the vectors), sunbeam
  7, 20×20, post-wall surface obs 225 / menu 34 / head 16 / digest
  15. Scripted anchor banked: **0.9086**
  (trait-screen-2026-08-15/results.md, re-baseline step 1).
- **Family-gen v5 obligations** (PIPELINE.md): roster-3 and roster-5
  worlds guaranteed by stratification, playful stratification, and —
  the new part — **trait spreads enter the family**, with the
  data-thinning cost priced (the F-014 precedent: roster-5
  stratification was adopted with its measured signal cost, 0.090 →
  0.041, quantified not assumed).
- **The payoff being built toward** (character brainstorm, serving-
  time dial section): π(a|s, traits) trained across a region, so the
  trait vector becomes a serving-time personality dial inside a
  **certified trait envelope**. Spread training is what makes the
  envelope more than the five points we happen to serve.
- **Measured safe region** (trait screen, stages 1–2): every need at
  factors [0.5×, 2×] of default is zero-distress in both scripted
  and policy company. Below 0.5× is unscreened (the owner's floor
  rule doubles as the envelope's measured edge, an F-009 validity
  line). Note the edge case: Biscuit's play 0.8 IS 2× default — her
  signature dial sits on the envelope boundary, so any spread around
  her sheet is one-sided on that axis.

## 2. Why spreads at all (the alternative, stated honestly)

The family could stay trait-pinned (v4 behavior: every world serves
the same five sheets). That trains minds that have only ever seen one
point in trait space — the dial payoff dies (extrapolation cliff),
and the estimator arm loses its cheapest training signal (neighbor
traits are unobserved; inference is only learnable if neighbors
actually vary). The cost of spreading is data thinning: fewer
decisions per trait condition at fixed collection budget. The design
question is where between those poles phase 1 sits, and what the
thinning actually costs.

## 3. The five spread decisions — ALL DECIDED (owner, 2026-08-16)

Verdicts, recorded for the prereg to adopt-and-cite:

- **3a — FULL ENVELOPE, distribution-shaped**: per-dial triangular
  distribution, mode at the seat's served value, endpoints at the
  measured envelope bounds (0.5×–2× of default). Full corner-to-
  corner support with mass concentrated on the served sheets
  (owner: "full coverage, centered on our served distribution,
  proportionally less at the extremes"). Collection budget RAISED
  for v5 to offset density loss (multiplier proposed at prereg
  with cost numbers). Biscuit's play dial is one-sided by
  construction (mode on the envelope edge).
- **3b — OFF-RAIL** (free box; welfare safety lives at the cert
  envelope corners, not in per-world balance).
- **3c — canonical share 1-in-3**, movable by the 3e probe.
- **3d — INDEPENDENT per-seat draws + a small CORNER STRATUM**
  (a few worlds where each seat's dials draw from the envelope
  extremes) — combination coverage for the estimator without
  spurious correlations, plus guaranteed in-distribution support
  for the certification corners.
- **3e — the price probe ADOPTED** (pinned vs spread cells at
  matched budget, v4 clone battery, per-class with play/chase
  canary). Decision-rule thresholds set at prereg freeze.
- **Roster-3 — RANDOM TRIOS STAY; the audit RECORDS, never
  excludes.** Owner: lower welfare in odd trios "isn't even a
  cost, it will help us identify stress points in the kitty
  ecosystem." Trio QA cells become findings material (F-020's
  predictions in the wild); exclusion only for catatonia-grade
  breakage, with recorded reason. The gym is not the sanctuary.

Original decision write-ups follow (rationale record):

## 3-orig. The five spread decisions (as posed)

**3a. Spread region.** Proposal: a per-seat box centered on the
served vector, each dial sampled within the measured envelope
[0.5×, 2×]-of-default, clipped so no dial leaves it. Concretely: a
±25% multiplicative jitter per dial (the family-gen house style —
chow already jitters ±1) keeps every draw well inside the envelope
except where a sheet already touches the edge (Biscuit's play 0.8),
which clips one-sided. Alternative if the dial payoff wants corners:
widen to the full envelope box per dial. The narrow box prices
cheaper; the wide box certifies more.

**3b. On-rail or off-rail.** The locked sheets are budget-balanced;
random jitter breaks balance. Proposal: sample OFF-rail (free box).
Reasons: the dial's welfare-safety comes from the certified envelope
corners at battery time, not from every training world being
balanced; the zero-distress screen already covers the whole box
scripted-side; and off-rail worlds are exactly where a mind learns
what an unbalanced neighbor looks like. Counter-position (stated so
it can be chosen): sample only rail-adjacent vectors so training
welfare stays near anchor and the family's welfare band stays tight
for gating.

**3c. Canonical share.** Some fraction of the family stays at the
exact served sheets — those are the worlds the served config
actually is, and the clone-fidelity measurements want them.
Proposal: stratify like roster — 1 in 3 worlds canonical, 2 in 3
spread. The price probe (3e) can move this number before the freeze.

**3d. Correlation structure.** Independent draws per seat per world
(proposal), or correlated (whole-roster "hot" and "cold" worlds).
Independent is simpler, covers more of the joint space, and matches
how the serving dial would actually be used (edit one cat). No known
argument for correlated draws yet.

**3e. Pricing the thinning.** F-014's pattern: adopt the
stratification with its cost measured, not assumed. Cheapest honest
instrument we have: the clone stage. Collect dataset v5 twice at
matched budget (pinned-family vs spread-family cells), train the v4
clone battery on each, compare per-class fidelity — the play/chase
classes (menu 18–32) are the canary, per F-015 conditioned by class.
If spread costs more than a registered bound (to be set in the
prereg), the canonical share rises. This rides the dataset-v5
collection that phase 1 needs anyway; the marginal cost is one extra
collection cell plus two clone trainings, both cheap on this
machine.

**One more, half-decision: roster-3 worlds.** Which three bodies
does a roster-3 world carry? v4 keeps the first N of the shuffled
roster; with per-seat sheets that now selects which CHARACTERS
exist. Proposal: keep the v4 rule (rng-shuffled subset, manifest
records who), so every character appears in roster-3 worlds at equal
rate. The doter/cuddler pairing findings (F-012: measure channels in
the company where they're healthy) suggest checking the manifest
afterward for pathological subsets rather than constraining the
sampler.

## 4. Mechanical prerequisites (no owner input, queued behind wave 1)

- **Post-wall python binding venv**: built at current main (surface
  225/34/16), pinned and printing its engine commit per the exp-005
  lesson. Lives with the phase-1 experiment dir when that opens.
- **family-gen v6** (the tool was already at v5 — playful guarantee;
  earlier docs' "v5" label for this work was stale): **BUILT
  2026-08-16** per the decided §3 design — trait plans
  canonical/spread/corner cycled on the roster-decorrelated block,
  triangular-at-the-sheet sampling in factor space, `--traits
  pinned` for the price probe's cell A, base-must-carry-a-playful
  assert. Sampler-sequence caveat applies (v6 ≠ v5 byte-for-byte;
  manifest stamp carries it).
- **Collection-base fact found by the v6 smoke test**: the served
  `cloudkitty.toml` carries only Pumpkin's and Clementine's sheets —
  the Miso/Biscuit/Kittybear sheets are owner-locked design
  (2026-08-15) that deliberately did NOT ship in the wall rider
  (trait changes void the soaking world's certification; they land
  at the phase-1 cutover). Consequence: the phase-1 collection base
  = served config + the three locked sheets + demonstrator
  behavior(s); a committed collect-config lands with the collection
  work, and §1's "served cloudkitty.toml is the source of truth for
  the vectors" holds only after the phase-1 seating rider. Without
  the sheets, spread sampling centers Biscuit's play on 1.0 instead
  of her signature 2.0 (verified both ways in the smoke test).
- **Class-credit re-baseline, remaining steps** (F-013/F-015
  standing trigger; scripted anchor already banked): class-
  conditioned probe batches on the post-wall engine. Compute-shaped;
  waits for PPO cores to free.

## 4b. Here*-family mask/enforcement divergence (033 review finding,
2026-08-15 — measurement rides dataset-v5 QA)

Here* legality is the first message law that reads mid-tick element
state, so the RL mask (frozen pre-tick snapshot) and enforcement
(live elements after earlier activities apply) can disagree within a
tick: a mask-legal HereFood off a servings-1 bowl silently downgrades
to Silent if an earlier-turn Eat empties it. The ordering is the
spec's deliberate emission-time-truth design (rots in the safe
direction), and only Here* diverges (Want*/Purr state mutates in
phase 4). Consequence for us: a mask-legal head choice can be voided
at apply time — a small bias in action-selection statistics that
mask_oracle structurally cannot catch (it probes both sides against
the same frozen snapshot). Registered bookkeeping item: during
dataset-v5 collection QA, measure the mask-legal-but-voided Here*
rate directly (decisions vs emissions on replay) and report it with
the acceptance record, alongside the usual mask-mismatch stat. If
negligible, it stays a documented asymmetry; if not, the phase-1
prereg decides what to do with it. (Do not conflate with exp-005's
0.207% probe-band mask-mismatch — that band predates the Here*
surface; its cause is cooldown-timing, not element state.)

## 4c. Estimator-arm riders for the care-coupling program (owner
direction 2026-08-16 — cheap now, load-bearing two generations out)

The registered estimator aux head is also the future care-coupling
experiment's instrument (ROADMAP parking lot: the interiority axis).
Two near-free riders to write into the phase-1 prereg:

- **Per-pair calibration logging, banked.** The aux head's
  prediction error is logged anyway; log it PER (estimator, target)
  PAIR and commit the curves — they are the pre-fog calibration
  baseline for the eventual C-grounded/C-free comparison, and the
  per-pair breakdown is mandatory there (a wireheader can stay
  calibrated on cats it ignores; never read only the average).
- **Aux-head weights stay in checkpoints.** The belief-intervention
  diagnostic runs on torch checkpoints in the python harness (no
  artifact/schema change ever needed for it) — so export can strip
  the head from .ckpolicy, but checkpoint retention must not.

Estimator progression, for orientation: phase 1 = the one unslotted
cat (roster 5, kitty_slots 3 — real signal for exactly one seat at
a time); fog = the out-of-view set, dynamic; interiority = everyone
(trainer-side obs masking for research arms, engine wall only on
seating).

## 5. Interactions worth remembering at prereg time

- The estimator arm (registered, ROADMAP) and spread training are
  mutually reinforcing: spreads create the neighbor-trait variance
  the estimator head predicts, and the estimator gives spread
  training a measurable representation payoff. If 3e forces the
  canonical share up, the estimator arm's power drops with it —
  price them together.
- exp-005's dose-response lands before the prereg freezes; the
  lineage arms' anchors are collected POST-rebalance in healthy
  company (brainstorm sequencing rule 1). Trait spreads do not
  change the anchor recipe — anchors are collected at the served
  (canonical) sheets.
- Stage-3 exchange-rate re-derivation (trait screen) happens under
  the spread-trained generation. The spread region chosen in 3a is
  the region stage 3 can see — a narrow box now bounds the envelope
  the dial can ever certify.
