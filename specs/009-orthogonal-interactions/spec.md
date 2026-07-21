# Feature Specification: Orthogonal-Only Interactions

**Feature Branch**: `009-orthogonal-interactions`

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "Right now kitties can interact with things on diagonal
tiles (e.g. eat, sleep, play, cuddle), and I'd like to make it so they can only
interact with adjacent tiles." (Backlog P1, marked *up next*: interactions become
orthogonal-only — the four von Neumann neighbors plus the kitty's own tile —
aligning interaction range with the strictly 4-way movement.)

## The gap being closed

Kitties move only north, east, south, and west — yet today they can eat from a
bowl, drink from a puddle, groom a friend, or catch a chase across a diagonal:
a tile they could not even step toward directly. A watcher who has internalized
how kitties walk sees them act through corners. After this change, a kitty's
reach is exactly the tiles it can step to (plus the tile it stands on), so what
a kitty can *do* finally matches what a kitty can *walk*. Kitties will sometimes
take one extra step to get properly beside their target — that is the point.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reach matches walk (Priority: P1)

A viewer watches a kitty approach a chow bowl. The kitty walks until the bowl
is directly beside it (or it stands on an adjacent tile in one of the four
compass directions) and eats there. It never stops corner-to-corner with the
bowl and eats across the diagonal — and the same holds for drinking, playing
with a bug, grooming a friend, resting together, and pouncing at the end of a
chase.

**Why this priority**: This is the feature — the owner's explicit decision.
Every other requirement exists to support it safely.

**Independent Test**: Run a world for thousands of ticks and record every
interaction with its participants' positions; verify no interaction ever
occurred between a kitty and a target that was diagonal-only (both coordinates
differing). Deliverable value: the world's visible logic is self-consistent.

**Acceptance Scenarios**:

1. **Given** a kitty one diagonal step from a chow bowl, **When** it decides to
   eat, **Then** it first steps to a tile orthogonally beside the bowl and only
   then begins eating.
2. **Given** a kitty orthogonally beside a water puddle, **When** it drinks,
   **Then** the drink proceeds exactly as today.
3. **Given** a kitty chasing a bug that sits one diagonal step away, **When**
   the kitty tries to catch it, **Then** the catch does not land; the kitty
   must close to an orthogonal neighbor (or the same tile) first.
4. **Given** two kitties corner-to-corner, **When** one proposes to cuddle,
   groom, or play with the other, **Then** the engine treats the proposal as
   out of range and the kitty idles or repositions — the interaction never
   fires diagonally.

---

### User Story 2 - Honest travel judgment (Priority: P2)

A viewer sees kitties make sensible choices between distant targets. Because
kitties walk only in compass directions, the true cost of reaching a target is
the sum of its horizontal and vertical distance — today's estimates undercount
anything diagonal. With honest distances, a bowl that *looks* closer but sits
far off-axis no longer wins over a bowl that is genuinely fewer steps away, and
a chase that is actually closing ground is never abandoned as hopeless.

**Why this priority**: Without it, US1 creates visible inconsistency — kitties
would pick targets and judge chase progress by a diagonal shortcut they can
neither walk nor use. It rides the same decision surfaces as US1 and lands in
the same change.

**Independent Test**: Place two same-type targets at equal walking distance but
different diagonal shortcuts; the kitty's choice (by fixed tie-break) is
identical to the choice it would make if both were on-axis. Chase patience:
a pursuit whose walking distance shrinks is never marked hopeless.

**Acceptance Scenarios**:

1. **Given** a hungry kitty with one bowl 6 steps away on-axis and another
   5 walking steps away off-axis, **When** it picks a target, **Then** it picks
   the 5-step bowl — walking steps decide, not straight-line shortcuts.
2. **Given** a kitty chasing a target diagonally offset by one tile in each
   axis, **When** the kitty converts that to a purely orthogonal offset,
   **Then** the chase counts as gaining ground (its patience clock resets)
   rather than stalling.
3. **Given** distance-valued comfort settings (how far is worth walking for a
   nap or a playmate), **When** distances are judged, **Then** the same named
   settings apply, now measured in walking steps.

---

### User Story 3 - The constitution still holds (Priority: P3)

An owner trusts that tightening reach never hurts a kitty. Relief for an urgent
need still always exists and is still always walkable; no kitty can be trapped,
starved, or stuck by the stricter range; long-running worlds show the same
contentment as before, with at most an extra step here and there.

**Why this priority**: Non-negotiable but expected to hold by design — movement
was already 4-way, so nothing reachable becomes unreachable. Verification work,
not new behavior.

**Independent Test**: The full invariant/property suite — with its adjacency
assumptions updated to orthogonal — passes over tens of thousands of randomized
ticks: needs stay bounded, safeguard relief arrives, happiness respects its
floor, no kitty is ever removed or alone.

**Acceptance Scenarios**:

1. **Given** a kitty whose need crosses the safeguard threshold with no relief
   in the world, **When** the safeguard acts, **Then** relief spawns and the
   kitty can walk to an orthogonally-adjacent tile and use it, exactly as
   Article I promises.
2. **Given** any seeded world run twice, **When** the runs are compared tick by
   tick, **Then** they are identical (Article V — determinism untouched).
3. **Given** a world saved before this change with a kitty mid-meal at a
   diagonal to its bowl, **When** that save is resumed under the new rules,
   **Then** the meal ends gracefully on the next tick (the standing
   "counterpart gone" rule) and the kitty re-plans — no error, no stuck state.

