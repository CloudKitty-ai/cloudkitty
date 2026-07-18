# Feature Specification: CloudKitty MVP

**Feature Branch**: `001-cloudkitty-mvp`

**Created**: 2026-07-18

**Status**: Draft

**Input**: User description: "Build the MVP of CloudKitty: a 2D tile-based simulated
world where kitties frolic and play — a cute sandbox with pluggable per-kitty behavior,
split into a server that owns all game logic and a read-only web viewer." (Full prompt
retained in version control history; all constitution articles take precedence.)

## Clarifications

### Session 2026-07-18

- Q: How should distress events be recorded while a need stays ≥ 90? → A:
  Edge-triggered — one event when a need crosses the threshold; no new event until
  the need drops below the threshold and crosses it again.
- Q: Should determinism be kept, and how do built-in behaviors interact with the
  Article IV time budget? → A: Keep full determinism (Article V unchanged). Built-in
  behaviors run synchronously within the tick and are never subject to the
  wall-clock time budget; the budget and fallback machinery apply only to future
  external behaviors.
- Q: What is the default external-behavior time budget? → A: 50% of the configured
  tick duration (400 ms at the default 800 ms tick), configurable like all other
  simulation constants.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Watch a Living Kitty World (Priority: P1)

A viewer starts the CloudKitty server with the default configuration, opens the web
viewer in a browser, and watches a cute 2D tile world where at least two kitties move
around, eat chow, drink water, sleep (preferring sunbeams), play, chase bugs, groom
themselves and each other, meow in speech bubbles, and purr when happy. Needs rise over
time and visibly fall when acted on; each kitty shows a happiness indicator and
sleeping/resting poses. The viewer never interacts with the simulation — it is a
window into the world.

**Why this priority**: This is the product. Without a visible, continuously running,
believable world there is nothing to demo, extend, or enjoy. Every other story builds
on the simulation loop and viewer this story requires.

**Independent Test**: Start the server with defaults, open the viewer, and observe for
several minutes. Delivers value entirely on its own: a watchable kitty sandbox.

**Acceptance Scenarios**:

1. **Given** a machine with the project installed, **When** the operator starts the
   server with the default configuration and opens the viewer, **Then** a 32×32 tile
   grid appears showing at least 2 kitties and at least one of each visible element
   type (water, chow, bug, sunbeam).
2. **Given** the world is running at the default speed (one tick per 800 ms), **When**
   the viewer watches over time, **Then** each kitty is observed moving, eating,
   drinking, sleeping, playing, grooming, and meowing, and the world updates visibly
   every tick.
3. **Given** a kitty whose needs are mostly satisfied, **When** its happiness exceeds
   the purr threshold (default 70) or rises this tick, **Then** the kitty may purr and
   the viewer can see it is happy.
4. **Given** a kitty acts on a need (e.g., eats), **When** the action resolves,
   **Then** the corresponding need visibly drops by the configured amount and
   happiness responds accordingly.
5. **Given** a kitty meows, **When** the viewer is watching, **Then** a speech bubble
   with the message (e.g., "I want to play!") appears near that kitty.

---

### User Story 2 - Kitties Are Always Safe (Priority: P1)

Anyone observing or extending CloudKitty can trust that the constitution's guarantees
hold at all times: kitties never suffer, never die, and are never alone. Needs stay
within bounds, happiness never falls below its floor, distress is only ever a recorded
signal, relief resources always appear when a kitty needs them, and no sequence of
events ever removes a kitty or leaves fewer than two in the world.

**Why this priority**: The constitution makes these articles inviolable and requires
automated tests in CI. Safety is co-equal with the visible world — a build that
violates any article is not shippable regardless of how cute it looks.

**Independent Test**: Run the automated invariant suite: randomized worlds driven for
at least 10,000 ticks with randomized configurations and behaviors, asserting all
constitution invariants every tick.

**Acceptance Scenarios**:

