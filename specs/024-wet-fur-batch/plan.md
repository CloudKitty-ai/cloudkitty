# Implementation Plan: The Wet-Fur Engine Batch

**Branch**: `024-wet-fur-batch` | **Date**: 2026-08-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/024-wet-fur-batch/spec.md`

## Summary

Three items, one comparability break. (1) **Wet fur**: a new `[water]`
config section prices water-tile occupancy in bath need — charged inside
`advance_needs` (the existing needs phase, before the same-tick happiness
recompute), gated by a pre-charge ceiling, scaled by the kitty's own bath
rise trait, with the no-distress-from-swimming guarantee enforced **at
config validation time** (arithmetic over the roster) and re-proven at
runtime by the property suite. (2) **Chase sidestep**: the stall branch of
the Chase apply arm (`action.rs:513`) learns the FR-008 sidestep
discipline — a deterministic, never-synchronized draw from the master RNG
at apply time (the house pattern the deliberate purr established), among
lawful non-retreating steps. (3) **Equivalence guardrail**: a
`cloudkitty-rl` integration test asserting `zero_distance_relief_exists`
agrees with `action::validate` over a need × fixture matrix — which has
already earned its keep: planning discovered a real eat-side divergence
(empty adjacent bowl counts as relief but `Eat` doesn't validate) that
this batch reconciles in favor of the authoritative layer.

## Technical Context

**Language/Version**: Rust (stable toolchain, workspace edition), no new dependencies

**Primary Dependencies**: existing workspace crates only — `cloudkitty-core` (engine), `cloudkitty-rl` (welfare + harness), `serde`/`toml` (config)

**Storage**: none new — snapshot format untouched (no new world state; config fingerprint covers only w/h/seed/kitty-ids, so old snapshots keep loading — verified `config/mod.rs:783-793`, `persist.rs:93-139`)

**Testing**: `cargo test --workspace` (unit + property + integration), golden regeneration via `UPDATE_GOLDENS=1`, pytest for the Python surface (unaffected — no schema change)

**Target Platform**: unchanged (server binary + headless test drivers)

**Project Type**: simulation engine batch — three bounded changes in `cloudkitty-core` + one test in `cloudkitty-rl`

**Performance Goals**: needs-phase water lookup is O(kitties × water elements) per tick — bounded (≤ 4–6 kitties served, water capped at area/32); no measurable tick-time impact expected

**Constraints**: no observation/action schema change (182/40 asserted); RNG stream-shape discipline (config may change outcomes, never draw shape); served `cloudkitty.toml` untouched; frozen exam configs untouched (verified: `Config` has no `deny_unknown_fields` — new sections with serde defaults keep hash-pinned exams valid)

**Scale/Scope**: ~4 source files touched in core (`world.rs`, `action.rs`, `config/*`), 1 behavior file (`needs_driven.rs`), 1 new test file in rl, golden regeneration, screen-config migration

## Constitution Check

*GATE: evaluated against constitution v1.2.0 before Phase 0; re-checked after Phase 1.*

- **Article I (no suffering)**: PASS. The water charge is need pressure on
  an existing bounded need (`Need::add` clamps 0–100 by construction,
  `needs.rs:59-74`). The ceiling + dial-bounds arithmetic guarantees the
  charge can never carry bath across the safeguard threshold (FR-004);
  validation rejects any configuration where it could. Relief guarantee
  untouched (bath's relief is grooming, available anywhere —
  `zero_distance_relief_exists` returns true unconditionally for Bath).
- **Article II (no death)**: PASS — nothing touches kitty existence.
- **Article III (never alone)**: PASS — untouched.
- **Article IV (engine is the law)**: PASS with note. The sidestep is not
  a "reshaped proposal": the proposal is *Chase target X*, and how the
  engine routes a legal chase's step (today `Direction::toward`, after
  this batch `toward`-or-sidestep) is engine execution detail, exactly
  like the stall is today. Validation outcomes for every action are
  unchanged except where the spec changes them (none). The water charge
  is engine physics, not advisor reshaping.
- **Article V (deterministic, fair)**: PASS. The sidestep draws from the
  master RNG at apply time in the tick's fair apply order (the spec 022
  deliberate-purr pattern, `world.rs:887-909`); draw count depends only
  on world state (blocked or not), never on config — the fixed-shape rule
  (`world.rs:866-874`) governs config, and no new config key alters draw
  shape. The water charge draws no randomness at all (reads don't shape
  the stream). Tick phase order unchanged.
- **Article VI (spec-first, config constants)**: PASS. Every new constant
  is a config key with a documented default (`[water] bath_gain = 1.5`,
  `bath_gain_ceiling = 50.0`); the batch updates the spec-contract
  validation-order guard fixture in the same change (adding a section
  appends to the order — documented, deliberate). The invariant suite
  gains the water-safeguard property; CI gates unchanged.

**Post-Phase-1 re-check**: still PASS. The design added no new projects,
no new dependencies, no state, no schema. The one metric-semantics change
(eat-side relief predicate tightened to stocked-chow, R7) is a
certification-measurement correction riding the batch's designed
comparability break — surfaced to the owner in the plan report, not
hidden.

## Project Structure

### Documentation (this feature)

```text
specs/024-wet-fur-batch/
├── plan.md              # This file
├── research.md          # Phase 0 output — R1..R10 decisions
├── data-model.md        # Phase 1 output — config/state/fixture entities
├── quickstart.md        # Phase 1 output — validation guide
├── contracts/
│   ├── water-config.md      # [water] section contract
│   ├── chase-sidestep.md    # sidestep semantics contract
│   └── equivalence-matrix.md# need × fixture agreement contract
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── world.rs             # advance_needs: water charge; (no other phase touched)
├── action.rs            # Chase apply arm: sidestep on stall
├── config/mod.rs        # WaterConfig section + Default + need_rate_for (unchanged)
├── config/defaults.rs   # default_water_bath_gain, default_water_bath_gain_ceiling
├── config/validate.rs   # validate_water (incl. roster-arithmetic safeguard bound)
└── behavior/needs_driven.rs  # water_step_cost × bath-trait scaling

crates/cloudkitty-core/tests/
├── invariants_proptest.rs    # (existing gate — must stay green)
└── water_safeguard.rs        # NEW: the executable no-distress-from-swimming guard

crates/cloudkitty-rl/tests/
├── welfare_validate_equivalence.rs  # NEW: the guardrail (mask_oracle.rs precedent)
└── goldens/run-json.golden.json     # regenerated once (UPDATE_GOLDENS)

experiments/exp-001-bc-mappo/configs/
└── cloudkitty-24x24-screen.toml     # values-preserved migration ([water] explicit)
```

**Structure Decision**: everything lands in existing crates and files;
the only new files are the two test files and the three contract docs.
No new modules, no new crates.

## Complexity Tracking

No constitutional violations to justify. The one deliberate deviation
from the spec's letter (FR-006 said "per-kitty seeded shuffle"; the
engine-side mechanism uses master-RNG draws in fair apply order, which
delivers the same two guarantees — deterministic, never synchronized —
without inventing per-kitty RNG plumbing in the apply phase) is recorded
as research decision R5 and amended into the spec in this change.
