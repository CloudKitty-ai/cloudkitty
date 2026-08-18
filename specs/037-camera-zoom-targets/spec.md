# Feature Specification: Camera zoom targets

**Feature Branch**: `037-camera-zoom-targets`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "the camera's zoom floor and ceiling are expressed
in tiles, which makes a kitty 34px on a phone and 120px on 4K — a 3.5× spread at
the same zoom. Re-express the floor as a pixel target clamped into a tile band,
and the ceiling as an absolute tile count."

**Amends spec 036** (camera mode), which is shipped. This supersedes its FR-003,
FR-005 and SC-001. Everything else in 036 stands: the fit, the anchor, the
hysteresis, the deadzone, following, persistence and the card mark are all
untouched.

## Overview

Camera mode frames a fixed number of **tiles** — 10 at its floor, 15 at its
ceiling. A tile's size in pixels is therefore whatever the map's width divides
to, and the map varies by display:

| display | map | camera tile at floor | at ceiling | crosses 44px? |
|---|---:|---:|---:|---|
| phone | 340 | 34px | 23px | **never** |
| laptop | 460 | 46px | 31px | at the floor only |
| 1080p | 640 | 64px | 43px | **crosses mid-band** |
| WQHD | 1000 | 100px | 67px | always |
| 4K | 1200 | 120px | 80px | always |

**The same "zoom" produces a 3.5× spread in how big a kitty actually is.** Every
art value in the client is a fraction of the tile, so a whisker dialled until it
reads at 120px is a third of that on a phone. One dialling pass cannot be right
everywhere, which makes the spread a blocker for the art work queued behind it.

Two other faults fall out of the same cause. A phone never reaches the
fine-detail threshold at all, so it never shows the detail the camera exists to
reveal. And 1080p crosses that threshold *inside* the band, which is the
detail-pop 036 accepted for now.

This feature changes what the two limits are expressed in. The floor becomes a
**pixel target**, held inside a band of tile counts so a small display cannot
become a keyhole. The ceiling becomes an **absolute tile count**, because how
much world to keep is a question about tiles and always was.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The kitties are the same size wherever I watch (Priority: P1)

Someone opening the meadow on a laptop and someone opening it on a 4K monitor
see kitties at comparable size. The art reads the same for both: the whiskers
are whiskers, the meniscus is a waterline, the eyes have their limbal ring.

**Why this priority**: This is the feature, and it is a prerequisite for every
piece of art work behind it. Until apparent size is consistent, each dialling
session is only correct for the display it was done on.

**Independent Test**: Open the meadow at each supported display size and measure
a kitty at the zoom floor. The largest and smallest differ by well under the
3.5× they differ by today.

**Acceptance Scenarios**:

1. **Given** camera mode is on, **When** the same world is viewed on a laptop
   and on a 4K display, **Then** a kitty's drawn size differs between them by
   less than a factor of two.
2. **Given** camera mode is on at its floor, **When** a kitty is measured on any
   supported display, **Then** she is at least the size the fine-detail
   threshold requires.

---

### User Story 2 - A small screen still shows a meadow, not a keyhole (Priority: P2)

Someone on a phone or a small laptop still sees enough of the world for the
scene to be worth watching: several kitties, some scenery, a sense of place.

**Why this priority**: A pixel target alone would take this away. On a phone a
90px target frames under 4 tiles, which is 8% of the world — the camera would
hold one kitty and a patch of grass. This story is what stops the fix for US1
being worse than the problem.

**Independent Test**: On the smallest supported display, count the tiles in
frame at the zoom floor. It is never fewer than the agreed minimum, whatever
the pixel target would have asked for.

**Acceptance Scenarios**:

1. **Given** a display small enough that the pixel target would frame fewer
   tiles than the minimum, **When** the camera is at its floor, **Then** it
   frames the minimum and the kitties are drawn smaller than the target rather
   than the world being cropped further.
2. **Given** a display large enough that the pixel target would frame more tiles
   than the maximum, **When** the camera is at its floor, **Then** it frames the
   maximum and the kitties are drawn larger than the target.

---

### User Story 3 - Fine detail stops appearing and disappearing (Priority: P3)

The tabby forehead stripes, the bowl's fish decal and the butterfly antennae
are either there or not, for a given display, and do not flicker in and out as
the clowder gathers and scatters.

**Why this priority**: 036 accepted this pop deliberately, to be judged in
motion. Judged, it is a distraction, and this feature removes its cause rather
than tuning around it — a floor above the threshold on every display means the
band can never straddle it.

**Independent Test**: On a 1080p display, watch a full session at 5 kitties
through gathering and scattering. The fine detail never switches state.

**Acceptance Scenarios**:

1. **Given** camera mode is on, **When** the camera moves anywhere within its
   range on any supported display, **Then** whether fine detail is drawn does
   not change.

---

### Edge Cases

- **A display so small the minimum tile count is still unreadable.** The
  minimum wins and the kitties are simply small; the camera never crops below
  it to buy size. Legibility past that point is a question for the whole-world
  view, not for the camera.
- **A display so large the maximum tile count binds.** The kitties are drawn
  larger than the target rather than the camera framing more world than a
  camera should.
