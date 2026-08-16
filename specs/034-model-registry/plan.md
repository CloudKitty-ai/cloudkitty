# Implementation Plan: Model Registry & Served Behavior Descriptions

**Branch**: `034-model-registry` | **Date**: 2026-08-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/034-model-registry/spec.md`

## Summary

Replace the meaningless raw model id on kitty cards with a served,
human-readable behavior description ("Transformer · BC+PPO", "Scripted"),
backed by a sha256-keyed TOML registry living beside the artifacts in
`policies/`. The server resolves each seated artifact's sha against the
registry at startup — refusing to boot on a missing row (owner ruling) — and
stamps the display line onto each kitty as a new optional serde field, which
every existing serving surface (REST + WS) then carries for free. A repo test
makes the registry impossible to silently skip. Full decisions in
[research.md](research.md) (D1–D8).

## Technical Context

**Language/Version**: Rust (workspace toolchain, edition 2021) — server +
core crates only; no Python/client code in scope

**Primary Dependencies**: `toml` (already a workspace dep — registry
parsing), `serde` (field on `Kitty`), `sha2` (already used by
`PolicyArtifact::load`; the repo test reuses it)

**Storage**: one new committed file `policies/registry.toml`; no database, no
new persistence (snapshots carry the field incidentally; resume re-stamps it)

**Testing**: `cargo test` — unit tests beside the registry loader, server
integration tests for serving + refusal, one repo-integrity test (FR-008)

**Target Platform**: the existing server binary (macOS dev, Linux box);
deploys with the phase-1 rollout — the frozen box is untouched until then

**Project Type**: existing multi-crate workspace; changes confined to
`cloudkitty-core` (one field), `cloudkitty-server` (registry load + stamp +
refusal), `policies/` (registry + README), docs/CHANGELOG

**Performance Goals**: registry resolution once per distinct artifact at
startup; zero per-tick cost; serving overhead one short optional string per
kitty (SC-004)

**Constraints**: no schema pin moves, no `Config` change, no
`Config::fingerprint` movement, no `--fresh` required (FR-011, verified —
research D7); `behavior` string and every existing served field byte-stable
(FR-009, SC-003)

**Scale/Scope**: 3 registry rows at ship; 5 kitties served; ~6 files touched
plus tests

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-evaluated post-design — **PASS** both.*

- **Article I (no suffering)**: PASS — no needs, thresholds, or welfare
  mechanics touched.
- **Article II (no death)**: PASS — no kitty lifecycle code touched.
- **Article III (never alone)**: PASS — roster untouched.
- **Article IV (engine is the law)**: PASS — no proposal, validation, or
  fallback path changes. The refusal (FR-007) is *startup* config validation,
  the same class as unknown-behavior-name errors, not a runtime behavior
  outcome.
- **Article V (server-authoritative, deterministic)**: PASS — the client
  remains a pure view reading one more served string. The field is stamped
  before tick 0, constant for the run, and never read by simulation code:
  same seed + config + tick count still yields the same world state.
  Serialization of the field is deterministic (fixed per-run value).
- **Article VI (spec-first, test-guarded)**: PASS — this spec precedes code;
  the display strings live in the registry file (data, not magic numbers in
  code); the one in-code constant ("Scripted") is a specced contract value
  (FR-005), asserted by integration test. FR-008's repo test is the CI guard.

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/034-model-registry/
├── spec.md
├── plan.md              # this file
├── research.md          # D1–D8
├── data-model.md
├── quickstart.md
├── contracts/
│   └── registry-and-serving.md
└── checklists/requirements.md   # 16/16
```

### Source Code (repository root)

```text
policies/
├── registry.toml                      # NEW — 3 rows (D1)
└── README.md                          # amended: same-PR rule, naming pointer (D8)

crates/cloudkitty-core/src/
└── kitty.rs                           # + behavior_description: Option<String> (D3)

crates/cloudkitty-server/src/
├── lib.rs                             # register_policy_behaviors: registry load,
│                                      #   refusal, name→display map (D4); stamp fn
├── main.rs                            # stamp call after world generate/restore
└── persist.rs                         # re-stamp beside the behavior re-stamp (D3)

crates/cloudkitty-server/tests/
├── registry_integrity.rs              # NEW — FR-008 repo test (D5)
└── server_integration.rs              # serving assertions: Scripted default,
                                       #   display line, absent-for-plugin, refusal

CHANGELOG.md                           # one-liner, ## Unreleased, no markers (D7)
```

**Structure Decision**: no new crates, no new modules beyond one test file —
the feature threads through the exact seams that already exist for artifact
validation (registration) and behavior authority on resume (re-stamp loop).

## Phase 0 — research.md

Complete: [research.md](research.md). No NEEDS CLARIFICATION remained (the
spec's single owner question was resolved pre-plan: FR-007 refuse).

## Phase 1 — Design & Contracts

- [data-model.md](data-model.md) — registry row, resolution map, the Kitty
  field and its lifecycle.
- [contracts/registry-and-serving.md](contracts/registry-and-serving.md) —
  normative registry file shape, served-field contract, refusal contract,
  initial rows.
- [quickstart.md](quickstart.md) — end-to-end validation scenarios.

Post-design constitution re-check: PASS (unchanged — see gate above).
