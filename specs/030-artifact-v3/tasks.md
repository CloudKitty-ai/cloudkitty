---

description: "Task list for Policy Artifact v3 — Entity-Attention Format"
---

# Tasks: Policy Artifact v3 — Entity-Attention Format

**Input**: Design documents from `specs/030-artifact-v3/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — Article VI requires the load, reject, and parity behaviors
to be CI-gated (quickstart.md defines the `cargo test` targets).

**Organization**: Grouped by user story. US1 (serve) is the MVP; US2 (reject) and
US3 (parity) are independent increments on the same foundation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no incomplete-task dependency)
- **[Story]**: US1 / US2 / US3; setup, foundational, and polish carry no label

## Path Conventions

Rust workspace. Primary crate `crates/cloudkitty-rl/`; server wiring in
`crates/cloudkitty-server/`. Paths are repo-relative.

---

## Phase 1: Setup

- [X] T001 Create `crates/cloudkitty-rl/src/attn.rs` with a module doc header
  citing `specs/030-artifact-v3/contracts/forward-v3.md`, and declare `mod attn;`
  in `crates/cloudkitty-rl/src/lib.rs`.
- [X] T002 [P] Add empty compiling scaffolds for the three test files:
  `crates/cloudkitty-rl/tests/artifact_v3_load.rs`,
  `crates/cloudkitty-rl/tests/artifact_v3_reject.rs`,
  `crates/cloudkitty-rl/tests/artifact_v3_parity.rs`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: These are the shared load path and fixture machinery every user
story flows through. No user story work can begin until this phase is complete.

- [X] T003 Refactor `PolicyArtifact` in `crates/cloudkitty-rl/src/policy.rs` into
  a version-keyed enum `{ V2(MlpArtifact), V3(AttnArtifact) }`; move the existing
  v2 struct and forward verbatim into `MlpArtifact`; make `forward`, `sha256`, and
  the schema accessors dispatch. The existing v2 tests MUST still pass byte-
  identically (FR-010).
- [X] T004 In `crates/cloudkitty-rl/src/policy.rs`, replace the exact-match
  version gate with a supported-set `{2, 3}` dispatch; change
  `UnsupportedVersion` to carry the supported set; route version 2 → the v2 path,
  3 → the v3 path (contracts/policy-artifact-v3.md "Version gate"). Depends on T003.
- [X] T005 [P] Add the `V3Header` struct in `crates/cloudkitty-rl/src/attn.rs`
  with `#[serde(deny_unknown_fields)]` and the nine required fields; parse it with
  `serde_json::from_slice` (data-model.md "V3 Header").
- [X] T006 [P] Implement token-layout derivation in
  `crates/cloudkitty-rl/src/attn.rs` from `ObservationConfig` and the `observe.rs`
  block widths (per-type offset, width, count, type-emb row); unit-test it sums to
  `observation_len` and yields 23 tokens at the default slot config.
- [X] T007 Implement derived tensor sizing and blob slicing in
  `crates/cloudkitty-rl/src/attn.rs`: from the hyperparameters and layout, compute
  every module's tensor size in the fixed order (forward-v3.md "Weight-blob module
  order"), assert the total blob byte length, and slice the blob into a named-block
  `AttnArtifact`. Depends on T005, T006.
- [X] T008 [P] Implement `Scratch` in `crates/cloudkitty-rl/src/attn.rs`, sized
  from the hyperparameters (token matrix `23×d`, attention scores, per-layer
  temporaries, summary `2d`, output vector), with no per-forward allocation
  (FR-012).
- [X] T009 [P] Implement the v3 `write_artifact` fixture builder in
  `crates/cloudkitty-rl/src/attn.rs` (header JSON + newline + module-ordered blob),
  mirroring the v2 writer (FR-019). Depends on T007 for the layout.

**Checkpoint**: a valid v3 artifact parses into an `AttnArtifact`; a v2 artifact
still loads unchanged; fixtures can be built in-test.

---

## Phase 3: User Story 1 - Serve a v3 policy alongside v2 (Priority: P1) 🎯 MVP

**Goal**: A v3 artifact loads, runs the attention forward, and serves lawful
decisions through the unchanged behavior seam, beside a v2 seat.

**Independent Test**: Boot with one v3 and one v2 seat against a scripted world;
both log before the first tick and produce legal decisions.

### Tests for User Story 1

- [X] T010 [P] [US1] Load-and-serve test in
  `crates/cloudkitty-rl/tests/artifact_v3_load.rs`: build a small synthetic v3
  fixture (T009), load it, run the forward, assert output width `= menu_len +
  message_head_len` and that a decoded decision is legal; in the same test, load a
  v2 fixture and assert it still serves (SC-004). Write to fail first.
- [X] T011 [US1] Integration test in `crates/cloudkitty-server/tests/`: boot the
  server against a scripted world with a v3 seat and a v2 seat; assert both log
  their hash and schema versions before the first tick and the world ticks without
  error.

### Implementation for User Story 1

- [X] T012 [US1] Implement the attention forward in
  `crates/cloudkitty-rl/src/attn.rs`: embed (per-type linear + type-emb row), `L`
  pre-norm encoder layers (masked multi-head attention + ReLU FFN), summary
  `[self ∥ masked mean pool]` + LayerNorm, and the four heads scattered into the
  43-wide vector via `ActionCodec::v2`-derived targets (forward-v3.md). Generic
  over `d_model`/`heads`/`encoder_layers`/`ffn`. Depends on T007, T008.
- [X] T013 [US1] Wire `AttnArtifact::forward` into the `PolicyArtifact::V3`
  dispatch and confirm `decide_sync` in `crates/cloudkitty-rl/src/behavior.rs`
  splits the vector at `menu_len` with no change (FR-016). Depends on T012, T003.
