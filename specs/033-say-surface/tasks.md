# Tasks: Say-Surface Finalization

**Input**: Design documents from `/specs/033-say-surface/`

**Prerequisites**: plan.md, spec.md, research.md (decisions D1–D8),
data-model.md, contracts/say-surface-v3.md, contracts/artifact-pins-delta.md

**Tests**: INCLUDED — TDD is house law (Article VI; fix criteria, then loop).
Every test task is written first and verified failing for the right reason.

**Organization**: by user story after a foundational phase. Note: this
feature's stories share one engine surface (the enum, the config, the
pins), so the foundational phase is heavier than usual and the stories are
thin verification+integration slices over it — that is the honest shape of
a schema wall, not a layering failure.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: pin the pre-wall baseline so every later diff is attributable.

- [x] T001 Verify green baseline: run `cargo test --workspace` in the 033
      worktree at branch point; record pre-wall derived numbers (HEAD_KINDS
      8, head 9, digest 32, obs 197, mask 9, logits 43) in the task log to
      compare against contracts/say-surface-v3.md's Post column.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the vocabulary, config, and pin turns every story sits on.

**⚠️ CRITICAL**: no user story work until this phase compiles green
(except the parity gate, which is expected red until T021 — see note).

- [x] T002 [P] Write FAILING schema-four pin test in
      `crates/cloudkitty-rl/tests/schema_four_pins.rs`: asserts the full
      derived chain against contract literals (HEAD_KINDS 15, head 16,
      message mask 16, MEOW_DIGEST 60, observation_len 225 at served slots,
      menu 34, v3 logits 50) plus kitty_slots == 3 (FR-011).
- [x] T003 [P] Write FAILING rename pin test (same file or
      `crates/cloudkitty-core/src/meow.rs` tests): Mew serializes to
      `mew`, sits at head index 3 / digest column 2, legality cooldown-only
      (byte-identical to pre-rename FollowMe semantics, SC-004).
- [x] T004 Extend `MessageKind` in `crates/cloudkitty-core/src/meow.rs`:
      rename FollowMe → Mew; append HereFood, HereWater, HereCritter,
      HereSunbeam, Chirp, Trill, Ekekek (wire names per contract);
      `related_need()` exhaustive — Some(need) for want-kinds only, None
      for Purr/WaitForMe/Here*/sound-words (no unreachable left).
