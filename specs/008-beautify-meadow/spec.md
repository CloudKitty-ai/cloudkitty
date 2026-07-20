# Feature Specification: The Meadow Itself — Beautification II, Step 2

**Feature Branch**: `008-beautify-meadow`

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "Beautification step 2: beautify the map itself, in a
way that will work with different world sizes — water, sunbeams, and the world
canvas itself. Direction agreed in the 2026-07-20 ideation (recorded in
BACKLOG.md): organic grass replacing the checkerboard, smooth-shored ponds,
a world edge, sunbeams rendered as light, and worn paths as a keyboard toggle
in the greeble mold."

## Vision

The residents got their glow-up in 005 and their props in 007; the ground they
live on is still a flat checkerboard with square blue puddles. This feature
makes the world worthy of its kitties: a meadow that reads as a real garden —
varied grass, soft-shored ponds, warm pools of light, a framed edge — at any
world size, without the simulation learning a single new fact. Everything here
is decoration in the viewer's eye only: deterministic, repeatable, and derived
purely from where things already are.

One principle anchors every piece: **decoration is a stable function of
position**. The same world must grow the same meadow on every reload and every
restart, the way each kitty keeps its face and each butterfly keeps its wings.
Density scales naturally with area, so a tiny test world and a sprawling one
both read as complete places, never as a repeated wallpaper swatch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An organic meadow replaces the checkerboard (Priority: P1)

Elizabeth opens the viewer and the ground is no longer an alternating grid of
two green squares: it is a meadow — several close shades of grass blended
tile by tile, with sparse tufts, clover, and tiny flowers scattered where they
happen to grow. The tile grid itself is no longer drawn; a debug keystroke can
bring the grid lines back when she wants to see the underlying lattice.

**Why this priority**: the ground is most of the pixels on screen. Every other
piece of this feature (ponds, edge, light, paths) sits on top of this canvas —
it is the step that retires the "programmer art" look, and it is independently
shippable and instantly visible.

**Independent Test**: open the viewer on a fresh world and on the owner's usual
world; the ground reads as varied meadow with no visible checkerboard, the
scatter decoration is identical after a reload, and the grid appears/disappears
with its debug key.

**Acceptance Scenarios**:

1. **Given** a running world at default size, **When** the viewer loads,
   **Then** the ground shows at least three distinguishable close grass tones
   and scattered small flora, with no alternating-square pattern visible.
2. **Given** the same world, **When** the page is reloaded or the server is
   restarted with the same world, **Then** every grass tone and every tuft,
   clover, and flower is in exactly the same place.
3. **Given** the viewer showing the meadow, **When** the grid debug key is
   pressed, **Then** the tile grid lines appear over the meadow; pressing it
   again hides them; a fresh load starts with the grid hidden.
4. **Given** a much larger world, **When** viewed, **Then** the meadow shows
   no visible repetition or banding, and decoration density per screen area
   looks the same as the default world.

---

### User Story 2 - Water gathers into ponds (Priority: P2)

Contiguous water tiles no longer render as individual blue squares: they merge
into a single pond with a smooth, gently curved shoreline. Larger ponds carry
a lily pad. Where a kitty drinks is exactly where it always was — the water is
the same water, it just finally looks like something a cat would crouch beside.

**Why this priority**: water is the most jarring remnant of the tile look once
the grass is organic — a square puddle in a soft meadow. It is the "water" item
called out in the direction, and it completes the ground layer.

**Independent Test**: place worlds with a single water tile, a 2×2 cluster, and
an irregular blob; each renders as one smooth-shored shape with no internal
seams, stable across reloads.

**Acceptance Scenarios**:

1. **Given** two or more adjacent water tiles, **When** viewed, **Then** they
   render as one continuous pond with a smooth shoreline and no straight
   tile-boundary seams inside it.
2. **Given** a single isolated water tile, **When** viewed, **Then** it renders
   as a small rounded pool, not a square.
3. **Given** a pond of sufficient size, **When** viewed, **Then** it carries a
   lily pad accent; tiny pools carry none.
4. **Given** any pond, **When** kitties path to drink, **Then** they stop at
   the same tiles as before — the shoreline is visual only and pathing,
   distances, and the drink interaction are unchanged.

---

### User Story 3 - The world has an edge (Priority: P3)

The world no longer stops mid-lawn at a hard rectangle: a soft frame — taller
grass fringe in the same hand as the meadow — wraps the boundary so any size
world reads as a garden with an edge rather than a screenshot of infinity.

**Why this priority**: it is the piece that makes *different world sizes* each
feel intentional and complete, but it decorates the border rather than the
majority of pixels — after grass and water.

