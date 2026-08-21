# Feature Specification: Bugs 2.0 — the roam-cell tether

**Feature Branch**: `039-bugs2-tether`

**Created**: 2026-08-21

**Status**: Draft

**Input**: Owner-ratified bugs-2.0 package (2026-08-21), consolidated in
`experiments/bugs2-spec-input-2026-08-21.md`: adopt the 4×4 roam-cell
tether for bugs, keep timed lifetimes at a longer value, change no
reward values, and leave the scripted behaviors untouched. Motivation
and economics: trained minds exhibit essentially zero bug play (the
banked zero-play baseline) because hunts are long, unreliable, and
subject to invisible expiry — while the measured pair-payment structure
means a duet always pays more, so making hunts cheap cannot overshoot
into bug-grinding. The full brainstorm-and-review record lives in the
input document and the chase census beside it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A bug keeps to its patch (Priority: P1)

Today a bug wanders the whole world at random, so a cat that starts a
chase is pursuing a moving target that can lead it anywhere, and a
watcher who spots a bug by the pond has learned nothing about where
bugs will be. With the tether, the world is divided into small
fixed-position cells, and a bug spends its whole life inside the cell
it was born in. Bug locations become durable facts: a patch of the
meadow *has bugs*, a cat that visits the patch finds them there, and
the endgame of a hunt happens in a bounded arena where the bug's
escape options run out at the cell walls.

**Why this priority**: This is the core of the arc — the single
mechanism the owner adopted. Everything else in the package (the
lifetime change, the acceptance measurements) assumes it.

**Independent Test**: Run a world with the tether enabled and track
every bug over its full lifetime across many seeds: no bug ever
occupies a tile outside the cell it started in. Disable the tether and
confirm the world behaves exactly as it does today.

**Acceptance Scenarios**:

1. **Given** a world with 4×4 roam cells enabled for bugs, **When**
   any bug moves on any tick, **Then** its destination lies inside the
   same cell as its current position — over any horizon, a bug never
   stands outside the cell it was born into.
2. **Given** a bug adjacent to its cell boundary, **When** its
   movement draw points outward, **Then** the bug simply does not move
   that tick (exactly as if the step had been blocked), and its
   movement cadence is otherwise unchanged.
3. **Given** a world with the tether not configured, **When** the
   world runs from a fixed seed, **Then** its evolution is
   indistinguishable from today's behavior — the feature absent means
   nothing changed.
4. **Given** a tethered world, **When** a greeble moves, **Then** it
   roams the whole world exactly as today — the tether applies to
   bugs only.

---

### User Story 2 - Worlds that don't divide evenly (Priority: P2)

The served world is 20×20 and divides into exactly 25 4×4 cells, but
the family of benchmark and training worlds includes sizes that do not
divide evenly (26×26 is the live example). Whoever configures such a
world gets well-defined behavior at the edges rather than a surprise:
the cell grid is anchored at the world's origin, and the leftover rows
and columns form smaller edge cells.

**Why this priority**: The acceptance grid explicitly tests 26×26, and
the tail-benchmark family lives there. Undefined edge behavior would
make those measurements meaningless.

**Independent Test**: Run a 26×26 world with 4×4 cells: bugs born in
interior cells keep 4×4 ranges; bugs born in the two-wide edge strips
keep those smaller ranges; no tile belongs to more than one cell and
no tile belongs to none.

**Acceptance Scenarios**:

1. **Given** a 26×26 world with cell size 4, **When** the partition is
   derived, **Then** it is a grid of 4×4 cells from the origin with
   4×2, 2×4, and 2×2 remainder cells along the far edges — every tile
   in exactly one cell.
2. **Given** a bug born in a remainder cell, **When** it lives out its
   life, **Then** it stays inside that smaller cell, same rule, no
   special case.
3. **Given** a world smaller than one cell in either dimension,
   **When** the world runs, **Then** the whole world is a single cell
   and bug behavior is today's behavior (already bounded by the map).

---

### User Story 3 - The world's operator chooses the ecology (Priority: P2)

