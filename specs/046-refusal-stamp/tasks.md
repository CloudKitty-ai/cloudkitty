# Tasks: Refusal Stamp

**Input**: Design documents from `/specs/046-refusal-stamp/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/refusal-event.md, quickstart.md

**Tests**: red-first is house law (CLAUDE.md rules 5/6, Constitution
Article VI) — every assertion gets its exact-bug injection cycle,
recorded in `specs/046-refusal-stamp/redden-list.md`. Test tasks are
listed before their implementation tasks; where a test must compile
against a new type, write the test red (assertion-red, not
compile-red) as soon as the type exists.

**Organization**: US1 = per-tick refusal attribution (P1, the feature);
US2 = ring sized for the baseline window (P2); US3 = additive delivery,
nothing else moves (co-P1, the launch bar).

## Phase 1: Setup

- [ ] T001 Create `specs/046-refusal-stamp/redden-list.md` with the house columns (cycle, assertion, injected bug, predicted failure, observed red, restored green) ready to receive every rule-5 cycle in this feature

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 Add `RefusalEvent` struct (`kitty_id: KittyId, proposed: Action, tick: u64`; derives per data-model.md, `Copy` iff `Action: Copy`) and `pub type RefusalLog = EventLog<RefusalEvent>` in `crates/cloudkitty-core/src/events.rs`
- [ ] T003 Add `EventLog::set_capacity(&mut self, capacity: usize)` (floor 1, trim oldest-first when over) in `crates/cloudkitty-core/src/events.rs`, with unit test `set_capacity_trims_oldest_first_and_floors_at_one` (red-first: assert on the kept ticks, inject a trim-newest bug)
- [ ] T004 Add `refusal_retention: usize` to `EventsConfig` in `crates/cloudkitty-core/src/config/mod.rs` with `#[serde(default = "default_refusal_retention", skip_serializing_if = "is_default_refusal_retention")]`, the skip helper keyed to the default VALUE (043/045 precedent), `Default` impl updated, `Copy` retained; `default_refusal_retention() = 4000` in `crates/cloudkitty-core/src/config/defaults.rs`
- [ ] T005 Add the `("[events] refusal_retention", ...)` row to `validate_events` in `crates/cloudkitty-core/src/config/validate.rs` (spec 020 D2 shape); test: retention 0 rejected with the row-shaped message, 1 accepted (red-first: drop the row, predict the miss) — covers US2 acceptance scenario 3
- [ ] T006 Add `refusal_log: RefusalLog` to `World` in `crates/cloudkitty-core/src/world.rs` with `#[serde(default)]`; initialize from `config.events.refusal_retention` in `World::generate`; fix every struct-literal site the compiler enumerates (E0063), including the `world.rs:163` default block (capacity-0 ring there, matching the sibling logs)

**Checkpoint**: `cargo build --workspace` green; no behavior change yet.

## Phase 3: User Story 1 — Per-tick refusal attribution (P1) 🎯 MVP

**Goal**: every validation refusal recorded (kitty, proposal verbatim, tick), served at `/events/refusal`.

**Independent test**: drive a known refusal (second-in-turn-order kitty proposing a move into a just-occupied cell), read the event back from the ring, then over the endpoint.