**Independent Test**: view worlds at several sizes; each shows the frame
hugging its own bounds, with corners handled, and no kitty or prop is ever
obscured by it.

**Acceptance Scenarios**:

1. **Given** a world of any size, **When** viewed, **Then** a decorative edge
   frames the full boundary, including corners, scaled to that world's bounds.
2. **Given** a kitty walking along the outermost tiles, **When** viewed,
   **Then** the kitty remains fully legible — the frame never covers a
   resident or a prop.

---

### User Story 4 - Sunbeams become light (Priority: P4)

Sunbeam tiles stop being yellow-tinted squares and become what they are: a
warm radial pool of light that bleeds softly past its tile bounds, glowing
under the existing pulse and dust motes. A napping kitty in a sunbeam finally
looks like a kitty napping in a sunbeam.

**Why this priority**: sunbeams are the smallest surface (a handful of tiles)
but the highest charm-per-pixel — and the existing pulse/motes ambience
already carries part of the effect, so this step is the finishing of an
already-started thought.

**Independent Test**: view a world with sunbeams; each renders as a soft warm
glow rather than a hard-edged square, the existing pulse and motes still play
over it, and reduced motion leaves a readable static glow.

**Acceptance Scenarios**:

1. **Given** a sunbeam tile, **When** viewed, **Then** it renders as a soft
   radial warm glow that extends slightly past the tile's bounds with no hard
   square edge.
2. **Given** the existing sunbeam ambience (pulse, motes), **When** the new
   glow ships, **Then** the ambience plays over the glow unchanged, and under
   reduced motion the glow holds still while remaining clearly visible as a
   sunbeam.
3. **Given** kitties seeking sunbeams, **When** one naps there, **Then** the
   kitty reads clearly against the glow.

---

### User Story 5 - Worn paths, revealed on request (Priority: P5)

A keystroke — in the same family as the greeble toggle — reveals faint worn
trails where the kitties have actually walked this session, fading slowly so
the meadow remembers recent traffic and forgets old habits. Off by default;
another press hides it; the footer hints at the key alongside the greeble
note. The trails are the session's own memory: they start blank on every load
and clear whenever the view's continuity breaks.

**Why this priority**: it is the delight feature — emergent, personal to each
world's actual life — but it layers on top of everything else and the meadow
is complete without it.

**Independent Test**: watch kitties walk with the toggle on; trails darken
along their actual routes and fade over minutes; toggling off hides them
instantly; a reload starts clean.

**Acceptance Scenarios**:

1. **Given** a fresh viewer load, **When** nothing is pressed, **Then** no
   paths are visible and the footer lists the paths key alongside the
   existing toggle hints.
2. **Given** the toggle is on, **When** kitties walk, **Then** faint trails
   appear along the routes actually walked, strengthen with repeated passage,
   and fade gradually as time passes.
3. **Given** visible trails, **When** the page reloads or the view snaps due
   to a discontinuity (world change, restart), **Then** accumulated trails are
   cleared and accumulation starts fresh.
4. **Given** trails accumulated with the toggle off, **When** the toggle is
   pressed, **Then** trails walked while hidden are shown too — the toggle
   controls visibility, not memory (within the same session).

---

### Edge Cases

- A world with no water tiles at all: no pond layer renders; nothing errors,
  nothing looks missing.
- A pond touching the world boundary: the shoreline meets the world edge
  cleanly, without spilling past the frame.
- Very small worlds (a few tiles across): the edge frame does not swallow the
  playfield; decoration density stays sensible rather than crowding.
- Very large worlds: decoration and trails must not degrade smoothness —
  drawing cost stays proportional to what is on screen.
- Two sunbeams adjacent or overlapping: glows blend softly instead of banding.
- Reduced-motion preference: all static decoration (grass, ponds, edge, glow,
  revealed trails) remains; anything that moves obeys the established ambient
  rules.
- The grid debug key and the paths key must not collide with existing keys
  (greeble toggle and any shipped debug keys).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The ground MUST render as an organic meadow — several close
  grass tones varying tile by tile plus sparse scattered flora (tufts, clover,
  tiny flowers) and a barely-visible per-tile brightness variation — replacing
  the alternating checkerboard entirely.
- **FR-002**: All meadow decoration MUST be a deterministic function of
  position within the world: identical on every reload and server restart of
  the same world, with no randomness that shifts between sessions and no new
  served data.
- **FR-003**: Decoration MUST scale to any world size — density proportional
  to area, no visible repetition, banding, or tiling artifacts at small or
  large sizes.
- **FR-004**: The tile grid MUST become a debug-only overlay: hidden by
  default, shown/hidden by a dedicated keystroke in the established toggle
  family, with a footer hint. Fresh loads always start hidden.
