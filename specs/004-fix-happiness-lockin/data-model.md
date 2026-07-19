# Data Model: Fix Low-Happiness Lock-In

**Date**: 2026-07-18 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Delta document: only additions and changes relative to the MVP data model
([001 data-model.md](../001-cloudkitty-mvp/data-model.md)). All types keep
their serde derives; field names below are canonical wire names. Defaults for
new tunables are documented in [research.md §R8](./research.md).

## Kitty (extended)

| Field | Type | New/Changed | Notes |
|-------|------|-------------|-------|
| `pursuit` | Option\<Pursuit\> | **new** | current chase bookkeeping; engine-maintained; serde-defaulted (`None`); omitted from JSON when absent |
| `abandoned_chases` | Vec\<AbandonedChase\> | **new** | targets excluded after a futile chase (FR-006); engine-maintained and engine-pruned; serde-defaulted (empty); omitted from JSON when empty |
| `last_relief` | BTreeMap\<NeedKind, u64\> | **new** | tick each need last received relief; stamped by `lower_need`; serde-defaulted (empty); missing key reads as 0 ("never relieved") |
| `distress_since` | BTreeMap\<NeedKind, u64\> | **new** | tick each *active* distress began; keys ⊆ `in_distress` after every needs phase; serde-defaulted (empty) |
| `in_distress` | BTreeSet\<NeedKind\> | unchanged | remains the edge-trigger authority; kept for wire compatibility |

**Engine-maintained, behavior-readable**: all three new fields are written
only by the engine from *applied* actions and the needs phase — a behavior
(built-in or external) can read them via `DecisionContext.me` but cannot
forge them (Article IV).

## Pursuit and AbandonedChase (new)

```
Pursuit        { target: TargetRef, started: u64, closest: u32 }
AbandonedChase { target: TargetRef, until: u64 }
```

Patience is **elapsed** ticks (`tick − started`), not consecutive applied
chases — a one-tick opportunistic detour or meow does not reset a chase's
clock (analyze finding I2).

- Updated in the apply phase, immediately after `last_action` is recorded,
  from the **validated** action, in this order:
  1. pursuit target no longer exists → pursuit cleared, **no** exclusion
     (the target died; stale state never survives expiry);
  2. applied `Play` whose target equals `pursuit.target` → pursuit cleared
     (a catch, not an abandonment);
  3. applied `Chase(t)`: `t == pursuit.target` →
     `closest = min(closest, distance)`; different/new target → replaced by
     `Pursuit { target: t, started: tick, closest: distance }`;
  4. otherwise, if `tick − started ≥ behavior.chase_patience_ticks` and
     `distance(kitty, target) ≥ closest` → push
     `AbandonedChase { target, until: tick + behavior.chase_exclusion_ticks }`
     and clear pursuit. (A pursuit the kitty merely lost interest in also
     expires through this arm — briefly excluding a target it already walked
     away from is harmless.)
- `abandoned_chases` entries with `until ≤ tick` are pruned in the same
  apply-phase pass, keeping the list bounded (≈ exclusion ÷ patience
  entries) without a separate cap.

**Viability rule (behavior-side, shared)**: play candidate `c` is
*non-viable* iff `abandoned_chases` holds `c` with `until > tick`, **or**
`pursuit.target == c` with `tick − started ≥ behavior.chase_patience_ticks`
and `distance(kitty, c) ≥ pursuit.closest`. Non-viable candidates are
skipped in target selection and excluded from the solo-play reach test —
with every nearby target excluded, solo play (R5) unlocks.

## Need selection score (behavior-shared, `behavior/selection.rs`)

```
urgency(kind) = max(0, pressure(kind) − thresholds.safeguard)
score(kind)   = pressure(kind)
                + behavior.urgency_weight × urgency(kind)
                − behavior.tile_cost × travel_distance(kind)
```

- `travel_distance` keeps its existing per-need semantics (Chebyshev; bath
  and sleep are 0; play now measures nearest **viable** critter-or-kitty).
- Winner: highest score; ties broken by smallest `last_relief[kind]`
  (missing = 0), then `NeedKind::ALL` order (final deterministic fallback).
