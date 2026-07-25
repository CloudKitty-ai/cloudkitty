# Tasks: Held-Out Evaluation Suite

**Input**: Design documents from `/specs/017-eval-suite/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R11), data-model.md,
contracts/{suite-cli,suite-manifest,exam-configs}.md, quickstart.md

**Tests**: included — the spec names eight guarding tests (Article VI) plus
three contract-bound guards (R3 cell siblings, R7 threshold derivation,
FR-007 distinctness); quickstart.md carries the spec-test → test-name map.

**Organization**: by user story, in spec priority order. Every cargo
invocation needs `export PATH="$HOME/.cargo/bin:$PATH"`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- **[US#]**: user story (spec.md); Setup/Foundational/Polish carry no label

## Phase 1: Setup (the exam data)

**Purpose**: the committed worlds every story runs against. Contents are
fixed by contracts/exam-configs.md — transcription, not design.

- [ ] T001 [P] Create `evals/v1/scale.toml`, `evals/v1/scarcity.toml`, and `evals/v1/heterogeneity.toml` exactly per contracts/exam-configs.md (full TOMLs given there, in-file rationale comments included)
- [ ] T002 [P] Create `evals/v1/mixed-roster-guest.toml`, `evals/v1/mixed-roster-half.toml`, and `evals/v1/mixed-roster-host.toml` per contracts/exam-configs.md — identical except header comment and the behavior column (seat map table in the contract)
- [ ] T003 Create `evals/v1/manifest.toml` per contracts/suite-manifest.md — version `eval-suite-v1`, verdict constants (`differential_tolerance = 0.0`; `tail_probability = 0.01`; thresholds guest 11 / half 10 / host 6 with the binomial-rule derivation comment), four `[[exam]]` entries, `sha256` per member computed from the files as committed (`shasum -a 256 evals/v1/*.toml`); the header comment MUST state the held-out doctrine verbatim (FR-007): "results against a suite version are void if any of its exams appeared in training"

**Checkpoint**: `evals/v1/` complete; every downstream test has its data.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: the two additive harness hooks and the manifest loader every
story builds on.

- [ ] T004 Add `run_one_with(request, observer: impl FnMut(&World))` to `crates/cloudkitty-rl/src/harness.rs` — called once per tick after the tick completes; `run_one` delegates with a no-op observer (research.md R6; behavior byte-identical, SC-004). Unit test in the same file: the observer fires exactly `ticks` times and sees advancing `world.tick`
- [ ] T005 Create `crates/cloudkitty-rl/src/suite.rs` (register in `lib.rs`): `SuiteManifest`/`VerdictConstants`/`ExamEntry`/`CellEntry` deserialization and load-time validation per data-model.md — file existence, SHA-256 verification (mismatch error names the file), config parse + `Config::validate()` + `RlConfig` validation (failure names exam and field), unique exam names, exactly one `mixed-roster` exam, per-cell candidate ≥ 1 and scripted ≥ 1, thresholds present for every cell. Unit tests: a valid manifest parses; a tampered hash and an invalid config each produce the named error

**Checkpoint**: manifest loads and verifies; harness observable — story
implementation can begin.

---

## Phase 3: User Story 1 — suite scoring in one invocation (P1) 🎯 MVP

**Goal**: `kitty-eval --suite evals/v1 --brain needs_driven` scores the
three standard exams (scale/scarcity/heterogeneity) and emits the human +
JSON report. Until US3 lands, the mixed-roster exam appears in the report
as an explicit `pending: mixed-roster scoring lands with US3` entry —
never silently absent, never half-scored. FR-001's "every exam" is
satisfied only when Phase 5 completes; phases 3–5 ship together in this
branch's single PR.

**Independent test**: quickstart.md scenarios 1, 3, 5 — suite numbers
equal standalone single-config runs on the same seeds; two runs produce
byte-identical JSON; an invalid exam fails before any scoring.

- [ ] T006 [US1] Standard-exam orchestration in `crates/cloudkitty-rl/src/suite.rs`: per exam, subject runs (both roster modes for a policy subject, all-subject for a built-in), the all-`needs_driven` baseline, paired deltas, per-mode first-seed determinism self-check — composing the existing `run_many`/`paired_against_baseline`/`run_one`; seeds and ticks from the exam config's own `[rl.eval]` (contracts/suite-cli.md execution order)
- [ ] T007 [US1] Report types in `crates/cloudkitty-rl/src/suite.rs`: `SuiteReport`/`ExamOutcome` per data-model.md — `suite_version`, `subject`, per-exam `config_sha256`, `reference_bounds` with the `calibrated_to: "default world"` label (never a verdict); serde JSON stable-ordered for byte-identical output; human-report rendering per exam **without** the "welfare bounds" verdict line (research.md R11)
- [ ] T008 [US1] `--suite` branch in `crates/cloudkitty-rl/src/bin/kitty-eval.rs`: flag parsing (`--suite DIR`, manifest at `DIR/manifest.toml`); reject `--config`/`--seeds`/`--ticks`/`--roster` alongside it (exit 1); candidate binding — `--artifact` registers the loaded `PolicyBehavior` under `policy:{path}` **and** `policy:candidate`, `--brain` aliases the built-in's `Arc` as `policy:candidate` (research.md R4); execution order and exit codes 1/2/3 per contracts/suite-cli.md (exit 4 lands in US3); missing/empty suite is a usage error
- [ ] T009 [P] [US1] Guarding test `a_suite_run_reproduces_each_exams_standalone_numbers` in `crates/cloudkitty-rl/tests/eval_suite.rs`: suite run on `needs_driven` (short-tick scratch manifest over the real exam configs is acceptable for runtime) equals standalone harness runs per exam, same seeds
- [ ] T010 [P] [US1] Guarding test `an_invalid_exam_fails_the_suite_before_any_scoring` in `crates/cloudkitty-rl/tests/eval_suite.rs`: scratch manifest pointing at a `width = 0` config → error names exam file and field, nothing scored; plus a wrong-hash variant naming the file
- [ ] T011 [P] [US1] Guarding test `two_suite_runs_produce_identical_json` in `crates/cloudkitty-rl/tests/eval_suite.rs`: serialize two `SuiteReport`s from two runs; assert byte equality (SC-002)

**Checkpoint**: MVP — the suite mode measures, loudly and reproducibly.

---

## Phase 4: User Story 2 — the v1 exams are lawful, distinct instruments (P2)

**Goal**: the committed exam worlds are proven lawful and provably not
training/certification configs.

**Independent test**: quickstart.md scenario 1's cross-check plus the two
tests below — runnable without US1 (they drive the harness directly).

- [ ] T012 [P] [US2] Guarding test `every_v1_exam_sustains_an_invariant_asserted_run` in `crates/cloudkitty-rl/tests/eval_suite.rs`: each `evals/v1/*.toml` (cells with `policy:candidate` normalized to `needs_driven` for this test) loads, validates, and sustains a ≥ 2,000-tick `run_one` with zero fallbacks and the per-tick invariant assertions active (spec guarding test 5; expected numbers ≈ the measured baselines in contracts/exam-configs.md)
- [ ] T013 [P] [US2] Guarding test `no_exam_equals_a_training_or_certification_config` in `crates/cloudkitty-rl/tests/eval_suite.rs`: no `evals/v1/*.toml` byte-equals `cloudkitty.toml`, `training.toml`, `cloudkitty16.toml`, or `cloudkitty48.toml`; plus parsed axis assertions (SC-005): scale has ≥ 2× the default world's tiles and a roster larger than training's 5; scarcity's minimums equal the `hard_min` floor per element type; heterogeneity's max/min trait-rate ratio exceeds both other worlds'; the mixed-roster geometry (28×28) and roster size (6) appear in neither `cloudkitty.toml` nor `training.toml` (FR-007, SC-005)

**Checkpoint**: the instrument's content is certified lawful and held-out.

---

## Phase 5: User Story 3 — the mixed-roster exam and its verdict (P2)

**Goal**: composition cells, the all-scripted baseline, the guest-welfare
differential, identity and duet reads, the verdict, exit 4.

**Independent test**: quickstart.md scenario 2 — `--brain playful` bound
as candidate runs the exam end-to-end and renders a verdict, no artifact
required.

- [ ] T014 [US3] Cell orchestration in `crates/cloudkitty-rl/src/suite.rs`: per cell, `EvalRequest { subject: None, .. }` runs of the frozen cell config (research.md R5); the derived all-scripted baseline — clone the cell config, rewrite every `behavior == "policy:candidate"` to `"needs_driven"`, scripted seats untouched (R4) — on the same seeds; paired deltas; per-cell and baseline first-seed determinism self-checks (R9)
- [ ] T015 [US3] Cell metrics in `crates/cloudkitty-rl/src/suite.rs`: `KittyDifferential` (scripted seats: seed-mean `mean_happiness` cell vs baseline), `least_happy_out_group_seeds` per cell, `DuetShare` per kitty via a `run_one_with` observer counting `Kitty::partner().is_some()` ticks (data-model.md; R6)
- [ ] T016 [US3] Verdict in `crates/cloudkitty-rl/src/suite.rs` + exit wiring in `crates/cloudkitty-rl/src/bin/kitty-eval.rs`: `MixedRosterVerdict` evaluating the three checks per cell against `VerdictConstants` (R7), `ExploitationSignature` emission (negative differential under passing aggregate check — cell, kitty, differential), human verdict block per contracts/suite-cli.md, exit 4 with precedence 1 > 2 > 3 > 4 (R8). Verdict evaluation is a pure function over `CellOutcome`s, unit-testable on synthetic data
- [ ] T017 [P] [US3] Guarding test `a_builtin_candidate_exercises_cells_differentials_and_verdict` in `crates/cloudkitty-rl/tests/eval_suite.rs`: `playful` bound as `policy:candidate` (short-tick scratch manifest over the real cell files) → three cells + baseline run, differentials/identity/duet populated, a verdict rendered (spec test 7a; SC-007)
- [ ] T018 [P] [US3] Guarding test `a_negative_host_differential_renders_the_exploitation_signature` in `crates/cloudkitty-rl/tests/eval_suite.rs`: synthetic `CellOutcome`s with a negative host-cell differential under a healthy aggregate → verdict fails, signature names cell, kitty, and differential (spec test 7b)
- [ ] T019 [P] [US3] Guarding test `two_subjects_share_the_frozen_exam_without_touching_it` in `crates/cloudkitty-rl/tests/eval_suite.rs`: score `needs_driven` then `playful` as candidate; assert `evals/v1/` file bytes unchanged between and after runs; plus one assertion that a cell config with **no** candidate binding fails `validate_behavior_names` loudly, naming the kitty and `policy:candidate` (spec test 8, FR-011 including its outside-suite clause)
- [ ] T020 [P] [US3] Guarding test `cell_configs_differ_only_in_behavior` in `crates/cloudkitty-rl/tests/eval_suite.rs`: parse the three cell TOMLs; assert equality of every field except `[[kitty]].behavior` (R3)
- [ ] T021 [P] [US3] Guarding test `least_happy_thresholds_match_the_binomial_rule` in `crates/cloudkitty-rl/tests/eval_suite.rs`: recompute smallest k with P(Binomial(n_seeds, out_share) ≥ k) ≤ the manifest's `tail_probability` — every input read from the manifest and the cell configs (seed count from `[rl.eval]`, out-group share from scripted-seat counts), nothing hardcoded but the rule itself; assert manifest values 11/10/6 (R7)

**Checkpoint**: the exploitation probe works and is provably artifact-agnostic.

---

## Phase 6: User Story 4 — freeze and versioning (P3)

**Goal**: a landed suite version is mechanically immutable; results carry
their identity.

**Independent test**: quickstart.md scenario 4 — append one byte to a
landed exam; startup and CI both fail naming the file; restore; both pass.

- [ ] T022 [US4] Guarding test `a_landed_exam_file_cannot_change_without_failing_ci` in `crates/cloudkitty-rl/tests/eval_suite.rs`: walk every `evals/*/manifest.toml` in the repository, recompute each member's SHA-256, assert equality with the recorded value — failure names the file (spec test 2, SC-003; old versions stay guarded forever). Note for the future: when a v2 lands, add a side-by-side test that each version invoked by name runs exactly its own exams (FR-012's multi-version clause — untestable while only v1 exists)
- [ ] T023 [US4] Land `eval-suite-v1`: recompute final hashes over the exam files as actually committed, record them in `evals/v1/manifest.toml`, run quickstart.md scenario 4 (tamper → both guards fail naming the file → restore → both pass), and verify a full suite run stamps `suite_version` and per-exam `config_sha256` in the JSON (FR-013)

**Checkpoint**: frozen means frozen, demonstrably.

---

## Phase 7: Polish & cross-cutting

- [ ] T024 [P] Run all six quickstart.md scenarios end-to-end and record actual vs expected in a comment on the PR (SC-001, SC-002, SC-003, SC-007 covered; scenario 6 confirms SC-004)
- [ ] T025 [P] Add a short "The exam suite" paragraph to `docs/rl-training.md` under Scoring and deploying: `kitty-eval --suite evals/v1` measures beside the bar, the default world remains the sole certification bar, exam bounds doctrine in one sentence, and the held-out doctrine verbatim (FR-007): results against a suite version are void if any of its exams appeared in training
- [ ] T026 `cargo fmt --all`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` green; confirm existing harness/binary tests pass **unmodified** (SC-004) and the single-config invocation output is byte-shaped as before

