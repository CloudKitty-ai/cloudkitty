# Tasks: Teacher sleep rule reads the floor

**Input**: Design documents from `/specs/057-teacher-sleep-floor/`

**Prerequisites**: plan.md, spec.md, research.md (D3–D5), data-model.md, contracts/sleep-pressure.md

**Tests**: REQUIRED — house red-first rule (CLAUDE.md rule 5): every fixture is written failing first, and every assertion gets its mutate red before it counts.

**Organization**: three P1 stories; US1 carries the new logic, US2 guards the unchanged warm path, US3 is the byte pin.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: capture the comparison baseline before any code moves.

- [X] T001 Capture the floor-0 baseline: run `kitty-eval --brain needs_driven --config evals/anchor-b3.toml` at the branch point (705290d) and save the output under the scratchpad for T012's exact-match diff (baseline is reproducible from git; scratch copy is a convenience, not an artifact)

---

## Phase 2: Foundational

**Purpose**: the predicate both stories score against.

- [X] T002 Add `warm_option_in_play(ctx)` to `crates/cloudkitty-core/src/behavior/selection.rs` composing the on-beam check (`world.element_at`), `warm_friend_beside` (T092/031), and `sunbeam_worth_walking` (D4); doc comment names contract P3 (no new reads) and the deliberate exclusion of the cuddle-cosleep walk

**Checkpoint**: helper compiles with a unit test per branch of the disjunction.

---

## Phase 3: User Story 1 - A worthless nap loses (Priority: P1) 🎯 MVP

**Goal**: floored pressure + zero-pressure skip; the nap-regrow loop cannot start.

**Independent Test**: spec story 1 scenarios on floor-15 fixtures.

### Tests (write first, watch them fail)

