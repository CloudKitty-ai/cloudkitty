# Implementation Plan: Water-Averse Pathing

**Branch**: `009-orthogonal-interactions` (shared batch branch) | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-water-averse-pathing/spec.md`

## Summary

Kitties learn to prefer dry paws. One new named tunable —
`water_step_cost`, in `[behavior]` beside `tile_cost` — is woven into the two
places behaviors already reason about travel: the greedy stepper
(`step_toward`) prices each candidate step's wetness when choosing among
distance-improving steps, and need-selection prices targets through a shared
`priced_travel` estimate so a bowl across a pond scores (and is chosen) like
the detour it really is. The engine is untouched — `Move` validation and the
anti-stuck guarantee are exactly what they were, because crossing stays legal
and the stepper still takes a wet improving step whenever it is the only
improving step. Builds directly on 009: all distances are Manhattan walking
steps; water adds a per-wet-step surcharge on top.

## Technical Context

**Language/Version**: Rust, stable toolchain (unchanged workspace)

**Primary Dependencies**: none new

**Storage**: snapshots unchanged (no new kitty or element state)

**Testing**: `cargo test --workspace` + clippy + fmt; new unit tests in
`needs_driven.rs`/`selection.rs`/`config.rs`, a crafted skirt/wade
integration test beside the welfare suite

**Target Platform**: local server (unchanged)

**Project Type**: behavior-layer change in `cloudkitty-core`, plus one config
field

**Performance Goals**: pricing is O(path length × water count) per estimate
with tiny constants (water ≤ floor(area/32) elements); nothing hot

**Constraints**: determinism (no RNG touched); Article IV split — preference
in behaviors, law unchanged; existing config files remain valid unedited

**Scale/Scope**: 3 source files + config.rs + 3 shipped tomls (one documented
line each) + tests

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design. PASS on both.*

| Article | Check | Verdict |
|---------|-------|---------|
| I — Cannot Suffer | Relief reachability untouched: crossing stays legal, and the stepper wades whenever wet is the only improving step, so no layout can trap a kitty. Estimates add finite cost, never a skip — an only-option target is still chosen. Welfare suite re-run. | ✅ PASS |
| II — Cannot Die | Untouched. | ✅ PASS |
| III — Cannot Be Alone | Untouched. | ✅ PASS |
| IV — Engine Is Law | The dividing line *is* the feature: `Move` validation and every engine rule unchanged; only behavior proposals change. | ✅ PASS |
| V — Deterministic | Cost comparison and L-path crossing count are pure functions; tie-breaks stay direction-order/id-order; no RNG. | ✅ PASS |
| VI — Spec-First | Spec approved first; the one new constant is named in config with a documented default and startup validation; tests amended in the same change. | ✅ PASS |

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/010-water-averse-pathing/
├── spec.md              # approved
├── plan.md              # this file
├── research.md          # R1–R7
├── data-model.md        # vocabulary + config field (no new entities)
├── quickstart.md        # validation guide
├── contracts/
│   └── water-cost-contract.md
└── tasks.md             # /speckit-tasks output
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config.rs                  # water_step_cost: serde default, validation, Default
├── behavior/
│   ├── selection.rs           # priced_travel helper; priced target choice for
│   │                          # eat/drink; sleep estimate priced; playmates unpriced
│   └── needs_driven.rs        # step_toward wet-step surcharge + dry-preferring
│                              # fallback; seek_element walks to the priced choice
└── (engine files)             # UNTOUCHED: action.rs validation, world.rs, spawn.rs

cloudkitty.toml, cloudkitty16.toml, cloudkitty48.toml
                               # + one documented water_step_cost line each
crates/cloudkitty-core/tests/welfare_longrun.rs
                               # crafted skirt/wade run; suite re-run
client/                        # UNTOUCHED (swim pose stays on the backlog)
```

**Structure Decision**: behavior-layer only. The engine's movement law is
deliberately not a file in this feature.

## Phase 0 → Phase 1 artifacts

- Research decisions (R1–R7): [research.md](./research.md)
- Vocabulary and config field: [data-model.md](./data-model.md)
- Config/behavior contract: [contracts/water-cost-contract.md](./contracts/water-cost-contract.md)
- Runnable validation: [quickstart.md](./quickstart.md)
