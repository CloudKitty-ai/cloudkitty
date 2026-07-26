# Tasks: Kitty-Eval Dedup — Single-Source the Certification CLI

**Input**: Design documents from `/specs/018-kitty-eval-dedup/`

**Prerequisites**: plan.md, spec.md, research.md (D1–D6), data-model.md, contracts/cli-support.md, quickstart.md

**Tests**: The spec requires exactly one new test (FR-009 share-guard); all other verification is the byte-comparison procedure and the unchanged existing suite (FR-007/FR-008). No TDD scaffolding beyond that.

**Organization**: Grouped by the spec's three user stories. Note: this is a refactor of one binary + one library module, so most tasks touch the same files and run sequentially; parallel opportunities are genuinely few and marked honestly.

## Format: `[ID] [P?] [Story?] Description`

## Phase 1: Setup

**Purpose**: Freeze the pre-refactor baseline before any code moves.

- [ ] T001 Capture baseline outputs from a `v2.3` worktree per quickstart.md §1: build the baseline binary, run the suite-mode and single-config-mode commands, store the four outputs (human + JSON × two modes) under `/tmp/ck-018-verify/`; record exit codes. Foreground, generous timeout.

---

## Phase 2: Foundational

**Purpose**: The module every story lands in.

- [ ] T002 Create `crates/cloudkitty-rl/src/cli_support.rs` with the contract's doc header (internal plumbing, not a stability promise — contracts/cli-support.md "Standing") and register `pub mod cli_support;` in `crates/cloudkitty-rl/src/lib.rs`. Compiles empty; `cargo build -p cloudkitty-rl` green.

**Checkpoint**: module exists — story work can begin.

---

## Phase 3: User Story 1 — Run reporting is single-sourced (P1) 🎯 MVP

**Goal**: One renderer for the per-run panel and paired block, consumed by both CLI modes; drift structurally impossible.