1. **Given** any randomized valid configuration and behavior mix, **When** the world
   runs for at least 10,000 ticks, **Then** no kitty is ever removed, the population
   never drops below 2, every need stays within 0–100, and happiness never falls
   below the floor (default 5).
2. **Given** any kitty's need exceeds the safeguard threshold (default 75), **When**
   no reachable resource satisfying that need exists, **Then** one spawns during the
   next environment phase even if the element type is at its configured maximum.
3. **Given** any kitty's need reaches the distress threshold (default 90), **When**
   the tick completes, **Then** a distress event (kitty id, need, tick) is recorded
   and retrievable, and nothing punitive happens to the kitty.
4. **Given** a configuration listing fewer than 2 kitties, **When** the server starts,
   **Then** startup is rejected with a clear error naming the violated rule.

---

### User Story 3 - Different Kitties, Different Personalities (Priority: P2)

An operator configures each kitty with a named behavior strategy. Two kitties with
different behaviors (e.g., `needs_driven` and `playful`) observably act differently:
the playful kitty chases and plays more while the needs-driven kitty prioritizes its
most pressing need. Behaviors only propose actions; the engine validates every
proposal and falls back to a safe default when a behavior is slow, broken, or invalid.

**Why this priority**: Pluggable per-kitty behavior is the MVP's differentiating
feature and the foundation for future external behavior plugins, but it requires the
P1 world to exist first.

**Independent Test**: Configure two kitties with the two shipped behaviors, run the
world, and compare their action histories; separately, inject a misbehaving strategy
and confirm the engine's fallback keeps the world running safely.

**Acceptance Scenarios**:

1. **Given** two kitties configured with `needs_driven` and `playful` respectively,
   **When** the world runs for a substantial period, **Then** their action
   distributions measurably differ (the playful kitty plays/chases more often).
2. **Given** a behavior returns an invalid, malformed, or late proposal (or none),
   **When** the engine applies actions, **Then** that kitty safely idles or falls
   back to the default behavior, no error state occurs, and the tick loop is not
   delayed beyond its budget.
3. **Given** a behavior decides for a kitty, **When** it receives its decision
   context, **Then** the context is read-only and contains the kitty's own full
   state plus a world snapshot including other kitties' positions and recent meows,
   taken at the start of the tick.

---

### User Story 4 - The World Survives a Restart (Priority: P2)

An operator stops the server (gracefully) and starts it again. The world resumes
exactly where it left off: same kitty positions and needs, same elements, and the same
future — because the random state is preserved, the resumed world unfolds exactly as
it would have without the restart. Starting with a fresh-world option discards the
saved state and generates a new world.

**Why this priority**: Persistence makes the sandbox feel like a persistent home for
kitties rather than a demo, and determinism-across-restarts is a constitutional
requirement — but it depends on the P1 world existing.

**Independent Test**: Run a world, stop it, restart it, and field-by-field compare the
resumed state to the saved state; run a parallel uninterrupted world with the same
seed and confirm identical evolution.

**Acceptance Scenarios**:

1. **Given** a running world, **When** the operator stops the server gracefully and
   restarts it with the same configuration, **Then** kitty positions, needs, elements,
   tick count, and random state resume identically.
2. **Given** a running world, **When** the state-saving interval (default every 100
   ticks) elapses, **Then** the world state is saved without interrupting the
   simulation.
3. **Given** a saved world exists, **When** the operator starts with the fresh-world
   option, **Then** the saved state is ignored and a new world is generated.
4. **Given** a saved world that fails validation (violates constitution invariants or
   is incompatible with the current configuration), **When** the server starts,
   **Then** it refuses to start with a clear error explaining the mismatch and how to
   proceed (e.g., start fresh), rather than silently discarding the world.
5. **Given** two servers started with identical seed, configuration, and built-in
   behaviors, **When** both run the same number of ticks, **Then** their world states
   are identical.

---

### User Story 5 - Shape the World Through Configuration (Priority: P3)

