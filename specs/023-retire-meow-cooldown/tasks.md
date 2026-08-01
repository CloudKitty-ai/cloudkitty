# Tasks: Meow Channel Economics — Retire the Engine-Enforced Meow Cooldown

**Input**: Design documents from `/specs/023-retire-meow-cooldown/`

**Prerequisites**: plan.md, spec.md (clarified + plan-phase correction
2026-07-31), research.md (D1–D7), data-model.md, contracts/meow-channel.md
— **and spec 022's implementation complete on this branch** (023 builds on
purr paths that already stamp nothing).

**Tests**: included (Article VI; contract guarding tests 1–10 all mapped).

**Organization**: config rename is foundational (everything reads the
renamed keys; the served config must flip in the same commit). US1 removes
the swallow, US2 makes courtesy complete (third emitter + spacing
invariant), US3 verifies the dials and handoffs.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Verify spec 022 tasks are complete and the workspace is green on this branch (`cargo test --workspace`) before starting — 023's guard tests assume purr paths stamp nothing (repo root)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the config rename every consult and stamp site reads.

**⚠️ CRITICAL**: T002–T004 land as one commit — the repo `cloudkitty.toml`
must never be unloadable in between.

- [ ] T002 Rename `MeowConfig` fields in crates/cloudkitty-core/src/config/mod.rs: `courtesy_ticks` (default fn 10) and `urgent_courtesy_ticks` (default fn 5) with `#[serde(default = ...)]` on all four real fields (posture aligned with PurrConfig, research D2); add deserialize-only sentinels `cooldown_ticks`/`urgent_cooldown_ticks: Option<u64>`; default fns in crates/cloudkitty-core/src/config/defaults.rs; `validate_meow` in crates/cloudkitty-core/src/config/validate.rs (urgent ≤ base; each sentinel `Some` → error naming old key and replacement); sweep all `config.meow.cooldown_ticks`/`urgent_cooldown_ticks` readers (emit_meow in action.rs, tests) to the new names and verify no purr-phase reader remains (022 removed them)
- [ ] T003 Config unit tests in crates/cloudkitty-core/src/config/mod.rs: retired-key TOMLs each fail naming the replacement (US3 scenario 2 / contract test 6); partial `[meow]` table default-fills; urgent > base rejected; absent table yields defaults 10/5
- [ ] T004 Rewrite the `[meow]` section of cloudkitty.toml (lines 155-159): `courtesy_ticks = 10`, `urgent_courtesy_ticks = 5`, comments rewritten from law-language to courtesy-language per contracts/meow-channel.md schema block (research D6 — same commit as T002)

**Checkpoint**: workspace green, repo config loads, semantics unchanged
(enforcement still in place, reading renamed keys).

---

## Phase 3: User Story 1 — An agent's meow always happens (Priority: P1) 🎯 MVP

**Goal**: the silent swallow is gone — every validated meow action emits
and stamps; turn cost and all bounding surfaces unchanged.

**Independent Test**: same-kind meows on consecutive ticks all emit; digest
presence saturates (clamped); recent record stays pruned; bookkeeping
timestamps advance on every emission.

- [ ] T005 [US1] Delete the `can_meow` early-return (swallow) in `emit_meow`, crates/cloudkitty-core/src/action.rs:706-710; the stamp and push run unconditionally; update the function and call-site doc comments to the record-not-law semantics citing spec 023 (research D1)
- [ ] T006 [US1] Re-baseline `meows_on_cooldown_are_silently_dropped` in crates/cloudkitty-core/src/action.rs: replaced by a repeat-emits test (consecutive same-kind meows both recorded — contract test 1, SC-001) plus an emission-always-stamps test (timestamp advances, urgent rule applied at stamp time — contract test 2); doc comment notes the deliberate retirement of the swallow assertion (SC-007)
- [ ] T007 [P] [US1] Bounded-chatty-advisor tests: extend the digest clamp test in crates/cloudkitty-rl/src/observe.rs (per-tick same-kind meows saturate presence at the clamp, never compound) and assert `recent_meows` stays within the pruning window under per-tick meowing in crates/cloudkitty-core/src/world.rs (contract test 3, US1 scenario 2)

**Checkpoint**: no swallow anywhere; agents fully governed by economics.

---

## Phase 4: User Story 2 — Scripted kitties stay polite, with no dead air (Priority: P2)

**Goal**: courtesy is complete (all three emitters consult, including the
approach-etiquette yield) and provably spaced at 10/5.

**Independent Test**: persistently urgent scripted kitty repeats every 5
ticks with no dead air; approach dance emits "Wait for me!" at most once
per courtesy interval while still progressing; spacing invariant holds over
randomized long runs.

