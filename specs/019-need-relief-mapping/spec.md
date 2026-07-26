# Feature Specification: Need→Relief Mapping — One Source of Truth for the Baseline Cat

**Feature Branch**: `019-need-relief-mapping`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "Make the needs-driven behavior's need-to-resource correspondence single-sourced and compiler-enforced. Today the mapping from each need kind to what relieves it is encoded independently in multiple places inside the built-in needs_driven behavior stack: the target-selection scoring logic maps each need to the resource whose distance it prices (eat to chow, drink to water, sleep to sunbeam, cuddle to a friend, and so on), the pursuit logic separately maps each need to the action that relieves it, and the take-what-is-here opportunistic logic repeats per-need adjacency checks in the same shape three times. Code comments explicitly acknowledge the hazard (\"Mirrors pursue's sleep arm exactly\", \"the mirror the 004 review demanded\") — the invariant that what gets scored and what gets walked to can never disagree is currently enforced by comments and reviewer vigilance, not structure; the compiler cannot catch drift between the separate exhaustive matches. This matters beyond code hygiene: needs_driven is the counterfactual anchor of the entire evaluation suite (spec 017's sign tests and differentials pair candidates against needs_driven twins), so a silent scoring-vs-walking divergence would skew every downstream measurement. Goal: consolidate the need-to-(resource, relief-action) correspondence into a single authoritative definition per need kind, the way the kitty module already centralizes activity mappings, so that adding or changing a need touches one site and the score/walk agreement becomes structural. This is a behavior-preserving refactor: every kitty decision must remain bit-identical — verified by the determinism suite, the full welfare gates, and byte-identical eval/certification reruns against pre-refactor builds. No behavior changes, no new needs, no tuning changes."

## The problem in one paragraph

The default cat decides in three steps: it *scores* which need to serve
(pricing the distance to whatever relieves each need), it *walks and acts*
to relieve the chosen need, and along the way it *opportunistically grabs*
relief it happens to be standing next to. Each of those three steps
independently encodes the same fact — which resource relieves which need —
and the code's own comments admit they are hand-maintained mirrors of one
another. If the mirrors ever drift (a need scored against one resource but
walked toward another), the default cat doesn't crash; it quietly becomes a
slightly different cat. And this particular cat is the measuring stick for
everything: the evaluation suite's sign tests and differentials compare
every candidate policy against a world of these cats, so a silent drift here
would bias every measurement downstream while looking like a perfectly
healthy world. This refactor gives the need→relief correspondence one
authoritative home so the three steps cannot disagree — the agreement
becomes a property of the structure, checked by the compiler, instead of a
promise kept by comments.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Score and walk cannot disagree (Priority: P1)

As a maintainer of the default behavior, the answer to "what relieves this
need?" lives in exactly one place, and both the scoring step and the
pursuit step consume that one answer. It is structurally impossible for a
need to be scored against one relief source and pursued toward another —
the situation the current comments warn about can no longer be written.

**Why this priority**: This is the drift channel with measurement stakes.
The score/walk agreement is the invariant a past review explicitly demanded
and that comments currently police; making it structural protects the
evaluation suite's counterfactual anchor.

**Independent Test**: Review confirms a single authoritative definition per
need kind exists and that both scoring and pursuit derive from it, with no
remaining independent per-need mapping in either; the full determinism
suite and welfare gates pass unchanged, proving the consolidation changed
no decision.

**Acceptance Scenarios**:

1. **Given** the refactored behavior, **When** a need is selected by
   scoring and then pursued, **Then** both steps derived their
   need→relief answer from the same single definition — verified by
   inspection that no second encoding of the correspondence remains.
2. **Given** any seeded world and any number of ticks, **When** the
   pre-refactor and post-refactor engines run the same configuration,
   **Then** every kitty's every decision is identical (bit-identical world
   states throughout).

---

### User Story 2 - Opportunistic grabbing consumes the same source (Priority: P2)

As a maintainer, the take-what-is-here logic (relieving a need the kitty
happens to be adjacent to, before committing to a journey) no longer
repeats its own per-need copies of the correspondence; its three
same-shaped blocks derive from the same single definition the other steps
use.

**Why this priority**: Same invariant, third consumer. Slightly lower
stakes than User Story 1 because a drift here surfaces as visibly odd
behavior (a cat ignoring the bowl it stands beside) rather than as a
silent scoring skew — but it is the same class of hazard and the same fix.

**Independent Test**: Review confirms the opportunistic step holds no
independent need→relief encoding; determinism suite and welfare gates pass
unchanged.

**Acceptance Scenarios**:

1. **Given** a kitty adjacent to a relief source for a pressing need,
   **When** the opportunistic step evaluates it post-refactor, **Then** the
   decision is identical to the pre-refactor engine's in every seeded
   scenario, and the step's need→relief knowledge comes from the single
   definition.

---

### User Story 3 - Adding or changing a need touches one site (Priority: P3)

As a future maintainer adding a need kind (or changing which resource
relieves an existing need), I edit the single authoritative definition, and
every consumer — scoring, pursuit, opportunistic grabbing — follows. The
compiler forces completeness for the new need at that one site; there is no
checklist of mirrors to remember.

