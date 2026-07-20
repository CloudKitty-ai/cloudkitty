# Feature Specification: Graphics Refresh — Vector Cats & Animation

**Feature Branch**: `005-graphics-refresh`

**Created**: 2026-07-18

**Status**: Draft

**Input**: User description: "Graphics refresh: make the CloudKitty viewer even cuter with procedural vector cats and animation. All work is in client/ — no engine changes; the viewer remains a pure view (Article V): it never simulates or predicts, only renders and eases between states the server already sent. Direction was decided during ideation (2026-07-18, recorded in BACKLOG.md): procedural vector cats over pixel sprite sheets. De-risk the aesthetic floor first with a static cat-portrait gallery. Scope in build order: interpolation clock, vector cats with per-kitty identity and facing, action and idle animations, dramatizing served data (solo play, chase abandonment, pursuit, relief, long-distress thought bubble), ambient life and element juice. Hygiene: prefers-reduced-motion fallback and pausing when the tab is hidden. All tunables named per Article VI; server-owned ones in [viewer] via /config."

## Clarifications

### Session 2026-07-19

- Q: Are "idle" and "sitting" two poses or one? → A: One — the idle pose is
  a *standing* cat; a distinct sitting pose is skipped for now (owner
  decision at /speckit-analyze remediation). The pose vocabulary is eight:
  idle standing, walking, sleeping curl, resting loaf, pouncing, eating,
  drinking, grooming.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Portrait Gallery (Priority: P1)

Elizabeth opens a gallery page and sees the new cat design standing still:
every fur variant, every pose the live viewer will use, side by side at both
world size and a larger inspection size. She judges whether the procedural
cat is *cuter than the emoji it replaces* — and nothing else in this feature
proceeds until it is.

This story exists to retire the feature's one real risk early: a procedural
cat that reads as clip-art would be a step **down** from the current
professionally-drawn emoji. The gallery makes the look arguable, iterable,
and cheap to reject. If the design cannot get past clip-art after honest
iteration, the recorded fallbacks are pixel sprites or emoji-faces-on-vector-
bodies — and only one story has been spent finding out.

**Why this priority**: Every later story builds on this geometry. Approving
it first converts "rewrite the renderer and hope" into "extend a look we
already like."

**Independent Test**: Open the gallery page in a browser (no running
simulation required). Verify every fur variant and every pose appears, that
the three default kitties are told apart at a glance, and that the design
reads as cute at actual world tile size — not just when enlarged.

**Acceptance Scenarios**:

1. **Given** the gallery page, **When** it loads, **Then** it shows every fur
   variant and every pose used by the live viewer (idle standing, walking,
   sleeping curl, resting loaf, pouncing, eating, drinking, grooming), each
   rendered at world tile size and at an enlarged inspection size.
2. **Given** the gallery page, **When** viewed with no name labels, **Then**
   each default kitty's portrait is visually distinct from the others by fur
   alone.
3. **Given** the gallery is judged not-yet-cute-enough, **When** the cat
   geometry or palette is revised, **Then** only the gallery and the drawing
   parameters change — no other viewer behavior is touched, and the revision
   loop costs minutes, not a redraw of art assets.

---

### User Story 2 - Recognizable Kitties in the World (Priority: P2)

A viewer watches the live world and sees *cats*, not glyphs: each kitty drawn
with its own stable fur color, pattern, and eye color, facing the direction it
last moved. Miso always looks like Miso — across reloads, reconnects, and
server restarts — because appearance derives from who a kitty is, not from
when the page loaded.

**Why this priority**: Identity is the single biggest cuteness upgrade after
the look itself. It also unlocks the panel and the world telling one coherent
story ("the calico is the one who wants a bath").

**Independent Test**: Open the live viewer against a running world. Cover the
panel; identify each kitty by appearance alone. Reload; confirm every kitty
kept its exact appearance. Watch a kitty walk; confirm it faces its direction
of travel and keeps facing that way when it stops.

**Acceptance Scenarios**:

1. **Given** the default world, **When** the viewer renders it, **Then** each
   kitty appears as the approved vector cat with a palette (fur color,
   pattern, eye color) derived stably from its identity — the same kitty gets
   the same appearance in every session.