- [ ] T007 [US1] Write unit test `a_refused_proposal_is_stamped_with_kitty_proposal_and_tick` in `crates/cloudkitty-core/src/world.rs` tests: forced refusal (occupied-cell move) records exactly one event with the verbatim proposal and tick; a chosen Idle records nothing (scenario US1-1/US1-2). Red-first: implement recording, then invert the predicate to `validated == proposal` and predict the false stamp
- [ ] T008 [US1] Write unit test `a_legal_proposal_overridden_by_duration_enforcement_is_not_a_refusal` in `crates/cloudkitty-core/src/world.rs` tests: kitty inside a scene minimum proposes a LEGAL different action (research R1's nuance — e.g. a legal Move elsewhere), duration enforcement continues the scene, no event recorded (scenario US1-3). Red-first: move the recording after `enforce_durations` keyed on the enforced action and predict the false stamp
- [ ] T009 [US1] Implement recording in `run_applied_phases_from_decisions` in `crates/cloudkitty-core/src/world.rs`: after `let validated = action::validate(...)`, `if proposal != Action::Idle && validated == Action::Idle { self.refusal_log.record(RefusalEvent { kitty_id, proposed: proposal, tick: self.tick }) }` — before `enforce_durations`, inside the turn-order loop (ring order = turn order, spec edge case)
- [ ] T010 [US1] Write test `a_refused_partnered_proposal_carries_the_asked_partner` in `crates/cloudkitty-core/src/world.rs` tests: refused `Play { target: Some(kitty) }` event's `proposed` names the partner (SC-002, scenario US1-4). Red-first: swap the recorded field to the enforced action and predict the lost target
- [ ] T011 [US1] Write driver-parity test `both_tick_drivers_stamp_identical_refusal_streams` in `crates/cloudkitty-core/tests/joint_action_parity.rs` (or its established parity harness): same seeded world + identical decisions through the behavior loop and `tick_with_proposals`, refusal streams byte-equal (scenario US1-5, FR-002)
- [ ] T012 [US1] Write serialization emit-proof test `a_refusal_event_serializes_the_proposal_verbatim` in `crates/cloudkitty-core/src/events.rs` tests: record a REAL event from a driven world (no hand-written fixture — rule 5's third lie), pin its JSON, round-trip it (FR-008 layer 2; pins the contract's wire shape)
- [ ] T013 [US1] Serve the ring: `refusals: Arc<Vec<RefusalEvent>>` in the snapshot state in `crates/cloudkitty-server/src/sim_task.rs` (from `world.refusal_log.to_vec()`), handler `get_refusals` in `crates/cloudkitty-server/src/api.rs`, route `/events/refusal` in `crates/cloudkitty-server/src/lib.rs` — mirror `get_activity_ends` exactly (oldest first, full ring)
- [ ] T014 [US1] Server test for the endpoint in `crates/cloudkitty-server/src/api.rs` (or the established server-test home): a world driven into a refusal serves a non-empty array whose entries match the ring; a fresh world serves `[]` (scenario US1-6 — the zero is only readable because the emit-proof exists, F-029)

**Checkpoint**: US1 independently deliverable — the census could run against a lab box now.

## Phase 4: User Story 2 — Ring sized for the baseline window (P2)

**Goal**: retention knob honored, default holds ≥15,000 ticks at ~0.23 refusals/tick.

**Independent test**: small-retention world overflows correctly; default maths documented in the test.

- [ ] T015 [P] [US2] Write test `the_refusal_ring_honors_configured_retention` in `crates/cloudkitty-core/src/world.rs` tests: retention 3, drive ≥5 refusals, ring holds the newest 3 (scenario US2-2; the generic EventLog trim is already covered — this pins the CONFIG WIRING from `refusal_retention` to the ring, red-first: hardcode `RefusalLog::new(1000)` in `generate` and predict the wrong cap)
- [ ] T016 [P] [US2] Write test `default_retention_covers_the_baseline_window` in `crates/cloudkitty-core/src/config/mod.rs` tests: `default_refusal_retention() >= (15_000 as f32 * 0.23) as usize` with the sizing math in the assertion message (scenario US2-1, FR-004 — the arithmetic pin that reddens if someone shrinks the default below the window)

**Checkpoint**: sizing contract pinned.

## Phase 5: User Story 3 — Additive delivery: nothing else moves (co-P1)

**Goal**: byte-identical dynamics, stamp unmoved, pre-046 saves resume at configured capacity.

**Independent test**: quickstart steps 3–4.

- [ ] T017 [US3] Add `refusal_retention` to `roam_cell_stays_out_of_the_default_serialization` in `crates/cloudkitty-core/src/config/mod.rs` tests (red-first: delete the skip attribute, predict the leak — the test's own documented discipline) and a parse-equality arm: config with `refusal_retention = 4000` explicit == config with it absent (scenario US3-3, SC-004)
- [ ] T018 [US3] Write resume test `a_pre_046_save_resumes_with_the_configured_refusal_capacity` in `crates/cloudkitty-core/tests/snapshot_resume.rs`: serialize a world, DELETE the `refusal_log` key from the JSON (that is what a pre-046 save is), load via `persist::load_and_validate`, assert ring empty AND capacity honors config after re-stamp — drive refusals past 1 and assert the ring holds >1 (scenario US3-2 + research R3; red-first is T019's cycle: without the re-stamp this test is the predicted red)
- [ ] T019 [US3] Implement the capacity re-stamp in `crates/cloudkitty-server/src/persist.rs` `load_and_validate`: after the fingerprint check, `world.refusal_log.set_capacity(config.events.refusal_retention)`, with the retention-is-configuration comment citing the behavior re-stamp precedent (research R3). T018 goes green here — its pre-implementation red IS the rule-5 cycle, record it
- [ ] T020 [US3] Verify the evolution golden passes UNREGENERATED (`crates/cloudkitty-core/tests/evolution_golden.rs`) and run the full suite; READ THE COUNT and record it in the redden-list header (SC-003, scenario US3-1 — the recording site only observes)
- [ ] T021 [P] [US3] Write RL-surface test `the_refusal_stamp_never_moves_the_mask` in `crates/cloudkitty-rl/src/mask.rs` tests if any config/world plumbing touched the rl crate's inputs; if the rl crate provably reads neither `EventsConfig` nor `refusal_log`, record that as the no-honest-red caveat in the redden-list instead of writing a vacuous test (scenario US3-4, rule 6)

**Checkpoint**: launch bar met — dynamics untouched, additivity proven.

## Phase 6: Polish & Cross-Cutting

- [ ] T022 [P] Run quickstart step 2 (bounded live boot via `perl -e 'alarm 12; exec @ARGV'`, macOS-safe) against a lab config; confirm `/events/refusal` populates and paste the first real payload into `specs/046-refusal-stamp/redden-list.md` notes as the live emit-proof
- [ ] T023 [P] Add the refusal-stamp one-liner to `## Unreleased` in `CHANGELOG.md` (changelog practice: marker + one line as the arc merges)
- [ ] T024 [P] Document the sibling-ring capacity gap (distress/activity retention edits silently lose to the persisted capacity on resume — research R3, reported not fixed) in the PR body draft; keep it OUT of code changes (CLAUDE.md rule 3)
- [ ] T025 Full-suite close-out: `cargo fmt --check`, CI's exact clippy (`cargo clippy --workspace --all-targets -- -D warnings`), `cargo test --workspace`; READ THE COUNT, compare to the pre-branch baseline count, record both in the redden-list header

## Dependencies

- Phase 2 → everything (types/config/field are load-bearing).
- US1 (T007–T014): T009 needs T002/T006; T013 needs T009; T014 needs T013.
- US2 (T015–T016): needs Phase 2 only — parallel to US1 after T006, [P] within phase.
- US3 (T017–T021): T017 needs T004; T018–T019 need T003/T006; T020 needs T009 (the recording exists to be proven inert); T021 anytime after T004/T006.
- Polish after all stories.

## Parallel example

After T006: {T007+T008 (US1 tests), T015+T016 (US2), T017 (US3 stamp guard)} touch disjoint test surfaces and can proceed in any interleaving; T009 serializes behind T007/T008.

## Implementation strategy

MVP = Phases 1–3 (US1): the census could already consume a lab box.
US2/US3 are small and land in the same PR — the launch bar (US3) is
non-negotiable before merge, so the PR ships all phases; the phase
split exists for red-first ordering, not staged delivery.
