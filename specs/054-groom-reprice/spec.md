# Feature Specification: Groom-other reprice — cuddle relief scales with delivered bath relief

**Feature Branch**: `054-groom-reprice`

**Created**: 2026-09-11

**Status**: Draft

**Input**: Owner design handoff (relayed via Experiments 2026-09-11, kickoff given by the owner the same day): "groomer cuddle relief scales with DELIVERED bath relief. x = min(target_bath, groom_relief 20) / 20 per groomed tick; groomer cuddle/tick c(x) = 0.25 + 1.75 * sigmoid(12 * (x - 0.27)) (smooth fit to her tiers: 2 at x>=.5, 1 at >=.25, 0.5 at >.1, floor 0.25; alternative exact-fit form 0.25 + 1.75 * min(1, (2x)^1.21) has one kink at x=.5). Replaces flat groom_cuddle_relief; lands WITH the reseat alongside the owed #332 revert — never on the frozen roster."

## Owner design rules *(verbatim, carried per the handoff)*

1. THE CHARM FLOOR IS THE DRIP TIER: the 0.25 floor equals rest_drip_relief
   by design, so clean-target grooming never beats drip-resting —
   charm-grooming stays paid (owner explicitly wants some grooming of clean
   cats for flavor) while farming gains nothing over the existing cheapest
   cuddle route. Above-floor income is additionally capped by real bath
   accrual (you can only be paid for dirt that exists).
2. Peak 2.0/tick to ONE party keeps rest_mutual (8.0 to both) dominant 4x —
   the spec-041 rider doctrine holds.
3. This is PRICING (relief -> needs -> happiness -> team Nash), not a
   per-seat reward term — F-018 layer 2 respected.
4. Implementation site is the Part B relief-farm row's: action.rs:747-760,
   law-class, no schema consequence, post-LOCK fine.

## Clarifications

### Session 2026-09-11

- Q: Which curve form — the smooth logistic or the exact-fit kinked
  alternative? → A: Owner: the logistic,
  `c(x) = 0.25 + 1.75·σ(12·(x − 0.27))` — "fully smooth, saturates at 2.
  Fit: c(0) = 0.31, c(0.10) = 0.43, c(0.25) = 1.00, c(0.50) = 1.90,
  c(1) = 2.00 — within ~0.07 of every tier" — unless a compelling reason
  surfaces (the floor question below was that check). *[Superseded by the
  ramp ruling below.]*
- Q: The logistic pays c(0) = 0.31 at a clean target, 0.06/tick above the
  0.25 drip tier — keep it and restate rule 1 with the fit tolerance, or
  require an exact 0.25 floor? → A: A (owner) — the logistic stands as-is;
  rule 1's floor calibration reads "within fit tolerance (≤0.07) of the
  drip tier". *[Superseded by the ramp ruling below, which restores the
  exact floor.]*
- Q: `groom_cuddle_relief` is pinned in frozen evals/v2, current evals/v3,
  the served config, and the training config under strict parsing — how do
  they keep loading once the flat price is retired? → A: A (owner) —
  `groom_cuddle_relief` becomes a recognised-but-inert legacy key (house
  precedent: keys recognised only so strict parsing can hold); the served
  and training configs are scrubbed of it in this same change; any
  evals/v4 re-cut is the reseat sitting's decision.
- Q: How should the curve be evaluated so Article V determinism and
  cross-platform goldens survive — the sigmoid's exp() would be the first
  transcendental in the tick path, and platform libm differs by ~1 ulp
  between macOS and Linux? → A: The question dissolves (owner ruling A,
  2026-09-11, after discussion with Experiments): the curve is a **clamped
  linear ramp**, `c(x) = min(2.0, 0.25 + 3.5·x)` — pure add/mul/min, the
  tick path's native arithmetic class, deterministic by construction, and
  replicable in one line of lab numpy. This supersedes the logistic: the
  floor becomes exactly 0.25 (rule 1's strict "never beats drip-resting"
  reading is restored), saturation is exact at x = 0.5, and the accepted
  trade is mid-dirty pay ~0.10–0.13 above the original tiers
  (c(0.10) = 0.60 vs 0.5, c(0.25) = 1.125 vs 1), which the owner has seen.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Grooming pays for the cleaning it actually delivers (Priority: P1)

