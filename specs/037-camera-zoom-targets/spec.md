# Feature Specification: Camera zoom targets

**Feature Branch**: `037-camera-zoom-targets`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "the camera's zoom floor and ceiling are expressed
in tiles, which makes a kitty 34px on a phone and 120px on 4K — a 3.5× spread at
the same zoom. Re-express the floor as a pixel target clamped into a tile band,
and the ceiling as an absolute tile count."

*The ceiling half of that description no longer holds: clarification on
2026-08-18 made the ceiling a pixel target too, which is what turns the zoom
range into a constant. The Input is kept as written because it is the record of
what was asked for, not of what was settled.*

**Amends spec 036** (camera mode), which is shipped. This supersedes its FR-003,
FR-005 and SC-001. Everything else in 036 stands: the fit, the anchor, the
hysteresis, the deadzone, following, persistence and the card mark are all
untouched.

**"Everything else" was too blunt, and 036 now says so at each site.** The word
*nominal* is FR-003's, and it is load-bearing in seven other places: FR-004 and
FR-014, User Story 1's second acceptance scenario, two edge cases, an
Assumption, and SC-001's own wording. Each carries a pointer to this spec rather
than being rewritten, following the precedent set when 006 superseded 004's
floors — 036 is the record of what shipped, and until this feature is built its
rules are still what the client does.

**036's success criteria were walked on 2026-08-18.** SC-001 is superseded
here; of the thirteen that remain, eleven are untouched by this feature and two
needed work:

