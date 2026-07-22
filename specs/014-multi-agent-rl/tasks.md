# Tasks: Multi-Agent RL Readiness

**Input**: Design documents from `/specs/014-multi-agent-rl/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — the spec and Article VI name guarding tests explicitly
(golden parity, codec totality, encoder determinism, mask oracle,
reproducibility, welfare with a policy kitty). Test tasks precede their
implementation tasks and must fail first.

**Organization**: Grouped by user story. The spec's phasing is deliberately
stacked (seam → encodings → Python → evaluation → deployment): US1 is the
load-bearing slice; US2–US4 each stand on it but remain independently
testable increments.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- **[Story]**: US1–US4 from spec.md
- Paths are exact; crate layout per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: the two new crates exist, compile empty, and CI knows about them

- [X] T001 Add `cloudkitty-rl` workspace member: create `crates/cloudkitty-rl/Cargo.toml` (deps: cloudkitty-core, serde, serde_json, rand, rand_chacha, thiserror, tracing; dev-deps: proptest, toml) and `crates/cloudkitty-rl/src/lib.rs` declaring empty modules `config`, `observe`, `codec`, `mask`, `global_state`, `reward`, `episode`, `vector`, `welfare`, `policy`, `behavior`; add the member to the root `Cargo.toml`
- [X] T002 [P] Add `cloudkitty-py` crate: `crates/cloudkitty-py/Cargo.toml` (cdylib, pyo3 with `abi3-py39` + `extension-module`, numpy, cloudkitty-rl), `crates/cloudkitty-py/pyproject.toml` (maturin build backend), stub `crates/cloudkitty-py/src/lib.rs` with an empty `#[pymodule]`; add the member to the root `Cargo.toml` (gate `extension-module` behind a feature so plain `cargo test` still links)
- [X] T003 [P] Extend `.github/workflows/ci.yml`: run `cargo test -p cloudkitty-rl` in the standard job; add a **required** Python job (maturin develop + pytest in `crates/cloudkitty-py` — SC-002's two-process reproducibility gate lives here, so the job must gate the merge once T030 lands); only the optional `pettingzoo` conformance step is continue-on-error

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the dispatch split every headless path stands on (research.md R5, FR-017)

**⚠️ CRITICAL**: no user story work can begin until this phase is complete

- [X] T004 Split dispatch in `crates/cloudkitty-core/src/behavior/mod.rs`: extract a pure budgetless decision resolver (panic isolation + `needs_driven` fallback + per-decision provenance mark `PolicyMade`/`FallbackTaken`, no wall clock) and re-express today's served-world path as that resolver wrapped in the existing `tokio::time::timeout` — behavior byte-for-byte unchanged; the entire existing test suite must pass untouched
- [X] T005 Expose the parity-capture seam from the resolver in `crates/cloudkitty-core/src/behavior/mod.rs`: the per-kitty decision seeds (drawn in stable id order, as today) and the dispatched proposals are returned to the caller — never stored in world state (research.md R4)

**Checkpoint**: foundation ready — US1 can begin

---

## Phase 3: User Story 1 — Joint-action tick seam (Priority: P1) 🎯 MVP

**Goal**: advance the world one constitutional tick from externally supplied
per-kitty proposals, with the honest proposed/validated/applied record —
byte-identical futures from the same seed (contracts/joint-action-seam.md)

**Independent Test**: drive a world ≥ 5,000 ticks by externally feeding it
the decisions its built-ins would have made; serialization (RNG state
included) is byte-identical to the behavior-driven run

### Tests for User Story 1 (write first, must fail)

- [X] T006 [P] [US1] Golden-parity test (SC-001): behavior-driven run collecting dispatched proposals vs joint-action run fed those proposals, same seed, default world, ≥ 5,000 ticks, byte-identical serialization including RNG state, in `crates/cloudkitty-core/tests/joint_action_parity.rs`
- [X] T007 [P] [US1] Degradation test: joint proposals with one absent entry, one malformed substitution, and one unknown-id entry → those kitties idle / entry reported unconsumed, all others act, invariants hold, in `crates/cloudkitty-core/tests/joint_action_degradation.rs`

### Implementation for User Story 1

- [X] T008 [US1] Define `JointProposal`, `TickReport` (per-kitty proposed/validated/applied triple + provenance + decision seed; tick-level distress events and activity endings), and `Provenance` in a new `crates/cloudkitty-core/src/seam.rs`, exported from `lib.rs` — the joint-action absent/malformed substitution gets its own provenance variant (e.g. `SubstitutedIdle`), never reusing `FallbackTaken` (FR-017's mark is for dispatched decisions)
- [X] T009 [US1] Refactor `World::tick` internals in `crates/cloudkitty-core/src/world.rs` into one shared phase pipeline (fair order → validate → durations → apply → activity ends → environment → needs → distress → purr → invariants) consumed by the existing tick — no observable change; full suite still green
- [X] T010 [US1] Implement `World::tick_with_proposals` in `crates/cloudkitty-core/src/world.rs`: identical master-RNG draw shape (per-kitty decision seeds in stable id order, fair-order draws), behavior dispatch as the only bypassed step, returns the `TickReport`
- [X] T011 [US1] Implement the budgetless behavior-driven driver `drive_tick` in `crates/cloudkitty-core/src/seam.rs` (uses the T004 resolver; returns `TickReport` plus the dispatched proposals — the parity capture)
- [X] T012 [US1] Draw-shape assertion: RNG state after a joint-action tick equals RNG state after the equivalent behavior-driven tick, added to `crates/cloudkitty-core/tests/joint_action_parity.rs`; make T006/T007 pass; run the full workspace suite

**Checkpoint**: the seam ships — independently valuable (scripted scenarios,
replay harnesses, the backlog's plugin door)

---

## Phase 4: User Story 2 — Cooperative rollouts in Python (Priority: P2)

**Goal**: PettingZoo-parallel rollouts from Python with observations, masks,
global state, one team reward, mixed control, and vectorized batches
(contracts/encodings.md, contracts/python-env.md)

**Independent Test**: random-policy rollout from Python matches the contract
(shapes, bounds, bookkeeping); two processes with the same seed and action
sequence produce bit-identical observation/mask/global-state/reward streams

### Encodings (Rust, `cloudkitty-rl`)

- [X] T013 [P] [US2] `RlConfig` types parsing the `[rl.*]` TOML blocks with documented defaults (slot counts 3/4/2/2/2, normalization constants, reward `p`/`epsilon`/`mode`/shaping-off, horizons 2000/20000) in `crates/cloudkitty-rl/src/config.rs` (Article VI: every constant configured)
- [X] T014 [US2] Observation encoder + `TargetTable` in `crates/cloudkitty-rl/src/observe.rs`: schema v1 per data-model.md — self block with static traits, kitty and critter slots with **target-priority fill** (nearest, ties by id, the ongoing activity's referenced kitty or played-with critter always granted a slot — keyed on `Activity::partner()` plus the `Playing` element target, not `duet_partner()` — `is-activity-target` bit), chow/water/sunbeam slots nearest-K, meow digest, episode clock; version and exact-size constants exported
- [X] T015 [US2] Action codec v1 in `crates/cloudkitty-rl/src/codec.rs`: the normative 40-entry table from contracts/encodings.md, total both directions (vacant/stale slots decode to engine-rejectable proposals, never errors)
- [X] T016 [US2] Legal-action mask v1 in `crates/cloudkitty-rl/src/mask.rs`: one bit per entry, "applies as proposed" against the frozen snapshot (validation passes + duration enforcement would not rewrite), versioned with the codec
- [X] T017 [P] [US2] Global state v1 in `crates/cloudkitty-rl/src/global_state.rs`: full roster untruncated, bounded configured element summary, episode clock; versioned
- [X] T018 [P] [US2] Team reward in `crates/cloudkitty-rl/src/reward.rs`: unclamped happiness recomputed from needs × configured weights, normalized, power mean over the full roster with `ε`; level default, delta option; shaping hook potential-based and off by default

### Encoding tests

- [X] T019 [P] [US2] Codec-totality proptest (every index ↔ proposal, both directions, random worlds and vacant slots) in `crates/cloudkitty-rl/tests/codec_totality.rs`
- [X] T020 [P] [US2] Mask pure-oracle proptest — for every menu entry, mask verdict == engine validate-plus-enforcement verdict, **no carve-outs** — plus the never-all-zero property across randomized rosters/activities including named crowded-continuation constructions exercising target-priority: a ≥ 5-kitty crowded duet, a crowded co-sleep, a crowded groom, and a default-population critter cluster around an ongoing element play, in `crates/cloudkitty-rl/tests/mask_oracle.rs`
- [X] T021 [P] [US2] Encoder determinism + bounds tests (same snapshot → identical observation and global-state vectors; all values in documented bounds) in `crates/cloudkitty-rl/tests/encoding_determinism.rs`
- [X] T022 [P] [US2] Reward property tests (strictly increasing; concave; finite value/gradient at zero via ε; p ∈ {1, 0, −8} behaviors) in `crates/cloudkitty-rl/tests/reward_properties.rs`

### Episodes and vectorization

- [X] T023 [US2] `Episode` in `crates/cloudkitty-rl/src/episode.rs`: reset(seed)/step per data-model.md — decode via codec + target table, **mixed control** (scripted kitties resolved from their own engine-dealt decision streams via the T004 resolver), truncation-only at horizon (≥ 1 enforced at construction), infos with applied action/survived/mask/decision seed/provenance
- [X] T024 [US2] `VectorizedEnvironment` in `crates/cloudkitty-rl/src/vector.rs`: N independent worlds, `std::thread::scope` fan-out, positionally gathered results
- [X] T025 [P] [US2] Mixed-control test (scripted kitties bit-deterministic; team reward counts the full roster) in `crates/cloudkitty-rl/tests/mixed_control.rs`
- [X] T026 [P] [US2] Vectorized-independence test (world i in a batch == the same world stepped alone) in `crates/cloudkitty-rl/tests/vector_independence.rs`

### Python surface (`cloudkitty-py`)

- [X] T027 [US2] `ParallelEnv` PyO3 wrapper in `crates/cloudkitty-py/src/lib.rs`: reset/step/state()/agents/possible_agents/observation_space/action_space per contracts/python-env.md; NumPy arrays out; out-of-range action raises, in-range vacant-slot actions never do; GIL released around engine work
- [X] T028 [US2] `VectorEnv` wrapper in `crates/cloudkitty-py/src/lib.rs` (same file — sequential after T027): batched reset/step, leading world axis, GIL released across the fan-out
- [X] T029 [P] [US2] pytest smoke in `crates/cloudkitty-py/tests/test_parallel_env.py`: shapes, bounds, terminations always false, truncation exactly at horizon, one broadcast team scalar, info keys
- [X] T030 [P] [US2] Two-process bit-reproducibility test (SC-002: observation, mask, global-state, and reward streams) in `crates/cloudkitty-py/tests/test_reproducibility.py`
- [X] T031 [P] [US2] `crates/cloudkitty-py/examples/random_rollout.py` and `crates/cloudkitty-py/examples/bench.py` (bench prints steps/s single-threaded and vectorized-scaling, with the measurement method printed alongside — SC-003)
- [X] T032 [US2] Optional PettingZoo conformance test (skipped cleanly when the package is absent) in `crates/cloudkitty-py/tests/test_pettingzoo_conformance.py`

**Checkpoint**: trainers can produce cooperative rollouts; US2 independently done

---

## Phase 5: User Story 3 — Score any brain against the welfare bar (Priority: P2)

**Goal**: `kitty-eval` reports the trusted long-run welfare scorecard for any
built-in, with paired-seed baseline comparison (contracts/evaluation-harness.md);
artifact scoring joins in US4

**Independent Test**: the harness on `needs_driven` and `playful` reproduces
the welfare suite's numbers for the same seeds; the paired comparison is
stable across repeat runs

- [X] T033 [US3] Lift the long-run welfare metric computation from `crates/cloudkitty-core/tests/welfare_longrun.rs` into `crates/cloudkitty-rl/src/welfare.rs` (mean happiness, low streaks and share, floor touches, pinned streaks, distress age) and rewire the CI test to consume the shared module — same numbers, one implementation (research.md R7)
- [X] T034 [US3] `kitty-eval` binary in `crates/cloudkitty-rl/src/bin/kitty-eval.rs`: CLI per the contract (`--brain`/`--artifact`, `--config`, `--seeds`, `--ticks`, `--roster`, `--json`); budgetless headless runs; JSON + human table per seed and aggregated; welfare aggregate with plain mean and least-happy mean beside it; paired `needs_driven` baseline deltas; fallback counting with nonzero → nonzero exit
- [X] T035 [P] [US3] Baseline-reproduction test (harness numbers == welfare suite's for the same seeds, `needs_driven` and `playful`) in `crates/cloudkitty-rl/tests/harness_baseline.rs`
- [X] T036 [P] [US3] Paired-comparison stability test (repeat runs identical) in `crates/cloudkitty-rl/tests/harness_stability.rs`

**Checkpoint**: the bar exists and baselines the built-ins before any training

---

## Phase 6: User Story 4 — A kitty gets a trained mind (Priority: P3)

**Goal**: a config-named, validated, content-hashed artifact seated in the
existing behavior seam; the whole CI suite passes with a policy kitty
(contracts/policy-artifact.md)

**Independent Test**: a config naming a policy boots the server with the
artifact validated and hash-logged before any tick; a corrupted artifact
fails startup naming the config field; the full suite passes with the
policy kitty rostered

- [X] T037 [P] [US4] Artifact format v1 in `crates/cloudkitty-rl/src/policy.rs`: length-prefixed JSON header (versions, layer shapes, activation) + little-endian f32 blob; loader with full startup validation chain and SHA-256 content hash (logged + exposed); include a writer helper for test fixtures
- [X] T038 [US4] MLP forward pass in `crates/cloudkitty-rl/src/policy.rs`: hand-rolled f32, fixed accumulation order, reused buffers, no I/O (research.md R3)
- [X] T039 [US4] `PolicyBehavior` in `crates/cloudkitty-rl/src/behavior.rs`: encode → infer → mask → select → decode; greedy default with lowest-index ties; optional sampling from the kitty's decision stream; non-finite-logit totality (never NaN into a proposal); implements the existing `Behavior` trait as a non-built-in
- [X] T040 [US4] Server wiring in `crates/cloudkitty-server/src`: `behavior = "policy:<name>"` resolved through `[rl.policy.<name>].artifact`, constructed at startup via cloudkitty-rl, validation failure exits with an error naming the config field (add the cloudkitty-rl dependency to `crates/cloudkitty-server/Cargo.toml`)
- [X] T041 [P] [US4] Artifact validation tests (missing / truncated / corrupt / schema-mismatched → error naming the field; hash stability across loads) in `crates/cloudkitty-rl/tests/artifact_validation.rs`
- [X] T042 [P] [US4] Selection tests (same artifact + observation + decision seed → same action across processes; garbage logits — NaN, ±inf, all-equal — still select a masked-in action) in `crates/cloudkitty-rl/tests/policy_selection.rs`
- [X] T043 [US4] `kitty-eval` artifact scoring integration in `crates/cloudkitty-rl/tests/harness_policy.rs`: both roster modes scored (all-policy and one-among-`needs_driven`); a deliberately panicking artifact → nonzero exit with fallback counts reported (FR-013; US3 scenarios 3–4)
- [X] T044 [US4] Server integration test in `crates/cloudkitty-server/tests/policy_kitty.rs`: boot with a fixture policy config (hash logged before tick 1), corrupted-artifact startup failure naming `[rl.policy.<name>].artifact`, viewer-visible state indistinguishable from a built-in kitty
- [X] T045 [US4] Full-suite-with-policy-kitty guard in `crates/cloudkitty-rl/tests/policy_ci.rs`: determinism and welfare suites run with a fixture policy kitty rostered (SC-005's suite clause) as normal CI gates; the p99 decision-latency check (< 10% of the default budget) is an `#[ignore]`-by-default test run explicitly on the reference machine, method documented in the test

**Checkpoint**: all four stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T046 [P] `docs/rl-training.md`: reference training script (any PettingZoo-compatible cooperative trainer) + artifact exporter walkthrough, using the recommended training world from research.md R11 (5 kitties on 24×24, roster-randomized vectorized batches) — documentation, not a supported surface (spec Assumptions)
- [ ] T047 [P] Record measured SC-003 throughput and its measurement method in `specs/014-multi-agent-rl/quickstart.md` beside the ≥ 5,000 steps/s target, pinning a numeric floor for "near-linear" scaling (e.g. ≥ 6× at 8 workers) from the measured result
- [ ] T048 Run the full `specs/014-multi-agent-rl/quickstart.md` validation end-to-end; SC-006 cleanliness checks (no reward vocabulary in `crates/cloudkitty-core/src/`; every new constant reachable from `cloudkitty.toml` `[rl.*]`; constitution untouched at v1.1.0)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (P1)**: none
- **Foundational (P2)**: after Setup — **blocks everything**
- **US1 (P3)**: after Foundational; the seam is the load-bearing slice
- **US2 (P4)**: after US1 (episodes step through the seam)
- **US3 (P5)**: after US1 + T004/T005 (headless driver, welfare module); does **not** need US2's Python surface — built-in scoring ships without it; T033 can start any time after Setup
- **US4 (P6)**: after US2 (encodings, mask, codec) and US3 (T034 for T043); T037/T038 can start after Setup
- **Polish (P7)**: after all stories

### Within-story ordering

- Tests are written first and must fail (T006/T007 before T008–T012;
  T019–T022 may be written alongside their modules but must fail before
  the module lands)
- T014 → T015 → T016 are sequential (codec names observation slots; mask
  needs both); T009 → T010 sequential (same file)
- T027 → T028 sequential (same `lib.rs`)

### Parallel Opportunities

- Setup: T002, T003 together after T001
- US1 tests: T006 ∥ T007
- US2: T013 ∥ T017 ∥ T018 while T014–T016 proceed sequentially; all four
  encoding-test tasks T019–T022 in parallel; T025 ∥ T026; T029–T031 in
  parallel after T028
- US3: T035 ∥ T036 after T034
- US4: T037 ∥ T041 ∥ T042 fan-out; T046 ∥ T047 in Polish
- Cross-story: after US1, one contributor can run US2 while another does
  T033–T036 (US3 built-in scoring) — they share no files

---

## Parallel Example: User Story 2

```bash
# After T014–T016 land, launch the encoding guards together:
Task: "Codec-totality proptest in crates/cloudkitty-rl/tests/codec_totality.rs"
Task: "Mask pure-oracle proptest in crates/cloudkitty-rl/tests/mask_oracle.rs"
Task: "Encoder determinism tests in crates/cloudkitty-rl/tests/encoding_determinism.rs"
Task: "Reward property tests in crates/cloudkitty-rl/tests/reward_properties.rs"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phases 1–2 (setup + dispatch split)
2. Phase 3: the joint-action seam, parity-proven
3. **STOP and VALIDATE**: golden parity green in CI — the seam alone is
   worth shipping (scripted scenarios, replay tooling, the plugin door)

### Incremental Delivery

Each story lands as its own reviewable increment behind green CI:
seam (US1) → rollouts (US2) → scorecard (US3) → deployment (US4) →
polish. US3's built-in baselines can land before or alongside US2 if the
sitting allows — they share only the Phase 2 foundation.

---

## Notes

- Constitution guards ride every phase: the full existing suite must stay
  green after T004, T009, and every engine-adjacent task
- Commit after each task or logical group (branch discipline per repo
  convention; CI green before merge)
- Total: 48 tasks — Setup 3, Foundational 2, US1 7, US2 20, US3 4,
  US4 9, Polish 3
