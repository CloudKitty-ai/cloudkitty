# Tasks: Python Training Surface — Dependency Advisory Clearance (pyo3 Upgrade)

**Input**: Design documents from `/specs/015-pyo3-upgrade/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/python-surface.md, quickstart.md

**Tests**: No new test tasks — by design (spec FR-003, research.md §4): the **unmodified** existing suite IS the acceptance instrument. Any task that edited a test file would violate SC-002.

**Organization**: Tasks grouped by user story. This feature is unusual: the entire code change is foundational (one crate compiles at the new versions), and each user story is then an independent *verification* increment against its own gate.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files / no dependencies)
- **[Story]**: US1 (audit clean), US2 (behavior parity), US3 (build path)

## Path Conventions

Single Rust workspace at repo root; the feature touches only `crates/cloudkitty-py/` plus `Cargo.lock` and `BACKLOG.md`.

---

## Phase 1: Setup (Baseline Capture)

**Purpose**: Record the pre-upgrade truth the success criteria are measured against.

- [ ] T001 Verify tooling: `cargo audit` installed (`cargo install cargo-audit` if missing) and a Python ≥3.9 virtualenv with floating `maturin pytest numpy` (mirroring CI), per quickstart.md Prerequisites
- [ ] T002 Capture the pre-upgrade baseline: run `cargo audit` at repo root and save its output (expect exactly 2 advisories: RUSTSEC-2025-0020, RUSTSEC-2026-0177 against pyo3 0.21.2) to `specs/015-pyo3-upgrade/baseline-audit.txt`
- [ ] T003 Capture the pre-upgrade Python gate: `cd crates/cloudkitty-py && maturin develop --release && pytest tests -v` — record pass/fail status (including the PettingZoo conformance result if installed) as the parity reference for US2/US3

**Checkpoint**: Baseline recorded — every later "unchanged" claim now has a referent.

---

## Phase 2: Foundational (The Upgrade Itself)

**Purpose**: The one real code change. Everything after this phase is verification.

**⚠️ CRITICAL**: No user story verification is meaningful until this phase compiles clean.

- [ ] T004 Bump `pyo3 = { version = "0.29", features = ["abi3-py39"] }` and `numpy = "0.29"` in `crates/cloudkitty-py/Cargo.toml` (targets verified available: research.md §1)
- [ ] T005 Fix compile errors in `crates/cloudkitty-py/src/lib.rs` until `cargo build -p cloudkitty-py` succeeds — expected: `into_pyarray_bound` → `into_pyarray` (9 sites), `PyArray1::from_vec_bound` → `from_vec` (1 site), possible `IntoPyObject`/`Py<PyAny>` adjustments in `box_space`/`discrete_space`/`observation_space`/`action_space`; consult pyo3 0.22–0.29 migration guides for anything unexpected (research.md §2)
- [ ] T006 Regenerate `Cargo.lock` (falls out of the build) and confirm no other workspace member's dependencies changed: `git diff Cargo.lock` shows only pyo3/numpy-family churn
- [ ] T007 Run `cargo test` (full workspace) at repo root — all Rust tests pass, including cloudkitty-py's non-extension-module link path
- [ ] T008 Deprecation sweep per spec edge case: note any deprecation warnings from `cargo build -p cloudkitty-py 2>&1`; fix only mechanical ones in `crates/cloudkitty-py/src/lib.rs`, and list any deliberately left in the PR description for the next maintenance pass

**Checkpoint**: Workspace compiles and passes Rust tests at pyo3/numpy 0.29 — user story gates can now run (in any order, or in parallel).

---

## Phase 3: User Story 1 - A Clean Security Audit (Priority: P1) 🎯 MVP

**Goal**: `cargo audit` reports zero advisories (SC-001), closing the reason this feature exists.

**Independent Test**: One command at repo root; compare against T002's baseline.

- [ ] T009 [US1] Run `cargo audit` at repo root — expect **0 advisories** (baseline was 2); save output beside the baseline as `specs/015-pyo3-upgrade/post-audit.txt`
- [ ] T010 [P] [US1] Confirm the vulnerable versions are gone from the dependency graph: `grep -A2 'name = "pyo3"' Cargo.lock` shows only 0.29.x, no 0.21.x remnant anywhere in `Cargo.lock`

**Checkpoint**: SC-001 met — the audit is clean.

---

## Phase 4: User Story 2 - Training Scripts Don't Notice (Priority: P2)

**Goal**: Zero observable behavior change (FR-003/FR-004): unmodified suite passes, rollouts bit-identical.

**Independent Test**: Build the extension, run the untouched pytest suite, diff the surface against the contract.

- [ ] T011 [US2] Build and test: `cd crates/cloudkitty-py && maturin develop --release && pytest tests -v` — 100% pass with `git status` confirming **zero modified files under `crates/cloudkitty-py/tests/`** (SC-002); the two-process reproducibility test passing IS the bit-identical gate (SC-003)
- [ ] T012 [P] [US2] Optional-dependency scenario: with `pettingzoo` installed, run `pytest crates/cloudkitty-py/tests/test_pettingzoo_conformance.py -v` — result no worse than T003's baseline (spec US2 scenario 3)
- [ ] T013 [P] [US2] Contract check per quickstart.md §6: introspect the built module (`dir(cloudkitty)`, `dir(cloudkitty.ParallelEnv)`, `dir(cloudkitty.VectorEnv)`) and verify every name, constant, and signature matches `specs/015-pyo3-upgrade/contracts/python-surface.md` exactly — nothing added, renamed, or missing

**Checkpoint**: SC-002/SC-003 met — the surface didn't move.

---

## Phase 5: User Story 3 - The Build Path Keeps Working Everywhere (Priority: P3)

**Goal**: Same commands, same floors, zero CI edits (FR-006/FR-007/FR-008).

**Independent Test**: Confinement spot-checks locally; CI's unchanged job goes green on the PR.

- [ ] T014 [P] [US3] Confinement checks per quickstart.md §5: `cargo tree -p cloudkitty-server | grep pyo3` finds nothing (server stays pyo3-free, FR-007) and `grep abi3-py39 crates/cloudkitty-py/Cargo.toml` confirms the CPython ≥3.9 floor survived the bump (FR-006)
- [ ] T015 [US3] Verify zero CI changes: `git diff --stat` for the whole branch shows nothing under `.github/` (FR-008); final confirmation is the unchanged `python surface (maturin + pytest)` job passing on the PR (SC-004)

**Checkpoint**: All three stories verified independently.

---

## Phase 6: Polish & Close-Out

**Purpose**: Retire the gate this feature exists to clear.

- [ ] T016 Remove the "Upgrade pyo3 past its advisories" entry from `BACKLOG.md` P1 (SC-005), noting in the PR that the RL-work gate is retired (unblocks P4 crepuscular rewards)
- [ ] T017 Run the full quickstart.md runbook top-to-bottom once, in order, as the final end-to-end validation; then delete the scratch capture files `specs/015-pyo3-upgrade/baseline-audit.txt` and `post-audit.txt` if the owner prefers the PR description to carry the before/after instead (owner's call at review)
- [ ] T018 Mark completed tasks `[X]` in `specs/015-pyo3-upgrade/tasks.md` and prepare the PR (branch `015-pyo3-upgrade`, merge-commit convention, CI green before merge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none — start immediately
- **Foundational (Phase 2)**: needs T001 (tooling); T002/T003 baselines should exist before T004 changes anything
- **User Stories (Phases 3–5)**: all require Phase 2 complete; then mutually independent — any order, or in parallel
- **Polish (Phase 6)**: requires all three stories verified

### User Story Dependencies

- **US1 (P1)**: only Phase 2 — one command
- **US2 (P2)**: only Phase 2 — no dependency on US1
- **US3 (P3)**: only Phase 2 locally; SC-004's final confirmation lands with the PR's CI run

### Parallel Opportunities

- T002 ∥ T003 (different tools, read-only)
- After Phase 2: T009 ∥ T011 ∥ T014 (audit, pytest, confinement checks touch disjoint surfaces)
- Within stories: T010, T012, T013 marked [P]

Realistically this is a one-sitting, one-person feature — the parallelism above mostly means "order doesn't matter after Phase 2."

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3**: baseline, upgrade, clean audit. That alone satisfies the feature's reason for existing (US1) — but do **not** ship without Phase 4: FR-003/FR-004 are requirements, not polish, and US2's suite run is minutes of work. Incremental checkpoints exist mainly as diagnosis boundaries: if T011 fails, the defect is in Phase 2's edits, not in the gates.

## Notes

- No new test files, no test edits — the suite's *unmodified* status is itself part of the acceptance criteria (SC-002).
- Commit after Phase 2 (the change), after each story's checkpoint (the evidence), and at close-out.
- Constitution: no simulation crate is touched at any task; Article V is actively verified by T011.
