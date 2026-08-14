# Phase 1 Data Model: Shared Sunbeam Warmth

No new entities, config keys, or persisted state. The rule is a predicate
over existing world state, evaluated per serviced tick inside
`apply_sleep_relief`.

## Inputs (all existing)

| Input | Source | Already in scope? |
|-------|--------|-------------------|
| `in_sunbeam` | own tile holds a Sunbeam element (re-checked each serviced tick by the `Activity::Sleeping` arm) | yes — function parameter |
| `partner` | the sleeper's `Sleeping { with_friend }`, filtered by `is_available_friend` | yes — function parameter |
| partner activity | `world.kitty(partner).activity` | yes — read for the cuddle tier |
| partner position | `world.kitty(partner).pos` | new read, existing accessor |
| partner tile element | `world.element_at(partner_pos).element_type()` | new read, same accessor as the own-tile rule |
| `sleep_relief` / `sleep_relief_sunbeam` | `config.actions` | yes |

## The predicate

```
mutual        := partner is Some AND partner.activity ∈ {Sleeping, Resting}
                 (the FR-014/15 predicate, already computed for the cuddle
                 tier — hoisted so ONE evaluation feeds both uses)
partner_warm  := mutual AND partner's tile holds a Sunbeam
sleep_rate    := sleep_relief_sunbeam  if in_sunbeam OR partner_warm
                 sleep_relief          otherwise
```

Properties (spec FRs):

- **Receiver**: only the Sleeping kitty whose relief is being applied —
  the function only runs for the Sleeping activity (FR-004).
- **One hop**: `partner` is the direct partner; nothing traverses further
  (FR-002).
- **No stacking**: the rate is selected, not summed — any beam combination
  yields exactly `sleep_relief_sunbeam` (FR-003).
- **No stickiness**: every input is read fresh each serviced tick (FR-006).
- **Untouched channels**: the cuddle tier below the rate choice reads the
  same `mutual` value and its rates are not modified (FR-007).

## State transitions

None. No stored state; the predicate is stateless over the current tick's
world.