**Why this priority**: This is the payoff that compounds over time, but it
only matters when a need next changes; the P1/P2 stories deliver the
protection immediately.

**Independent Test**: A thought-experiment walkthrough recorded in the
feature's validation notes: enumerate the edit sites a hypothetical new
need would require before and after, demonstrating the count for the
need→relief correspondence drops to one. (No actual new need is added —
that would violate the behavior-preservation bar.)

**Acceptance Scenarios**:

1. **Given** the refactored structure, **When** the validation walkthrough
   traces a hypothetical new need through the behavior stack, **Then** the
   need→relief correspondence requires exactly one new entry in one place,
   and omitting any consumer is a compile-time error rather than a silent
   gap.

---

### Edge Cases

- Some needs relieve against non-element targets (companionship needs
  price distance to another kitty; rest needs may relieve in place). The
  single definition must represent every relief shape the current mirrors
  encode — element kinds, kitty proximity, terrain (sunbeam) — without
  flattening their genuine differences.
- The scoring step prices distance (including water-averse path pricing),
  while pursuit walks (including sidestep fallbacks). These steps share the
  *correspondence*, not their full logic; the refactor must not merge
  behaviors that are deliberately different, only the fact they both
  consult.
- The opportunistic step's three blocks include per-need urgency-versus-
  detour thresholds; consolidating the correspondence must not alter any
  threshold comparison or its evaluation order (decision order is part of
  bit-identical behavior).
- Tie-breaking and RNG draw order are part of the deterministic contract
  (fixed draw shape); the refactor must not change the number, order, or
  consumers of any random draw.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The correspondence from each need kind to what relieves it
  (the relief source scored for distance, and the action taken to relieve
  it) MUST exist as exactly one authoritative definition per need kind.
- **FR-002**: The target-selection scoring step, the pursuit step, and the
  opportunistic take-what-is-here step MUST all derive their need→relief
  knowledge from that single definition; no independent re-encoding of the
  correspondence may remain in any of the three.
- **FR-003**: Completeness MUST be structurally enforced: introducing a new
  need kind without defining its relief correspondence, or without every
  consumer handling it, MUST fail at build time — never silently at run
  time.
- **FR-004**: Every kitty decision MUST be unchanged: for any seeded
  configuration, pre- and post-refactor engines MUST produce bit-identical
  world states at every tick (Article V determinism, applied as the
  refactor's acceptance bar).
- **FR-005**: The existing determinism suite, long-run welfare gates, and
  all other automated tests MUST pass without modification to their
  assertions; no test may be weakened to accommodate the refactor.
- **FR-006**: Behavior preservation MUST additionally be verified
  end-to-end through the evaluation instrument: a certification run and a
  suite evaluation executed pre- and post-refactor with identical inputs
  MUST produce byte-identical reports (the default cat is the suite's
  baseline; this check proves the measuring stick did not move).
- **FR-007**: The hand-maintained mirror comments ("mirrors X exactly")
  MUST be retired along with the mirrors they police; documentation at the
  single definition MUST state the invariant it now structurally provides.
- **FR-008**: The refactor MUST NOT add needs, change tuning values,
  thresholds, pricing, or any configuration surface.

### Key Entities

- **Need kind**: one of the six drives a kitty balances (eat, drink,
  sleep, play, cuddle, groom); the key the correspondence is defined over.
- **Relief correspondence**: the authoritative fact this feature
  centralizes — for a given need kind, what in the world relieves it and
  through what action.
- **Consumer steps**: the three decision stages (scoring, pursuit,
  opportunistic grabbing) that today each carry a private copy of the
  correspondence and afterward share the single definition.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Exactly one definition of the need→relief correspondence
  exists; a reviewer can identify it and confirm zero remaining
  independent encodings across the three consumer steps (the mirror sites
  named in the 2026-07-26 survey all read as resolved).
- **SC-002**: Pre- and post-refactor engines produce bit-identical world
  states for the determinism suite's full scenario set, and the long-run
  welfare gates pass unchanged.
- **SC-003**: A certification run and a suite evaluation with identical
  inputs produce byte-identical reports (human and machine-readable)
  against pre-refactor builds — four comparisons, all identical.
- **SC-004**: The full automated test suite passes with zero assertion
  changes.
- **SC-005**: The recorded new-need walkthrough shows the need→relief
  correspondence costs exactly one edit site, with every consumer's
  handling enforced at build time.

## Assumptions

- The kitty module's existing centralized activity mappings are the
  house pattern this feature follows; matching that shape is preferred
  over inventing a new one, but the spec constrains outcomes (one
  definition, structural enforcement), not the exact form.
- The correspondence being centralized is the need→relief fact only;
  scoring economics (distance pricing, water aversion), walking mechanics
  (sidesteps), and urgency thresholds remain where they are — this feature
  moves knowledge, not logic.
- The behavior-preservation bar (bit-identical determinism plus byte-
  identical evaluation reruns plus unchanged tests) stands in for new test
  development; the only new automated coverage this feature may add is a
  compile-time or test-time guard that the single definition is the sole
  source, if one is cheap to express.
- Scope is the built-in needs-driven behavior stack only; no other
  behavior, engine phase, serialization format, or observation schema is
  touched.
