# Implementation Plan: Python Training Surface — Dependency Advisory Clearance (pyo3 Upgrade)

**Branch**: `015-pyo3-upgrade` | **Date**: 2026-07-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/015-pyo3-upgrade/spec.md`

## Summary

Raise the Python binding stack from pyo3 0.21.2 / numpy 0.21 to **pyo3 0.29.0 / numpy 0.29.0** (both verified available on crates.io, released 2026-06-11/13 in lockstep), clearing RUSTSEC-2025-0020 and RUSTSEC-2026-0177 so `cargo audit` runs clean and the BACKLOG P1 gate on further RL work retires. The entire migration surface is one logic-free file (`crates/cloudkitty-py/src/lib.rs`, 704 lines) already written against the Bound API; the observable Python surface is frozen by contract (`contracts/python-surface.md`) and guarded by the unmodified existing pytest suite, whose SC-002 two-process reproducibility test is the behavioral gate.

## Technical Context

**Language/Version**: Rust (stable, currently 1.97.1; target MSRV requirement 1.83 — comfortably met) + Python ≥ 3.9 (abi3 floor), CI on Python 3.11

**Primary Dependencies**: pyo3 0.21.2 → **0.29.0**, numpy (rust-numpy) 0.21 → **0.29.0**; both confined to `crates/cloudkitty-py`. Build: maturin (floating, unpinned in CI).

**Storage**: N/A

**Testing**: `cargo test` (workspace), `maturin develop --release` + `pytest crates/cloudkitty-py/tests` (smoke + SC-002 two-process reproducibility), optional PettingZoo conformance (continue-on-error), `cargo audit` as the acceptance instrument for SC-001.

**Target Platform**: Linux CI + macOS dev; wheel targets CPython ≥ 3.9 via `abi3-py39`.

**Project Type**: Dependency maintenance on a library binding crate (no new capability).

**Performance Goals**: None new — no measurable performance change expected or required; CI job stays within its existing runtime envelope.

**Constraints**: Zero observable Python API change (FR-003); bit-identical rollouts (FR-004); zero CI config changes (FR-008); server binary stays pyo3-free (FR-007).

**Scale/Scope**: One crate, one source file (~10–25 hand-edited lines expected: `_bound` renames + possible conversion-trait signature nudges), two manifest lines, `Cargo.lock` churn.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Status |
|---------|------|--------|
| I — Kitties Cannot Suffer | No simulation behavior may change | ✅ PASS — no simulation crate is touched (FR-007); bindings are logic-free |
| II — Kitties Cannot Die | No kitty-removal path may be introduced | ✅ PASS — same; no engine code changes |
| III — Kitties Cannot Be Alone | Roster invariants unchanged | ✅ PASS — same |
| IV — Engine Is the Law | Proposal validation unchanged | ✅ PASS — bindings pass proposals through unchanged; validation lives in the engine |
| V — Deterministic Simulation | Same seed + config → same world state | ✅ PASS, actively guarded — FR-004/SC-003 make the existing two-process bit-reproducibility test the acceptance gate; a dependency that perturbed rollouts would fail it |
| VI — Spec-First, Test-Guarded | Spec before implementation; constants in config | ✅ PASS — this spec/plan precede the change; no simulation constants involved; existing CI gates are the guard |

**Post-Phase-1 re-check**: design produced no new components, no new configuration, no simulation contact — all gates still pass.

## Project Structure

### Documentation (this feature)

```text
specs/015-pyo3-upgrade/
├── spec.md              # /speckit-specify output
├── plan.md              # This file
├── research.md          # Phase 0: version targets verified live, migration survey
├── quickstart.md        # Phase 1: validation runbook (build, test, audit)
├── contracts/
│   └── python-surface.md  # Phase 1: the frozen Python API surface (FR-003's contract)
└── checklists/
    └── requirements.md  # Spec quality checklist (16/16)
```

`data-model.md` is deliberately absent: the feature introduces no entities, state, or schema — the closest analogue is the *existing* Python API surface, which is frozen (not designed) in `contracts/python-surface.md`.

### Source Code (repository root)

```text
crates/cloudkitty-py/
├── Cargo.toml           # the two version bumps (pyo3, numpy)
├── src/
│   └── lib.rs           # the entire migration surface (704 lines, logic-free bindings)
└── tests/               # UNCHANGED — pytest suite is the acceptance gate
    ├── test_parallel_env.py
    └── test_pettingzoo_conformance.py

Cargo.lock               # regenerated (library churn, no hand edits)
```

Untouched by requirement: `crates/cloudkitty-core`, `crates/cloudkitty-rl`, `crates/cloudkitty-server`, `.github/workflows/` (FR-007, FR-008).

**Structure Decision**: existing single-workspace layout; no structural change of any kind. The upgrade is confined to `crates/cloudkitty-py/{Cargo.toml, src/lib.rs}` plus the regenerated lockfile.

## Implementation Approach

Single-jump upgrade (0.21 → 0.29 directly; the spec's gates judge the result, not the path), compiler-driven:

1. **Bump** `pyo3 = { version = "0.29", features = ["abi3-py39"] }` and `numpy = "0.29"` in `crates/cloudkitty-py/Cargo.toml`.
2. **Fix compile errors** in `lib.rs`, consulting the pyo3 0.22→0.29 migration guides as errors surface. Expected classes of change (research.md §2):
   - `_bound` constructor renames: `into_pyarray_bound` → `into_pyarray` (9 sites), `PyArray1::from_vec_bound` → `from_vec` (1 site).
   - Conversion-trait era (`IntoPyObject` replacing `IntoPy`/`ToPyObject`, pyo3 0.23): may touch the 4 helpers returning `PyResult<PyObject>`; `PyObject` may need spelling as `Py<PyAny>` if the alias is deprecated by 0.29.
   - Anything else the 0.26–0.29 guides reveal (unverified territory; expected small for Bound-API code).
3. **Deprecation policy** (spec edge case): warnings must not fail anything; fix mechanically where trivial, otherwise note for the next maintenance pass.
4. **Validate** per `quickstart.md`: workspace `cargo test` → `maturin develop --release` + unmodified pytest (incl. SC-002 reproducibility) → optional PettingZoo run → `cargo audit` clean → contract check against `contracts/python-surface.md`.
5. **Close out**: remove the BACKLOG P1 entry (SC-005) in the same PR.

## Complexity Tracking

No constitution violations; table not needed.
