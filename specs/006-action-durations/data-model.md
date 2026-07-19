# Data Model: Action Durations

**Date**: 2026-07-19 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Delta document relative to [001 data-model.md](../001-cloudkitty-mvp/data-model.md)
and [004 data-model.md](../004-fix-happiness-lockin/data-model.md). All types
keep serde derives; field names are canonical wire names.

## Activity (extended enum)

```
Activity = Idle
         | Resting  { with_friend: Option<KittyId> }            (existing)
         | Sleeping { in_sunbeam: bool,
                      with_friend: Option<KittyId> }            (existing)
         | Eating                                               (new)
         | Drinking                                             (new)
         | Playing  { target: Option<TargetRef> }               (new)
         | Grooming { target: Option<KittyId> }                 (new)
```

- Tagged as today (`"state"`, snake_case): new wire values `eating`,
  `drinking`, `playing`, `grooming`. Optional payload fields are
  serde-defaulted and omitted when absent — existing variants' wire shapes
  are byte-identical to 004.
- `Playing.target`: `None` = solo play; `Some(Element)` = critter play;
  `Some(Kitty)` = social play duet. `Grooming.target`: `None` = self-groom
  (bath); `Some(kitty)` = grooming a friend.

### Activity ↔ config-key ↔ need mapping (single source of truth)

| Activity state | `[actions.durations]` key | Relieved need (need-zero rule) | Per-tick effects (unchanged values) |
|---|---|---|---|
| `Eating` | `eat` (2/5) | `eat` | `eat_relief` to actor; 1 serving consumed |
| `Drinking` | `drink` (2/5) | `drink` | `drink_relief` to actor |
| `Playing` | `play` (2/5) | `play` (either partner if duet) | `play_relief` each partner / `solo_play_relief` solo |
| `Grooming` | `bath` (2/5) | actor's `bath` (self) / target's `bath` (friend) | self: `groom_relief` bath; friend: target `groom_relief` bath + actor `cuddle_relief` |
| `Sleeping` | `sleep` (2/8) | `sleep` | `sleep_relief` / `sleep_relief_sunbeam`; `cuddle_relief` both when co-sleeping |
| `Resting` | `cuddle` (2/8) | `cuddle` (either partner; solo rest: actor's `cuddle`) | duet: `cuddle_relief` both; solo: none (posture only) |

Solo rest relieves nothing today and continues to relieve nothing; its
need-zero rule therefore never fires and it ends by interrupt (FR-004) or
the `cuddle` max — documented, not accidental.

## Kitty (extended)

| Field | Type | New/Changed | Notes |
|-------|------|-------------|-------|
| `activity` | Activity | **extended** | four new variants above; engine-written only |
| `activity_clock` | Option\<ActivityClock\> | **new** | duration bookkeeping; engine-maintained; serde-defaulted `None`; omitted from JSON when absent |

```
ActivityClock { started: u64, applied: u64 }
```

- `started`: tick the activity was first applied. `applied`: last tick the
  activity was **serviced** (started, continued, or pause-continued) —
  stamped on *every* tick the activity survives, whether or not effects
  landed that tick. Effects application is decided separately: the duet
  double-relief guard and the empty-bowl pause both skip *effects*, never
  the stamp. (Analyze finding C1: if a paused activity stopped stamping, no
  end rule could ever reach it — a kitty could be locked eating an empty
  bowl forever, the exact lock-in shape 004 eliminated.)
- **Elapsed convention (used everywhere)**: `elapsed = tick − started + 1`,
  evaluated during the tick's end-resolution; an activity that ended with
  `elapsed = n` applied relief exactly `n` times. "Minimum met" ⇔
  `elapsed ≥ min`; cap fires when `elapsed ≥ max`.
- **No legacy support** (clarified 2026-07-19): pre-006 snapshots are not
  healed. Non-Idle `activity` with `activity_clock: None` (or a one-sided
  duet) is a strict load-validation failure — refused with the standard
  clear error suggesting a fresh world. Frozen test fixtures that predate
  006 are migrated mechanically (stamp a clock on any non-Idle activity)
  as test-asset maintenance, not engine behavior.

## Engine flow (phase 2 of the unchanged four-phase tick)

Per kitty, in stable id order (existing loop, two new steps marked ★):

1. ★ **Prune dead activity**: counterpart gone → `activity = Idle`,
   `clock = None` (FR-010; min notwithstanding). "Gone" = element expired
   or no longer adjacent; groom target no longer adjacent; duet partner no
   longer in the reciprocal activity.
2. `validate(proposal)` — unchanged rules, plus availability split:
   `Rest { with: Some }` and `Play { Kitty }` require
   **conscriptable** friend (adjacent ∧ partner `activity == Idle`);
   `Sleep { with }` / `Groom { target }` keep plain adjacency.
3. ★ **Duration enforcement** (FR-003/004): ongoing activity ∧
   `elapsed < min` ∧ validated ≠ continuation → replace with continuation
   action. Ongoing ∧ validated is same-activity or `Idle` → normalize to
   continuation (clock untouched — no laundering). Ongoing ∧
   `elapsed ≥ min` ∧ validated is a different action → end activity, apply
   validated normally — **and if the ended activity was a duet, clear the
   partner's side in this same slot** (FR-009 atomicity: a partner whose
   slot already ran keeps this tick's relief; one that has not yet run
   finds itself free and decides normally in its own slot; no one-sided
   duet state ever reaches the phase-4 invariant check).