- [X] T003 [US1] Failing fixture `sleep_floor_worthless_nap_loses`: floor 15, sleep 18, no warm option, competing need 8 with its relief ADJACENT (distance 0, so no travel/exposure cost erodes the 8) → the competing need wins (pressure 3 loses) in `selection.rs` test module
- [X] T004 [P] [US1] Failing fixture `sleep_floor_at_floor_no_scene`: floor 15, sleep 15 (at floor), no warm option, all else quiet → no Sleep action this tick, in `needs_driven.rs` test module
- [X] T005 [P] [US1] Failing fixture `sleep_floor_under_floor_no_renap`: floor 15, sleep 12 (under floor, beam expired mid-scene precondition), no warm option → no re-nap decision (need dynamics are 056's engine law, NOT asserted here), in `needs_driven.rs` test module
- [X] T006 [P] [US1] Failing fixture `sleep_floor_discount_not_ban`: floor 15, sleep 40, no warm option, nothing else to do → still naps (D2: discount, never ban) in `selection.rs` test module

### Implementation

- [X] T007 [US1] Effective-pressure binding in `scored()` (D3): `max(need − floor, 0)` for Sleep when `!warm_option_in_play`, urgency riding on the same binding, in `crates/cloudkitty-core/src/behavior/selection.rs`
- [X] T008 [US1] Zero-pressure skip (D5): return `None` when `floor > 0.0 && !warm && effective == 0.0`, mirroring `action.rs:925`'s gate shape, in `crates/cloudkitty-core/src/behavior/selection.rs`

**Checkpoint**: T003–T006 green; rule 6 sort — these four are the guards of the change and MUST have been red first.

---

## Phase 4: User Story 2 - A warm option keeps the full need (Priority: P1)

**Goal**: the warm path is provably unchanged.

**Independent Test**: floor-15 warm fixtures decide identically to floor-0.

### Tests

- [X] T009 [US2] Fixtures ×3 (`sleep_floor_warm_*`): floor 15, sleep 18 with (a) on-beam, (b) beam within `sunbeam_reach`, (c) settled partner warm beside — each scores pressure 18 and matches the floor-0 decision, in `selection.rs` test module
- [X] T010 [US2] Kept-behavior re-read (CLAUDE.md rule 6): re-read the existing sleep tests in `needs_driven.rs` and `selection.rs` (opportunism rung, pursue arm, T092, cosleep routing) and confirm each still asserts the behavior this spec promises not to move; ALSO confirm `warm_option_in_play` reads only `ctx.world`/`ctx.me`/`ctx.config` (FR-005, doctrine rule 5); run the pile green; report any vacuous must-fail found (rule 3 if pre-existing)

**Checkpoint**: warm path pinned by fixtures, not by reading the diff.

---

## Phase 5: User Story 3 - Floor 0 is today, byte for byte (Priority: P1)

**Goal**: FR-004/P1 — the pin that makes this mergeable.

**Independent Test**: exact-match, not statistics.

- [X] T011 [US3] Run the spec 056 floor-0 regression pin and the full `cargo test -p cloudkitty-core`; all green, counts reported
- [X] T012 [US3] Cert leg exact-match: re-run T001's command on the branch head and diff against the baseline — empty diff required (SC-001, validation (a) of the 006 protocol)

---

## Phase 6: Polish & Cross-Cutting

- [X] T013 Mutate reds (SC-005, one cycle per assertion family, prediction declared per run): (a) pressure binding back to raw `need` → predict T003 red, floor-0 pile green; (b) skip gate deleted → predict T004 red; (c) warm predicate short-circuited to `true` → predict T003/T006 red family — via `scripts/mutate.sh --expect` in the worktree
- [X] T014 CHANGELOG.md `## Unreleased` one-liner (public-voice at write time; compatibility marker: behavior change only at `sleep_floor_off_beam > 0`, served config unaffected)
- [X] T015 Run quickstart.md end-to-end and mark task checkboxes; then notify Experiments the acceptance items are on the branch (their read: SC-002..004 legs)

---

## Execution deviations (recorded at completion, 2026-09-21)

- T001/T012: the anchor config lives at
  `experiments/fog-gen1-cert/anchor-b3.toml` (not `evals/`); same leg,
  corrected path. Result: 10 seeds, delta +0.0000, empty JSON diff.
- T004/T005 stage floor 25 (the handover's tier value), not 15, with
  sleep 25/22: below pressure 20 `decide_action`'s potter gate wanders
  40% of ticks, so a floor-15/need-15 fixture was green by RNG luck —
  a wrong-reason green caught before implementation. The fixtures also
  stage one beam OUT OF REACH (a beam-less world takes the
  fog-exploration rung and never reaches the nap) and make sleep the
  relief-recency tie-winner so the skip gate, not a lucky tie, is what
  the tests pin. All three change-guards were observed red before
  T007/T008.
- T013: three cycles, all RED CONFIRMED with predictions matched —
  (a) raw-need term → worthless_nap_loses red; (b) gate disabled →
  exactly the two gate fixtures red (the tie-boost proved the gate
  load-bearing); (c) warm predicate always-true → worthless_nap_loses
  + gate fixtures + warm_option_branches red.

## Dependencies & Execution Order

- Phase 1 (T001) first — the baseline must predate the code change.
- Phase 2 (T002) blocks T003+ (fixtures reference the predicate).
- US1 tests (T003–T006) before US1 implementation (T007–T008); T004/T005/T006 parallel after T003 establishes the fixture shape.
- US2 (T009–T010) after T007–T008 (it pins the implemented state); could draft fixtures earlier but they only mean something against the new code.
- US3 (T011–T012) last among stories — the pin covers the whole diff.
- Polish (T013–T015) after all stories; T013 before T014/T015 (a failed red reopens implementation).

## Implementation Strategy

MVP is US1, but this feature merges whole or not at all: US3's byte pin and T013's reds are merge gates, not nice-to-haves. Single-developer sequential is the intended path; the only real parallelism is inside the fixture batches (T004–T006, and the three cases of T009).
