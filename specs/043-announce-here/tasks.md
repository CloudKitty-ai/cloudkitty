# Tasks: The `announce_here` Knob

**Input**: Design documents from `/specs/043-announce-here/`

**Prerequisites**: plan.md, spec.md (FR-006 as amended — Experiments accepted 2026-08-30), research.md (D1–D8), data-model.md, contracts/announce-here-knob.md, quickstart.md

**Tests**: REQUIRED — FR-010 mandates the gate-zero instrument, and house rules 5/6 mandate red-first evidence for every new guard. Red-first observations are recorded in `specs/043-announce-here/redden-list.md`.

**Organization**: Two commits (plan Structure Decision), three P1 stories: US1 = armed corpus (the here path), US2 = byte-identical launch, US3 = gate zero.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: Sorted checks before any code (house rule 6) and a pinned baseline to prove continuity against.

- [X] T001 Create `specs/043-announce-here/redden-list.md`: the sorted list — must-RED guards (each with its predicted failure reason): stamp-guard key, HERE_KINDS order pin, precedence, phase gate, selection cycling (must red under the handoff's literal aliasing formula), legality, vocabulary, gate-zero assertions 1–3 injection cycles, density-ladder period-ignored injection (T019), armed-determinism impurity injection (T020); must-GREEN kept pile (re-read, not just re-run): `meow_courtesy`, `say_surface_grounding`, `behavior_variation`, both behaviors' decide tests, `evolution_golden`, stamp guard, full suite
- [X] T002 Create `specs/043-announce-here/continuity-baseline.md`: at branch base (69e65eb) run and record `cargo test -p cloudkitty-core roam_cell_stays_out_of_the_default_serialization`, `cargo test -p cloudkitty-core --test evolution_golden`, and the full-suite pass count; pin golden `7b361b2a…` and the current `engine_defaults_sha256` value

---

## Phase 2: Foundational (commit 1 — config surface, inert)

**Purpose**: The knob exists, provably inert. Blocks all stories. Ends as commit 1, green and stamp-proven.

- [X] T003 Add `u64_is_zero` helper beside `f32_is_zero` in `crates/cloudkitty-core/src/config/mod.rs`
- [X] T004 Add `pub announce_here: u64` to `BehaviorConfig` in `crates/cloudkitty-core/src/config/mod.rs` with `#[serde(default, skip_serializing_if = "u64_is_zero")]` and the D7 doc-comment (density semantics, precedence rule + owner-ruling date 2026-08-23, D3 derivation)
- [X] T005 Extend `roam_cell_stays_out_of_the_default_serialization` in `crates/cloudkitty-core/src/config/mod.rs` with the `"announce_here"` key — red-first: temporarily drop the `skip_serializing_if` attribute, predict "announce_here appears in default serialization", observe red, restore, observe green; record in redden-list
- [X] T006 [P] Config unit guards in `crates/cloudkitty-core/src/config/mod.rs` tests: `announce_here = 0` parses equal to default/absent (spec US2-2); a TOML setting `announce_here = 4` round-trips; unknown-field rejection unchanged (kept green)
- [X] T007 [P] Add `MessageKind::HERE_KINDS: [MessageKind; 4]` const in `crates/cloudkitty-core/src/meow.rs` with a unit test pinning it to `MessageKind::ALL` order (`HereFood, HereWater, HereCritter, HereSunbeam`) — red-first: introduce a swapped order, predict the pin names the swap, restore
- [X] T008 Commit 1 gate: `cargo test --workspace` all green, stamp guard green, golden `7b361b2a…` green unregenerated; commit "043 announce_here: config surface (inert)" and record the three witnesses in continuity-baseline.md

**Checkpoint**: knob parseable, unreadable-by-code, stamp unmoved.

---

## Phase 3: User Story 1 — Armed corpus: the here path (Priority: P1) 🎯 MVP

**Goal**: `announce()` speaks Here\* under knob + phase + legality, per FR-003–FR-008 and the amended FR-006.

**Independent Test**: unit guards in `behavior/mod.rs` drive `announce()` directly with crafted `DecisionContext`s (quickstart §3).

### Tests first (write all five, observe red for the predicted reason — the here path does not exist)

- [X] T009 [US1] Precedence guard in `crates/cloudkitty-core/src/behavior/mod.rs` tests: want armed (need ≥ 30) AND adjacent referent AND knob on AND phase tick → `announce` returns the want-kind, never the here-kind (FR-004, US1-2)
- [X] T010 [US1] Phase-gate guard: knob on, referent adjacent, `(tick + id) % period != 0` → `None` (FR-005, US1-3)
- [X] T011 [US1] Selection-cycling guard: two legal here-kinds at period 4, walk consecutive speaking ticks → the pick cycles both kinds in `HERE_KINDS` order via `((tick + id) / period) % n_legal` (amended FR-006, US1-4). This guard MUST also red under the handoff's literal `(tick + id) % n_legal` — that injection is T014's verification
- [X] T012 [US1] Legality guards: phase tick + no adjacent referent → `None`; a cooldown-stamped kind drops out of the legal set and the index re-derives over the survivors (FR-007, edge cases)
- [X] T013 [US1] Vocabulary guard: here-kind disabled in `meow.vocabulary` → never selected even when adjacent + phase (FR-007, US1-5)

### Implementation

- [X] T014 [US1] Extend `announce()` in `crates/cloudkitty-core/src/behavior/mod.rs`: want loop byte-unchanged; on `None`, here path = phase gate → `HERE_KINDS` filtered through `meow::message_legal` → D3 index. T009–T013 green. Rule-5 injection for T011: temporarily use the literal aliasing formula, predict "cycling guard reds: index pinned to first legal kind", observe, restore; record in redden-list
- [X] T015 [US1] Kept-green pass: re-read then run `meow_courtesy`, `say_surface_grounding`, `behavior_variation`, needs_driven + playful decide tests, full `cargo test -p cloudkitty-core` — zero modified existing tests (rule 6 sort: all must-green)

**Checkpoint**: US1 fully functional at unit level.

---

## Phase 4: User Story 3 — Gate zero: speech never moves action (Priority: P1)

**Goal**: the in-tree paired instrument (FR-010, SC-002, SC-006) — contracts §3.

**Independent Test**: `cargo test -p cloudkitty-core --test announce_here_gate_zero`.

- [X] T016 [US3] Write `crates/cloudkitty-core/tests/announce_here_gate_zero.rs` per research D5: same-seed worlds A (defaults) and B (defaults + `announce_here = 1`) ticked in lockstep; per tick, per kitty in id order, feed `(id, pos, activity, last_action)` serde-serialized into a Sha256 per world; harvest each tick's `recent_meows` entries before pruning. Assertions: (1) digests equal, (2) ≥ 1 Here\* in B, (3) want+WaitForMe streams equal
- [X] T017 [US3] Rule-5 injection cycle, one per assertion (predict each failure first, record in redden-list): (1) give B a divergent `playful_comfort` → digest mismatch red; (2) set B's knob to 0 → non-vacuity red; (3) temporarily let the here path run BEFORE the want loop → want-stream red. Restore each; observe green
- [X] T018 [US3] Tune the tick count so assertion 2 passes with margin on the default generated world (target ~2,000; raise if Here\* emissions are scarce) and runtime stays reasonable; note the chosen count + observed emission count in the test's doc-comment
- [X] T019 [US3] Density-ladder test in `crates/cloudkitty-core/tests/announce_here_gate_zero.rs` (SC-003, analyze C1): same seed and duration at periods 1, 4, 16 → Here\* emission counts strictly decreasing (deterministic, so exact counts; assert strict `>` between arms). Red-first: temporarily ignore the period in the phase gate (treat any N ≥ 1 as 1), predict "all three arms emit the period-1 count", observe red, restore
- [X] T020 [US3] Armed-determinism assertion in the same harness (SC-004, analyze C2): run world B (knob = 1) twice from the same seed → full message streams bitwise equal (extends `determinism.rs` coverage, which proves knob-off only). Red-first note: the here path is a pure function, so the honest injection is impurity itself — a process-global `static AtomicU64` counter mixed into the selection index (announce has no RNG access, so a `gen_bool` won't compile); predict "second run's stream diverges once counts differ", observe red, restore; record in redden-list

**Checkpoint**: gate zero CI-guarded; the no-scripted-here-listener invariant is now enforced; SC-003/SC-004 covered in-tree.

---

## Phase 5: User Story 2 — Byte-identical launch (Priority: P1)

**Goal**: SC-001 proven by the standing witnesses, unmodified (research D6).

**Independent Test**: quickstart §1.

- [X] T021 [US2] Final continuity proof: stamp guard green with `announce_here` in its key list, `evolution_golden` green with `7b361b2a…` unregenerated, `cargo test --workspace` green with zero modified existing tests; append the run evidence to `specs/043-announce-here/continuity-baseline.md` (US2 acceptance 1–3)

**Checkpoint**: all three stories independently proven.

---

## Phase 6: Polish & Delivery

- [X] T022 [P] Add the commented `announce_here` documentation block under `[behavior]` in `cloudkitty.toml` (value NOT set — 042 pattern; served world launches knob-off)
- [X] T023 [P] Add the `## Unreleased` line to `CHANGELOG.md` (no `[stamp]` marker — the stamp does not move)
- [X] T024 Run quickstart.md §1–§3 end-to-end from a clean `cargo test` state; fix anything that drifted
- [X] T025 Finalize `specs/043-announce-here/redden-list.md`: every must-RED shows an OBSERVED red with its predicted reason; every must-GREEN pile re-read and green
- [X] T026 Commit 2 ("043 announce_here: the here path + gate-zero instrument") and draft the PR body — MUST carry the D3 deviation note to Experiments (aliasing finding + adopted derivation, accepted 2026-08-30) and cite gate zero as the screen's acceptance test. Opening the PR is the owner's call

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6, strictly: the commit structure (inert surface first) and TDD ordering (T009–T013 red before T014) are load-bearing, not stylistic.
- US ordering is fixed by construction: US1's implementation (T014) is what US3 instruments (T016) and what US2's final proof (T021) certifies against. The stories are independently *testable* (each has its own named checks) but land in this order.
- [P] within a phase: T006/T007 (different files); T022/T023 (different files). T009–T013 share `behavior/mod.rs` — written together but sequential, no [P].

## Implementation Strategy

Single developer, sequential phases, two commits. MVP = Phases 1–3 (the knob speaks, unit-proven); Phases 4–5 make it mergeable (the spec's acceptance is SC-002, not the MVP). No deploy rides this PR.

**Task count**: 26 (Setup 2, Foundational 6, US1 7, US3 5, US2 1, Polish 5).
