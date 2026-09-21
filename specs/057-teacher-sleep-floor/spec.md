# Feature Specification: Teacher sleep rule reads the floor

**Feature Branch**: `057-teacher-sleep-floor`

**Created**: 2026-09-21

**Status**: Draft

**Input**: Experiments handover
`experiments/beam-world-screen-2026-09-19/HANDOVER-product-2026-09-21.md`
(main 705290d); kickoff on the owner's word ("Go", 2026-09-21, Product
session).

## Why (one paragraph)

The Gen 2 world package is fully ruled (#390): sleep floor 15, beam ttl
3,000, off-beam relief 3, count 6. Under a floor, a plain-tile nap
relieves sleep only down to the floor (spec 056), and the scripted
`needs_driven` teacher does not know that: it prices the walk to a beam
but scores every nap by the full need, so when no beam is in reach it
naps on the spot, the nap ends at the floor, the need regrows, and it
naps again. On the floor-15 count-6 package world that loop moves the
teacher's sleep share from 0.088 to 0.118 and dilutes its beam
placement from 0.458 to 0.341 — and the Gen 2 corpus is recorded from
this teacher, so the loop would be taught to the clone. The fix is the
doctrine-rule-2 shape: the teacher's sleep pressure becomes the relief
a nap here would actually deliver, not the need itself. Nothing
deploys; the served floor stays 0 and floor 0 is byte-identical.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A worthless nap loses (Priority: P1)

A kitty on the floor-15 world has sleep need 18, stands on plain
ground, has no sunbeam within reach and no warm partner beside it. A
nap here would relieve 3 points and stop at the floor. Its sleep
pressure is 3, not 18, so any other need above 3 wins the turn and the
nap-regrow loop never starts. A kitty whose need is at or under the
floor has pressure 0 off-beam: it does not begin a nap that would
relieve nothing.

**Why this priority**: this is the loop itself — the reason the spec
exists. The corpus records what this rule decides.

**Independent Test**: fixture world at floor 15, one kitty at need 18
on plain ground with no beam within reach and a competing need above
3; the kitty acts on the competing need. Same fixture at need 15 or
below with all other needs quiet: the kitty does not begin a sleep
scene.

**Acceptance Scenarios**:

1. **Given** floor 15, need 18, no warm option, a groom-worthy need at
   8, **When** the teacher scores its options, **Then** sleep scores as
   pressure 3 and the other need wins.
2. **Given** floor 15, need 15 (at the floor), no warm option, all
   other needs quiet, **When** the teacher decides, **Then** no sleep
   scene begins this tick.
3. **Given** floor 15, need 40, no warm option and nothing else to do,
   **When** the teacher decides, **Then** it may still nap — pressure
   25 is real relief, the rule discounts the nap, never bans it.

---

### User Story 2 - A warm option keeps the full need (Priority: P1)

The same kitty at need 18 stands one tile from a sunbeam (within
`sunbeam_reach`), or on a beam, or beside a mutual partner on a beam
(spec 031 conduction). That nap clears the need to 0, so the pressure
stays the full 18 and the sleep decision is unchanged from today. The
floor never discounts a nap that the world would honor in full.

**Why this priority**: equal to story 1 — the discount applying to
warm naps would suppress exactly the placement the corpus needs to
teach.

**Independent Test**: fixture at floor 15, need 18, beam within reach:
the teacher's decision is identical to the same fixture at floor 0.

**Acceptance Scenarios**:

1. **Given** floor 15, need 18, a beam within `sunbeam_reach`,
   **When** the teacher scores sleep, **Then** the pressure is 18 and
   the choice matches the floor-0 choice on the same world.
2. **Given** floor 15, need 18, kitty already on a beam, **When** the
   teacher scores sleep, **Then** the pressure is 18.

---

### User Story 3 - Floor 0 is today, byte for byte (Priority: P1)

On every shipped and frozen configuration the floor is 0, and
`max(need − 0, 0)` is `need`. Every decision on every served seed is
unchanged: the all-scripted certification leg exact-matches
`kitty-eval --brain needs_driven` as it does today, and no shipped
toml changes meaning.

**Why this priority**: spec 056's pin extends to the teacher; a served
behavior change here would be an unruled deploy.

**Independent Test**: the existing floor-0 regression pin and the
all-scripted cert leg on `anchor-b3.toml`, both of which must pass
with zero diffs.

**Acceptance Scenarios**:

1. **Given** floor 0 and any seed, **When** the teacher decides,
   **Then** every action matches the pre-change binary exactly.

---

### Edge Cases

- **Need exactly at the floor, off-beam**: pressure is 0 — the term is
  `max(need − floor, 0)`, never negative, and a zero-pressure nap is
  not begun (story 1, scenario 2).
- **Need under the floor, off-beam** (a nap begun on a beam that the
  beam expired out from under — ttl 3,000 makes this real): pressure
  is 0; the kitty does not re-nap in place. The need itself is left
  where it is (056's rule: never raised).
- **All needs quiet and pressure 0**: the teacher falls through to its
  existing idle/wander behavior; no new "do nothing" state is
  introduced.
- **Beam appears mid-scene**: out of scope — this rule prices the
  decision to begin a nap; scene endings stay as 056 settled them
  ("at the floor this tile can reach").
- **want_sleep announcements**: a kitty holding need above
  `announce_threshold` but below any worthwhile pressure still
  announces (056's consequence stands); the announcement is a state
  read, not a promise to nap. Stated as a consequence, not changed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The teacher's sleep pressure, when no warm option is in
  play, MUST be the relief a nap on this tile can deliver:
  `max(need − floor, 0)`, where floor is `actions.sleep_floor_off_beam`
  as the engine already validates it.
- **FR-002**: "Warm option in play" MUST mean: standing on a sunbeam,
  OR a mutual partner warm beside (the spec 031 conduction condition),
  OR a sunbeam within `sunbeam_reach` (priced, the existing
  worth-walking test). With any warm option in play the pressure MUST
  remain the full need.
- **FR-003**: A zero-pressure sleep option MUST lose to any positive
  competing score and MUST NOT begin a scene when nothing competes —
  pressure 0 means the nap is not worth starting, not that it ties.
- **FR-004**: At floor 0 the scoring MUST be byte-identical to today:
  same decisions, same actions, same RNG consumption on every seed.
  (The term reduces to `need` arithmetically; the requirement is that
  the implementation preserves this exactly — no reordered draws, no
  changed tie-breaks.)
- **FR-005**: The rule MUST read only the observation-derived warm
  options and global configuration constants — no per-cat hidden
  state, no new observation fields (doctrine rule 5; the student can
  learn a world constant from consequences).
- **FR-006**: The walk pricing MUST NOT change: `sunbeam_reach` stays
  at 8 and `sleep_travel_distance` keeps its meaning. (Design
  decision D1 below records why and what would reopen it.)
- **FR-007**: Scene-end rules from spec 056 MUST be untouched: this
  spec prices beginning a nap; how a nap ends is 056's settled law.
- **FR-008**: No served-world change: the served floor stays 0,
  nothing deploys from this spec, and no shipped or frozen toml is
  edited.

### Key Entities

- **Sleep pressure**: the value the sleep option carries into the
  teacher's scoring; today the raw need, after this spec the relief a
  nap would deliver when no warm option is in play.
- **Warm option**: the three conditions under which a nap clears the
  need fully (on-beam, conducted beside a mutual partner, beam within
  reach).
- **The floor** (`actions.sleep_floor_off_beam`): spec 056's config
  key; 0 on every served/shipped config, 15 on the Gen 2 package
  world.

## Design decisions

- **D1 — the walk price does not learn the floor (this corpus).** The
  handover's change 2 is declined for the first Gen 2 corpus, per
  Experiments' own recommendation: `sunbeam_reach` stays 8 and the walk
  price is unchanged. What reopens it: the shelf's declared pre-PPO
  read — teacher placement on the new corpus against the ~0.4 bar. A
  corpus under the bar moves reach or count before any training; only
  that read, not intuition, moves this dial.
- **D2 — discount, never a ban.** The pressure term scales the nap's
  worth; it does not make off-beam sleep illegal. A tired-enough kitty
  with nothing better to do still naps on the ground (story 1,
  scenario 3). The corpus should carry "ground naps are worth little
  under a floor", not "ground naps do not exist".

## Consequences (stated, per the handover)

- On the floor-15 package world the teacher's sleep share falls back
  toward its floor-0 value (0.088; it is 0.118 with the loop) and naps
  begun at or under the floor with no warm option go to zero.
- Placement (naps begun on a beam) is expected to recover toward the
  floor-0 value (0.458 from 0.341); it is REPORTED, not gated — the
  ~0.4 bar belongs to the corpus read, not to this spec.
- Teacher welfare stays within the seed spread of today's floor-15
  numbers (happiness 86.2, 0 distress crossings over 150).
- Kitties with sleep need between the floor and `announce_threshold`
  may hold want_sleep announcements longer, since they no longer
  relieve the need with worthless naps; this is the world speaking
  truthfully and is accepted.

## Doctrine check (CLAUDE.md rule 8, against experiments/DESIGN-DOCTRINE.md)

- **Rule 2 (prices are physics) — moved the shape of FR-001.** The
  pressure is what the world pays for the act: the relief this tile
  delivers. It is not a nudge away from ground naps — the number comes
  from the consequence (relief to the floor), not from a wish for beam
  placement. D2 follows from this: physics discounts, only a nudge
  would ban.
- **Rule 5 (teacher acts on what the student sees) — checked, moved
  FR-005.** Inputs: the kitty's own need, tile contents, partner
  adjacency, beam distance — all observation-derived — plus two global
  config constants (floor, reach). Constants are world physics, the
  same for every cat every tick; the student meets them through
  consequences. No new observation field, no schema change, no retrain
  boundary crossed by the read itself.
- **Rule 9 (frozen models cannot answer a reprice) — moved the
  sequencing.** A teacher change orphans the corpus, so it must land
  at the generation boundary, before the Gen 2 record — which is
  exactly where this spec sits (it is the shelf's named prerequisite
  for the re-record). No frozen roster is asked to answer it; the
  serve stays at floor 0.
- Rules 1, 3, 4, 6, 7, 8, 10 — checked, moved nothing: no reward term,
  no specialist relief, no charm pay, no free-register read, no new
  behavior awaiting a world, no information-scarcity design, no
  welfare gate changed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Floor-0 byte equivalence — the all-scripted cert leg on
  `anchor-b3.toml` exact-matches `kitty-eval --brain needs_driven`,
  and the spec 056 floor-0 regression pin passes unchanged.
- **SC-002**: On the floor-15 count-6 package world (tier 5 comparator
  leg, 30 seeds × 20k ticks), naps begun at or under the floor with no
  warm option number zero, and the teacher's sleep share falls from
  0.118 toward the floor-0 value 0.088.
- **SC-003**: Teacher welfare on the same leg stays within the seed
  spread of today's floor-15 numbers (happiness 86.2; 0 distress
  crossings over 150 need-episodes).
- **SC-004**: Placement (naps begun on a beam) is reported beside the
  0.341/0.458 reference numbers; no gate in this spec.
- **SC-005**: A `scripts/mutate.sh --expect` red exists for the new
  term: mutating the pressure back to `need` goes red on a floor-15
  fixture and stays green at floor 0 — the mutation is invisible
  exactly where the term is inert, which is the point of SC-001.

## Assumptions

- The engine-side floor semantics (relief clamped at the floor, need
  never raised, scene end at the reachable floor) are complete and
  correct as merged in spec 056; this spec builds on them and re-tests
  none of them.
- The three warm-option predicates exist today (on-beam check,
  conduction condition, priced reach test) and this spec composes
  them rather than defining new ones.
- Experiments runs the tier 5 comparator leg and the corpus read on
  their side once a branch exists; SC-002 through SC-004 are read
  there, on their harness, not re-implemented in CI.
- The Gen 2 package world named throughout is floor 15, ttl 3,000,
  off-beam relief 3, count 6 (#390, all owner-ruled).
