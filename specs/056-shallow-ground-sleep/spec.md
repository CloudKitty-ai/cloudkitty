# Feature Specification: Shallow ground sleep

**Feature Branch**: `056-shallow-ground-sleep`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: "Off-beam sleep relieves sleep need only down to a configurable floor; sleep on a sunbeam, or conducted beside a mutual partner on a sunbeam (spec 031), clears it fully. One config key, default 0 = today's law. The spec must settle the early-end rule. Handover: experiments/beam-world-screen-2026-09-19/HANDOVER-product-shallow-ground-2026-09-20.md (owner's word: 'Shallow ground sounds good. Let's try 10/15/20/25')."

## Why (one paragraph)

The beam-world screen (tiers 1–4) found that a sunbeam is worth zero
ticks to the served Gen 1 minds: they begin naps at a sleep need of 7–9,
every nap already runs the six-tick minimum, and six ground ticks clear
the need — so the beam's higher rate has nothing to relieve, and PPO
correctly drops the walk to it. For a beam to matter, it must change the
outcome of a nap the cat actually takes. Shallow ground does that at
every need level without touching when cats sleep or how long: a cat that
naps on the ground wakes a little tired, every time; only a beam gives
real rest. Experiments' tier-5 screen (declared, PREREG-tier5.md) runs
floors 10/15/20/25 the night this lands; the served world keeps floor 0
until the owner rules after the screen.

## Clarifications

### Session 2026-09-20

- Q: Should a ground nap under a floor end early once the sleep need
  reaches the floor (the lowest level that tile can reach), rather than
  running to the 12-tick maximum because zero is unreachable? → A: Yes —
  finished = the floor this tile can reach (D1 CONFIRMED by the owner;
  FR-004 stands as written).
- Q: Is `actions.sleep_floor_off_beam` the final name for the config
  key? → A: Yes (D2 CONFIRMED by the owner; the name is frozen —
  Experiments' PREREG-tier5.md wires to it).
- Q: Should the floor's upper validation bound track the world's
  configured distress threshold, rather than the fixed number 90? → A:
  Yes — the bound is the configured `[thresholds] distress`, whatever that
  world sets it to (FR-006 tightened).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The floor holds on the ground (Priority: P1)

A world-tuner sets the floor to a nonzero level. A cat that sleeps on
plain ground has its sleep need relieved tick by tick as today, but the
need never drops below the floor — and a cat whose need is already under
the floor sleeps without its need being raised.

**Why this priority**: this is the law itself. Everything else in the
feature qualifies or bounds it.

**Independent Test**: one off-beam sleeper, floor above zero, need above
the floor: run the nap and read the need at the end.

**Acceptance Scenarios**:

1. **Given** floor 20 and an off-beam sleeper at sleep need 40, **When**
   enough sleep ticks pass to relieve 40, **Then** the need reads exactly
   20, not lower.
2. **Given** floor 20 and an off-beam sleeper at sleep need 12 (already
   under the floor), **When** it sleeps, **Then** its need stays 12 —
   never raised toward the floor.
3. **Given** floor 0 (the default), **When** any cat sleeps anywhere,
   **Then** relief is exactly today's law, byte for byte.

---

### User Story 2 - The beam clears it fully (Priority: P1)

The same world: a cat that sleeps on a sunbeam tile, or off-beam beside a
mutual partner who stands on a sunbeam tile (spec 031's conducted
warmth), has its need relieved all the way to zero, floor or no floor.

**Why this priority**: the floor only creates value if the beam escapes
it — the pair of stories is one law with two sides.

**Independent Test**: same nap, sleeper on a beam (and separately,
conducted): the need reaches zero.

**Acceptance Scenarios**:

1. **Given** floor 20 and a sleeper on a sunbeam tile, **When** it sleeps
   long enough, **Then** its sleep need reaches 0.
2. **Given** floor 20 and an off-beam sleeper whose mutual co-sleep
   partner stands on a sunbeam tile, **When** it sleeps long enough,
   **Then** its sleep need reaches 0 (conduction escapes the floor
   exactly as it upgrades the rate).
3. **Given** a conducted sleeper whose warm partner wanders off mid-nap,
   **When** the next sleep tick lands, **Then** that tick relieves at the
   plain rate and respects the floor — the escape is per-tick
   circumstance, as the rate already is.

---

### User Story 3 - Naps still end honestly (Priority: P1)

A ground nap under a floor still ends when it has done all it can — it
does not grind to the maximum duration because zero is unreachable.

**Why this priority**: without this, the floor silently rewrites nap
lengths world-wide (every ground nap runs to the 12-tick cap), which is a
different law — restless ground — than the one the owner approved.

**Independent Test**: a ground nap that reaches the floor after the
minimum duration ends on that tick, not at the cap.

**Acceptance Scenarios**:

1. **Given** floor 20 and an off-beam sleeper whose need reaches 20 after
   the minimum duration is met, **When** scene ends resolve, **Then** the
   nap ends that tick (finished = no further relief possible where it
   lies), exactly as a floor-0 nap ends at need 0 today.
2. **Given** floor 0, **When** any nap ends, **Then** the ending tick is
   identical to today's law on the same world and seed.

---

### Edge Cases

- Co-sleep duet ends: today either sleeper reaching 0 can end the scene;
  under the law each sleeper's "finished" level is the floor *its own*
  circumstances can reach (0 on-beam or conducted, the floor otherwise).
  A beam sleeper duetting with a ground sleeper finishes at different
  levels; the existing either-side rule then applies unchanged.
- Floor equal to a cat's current need: relief ticks leave it exactly in
  place; the nap ends at the minimum duration (no further relief was ever
  possible).
- Floor at or above the level cats begin naps at (served minds start at
  7–9; a floor of 10+ exceeds it): ground naps relieve nothing, end at
  the minimum, and the cat stays at its starting need — legal, and
  exactly the pressure the screen wants to price.
- Invalid floors: negative, or at/above the configured distress
  threshold — rejected at startup with a clear error, like every
  bounded config value (Article I pressure must stay relievable somewhere; the beam
  always relieves fully, so distress remains escapable at any legal
  floor, but a floor at distress level would let ground sleep *sustain*
  distress pressure, which the bound forbids).
- The conducted check and the floor check must agree: the same
  circumstance that selects the sunbeam-grade rate is the one that
  escapes the floor — one predicate, never two that can drift.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: One config key, **`actions.sleep_floor_off_beam`** (name
  pinned by this spec — Experiments wires PREREG-tier5.md to it), a need
  level, **default 0**. Absent from a config file means 0; every
  shipped, served, and frozen toml therefore parses to today's law
  unchanged, and no existing file is edited.
- **FR-002**: Off-beam sleep relief MUST NOT take the sleep need below
  the floor: each sleep tick relieves at today's rate but clamps at the
  floor. A need already at or under the floor is left exactly where it
  is — the floor never raises a need.
- **FR-003**: Sleep on a sunbeam tile, or off-beam with conducted warmth
  (a mutual co-sleep partner standing on a sunbeam tile, spec 031), MUST
  relieve to 0 exactly as today. The circumstance that selects the
  sunbeam-grade rate MUST be the same single predicate that escapes the
  floor, evaluated per tick — a partner wandering off mid-nap re-imposes
  the floor on later ticks.
- **FR-004** (the early-end rule, D1): a sleep scene's "finished" level
  for early ending MUST become *the lowest level the sleeper's current
  circumstances can reach* — 0 when on-beam or conducted, the floor
  otherwise — instead of the literal 0. Minimum-duration and
  maximum-duration behavior are unchanged; for a co-sleep duet, each
  side's finished level is its own, and the existing either-side rule is
  untouched. At floor 0 this predicate is exactly today's (0 is the
  reachable floor everywhere), so the default changes nothing.