An operator edits the configuration file to change world size, simulation speed, the
kitty roster, element counts, and simulation constants (need rates, action effects,
thresholds, weights, cooldowns, time-to-live values). Valid changes take effect on the
next start; invalid configurations are rejected at startup with clear, specific
errors.

**Why this priority**: Configurability makes the sandbox tunable and testable, but
sensible defaults mean the product works without touching it.

**Independent Test**: Start the server with modified configurations and verify the
world reflects each change; start with each class of invalid configuration and verify
rejection with an actionable message.

**Acceptance Scenarios**:

1. **Given** a configuration with a different world size, tick duration, or element
   minimum/maximum, **When** the server starts, **Then** the simulation reflects the
   configured values.
2. **Given** a configuration where an element type's minimum or maximum falls outside
   the hard bounds (minimum 1 per type — 0 allowed for greebles; maximum
   `floor(world area / 32)` per type), **When** the server starts, **Then** the
   configuration is rejected with an error naming the offending value and the
   allowed range.
3. **Given** the default configuration, **When** the operator makes no edits,
   **Then** the world runs with all documented defaults (32×32 grid, 800 ms tick,
   default need rates, thresholds, and weights).

---

### User Story 6 - The Greeble Mystery (Priority: P3)

A viewer watches a kitty suddenly sprint across the world, pounce, and bat at…
nothing. Greebles — fast, erratic critters — are fully present in the world and in the
data the viewer's browser receives, but the viewer never renders them, so kitties
visibly play with invisible friends. A developer can flip a debug toggle in the viewer
to reveal greebles during development.

**Why this priority**: Pure charm — it makes the sandbox feel alive and mysterious.
It layers on top of elements, chasing, and the viewer, so it comes after the world
works.

**Acceptance Scenarios**:

1. **Given** a world containing a greeble, **When** a viewer requests the world state
   or receives a live update, **Then** the greeble is present in the data like any
   other element, but the viewer does not render it.
2. **Given** a kitty chasing or playing with a greeble, **When** the viewer watches,
   **Then** the kitty visibly chases and plays with an empty tile.
3. **Given** the viewer's debug toggle is enabled, **When** a greeble exists,
   **Then** it is rendered.

---

### Edge Cases

- A kitty attempts to move off the grid edge or onto a tile occupied by another
  kitty: the move resolves to idle (never an error, never a stacked kitty).
- Every tile is occupied when a spawn is required: spawn is deferred to subsequent
  environment phases until a tile frees up; the safeguard obligation remains
  outstanding and is fulfilled at the first opportunity.
- A kitty meows while the message type is on cooldown: the meow is silently dropped
  but still consumes the kitty's action for the tick.
- Chow reaches zero servings mid-tick: the element despawns during the environment
  phase; if the type falls below its minimum, a replacement spawns.
- Two kitties both try to eat the last serving in the same tick: actions apply in
  stable kitty-id order; the first consumes the serving, the second's action resolves
  to idle.
- A sleeping kitty's sunbeam expires mid-sleep: sleep continues at the normal
  (non-sunbeam) rate.
- A co-sleeping or co-resting partner moves away: the remaining kitty continues the
  action solo (no Cuddle benefit from that tick onward).
- A behavior exceeds its time budget, throws an error, or returns an action that is
  invalid for the current state: the engine substitutes the fallback (default
  built-in behavior, or idle), affecting only that kitty for that tick.
- The distress event log grows unboundedly during a long run: retention is bounded
  (see Assumptions) so memory and payloads stay stable.
- A viewer's live connection drops: the viewer re-fetches a full state snapshot and
  re-subscribes; the simulation is unaffected.
- The server is killed ungracefully between periodic saves: on restart the world
  resumes from the most recent valid save; up to one save-interval of progress may
  be lost, but the loaded state must still pass all invariant validation.
- A chase target (bug, greeble, or friend) disappears or moves before the action
  applies: the action resolves to idle for that tick.
- World is configured so small that kitties plus minimum elements exceed available
  tiles: the configuration is rejected at startup with a clear error.