4. Record `last_action` = the action actually applied (continuation action
   on continuation ticks — keeps the unmodified viewer's "doing" line
   truthful through a meal).
5. `apply(action)` — starting an activity sets `activity` +
   `clock = { started: tick, applied: tick }` (duets: both partners,
   reciprocal activities, same clock values) and applies tick-1 effects.
   Continuation **always** stamps `applied = tick`; effects land only when
   both (a) not already applied this tick (`clock.applied < tick` on
   entry — the duet double-relief guard) and (b) resources permit (the
   empty-bowl pause skips relief and consumption but still stamps).
6. `update_pursuit(...)` — unchanged (004).

After the loop, before the environment phase:

7. ★ **End-resolution pass** (id order; duet pairs resolved once,
   atomically): for **each kitty with an ongoing activity** (clock present
   — every surviving activity was serviced this tick by construction), end
   (`activity = Idle`, `clock = None`) when
   `elapsed ≥ max`, or `elapsed ≥ min ∧ governing need = 0`
   (duet: either partner's; solo rest has no governing need), or
   `elapsed ≥ min ∧ Eating ∧ no adjacent chow with servings > 0`.

Phases 3 (environment) and 4 (needs/invariants) are untouched.

## Config (extended)

| Section.key | Default | Validation |
|-------------|---------|------------|
| `actions.durations.eat` | { min 2, max 5 } | 1 ≤ min ≤ max |
| `actions.durations.drink` | { min 2, max 5 } | 1 ≤ min ≤ max |
| `actions.durations.play` | { min 2, max 5 } | 1 ≤ min ≤ max |
| `actions.durations.bath` | { min 2, max 5 } | 1 ≤ min ≤ max |
| `actions.durations.sleep` | { min 2, max 8 } | 1 ≤ min ≤ max |
| `actions.durations.cuddle` | { min 2, max 8 } | 1 ≤ min ≤ max |

- Violations report field, value, allowed range (established style).
- `min = max = 1` everywhere lawfully restores pre-006 instant actions.
- No new relief keys (clarified 2026-07-19: full existing relief per tick).
- Config fingerprint (width/height/seed/kitty ids) unchanged — a design
  hygiene choice; snapshot compatibility itself is a non-goal (2026-07-19).

## Invariants (additions to `invariants::check`)

- **Strict biconditional**: `activity_clock` present ⟺ `activity ≠ Idle`;
  when present, `started ≤ applied ≤ tick`. No legacy tolerance — a
  clockless in-progress activity is refused at load (FR-013).
- Clock present after a completed tick ⇒ `elapsed ≤ max` for the mapped
  activity (the end-resolution pass ran).
- **Strict duet symmetry**: `Playing { target: Kitty(b) }` ⇒ kitty `b` is
  `Playing { target: Kitty(me) }` with an identical clock, and likewise
  for cuddle (`Resting { with_friend }` reciprocal). Holds at every
  invariant check — interrupts clear both sides in-slot (step 3), so no
  one-sided state can survive to phase 4.
- Existing invariants unchanged; property suite runs fresh worlds and
  round-trips mid-activity 006 snapshots.

## Wire / persistence summary

- **World (persistence)**: `Kitty.activity_clock` added (omitted when
  `None`); `Activity` gains four variants. Pre-006 snapshots are not
  supported (strict load validation, clean refusal); 006 snapshots resumed
  mid-activity continue to the identical outcome (`applied` records
  whether the saved tick already serviced the activity).
- **WorldSnapshot (wire + decisions)**: same structs — `activity_clock`
  and new `activity.state` values appear in `/world` and WS frames
  automatically; `last_action` repeats the activity's action on
  continuation ticks. See
  [contracts/http-api-delta.md](./contracts/http-api-delta.md).
- **DecisionContext**: behaviors read `ctx.me.activity` +
  `ctx.me.activity_clock` (no new writes; Article IV). See
  [contracts/behavior-delta.md](./contracts/behavior-delta.md).
