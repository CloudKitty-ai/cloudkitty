# Tasks: Gen 2 Observation Schema Bump

**Input**: Design documents from `/specs/058-gen2-observation-schema/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R12),
data-model.md, contracts/observation-v6.md, quickstart.md

**Tests**: included — house rule 5 makes red-first mandatory. Every
new assertion runs through `scripts/mutate.sh --expect <prediction>`;
each test task states its prediction. Rule 6 applies to the bump:
guards of the OLD layout must go red exactly where listed, kept
behavior must stay green.

**Organization**: by user story; US1 is the wall itself, US2 the
column map, US3 the reserve proofs. One stated independence
exception: the encoder cannot move until T004 decouples the v5
oracle (Foundational, blocking by design).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Verify worktree `~/ai/cloudkitty-schema-bump` is on
  `product/schema-bump` at origin/main ≥ 3d24af73 and
  `cargo test --workspace` is green pre-change (baseline record in
  the PR body)

## Phase 2: Foundational (blocking prerequisites)

- [X] T002 Add identity-dial accessors `comfort_slack_for(id)`,
  `consent_line_for(id)`, `favourite_weight_for(id, kind)` with
  per-kitty roster overrides and world defaults (the `need_rate_for`
  pattern) in crates/cloudkitty-core/src/config/mod.rs; defaults in
  config/defaults.rs (data-model table)
- [X] T003 Validate the new dials (comfort_slack ≥ 0 finite;
  per-kitty consent_line 0–100; favourite weights [0,1]; NaN
  rejected) in crates/cloudkitty-core/src/config/validate.rs — test
  first, mutate predictions: an out-of-range favourite weight and a
  NaN slack each fail validation by name
- [X] T004 Decouple the v5 oracle: convert
  crates/cloudkitty-rl/tests/schema_five_pins.rs to assert a LITERAL
  v5 offset table (no reads of live `offsets::*` constants), so the
  encoder can move without silently dragging the oracle — mutate
  prediction: editing one literal in the table reds the pin
- [X] T005 Run the config sweeps with the new toml keys' defaults in
  place (`cargo test --workspace` config-sweep tests +
  config-sweep-exclusions.txt check): new root toml keys redden two
  sweeps until defaults land (rust-toolchain-pin lesson)

**Checkpoint**: dials readable, v5 oracle frozen — the wall can move.

## Phase 3: User Story 1 — the schema wall (P1) 🎯 MVP

**Goal**: observation v6 + global state v2 live: size-invariant
spatial cells, five-of-six visibility, identity block, no clock,
waypoint bearing, reserve cells present-at-zero.

**Independent Test**: quickstart scenarios 1, 2, 3, 6, 7, 8.

### Tests first (red before implementation)

- [X] T006 [US1] Write crates/cloudkitty-rl/tests/schema_six_pins.rs
  asserting every contract offset literally (self 109, row 58, slots
  6/5/7/11, no clock, versions 6 and 2) — RED against the v5 encoder
  by construction; mutate prediction post-green: any single offset
  literal edit reds it
- [X] T007 [P] [US1] Write the size-invariance test (quickstart 2) in
  crates/cloudkitty-rl/tests/size_invariance.rs: same relative scene
  at 20×20 vs 100×100, spatial cells identical — prediction: RED
  under the v5 width/height-normalized encoder (cells differ), green
  only after FR-001
- [X] T008 [P] [US1] Write the row-visibility property test
  (quickstart 3) in crates/cloudkitty-rl/tests/row_visibility.rs:
  randomized friend states; row carries bath, layout has no cell for
  the five needs/happiness; heard rows carry bath 0 — prediction:
  RED (v5 rows carry needs+happiness)
- [X] T009 [P] [US1] Write the no-clock, overshoot, and
  waypoint-value tests (quickstart 6, 8; FR-012) in
  crates/cloudkitty-rl/tests/clock_and_range.rs: stationary world
  encodes tick-stable; dx=2,dy=3 at r=4 encodes Manhattan 5 unclamped
  (FR-001a); waypoint cells equal the L1 unit bearing toward
  `Lattice::waypoint(own explore index)` and (0,0) when standing on
  it — predictions: clock test RED (v5 clock cell moves), overshoot
  RED (no such cells yet), waypoint RED (no such cells yet); mutate
  prediction post-green: swapping the waypoint bearing components
  reds the value test

### Implementation

- [X] T010 [US1] Rewrite the encoder in
  crates/cloudkitty-rl/src/observe.rs per the contract: spatial
  group helper (Manhattan bearing + /40 + log400, zero-distance
  (0,0)), wall cells, identity block via T002 accessors, row
  removals + bath cell, heard-row mask, waypoint bearing via
  `Lattice`, reserve push (two 0.0), clock cell and `episode_clock`
  parameter removed, `OBSERVATION_SCHEMA_VERSION = 6`, offsets
  module and `block_widths`/`observation_len` updated — T006–T009
  green; rule 6 sort: schema_five_pins stays GREEN (literal table,
  T004), encoder-coupled v5 row tests in observe.rs's test module go
  red and are updated to v6 with each rename listed in the PR
- [X] T011 [US1] Remove `behavior::served_clock` and its serving
  plumbing in crates/cloudkitty-core/src/behavior/mod.rs and callers
  (R9) — rule 6: its unit tests are deleted with it, stated in the
  PR
- [X] T012 [US1] Extend crates/cloudkitty-rl/src/global_state.rs per
  kitty with the +8 identity extension via T002 accessors;
  `GLOBAL_STATE_SCHEMA_VERSION = 2`; `global_state_len` updated —
  test first: global-state pins for the new per-kitty width, mutate
  prediction: dropping the consent cell reds the width pin
- [X] T013 [US1] Verify the artifact version gate end to end
  (quickstart 7): a v5-pinned policy refuses to load against v6 with
  a clear error, and the served Gen 1 path still loads v5 — test in
  the existing version-gate suite, mutate prediction: forcing the
  gate to accept mismatched versions reds it

**Checkpoint**: the wall is up; `cargo test --workspace` green.

## Phase 4: User Story 2 — column map (P2)

**Goal**: named, version-keyed cell lookups through the binding.

**Independent Test**: quickstart scenario 4.

- [X] T014 [P] [US2] Write
  crates/cloudkitty-rl/tests/schema_map.rs: v5 lookups equal the
  T004 literal table; v6 lookups equal the T006 pins; unknown
  version/name are errors; action-menu names match the codec table —
  RED (module absent); mutate prediction post-green: swapping two
  v5 entries reds the oracle cross-check
- [X] T015 [US2] Implement crates/cloudkitty-rl/src/schema_map.rs:
  `column_map(version)` with v6 derived from the encoder's offset
  constants, v5 as the literal table, action menu v2 names,
  `UnknownSchemaVersion`/`UnknownCell` errors (R8)
- [X] T016 [US2] Export `COLUMN_MAPS` and `ACTION_MENU` from
  crates/cloudkitty-py/src/lib.rs beside the `*_SCHEMA_VERSION`
  constants; python-side check per quickstart 4 (maturin develop,
  VIRTUAL_ENV set)

**Checkpoint**: readers can flip; Experiments' lane unblocked.

## Phase 5: User Story 3 — dirt reserve proofs (P3)

**Goal**: the two reserve cells provably inert (e_col bar, R10).

**Independent Test**: quickstart scenario 5.

- [X] T017 [US3] Write the inertness property test in
  crates/cloudkitty-rl/tests/dirt_reserve.rs: both cells exactly 0.0
  over randomized worlds/configs, and no encoder write path reaches
  the reserve range (offsets 107–108 written only by the reserve
  push) — mutate prediction: making the encoder write any nonzero
  into offset 107 reds it
- [X] T018 [US3] Record the inertness result in the contract
  (contracts/observation-v6.md, "proven inert" line with date and
  test name) — the pre-freeze proof the prereg cites

## Phase 6: Polish & cross-cutting

- [X] T019 [P] CHANGELOG.md `## Unreleased` bullet with compatibility
  markers: observation v6 + global state v2 invalidate all schema-5
  policies/corpora for Gen 2 training; served Gen 1 world unaffected
  (public-voice at write time)