- **SC-006** (no more than 3 anchor changes a minute) is the one this feature
  endangered, and it was not obvious. The anchor drives the aim only while the
  ceiling BINDS — 19% of the time on a large viewport, ~100% on a phone once the
  ceiling is viewport-dependent — so 037 would have turned a mostly-invisible
  count into a visible one on exactly the screens least able to absorb it.
  **Settled ahead of implementation** by raising the anchor hysteresis from 1.5
  to 2.5 (PR #245): every viewport now measures inside the bar, and the ceiling
  did not have to move. See `client-measurements/037-zoom/sc006-2026-08-18.md`.
- **SC-005** (the camera never draws a frame with no kitty in it) **does not
  survive at the smallest viewport. It is WAIVED for this spec** (owner,
  2026-08-18) — knowingly, with a recorded remedy, not quietly failed. At a 340px map the frame is ~6.8 tiles and the camera
  draws 3 empty frames per 1500 ticks. The target is never empty; the easing
  is — 036's anchor guarantees a kitty where the camera is heading and its
  FR-008 forbids cutting, so a trip between two anchors can cross more empty
  grass than a small frame is wide. **The remedy is camera behaviour, not a
  limit**, and it is deferred to the camera-logic work rather than solved by
  widening the band: see `BACKLOG.md`. Recorded here so the criterion is
  knowingly deviated from rather than quietly failed.
- **SC-010** names "10 tiles" outright and is annotated at its site in 036.
- **SC-013** is measured "at the zoom ceiling on a phone, where a kitty is at
  her smallest". Still valid, and the case gets easier: that tile goes from
  23px to 50px.
- **SC-003** (frame rate within 10%) survives, and moves the right way — the
  ground bake gets *smaller* under a pixel floor.
- **SC-004** and **SC-012** (camera off unchanged; ground decoration identical
  at every width) are restated here as SC-007 and re-run by this feature's tasks.
- The remaining seven — SC-002, SC-005, SC-007, SC-008, SC-009, SC-011 and
  SC-014 — govern cuts, the empty frame, restore, following, reduced motion,
  view-independence and keyboard access. **None of them reads a tile count**,
  which is why they pass through untouched.

## Overview

Camera mode frames a fixed number of **tiles** — 10 at its floor, 15 at its
ceiling. A tile's size in pixels is therefore whatever the map's width divides
to, and the map varies by viewport:

| CSS viewport | map | camera tile at floor | at ceiling | crosses 44px? |
|---|---:|---:|---:|---|
| phone | 340 | 34px | 23px | **never** |
| laptop / Retina | 460 | 46px | 31px | at the floor only |
| 1080p 27in | 640 | 64px | 43px | **crosses mid-band** |
| large monitor | 1000 | 100px | 67px | always |
| at the 1200px cap | 1200 | 120px | 80px | always |

**"Viewport", not "resolution", and the difference inverts intuition.** The map
is sized from `documentElement.clientHeight` and `clientWidth`, which are CSS
pixels; the device pixel ratio only sharpens the canvas and never reaches the
tile. So a 15-inch Retina laptop at default scaling reports a *smaller* viewport
than a 27-inch 1080p monitor, and gets the smaller map. A high-resolution
display is often at the small end of this table, not the large one.

**The same "zoom" produces a 3.5× spread in how big a kitty actually is.** Every
art value in the client is a fraction of the tile, so a whisker dialled until it
reads at 120px is a third of that on a phone. One dialling pass cannot be right
everywhere, which makes the spread a blocker for the art work queued behind it.

Two other faults fall out of the same cause. A phone never reaches the
fine-detail threshold at all, so it never shows the detail the camera exists to
reveal. And 1080p crosses that threshold *inside* the band, which is the
detail-pop 036 accepted for now.

*Both of those were settled on 2026-08-18 — not by moving the band, but by
deleting the threshold outright (see User Story 3). The final column above is
kept as the record of the fault; there is no 44px line in the client any more.
The 3.5× spread, which is the feature's actual subject, is untouched by that.*

This feature expresses **both** limits in pixels: the camera zooms in until a
tile is about 100px and widens until a tile would fall below about 50px. The
range between them is then `floor ÷ ceiling` — **2.00× on any viewport that
reaches both targets**, rather than a number that varies arbitrarily with the
window. Two of the five candidate viewports actually do: the range measures
1.13× at 340px, 1.53× at 460px, 2.00× at 640px, 1.90× at 1000px and 1.58× at
1200px — the last two clamped by the world's own edge. The gain over today is real but it is a
*narrower* spread, not a constant. A minimum tile count protects the smallest viewports from becoming a
keyhole; nothing caps the top, because a larger viewport simply frames more
tiles at the same legible size, which is the correct answer.

## Clarifications

### Session 2026-08-18

- Q: On a large viewport the camera's most-zoomed-in view already frames most of
  what the ceiling allows — how much zoom range should it keep? → A: Range is the
  priority, and consistent apparent size the least of the three so long as size
  stays inside a band. So **both** limits become pixel targets rather than one
  being a tile count: floor at a 100px tile, ceiling at a 50px tile. Range is
  then `floor ÷ ceiling` — a constant 2.00× by construction, on every viewport
  that reaches the target.
- Q: Does the small end need more protection than a minimum tile count, given it
  loses most of its zoom range? → A: No. Pinch zoom is the escape hatch on a
  phone, and is already the accepted answer for short viewports elsewhere in
  this client.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The kitties are the same size wherever I watch (Priority: P1)

Someone on a small laptop and someone on a large monitor both see kitties
inside a known size band, and both see the same amount of zoom between the
camera's closest and widest views. The art reads for both: the whiskers are
whiskers, the meniscus is a waterline, the eyes have their limbal ring.

**Why this priority**: This is the feature, and it is the prerequisite for every
piece of art work behind it. Every art value is a fraction of the tile, so until
apparent size sits in a known band, each dialling session is only correct for
the viewport it was done on.

**Independent Test**: Open the meadow at each supported viewport size and
measure a kitty at the zoom floor and at the ceiling. Every measurement falls
inside the band, and the ratio between a viewport's own floor and ceiling is the
same wherever the target is reachable.

**Acceptance Scenarios**:

1. **Given** camera mode is on, **When** a kitty is measured at the zoom floor
   on any supported viewport, **Then** she is inside the size band.
2. **Given** camera mode is on, **When** the camera is at its ceiling on any
   supported viewport, **Then** a kitty is no smaller than the ceiling target —
   the bar the art is dialled against, since the portrait cards are 47px.
3. **Given** two viewports that both reach the pixel target, **When** each
   camera moves from its floor to its ceiling, **Then** both travel the same
   ratio.

---

### User Story 2 - A small screen still shows a meadow, not a keyhole (Priority: P2)

Someone on a phone or a small laptop still sees enough of the world for the
scene to be worth watching: several kitties, some scenery, a sense of place.

**Why this priority**: A pixel target alone would take this away. On a phone a
100px target frames 3.4 tiles, which is under 3% of the world — the camera would
hold one kitty and a patch of grass. This story is what stops the fix for US1
being worse than the problem.

**Independent Test**: On the smallest supported viewport, count the tiles in
frame at the zoom floor. It is never fewer than the minimum, whatever the pixel
target would have asked for.

**Acceptance Scenarios**:

1. **Given** a viewport small enough that the pixel target would frame fewer
   tiles than the minimum, **When** the camera is at its floor, **Then** it
   frames the minimum and the kitties are drawn smaller than the target rather
   than the world being cropped further.
2. **Given** any viewport, **When** the camera is at its floor, **Then** no
   upper limit on tiles applies — a larger viewport frames more tiles at the
   same legible size, which is the wanted answer rather than a case to guard.

---

### User Story 3 - Fine detail stops appearing and disappearing (Priority: P3)

The tabby forehead stripes, the bowl's fish decal and the butterfly antennae
are either there or not, for a given viewport, and do not flicker in and out as
the clowder gathers and scatters.

**Why this priority**: 036 accepted this pop deliberately, to be judged in
motion. Judged, it is a distraction. **Delivered 2026-08-18 by deleting the
threshold outright** rather than by keeping the band clear of it — the owner
judged fine detail at 21px on three monitors and found it good, so the gate
went. That also frees `ceilingPx`, which had been set to clear 44 with margin.

**Independent Test**: On a 27-inch 1080p viewport, watch a full session at 5
kitties through gathering and scattering. The fine detail never switches state.

**Acceptance Scenarios**:

1. **Given** camera mode is on, **When** the camera moves anywhere within its
   range on any supported viewport, **Then** whether fine detail is drawn does
   not change — because the whole band sits above the threshold, not because the
   band happens to avoid it.

---

### Edge Cases

- **A viewport so small the minimum tile count still leaves kitties under the
  target.** The minimum wins and they are simply smaller; the camera never crops
  below it to buy size. Pinch zoom is the escape hatch there, and is already the
  accepted answer for short viewports in this client.
- **A viewport whose floor and ceiling nearly meet.** On the smallest viewports
  the minimum tile count sits close to where the 50px ceiling falls, so the zoom
  range shrinks toward 1×. That is arithmetic rather than a fault: a 340px map
  cannot hold many legible tiles.
- **The ceiling meets the world.** The ceiling must always crop: a ceiling equal
  to the world size would make camera-on and camera-off identical at full
  zoom-out and quietly retire 036's FR-005, which exists to let a wanderer
  leave.
- **The window is resized across a boundary mid-session**, so the governing
  rule changes from the pixel target to a clamp. The frame changes width; it
  must not jump, since 036's FR-008 forbids cuts. There are **two** such
  boundaries, not one: the minimum tile count at the small end and the world
  clamp at the large.
- **The window is resized while the camera is mid-movement.** The target moves
  under an easing already in progress. The easing continues toward the new
  target rather than restarting, which is 036's behaviour for any moving target
  and needs nothing new — but it is the case most likely to be missed, because
  it requires two things to happen at once.
- **A world that is not 20 tiles.** The minimum is a count, so a small world
  could make it exceed the world itself; the frame can never be wider than the
  world (036 FR-029). A *larger* world would only help — the ceiling stops
  meeting the world's edge, so the range holds everywhere — but **it is not the
  expected direction, merely a possible one** (corrected 2026-08-19; see the Fog
  dependency). The world could equally stay 20 tiles or shrink, which is why the
  small-world case is guarded rather than assumed away.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The camera's zoom floor MUST be expressed as a target size for a
  tile in pixels, not as a count of tiles. **Supersedes 036 FR-003.**
- **FR-002**: The camera's zoom ceiling MUST also be expressed in pixels, as the
  smallest tile it will widen to. **Supersedes 036 FR-005**, which set the
  ceiling as a multiple of the floor.
- **FR-003**: The zoom range MUST be the same on every viewport that can reach
  **both** pixel targets, since it is then the ratio of the two. Where both are
  reachable the two targets are consequently **not independent**: the range is
  their quotient, so moving either one moves it. They are dialled as a pair, and
  a change to the floor that leaves the ceiling alone is a change to how far the
  camera zooms, whether or not that was the intent.

  **That coupling is a property of this stage of the build, not a principle to
  preserve** (owner, 2026-08-18). The two limits *should* be independent: a
  per-platform deviation is already visible at the small end, and a
  client-controlled zoom — or any deliberate widening of the range — would need
  them to move separately. **Anything later that decouples them is an
  improvement, not a regression against this requirement.**

  **The claim is also narrower than it reads.** Only two of the five candidate
  viewports reach both targets. **Measured on the implementation, 2026-08-18:
  1.13× at 340px, 1.53× at 460px, 2.00× at 640px, 1.90× at 1000px, 1.58× at
  1200px.** Only 640px comes out at the nominal 2.00×: the small end is held by
  `minTiles` and the large end by the world's edge, which the ceiling must stay
  one tile inside so the camera still crops (FR-007). "Constant" describes the
  middle of the supported range, not its ends, and the ends are where the
  interesting devices are.
- **FR-004**: *Withdrawn 2026-08-18 — the threshold it constrained no longer
  exists.* The owner judged fine detail at 21px on three monitors and had it
  drawn at every size, removing the 44px gate from `cat-v2.js` and `props.js`
  outright. There is now no threshold for the band to clear, and `ceilingPx` is
  free of it. 50 stays on its own merit: `PORTRAIT_CAT` is 47, so the cards the
  art is tuned against sit just below the camera's smallest tile, and nothing in
  the meadow is ever smaller than what was dialled.
- **FR-005**: The number of tiles the floor frames MUST NOT fall below a
  minimum, so a small viewport shows a scene rather than a keyhole. No maximum
  applies: a larger viewport framing more tiles at the same legible size is the
  wanted behaviour.
- **FR-006**: Where the minimum tile count binds, the kitties MUST be drawn
  smaller than the target rather than the world being cropped further.
- **FR-011**: *Withdrawn 2026-08-18, with the threshold it arbitrated.* It
  ruled that the minimum tile count wins where holding it would push a tile
  below the fine-detail threshold. With no threshold there is nothing left for
  it to outrank that FR-006 does not already say: the minimum wins over the
  pixel target, and the kitties are drawn smaller.
- **FR-020**: The camera MUST always draw a kitty at least **`minZoomVsBase`
  times** the size the whole-world view would draw her at. **Added 2026-08-19
  after the first deploy**, at 1.5×.

  This is the job 036 did for free and this spec dropped. `nominalAcross: 10`
  on a 20-tile world is exactly half of it, so 036's floor was 2.00× the
  whole-world tile on *every* display — which is why its SC-001 could say
  "about 2× at nominal". Replacing that with a pixel target made apparent SIZE
  consistent and silently let the zoom BENEFIT vary: 3.33× base on a phone
  against **1.05× on WQHD**, where the camera at its widest was five percent
  bigger than no camera at all. Reported from a 1100px map, and FR-007's
  `world - 1` clamp is what let it happen.

  `cssWidth` cancels out of `cssWidth/ceilTiles ≥ k · cssWidth/world`, so this
  is a pure tile cap of `world / k` — 13.3 tiles on a 20-tile world. It
  therefore binds only where the pixel ceiling would have overshot, which is
  the large maps, and leaves the small ones to the pixel target. **It would
  retire itself if the world grew**: at 40×40 it allows 26.7 tiles and the 50px
  target only asks for 24. *Whether the world ever grows is an open question —
  see the Fog dependency — so treat that as a property worth having rather than
  a plan.*

- **FR-007**: The ceiling MUST never frame more of the world than the world has,
  so the camera still crops and 036's FR-005 behaviour — letting a wanderer leave
  rather than shrinking everyone — is preserved. **Demoted to a backstop,
  2026-08-19**: as the *only* bound it was not an answer, because on a 20-tile
  world the pixel ceiling asks for 24 tiles and one tile of crop is
  indistinguishable from camera-off. FR-020 is what governs now; this survives
  for worlds too small for FR-020's cap to bite. This is a **separate** constraint
  from 036's FR-029: FR-029 keeps the frame from showing ground outside the world
  once its width is decided, while this decides that width. Both bind against the
  world's edge and neither replaces the other.
- **FR-012**: Where the world clamp binds, that viewport's zoom range MUST be
  smaller than the constant the band otherwise guarantees, and this is accepted
  rather than compensated for. Widening the floor to restore the range would give
  up the apparent-size consistency the feature exists for.
- **FR-008**: The camera dials that measure a *distance* — the aim deadzone and
  the fit margin — MUST stay denominated in tiles. They describe how far the
  clowder moves in the WORLD, not how far the image moves on a screen: the
  deadzone exists to ignore a kitty shuffling a tile. Re-expressing them in
  pixels would make the camera ignore more world on a small viewport, which is
  backwards. Their pixel effect is already constant wherever the pixel target is
  reachable, because the tile is — that falls out of the scheme rather than
  needing to be required.

- **FR-009**: With camera mode off, the view MUST remain exactly what it is
  today. This feature changes only the camera's limits.
- **FR-010**: The limits MUST be verified across the supported viewport range
  by a sweep at no coarser than 20px steps, together with the specific widths
  named in the Overview table. "The full range" is not something an
  implementation can be shown to have met; a stated sample is.
- **FR-013**: The floor MUST NOT exceed the ceiling. On a viewport small enough
  that the minimum tile count reaches where the ceiling target falls, the two may
  MEET — leaving that viewport no zoom range at all, which is acceptable — but
  they may never cross, which would ask the camera to widen past its own floor.
- **FR-015**: The floor and the ceiling MUST be derived from the viewport as it
  is when the camera decides a frame, never from a measurement taken earlier in
  the session. A viewport can change at any moment, and a limit computed once at
  startup would leave the camera obeying a window that no longer exists.
- **FR-016**: Between the floor and the ceiling the camera MUST be free to sit
  at any width. The limits bound the fit; they do not replace it. 036's fit —
  the clowder's bounding box plus its margin — still chooses the width whenever
  it falls between them, which is what keeps the camera answerable to the group
  rather than snapping between two positions.
- **FR-017**: At each boundary between regimes — where the minimum tile count
  starts binding, and where the world clamp starts binding — the two rules that
  meet there MUST give the same width, so there is no viewport width at which
  the answer switches. This is what makes SC-009's continuity a property of the
  scheme rather than something to be tuned into it.
- **FR-018**: A viewport larger than the map cap MUST behave exactly as the cap
  does. Past the cap the map stops growing, so the limits stop changing with it.
  This is why no maximum tile count is needed, and why a later change to the cap
  would change the widest frame the camera can produce.
- **FR-019**: The camera MUST consume the map's width as the layout produced it,
  with no branch of its own for orientation or for a short viewport. The client
  already fits the map to its width and lets the page scroll when the viewport
  is under 500px tall; that branch decides how large the map is, and the camera
  only asks how large it turned out.
- **FR-014**: A viewport measurement of zero or otherwise not a finite number
  MUST produce a usable frame rather than an undefined one. The map has no width
  until the page has laid out, and every limit in this feature is derived by
  dividing that width by a pixel target, so the first frame of every session
  meets this case.

### Key Entities

- **Size band**: the two pixel values the camera works between — the tile size
  it zooms in to, and the smallest tile it will widen to. The art is dialled
  against the band, not against a point.
- **Zoom range**: the ratio of those two. A property of the band rather than of
  the viewport, which is the whole point of expressing both in pixels.
- **Minimum tile count**: the fewest tiles the floor may frame, protecting the
  scene on the smallest viewports at the cost of their size and range.
- **Supported viewport range**: the span this feature is verified across — a
  ~340px map at the small end, the ~1200px cap at the large. **Defined here
  once**: wherever FR-010 or SC-001 say "the supported viewport range" they mean
  this and nothing else.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across the supported viewport range, a kitty's drawn size at the
  zoom floor varies by no more than a factor of 2 — measured at **1.994× for a
  113px target with a 6-tile minimum**, against 3.53× before this feature.
  **Supersedes 036 SC-001.**

  *The margin is now thin on purpose, and the arithmetic is worth keeping: the
  smallest cat in the range is fixed at 340/`minTiles` = 56.7px and does not
  move with `floorPx`, so the spread is simply `floorPx / 56.7`. The bar puts a
  hard ceiling on the floor target at 113px — 114 measures 2.01× and fails.
  Raising it further means lowering `minTiles` and paying for it in phone
  framing.*
- **SC-002**: *Withdrawn 2026-08-18.* There is no threshold to be above.
- **SC-003**: **Met by construction rather than by measurement.** Fine detail
  cannot change state at any size, on any viewport, in camera mode or out of
  it, because the gate that could change it has been deleted. What US3 asked
  for is delivered by removing the cause rather than by keeping the band clear
  of it.
- **SC-004**: *Withdrawn by the owner, 2026-08-18.* It required the zoom range to
  be identical across viewports, which follows from the construction rather than
  needing to be asserted — and pinning it would have to be renegotiated the
  moment anything widens the range deliberately, such as manual zoom. The number
  is kept unused so references elsewhere stay valid.
- **SC-005**: No supported viewport frames fewer than the minimum tiles at the
  zoom floor.
- **SC-006**: On every supported viewport, the ceiling frames fewer tiles than
  the world has, so the camera always crops.
- **SC-007**: With camera mode off, the rendered view is indistinguishable from
  the build shipped today.
- **SC-008**: *Withdrawn 2026-08-18.* Its "within 25%" was an invented constant
  with no reasoning behind it, and the property it measured follows from the
  scheme rather than needing a bar — see FR-008, which now records the decision
  instead of demanding the consistency.
- **SC-009**: A window resized across either boundary — where the minimum tile
  count starts or stops binding, and where the world clamp starts or stops
  binding — produces no visible jump in the frame's width. Continuous resizing
  produces continuous change, not merely an absence of jumps at the two crossings.
- **SC-010**: A resize that lands while the camera is already easing toward a
  target changes what it is easing toward, without restarting or cutting the
  movement in progress.

## Out of Scope

- **Every other part of camera mode.** The fit, the anchor and its hysteresis,
  the deadzone's existence, following, persistence, the card mark and the world
  clamp are all 036's and unchanged. Only the two limits move.
- **Choosing the final numbers.** The target, the band and the ceiling are
  dialled with the owner against the lab, as every art value in this client is.
  This spec fixes what they mean, not what they are. **The deferral ends at the
  dialling session**, which gates both deployment and the refresh of 036's
  pointers: nothing ships carrying an undialled number, and every figure quoted
  in this spec is provisional until that session settles it.
- **The whole-world view's own scale.** Camera mode off is untouched; a kitty
  is 17px on a phone there and that is a separate question.
- **Making small viewports legible by other means.** If the minimum tile count
  still leaves a phone too small to read, the answer is a different feature.

## Assumptions

- **The supported viewport range is the one defined in Key Entities**, and its
  ends are measured rather than chosen: a phone at the low end, and at the high
  end the largest map the client will draw. The cap is a shipped constant.
- **The minimum tile count starts at 6, and it is the one deferred number with
  a real conflict behind it.** Lowering it buys apparent size and zoom range on
  small viewports and costs framing; raising it does the reverse. At 6 a 340px
  map gives a 57px tile — larger than the 47px portrait cards — and a zoom
  range of about 1.13×. Unlike the band, it cannot be judged from a table — it
  is a question about how much meadow is worth looking at.
- **The band is 113px down to 50px, with a 1.5× floor against the whole-world
  view** (owner, 2026-08-19, after seeing the first deploy on a 1100px map).
  113 restores 036's close-up — its floor was 110px on that display — and takes
  everything SC-001's factor-of-2 allows. The 1.5× rule is what stops the
  ceiling drifting out to 95% of the world. *The text below is the original
  100/50 reasoning, kept because the argument for the ceiling still stands.*

- **The band is 100px down to 50px, for now.** 100 is what a large monitor
  already shows at 036's full zoom, so that viewport's behaviour does not change
  and every value dialled against it stays valid. 50 was originally chosen to
  sit above the 44px fine-detail threshold with margin; with that threshold
  deleted it stands on its own — `PORTRAIT_CAT` is 47, so the camera's smallest
  tile is never smaller than the cards the art is tuned against. Owner's call,
  2026-08-18, explicitly to be tuned later.
- **~~The fine-detail threshold is the right legibility bar.~~** *Withdrawn
  2026-08-18.* It was never validated, only inherited from 036 — and when it was
  finally looked at, it failed: fine detail read at 21px on three monitors, so
  the gate was deleted and the detail is drawn at every size. The legibility bar
  is now a judgement made by eye, not a constant in the source.
  **The argument recorded here was camera-ON only, and the smaller case is the
  default one** (raised in review of PR #246). Camera mode starts OFF, where the
  tile is `cssWidth / world.width` — **17px on a 340px phone map**, below the
  21px that was judged. The owner's decision was explicitly to draw fine detail
  at every size and stop gating on resolution, so this is inside it rather than
  a gap in it; but "the band clears the threshold at both ends" was never the
  whole reason, and the number nobody looked at is 17, not 21.
- **A factor of 2 is a reasonable bar for the size band.** The scheme measures
  1.76×, and the whole of the excess is the smallest viewports, where the
  minimum tile count deliberately wins.
- **The smallest viewports may fall below the target, and that is accepted.**
  Pinch zoom is the escape hatch on a phone and is already the accepted answer
  for short viewports in this client, so the minimum tile count needs no
  further protection. **Tested, not assumed** (owner, 2026-08-18): pinch zoom
  and panning were tried on a phone with camera mode on and work well. This
  carries more weight than it was written for — the small end also gives up
  framing (2.81 of 5 kitties at 340px) and the odd empty frame, and the owner's
  judgement is that the gesture covers those deficiencies too.
- **Expressing the ceiling in pixels is a reversal, and deliberate.** An earlier
  draft argued that how much world to keep does not depend on pixels. That was
  wrong once the zoom range became the priority: the ceiling's real job is to
  widen until the kitties stop being legible, which is a pixel question, and
  making it one is what turns the range into a constant.
- **The pop is worth removing rather than tuning — and it was removed at the
  source.** 036 shipped it so it could be judged in motion. Judged, the answer
  was not a band that clears the threshold but no threshold at all, which costs
  this feature nothing and frees `ceilingPx` of a constraint it was carrying.

## Dependencies

- **Spec 036 (camera mode)**, shipped. This feature has no meaning without it
  and amends three of its requirements.
- **The meadow lab's phase and scale cards**, which are where the numbers get
  dialled and where a strip showing each viewport's camera tile would live.
- **Fog Generation — an influence, not a dependency** (owner, 2026-08-18).
  **Corrected 2026-08-19, because this spec had Fog wrong.** Fog is not a map
  change. **It restricts what the KITTIES can see**: today they have global
  awareness, the coming generation is the first that must *infer* another
  kitty's state rather than reading it, and Fog limits what they can see of the
  map on top of that — the aim being more robust communication. Whether the
  world grows, and what size is even optimal, is **an open research question
  downstream of that**, not a planned change. Earlier text here assumed
  "Fog ⇒ bigger world" and reasoned from it.

  **What that means for the camera is narrow and worth stating: Fog changes
  what the kitties see, not what the viewer sees.** It touches no geometry in
  this spec. Its entire effect arrives through CLUSTERING BEHAVIOUR — and so
  through exactly the measured figures that were read off one generation
  (how often the ceiling binds, how many kitties are in frame, the anchor-change
  rates that set `hysteresis`). The arithmetic — the band, the ratio,
  `world / minZoomVsBase` — is untouched by it.

  On today's 20×20 world the 50px ceiling wants 20 tiles on a 1000px map and 24
  on a 1200px one, so the largest viewports clamp against the world's edge. A
  larger world would remove that clamp; **it is no longer safe to assume one is
  coming.** Nothing here is conditional on Fog landing and no acceptance
  criterion waits for it.