---

## Dependencies

```text
Phase 1 (T001–T003) ──► Phase 2 (T004, T005) ──► US1 (T006→T007→T008; T009–T011 after T008)
                                        │
                                        ├──► US2 (T012, T013 — needs only Phase 1 + T004)
                                        │
                                        └──► US3 (T014→T015→T016; T017–T021 after T016;
                                              T014 also needs T008's candidate binding)
US1 + US3 ──► US4 (T022 after T003; T023 last before Polish)
All ──► Polish (T024–T026)
```

- T001 ∥ T002 (different files); T003 needs both.
- T004 ∥ T005 (different files).
- Within US1: T006 → T007 → T008 sequential (same files); T009–T011 parallel after T008.
- US2 (T012–T013) can run in parallel with all of US1 — it needs only the
  exam files and `run_one`.
- Within US3: T014 → T015 → T016 sequential (suite.rs); T017–T021 parallel
  after T016.
- T022 anytime after T003; T023 is the landing step — after every task
  that could touch `evals/v1/`.

## Parallel execution examples

- **After Phase 2**: one track starts T006 (US1) while another writes
  T012/T013 (US2) — disjoint files, disjoint concerns.
- **After T008**: T009, T010, T011 in parallel (independent tests, one
  shared test file — coordinate on file creation, then parallel test fns).
- **After T016**: T017–T021 in parallel (same coordination note).

## Implementation strategy

**MVP first**: Phases 1–3 deliver US1 — a working, reproducible,
loud-failing suite mode over the real exam files, with the mixed-roster
exam explicitly `pending` until US3. A complete increment for review, not
for shipping: the branch ships whole (phases 3–5 together satisfy
FR-001's "every exam").

**Increment 2**: US2 certifies the content (cheap, parallel with US1).

**Increment 3**: US3 is the feature's heart — the exploitation probe —
and lands as one reviewable unit: orchestration, metrics, verdict, exit 4.

**Increment 4**: US4 landing freezes v1 — deliberately last, so hashes are
recorded exactly once, over files nothing will touch again.

Per CLAUDE.md: fix success criteria first (each phase's checkpoint and the
quickstart scenarios are those criteria), loop until verified, never
weaken a test to pass.