The tether is a property of a *world*, not of the engine: the served
world adopts 4×4, the acceptance grid needs arms with 3×3 cells, other
lifetimes, and no tether at all, and training worlds will want the
same choices. The operator sets the bug roam-cell size in the world's
configuration; leaving it unset means bugs roam free exactly as they
do today. In the same package, the served world's bug lifetime rises
from 300 to 600 ticks, so patches relocate on a calm cadence (roughly
every eight real-world minutes) instead of churning.

**Why this priority**: Without the configuration surface, the
acceptance grid cannot run its arms, and the served world cannot adopt
the package. It is second only to the mechanism itself.

**Independent Test**: Boot worlds with the cell size at 3, at 4, and
absent, and with bug lifetime at 300 and 600, and confirm each
combination takes effect from configuration alone with no other
change; confirm invalid values are refused at load with the offending
value named.

**Acceptance Scenarios**:

1. **Given** a configuration that sets a bug roam-cell size, **When**
   the world boots, **Then** bugs obey that cell size; **Given** the
   key is absent, **Then** bugs roam free (today's behavior, exactly).
2. **Given** a configuration setting the served package (cell 4, bug
   lifetime 600), **When** the world runs, **Then** bug expiry and
   respawn behave exactly as today except the lifetime — the respawn
   machinery, placement preferences, and lifetime jitter are
   untouched.
3. **Given** a configuration with a nonsensical cell size (zero, one,
   or negative), **When** the world loads, **Then** it is refused
   with a message naming the field and the offending value — a cell
   of one would silently freeze every bug in place, which is a
   different world than anyone asked for.

---

### Edge Cases

- A bug standing exactly on a cell corner has two of four directions
  outward: both are lost steps; the bug still moves on its cadence
  when the draw points inward. A 1-in-4 chance of motion per moving
  tick at a corner is accepted behavior, not a defect.
- A saved world from before this change loads normally (no new
  persisted state, no fingerprint movement) and its existing bugs
  become tethered to whatever cell they stand in at load — mid-life
  adoption, by the same rule that governs newborns.
- A bug's spawn placement is unchanged (spread preference, interior
  bias, lifetime jitter); the cell is simply derived from wherever the
  spawn lands. Nothing steers spawns toward "good" cells this arc.
- Another element or a cat standing on a bug's only inward tile:
  the step is lost to occupancy exactly as today; occupancy rules do
  not change.
- The tether never applies to greebles, chow, water, or sunbeams —
  bugs only, by ruling. Greebles remain the free-range, mostly
  uncatchable wanderers by design.
- Cat behavior is untouched: chase, play, patience, and exclusion
  rules are byte-for-byte today's. Only the prey's world changed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The world MUST support confining each bug's movement to
  a fixed axis-aligned cell of the world grid: a bug never moves to a
  tile outside the cell containing its current position, and since it
  can never leave, that cell is the one it occupied at birth (or, for
  a bug loaded from an older save, at load).
- **FR-002**: The cell partition MUST be anchored at the world origin
  and tile the whole world: with cell size N, interior cells are N×N,
  and worlds whose width or height is not a multiple of N have
  smaller remainder cells along the far edges. Every tile belongs to
  exactly one cell; a world smaller than N in a dimension is one cell
  across that dimension.
- **FR-003**: A movement draw that points outside the bug's cell MUST
  cost the step (the bug stays put that tick) and MUST NOT be redrawn
  or otherwise compensated — identical in kind to today's blocked
  step, so movement cadence, the number of random draws per tick, and
  determinism from a fixed seed are all preserved.
- **FR-004**: The bug roam-cell size MUST be a world-configuration
  choice: absent means unbounded roaming (today's behavior,
  indistinguishable), and a set value applies to bugs only. The
  served world adopts 4. Greebles MUST remain unbounded regardless of
  the setting.
- **FR-005**: Configuration validation MUST refuse a roam-cell size
  that is zero, one, or negative, naming the field and the value —
  a one-tile cell silently immobilizes every bug and is refused
  rather than served.
- **FR-006**: The served world's bug lifetime MUST change from 300 to
  600 ticks. Expiry, respawn to minimums, spawn placement, and
  lifetime jitter MUST be otherwise untouched. Greeble lifetime is
  unchanged this arc.
- **FR-007**: The change MUST introduce no new persisted world state:
  saved worlds from before the change load without migration, their
  bugs adopting the tether at load position, and the world
  save-compatibility fingerprint MUST NOT move.