- **FR-005**: Contiguous water tiles MUST render as a single pond with a
  smooth curved shoreline (no internal tile seams); an isolated water tile
  renders as a rounded pool. Ponds above a defined size carry a lily pad
  accent.
- **FR-006**: All water rendering MUST be purely visual: which tiles are
  water, kitty pathing, drink interactions, and all served data are unchanged.
- **FR-007**: The world boundary MUST carry a decorative edge (grass fringe
  frame in the meadow's own style) that scales to any world size, handles
  corners, and never obscures a kitty or prop.
- **FR-008**: Sunbeam tiles MUST render as a soft radial warm glow bleeding
  slightly past tile bounds, replacing the hard-edged tinted square; the
  existing sunbeam ambience (pulse, motes) plays over it unchanged, and
  adjacent glows blend without banding.
- **FR-009**: The viewer MUST offer a worn-paths overlay: session-local
  accumulation of where kitties actually walk, strengthening with repetition
  and fading gradually with time; revealed/hidden by a dedicated keystroke in
  the established toggle family (off by default, footer hint); accumulation
  is cleared on reload and on any view discontinuity; path data never leaves
  the viewer.
- **FR-010**: Every new visual layer (meadow scatter, ponds, edge, glow,
  paths, grid overlay) MUST be individually controllable via named settings
  in the established tunables home, and every color MUST live in a named
  palette, per Article VI.
- **FR-011**: Kitty and prop legibility MUST take precedence over decoration:
  residents, props, and overlays remain instantly readable against every new
  layer at both fine and coarse sizes.
- **FR-012**: Reduced-motion preference MUST keep all static decoration
  visible while stilling any decorative motion, following the established
  ambient rules.
- **FR-013**: The feature MUST ship with zero engine or server changes: no new
  endpoints, no new served fields, no simulation contact, and no
  configuration file changes.
- **FR-014**: The new meadow look MUST pass a human approval checkpoint
  (judged live, all layers visible, at more than one world size) before it
  replaces the current ground rendering as the default view; revisions loop
  until approved and the outcome is recorded.

### Key Entities

- **Meadow decoration**: the per-position ground treatment — grass tone,
  brightness variation, and optional flora accent for each tile; derived
  entirely from world position, never stored or served.
- **Pond**: a visual grouping of contiguous water tiles with one continuous
  shoreline; size determines lily pad presence; membership is exactly the
  served water tiles.
- **World edge**: the decorative frame at the world boundary; a function of
  world dimensions only.
- **Sunbeam glow**: the light-pool treatment of a served sunbeam location.
- **Worn-path trace**: session-local, viewer-only memory of recent kitty
  movement per location — intensity rises with passage, decays with time,
  clears on reload/discontinuity; never transmitted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a default-size world, no alternating-square pattern is
  discernible anywhere on the ground, and reloading the page twice produces a
  pixel-identical meadow both times.
- **SC-002**: On a world at least four times the default area, an observer
  panning the whole map finds no visibly repeated decoration patch and no
  banding.
- **SC-003**: Every group of adjacent water tiles renders as one shape:
  an observer can not locate any internal tile boundary within any pond.
- **SC-004**: Each of the three toggles (grid and paths from this feature,
  greebles as shipped) behaves independently: one keypress each, correct
  default state on fresh load, footer hints present for all.
- **SC-005**: With every layer enabled on a default-size world, one minute of
  viewing shows no perceptible stutter or slowdown relative to the current
  viewer.
- **SC-006**: A viewer can locate every kitty and every prop within two
  seconds against the new ground at default zoom — legibility is not reduced
  by any decoration layer.
- **SC-007**: The version-control diff for the feature touches only viewer
  files: engine, server, and configuration are byte-identical.
- **SC-008**: The recorded approval checkpoint is signed off before the new
  look becomes the default, with any revision rounds noted.

## Assumptions

- The established toggle family (greeble reveal) and footer-hint pattern are
  the model for the grid and paths keys; exact key choices are decided at
  design time avoiding collisions.
- The existing sunbeam ambience (pulse and motes) and the ambient rules
  (subtle, individually toggleable, reduced-motion aware) shipped in the 005
  refresh remain in place; this feature layers under/around them.
- Day–night lighting is explicitly out of scope — it remains its own backlog
  entry and lands on top of this look later.
- The approval checkpoint is judged in the live viewer (a demo world, never
  the owner's real save), since the ground reads only in context — the
  gallery remains the home for portrait-style judgement of residents and
  props.
- Worn paths are presentation-only by decision recorded 2026-07-20: local
  accumulation, cleared on reload and discontinuity, never served — the
  server never learns where cats walked.
