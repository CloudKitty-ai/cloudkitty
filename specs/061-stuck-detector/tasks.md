# Tasks: Stuck Detector at Decoding

**Input**: Design documents from `specs/061-stuck-detector/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/stuck-detector.md, quickstart.md

**Tests**: included — Article VI and the house rules demand test-guarded
work; every assertion goes through the rule-5 red cycle
(`scripts/mutate.sh --expect <prediction>`), staged bugs per the
quickstart table. Changed-behaviour checks are sorted (rule 6) in a
`test-sort.md` before the suites run.

**Organization**: by user story, after a foundational phase that owns
the shared signature engine and configuration.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: the module exists and compiles; no behavior.

- [ ] T001 Create `crates/cloudkitty-server/src/stuck.rs` (module doc
      naming spec 061 and the verified rule) and declare `mod stuck;`
      in `crates/cloudkitty-server/src/lib.rs`; `cargo check -p
      cloudkitty-server` green.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: config can load and the verified signature engine exists —
every story consumes both.

**⚠️ CRITICAL**: no user story work before this phase completes.

- [ ] T002 [P] Core config passthrough: add `#[serde(default,
      skip_serializing)] pub stuck_detector: ForeignTable` beside the
      `watchdog` field in `crates/cloudkitty-core/src/config/mod.rs`
      plus the `Default` impl; extend
      `the_foreign_tables_never_serialize` to cover it. Red cycle:
      predict the leak test red with `skip_serializing` removed
      (`engine_defaults_sha256` must not move — research.md R7).
- [ ] T003 [P] Add `stuck_detector` to `FOREIGN_TABLES` in
      `experiments/tools/complete_config_3.py` (keeps the config sweeps
      green; rust-toolchain-pin trap: no new root `.toml` anywhere in
      this feature).
- [ ] T004 `StuckConfig` in `crates/cloudkitty-server/src/stuck.rs`:
      `from_toml_str` + `validate` on the watchdog loader shape
      (`deny_unknown_fields`), doc-commented defaults `mode="off"`,
      `window=30`, `armed_line=75.0`, `radius=1` (the replay-verified
      value; others unverified, say so in the doc comment),
      `recent_fires=256`; unit tests for absent table = defaults,
      unknown key, `window=1`, `armed_line=0`, `radius=0`, bad mode
      each failing at load with the key named (quickstart §6, contract
      §1). Red cycle: stage `validate` accepting `window = 1`, predict
      the rejection test red.
- [ ] T005 Write the first cut of
      `specs/061-stuck-detector/test-sort.md` (CLAUDE.md rule 6 —
      BEFORE any suite runs: sort changed-behaviour guards that must
      go red from kept behaviour that must stay green; extend it as
      each later phase lands), then the `SeatSignature` state machine
      in `crates/cloudkitty-server/src/stuck.rs` per data-model
      transitions: anchor/configured-radius confinement; per-need
      armed scene-free streaks with scene-PAUSE and OWN-relief CLEAR
      (`Activity::governing_need()` equal to the need, restricted to
      the seat's own relief — grooming WITH a target does not clear
      the groomer's bath streak, solo rest clears nothing); the
      post-fire reset as FR-007's stand-down. Unit tests porting the
      replay semantics — the synthetic F-044 two-tile pacer fires
      `200 // window` times at every swept setting (parity with
      `stuck_rule_replay.py`: the reset alone spaces refires, no
      extra stand-down tick), a 1–2-tick scene flicker does NOT reset
      the window (red cycle: implement the strict gate as the staged
      bug and predict the flicker test red), own-relieving scene
      clears while groom-other does not, a scene-free below-line tick
      clears (an in-scene below-line tick only pauses), escape resets
      anchor, mid-window arming starts at the crossing.
- [ ] T006 `StuckDetector` observer in
      `crates/cloudkitty-server/src/stuck.rs`: per-mind-seat tracking
      from `&World`, mind-class rule (`policy:*` prefix OR plugin
      `class = "mind"` — research.md R6), `FirePlan` emission for the
      NEXT tick into the shared (Mutex) fire set the wrapper will
      read, unconsumed-plan expiry (research.md R2 residual: state
      already reset at emission, episode re-accumulates); unit tests
      on bare `World`s. Red cycle: stage the plan keyed to the
      CURRENT tick instead of the next, predict the exact-fire-tick
      test (T009) red.

**Checkpoint**: signature engine verified against the replay semantics;
config loads; test-sort.md exists; nothing wired.

---

## Phase 3: User Story 1 - A trapped mind gets freed (Priority: P1) 🎯 MVP

**Goal**: an enforcing detector breaks the F-044 loop shape within one
window plus one tick; healthy and relieving shapes never fire.

**Independent Test**: quickstart §1 — a doctored dithering mind advisor
with an armed need fires and is freed; below-line and in-scene arms
never fire.

### Implementation for User Story 1