## Requirements *(mandatory)*

### Functional Requirements

#### World & Time

- **FR-001**: The world MUST be a rectangular grid of tiles, default 32×32, with
  width and height configurable at startup.
- **FR-002**: The simulation MUST advance on a fixed tick, default 800 ms per tick,
  configurable at startup only (no live speed changes in the MVP).
- **FR-003**: Each tick MUST execute in this fixed order: (1) snapshot the world and
  let all behaviors decide against that same snapshot; (2) apply actions in stable
  kitty-id order; (3) environment phase — bug/greeble movement, expiry, consumption
  cleanup, spawn-to-minimum, safeguard spawning; (4) needs increase, happiness is
  recomputed, distress events are recorded, invariants are asserted; (5) the new
  state is published to connected viewers.
- **FR-004**: All randomness MUST flow through a single seeded random source; given
  the same seed, configuration, and built-in behaviors, the same number of ticks
  MUST always produce the same world state. Randomness consumed during concurrent
  behavior decisions MUST be derived deterministically (independent of decision
  completion order or wall-clock timing).

#### Configuration

- **FR-005**: The world MUST be initialized from a configuration file covering world
  size, tick duration, random seed, kitty roster (id, name, starting position,
  behavior name), element rules (min/max counts, permanence/time-to-live), and all
  simulation constants (need rates, action effects, thresholds, weights, cooldowns).
- **FR-006**: Every simulation constant named in this spec MUST be configurable with
  the documented default; no such constant may be hard-coded.
- **FR-007**: The system MUST reject invalid configurations at startup with a clear
  error naming the offending value and the allowed range. Invalid includes: fewer
  than 2 kitties; element min/max outside hard bounds; malformed or missing required
  fields; kitty starting positions off-grid or duplicated; worlds too small to hold
  the configured kitties and element minimums.

#### Environment Elements

- **FR-008**: The world MUST support five element types, each occupying one tile:
  water (drinkable; permanent by default), chow (finite servings; despawns when
  empty; may also expire on a timer), bug (moves 1 tile every 2 ticks in a random
  direction; expires after a lifetime), greeble (moves 1–2 tiles per tick, changing
  direction frequently; present in all data but never rendered by the viewer by
  default; always perceivable by kitties), and sunbeam (resting/sleeping tile with
  enhanced sleep recovery; expires and respawns elsewhere).
- **FR-009**: Each element type MUST have configurable minimum and maximum counts,
  constrained by hard bounds derived from world size: hard minimum 1 per type (0
  allowed for greebles) and hard maximum `floor(world area / 32)` per type.
  Configured values outside the hard bounds MUST be rejected at startup.
- **FR-010**: Elements MUST be either permanent or expire after a configurable
  time-to-live in ticks.
- **FR-011**: When an element type falls below its configured minimum (through
  expiry or consumption), a new element of that type MUST spawn during the
  environment phase at a randomly chosen unoccupied tile.
- **FR-012**: Safeguard (constitution): whenever any kitty's need exceeds the
  safeguard threshold (default 75) and no reachable resource satisfying that need
  exists, the environment MUST spawn one on the next environment phase, regardless
  of configured maximums.

#### Kitties, Needs & Happiness

- **FR-013**: The world MUST always contain at least 2 kitties; kitties MUST never
  be removed, and no death, despawn, health, or damage mechanic may exist for them.
  Expiry applies only to environment elements. A runtime assertion MUST re-verify
  the population invariant every tick.
- **FR-014**: Each kitty MUST have six needs — Eat, Drink, Sleep, Play, Cuddle,
  Bath — each a bounded value from 0 to 100 that never leaves that range. No
  negative state beyond need pressure (no pain, injury, sickness, or starvation)
  may exist.
- **FR-015**: Each need MUST rise by a configurable global per-need rate every tick
  (defaults per tick: Eat 0.5, Drink 0.7, Sleep 0.3, Play 0.4, Cuddle 0.25,
  Bath 0.2).
