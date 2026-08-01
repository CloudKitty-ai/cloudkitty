# Feature Specification: The Wet-Fur Engine Batch

**Feature Branch**: `024-wet-fur-batch`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "The exp-002 generation's engine batch per
HANDOFF-2026-08-01-wet-fur-batch.md — wet-fur bath cost for water
occupancy, the chase sidestep, and the welfare↔validation equivalence
guardrail, bundled deliberately so the generation's one comparability
break happens exactly once. Binding pins from BACKLOG 'Rethink how water
works for learned cats' (owner-set 2026-07-31) and the handoff's hard
constraints (owner-fixed 2026-08-01)."

## The batch framing *(read first)*

This spec bundles three items of different character — a dynamics change
(wet fur), a behavior-polish dynamics change (chase sidestep), and a pure
test (the equivalence guardrail) — **on purpose**. The exp-002 generation
trains and evaluates on one engine (the one-engine rule), so every
dynamics change it needs must land in a single break: when this batch
merges, every trajectory baseline and all six pool certifications lapse,
once, by design. Nothing else rides along: no other dynamics changes, no
schema changes, and the served world's configuration is not touched.

The pre-change measurement this break would otherwise destroy — s6's
water-occupancy behavior on the old engine — was captured by Experiments
before this spec began (`e144867`); the batch is unblocked.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Wet fur: water costs bath, honestly (Priority: P1)

Today, water aversion is scripted-behavior *style*, not physics: the
engine charges nothing for crossing or occupying a wet tile, so a trained
policy that sheds the scripted mannerism wades and lounges in ponds for
free (the live cat does exactly this — accepted as a quirk, now priced).
After this change, occupying a water tile charges the **bath need** each
tick: real to every decider, felt by RL directly through reward
(happiness = 100 − weighted needs) and by scripted cats through their
existing priority ladder. A watcher sees catlike water manners — skirt
the puddle when the detour is short, swim briskly when it is long — and
the charming aftermath falls out for free: a swim raises bath, and bath's
relief is grooming, so cats groom on the shore.

**Why this priority**: This is the reason the batch exists — exp-002
trains on this engine, and the water cost must be real before the
generation bakes in free wading.

**Independent Test**: Drive a headless world with a cat on and off water
tiles; assert the bath charge per occupied tick, the clamp, the trait
scaling, and that a scripted cat's route preference shifts — with no
other need or movement dynamics changed.

**Acceptance Scenarios**:

1. **Given** a cat whose bath need is below the clamp, **When** it
   occupies a water tile for one tick, **Then** its bath need rises by
   the configured gain scaled by its own bath trait, in addition to
   ordinary ambient accrual.
2. **Given** a cat whose bath need is at or above the clamp (50),
   **When** it occupies a water tile, **Then** the water charge does not
   apply (ambient accrual continues unchanged).
3. **Given** any cat on any water tile, **When** it moves, **Then**
   movement remains 1 tile/tick — swimming never stalls, slows, or
   reshapes movement.
4. **Given** a thirsty cat adjacent to water, **When** it drinks,
   **Then** drinking works exactly as before and incurs no bath charge —
   the charge attaches to *occupying* the water tile, never to using
   water as a drinking destination.
5. **Given** the default dial, **When** a scripted cat's route to a goal
   passes a 1-tile puddle with a short detour available, **Then** it
   skirts; **When** the only dry route is a long way around, **Then** it
   swims (slightly-averse-but-willing, the catlike setting).
6. **Given** any voluntary sequence of moves from any reachable state,
   **When** a cat swims as much as it likes, **Then** the water charge
   can never carry bath across the safeguard threshold (75) — no
   safeguard or distress event is ever attributable to swimming.

---

### User Story 2 - Chases route around friends (Priority: P2)

A chase step is applied engine-side straight toward the target, and a
friend standing in the lane stalls the chase in place — bounded by the
patience clock, but a kitty visibly frozen mid-pounce behind a bystander
is the same flavor of jank as the 2026-07-20 dance family. After this
change, a blocked chase step sidesteps around the blocker the same way
the behavior stepper learned to in spec 012: deterministically, per-kitty
seeded, never synchronized between two cats (no new dance modes).

**Why this priority**: exp-002 policies train heavily on play/chase; the
fix must land before the generation bakes in the stall. Second to wet fur
only because wet fur is the batch's reason for existing.

**Independent Test**: Fixture worlds with a blocker in the chase lane;
assert the chase advances via a lawful adjacent step instead of stalling,
that two mirrored chasers never sidestep in lockstep, and that the run is
bit-reproducible from the seed.

**Acceptance Scenarios**:

1. **Given** a chasing cat whose straight step toward its target is
   occupied by another kitty, **When** the chase step applies, **Then**
   the cat takes a lawful sidestep that keeps the chase alive instead of
   stalling in place.
2. **Given** the same world and seed, **When** the run repeats, **Then**
   the sidesteps are identical (Article V determinism).
