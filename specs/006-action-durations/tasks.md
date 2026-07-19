# Tasks: Action Durations

**Input**: Design documents from `/specs/006-action-durations/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — Article VI makes the property/regression suite a required CI
gate, and SC-001…007 are defined as deterministic test assertions. Long-run and
regression tests are written alongside (not strictly before) implementation, per
the 004 precedent; unit tests for each engine rule land in the same task as the
rule where the file is shared.

**Organization**: By user story, sequenced US1 → US2 → US3 → US4 (each later
story extends the engine passes the earlier one introduces; each checkpoint is
independently testable and leaves the suite green).

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Rust workspace per plan.md: engine in `crates/cloudkitty-core/src/`, engine
tests in `crates/cloudkitty-core/tests/`, server tests in
`crates/cloudkitty-server/tests/`, config file at repo root.

---

## Phase 1: Setup (Configuration surface)

**Purpose**: The duration bounds exist, validate, and ship as documented
defaults before any engine logic reads them.

- [x] T001 Add `DurationBounds { min, max }` and `DurationsConfig` (eat, drink, play, bath, sleep, cuddle) with serde defaults (2/5, 2/5, 2/5, 2/5, 2/8, 2/8) as `[actions.durations]` under `ActionEffects` in crates/cloudkitty-core/src/config.rs
- [x] T002 Validate every `[actions.durations]` entry (`1 ≤ min ≤ max`) in `Config::validate`, error naming field, value, and allowed range in the established style, in crates/cloudkitty-core/src/config.rs
- [x] T003 [P] Add `[actions.durations]` defaults with comments to cloudkitty.toml
- [x] T004 Config unit tests: a toml omitting `[actions.durations]` yields the documented defaults; bad bounds (min 0, max < min) rejected with the named field; `min = max = 1` accepted; fingerprint unaffected by duration keys — in crates/cloudkitty-core/src/config.rs

---

## Phase 2: Foundational (State model — blocks all stories)

**Purpose**: The `Activity` vocabulary and the clock exist, serialize, and
load from every snapshot generation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Extend `Activity` with `Eating`, `Drinking`, `Playing { target: Option<TargetRef> }`, `Grooming { target: Option<KittyId> }` (tag scheme unchanged; optional payloads defaulted + skipped when absent) plus helpers: relieved-need mapping, `durations`-key mapping, updated `partner()` — in crates/cloudkitty-core/src/kitty.rs
- [x] T006 Add `ActivityClock { started, applied }` and `Kitty.activity_clock: Option<ActivityClock>` (serde default `None`, `skip_serializing_if`), initialize in `Kitty::new` — in crates/cloudkitty-core/src/kitty.rs
- [x] T007 Serde tests: each new `Activity` variant's wire shape; clock round-trip; a pre-006 kitty JSON (no `activity_clock`, in-progress `sleeping`) deserializes with `None` clock; existing variants byte-identical — in crates/cloudkitty-core/src/kitty.rs
- [x] T008 Add `World::is_conscriptable_friend` (adjacency ∧ partner `activity == Idle`) beside `is_available_friend`, with unit tests — in crates/cloudkitty-core/src/world.rs

**Checkpoint**: `cargo test --workspace` green; state model complete, engine
behavior unchanged.

---

## Phase 3: User Story 1 — Every Action Lasts Long Enough to See (Priority: P1) 🎯 MVP

**Goal**: All six need-relieving actions become engine-continued multi-tick
activities with a clock, full per-tick relief, and an enforced minimum.

**Independent Test**: In a deterministic run, every eat/drink/play/groom/
sleep/rest instance lasts ≥ its configured min with relief applied every tick;
proposals during the min are superseded; same-activity proposals never reset
the clock. (Activities end via post-min behavior switches — normal selection —
until US2/US3 add engine end rules; the suite stays green.)

### Implementation for User Story 1

- [x] T009 [US1] Rework `apply()` so Eat/Drink/Groom/Play set their new `Activity` variant + `ActivityClock { started: tick, applied: tick }` instead of `set_idle`, applying tick-1 effects (relief; Eat consumes 1 serving) — in crates/cloudkitty-core/src/action.rs
- [x] T010 [US1] Set `ActivityClock` when Sleep/Rest start (alongside their existing `Activity` writes), and stamp `applied` in their continuation paths — in crates/cloudkitty-core/src/action.rs
- [x] T011 [US1] Generalize `continue_current_activity` to all six variants: **always stamp `clock.applied = tick` on every serviced tick** (analyze C1 — end rules key off the clock, so the stamp must never be skipped); apply per-tick effects only when `clock.applied < tick` on entry (duet guard) and resources permit; Eating consumes a serving per effect-applied tick; sunbeam re-check kept for sleep — in crates/cloudkitty-core/src/action.rs
- [x] T012 [US1] Add the duration-enforcement step to the phase-2 loop in `World::tick`: ongoing ∧ `elapsed < min` ∧ validated ≠ continuation → replace with the activity's continuation action; validated same-activity or `Idle` → normalize to continuation (clock untouched); ongoing ∧ `elapsed ≥ min` ∧ different validated action → clear activity+clock **on both sides if the ended activity was a duet** (analyze I1 — no one-sided duet may survive to phase 4), then apply validated; record `last_action` as the action actually applied — in crates/cloudkitty-core/src/world.rs
- [x] T013 [US1] Unit tests: a meal runs ≥ min with `eat_relief` each tick and `last_relief` stamped per tick; a mid-min Move proposal is superseded by continuation; re-proposing Sleep every tick never resets `started` — in crates/cloudkitty-core/src/world.rs. (If this checkpoint shifts tests/behavior_variation.rs expectations, re-pin them here rather than waiting for T020.)
- [x] T014 [P] [US1] Unit test: `last_action` reads as the activity's action on every continuation tick (eat and sleep cases) — in crates/cloudkitty-core/src/action.rs

**Checkpoint**: activities visibly span ticks; suite green; welfare bounds may
already tighten (do not loosen).

---

## Phase 4: User Story 2 — Actions End When the Job Is Done (Priority: P2)

**Goal**: The engine ends an activity at the first tick where the minimum is
met and the relieved need is 0 — or the bowl is empty.

**Independent Test**: In a deterministic run, zero activities continue past
min-met ∧ need-0; a bowl emptied post-min ends the meal that tick; emptied
pre-min pauses relief/consumption until the min.

### Implementation for User Story 2

- [x] T015 [US2] Add the end-resolution pass to `World::tick` (after the apply loop, before `environment_phase`, kitty-id order): examine **every kitty with an ongoing activity** (clock present — never gate on `applied == tick`, analyze C1) and end when `elapsed ≥ min` with the governing need at 0 (`activity = Idle`, `clock = None`; governing need per the data-model mapping table — groom-friend: the target's bath; solo rest: none) — in crates/cloudkitty-core/src/world.rs
- [x] T016 [US2] Eating resource rules: end-resolution also ends a post-min `Eating` with no adjacent chow carrying servings; pre-min empty-bowl continuation keeps the pose, skips relief and consumption, **but still stamps `clock.applied`** (analyze C1 — a paused meal must remain reachable by every end rule, or the kitty is locked forever) — in crates/cloudkitty-core/src/action.rs and crates/cloudkitty-core/src/world.rs
- [x] T017 [US2] Unit tests: need hits 0 on the min tick → ends exactly there; need 0 before min → continues clamped to min then ends; both empty-bowl branches; the freed kitty decides freely next tick — in crates/cloudkitty-core/src/world.rs

**Checkpoint**: activities self-terminate; no cat polishes a zeroed need.

---

## Phase 5: User Story 3 — No Action Overstays (Priority: P3)

**Goal**: The configured maximum ends any activity unconditionally; sleep and
rest live fully under the framework.

**Independent Test**: 20k ticks: zero instances exceed max; a sleeping cat at
cap 8 wakes even under endless Idle proposals and may re-enter with a fresh
clock; `min = max = 1` reproduces pre-006 instant actions.

### Implementation for User Story 3

- [x] T018 [US3] Add the max rule to end-resolution (`elapsed ≥ max` ends, all six variants including `Sleeping`/`Resting`) — in crates/cloudkitty-core/src/world.rs
- [x] T019 [US3] Unit tests: sleep capped at 8 despite continuation proposals; lawful immediate re-entry gets a fresh `started`; a different proposal between min and max interrupts; `min = max = 1` world behaves like pre-006 (spot-check eat) — in crates/cloudkitty-core/src/world.rs
- [x] T020 [P] [US3] Re-run and, only if needed, re-pin expectations in crates/cloudkitty-core/tests/behavior_variation.rs (built-ins unchanged by design; gates now redundant with engine bounds, not wrong)

**Checkpoint**: stuck-in-one-action is now impossible by construction.

---

## Phase 6: User Story 4 — Shared Activities Share Fairly (Priority: P4)

**Goal**: Cuddle and social play are engine-recorded duets — conscription only
of idle partners, one shared clock, once-per-tick effects, atomic end; looser
counterparts (critters, groom targets) end the scene by leaving.

**Independent Test**: Duet partners' needs drop every shared tick, both
activities start/end on identical ticks; a busy or sleeping partner can't be
conscripted; a vanished critter or departing groom target ends the activity
immediately; a post-min interrupt by either partner frees both in the same
tick.

### Implementation for User Story 4

- [x] T021 [US4] Tighten `validate()`: `Rest { with: Some }` and `Play { Kitty }` require `is_conscriptable_friend`; `Sleep { with }` and `Groom { target }` keep plain adjacency — in crates/cloudkitty-core/src/action.rs
- [x] T022 [US4] Duet start in `apply()`: cuddle/social play set reciprocal activities (`Resting { with_friend }` both sides / `Playing { target: Kitty }` both sides) and identical clocks on both partners — in crates/cloudkitty-core/src/action.rs
- [x] T023 [US4] Once-per-tick duet effects: first partner's slot applies both parties' relief and stamps both clocks; the second slot (or its normalized continuation, including both-proposed-play-at-each-other) is a no-op via the `applied` guard — in crates/cloudkitty-core/src/action.rs
- [x] T024 [US4] Atomic pair end-resolution: treat reciprocal pairs as one unit — end both when either partner's governing need is 0 (after the shared min) or at the shared max (interrupt-driven duet ends are T012's both-sides clear; this task covers the engine end rules) — in crates/cloudkitty-core/src/world.rs
- [x] T025 [US4] Pre-validate prune step in the phase-2 loop: an activity whose counterpart is gone (element expired / out of adjacency, groom target departed, duet no longer reciprocal) is cleared immediately — min notwithstanding — before the kitty's proposal validates — in crates/cloudkitty-core/src/world.rs
- [x] T026 [US4] Migrate the frozen 004 test fixtures to strict 006 shape (stamp an `ActivityClock` on any kitty with a non-Idle activity; make any one-sided cuddle reciprocal or solo) so they pass strict load validation — asset maintenance, semantics unchanged — in specs/004-fix-happiness-lockin/stuck-state-tick1465.json (and stuck-state-config.toml only if durations must be pinned)
- [x] T027 [US4] Unit tests: busy/sleeping partner not conscriptable; duet relief exactly once per tick per partner; identical start/end ticks for engine ends **and for a post-min interrupt by either partner (both freed the same tick, whichever id order)**; critter-vanish and groom-target-walks immediate ends — in crates/cloudkitty-core/src/world.rs

**Checkpoint**: all four stories complete; every FR implemented.

---

## Phase 7: Polish & Cross-Cutting (invariants, suites, contracts, docs)

- [x] T028 Extend `invariants::check`: strict biconditional clock ⟺ non-Idle activity, with `started ≤ applied ≤ tick`; post-tick `elapsed ≤ max`; unconditional duet symmetry (reciprocal activity, identical clocks) — no legacy tolerance, so a pre-006 snapshot fails load validation with the standard clear error — with unit tests — in crates/cloudkitty-core/src/invariants.rs
- [x] T029 [P] Property tests: mid-activity 006 worlds round-trip (serialize → load → identical continuation to the uninterrupted run); a pre-006 shape (in-progress `Sleeping` with `activity_clock` stripped) is refused by strict load validation with the standard clear error — in crates/cloudkitty-core/tests/invariants_proptest.rs
- [x] T030 [P] New suite asserting SC-001/002/004/005/006: 20k-tick instrumented run (min/max adherence, need-zero promptness, every kind seen ≥ 2 ticks), 5k-tick same-seed timeline determinism, save/resume-mid-activity equivalence — in crates/cloudkitty-core/tests/activity_durations.rs
- [x] T031 Re-baseline welfare bounds on the new engine with 004 floors asserted beside the new constants (SC-003), and confirm the migrated fixtures (T026) still pass with recovery at least as fast — in crates/cloudkitty-core/tests/welfare_longrun.rs and crates/cloudkitty-core/tests/stuck_state_regression.rs
- [x] T032 [P] Server contract tests: `activity_clock` present mid-activity and omitted when idle; new `activity.state` values serve; `/config` echoes `actions.durations` defaults — in crates/cloudkitty-server/tests/server_integration.rs
- [x] T033 [P] Amend base contracts with 006 pointers: specs/001-cloudkitty-mvp/data-model.md, specs/001-cloudkitty-mvp/contracts/behavior.md, specs/001-cloudkitty-mvp/contracts/http-api.md; note in specs/004-fix-happiness-lockin/spec.md that its welfare baselines are superseded as floors by 006
- [x] T034 Run the full quickstart walkthrough (specs/006-action-durations/quickstart.md): fmt + clippy + suite, live-server observation, config-abuse rejection, and the old-snapshot refusal / fresh-world boot check (never modify or commit the owner's snapshot.json)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)** → **Foundational (2)** → user stories strictly in order
  **US1 (3) → US2 (4) → US3 (5) → US4 (6)** → **Polish (7)**.
- The stories are sequential by design: US2 and US3 extend the
  end-resolution pass US2 creates over the machinery US1 creates; US4
  builds duet rules on all three. Each checkpoint leaves the whole suite
  green, so any prefix is shippable.

### Within Each Phase

- T009 → T010 → T011 → T012 (same files, layered mechanics); tests after
  the mechanics they pin.
- T015 → T016; T021 → T022 → T023 → T024 → T025 → T026.

### Parallel Opportunities

- T003 beside T001/T002; T005 ∥ T006 (same file — sequence in practice,
  parallel only across contributors); T014 beside T013; T020 beside T018/T019;
  T029 ∥ T030 ∥ T032 ∥ T033 (different files) once their phases' mechanics
  exist.

## Parallel Example: Polish phase

```bash
# After T028 and T031 land, these four touch four different files:
Task: "Round-trip + strict-refusal properties in crates/cloudkitty-core/tests/invariants_proptest.rs"
Task: "SC suite in crates/cloudkitty-core/tests/activity_durations.rs"
Task: "Wire assertions in crates/cloudkitty-server/tests/server_integration.rs"
Task: "Contract pointers in specs/001-cloudkitty-mvp/ and specs/004-fix-happiness-lockin/"
```

## Implementation Strategy

**MVP = Phases 1–3 (US1)**: durations exist, actions are visible and relieve
per tick; ends still come from behavior switches. Stop, validate, observe in
the live viewer. Then add engine end rules (US2), the cap (US3), and duet
fairness (US4) as three further independently green increments, finishing
with the suites that freeze the guarantees into CI (Phase 7).
