# Feature Specification: Fair Turn Order

**Feature Branch**: `013-fair-turn-order`

**Created**: 2026-07-20

**Status**: Draft

**Input**: Owner proposal: "Can we resort the kitty action order based on rng
(using our world seed so it's deterministic) so that the turn order is fair
rather than ID derived?" — with the constitutional wording decision: the
constitution states the *principle* ("kitties should have a fair and equal
chance at turn order"), never the mechanism.

## The gap being closed

Since the world began, actions have been applied in kitty-id order every
tick — which means the lowest-id kitty has silently won every within-tick
contest, forever: the last serving in a shared bowl, a tile two kitties step
toward at once, the race to conscript a mutual friend into a cuddle. No
single tick is unjust; the *pattern* is. After this change, the order kitties
act in is drawn fresh each tick from the world's seeded randomness: fair
over time, identical on every replay of the same seed.

**This is a constitutional amendment** (v1.0.0 → v1.1.0). Article V's tick
clause (2) — "actions are applied in stable kitty-id order" — named an
implementation that embodied the bias. The amended clause states the
guarantee instead: *"actions are applied in a per-tick order that is fair:
every kitty has an equal, reproducible chance to act first, and no kitty is
ever systematically favored."* Per the Governance clause, the constitution,
this spec, and the guarding tests change together.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No kitty is the favorite (Priority: P1)

An owner watching contested moments — two kitties reaching one bowl's last
serving, racing to the same tile, courting the same free friend — sees each
kitty win its fair share over time, not the same low-id kitty every time.

**Why this priority**: the amendment's whole substance.

**Independent Test**: over many thousands of ticks, each kitty occupies the
first slot of the turn order at statistically equal rates (the Article VI
guarding property), and no kitty is ever locked out of any position.

**Acceptance Scenarios**:

1. **Given** a long run of the default world, **When** first-slot occupancy
   is tallied per kitty, **Then** every kitty's share is statistically
   indistinguishable from equal (within a generous tolerance far outside
   noise).
2. **Given** repeated contests for a single-serving bowl between the same
   two kitties across a run, **Then** neither kitty wins them all.

---

### User Story 2 - Replays are still perfect (Priority: P2)

Determinism is untouched: the per-tick order is drawn from the world's
single seeded RNG, so the same seed produces the same orders, the same
contest winners, the same world — every run, and across save/restore.

**Independent Test**: the existing full-serialization replay and
save/restore determinism suites pass unchanged in spirit.

**Acceptance Scenarios**:

1. **Given** any seeded world run twice, **When** compared tick by tick,
   **Then** identical — including every contested outcome.
2. **Given** a world saved mid-run and restored, **Then** its future matches
   the unbroken run exactly (the RNG state rides the snapshot, and the
   turn-order draws ride the RNG).

---

### Edge Cases

- **Decision gathering keeps id order**: all kitties decide against the same
  snapshot, so gathering order confers no advantage — it only assigns each
  kitty's per-tick decision-RNG stream, which should stay stable and simple.
  Fairness applies where advantage lives: the apply phase.
- **Draw-count stability**: the shuffle costs a fixed number of RNG draws
  per tick (kitty count is constant), so the draw stream's shape never
  depends on world state.
- **The 012 etiquette's id-based right-of-way is unaffected**: that is
  deliberate symmetry-breaking between two specific kitties (and alternates
  by tick parity); it is not a turn-order advantage.
- **Old snapshots**: no schema change; a pre-013 save resumes under fair
  order from its first restored tick.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each tick, the order in which kitty actions are applied MUST
  be a fresh permutation drawn from the world's single seeded RNG — uniform
  over all orderings, so every kitty has an equal chance at every position.
- **FR-002**: The draw MUST consume a state-independent number of RNG draws
  per tick, and determinism MUST be fully preserved: same seed + config +
  ticks → same orders, same outcomes, including across save/restore.
- **FR-003**: Decision gathering (and its per-kitty RNG stream assignment)
  MUST remain in stable kitty-id order — fairness governs application, not
  observation.
- **FR-004**: The constitution MUST be amended in this same change (Article
  V clause (2) restated as the fairness principle; version 1.1.0), and a
  property test MUST guard the new clause (Article VI): first-slot occupancy
  statistically equal across kitties over a long run.
- **FR-005**: No config, API, snapshot-schema, or client changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Over ≥ 10,000 drawn orders in the default world, each kitty's
  first-slot share lies within a tolerance that equal chance passes
  comfortably and any systematic bias fails (bounds set > 6 standard
  deviations from fair).
- **SC-002**: The full determinism suite passes: identical replays,
  identical save/restore futures.
- **SC-003**: The full welfare/property suite passes — fairness must not
  disturb any Article I–III guarantee.
- **SC-004**: Constitution v1.1.0, this spec, and the guarding test land in
  one change (Governance clause honored).

## Assumptions

- Fisher–Yates over the decisions vector, seeded by the world RNG, is the
  mechanism — deliberately *not* named in the constitution, which now states
  only the principle (owner decision, 2026-07-20).
- "Fair" means equal chance at each turn-order position per tick,
  independent across ticks. It does not mean equalizing *outcomes* (a kitty
  standing closer to the bowl still gets there first — fairness governs
  ties, not geography).
- Purr-phase and environment iteration keep their current deterministic
  orders: neither confers within-tick advantage between kitties.
