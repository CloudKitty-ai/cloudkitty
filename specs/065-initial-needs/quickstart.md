# Quickstart: Initial-Needs Distribution (spec 065)

Validation scenarios proving the feature end-to-end. Scratch configs
live in the session scratchpad, never under experiments/ (the
shipped-config sweep loads every experiments toml).

## Prerequisites

- Worktree at the feature branch; `cargo build` green.
- bc-collect (standalone workspace, `experiments/tools/bc-collect`)
  for byte-identity.

## 1. Inert when absent (SC-001)

Baseline before the change (tasks.md T001), then after: bc-collect on
a scratch copy of
`experiments/world-size-screen-2026-09-24/size100.toml`,
`--rollouts 1 --ticks 2000 --seed-base 993001`; `cmp` every array —
identical; meta delta = engine_commit only. Full `cargo test`: green,
zero golden movement.

## 2. A distressed start (SC-002, SC-004)

Scratch toml: any passing base config plus

```toml
[initial_needs]
cuddle = 92.0
eat = { min = 40.0, max = 70.0 }
```

Expected: every kitty's cuddle is 92.0 at tick 0 and its eat in
[40, 70] with kitties differing; happiness = the engine's weighted
floored number for the vector; cuddle (≥ distress threshold 90)
appears in `in_distress`, `distress_since[cuddle] == 0`, and the
distress log holds a tick-0 event per kitty. Run 200 ticks: relief
plays out; invariants green.

## 3. Per-kitty override precedence (SC-002)

Add to one kitty: `initial_needs = { cuddle = 10.0 }`. Expected: that
kitty's cuddle is 10.0 (no distress entry for it), its eat still
draws from the roster-wide [40, 70]; all other kitties unchanged.

## 4. Determinism + 062 composition (SC-003)

Same seed+config twice → byte-equal worlds. Then add a `[starts]`
table: positions draw as 062 pins (its golden-draw suite green),
needs draw exactly as without `[starts]` — and vice versa.

## 5. All needs armed (SC-005)

All six needs at `{ min = 85.0, max = 100.0 }`, 4000 ticks: completes,
invariants green throughout, happiness floored at start and recovering
— the mitigation's floor-initialized case expressible as a pure config
addition.

## Teardown

Delete scratch tomls; no goldens or fixtures touched anywhere above.
