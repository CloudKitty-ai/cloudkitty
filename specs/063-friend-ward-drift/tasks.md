# Tasks: Friend-Ward Drift (bounded-detour social bias)

**Input**: Design documents from `/specs/063-friend-ward-drift/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/drift-law.md, quickstart.md

**Tests**: included — Article VI (test-guarded) and CLAUDE.md rule 5
(red-first: every new assertion gets a `scripts/mutate.sh --expect
<prediction>` cycle, prediction declared BEFORE the run, file
committed first). Rule 6: before each story's suite runs, sort its
checks — guards of the change must go red, kept behavior must stay
green; read the must-pass pile, don't only run it.

**Organization**: by user story. All paths relative to the worktree
root (`~/ai/cloudkitty-friend-ward`). Terminology: the spec's "potter"
is the code's `wander` (needs_driven.rs); contract Site 2 carries the
mapping.

## Phase 1: Setup

**Purpose**: a byte-identity baseline to measure FR-002 against.

- [X] T001 Record the pre-change baseline: from `experiments/tools/bc-collect`
      (standalone workspace) at current HEAD, run a short collection
      (`--rollouts 1 --ticks 2000 --seed-base 993001`) on a scratch copy of
      `experiments/world-size-screen-2026-09-24/size100.toml` into the
      scratchpad (`<scratch>/baseline-pre/`); note the HEAD SHA beside it.
      Raws stay in the scratchpad, never under `client/` or committed.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: config surface and the fenced knowledge helper — every
story reads these.

- [X] T002 Add the three `[behavior]` fields to `BehaviorConfig` in
      `crates/cloudkitty-core/src/config/mod.rs`: `friend_ward_drift: bool`
      (`#[serde(default, skip_serializing_if = <bool-false skip>)]` — add a
      `bool_is_false`-style helper beside `f32_is_zero` if none exists),
      `friend_ward_gate: Option<u32>` and `friend_ward_detour: Option<f32>`
      (both `#[serde(default, skip_serializing_if = "Option::is_none")]`),
      with accessor fns defaulting to 10 / 4.0 reading
      `crates/cloudkitty-core/src/config/defaults.rs` constants.
- [X] T003 Add validation in `validate_behavior` in
      `crates/cloudkitty-core/src/config/validate.rs` (existing position 7,
      order list untouched): present gate must be > 0, present detour must
      be finite and >= 0; error strings name `[behavior] friend_ward_gate` /
      `[behavior] friend_ward_detour`. Applies flag on or off.
- [X] T004 Unit tests for T002+T003 in the config test modules: absent keys
      → defaults via accessors; serialization skips all three when
      absent/false (the `GET /config` must-not-grow surface); gate 0 and
      detour -1.0/NaN rejected by name; flag-on with absent dials loads
      10/4.0. Then mutate reds (predictions declared first), e.g.: break an
      accessor default (10→0) expecting the default test's failure; drop a
      validation arm expecting the rejection test's failure.
- [X] T005 Add the kind-fenced freshest-stamp query to `FogView` in
      `crates/cloudkitty-core/src/world.rs` as a SIBLING of `heard_unseen`
      (world.rs:1815, untouched): per unseen roster member, the freshest
      audible stamp within the window whose kind is a law-named want or
      here word; same audibility rule (start-of-tick, age in window).
- [X] T006 Add `nearest_known_friend(ctx) -> Option<(KittyId, Position)>`
      and the `drift_fires` gate check to
      `crates/cloudkitty-core/src/behavior/selection.rs`: visible others
      (any activity state) chained with T005's stamps,
      `min_by_key((manhattan, id))`; fires ⇔ flag on ∧ Some ∧ distance >
      gate accessor.
- [X] T007 Unit tests for T005+T006 in `world.rs` and `selection.rs` test
      modules: want/here stamp qualifies, free-register/Purr/WaitForMe
      never do; a fresher free-register meow neither places the friend nor
      hides that friend's older qualifying stamp (spec edge case); visible
      beats stale stamp by distance only; `(manhattan, id)` tiebreak;
      no-friend → None; gate boundary (distance == gate does NOT fire,
      > gate does). Then mutate reds (predictions first), e.g.: widen the
      kind fence to all kinds expecting the fence test red; flip `>` to
      `>=` on the gate expecting the boundary test red.