- **The ceiling meets the world.** The ceiling must always crop: a ceiling equal
  to the world size would make camera-on and camera-off identical at full
  zoom-out and quietly retire 036's FR-005, which exists to let a wanderer
  leave.
- **The window is resized across a boundary mid-session**, so the governing
  rule changes from the pixel target to a clamp. The frame changes width; it
  must not jump, since 036's FR-008 forbids cuts.
- **A world that is not 20 tiles.** The tile band is a count, so a smaller world
  could make the minimum exceed the world itself. The frame can never be wider
  than the world (036 FR-029).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The camera's zoom floor MUST be expressed as a target size for a
  tile in pixels, not as a count of tiles. **Supersedes 036 FR-003.**
- **FR-002**: The number of tiles the floor frames MUST be held inside a band
  with a minimum and a maximum. Below the minimum the camera frames the minimum
  and accepts smaller kitties; above the maximum it frames the maximum and
  accepts larger ones.
- **FR-003**: The pixel target MUST be at or above the fine-detail threshold on
  every supported display, so that detail is available wherever the camera is
  used.
- **FR-004**: The zoom ceiling MUST be expressed as an absolute count of tiles,
  not as a multiple of the floor. **Supersedes 036 FR-005.**
- **FR-005**: The ceiling MUST always be narrower than the world, so the camera
  still crops at full zoom-out and 036's FR-005 behaviour — letting a wanderer
  leave rather than shrinking everyone — is preserved.
- **FR-006**: Whether fine detail is drawn MUST NOT change while the camera
  moves within its range on a given display.
- **FR-007**: Camera dials that are denominated in tiles and govern a
  *distance* — the aim deadzone and the fit margin — MUST have a consistent
  effect in pixels across displays, or be re-expressed so that they do. Under
  the current tile band their pixel effect is near-constant; a wider band makes
  it vary, and a fix that made apparent size consistent while making the
  camera's responsiveness inconsistent would only move the problem.
- **FR-008**: With camera mode off, the view MUST remain exactly what it is
  today. This feature changes only the camera's limits.
- **FR-009**: The limits MUST be verified at the full range of supported
  displays, from the smallest phone to the largest capped desktop map.

### Key Entities

- **Pixel target**: the size a tile should be drawn at when the camera is at its
  floor. The value the art is dialled against.
- **Tile band**: the minimum and maximum number of tiles the floor may frame.
  The minimum protects the scene on small displays; the maximum stops a large
  display from framing so much world that the camera stops being a camera.
- **Ceiling**: how many tiles the camera may widen to before it stops fitting.
  A count, independent of the floor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across the supported display range, a kitty's drawn size at the
  zoom floor varies by less than a factor of 2, against a factor of 3.5 today.
  **Supersedes 036 SC-001.**
- **SC-002**: On every supported display, a kitty at the zoom floor is at or
  above the fine-detail threshold.
- **SC-003**: On every supported display, fine detail never changes state while
  the camera moves within its range, observed across a full session at 5
  kitties.
- **SC-004**: No supported display frames fewer than the agreed minimum tiles at
  the zoom floor.
- **SC-005**: On every supported display, the ceiling frames fewer tiles than
  the world has, so the camera always crops.
- **SC-006**: With camera mode off, the rendered view is indistinguishable from
  the build shipped today.
- **SC-007**: The aim deadzone and the fit margin have the same effect in
  pixels, within 25%, across the supported display range.
- **SC-008**: A window resized across a governing-rule boundary produces no
  visible jump in the frame's width.

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

- **The supported display range runs from a ~340px map to the ~1200px cap.**
  Those are the measured extremes: a phone at the low end, and the largest map
  the client will draw at the high end. The cap is a shipped constant, not an
  assumption about hardware.
- **The fine-detail threshold is the right legibility bar.** It is the line the
  client already draws between detail that reads and detail that becomes noise,
  and it is already documented as a legibility guard rather than a performance
  one. Adopting it here keeps one definition of "big enough" rather than
  inventing a second.
- **A factor of 2 is a reasonable bar for "roughly similar".** It is a large
  improvement on 3.5 and is achievable across the whole range without
  keyholing; a tighter bar would force either a keyhole on phones or a very
  large minimum. The bar is a judgement and can be revisited once the numbers
  are dialled.
- **The tile band is a better instrument than a second pixel rule.** Clamping in
  tiles keeps the framing question in the unit framing is asked in, and means
  the two regimes fail toward opposite, sensible ends: small screens keep their
  scene, large ones keep their camera.
- **The ceiling stays a single number rather than a target.** How much world to
  keep does not depend on the display's pixels — a 15-tile frame is the same
  fraction of the meadow everywhere — so expressing it in tiles is not the bug
  that expressing the floor in tiles was.
- **The pop is worth removing rather than tuning.** 036 shipped it deliberately
  so it could be judged in motion; the alternative fix (ramping detail with
  size instead of switching it) is a larger piece of art work, and a floor
  above the threshold removes the cause for nothing extra.

## Dependencies

- **Spec 036 (camera mode)**, shipped. This feature has no meaning without it
  and amends three of its requirements.
- **The meadow lab's phase and scale cards**, which are where the numbers get
  dialled and where a strip showing each display's camera tile would live.
