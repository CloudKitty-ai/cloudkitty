# Tasks: Contagion Membership Dial + Charge-Aware Ladder

**Input**: Design documents from `specs/045-contagion-membership/`
(spec.md, plan.md, research.md D1–D9, data-model.md,
contracts/config-surface.md, quickstart.md)

**Discipline**: CLAUDE.md rules 5/6 — every new assertion goes red first
via the exact bug it catches, recorded in `redden-list.md`; kept
behavior sorted into the must-pass pile before suite runs; READ THE
COUNT after every run. Two-commit delivery (plan): commit 1 = inert
config surface, commit 2 = engine branch + ladder + tests + docs.

## Phase 1: Setup

- [X] T001 Run `cargo test --workspace` at the branch tip and create
  `specs/045-contagion-membership/redden-list.md` with the baseline
  count, the default-config stamp sha (must equal `6c73f894…`), and the
  044-style cycle table header.

## Phase 2: Foundational (config surface — blocks all stories; commit 1)

- [X] T002 Add `ContagionMembership` enum (`OptionA` default /
  `Bidirectional`; TOML `"option_a"` / `"bidirectional"`; `is_option_a`
  helper) and the `WaterConfig.contagion_membership` field with
  `#[serde(default, skip_serializing_if =
  "ContagionMembership::is_option_a")]` + doc comment naming the owner
  ruling context, in `crates/cloudkitty-core/src/config/mod.rs`.
- [X] T003 Add `bool_is_false` helper beside `f32_is_zero` and the
  `BehaviorConfig.contagion_aware_ladder` field (`#[serde(default,
  skip_serializing_if = "bool_is_false")]`) + doc comment, in
  `crates/cloudkitty-core/src/config/mod.rs`.
- [X] T004 Stamp + parse-equality tests in `config/mod.rs` tests:
  default serialization contains NEITHER new key; explicit
  `contagion_membership = "option_a"` and `contagion_aware_ladder =
  false` parse equal to absent. Red-first: remove each
  `skip_serializing_if` attr in turn (leaked-key red), restore; record
  both cycles in redden-list.
- [X] T005 Unknown-variant rejection test in `config/mod.rs` tests: a
  `[water]` table with `contagion_membership = "both"` is rejected and
  the error message names `option_a` and `bidirectional`. Natural red:
  written against the enum before checking serde's message; if serde's
  message is opaque, add the clearer wrapper research D8 allows.
- [X] T006 Commit 1 (inert surface): full workspace suite green, count
  recorded, stamp sha byte-equal to baseline, `git status` clean.

## Phase 3: User Story 1 — Bidirectional membership for the lab arms (P1)

**Goal**: `bidirectional` admits the referenced dry adjacent cat to the
existing charge; `option_a` stays byte-identical 044.

**Independent test**: quickstart §2 — the membership differential suite
alone proves the story.

- [X] T007 [US1] Red-first differential tests in
  `crates/cloudkitty-core/tests/waterline_contagion.rs`: for each
  paired kind, the referenced dry adjacent cat moves `ambient + charge`
  under `bidirectional` and `ambient` only under `option_a`, while the
  NAMER's charge is equal under both. Run before T010: the
  bidirectional arms red naturally (engine still behaves as option_a);
  record the observed reds.
- [X] T008 [US1] Red-first multi-payer test in
  `tests/waterline_contagion.rs`: two wet groomers referencing one dry
  adjacent cat move it by exactly `ambient + one charge` (FR-003).
  Reds pre-implementation; record.
- [X] T009 [US1] Kept-behavior arms in `tests/waterline_contagion.rs`,
  sorted must-pass per rule 6: under `bidirectional`, the non-adjacent
  referenced cat and the wet member stay uncharged (adjacency gate and
  wet exemption are membership-independent); both-dry and both-wet
  scenes unchanged. These must be green before AND after T010.
