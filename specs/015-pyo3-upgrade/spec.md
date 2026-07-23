# Feature Specification: Python Training Surface — Dependency Advisory Clearance (pyo3 Upgrade)

**Feature Branch**: `015-pyo3-upgrade`

**Created**: 2026-07-23

**Status**: Draft

**Input**: User description: "pyo3 upgrade"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Clean Security Audit (Priority: P1)

As the project owner, I run the workspace's dependency security audit and it reports zero known advisories, so that future reinforcement-learning work (crepuscular rewards and beyond) starts from a clean foundation instead of accumulating known-vulnerable dependencies — and so the standing gate "do this before any more RL work" (BACKLOG P1) is satisfied and retired.

**Why this priority**: This is the entire reason the work exists. Two published advisories (RUSTSEC-2025-0020, RUSTSEC-2026-0177) are pinned to the Python binding dependency at its current version. Neither vulnerable code path is invoked by this project today — the upgrade is hygiene, not an active hole — but the audit noise masks any *future* real finding, and the owner has gated all further RL work behind clearing it.

**Independent Test**: Run the dependency security audit against the workspace lockfile; it completes with zero advisories reported.

**Acceptance Scenarios**:

1. **Given** the upgraded workspace, **When** the dependency security audit runs, **Then** it reports no known advisories for any workspace member.
2. **Given** the upgraded workspace, **When** the advisory database gains a new entry for the *old* dependency versions, **Then** the audit remains clean, because the workspace no longer depends on those versions.

---

### User Story 2 - Training Scripts Don't Notice (Priority: P2)

As a user of the Python training surface, my existing scripts, tests, and tooling — environment construction, reset/step loops, observation and reward structures, the multi-world batch runner — behave exactly as before the upgrade, with no edits required on my side.

**Why this priority**: The binding layer's contract is the product; the upgrade is an internal spring-cleaning. Any observable behavior change (a renamed method, a reshaped return value, a drifted rollout) would turn a maintenance chore into a breaking change and violate the trust that the 014 surface's determinism guarantees established.

