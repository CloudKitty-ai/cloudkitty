# Tasks: Shallow ground sleep

**Input**: Design documents from `/specs/056-shallow-ground-sleep/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/config-key.md

**Tests**: required — every new behavioral claim carries a mutate.sh red
(house rule 5; spec FR-009). Test tasks precede their implementation
tasks; red-first means the guard is written and RED before the law lands.

## Phase 1: Setup

- [x] T001 Confirm clean baseline in the worktree: `cargo test --workspace` green at HEAD (a75de63) so every later red is ours, in /Users/elizabethkelly/ai/cloudkitty-shallow-ground

## Phase 2: Foundational (blocking prerequisites)

- [x] T002 Add `sleep_floor_off_beam: f32` to `ActionsConfig` with `#[serde(default)]`, 0.0 in the `Default` impl, and the doc comment naming the law and spec 056, in crates/cloudkitty-core/src/config/mod.rs
- [x] T003 Unit test beside the spec-050 precedent (~line 1976): absent key parses to 0.0 (= old law); test the parse only, bounds live in T004's guard, in crates/cloudkitty-core/src/config/mod.rs
- [x] T004 Validation: the key joins the `[actions]` finite/≥0 sweep (~line 746) AND one cross-field check `sleep_floor_off_beam < needs.distress` (configured value, never literal 90) beside the existing cross-section checks; unit tests refuse a negative floor and a floor ≥ the configured distress; mutate red per plan ledger item 6 (drop the cross-check → predict the refusal test fails), in crates/cloudkitty-core/src/config/validate.rs
- [x] T005 Extract the warmth circumstance into one shared `World` helper (own tile sunbeam OR `is_settled`-mutual partner on a sunbeam) and re-point `apply_sleep_relief`'s rate choice at it — pure refactor, zero behavior change: `sleeping_in_a_sunbeam_is_more_restful` and the spec-031 conduction tests must stay green, in crates/cloudkitty-core/src/action.rs and crates/cloudkitty-core/src/world.rs

## Phase 3: User Story 1 — The floor holds on the ground (P1) [US1]

**Goal**: off-beam relief clamps at the floor; an under-floor need is never raised.

**Independent test**: one off-beam sleeper, floor 20, need 40 → nap ends with need exactly 20; need 12 stays 12.

- [x] T006 [US1] RED FIRST: unit tests beside `sleeping_in_a_sunbeam_is_more_restful` (~line 1414): (a) `the_floor_holds_on_plain_ground` (floor 20, need 40 → exactly 20, never lower); (b) `a_need_under_the_floor_is_never_raised` (floor 20, need 12 → 12), in crates/cloudkitty-core/src/action.rs
- [x] T007 [US1] Implement the clamp in `apply_sleep_relief` (~line 885): plain-tile relief amount becomes `sleep_relief.min((need − floor).max(0.0))` per data-model.md; the warm branch is untouched, in crates/cloudkitty-core/src/action.rs
- [x] T008 [US1] Mutation cycle: `scripts/mutate.sh --expect` ledger items 1 and 4 (drop the clamp → (a) reds; clamp the need with `max(floor, …)` instead of capping the amount → (b) reds), predictions stated before each run, in /Users/elizabethkelly/ai/cloudkitty-shallow-ground

## Phase 4: User Story 2 — The beam clears it fully (P1) [US2]

**Goal**: beam and conducted sleep escape the floor; the escape is the shared per-tick predicate.

**Independent test**: same floor-20 world; on-beam sleeper reaches 0; conducted sleeper reaches 0; wandered partner re-imposes the floor next tick.

- [x] T009 [US2] RED FIRST: unit tests: (a) `a_beam_nap_clears_under_a_floor` (floor 20, sleeper on sunbeam → 0); (b) `a_conducted_nap_clears_under_a_floor` (floor 20, off-beam sleeper, mutual partner on sunbeam → 0); (c) `a_wandered_partner_reimposes_the_floor` (analyze A1: stage the beam-departure form — partner steps off the sunbeam mid-nap, adjacency kept — conduction lost → later ticks clamp), in crates/cloudkitty-core/src/action.rs
- [x] T010 [US2] Confirm the escape rides the T005 shared predicate (no second warmth computation anywhere in the relief path); mutation cycle ledger items 2 and 3 (apply the clamp unconditionally → (a) reds; drop `partner_warm` from the escape → (b) reds), in crates/cloudkitty-core/src/action.rs

