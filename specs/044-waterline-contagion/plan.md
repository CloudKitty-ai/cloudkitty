# Implementation Plan: Waterline Contagion (price, not law)

**Branch**: `044-waterline-contagion` | **Date**: 2026-08-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/044-waterline-contagion/spec.md`

## Summary

A dry cat whose own activity pairs it with a partner standing in water
accrues the wet-fur bath charge, scaled by one new `[water]
contagion_factor` dial that is inert at 0.0 (byte-identical launch).
Approach: pre-collect wet/contagious id sets in `advance_needs` and add
a second, mutually-exclusive charge arm beside occupancy; widen
`validate_water`'s headroom budget to `max(1, factor)`; prove inertness
with the existing stamp guard + golden + determinism instruments and
armed behavior with one new integration test file.

## Technical Context

**Language/Version**: Rust (workspace pin via `rust-toolchain.toml`, merged #305)

**Primary Dependencies**: serde/toml (config surface); no new crates

**Storage**: TOML config only; no world-schema or persisted-state change

**Testing**: `cargo test --workspace` (737-test baseline); new integration file `tests/waterline_contagion.rs`; validator unit tests

**Target Platform**: engine crate `cloudkitty-core` (server + lab); RL crate untouched

**Project Type**: library/engine (Rust workspace)

**Performance Goals**: two `BTreeSet` collections per tick, only when armed; zero work at factor 0.0

**Constraints**: byte-identical at factor 0.0 (stamp + golden unmoved); no RNG; no legality/mask/refusal change; per-tick worst case unchanged at factor ≤ 1.0

**Scale/Scope**: ~4 files touched (`config/mod.rs`, `config/validate.rs`, `world.rs`, new test file) + CHANGELOG

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Article I (no suffering)**: contagion is need pressure only, gated at
  the same ceiling; the widened `validate_water` budget keeps the
  safeguard threshold unreachable by water alone — the guarantee is
  *strengthened* to cover the new charge (FR-009, SC-004). No new
  distress source: distress events remain signals, and the relief
  guarantee is untouched.
- **Article II (no death)**: untouched; no removal path added.
- **Article III (never alone)**: untouched; contagion prices scenes but
  never forbids them (FR-007 — no legality change).
- **Article IV (plugins)**: no proposal/validation surface change;
  scripted and learned deciders feel the same price through needs.
- **Article V (fairness/determinism)**: charge computed from pre-loop
  snapshots, so tick order cannot affect who pays; no RNG (FR-008);
  armed determinism pinned in-tree.
- **Article VI (tests in CI)**: every FR lands with a guard — see
  quickstart and D5/D6.

## Project Structure

### Documentation (this feature)

```text
specs/044-waterline-contagion/
├── plan.md              # This file
├── research.md          # D1–D7 decisions
├── data-model.md        # WaterConfig delta + derived sets + charge table
├── quickstart.md        # Validation runbook (SC-001..SC-006)
├── contracts/
│   └── config-surface.md
└── tasks.md             # /speckit-tasks output (not created by plan)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/
│   ├── mod.rs           # WaterConfig.contagion_factor (D1); stamp-guard test extension (D5)
│   └── validate.rs      # validate_water: bounds + widened budget (D4)
└── world.rs             # advance_needs: wet_ids/contagious pre-collection + else-if arm (D2, D3)

crates/cloudkitty-core/tests/
└── waterline_contagion.rs   # NEW — armed accrual/exemption/gate/nothing-cases/determinism (D6)

CHANGELOG.md             # one line under ## Unreleased
```

**Structure Decision**: single-crate change inside `cloudkitty-core`;
the RL crate is deliberately untouched (KITTY_SLOT float is wall-gated,
out of scope). Delivery follows the 043 shape: commit 1 = config
surface inert (D1 + D4 + stamp guard), commit 2 = charge path + armed
tests (D2 + D3 + D6).

## Phase 0: research.md

Complete — no NEEDS CLARIFICATION remained; seven decisions D1–D7
recorded with rationale and rejected alternatives.

## Phase 1: data-model.md, contracts/, quickstart.md

Complete — entity delta, derived per-tick values, charge invariants;
config-surface contract with acceptance/rejection matrix; runnable
validation guide mapped to SC-001..SC-006.

## Complexity Tracking

No constitution violations; table omitted.
