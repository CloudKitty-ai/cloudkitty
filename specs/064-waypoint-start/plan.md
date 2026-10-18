# Implementation Plan: Waypoint Start-Index by Position

**Branch**: `product/waypoint-start` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

One flag, one new Lattice lookup, one branch at the one seeding site.
Flag off: `kitty.explore_waypoint = lattice.start_index(kitty.id)` as
today, bit-for-bit. Flag on: `lattice.nearest_index(kitty.pos)` — the
tour index minimizing `(manhattan(waypoint(i), pos), i)`. No RNG, no
schema change, no dials.

## Technical Context

**Language/Testing/Platform/Structure**: as spec 063's plan — Rust
workspace, changes confined to `cloudkitty-core`, `cargo test` +
`scripts/mutate.sh` red-first, local gate `cargo fmt` + `clippy
--all-targets`.

**Key facts grounding the design** (read 2026-10-18 at c8db8781):

- The ONE seeding site is `World::generate` (world.rs ~157): runs
  after every placement mechanism (explicit coords, 062 draws,
  defaults — kitties already positioned and sorted by id) and before
  `advance_tours` and world stocking — FR-004 is satisfied by the
  site's existing position in the generation sequence.
- `Lattice::start_index` is `kitty_id % cycle_len` (explore.rs:152);
  `waypoint(index)` is a pure serpentine-cycle lookup; `cycle_len` ≥ 1
  always.
- `advance_tours` immediately after seeding already implements "a cat
  spawned on (or beside a held) waypoint is already past it" — nearest
  seeding makes this case common instead of rare, and the existing
  rule handles it unchanged.
- Config home: `BehaviorConfig` beside 063's keys, same
  skip-serialization discipline (`GET /config` must not grow); a plain
  bool, no validation arm needed.

## Research decisions

- **D1 — Lookup lives on `Lattice`** (`nearest_index(pos) -> u32`,
  linear scan over the cycle, `min_by_key((manhattan, i))`): the
  lattice already owns `start_index`/`waypoint`/`cycle_len`; a sibling
  keeps one geometry home. Linear scan is generation-time-only, cycle
  lengths are small (≤ ~2·nx·ny grid points); no cache or cleverness.
  Alternative (closed-form from the serpentine layout) rejected:
  clever index math is where the serpentine's reflection bugs live,
  and the existing `waypoint_at` test shows the house prefers the
  readable form checked against the built lattice.
- **D2 — Flag name** `waypoint_start_by_position: bool`,
  `#[serde(default, skip_serializing_if = "std::ops::Not::not")]`
  (the exact 063/045 pattern). No dials (spec Key Entities).
- **D3 — Branch at the seeding loop**, not inside `start_index`:
  `start_index` keeps its documented id-law for every other caller
  and for flag-off literal identity; the loop picks the seeder.
- **D4 — Byte-identity evidence** reuses the 063 recipe: bc-collect
  size100 seed 993001 baseline before any change, byte-compare after
  (meta modulo engine_commit), plus the standing golden suites.

## Constitution Check

PASS (pre- and post-design): Articles I–III untouched; IV untouched
(world setup, not proposal validation); V — determinism preserved, no
draw added or moved, flag-off stream identical; VI — spec-first, the
flag is config with a documented default, no magic numbers.

## Project Structure

```text
specs/064-waypoint-start/
├── plan.md            # This file (research inlined above)
├── contracts/seeding-law.md
├── quickstart.md
└── tasks.md           # /speckit-tasks

crates/cloudkitty-core/src/
├── explore.rs         # Lattice::nearest_index + unit tests
├── world.rs           # the seeding branch in World::generate
└── config/mod.rs      # the flag (defaults.rs untouched — bool)
```

## Complexity Tracking

No violations; not needed.