- The old two-mode selection (`safeguard` lock / `most_convenient` with its
  ±20 band) is removed. `highest_pressure()` remains only where raw pressure
  is the question (meow urgency), not selection.

## Action (changed)

```
Play { target: Option<TargetRef> }     // was Play(TargetRef)
```

- Wire compatibility: `{"action":"play","target":"element","id":103}`
  (social) still parses; solo play serializes as `{"action":"play"}`.
- **Validation**: `Some(target)` — unchanged rules (critter adjacency /
  available friend). `None` — always legal (mirrors self-groom).
- **Application**: `Some` — unchanged (`play_relief` to actor, and to
  partner if kitty). `None` — `solo_play_relief` to actor only.
- `Chase` is unchanged; chase legality (critters and kitties only) is
  unchanged.

## Config (extended)

| Section.key | Default | Validation |
|-------------|---------|------------|
| `behavior.urgency_weight` | 2.0 | finite, ≥ 0 |
| `behavior.tile_cost` | 1.0 | finite, ≥ 0 |
| `behavior.worth_a_detour` | 30.0 | 0 ≤ v ≤ 100 |
| `behavior.chase_patience_ticks` | 12 | ≥ 1 |
| `behavior.chase_exclusion_ticks` | 60 | ≥ 1 |
| `behavior.solo_play_reach` | 8 | ≥ 1 |
| `actions.solo_play_relief` | 10.0 | ≥ 0 and ≤ `actions.play_relief` |
| `viewer.distress_patience_ticks` | 60 | ≥ 1 |

- `[viewer]` is a new section holding constants consumed by the client via
  `/config`; the simulation never reads it.
- Every violation reports field, value and allowed range (FR-011), matching
  the existing validation style.
- Config fingerprint (width/height/seed/kitty ids) is **unchanged** —
  existing snapshots resume under the new config keys.

## Tick-order placement (unchanged order, new bookkeeping)

Article V's four phases are untouched; new writes slot into existing steps:

1. **Decide** — behaviors read `pursuit` / `last_relief` / `distress_since`
   from the snapshot; no new writes.
2. **Apply (kitty-id order)** — after `last_action` is recorded: pursuit
   bookkeeping (above); `lower_need` stamps `last_relief[kind] = tick` on
   every relief it applies (actions, passive sleep continuation, partner
   effects — one choke point covers all paths).
3. **Environment** — unchanged (movement, expiry, spawn-to-minimum,
   safeguard).
4. **Needs / invariants** — beside the existing edge-trigger: crossing the
   distress threshold inserts `distress_since[kind] = tick`; dropping below
   removes the entry; self-heal inserts `tick` for any `in_distress` member
   missing a `distress_since` entry (pre-004 snapshot resumed — ages count
   from resume).

## Invariants (additions to `invariants::check`)

- `distress_since` keys ⊆ `in_distress` members (no orphaned ages). The
  reverse direction is legal transiently — a pre-004 snapshot arrives with
  distress but no start ticks, and the next needs phase self-heals it —
  so equality would wrongly refuse old saves at load-time validation.
- `pursuit.closest` ≤ the world's maximum possible distance;
  `pursuit.started` ≤ current tick when `pursuit` is `Some`.
- Every `abandoned_chases` entry has `until > tick` after the apply-phase
  prune (no expired entries linger).
- Existing invariants unchanged; the property suite runs both with fresh
  worlds and with the new fields defaulted (pre-004 snapshot shape).

## Wire / persistence summary

- **World (persistence)**: gains the four kitty fields; all serde-defaulted
  → pre-004 snapshots load; 004 snapshots omit empty/None fields, keeping
  files tidy.
- **WorldSnapshot (wire + decisions)**: same Kitty struct, so `pursuit`,
  `abandoned_chases`, `last_relief` and `distress_since` appear in `/world`
  and WS payloads automatically; viewers derive distress age as
  `world.tick − distress_since[need]`. See
  [contracts/http-api-delta.md](./contracts/http-api-delta.md).
