# Feature Specification: Water-Averse Pathing

**Feature Branch**: `009-orthogonal-interactions` (shared — specced alongside 009
and 011 as one QoL batch, at the owner's direction)

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "Let's make the cost for pathing across water higher.
I'd like for kitties to prefer not to cross water (but I also don't want to risk
them getting stuck). Also a 'swim' animation for crossing water (later, not a
high priority)." (Backlog P1: crossing stays *legal* — only the *preference*
changes — with a named cost in the `tile_cost` family; the swim pose is parked
as its own later, low-priority item.)

## The gap being closed

Movement is terrain-blind today: a kitty bound for a chow bowl will stroll
straight through a pond as if it were grass. Cats famously would not. After
this change, kitties treat stepping onto water as expensive and walk around
ponds when a dry route is reasonable — visibly skirting the shorelines the
meadow now draws so nicely — while a truly necessary crossing is still just a
paddle, never a wall. The anti-stuck guarantee is structural: the engine's law
does not change at all (wading stays legal, so no layout can ever trap a
kitty); only the kitties' *taste* changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Kitties skirt their ponds (Priority: P1)

A viewer watches a hungry kitty whose bowl lies on the far side of a pond.
Instead of splashing straight through, the kitty walks around the shoreline —
a slightly longer route it plainly prefers — and arrives dry. Across a session,
kitties are seen wading only when water genuinely blocks every sensible route.

**Why this priority**: This is the feature — the owner's stated preference,
and the visible charm.

**Independent Test**: In a crafted world with a pond strip between a kitty and
its target and a dry detour of modest extra length, the kitty takes the dry
route every time (deterministically). Remove the detour, and it wades.

**Acceptance Scenarios**:

1. **Given** a target reachable by a dry detour a few steps longer than the
   wet shortcut, **When** the kitty travels, **Then** it takes the dry detour
   and never enters a water tile.
2. **Given** a target reachable *only* by crossing water, **When** the kitty
   travels, **Then** it crosses — the preference yields, the kitty is never
   stuck, and it reaches its target.
3. **Given** a kitty standing on a water tile (a fresh puddle spawned nearby,
   or an old save), **When** it next moves, **Then** dry steps are preferred
   and it gets out of the water rather than lingering.
4. **Given** a viewer watching the 008 meadow, **When** kitties travel around
   ponds, **Then** the detours trace the drawn shorelines — the preference
   operates on exactly the water tiles the viewer sees merged into ponds.

---

### User Story 2 - Distant targets are priced honestly (Priority: P2)

A kitty choosing between two bowls should know that the one across the pond is
really a detour. When need-selection weighs "how far is relief", a target whose
route crosses water counts the crossing cost, so a slightly nearer bowl behind
a pond can lose to a slightly farther bowl on dry land — matching the walk the
kitty will actually take.

**Why this priority**: Without it, a kitty picks the across-the-pond bowl by
raw distance, then pays the detour anyway — a visible mismatch between choice
and cost. Valuable, but the feature stands without it (US1 alone changes the
walking).

**Independent Test**: Two same-type targets, one nearer but across water, one
farther but dry, tuned so the crossing cost tips the score: the kitty picks
the dry one, deterministically.

**Acceptance Scenarios**:

1. **Given** a bowl 4 steps away across a pond and a bowl 6 steps away on dry
   grass, with the water cost pricing the crossing above 2 steps, **When** the
   kitty selects a target, **Then** it picks the dry bowl.
2. **Given** an urgent need and only the across-water bowl in the world,
   **When** the kitty selects, **Then** it still goes — pricing never makes
   relief unreachable, it only orders choices.

---

### User Story 3 - Never stuck, never trapped (Priority: P3)

An owner trusts that a preference can never harm a kitty. However the water
lies — rings, walls, a kitty spawned mid-pond — every kitty always has its
legal moves, safeguard relief still arrives in time, and the long-run welfare
suite shows the same contentment as ever. A paddling kitty is the fallback,
never the trap.

