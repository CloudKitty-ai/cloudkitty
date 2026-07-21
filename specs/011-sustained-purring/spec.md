# Feature Specification: Sustained Purring

**Feature Branch**: `009-orthogonal-interactions` (shared — specced alongside 009
and 010 as one QoL batch, at the owner's direction)

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "I want our kitties to be able to purr for more than
just a single tick, and not have it take up an action for them (maybe a min and
max duration for purr, and a cooldown before purring again)." (Backlog P1: purring
becomes a *sustained background state* — named min/max duration and cooldown
tunables, the purr meow fires once at purr start, state is saved and served so
the viewer can show a rumbling kitty.)

## The gap being closed

Today a purr is a single-tick *action*: it must be earned (happiness above the
purr threshold, or happiness that just rose), it emits one purr meow, and it
spends the kitty's entire turn — so a purring cat is a cat doing nothing else,
for exactly one tick. Real cats rumble for minutes while loafing, kneading, or
being adored. After this change, purring is something a kitty *is*, not
something it *does*: a contented kitty starts purring and keeps purring — for
a while, through whatever else it's doing — then rests its motor before the
next rumble. No turn is ever spent on it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The purr runs in the background (Priority: P1)

A viewer sees a happy kitty begin to purr and *stay* purring across many ticks
— while it walks, eats, cuddles, or naps — then wind down. The kitty never
pauses its life to purr; purring rides along with everything else.

**Why this priority**: This is the feature — the owner's explicit intent that
purring stop costing a turn and stop lasting one tick.

**Independent Test**: Drive a world where one kitty's happiness sits above the
purr threshold; observe the kitty purring for a multi-tick stretch during
which it also completes other actions (moves, meals, naps). No tick shows the
kitty idle *because of* purring.

**Acceptance Scenarios**:

1. **Given** a kitty whose happiness is above the purr threshold and whose
   purr is off cooldown, **When** the tick advances, **Then** the kitty
   starts purring — and still takes whatever action it would otherwise have
   taken that tick.
2. **Given** a purring kitty, **When** ticks pass, **Then** the purr persists
   for its drawn duration while the kitty goes about its business, and then
   ends on its own.
3. **Given** a kitty whose purr just ended, **When** it remains happy,
   **Then** it does not purr again until the cooldown has passed — then the
   rumble returns.
4. **Given** a kitty that was never earned a purr (happiness below threshold
   and not rising), **When** ticks pass, **Then** it does not purr — the
   earned rule stands.

---

### User Story 2 - One meow per rumble, and a visible purr (Priority: P2)

A viewer hears about a purr exactly once — a single purr meow when the rumble
begins, not a bubble every tick — and can *see* which kitties are currently
purring, because the world reports purring as part of each kitty's state.

**Why this priority**: The anti-spam rule keeps meows meaningful, and serving
the state is what lets the viewer show a rumbling kitty at all. Both are part
of making the sustained purr real to a watcher.

**Independent Test**: Over a purr lasting N ticks, exactly one purr meow is
recorded at its start; the kitty's served state reads as purring for the whole
stretch and not-purring after.

**Acceptance Scenarios**:

1. **Given** a purr that starts this tick, **When** the meow log is inspected,
   **Then** exactly one purr meow was emitted at purr start, and none on the
   following purring ticks.
2. **Given** a purring kitty, **When** a watcher inspects the world through
   the API or the viewer, **Then** the kitty is reported as purring; when the
   purr ends, the report clears.
3. **Given** a viewer watching the meadow, **When** a kitty purrs, **Then**
   the watcher can tell — a gentle cue on the kitty, with the exact treatment
   an implementation decision (no grand new animation is required by this
   feature).

---

### User Story 3 - Saved, replayed, identical (Priority: P3)

An owner restarts the server mid-purr and the kitty resumes rumbling exactly
where it left off, for exactly as long as it would have. Two runs of the same
seed purr at the same ticks for the same durations, always.

**Why this priority**: Constitutional plumbing (Article V) — expected, not
novel, but purr durations are drawn randomly and randomness must be seeded and
saved like everything else.

**Independent Test**: Save mid-purr, restore, and compare against an
uninterrupted run: identical purr timelines. Old snapshots (from before the
feature) load cleanly with all kitties quiet and eligible to purr.

**Acceptance Scenarios**:

1. **Given** a world saved while a kitty purrs, **When** it is restored,
   **Then** the purr continues with its remaining duration and the future
   matches an unbroken run tick for tick.
2. **Given** a snapshot saved before this feature existed, **When** it loads,
   **Then** every kitty starts quiet (not purring, no cooldown) and the world
   runs on without error.

---

### Edge Cases

- **Happiness dips mid-purr**: the purr runs its drawn duration regardless — a
  purr has momentum, and Article I's floor means no kitty is ever miserable
  anyway. (The earned rule gates *starting* a purr, not sustaining one.)