- **FR-016**: Happiness MUST equal 100 minus the weighted average of the six needs
  (default weights: Eat 0.25, Drink 0.25, Sleep 0.15, Play 0.15, Cuddle 0.10,
  Bath 0.10), clamped to a configurable floor (default 5); it MUST never reach zero.
- **FR-017**: When any need crosses from below to at-or-above the distress
  threshold (default 90), exactly one distress event (kitty id, need, tick) MUST be
  recorded and exposed via the API; no further event is recorded for that kitty and
  need until the need drops below the threshold and crosses it again. Distress
  events are a signal only — no punishment mechanic may attach to them.
- **FR-018**: "Friend" MUST mean any other kitty; partner interactions MUST use
  adjacency (Chebyshev distance ≤ 1). Kitties MUST have full awareness of the world
  when deciding.

#### Actions

- **FR-019**: Each kitty MUST take exactly one action per tick, drawn from: move
  (one tile north/east/south/west), rest (alone or with an adjacent friend), sleep
  (multi-tick; alone or with an adjacent friend), groom (self or adjacent friend),
  eat, drink, chase (bug, greeble, or friend), play (bug, greeble, or friend), purr,
  meow (one of the defined messages), and idle.
- **FR-020**: Action legality and effects (all magnitudes configurable defaults):
  - move: blocked moves (grid edge or kitty-occupied destination) resolve to idle.
  - rest: lying down; with an adjacent friend it also lowers both kitties' Cuddle.
  - sleep: lowers Sleep ~5 per tick (~8 per tick in a sunbeam); adjacent co-sleeping
    also lowers Cuddle; sleep spans multiple ticks and is interruptible by the
    kitty's behavior.
  - groom: lowers own Bath ~30; grooming an adjacent friend lowers the friend's
    Bath and the groomer's Cuddle.
  - eat: requires being on or adjacent to chow; consumes one serving; lowers Eat
    ~40.
  - drink: requires being on or adjacent to water; lowers Drink ~40.
  - chase: moves one step toward the target.
  - play: requires adjacency/co-location with the target; lowers Play ~25 (both
    kitties when the target is a friend).
  - purr: allowed only when Happiness exceeds the purr threshold (default 70) or
    Happiness rose this tick.
  - idle: always legal; the universal safe fallback.
- **FR-021**: Any action that is illegal for the current world state MUST resolve to
  idle for that tick — never an error state.

#### Communication

- **FR-022**: Kitties MUST be able to meow exactly these messages: "I want to
  eat!", "I want to drink!", "Follow me!", "I want to play!", "I want to cuddle!",
  plus Purr ("I am happy"). Meows MUST be visible to all kitties in their decision
  context and to viewers as speech bubbles.
- **FR-023**: Each message type MUST have a per-kitty cooldown that scales inversely
  with severity: default 15 ticks, dropping to 5 ticks while the related need is at
  or above 75. A meow attempted during cooldown MUST be silently dropped while still
  consuming the kitty's action for that tick.

#### Pluggable Behavior

- **FR-024**: Each kitty MUST be assigned a named behavior strategy in
  configuration; different kitties MUST be able to use different behaviors in the
  same world.
- **FR-025**: A behavior MUST receive a read-only decision context — the kitty's own
  full state plus the start-of-tick world snapshot including other kitties'
  positions and recent meows — and return exactly one proposed action.
- **FR-026**: The engine MUST validate every proposed action against the rules and
  current world state. Invalid, malformed, late, or absent proposals MUST resolve to
  a safe no-op (idle) — never an error state, never a rule violation.
- **FR-027**: External (non-built-in) behavior decisions MUST be subject to a
  wall-clock time budget (default: 50% of the configured tick duration, i.e.
  400 ms at defaults; configurable) with automatic fallback to the default
  built-in behavior;
  a slow or failed behavior may degrade only that kitty's cleverness, never the
  tick loop or the constitution. Built-in behaviors run synchronously within the
  tick and are exempt from the wall-clock budget, so same-seed determinism holds by
  construction; the timeout-and-fallback path MUST still be covered by dedicated
  tests using a deliberately slow or faulty test behavior.
