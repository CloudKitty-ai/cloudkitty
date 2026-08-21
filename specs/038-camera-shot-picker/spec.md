# Feature Specification: Camera shot picker

**Feature Branch**: `038-camera-shot-picker`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "Shot-picker camera: replace 036's aim-chase camera
model with a hold-until-broken shot grammar, grounded in the
client-measurements/camera-aim findings of 2026-08-20."

**Source material**: the 2026-08-20 design session (three owner rulings,
recorded under Clarifications) and `client-measurements/README.md` § camera-aim
— the aim-at-density refutation, the fit-never-governs finding, and the
shot-grammar simulation (`shot-survival.mjs`, fixture-verified). Where this
spec disagrees with the measurements' stated assumptions, this spec wins.

> **Supersedes parts of spec 036** (camera mode). This spec replaces 036's
> group-camera model: **FR-004** (fit every kitty), **FR-006** (aim at the
> most central kitty), **FR-007** (anchor hysteresis) and **SC-006** (anchor
> change rate). It heals 036 **SC-005**'s accepted deviation (empty frames
> while easing). Everything else in 036 — the control, following, persistence,
> the invariants, camera-off behaviour — stands, and 037's pixel band stays as
> the outer zoom bounds. A banner in 036 records the supersession.

## Overview

036's camera is a tracker: it continuously chases an aim derived from all five
kitties at once. Measurement shows what that buys — the camera is pinned at its
widest bound 87% of ticks (the fit never governs), and it is in motion on 60%
of ticks while its target only meaningfully moves ~4 times a minute (the rest
is easing tail). The owner's judgement of the result: "a little too active."

038 makes the camera a shot picker instead. It chooses a **shot** — the most
kitties whose groups can share a frame — sizes the frame to that shot, and then
**holds it perfectly still**. It corrects gently only when a member presses the
frame's edge, admits a nearby group by widening when the two can share the
frame, and re-frames deliberately — a rare fast pan — only when a strictly
bigger gathering persists somewhere the frame cannot reach by widening.

The design collapsed during the owner Q&A: a "transition" to a nearby group is
not a camera move at all, it is the frame widening to hold both groups while
the meadow decides which one survives. The only true transition left is the
far pan, and the measurement says it is rare (one in 4.7 minutes across every
tested configuration) — structurally, not luckily: on this world most rivals
can simply be admitted.

## Clarifications

### Session 2026-08-20

- Q: When a bigger group forms elsewhere while the camera holds a good shot,
  how eager should the switch be? → A: Patient, modulated by distance — a
  close rival may naturally converge or cross-pollinate with the current
  group, so hold; a distant one will not, so more eagerness helps. (In this
  spec, distance-modulation falls out of frame geometry: close rivals are
  admitted by widening, only far ones can force a transition.)
- Q: Does "interest" mean kitty count alone, or should activity matter? → A:
  Count only. Activities last under 10 ticks; "numbers will always win out in
  interest over 15+ ticks." 15 ticks is therefore the far-rival persistence
  bar.
- Q: Which transition grammar? → A: Breathe (widen until both groups share the
  frame, then tighten) with fast pan as the fallback; defocus cut dropped;
  dissolve cut held in reserve.
- Q (separate message, same session): design with spec 032's lookahead in
  mind? → A: Working camera logic comes first, but the design should be able
  to use up to 15 future frames later if that buys something substantial.

### Session 2026-08-21

- Q: When a single group is too spread to fit even the widest frame (42–61%
  of phone ticks in the sim), should the camera frame it partially or shed
  kitties until the rest fit fully? → A: Partial framing — centre the group
  and hold on its centre with a drift deadband; edge kitties may be
  half-visible and wander in and out of frame.
- Q: While following a kitty who has wandered off alone, should the camera
  show just her, or widen toward the nearest other kitty to keep two in
  frame? → A: Just her. Minimum-two is a group-mode rule; a follow is the
  viewer's explicit choice and exempts it.
