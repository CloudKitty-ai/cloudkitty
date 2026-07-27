# Tasks: Need→Relief Mapping — One Source of Truth for the Baseline Cat

**Input**: Design documents from `/specs/019-need-relief-mapping/`

**Prerequisites**: plan.md, spec.md, research.md (D1–D5), data-model.md, quickstart.md

**Tests**: No new test tasks — the spec's bar is the existing suite passing with zero assertion changes (FR-005) plus the four-way byte comparison (FR-006). The compile-time guard *is* the deliverable (exhaustive matches), not a test. New coverage only if something proves cheap and additive during implementation.

**Organization**: Grouped by the spec's three user stories. Small feature: one new ~70-line module, three rewired functions, heavy verification.

## Format: `[ID] [P?] [Story?] Description`

## Phase 1: Setup

**Purpose**: Freeze the pre-refactor baseline before any code moves.

- [X] T001 Capture baseline outputs from a `c6fbeae` worktree per quickstart.md §2: build the baseline `kitty-eval`, run the suite-mode and certification-mode commands, store the four outputs; record exit codes. Foreground, generous timeout.

---

## Phase 2: Foundational

**Purpose**: The one authoritative definition both stories consume.

- [X] T002 Create `crates/cloudkitty-core/src/behavior/relief.rs`: the crate-internal `ReliefSource` enum (five shapes per data-model.md — `Element { kind: ElementType, use_it: Action }`, `Sunbeam`, `Playmate`, `Friend`, `InPlace { use_it: Action }`) and the exhaustive `impl NeedKind { pub(crate) fn relief(self) -> ReliefSource }` with the six pairings. Module docs state the invariant this definition now provides structurally (score/walk/grab agreement on the pairing) and name the shared helpers that carry within-shape agreement (`sunbeam_worth_walking`, `priced_nearest_element`, `adjacent_playmate`, `play_action_with`) — the replacement FR-007 requires for the retired mirror comments. Register `mod relief;` in `crates/cloudkitty-core/src/behavior/mod.rs`. `cargo build -p cloudkitty-core` green (the new code may be temporarily unused).

**Checkpoint**: the definition exists — consumer rewiring can begin.

---

## Phase 3: User Story 1 — Score and walk cannot disagree (P1) 🎯 MVP

**Goal**: `distance_given` and `pursue` derive the need→relief pairing from `relief()`; no independent encoding remains in either.

**Independent Test**: full workspace suite green with zero assertion changes; four-way byte comparison vs the T001 baseline identical (quickstart §1–2).

- [X] T003 [P] [US1] Rewire `distance_given` in `crates/cloudkitty-core/src/behavior/selection.rs` (baseline lines 109–131) to `match need.relief()` with the five shape arms carrying the **current bodies untouched** (data-model.md consumer table: `Element` → `priced_nearest_element(kind).map(cost)`, `Sunbeam` → `sleep_travel_distance(ctx)`, `Playmate` → `play_travel_distance`, `Friend` → `nearest_friend` + `priced_travel`, `InPlace` → `Some(0.0)`). Retire the mirror comments per FR-007: reword selection.rs's "the mirror the 004 review demanded" (baseline ~179–180) and "Mirrors `pursue`'s sleep arm exactly" (~188–190) to point at the invariant now documented on `relief()` — the helpers themselves stay exactly where they are.
- [X] T004 [P] [US1] Rewire `pursue` in `crates/cloudkitty-core/src/behavior/needs_driven.rs` (baseline lines 135–192) to `match choice.need.relief()` with the current arm bodies moved untouched: `Element { kind, use_it }` → `seek_element(ctx, kind, use_it)`; `Sunbeam` → the existing standing-on short-circuit + `sunbeam_worth_walking` match; `Playmate` → `selection::play_action_with(ctx, choice.playmate)`; `Friend` → the existing free-friend seek with `(manhattan, id)` min, etiquette wait, and `Idle` fallback; `InPlace { use_it }` → `use_it`. Every inline comment moves with its body, with one FR-007 exception: the sleep arm's "so what gets chosen and what gets walked can never disagree" comment (baseline needs_driven.rs:151–153) is reworded to reference the invariant now documented on `relief()`, same treatment as the selection.rs pair in T003.
- [X] T005 [US1] Checkpoint verification: `cargo test --workspace` green; rebuild release and run the four-way byte comparison vs the T001 baseline (quickstart §2) — all four identical before proceeding.

