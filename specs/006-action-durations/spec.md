# Feature Specification: Action Durations

**Feature Branch**: `006-action-durations`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "Give kitty actions a minimum and maximum duration in ticks, engine-enforced. Three purposes: (1) actions become visible to viewers — a minimum of 2 ticks for eat, drink, sleep, cuddle, play, bath gives the action time to be seen (and gives the upcoming 005 graphics refresh time to play its animations); (2) a maximum prevents kitties from getting stuck in one action too long; (3) overall happiness increases, because each tick of an ongoing action reduces needs again. Defaults: min 2 for all; max 5 for eat, drink, play, bath; max 8 for sleep, cuddle. When a need reaches 0, the current action stops and changes (assuming the minimum tick count has been met)."

## Clarifications

### Session 2026-07-20

- Q: Are the shipped duration defaults right once the animations exist? →
  A: Sleep and cuddle minimums raised 2 → 3 ticks (owner decision): with
  the 005 graphics live, a nap or cuddle worth watching should hold on
  screen for at least three ticks. All other defaults unchanged; the
  configurable bounds and validation rules are untouched.

### Session 2026-07-19

- Q: When an activity runs for multiple ticks, how much relief should each
  tick apply? → A: Full relief every tick — each tick applies the existing
  per-action relief value (no rescaling, no new relief config keys); a
  3-tick meal delivers three times today's meal.
- Q: When a kitty starts social play with another kitty, what happens to
  the partner? → A: Shared activity, shared clock — both kitties enter the
  play activity together (the partner too, though it did not propose it),
  locked by the shared minimum, relieved every tick, ending together; the
  same duet mechanics as cuddling.
- Q: Must pre-006 snapshots keep loading? → A: No — backwards compatibility
  is not required at this stage (owner decision, 2026-07-19). No heal paths;
  the engine may cleanly refuse an old snapshot and suggest a fresh world.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every Action Lasts Long Enough to See (Priority: P1)

Today a kitty eats, drinks, plays, or grooms in a single instant: the action
is applied and finished within one tick, so a viewer watching the world sees
at most one frame of it — and the upcoming graphics refresh would have no
time to play a chomp or a pounce. After this change, every need-relieving
action is an ongoing activity with a minimum duration: a meal is a small
scene, not a flicker. And because each tick of the activity applies the
action's relief again, a two-tick meal genuinely feeds a cat more than
today's instant bite — kitties get happier just by living at a watchable
pace.

**Why this priority**: This is the heart of all three stated purposes —
visibility, welfare, and the foundation the other stories refine. Without
minimum durations there is nothing to cap, end early, or observe.

**Independent Test**: Run a long deterministic world and inspect the applied
action history: every eat, drink, play, bath (grooming), cuddle, and sleep
lasts at least its configured minimum number of consecutive ticks, and the
need it relieves drops on every one of those ticks. Welfare metrics
(mean happiness, time in low happiness) improve against the pre-change
baseline.

**Acceptance Scenarios**:

1. **Given** a kitty adjacent to chow that starts eating, **When** the world
   advances, **Then** the kitty remains eating for at least the configured
   minimum (default 2 ticks), its eat need dropping by the configured relief
   on each tick of the meal.
2. **Given** any of the six need-relieving activities (eat, drink, sleep,
   play — social or solo, cuddle, bath), **When** it begins, **Then** it
   continues for at least its configured minimum even if the kitty's
   behavior proposes something else during that window — the engine, not the
   behavior, guarantees the floor (Article IV: behaviors propose, the engine
   is the law).
3. **Given** the same world seed and configuration, **When** the run is
   repeated, **Then** the same activities start and end on the same ticks
   (Article V determinism).
4. **Given** a kitty whose behavior proposes the same activity again while
   already performing it, **When** the proposal is applied, **Then** it
   continues the existing activity — it never restarts the duration clock (a
   kitty cannot launder the maximum by re-proposing sleep every tick).

---

### User Story 2 - Actions End When the Job Is Done (Priority: P2)

