# Tasks: Fix Low-Happiness Lock-In

**Input**: Design documents from `/specs/004-fix-happiness-lockin/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — the spec's success criteria define concrete test bounds (SC-001–006) and Article VI makes the extended property suite a CI gate.

**Organization**: Grouped by user story. US1 is the MVP; US2–US4 build on the shared selection module US1 creates; US5 is fully independent of the others.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1–US5, mapping to spec.md user stories

## Phase 1: Setup (Configuration)

**Purpose**: Every new tunable exists, validated, before any logic reads it (Article VI first).

- [X] T001 Add new config fields with serde defaults and validation in crates/cloudkitty-core/src/config.rs: `BehaviorConfig { urgency_weight: 2.0, tile_cost: 1.0, worth_a_detour: 30.0, chase_patience_ticks: 12, chase_exclusion_ticks: 60, solo_play_reach: 8 }`, `ActionsConfig { solo_play_relief: 10.0 }`, and new `ViewerConfig { distress_patience_ticks: 60 }` section wired into `Config`; validation errors name field, value and allowed range per data-model.md constraints (urgency_weight/tile_cost finite ≥ 0; worth_a_detour 0–100; chase_patience_ticks/chase_exclusion_ticks/solo_play_reach/distress_patience_ticks ≥ 1; solo_play_relief ≥ 0 and ≤ play_relief); unit tests for each rejection and for defaults; confirm `fingerprint()` is untouched
- [X] T002 Document the new keys with defaults and comments in cloudkitty.toml (`[behavior]` additions, `[actions] solo_play_relief`, new `[viewer]` section), matching the R8 table in specs/004-fix-happiness-lockin/research.md

**Checkpoint**: `cargo test -p cloudkitty-core config` green; `/config` will echo the new keys with no further server work.

---

## Phase 2: Foundational (Action shape)

**Purpose**: `Play`'s optional target is a cross-cutting type change; landing it first means every later story writes pattern matches once. US3 gives it behavior; US2's new play-construction sites need the final shape.

**⚠️ CRITICAL**: Complete before US2/US3 work begins.

- [X] T003 Widen `Action::Play(TargetRef)` to `Play { target: Option<TargetRef> }` in crates/cloudkitty-core/src/action.rs with wire compatibility (old `{"action":"play","target":...,"id":...}` parses; solo serializes as `{"action":"play"}`); validation: `Some` keeps existing rules, `None` always legal; application: `Some` unchanged, `None` relieves play by `config.actions.solo_play_relief` (actor only); sweep all existing `Play(` construction/match sites in crates/cloudkitty-core (behaviors, world.rs, tests) to the new shape with `Some(target)` semantics unchanged
- [X] T004 Add wire-compatibility and legality unit tests in crates/cloudkitty-core/src/action.rs: old-shape JSON round-trip for social play, targetless shape round-trip, solo play always validates, solo apply uses `solo_play_relief` not `play_relief`

**Checkpoint**: full workspace compiles; existing behavior tests still pass with unchanged social-play semantics.

---

## Phase 3: User Story 1 — A kitty tends its needs in proportion, never fixating (Priority: P1) 🎯 MVP

**Goal**: Replace the two-mode (safeguard-lock / convenience-band) selection with one urgency-weighted, distance-aware score in both built-in profiles (research.md R1).

**Independent Test**: A kitty with bath 100 (distance 0) and play 100 (nearest partner far) grooms within a few ticks; a kitty with eat 80 five tiles from chow still beats a 50-point bath; resuming the stuck fixture, sleep and bath unpin without a successful play.

- [X] T005 [US1] Create crates/cloudkitty-core/src/behavior/selection.rs: `choose_need(ctx) -> NeedKind` implementing `score = pressure + urgency_weight × max(0, pressure − safeguard) − tile_cost × travel_distance` over all six needs (no convenience band); move `travel_distance` here from needs_driven.rs unchanged; initial tie-break = `NeedKind::ALL` order (US4 upgrades it); register module in crates/cloudkitty-core/src/behavior/mod.rs; unit tests encode the R1 worked example (Miso tick-1465 pressures/distances → bath, then play-vs-sleep flips on partner distance)
- [X] T006 [US1] Rewire crates/cloudkitty-core/src/behavior/needs_driven.rs: delete `WORTH_A_DETOUR`/`TILE_COST` consts and `most_convenient`; `take_what_is_here` reads `config.behavior.worth_a_detour`; the safeguard-lock branch is replaced by `selection::choose_need`; pre-selection gates (opportunism, meow, purr, wander) keep current order and semantics
- [X] T007 [P] [US1] Rewire the get-serious path in crates/cloudkitty-core/src/behavior/playful.rs to use `selection::choose_need` (FR-014); personality gates (`playful_comfort`, purr generosity, opportunism-first) unchanged
- [X] T008 [US1] Add US1 acceptance tests in crates/cloudkitty-core/src/behavior/selection.rs and needs_driven.rs test modules: pinned-bath-beats-far-play (acceptance 1), urgent-eat-with-nearby-chow-beats-moderate-bath (acceptance 2), and a decision-context reconstruction of the stuck kitty asserting the chosen need is bath, not play (acceptance 3, unit-level; the full fixture resume lands in T028)

**Checkpoint**: US1 alone is shippable — lock-in's amplifier is gone even with today's play throughput.

---

## Phase 4: User Story 2 — Play is actually attainable (Priority: P2)

**Goal**: Opportunistic play, distance-based targeting across critters and friends, and engine-tracked chase give-up (research.md R2, R4).

**Independent Test**: A kitty en route to water plays with an adjacent bug first; the nearer of {critter, friend} is chosen; a chase not closing within `chase_patience_ticks` is abandoned and the target skipped.

- [X] T009 [P] [US2] Add `Pursuit { target: TargetRef, started: u64, closest: u32 }`, `AbandonedChase { target: TargetRef, until: u64 }`, serde-defaulted `Kitty.pursuit: Option<Pursuit>` (skip_serializing_if None) and `Kitty.abandoned_chases: Vec<AbandonedChase>` (skip_serializing_if empty) in crates/cloudkitty-core/src/kitty.rs, with serialization round-trip tests
- [X] T010 [US2] Engine pursuit bookkeeping in crates/cloudkitty-core/src/world.rs apply loop, immediately after `last_action` recording, per data-model.md order: dead-target pursuit clears without exclusion; applied Play against the pursuit target clears (catch); same-target applied Chase lowers `closest`; different-target Chase resets `{target, started: tick, closest}`; otherwise a stale pursuit (`tick − started ≥ chase_patience_ticks` and distance ≥ `closest`) moves into `abandoned_chases` with `until = tick + chase_exclusion_ticks` and clears; expired `abandoned_chases` entries pruned in the same pass; unit tests for every transition including detour-survival (interleaved eat does not reset the clock)
- [X] T011 [US2] Add shared play-target selection to crates/cloudkitty-core/src/behavior/selection.rs: candidates = critters ∪ other kitties ordered by (distance, stable id); a candidate is non-viable iff it appears in `abandoned_chases` with `until > tick`, or equals `pursuit.target` with `tick − started ≥ chase_patience_ticks` and current distance ≥ `pursuit.closest`; `travel_distance(Play)` now measures nearest *viable* candidate; unit tests: friend-nearer-than-critter chosen, exhausted-patience target skipped, excluded target skipped for its whole window, improving chase stays viable
- [X] T012 [US2] Use the shared targeting in crates/cloudkitty-core/src/behavior/needs_driven.rs `pursue(Play)` (replacing critters-then-friends) and append opportunistic play to `take_what_is_here` after the eat → drink → sunbeam-nap checks: adjacent viable critter-or-kitty + play ≥ `worth_a_detour` → `Play { target: Some(..) }`
- [X] T013 [P] [US2] Use the shared targeting for crates/cloudkitty-core/src/behavior/playful.rs play/chase choices (replacing its critters-then-friends order); keep its opportunism-first structure
- [X] T014 [US2] US2 acceptance tests in crates/cloudkitty-core/src/behavior/needs_driven.rs and world.rs test modules: bug-adjacent-while-walking-to-water plays first then resumes (acceptance 1), nearest-is-friend targets friend (acceptance 2), non-closing chase abandoned at patience and not re-selected for the full exclusion window (acceptance 3 / FR-006), two-uncatchable-targets scenario ends with both excluded so the reach test empties (I1 regression), opportunistic play never preempts adjacent eat when eat is also above threshold (edge case)

**Checkpoint**: play succeeds at a sustainable rate for cats near company; give-up ends greeble futility.

---

## Phase 5: User Story 3 — Solo play backstop (Priority: P3)

**Goal**: Play becomes self-satisfiable in the limit (research.md R5); the client renders it.

**Independent Test**: An isolated kitty with play ≥ safeguard and no viable partner within `solo_play_reach` solo-plays and its play need falls; with a partner adjacent (even sleeping), social play is chosen.

- [X] T015 [US3] Add the solo-play rule to the shared play pursuit in crates/cloudkitty-core/src/behavior/selection.rs and wire through crates/cloudkitty-core/src/behavior/needs_driven.rs: when play ≥ `thresholds.safeguard` and no viable candidate within `behavior.solo_play_reach`, propose `Play { target: None }`; viable-partner-in-reach always preferred
- [X] T016 [P] [US3] Wire the same solo rule into crates/cloudkitty-core/src/behavior/playful.rs (a playful cat alone entertains itself sooner rather than pacing)
- [X] T017 [P] [US3] Render targetless play in client/app.js `doingFor` as solo play (e.g. "pouncing at nothing 🎈"), leaving social play and greeble secrecy ("… nothing? 👻") untouched
- [X] T018 [US3] US3 acceptance tests in crates/cloudkitty-core/src/behavior/needs_driven.rs tests and a multi-tick test in crates/cloudkitty-core/src/world.rs tests: isolated kitty solo-plays and play falls at `solo_play_relief` rate (acceptance 1), adjacent partner (including a sleeping one) yields social play instead (acceptance 2 + edge case)

**Checkpoint**: no world geometry can leave play unattainable — the Article I assumption is structural now.

---

## Phase 6: User Story 4 — Fair tie-breaking at the cap (Priority: P4)

**Goal**: Ties go to the need longest without relief (research.md R3); the bath-starvation queue is impossible.

**Independent Test**: Two needs at 100 with equal travel cost → the longer-unrelieved wins; repeated ties alternate; same-seed runs identical.

- [X] T019 [US4] Add serde-defaulted `Kitty.last_relief: BTreeMap<NeedKind, u64>` in crates/cloudkitty-core/src/kitty.rs and stamp `last_relief[kind] = world.tick` inside `lower_need` in crates/cloudkitty-core/src/action.rs (single choke point — covers action, passive-sleep and partner relief paths); serialization round-trip test
- [X] T020 [US4] Upgrade the tie-break in crates/cloudkitty-core/src/behavior/selection.rs: equal scores → smallest `last_relief` value (missing = 0) → `NeedKind::ALL` order as final deterministic fallback
- [X] T021 [US4] US4 acceptance tests in crates/cloudkitty-core/src/behavior/selection.rs tests: bath-vs-play tie at the cap goes to longer-unrelieved bath (acceptance 1), repeated engineered ties alternate rather than repeating, and two identical seeded decision contexts choose identically (acceptance 2 / SC-006 unit-level)

**Checkpoint**: with US1+US4, no need can be permanently shadowed at the cap.

---

## Phase 7: User Story 5 — Trouble is visible while it is happening (Priority: P5)

**Goal**: Per-need distress age in the payload; gentle cue in the panel (research.md R6). Independent of US1–US4.

**Independent Test**: Drive one need into sustained distress → API reports its unresolved duration; the panel cue appears after `viewer.distress_patience_ticks` and clears on recovery.

- [X] T022 [P] [US5] Add serde-defaulted `Kitty.distress_since: BTreeMap<NeedKind, u64>` (skip_serializing_if empty) in crates/cloudkitty-core/src/kitty.rs with round-trip test
- [X] T023 [US5] Maintain `distress_since` in the needs phase of crates/cloudkitty-core/src/world.rs beside the existing edge-trigger: crossing inserts current tick, recovery removes, self-heal inserts current tick for any `in_distress` member missing an entry (pre-004 resume); unit tests for all three transitions
- [X] T024 [US5] Add invariants to crates/cloudkitty-core/src/invariants.rs: `distress_since` keys == `in_distress` members post-needs-phase; `pursuit.ticks ≥ 1` and sane `closest` when present (covers US2's field too — this file is touched once)
- [X] T025 [P] [US5] Server integration test in crates/cloudkitty-server/tests/server_integration.rs: `/world` kitty payload carries `distress_since` for a distressed kitty and omits it when empty; `/config` echoes `viewer.distress_patience_ticks`
- [X] T026 [P] [US5] Client cue in client/app.js and client/index.html: read `viewer.distress_patience_ticks` from `/config`, adding the `/config` fetch if the client does not already perform one and defaulting gracefully if it is unavailable (no hard-coded threshold); when any `world.tick − distress_since[need]` exceeds it, show a gentle caring cue on the kitty card (longest-running distress only — no stacked alarms); clears on recovery; style `.kitty-card .patience` in index.html

**Checkpoint**: the next lock-in-shaped bug announces itself in one glance (SC-007).

---

## Phase 8: Polish, Verification & Doc Reconciliation

**Purpose**: Encode the success criteria as permanent guards; reconcile amended MVP docs (constitution: spec and code must agree).

- [X] T027 [P] Create crates/cloudkitty-core/tests/welfare_longrun.rs per research.md R10: one seeded 20,000-tick default-shaped run asserting SC-001 (no >100-consecutive-tick stretch below happiness 45), SC-002 (floor never touched; ≤5% of ticks below 45 per kitty), SC-003 (no need within 1.0 of cap for >25 consecutive ticks while zero-distance relief exists — per the SC-003 definition: bath/sleep always, play always once solo exists, cuddle when a kitty is adjacent, eat/drink when the resource is adjacent), SC-004 (no distress age >150; mean happiness ≥ 65), SC-006 (second same-seed run tick-for-tick identical)
- [X] T028 [P] Create crates/cloudkitty-core/tests/stuck_state_regression.rs: deserialize specs/004-fix-happiness-lockin/stuck-state-tick1465.json and load its frozen config fixture specs/004-fix-happiness-lockin/stuck-state-config.toml (checked in beside the snapshot — do NOT read the live repo cloudkitty.toml, which the operator tunes); run 300 ticks; assert bath and sleep unpin within 25 ticks and the stuck kitty's happiness exceeds 60 within 300 (SC-005); doctored critters-far variant proves solo play alone carries play downward
- [X] T029 Extend crates/cloudkitty-core/tests/invariants_proptest.rs: new fields hold their invariants across randomized runs; a world JSON stripped of the three new fields (pre-004 shape) deserializes and ticks lawfully
- [X] T030 Extend crates/cloudkitty-core/tests/behavior_variation.rs: both profiles remain distinct (playful still plays materially more) and neither exhibits lock-in (no need pinned at cap >25 ticks with zero-distance relief available) over the comparison run
- [X] T031 [P] Reconcile MVP docs amended by this feature: specs/001-cloudkitty-mvp/data-model.md (Kitty fields, Action Play shape, needs tie-break note → pointer to 004), specs/001-cloudkitty-mvp/contracts/http-api.md (kitty payload additions → pointer to 004 delta), specs/001-cloudkitty-mvp/contracts/behavior.md (Play optionality, DecisionContext additions → pointer to 004 delta)
- [X] T032 Run the full gate per quickstart.md §1–2: `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, plus the backward-compat resume of the archived fixture via the release binary
- [X] T033 Manual quickstart pass per quickstart.md §3–4: live server observation (no fixation, opportunistic play, greeble give-up via `g`, solo play copy, gentle cue appearance/clearing — SC-007) and the 5-minute welfare spot-check beating the 14–22% below-45 baseline

---

## Dependencies

```
Phase 1 (T001–T002)  ──►  everything
Phase 2 (T003–T004)  ──►  US2, US3 (Play shape); US1 unaffected
US1 (T005–T008)      ──►  US2 (selection.rs exists), US4 (tie-break site)
US2 (T009–T014)      ──►  US3 (viability rule feeds solo-reach test)
US4 (T019–T021)      ──►  independent of US2/US3 after US1
US5 (T022–T026)      ──►  independent of US1–US4 entirely (Phase 1 only)
Phase 8              ──►  T027/T028/T030 need US1–US4; T029 needs all fields
                          (T022 included); T031 anytime after Phase 2
```

Story completion order: **US1 → US2 → US3**, with **US4** insertable any time after US1 and **US5** parallel to everything.

## Parallel Opportunities

- After Phase 1: US5 (T022–T026) can proceed in parallel with Phases 2–6 — different files end to end except invariants.rs (T024, scheduled once for both stories' fields)
- Within US1: T007 (playful.rs) ∥ T006 (needs_driven.rs) once T005 lands
- Within US2: T009 (kitty.rs) ∥ T011 prep; T013 (playful.rs) ∥ T012 (needs_driven.rs)
- Within US3: T016 (playful.rs) ∥ T017 (client) ∥ T015 tail
- Phase 8: T027 ∥ T028 ∥ T031 (different files)

## Implementation Strategy

**MVP = US1 alone** (with Phases 1–2): removing the safeguard lock is the
single highest-welfare change and is shippable by itself — even with today's
play throughput, kitties stop ignoring zero-distance relief, which caps
episode depth immediately. Each subsequent story is an independently
testable increment: US2 restores play throughput, US3 makes lock-in
structurally impossible, US4 closes the tie-break hole, US5 makes any future
regression visible. Phase 8 then freezes the welfare gains as CI-guarded
regression bounds before the PR.
