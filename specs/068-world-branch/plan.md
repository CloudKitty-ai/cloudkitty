# Implementation Plan: World Branch API (Snapshot, Restore and a One-Tick Proposal Override from Python)

**Branch**: `product/068-world-branch` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/068-world-branch/spec.md`
(owner kickoff "One spec" 2026-11-05; clarifications ruled the same day).

## Summary

Give the Python binding a branch primitive: `snapshot()` → opaque bytes
carrying the whole episode state (world with RNG, the already-dealt next
seeds, episode position, truncation, reward baselines, current seed) and
its identity (engine commit, config digest, control map); `restore(bytes)`
replacing the state wholesale and returning what `reset` returns;
`fork()` as sugar. Beside it, `override(kitty, action=None,
message=None)`: a one-tick proposal substitution for an engine-decided
seat, each half independently, ruled on by the engine's law at the apply
slot and marked with a new, half-naming provenance that a per-seat
`tick_records()` reader exposes for every roster kitty. A world that never
calls any of these is byte-identical to today. Technical approach: JSON of
a new `EpisodeSnapshot` struct in the rl crate (research R1–R4), decoded
overrides stored on the `Episode` and applied in `step_inner` where
scripted marks are already restored (R5–R6), wrapper-side report retention
for the reader (R7), per-index worker commands for `VectorEnv` (R8).

## Technical Context

**Language/Version**: Rust (workspace toolchain per `rust-toolchain.toml`),
pyo3 0.29 (`abi3-py39`), Python 3.11/3.12 in CI.

**Primary Dependencies**: `serde`/`serde_json` (already in core and rl),
`sha2` 0.10 (already in rl), pyo3 + numpy (py crate). No new crates.

**Storage**: none. The snapshot is an in-process byte string (FR-016);
nothing is written to disk by the engine.

**Testing**: `cargo test -p cloudkitty-rl` (new `tests/branch.rs`),
`pytest crates/cloudkitty-py/tests` after `maturin develop` (new
`test_branch.py`), the existing byte-identity/golden/pin suites unchanged
(SC-007), `scripts/mutate.sh --expect` for every new guard's red.

**Target Platform**: the lab's macOS binding and the ubuntu CI runners;
no server change (Article V; the server crate is untouched).

**Project Type**: library (Rust crates + Python extension module).

**Performance Goals**: SC-006 — restore + one step from a snapshot at
tick 10,000 of the served-size world under 1/100 of replaying 10,000
ticks (≈ under 5 ms at the lab's 20,000 ticks/s); CI asserts a loose
1/10, the quickstart records the measured ratio.

**Constraints**: FR-015 byte-identity without the API (no schema bump,
no fingerprint or defaults-stamp move, no draw-order change, zero golden
re-cuts); spec 067 D16 (a needy seat's control never changes); the
override reaches no verdict (FR-010); the free register is never scripted
by default (FR-014).

**Scale/Scope**: three crates touched (core: two derive lines + three
enum variants; rl: episode snapshot/restore/override + vector commands;
py: six methods, error mapping, docstrings); two new test files; docs
(`docs/howto-rl.md`), CHANGELOG Unreleased entry.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I–III (no suffering, no death, never alone)**: untouched. A
  restored world is a serialized lawful world; no code path removes a
  kitty; the override proposes acts the engine validates. PASS.
- **Article IV (the engine is the law; behaviours are untrusted
  advisors)**: the override is a proposal and nothing more — validation,
  consent, needy and duration enforcement rule at the apply slot exactly
  as for any proposal (FR-010, SC-005); refusals resolve to idle and are
  stamped as refusals today. PASS.
- **Article V (server-authoritative, deterministic)**: the server crate is
  not touched; determinism is strengthened — the restored episode
  continues byte-identically because the snapshot carries the RNG and the
  already-dealt seeds (R2), and a world without branch calls draws in the
  same order (FR-015). Snapshot/restore sit between ticks; the tick stays
  atomic. PASS.
- **Article VI (spec-first, test-guarded)**: spec written, clarified and
  doctrine-checked before this plan; every requirement has a guard in
  tasks.md with a rule-5 red prediction; constants (none new) stay in
  config. PASS.

Post-design re-check (after Phase 1): unchanged — the data model adds no
world mechanic, the contracts expose readers and a proposal path only.
PASS. No Complexity Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/068-world-branch/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R12
├── data-model.md        # EpisodeSnapshot, Identity, PendingOverride, Provenance, tick record
├── quickstart.md        # validation scenarios + the SC-006 measurement
├── contracts/
│   └── python-api.md    # ParallelEnv / VectorEnv surface, errors, docstring text
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks output
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/seam.rs            # DealtSeeds: derive Serialize/Deserialize; Provenance: 3 variants
crates/cloudkitty-rl/src/episode.rs           # EpisodeSnapshot, Identity, PendingOverride, snapshot/restore/override_next/control, EpisodeError variants, step_inner hook
crates/cloudkitty-rl/src/vector.rs            # Command::{Snapshot,Restore,Override}, Reply enum, per-index send
crates/cloudkitty-rl/tests/branch.rs          # NEW: Rust guards (US1, US2, US5; US4 via VectorizedEnvironment)
crates/cloudkitty-py/src/lib.rs               # ParallelEnv.{snapshot,restore,fork,override,tick_records}; VectorEnv.{snapshot,restore,override,tick_records}(i); provenance_str; episode_err; docstrings
crates/cloudkitty-py/tests/test_branch.py     # NEW: Python guards (surfaces, fork, reader, docstring line, loose SC-006)
docs/howto-rl.md                              # a "Branching a world" section (shared doc)
CHANGELOG.md                                  # Unreleased entry, public voice, no compatibility marker
```

**Structure Decision**: the existing three-crate layout; no new crate, no
new module. The snapshot and override live on `Episode` because that is
the one owner of every field they touch; the reader lives in the Python
wrappers because the report it reads is already returned to them (R7).

## Phase 0 → research.md

Done: R1 encoding, R2 contents, R3 identity, R4 restore return, R5
override mechanism, R6 provenance, R7 reader, R8 vector commands, R9
fork, R10 errors, R11 guards and reds, R12 docstrings. No open unknowns.

## Phase 1 → data-model.md, contracts/, quickstart.md

Done; see the files. The engine commit reaches the rl crate as a plain
`&str` argument from the py crate (which already has the build-time
value) — `Episode::snapshot(engine_commit: &str)` /
`Episode::restore(engine_commit: &str, bytes: &[u8])` — so neither core
nor rl grows a build script, and the Rust tests pass a literal.

## Doctrine and welfare (carried from the spec)

Rules 2, 5, 6, 9, 10, 12 moved choices (spec §Design-doctrine check);
this plan adds no new behaviour, price, observation or gate. The k > 1
marker-review line is carried in the four docstrings (R12, FR-017).