---

### Edge Cases

- **Old snapshots**: a world saved under diagonal rules may resume with an
  in-progress interaction whose counterpart is now out of range. The existing
  per-tick counterpart check ends such activities gracefully; nothing crashes
  and no kitty freezes.
- **Crowded targets**: all four orthogonal neighbors of a bowl are occupied by
  other kitties. The kitty waits or re-plans, exactly as it does today when a
  tile is blocked; the engine idles any out-of-range proposal (Article IV).
  Occupancy is momentary — kitties finish and move — so no permanent
  starvation risk is introduced.
- **Corners and edges**: a target on a corner tile has only two orthogonal
  neighbors (an edge tile, three). Still reachable — movement was always
  4-way, so any tile a kitty could reach before, it can reach now.
- **Same-tile interactions**: a kitty standing on its target's tile (a sunbeam
  it naps in, a bug it has landed on) remains in range — "own tile" counts,
  as it does today.
- **Reach-valued settings shift meaning slightly**: a playmate at a far
  diagonal now measures more walking steps than its old straight-line
  distance, so it may fall outside a comfort radius it used to sit inside.
  This is the honest reading of the same numbers; the configured values do
  not change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A kitty MUST be able to interact with a target — eat, drink,
  play with an element or a friend, rest/cuddle with a friend, groom a friend,
  or catch a chase — only when the target is on the kitty's own tile or on one
  of the four orthogonally-adjacent tiles (north, east, south, west).
- **FR-002**: The engine MUST enforce FR-001 in validation: a proposal whose
  target is only diagonally adjacent is out of range and resolves to an idle
  turn, never to the interaction (Article IV — behaviors propose, the engine
  is the law).
- **FR-003**: An in-progress interaction whose counterpart is no longer within
  orthogonal range MUST end gracefully via the existing counterpart-gone rule
  — including interactions restored from snapshots saved under the old
  diagonal rules. Old saves MUST load and continue without error.
- **FR-004**: Built-in behaviors MUST walk to an orthogonally-adjacent tile
  (or the target's own tile, where standing on it is the interaction) rather
  than stopping diagonal to a target and stalling.
- **FR-005**: Every distance used in decisions and progress tracking — travel
  scoring, nearest-target selection and its tie-breaks, playmate and sunbeam
  reach checks, and chase closing-distance/patience — MUST measure true 4-way
  walking distance (the sum of horizontal and vertical offsets), so estimates
  match what walking actually costs.
- **FR-006**: All existing distance-valued configuration keeps its names and
  values (Article VI — no renames, no new mandatory fields); the documented
  meaning of those values becomes "walking steps". Existing world files MUST
  remain valid without edits.
- **FR-007**: The Article I guarantee MUST be re-verified under the stricter
  range: safeguard-spawned relief remains reachable and usable (walk to an
  orthogonal neighbor, then interact), and the invariant/property suite's
  adjacency assumptions are updated to orthogonal and pass.
- **FR-008**: Determinism (Article V) MUST be preserved: identical seeds
  produce identical worlds, all tie-breaks remain fully deterministic, and
  save/restore continues to reproduce the same future.
- **FR-009**: The served API surface MUST NOT change shape: no new fields, no
  removed fields, no viewer changes required. The change is visible only as
  kitties positioning themselves beside — never corner-to-corner with — what
  they use.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across property-suite runs of at least tens of thousands of
  ticks over randomized worlds, zero interactions occur between a kitty and a
  diagonal-only target — every observed interaction pair differs in at most
  one axis by at most one tile.
- **SC-002**: The full invariant/property suite passes with its adjacency
  assertions tightened to orthogonal: needs bounded, safeguard relief
  provided and consumed, happiness floor respected, never fewer than two
  kitties, no kitty removed.
- **SC-003**: A world saved under the previous rules resumes without error,
  and any interaction stranded out of range ends within one tick of resuming.
- **SC-004**: Two runs of the same seeded world remain tick-for-tick
  identical, before and across a save/restore.
- **SC-005**: Existing configuration files (including the owner's three world
  files) start unmodified — zero config edits required by this feature.
- **SC-006**: In a watchable demo world, a kitty approaching a diagonal target
  visibly takes the extra step to stand beside it before interacting — the
  behavior a viewer can confirm with their own eyes within one sitting.

## Assumptions

- "Adjacent" means the four von Neumann neighbors **plus the kitty's own
  tile** — distance zero stays in range, preserving same-tile interactions
  (napping in a sunbeam, landing on a bug). This matches the owner's decision
  recorded in the backlog.
- Distance-valued tunables are *reinterpreted*, not renamed or rescaled: the
  same numbers now denominate walking steps. Marginal behavioral shifts at
  far diagonals (a playmate drifting out of solo-play range, a sunbeam out of
  nap range) are accepted as the honest reading.
- Element spawn *spreading* — the aesthetic "land well away from same-type
  clusters" sampling — is not an interaction and is out of scope; it keeps its
  current distance measure. (Changing it would reshuffle seeded worlds for no
  behavioral gain.)
- Movement itself is untouched: it was already strictly 4-way, which is
  precisely why this change cannot make anything unreachable.
- Water-averse pathing and the swim pose are separate backlog items and out of
  scope here.
- No new configuration is needed: this is an alignment of semantics, not a new
  tunable surface. (Article VI is satisfied because no new constants are
  introduced; existing named values keep their homes.)