A kitty stops eating when it is full. When the need an activity relieves
reaches 0, the activity ends — once its minimum duration has been met — and
the kitty chooses something new on the next tick. Time stops being wasted
polishing a need that is already at zero, which means more ticks spent on
whatever actually wants attention, which means happier cats. Resources agree
with needs: an emptied bowl ends a meal the same way a full belly does.

**Why this priority**: The efficiency half of the welfare purpose. Minimum
durations alone would occasionally overshoot (relieving a need already at
0); this story returns those ticks to the kitty.

**Independent Test**: In a long deterministic run, no activity continues
past its minimum while the need it relieves sits at 0; every such activity
ends on the tick the condition is first true (minimum met and need at 0, or
bowl empty). A kitty observed finishing a meal moves on to a different
concern the following tick.

**Acceptance Scenarios**:

1. **Given** a kitty mid-meal whose eat need reaches 0 on tick N with the
   minimum already met, **When** tick N completes, **Then** the meal is over
   and on tick N+1 the kitty's behavior selects freely among its needs.
2. **Given** a kitty whose need reaches 0 *before* the minimum is met,
   **When** the world advances, **Then** the activity continues harmlessly to
   its minimum (relief clamps at 0 — a content cat licking the bowl) and
   ends there.
3. **Given** a bowl that runs out of servings mid-meal after the minimum is
   met, **When** the serving is consumed, **Then** the meal ends; **Given**
   it runs out before the minimum, **Then** the kitty keeps the eating pose
   until the minimum (no further relief, no further consumption) and the
   meal ends at the minimum.
4. **Given** an activity that ended at need 0, **When** the next tick's
   decisions run, **Then** the kitty is free to start any lawful action —
   nothing about the ended activity lingers.

---

### User Story 3 - No Action Overstays (Priority: P3)

A kitty can no longer be stuck in one activity indefinitely. Every activity
has a configured maximum duration, enforced unconditionally by the engine:
at the cap, the activity ends regardless of what the kitty's behavior
proposes, and the kitty re-decides from scratch next tick. Sleep and rest —
today's only multi-tick activities, which persist on open-ended behavior
whim — are brought under the same framework rather than living beside it as
special cases.

**Why this priority**: The anti-stuck purpose. It matters most as a
guarantee (a backstop against future behavior bugs of the kind the 004
lock-in fix addressed) and less as a daily occurrence, so it follows the
stories that change everyday life.

**Independent Test**: In a long deterministic run, zero activity instances
exceed their configured maximum. A kitty whose sleep need is still high when
the sleep cap hits wakes, re-decides, and may lawfully choose to sleep again
— with a fresh clock — converging because every sleeping tick drains the
need.

**Acceptance Scenarios**:

1. **Given** a kitty that has been sleeping for the configured maximum
   (default 8 ticks), **When** the cap is reached, **Then** the engine ends
   the sleep even if the behavior would happily continue it.
2. **Given** an activity between its minimum and maximum, **When** the
   kitty's behavior proposes a different action through its normal
   selection, **Then** the switch is honored — a newly urgent need can
   interrupt (the lock of the minimum is the only lock, and it is short).
3. **Given** the configured bounds, **When** configuration is validated at
   startup, **Then** every activity's bounds satisfy 1 ≤ minimum ≤ maximum,
   and a violation is rejected with a clear error naming the field, value,
   and allowed range.
4. **Given** a kitty at an activity's cap with the need still high, **When**
   it re-enters the same activity on a later tick, **Then** that is a new
   activity with a new clock — permitted, bounded, and convergent (each
   tick of the activity relieves the need, so repeats shrink).

---

### User Story 4 - Shared Activities Share Fairly (Priority: P4)

Cuddles and social play are duets. When two kitties cuddle or play together,
both receive relief on every tick of the shared activity, their clocks run
together from the same starting tick, and the activity ends for both at the
same moment — when either partner's relevant need reaches 0 (after the
minimum) or the maximum arrives. Duets with the world's smaller creatures
are looser: a critter that scurries out of reach or expires mid-play simply
ends the game where it stands, and a kitty being groomed (who is not
performing an activity of its own) may wander off, ending the grooming.