- **FR-028**: The MVP MUST ship at least two contrasting behaviors: `needs_driven`
  (pursues the highest-pressure need with mild randomness; also the fallback) and
  one contrasting strategy (e.g., `playful`, over-weighting Play/chase) to
  demonstrate per-kitty variation.
- **FR-029**: The behavior interface MUST be designed so a future implementation can
  call an external resource (script, remote API, or local service) without engine
  changes: decisions are asynchronous, time-budgeted, and engine-validated.

#### Persistence

- **FR-030**: The world MUST run in memory and save its complete state to a single
  file on graceful shutdown and every N ticks (default 100, configurable). The
  saved state MUST include the random source's state so determinism survives
  restarts.
- **FR-031**: On startup, if a saved world exists, it MUST be loaded and validated
  against constitution invariants and compatibility with the current configuration;
  if none exists, a fresh world MUST be generated. A fresh-start option MUST ignore
  any saved world.
- **FR-032**: A saved world that fails validation MUST cause startup to fail with a
  clear error explaining the problem and how to proceed; the system MUST NOT
  silently discard a saved world.

#### API & Live Updates

- **FR-033**: The server MUST expose read-only API access to: the full world state
  (greebles included — invisibility is a viewer rendering rule, not a data filter),
  the kitty list, an individual kitty by id, recorded distress events, and the
  active configuration.
- **FR-034**: The server MUST push the full world state to subscribed viewers every
  tick over a live connection; a viewer MUST be able to fetch a full snapshot once
  and then subscribe for per-tick updates.

#### Viewer

- **FR-035**: The system MUST serve a single-page web viewer that renders the tile
  grid, elements, and kitties in a simple, cute style (basic shapes or emoji
  suffice), including meow speech bubbles, a per-kitty happiness indicator, and
  visible sleeping/resting poses.
- **FR-036**: The viewer MUST be strictly read-only: it renders received state and
  never computes, predicts, or mutates simulation outcomes. All game logic lives on
  the server.
- **FR-037**: The viewer MUST NOT render greebles by default and MUST provide a
  debug toggle that reveals them during development.

### Key Entities

- **World**: The complete simulation state — grid dimensions, current tick, kitties,
  elements, recent meows, distress events, and random source state.
- **Tile / Position**: A grid coordinate. Tiles may hold at most one kitty and at
  most one element; a kitty and an element may share a tile.
- **Kitty**: A permanent inhabitant with id, name, position, six needs, happiness,
  current activity (e.g., sleeping), and an assigned behavior name. Never removed.
- **Need**: A bounded 0–100 pressure (Eat, Drink, Sleep, Play, Cuddle, Bath) with a
  global per-need rise rate.
- **Element**: An environment object on a tile — water, chow (with servings), bug,
  greeble, or sunbeam — with optional time-to-live and per-type min/max counts.
- **Action**: A kitty's single per-tick act (move, rest, sleep, groom, eat, drink,
  chase, play, purr, meow, idle) with configured effect magnitudes.
- **Meow / Message**: One of six fixed communications, visible to all kitties and
  viewers, subject to per-kitty per-type cooldowns.
- **Behavior**: A named strategy that maps a read-only decision context to one
  proposed action, subject to engine validation, a time budget, and fallback.
- **Distress Event**: A record (kitty id, need, tick) emitted when a need is at or
  above the distress threshold; observability only.
- **Configuration**: The startup definition of the world — size, tick duration,
  seed, kitty roster, element rules, and all simulation constants.
- **Saved World (Snapshot)**: The persisted form of the World, including random
  source state, written periodically and on graceful shutdown, validated on load.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Within 1 minute of a first-time start with the default configuration,
  a viewer sees a rendered world with at least 2 kitties and at least one of each
  visible element type; within 10 minutes of watching at default speed, every core
  kitty activity (moving, eating, drinking, sleeping, playing, grooming, meowing)
  has been observed.
