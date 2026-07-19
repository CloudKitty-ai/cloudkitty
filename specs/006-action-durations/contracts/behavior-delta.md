# Behavior Contract Delta: Action Durations

**Base contracts**: [001 behavior.md](../../001-cloudkitty-mvp/contracts/behavior.md),
[004 behavior-delta.md](../../004-fix-happiness-lockin/contracts/behavior-delta.md).
The `Behavior` trait, decision budget, fallback, and validation pipeline are
unchanged. This delta covers how proposals are treated while an activity is
in progress, and what behaviors can now read.

## The one-sentence version

Your proposals still work exactly as before — except that for the first
`min` ticks of an activity they are advisory-only (the engine continues the
activity regardless), and an activity you never end yourself will be ended
for you at `max` ticks or when its need reaches 0.

## DecisionContext additions (read-only, engine-authored)

Via `ctx.me`:

| Field | Meaning for a behavior author |
|-------|-------------------------------|
| `activity` | Now covers all six need-relieving activities (`eating`, `drinking`, `playing`, `grooming` join `resting`/`sleeping`). What your kitty is *actually* doing across ticks, as recorded by the engine. |
| `activity_clock` | `{ started, applied }` — when the current activity began and the last tick its effects landed. Derive elapsed as `tick − started + 1`. Compare against `ctx.config.actions.durations.*` to know whether your kitty is still inside its minimum (proposals superseded) or past it (proposals honored). Absent when no activity is in progress. |

## How the engine treats your proposal mid-activity

Given an ongoing activity with elapsed `e`, minimum `min`, maximum `max`
(from `actions.durations.<activity>`):

- **`e < min`** — any proposal (including a valid, different action) is
  superseded by continuation of the current activity. Not an error, not a
  fallback: the engine simply keeps the scene going. Your decision budget
  is still spent; propose cheaply if you can tell (via `activity_clock`)
  that you're inside a minimum.
- **`min ≤ e < max`** — a valid proposal of a *different* action ends the
  activity and applies your action this tick (the interrupt path — a newly
  urgent need can take over). Proposing the *same* activity, or `Idle`,
  continues it **without resetting the clock**: re-proposing sleep every
  tick cannot extend it past `max`.
- **End conditions (engine's, regardless of proposals)** — the activity
  ends after the tick in which: `e ≥ max`; or `e ≥ min` and the governing
  need is 0 (per the data-model mapping table; for duets: either
  partner's); or `e ≥ min` and an eating kitty's bowl has no servings
  left. Your kitty decides fresh next tick. Expect scenes shorter than
  `max` to be *normal*, not exceptional: the built-ins' meow and purr
  gates fire post-minimum as interrupts, so a meal may pause for a meow
  and lawfully resume as a new activity — fragmentation is fine,
  starvation is not.
- **Counterpart gone** — a critter that expired or moved away, a groomed
  friend who left, a duet that broke: the activity ends immediately (even
  inside the minimum) and your proposal that tick resolves normally.

Relief applies on **every tick** of an activity at the full configured
per-action value (`eat_relief`, `play_relief`, …) — a 3-tick meal is three
meals' worth. `last_relief` is stamped each tick as usual, so 004's
tie-break sees multi-tick activities correctly.

## Availability change for duet proposals

- `Play { kitty }` and `Rest { with: Some }` (cuddle) now require the
  partner to be adjacent **and idle** (no ongoing activity). A kitty
  mid-meal or asleep cannot be conscripted into your duet; the proposal
  resolves to `Idle` as usual. On success, **both** kitties enter the
  shared activity with one clock — your partner is as committed as you
  are, and the duet ends for both together, always in the same tick:
  engine ends resolve the pair atomically, and a post-minimum interrupt
  by *either* partner clears both sides in that partner's apply slot.
  Your kitty can find itself freed mid-tick because its partner left —
  its own proposal then simply applies as normal.
- `Sleep { with }` (co-sleeping) and `Groom { target }` are unchanged
  (plain adjacency): the referenced kitty is *not* conscripted, keeps its
  own clock (or none), and may leave — which ends your activity.

## What built-ins do (reference)

The built-in profiles' selection is structurally unchanged: they already
propose `Idle` during sleep/rest (now normalized to continuation), and their
scored selection naturally re-proposes the same need until it's relieved
(continuation) or another need wins (the interrupt path). One quality
adjustment was needed (post-merge review): playmate viability and cuddle
seeking now skip kitties with an activity in progress — a busy friend is not
a conscriptable duet partner, and treating one as viable at distance 0 would
suppress the solo-play backstop for the length of its scene. Plugin authors
should copy that rule: check `activity`/`activity_clock` on a prospective
duet partner before proposing. External behaviors get the same enforcement
treatment either way — there is nothing to opt into and no way to opt out
(Article IV).

## Compatibility

- A missing `activity_clock` in a decision payload simply means "no
  activity in progress". (Pre-006 compatibility is otherwise a non-goal —
  clarified 2026-07-19.)
- All bounds come from `ctx.config.actions.durations.*` — read them, never
  hard-code (Article VI).
