# Research: Action Durations

**Date**: 2026-07-19 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

No NEEDS CLARIFICATION markers remained after `/speckit-clarify` (full relief
per tick; shared-clock duets). The decisions below resolve the design
unknowns the plan's Technical Context implies — each grounded in the code as
it stands on `main` (post-004).

## R1 — Where activity state lives: extend `Activity`, add one clock field

**Decision**: Extend the existing `Activity` enum (today `Idle` / `Resting` /
`Sleeping`) with `Eating`, `Drinking`, `Playing { target: Option<TargetRef> }`,
and `Grooming { target: Option<KittyId> }`. Add one new engine-maintained
field on `Kitty`:

```rust
pub struct ActivityClock {
    /// Tick the activity was applied for the first time.
    pub started: u64,
    /// Last tick this activity was serviced (started, continued, or
    /// pause-continued) -- stamped every surviving tick regardless of
    /// whether effects landed. Guards duet double-application and makes
    /// save/resume exact.
    pub applied: u64,
}
// Kitty: #[serde(default, skip_serializing_if = "Option::is_none")]
// pub activity_clock: Option<ActivityClock>,
```

**Rationale**: `Activity` is already the engine's "what is this kitty doing
across ticks" concept, already serialized, already continued by
`continue_current_activity`, and already rendered by viewers via
`activity.state`. A parallel "ongoing action" struct would create two
sources of truth for sleeping/resting. One optional clock field beside it
keeps the wire additive (new kitty key, omitted when absent) and the
elapsed/min/max math in one place. `applied` means *serviced this tick*,
not *effects landed this tick*: duet effects are applied once per tick by
whichever partner's apply slot comes first (the other slot sees
`applied == tick` on entry and skips effects — see R5), the empty-bowl
pause skips effects but still stamps, and a resumed snapshot knows whether
the saved tick already serviced the activity. The stamp-always rule is
load-bearing (analyze C1): end rules key off the clock, so an activity
that stopped stamping would become unreachable by every end condition —
a kitty locked eating an empty bowl forever.

**Alternatives considered**: (a) `OngoingActivity` struct replacing
`Activity` — bigger wire break, migration for sleeping/resting; (b) clock
embedded per enum variant (`Eating { started }`) — repeats two fields
across six variants and changes the existing `Sleeping`/`Resting` wire
shapes, breaking pre-006 loads; rejected.

## R2 — Enforcement points: wrap the existing apply loop, don't restructure it

**Decision**: Phase 2 (apply, stable kitty-id order) gains two engine steps
around the existing per-kitty `validate → record last_action → apply →
update_pursuit` sequence, plus one pass after the loop:

1. **Pre-validate prune**: if the kitty's activity's counterpart is gone
   (element expired/moved out of adjacency; groomed friend walked away;
   duet partner no longer in the reciprocal activity), clear activity +
   clock *before* validation — the kitty's proposal then resolves normally.
   This is the "ends immediately, minimum notwithstanding" path (FR-010).
2. **Duration enforcement** (after validate, before recording
   `last_action`): with an ongoing activity at `elapsed < min`, any
   validated action that is not a continuation of that activity is replaced
   by the continuation action (FR-003). At `elapsed ≥ min`, a different
   validated action ends the activity (clear activity + clock — **both
   sides if it was a duet**: FR-009 atomicity, analyze I1; a partner whose
   slot already ran keeps this tick's relief, one that has not yet run
   decides freshly in its own slot) and applies
   normally (FR-004). A validated proposal of the *same* activity, or
   `Idle`, is normalized to the continuation action without touching
   `started` (FR-004, no clock laundering). `last_action` records what was
   actually applied — the continuation action on continuation ticks — so
   the record stays honest and the unmodified viewer keeps narrating
   correctly ("eating 🍥" every tick of the meal).
3. **End-resolution pass** (after all kitties have applied, before the
   environment phase — the slot analogous to `update_pursuit`, run in
   kitty-id order): for each kitty **with an ongoing activity** (clock
   present — never gated on `applied == tick`, so a paused activity stays
   reachable by every end rule; analyze C1),
   compute `elapsed = tick − started + 1` and end the activity (activity →
   `Idle`, clock → `None`) when `elapsed ≥ max`, or when `elapsed ≥ min`
   and the governing need is 0, or when `elapsed ≥ min` and an `Eating`
   activity has no adjacent chow with servings left (FR-005/006/008). Duet
   pairs are resolved once, atomically for both (R5).

**Rationale**: This is exactly the 004 pattern (`update_pursuit` as
engine bookkeeping inside phase 2), keeps the constitution's four-phase
order intact, and needs no changes to `gather_decisions` or any behavior.
Ending in a post-apply pass (not inside `apply`) is required because
need-zero can only be judged after the tick's relief has landed, and duets
must end for both partners even though they apply in different slots.