- [X] T014 [US1] In `crates/cloudkitty-server/src/lib.rs`, confirm
  `register_policy_behaviors` logs the supported set and schema versions and
  adjust the log/error text for the version set. Depends on T004.

**Checkpoint**: US1 fully functional — v3 and v2 serve side by side.

---

## Phase 4: User Story 2 - Reject an incompatible artifact at startup (Priority: P1)

**Goal**: Every incompatible artifact fails at startup naming the field and
reason, before any tick.

**Independent Test**: Feed the loader one crafted bad artifact per rejection class
and assert a named startup failure with no tick run.

### Tests for User Story 2

- [X] T015 [P] [US2] Reject tests in
  `crates/cloudkitty-rl/tests/artifact_v3_reject.rs`, one case per class —
  version-not-supported, unknown header key, schema mismatch, bad `architecture`,
  bad hyperparameter (`d_model % heads != 0` and non-positive), blob-size
  mismatch — each asserting the error variant and that the message names the
  field/reason. Write to fail first.

### Implementation for User Story 2

- [X] T016 [US2] Add the semantic validation guards to the v3 load path in
  `crates/cloudkitty-rl/src/attn.rs` / `policy.rs` (schema pins, `architecture`,
  hyperparameter positivity + `d_model % heads == 0`, token-width sum, output
  width), and the `Architecture` and `Hyperparameter` error variants, each
  carrying the offending field/reason (contracts/policy-artifact-v3.md "Error
  taxonomy"). Depends on T004, T007.
- [X] T017 [US2] Confirm every failure surfaces with the
  `[rl.policy.<name>].artifact` context through the server load path's existing
  `with_context`; add one reject case to the server integration test if cheap.
  Depends on T016, T014.

**Checkpoint**: US1 and US2 both hold — good artifacts serve, bad ones fail loud.

---

## Phase 5: User Story 3 - Certify the forward against the oracle (Priority: P2)

**Goal**: The Rust forward matches the numpy reference within 1e-4 over the fixed
parity rows, and is reproducible on the same binary.

**Independent Test**: Run the forward on the fixture rows; assert ≤1e-4 max abs
logit error, greedy argmax match, and identical output across two runs.

### Tests for User Story 3

- [X] T018 [P] [US3] Parity test in
  `crates/cloudkitty-rl/tests/artifact_v3_parity.rs`: read the parity fixture,
  run the forward per row, assert ≤1e-4 max abs logit error and greedy activity
  argmax match, and assert two runs give identical output (FR-017, FR-018). Write
  to fail first; `#[ignore]` the real-checkpoint case until the oracle fixture
  lands.

### Implementation for User Story 3

- [X] T019 [P] [US3] Implement the dependency-free parity-fixture reader
  (`u32 n_rows`, `u32 obs_len`, `u32 logit_len`, then `f32` rows) as a small test
  helper (forward-v3.md "Parity fixture format").
- [X] T020 [US3] Provide a parity fixture and verify numeric correctness. DONE
  2026-08-13: Experiments delivered `oracle.ckpolicy` + `oracle.parity` (main @
  8281c07, sha256s verified), now committed at
  `crates/cloudkitty-rl/tests/fixtures/`. The gate is un-`#[ignore]`d and runs in
  CI: **max abs logit error 1.842e-5** over 144 rows (128 real validation rows +
  16 vacancy-stress rows), greedy activity argmax matches on every row — well
  inside the 1e-4 contract. Depends on T012, T009, T019.
- [X] T021 [US3] Add the per-row timing report to the parity test and assert it is
  well under the 800 ms tick (SC-005). Depends on T012.

**Checkpoint**: the forward is certified; a trained checkpoint can become a
servable v3 artifact.

---

## Phase 6: Polish & Cross-Cutting

- [X] T022 [P] Add a v3 policy-artifact line to `CHANGELOG.md` under `## Unreleased`
  (per changelog practice; do NOT tag).
- [X] T023 [P] Add a short "policy artifact v3" note where v2 is documented
  (`docs/`), pointing at the spec 030 contracts rather than restating them.
- [X] T024 Run the `quickstart.md` scenarios end to end and confirm the v2 path is
  byte-identical.
- [X] T025 `cargo fmt` and `cargo clippy` clean across `cloudkitty-rl` and
  `cloudkitty-server`.

---

## Dependencies & Execution Order

- **Setup (T001–T002)**: start immediately.
- **Foundational (T003–T009)**: after setup; BLOCKS all user stories. T003→T004
  are sequential (same file); T005/T006/T008/T009 are parallel; T007 depends on
  T005+T006; T009 on T007.
- **US1 (T010–T014)**: after foundational. T012 depends on T007+T008; T013 on
  T012+T003; T014 on T004.
- **US2 (T015–T017)**: after foundational. T016 depends on T004+T007; T017 on
  T016+T014. Independent of US1 except the shared server test file (T017/T011).
- **US3 (T018–T021)**: after US1's forward (T012). T020's real-checkpoint parity
  is the only task gated on the Experiments oracle; the synthetic round-trip does
  not wait.
- **Polish (T022–T025)**: after the desired stories.

## Parallel Opportunities

- T005, T006, T008, T009 run in parallel within Foundational (distinct concerns in
  the same new file — coordinate or serialize if edited together).
- Once Foundational completes, US1 and US2 can proceed in parallel; US3 follows the
  forward.

## Implementation Strategy

MVP is Setup + Foundational + US1 — a v3 policy serving beside v2. US2 hardens the
loader; US3 certifies the forward. The Experiments oracle gates only T020's real-
checkpoint parity; every other task lands without it.