**Checkpoint**: config + knowledge land with zero behavior change —
full suite must be green with no golden movement before any story
starts.

---

## Phase 3: User Story 1 — toggleable flag, inert when off (P1) 🎯 MVP

**Goal**: flag-off is byte-for-byte today's engine; flag-on is
accepted config. (After Phase 2, the flag exists but nothing reads it
in behavior — US1 is provable now and stays the standing guard while
US2/US3 land.)

**Independent Test**: full suite green with zero golden/pin re-cuts;
baseline byte-compare; config A/B loads.

- [X] T008 [US1] Run the full flag-off surface: `cargo test` workspace-wide
      — all goldens (`crates/cloudkitty-core/tests/`: determinism.rs,
      evolution_golden.rs, starts_goldens.rs), unit suites, config sweep
      tests. Zero failures, zero re-cuts in `git status`.
- [X] T009 [US1] Byte-identity vs baseline: rebuild bc-collect at this tree,
      re-run T001's exact invocation into `<scratch>/baseline-post/`, and
      byte-compare every output file against `<scratch>/baseline-pre/`
      (`cmp` each array + meta modulo the engine_commit stamp field — list
      any other delta as a failure).
- [X] T010 [US1] Flag-on load test in the config test module: a toml with
      `friend_ward_drift = true` (dials absent, then present) parses,
      validates, and constructs a world; `GET /config`-surface
      serialization of a flag-ON config includes exactly the set fields.
      Mutate red (prediction first): flip the flag's serde default to
      `true` expecting the absent-key default test red specifically — a
      narrow mutation, not a deserialization break that reddens half the
      suite for the wrong reason.

**Checkpoint**: MVP — the mechanism's safety story is proven; US2/US3
add the behavior.

---

## Phase 4: User Story 2 — friend-ward choice among relief options (P2)

**Goal**: the bounded-detour band at the shared priced selection, per
contracts/drift-law.md Site 1.

**Independent Test**: staged two-option scenarios flip with the flag;
gate/no-friend scenarios never flip; score and walk agree.

- [X] T011 [US2] Implement the band re-rank in `priced_nearest_element` in
      `crates/cloudkitty-core/src/behavior/selection.rs` with an optional
      acceptance-cap parameter: drift not firing → today's `(cost, id)`
      path bit-for-bit; firing → band = `cost <= min(min_cost + detour,
      cap?)`, winner by `(manhattan(candidate_pos, friend_pos), cost, id)`,
      f32 via `total_cmp`. Update `sunbeam_worth_walking` to pass
      `sunbeam_reach` as cap; element callers pass none. Callers'
      signatures otherwise unchanged (`seek_element` in
      `crates/cloudkitty-core/src/behavior/needs_driven.rs`,
      `distance_given`/`sleep_travel_distance` in selection.rs keep flowing
      through the one helper — the 004 agreement rule).
- [X] T012 [US2] Unit tests in `selection.rs`/`needs_driven.rs` test
      modules, staged per spec SC-002/SC-003 and the contract: friend-ward
      pick inside band; cheapest wins when the gap exceeds the band;
      B = 0 with distinct costs equals flag-off; single candidate equals
      flag-off; friend within gate / no known friend equal flag-off
      per-context (`identical to flag-off` asserted by running both
      configs through the same context); beyond-reach beam never promoted
      over an in-reach one (cap clause); memory phantom still loses ties
      to a real sighting; walk side pursues the same bowl the score chose
      (extend the existing agreement test shape); flag-ON determinism for
      the band path — identical contexts choose identically with the
      drift firing (FR-010 must not wait for US3).
- [X] T013 [US2] Rule 6 sort + mutate reds for US2 (predictions declared
      first, file committed first), minimum set: (1) remove the cap clause
      expecting the beam-promotion test red; (2) re-rank over ALL
      candidates instead of the band expecting the beyond-band test red;
      (3) key friend distance from `me.pos` instead of `candidate_pos`
      expecting the friend-ward-pick test red; (4) make the drift fire with
      the flag off expecting a flag-off-identity test red. Kept-behavior
      pile (existing selection tests incl.
      `a_bowl_across_a_pond_loses_to_a_farther_dry_bowl_but_wins_alone`,
      `the_bowl_walked_toward_is_the_bowl_the_priced_score_chose`) read
      and re-run green.