3. **Given** a blocked cat with no lawful sidestep either (fully boxed
   in), **When** the chase step applies, **Then** it stalls as today and
   the patience clock governs, unchanged.
4. **Given** the sidestep exists, **When** chase abandonment statistics
   are measured, **Then** expectations tied to stall-fed abandonment
   (patience tuning) are re-baselined in this same change, deliberately
   and documented — stalls previously *fed* the abandon/exclusion tuning.

---

### User Story 3 - The welfare↔validation equivalence guardrail (Priority: P3)

The welfare layer's "relief exists at zero distance" predicate and the
engine's action validation encode the same law in two places, and only
the latter is authoritative. Nothing ties them together today — the spec
021 detour happened precisely because a divergence between "what the
metric assumes relieves" and "what the engine actually allows" had to be
untangled by hand. After this change, an equivalence test asserts, for
each need kind over a table of fixture worlds (neighbor free / busy /
absent; relief elements present / absent), that the metric's
zero-distance predicate agrees with "at least one lawful relieving action
validates." Any future drift becomes a red test instead of silent
certification skew.

**Why this priority**: Pure test, no behavior change, no re-baseline —
but it protects the certification measuring stick that the other two
items are about to be re-measured with, and cuddle puddles will touch
these exact predicates later.

**Independent Test**: It *is* a test. Run it; it passes on the current
law and fails when either side is deliberately perturbed.

**Acceptance Scenarios**:

1. **Given** every need kind and every fixture in the matrix, **When**
   the equivalence test runs, **Then** the welfare predicate and action
   validation agree.
2. **Given** the test suite, **When** it exercises the two layers,
   **Then** it consumes public APIs only — the measuring layer must not
   import behavior-layer knowledge.

---

### Edge Cases

- **Clamp boundary**: the gate is on the pre-charge bath value — a cat
  entering the tick just under 50 receives that tick's charge and may
  land above 50 (bounded overshoot of at most one scaled charge). The
  clamp plus ~25 points of headroom below the safeguard threshold is
  sized so overshoot plus ordinary ambient accrual still cannot crowd
  the safeguard line.
- **Lounging, not just crossing**: the charge is per occupied tick, so a
  cat that lounges in a pond accrues until the clamp and then sits
  free — priced but never punished (Article I: need pressure only).
- **High-trait swimmers**: a cat with an extreme configured bath rise
  scales the charge proportionally; validation must bound the
  configurable dial so no legal configuration can break the safeguard
  headroom arithmetic.
- **Chase through water**: a chase that routes across water pays the
  occupancy charge like any other occupancy — no special case.
- **Sidestep near walls/corners**: a blocked chase at the grid edge has
  fewer lawful sidesteps; when none exists, today's stall behavior is
  preserved exactly.
- **Two chasers, one lane**: mirrored blocked chases must not sidestep
  identically forever (the livelock family); per-kitty seeding

  guarantees decorrelation.
- **Legacy snapshots**: worlds saved before this change carry no new
  state; they must load and resume cleanly with the new keys at engine
  defaults.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Configuration MUST gain a water-cost dial,
  `water_bath_gain`, engine default **1.5** (bath per occupied tick,
  before trait scaling), with validation bounds such that no legal value
  can defeat the safeguard-headroom guarantee (FR-004). The legible
  framing: 1.0 equals 5× the ambient bath rise (0.2/tick).
- **FR-002**: While a kitty occupies a water tile and its bath need is
  **below 50** (pre-charge), the engine MUST charge bath by
  `water_bath_gain × (kitty's bath rise / 0.2)` that tick — per-cat
  personality scaling through the existing trait, on top of ordinary
  ambient accrual. At or above 50, no water charge applies.
- **FR-003**: Water occupancy MUST NOT change movement: 1 tile/tick,
  no stall, no slow, no reshaping of any action. The charge attaches to
  occupancy only — using water as a *drinking destination* (adjacency)
  stays exactly as free as today.
- **FR-004**: The batch MUST include an **executable guard** — not
  prose — asserting that no voluntary swimming from any reachable state
  can carry bath across the safeguard threshold (75) via the water
  charge: the clamp (50), the dial bounds, and trait scaling must
  together leave the safeguard unreachable by water. Certification
  hygiene by construction.
- **FR-005**: The scripted pathfinder's existing water-detour surcharge
  MUST scale by the same bath trait, so both deciders (scripted ladder,
  learned reward) express one coherent per-cat preference — a low-bath
  cat is legibly "the swimmer" to both.
- **FR-006**: A chase step blocked by another kitty MUST resolve to a
  lawful, never-reversing sidestep (closing steps preferred; a
  perpendicular arc only when nothing closes — routing around a blocker
  in an axis-aligned lane necessarily arcs) carrying the spec 012
  FR-008 guarantees: **deterministic given the seed, never synchronized
  across kitties**, falling back to today's stall only when no lawful
  sidestep exists. *(Amended at plan time — the FR-008 mechanism as built is
  behavior-side and draws per-kitty decision randomness that does not
  exist in the apply phase; the engine delivers the same two guarantees
  via seeded master-RNG draws in the tick's fair apply order, the spec
  022 deliberate-purr pattern. Research R5; 023 wait-for-me precedent.)*