- **The old purr action retires**: no kitty ever again spends a turn purring,
  and nothing may propose it as an action. Whatever a behavior would have done
  in a purr-proposing moment, it now simply does something else — the engine's
  fallback-to-idle machinery already covers any stale proposal shape.
- **Continuous contentment**: a kitty that stays blissful purrs in waves —
  duration, cooldown, duration — rather than one endless drone; the cooldown
  is what gives the rumble a rhythm.
- **Minimum equals maximum**: a fixed-length purr is a legal configuration
  (min = max); the duration draw still occurs identically for determinism.
- **Zero cooldown**: legal — back-to-back purrs are then possible; still
  distinct purrs, each with its own start meow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Purring MUST be a background state on a kitty, never an action:
  a purring kitty proposes, performs, and completes every activity exactly as
  a non-purring kitty does, and no turn is ever consumed by purring.
- **FR-002**: A purr MUST start only when earned — happiness above the purr
  threshold, or happiness that just rose (today's rule, unchanged) — and only
  when the kitty is not already purring and its cooldown has elapsed. The
  world starts purrs itself; behaviors do not propose them.
- **FR-003**: Each purr's duration MUST be drawn at purr start from the
  world's seeded randomness, between a configured minimum and maximum
  (inclusive); the purr ends when the duration elapses, and a configured
  cooldown MUST pass before that kitty may purr again.
- **FR-004**: The three quantities MUST be named configuration values
  (`purr_min_ticks`, `purr_max_ticks`, `purr_cooldown_ticks` — Article VI),
  validated at startup (1 ≤ min ≤ max, cooldown ≥ 0) with the standard
  naming-the-field error, documented in the shipped world files, and
  defaulted sensibly when absent so existing configs keep working unedited.
- **FR-005**: The purr meow MUST fire exactly once, at purr start, and never
  on subsequent purring ticks; all other meow rules are untouched.
- **FR-006**: The single-tick purr action MUST be retired: no built-in
  behavior proposes it, and a stale or external purr proposal resolves to an
  idle turn like any other invalid proposal (Article IV) — never to a lost
  turn spent "purring".
- **FR-007**: Purr state (purring or not, and whatever timing the engine
  needs to resume it faithfully) MUST be saved in snapshots and MUST be
  visible in the served kitty state, so watchers and the viewer can tell a
  purring kitty from a quiet one. Snapshots from before this feature MUST
  load with all kitties quiet and immediately eligible.
- **FR-008**: The viewer SHOULD give a purring kitty a gentle visible cue;
  the treatment is an implementation choice and deliberately modest — an
  elaborate rumble animation is not required and may be its own later item.
- **FR-009**: Determinism MUST be preserved (Article V): duration draws come
  from the seeded world randomness in fixed tick order, same seed means same
  purr timeline, and save/restore reproduces the identical future.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a driven world, a purring kitty completes other actions on
  100% of its purring ticks where it would otherwise have acted — zero turns
  are consumed by purring across the entire run.
- **SC-002**: Every observed purr lasts between the configured minimum and
  maximum ticks inclusive, consecutive purrs by one kitty are separated by at
  least the configured cooldown, and each purr produces exactly one purr meow.
- **SC-003**: A save taken mid-purr, restored, matches an uninterrupted run of
  the same seed tick for tick; pre-feature snapshots load cleanly with all
  kitties quiet.
- **SC-004**: The full invariant/property suite passes unchanged in spirit:
  needs bounded, relief guaranteed, happiness floor held, no kitty removed or
  alone — purring changes no welfare arithmetic.
- **SC-005**: A watcher at the viewer can identify which kitties are purring
  at a glance during a single sitting, and existing world files start with
  zero required edits.

## Assumptions

- The earned rule is kept verbatim from today (happiness above the purr
  threshold, or a happiness rise) as the *start* condition; it does not end a
  purr early — durations run their course for momentum and simplicity.
- A purr is pure charm: it changes no needs, no happiness arithmetic, and no
  welfare guarantee — it is expression, not mechanics. (Any future "purring
  soothes nearby kitties" idea would be its own spec.)
- Retiring the purr action is a compatible evolution of the proposal surface:
  stale proposals fall to idle exactly like today's invalid proposals — no
  special migration is needed beyond the standing fallback rule.
- The viewer cue (FR-008) is intentionally modest and needs no art-approval
  gate; if design grows a full rumble animation later, that lands with its
  own gate like other viewer art.
- Purr timing shown to watchers needs no new endpoint — purring rides the
  existing kitty state everywhere kitty state already appears.
- Orthogonal-only interactions (009) and water-averse pathing (010) share
  this branch but are independent of purring; nothing here depends on them.
