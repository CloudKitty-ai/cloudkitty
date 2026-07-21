# Data Model: Sustained Purring

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## New kitty state (serialized in snapshots, served in every kitty payload)

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `purring_until` | `Option<u64>` | `None` (omitted when absent) | `Some(t)` ⇒ the kitty is purring and stops at tick `t`. The viewer's "is rumbling" signal. |
| `purr_cooldown_until` | `u64` | `0` | No new purr may begin before this tick. |

Both `#[serde(default)]`: a pre-011 snapshot loads with every kitty quiet
and immediately eligible (spec FR-007).

## New configuration (`[purr]`, whole table optional)

| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `min_ticks` | u64 | 6 | ≥ 1, ≤ `max_ticks` — startup error naming the field |
| `max_ticks` | u64 | 15 | ≥ `min_ticks` |
| `cooldown_ticks` | u64 | 30 | any (0 is legal: back-to-back purrs) |

## The purr lifecycle (engine-owned, `purr_phase`, stable kitty-id order)

```text
        earned (happiness > thresholds.purr OR happiness_rose)
        AND tick >= purr_cooldown_until
quiet ────────────────────────────────────────────────────────► purring
  ▲     duration = min_ticks + rng.gen_range(0, max−min+1)          │
  │     purring_until = tick + duration                             │
  │     purr meow recorded (exactly once, bypasses proposal gate)   │
  │                                                                 │
  └───────────────── tick >= purring_until ─────────────────────────┘
        purr_cooldown_until = tick + cooldown_ticks
```

- One RNG draw per start, even when min == max (fixed draw-count rule).
- Nothing ends a purr early; the earned rule gates *starting* only.
- Purring never touches needs, happiness, activities, or the action slot.

## Retired surface

`Action::Purr`: variant retained solely because serialized `last_action` in
pre-011 snapshots may contain `"purr"`; validation resolves it to Idle
unconditionally, apply is a no-op, and no behavior constructs it.

## Explicitly unchanged

Needs/happiness arithmetic, all welfare guarantees, activity/duet machinery,
meow rules for every other message, spawn, movement, the API route set
(payloads gain only the two kitty fields).
