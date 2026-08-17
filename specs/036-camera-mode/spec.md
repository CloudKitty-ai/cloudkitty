# Feature Specification: Camera mode

**Feature Branch**: `036-camera-mode`

**Created**: 2026-08-17

**Status**: Draft

**Input**: User description: "036"

**Source material**: `docs/camera-mode-design-notes.md` on branch
`client-camera-notes`, written 2026-08-16 and settled with the owner over that
session and the next. The notes are the argued-with draft; this spec is what
survived. Where the two disagree, this spec wins.

**Number**: 036, not 035. Another thread claimed 035 for surface expansion in a
worktree that is unpushed as of 2026-08-17, so `specs/` on `main` still tops out
at 034 and sequential numbering would have collided.

## Overview

Today the client draws the whole 20×20 world at once. Every kitty is on screen
and every kitty is small: about 31 CSS pixels on a common laptop, which is below
the size at which the cat art was drawn to read.

Camera mode makes the view a window instead of a map. It holds the group at
roughly twice that scale, widening only as far as it must and refusing to widen
past a fixed ceiling. Clicking a kitty aims the window at her.

The whole feature turns on one decision the owner made early: **following a
kitty changes only where the camera aims, never how wide it sits.** That
collapses what looked like two features into one. Hold-the-group and follow-one
differ by a single value, the anchor, so there is one path through the code and
no handoff between modes to get wrong.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the kitties at a size worth looking at (Priority: P1)

A viewer opens the meadow and finds the kitties small. She turns camera mode on
with the control beside the sundial. The view closes in on the group and holds
them there, following them around the meadow as they move, easing rather than
jumping. When a kitty wanders far enough that keeping everyone in shot would
shrink the rest back to specks, the camera stops widening and lets her go; her
card still shows what she is doing.

**Why this priority**: This is the feature. It delivers the whole of the value
on its own — bigger kitties, held automatically — with no clicking, no
selection, and nothing to learn. Every later story refines where it aims.

**Independent Test**: Turn the control on with a 5-kitty roster and watch a few
hundred ticks. The kitties are visibly larger, the frame tracks them, and the
motion never cuts. Turning the control off returns the view shipped today.

**Acceptance Scenarios**:

1. **Given** camera mode is off, **When** the viewer activates the control,
   **Then** the view narrows to the group and holds it, and every change of aim
   and scale is eased rather than cut.
2. **Given** camera mode is on and the kitties are huddled together, **When**
   the fit would narrow the view below the nominal width, **Then** the camera
   stops at nominal and does not zoom further in.
3. **Given** camera mode is on and one kitty wanders to the far edge, **When**
   fitting everyone would exceed the ceiling, **Then** the camera holds at the
   ceiling, aims at a kitty inside the main group, and lets the wanderer leave
   the frame.
4. **Given** camera mode is on, **When** the viewer deactivates the control,
   **Then** the view returns to the whole world exactly as it renders today.

---

### User Story 2 - Watch one kitty in particular (Priority: P2)

A viewer notices Clementine doing something and wants to keep her in view. She
clicks Clementine and the camera aims at her and stays with her. Clicking
Clementine again releases her, and the camera goes back to holding the group.

**Why this priority**: The reason a viewer looks at a specific kitty is that
something is happening to that kitty, and the whole-group camera has no way to
know which one she means. It is the highest-value addition on top of P1, and it
is what makes the meadow feel like it has characters rather than traffic.

**Independent Test**: With camera mode on, click each kitty in turn and confirm
the camera aims at her and stays with her across her whole activity, including
sleep. Click her again and confirm the camera returns to the group.

**Acceptance Scenarios**:

1. **Given** camera mode is on and no kitty is followed, **When** the viewer
   clicks a kitty, **Then** the camera aims at that kitty and keeps aiming at
   her while she moves.
2. **Given** a kitty is followed, **When** the viewer clicks the same kitty
   again, **Then** the follow is released and the camera holds the group, with
   camera mode still on.
3. **Given** camera mode is off, **When** the viewer clicks a kitty, **Then**
   camera mode turns on and that kitty is followed.
4. **Given** a kitty is followed, **When** she falls asleep for several ticks,
   **Then** the camera stays with her and does not time out, drift away, or
   release her.
