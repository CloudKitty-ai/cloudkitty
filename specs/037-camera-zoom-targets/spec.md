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

## Overview

Camera mode frames a fixed number of **tiles** — 10 at its floor, 15 at its
ceiling. A tile's size in pixels is therefore whatever the map's width divides
to, and the map varies by display:

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

This feature expresses **both** limits in pixels: the camera zooms in until a
tile is about 100px and widens until a tile would fall below about 50px. The
range between them is then `floor ÷ ceiling` — a constant **2.00×** on every
viewport that can reach the target, rather than a number that varies with the
window. A minimum tile count protects the smallest viewports from becoming a
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
   supported viewport, **Then** a kitty is still at or above the fine-detail
   threshold.
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
are either there or not, for a given display, and do not flicker in and out as
the clowder gathers and scatters.

**Why this priority**: 036 accepted this pop deliberately, to be judged in
motion. Judged, it is a distraction, and this feature removes its cause rather
than tuning around it — a floor above the threshold on every display means the
band can never straddle it.

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
  must not jump, since 036's FR-008 forbids cuts.
- **A world that is not 20 tiles.** The minimum is a count, so a small world
  could make it exceed the world itself; the frame can never be wider than the
  world (036 FR-029). A *larger* world is the expected direction — see the Fog
  dependency — and it only helps: the ceiling stops meeting the world's edge, so
  the range holds everywhere.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The camera's zoom floor MUST be expressed as a target size for a
  tile in pixels, not as a count of tiles. **Supersedes 036 FR-003.**
- **FR-002**: The camera's zoom ceiling MUST also be expressed in pixels, as the
  smallest tile it will widen to. **Supersedes 036 FR-005**, which set the
  ceiling as a multiple of the floor.
- **FR-003**: The zoom range MUST therefore be the same on every viewport that
  can reach the pixel target, since it is the ratio of the two.
- **FR-004**: Both ends of the band MUST sit above the fine-detail threshold,
  with margin, so that detail is drawn at every point in the camera's range and
  cannot flicker as the camera moves.
- **FR-005**: The number of tiles the floor frames MUST NOT fall below a
  minimum, so a small viewport shows a scene rather than a keyhole. No maximum
  applies: a larger viewport framing more tiles at the same legible size is the
  wanted behaviour.
- **FR-006**: Where the minimum tile count binds, the kitties MUST be drawn
  smaller than the target rather than the world being cropped further.
- **FR-007**: The ceiling MUST never frame more of the world than the world has,
  so the camera still crops and 036's FR-005 behaviour — letting a wanderer leave
  rather than shrinking everyone — is preserved.
- **FR-008**: Camera dials denominated in tiles that govern a *distance* — the
  aim deadzone and the fit margin — MUST have a consistent effect in pixels
  across viewports, or be re-expressed so that they do. A fix that made apparent
  size consistent while making the camera's responsiveness inconsistent would
  only move the problem.
- **FR-009**: With camera mode off, the view MUST remain exactly what it is
  today. This feature changes only the camera's limits.
- **FR-010**: The limits MUST be verified across the full range of supported
  viewports, from the smallest phone to the 1200px map cap.

### Key Entities

- **Size band**: the two pixel values the camera works between — the tile size
  it zooms in to, and the smallest tile it will widen to. The art is dialled
  against the band, not against a point.
- **Zoom range**: the ratio of those two. A property of the band rather than of
  the viewport, which is the whole point of expressing both in pixels.
- **Minimum tile count**: the fewest tiles the floor may frame, protecting the
  scene on the smallest viewports at the cost of their size and range.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across the supported viewport range, a kitty's drawn size at the
  zoom floor varies by no more than a factor of 2 — measured at 1.76× for a
  100px target with a 6-tile minimum, against 3.50× today. **Supersedes 036
  SC-001.**
- **SC-002**: On every supported viewport, a kitty is at or above the
  fine-detail threshold at BOTH ends of the camera's range, not only at the
  floor.
- **SC-003**: On every supported viewport, fine detail never changes state while
  the camera moves within its range, observed across a full session at 5
  kitties.
- **SC-004**: Every viewport that reaches the pixel target has the same zoom
  range, within 1%.
- **SC-005**: No supported viewport frames fewer than the minimum tiles at the
  zoom floor.
- **SC-006**: On every supported viewport, the ceiling frames fewer tiles than
  the world has, so the camera always crops.
- **SC-007**: With camera mode off, the rendered view is indistinguishable from
  the build shipped today.
- **SC-008**: The aim deadzone and the fit margin have the same effect in
  pixels, within 25%, across the supported viewport range.
- **SC-009**: A window resized across the point where the minimum tile count
  starts or stops binding produces no visible jump in the frame's width.

## Out of Scope

- **Every other part of camera mode.** The fit, the anchor and its hysteresis,
  the deadzone's existence, following, persistence, the card mark and the world
  clamp are all 036's and unchanged. Only the two limits move.
- **Choosing the final numbers.** The target, the band and the ceiling are
  dialled with the owner against the lab, as every art value in this client is.
  This spec fixes what they mean, not what they are.
- **The whole-world view's own scale.** Camera mode off is untouched; a kitty
  is 17px on a phone there and that is a separate question.
- **Making small displays legible by other means.** If the minimum tile count
  still leaves a phone too small to read, the answer is a different feature.

## Assumptions

- **The supported viewport range runs from a ~340px map to the ~1200px cap.**
  Those are the measured extremes: a phone at the low end and the largest map
  the client will draw at the high end. The cap is a shipped constant.
- **The band is 100px down to 50px, for now.** 100 is what a large monitor
  already shows at 036's full zoom, so that viewport's behaviour does not change
  and every value dialled against it stays valid; 50 sits above the 44px
  fine-detail threshold with enough margin that detail cannot flicker at the
  ceiling. Owner's call, 2026-08-18, explicitly to be tuned later.
- **The fine-detail threshold is the right legibility bar.** It is the line the
  client already draws between detail that reads and detail that becomes noise,
  and it is documented as a legibility guard rather than a performance one.
- **A factor of 2 is a reasonable bar for the size band.** The scheme measures
  1.76×, and the whole of the excess is the smallest viewports, where the
  minimum tile count deliberately wins.
- **The smallest viewports may fall below the target, and that is accepted.**
  Pinch zoom is the escape hatch on a phone and is already the accepted answer
  for short viewports in this client, so the minimum tile count needs no
  further protection.
- **Expressing the ceiling in pixels is a reversal, and deliberate.** An earlier
  draft argued that how much world to keep does not depend on pixels. That was
  wrong once the zoom range became the priority: the ceiling's real job is to
  widen until the kitties stop being legible, which is a pixel question, and
  making it one is what turns the range into a constant.
- **The pop is worth removing rather than tuning.** 036 shipped it so it could
  be judged in motion; a band entirely above the threshold removes its cause for
  nothing extra.

## Dependencies

- **Spec 036 (camera mode)**, shipped. This feature has no meaning without it
  and amends three of its requirements.
- **The meadow lab's phase and scale cards**, which are where the numbers get
  dialled and where a strip showing each viewport's camera tile would live.
- **Fog Generation, for the clean version.** On today's 20×20 world the 50px
  ceiling wants 20 tiles on a 1000px map and 24 on a 1200px one, so the largest
  viewports clamp against the world's own edge and lose part of their range.
  Fog is expected to grow the world substantially; at 40×40 nothing clamps and
  the range holds everywhere. **This feature is worth shipping before Fog** —
  it strictly improves on the current 3.5× spread either way — but its full
  benefit on the largest viewports arrives with the bigger world.