- [x] T005 Extend `HEAD_KINDS` in `crates/cloudkitty-rl/src/observe.rs` to
      15 (Mew in FollowMe's slot, seven appended in contract order); update
      the module doc-comment's digest description.
- [x] T006 Add `VocabularyConfig` to `crates/cloudkitty-core/src/config/mod.rs`
      per research D3: fifteen named bools on `MeowConfig` as
      `[meow.vocabulary]`, per-field serde defaults (trill/ekekek false),
      deny_unknown_fields, validation message naming the field.
- [x] T007 [P] Add `World::adjacent_critter(pos)` in
      `crates/cloudkitty-core/src/world.rs`: ∃ element `is_critter() &&
      pos.is_adjacent(e.pos)`; doc-comment binds it to Play-critter's
      validate arm (research D2).
- [x] T008 Restructure `message_legal` in `crates/cloudkitty-core/src/meow.rs`
      into explicit tiers (research D1): want (need-armed + cooldown), Purr
      (`purr_earned` + cooldown), Here* (T007/existing predicates +
      cooldown), free register (cooldown), WaitForMe (cooldown, engine-only,
      NOT flag-gated); every speakable arm additionally checks its
      `[meow.vocabulary]` flag. Depends on T004, T006, T007.
- [x] T009 Turn the four version constants: `OBSERVATION_SCHEMA_VERSION` 3→4
      (`crates/cloudkitty-rl/src/observe.rs`), `ACTION_SCHEMA_VERSION` 2→3
      (`crates/cloudkitty-rl/src/codec.rs`), `MASK_SCHEMA_VERSION` 2→3
      (`crates/cloudkitty-rl/src/mask.rs`), `PROPOSAL_WIRE_VERSION` 1→2
      (`crates/cloudkitty-core/src/action.rs`).
- [x] T010 Sweep compile/test fallout across the workspace: FollowMe
      mentions in `crates/cloudkitty-core/src/behavior/test_behaviors.rs`
      and `crates/cloudkitty-core/src/action.rs`; every existing test that
      enumerates kinds or hardcodes pre-wall widths (digest
      freshest-emitter test, codec roundtrip fixtures, `test_support`
      derivations, timing test dims). T002 and T003 now PASS; `cargo test
      --workspace` green EXCEPT `artifact_v3_parity` (stale oracle —
      expected red until T021, never `#[ignore]`d).

**Checkpoint**: engine speaks schema 4; the vocabulary exists and is
law-correct by unit tests; parity gate awaiting the oracle swap.

---

## Phase 3: User Story 1 — A cat can announce what is here (P1) 🎯 MVP

**Goal**: the Here family lands end-to-end: grounded legality, broadcast,
digest with emitter tracking and intensity 0.0.

**Independent Test**: place a cat at each referent; the matching Here kind
is legal there, illegal elsewhere; hearers' digests carry the speaker's
live offset; `recent_meows` serves the event.

- [x] T011 [P] [US1] Write FAILING legality tests in
      `crates/cloudkitty-core/src/meow.rs` (or `tests/`): each Here kind ×
      {at referent → legal; bare grass → Silent; empty bowl → Silent
      (US1/AC3); far-away critter with Chase-legal target → Silent
      (US1/AC4); beamless tile → Silent (US1/AC5)}; cooldown applies
      (spec-028 machinery). PLUS the announce-then-consume boundary test
      (US1/AC6, FR-016 + FR-005): emit HereFood at a stocked bowl
      (accepted), eat it empty (bowl despawns) — assert the eat proceeded
      normally (relief granted, no downgrade, no penalty, ordinary
      needs/happiness path) AND the HereFood digest entry persists for its
      normal freshness window still tracking the speaker (announcements are
      never retracted when the referent dies — emitter-tracking and
      emission-time truth in one observable).
- [x] T012 [P] [US1] Write FAILING grounding property test (SC-002) in
      `crates/cloudkitty-core/tests/`: randomized worlds/behaviors over
      thousands of ticks — every accepted Here* emission implies its
      predicate at that tick; every predicate-true proposal refused only by
      cooldown or flag.
- [x] T013 [P] [US1] Write FAILING digest integration test in
      `crates/cloudkitty-rl/src/observe.rs` tests: an emitted HereFood
      appears in every OTHER kitty's digest at column 8 as [recency, dx,
      dy, 0.0] tracking the SPEAKER's live position across a subsequent
      move (emitter-tracking, FR-005); intensity exactly 0.0 (clarify
      verdict). Then the SC-001 breadth loop in the same harness: iterate
      all five active new kinds (four Here* at their referents, chirp
      anywhere) — each emits, lands in hearers' digests at its contract
      column within the freshness window, intensity 0.0.
- [x] T014 [US1] Make T011–T013 pass: wire the Here* arms' emission path —
      `Meow` stamped with intensity 0.0 for all non-want kinds at the
      message-application site in `crates/cloudkitty-core/src/world.rs`
      (per data-model), broadcast + `recent_meows` untouched-by-design
      (verify via test), digest columns flow from T005's derivation.

**Checkpoint**: US1 fully functional — the altruistic channel exists.

---

## Phase 4: User Story 2 — The cats get words of their own (P2)

**Goal**: the free register: mew's rename inert, chirp active, reserves
never-legal by default and chirp-equivalent when armed.

**Independent Test**: mew/chirp legal anywhere off cooldown; trill/ekekek
never-legal under defaults, legal-when-enabled; shapes identical throughout.

- [x] T015 [P] [US2] Write FAILING free-register tests in
      `crates/cloudkitty-core/src/meow.rs` tests: mew and chirp legal on
      bare grass off cooldown (no grounding — US2/AC1); trill/ekekek →
      Silent on every tick under defaults (US2/AC2); with a config enabling
      them, behavior chirp-equivalent; cooldown still binds all four.
- [x] T016 [US2] Make T015 pass (expected: mostly already true via
      T006/T008 — this task exists to prove it, then fix any gap); verify
      the rename pin test (T003) still green post-integration.