**Checkpoint**: US1 delivered — the score/walk pairing is single-sourced and proven unchanged.

---

## Phase 4: User Story 2 — Opportunistic grabbing consumes the same source (P2)

**Goal**: `take_what_is_here` holds no per-need copies; the emergency ladder's order is explicit and load-bearing.

**Independent Test**: same instruments — workspace suite green, four-way byte comparison identical.

- [X] T006 [US2] Rewrite `take_what_is_here` in `crates/cloudkitty-core/src/behavior/needs_driven.rs` (baseline lines 93–130): declare `const OPPORTUNISM_LADDER: [NeedKind; 4] = [Eat, Drink, Sleep, Play];` beside it (the "emergency ladder" comment moves onto the constant), iterate it, and per rung `match need.relief()`: `Element { kind, use_it }` → `needs.get(need) >= detour` + adjacency over `elements_of(kind)` → `use_it`; `Sunbeam` → threshold + standing-on (`element_at(me.pos)` is a Sunbeam) → `Sleep { with: None }` (its "too good to waste" comment moves along); `Playmate` → threshold + `selection::adjacent_playmate` → `play_with` (comment moves along); `Friend` / `InPlace` → skip (not opportunistic — exactly today's behavior; Cuddle and Bath are absent from the current ladder). Threshold comparison count, predicate order, and rung order preserved exactly.
- [X] T007 [US2] Checkpoint verification: `cargo test --workspace` green; four-way byte comparison vs T001 baseline identical (this run also covers `playful`, which shares `take_what_is_here` — quickstart §2 note).

**Checkpoint**: US2 delivered — all three consumers derive from the single definition.

---

## Phase 5: User Story 3 — Adding or changing a need touches one site (P3)

**Goal**: The compile-forced one-site property is demonstrated and recorded; nothing lands.

**Independent Test**: quickstart §4's recorded walkthrough shows the correspondence costs exactly one `relief()` arm, with omission a compile error.

- [X] T008 [US3] Run the quickstart §4 walkthrough: temporarily add a hypothetical `NeedKind` variant, record which sites the compiler forces (expected: `relief()` plus any pre-existing engine-side exhaustive `NeedKind` matches outside this feature's scope — enumerate them honestly), confirm the behavior-stack correspondence costs exactly the one `relief()` arm, revert. Record the before/after edit-site lists and the compiler-error sites in `specs/019-need-relief-mapping/quickstart.md`; working tree clean afterward (FR-008: nothing lands).

**Checkpoint**: all three stories delivered.

---

## Phase 6: Polish & Final Verification

- [X] T009 Final sweep: quickstart §3 single-definition review (grep for the retired mirror comments returns nothing; no need→resource pairing outside `relief()`); `cargo fmt --all` + `cargo clippy --workspace --all-targets -- -D warnings` green; final `cargo test --workspace` + four-way byte comparison; fill every quickstart "Record" block; remove the baseline worktree; mark BACKLOG "Refactoring targets" item 2 shipped; mark all tasks `[X]` in this file.

---

## Dependencies & Execution Order

- T001 ⊥ T002 (independent; T001 listed first to freeze the baseline).
- T003 [P] T004 — different files, both depend only on T002; land together or in either order, then T005 gates.
- T006 depends on T005 (checkpoint discipline) and touches the same file as T004.
- T008 after T007 (walkthrough runs against the finished structure).
- T009 last.

### Parallel Opportunities

T001 with T002; T003 with T004. Everything else is sequential checkpoint discipline — appropriate for a refactor whose bar is bit-identity.

## Implementation Strategy

US1 is the MVP: it closes the score/walk drift channel the 004 review
first demanded a mirror for, converting a comment-enforced invariant into
a structural one. Each story ends at a fully-verified checkpoint (suite +
four-way bytes), so stopping after any story leaves the tree green,
verified, and strictly better than before. The byte comparison runs three
times (T005, T007, T009) — after each behavioral surface is touched.