**Independent Test**: share-guard test passes; suite-mode and certification-mode outputs byte-identical to T001 baseline (quickstart §1 diff for both modes' human output).

- [ ] T003 [US1] Move `print_run_panel` from `crates/cloudkitty-rl/src/suite.rs` (v2.3 lines 919–948) into `cli_support.rs`: signature `(w: &mut dyn Write, run: &RunOutcome, default_world_bounds: bool)`; `false` arm keeps the FR-003/R11 omission comment (moves with the code); `true` arm inserts the bounds block (PASS / BOUND VIOLATED lines, exact strings from `bin/kitty-eval.rs` v2.3 lines 153–160) between the max-distress-age line and the fallback loop. Update `suite.rs` call sites to `cli_support::print_run_panel(w, run, false)` with a stdout writer.
- [ ] T004 [US1] Move `print_paired` from `suite.rs` (v2.3 lines 950–957) into `cli_support.rs`: signature `(w: &mut dyn Write, paired: &[PairedDelta], baseline_label: &str, prefix: &str)`; suite call sites pass `prefix = "  "` (research D3). Convert the suite-side per-exam printers that call these renderers to thread the writer (public `suite::human_report(&SuiteReport)` signature unchanged — it locks stdout internally, research D4).
- [ ] T005 [US1] Rewire `human_report` in `crates/cloudkitty-rl/src/bin/kitty-eval.rs` (v2.3 lines 126–193): per-run body replaced by `cli_support::print_run_panel(w, run, true)`; paired loop replaced by `cli_support::print_paired(w, &output.paired, "needs_driven baseline"…, "")` — reproduce the current header line `-- paired vs needs_driven baseline --` and aggregate lines locally, unchanged. Delete the now-dead local rendering code.
- [ ] T006 [US1] Add the FR-009 share-guard test in `crates/cloudkitty-rl/tests/eval_suite.rs`: construct one `RunOutcome` fixture; render via `cli_support::print_run_panel` with `default_world_bounds = false` and `true` into buffers; assert (a) the `false` rendering is a byte-prefix+suffix of the `true` rendering differing exactly by the bounds block, (b) `suite::human_report` output for a report embedding that run contains the `false` rendering verbatim. Name contains `share_guard` (quickstart §3 filter).
- [ ] T007 [US1] Checkpoint verification: rebuild, rerun both quickstart §1 feature-side commands, diff human outputs against T001 baseline — byte-identical required before proceeding. `cargo test -p cloudkitty-rl` green.

**Checkpoint**: US1 delivered — rendering single-sourced, guard in tree, bytes proven.

---

## Phase 4: User Story 2 — Subject resolution is single-sourced (P2)

**Goal**: One resolution ladder, one JSON writer, one fallback-gate printer inside the binary; identical messages in both modes by construction.

**Independent Test**: quickstart §2 error-path spot checks — five rejections produce identical text and exit codes vs the T001 baseline binary.

- [ ] T008 [US2] Extract `resolve_subject(registry: &mut BehaviorRegistry, args: &Args, bind_candidate: bool) -> Result<String, ExitCode>` in `bin/kitty-eval.rs`, replacing both ladders (v2.3 lines 206–251 and 336–366); `bind_candidate = true` performs the `suite::CANDIDATE_BEHAVIOR` registration with the existing collision guard (`if name != suite::CANDIDATE_BEHAVIOR`), `false` skips it; every message string appears exactly once afterward (research D2).
- [ ] T009 [US2] Extract `write_json(path: &Path, value: &impl Serialize) -> Result<(), ExitCode>` in `bin/kitty-eval.rs`, replacing both blocks (v2.3 lines 274–287 and 441–454) with the exact `"cannot write {path}: {e}"` message preserved.
- [ ] T010 [US2] Extract the fallback-gate printer (the FR-013 "fails rather than reporting the fallback's welfare" eprintln, v2.3 lines 291–295 and 458–462) into one function used by both modes.
- [ ] T011 [US2] Run quickstart §2: all five error paths against baseline and feature binaries; confirm identical stderr/stdout and exit codes. Record in quickstart.

**Checkpoint**: US2 delivered — binary self-duplication gone.

---

## Phase 5: User Story 3 — Scoring orchestration and self-checking are single-sourced (P3)

**Goal**: The baseline-once / per-mode / self-checked / paired sequence exists once, in `cli_support`; both `score_standard` and the binary consume it.

**Independent Test**: single-config certification JSON + human output byte-identical to baseline; forced determinism failure still exits 3 with unchanged message.

- [ ] T012 [US3] Extract the mode-sweep core from `score_standard` (`suite.rs` v2.3 lines 519–555) into `cli_support`: fn + result struct per data-model.md (baseline runs, per-mode runs, paired deltas; internal first-seed self-check via `suite`'s private `self_check` — keep `self_check` private by having the sweep fn accept the check as the existing code path does, or move the sweep's self-check call through a crate-internal path; the constraint is D5: `self_check` stays out of the public surface). `score_standard` consumes the sweep; cell/baseline self-check call sites (v2.3 lines 642–651, 659–668) untouched.
- [ ] T013 [US3] Rewire the single-config path in `bin/kitty-eval.rs` `main` (v2.3 lines 385–430) to consume the sweep fn; delete the inline baseline/mode-loop/self-check copy; preserve the exact run ordering, `EvalOutput` assembly, and exit-code mapping (determinism → 3 at the same detection point; occurrence-based precedence).
- [ ] T014 [US3] Verify the determinism-failure path: temporarily force a self-check mismatch (local, uncommitted) and confirm both modes exit 3 with the pre-refactor message; revert. `cargo test --workspace` green.

**Checkpoint**: all three stories delivered — the four concerns exist once each.

---

## Phase 6: Polish & Final Verification

- [ ] T015 Run quickstart §5 (SC-004): add a trailing marker to the shared panel header in `cli_support.rs`, observe it in both modes' output, revert; record in quickstart.
- [ ] T016 Run the full quickstart §1 byte-comparison (all four diffs) plus §4 (`cargo test --workspace`; diff of pre-existing test files vs v2.3 shows zero assertion changes); fill every "Record" block in `specs/018-kitty-eval-dedup/quickstart.md`; remove the `/tmp` worktree.
- [ ] T017 `cargo fmt --all` + `cargo clippy --workspace --all-targets -- -D warnings` green; confirm binary production line count decreased vs v2.3 and sweep the survey duplication list (SC-001/SC-005, quickstart §6); update the BACKLOG "Refactoring targets" entry to mark item 1 shipped.

---

## Dependencies & Execution Order

- T001 ⊥ T002 (independent; both before everything else — T001 may run [P] with T002 in wall-clock terms but is listed first to freeze the baseline).
- US1 (T003→T004→T005→T006→T007) strictly sequential (same files); requires T002.
- US2 (T008→T009→T010→T011) sequential within `bin/kitty-eval.rs`; independent of US1's library work in principle, but runs after US1 to keep the binary diff reviewable (owner preference for one-at-a-time applies within the feature too).
- US3 (T012→T013→T014) requires US1's writer conversion in `suite.rs` to be settled (both touch `score_standard`'s neighborhood); runs last of the stories.
- Polish (T015–T017) after all stories.

### Parallel Opportunities

Genuinely few: T001 with T002; nothing else safely parallel (single binary file, single library module). This is expected for a dedup refactor and not worth forcing.

## Implementation Strategy

US1 is the MVP: it alone kills the drift channel with measurement stakes
(the hand-diffed report agreement) and lands the permanent guard. Each
story ends at a byte-verified checkpoint; stopping after any story leaves
the tree green, verified, and strictly better than before. The byte
comparison runs three times (T007 checkpoint, T011 error paths, T016
final) — cheap insurance ordered from most-likely-to-regress to
comprehensive.