- [ ] T007 [US1] `StuckGuard` `Behavior` wrapper in
      `crates/cloudkitty-server/src/stuck.rs` (SeatClassed pattern,
      forwards `decide`/`try_decide`/`is_builtin` per the wrapper
      contract; wraps in EVERY mode, forwarding when idle): consume
      the seat's `FirePlan` keyed by tick; call the inner advisor
      FIRST (capturing the replaced proposal; a `None` from
      `try_decide` records as "none" and observe returns `None` so
      the engine fallback runs), then in enforce return
      `Teacher::NEEDS_DRIVEN.decide(&ctx)`, in observe return the
      inner decision untouched (research.md R3). NO free-register
      kind is named in the wrapper (doctrine rule 6 re-verify clause;
      the FR-005 guard is the T009 test). Red cycle: stage enforce
      returning the inner decision, predict the applied-action assert
      (T009) red.
- [ ] T008 [US1] Wiring: thread the shared fire-set/record handle and
      mode from `load_config` (`crates/cloudkitty-server/src/main.rs`,
      `[stuck_detector]` parse) to BOTH registry builders in
      `crates/cloudkitty-server/src/lib.rs` (~:189 policy seats, ~:332
      mind-class plugins; scripted seats and built-ins never wrapped)
      and to `crates/cloudkitty-server/src/sim_task.rs`: extend
      `sim_task::spawn`'s signature (its in-file tests ~:337/364/399
      and the `server_integration.rs:130` harness update with it) and
      call `detector.observe(&world)` beside the watchdog observe.