5. **Given** a kitty is followed and another kitty is beside her, **When** the
   camera aims at the followed kitty, **Then** the frame is no narrower than it
   would be holding the group, so the neighbour stays in shot.

---

### User Story 3 - The meadow remembers how I was watching it (Priority: P3)

A viewer who turned camera mode on and settled on a kitty closes the tab and
comes back later. The meadow opens the way she left it.

**Why this priority**: Without it, every visit starts zoomed out and every
returning viewer re-does the same two actions. It costs little and it is the
difference between a setting and a chore.

**Independent Test**: Set each of the three states (off; on holding the group;
on following a named kitty), reload, and confirm each comes back. Then remove
that kitty from the roster, reload, and confirm the view opens holding the
group rather than failing.

**Acceptance Scenarios**:

1. **Given** camera mode is on and no kitty is followed, **When** the viewer
   reloads, **Then** camera mode is on and the camera holds the group.
2. **Given** camera mode is off, **When** the viewer reloads, **Then** the whole
   world view is restored.
3. **Given** a kitty is followed, **When** the viewer reloads, **Then** the same
   kitty is followed.
4. **Given** a kitty is followed, **When** she is removed from the roster and
   the viewer reloads, **Then** the follow is dropped, the camera holds the
   group, and camera mode itself is unchanged.

---

### User Story 4 - Know which kitty I am following (Priority: P4)

The card for the followed kitty is marked, so the viewer can tell at a glance
which one the camera is holding — including after a reload, when she did not
make the choice in this session.

**Why this priority**: The camera's aim is its own feedback while a kitty is
moving, but it is ambiguous when the group is tight and unreadable after a
reload. This closes that gap. It is last because the feature works without it.

**Independent Test**: Follow each kitty in turn and confirm exactly one card is
marked at a time and that it is the right one. Unfollow and confirm no card is
marked.

**Acceptance Scenarios**:

1. **Given** a kitty is followed, **When** the viewer looks at the cards,
   **Then** that kitty's card is marked and no other card is.
2. **Given** a followed kitty is released, **When** the viewer looks at the
   cards, **Then** no card is marked.
3. **Given** a kitty is followed, **When** the viewer reloads, **Then** her card
   is marked on the restored page.

---

### Edge Cases

- **A kitty leaves the roster while the page is open.** If she was followed, the
  follow is dropped and the camera holds the group without interruption. This
  path is required regardless of persistence, so it is not special to reload.
- **The group is wider than the ceiling in one dimension only.** The frame is
  square in tiles and the map is square, so the wider dimension governs; the
  ceiling binds on the larger spread.
- **Every kitty is on the same tile.** The fit collapses to nothing and the
  nominal width applies as the floor, so the camera sits at nominal.
- **Two kitties are equally central.** The anchor rule must resolve
  deterministically rather than alternating between them from frame to frame.
- **The viewer clicks empty ground, an element, or a decoration.** Nothing
  happens; the current follow is left alone. Only a kitty toggles a follow.
- **The viewer clicks where two kitties overlap.** Kitties overlap freely
  because they are depth-sorted sprites, so the click resolves to exactly one of
  them and never to both.
- **The window is resized, or a phone is rotated, while camera mode is on.** The
  frame keeps its width in tiles; the tile's pixel size changes with the canvas.
- **A viewer has reduced motion set.** The camera arrives at its target
  immediately with no easing, at every scale and on every anchor change.
- **The roster is at its 3-kitty minimum.** A small group fits at nominal most
  of the time, so the camera rarely widens and mostly sits at the zoom floor.

## Requirements *(mandatory)*

### Functional Requirements

**The frame**

- **FR-001**: The map MUST carry a camera-mode control that turns camera mode on
  and off. Its placement is already built and settled; this feature owes it
  behaviour, not position.
- **FR-002**: With camera mode off, the client MUST render the whole world
  exactly as it renders today: the same fixed tile derived from the world size
  and the viewport, with no easing and no anchor.
- **FR-003**: With camera mode on, the camera's nominal frame MUST be 10 tiles
  across, which is twice today's scale on a 20-tile world.
- **FR-004**: The camera MUST try to hold every kitty in frame, and MUST NOT
  narrow below the nominal width. Nominal is a floor, so a huddled group does
  not zoom past comfort. When the fit is what binds, no kitty may be drawn
  touching the frame's edge: a margin holds the outermost clear of it.
