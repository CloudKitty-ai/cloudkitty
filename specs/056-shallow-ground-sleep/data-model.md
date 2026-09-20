# Data model: Shallow ground sleep (spec 056)

## The floor

| Field | Home | Type | Default | Bounds |
|---|---|---|---|---|
| `sleep_floor_off_beam` | `ActionsConfig` (`[actions]` in TOML) | f32 | 0.0 (serde default; absent = 0) | `0 ≤ floor < [thresholds] distress` (configured value), finite — else startup ConfigError |

Semantics: the lowest Sleep-need value plain-ground sleep can reach.
Never raises a need. Fixed for the world's life like every config dial.

## The warmth circumstance (existing, becomes shared)

One predicate, per sleeper per tick: own tile is a sunbeam, OR the
sleeper's mutual co-sleep partner (spec-041 `is_settled` gate) stands on
a sunbeam tile (spec-031 conduction). Today it selects the relief rate
(`sleep_relief_sunbeam` vs `sleep_relief`); after this spec it also
decides the floor escape and the finished level. One helper, three uses,
zero drift.

## Relief transition (per sleep tick)

```
warm  → need := max(0, need − sleep_relief_sunbeam)        (unchanged)
plain → need := need − min(sleep_relief, max(0, need − floor))
        (clamps at floor; need already ≤ floor moves by 0)
```

## Finished level (early-end, `Activity::Sleeping` only)

```
finished(kitty) = need(Sleep) ≤ (warm ? 0.0 : floor)
```

Evaluated after the scene's minimum duration as today; either side of a
duet, each with its own level; every other activity keeps literal 0.
At floor 0 both rules reduce exactly to today's law.

## Not stored / not changed

No snapshot field, no wire field, no observation element, no client
surface. The key appears in `GET /settings` and the boot log (spec 052).