- Q: If the destination group dissolves or shrinks while a far pan is in
  flight, should the camera commit and finish the pan, or abort and
  re-evaluate mid-flight? → A: Commit. Finish the pan, then let the normal
  grammar act from the destination.

### Session 2026-08-21 (code-review remediation)

- Q: When the viewer taps a kitty to follow while a committed far pan is in
  flight, should the camera finish the pan first (up to the pan's full
  duration of visible disagreement with the already-marked card) or redirect
  immediately? → A: Redirect immediately. Commitment protects against
  grammar dithering, not against the viewer; the redirect is one eased
  correction from wherever the pan had reached.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A camera calm enough to leave open (Priority: P1)

A viewer opens the meadow with camera mode on and leaves it in the corner of
her screen. The camera frames a group of kitties and then does not move — not
drifting, not creeping, genuinely still — until a kitty walks toward the edge
of the frame, at which point it eases once to re-centre and is still again.
The meadow reads like a nature documentary on a tripod, not a hand-held
follow.

**Why this priority**: This is the complaint the feature exists to fix. The
shipped camera is in motion most of the time, and nearly all of that motion
is easing toward a goal it has already reached. Stillness is the product.

**Independent Test**: With a 5-kitty roster in ordinary play, observe the
camera for several minutes. It is at complete rest most of the time; every
motion is a discrete, eased episode with a visible reason (a kitty pressing
the edge, a group admitted, a rare pan); no motion episode trails off into
sub-pixel creep.

**Acceptance Scenarios**:

1. **Given** a framed group whose members are all comfortably inside the
   frame, **When** they mill about without approaching its edge, **Then** the
   camera does not move at all — no drift of aim or width, however long the
   milling lasts.
2. **Given** a framed group, **When** a member walks toward the frame's edge,
   **Then** the camera makes one eased correction that restores comfortable
   room, and returns to complete rest.
3. **Given** any correction or transition, **When** it completes, **Then** the
   motion ends — it does not asymptotically creep toward its target.

---

### User Story 2 - The stage always has kitties on it (Priority: P1)

However the kitties scatter, the viewer always sees at least two of them. The
camera never frames empty meadow and never dwindles to a single-cat portrait
while a pair exists anywhere it could frame.

**Why this priority**: The owner's first-listed requirement. It also heals
036 SC-005's accepted deviation — under a shot grammar the subject is always
kitties, so an empty frame is impossible by construction rather than rare.

**Independent Test**: Across a long observed session, count kitties at least
partially in frame each tick. The count is ≥2 on effectively every tick, and
a frame with zero kitties never occurs outside the moving middle of a far
pan.

**Acceptance Scenarios**:

1. **Given** kitties scattered so that no two groups can share a frame,
   **When** the camera picks its shot, **Then** it frames at least two
   kitties.
2. **Given** every kitty solitary and the closest pair too far apart to both
   sit fully inside even the widest frame, **When** the camera picks its
   shot, **Then** it goes to its widest, centres on that closest pair, and
   tolerates a partially visible kitty rather than framing only one.
3. **Given** the shot's kitties disperse until fewer than two remain framed,
   **When** the shot breaks, **Then** the camera re-frames to the best
   available shot without ever showing an empty frame.

---

### User Story 3 - The camera finds the action (Priority: P2)

The viewer sees the biggest gathering the frame can hold. When a second group
wanders near, the camera widens to include it — showing the meeting rather
than choosing sides — and when a group disperses, the camera tightens onto
what remains. Kitties are drawn noticeably larger than under the shipped
camera, because the frame is sized to the group it holds instead of sitting
pinned at its widest.

**Why this priority**: Interest is the other half of the owner's balance.
Sizing to the shot is also what returns the zoom to service: measurement
shows the shipped camera at its widest bound 87% of ticks, where this grammar
sits there 0–5%.

**Independent Test**: In ordinary play, confirm the framed set is the biggest
gathering (or tied with it) nearly all the time; watch a widen-admission and
a tighten-after-dispersal happen; compare drawn kitty size against the
shipped camera on the same display.

