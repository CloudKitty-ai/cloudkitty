# Implementation Plan: Kitty-Eval Dedup — Single-Source the Certification CLI

**Branch**: `018-kitty-eval-dedup` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/018-kitty-eval-dedup/spec.md`

## Summary

Four concerns exist twice between `kitty-eval` (the certification binary)
and the `cloudkitty-rl` library: subject resolution (duplicated *within*
the binary), per-run human rendering, the first-seed determinism
self-check, and the baseline+roster-mode scoring orchestration (each
duplicated *against* `suite.rs`). The plan single-sources all four with
zero observable change: a new documented `cli_support` module in the
library gathers everything promoted for the binary's benefit (per the
2026-07-26 clarification), subject resolution collapses to one private
function inside the binary, and renderers gain an internal writer
parameter so the new share-guard test (FR-009) can capture output
in-process. Verification is the spec's bar: byte-identical human and JSON
output against pre-refactor builds (baseline: tag `v2.3`) in both modes,
full test suite green with zero assertion changes.

## Technical Context

**Language/Version**: Rust (workspace toolchain, edition 2021)

**Primary Dependencies**: `cloudkitty-rl` (suite, harness), `cloudkitty-core` (registry, config) — no new dependencies

**Storage**: N/A (JSON report files written by the CLI, shapes frozen)

**Testing**: `cargo test --workspace` (unit + integration incl. `tests/eval_suite.rs`); new share-guard test; byte-diff procedure per quickstart

**Target Platform**: developer machines + CI (same as today)

**Project Type**: CLI binary + library refactor, single workspace

**Performance Goals**: unchanged — no measurable runtime difference expected or required

**Constraints**: byte-identical human report, byte-identical JSON, identical exit codes 0–4 (occurrence-based precedence), identical error messages; library public surface grows only by the `cli_support` module

**Scale/Scope**: `bin/kitty-eval.rs` (~465 lines) and the render/score sections of `suite.rs` (~1,444 lines); net deletion expected in the binary

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I–III (welfare, immortality, companionship)**: PASS — no engine
  code is touched; the refactor is confined to the RL crate's CLI and
  library plumbing.
- **Article IV (engine is the law)**: PASS — no behavior/proposal surface
  involved.
- **Article V (deterministic simulation)**: PASS — determinism is not
  merely preserved but load-bearing: the byte-identical verification bar
  (FR-008) depends on it and re-verifies it.
- **Article VI (spec-first, test-guarded)**: PASS — spec 018 ratified and
  clarified before this plan; FR-007 forbids weakening tests; FR-009 adds
  a guard for the new invariant; no simulation constants involved.

**Post-Phase-1 re-check**: PASS — the design adds one library module and
three binary-local helpers; no article is implicated by any artifact.

## Project Structure

### Documentation (this feature)

```text
specs/018-kitty-eval-dedup/
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D6
├── data-model.md        # Phase 1: promoted surface + helper shapes
├── quickstart.md        # Phase 1: byte-diff procedure, share-guard, walkthroughs
├── contracts/
│   └── cli-support.md   # Phase 1: the one new module's contract
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-rl/
├── src/
│   ├── lib.rs           # + `pub mod cli_support;`
│   ├── cli_support.rs   # NEW — the gathered CLI-support surface:
│   │                    #   run panel + paired renderers (moved from suite.rs),
│   │                    #   mode-sweep orchestration (extracted from suite.rs)
│   ├── suite.rs         # renderers/orchestration core removed → calls cli_support;
│   │                    #   self_check stays private here (no longer needed by the binary)
│   ├── harness.rs       # untouched (RosterMode fold explicitly out of scope)
│   └── bin/kitty-eval.rs  # −~150 lines: one resolve_subject, one write_json,
│                          #   one fallback-gate printer; consumes cli_support
└── tests/
    └── eval_suite.rs    # + share-guard test (FR-009)
```

**Structure Decision**: single new library module (`cli_support`) as the
documented home for every promoted item, per the clarification ruling;
binary-local duplication collapses into private functions inside
`kitty-eval.rs`; `suite.rs` shrinks and consumes the moved pieces. No
other crate, no engine code, no config, no client files.

## Complexity Tracking

No constitution violations; table intentionally empty.
