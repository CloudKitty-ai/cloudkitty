# Research: pyo3 Upgrade (015)

Phase 0 output. All Technical Context unknowns resolved; no NEEDS CLARIFICATION remain.

## 1. Version targets (verified live against crates.io, 2026-07-23)

**Decision**: pyo3 **0.29.0** + numpy (rust-numpy) **0.29.0**.

**Rationale**:
- pyo3 0.29.0 (released 2026-06-11) is the current max stable and the exact version RUSTSEC-2026-0177 names as fixed; RUSTSEC-2025-0020 was fixed earlier (0.24.1), so one target clears both.
- numpy 0.29.0 (released 2026-06-13, two days after pyo3) exists — **the lockstep companion is available**, so the spec's wait-don't-partial edge case does not trigger and the work can proceed immediately.
- MSRV check: both crates declare `rust_version = 1.83`; local toolchain is 1.97.1 and CI floats stable — no toolchain work needed.
- Recent history note: pyo3 0.28.0/0.28.1 were yanked (0.28.2/0.28.3 stand) — mild evidence that jumping straight to the current stable (0.29.0, unyanked for six weeks) is the safer landing spot than an intermediate hop.

**Alternatives considered**:
- **0.24.1** (minimum for the older advisory only): rejected — leaves RUSTSEC-2026-0177 open, fails SC-001, and guarantees a second migration soon.
- **Stepping through versions** (0.22 → 0.23 → … → 0.29): rejected — the gates judge the result, not the path (spec assumption); the binding file is small enough that compiler-driven single-jump is cheaper than seven intermediate compile-fix cycles.
- **Waiting for pyo3 1.0**: rejected — no released 1.0 exists to target; the advisories are open now and the gate blocks RL work.

## 2. Migration surface survey (verified against `lib.rs`, 2026-07-23)

**Decision**: treat as compiler-driven mechanical migration; no redesign of the binding layer.

**Rationale** (what's already true of the code):
- The file is already on the **Bound API** (`Bound<'py, T>` throughout, `#[pyo3(signature = ...)]` attributes) — the hard half of post-0.21 migrations is done. No GIL-refs, no deprecated `to_object`/`into_py` conversion calls anywhere.
- Known-required renames (deprecated in 0.23, removed later): `into_pyarray_bound` → `into_pyarray` (9 call sites), `PyArray1::from_vec_bound` → `from_vec` (1 site).
- Probable touch points: the 4 helpers returning `PyResult<PyObject>` (`box_space`, `discrete_space`, `observation_space`, `action_space`) under the 0.23 `IntoPyObject` conversion-trait rework; `PyObject` → `Py<PyAny>` respelling if the alias is deprecated by 0.29.
- **Unverified territory**: 0.26–0.29 changelogs were not reviewed in detail; consult the official migration guides when compile errors surface. Expected impact for Bound-API code: small.
- Neither advisory's vulnerable API is called (`PyString::from_object`, `PyCFunction::new_closure` absent from the workspace) — confirms hygiene posture, informs no code change.

**Alternatives considered**: pinning `gil-refs`-era compatibility features — not applicable (feature removed upstream in 0.23; code never used it).

## 3. Build & CI tooling

**Decision**: no CI or build-tooling changes (FR-008 as a plan fact, not just a requirement).

**Rationale**: CI installs `maturin pytest numpy` unpinned on Python 3.11 and builds with `maturin develop --release`; current maturin supports pyo3 0.29 (contemporary releases). The `extension-module` feature indirection in `Cargo.toml` (maturin enables it; plain `cargo test` links libpython) is version-agnostic and carries over. `abi3-py39` remains supported and keeps the CPython ≥ 3.9 wheel floor (FR-006).

**Alternatives considered**: pinning maturin for reproducibility — rejected; would *add* a pin the spec forbids introducing, and floating has been stable in CI.

## 4. Acceptance instrumentation

**Decision**: reuse the existing gates unchanged; add nothing.

**Rationale**: the pytest suite (unmodified) is the FR-003 contract check in executable form; `test_parallel_env.py`'s two-process reproducibility test is precisely FR-004/SC-003; `cargo audit` is SC-001's instrument; the unchanged CI job is SC-004's. A new test would either duplicate an existing gate or test the dependency rather than our surface.

**Alternatives considered**: adding an API-snapshot test (introspecting the module and asserting names/signatures) — deferred; `contracts/python-surface.md` records the frozen surface for human verification this round, and an executable snapshot can join a future maintenance pass if surface drift ever actually bites.