A kitty grooms a friend. Each groomed tick, the friend's bath need drops as
today; the groomer's cuddle relief is no longer a flat payment but a function
of how much cleaning that tick actually delivered: `x` is the delivered bath
relief as a fraction of a full groom tick (`x = delivered / groom_relief`,
where delivered is the bath relief the target actually received, capped by
the dirt they actually had), and the groomer earns `c(x)` cuddle relief that
tick. Grooming a genuinely dirty friend pays near the 2.0 peak; grooming a
half-clean friend pays proportionately; the payment falls tick by tick as
the target comes clean, because the dirt being consumed is the thing being
paid for.

**Why this priority**: This is the reprice — the mechanism that makes
groom-other income honest. Everything else in this spec is consequence
management.

**Independent Test**: Drive a two-kitty world where one grooms the other at
known bath levels; assert the groomer's per-tick cuddle relief equals `c(x)`
at each tick's delivered fraction, including the decay as the target cleans.

**Acceptance Scenarios**:

1. **Given** a target with bath need at or above a full groom tick's relief,
   **When** a groomed tick applies, **Then** the target's bath drops by the
   full groom relief and the groomer receives exactly 2.0 cuddle relief.
2. **Given** a target with bath need at half a groom tick's relief,
   **When** a groomed tick applies, **Then** the delivered fraction is 0.5
   and the groomer receives exactly 2.0 — the saturation point.
3. **Given** a target with zero bath need, **When** a groomed tick applies,
   **Then** the groomer receives the curve's clean-target value (the floor
   tier), and the target's bath stays at zero.
4. **Given** a groom scene running while the target's bath falls,
   **When** successive ticks apply, **Then** each tick's payment is computed
   from that tick's delivered relief — the payment decays with the dirt,
   never riding a stale opening value.
5. **Given** solo grooming (no target), **When** ticks apply, **Then**
   nothing changes from today: the groomer's own bath drops and no cuddle
   relief is paid — the curve concerns kitty-directed grooming only.

---

### User Story 2 - The relief farm closes; charm grooming survives (Priority: P2)

A policy that would farm groom income finds the exploit priced out
pre-emptively: a clean or nearly-clean target pays only the floor tier —
calibrated to the drip-rest tier, the existing cheapest cuddle route — and
above-floor income exists only where real dirt exists. Meanwhile the flavor
the owner wants stays: grooming a clean cat still pays something, so
charm-grooming remains a real (just never optimal) choice — and the floor
also pays a scene's tail ticks, where the engine's scene minimum holds a
groom open on an already-clean target (exactly the charm case). The
partnered-rest economy stays dominant: the curve's 2.0/tick peak to one
party sits 4× under the 8.0-to-both mutual-rest anchor.

(Evidence note, corrected 2026-09-11 per Experiments' RESULTS.md @
2dfc899: the earlier "farm germinating at the flat 0.5 price" read was an
instrument artifact and is retracted — no farm has been observed. The
reprice's motivation is the surviving finding: PPO decays groom-other from
the imitated ~13/1k cat-ticks to 0.9–8.4/1k at plateau under the flat
price — the behavior is imitated fine, then reward-starved during RL. The
curve raises honest groom pay toward its real delivered value while the
floor/cap design closes the farm route in advance.)

**Why this priority**: The reward starvation is why the reprice exists;
the floor and dominance calibrations are why it is safe to ship. The
calibrations are the design rules, verbatim above.

**Independent Test**: Compare per-tick cuddle income across the three
routes at anchor values — groom-a-clean-cat (floor tier), drip-rest (0.25),
mutual rest (8.0 each) — and assert the ordering the design rules state.

**Acceptance Scenarios**:

1. **Given** the anchor pricing (drip 0.25, mutual rest 8.0 to both),
   **When** the curve is evaluated, **Then** its peak per-tick payment to
   one party is at most one quarter of the mutual-rest payment per party
   (rule 2's 4× dominance).
2. **Given** a clean target, **When** a kitty grooms it repeatedly,
   **Then** total cuddle income is exactly the 0.25 floor per tick —
   equal to the drip tier, so farming a clean cat never beats
   drip-resting (rule 1, strict).
3. **Given** a dirty target, **When** it is groomed to clean, **Then**
   cumulative above-floor income is bounded by the dirt that actually
   existed — no scene can be paid twice for the same bath need.

---

### User Story 3 - One curve, every reader (Priority: P3)

The scripted brain and the observability surfaces follow the same pricing
the effect pays. The scripted wet-responder seam that prices a groom scene
(exposure vs. scene value: the groomee's bath pressure plus the groomer's
expected cuddle relief, spec 045 seam 3) values the groomer's side by the
curve at the groomee's actual bath — not a stale flat number — and the
meow-response exposure gate does the same. The key-settings block
(spec 052) shows the new pricing dials with value, default, and source; the
docs state the curve, its constants, and the design intent.

**Why this priority**: A pricing change that leaves a reader on the old
price creates silent drift between what the scripted teacher expects and
what the world pays — the exact class of bug the one-effect-body comment in
the engine exists to prevent.

**Independent Test**: The 045 pinned seam tests re-pointed at curve values
pass red-then-green; the served key-settings block lists the new dials; no
reader of the retired flat price remains.

**Acceptance Scenarios**:

1. **Given** the wet-responder pricing seam, **When** it values a groom
   scene, **Then** the groomer-relief term is the curve evaluated at the
   groomee's current bath (delivered-fraction basis), and the 045
   sensitivity property (the decline bar tracks the configured pricing)
   holds against the curve's dials.
2. **Given** the served world's `/settings` block, **When** it renders,
   **Then** the groom pricing dials appear with value, default, and source,
   and the retired flat dial no longer appears as a key setting.
3. **Given** the shipped documentation of cuddle-relief semantics,
   **When** a reader looks up groom-other, **Then** the curve, its
   constants, and the floor/dominance calibrations are stated.

---

### Edge Cases

- Target bath deeper than one full groom tick → `x` caps at 1; the payment
  saturates at the curve's 2.0 ceiling, never above.
- Delivered relief is what the target actually received: a target with
  bath 7 against a 20-point groom tick delivers `x = 0.35` — the cap by
  existing dirt is per-tick, not per-scene.
- The floor is income, not a charge: `c(x)` is never negative and never
  zero — charm grooming always pays the floor tier (owner rule 1's flavor
  guarantee).
- Curve inputs are always in [0, 1] by construction (delivered relief is
  clamped by both the target's bath and the full-tick relief); the curve
  needs no out-of-range behavior, and validation keeps its dials finite
  and non-negative like every relief dial.
- The contagion-era seams (spec 044/045) are deployed inert for Gen 1 but
  still compile and still price — they must read the curve so they cannot
  drift while inert.
- Existing configuration files pin the retired flat dial (frozen evals/v2,
  current evals/v3, the served config, the training config) — all keep
  loading via the recognised-but-inert legacy key (FR-010); breaking the
  current eval suite's ability to load is not an acceptable outcome.
- Precision: dial values print and serve as written (the spec 052
  shortest-round-trip lesson applies to any new f32 dials).

## Requirements *(mandatory)*

### Functional Requirements

**The curve (User Story 1)**

- **FR-001**: Kitty-directed grooming MUST pay the groomer cuddle relief
  per groomed tick as a function of that tick's **delivered** bath relief:
  `x = delivered / groom_relief` where `delivered` is the bath relief the
  target actually received that tick (bounded by the target's current bath
  need and by the full-tick groom relief), and the payment is `c(x)`.
- **FR-002**: The curve is the clamped linear ramp
  `c(x) = min(2.0, 0.25 + 3.5 · x)` (per the 2026-09-11 clarifications,
  superseding the logistic): floor exactly 0.25 at x = 0, strictly
  increasing until exact saturation at 2.0 from x = 0.5, constant 2.0
  after (c(0) = 0.25, c(0.10) = 0.60, c(0.25) = 1.125, c(x ≥ 0.5) = 2.0).
- **FR-002a**: The curve MUST be evaluated using only the tick path's
  native arithmetic class (addition, multiplication, min/clamp) — no
  transcendental or platform-library math enters world dynamics — so
  Article V determinism and cross-platform golden identity hold by
  construction. Strict monotonicity below saturation ("getting dirtier
  always pays more") is a pinned invariant.
- **FR-003**: The curve REPLACES the flat `groom_cuddle_relief` payment.
  Solo grooming is untouched (no cuddle payment, exactly as today); the
  groomee's side (bath relief received) is untouched; no other action's
  pricing moves.

**Calibration (User Story 2, owner rules 1–2)**

- **FR-004**: The curve's floor MUST equal the drip-rest tier exactly
  (0.25 at anchor values), restoring rule 1's strict reading: clean-target
  grooming never out-earns drip-resting, while the floor stays strictly
  positive so charm-grooming remains paid.
- **FR-005**: The curve's per-tick peak payment to one party MUST remain
  at most one quarter of the mutual-rest per-party payment at anchor
  values (2.0 vs 8.0) — the spec-041 rider doctrine — and this dominance
  MUST be asserted by a test at the anchor pricing.
- **FR-006**: Above-floor income MUST be capped by real bath accrual: each
  tick's payment derives only from relief actually delivered that tick,
  so cumulative above-floor income over any scene is bounded by the dirt
  that existed.

**Layer discipline (owner rule 3)**

- **FR-007**: This change is PRICING — relief flowing through needs,
  happiness, and the team objective — and MUST NOT add, remove, or reweight
  any per-seat reward term. The observation/reward schema (schema 5, 408
  floats) MUST be byte-identical before and after; no retraining artifact
  changes shape.

**One curve, every reader (User Story 3)**

- **FR-008**: Every reader of the retired flat price MUST read the curve at
  the same delivered-fraction basis the effect pays: the effect application
  itself, the scripted wet-responder scene-pricing seam (spec 045 seam 3),
  and the scripted meow-response exposure gate. No reader may retain a flat
  valuation; the 045 pinned sensitivity tests are re-pointed at the curve's
  dials, red-then-green.
- **FR-009**: The curve's constants (floor, slope, ceiling — 0.25, 3.5,
  2.0) are configuration dials with the owner's values as engine defaults,
  per Article VI (documented defaults, no magic numbers); validation
  bounds them like every relief dial (finite, non-negative, ceiling ≥
  floor, and monotonicity preserved: slope ≥ 0).
- **FR-010**: Every configuration file that pins the retired flat dial MUST
  keep loading: `groom_cuddle_relief` is retained as a recognised-but-inert
  legacy key (clarified 2026-09-11, ruling A; house precedent — keys
  recognised only so strict parsing can hold), so frozen `evals/v2/*`
  (never edited) and current `evals/v3/*` (the reseat's certification
  suite) load unchanged, their pinned flat values inert under the new
  physics. The served config and the training config are scrubbed of the
  legacy key in this same change; whether the reseat cuts an evals/v4 with
  curve-native pins is that sitting's decision.
- **FR-011**: The key-settings surface (spec 052) MUST list the new pricing
  dials (value, default, source) and stop listing the retired flat dial;
  the key-name golden moves accordingly, and the engine-defaults stamp
  moves only by this declared config-surface delta.
- **FR-012**: The cuddle-relief semantics documentation MUST state the
  curve, its constants and defaults, the delivered-relief basis, and the
  two calibrations (floor = drip tier, 4× mutual-rest dominance), replacing
  the flat-price description.

**Timing (the handoff's landing rule)**

- **FR-013**: This reprice lands WITH the Gen 1 reseat and MUST NOT be
  active on the frozen roster: it is not deployed to the serving world
  before that world's roster is retrained under the new pricing (the
  frozen-models-cannot-answer-a-reprice doctrine — Clementine's
  clean-target grooms would pay ~the floor, recreating her futile loop
  worse). It is sequenced alongside the owed #332 revert
  (`groom_cuddle_relief` bump), which this spec supersedes naturally: the
  flat dial the revert would have restored is retired by FR-003. Nothing
  in this arc deploys.
- **FR-014**: A step-7 read is owed once this lands (recorded as a
  follow-up, not built here): groom latency vs bath level — private income
  now prefers dirty targets; the team objective is the counterweight.

### Key Entities

- **Delivered bath relief**: the bath-need drop the groom target actually
  received on one tick — the quantity that earns; capped by the target's
  dirt and the full-tick relief.
- **The pricing curve `c(x)`**: the single mapping from delivered fraction
  to groomer cuddle relief; one definition, read identically by the effect
  body, the scripted pricing seams, and the documentation.
- **The retired flat dial**: today's `groom_cuddle_relief` — engine default
  15.0, served at 2.0, anchor-pinned at 0.5 — replaced by the curve;
  legacy-key handling per FR-010.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The entire pre-existing automated test suite passes, with the
  only intended reds being the pinned tests this spec re-points (the flat
  groom-pay assertions and the 045 seam sensitivities), each red for the
  predicted reason before its re-point.
- **SC-002**: The curve's anchor points hold exactly under test at
  defaults: c(0) = 0.25, c(0.10) = 0.60, c(0.25) = 1.125, c(0.5) = 2.0,
  c(1) = 2.0 — strictly increasing on [0, 0.5], constant at the ceiling
  after — and the evaluation path contains no transcendental math
  (FR-002a), so the same inputs produce bit-identical payments on every
  supported platform.
- **SC-003**: In a driven scene, per-tick groomer income equals c(delivered
  fraction) at every tick, including the decay as the target cleans; a
  clean-target scene's income never exceeds the 0.25 floor;
  cumulative above-floor income never exceeds what the target's opening
  dirt can deliver.
- **SC-004**: At anchor pricing, the curve peak (2.0/tick, one party) is
  exactly 4× under mutual rest (8.0/tick per party), asserted.
- **SC-005**: The observation/reward schema is byte-identical (schema 5,
  408 floats); no reward term changes; the change is invisible to every
  training artifact except through world dynamics.
- **SC-006**: All shipped and frozen configuration files load: evals/v2
  and evals/v3 byte-unchanged via the inert legacy key; the served and
  training configs scrubbed of it and loading cleanly.
- **SC-007**: The served `/settings` block lists every new pricing dial
  with value + default + source and no longer lists the retired flat dial;
  `GET /config` on the served world is byte-identical except for the
  declared dial changes.

## Assumptions

- **Anchor calibration values**: drip-rest 0.25, mutual rest 8.0 to both,
  full groom tick 20 — the shakeout anchor's pins, which the design's
  numbers are calibrated against (verified in the anchor config). If the
  reseat re-pins any of these, the two calibration rules (floor = drip
  tier, 4× dominance) are the invariants to re-check, not the raw numbers.
- **The #332 revert is superseded, not performed**: retiring the flat dial
  discharges the owed revert (there is no bumped flat value left to
  revert); the reseat sitting confirms this disposition.
- **Contagion stays inert**: the 044/045 seams read the curve but remain
  deployed-inert for Gen 1 per the standing owner ruling; nothing here
  re-activates them.
- **Eval-suite evolution is the reseat's decision**: whether the reseat
  cuts an evals/v4 with curve-native pins is out of scope here; this spec
  only guarantees v2/v3 keep loading.
- **Nothing deploys from this arc**; the box, the shakeout artifacts, and
  the frozen roster are untouched until the reseat.
