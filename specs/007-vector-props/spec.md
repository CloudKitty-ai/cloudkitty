# Feature Specification: Vector Props — Retire the Remaining Emoji

**Feature Branch**: `props-style-direction`

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "Everything we discussed for Beautification II
step 1 (backlog entry + style conversation, 2026-07-20): replace the world
canvas's remaining platform emoji with parametric vector props drawn in the
cats' own chibi/outline vocabulary, judged in the portrait gallery under the
same approval gate that vetted the cats. The props and their agreed looks:
the chow bowl becomes a squat terracotta cat bowl whose drawn kibble mound
shrinks with servings (the food level *is* the data display, replacing the
meter); the bug becomes a **butterfly** (owner decision) — two chubby upper
wings, small lower lobes, dash body, thread antennae, wings flapping on the
animation phase, an airborne read from a gentle hover-bob plus a small
detached shadow (which also masks the engine's one-tile hops), per-individual
colorways derived from the stable element id (soft lavender / pale lemon /
peachy-white — hues the meadow doesn't use), and a faster, panicked flap
while the butterfly is the target of a served pursuit (no new data); the
greeble becomes a drawn wisp — teardrop blob, wavy skirt, hollow eyes, the
existing 55% alpha, slow bob, and a softer slightly-dashed outline, the one
thing drawn as not-quite-there (blank face vs. tiny mischievous grin left
open for the gallery); the sleep wisp becomes three hand-drawn rounded Zs
drifting up and fading on phase; the cuddle heart becomes a plump drawn
heart with a soft heartbeat pulse; the thought-bubble icons are redrawn as
mini-props in one ink weight — the bowl reused, a water drop, the Zs, a yarn
ball for play, the heart, and three glinting soap bubbles for bath. Props
get a small curated palette block of world-adjacent hues so one hand appears
to have drawn everything. With real butterflies in the world, the solo-play
imaginary plaything firmly stays the golden twinkling star (FR-009 of 005).
Greeble secrecy is untouched. Panel prose emoji stay for now. Zero engine or
server changes."

## Clarifications

*(none yet — the direction was settled in the 2026-07-20 design
conversation recorded in BACKLOG.md; the one deliberately open question,
the greeble's face, is a gallery-gate judgement, not a spec ambiguity)*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Props Gallery (Priority: P1)

Elizabeth opens the existing portrait gallery and finds a new props section:
every prop the world will use, drawn still, at world tile size and at the
larger inspection size — the bowl at each kibble level, the three butterfly
colorways, the greeble wisp at its translucency, the Zs, the heart, and the
full thought-icon set. She judges whether the props read as drawn by the
same hand as the approved cats — and nothing replaces a live emoji until
they do.

**Why this priority**: Same reasoning as the cats' gallery gate — the look
is the risk, and the gallery makes it arguable, iterable, and cheap to
reject. Every later story builds on approved geometry.

**Independent Test**: Open the gallery page from disk (no server). Verify
every prop appears with its states at both sizes, beside the cats they must
harmonize with, and that each reads correctly at true tile size.

**Acceptance Scenarios**:

1. **Given** the gallery page, **When** it loads, **Then** a props section
   shows every prop with its meaningful states — bowl at 5/3/1/0 servings,
   butterfly in all three colorways at two flap positions, greeble wisp at
   its in-world translucency, sleep Zs, heart, and all six thought icons —
   each at world tile size and at inspection size.
2. **Given** the props beside the cat portraits, **When** viewed together,
   **Then** they read as one drawing hand: same outline weight, same
   flat-fill-plus-shade shading, palette hues that sit comfortably on the
   grass colors.
3. **Given** a not-yet-right prop, **When** its parameters or palette are
   revised, **Then** only the drawing definitions and the gallery change,
   and the revision loop costs minutes.
4. **Given** the greeble's open face question, **When** the gallery is
   judged, **Then** blank-vs-grin is decided and recorded with the
   approval.

---

### User Story 2 - Bowl and Butterfly in the World (Priority: P2)

A viewer watches the live world: kibble sits in a proper terracotta cat
bowl whose mound visibly shrinks bite by bite, and butterflies — each its
own color, every session — flutter above the grass with their shadows
beneath them, panicking prettily when a cat locks on. The last "food as a
fish-cake emoji" and "bug as a caterpillar emoji" are gone.

**Why this priority**: These are the two props that live *on the ground*
and carry simulation data (servings, pursuit); they deliver most of the
in-world upgrade.

**Independent Test**: Watch a live world. Identify chow and butterflies at
a glance without the panel; watch a bowl empty across a meal; cover the
panel and tell two butterflies apart by color; reload and confirm each
butterfly kept its color.

**Acceptance Scenarios**:

1. **Given** a chow bowl at 5 servings and one at 1, **When** rendered,
   **Then** the two read differently at a glance from the mound alone, and
   a meal in progress visibly shrinks the mound tick by tick; the separate
   serving-meter bar is gone.
2. **Given** two butterflies on screen, **When** viewed with the panel
   covered, **Then** they are distinguishable by colorway, and the same
   butterfly keeps its colorway across frames and reloads.
3. **Given** a butterfly, **When** idle in the world, **Then** it hovers
   with a gentle bob above a small detached shadow, wings flapping on the
   animation phase — and its tile-to-tile hops read as flight, not
   teleporting.
4. **Given** a butterfly that is the target of a kitty's served pursuit,
   **When** rendered, **Then** its flap visibly quickens for the duration
   of the pursuit — derived from served data only.
5. **Given** reduced-motion preference, **When** the world renders, **Then**
   bowls and butterflies appear as static drawings (no flap, bob, or
   shadow animation), with all state information (kibble level, colorway)
   intact.

---

### User Story 3 - Overlays, Wisps, and Thought Icons (Priority: P3)

The finishing pass: the greeble revealed by the `g` toggle is a drawn wisp
that looks genuinely not-quite-there; a sleeping cat's Zs drift and fade
like a lullaby; cuddling cats share a softly beating drawn heart; and the
thought bubbles' wants are drawn in one consistent ink — bowl, drop, Zs,
yarn ball, heart, soap bubbles.

**Why this priority**: Pure consistency payoff on overlays that already
work; nothing here carries new simulation data.

**Independent Test**: Toggle `g` and inspect the wisp; watch a sleeping,
a cuddling, and a long-wanting kitty; confirm every remaining world-canvas
emoji is gone.

**Acceptance Scenarios**:

1. **Given** greebles revealed with `g`, **When** rendered, **Then** the
   wisp appears at the same translucency as today, with its softer
   dashed-feeling outline and slow bob; hidden greebles remain exactly as
   hidden as ever.
2. **Given** a sleeping kitty, **When** watched, **Then** drawn Zs drift
   gently upward and fade, replacing the emoji wisp; under reduced motion
   a static ladder of Zs shows instead.
3. **Given** a cuddling pair, **When** rendered, **Then** the drawn heart
   floats between them with a soft pulse (static under reduced motion).
4. **Given** each of the six needs held past the patience threshold,
   **When** its thought bubble shows, **Then** the need's icon is the
   drawn mini-prop (bowl, drop, Zs, yarn, heart, bubbles), legible at
   bubble size.
5. **Given** the finished feature, **When** the world canvas renders any
   scene, **Then** no platform emoji glyph appears anywhere on it (the
   panel's prose emoji are out of scope and unchanged).

---

### Edge Cases

- **Empty bowl**: unreachable in served data today — the engine expires
  an emptied bowl in the same tick's environment phase, so no published
  state carries 0 servings. The empty-bowl drawing exists defensively and
  as a gallery state, so the look is designed rather than accidental
  (analyze remediation E1).
- **Imaginary vs. real**: with butterflies now real, the solo-play
  imaginary plaything stays the golden twinkling star and must remain
  visually distinct from every real prop (005 FR-009 continues to hold).
- **Greeble secrecy**: the wisp is only ever drawn under the `g` toggle;
  its redesign changes how it looks, never when it is shown, and its
  translucency stays as shipped.
- **Butterfly at world edge / on a shared tile**: hover-bob and shadow must
  not spill outside the canvas or visually detach at tile boundaries.
- **Coarse sizes**: at very small tile sizes (large worlds shrink tiles),
  fine details (antennae, glints, dashes) drop away by the same
  size-threshold rule the cats use; silhouettes must still read.
- **Reduced motion**: all prop animation (flap, bob, pulse, drift) stops;
  static props with full state information remain; informational cues are
  never motion-gated.
- **Old servers**: props render entirely from data every server already
  serves (element kind, servings, ids, pursuit, activity); against any
  older server the feature degrades not at all.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every prop MUST be drawn from the same parametric drawing
  vocabulary as the approved cats (shared conventions: outline-first,
  flat fill plus one shade tone, unit-box geometry scaled to tile size,
  animation-phase hooks) — the gallery and the live world MUST use the
  same drawing definitions, never copies.
- **FR-002**: The gallery MUST gain a props section, viewable with no
  running simulation, showing every prop with its meaningful states at
  world tile size and at an enlarged inspection size, rendered beside or
  in visual reach of the cat portraits they must harmonize with.
- **FR-003**: The props look MUST be explicitly approved (including the
  greeble face decision) before any live-world emoji is replaced; the
  approval is recorded in the feature's artifacts, extending the existing
  gallery-approval record pattern.
- **FR-004**: The chow bowl MUST display its remaining servings as a drawn
  kibble mound whose size tracks the served serving count — replacing the
  separate meter — with 0 servings rendering an empty (not absent) bowl;
  the mound level MUST be readable at world tile size.
- **FR-005**: The butterfly (replacing the bug's emoji) MUST derive a
  stable per-individual colorway from its served element identity — the
  same butterfly renders the same colors across frames, sessions, and
  reloads — with at least three colorways in hues distinct from the
  existing world palette, pairwise distinguishable at tile size.
- **FR-006**: The butterfly MUST read as airborne: wings flapping on the
  local animation phase, a gentle hover-bob, and a small shadow drawn
  detached beneath it; while the butterfly is the target of any kitty's
  served pursuit its flap rate MUST visibly increase, derived from served
  data only.
- **FR-007**: The greeble wisp MUST render only under the existing debug
  toggle, at the existing translucency, with its distinct not-quite-there
  treatment (softer/dashed outline, slow bob); the toggle's behavior and
  default MUST NOT change.
- **FR-008**: The sleep indicator MUST become drawn Zs (drifting and
  fading on the local phase; static under reduced motion) and the cuddle
  indicator a drawn heart with a soft pulse (static under reduced
  motion), both replacing their emoji.
- **FR-009**: All six thought-bubble need icons MUST be drawn mini-props
  in one consistent ink weight — bowl (reusing the chow prop), water
  drop, Zs, yarn ball, heart, and a three-bubble soap cluster for bath —
  each legible at thought-bubble size.
- **FR-010**: After this feature, the world canvas MUST contain no
  platform emoji glyphs in any rendered scene; the panel's prose emoji
  are explicitly out of scope and unchanged.
- **FR-011**: The solo-play imaginary plaything MUST remain the golden
  twinkling star, visually distinct from every real prop including the
  new butterflies (continuity of 005's FR-009).
- **FR-012**: Prop colors MUST come from a small curated, named palette
  of world-adjacent hues (no per-callsite literals — Article VI), and all
  new animation tunables (flap rates, bob amplitudes, pulse periods,
  drift speeds, size thresholds) MUST be named values in the established
  tunables home.
- **FR-013**: Under reduced-motion preference every prop animation MUST
  stop, leaving static drawings with full state information; prop detail
  MUST degrade at small tile sizes by the same fine/coarse threshold rule
  the cats use.
- **FR-014**: The feature MUST require zero engine or server changes and
  no new served data: every visual derives from fields every current and
  older server already serves.

### Key Entities

- **Prop**: a named parametric drawing (bowl, butterfly, greeble wisp,
  sleep Zs, heart, thought icons) in the shared vocabulary — the unit the
  gallery displays and the live world reuses.
- **Prop appearance**: the butterfly's per-individual colorway, derived
  stably from served element identity — mirroring how kitty identity
  drives cat appearance.
- **Prop state**: the served data a prop displays — servings for the
  bowl, pursuit-targeted for the butterfly's panic flap, activity for the
  overlays — never invented, never predicted.
- **Props palette**: the small curated set of named world-adjacent hues
  (terracotta, butterfly lavender/lemon/peach, ink, blush) all props draw
  from.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The gallery props section shows 100% of the props with all
  their meaningful states (including all bowl levels and all butterfly
  colorways) at both sizes, and the look is explicitly approved — with
  the greeble face decided — before any live emoji is replaced.
- **SC-002**: In a live world viewed with the panel covered, an observer
  can identify chow, a butterfly, and (with the toggle) a greeble at
  world tile size, and can order two bowls by fullness from the mound
  alone.
- **SC-003**: Two butterflies on screen are distinguishable by colorway
  alone, and every butterfly's colorway is bit-for-bit stable across a
  reload and a server restart.
- **SC-004**: A butterfly under active pursuit is visibly more agitated
  than one at peace, within one tick of the pursuit appearing in served
  data, and calms within one tick of it ending.
- **SC-005**: After the feature, a survey of every rendered world scene
  (all activities, all beats, toggle on and off) finds zero platform
  emoji glyphs on the world canvas, while the imaginary plaything remains
  the star and is never confused with a real butterfly.
- **SC-006**: With reduced motion preferred, all prop state information
  (kibble level, colorway, greeble presence under toggle, thought icons)
  remains fully readable with zero prop animation.
- **SC-007**: The feature ships with zero engine or server changes
  (empty diff outside the client and its specs) and renders identically
  against any server version that serves today's fields.

## Assumptions

- The 005 architecture is the substrate and is retained: the shared
  drawing vocabulary file, the gallery page and its approval-gate ritual,
  the animation layer's phase/reduced-motion/discontinuity machinery, and
  the named-tunables home. This feature extends them rather than adding
  parallel structures.
- Served element ids are stable for an element's lifetime (they are — the
  engine allocates monotonically), which is what makes per-butterfly
  colorways stable; a butterfly's colorway may change only when the
  butterfly itself is replaced by a new individual.
- The engine's bug movement (one-tile hops on its own cadence) is
  unchanged; the airborne treatment is presentation over existing
  movement, not new motion data.
- "Bug" remains the engine and wire name for the element; "butterfly" is
  purely how the viewer draws it. Wire compatibility is untouched.
- The panel's prose emoji ("eating 🍥", "drinking 💧") are text in
  sentences and stay for now; whether the doing-line should reference the
  new props is a future decision, out of scope here.
- Out of scope: the meadow/map work (Beautification II step 2, its own
  backlog entry), any new elements or behaviors, day–night lighting, and
  all engine/server code.
