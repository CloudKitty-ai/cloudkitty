# Tasks: No Stale Re-Proposal

**Input**: Design documents from `/specs/048-no-stale-reproposal/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/stale-scene-rule.md, quickstart.md

**Tests**: red-first is mandatory house practice (CLAUDE.md rules 5/6; constitution Article VI). Every new guard's red cycle is predicted, run with `--no-fail-fast`, and recorded in `specs/048-no-stale-reproposal/redden-list.md`. Commit before every mutate-then-revert cycle (checkout-trap rule).

**Organization**: by user story; the one-line behavioral edit lands in US1 and US2/US3 ride the shared predicate (FR-003 full coverage), so US2/US3 are guard-and-verify phases.

## Phase 1: Setup

- [ ] T001 Create `specs/048-no-stale-reproposal/redden-list.md` scaffold (cycle table: prediction / observed / restore / count re-read), noting the 047 `--no-fail-fast` standard

---

## Phase 2: Foundational (blocking prerequisite)

**Purpose**: the shared predicate exists before any story consumes it (plan D1, FR-002)

- [ ] T002 Factor `World::counterpart_gone(&self, kitty_id) -> bool` out of `prune_dead_activity`'s match in `crates/cloudkitty-core/src/world.rs` (behavior-identical: prune becomes early-outs + `if self.counterpart_gone(id) { self.end_activity(id) }`); full suite green, COUNT READ
- [ ] T003 Refactor-integrity cycle in `specs/048-no-stale-reproposal/redden-list.md`: mutate one arm of the factored predicate (duet arm → `false`), predict which EXISTING prune witnesses red, run `cargo test --workspace --no-fail-fast`, record, restore, re-read count (proves the factoring kept the guards pointed at the predicate)

**Checkpoint**: predicate shared and guarded — story phases can begin

---

## Phase 3: User Story 1 - The critter got away; do something real (P1) 🎯 MVP

**Goal**: a cat whose critter-play scene lost its critter makes a fresh decision the same tick — no stale proposal, no idle tick, no refusal row.

**Independent Test**: stage mid-play cat + moved/expired critter, advance one turn: real action, no refusal row (quickstart §1).

### Tests (red-first — write, predict red, then implement)

- [ ] T004 [US1] Behavior guard in `crates/cloudkitty-core/src/behavior/needs_driven.rs` tests: cat mid-`Playing{Element}`, critter no longer adjacent in snapshot → `finish_what_you_started` returns `None` (red until T008)
- [ ] T005 [US1] Behavior guard, expired variant in `crates/cloudkitty-core/src/behavior/needs_driven.rs` tests: critter absent from world entirely → `None` (red until T008)
- [ ] T006 [US1] Must-stay-green pin in `crates/cloudkitty-core/src/behavior/needs_driven.rs` tests: critter still adjacent → continuation returned exactly as today (FR-004; sorted per CLAUDE.md rule 6 BEFORE T008 runs)
- [ ] T007 [US1] E2E guard in `crates/cloudkitty-core/src/world.rs` tests: staged world, dead critter scene at tick boundary, one `tick` → the cat's applied action is real (not Idle) AND no refusal row stamped that tick (FR-007/SC-002; red until T008)

### Implementation

- [ ] T008 [US1] Consult the predicate in `finish_what_you_started` in `crates/cloudkitty-core/src/behavior/needs_driven.rs`: after the governing-need short-circuits, `counterpart_gone` on `ctx.world` → return `None` (plan D2); T004/T005/T007 flip green, T006 stays green, suite green COUNT READ
- [ ] T009 [US1] Personality doctrine guard (contract invariant 3) in `crates/cloudkitty-core/src/behavior/mod.rs` tests: needs_driven AND playful both fall through on the same staged dead critter scene (red-first by reverting T008 in a recorded cycle)

**Checkpoint**: US1 fully functional — MVP

---

## Phase 4: User Story 2 - The groomed friend walked away (P2)

**Goal**: grooming falls through the same way (shared predicate — no new implementation).

**Independent Test**: stage grooming pair, move/busy the target friend, advance: fresh action (quickstart §1).

- [ ] T010 [US2] Behavior guard in `crates/cloudkitty-core/src/behavior/needs_driven.rs` tests: cat mid-`Grooming{Some}`, friend unavailable in snapshot → `None`; red-first via a recorded revert-of-T008 cycle (implementation already landed in US1)
- [ ] T011 [US2] Must-stay-green pin in `crates/cloudkitty-core/src/behavior/needs_driven.rs` tests: friend present and available → grooming continuation unchanged (FR-004)
- [ ] T012 [US2] One-definition cycle (contract invariant 1) in `specs/048-no-stale-reproposal/redden-list.md`: mutate the groom arm of `counterpart_gone`, predict BOTH a prune witness AND T010 red, `--no-fail-fast`, record, restore, count re-read (FR-002's no-drift guard)

**Checkpoint**: US1 + US2 green independently

---

## Phase 5: User Story 3 - The refusal instrument reads true (P3)

**Goal**: stale rows gone from the refusal stream; genuine refusals (incl. same-tick races) untouched.

**Independent Test**: probe re-run reports zero dead-at-snapshot re-proposals; race band unchanged (quickstart §3).

- [ ] T013 [US3] Race must-stay-green pin in `crates/cloudkitty-core/src/world.rs` tests: staged duet where the partner's earlier apply slot interrupts the duet the same tick → the stale continuation IS still refused and stamped `absorbed=false` (SC-005; if an equivalent 046 pin already exists, cite it in redden-list.md instead of duplicating — FR-002-style one home)
- [ ] T014 [US3] Probe re-run per `specs/048-no-stale-reproposal/quickstart.md` §3 (cherry-pick 275896e -n on a CLEAN COMMITTED tree, run all four arms, revert ride-along): expect `reproposed 0` on dead-at-snapshot in every class, PlayDuet races in the 2,600–3,400 band; record the four result blocks in `specs/048-no-stale-reproposal/redden-list.md` §probe-after (SC-001/SC-002/SC-005 evidence)

**Checkpoint**: all stories verified

---

## Phase 6: Polish & Cross-Cutting

- [ ] T015 Golden evolution pin re-pin in its fixture home (expected exactly one move, at the first artifact tick) + `CHANGELOG.md` Unreleased entry with the 039-style marker justifying the re-pin (FR-008); defaults-stamp test confirmed UNTOUCHED (SC-004)
- [ ] T016 `cargo fmt --all --check` + `cargo clippy --workspace --all-targets -- -D warnings` (CI-exact) in the worktree
- [ ] T017 Final `cargo test --workspace --no-fail-fast` COUNT READ + quickstart.md walked top to bottom; redden-list.md complete (every cycle has prediction/observed/restore/count)

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6
- US2/US3 depend on US1's T008 (the single implementation edit) — this is deliberate (FR-003 full coverage via one shared edit), so the stories verify independently but do not implement independently.
- Within US1: T004–T007 written and observed red before T008; T006 sorted must-stay-green first (rule 6).

### Parallel Opportunities

Test-writing tasks touching the same files are sequential by design. Genuinely parallel: none worth claiming — the feature is two files. Execute sequentially.

## Implementation Strategy

MVP = Phase 3 (US1) — after T009 the fix is complete and demonstrable; Phases 4–5 add guards and evidence, not behavior. Stop-and-validate points at each checkpoint. Commit after each task or logical group; ALWAYS commit before a mutate/revert cycle.