**Why this priority**: Correctness for the social half of the activity set.
It refines the rules the earlier stories establish rather than introducing
new value of its own.

**Independent Test**: In a deterministic run containing cuddles and social
play, verify: both partners' needs drop on every shared tick; both
activities start and end on identical ticks; a play-with-critter ends the
tick its critter vanishes or breaks adjacency; a groom ends the tick its
target walks away — all without any partner ever being trapped by the
other's minimum beyond their shared start.

**Acceptance Scenarios**:

1. **Given** two kitties starting a cuddle on the same tick, **When** the
   activity runs, **Then** both receive cuddle relief every tick and the
   cuddle ends for both on the same tick (either's need at 0 after the
   shared minimum, or the maximum).
2. **Given** a kitty playing with a critter, **When** the critter expires or
   moves out of adjacency, **Then** the play ends immediately — minimum
   notwithstanding — with relief already granted retained (the world moved
   on; no relief is invented for an absent playmate).
3. **Given** a kitty grooming a friend, **When** the friend (who remains
   free to act) moves away, **Then** the grooming ends immediately; while
   adjacency holds, the groomer's activity honors its normal min/max and
   per-tick effects (friend's bath relief, groomer's cuddle relief).
4. **Given** two kitties napping together, **When** one wakes (its own
   need-zero or cap), **Then** the other may lawfully sleep on — co-sleeping
   is companionship, not a shared clock, and each sleeper wakes on its own
   terms.

---

### Edge Cases

- **Same-activity proposal mid-activity**: always continuation, never a
  clock reset — the maximum cannot be laundered (echoes the 004 lesson that
  switching targets must not launder staleness).
- **Need at 0 before the minimum**: activity continues to the minimum with
  relief clamping at 0; harmless by construction.
- **Bowl empties below the minimum**: eating pose continues (no relief, no
  consumption) until the minimum; ends there. Above the minimum, emptiness
  ends the meal at once.
- **Partner or target gone**: any activity whose counterpart ceases to exist
  or leaves adjacency (critter expiry/movement, groom-target wandering off)
  ends immediately, minimum notwithstanding. Kitty cuddle/play partners
  cannot vanish (Article II) and do not move mid-activity, so the joint
  clock is safe for them.
- **Sunbeam expires mid-sleep**: sleep continues; only the sunbeam bonus is
  lost from that tick on (unchanged from today).
- **Urgent need during the minimum**: locked out for at most the minimum
  (default 2 ticks) — bounded and small; the safeguard spawner and distress
  bookkeeping are unaffected, so Article I timing guarantees hold with a
  worst-case delay of the minimum.
- **Maximum reached, need still high**: lawful immediate re-entry with a
  fresh clock; convergent because per-tick relief shrinks the need every
  pass (a full sleep now relieves up to 8× the old single application).
- **Mid-activity snapshot**: a world saved mid-meal resumes and finishes the
  meal on the same tick it would have without the save/load (duration
  bookkeeping is part of deterministic, serialized state).
- **Pre-006 snapshot**: not supported. One carrying an in-progress activity
  without a clock fails strict load validation with the standard clear
  error ("start a fresh world"); nothing heals, nothing guesses.
- **Config bounds abuse**: min of 0, max below min, or non-numeric values
  are startup validation errors naming field, value, and range; extreme but
  valid values (min = max = 1) restore today's instant actions lawfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The six need-relieving activities — eat, drink, sleep, play
  (social and solo), cuddle (resting with a friend), and bath (grooming) —
  MUST each be an ongoing multi-tick activity with a configured minimum and
  maximum duration in ticks.
- **FR-002**: Duration bounds MUST be configurable per activity with these
  defaults: minimum 2 for eat, drink, play, and bath; minimum 3 for sleep
  and cuddle (raised from 2 by owner tuning on 2026-07-20, once the 005
  animations made durations visible); maximum 5 for eat, drink, play, and
  bath; maximum 8 for sleep and cuddle. Startup validation MUST enforce
  1 ≤ minimum ≤ maximum per activity, rejecting violations with an error
  naming the field, the offending value, and the allowed range (no magic
  numbers anywhere — Article VI).
