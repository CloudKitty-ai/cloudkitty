# Data Model: Waterline Contagion (spec 044)

## Modified entity: `WaterConfig` (`config/mod.rs:122`)

| Field | Type | Default | Serde | Constraint (validate_water) |
|---|---|---|---|---|
| `bath_gain` | f32 | 3.5 | existing | existing: finite, 0–100 |
| `bath_gain_ceiling` | f32 | 60.0 | existing | existing: finite, 0–100 |
| **`contagion_factor`** (new) | f32 | **0.0** | `default, skip_serializing_if = "f32_is_zero"` | finite and ≥ 0 (checked even when `bath_gain` is 0); budget: `ceiling + max(1, factor) × gain × max_ratio < safeguard` when `gain > 0` |

No other persisted entity changes. No world-state schema change: wetness
is `pos ∈ water tiles` this tick, scene membership is the existing
`Activity::partner()` (`kitty.rs:106`), and both are derived, never
stored.

## Derived per-tick values (in `advance_needs`, dropped after the loop)

| Value | Type | Definition |
|---|---|---|
| `water` | `Vec<Position>` | existing: positions of water elements (collected only when `bath_gain > 0`) |
| `wet_ids` | `BTreeSet<KittyId>` | kitties whose `pos` is in `water`; collected only when `contagion_factor > 0 && bath_gain > 0` |
| `contagious` | `BTreeSet<KittyId>` | kitties NOT in `wet_ids` whose `activity.partner()` is in `wet_ids` |

## The charge (per kitty, per tick, mutually exclusive arms)

```text
ambient  : always            needs.bath += need_rate_for(id, Bath)
occupancy: on water tile     if bath < ceiling { needs.bath += bath_gain × bath_ratio(id) }
contagion: else, contagious  if bath < ceiling { needs.bath += contagion_factor × bath_gain × bath_ratio(id) }
```

Invariants:

- At most one of {occupancy, contagion} per cat per tick (else-if,
  FR-005); at most one contagion source (own activity names ≤ 1
  partner — clarified Option A).
- Ceiling gates on the pre-charge value; overshoot ≤ one scaled charge
  (FR-004), the bound `validate_water` budgets.
- Reciprocity by kind: social play — both members name each other, both
  can pay; rest / co-sleep / groom — the naming side only.
- No RNG anywhere in the phase (FR-008).