- [ ] T009 [US1] Scenario-1 suite (unit in
      `crates/cloudkitty-server/src/stuck.rs` + integration in
      `crates/cloudkitty-server/tests/server_integration.rs`,
      STATE-DEPENDENT doctored advisor per quickstart §1 — dithers on
      its home tiles only, so one scripted step genuinely frees it):
      enforce mode fires on the EXACT tick the observe convention
      predicts (equality, not a ≥ bound), the applied action on the
      fire tick is the scripted brain's, the seat leaves the home
      tiles within one window plus one tick of signature completion
      (SC-001's bound, both sides), no consecutive-tick refire
      (FR-007), below-line and relieving-scene arms never fire
      (US1/AC2, AC3), boxed-in and refused-substitute edge cases
      resolve through the ordinary proposal path with the fire still
      recorded, two seats sharing one wrapped behavior instance each
      fire on their own window, and `Teacher::NEEDS_DRIVEN` never
      emits a free-register kind across a behavior sweep (FR-005 —
      the kinds are named in test code only). Red cycles per
      quickstart table: skip the substitution, predict the
      loop-breaks assertion red; drop the post-fire reset, predict
      the consecutive-fire guard red; stage NEEDS_DRIVEN emitting a
      free kind at the seam, predict the FR-005 test red.

**Checkpoint**: US1 independently functional — a stuck mind is freed,
on the record of the tests alone.

---

## Phase 4: User Story 2 - Every intervention is on the record (Priority: P2)

**Goal**: every fire carries full FR-011 attribution in the serving
logs and on a status surface with per-seat counts.

**Independent Test**: quickstart §2 — force one fire; the tracing event
and `/stuck` entry carry every contract field; counts visible without
log reading.

### Implementation for User Story 2

- [ ] T010 [US2] `FireRecord` + ring + per-seat counts in
      `crates/cloudkitty-server/src/stuck.rs`: wrapper constructs the
      record with every field mandatory (SC-003) including the anchor
      tile and confinement span (FR-011), emits one structured tracing
      event (target `cloudkitty_server::stuck`, WARN enforce / INFO
      observe, contract §3's exact flattened field names, absent
      message = `""`), pushes to the bounded ring (`recent_fires`).
      Red cycle: stage the observe-mode event at WARN, predict the
      level assert red.
- [ ] T011 [US2] Status surface: `StuckStatus` (config echo incl.
      radius, per-seat enforced/observed counts, `armed` live trigger
      state — the FR-012 forward hook — and the ring) published on a
      watch channel from `crates/cloudkitty-server/src/sim_task.rs`
      into `AppState` in `crates/cloudkitty-server/src/api.rs`;
      `GET /stuck` handler + route in
      `crates/cloudkitty-server/src/lib.rs` (the `/welfare` pattern;
      serves config echo and empty collections when off).
- [ ] T012 [P] [US2] `/settings` rows for `[stuck_detector]` in
      `crates/cloudkitty-server/src/settings.rs` (extend
      `settings::build`'s signature and the pinned-key test), and the
      boot log line in `crates/cloudkitty-server/src/main.rs`
      (watchdog precedent). Red cycle: stage a renamed settings key,
      predict the pinned-key test red.
- [ ] T013 [US2] Scenario-2 suite: unit assert on the record's fields
      (`proposal_replaced` equals the doctored advisor's known
      output, anchor and confinement span correct); integration in
      `crates/cloudkitty-server/tests/server_integration.rs` via the
      `start_server_with` harness: `GET /stuck` shows the per-seat
      count, the full `recent` entry, AND the `armed` live trigger
      rows (confined count + hottest streak for a mid-window seat —
      FR-012, US2/AC1, AC2). Red cycles: drop one record field,
      predict the attribution assert red (SC-003); stage `armed`
      served empty mid-window, predict the trigger-surface assert
      red.

**Checkpoint**: US1 + US2 both work; fires are observable end to end.

---

## Phase 5: User Story 3 - The baseline stays trustworthy (Priority: P3)

**Goal**: off and observe are provably inert; enforce replays
identically; scripted seats are untouchable.

**Independent Test**: quickstart §§3–4, 6 — paired byte-identity,
fingerprint-identical replays, scripted-seat absence.

### Implementation for User Story 3

- [ ] T014 [P] [US3] Non-interference tests (watchdog
      `watched_and_unwatched_worlds_are_identical` template,
      `crates/cloudkitty-server/src/stuck.rs`, budgetless): paired
      worlds with the detector constructed-and-OFF (mind seats
      wrapped, forwarding — a real path, not absence-vs-absence) vs
      absent, byte-identical over 2000 ticks; observe-paired worlds
      byte-identical on a FIRING shape while the fire record exists —
      the FR-008 extension made testable (US3 + SC-002's off/observe
      no-divergence arm; enforce diverges by design and is not
      paired). Red cycle: mutate world-visible state in the observe
      path, predict byte-identity red.
- [ ] T015 [P] [US3] Determinism replay test in
      `crates/cloudkitty-server/tests/stuck_determinism.rs`
      (fingerprint pattern from `cloudkitty-core/tests/determinism.rs`,
      budgetless): two runs, same seed/config, enforce, deterministic
      firing seat → identical world fingerprints AND identical
      fire-record sequences end to end (SC-004, US3/AC2). Red cycle:
      key a fire decision off wall-clock, predict the sequence-equality
      red.
- [ ] T016 [P] [US3] Boundary tests (SC-005, US3/AC1): a scripted-class
      seat driven through the firing loop shape shows no tracking
      entry, no fire, and absence from every `/stuck` collection
      (not-wrapped by construction, asserted anyway) — unit in
      `crates/cloudkitty-server/src/stuck.rs` + integration in
      `crates/cloudkitty-server/tests/server_integration.rs`. Red
      cycle: stage the mind-class rule wrapping a scripted seat,
      predict the absence asserts red (quickstart table row 6).

**Checkpoint**: all three stories independently green.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T017 Finalize `specs/061-stuck-detector/test-sort.md` (started
      at T005, extended each phase): reconcile the full sort — every
      changed-behaviour guard's red on record with its prediction,
      kept-behaviour pile read not just run, any vacuous guard
      restaged on record (CLAUDE.md rule 6).
- [ ] T018 CHANGELOG entry under Unreleased in `CHANGELOG.md`
      (public-voice at write time; never retag) naming the three-state
      detector, shipped dark, defaults window 30 / armed 75 / radius 1.
- [ ] T019 Full validation: workspace `cargo test` + fmt + clippy;
      run the quickstart §5 anchor
      (`python3 specs/061-stuck-detector/stuck_rule_replay.py` from the
      native checkout root, both `--relief` rules) and confirm the
      committed table still reproduces; note in the PR that SC-001's
      full F-044 reproduction and SC-002's declared paired soak are
      battery-time reads run through the SERVER harness (the python
      lab paths never see the detector; doctrine rule 10), mechanism
      guarded by T009/T014/T015.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (P1)**: none.
- **Foundational (P2)**: after Setup; T002/T003 parallel; T004 → T005 →
  T006 sequential (same file). BLOCKS all stories.
- **US1 (P3)**: after Foundational. T007 → T008 → T009.
- **US2 (P4)**: after US1 (records are constructed in the wrapper T007
  and wired surfaces T008). T010 → T011; T012 parallel with T011;
  T013 last.
- **US3 (P5)**: after US1 (needs the firing fixture); T014/T015/T016
  parallel (different files/suites). Independent of US2.
- **Polish (P6)**: after all stories.

### Parallel Opportunities

- T002 ∥ T003 (core config vs experiments tool).
- T012 ∥ T011 (settings/main vs api/lib/sim_task).
- T014 ∥ T015 ∥ T016 nominally (different suites), but T014 and
  T016's unit parts BOTH edit `stuck.rs` tests and T016's integration
  part follows T013's edits in `server_integration.rs` — sequence
  those two files, parallelize only T015's new
  `stuck_determinism.rs`.

## Implementation Strategy

MVP = Phases 1–3 (US1): a stuck mind is freed, test-proven, before any
observability work. Then US2 (the record), then US3 (the inertness and
determinism proofs), then polish. Stop and validate at each checkpoint;
commits come with implement (060 pattern), via
`git -c commit.gpgsign=true commit` with the house trailer.

## Notes

- SC-002's declared number is a battery-time paired read, never a pass
  bar (doctrine rule 10); these tasks guard the mechanism and the
  no-divergence arm only.
- The served-path bench residual (research.md R2) is documented
  behavior, not a task: deterministic suites run budgetless.
- Raws for the quickstart §5 anchor live in the NATIVE checkout; run
  the replay from there, never move raws into this worktree.
