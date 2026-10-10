# Tasks: Parameterized Teacher Rework

**Input**: Design documents from `specs/059-teacher-rework/`
(plan.md, research.md R1–R14, data-model.md, contracts/, quickstart.md)

**Prerequisites**: branch `product/teacher-rework` at 2f80adf8+, merged
past eb9e860b (the consent ruling is in-tree)

**Tests**: INCLUDED — house rules 5/6 make red-first guards part of the
work, not optional. Every new/changed assertion goes through
`scripts/mutate.sh --expect <prediction>` with the prediction stated
first; the rule-6 sorted piles live in contracts/consent-gate.md and
contracts/cue-answer.md.

**Organization**: by user story (US1 one teacher + consent gate, US2
imitability audit, US3 cue-answer rungs).

## Phase 1: Setup

- [X] T001 Record the rule-6 baseline: run `cargo test --workspace` in
      the worktree and note suite counts (the must-pass pile is read,
      not only run) in the eventual PR self-review notes

## Phase 2: Foundational (blocking all stories)

- [X] T002 [P] Move `COMFORT_SLACK_NORMALISER` (40.0) into
      crates/cloudkitty-core/src/config/mod.rs and add
      `Config::slack_cell_for(kitty_id) -> f32`; rewire
      crates/cloudkitty-rl/src/observe.rs:765-771 to call it and
      re-export the constant for crates/cloudkitty-rl/tests/schema_six_pins.rs
      (which must stay green UNEDITED — must-pass)
- [X] T003 [P] Add `[behavior] response_commitment_ticks` (f32, default
      3.0) in crates/cloudkitty-core/src/config/mod.rs; validation in
      the shared finite-non-negative loop in
      crates/cloudkitty-core/src/config/validate.rs; mutate red on the
      validation guard (prediction: a negative value passes validate)
- [X] T004 Create crates/cloudkitty-core/src/behavior/teacher.rs
      skeleton (`Teacher { preset, wander, groom_response, luxury }`
      per data-model.md) and register the three preset rows in
      `with_builtins` (behavior/mod.rs:141-146); rewire the hard-wired
      fallback (mod.rs:370 and 485-487) to the needs_driven preset
      instance; `every_builtin_declines_a_snapshot_dead_scene`
      (mod.rs:624-650) must pass with the new `teacher` entry

## Phase 3: US1 — One teacher, dialed per cat + target-side consent (P1)

**Goal**: presets byte-equal outside consent sites; the engine gate per
ruling eb9e860b; each dial moves behavior independently.

**Independent test**: SC-001 recorder + SC-004 dial tests + the
consent-gate guard battery (quickstart.md map).

- [X] T005 [US1] RED FIRST (rule 6 must-fail pile): with predictions
      stated per test, observe the four old consent guards fail
      against the coming change — playful.rs:156-240 battery
      (`a_serious_playful_cat_honors_the_consent_line`,
      `an_adjacent_burdened_friend_is_not_batted_into_a_game`,
      `blocking_the_only_playmate_may_buy_solo_play…`) and
      `needs_driven_opportunism_ignores_the_consent_line`
      (needs_driven.rs:688-720); record each red in the self-review
      notes
- [X] T006 [US1] Implement the engine consent gate per
      contracts/consent-gate.md: a step after `action::validate` in
      `run_applied_phases_from_decisions`
      (crates/cloudkitty-core/src/world.rs:352-376) AND
      `apply_slot_verdict` (world.rs:580-595); `Play{Kitty}` only;
      predicate `top_non_play(target) > consent_line_for(target) &&
      top_non_play(target) > target.play`, line ≤ 0 open; add
      `RefusalReason::ConsentDeclined` in
      crates/cloudkitty-core/src/events.rs:93-104 and the consent arm
      in `refusal_reason` (crates/cloudkitty-core/src/action.rs:442-460)
- [X] T007 [US1] Delete proposer-side consent: the filters at
      crates/cloudkitty-core/src/behavior/selection.rs:564, :618, :929;
      collapse `take_what_is_here_consenting` (needs_driven.rs:143) and
      `choose_consenting` (selection.rs:55) into the plain forms;
      rewrite the T005 guards against the engine gate (same protected
      scenarios, new enforcement site) and see them green for the
      stated reason
- [X] T008 [P] [US1] Mask consent-blindness guard in
      crates/cloudkitty-rl/tests/: `legal_action_mask` output is
      identical under hidden target-need extremes with a consent line
      set; mutate red (prediction: moving the gate inside
      `action::validate` flips PlayKitty mask bits → guard fails)
- [X] T009 [US1] Gate guards via scripts/mutate.sh --expect, one cycle
      each in crates/cloudkitty-core/tests/: refuses at the TARGET's
      per-kitty line not the world line; stamps `consent_declined`;
      a line ≤ 0 world is byte-identical at consent sites