- **FR-003**: The engine MUST enforce the minimum: from the tick an activity
  is applied until its minimum is met, the activity continues regardless of
  what the kitty's behavior proposes (proposals during the window are
  disregarded in favor of continuation — Article IV: the engine is the law).
- **FR-004**: Between minimum and maximum, a behavior's proposal of a
  different lawful action MUST end the activity and take effect through
  normal validation; a proposal of the same activity MUST continue it
  without resetting its clock.
- **FR-005**: The engine MUST end any activity that reaches its configured
  maximum, unconditionally, on that tick; the kitty decides freshly on the
  next tick.
- **FR-006**: An activity MUST end at the first tick where its minimum has
  been met AND its governing need is 0 (early termination); below the
  minimum, need-zero does not end it and relief clamps harmlessly. The
  governing need per activity is the mapping table in
  [data-model.md](./data-model.md) — notably: grooming a friend is governed
  by the *target's* bath need, and solo rest (which relieves nothing) has no
  governing need and ends only by interrupt or its maximum.
- **FR-007**: Every tick of an ongoing activity MUST apply that activity's
  full configured relief — the same per-application value used today, not a
  rescaled fraction — through the existing single relief choke point, so
  relief timestamps (`last_relief`) and all welfare bookkeeping remain
  consistent with 004's selection mechanics. No new relief config keys are
  introduced.
- **FR-008**: Eating MUST consume one serving per eating tick. A bowl
  emptied after the minimum ends the meal that tick; before the minimum,
  the activity continues to the minimum without further relief or
  consumption.
- **FR-009**: Kitty–kitty cuddle and social play MUST relieve both partners
  every tick, share one synchronized clock from their common starting tick,
  and end for both partners simultaneously at the earliest of: either
  partner's relevant need reaching 0 (after the shared minimum), or the
  maximum. The partner enters the shared activity even though it did not
  propose it — the engine records the duet for both (clarified 2026-07-19).
  A post-minimum interrupt (FR-004) by *either* partner likewise ends the
  duet for **both in the same tick** — the engine clears both sides in the
  interrupter's apply slot, so no one-sided duet state ever survives a tick
  (a partner whose slot already ran keeps that tick's relief; one that has
  not yet run decides freshly in its own slot). Co-sleeping kitties keep
  independent clocks and wake independently.
- **FR-010**: Any activity whose partner or target ceases to exist or
  leaves adjacency (critter expiry or movement; a groomed friend walking
  away) MUST end immediately, minimum notwithstanding, retaining relief
  already granted and inventing none for the absent counterpart.
- **FR-011**: Sleep and rest MUST be governed by this same framework —
  minimum, maximum, need-zero termination, continuation semantics —
  replacing their current open-ended behavior-driven persistence; the
  sunbeam sleep bonus and cuddle-while-resting effects are preserved
  per-tick.
- **FR-012**: Activity duration state MUST be part of the deterministic,
  serialized world state: a snapshot saved mid-activity resumes to the same
  outcome as an uninterrupted run, and same seed + config + ticks yields
  identical activity timelines (Article V).
- **FR-013**: Backwards compatibility is explicitly NOT required (clarified
  2026-07-19): there are no heal paths and no legacy tolerance. A pre-006
  snapshot (e.g., one carrying an in-progress activity without duration
  bookkeeping) MAY be refused at load with the standard clear error
  suggesting a fresh world — refused cleanly, never undefined behavior.
  Invariants are strict from the start (clock present ⟺ activity in
  progress).
- **FR-014**: API changes MUST be additive only: the served activity state
  may gain progress information (e.g., the tick the activity started), no
  existing field changes meaning or shape, and current consumers — including
  the unmodified viewer — keep working.
- **FR-015**: Engine invariants MUST be extended to guard the new
  guarantees (an activity's elapsed duration never exceeds its configured
  maximum; duration bookkeeping is absent whenever no activity is in
  progress; a recorded start never lies in the future), and the long-run
  welfare suite MUST be re-baselined so CI enforces welfare at least as
  good as the 004 baselines.

