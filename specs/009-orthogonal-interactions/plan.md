# Implementation Plan: Orthogonal-Only Interactions

**Branch**: `009-orthogonal-interactions` | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-orthogonal-interactions/spec.md`

## Summary

Interaction range tightens from the eight surrounding tiles (Chebyshev ≤ 1) to
the four compass neighbors plus the kitty's own tile (Manhattan ≤ 1), matching
the strictly 4-way movement — and every distance that informs a decision or
tracks progress moves from Chebyshev to Manhattan, because with 4-way movement
Manhattan *is* the true walk cost. The whole change is a semantic sweep across
`cloudkitty-core`: redefine `Position::is_adjacent`, introduce
`manhattan_distance`, migrate every decision-path call site, and simplify the
greedy stepper (whose two-part progress score existed only to patch over
Chebyshev's blindness). No config schema changes, no API shape changes, no
client changes, no new tunables. Spawn *spreading* deliberately keeps Chebyshev
(it is aesthetic spacing, not interaction — spec Assumptions).

## Technical Context

**Language/Version**: Rust, stable toolchain (workspace as shipped in 001)

**Primary Dependencies**: none new — `cloudkitty-core` stays HTTP-free and
filesystem-free; `cloudkitty-server` untouched

**Storage**: existing JSON snapshots — schema unchanged; old saves load as-is
(FR-003), stranded diagonal activities end via the standing counterpart-gone
rule

**Testing**: `cargo test --workspace` (unit + integration + the property
suite), `cargo clippy -- -D warnings`, `cargo fmt --check`; no JS changes so
`node client/test-meadow.mjs` is untouched but still run in CI

**Target Platform**: local server (unchanged)

**Project Type**: simulation engine change, single crate touched

**Performance Goals**: none at risk — Manhattan is the same arithmetic cost as
Chebyshev (`dx + dy` vs `max(dx, dy)`)

**Constraints**: determinism (Article V) — no RNG draws added or removed, all
tie-breaks stay `(distance, id)`-shaped; zero config-file edits (SC-005)

**Scale/Scope**: ~6 source files in `cloudkitty-core`, ~30 call sites, plus
test amendments; no other crate, no client, no config

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design. PASS on both.*

| Article | Check | Verdict |
|---------|-------|---------|
| I — Cannot Suffer | Safeguard spawn logic untouched; relief remains reachable because movement (already 4-way) is untouched — a kitty can always walk to an orthogonal neighbor of any element. Property suite re-run with tightened adjacency assertions (FR-007). | ✅ PASS |
| II — Cannot Die | No kitty-removal path exists or is touched. | ✅ PASS |
| III — Cannot Be Alone | Roster logic untouched. | ✅ PASS |
| IV — Engine Is Law | The change *strengthens* the enforcement surface: `validate` inherits the tighter range through `is_adjacent`/`adjacent_element`/`is_conscriptable_friend`, so diagonal proposals resolve to Idle exactly like any illegal proposal. | ✅ PASS |
| V — Deterministic | No new randomness; `Direction::toward` tie rules and all `min_by_key` tie-breaks keep their deterministic shapes with the new metric. Same seed + new rules → same world, always. (A given seed produces a *different* world than under the old rules — that is the feature, not a violation; determinism is within a rules version, as with every behavior change shipped so far.) | ✅ PASS |
| VI — Spec-First, Test-Guarded | Spec written and approved first; no new constants (semantics reinterpreted, names kept — FR-006); grid tests, validation tests, behavior tests, and the property suite amended in the same change. | ✅ PASS |

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/009-orthogonal-interactions/
├── spec.md              # Feature specification (approved)
├── plan.md              # This file
├── research.md          # Phase 0: decisions R1–R8
├── data-model.md        # Phase 1: distance-vocabulary model (no new entities)
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   └── interaction-range-contract.md   # Phase 1: validation + API contract
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── grid.rs                    # is_adjacent → Manhattan ≤ 1; new manhattan_distance;
│                              # chebyshev_distance retained for spawn spread only
├── action.rs                  # validation inherits (no edit expected beyond comments);
│                              # chase apply (Direction::toward) verified unchanged
├── world.rs                   # adjacent_element / nearest_* / friend helpers /
│                              # update_pursuit tie-breaks & distances → Manhattan
├── behavior/
│   ├── selection.rs           # all scoring & reach distances → Manhattan
│   └── needs_driven.rs        # step_toward simplifies to pure-Manhattan progress;
│                              # sunbeam/cuddle/seek distances → Manhattan
└── spawn.rs                   # UNTOUCHED (spread heuristic keeps Chebyshev, by spec)

crates/cloudkitty-core/tests/
└── welfare_longrun.rs         # adjacency assertions inherit; new per-tick
                               # "interacting ⇒ orthogonally in range" assertion

client/                        # UNTOUCHED (FR-009)
cloudkitty.toml (+16/48)       # UNTOUCHED (FR-006, SC-005)
```

**Structure Decision**: single-crate semantic sweep inside `cloudkitty-core`.
The one deliberate *non*-change: `spawn.rs` keeps `chebyshev_distance` for its
spread sampling, so `grid.rs` retains both metrics with doc comments naming
which concern each serves.

## Phase 0 → Phase 1 artifacts

- Research decisions (R1–R8): [research.md](./research.md)
- Distance vocabulary and compatibility notes: [data-model.md](./data-model.md)
- Validation/API contract: [contracts/interaction-range-contract.md](./contracts/interaction-range-contract.md)
- Runnable validation guide: [quickstart.md](./quickstart.md)