**Alternatives considered**: ending inside each kitty's own apply slot —
breaks duet atomicity (partner A ends, partner B's slot still continues);
ending in the needs phase — moves activity mutation out of the apply phase
and would let the environment phase see half-ended duets; rejected.

## R3 — Counting convention: inclusive elapsed, end-on-the-tick

**Decision**: An activity applied first on tick T has `elapsed = tick − T + 1`
(the applying tick counts as tick 1 of the activity). "Minimum met" ⇔
`elapsed ≥ min` evaluated at end-resolution of the current tick; an activity
ending at `elapsed = n` received exactly `n` applications of relief. With
`min = 2`: relief lands at least twice; with `max = 5`: at most 5 times, and
the activity is gone before tick T+5's decisions.

**Rationale**: "min 2 ticks" must mean "the viewer can see it for 2 ticks
and it relieved twice" — the inclusive count delivers both with no
off-by-one debate. All tests and invariants use this single definition
(written once in `data-model.md`, referenced everywhere).

## R4 — Ending ≠ waking into idleness: re-decide next tick, no dead tick

**Decision**: End-resolution sets `Activity::Idle` at the end of tick T; on
tick T+1 the kitty decides fresh with full selection. There is no forced
idle action and no cooldown on re-entering the same activity (new clock).

**Rationale**: With full per-tick relief, re-entry converges fast: eat/drink
(relief 40) zero a full need in 3 ticks, groom (30) in 4, play (25) in 4,
cuddle (20) in 5 — all inside their maxes, so the need-zero rule ends
almost every activity and re-entry is rare. Sleep is the exception
(relief 5/8 per tick; a full sleep need takes 13–20 relieving ticks), so
sleep hits its max-8 review point and lawfully re-enters with no visible
gap — the cap acts as a "still the right thing?" checkpoint, satisfying
the anti-stuck purpose without a cosmetic forced wake. A cooldown was
rejected: it would fight Article I (delaying relief) to solve a problem
convergence already solves.

## R5 — Duets: conscription at start, once-per-tick effects, atomic end

**Decision**: Availability splits in `World`:

- `is_available_friend` (adjacency, unchanged) keeps governing the
  *non-conscripting* partner references: `Sleep { with }` (co-sleeping,
  independent clocks) and `Groom { target }` (target stays free).
- New `is_conscriptable_friend(me, friend)`: adjacency **and**
  `friend.activity == Idle`. Governs validation of `Rest { with: Some }`
  (cuddle) and `Play { Kitty }` (social play) — a kitty mid-activity cannot
  be conscripted out of it (its own minimum would be violated), and a
  sleeping cat is not yanked awake to cuddle.

Applying a cuddle/social-play sets **both** kitties' activities (reciprocal:
`Resting { with_friend: Some(other) }` both sides / `Playing { target:
Kitty(other) }` both sides) and one shared clock value (`started = applied =
tick` on both). Per-tick effects for the pair are applied exactly once per
tick: whichever partner's apply slot runs first applies both partners'
relief and stamps both clocks' `applied = tick`; the second partner's slot
(or an enforced continuation) sees `applied == tick` on entry, skips
effects, and re-stamps its own clock (a no-op in effect terms only —
`applied` always advances; analyze C1). Ends are atomic for both partners
whichever way they arrive: engine ends (end-resolution treats the pair as
one unit — either partner's governing need at 0 after the shared min, or
the shared max, identical `started` making the max tick identical by
construction) *and* behavior interrupts (a post-min different action by
either partner clears both sides in the interrupter's slot; analyze I1 —
no one-sided duet ever survives to the invariant check).

**Migration note**: none — backwards compatibility is a non-goal
(clarified 2026-07-19). Today's one-sided `Rest { with }` state shape
ceases to exist; a pre-006 snapshot carrying one fails strict load
validation like any other legacy shape, and the duet-symmetry invariant
holds unconditionally.

**Rationale**: The clarification chose shared-clock duets; conscription
at *start* (partner must be Idle) is what makes the shared minimum lawful
for a cat that didn't propose it — it only ever costs a kitty that was
doing nothing. Once-per-tick effects via the `applied` stamp is the
smallest guard against double relief when both partners' slots run in the
same tick (including the both-proposed-play-at-each-other case, where the
second proposal normalizes to continuation).

## R6 — Sleep and rest join the framework; gates in behaviors become redundant, not wrong

**Decision**: `Sleeping`/`Resting` get clocks like everything else:
min 2 / max 8 (cuddle bounds cover solo rest too — same `Resting` state).
The engine's need-zero rule (sleep need 0 after min) and cap-8 replace
"sleep until the behavior decides to wake" as the *guarantee*; the
built-ins' existing wake logic (propose something else when sleep pressure
is low) keeps working as the *usual* path and needs no edits — a behavior
switching post-min is FR-004's interrupt, and one that never wakes is now
bounded by the cap.

**Rationale**: FR-011 requires one framework, no special cases. Leaving
behavior gates untouched honors the spec's "no behavior-selection changes"
boundary; the engine bounds are a floor of safety under whatever behaviors
do (Article IV posture).