**Why this priority**: Non-negotiable, but guaranteed by construction (the
engine's movement law is untouched); this story is verification.

**Independent Test**: The invariant/property suite, including watery layouts
(dense water worlds, water-ringed kitties and targets), passes: needs bounded,
relief consumed in time, no kitty immobile when a legal move exists.

**Acceptance Scenarios**:

1. **Given** a kitty fully ringed by water tiles, **When** it needs to travel,
   **Then** it wades out — exactly as today — and reaches relief.
2. **Given** any seeded world run twice, **When** compared tick by tick,
   **Then** the runs are identical (the preference is deterministic; no new
   randomness).
3. **Given** the shipped world files without the new setting, **When** the
   server starts, **Then** it starts cleanly with a sensible documented
   default — no config edits forced.

---

### Edge Cases

- **Drinking is unaffected**: kitties drink from *beside* water, never from on
  top of it, so avoiding water tiles never gets between a kitty and its drink
  — the preference and the need pull the same direction (right up to the
  shore, not into the pond).
- **Local choices, not a map solver**: kitties choose step by step, as they
  always have. The preference weighs each candidate step; it does not promise
  globally optimal routes around elaborate mazes — a kitty may occasionally
  wade where a perfect navigator would have found a long dry way. That is
  cat-like, and never worse than today's always-wade.
- **All dry steps blocked by friends**: a wet step that makes progress beats
  standing still forever; the preference is a cost, not a prohibition, so
  crowding resolves the way it does today.
- **Water under a kitty**: elements spawn on free tiles, but old saves or
  future spawn changes may put a kitty on water; the kitty simply prefers its
  way off (US1 scenario 3). Nothing special is stored.
- **Composition with orthogonal-only interactions (009)**: both features
  touch travel judgment. Distances are walking steps (009); water adds a
  per-wet-step surcharge on top (010). Specced separately, designed to
  compose.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a kitty chooses its next step, a step onto a water tile
  MUST cost extra — by a named, configured amount — so that among steps making
  equal progress, dry beats wet, deterministically.
- **FR-002**: The engine's movement law MUST NOT change: stepping onto water
  remains legal exactly as today (Article IV — the preference lives in
  behavior proposals; the engine never forbids the crossing). This is the
  anti-stuck guarantee, by construction.
- **FR-003**: The extra cost MUST be a named configuration value in the
  existing travel-pricing family (alongside the cost of a plain step),
  validated at startup, documented in the shipped world files, and defaulted
  sensibly when absent — existing config files keep working unedited.
- **FR-004**: Need-selection's travel estimates SHOULD count water along the
  way to a candidate target, so relief across a pond scores like the detour it
  really is; the estimate MUST be deterministic and MUST never make an
  only-option target unreachable or unpickable.
- **FR-005**: A kitty standing on water MUST prefer stepping off it, all else
  equal — water's surcharge applies to staying wet, not just getting wet.
- **FR-006**: Determinism MUST be preserved: the preference introduces no new
  randomness, tie-breaks remain fixed, and same seed still means same world.
- **FR-007**: Article I MUST be re-verified under watery layouts: safeguard
  relief remains reachable and consumed in time even when water lies between
  every kitty and everything it needs.
- **FR-008**: The served API and the viewer MUST NOT change: the feature is
  visible purely as kitties walking around ponds. (The swim pose for a wading
  kitty is a separate, later, low-priority backlog item — explicitly out of
  scope here.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In crafted detour worlds (dry route ≤ a few steps longer than
  the wet shortcut), kitties take the dry route in 100% of runs; with the
  detour removed, they cross 100% of the time — never stuck, both directions
  deterministic.
- **SC-002**: Across property-suite runs of tens of thousands of ticks over
  randomized worlds including water-heavy layouts, every constitutional
  guarantee passes: needs bounded, safeguard relief arrives and is consumed,
  happiness floor holds, no kitty is ever unable to act while a legal move
  exists.
- **SC-003**: Watching a demo world with real ponds for one sitting, a viewer
  can point at a kitty visibly walking around a pond it would previously have
  walked through.
- **SC-004**: Two runs of the same seeded world remain tick-for-tick
  identical, before and across a save/restore.
- **SC-005**: Existing world files start unmodified; the new setting appears
  documented in the shipped configs and rejects invalid values (e.g.,
  negative cost) with the standard naming-the-field startup error.

## Assumptions

- The preference is priced, not absolute: a large-but-finite surcharge per wet
  step, tuned so modest detours win and hopeless detours lose. The exact
  default value is a planning/tuning decision judged in a live world.
- Kitties keep their existing step-by-step navigation; this feature adjusts
  its taste, not its sophistication. No route-planning machinery is in scope.
- Travel *estimates* (US2) may approximate water along a route rather than
  compute exact cheapest paths, provided the approximation is deterministic
  and never blocks an only option.
- The swim pose (viewer art for a kitty on a water tile, with its own mini
  gallery gate) stays parked on the backlog — not part of this change.
- Orthogonal-only interactions (009) and sustained purring (011) are separate
  specs sharing this branch; this feature composes with 009's walking-step
  distances and is independent of 011.
