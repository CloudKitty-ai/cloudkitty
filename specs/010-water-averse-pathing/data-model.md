# Data Model: Water-Averse Pathing

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

No new entities, no snapshot changes, no API changes. One config field and
two derived quantities.

## The new configuration field

| Field | Home | Type | Default | Validation |
|-------|------|------|---------|------------|
| `water_step_cost` | `[behavior]` (`BehaviorConfig`), beside `tile_cost` | f32 | 4.0 | finite and ≥ 0, else startup error naming the field |

Semantics: the extra effort a kitty ascribes to placing a paw on a water
tile, denominated in tiles of travel (the `tile_cost` family). 0 disables
the preference; the engine never reads it.

## Derived vocabulary (pure functions, no storage)

| Quantity | Definition | Consumers |
|----------|------------|-----------|
| **step cost** | `manhattan(dest → target) + water_step_cost × is_water(dest)` | `step_toward`'s ordering among improving steps; dry-preferring fallback |
| **priced travel** | `manhattan(from → to) + water_step_cost × |{water tiles on the dominant-axis-first L-path, endpoint excluded}|` | eat/drink target choice (min by `(priced, id)`), sleep estimate + `sunbeam_reach` comparison, cuddle estimate |

## Invariants (what tests pin)

- **Same options, new ordering**: the set of steps `step_toward` will take is
  identical to 009's; only preference among improving steps changes. Wading
  happens whenever wet is the sole improving step — anti-stuck by
  construction.
- **Score/walk agreement** (the 004 rule, extended): the element chosen by
  the priced score is the element the walk pursues, under identical
  arithmetic.
- **Pricing reorders, never removes**: `priced_travel` is finite for every
  target; a need with any relief path is never skipped because of water.
- **Determinism**: no RNG anywhere in the preference; ties resolve by
  direction order / id order as before.

## Explicitly unchanged

Engine (`Move` validation, chase stepping, spawning, invariants), snapshot
schema, API payloads, client, playmate ordering (moving targets, unpriced —
R3), all existing config values.
