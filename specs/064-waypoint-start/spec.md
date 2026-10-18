# Feature Specification: Waypoint Start-Index by Position

**Feature Branch**: `product/waypoint-start`

**Created**: 2026-10-18

**Status**: Draft

**Input**: Owner kickoff 2026-10-18 (her words: "Let's implement both" —
dispersion Candidates 1 and 2; this spec is Candidate 1, her original
ruling "1) yes", 2026-10-15). Requirements note:
`experiments/gen2-teacher-dispersion-2026-10-15/REQUIREMENTS.md`.
Candidate 2 (heard-beacon narrowing) is a separate spec; Candidate 3
(friend-ward drift) shipped as spec 063.

## Why now

A dispersed cat's blind search is today seeded by identity, not
geography: the exploration tour's starting waypoint comes from the
cat's id modulo the tour cycle, so a corner-spawned cat's first
assigned waypoint can be across a 100×100 map — a long trek before any
food is found. The corners bench (requirements §Measured grounds) puts
the opening-act cost at 11–13% distress share vs ~0% central, and the
063 screen showed the damage lives in the distress TAIL, not the mean —
which is exactly what a shorter first trek attacks. The fix is purely
positional: start the tour at the waypoint nearest where the cat
actually stands.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A toggleable flag that is inert when off (Priority: P1)

An operator runs any existing config on the new engine. With the flag
absent or off, every world behaves byte-for-byte as today. With it on,
the same config otherwise unchanged runs the positional seeding — so
Experiments' corners A/B is a pure config comparison (the 063 pattern).

**Why this priority**: inert-when-off is the standing gate on every
dispersion candidate; an off-flag that leaks poisons both screen arms
and every golden.

**Independent Test**: full suite green with zero golden/pin re-cuts;
a collection run at a fixed seed, flag absent, byte-identical to the
pre-feature engine; a flag-on config validates and runs.

**Acceptance Scenarios**:

1. **Given** a config with no waypoint-start key, **When** a full run
   executes on the new engine, **Then** every readable output surface
   is byte-identical to the pre-feature engine at the same seed.
2. **Given** the flag explicitly off, **When** the same run executes,
   **Then** outputs equal the flag-absent run.
3. **Given** the flag on, **When** validation and a full run execute,
   **Then** both succeed.

---

### User Story 2 - The tour starts where the cat is (Priority: P2)

A cat spawns in a corner of a big map with the flag on. Its first
exploration waypoint is the tour stop nearest its start position —
not wherever its id lands on the cycle — so its first blind search
sweeps its own neighborhood first.

**Why this priority**: this is the candidate itself — her "1) yes".

**Independent Test**: staged worlds where id-seeding and
position-seeding disagree; flag-on initial indices equal the nearest
waypoint, flag-off equal today's id-modulo value.

**Acceptance Scenarios**:

1. **Given** flag on and a cat whose start sits beside waypoint k but
   whose id maps to a different waypoint, **When** the world is
   generated, **Then** the cat's tour index is k.
2. **Given** flag on and a start equidistant from two waypoints,
   **When** the world is generated, **Then** the tie resolves
   deterministically (the lower tour index), identically on every
   machine and run.
3. **Given** flag off, **When** the world is generated, **Then** every
   tour index equals today's id-derived value.
4. **Given** flag on, randomized starts (spec 062) also on, **When**
   worlds are generated across seeds, **Then** each cat's tour index
   is the nearest waypoint to its DRAWN start — the two knobs compose
   with no draw-order change (the 062 sub-stream is untouched).

---

### Edge Cases

- Several cats share a nearest waypoint: all start there; the engine's
  existing arrival/contention rule (advance when standing on it, or
  beside it while another cat holds it) already handles shared
  waypoints — no new rule. DECLARED consequence (review 1 observation):
  cats starting in the same area seed the same index and may tour in
  LOCKSTEP where the id law spread them — a real behavior change the
  corners-vs-central reads should expect; whether it matters is the
  screen's to measure.
- Explicit per-kitty coordinates, drawn starts (062), or default grid
  placement: the seeding reads the FINAL start position, whatever
  placed it.
- One-waypoint lattice (small world / large vision radius): nearest is
  the only one; flag-on equals flag-off behavior there (index 0 for
  everyone — identical to id-modulo on a cycle of 1).
- Mid-run state is untouched: the flag changes only the initial value
  at world generation; advancement, fog masking of other cats' tour
  state, and save/load round-trips carry whatever value exists.