### Key Entities

- **Activity duration bookkeeping**: engine-maintained record of when the
  current activity began (and thereby how long it has run), carried per
  kitty as part of world state; readable by behaviors and viewers, writable
  only by the engine.
- **Duration policy**: the per-activity configured bounds (minimum,
  maximum) with documented defaults; part of configuration, subject to
  startup validation.
- **Ongoing activity**: the existing per-kitty activity concept (today only
  sleeping/resting), extended to cover all six need-relieving activities
  uniformly, including its partner linkage for duets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a 20,000-tick deterministic run with default configuration,
  100% of activity instances last at least their configured minimum and at
  most their configured maximum — zero violations in either direction
  (except the documented immediate-end cases: vanished or departed
  counterpart).
- **SC-002**: In the same run, zero activity instances continue past the
  first tick at which their minimum is met and their need is 0; each ends
  exactly there.
- **SC-003**: Welfare with default configuration is at least as good as the
  004 baselines on every guarded metric — per-kitty mean happiness, share
  of ticks below happiness 45, and longest consecutive low-happiness
  episode — and the improvement expected from per-tick relief is captured
  by re-baselined CI bounds (never loosened below the 004 guarantees).
- **SC-004**: An observer watching the live viewer sees every eat, drink,
  play, bath, cuddle, and sleep for at least 2 consecutive ticks at default
  configuration — no single-frame actions remain.
- **SC-005**: Two runs with the same seed, configuration, and tick count
  produce identical worlds, including identical activity start/end ticks
  (verified over at least 5,000 ticks).
- **SC-006**: A snapshot saved mid-activity and resumed reaches the same
  world state at every subsequent tick as the uninterrupted run; a snapshot
  that fails strict load validation (e.g., pre-006 shape mid-activity) is
  refused with a clear error, never loaded incorrectly.
- **SC-007**: The existing viewer, unmodified, renders a 006 world with no
  errors and no changed behavior beyond actions being visible longer.

## Assumptions

- "Cuddle" is the existing rest-with-a-friend action; "bath" is the
  existing grooming action (self-groom relieves the groomer's bath need;
  grooming a friend relieves the friend's bath need and the groomer's
  cuddle need — these per-application effects become per-tick effects,
  otherwise unchanged).
- Solo rest (resting without a partner) is the same activity family as
  cuddle and inherits the cuddle bounds (min 3, max 8); it remains
  otherwise unchanged.
- Chase and movement are not need-relieving activities and are untouched:
  chase keeps its 004 pursuit/patience mechanics; a chase that catches its
  target still transitions into play, and the play then carries the new
  duration rules.
- Behavior selection (004's scored selection) is structurally unchanged;
  behaviors need no modification to remain *lawful* — during a minimum
  their proposals are simply superseded by continuation, and existing
  built-ins already propose continuation (idle) during sleep/rest.
  *Quality* needed one adjustment (post-merge review, 2026-07-19): the
  built-ins now treat a kitty mid-activity as a non-viable duet target
  (playmate viability and cuddle seeking skip it), because proposing at a
  non-conscriptable partner predictably bounces to Idle and would suppress
  the solo-play backstop for as long as the partner's scene runs. Behaviors
  MAY read the new duration bookkeeping to make smarter proposals, but
  nothing requires it.
- No re-entry cooldown is needed after a maximum-length activity:
  per-tick relief guarantees convergence, and brief lawful re-entry is
  true-to-life (a cat that wakes hungry for more sleep goes back to sleep).
- Meow, purr, and idle remain instantaneous non-activities; opportunistic
  play (batting at an adjacent critter mid-errand, from 004) starts a
  normal play activity under these rules.
- The happiness formula itself is unchanged; welfare improves solely
  because activities deliver more total relief per undertaking.
- Backwards compatibility with pre-006 saves is a non-goal by owner
  decision (2026-07-19): existing worlds may simply be started fresh. New
  duration keys remain tunables outside the config fingerprint as a matter
  of design hygiene, not as a compatibility promise.