## Phase 5: User Story 3 — Naps still end honestly (P1) [US3]

**Goal**: the sleep scene's finished level is the reachable floor (owner-confirmed D1); floor-0 end ticks are today's.

**Independent test**: floor 20 ground nap ends the tick need hits 20 (after min 6); floor-0 nap's end tick unchanged.

- [x] T011 [US3] RED FIRST: tests beside `a_finished_need_ends_the_meal_at_the_first_lawful_tick` (~line 3448): (a) `a_ground_nap_ends_at_the_reachable_floor` (floor 20: ends the first lawful tick need ≤ 20, NOT at the 12-tick cap); (b) `a_floor_zero_nap_ends_exactly_as_today` (pin the end tick — the unit half of FR-007); (c) analyze C1: `a_nap_begun_at_the_floor_ends_at_the_minimum` (need starts exactly at floor 20, off-beam → no relief possible, nap ends at the 6-tick minimum), in crates/cloudkitty-core/src/world.rs
- [x] T012 [US3] Implement the finished level in `resolve_activity_ends` (~line 636): for `Activity::Sleeping` the `need_zero` comparison becomes `≤ (warm ? 0.0 : floor)` via the T005 shared helper, each duet side its own level, either-side rule untouched, every other activity keeps literal 0, in crates/cloudkitty-core/src/world.rs
- [x] T013 [US3] Mutation cycle ledger item 5 (keep finished = 0 for sleeping → (a) reds by running to the cap); then rule-6 sort: re-read and run the kept pile — all existing sleep/cosleep/duet-end tests, the Article I property suite, both config sweeps — and confirm zero reds, in /Users/elizabethkelly/ai/cloudkitty-shallow-ground

## Phase 6: Polish & cross-cutting

- [x] T014 [P] Register the key in the spec-052 key-settings block (rows ~201, lists ~382/~451, pattern = `relief_memory_margin`); the lists' existing tests must pick it up — if none reds while absent, say so per rule 6 (a must-fail that stays green is vacuous), in crates/cloudkitty-server/src/settings.rs
- [x] T015 [P] One comment line in `[actions]` beside `sleep_relief_sunbeam` (contract wording from contracts/config-key.md); NO value line — the served world keeps the default, in cloudkitty.toml
- [x] T016 [P] Changelog one-liner under `## Unreleased`, passed through the public-voice tell budget at write time; no compatibility marker — state the default-0 equivalence as the reason (a missing marker is a claim), in CHANGELOG.md
- [x] T017 Full sweep: `cargo fmt --check`, clippy clean, `cargo test --workspace`; then the quickstart hand-check (floor 20 scratch toml: watch one ground nap end at 20; floor 95: server refuses naming the key), in /Users/elizabethkelly/ai/cloudkitty-shallow-ground
- [x] T018 Push branch, open the PR (house body: summary, the red ledger with predictions, D1/D2 owner confirmations cited, analyze C2 note — SC-001's world-level evidence is Experiments' pinned-seed action-for-action run, the in-repo proof is unit-layer plus the untouched seeded suites — generated-with + session lines), wait CI green, then ping Experiments that the branch is mergeable (their eight tier-5 arms run that night) — merge stays on the owner's word, in /Users/elizabethkelly/ai/cloudkitty-shallow-ground

## Dependencies

- T001 → everything.
- T002 → T003/T004 (field must exist) → T006+ (config in tests).
- T005 → T007, T010, T012 (the shared predicate).
- Story order US1 (T006–T008) → US2 (T009–T010) → US3 (T011–T013): US2's
  escape tests read the clamp US1 lands; US3's end rule reads both. Each
  story remains independently testable at its own layer.
- T014/T015/T016 [P] are parallel after Phase 5; T017 → T018 last.

## Implementation strategy

MVP = Phases 1–3 (the floor itself, guarded); US2 and US3 complete the
law the owner approved — all three P1 stories ship in this one PR, in
order. No deploy rides the arc; the served world keeps floor 0.
