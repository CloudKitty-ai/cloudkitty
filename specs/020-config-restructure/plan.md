# Implementation Plan: Config Restructure — Table-Driven Validation, Navigable Layout

**Branch**: `020-config-restructure` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/020-config-restructure/spec.md`

## Summary

The engine's configuration module (~1,800 lines) pays a seven-line toll
per bounded field, hides six sections' rules inside a validator named for
one, and interleaves two unrelated jobs. The plan: (1) split `config.rs`
into a `config/` directory module — types primary in `mod.rs`, the ~20
`default_*` functions in `defaults.rs`, all validators in `validate.rs` —
with the public path (`crate::config::*` and the root re-exports)
unchanged; (2) dissolve `validate_behavior` into six honestly-named
section validators called in the catch-all's first-occurrence order (the
amended FR-004's documented sequence); (3) collapse every mechanical
bound guard into the table-loop form the file already uses twice, one row
per field carrying its exact message bytes (the guards' rationale
parentheticals differ per field — rows carry full verbatim strings, the
loop owns only the if/return shape). Verified by the existing unit suite
unchanged plus an enumerated pre/post sweep of every rejection path:
byte-identical messages for all single-fault configurations, the
multi-fault tiebreak re-specified per the 2026-07-26 clarification.

## Technical Context

**Language/Version**: Rust (workspace toolchain, edition 2021)

**Primary Dependencies**: none new — `serde`/`toml` usage untouched (FR-005)

**Storage**: N/A — accepted TOML shapes, defaults on omitted fields, unknown-field handling all frozen

**Testing**: `cargo test --workspace` with zero assertion changes (FR-007); the FR-008 enumerated rejection-path sweep (throwaway harness, both builds, diffed)

**Target Platform**: unchanged

**Project Type**: single-module engine refactor (`cloudkitty-core::config`)

**Performance Goals**: unchanged — validation runs once at startup; table loops replace repeated if-blocks one-for-one

**Constraints**: byte-identical rejection messages per rejection path (single-fault absolute; multi-fault per the amended FR-004's documented section sequence); public surface unchanged (FR-006 — no consuming code touched); serde behavior untouched; no field/default/bound changes (FR-009)

**Scale/Scope**: `crates/cloudkitty-core/src/config.rs` (1,818 lines: production 1–1279, tests 1280+) → three files; ~46 `ConfigError::invalid` sites, ~13 mechanical guards to table rows; nothing outside the module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I–III**: PASS — validation *rules* are frozen (FR-004/FR-009);
  the Article III two-kitty rejection and every welfare-relevant bound
  keep their exact semantics and messages.
- **Article IV**: PASS — no behavior/proposal surface involved.
- **Article V**: PASS — validation is deterministic string-in/error-out;
  no RNG, no tick machinery touched.
- **Article VI**: PASS — spec-first flow complete (spec ratified,
  clarified twice — initial pass plus the 2026-07-26 FR-004 amendment
  the plan-phase code contact forced); tests guarded (FR-007); this
  feature *organizes* the config constants Article VI mandates, adding
  and removing none.

**Post-Phase-1 re-check**: PASS — the design is a file split plus
table-folding inside one module; no article implicated.

## Project Structure

### Documentation (this feature)

```text
specs/020-config-restructure/
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D5
├── data-model.md        # Phase 1: section map, table-row shape, call sequence
├── quickstart.md        # Phase 1: rejection-path sweep + walkthrough + records
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

No `contracts/` directory: the module's public API is explicitly
unchanged (FR-006), and the operator-facing contract — the rejection
messages — is verified byte-exactly by the quickstart's enumerated sweep
rather than restated in a document that could drift from it.

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config.rs            # DELETED (becomes the directory below)
└── config/
    ├── mod.rs           # the types (primary content), ConfigError,
    │                    #   serde attributes (`default = "defaults::…"`),
    │                    #   validate() calling section validators in the
    │                    #   documented sequence, the #[cfg(test)] module
    ├── defaults.rs      # the ~20 default_* functions, unchanged bodies
    └── validate.rs      # per-section validators + the table-row helpers;
                         #   validate_behavior dissolved into behavior,
                         #   purr, actions, viewer, events, persistence
```

**Structure Decision**: a directory module keeps every import path
(`crate::config::Config`, root re-exports) byte-compatible — no consumer
in engine, server, RL crate, or bindings changes (FR-006/SC-004). Serde
`#[serde(default = "…")]` attribute paths change only *inside* the module
(`"defaults::default_x"`), which is invisible to parsing behavior. The
tests module stays in `mod.rs` unmodified, satisfying FR-007's
zero-assertion-change bar structurally.

## Complexity Tracking

No constitution violations; table intentionally empty.