**Checkpoint**: the free register is law-complete; reserves are inert.

---

## Phase 5: User Story 3 — Vocabulary armed by config, never by fork (P2)

**Goal**: flags gate legality only; layout provably flag-independent;
strictness posture intact.

**Independent Test**: two configs differing only in flags → identical
shapes, different legality; misspelled key refuses boot.

- [x] T017 [P] [US3] Write FAILING layout-invariance tests in
      `crates/cloudkitty-rl/tests/vocabulary_flags.rs` (the name
      quickstart.md step 5 invokes) (obs/mask lengths byte-identical across
      flag settings; a disabled HereFood at a stocked bowl → mask false +
      Silent downgrade, US3/AC1-2) and config tests in
      `crates/cloudkitty-core/src/config/` (omitted table → defaults with
      reserves off, US3/AC3; misspelled key → boot refusal naming the
      field, US3/AC4).
- [x] T018 [US3] Make T017 pass; add the explicit `[meow.vocabulary]`
      table (all fifteen, documented defaults) to the shipped
      `cloudkitty.toml`; add a `GET /config` echo assertion to
      `crates/cloudkitty-server/tests/` (vocabulary table serves, reserves
      false).

**Checkpoint**: experiments can arm words by flag; nothing structural moves.

---

## Phase 6: User Story 4 — The generation gate (P2)

**Goal**: stale artifacts refused by name; new-schema artifacts serve; the
parity gate crosses the wall green; main's shipped config survives CI with
scripted seats.

**Independent Test**: quickstart step 4 + the shipped-config gates.

- [x] T019 [P] [US4] Update/extend rejection tests in
      `crates/cloudkitty-rl/tests/artifact_v3_reject.rs`: an artifact
      pinning observation 3 / action 2 / mask 2 (each independently) is
      refused naming the pin and expected value (US4/AC2), for both v2- and
      v3-format artifacts; version-set semantics unchanged.
- [x] T020 [P] [US4] Update `crates/cloudkitty-rl/src/test_support.rs`
      consumers and `artifact_v3_load.rs`/timing tests to the derived
      schema-4 dims (should be automatic via constants — this task verifies
      and pins expectations at 225/50).
- [x] T021 [US4] THE HANDSHAKE (FR-013): message Experiments for the
      schema-4 oracle export (225-wide obs, 50 logits, ≥100 rows incl.
      vacancy-stress + never-legal new kinds, reserves covered); on
      delivery verify shas + row shape, replace
      `crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy` +
      `oracle.parity` in place, update `artifact_v3_parity.rs` width
      expectations; parity gate GREEN at ≤1e-4 + exact argmax.
      **Implementation pauses here until the fixture lands.**
- [x] T022 [US4] Wall-window config (FR-014, research D5): shipped
      `cloudkitty.toml` seats all four kitties `needs_driven` and REMOVES
      the `[rl.policy.*]` blocks (registration validates artifacts at boot
      — stale-pin blocks would fail startup); artifacts STAY in `policies/`
      with a wall-window note added to `policies/README.md`; update
      `crates/cloudkitty-server/tests/policy_kitty.rs` and the
      shipped-config gates for the scripted-seat window (the
      "seats-a-policy-this-binary-can-open" assertion becomes
      window-aware: no policy seats is the lawful wall state).

**Checkpoint**: the wall PR is CI-green end-to-end on main's gates.

---

## Phase 7: User Story 5 — The living documents (P3)

**Goal**: the encodings contract reborn living; the field guide born
complete at fifteen words.

**Independent Test**: quickstart step 7.

- [x] T023 [P] [US5] Write `docs/encodings.md` (FR-017/FR-019): versioned
      field tables — observation v3 AND v4 (self 34 with offsets/norms,
      slots, digest incl. intensity semantics, clock), action menu v2 +
      message head (9 and 16), mask layouts, global-state v1, bc-collect
      dataset format; preamble states the schema-moving-specs rule; every
      row verified against code, with Experiments' draft
      (`experiments/encodings-draft-2026-08-15.md`) as raw material and the
      two flagged orderings (Direction::ALL, ElementType::ALL) resolved
      with file:line citations; cites contracts/say-surface-v3.md.