- [X] T020 [P] Update specs/INDEX.md with spec 058
- [X] T021 [P] Doc comment pass: observe.rs/global_state.rs headers
  describe v6/v2 (the 049-style module docs), contract path named
- [X] T022 Full gate: `cargo test --workspace`, config sweeps,
  `vocabulary_flags` with trill/ekekek armed (FR-017, quickstart 10),
  every mutate cycle's predictions recorded for the PR self-review
- [X] T023 Remove BACKLOG.md entries this spec ships (distance
  encoding / schema-bump items if present; shipped-P1-comes-out-at-
  merge rule) and verify `gh pr view --json files` shows only
  product-lane paths before the PR
- [ ] T024 DEFERRED OBLIGATION (post-059, pre-collection): re-run the
  friend-field read sweep against the merged teacher-rework rules and
  re-verify the FR-011 strip list (safe direction only — reads can
  only have been removed); record the re-verify in
  specs/058-gen2-observation-schema/contracts/observation-v6.md
  beside the leak-audit enumeration

## Dependencies & Execution Order

- Phase 2 blocks everything: T002/T003 feed T010/T012; T004 blocks
  T010 (the stated independence exception); T005 after T002.
- US1 internally: T006–T009 red first → T010 → T011–T013.
- US2: T014 red → T015 → T016. T015's v6 side depends on T010's
  constants; its v5 table depends only on T004 — the v5 half can
  start parallel with US1.
- US3: T017 depends on T010 (cells exist); T018 after T017.
- Polish after all stories; T022 is the merge gate.

## Parallel opportunities

- T007, T008, T009 (different test files) once T006's shape is set.
- T014's v5 table + oracle cross-check parallel with US1.
- T019, T020, T021 freely parallel.

## Implementation strategy

MVP = Phase 1–3 (the wall). US2 before any Experiments handback (they
flip readers on the map). US3 before the prereg freeze cites the
proof. Single PR per house practice: push → PR → self-review comment →
CI green → merge; lane = product/.