- [X] T010 [US1] Move the needs_driven ladder into Teacher
      (finish_what_you_started, take_what_is_here, groom_response,
      wander with its exact RNG short-circuit, pursue) in
      crates/cloudkitty-core/src/behavior/teacher.rs; the
      `needs_driven` registration is the toggled Teacher; existing
      needs_driven.rs unit tests (680-2574) stay green against it,
      including the 057 sleep-floor guards — FR-006's must-pass pile;
      read, not only run
- [X] T011 [US1] Move playful into Teacher (get-serious weighted line,
      luxury `scored_play_action`) with playful toggles; the
      comfort_weight battery (playful.rs:367-479) and remaining playful
      tests stay green against the preset
- [X] T012 [US1] Slack gate on luxury entry in teacher.rs:
      `now − last_relief_tick ≥ slack_cell_for(me) × 40` (kitty.rs:436
      state, no new field); slack-0 inert; SC-004 unit test (higher
      slack returns to luxury later by the tick difference, gate reads
      the cell value incl. clamp); mutate red (prediction: gate reading
      raw slack instead of the cell breaks the clamp case)
- [X] T013 [US1] Favourite weights in the partnered pursuit comparison
      (`value × (1 + favourite_weight_for(me, kind))`) in teacher.rs /
      selection.rs; all-zero byte-inert; SC-004 equal-value tip test;
      mutate red
- [X] T014 [US1] Stream recorder (fog_continuity.rs `record_streams`
      pattern, crates/cloudkitty-core/tests/): per-tick action+message
      digests, old brains vs presets, on cloudkitty.toml AND
      experiments/fog-gen1-cert/anchor-b3.toml; emits the per-site
      fired/decision-moved counts as JSON
- [X] T015 [US1] FR-015 (ordering gate: BEFORE SC-001 freezes): run the
      recorder, fill the counter columns in
      specs/059-teacher-rework/contracts/audit-record.md, commit the
      raw JSON beside the recorder fixtures; THEN freeze the SC-001
      stream-equality assertions (equal everywhere except
      recorder-marked consent ticks; scale sanity vs
      experiments/biscuit3-comfort-sweep-2026-09-01/RESULTS.md:370-395)