- **FR-008**: The change MUST NOT alter any reward value, any
  observation/action/mask schema, any scripted behavior, or any cat
  decision rule. Scripted behaviors are measurement infrastructure
  (anchors, character definitions, the census's skill rows): the
  world changes, the rulers don't.
- **FR-009**: With the roam-cell configuration absent, a world run
  from a fixed seed MUST evolve identically to the pre-change engine
  — the feature's presence in the codebase is unobservable until
  configured.
- **FR-010**: The acceptance-economics division of proof follows the
  house pattern: this arc proves *confinement and inertness*
  (FR-001–FR-009) with engine-level tests; Experiments' pre-registered
  chase-census grid proves the *economics* (their instrument, their
  arms, run against a branch build of this change before the served
  world adopts it).

### Key Entities

- **Roam cell**: a fixed axis-aligned region of the world grid,
  derived from world dimensions and a configured size — not stored,
  not persisted, not visible in any payload; purely a constraint on
  bug movement.
- **Bug**: the tethered critter. Gains no new attributes; its cell is
  implied by its position.
- **World configuration, elements section**: gains one optional
  roam-cell size for bugs; the served world's bug lifetime value
  changes 300 → 600.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across the full acceptance geometry set (20×20 and
  26×26) and at least 10 seeds each, zero tether violations: no bug
  ever observed outside its birth cell over full lifetimes.
- **SC-002**: With the tether unconfigured, a seeded world's full
  evolution is identical to the pre-change engine's over at least
  10,000 ticks — not statistically similar, identical.
- **SC-003**: Bug movement cadence under the tether matches today's
  measured cadence (a bug attempts a move every other tick;
  lost-to-boundary steps replace lost-to-occupancy steps, never a
  redraw), verified by direct count over seeded runs.
- **SC-004**: Experiments' pre-registered acceptance grid, run on a
  branch build, clears the ratified bars — unskilled bug hunt value
  above the solo-play line (>10 where today reads 7.9), skilled hunt
  value inside the opportunistic corridor (between self-duet and
  team-duet bands), and expiry-ruin at or under ~1% of engaged hunts
  at lifetime 600 — with the pre-registered cell-size decision rule
  (largest cell clearing the first bar) landing on the shipped size.
- **SC-005**: The definition-of-done re-baselines exist on the
  post-change world before the arc is called shipped: fresh scripted
  and playful anchors re-banked, the zero-play baseline re-banked,
  the tail-benchmark divergence note recorded, and the fog
  before/after confound note recorded.

## Assumptions

- **Greeble lifetime stays 300.** The ratified lifetime discussion
  (ruin, patch relocation) is about bugs; nothing in the package
  needs greeble expiry to change, so it doesn't. Flag at spec review
  if the owner intended symmetry.
- **Lifetime 600 is confirmed as a formality at spec review** (the
  input doc's own instruction): the derivation says anything in
  [450, 900] plateaus, the census verifies, and 600 rode the ratified
  package unobjected.
- **The cell grid is world-aligned, not bug-centered** — cells are
  fixed regions of the map (per the owner's "4x4 grid" framing and
  the review's statelessness grounds), so a bug born near a cell edge
  simply has a lopsided territory. Accepted.
- **The pounce is fully out of scope** — deferred by ruling as the
  mechanics fallback (revisited only if the census grid fails) and as
  a possible Client-side charm arc independent of this one.
- **A remaining-lifetime observation field is out of scope** — it is
  an observation-schema bump reserved for fog-era machinery; short
  hunts make unobservable decay rare enough to accept (the ~1% ruin
  bar in the acceptance criteria is the check on that acceptance).
- **Sequencing**: this arc merges only after the phase-1 world is
  serving (the --fresh has run) and its acceptance grid has passed on
  the branch; the served world adopts the package by configuration at
  a deploy the owner gates, as always. Downstream (re-evaluating
  incumbents, corpus re-collection, next-generation training on the
  post-change world) belongs to Experiments per the D-003 sequencing
  rule and is out of this arc's scope beyond SC-005's re-baseline
  gate.
- **Dependency**: the acceptance grid depends on Experiments' census
  tool patch (tagging expiry-abandons separately from
  patience-abandons); Experiments owns it and lands it before the
  first branch build needs it.