- **SC-002**: An automated invariant suite drives randomized worlds for at least
  10,000 ticks and completes with zero violations: no kitty removed, population
  always ≥ 2, all needs within 0–100, happiness never below its floor, and every
  safeguard obligation fulfilled at the first available opportunity. This suite is
  a required CI gate.
- **SC-003**: After a graceful stop and restart, the resumed world matches the saved
  world exactly (kitty positions, needs, elements, tick count, random state), and
  its subsequent evolution is identical to an uninterrupted run with the same seed
  and configuration.
- **SC-004**: Two runs with identical seed, configuration, and built-in behaviors
  produce identical world states after any equal number of ticks, 100% of the time.
- **SC-005**: Two kitties configured with the two shipped behaviors show measurably
  different action distributions over a 1,000-tick observation window (e.g., the
  playful kitty performs at least 50% more play/chase actions than the needs-driven
  kitty under the default configuration).
- **SC-006**: 100% of invalid configurations (fewer than 2 kitties, min/max outside
  hard bounds, malformed fields, off-grid or duplicate starting positions,
  over-full worlds) are rejected at startup with an error that names the offending
  value and the allowed range.
- **SC-007**: Greebles appear in 100% of world-state payloads in which they exist
  and in 0% of default viewer renderings; enabling the debug toggle reveals them.
- **SC-008**: Connected viewers receive each new world state within one tick period
  of its computation; a viewer that reconnects after a dropped connection resumes
  live viewing without operator intervention and without affecting the simulation.

## Assumptions

- **Reachability**: the MVP grid has no impassable terrain, and blocked-by-kitty
  tiles change constantly, so a resource is "reachable" if it exists anywhere on the
  grid. The safeguard check therefore reduces to existence of a satisfying resource.
- **Sleep continuation**: a sleeping kitty continues sleeping by engine default until
  its behavior proposes a different action or its Sleep need reaches 0; behaviors may
  interrupt sleep at any tick.
- **Distress event retention**: distress events are kept in memory with a bounded,
  configurable retention (default: the most recent 1,000 events) and are included in
  saved world state; long-term historical storage is out of scope.
- **Recent meows**: the decision context and viewer show meows from a bounded recent
  window (default: the last 10 ticks); older meows expire from view.
- **Invalid saved world**: startup fails safe with a clear error rather than silently
  regenerating, so an operator never loses a world unknowingly (aligned with the
  constitution's protective stance).
- **Ungraceful termination**: recovery from the most recent periodic save is
  acceptable; at most one save-interval of progress is lost.
- **Element/kitty placement**: elements spawn only on tiles unoccupied by other
  elements; kitties and elements may share a tile (that is how eating, drinking, and
  sunbeam sleeping work); kitties never share a tile with each other.
- **Purr and meow**: purring is the "I am happy" communication and is subject to the
  same cooldown mechanism as other messages (severity scaling does not apply since no
  need is related; the default 15-tick cooldown applies).
- **Single world per server**: one server instance runs exactly one world; multiple
  worlds are out of scope.
- **Audience**: viewers are on the same machine or trusted local network; the API and
  viewer are unauthenticated and read-only in the MVP.
- **Deployment note**: the user's acceptance criteria reference a specific runtime
  toolchain for starting the server; technology choices are deferred to the
  implementation plan and do not constrain this specification.

## Out of Scope for the MVP (Later Features)

The following are explicitly out of scope. MVP design decisions must avoid *blocking*
them but must not implement them:

- Age, fur, and eye stats; per-kitty need rates
- Friendship/relationship tracking; friend-proximity preference
- Day–night cycle and moonbeams
- Food types and desirability modifiers; water-near-food rules
- Ear/tail affect displays
- Dynamic in-game speed changes
- Kittens; expanding worlds
- Additional communications; state sharing between worlds