- **FR-005**: Only sleep is touched. Rest, grooming, eating, drinking,
  play, cuddle relief riding a co-sleep pile, and every other need and
  scene keep today's law verbatim — the change is scoped to sleep-need
  relief and the sleep scene's finished level.
- **FR-006**: The floor MUST be validated at startup: `0 ≤ floor <` the
  world's **configured** distress threshold (`[thresholds] distress`, default
  90) — the bound tracks the configured value, not the number 90.
  Out-of-range values are a startup configuration error with a clear
  message, never a clamp.
- **FR-007**: With the key absent or 0, the simulation MUST be
  step-for-step identical to today: same worlds, same seeds, same
  actions, same needs, tick for tick.
- **FR-008**: The key MUST appear in the served config's `[actions]`
  commentary (one doc line) and in the `GET /settings` surface
  (spec 052), like every world-law dial.
- **FR-009**: Every new behavioral claim is test-guarded with its red
  proven via the house mutation cycle (`scripts/mutate.sh`): the floor
  holds, the beam clears, conduction clears, an under-floor need is
  never raised, the early-end fires at the reachable floor, and
  default-0 equivalence.

### Key Entities

- **The floor** (`actions.sleep_floor_off_beam`): a need level
  (validated `< [thresholds] distress`, the configured value); the lowest
  sleep-need value plain-ground sleep can reach. Default 0 — today's
  law.