- **FR-005**: The camera MUST NOT widen beyond 1.5× nominal, that is 15 tiles.
  Past that it stops trying to fit and allows kitties to leave the frame.
- **FR-006**: When the camera cannot fit every kitty, it MUST aim at the kitty
  nearest the group's centre of mass. It MUST NOT aim at the bounding-box
  midpoint or at the centre of mass itself, because both are usually empty
  ground.
- **FR-007**: In group mode the anchor kitty MUST change only when another kitty
  is clearly more central, by a margin of at least 1.5× in distance, so the
  camera does not flick between kitties at opposite ends of the meadow.
- **FR-008**: The camera MUST NOT cut. Every change of aim and of width is
  eased, however far the target moves between frames.
- **FR-009**: Easing MUST be corrected for frame rate, so the camera settles at
  the same real speed on a 60Hz and a 120Hz display. Aim MUST settle slightly
  faster than width.
- **FR-010**: When the viewer has reduced motion set, the camera MUST move to
  its target immediately, with no easing.

**Following**

- **FR-011**: Clicking or tapping a kitty MUST follow her. Clicking or tapping
  the followed kitty again MUST release her.
- **FR-012**: Clicking a kitty while camera mode is off MUST turn camera mode on
  and follow her.
- **FR-013**: Releasing a followed kitty MUST leave camera mode on, holding the
  group. The control is the only way back to the whole world.
- **FR-014**: Following MUST change only where the camera aims. The nominal
  width and the ceiling are unchanged, so kitties near the followed one stay in
  shot.
- **FR-015**: A followed kitty MUST be the anchor unconditionally. The
  hysteresis of FR-007 applies to group mode only.
- **FR-016**: Following MUST have no timeout, no drift-away, and no
  auto-release. A sleeping kitty is followed exactly like a moving one.
- **FR-017**: The followed kitty MUST be marked on her card, and no other card
  may carry that marking.

**Persistence**

- **FR-018**: Camera mode, on or off, MUST survive a reload.
- **FR-019**: The followed kitty MUST survive a reload, identified by her id.
- **FR-020**: If a restored followed id matches no kitty in the world, the
  client MUST drop the follow and hold the group. Camera mode itself is
  unaffected.

**Scope and invariants**

- **FR-021**: Camera mode MUST remain a property of the view alone. It MUST NOT
  read, write, or influence any simulation state, in keeping with Article V.
  Two viewers watching the same world at different zooms see the same world.
- **FR-022**: The camera MUST be verified against 3-, 4-, and 5-kitty rosters,
  the three currently in use, and must satisfy every requirement here at each.
- **FR-023**: The cards MUST continue to show every kitty in the world,
  including any outside the frame, so a kitty who leaves the frame is still
  accounted for.
- **FR-024**: Ground decoration density MUST remain a property of the world, not
  of the frame. Scenery does not thicken or thin as the camera zooms.
- **FR-025**: The camera MUST NOT offer free panning or free zooming. The only
  controls are the toggle and the click-to-follow.

### Key Entities

- **Frame**: what the viewer sees — an aim point in world coordinates and a
  width in tiles. Derived fresh each frame from where the kitties are. Never
  stored in the world and never sent to the server.
- **Anchor**: the kitty the camera is currently aiming at. In group mode it is
  chosen by centrality and held by hysteresis; when a kitty is followed, she is
  the anchor.
- **Follow selection**: which kitty the viewer chose, or none. Identified by the
  kitty's authored id, and the one piece of camera state that outlives the page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With camera mode on, a kitty is drawn at least 1.3× her
  whole-world size at the widest the camera goes, and about 2× at nominal, on
  the same display.
- **SC-002**: Across a full observed session at 5 kitties, the camera never
  cuts: aim and width change continuously in every frame, with no visible jump
  at any group spread.
- **SC-003**: Motion stays as smooth with camera mode on as it is with camera
  mode off: the sustained frame rate on the same display is within 10% of the
  whole-world view's. Motion that stutters at the new scale fails this criterion
  regardless of how it looks when still.
- **SC-004**: With camera mode off, the rendered view is indistinguishable from
  the build shipped today.