- [x] T024 [P] [US5] Add successor pointer to
      `specs/014-multi-agent-rl/contracts/encodings.md` (FR-018): one
      header note — frozen at v1; living truth at docs/encodings.md.
- [x] T025 [US5] Write `docs/meows.md` (FR-020/FR-021) in the house voice
      (owner's public-voice guidance applies): grammar-in-one-breath +
      two-tier doctrine; sixteen entries (Silent + 15) each with law /
      intent / observed columns — law cells verbatim from
      contracts/say-surface-v3.md; observed cells cite
      `experiments/exp-004-meow-channel/results/` and
      `policies/purrsonality.md` (purr-as-contact-call, mew's "I'm coming,
      stay put", doter dialect inversion) or state their honest emptiness
      (Here*/chirp: "meaning awaits the cats"; reserves: "not yet spoken
      anywhere"); WaitForMe footnote; non-guarantees section (FR-016,
      F-011, spec-023 treatment); digest paragraph for plugin authors;
      as-is display note; FR-021 rule in the preamble.

**Checkpoint**: a stranger can learn the language from docs/ alone.

---

## Phase 8: Polish & Cross-Cutting

- [x] T026 [P] Update `docs/plugins.md` (research D4): message-kind list
      (mew replaces follow_me; seven kinds join; legality summarized),
      PROPOSAL_WIRE_VERSION 2 note; update the demo plugin
      (`docs/examples/demo_plugin.py`) if it names kinds.
- [x] T027 [P] Check `docs/rl-training.md` for pre-wall widths/schema
      references and update alongside the v3 pointer paragraph if stale.
- [x] T028 CHANGELOG.md wall entry under ## Unreleased: the say-surface
      finalization story with **[obs-schema]** and **[stamp]** markers
      (artifacts refuse to load; engine-defaults hash moves via
      [meow.vocabulary]); note the scripted-seat wall window and the
      client-only deploy rule; the config rider lands its own entry in its
      own PR.
- [x] T029 Full validation: `cargo test --workspace` green INCLUDING
      parity; run quickstart.md steps 1–6 top to bottom; re-run the suite
      after any fix and READ THE COUNT (house rule); confirm stamp movement
      is exactly the expected [meow.vocabulary] delta.
- [x] T030 Fresh-eyes review pass over the full worktree diff (general
      agent against `git -C <worktree> diff` — the 031 lesson: point the
      reviewer at the worktree explicitly); close or consciously defer
      every finding before requesting Elizabeth's merge word.

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2**: strictly sequential (baseline before changes).
- **Phase 2 internal**: T002/T003 (failing tests) and T007 parallel; T004 →
  T005; {T004, T006, T007} → T008; T008 → T009 → T010.
- **Phases 3–5 (US1–US3)**: independent of each other once Phase 2 lands;
  each is tests-first internally. US2 and US3 are thin — they mostly prove
  foundational behavior story-by-story.
- **Phase 6 (US4)**: T019/T020 parallel after Phase 2; T021 blocks on the
  Experiments handshake (send the request when Phase 2 lands so the export
  overlaps Phases 3–5); T022 independent of T021 but both precede T029.
- **Phase 7 (US5)**: T023/T024 parallel any time after Phase 2 (numbers
  final); T025 after T023 (law cells cite the same tables).
- **Phase 8**: T026/T027 parallel; T028 after all stories; T029 after
  everything incl. T021; T030 last.

## Parallel Opportunities

```text
Phase 2 open:   T002 ∥ T003 ∥ T007
After Phase 2:  T011 ∥ T012 ∥ T013 ∥ T015 ∥ T017 ∥ T019 ∥ T020 ∥ T023 ∥ T024
                (and send the T021 oracle request immediately)
Polish:         T026 ∥ T027
```

## Implementation Strategy

MVP = Phases 1–3 (US1): the Here family live end-to-end behind the new
schema. In practice the wall ships as ONE PR (FR-014/FR-015 — one
re-baseline), so the incremental value of story checkpoints is
verification, not deployment: stop at each checkpoint, run its independent
test, then continue. The single hard external dependency is T021's oracle;
requesting it at the Phase-2 checkpoint hides the handshake latency behind
Phases 3–5. Total: 30 tasks.