- [X] T016 [US1] Must-pass confirmations: `evolution_golden` green with
      the fixture SHA unchanged; SC-004 per-kitty consent test (a
      kitty's own line refuses at ITS value — target-side); full
      cloudkitty-core suite counts recorded, with the 057 floor tests
      individually named in the self-review must-pass list (FR-006)

## Phase 4: US2 — The imitability audit (P1)

**Goal**: zero teacher decision reads of hidden friend state;
per-site record complete.

**Independent test**: SC-002 sweep + SC-003 twin (quickstart.md).

- [X] T017 [US2] Re-key `partner_value`
      (crates/cloudkitty-core/src/behavior/selection.rs:693): play-need
      term → freshest audible WantPlay intensity (0 when silent);
      w_serious term → sum of the partner's audible non-play want
      intensities; byte-inert at the committed all-zero 042 dials
      (recorder confirms); unit test at nonzero dials + mutate red
- [X] T018 [US2] Remove `top_non_play` from the behavior layer
      (selection.rs:702) — its only home is the engine consent step;
      grep-level sweep of crates/cloudkitty-core/src/behavior/ for
      friend `needs.get`/`happiness` reads, confirming only the
      retained bath sites (audit-record.md rows 1-3) remain
- [X] T019 [P] [US2] SC-003 twin test in crates/cloudkitty-core/tests/:
      paired teacher decisions over randomized hidden friend states are
      identical (consent gate excluded — engine-side, target-keyed);
      mutate red (prediction: reintroducing the selection.rs:693 hidden
      play read fails the pair)
- [X] T020 [US2] Finalize
      specs/059-teacher-rework/contracts/audit-record.md: every row
      resolved with its enforcement test named; SC-002's sweep output
      recorded in the file

## Phase 5: US3 — Cue-answer rungs (P2)

**Goal**: demonstrable answering keyed to digest-visible calls, gated
and bounded per contracts/cue-answer.md.

**Independent test**: SC-005 + the guards-owed list.

- [X] T021 [US3] Response term + fire condition in
      crates/cloudkitty-core/src/behavior/teacher.rs:
      `intensity ≥ max(reply_intensity_floor, top_pressure(me)/100)`,
      valuation-only on partnered rest (WantCuddle) / friend play
      (WantPlay) via `meow::freshest_audible`; derived constants
      (I_min, HANDSHAKE_TICKS, D_w, k, h) in their one documented
      home; response terms apply in serious pursuit only, never
      inside `scored_play_action` (no double-count); and the FR-011
      validator WARN (digest_window_ticks vs typical approach
      distance) in crates/cloudkitty-core/src/config/validate.rs with
      its own mutate cycle
- [X] T022 [US3] FR-016 contention in teacher.rs: feasibility filter
      (`d ≤ window_remaining − HANDSHAKE_TICKS`), `score =
      intensity − k·d`, tie chain score → intensity → nearer → lower
      id, commitment margin h against a mid-approach challenger.
      FIRST verify the incumbent (the answered caller mid-walk) is
      derivable from existing state (activity/pursuit target); if it
      is not, STOP and surface the choice — a new Kitty field is a
      serialization + golden-digest change the plan currently claims
      to avoid (it would ride the FR-014 re-record, but the plan.md
      Storage line and data-model.md must be amended before coding it)
- [X] T023 [US3] The guards-owed battery
      (contracts/cue-answer.md), each via scripts/mutate.sh --expect:
      term present in-window / absent one tick past; threshold both
      directions; feasibility drops a louder-unreachable caller;
      iso-line flip (spec US3 scenario 5); margin holds an in-margin
      challenger; free-register deafness (armed trill/ekekek moves
      nothing); scripted emission stays want/here-only (a guard on
      `announce` that reds if any free-register kind is emitted —
      FR-012's emission half, pinning behavior/mod.rs:504-537);
      consent + adjacency unchanged after the term (staging per
      research R13: emit while hearer busy)
- [X] T024 [US3] SC-005 sample: run
      experiments/tools/bc-collect on a seeded `teacher` roster;
      confirm nonzero answered-call rate, zero response outside digest
      visibility, zero consent/adjacency bypass; record the numbers in
      the self-review notes. Corpus labeling is Experiments' lane —
      their call (e1b3e095): bc-collect gains a `label_proposed`
      action column, applied labels unchanged. While sampling, check
      their mask-legality expectation (a consent-refused proposal
      should always be mask-legal); a counterexample is a FINDING to
      report to them, never silently dropped

## Phase 6: Polish & close

- [X] T025 [P] Update the dial doc comment
      (crates/cloudkitty-core/src/config/mod.rs:346-353 — "the teacher
      doesn't read them yet" is now false) and the `[behavior]` docs
      for response_commitment_ticks
- [X] T026 [P] CHANGELOG.md Unreleased entry (public-voice at write
      time) and specs/INDEX.md gains 059
- [X] T027 Fresh binding: `VIRTUAL_ENV=… maturin develop` then
      `pytest crates/cloudkitty-py/tests` (local merge gate; the
      scratchpad ckpy venv is stale until rebuilt); confirm
      `ParallelEnv(control={…:"teacher"})` resolves
- [X] T028 SC-006: both shipped-config sweeps green with ZERO config
      edits (`cargo test -p cloudkitty-core --test shipped_configs`,
      `-p cloudkitty-rl --test shipped_configs_rl`); full workspace run
      with counts vs the T001 baseline
- [X] T029 Spec-058 T024 obligation (FR-014): re-run the friend-field
      read sweep over the final tree, re-verify 058's FR-011 strip
      list, record the result in
      specs/058-gen2-observation-schema/contracts/observation-v6.md
- [X] T030 Quickstart end-to-end smoke (server starts with the three
      registry names; consent refusal visible as `consent_declined`;
      a staged answer walk completes) and assemble the PR self-review
      (rule-6 sorted lists, every mutate cycle's prediction/outcome)

## Dependencies

- Phase 2 → everything. T004 → T005+ (the Teacher must exist to move
  logic into).
- US1 internal: T005 → T006 → T007 (red before the gate, gate before
  deletion); T010 → T011 → T012/T013 (ladder before its gates);
  T014 → T015 → the SC-001 freeze inside T015; T016 last.
- US2 depends on US1's T007/T010 (the sites it re-keys must be in
  their final home). T017 → T018; T019/T020 after.
- US3 depends on T004 + T021 → T022 → T023 → T024; independent of US2.
- Phase 6 last; T029 after all behavior edits; T027/T028 after any
  source change.

## Parallel opportunities

- T002 ∥ T003 (different config surfaces).
- T008 ∥ T009 (different crates) once T006 lands.
- T019 ∥ T020 after T017/T018.
- T025 ∥ T026 anytime after US1-US3 stabilize.

## Implementation strategy

US1 is the MVP: with it merged-able, the corpus could be collected on
dialed teachers with consent ruled correctly even if US3 slipped.
US2 is the honesty proof on top; US3 is additive demonstrations.
Deliver in that order, one worktree, single PR per the house pattern
(push → PR → self-review comment → CI green → merge).