- **The escape**: the spec 031 warmth circumstance (own tile is a
  sunbeam, or conducted from a mutual partner's sunbeam tile). One
  predicate selects both the sunbeam-grade rate and the full-clear.
- **Finished level**: per sleeper per tick, the lowest need its current
  circumstances allow; the early-end rule compares against it instead of
  0.

## Design decisions

- **D1 — finished means "no further relief possible where it lies".**
  The handover names the fork: either "finished" becomes "at the floor
  this tile can reach", or every ground nap runs to the 12-tick cap.
  This spec picks the former (Experiments' reading, and the only one
  that is the owner's approved law): the floor changes *how rested a
  ground nap leaves you*, not *how long cats lie there*. The cap-running
  alternative would move every nap length in the world as a side effect
  and re-price sleep time wholesale — a second, unasked-for law.
- **D2 — the key name is pinned: `actions.sleep_floor_off_beam`.** The
  handover leaves the name to Product; keeping the proposed name matches
  its siblings (`sleep_relief`, `sleep_relief_sunbeam`), reads as what it
  is, and lets Experiments wire the prereg without a round-trip.

## Consequences (stated, per the handover)

- **Want words**: with a floor at or above the served
  `announce_threshold` (20), a ground sleeper stays armed for
  `want_sleep` between naps, so meadow `want_sleep`/`here_sunbeam`
  traffic rises at the 20 and 25 screen levels. Under the fog this is
  the channel carrying a real fact — where rest is — which doctrine
  rule 8 asks for; it is also a louder meadow. The tier-5 screen reads
  meow rates per level so the owner can see the trade before any served
  ruling.
- **Distress** (corrected at review, 2026-09-20): the bound keeps
  distress from being plain ground's *resting* state, but a floored
  cat's need still regrows from the floor between naps, and safeguard
  spawning covers Eat and Drink only — no mechanism spawns a sunbeam
  for a tired cat; beam supply is the world's element rules. The
  tier-5 floors (10–25) sit far under distress (90), so the screen is
  unaffected; a world that pushes the floor near distress buys watchdog
  traffic, and a tighter bound (safeguard, the wet-fur precedent) is an
  owner call for a later spec if the screen ever makes it matter.
- **The scripted teacher** (corrected at review, 2026-09-20):
  `needs_driven` chooses *where* to sleep without reading relief
  amounts, and that choice is unchanged. The corpus's shape does change
  under a floor: plain naps end earlier (at the floor), the freed ticks
  are re-decided, and a nap begun at or under the floor is a
  minimum-length scene that relieves nothing and repeats as the need
  regrows. The floor acts on the RL reward, which is the point of the
  screen; the re-decide churn is a dynamics fact the tier-5 read should
  expect at floors 10/15.
- **Client**: nothing to draw; needs are not shown.
- **No served deploy**: the served world keeps floor 0 until the owner
  rules after the tier-5 screen.

## Doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md`:

- **Rule 2** (prices are physics: price states of the world, never
  nudges) moved the shape of the whole feature: the floor is a property
  of *where you sleep*, applied to every sleeper identically — not a
  reward-term nudge toward beams.
- **Rule 7** (build a behavior when the world that values it exists)
  moved the direction: rather than paying minds to visit a beam that
  changes nothing (tier 2 showed PPO correctly refuses that), the world
  is changed so the beam has real value, then the screen asks whether
  the behavior follows.
- **Rule 8** (design scarcity of information, not incentives for
  behavior) moved the want-word consequence from "problem" to "stated
  trade": the louder meadow at floors ≥ 20 is the here-word channel
  carrying a real fact, which is what the rule wants the world to
  create.
- **Rule 9** (frozen models cannot answer a reprice) moved the screen's
  design and this spec's deploy posture: gen1-A comparators run on the
  floor worlds as reads, PPO fine-tunes answer the reprice, and the
  served world does not move until the owner rules.
- Rules 1, 3–6, and 10 moved nothing: no reward term changes, no side
  relief is added, no scripting of the free register, the teacher is
  untouched, and welfare gating stays with the screen's existing
  two-layer reads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the key absent and with it set to 0, a seeded world
  reproduces today's law exactly: zero divergent ticks over the
  equivalence run (action for action against the served toml).
- **SC-002**: At a nonzero floor, 100% of plain-ground naps in the test
  worlds end with sleep need exactly at max(floor, starting need − total
  relief) and never below the floor; 0 naps raise a need.
- **SC-003**: At the same floor, 100% of on-beam and conducted naps can
  reach need 0.
- **SC-004**: At a nonzero floor, a ground nap whose need reaches the
  floor after the minimum duration ends that tick — 0 naps run to the
  maximum for want of an unreachable zero.
- **SC-005**: Experiments' acceptance list is satisfied on the branch:
  the four relief tests plus the early-end test each mutation-proven
  red, default-0 equivalence shown, the doc line present, the key served
  by `/settings` — and the eight tier-5 arms can launch the night the
  branch is mergeable.

## Assumptions

- The handover (`experiments/beam-world-screen-2026-09-19/HANDOVER-product-shallow-ground-2026-09-20.md`,
  owner-approved in-session 2026-09-20) is the source of intent; the
  tier-5 prereg is Experiments' and out of scope here.
- D1 and D2 are this spec's calls, made where the handover invited them;
  both are flagged in the PR for the owner's review.
- The floor is compared in need units on the same scale as the distress
  threshold; fractional values are legal like other relief dials.
- Compatibility markers for the changelog entry: none expected —
  default 0 is proven equivalent (FR-007), so no `[world-fresh]`,
  `[obs-schema]`, or `[rng-sequence]`; a missing marker is a claim and
  the equivalence run is its evidence.
- No served deploy rides this arc; the tier-5 screen runs on lab builds
  from the merged branch.
