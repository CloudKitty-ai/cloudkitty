# Tasks: The Meow Channel — exp-004 Schema Batch

**Input**: Design documents from `/specs/028-meow-channel/`

**Prerequisites**: plan.md, spec.md (clarified 2026-08-08), research.md (R1–R18),
data-model.md, contracts/encodings-v2.md, quickstart.md

**Tests**: House practice — every task is one coherent edit+test unit; new
structural guarantees get named tests; existing pinned tests are rewritten (never
weakened) where their pinned behavior is the thing the spec changes, with the
replacement named in the task.

**Organization**: By user story, but note the honest dependency shape in
"Dependencies" below — the pair type (US1) is load-bearing for US2/US4, which is
unusual for this house and declared rather than hidden.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: Capture the pre-028 world before the engine moves.

- [X] T001 Generate and commit the pre-batch snapshot fixture
      `crates/cloudkitty-core/tests/fixtures/pre-028-world.json`: at THIS commit
      (before any engine change), run the shipped `cloudkitty.toml` config
      scripted-only for ~500 ticks via a throwaway runner so meows, per-kind
      cooldowns, distress state, and purr state are all populated, serialize the
      full `World`, commit the JSON, delete the runner. (R16 — this task MUST
      precede every engine change; the fixture is the resume-test's witness that
      the wall is policy-side only.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Vocabulary and config surface every story reads.

**⚠️ CRITICAL**: Mid-branch behavior is transitional after these tasks (declared
in each); the branch is judged at its tip, each task still compiles green.

- [X] T002 Extend the vocabulary in `crates/cloudkitty-core/src/meow.rs`: append
      `WantBath`, `WantSleep` variants; make `for_need`/`related_need` total over
      all six `NeedKind`s; add `Meow.intensity: f32` with `#[serde(default)]`;
      update `need_to_message_mapping_round_trips` to totality and keep
      `wait_for_me_is_a_patience_word` green. (Transitional: the urgent lottery
      can now announce Sleep/Bath — superseded in T012.)
- [X] T003 Rebuild the config surface (`crates/cloudkitty-core/src/config/mod.rs`,
      `defaults.rs`, `validate.rs`, root `cloudkitty.toml`): `MeowConfig` → three
      keys (`recent_window_ticks` 10, `announce_threshold` 30.0,
      `announce_hysteresis` 5.0) + retire `courtesy_ticks`/`urgent_courtesy_ticks`/
      `urgent_need_threshold` as spec-023-style loud sentinels; `ActionEffects` +
      `cosleep_drip_relief`/`cosleep_mutual_relief` (15.0/15.0, serde-defaulted);
      `BehaviorConfig` + `cuddle_real_threshold` (15.0); `validate_meow` rewritten
      (ranges + retirement errors, frozen message style, section order unchanged);
      `validate_actions` finiteness loop → 12 dials. Interim wiring so the crate
      compiles: `emit_meow` stamps `tick + recent_window_ticks` (delete
      `cooldown_for` and its two unit tests — replaced by T010's mask-cadence
      enforcement), scripted urgent lottery reads `announce_threshold`. Rewrite
      `meow_courtesy_defaults_land_and_the_rows_hold` + add
      `the_retired_courtesy_trio_is_rejected_loudly`; update `cloudkitty.toml`
      `[meow]` block + new `[actions]`/`[behavior]` keys with comments; extend
      the server integration test
      `the_viewer_config_travels_through_the_config_endpoint` to assert the new
      dials travel through GET /config (FR-025); both
      shipped-config sweep tests stay green under the SETTLED sweep policy
      (analyze finding C1; decided by Experiments 2026-08-08 — all 62
      `experiments/` TOMLs carrying `courtesy_ticks` are pinned-generation
      records, none updatable): add a root-level exclusion manifest
      `config-sweep-exclusions.txt` read by BOTH sweeps, with directory-level
      entries + one rationale line each for the nine pinned dirs —
      `exp-002-mixed-population/family` (32, prereg family record),
      `exp-003-water-schema/family` (15, byte-frozen prereg, PR #115),
      `exp-003-water-schema/results` (2, committed-results record),
      `screens/geometry-20x20-2026-08-07` (3), `screens/geometry-20x20-optE-2026-08-07`
      (2), `screens/geometry-22x22-2026-08-05` (2), `screens/scarcity-2026-08-05`
      (2) (measurement records behind registered findings),
      `rebaseline-2026-08-06/configs` (3, re-baseline record),
      `exp-001-bc-mappo/configs` (1, historical) — and the stated rule that the
      manifest only ever names pinned-generation dirs: new experiment output
      (exp-004's family v5 included) is in sweep scope by default. Migrate
      `specs/004-fix-happiness-lockin/stuck-state-config.toml` by deleting its
      three retired `[meow]` keys (Product-owned; its stuck-state semantics
      don't touch meow). Nothing under `experiments/` is edited.

**Checkpoint**: vocabulary + dials exist; old courtesy machinery gone.

---

## Phase 3: User Story 1 — Announcing without giving up the turn (P1) 🎯 MVP

**Goal**: Every decision is (activity, message); menu 34; head 9; artifact v2;
determinism holds with one RNG deal per kitty.

**Independent Test**: seeded world where activities are distribution-identical to
pre-change while messages ride along; `cargo test -p cloudkitty-core` +
determinism suites green.

- [X] T004 [US1] Introduce `Decision { activity, message }` across the seam
      (`crates/cloudkitty-core/src/seam.rs`, `behavior/mod.rs`): `Behavior::decide`
      → `Decision`; `JointProposal`/`ResolvedDecision` carry it;
      `KittyTickRecord` grows `proposed_message`/`applied_message`; fallback/
      reseed paths untouched in draw shape. Scripted deciders transitional:
      former `Action::Meow` returns become `(Idle, Some(kind))`;
      `wait_for_them` becomes `(Idle, Some(WaitForMe))` (final form) in
      `behavior/selection.rs`; update seam/parity tests
      (`joint_action_parity.rs`, `the_resolver_and_the_served_path_decide_identically`).
- [X] T005 [US1] Retire `Action::Meow` and build the message apply path in
      `crates/cloudkitty-core/src/action.rs` + `meow.rs`: `validate` → `false`
      for `Meow` (Purr precedent; add `a_retired_meow_proposal_lawfully_resolves`
      beside the purr twins, keep the round-trip corpus green); new
      `message_legal` skeleton (Silent true, `WaitForMe` cooldown-clear —
      today's voluntary `wait_for_them` check made law, so the yield word
      survives illegal→Silent enforcement; `Purr` earned-only, today's validate
      gate unchanged; others true — grounding lands in T010); apply order =
      activity then message; `emit_message` stamps intensity (need/100 want-kinds,
      0.0 else) + per-kind cooldown + `recent_meows` push; illegal proposed
      message downgrades to Silent in the record. Rewrite
      `repeated_meows_all_emit_and_stamp` to the new emission shape; delete the
      urgent-stamp tests (courtesy retired, T003 note).
- [X] T006 [US1] Menu v2 + `MessageCodec` in `crates/cloudkitty-rl/src/codec.rs`:
      drop the meow-row extend (34 rows), fix the stale `+7` capacity hint,
      `ACTION_SCHEMA_VERSION = 2`; define `HEAD_KINDS: [MessageKind; 8]` in
      `observe.rs` (normative appended order, replacing `LEARNED_MEOWS`; the
      digest itself stays 6×3 until T011 — keep a shim over the first six
      entries so observe compiles unchanged); add `MessageCodec` (Silent +
      `HEAD_KINDS`); codec tests: 34-entry
      normative order, total decode both codecs, encode-inverts-decode,
      `WaitForMe` inexpressible; update `codec_totality.rs`.
- [ ] T007 [US1] Two heads through rl (`crates/cloudkitty-rl/src/policy.rs`,
      `behavior.rs`, `episode.rs`, `mask.rs`): `ARTIFACT_VERSION = 2`, final
      layer out-width == menu_len + 9, `SchemaExpectations.message_head_len`,
      byte-frozen-style width error; `select` samples both heads from ONE
      `gen_u64` split hi/lo u32 (greedy draws nothing);
      `Episode::step(BTreeMap<KittyId, (usize, usize)>)`;
      `AgentInfo.applied_message`; mask wire = 43-wide concat
      (`MASK_SCHEMA_VERSION = 2`, message half from `message_legal` probe);
      update `mask.rs` literal-index tests (idle 33, purr row now head index 6),
      `artifact_validation.rs`, `episode.rs`/`mixed_control.rs`/
      `vector_independence.rs`/`policy_ci.rs` fixtures, zero-artifact-style test
      helpers in `test_support.rs`.
- [ ] T008 [US1] Keep `crates/cloudkitty-py/src/lib.rs` compiling and honest:
      `MultiDiscrete([menu_len, 9])` action space (dict fallback analogue), step
      accepts pairs, `head_len` getter, mask `[43]`/`[n,43]`,
      `applied_message` in info, `recent_meows` returns snake_case wire names
      (R17 wart fix). Full pytest deferred to T018; `cargo build -p
      cloudkitty-py` green here.

**Checkpoint**: MVP — the channel exists structurally; determinism suites green.

---

## Phase 4: User Story 2 — Grounded legality (P2)

**Goal**: Certified announcements: grounding + hysteresis + per-kind cooldown in
engine law; Silent never masked, structurally.

**Independent Test**: property tests over randomized worlds — mask tracks dials
with hysteresis; every emission opens that kind's cooldown; Silent legal in every
reachable state.

- [ ] T009 [US2] Arming state in `crates/cloudkitty-core/src/kitty.rs` +
      `world.rs`: `announce_armed: BTreeSet<NeedKind>`
      (`#[serde(default, skip_serializing_if = …)]`), updated in the needs phase
      beside `record_distress` (insert at ≥ threshold, remove below
      threshold − hysteresis, hold in the band); tests: hysteresis edge triple
      (rising/held/falling per spec US2 scenarios), wire hygiene (absent when
      empty), pre-028 kitty JSON deserializes disarmed.
- [ ] T010 [US2] Full `message_legal` truth table in
      `crates/cloudkitty-core/src/meow.rs` + message-mask oracle in
      `crates/cloudkitty-rl/src/mask.rs`: want-kinds = armed ∧ cooldown clear,
      `FollowMe` = cooldown clear, `Purr`/`WaitForMe`/Silent as T005; add
      `legal_message_mask`; extend the oracle property suite
      (`tests/mask_oracle.rs`) to both heads; named tests
      `silent_is_never_masked` (property: every reachable state) and a
      mask-cadence replacement for the deleted courtesy property test
      (`scripted_meows_keep_courtesy_spacing…` in `tests/meow_courtesy.rs` →
      same-kind emissions from any emitter are ≥ `recent_window_ticks` apart —
      now enforced, strictly stronger than the voluntary courtesy it replaces).

**Checkpoint**: the channel is certified state; spam structurally impossible.

---

## Phase 5: User Story 3 — The coherent digest (P3)

**Goal**: 8 kinds × (recency, dx, dy, intensity) describing one emitter; obs 197.

**Independent Test**: two-emitter scenario — all four values describe the
freshest; layout test pins 197.

- [ ] T011 [US3] Digest v3 in `crates/cloudkitty-rl/src/observe.rs` (+ ripple):
      digest loop → `HEAD_KINDS`, freshest-emitter selection (max tick, tie-break
      min kitty id), 4-tuple with stamped intensity, `MEOW_DIGEST = 32`,
      `OBSERVATION_SCHEMA_VERSION = 3`; rewrite
      `the_default_layout_is_183_values` → `_197_values`, update
      `a_chatty_meower_saturates_the_digest_and_never_compounds` (saturation
      still holds — cooldown makes chattiness impossible anyway, test keeps the
      clamp), new coherence test (fresher-vs-nearer emitters), constant-0
      intensity test for purr/follow_me; ripple: `behavior.rs` expectations,
      py `observation_space`, `encoding_determinism.rs`; verify
      `GLOBAL_STATE_SCHEMA_VERSION` untouched by inspection (bump only if it
      encodes messages/menu — record the finding in the commit message).

**Checkpoint**: a listener has one coherent target per kind.

---

## Phase 6: User Story 4 — Demonstrators that use the channel (P4)

**Goal**: Deterministic announce; groom response keyed on the meow; routed naps.

**Independent Test**: seeded scripted runs — GroomKitty > 0; responses only to
audible meows; announcing cats mid-errand.

- [ ] T012 [US4] The deterministic announce rule in
      `crates/cloudkitty-core/src/behavior/needs_driven.rs` + `playful.rs` +
      `mod.rs` (shared helper): message = highest-pressure need whose want-kind
      is `message_legal` (equal pressures tie-break in `NeedKind::ALL` order,
      the selection.rs precedent), else Silent; computed AFTER and independent of the
      activity; delete the `gen_bool(0.3)`/`gen_bool(0.15)` lotteries and the
      transitional `(Idle, Some(kind))` returns from T004; tests: announcement
      never alters the chosen activity (decide with channel forced Silent ==
      decide normally, activity-wise — the engine-side half of FR-021), a
      grounded cat announces, an ungrounded cat is Silent.
- [ ] T013 [US4] Groom-response rung in
      `crates/cloudkitty-core/src/behavior/needs_driven.rs`: after opportunism,
      before the potter — own Cuddle ≥ `cuddle_real_threshold` ∧ audible
      `WantBath` (self-excluded, freshest emitter per digest rule) → adjacent ?
      `Groom { target: Some(emitter) }` : step toward; tests: the imitability
      pair (wet-but-SILENT neighbor ignored; meowing neighbor approached and
      groomed — `a_meow_keyed_groomer_ignores_silent_wet_cats`), ladder position
      (urgent eat still wins), GroomKitty appears in a seeded 20k-tick run
      (SC-002's engine half).
- [ ] T014 [US4] Cosleep routing in the `ReliefSource::Sunbeam` arm of
      `crates/cloudkitty-core/src/behavior/needs_driven.rs`: own Cuddle ≥
      `cuddle_real_threshold` → adjacent friend ? `Sleep { with: Some(f) }` :
      reachable friend (within `sunbeam_reach`) ? step toward : existing sunbeam
      logic; below gate → exactly today's behavior (regression-pinned); tests
      per spec US4 scenario 3 + the existing sunbeam tests updated.

**Checkpoint**: dataset v4's classes 13–15 are nonzero by construction.

---

## Phase 7: User Story 5 — Cosleep priced by presence (P5)

**Goal**: Dedicated dials, mutual tier, three-flow coupling severed.

**Independent Test**: passive vs mutual rates; defaults numerically identical to
today; duet/groomer unaffected by cosleep dials.

- [ ] T015 [P] [US5] Rework `apply_sleep_relief` in
      `crates/cloudkitty-core/src/action.rs`: tier = partner activity
      ∈ {Sleeping, Resting} → `cosleep_mutual_relief` else `cosleep_drip_relief`,
      both parties get the tier rate, sleeper's Sleep relief unchanged; duet and
      groomer keep `cuddle_relief`; tests: tier selection both ways,
      behavior-preserving-at-defaults (with all three dials equal at 15.0 a
      seeded run's cuddle trajectories match today's arithmetic — asserted
      numerically in one build, not cross-build), `a_departed_cosleeping_partner_stops_granting_cuddles`
      stays green, moving `cosleep_*` dials leaves duet/groom payments fixed.

---

## Phase 8: User Story 6 — Migration and observability (P6)

**Goal**: The wall behaves exactly as promised; the counter rides every report.

**Independent Test**: fixture resumes; retired keys refuse; counter matches the
census convention.

- [ ] T016 [US6] Resume + compat tests in
      `crates/cloudkitty-core/tests/snapshot_resume.rs` (+ kitty.rs test mod):
      `a_pre_028_world_resumes_and_runs` — deserialize T001's fixture as `World`,
      tick 200× under the shipped config, invariants green, old-kind meows and
      cooldowns intact, new fields defaulted (disarmed, intensity 0.0); plus
      kitty-level JSON compat cases for `announce_armed`/`Meow.intensity`
      following the existing pre-spec fixtures pattern.
- [ ] T017 [P] [US6] Distress-tick counter in `crates/cloudkitty-rl/src/welfare.rs`
      (+ `harness.rs`, `cli_support.rs`, `suite.rs` JSON): census state in
      `WelfareAccumulator::observe` (post-tick, ≥ `thresholds.distress`, episode
      edge below→at/above — the instrument's verbatim convention),
      `WelfareReport.distress_census`, one human-panel line, present in
      kitty-eval JSON and suite exam outcomes; NO verdict reads it; test
      `distress_census_matches_the_instrument_convention` — an inline
      `run_one_with` observer implementing the census closure verbatim must
      agree exactly with the accumulator over seeded scripted runs. (Era-record
      note, per Experiments: the 810/810 retro-replay against exp-003's
      committed evals was validated PRE-028 and is not reproducible on this
      engine — the era config at `46b22bc:cloudkitty.toml` carries retired keys
      and scripted meow semantics change, so exp-003 joins exp-002 in the
      era-engine-rebuild category. The acceptance check here is
      convention-agreement on the new engine, never era replay.)

---

## Phase 9: Polish & Cross-Cutting

- [ ] T018 Python binding full pass in `crates/cloudkitty-py/`: `maturin develop`
      + full pytest (PettingZoo conformance with `MultiDiscrete`, shapes/bounds,
      reproducibility, vector parity); schema constants re-export 3/2/2; fix any
      conformance fallout from the pair action space.
- [ ] T019 Process close-out: CHANGELOG.md Unreleased entry with
      `[obs-schema]`/`[rng-sequence]`/`[stamp]` markers + the NEW
      `engine_defaults_sha256` recorded (print via throwaway test, delete it);
      `cloudkitty.toml` comment sweep (window-doubles-as-cooldown note); assess
      the FromConfig type-level refactor (017 close-out) — adopt only if net
      simpler inside already-touched files, else record the skip here; full
      `cargo test --workspace` + quickstart.md walkthrough; confirm rollout
      notes (deploy gate, client handoff) are quoted in the eventual PR body.

---

## Dependencies & Execution Order

- **T001 strictly first** — the fixture must be born pre-028.
- **Foundational**: T002 → T003 (config reads the new variants' totality).
- **US1 (T004→T005→T006→T007→T008)**: sequential — the pair type, then its
  enforcement, then its encodings, then its consumers. **Load-bearing for US2
  and US4** (declared): grounding masks and the announce rule both need
  `Decision` + `message_legal`.
- **US2 (T009→T010)**: after US1.
- **US3 (T011)**: after T006 (`HEAD_KINDS`); independent of US2 — may run in
  parallel with Phase 4 planning but same-file discipline applies
  (`observe.rs` vs `mask.rs` are distinct; fine).
- **US4 (T012→T013→T014)**: after US2 (announce rule reads `message_legal`);
  T013/T014 sequential (same file `needs_driven.rs`).
- **US5 (T015 [P])**: only needs T003 — parallelizable with US2–US4 (distinct
  file region in action.rs vs T005's; rebase-order with T005 if worked
  concurrently, otherwise run after it).
- **US6**: T016 after all state fields exist (T009 latest); T017 [P] anytime
  after T003 (welfare.rs is untouched by other tasks).
- **Polish**: T018 after T011 (obs length final); T019 last.

### Parallel Opportunities

Single-implementer honest view: T015 and T017 are the genuinely parallel-safe
tasks (distinct files, no story dependencies beyond Foundational). Everything
else is a chain by design — one carrier type, one law, one digest.

## Implementation Strategy

**MVP = Phases 1–3** (fixture + vocabulary/config + US1): the channel exists,
determinism holds, artifact v2 defined — enough to validate the wall's shape
end-to-end before the behavioral stories land. Then US2 (certification), US3
(digest), US4 (demonstrators), US5/US6, polish. Commit per task with house
trailers; long verifications foreground.

**Out of scope, tracked elsewhere**: client `MEOW_TEXT` entries (Client thread,
pre-rollout), deploy gate (rollout notes — seats re-parked or gen-3 artifact
before the live box takes this binary), re-baseline + dataset v4 + pilot
(Experiments, post-merge).
