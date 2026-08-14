---

description: "Task list for Shared Sunbeam Warmth"
---

# Tasks: Shared Sunbeam Warmth

**Input**: Design documents from `specs/031-sunbeam-warmth/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included — spec FR-009 requires every acceptance scenario guarded
by a test (Article VI).

**Organization**: Grouped by user story. US1 (conduction) is the feature;
US2 (edges) makes it safe. Both are P1 and share the one changed function,
so the phases are sequential by design — there is no parallel surface in a
six-line engine change.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no incomplete-task
  dependency) — unused here; every task touches `action.rs`
- **[Story]**: US1 / US2; foundational and polish carry no label

## Path Conventions

Rust workspace. All code and tests in
`crates/cloudkitty-core/src/action.rs` (the house pattern keeps
action-effect tests in the same file's test module).

---

## Phase 1: Setup

No setup tasks — existing workspace, single-file change, no new
dependencies or scaffolding.

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T001 In `crates/cloudkitty-core/src/action.rs` `apply_sleep_relief`
  (~line 777), hoist the `mutual` predicate (currently computed for the
  cuddle tier at ~line 797) above the Sleep-rate choice, so one evaluation
  feeds both the rate arm and the cuddle tier (plan "Structure Decision",
  research D2). Pure refactor: behavior byte-identical, existing tests
  pass unchanged.

**Checkpoint**: `cargo test -p cloudkitty-core` green with zero behavior
change — the hoist is invisible.

---

## Phase 3: User Story 1 - Warmth conducts through the pile (Priority: P1) 🎯 MVP

**Goal**: A sleeper whose mutual partner stands on a sunbeam tile sleeps at
`sleep_relief_sunbeam`; either-on-beam covers both sleeping partners.

**Independent Test**: Hand-built pile, one tile holding a beam; assert
per-tick Sleep relief equals `sleep_relief_sunbeam` for each Sleeping
partner, on-beam or off (quickstart Scenario 1).

### Tests for User Story 1

- [X] T002 [US1] Add conduction tests to the `action.rs` test module
  (extend the `sleeping_in_a_sunbeam_is_more_restful` /
  `cosleep_pays_the_tier…` pattern), covering spec US1 scenarios 1–4:
  sleeper with beam-standing Sleeping partner gets the sunbeam rate;
  same with a beam-standing **Resting** partner (source per D1); both
  sleeping, beam under one → both at the sunbeam rate; beam-Resting
  partner itself receives NO sleep relief; beam expiry drops the rate on
  the next serviced tick. Write to fail first (the conduction arm does not
  exist yet).

### Implementation for User Story 1

- [X] T003 [US1] Implement the conduction arm in `apply_sleep_relief` in
  `crates/cloudkitty-core/src/action.rs`: `partner_warm = mutual AND
  world.element_at(world.kitty(partner).pos) is a Sunbeam` (research D3 —
  a failed lookup is simply false); `relief = sleep_relief_sunbeam if
  in_sunbeam || partner_warm else sleep_relief`. Depends on T001, T002.

**Checkpoint**: T002's tests pass; US1 is fully functional.

---

## Phase 4: User Story 2 - The rule's edges hold (Priority: P1)

**Goal**: One hop, no stacking, no drip-tier conduction, no awake
receiver, every other channel untouched.

**Independent Test**: One test per edge against hand-built world states
(quickstart Scenario 2).

### Tests for User Story 2

- [X] T004 [US2] Add edge tests to the `action.rs` test module, covering
  spec US2 scenarios 1–5: no chaining (A–B–C, beam under C → A plain
  rate); no stacking (both partners on beams → exactly one sunbeam rate
  each); drip-tier partner (on a beam but neither Sleeping nor Resting)
  conducts nothing; solo sleepers on and off beams at exactly today's
  rates; and a conduction pile's Cuddle relief is exactly the mutual tier
  it was before this feature (FR-007). These are assertions against the
  T003 implementation — expected to pass if the arm is correct; any
  failure is a bug in T003, fixed there.

**Checkpoint**: The full new test cluster and every pre-existing
cosleep/sunbeam/duet test pass together.

---

## Phase 5: Polish & Cross-Cutting

- [X] T005 Run the regression gates (quickstart Scenarios 3–4):
  `cargo test -p cloudkitty-core` and `cargo test -p cloudkitty-rl`
  unchanged suites all green (SC-003/SC-004 — the rule is inert where it
  does not fire).
- [X] T006 Add a shared-sunbeam-warmth line to `CHANGELOG.md` under
  `## Unreleased` (engine-rules change, no compatibility marker — no
  schema, stamp, or RNG-sequence move; note the re-baseline rides the
  pre-generation schedule). Do NOT tag.
- [X] T007 `cargo fmt --all -- --check` and
  `cargo clippy --workspace --all-targets -- -D warnings` clean.

---

## Dependencies & Execution Order

- **T001** (hoist) first — it is the surface T003 lands on.
- **T002** (failing tests) before **T003** (implementation) — TDD per the
  house pattern.
- **T004** after T003 (asserts against the implemented arm).
- **T005–T007** last.

Strictly sequential: every task edits or gates the same file. No [P]
opportunities, by the nature of the change.

## Implementation Strategy

MVP is T001–T003 — the rule working with its core scenarios guarded. T004
completes the safety envelope the spec demands before this can merge
(FR-009 covers US2's negatives, not just US1's positives — both stories
are P1 and both precede the PR). T005–T007 are the ship gates.