## R7 — Config shape: `[actions.durations]` with per-activity bounds

**Decision**: `ActionsConfig`… stays; a nested table is added:

```toml
[actions.durations]
eat    = { min = 2, max = 5 }
drink  = { min = 2, max = 5 }
play   = { min = 2, max = 5 }
bath   = { min = 2, max = 5 }
sleep  = { min = 2, max = 8 }
cuddle = { min = 2, max = 8 }   # also governs solo rest (same Resting state)
```

Rust-side: `DurationsConfig { eat, drink, play, bath, sleep, cuddle:
DurationBounds }`, `DurationBounds { min: u64, max: u64 }`, all
serde-defaulted (an omitted `[actions.durations]` section simply yields
the documented defaults; defaults above). Validation per
activity: `1 ≤ min ≤ max`, error naming field, value, and allowed range in
the established style. Keys are named for the *need-facing activity*
(bath, cuddle), matching how the spec and the owner speak about them; the
mapping to engine states (`bath → Grooming`, `cuddle → Resting`) is
documented in data-model.md. Fingerprint (width/height/seed/kitty ids)
untouched — durations are tunables (design hygiene; compatibility itself
is a non-goal per the 2026-07-19 clarification).

**Alternatives considered**: flat keys (`eat_min_ticks = 2`, …12 of them)
— noisier toml and validation; a `BTreeMap<String, DurationBounds>` —
loses compile-time completeness (a typo'd key silently defaults); rejected.

## R8 — Wire strategy: additive, and the unmodified viewer stays correct

**Decision** (details in [contracts/http-api-delta.md](./contracts/http-api-delta.md)):

- `activity.state` gains values `eating`, `drinking`, `playing`,
  `grooming` (existing tag scheme; `playing.target` is a *nested*
  TargetRef object -- never flattened, per the 004 malformed-play lesson --
  and `grooming.target` a plain kitty id, both omitted when absent).
- Kitty gains `activity_clock: { started, applied }`, omitted when absent.
- `last_action` now repeats the activity's action on every continuation
  tick (this is what keeps the *unmodified* viewer's "doing" line correct
  through a multi-tick meal — `doingFor` switches on `last_action`, so it
  renders "eating 🍥" for each tick of the meal with zero client changes;
  SC-007).
- `/config` echo gains `actions.durations.*` automatically.

**Rationale**: FR-014 additive-only. The `last_action`-repeats decision was
checked against `client/app.js` as it exists: `doingFor` never consults the
new activity states (it reads `last_action` and, for idle, `activityText`
over sleeping/resting only), and `faceFor` defaults unknown states to '🐱'
— so an old client renders new worlds correctly by construction.

## R9 — Serving economics: 1 serving per eating tick is safe

**Decision**: Keep the spec rule (one serving per eating tick; emptied bowl
ends the meal after min, or pauses relief/consumption below min). No config
change to chow servings or spawn minimums in this feature.

**Rationale**: Meals now consume up to 3 servings (need-zero at relief 40
ends a full-need meal in 3 ticks) instead of 1 — but they also happen ~3×
less often (the need is actually zeroed instead of shaved by 40), so
steady-state chow demand is roughly unchanged. The Article I safeguard
spawner remains the backstop for transient shortages, and the welfare
long-run will surface any miscalibration as a failing bound before merge.

## R10 — Test strategy and re-baselining

**Decision**: New `activity_durations.rs` integration suite instruments a
20k-tick default-config run, recording every activity instance (kitty,
kind, start, end, per-tick relief) from served snapshots, then asserts
SC-001 (min/max adherence, zero violations excepting documented
counterpart-loss ends), SC-002 (need-zero promptness), SC-004 (every kind
observed ≥ 2 ticks), plus a 5k-tick same-seed determinism replay including
activity timelines (SC-005) and a save/resume-mid-activity equivalence run
(SC-006). `invariants_proptest.rs` gains two cases: mid-activity 006
worlds round-trip (serialize → load → identical continuation), and a
pre-006 shape (in-progress `Sleeping`, no `activity_clock`) is *refused*
by strict load validation with the standard clear error — no heal paths
(clarified 2026-07-19). Welfare bounds in `welfare_longrun.rs` are
re-measured on the new engine and tightened to the observed envelope,
with a hard floor at the 004 bounds (SC-003: never looser).
`stuck_state_regression.rs` fixtures are migrated mechanically (stamp an
`activity_clock` on any non-Idle activity so they satisfy strict
validation — test-asset maintenance, semantics unchanged) and must still
pass (recovery is expected to speed up, not slow down).

**Rationale**: SC-001..007 are all deterministic and cheap to check from
recorded snapshots; encoding them as permanent CI gates follows the 004
precedent (welfare bounds as regression armor). Re-baselining direction is
one-way by construction: assert `new_bound ≥ 004_bound` in the test
constants themselves, so a future regression cannot hide behind a loosened
number.