- **FR-007**: Expectations and tuning tied to chase stalls feeding
  abandonment statistics (`chase_patience_ticks` calibration) MUST be
  re-baselined in this same change, with the re-baseline documented as
  deliberate (never a silent test weakening).
- **FR-008**: A welfare↔validation equivalence test MUST assert, for
  each need kind over a fixture matrix (neighbor free / busy / absent ×
  relief elements on/off/consumed), that the welfare layer's
  zero-distance-relief predicate agrees with "at least one lawful
  relieving action validates." It MUST consume public APIs only.
  *(Plan-phase finding: the test fails on today's law — the predicate
  counts any adjacent chow as Eat-relief while validation requires
  stocked chow, so a cat beside an empty bowl is "relieved" to the
  metric and refused by the engine. This batch reconciles the predicate
  to the authoritative side (stocked chow); pinned-streak accounting
  inherits the honest definition, landing inside the batch's designed
  comparability break. Research R7.)*
- **FR-009**: The batch MUST NOT change observation or action schema:
  observation stays 182 values, the action menu stays 40 rows, no new
  activity variant (Swimming stays out; a swim *pose* is client-only,
  separate track). This protects the warm-start-from-s6 lever.
- **FR-010**: The served world's configuration file MUST NOT be edited
  in this batch (it stays on the current engine + config until an
  exp-002 winner deploys). New configuration keys MUST carry engine
  defaults so every existing config and legacy snapshot loads
  unchanged. The experiments screen config MUST receive the
  values-preserved migration treatment (as in the 022 batch).
- **FR-011**: Golden/trajectory fixtures shifted by the dynamics change
  MUST be regenerated exactly once, values-only, and the comparability
  break recorded — the engine-defaults stamp moving is the designed,
  visible mark of the break.

### Key Entities

- **Water charge**: the per-tick bath cost of occupying a water tile —
  dial × trait scaling, gated by the clamp; a need-pressure mechanic,
  never a punishment (no new state, no new events).
- **Clamp** (config key `bath_gain_ceiling`): the pre-charge bath
  ceiling (50) above which water charges stop; together with dial
  bounds it guarantees safeguard headroom.
- **Sidestep**: a lawful adjacent step taken when the straight chase
  step is blocked by a kitty; per-kitty seeded, decorrelated.
- **Equivalence fixture matrix**: need kind × neighbor state × relief
  element presence; the table both layers must agree on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At the default dial, a scripted cat skirts a 1-tile puddle
  when a 2-tile detour exists, and swims when the dry detour exceeds the
  calibration threshold (~4 ticks of detour equivalent) — both shown in
  deterministic fixtures.
- **SC-002**: Property runs (randomized worlds, deliberately hostile
  behaviors, tens of thousands of ticks) show **zero** safeguard or
  distress events attributable to the water charge, at every legal dial
  value — the FR-004 guard, exercised at scale.
- **SC-003**: In a fixture where a bystander blocks the lane, the chase
  reaches its target (or the target flees normally) without a stall
  exceeding one tick; repeated runs from the same seed are
  bit-identical; mirrored two-chaser fixtures show decorrelated
  sidesteps over 1,000+ ticks.
- **SC-004**: The existing long-run welfare gate (20,000 ticks) passes
  on the new engine with every constitutional bound intact.
- **SC-005**: The equivalence test covers every need kind × every
  fixture in the matrix, passes on the law as shipped by this batch
  (eat-side reconciliation included — see FR-008), and fails when
  either layer is perturbed (verified once during development by
  deliberate perturbation, then the perturbation removed).
- **SC-006**: Observation length (182) and action-menu length (40) are
  asserted unchanged by tests that would fail the build on any schema
  drift.
- **SC-007**: Every existing config in the repository and a pre-batch
  snapshot both load and run on the new engine without edits (engine
  defaults fill the new keys).

## Assumptions

- The **final** dial value is a pre-registered exp-002 tuning decision,
  calibrated empirically by Experiments (welfare delta per crossing,
  s6 seated on the new build); the engine ships the dial and its
  starting value (1.5), and never treats it as a live-tunable.
- The one-time lapse of trajectory baselines and pool certifications is
  the designed cost of the batch; recertification is Experiments'
  workstream, not this spec's.
- Training-family variance in bath rise rates (so policies learn
  trait→cost rather than memorizing a constant) is Experiments' design
  care (F-010 applied prospectively), out of this spec's scope.
- The swim *pose* and any shake-off flourish are client-track work,
  independent of this batch; the engine exposes no new state for them
  (the client can already see position-on-water and bath).
- The brain-indicator viewer feature remains owner-deferred and is not
  part of this batch.