- **SC-005**: The camera's aim always rests on a kitty. It never settles on
  empty ground.
- **SC-006**: With 5 kitties, the anchor changes no more than 3 times per minute
  in ordinary play, so the camera reads as deliberate rather than restless.
- **SC-007**: After a reload, the restored view is in place before the first
  painted frame. The viewer never sees the camera travel from a default position
  to the restored one.
- **SC-008**: A viewer can go from the whole-world view to following a chosen
  kitty in one action.
- **SC-009**: With reduced motion set, the camera performs no easing at all.
- **SC-010**: The camera is judged acceptable at 3, 4, and 5 kitties
  independently, with the 3-kitty case confirming that 10 tiles is the right
  floor and the 5-kitty case exercising the anchor hysteresis.
- **SC-011**: The same world observed by one viewer with camera mode on and
  another with it off shows identical kitty positions, activities, and needs at
  the same tick. The camera changes what is seen, never what happens.
- **SC-012**: Ground decoration is identical, tile for tile, at every camera
  width and between camera mode on and off.

## Out of Scope

- **Free pan and free zoom.** Not ruled out forever, but not this feature. The
  camera is automatic apart from the toggle and the follow.
- **Any engine or simulation change.** This is client-only work.
- **Re-deriving the control's placement.** The seat was built and dialled with
  the owner on 2026-08-16 and is settled: the sundial at `right: 8.4%`, the
  control at `1.5%`, the gap between them `1.65%`, the control's box `5.25%`,
  both pinned to the same horizon so one rule serves the phone and the desktop.
- **Removing the detail threshold.** Art detail keyed to drawn size will switch
  on and off as the camera zooms on some displays. The owner has accepted this
  for now; see Assumptions.
- **A separate phone layout.** One rule serves both, which was settled when the
  control was built.

## Assumptions

- **Clicking a kitty while camera mode is off turns camera mode on.** Assumed
  from the owner's stated intent rather than confirmed in so many words:
  following without the camera means nothing, and making the viewer operate two
  controls to follow one kitty would be a small cruelty. This is the one
  interaction rule in the feature that was inferred.
- **The nominal width is 10 tiles on every device**, phone included. kitten.me
  narrows to 8 tiles on phones; we do not, because one layout rule for both was
  already settled for the control and the same reasoning applies here. On a
  narrow phone this yields a smaller pixel tile than on a desktop, still roughly
  twice today's.
- **Detail that depends on drawn size may pop.** On a 1080p display the camera
  crosses the 44-pixel detail threshold within the 10–15 tile band, so the tabby
  forehead stripes, the bowl's fish decal, and the butterfly antennae appear and
  disappear as the group gathers and scatters. The owner's call is to ship with
  it and judge it in motion. The eventual fix is to ramp detail with size rather
  than switch it, since the threshold guards legibility rather than performance.
- **The art at the camera's scale needs no review.** The card portraits have
  always drawn at 47 pixels and the meadow already reaches 48–60 pixels on WQHD
  and 4K displays, so the fine detail has been looked at on this project at this
  size. It should still be watched in motion, as confirmation rather than
  judgement.
- **Kitty ids are stable and the roster only changes at its top end.** Ids are
  authored by hand in configuration and copied through world generation, never
  derived from spawn order. This is already load-bearing in shipped client code,
  where a kitty's coat is chosen by her id. It is what lets a restored follow be
  a plain presence check rather than a name match.
- **The indicator's position on the card is a layout judgement**, to be tried
  both beside and beneath the name before one is chosen. The spec requires the
  marking, not its placement.
- **The tile has never been fixed.** It already varies by nearly a factor of
  three across viewports, from 21 pixels on a laptop to 60 on a 4K display, so
  nothing in the renderer is entitled to assume a constant tile. A camera that
  recomputes it per frame is a smaller departure than it sounds.

## Dependencies

- **The control's seat**, built inert on branch `client-camera-notes`
  (`#camera-toggle` in `index.html`, `initCameraControl` in `app.js`, geometry
  pinned in `test-motion.mjs`). It is unmerged on purpose: an inert control
  should not reach production, so it lands with the behaviour this spec
  describes.
- **The client's existing preference storage**, the mechanism already used for
  the theme and the cards, which this feature follows rather than replaces.