**Independent Test**: Run the existing Python test suite, entirely unmodified, against the upgraded build; every test passes. The two-process reproducibility test (014 SC-002's guard) is the sharpest instrument: identical seeds in separate processes must still yield bit-identical rollouts.

**Acceptance Scenarios**:

1. **Given** the upgraded binding, **When** the existing Python test suite runs without any modification to test files, **Then** all tests pass.
2. **Given** two separate processes constructing the environment with identical seeds and configuration, **When** each runs the same rollout on the upgraded binding, **Then** the resulting trajectories are bit-identical (unchanged from the pre-upgrade guarantee).
3. **Given** the optional ecosystem-conformance suite (PettingZoo) is installed, **When** it runs against the upgraded binding, **Then** its result is no worse than before the upgrade.

---

### User Story 3 - The Build Path Keeps Working Everywhere (Priority: P3)

As a developer (or CI), I build and install the Python extension exactly as before — same commands, same Python version floor, same wheel compatibility — on an upgraded dependency stack.

**Why this priority**: Valuable but low-risk: the build tooling floats to current versions already, and the compatibility floor is a declared property that simply must not regress silently.

**Independent Test**: The existing CI job (build the extension, run the test suite) passes with **zero changes to CI configuration**; the built wheel still targets the declared minimum Python version.

**Acceptance Scenarios**:

1. **Given** the upgraded manifests, **When** CI runs its unchanged Python-surface job, **Then** the extension builds and the suite passes.
2. **Given** the built artifact, **When** its compatibility metadata is inspected, **Then** the minimum supported Python version is unchanged (3.9 floor).

---

### Edge Cases

- **The lockstep companion isn't ready**: the numeric-array binding crate releases in lockstep with the main binding dependency and historically lags it. If no companion release supports the advisory-clearing target version at implementation time, the upgrade **waits** — a partial or mismatched upgrade (clearing one advisory but not the other, or pinning incompatible pairs) is out of scope. Waiting is acceptable because neither vulnerable code path is invoked today (verified 2026-07-23).
- **Deprecation warnings, not errors**: the target version may deprecate APIs the binding still uses without breaking them. Warnings must not fail the build or the suite; eliminating them is in scope only where the fix is mechanical, and any that remain are noted for the next maintenance pass.
- **A newer target appears mid-work**: if a version newer than the minimum advisory-clearing release is current at implementation time, prefer it — the requirement is a floor, not a pin.
- **Local environments older than CI**: developers with stale build tooling may fail to build the upgraded extension; the error must be resolvable by updating floating tools (no new pinned tool requirements introduced).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Python binding dependency MUST be upgraded to a version that resolves both RUSTSEC-2025-0020 (fixed in 0.24.1) and RUSTSEC-2026-0177 (fixed in 0.29.0) — i.e., at least 0.29.0 — preferring the latest stable release available at implementation time.
- **FR-002**: The numeric-array binding crate MUST be upgraded to the release matching the chosen binding-dependency version (the two release in lockstep). If no matching release exists at implementation time, the upgrade MUST wait for one rather than ship a mismatched pair or a partial (single-advisory) upgrade.
- **FR-003**: The Python-facing API surface — module name, classes, constructors, method names and signatures, returned structures and their shapes — MUST be observably unchanged: the existing Python test suite passes with zero modifications to test files.
- **FR-004**: The determinism guarantee of the training surface (014: identical seeds and configuration yield bit-identical rollouts across separate processes) MUST hold after the upgrade.
- **FR-005**: The workspace dependency security audit MUST report zero known advisories after the upgrade.
- **FR-006**: The built extension's Python compatibility floor (CPython 3.9, via the stable-ABI declaration) MUST be preserved.
- **FR-007**: The upgrade MUST remain confined to the Python binding crate and its manifests: the server binary MUST remain free of any Python binding dependency, and no simulation crate (core, RL) may change behavior.
- **FR-008**: CI configuration MUST NOT require changes for the upgraded build to pass (build tooling already floats; no new pins may be introduced).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The dependency security audit reports **0 advisories** for the workspace (down from 2).
- **SC-002**: The existing Python test suite passes **100%** with **0 modified test files**.
- **SC-003**: Two independent processes given identical seeds and configuration produce **bit-identical** rollouts, matching the pre-upgrade guarantee exactly.
- **SC-004**: The CI Python-surface job passes with **0 lines of CI configuration changed**.
- **SC-005**: The BACKLOG P1 gate ("upgrade before any more RL work") is closed: the entry is removed, unblocking the P4 crepuscular-rewards item and all future RL work.

## Assumptions

- The advisory-clearing target (≥ 0.29.0) exists and is stable — asserted by the advisory metadata itself (RUSTSEC-2026-0177 names 0.29.0 as fixed).
- The lockstep numeric-array crate's availability for the target version is **checked first at implementation time** and sets the schedule: available → proceed; not yet → wait (per the edge case above). This is acceptable because the audit findings are hygiene, not active exposure — verified 2026-07-23: neither vulnerable API (`PyString::from_object`, `PyCFunction::new_closure`) is called anywhere in the workspace.
- A single-jump upgrade (current → target, without stepping through intermediate versions) is acceptable; the gates (FR-003–FR-005) judge the result, not the path.
- The binding crate is the entire migration surface: one logic-free source file already written against the current-generation binding API, so expected code changes are mechanical renames plus possible conversion-trait signature adjustments (per the analysis recorded 2026-07-23). If implementation reveals a larger surface, that's new information for the plan, not a spec change.
- Constitution: Article VI (spec-first, test-guarded) is satisfied by this spec plus the pre-existing test gates; Articles I–V are unaffected because no simulation behavior changes (FR-007 makes this a requirement, not just an expectation).
- This is maintenance: no new user-facing capability is created, and the spec's "users" are the project owner and the training-surface consumers (today, the same person).