- A saved world generated flag-on then resumed flag-off (or vice
  versa): the index is world state, not re-derived at load — resuming
  never re-seeds, so the flag at load time changes nothing (the 062
  precedent for generation-time knobs).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST be a single on/off flag in the world
  config's behavior section, default off, "absent" and "off"
  indistinguishable; no served or committed experiment config carries
  it on in this feature's PRs.
- **FR-002**: With the flag off, the engine MUST be byte-identical to
  the pre-feature engine on every readable surface — decisions, RNG
  consumption, serialized config (the defaults stamp and `GET /config`
  must not grow), collection arrays, goldens. Zero re-cuts.
- **FR-003**: With the flag on, each cat's initial exploration-tour
  index MUST be the tour waypoint nearest (Manhattan) its final start
  position, ties to the lower index; computed at world generation
  only, from position alone — no RNG draw, no draw-order change
  anywhere (the 062 starts sub-stream in particular is untouched).
- **FR-004**: The seeding MUST read the start position AFTER all
  placement mechanisms (explicit coordinates, 062 draws, defaults)
  have placed the cat.
- **FR-005**: Flag-on worlds MUST remain deterministic per
  seed+config, and the flag MUST NOT change what any behavior reads at
  decision time (only the initial value of existing engine state
  moves — no observation or schema change).
- **FR-006**: The full existing test and config surface MUST pass
  unchanged, and new tests MUST fail if the flag leaks into flag-off
  seeding.

### Key Entities

- **Waypoint-start flag**: one behavior-section boolean, default off.
  No dials: "nearest" has no tunable (the gate/detour pattern of 063
  does not apply — there is nothing to bound).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full run at a fixed seed on a pre-feature config, flag
  absent and flag explicitly off, is byte-identical on every readable
  output surface to the pre-feature engine; zero golden, pin, or
  fixture changes in this feature's PRs.
- **SC-002**: Across staged worlds where id-seeding and
  position-seeding disagree, flag-on initial indices equal the nearest
  waypoint (ties to the lower index) for every cat; flag-off indices
  equal today's id-derived values.
- **SC-003**: With 062 randomized starts active, flag-on seeding
  matches each drawn position exactly across seeds, and the 062 draw
  goldens are unmoved.
- **SC-004**: Identical seed+config with the flag on produces
  identical worlds and runs (determinism).
- **SC-005**: The mechanism supports Experiments' corners-vs-central
  A/B as a pure config comparison on the landed binary (their reads,
  their lane).

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts world setup (where a cat's blind search begins), so
each doctrine rule was checked before planning:

- **Rule 9 (frozen models / pins) — moved choices.** FR-001/FR-002:
  flag default off, byte-inert, so no pin or golden re-cuts and no
  deploy question; turning it on in collection or served worlds is a
  freeze-sitting/deploy ruling, not this spec's. FR-003's no-RNG
  constraint exists so the 062 sub-stream and main stream stay
  byte-identical even flag-on — divergence is attributable to the
  seeding alone.
- **Rule 5 (teacher sees what the student sees) — checked, moved
  nothing.** No new read at decision time: the tour index is existing
  engine state the explore step already consumes; only its initial
  value moves, and it moves as a function of the cat's own position —
  which the observation carries.
- **Rule 8 (scarcity / incentives) — checked, moved nothing.** No
  observation, scarcity, or price change; the search starts nearer,
  the fog stays the fog.
- **Rule 2 (prices are physics) — checked, moved nothing.** No price
  or payout; world setup only.
- **Rules 1, 3, 4, 6, 7, 10–12 — checked, moved nothing.** No reward
  term, rider, edge, spoken word, behavior build, gate, invalidation
  clause, or relief-availability change. Rule 12 in particular:
  relief availability is untouched — the cat just searches its own
  neighborhood first.

## Assumptions

- The flag lives beside 063's keys in the behavior section and follows
  the same serialization discipline (absent/false never serializes);
  exact naming is plan-level.
- "Nearest" is Manhattan, matching walk distance everywhere else in
  the house (movement-is-manhattan).
- The one-waypoint and shared-waypoint cases need no new engine rules
  (existing contention handling covers them) — verified at plan time.
- Experiments' screening protocol (corners bench, 20×20 guard, watch
  channels) lives in their requirements note and is not duplicated
  here.
