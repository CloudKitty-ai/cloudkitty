# Tasks: Deliberate Purring & the Quiet Motor

**Input**: Design documents from `/specs/022-deliberate-purr/`

**Prerequisites**: plan.md, spec.md (clarified 2026-07-31), research.md
(D1–D10), data-model.md, contracts/deliberate-purr.md

**Tests**: included — Article VI makes the guarding tests part of the change
itself (FR-015 re-baselines land with the semantics they pin; contract lists
guarding tests 1–12).

**Organization**: by user story; US1 (deliberate purr) is the MVP increment
and works atop the unmodified motor; US2 (quiet motor) and US3 (rhythm
retune) follow. FR-013 couples US3 behind US2 (never ship the retune without
the silent motor).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no incomplete-task dependency)
- All paths relative to repo root.

## Phase 1: Setup

**Purpose**: clean baseline — no scaffolding needed (existing workspace).

- [x] T001 Verify green baseline: run `cargo test --workspace`, `cargo clippy --workspace -- -D warnings`, `cargo fmt --check` at the branch point; record any pre-existing failure before touching code (repo root)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the one state addition every story reads or writes.

**⚠️ CRITICAL**: complete before any user story phase.

- [x] T002 Add `purring_duration: Option<u64>` to `Kitty` with `#[serde(default, skip_serializing_if = "Option::is_none")]` beside `purring_until`, initialized `None` in the constructor, in crates/cloudkitty-core/src/kitty.rs (data-model.md pattern)
- [x] T003 Set `purring_duration = Some(duration)` at the motor's purr start and clear both `purring_until`/`purring_duration` together at purr end in `World::purr_phase`, crates/cloudkitty-core/src/world.rs (no behavior change yet — bookkeeping only)
- [x] T004 Unit tests in crates/cloudkitty-core/src/kitty.rs: serde round-trip includes the new field when `Some` and omits it when `None`; a legacy kitty JSON without the field deserializes to `None` (pre-022 snapshot shape)

**Checkpoint**: `cargo test -p cloudkitty-core` green; kitty state carries
duration with zero semantic change.

---

## Phase 3: User Story 1 — A kitty that chooses to purr really purrs (Priority: P1) 🎯 MVP

**Goal**: menu row 38 becomes the deliberate purr — earned-gated in
`validate()`, applied as a real purr start with apply-time duration draw and
a direct-recorded announcement; silent no-op when already purring; whole
turn always consumed.

**Independent Test**: an earned kitty proposing `Meow(Purr)` starts a purr
phase (duration in bounds) with exactly one announcement and its turn spent;
under an active motor cooldown it still starts; unearned proposals resolve
to `Idle` and the mask excludes row 38.

- [x] T005 [US1] Earned gate in `validate()`: the `Action::Meow { message: MessageKind::Purr }` arm becomes legal iff `happiness > config.thresholds.purr || happiness_rose` (motor rule verbatim); unearned resolves to `Idle` through the existing illegal-proposal path, in crates/cloudkitty-core/src/action.rs (research D2)
- [x] T006 [US1] Deliberate-purr apply branch: on `Meow(Purr)`, if `purring_until.is_some()` → silent no-op (turn consumed, no draw, no announcement); else draw duration via the existing bounds draw on the master RNG at apply time, set `purring_until`/`purring_duration`, push `Meow { kind: Purr }` directly to `recent_meows` (state announcement — no `emit_meow`, no stamp), in crates/cloudkitty-core/src/action.rs (research D1, D5; contract draw table)
- [x] T007 [US1] Re-baseline `purring_is_no_longer_an_action` in crates/cloudkitty-core/src/action.rs: keep the legacy `Action::Purr` → `Idle` half verbatim; replace the `Meow(Purr)` expectations with the earned-gate pair (earned → legal; unearned → `Idle`), doc comment citing spec 022 FR-015 (deliberate re-baseline, not weakening)
- [x] T008 [US1] Unit tests in crates/cloudkitty-core/src/action.rs: contract tests 1–3 — earned start (phase begins, duration in bounds, exactly one announcement, turn consumed), start under active motor cooldown (FR-005), already-purring silent no-op with RNG-stream equality (same seed with and without the no-op proposal → identical subsequent draws)
- [x] T009 [P] [US1] Mask tests in crates/cloudkitty-rl/src/mask.rs: row 38 legal for an earned kitty, excluded for an unearned one, mask never all-zero either way (idle row 39); no mask-side special case — assertions go through the existing derive-from-validate path (contract test 4)
- [x] T010 [US1] Every-purr-earned property test (SC-003 of this spec): randomized configs/seeds/behaviors over thousands of ticks, assert every tick where any kitty is purring satisfies the earned rule at its purr's start, in crates/cloudkitty-core/src/world.rs tests (contract test 5)

