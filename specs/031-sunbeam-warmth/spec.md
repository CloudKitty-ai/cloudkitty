# Feature Specification: Shared Sunbeam Warmth

**Feature Branch**: `031-sunbeam-warmth`

**Created**: 2026-08-13

**Status**: Draft

**Input**: Owner design request (`experiments/sunbeam-warmth-2026-08-13/
design-input.md`): when cosleeping partners share a pile and either one's
tile holds a sunbeam, both receive the sunbeam sleep-relief rate. One rule,
no new elements, no geometry change, no observation change.

## Context

Sleeping is 21.8% of all policy decisions on the live seats — 19.1% cosleep
against 2.7% solo, a 7:1 preference — but sleeping in a sunbeam is 0.15% of
kitty-ticks, and 145 of those 185 ticks are accidental beam overlap (probe
2026-08-13, committed beside the design input). The scripted demonstrators
seek sunbeams, so the behavior was in the BC data; RL optimized it away,
rationally: a solo sunbeam nap pays Sleep `sleep_relief_sunbeam`, while a
mutual cosleep pays Sleep `sleep_relief` plus Cuddle relief to each of two
cats, and Cuddle has almost no other relief channel.

Shared warmth removes the conflict: a pile touching a beam sleeps at
sunbeam grade, so the beam becomes a placement target for the cosleep
behavior the world already loves instead of a losing competitor. The
deployed policies are frozen and will not seek the bonus; the payoff
arrives with the next trained generation, for which the relational bind
(sunbeam token ↔ partner token) is the shape the entity-attention
architecture (spec 030) handles natively.

## Clarifications

### Session 2026-08-13 (pre-spec, with the owner)

- Q: The FR-014/15 mutual definition counts a Resting partner as present in
  the pile — does a beam-Resting cat conduct warmth, and does it receive
  upgraded relief itself? → A: **Receiver: Sleeping only** (only sleep
  provides sleep relief — the rule upgrades the rate on an existing channel
  and never opens a new one). **Source: Sleeping or Resting** per the
  FR-014/15 mutual definition — sleeping next to a warm friend in a sunbeam
  is the point, whether that friend is asleep or resting awake in the pile.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Warmth conducts through the pile (Priority: P1)

A kitty sleeps with a friend. The friend is settled in the pile (sleeping
or resting) on a tile holding a sunbeam. The sleeper's sleep relief runs at
the sunbeam rate, exactly as if it were on the beam itself. When both
partners are sleeping and either tile holds the beam, both sleep at the
sunbeam rate.

**Why this priority**: This is the feature — the one rule the owner asked
for.

**Independent Test**: Place two kitties adjacent, one tile holding a
sunbeam; put them in a mutual cosleep; assert per-tick Sleep relief equals
`sleep_relief_sunbeam` for each sleeping partner, on-beam or off.

**Acceptance Scenarios**:

1. **Given** kitty A Sleeping with partner B, B mutual (Sleeping or
   Resting) on a sunbeam tile, A not on a beam, **When** A's serviced tick
   applies sleep relief, **Then** A's Sleep need lowers by
   `sleep_relief_sunbeam`.
