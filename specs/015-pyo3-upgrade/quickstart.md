# Quickstart: Validating the pyo3 Upgrade (015)

The runbook proving the upgrade meets its gates. Every command exists today and
runs unchanged — that's the point (FR-003/FR-008): only the *results* move
(the audit goes clean).

## Prerequisites

- Rust stable ≥ 1.83 (`rustup default stable` — CI floats; local 1.97.1 verified fine)
- Python ≥ 3.9 with a virtualenv
- `pip install maturin pytest numpy` (floating versions, as CI does)
- `cargo install cargo-audit` (if not present)

## 1. Workspace still compiles and passes Rust tests

```sh
cargo test
```

**Expected**: all workspace tests pass, including `cloudkitty-py`'s Rust-side tests
(links a normal libpython; the `extension-module` feature stays off outside maturin).

## 2. The extension builds and the unmodified Python suite passes (SC-002, FR-003)

```sh
cd crates/cloudkitty-py
maturin develop --release
pytest tests -v
```

**Expected**: 100% pass with **zero modifications to any file under `tests/`**.
`test_parallel_env.py` includes the two-process reproducibility test — its pass is
the bit-identical-rollouts gate (SC-003/FR-004). Deprecation *warnings* are
tolerated; failures are not.

## 3. Optional: PettingZoo conformance (spec US2 scenario 3)

```sh
pip install pettingzoo
pytest tests/test_pettingzoo_conformance.py -v
```

**Expected**: result no worse than pre-upgrade (this suite is `continue-on-error`
in CI; it must not regress from its pre-upgrade status).

## 4. The audit goes clean (SC-001, FR-005)

```sh
cargo audit
```

**Expected**: **0 advisories** (pre-upgrade baseline: 2 — RUSTSEC-2025-0020,
RUSTSEC-2026-0177, both against pyo3 0.21.2).

## 5. Surface confinement spot-checks (FR-006, FR-007)

```sh
# The server binary must not link pyo3:
cargo tree -p cloudkitty-server | grep -c pyo3   # expected: 0 (grep exits nonzero)

# The wheel keeps its abi3-py39 floor:
grep 'abi3-py39' crates/cloudkitty-py/Cargo.toml  # expected: present, unchanged
```

## 6. Contract review (FR-003, human check)

Diff the built module against [contracts/python-surface.md](contracts/python-surface.md):

```sh
python -c "import cloudkitty; print(sorted(n for n in dir(cloudkitty) if not n.startswith('_')))"
python -c "import cloudkitty, inspect; e = cloudkitty.ParallelEnv; print([m for m in dir(e) if not m.startswith('_')])"
```

**Expected**: exactly the names the contract lists — nothing added, renamed, or gone.

## 7. Close-out (SC-004, SC-005)

- CI passes on the PR with **zero CI configuration changes** (SC-004).
- The PR removes the BACKLOG P1 pyo3 entry (SC-005) — the RL-work gate retires with it.
