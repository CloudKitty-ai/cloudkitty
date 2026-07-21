# Data Model: Orthogonal-Only Interactions

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

No new entities, no schema changes, no new configuration. This feature changes
the *meaning* of one predicate and one metric. The model below is the
vocabulary the code must agree on afterward.

## The distance vocabulary

| Concern | Metric after 009 | Definition | Where it lives |
|---------|------------------|------------|----------------|
| **Interaction range** ("adjacent") | Manhattan ≤ 1 | own tile + N/E/S/W neighbors (2–5 tiles depending on edges/corners) | `Position::is_adjacent` — the single shared predicate (R1) |
| **Decision distance** (scoring, nearest-target, reach tests, chase patience) | Manhattan | `dx + dy` — the true 4-way walk cost | `Position::manhattan_distance`, used by every decision path (R2, R4) |
| **Movement** | unchanged | one N/E/S/W step per tick, bounds + occupancy checked | `Position::step`, `Direction` (already orthogonal) |
| **Spawn spreading** | Chebyshev (unchanged) | aesthetic spacing of same-type elements | `Position::chebyshev_distance`, consumer: `spawn.rs` only (R8) |

## Semantic invariants (what tests pin)

- **Range–walk agreement**: a target chosen by any scored decision is pursued
  with the same metric that scored it — no path may price in one geometry and
  walk in another (the 004 lesson, now global).
- **Interaction ⇒ in range, every tick**: any kitty in an eating/drinking
  scene has its element within Manhattan 1 of its position on every tick of
  the scene (property-suite assertion, SC-001).
- **Adjacency truth table** (for `is_adjacent(a, b)`):
  - same tile → `true`
  - orthogonal neighbor (`dx + dy == 1`) → `true`
  - diagonal neighbor (`dx == 1 && dy == 1`) → **`false`** (was `true`)
  - anything farther → `false`

## Existing state touched only in meaning

| State | Storage | 009 effect |
|-------|---------|------------|
| `Kitty.activity` + counterpart checks | snapshot | counterpart "gone" now includes "only diagonally adjacent"; stranded scenes end gracefully on the first tick after an old save loads (FR-003) |
| `Kitty.pursuit.closest` | snapshot | unit changes from Chebyshev to Manhattan for new measurements; an old save's stored value is a lower bound under the new metric — worst case one restored chase times out early, once (R6, accepted transient) |
| Distance-valued tunables (`tile_cost`, `solo_play_reach`, `sunbeam_reach`, `worth_a_detour`) | config | names and values unchanged; unit "tiles of travel" now honestly means walking steps (FR-006) |

## Explicitly unchanged

Snapshot schema, API payloads (`/world`, `/kitties`, `/ws`, …), config schema
and every shipped config file, the client, `spawn.rs`, `Direction`,
`Position::step`.