**Checkpoint**: deliberate purring fully works against the still-noisy
motor — independently shippable MVP.

---

## Phase 4: User Story 2 — The meadow stays cozy while the channel goes quiet (Priority: P2)

**Goal**: spontaneous starts announce only per `announce_probability`
(default 0), silent starts stamp nothing, the Purr message-cooldown stamp is
deleted from all purr paths, and motor cadence is untouched.

**Independent Test**: default config → purr phases at unchanged cadence,
zero motor announcements; `p = 1` → every start announces once;
`p ∈ (0,1)` → per-draw announcements; purr timings identical across `p`
values for the same seed.

- [x] T011 [P] [US2] Config: add `announce_probability: f32` to `PurrConfig` with serde default in crates/cloudkitty-core/src/config/mod.rs, default fn (0.0) in crates/cloudkitty-core/src/config/defaults.rs, validation row (finite, 0 ≤ p ≤ 1) in crates/cloudkitty-core/src/config/validate.rs, plus a validation unit test rejecting −0.1, 1.1, and NaN
- [x] T012 [US2] Quiet the motor in `World::purr_phase`, crates/cloudkitty-core/src/world.rs: after the duration draw, always draw `gen_bool(announce_probability as f64)` on the master RNG (shape rule FR-011); push the start `Meow` only when it succeeds; **delete** the `set_meow_cooldown` stamp (world.rs:899-902) — no purr path stamps anything (FR-008, 023 handoff); update the surrounding comment to cite spec 022
- [x] T013 [US2] Re-baseline the spec-011 one-meow-per-purr tests in crates/cloudkitty-core/src/world.rs: assert against `announce_probability = 1.0` config (announcing world: one meow at start, none after) and add the default-config assertions — zero motor announcements, unchanged start cadence, and the Purr entry of `meow_cooldowns` never written by any start (stamp deleted; 023 T011 re-verifies from its side) — contract test 6, US2 scenarios 1–2
- [x] T014 [US2] p-invariance shape test in crates/cloudkitty-core/src/world.rs: same seed, `p = 0` vs `p = 1`, all else equal → identical purr start/end tick sequences across many ticks (contract test 7, research D10)

**Checkpoint**: meadow quiet by default, cadence provably unchanged,
deliberate announcements now the only channel traffic.

---

## Phase 5: User Story 3 — The purr rhythm reads as intentional texture (Priority: P3)

**Goal**: duration bounds 8/13, per-end factor draw from
[`cooldown_factor_min`, `cooldown_factor_max`] (1.75/2.75) stamping
⌈factor × duration⌉, loud retirement of `cooldown_ticks`, served config
updated.

**⚠️ FR-013**: this phase MUST NOT merge anywhere without Phase 4.

**Independent Test**: occupancy within ±2pp of ≈30.8% over ≥20k ticks
across configs sharing the 2.25 midpoint; stamps always ⌈f × d⌉ with f in
bounds, seed-reproducible; a config naming `cooldown_ticks` fails to load
naming the replacements.

- [ ] T015 [P] [US3] Add `SeededRng::gen_f32(&mut self) -> f32` in `[0,1)` mirroring `DecisionRng::gen_f32`'s 24-bit-mantissa recipe (rng.rs:108), with a unit test pinning determinism (same seed → same sequence) and range, in crates/cloudkitty-core/src/rng.rs (research D4)
- [ ] T016 [US3] Config schema in crates/cloudkitty-core/src/config/mod.rs + defaults.rs + validate.rs: `cooldown_factor_min`/`cooldown_factor_max: f32` (defaults 1.75/2.75; rows: finite, min > 0, min ≤ max); duration defaults 6→8 and 15→13; replace the `cooldown_ticks` field with the deserialize-only sentinel `Option<u64>` (`#[serde(default, skip_serializing)]`) rejected in `validate_purr` with an error naming the retired key and both replacements (research D6; FR-010)
- [ ] T017 [US3] Config unit tests in crates/cloudkitty-core/src/config/mod.rs: retired-knob TOML fails to load with the replacement-naming error (US3 scenario 3); factor-bounds validation rejects 0, negatives, NaN, min > max; equal bounds accepted; absent `[purr]` table still yields the new defaults (re-baseline `purr_table_defaults_when_absent_and_rejects_bad_bounds`)
- [ ] T018 [US3] Factor-drawn cooldown at purr end in `World::purr_phase`, crates/cloudkitty-core/src/world.rs: draw factor once per end via `gen_f32` scaling (even when bounds equal), stamp `purr_cooldown_until = tick + (factor × duration).ceil()` with `duration = purring_duration.unwrap_or(config.purr.min_ticks)` (FR-012 legacy convention), clearing both purr fields; unit tests: stamp within ⌈min×d⌉..=⌈max×d⌉, seed-reproducible exact value, equal-bounds fixed factor (contract test 8)
- [ ] T019 [US3] SC-004 occupancy test in crates/cloudkitty-core/src/world.rs: happiness pinned high, ≥20k ticks, occupancy within ±2pp of 1/(1 + mean factor bounds) under at least the default config and one alternate duration/factor config sharing the 2.25 midpoint (contract test 9)
- [ ] T020 [US3] Legacy-snapshot convention test in crates/cloudkitty-core/src/world.rs (or kitty.rs): fixture world JSON mid-purr *without* `purring_duration` restores and, at purr end, stamps exactly ⌈factor × min_ticks⌉ (FR-012; contract test 11 half)
- [ ] T021 [US3] Rewrite the `[purr]` section of cloudkitty.toml: `min_ticks = 8`, `max_ticks = 13`, `announce_probability = 0.0`, `cooldown_factor_min = 1.75`, `cooldown_factor_max = 2.75`, comments updated for chosen-purr semantics (research D8 — required for the repo config to keep loading; the 24×24 edit stays out, owner-timed)

