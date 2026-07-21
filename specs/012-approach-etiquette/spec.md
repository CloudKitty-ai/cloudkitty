# Feature Specification: Approach Etiquette ("Wait for me!")

**Feature Branch**: `009-orthogonal-interactions` (shared batch branch)

**Created**: 2026-07-20

**Status**: Draft

**Input**: Owner report + verified reproduction: "I'm noticing a lot of kitties
moving back and forth trying to get next to each other... one might be to have
one of the cats meow whatever need they are trying to fill to break the
deadlock" — refined: "To prevent issues where meow is on cooldown, let's add a
'Wait for me!' meow that only fires under circumstances like this."

## The gap being closed

Two kitties approaching *each other* decide against the same start-of-tick
snapshot, so each steps toward where the other just was — and under 009's
orthogonal interaction range they can lock into a corner-swapping dance at
walking distance 2, cuddle or game never starting (verified: 145 ticks in a
controlled world when the urgent-meow lottery is silenced; visible bouncing in
live worlds until the lottery lands). After this change, the pair has manners:
one kitty calls **"Wait for me!"** and holds still while the other closes the
corner. Deterministic, quick, and audibly adorable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The dance ends in a cuddle (Priority: P1)

Two kitties heading for each other meet near a corner; within a beat or two,
one stops and meows "Wait for me!", the other steps in beside it, and the
cuddle (or game) begins. A viewer never sees more than a moment of to-and-fro.

**Why this priority**: this is the reported problem.

**Independent Test**: the verified dance world (two cuddle-seekers, diagonal
start) resolves into Resting within a small fixed tick bound, with a
"Wait for me!" recorded — deterministically, with need-meows available or
on cooldown alike.

**Acceptance Scenarios**:

1. **Given** two kitties one corner apart, both seeking each other to cuddle,
   **When** ticks pass, **Then** the pair is cuddling within a few ticks and
   the yielding kitty meowed "Wait for me!" rather than pacing.
2. **Given** the same pair with every need-meow on cooldown, **When** ticks
   pass, **Then** the outcome is identical — the etiquette does not depend on
   any other message being available.
3. **Given** two kitties play-chasing each other, **When** they close to a
   corner, **Then** the same etiquette lands the pounce.

---

### User Story 2 - A new word in the meow vocabulary (Priority: P2)

Watchers see a genuine new utterance: "Wait for me!" appears in speech
bubbles and on the kitty card like any other meow, and it is heard *only* in
this situation — it is never spent on anything else, so it is effectively
always ready when the etiquette needs it.

**Why this priority**: the owner's explicit design call; also what makes the
fix legible to a watcher instead of looking like a freeze.

**Independent Test**: vocabulary round-trip (wire name, viewer text, cooldown
class) plus an observation run asserting Wait-for-me meows occur only at
yield moments.

**Acceptance Scenarios**:

1. **Given** a yielding kitty, **When** it holds its corner, **Then** a
   "Wait for me!" bubble appears (subject only to its own base cooldown, which
   nothing else consumes).
2. **Given** any other behavior in the world, **When** ticks pass, **Then**
   "Wait for me!" is never uttered outside a yield.

---

### User Story 3 - Nobody new gets stuck (Priority: P3)

The etiquette can never create a stall of its own: a kitty approaching a
partner who is *not* approaching back is delayed at most one extra tick, all
welfare and determinism guarantees hold, and old snapshots load untouched.

**Independent Test**: passive-partner unit case (yield alternates, arrival
within one tick of the direct walk); full suite green.

**Acceptance Scenarios**:

1. **Given** a higher-id kitty approaching a stationary partner, **When** it
   reaches the corner, **Then** it arrives beside the partner within one tick
   of the un-mannered walk (the yield alternates, never repeats).
2. **Given** any seeded world, **When** run twice, **Then** identical
   (no randomness in the rule).

---

### Edge Cases

- **Both kitties would yield**: impossible — only the higher id of the pair
  yields, and ids are strict.
- **Yield meow on its own cooldown** (a second dance within the base window):
  the turn is still spent holding still, so the symmetry still breaks; only
  the bubble is skipped. Etiquette works silent.
- **The partner moves away entirely**: next tick the distance is no longer 2
  and normal pursuit resumes; the rule only ever touches the exact corner
  moment.
- **Odd-tick arrival at the corner**: both step once more (one last dance
  beat), and the very next tick the yield resolves it — the bound is two
  ticks, not zero, and that is accepted.
- **Head-on transit** (different targets, opposing directions, mutual
  block): not an approach to each other, so the etiquette stays silent —
  FR-008's shuffled sidestep is what breaks these, within a couple of ticks
  in expectation rather than by fixed-phase luck.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The meow vocabulary MUST gain **"Wait for me!"** (wire name
  `wait_for_me`): no related need (base cooldown class, like "Follow me!"),
  rendered in viewer bubbles and card text like every other message, and
  emitted by the yield rule only — no behavior may use it for anything else.
- **FR-002**: When a kitty's pursued target is a **fellow kitty at exactly
  walking distance 2**, and the kitty holds the **higher id** of the pair,
  it MUST yield on alternating world ticks — proposing the "Wait for me!"
  meow instead of a step — while the lower id (and the higher id on
  non-yield ticks) walks as normal. The rule covers both kitty-approach
  paths: the cuddle walk and kitty-target play chases.
- **FR-003**: A yield MUST break the dance even when its meow is silenced by
  cooldown: the turn is spent stationary regardless.
- **FR-004**: A mutual approach at distance 2 MUST resolve into the intended
  interaction within two ticks; an approach to a passive partner MUST be
  delayed by at most one tick versus today.
- **FR-005**: The rule MUST be deterministic (no RNG) and live entirely in
  behavior proposals (Article IV — the engine is untouched).
- **FR-006**: Wire compatibility MUST hold: the new message kind is additive;
  pre-012 snapshots (which never mention it) load unchanged.
- **FR-007**: The dance regression MUST be pinned by tests derived from the
  verified reproduction, in both meows-available and meows-on-cooldown
  flavors, plus a play-chase variant.
- **FR-008**: The blocked-walk sidestep MUST de-synchronize: when no step
  closes distance, a kitty picks its sidestep from its own seeded
  per-decision randomness among free (dry-preferred) tiles, instead of a
  fixed direction order. (Added during implementation: the welfare gate
  surfaced the etiquette's sibling — kitties in *transit* to different
  targets meeting head-on and sidestepping in lockstep for dozens of ticks,
  verified at ticks 1329–1365. Same visible back-and-forth the owner
  reported; the id/parity rule cannot reach it because the dancers are not
  each other's targets. Seeded randomness keeps Article V intact while
  making synchronized phases impossible to sustain.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The reproduction world (two mutual cuddle-seekers, diagonal
  start) reaches Resting within 6 ticks in 100% of runs — previously 145
  ticks with meows silenced — and records at least one "Wait for me!".
- **SC-002**: Across the property suites, no "Wait for me!" is ever recorded
  outside a yield moment.
- **SC-003**: Full workspace suite green: welfare bounds, determinism replay,
  009/010/011 guards untouched.
- **SC-004**: A watcher at the demo world can see the etiquette: brief
  approach, one "Wait for me!" bubble, cuddle underway.

## Assumptions

- Tick-parity alternation (yield on even world ticks) is the progress
  guarantee against passive partners; one extra tick is an accepted cost.
- Three-way convergences are out of scope: the pairwise rule handles the
  reported geometry, and the welfare suite watches everything else.
- The new message participates in the standard meow plumbing (recent window,
  bubbles, serialization); no new config is needed — its cooldown is the
  existing base `cooldown_ticks`.