**Checkpoint**: US1 re-verified after US2 (T008's surface green again —
flag-off paths bit-identical).

---

## Phase 5: User Story 3 — friend-ward potter (P3)

**Goal**: the idle potter steers per contracts/drift-law.md Site 2,
cadence untouched.

**Independent Test**: staged potter scenarios steer vs stay uniform;
cadence binomial check.

- [X] T014 [US3] Implement the potter arm in `wander` in
      `crates/cloudkitty-core/src/behavior/needs_driven.rs`: drift fires →
      `step_toward(ctx, friend_pos)` (no direction draw); otherwise
      today's uniform draw. The cadence draw in
      `crates/cloudkitty-core/src/behavior/teacher.rs:137-142` is NOT
      touched.
- [X] T015 [US3] Unit tests in `needs_driven.rs`/`teacher.rs` test modules:
      steered step reduces Manhattan distance to the friend (through the
      step rule); friend within gate / no friend / flag off → uniform draw
      path (RNG consumed exactly as today, asserted via rng-state
      comparison — the 062 vacuity lesson); cadence unchanged: over a
      fixed window with the flag on, potter-fire count matches flag-off
      within binomial tolerance (SC-004 — pin n and the tolerance bound
      in the test comment alongside the declared prediction; the bound is
      chosen before the first run, never fitted after); flag-on
      determinism — identical
      contexts choose identically (extend the existing
      `decisions_are_deterministic_for_a_given_context` shape).
- [X] T016 [US3] Rule 6 sort + mutate reds for US3 (predictions first):
      (1) steer unconditionally (ignore the gate) expecting the
      within-gate-uniform test red; (2) consume an RNG draw on the steered
      path expecting the rng-state test red; (3) steer on the cadence draw
      too (change 0.4) expecting the binomial cadence test red.

**Checkpoint**: all three stories independently verified.

---

## Phase 6: Polish & cross-cutting

- [X] T017 Full flag-off re-verification: T008 surface + T009 byte-compare
      re-run at the final tree (baseline-pre unchanged); `git status
      --ignored` clean of stray fixtures.
- [X] T018 Flag-on smoke per quickstart.md §5: scratch size100 toml with
      the flag on (scratchpad only — knob-on tomls NEVER under
      `experiments/`), bc-collect 1×2000 ticks; arrays well-formed, run
      completes. Delete the scratch config after.
- [X] T019 Local gate: `cargo fmt` && `cargo clippy --all-targets` &&
      `cargo test` from the workspace root, all green.
- [X] T020 Doc touch: config field doc-comments reference spec 063 and the
      drift-law contract; CHANGELOG Unreleased entry (public voice at
      write time) in `CHANGELOG.md`.
- [X] T021 Verify spec SC checklist against reality (SC-001..SC-006) and
      record the mutate-red ledger (every prediction + outcome) in the PR
      body draft; any vacuous or wrong-reason red is unresolved debt, not
      a pass.

---

## Dependencies & execution order

- Phase 1 (T001) first — the baseline must predate every tree change.
- Phase 2: T002 → T003 → T004 (same files, sequential); T005 → T006 →
  T007 (T005 parallel-safe with T002/T003 — different files).
- US1 (T008–T010) after Phase 2; blocks nothing after it passes once,
  but re-runs at each later checkpoint.
- US2 (T011–T013) and US3 (T014–T016) both depend only on Phase 2 +
  US1's first pass. T011 and T014 touch different functions; T011/T012
  (selection.rs) and T014/T015 (needs_driven.rs wander) can proceed in
  parallel if careful — needs_driven.rs test module is shared, so
  sequential is safer solo: US2 then US3.
- Phase 6 last; T017/T018 may run in parallel, T019 before T020/T021.
- mutate.sh rule: never edit the tree mid-cycle; commit before each
  cycle (revert-guard: stash route for dirty files).

## Implementation strategy

MVP = Phase 1 + 2 + US1: a landed, validated, provably-inert flag.
US2 is the owner's ruled example and ships second; US3 completes her
ruling. Each checkpoint re-proves flag-off identity, so a stop at any
checkpoint leaves main-mergeable work.