**Acceptance Scenarios**:

1. **Given** a framed group and a separate group that could share a frame
   with it, **When** the second group persists nearby, **Then** the camera
   widens once to hold both, and does not instead jump between them.
2. **Given** a wide shot holding two groups, **When** one group disperses or
   walks out of reach, **Then** the camera eases tighter onto the group that
   remains.
3. **Given** a strictly bigger gathering somewhere the frame cannot reach by
   widening, **When** it persists for the owner's bar (~15 ticks), **Then**
   the camera commits to it with a single fast, eased pan — and an equal-size
   gathering never takes the shot from the incumbent.
4. **Given** ordinary play at five kitties, **When** frame widths are
   sampled, **Then** the camera spends most of its time meaningfully below
   its widest bound, and kitties are drawn correspondingly larger.

---

### User Story 4 - Following still works (Priority: P2)

The viewer clicks Clementine; the camera follows her exactly as 036 promised.
Under the hood the shot is now pinned to Clementine's group — so her
neighbours stay in frame, the frame is sized to her company rather than to
everyone, and no bigger gathering elsewhere can steal the camera while she is
followed.

**Why this priority**: Following is shipped behaviour with its own spec
(036 US2); this story exists to state how it composes with the new grammar
rather than to re-specify it.

**Independent Test**: Run 036 US2's independent test unchanged under the new
camera. Additionally confirm that while a kitty is followed, a larger
gathering elsewhere does not move the camera.

**Acceptance Scenarios**:

1. **Given** a kitty is followed, **When** the camera frames her, **Then**
   the shot is her group: she is always in frame, her nearby companions stay
   in shot, and the hold/correction behaviour of User Story 1 applies.
2. **Given** a kitty is followed, **When** a strictly bigger group persists
   far away, **Then** the camera stays with her — rival transitions are
   suspended while a follow is active.
3. **Given** a followed kitty is released, **When** the camera returns to
   group mode, **Then** it re-enters the grammar at the best current shot,
   eased, without a cut.
4. **Given** a followed kitty wanders off alone, **When** the camera frames
   her, **Then** the shot is her alone at the zoom-in floor — the frame does
   not stretch toward any other kitty.

---

### Edge Cases

- **Every kitty in one pile (night).** One group, one shot, at the zoom-in
  floor. The camera sits still for as long as the pile sleeps. Trivially the
  calmest case.
- **A single group wider than the widest frame.** The shot holds the group;
  the frame goes to its widest and centres the group, tolerating partially
  visible members at its edges, and the hold follows FR-007a (centre-drift,
  not member containment — the camera never chases edge kitties). Measured
  on the phone-width frame this is common (42–61% of ticks), so it is a
  first-class state, not an error.