2. **Given** A and B both Sleeping as partners, A on a sunbeam tile, B not,
   **When** each serviced tick applies relief, **Then** both lower Sleep by
   `sleep_relief_sunbeam` (A by today's own-tile rule, B by conduction).
3. **Given** A Sleeping on a sunbeam tile with partner B Resting beside it,
   **When** relief applies, **Then** A sleeps at the sunbeam rate and B
   receives no sleep relief (B is awake; resting pays only its existing
   cuddle relief).
4. **Given** the same pile after the sunbeam expires or drifts off both
   tiles, **When** the next serviced tick runs, **Then** both partners are
   back at the plain `sleep_relief` rate — conduction re-evaluates every
   serviced tick, like the own-tile rule does today.

---

### User Story 2 - The rule's edges hold (Priority: P1)

The rule is exactly one hop wide and never stacks: warmth conducts from the
direct partner only, two beams pay no more than one, a partner who has
wandered off or is merely nearby conducts nothing, and every existing
relief behavior is unchanged where the rule does not fire.

**Why this priority**: The edges are the difference between "one clean
rule" and a drifting welfare surface. They guard the constitution posture
(relief only increases, and only where intended).

**Independent Test**: One test per edge, asserting the rate chosen against
a hand-built world state.

**Acceptance Scenarios**:

1. **Given** A Sleeping with partner B, and a third kitty C on a sunbeam
   tile cosleeping with B (a chain A–B–C), **When** A's relief applies,
   **Then** A gets the plain rate — conduction is direct-partner only, no
   chaining.
2. **Given** A and B both Sleeping as partners, both on sunbeam tiles,
   **When** relief applies, **Then** each lowers Sleep by exactly
   `sleep_relief_sunbeam` — no stacking.
3. **Given** A Sleeping with partner B, B on a sunbeam tile but neither
   Sleeping nor Resting (walked away, chasing, eating — the drip tier),
   **When** A's relief applies, **Then** A gets the plain rate — the
   conduction source condition is exactly the FR-014/15 mutual definition.
4. **Given** a solo sleeper on a sunbeam tile, and separately a solo
   sleeper off one, **When** relief applies, **Then** rates are exactly
   today's (`sleep_relief_sunbeam` and `sleep_relief`) — solo behavior
   unchanged.
5. **Given** any pile the rule fires in, **When** relief applies, **Then**
   Cuddle relief (mutual tier, drip tier, rest-duet `cuddle_relief`) is
   exactly what it was before this feature — the rule touches only which
   Sleep rate is chosen, never any other channel.

---

### Edge Cases

- The conduction check reads the partner's *current* activity and tile
  every serviced tick, mirroring how `in_sunbeam` and partner availability
  are already re-checked — a partner that stands up or a beam that expires
  stops the warmth on the next serviced tick, no lingering state.
- A vacant/departed partner (already filtered by the availability check)
  conducts nothing; the rule adds no new failure mode to partner loss.
- Warmth never conducts *to* a Resting or otherwise-awake cat: there is no
  sleep-relief channel to upgrade, and the rule opens no new channel.
- Determinism: the rule reads only start-of-tick world state already
  consulted by the relief path (partner activity, partner tile, element
  type); no new randomness, no RNG-sequence change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A kitty in the Sleeping activity MUST receive Sleep relief at
  `sleep_relief_sunbeam` when its own tile holds a sunbeam (today's rule,
  unchanged) OR when its direct cosleep partner satisfies the FR-014/15
  mutual definition (partner activity Sleeping or Resting) AND the
  partner's tile holds a sunbeam. Otherwise the rate remains
  `sleep_relief`.
- **FR-002**: Conduction MUST be direct-partner only — the partner recorded
  in the sleeper's own activity, after the existing availability filter. No
  chaining through a third kitty, regardless of pile topology.
- **FR-003**: The sunbeam rate MUST NOT stack: any combination of own-tile
  and partner-tile sunbeams yields exactly `sleep_relief_sunbeam`.
- **FR-004**: Only Sleeping kitties receive sleep relief; the rule MUST NOT
  grant Sleep relief to a Resting or otherwise-awake cat, and MUST NOT
  create any new relief channel. It changes only which of the two existing
  Sleep rates is chosen.
- **FR-005**: The shared rate MUST be the existing `sleep_relief_sunbeam`
  dial — one number meaning "sunbeam-grade sleep." No new config key. The
  dial's default (8.0) is unchanged by this feature; re-pinning the value
  is the screen's decision (see Assumptions) and a separate config change.
- **FR-006**: The conduction condition MUST be re-evaluated every serviced
  tick from current world state, exactly as the own-tile sunbeam check is
  today. No cached or sticky warmth.
- **FR-007**: Every other relief behavior MUST be unchanged: Cuddle mutual
  tier, Cuddle drip tier, the rest-duet `cuddle_relief`, solo rest, solo
  sleep on and off beams, grooming. Scripted decision paths
  (`sunbeam_worth_walking` and the rest of `needs_driven`) MUST be
  untouched — they are distance-gated, not relief-derived, and the
  instruments keep their behavior.
- **FR-008**: No observation-schema, action-schema, mask, config-schema, or
  artifact change. No new elements, no geometry change, no RNG-sequence
  change.
- **FR-009**: The rule MUST be guarded by tests covering each acceptance
  scenario above, including the chain, stacking, drip-tier, and
  awake-receiver negatives.

### Key Entities

- **Conduction source**: the sleeper's direct cosleep partner, when mutual
  per FR-014/15 (Sleeping or Resting) and standing on a sunbeam tile.
- **Conduction receiver**: a Sleeping kitty only — the only activity with a
  sleep-relief channel to upgrade.
- **The shared rate**: `sleep_relief_sunbeam`, reused; no new dial.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a hand-built pile with either partner's tile holding a
  sunbeam, every Sleeping partner's per-tick Sleep relief equals
  `sleep_relief_sunbeam`; in the same pile without a beam, it equals
  `sleep_relief`.
- **SC-002**: The chain, stacking, drip-tier, and awake-receiver negatives
  each hold in tests (US2 scenarios 1–3 and US1 scenario 3).
- **SC-003**: A world driven with no sunbeam-adjacent cosleep anywhere
  produces byte-identical welfare trajectories before and after the change
  — the rule is inert where it does not fire.
- **SC-004**: Existing engine and welfare test suites pass unchanged except
  where a test deliberately constructs the conduction case.

## Assumptions

- **The dial value is screened, not specced.** The `{6, 7, 8}` screen
  (world-tuning-screens pattern, F-016 discipline: measure the channels,
  don't assume the dial's aim) is Experiments' instrument, run scripted-side
  after this rule lands. The owner's opening preference is 7. This spec
  ships the rule with the default untouched at 8.0; a default change
  afterward is a config change that moves `engine_defaults_sha256` and
  rides the re-baseline.
- **Re-baseline before the next generation's family freeze**, as the
  pipeline already requires — welfare trajectories shift wherever the rule
  fires, so baselines measured on the old engine are history there.
- **Census extension** (sunbeam positions alongside the existing
  position/cosleep tracking, to measure deliberate cosleep-on-beam in the
  next generation) is Experiments-side tooling, recorded in the design
  input's registered expectations — not part of this engine change.
- **Explicitly parked, not requested**: the sun-warmth situational
  happiness term (the dwell knob). It touches the happiness function itself
  and couples to purr legality; it is its own decision with its own screen,
  only if shared relief alone leaves sunny piles too brisk.
- Constitution posture: relief only ever increases where the rule fires; no
  cost, no new need pressure, no new failure mode on partner loss.
