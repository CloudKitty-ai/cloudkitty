# Data Model: The Wet-Fur Engine Batch

## New configuration (the only new data)

### `WaterConfig` — section `[water]`

| Field | Type | Default | Validation |
|---|---|---|---|
| `bath_gain` | f32 | 1.5 | finite, ≥ 0 (0 disables), ≤ 100 |
| `bath_gain_ceiling` | f32 | 50.0 | finite, in [0, 100]; safeguard-headroom bound (below) |

Section is `#[serde(default)]` on `Config` with per-field
`default_water_bath_gain` / `default_water_bath_gain_ceiling` fns in
`config/defaults.rs` (spec 020 FR-003 pattern). Old configs, frozen
exams, and legacy snapshots all keep loading: no fingerprint field feeds
from `[water]` (fingerprint = w/h/seed/kitty-ids only).

**Cross-section validation invariant (the load-time guard)**:

```
bath_gain_ceiling + bath_gain × max_roster_ratio < thresholds.safeguard
where max_roster_ratio = max(1.0, max over roster of
      need_rate_for(kitty, Bath) / needs.bath)
and   needs.bath > 0 whenever bath_gain > 0
```

Violation → `ConfigError::invalid` naming `[water] bath_gain_ceiling`
(or `[needs] bath` for the zero-baseline case), the offending kitty, and
the arithmetic in the expected-clause.

## Derived (not stored) quantities

- **Per-kitty water charge** (per occupied tick, pre-charge bath below
  ceiling): `bath_gain × need_rate_for(kitty, Bath) / needs.bath`.
  Computed inside `advance_needs`; never stored; applied via `Need::add`
  (0–100 clamp by construction).
- **Sidestep candidate pool** (per blocked chase apply): lawful steps
  (in-bounds, kitty-free) with Manhattan-to-target ≤ current, minus the
  blocked straight step. Transient; one uniform master-RNG `choose` when
  non-empty.

## Explicitly NOT added

- **No new world/kitty state**: no wetness flag, no charge accumulator,
  no sidestep memory. Snapshots are byte-compatible both directions.
- **No new events**: no water-charge event, no sidestep event (the
  activity log and pursuit bookkeeping already record what moved where).
- **No schema surface**: observation stays 182 (bath need + water slots
  + own traits already present — learnability needs nothing new), action
  menu stays 40, no new `Activity` variant.

## Modified semantics (no shape change)

- **`zero_distance_relief_exists(_, _, Eat)`** (rl `welfare.rs:57-60`):
  tightened from "any adjacent Chow element" to "adjacent **stocked**
  chow" — reconciled to the authoritative validate arm
  (`adjacent_stocked_chow`, `action.rs:366`). Pinned-streak accounting
  inherits the honest predicate; no struct changes.
- **`needs_driven` route scoring** (`needs_driven.rs:327-343`): the wet
  destination surcharge becomes
  `water_step_cost × (need_rate_for(me, Bath) / needs.bath)` — same
  ratio as the engine charge, so both deciders express one preference.
  Config key unchanged; behavior-internal arithmetic only.

## Equivalence fixture matrix (test data, `welfare_validate_equivalence.rs`)

Axes: `NeedKind` (all six) × neighbor state (adjacent-free /
adjacent-busy / absent) × relief element (present-adjacent / absent /
present-but-consumed [chow only]). Cells assert:
`zero_distance_relief_exists ⇔ ∃ lawful relieving action that validates`,
with the relieving-action set taken from the public spec-019 relief
mapping. Constructed worlds use public constructors only (the
`mask_oracle.rs` pattern) — no behavior-layer imports.