- **Two equal-size groups, no incumbent (cold start).** The tie must resolve
  deterministically (not alternate); the first framed shot is in place before
  the first painted frame (036 SC-007's spirit — no travel from a default).
- **The shot's groups drift apart until they no longer fit together.** The
  camera sheds the fewest kitties needed to fit again (incumbency breaks
  ties), easing tighter — the "breathe in" half of the grammar.
- **A kitty joins or leaves the world mid-shot.** Roster changes re-evaluate
  the shot the same way membership drift does; a departed shot member is shed
  without a cut, an arriving kitty is just a new group of one.
- **The viewer resizes the window or rotates a phone mid-shot.** The frame
  keeps its shot and re-derives width against the new bounds; a shot that no
  longer fits sheds per the shedding rule.
- **Reduced motion.** Corrections, widens, and pans all arrive instantly with
  no easing (extends 036 FR-010 to every motion class in this grammar).
- **3-kitty roster.** The biggest possible group may be 2; minimum-two and
  the grammar hold unchanged (036 FR-022's roster range still applies).
- **A far pan crosses empty meadow.** The frame may briefly hold no kitty
  mid-flight; the pan is fast enough that this reads as a camera move, not an
  empty scene. Outside a pan's middle, a zero-kitty frame never occurs.
- **The roster empties mid-session (a reseed between generations).** With
  camera on and nothing to shoot, the frame eases home to the whole-world
  view in one episode and waits; returning kitties re-enter through the
  ordinary cold-start pick, eased (2026-08-21, code review).
- **The destination dissolves mid-pan.** The pan commits and completes; on
  arrival the ordinary grammar takes over (widen, shed, or break-reframe
  from the destination). The camera never swerves mid-flight.

## Requirements *(mandatory)*

### Functional Requirements

**The shot**

- **FR-001**: The camera's unit of state MUST be a shot: a set of kitties and
  a frame (centre and width) that holds them. The shot is derived from where
  kitties are and is a property of the view alone (036 FR-021 unchanged).
- **FR-002**: Kitties MUST be grouped by proximity: kitties within a link
  radius of one another belong to one group, transitively. The radius is a
  dial; its default is 5 tiles, the measured value at which group identity
  survives minutes and the phone re-frames least.
- **FR-003**: The shot MUST hold the largest number of kitties whose groups
  can share a frame within the zoom bounds. Ties keep the incumbent shot.
- **FR-004**: In group mode, at least two kitties MUST be in the shot
  whenever any two could share the widest frame. When they cannot, the
  camera MUST frame the closest pair at its widest and tolerate partial
  visibility rather than framing a single kitty. A follow exempts this rule
  (see FR-014): the viewer's explicit choice outranks the group-mode
  default.
- **FR-005**: The frame MUST be sized to the shot with breathing room that
  scales with the frame's width — a proportion of it, not a fixed world
  distance. (The shipped absolute margin is 68% of the phone's frame, which
  is why it must not survive.) The result is clamped by 037's pixel band and
  the world edge (036 FR-029 unchanged).

**The hold**

- **FR-006**: While every shot member sits inside an inner safe-zone of the
  frame, the camera MUST NOT move: aim and width are pinned exactly, with no
  easing residue. Reaching a target MUST end the motion (snap within a small
  epsilon), so no motion decays asymptotically.
- **FR-007**: When a shot member presses the safe-zone boundary, the camera
  MUST make one eased correction that restores comfortable room and then
  return to rest. Corrections use gentle easing, frame-rate corrected
  (036 FR-009 unchanged). Chained corrections are VELOCITY-CONTINUOUS
  (owner, 2026-08-21, live judging): while a correction's cause persists —
  a walking kitty re-pressing the frame — successive moves inherit their
  momentum and read as one continuous follow, never as surge-and-stop;
  the final move still ends in an exact snap and full rest.
- **FR-007a**: When the shot cannot fully fit the frame (an overflow shot —
  common on the phone), the hold applies to the shot's CENTRE instead of to
  member containment: the camera is still while the centre stays within a
  drift tolerance, and makes one eased correction when it drifts past.
  Kitties at the edges may be half-visible and wander in and out of frame;
  the camera MUST NOT chase them (owner, 2026-08-21).

**Membership**

- **FR-008**: The shot MUST follow its kitties: members who stay grouped stay
  in the shot, and a kitty who walks into a shot group joins the shot without
  any camera event beyond the ordinary hold/correction behaviour.
- **FR-009**: A separate group that could share the frame with the shot MUST
  be admitted by widening — never switched to — once it has persisted briefly
  (default 5 ticks). Admission is one eased widen.
- **FR-010**: When the shot's groups can no longer share a frame — sustained
  briefly (default 3 ticks; added 2026-08-21 at acceptance measurement, when
  un-dwelled sheds flapped at the link boundary 3–8/min, a rate the
  reference model could not see because it never counted sheds) — the camera
  MUST shed the fewest kitties that restores fit, keeping the larger count
  and breaking ties toward the current membership, then ease tighter. A shot
  kept wider than its need by more than a judged slack also eases tighter
  without any membership change (the standing 'breathe in'). The dwell
  applies identically during a follow — companions shed through the same
  clock, never instantly — and un-fit ticks spent in whole-shot overflow
  (nothing droppable) bank no dwell (both 2026-08-21, code review). The
  licence to shed is RESTORING fit: when no shed can bring the remainder
  under the ceiling (the followed kitty's own group past it, say), nothing
  is shed and the overflow centre-hold (FR-007a) governs (2026-08-21,
  high review).
- **FR-011**: If the shot falls below two kitties, it breaks: the camera MUST
  re-frame per FR-003/FR-004, eased, without a cut.

**The far transition**

- **FR-012**: A disjoint group MUST take the shot only if it is strictly
  bigger than the entire framed set, cannot be admitted by widening, and has
  persisted for the far-persistence bar — default 15 consecutive ticks, the
  owner's number. An equal-size group never takes the shot.
- **FR-013**: The far transition is a fast pan: a single continuous eased
  move on a visibly quicker profile than corrections. The camera MUST NOT cut
  (036 FR-008 upheld); a faster easing profile for this one move is the only
  amendment to easing behaviour. A pan, once begun, MUST run to completion
  even if the destination group changes mid-flight; the normal grammar
  resumes from the destination (owner, 2026-08-21). One exception, ruled
  the same day: a follow change mid-pan redirects the camera immediately
  (see FR-014) — the viewer outranks the commitment. Dissolve-style
  transitions are out of scope (held in reserve).

**Composition with 036**

- **FR-014**: While a kitty is followed (036 US2), the shot MUST be pinned to
  her group: she is unconditionally in the shot, FR-008–FR-011 apply to her
  group, and FR-012 transitions are suspended. If she is solitary, the shot
  is her alone — the camera does not widen toward other kitties to satisfy
  FR-004 (owner, 2026-08-21). A fresh pin acts at once: it replaces any
  in-flight episode, a committed pan included (owner ruling 2026-08-21),
  and previously admitted company that no longer fits alongside her group
  is dropped with the tap; companions of an ONGOING follow shed through
  FR-010's dwell instead. All 036 following, release, persistence, and
  card-marking requirements are unchanged.
- **FR-015**: With camera mode off, the client MUST render the whole world
  exactly as today (036 FR-002 unchanged). The control, its keyboard access,
  and camera-mode persistence are untouched.
- **FR-016**: With reduced motion set, every motion class in this grammar —
  correction, widen, shed, break re-frame, and pan — MUST arrive immediately
  with no easing.

### Key Entities

- **Group**: kitties linked by proximity (within the link radius,
  transitively). Exists only as a per-tick reading of the world; never stored.
- **Shot**: the camera's subject — a set of kitties plus the frame holding
  them. The incumbent shot carries identity across ticks (membership may
  drift kitty by kitty); it is the thing ties and rivals are judged against.
- **Rival**: a group disjoint from the shot. Near rivals (could share the
  frame) are admitted by widening; far rivals (cannot) may force the pan.
- **Evidence window**: the recent ticks over which persistence (FR-009,
  FR-012) is judged. Deliberately a window so a future lookahead buffer
  (spec 032) can substitute future ticks without changing the grammar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In ordinary 5-kitty play, the camera is at complete rest — no
  aim or width change whatsoever — on at least 60% of ticks (the shipped
  camera moves on 60%), and no motion episode trails off: once within a small
  epsilon of its target, motion stops on that frame.
- **SC-002**: At least two kitties are at least partially in frame on ≥99% of
  ticks, and a frame containing zero kitties never occurs outside the moving
  middle of a far pan. (Succeeds 036 SC-005 and closes its accepted
  deviation.)
- **SC-003**: Re-framing events of every kind — widens, sheds, breaks, pans —
  total at most 3 per minute in ordinary play, and far pans alone at most 0.5
  per minute. (Succeeds 036 SC-006's ≤3/min bar; simulation measured ≤1.7
  and ≤0.21 respectively.)
- **SC-004**: The camera spends at most 20% of ticks at its widest bound in
  ordinary 5-kitty play on a desktop viewport (the shipped camera: 87%), and
  the median drawn kitty is at least 1.2× her size under the shipped camera
  on the same display (simulation: 1.45×).
- **SC-005**: The framed set is the largest gathering the frame could hold,
  or tied with it, on at least 90% of ticks; mean kitties in frame in
  ordinary 5-kitty play is at least 3.
- **SC-006**: Every 036 User Story 2 acceptance scenario (following) passes
  unchanged under the new grammar, plus: a followed kitty is never abandoned
  for a bigger gathering.
- **SC-007**: With camera mode off, the rendered view is indistinguishable
  from the shipped build (036 SC-004 continuity).
- **SC-008**: With reduced motion set, no easing occurs at any motion class,
  pan included.
- **SC-009**: The first framed shot after load is in place before the first
  painted frame; the viewer never sees the camera travel from a default
  (036 SC-007 continuity).
- **SC-010**: The camera is judged acceptable at 3, 4, and 5 kitties
  (036 FR-022's rosters), and on the phone's frame — where a shot wider than
  the frame is common — a centred, partially visible group reads as a
  deliberate framing, with break re-frames at most 1 per minute (simulation:
  0.43).

## Out of Scope

- **Dissolve and defocus transitions.** Dissolve is held in reserve if live
  judging finds long pans unpleasant; it would need its own amendment to the
  no-cut rule. Defocus is dropped (full-canvas blur is expensive on phones
  and tonally wrong).
- **Spec 032 lookahead.** The evidence window is shaped for it, but no
  lookahead is built here. When 032 lands, the named opportunity is
  pre-framing (framing a group's near-future sweep to reduce corrections),
  not the switch logic — pans are too rare to justify it.
- **Free pan and free zoom, the control's placement, keyboard following** —
  unchanged from 036's scope decisions.
- **Any engine or simulation change.** Client-only, deployable
  `--client-only` during the phase-1 wall window.
- **Re-tuning 037's pixel band** (floor/ceiling/minTiles/minZoomVsBase/
  ceilingRows). They stay as the outer clamps exactly as shipped.

## Assumptions

- **Dial defaults are measured, not sacred**: link radius 5 tiles, near
  persistence 5 ticks, far persistence 15 ticks (the owner's number; ticks
  are ~0.8s), shed persistence 3 ticks and tighten slack 1.15× (both added
  at acceptance measurement, 2026-08-21 — see acceptance-2026-08-21.md),
  breathing room ~20% of frame width per side (the desktop equivalent of
  today's margin, now proportional). All are lab dials to be
  judged live per house method; the grammar does not depend on their exact
  values.
- **The measurement basis is one 4.7-minute daytime sample** of one
  generation's clustering (350 ticks, 5 kitties, local world). Rates in the
  SCs carry generous headroom over the simulated values for exactly that
  reason; the grammar's structural findings (rivals are mostly admissible,
  survival is minutes) do not depend on the sample's fine detail.
- **The safe-zone is an inner region of the frame** whose size is a dial;
  corrections re-centre with enough lead room that a steadily walking group
  produces occasional discrete corrections, not continuous tracking.
- **Persistence is judged over a window of recent ticks** held by the
  camera; spec 032 would substitute future ticks in the same window. This is
  the one piece of architecture this spec fixes on purpose, at the owner's
  request.
- **Night resolves to a single static shot** (one sleeping pile at the zoom
  floor); no special-casing is needed or wanted.
- **036 remains the base spec** for everything not named here; where this
  spec is silent, 036 (as amended by 037) governs.

## Dependencies

- **Spec 036** (camera mode) — the base feature this amends; its banner gains
  a supersession note pointing here.
- **Spec 037** (camera zoom targets) — supplies the zoom bounds this grammar
  is clamped by.
- **`client-measurements/camera-aim/`** (PR #279) — the refutation, the
  fit-never-governs finding, and the grammar simulation this spec's numbers
  come from. Merging #279 before implementation keeps the references
  resolvable from `main`.
- **Spec 032** (future) — optional lookahead source for the evidence window;
  not required.