- [ ] T008 [US2] Third emitter (plan-phase correction, FR-004): change `wait_for_them()` to `wait_for_them(ctx: &DecisionContext) -> Action` in crates/cloudkitty-core/src/behavior/selection.rs — consult `ctx.me.can_meow(MessageKind::WaitForMe, ctx.world.tick)`; on courtesy return `Action::Idle` (silent stand); update both call sites (crates/cloudkitty-core/src/behavior/needs_driven.rs:203 and selection.rs:336) and the yield doc comment (the stand is the progress guarantee)
- [ ] T009 [US2] Re-baseline yield tests in crates/cloudkitty-core/src/behavior/selection.rs (incl. the `wait_for_them()` expectation at selection.rs:778) and add: on-courtesy yield is `Idle`, dance still progresses across ticks (tick-parity preserved), no WaitForMe emission inside the courtesy interval (contract test 5, US2 scenario 4)
- [ ] T010 [US2] SC-003 spacing-invariant property test in crates/cloudkitty-core/src/world.rs: long randomized runs under built-in rosters with per-tick emission capture (diff `recent_meows` by tick, research D4); assert per-kitty per-kind gaps ≥ applicable courtesy interval (urgent 5 at/above threshold at proposal time, else 10), including a forced approach-dance scenario and a persistent-urgency stretch asserting the no-dead-air refresh (contract test 4, US2 scenarios 1–2)

**Checkpoint**: courtesy complete and property-guarded; meadow character
preserved by construction.

---

## Phase 5: User Story 3 — The dials mean what they say (Priority: P3)

**Goal**: handoffs verified — purr stamps nothing, legacy snapshots
harmless. (The config-honesty scenarios landed in Phase 2: T003 covers US3
scenarios 1–2.)

- [ ] T011 [P] [US3] Purr-stamps-nothing guard test in crates/cloudkitty-core/src/world.rs: after deliberate and spontaneous purr starts (announce probability 0 and 1), assert the Purr entry of `meow_cooldowns` is never written (022 FR-008 handoff, contract test 7, US3 scenario 3)
- [ ] T012 [P] [US3] Legacy-snapshot test in crates/cloudkitty-core/src/kitty.rs or world.rs: a kitty JSON fixture with stamped `meow_cooldowns` restores and runs; a scripted consult respects the restored stamp (delayed next meow), and nothing else reads it (contract test 8, US3 scenario 4)

**Checkpoint**: all three stories green; full 023 semantics in place.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T013 [P] Doctrine amendment in specs/012-approach-etiquette/spec.md: dated note on the "lawfully silent" clause — the yield consults courtesy and stands silently (spec 023); progress guarantee restated as the stand (FR-008)
- [ ] T014 [P] Verify/extend the shared spec 001 annotation from 022's T024 in specs/001-cloudkitty-mvp/data-model.md: the "cooldown decides whether it is audible" clause deletion is attributed to spec 023 with the purr-row exception attributed to 022 (FR-008 — one dated note, both pointers)
- [ ] T015 [P] Record the reward-structure dependency in docs/rl-training.md: certification-assumptions note — spam backstop for learned agents is economics under the cooperative team reward; any per-kitty or competitive reward design revisits spec 023 before training (FR-011, research D5)
- [ ] T016 Doc-comment sweep in crates/cloudkitty-core/src/meow.rs (module header + `cooldown_for`) and crates/cloudkitty-core/src/kitty.rs (`can_meow`/`set_meow_cooldown`): courtesy/record language replaces enforcement language, citing spec 023
- [ ] T017 Gates: all pre-existing `cloudkitty-rl` tests pass without modification — the T007 digest-clamp extension is expected; no existing assertion may change (SC-004; contract test 9); full `cargo test --workspace`, `cargo clippy --workspace -- -D warnings`, `cargo fmt`, then run specs/023-retire-meow-cooldown/quickstart.md proof points foreground with generous timeout (SC-005/SC-006; contract test 10)

---

## Dependencies

```text
Phase 1 (T001 — requires 022 implementation complete)
  └─► Phase 2 (T002 → T003; T004 same commit as T002)
        └─► Phase 3 / US1 (T005 → T006; T007 ∥ after T005)
              └─► Phase 4 / US2 (T008 → T009; T010 after T008)
                    └─► Phase 5 / US3 (T011 ∥ T012)
                          └─► Phase 6 (T013 ∥ T014 ∥ T015; T016; T017 last)
```

- US2's spacing test (T010) needs US1 (emissions must be observable —
  under the swallow the invariant is vacuous).
- T011/T012 only verify — they can start any time after Phase 3 but are
  grouped for review coherence.

## Parallel Examples

- Phase 3: T007 (observe.rs/world.rs tests) ∥ T006 (action.rs tests).
- Phase 5: T011 ∥ T012 — different fixtures, no overlap.
- Phase 6: T013 ∥ T014 ∥ T015 — three independent documents.

## Implementation Strategy

MVP = Phases 1–3: the swallow is gone and economics governs agents — the
issue's core promise, testable alone (courtesy still holds at the renamed
defaults from Phase 2). US2 completes the courtesy story with the third
emitter and the property gate; US3 verifies the cross-spec handoffs. The
whole spec follows 022 on the shared branch; nothing merges to main before
the soak concludes, and the batch recert follows the merge.