- [X] T010 [US1] Implement the bidirectional arm in `advance_needs`
  (`crates/cloudkitty-core/src/world.rs`): pre-collect `wet_namers`
  (BTreeMap of wet cats' `Activity::partner()` targets) inside the
  existing factor-gated snapshot, extend the `contagious` filter with
  the membership check + `is_available_friend(wet, dry)`. T007/T008
  green, T009 still green; update the snapshot comment (Option A
  wording → membership-aware).
- [X] T011 [US1] Unit-layer referenced-role adjacency test in
  `world.rs` `mod tests` (the 044 mid-tick layer): a wet cat naming a
  dry partner two tiles away charges nothing under `bidirectional`;
  adjacent positive control pays. Red-first: delete the
  `is_available_friend` call from the new arm, predict the exact
  failure, observe, restore; record.
- [X] T012 [US1] Budget membership-invariance arm in `config/mod.rs`
  tests (FR-008): the 044 near-budget accept and reject configs
  accept/reject IDENTICALLY with `contagion_membership =
  "bidirectional"` added. Natural red channel: assert against the
  option_a outcomes recorded first; a divergence is the bug this
  catches.
- [X] T013 [US1] Boot log (FR-009): the armed contagion line in
  `crates/cloudkitty-server/src/main.rs` names the active membership
  rule in both variants; disabled line unchanged. Verify by running the
  server against a lab TOML in both states (quickstart §6).
- [X] T014 [US1] Same-seed determinism arm in
  `tests/waterline_contagion.rs`: two 500-tick runs, factor 1.0 +
  `bidirectional`, identical worlds — and within the same arm assert
  the legal-action mask of a charged cat equals the mask of its
  uncharged twin in the option_a run at the same tick (FR-007: the
  membership dial moves prices, never legality). Carry 044 T017's
  recorded no-honest-red caveat forward in redden-list rather than
  hiding it; the mask assertion has its own red channel (point it at a
  fake legality hook to prove it can fail).

## Phase 4: User Story 3 — The served world never notices (P1)

**Goal**: defaults byte-identical, provably.

**Independent test**: quickstart §1 + §4.

- [X] T015 [US3] Run `cargo test -p cloudkitty-core --test
  evolution_golden` unregenerated and re-assert the stamp sha equals
  baseline; record both in redden-list.
- [X] T016 [US3] Seeded byte-identity test in
  `tests/waterline_contagion.rs` (or the config integration suite per
  repo idiom): a 500-tick run under the explicit-default TOML
  (`"option_a"` + `false`) is byte-identical to the absent-key config
  run. Red channel shares T004's recorded skip-attr cycles (044 T017
  precedent — say so in redden-list).
- [X] T017 [US3] Run both config sweeps and validate the served TOML
  unchanged (`cargo test --workspace` covers the sweeps): zero edits to
  any existing config, READ THE COUNT, record.

## Phase 5: User Story 2 — A ladder that can feel the charge (P2)

**Goal**: gated scene-total exposure pricing at the three chooser seams;
off = byte-identical.

**Independent test**: quickstart §3.

- [X] T018 [US2] Red-first unit tests for the exposure helper in
  `crates/cloudkitty-core/src/behavior/selection.rs` tests: payer sets
  per membership (option_a: decider iff dry-with-wet-partner;
  bidirectional: each dry member with a wet counterpart; both-dry and
  both-wet → zero), ceiling cap `max(0, ceiling − payer.bath)`,
  `E_ticks` = `bounds.min` per D5 mapping (play/cuddle/sleep + the
  verified groom mapping), `bath_ratio(payer)` not decider. Written
  before T019 — natural reds (helper absent → compile fail counts,
  record per 044 T003 precedent).
- [X] T019 [US2] Implement `expected_scene_exposure(ctx, kind, partner)`
  in `behavior/selection.rs`, short-circuiting to 0 BEFORE any
  arithmetic when `contagion_aware_ladder` is false or
  `contagion_factor × bath_gain` is 0. T018 green. Verify the D5 groom
  duration mapping against the activity code here and record the
  finding in the config doc comment.