2. **Given** two kitties side by side, **When** viewed with the panel hidden,
   **Then** they are distinguishable by fur alone.
3. **Given** a kitty that just moved west, **When** it stands still on the
   next tick, **Then** it still faces west.
4. **Given** the greeble rule, **When** the world renders, **Then** greebles
   remain invisible by default and the `g` debug toggle still reveals them —
   the refresh changes how things look, never what is shown or hidden.

---

### User Story 3 - Cats That Glide, Not Teleport (Priority: P3)

Between one tick and the next, a walking cat slides smoothly across the tile
boundary instead of blinking from square to square. The world stops feeling
like a spreadsheet refresh and starts feeling alive — while remaining a pure
view: the motion shown is always an easing *between two states the server
already sent*, never a prediction of one it hasn't.

**Why this priority**: Smooth motion is the foundation the animation stories
stand on, and is independently delightful — even with no other change, gliding
cats are visibly better than teleporting ones.

**Independent Test**: Watch the live viewer at the default tick rate. Cats
visibly traverse tiles rather than jumping. Disconnect the server mid-motion;
on reconnect the viewer snaps to the fresh snapshot without cats sliding
across the map to catch up.

**Acceptance Scenarios**:

1. **Given** a kitty that moved one tile between two consecutive server
   states, **When** those states are rendered, **Then** the kitty is drawn
   gliding from the old position to the new one over the duration of one
   server tick, with the duration taken from served configuration — never
   hard-coded.
2. **Given** a reconnect after a dropped connection, **When** the fresh
   snapshot arrives, **Then** positions snap to it immediately (no easing
   across large distances).
3. **Given** the tab is hidden, **When** it becomes visible again, **Then**
   the viewer shows the latest served state within one tick, without
   replaying or animating through missed states.
4. **Given** a viewer whose user prefers reduced motion, **When** the world
   renders, **Then** positions update per-tick exactly as the pre-refresh
   viewer did — no continuous motion.

---

### User Story 4 - Expressive Actions and Idle Life (Priority: P4)

Every action a kitty takes *looks like something*: a pounce has wind-up and
squash-and-stretch, eating has a happy chomp, drinking ripples the water,
grooming has little licks, and falling asleep is a slow curl rather than an
instant swap. Between actions, cats are never statues — tails flick, ears
twitch, eyes blink, on a gentle local rhythm.

**Why this priority**: This is where "cute" becomes "alive." It depends on
both the approved look (US1/US2) and the animation clock (US3).

**Independent Test**: Watch the live world until each listed action occurs
(or drive them with a seeded world known to produce them). Confirm each is
visually distinguishable from the others without reading the panel. Watch an
idle cat for a minute; confirm it visibly moves (flick, twitch, blink) yet
never appears to act (no phantom eating or walking).

**Acceptance Scenarios**:

1. **Given** a kitty whose applied action is play or chase, **When** it is
   rendered, **Then** a pounce with anticipation and squash-and-stretch plays;
   eating, drinking, grooming, resting, and falling-asleep each likewise have
   their own distinguishable animation.
2. **Given** an idle kitty, **When** watched over time, **Then** idle motions
   occur at a configurable gentle frequency, and never misrepresent state —
   an idle cat never looks like it is performing an action.
3. **Given** a sleeping kitty, **When** it continues sleeping across ticks,
   **Then** it stays in its curled pose with a soft breathing motion rather
   than replaying the fall-asleep transition.
4. **Given** reduced-motion preference, **When** any of these states render,
   **Then** the static pose for the state is shown without animation.

---

### User Story 5 - The Stories the Data Already Tells (Priority: P5)

The simulation already serves its drama; the viewer finally performs it. A
kitty playing alone bats at an imaginary sparkle instead of pawing blank
grass. A kitty that gives up a hopeless chase sits down with drooped ears for
a sad beat. A kitty mid-pursuit wears determined eyes. A need being relieved
sparkles briefly. And a kitty that has wanted something for a long time shows
a soft in-world thought bubble with the icon of what it wants — the same
gentle cue the panel already gives, now visible where the kitty actually is.