**Checkpoint**: full 022 semantics in place; repo config loads; all three
stories green.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: determinism proof, doctrine reconciliation, schema-invariance
gate, final quality bar.

- [ ] T022 Determinism tests in crates/cloudkitty-core/src/world.rs: same seed + config + ticks → identical world state with purrs of both origins in play (drive one kitty via deliberate purr proposals); mid-purr save/restore → identical subsequent trajectory including the stamped cooldown (SC-006; contract test 11)
- [ ] T023 [P] Doctrine amendment in specs/011-sustained-purring/spec.md: dated note on the "purring is never an action" line — purring remains engine-owned state; initiation-by-choice added by spec 022 row 38 (FR-015)
- [ ] T024 [P] Doctrine amendment in specs/001-cloudkitty-mvp/data-model.md: dated note on "Meow: always legal; the cooldown decides whether it is audible" — purr row earned-gated (spec 022); cooldown clause deleted by spec 023 (FR-015)
- [ ] T025 [P] Mask-contract annotation in specs/014-multi-agent-rl/contracts/encodings.md: row 38 legal iff earned (spec 022); mask shape and no-carve-outs guard unchanged (FR-015)
- [ ] T026 SC-005 gate: all pre-existing `cloudkitty-rl` tests pass without modification — the T009 mask-test additions are expected; no existing assertion may change (observation width, menu 40, mask width, kind count all unchanged); then full `cargo test --workspace`, `cargo clippy --workspace -- -D warnings`, `cargo fmt` (repo root)
- [ ] T027 Run quickstart.md end-to-end: targeted proof-point commands foreground with generous timeout (SC-004 test is long-running), plus the manual quiet-meadow smoke if a client check is wanted (specs/022-deliberate-purr/quickstart.md)

---

## Dependencies

```text
Phase 1 (T001)
  └─► Phase 2 (T002 → T003 → T004)
        └─► Phase 3 / US1 (T005 → T006 → T007 → T008; T009, T010 after T006)
              └─► Phase 4 / US2 (T011 ∥ → T012 → T013 → T014)
                    └─► Phase 5 / US3 (T015 ∥ T016 → T017 → T018 → T019, T020; T021 after T016)
                          └─► Phase 6 (T022; T023 ∥ T024 ∥ T025; T026 → T027)
```

- US2 does not depend on US1's code (different files: world.rs vs
  action.rs) — it may start in parallel after Phase 2 if desired; priority
  order is the default.
- **FR-013 hard rule**: US3 never merges anywhere without US2.
- T021 (served config) requires T016 (schema) or the repo config fails to
  load in between — keep them in the same commit.

## Parallel Examples

- Phase 3: T009 (mask.rs) ∥ T010 (world.rs tests) once T005–T006 land.
- Phase 5: T015 (rng.rs) ∥ T016 (config/) — different files, no overlap.
- Phase 6: T023 ∥ T024 ∥ T025 — three independent doc annotations.

## Implementation Strategy

MVP = Phase 1 + 2 + 3 (US1): deliberate purring against the unmodified
motor — coherent, testable, demonstrable alone. US2 then flips the channel
quiet; US3 retunes the rhythm and retires the flat knob (config edit rides
the same commit as the schema change). Nothing here merges to main until
the §9.1 soak concludes; within the batch branch the increments stay
commit-separable for review. Spec 023's implementation follows on the same
branch (its tasks are its own file) — 022's stamp deletion (T012) is
already the batch-final semantics per the FR-008 handoff.