- [X] T020 [US2] Red-first `scored()` seam in `behavior/selection.rs`:
  at cranked factor the exposed Friend/Playmate need scores strictly
  below its unexposed twin; gate off ⇒ scores unchanged. Inject the
  seam AFTER observing the red (test written first); record.
- [X] T021 [US2] Red-first `play_score()` seam in
  `behavior/selection.rs`: a dry playmate outranks an otherwise-equal
  wet one at cranked factor; equal rank at factor 0.0 with gate on.
  Record the red.
- [X] T022 [US2] Red-first groom seam in
  `behavior/needs_driven.rs` (`groom_response`): decline iff scene
  exposure > groomee bath pressure + groomer's expected
  `groom_cuddle_relief` value (scene-total both sides, per Experiments
  review point 2 — verify the relief dial's source at implementation);
  a net-positive groom is still proposed. BEFORE writing the seam,
  enumerate every groom-initiation path (`groom_response` AND any
  `pursue` Friend-arm route from the 041 groom-for-cuddle channel) and
  either seam each or record why the T020 `scored()` seam already
  prices it. Record the red.
- [X] T023 [US2] Gate-off byte-identity in `behavior` tests: seeded
  scripted run with `contagion_aware_ladder = false` ≡ pre-045 run;
  with gate on + factor 0.0 ≡ gate off (043 gate-equality idiom). Red
  channel: temporarily hard-enable the gate, predict divergence,
  observe, restore; record.
- [X] T024 [US2] Ladder boot log line in
  `crates/cloudkitty-server/src/main.rs` emitted ONLY when the gate is
  on; default boot log byte-identical (contract). Manual verify per
  quickstart §6.
- [X] T025 [US2] Determinism arm: same-seed identical with gate on +
  cranked factor + each membership value (`tests/waterline_contagion.rs`
  or behavior tests per idiom) — and assert the ladder changed only
  PROPOSALS: the legal-action mask for a cat facing an exposed scene is
  identical with the gate on and off at the same tick (FR-007 armed
  case; Article IV).

## Phase 6: Polish & Cross-Cutting

- [X] T026 Update `docs/wet-fur-pricing.md`: membership paragraph
  (either-role rule, one-charge cap, budget invariance), ladder
  paragraph (scene-total shape, min-bounds horizon, wet-now scope
  disclosure pointer to research.md D4), "Where the law lives"
  additions.
- [X] T027 Add the spec-045 one-liner to `## Unreleased` in
  `CHANGELOG.md` (no compatibility markers — nothing moves at
  defaults).
- [X] T028 Final gate: `cargo clippy --workspace` + `cargo fmt --check`
  clean; full `cargo test --workspace`, READ THE COUNT against
  baseline + new-test arithmetic; redden-list complete (every Phase
  3/5 assertion has a recorded cycle); commit 2; `git status` clean.

## Dependencies

- T001 → everything.
- Phase 2 (T002–T006) blocks Phases 3–5 (both dials' fields must
  exist).
- US1 (T007–T014) and US2 (T018–T025) are independent of each other
  EXCEPT T018's membership payer-set arms want T010 merged semantics to
  test against — run US1 first (also priority order).
- US3 (T015–T017) runs after US1 (it certifies the engine branch's
  inertness) and re-runs implicitly in T028 after US2.
- Polish (T026–T028) last.

## Parallel Example

- T002 ∥ nothing (T003 same file — sequential).
- After T006: T007, T008, T009 are one file — write together,
  sequential; T013 (server) can proceed [P] alongside T007–T012 (core).
- After T019: T020/T021 (selection.rs) sequential; T022
  (needs_driven.rs) [P] with them; T024 (server) [P] with any core
  task.

## Implementation Strategy

MVP = Phase 2 + US1 + US3 (commit 1 + the membership half of commit 2):
that alone unblocks smoke arms A/B and the engine half of D/E, and is
independently shippable inert. US2 completes arms C/D/E. Stop-and-report
per CLAUDE.md rule 4 if any red-first cycle refuses to red after ~3 real
attempts.