**Why this priority**: Highest storytelling value per pixel — every beat here
renders data the server already sends and the viewer currently drops on the
floor. It depends on the expressive vocabulary from US4.

**Independent Test**: Using a world (or frozen states) exhibiting each
condition — solo play, an abandonment, an active pursuit, a relief, a
long-running distress — confirm each gets its distinct visual beat, and that
none of them invents state: every beat is traceable to served fields.

**Acceptance Scenarios**:

1. **Given** a kitty whose applied action is targetless play, **When**
   rendered, **Then** it pounces at a small imaginary plaything (sparkle or
   butterfly) that is visibly *imaginary* — it appears only during the
   animation and never resembles a real world element, preserving the rule
   that hidden things stay hidden.
2. **Given** a kitty that just abandoned a chase (a new entry appears in its
   served abandonment list), **When** rendered, **Then** it plays a brief
   sad beat (sit, ear droop) before resuming normal rendering.
3. **Given** a kitty with an active pursuit, **When** rendered, **Then** its
   expression reads as focused/determined for the duration of the pursuit.
4. **Given** a need that dropped sharply between two served states (relief
   was applied), **When** rendered, **Then** a brief sparkle plays by the
   kitty.
5. **Given** a kitty whose longest-running distress has exceeded the served
   patience threshold, **When** rendered, **Then** a soft thought bubble with
   the wanted need's icon appears near it — one bubble at most (the
   longest-running need), using the same served threshold as the panel cue,
   and disappearing when the distress resolves.

---

### User Story 6 - Ambient Life and Polish (Priority: P6)

The world itself breathes: water shimmers, sunbeams pulse warmly with
drifting dust motes, grass sways occasionally, and soft cloud shadows drift
across the ground. Existing furniture gets its juice — speech bubbles pop in
with a small bounce, the chow bowl shows its actual kibble level falling as
servings are eaten, and the tiny happiness bars over each cat ease to their
new values just as the panel bars already do.

**Why this priority**: Pure polish — lovely, but the last thing to build,
and every piece is independently droppable without weakening the stories
above.

**Independent Test**: Watch the live world. Ambient motion is present but
subtle (glanceable without distraction); each juice item behaves as
described; with reduced motion set, ambient effects are absent entirely.

**Acceptance Scenarios**:

1. **Given** the live world, **When** watched idle, **Then** water, sunbeams,
   grass, and light show gentle ambient motion that never obscures kitties,
   elements, or state.
2. **Given** a chow bowl at 3 of 5 servings, **When** rendered, **Then** its
   visible kibble level reads as clearly lower than a full bowl, and empties
   as servings are eaten.
3. **Given** a new meow, **When** its bubble appears, **Then** it pops in
   with a brief ease rather than appearing instantly; **Given** a happiness
   change, **Then** the over-cat bar eases to the new value.
4. **Given** reduced-motion preference, **When** the world renders, **Then**
   ambient effects are absent and juice reduces to instant transitions.

---

### Edge Cases

- **Reconnect / fresh snapshot**: any state arriving out of continuity (first
  paint, reconnect, server restart) renders by snapping, never by easing
  across the discontinuity.
- **Hidden tab**: the animation loop does no work while the page is hidden;
  on return, the viewer snaps to the latest served state (no catch-up replay,
  no accumulated animation debt).
- **Old server**: against a pre-005 server missing any newly served viewer
  configuration, the viewer falls back to named stand-in defaults and remains
  fully functional (same pattern as the existing distress-cue threshold).
- **Elements appearing/disappearing**: spawned or expired elements (bugs,
  chow, sunbeams) may fade briefly but must not glide from nowhere; a
  mid-chase target vanishing simply stops being drawn.
- **Roster mismatch mid-session**: if the set of kitties in a served state
  differs from the previous one (e.g., reconnect to a different world), the
  viewer rebuilds rather than easing between unrelated cats.
- **Two beats at once**: when multiple expressive cues apply (e.g., pursuit
  face during a pounce, sparkle during a thought bubble), the viewer layers
  or prioritizes them by a documented rule instead of flickering.
- **Missing emoji-era data**: states that lack optional fields (no pursuit,
  no abandonments, no distress ages) render normally with no beats — absence
  of drama is not an error.
