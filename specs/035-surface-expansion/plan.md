# Implementation Plan: Surface-Expansion Export

**Branch**: `035-surface-expansion` | **Date**: 2026-08-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/035-surface-expansion/spec.md`

## Summary

A deterministic Rust tool, `ckpolicy-expand`, that carries a certified
pre-wall artifact onto the current (schema-4) surface: read the old bytes
through a tooling-only loader entry, permute/extend the weight geometry per
the documented layout maps, pin the deaf-and-mute invariants (new inputs
exactly zero; new head outputs the constant −1.0e4), attest placement
structurally, and write a first-class current-generation artifact through
the crate's own writers. No forward pass in the tool — semantics belong to
Experiments' certification parity leg by the settled Q2 division. Decisions
D1–D8 in [research.md](research.md).

## Technical Context

**Language/Version**: Rust (workspace toolchain) — one new bin +
library module in `cloudkitty-rl`; no other crate moves

**Primary Dependencies**: none new — the crate already owns both artifact
formats, their writers, and `sha2`; args hand-parsed in house style

**Storage**: reads committed `policies/*.ckpolicy`; writes artifacts to a
caller-named output path; nothing committed in this arc beyond fixtures
(D7 — real expanded artifacts land at the seating PR)

**Testing**: `cargo test` — library unit tests (maps, invariants,
determinism, refusals), one engine-level integration test for the
deaf/mute property (SC-003), fixture round-trips

**Target Platform**: developer machines + CI; byte-identical output across
both (no RNG, no floats computed — only moved, zeroed, or set to the
constant floor)

**Project Type**: existing multi-crate workspace; changes confined to
`crates/cloudkitty-rl` plus `policies/README.md` (naming convention) and
docs/CHANGELOG

**Performance Goals**: none material — three artifacts of a few MB,
expanded in milliseconds; determinism matters, speed does not

**Constraints**: serving loader byte-untouched (FR-002); no schema-pin,
config, fingerprint, or stamp movement (FR-012); full pre-existing suite
unmodified (SC-005)

**Scale/Scope**: two mapping implementations (v2 MLP, v3
entity-attention), one attestation, one bin; ~3 source files + tests

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-evaluated post-design — **PASS** both.*

- **Articles I–III** (no suffering / no death / never alone): PASS — no
  engine or world code is touched.
- **Article IV** (engine is the law): PASS — expanded artifacts are
  ordinary untrusted advisors; their proposals face the same validation as
  any policy. The mute invariant is initialization, not a new enforcement
  path.
- **Article V** (server-authoritative, deterministic): PASS — the tool is
  offline tooling; the simulation is untouched. The tool itself is
  deterministic by construction (no RNG — values are moved, zeroed, or set
  to a constant).
- **Article VI** (spec-first, test-guarded): PASS — this spec precedes the
  tool; the floor and the zero rule are named constants with documented
  rationale, guarded by the attestation and the SC-003 engine test in CI.

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/035-surface-expansion/
├── spec.md
├── plan.md              # this file
├── research.md          # D1–D8
├── data-model.md
├── quickstart.md
├── contracts/
│   └── expansion-tool.md
└── checklists/requirements.md   # 16/16
```

### Source Code (repository root)

```text
crates/cloudkitty-rl/src/
├── expand.rs                          # NEW — maps (D3), invariants (D4/D5),
│                                      #   attestation (D6), EXPANSION_TOOL_VERSION
├── bin/ckpolicy-expand.rs             # NEW — arg parsing, report printing (D6)
├── policy.rs                          # + tooling-only raw-read entry (D2)
├── attn.rs                            # + tooling-only raw-read entry (D2)
└── lib.rs                             # `pub mod expand`

crates/cloudkitty-rl/tests/
└── expansion.rs                       # NEW — determinism, bijection, refusals,
                                       #   fixture round-trip through the SERVING loader

crates/cloudkitty-server/tests/
└── server_integration.rs              # + SC-003: expanded fixture mind seated,
                                       #   full vocabulary, speaking neighbor —
                                       #   mute + deaf A/B assertions

policies/README.md                     # Naming section: the `-o4` convention (FR-008)
CHANGELOG.md                           # one-liner, ## Unreleased, no markers
```

**Structure Decision**: mapping logic lives in the library (testable
directly), the bin stays thin. The v3 deafness parameter set is verified
against `experiments/attn-oracle-2026-08-15/model_v4.py` during
implementation (D3 verification duty); the SC-003 engine test binds the
behavior regardless.

## Phase 0 — research.md

Complete: [research.md](research.md), D1–D8. No NEEDS CLARIFICATION
remained (pre-settled; see spec Clarifications).

## Phase 1 — Design & Contracts

- [data-model.md](data-model.md) — the map entities, invariants, and
  attestation fields.
- [contracts/expansion-tool.md](contracts/expansion-tool.md) — CLI
  contract, attestation report, floor constant, naming + provenance
  strings.
- [quickstart.md](quickstart.md) — end-to-end validation runs.

Post-design constitution re-check: PASS (unchanged — see gate above).
