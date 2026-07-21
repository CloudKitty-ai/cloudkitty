# Contract: Sustained Purring

**Date**: 2026-07-20 | **Spec**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

## Configuration contract

```toml
[purr]
# A contented kitty rumbles for a while (a seeded draw between min and max
# ticks), then rests its motor for the cooldown before the next rumble.
# Purring is pure charm: it never costs a turn and never changes a need.
min_ticks = 6
max_ticks = 15
cooldown_ticks = 30
```

- **Absent table or absent keys**: defaults apply — every pre-011 config
  starts unedited.
- **Invalid**: `min_ticks = 0` or `min_ticks > max_ticks` → startup error in
  the standard voice naming `[purr] min_ticks` / `max_ticks`.
- **`cooldown_ticks = 0`**: legal — back-to-back purrs, each its own purr
  with its own start meow.

## Behavioral contract

| Guarantee | Statement |
|-----------|-----------|
| Background state | A purring kitty proposes, performs, and completes every action exactly as a quiet one; no tick is ever spent "purring". |
| Start | Only when earned — `happiness > thresholds.purr` or `happiness_rose` (unchanged rule) — and `tick ≥ purr_cooldown_until`. Started by the engine, never proposed. |
| Duration | Drawn once at start from the world RNG in `[min_ticks, max_ticks]`; runs to completion; nothing ends it early. |
| Meow | Exactly one purr meow per purr, at its start tick. All other meow rules untouched. |
| Cooldown | On purr end, `purr_cooldown_until = end + cooldown_ticks`. |

## API contract (additive only)

Every kitty payload (`/world`, `/kitties`, `/kitties/{id}`, `/ws`) gains:

```json
{ "purring_until": 1234, "purr_cooldown_until": 1260 }
```

`purring_until` is omitted when the kitty is quiet — its presence *is* the
"rumbling now" signal. No other payload changes; no new routes.

## Wire/compatibility contract

- Pre-011 snapshots (no purr fields; possibly `"last_action": "purr"`) load
  cleanly: kitties come up quiet and immediately eligible, and the retained
  `purr` action variant keeps `last_action` deserializable.
- A `purr` *proposal* (stale snapshot replay, future external behavior)
  validates to Idle unconditionally — never a spent turn, never an error.

## Determinism contract

Same seed + config + ticks → identical purr timeline (draws in stable
kitty-id order in a fixed tick phase); save/restore mid-purr resumes the
identical future.