- **Slow machines**: if the display cannot sustain smooth animation, the
  viewer degrades to coarser motion but never falls behind the served state
  (the newest state always wins over finishing an animation).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The viewer MUST provide a portrait gallery page, reachable
  alongside the live viewer and requiring no running simulation, that renders
  every fur variant and every pose used by the live viewer at both world tile
  size and an enlarged inspection size, using the same drawing definitions
  the live viewer uses (never a copy).
- **FR-002**: The gallery look MUST be explicitly approved before any
  animation or live-world rendering work builds on it; the approval (or a
  fallback decision — pixel sprites or emoji-faces-on-vector-bodies) is
  recorded in the feature's artifacts.
- **FR-003**: Each kitty's appearance (fur color, pattern, eye color) MUST
  derive deterministically and stably from the kitty's identity: the same
  kitty renders identically across frames, sessions, reloads, and server
  restarts, and the default kitties are pairwise distinguishable by fur
  alone.
- **FR-004**: A kitty MUST face the direction of its most recent movement and
  keep that facing while stationary; facing derives only from served
  positions/actions, never from prediction.
- **FR-005**: The viewer MUST render continuous motion by easing between the
  two most recent served states, with the easing duration derived from the
  served tick interval (fetched from configuration, with a named stand-in
  default when unavailable) — never hard-coded, and never extrapolating
  beyond the newest served state.
- **FR-006**: The viewer MUST remain a pure view (Article V): every visual —
  poses, beats, particles, ambient motion — is a presentational function of
  served states (including differences between consecutive served states) and
  a local animation clock; the viewer computes no simulation outcomes and
  sends nothing that influences the world.
- **FR-007**: Each of the following applied actions MUST have a visually
  distinguishable animation: play/chase (pounce with anticipation and
  squash-and-stretch), eat, drink, groom, rest, and the transition into
  sleep; ongoing sleep shows a held curl with soft breathing rather than a
  repeated transition.
- **FR-008**: Idle kitties MUST show occasional idle motion (tail flick, ear
  twitch, blink) at a configurable frequency, and idle motion must never
  visually imply an action the engine did not apply.
- **FR-009**: Targetless (solo) play MUST render with a small imaginary
  plaything that appears only during the play animation and is visually
  distinct from every real element kind; the greeble-secrecy rule is
  untouched (greebles hidden by default, `g` toggle unchanged).
- **FR-010**: The viewer MUST render pursuit and abandonment beats from
  served data only: a focused expression while a pursuit is present, and a
  brief sad beat when a kitty's served abandonment list gains a new entry.
- **FR-011**: A sharp drop in a served need between consecutive states
  (relief) MUST produce a brief positive visual beat by that kitty.
- **FR-012**: A kitty whose longest-running served distress age exceeds the
  served patience threshold MUST show one soft in-world thought bubble with
  the wanted need's icon — the same threshold the panel cue uses, at most
  one bubble per kitty, removed when the distress resolves.
- **FR-013**: Ambient effects (water shimmer, sunbeam pulse and motes, grass
  sway, drifting cloud shadows) MUST be subtle, must never obscure kitties or
  elements, and MUST be individually disableable via named constants.
- **FR-014**: Existing furniture MUST get its polish: speech bubbles ease in,
  the chow bowl's visible kibble level reflects remaining servings, and the
  over-cat happiness bar eases to new values.
- **FR-015**: When the user's system signals a reduced-motion preference, the
  viewer MUST fall back to per-tick snapping with static poses — behaviorally
  equivalent in motion terms to the pre-refresh viewer — with no continuous,
  idle, or ambient animation.
- **FR-016**: The animation loop MUST do no rendering work while the page is
  hidden and MUST resume by snapping to the latest served state when the page
  becomes visible.
- **FR-017**: All new visual tunables (durations, easings, frequencies,
  amplitudes) MUST be named values, never inline magic numbers (Article VI);
  any tunable the server should own lives in the served `[viewer]`
  configuration section with a documented default and a named client
  stand-in.
- **FR-018**: The refreshed viewer MUST remain fully functional against a
  pre-005 server: no new served field is required, and every new visual
  either works from existing served data or degrades gracefully to its
  stand-in defaults.
- **FR-019**: When rendering cannot keep up, the newest served state MUST
  take priority over completing an in-flight animation — the viewer may skip
  or shorten animation, but must never display state older than the previous
  served tick.

### Key Entities

- **Cat appearance**: the per-kitty visual identity — fur base color, fur
  pattern, eye color — derived stably from kitty identity; the unit the
  gallery displays and the live world reuses.
- **Pose**: a named static body configuration (idle standing, walking,
  sleeping curl, resting loaf, pounce, eating, drinking, grooming) defined by
  drawing parameters; the vocabulary both gallery and animations share.
- **Animation beat**: a short, named presentational sequence (pounce, chomp,
  sad beat, relief sparkle, bubble pop-in) triggered by served state or by
  differences between consecutive served states, played on the local clock.
- **Interpolated frame**: what the screen actually shows — a blend between
  the two newest served states at a progress determined by the local clock
  and the served tick interval.
- **Viewer configuration**: served `[viewer]` values the client reads (tick
  interval for easing duration, the existing distress patience threshold),
  each with a named client stand-in for older servers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The gallery shows 100% of the pose vocabulary used by the live
  viewer and at least as many fur variants as there are default kitties, each
  variant pairwise distinguishable at world tile size; the look is explicitly
  approved (or a fallback decision recorded) before any animation story is
  built.
- **SC-002**: In a running world at the default tick rate, a moving kitty is
  in visible transit between tiles for the majority of each tick interval —
  zero instantaneous position jumps except at documented discontinuities
  (first paint, reconnect, hidden-tab return).
- **SC-003**: A viewer shown the live world with the panel hidden can
  correctly identify every default kitty by appearance alone, and each
  kitty's appearance is bit-for-bit stable across a reload and a server
  restart.
- **SC-004**: Each of the seven action states (pounce/play, chase, eat,
  drink, groom, rest, sleep) is identifiable from the world view alone —
  without reading the panel — within one tick of the action being applied.
- **SC-005**: Every expressive beat driven by served data (solo-play
  plaything, abandonment beat, pursuit face, relief sparkle, long-distress
  bubble) appears when its serving condition holds and never otherwise, as
  verified against frozen states exhibiting each condition.
- **SC-006**: The viewer sustains smooth animation (no perceptible stutter,
  under 1% dropped frames over a one-minute observation) on a typical laptop
  at the default world size, and does no animation work while the tab is
  hidden.
- **SC-007**: With reduced motion preferred, observed rendering is
  motion-equivalent to the pre-refresh viewer (per-tick updates only), and
  all state information (positions, actions, happiness, distress cues)
  remains fully available.
- **SC-008**: The refreshed viewer, pointed at an unmodified pre-005 server,
  renders the world with all new visuals that need no new served data, and
  logs no errors from missing configuration.

## Assumptions

- The current viewer architecture (a canvas world plus a card panel, served
  as static files by the simulation server) is retained; this feature
  restyles and animates it rather than replacing it.
- The panel cards may keep their existing emoji faces initially; unifying
  card portraits with the vector look is a nice-to-have inside US2, not a
  separate requirement.
- The served configuration will additionally expose the server's tick
  interval under the `[viewer]` section if it is not already available to
  clients; this is an additive, backward-compatible configuration echo — the
  one permitted API-adjacent change, consistent with "possibly new `[viewer]`
  config keys" in the feature description.
- Appearance derives from kitty id (the only stable identity the wire
  provides today); richer identity (named fur genetics, age) remains the
  separate P2 "Age / fur / eye stats" backlog item, which this feature must
  not block: the palette derivation is expected to become overridable by
  served appearance data later.
- "Typical laptop" for SC-006 means hardware comparable to the development
  machine; no minimum-spec benchmarking beyond that is in scope.
- Out of scope, per the feature description: day–night lighting, ear/tail
  mood affect, zoom/camera work, and any engine or simulation change.
  Determinism (Article V) is unaffected: the animation clock is
  presentational, and identical served states always produce identical
  *logical* renderings (poses, beats, identities), with only sub-tick easing
  phase varying by wall clock.
