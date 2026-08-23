# Research: Camera shot picker (Phase 0)

No external unknowns — the "research" for this feature was performed as
measurements before the spec existed (`client-measurements/camera-aim/`,
PR #279): the aim-at-density refutation, the fit-never-governs finding, the
group-survival numbers, and a fixture-verified simulation of the settled
grammar. What remains for Phase 0 is fixing the design decisions the spec
deliberately left to planning. Thirteen, each with rationale and the
alternative rejected.

## D1 — Where the grammar lives

**Decision**: Inside the existing `Camera` class in `client/anim.js`. The
external contract is frozen: `update(world, view, { aspect, cssWidth })` in,
`left`/`top`/`across` out, `limitsFor` untouched.

**Rationale**: `render.js` reads exactly those three numbers (draw offset,
tile, letterbox predicate reads `camera.on`); preserving them makes this a
one-file change and keeps 037's single-derivation invariant
(`contracts/zoom.md` invariant 2) intact for free.

**Alternatives**: a separate `shot.js` module — rejected: a new script tag and
load-order entry for ~200 lines that only the camera calls; the class already
separates "wanting" (`targetFor`) from "getting there" (`update`), which is
the seam the grammar slots into.

## D2 — Decide on ticks, move on frames

**Decision**: Grammar decisions (grouping, chains, dwell evidence, shot
membership, episode triggers) run once per WORLD TICK — detected by
`world.tick` changing in `update`. Motion (episode progress, hold checks)
runs per frame against DRAWN positions (`view.posFor`, the 036 lesson: never
aim at served positions).

**Rationale**: dwells are defined in ticks (owner's 15); deciding per frame
would make dwell counts frame-rate dependent. The split also makes the
grammar drivable tick-by-tick in the harness with no animation clock.

**Alternatives**: decide per frame with millisecond dwells — rejected:
re-derives tick length (800ms) as a magic number and couples grammar tests to
the frame clock.

## D3 — Grouping and the 2D fit

**Decision**: Groups are connected components over kitty drawn positions with
link distance `linkTiles` (default 5). Fit uses the EXISTING width-cost
idiom: `widthNeeded = max(spanX + margins, (spanY + margins) / aspect)`;
a set fits iff `widthNeeded <= ceilingTiles`.

**Rationale**: the current `targetFor` already prices the vertical span in
width units via the canvas aspect — the client was 2D-correct all along (the
sim's width-only span was the approximation, noted at clarify). L=5 is the
measured radius: group identity survives median 88s, phone breaks 0.43/min.

**Alternatives**: L=4 (twitchy on the phone: 2.36 breaks/min), L=6 (merges
nearly the whole roster). Radius-from-seed neighbourhoods (the refuted
density rule) — wrong shape for membership: not symmetric, not transitive.

## D4 — Proportional margin replaces `fitMarginTiles`

**Decision**: `fitMarginTiles: 2.6` is removed. New dial `fitMarginFrac`
(default **0.195**, per side, of frame width). Margins enter the fit as
`widthNeeded = span / (1 - 2 * fitMarginFrac)`.

**Rationale**: 2.6 tiles/side is 39% of the desktop ceiling but 68% of the
phone's 7.6-tile frame — the phone overflow finding (spec FR-005). 0.195 is
the desktop-equivalent (2.6 / 13.33), so desktop framing is unchanged to
within a tenth of a tile while the phone margin scales down to ~1.5 tiles.

**Alternatives**: per-viewport margin table — rejected: a proportional dial
is one number and needs no breakpoints.

## D5 — Rival identity: majority-overlap chains

**Decision**: Dwell evidence keys on GROUP CHAINS, not exact member sets: a
group this tick continues a chain from last tick when they share at least
half the larger's members; counters live on chains.

**Rationale**: groups churn members while staying put. Exact-set keying
(the sim's conservative shortcut) resets a rival's clock on every join/leave
— a rival that churns one member every 14 ticks would never pan. Chaining
matches the survival measurement's definition, so the measured "minutes"
apply to the thing the counters count.

**Alternatives**: exact-set keying — rejected as above; centroid-distance
matching — rejected: two distinct groups can swap positions.

## D6 — Cold start and ties

**Decision**: With no incumbent, take the maximal-count window; ties resolve
to the candidate containing the lowest kitty id. With an incumbent, ties
always keep the incumbent (spec FR-003).

**Rationale**: deterministic, roster-order-proof, and the same tie idiom
`anchorFor` already uses (ids, never array order). The first decided shot is
in place before the first painted frame (SC-009) because `update` already
arrives-not-eases when `this.across` is 0.

**Alternatives**: nearest-to-world-centre — rejected: two equidistant groups
re-introduce a tie that ids already settle.

## D7 — Motion episodes replace continuous easing

**Decision**: Camera-mode motion becomes discrete EPISODES: a move latches
its goal (aim + across) at start, eases with cubic ease-in-out over a fixed
duration (`moveMs` gentle, `panMs` fast), SNAPS exactly to the goal on
arrival, and returns to REST. At rest the camera copies nothing and eases
nothing. `panRate`/`zoomRate` (exponential pursuit) are removed from
camera-mode paths.

**Rationale**: exponential easing never arrives — that IS the measured
easing tail (camera moving 60% of ticks against a target that moves 4/min).
Duration-based episodes are frame-rate independent by construction
(`t = elapsed/duration`), satisfy FR-006's snap requirement literally, and
make "at rest ≥60% of ticks" (SC-001) a state check rather than a threshold
check.

**Alternatives**: keep exponential easing + epsilon snap — rejected: still
retargets every frame while the goal drifts, so rest becomes an accident of
the deadzone rather than a state; harder to test.
**Interactions preserved**: reduced motion arrives instantly (episode
duration treated as 0); `view.still` frames hold (no episode progress — a
still frame is the same moment); camera off/on keeps its existing
arrive-not-ease cut.

## D8 — Hold triggers: safe-zone, and centre-drift for overflow

**Decision**: While at rest, per frame: if the shot FITS the frame, a
correction triggers when any member's drawn position exits the inner
safe-zone (`safeZoneFrac`, default 0.92 of the frame per axis; 0.80 until the 2026-08-21 calm pass, 0.88 until the 2026-08-22 re-census). If the shot
OVERFLOWS (fit > frame), the trigger is instead the shot's bounding-box
centre drifting more than `aimDeadzoneTiles` from the frame's aim
(spec FR-007a). The correction's latched goal re-centres on the current
bbox centre at the current fit width (clamped to bounds).

**Rationale**: member containment is meaningless for a shot the frame cannot
contain (42–61% of phone ticks); centre-drift with the existing deadzone
dial is the owner's clarified rule and reuses a shipped, judged constant.

**Alternatives**: velocity-led framing (lead the walkers) — deferred to
spec 032 pre-framing, where it belongs; a fresh overflow-tolerance dial —
rejected: `aimDeadzoneTiles` already expresses "how far the subject may
wander before the camera cares."

## D9 — Episode kinds and priorities

**Decision**: One episode at a time. Kinds, by precedence at decision time:
**pan** (committed: runs to completion, no re-decision until arrival, spec
FR-013) > **break re-frame** > **shed** > **widen** > **correction**. A
fresh trigger at REST starts one episode; mid-episode (except mid-pan) a
moved goal RE-LATCHES a new episode that inherits the old one's position
AND VELOCITY (a cubic Hermite with the carried tangent, landing at rest),
at any cadence — per frame during a live chase. (Thrice amended
2026-08-21, each cut teaching the next: restarting the clock at zero
velocity per frame was the crawl; mutating the in-flight goal was a
single-frame cut past the aim-lead pin; a hysteresis band between the two
produced rest-to-rest S-curve CHAINS that the owner judged live as "fits
and starts". Velocity carry dissolves the trilemma: restarts are free, so
a walker is ONE continuous tracked move that still ends in an exact snap
when its cause clears, and rest remains bit-still. The `relatchTiles`
band was retired the day it was born.) The pan's commitment has one
exception: a viewer follow change redirects immediately (owner ruling
2026-08-21).

**Rationale**: the spec makes pan the only committed move; everything else
may be superseded by fresher geometry, but episodic re-aiming (not
per-frame episode restarts, not pursuit) is what keeps every move finite.

**Alternatives**: a full interrupt queue — rejected: nothing in the grammar
generates bursts (events measured ≤1.7/min).
**Known and accepted**: a pan's goal latches at start, so the destination
group walks ~1.4 tiles during `panMs` and arrival may earn one immediate
correction — a counted, deliberate move inside SC-003's budget. The
eventual remover is spec 032 pre-framing (D10), not a smarter pan.

## D10 — The evidence function (the 032 seam)

**Decision**: One function owns persistence: it consumes the per-tick group
chains and returns, per chain, how many consecutive ticks the chain has been
(a) admissible-near or (b) a strictly-bigger far rival. Dwell thresholds
(`nearDwellTicks` 5, `farDwellTicks` 15) are compared OUTSIDE it. Today it
counts backwards over lived ticks; under 032 the same signature reads the
lookahead buffer instead.

**Rationale**: the owner's forward-compat instruction, made concrete: swap
the window's source, keep the grammar. Also the natural unit-test seam.

**Alternatives**: counters inlined in the decide loop — rejected: welds the
grammar to the backward window.

## D11 — What happens to the anchor machinery

**Decision**: `anchorFor` and the `hysteresis` dial are DELETED. `anchorId`
the field remains, holding the followed kitty's id or null (render/app read
nothing else from it; card marking keys on `followId`).

**Rationale**: the shot replaces the anchor as subject; 036 SC-006 is
superseded by 038 SC-003 (spec banner). Keeping dead hysteresis code would
invite the next reader to re-enable it.

**Alternatives**: keep `anchorFor` for the overflow aim point — rejected:
the overflow aim is the bbox centre by the owner's clarified rule, and a
centre is acceptable there precisely because the group is bigger than the
frame (empty-grass aim, FR-006's old concern, cannot drop anyone the frame
was going to show).

## D12 — Follow mode composition

**Decision**: `followId` pins the shot to the followed kitty's group: shot =
her chain (plus ordinary admissions), far-rival evidence is not evaluated,
minimum-two is not enforced (clarified: solitary follow frames her alone).
All 036 follow mechanics (click/release/persistence/card marking, FR-020
roster-drop) are untouched.

**Rationale**: spec FR-014 verbatim; the implementation is one branch in the
decide step choosing the subject chain.

## D13 — Dial inventory (all in `VIEW.camera`, documented defaults)

| Dial | Default | Status |
|---|---|---|
| `linkTiles` | 5 | new — measured (D3) |
| `nearDwellTicks` | 10 | owner-judged at the calm pass (2026-08-21; was 5) |
| `farDwellTicks` | 15 | new — the owner's number |
| `shedDwellTicks` | 3 | new — added at acceptance (shed flap, see acceptance-2026-08-21.md) |
| `tightenFrac` | 1.2 | added at acceptance (1.15); relaxed at the calm pass (2026-08-21 — the breathe-in was the calm-spell breaker; 1.3 broke SC-004) |
| ~~`relatchTiles`~~ | — | retired same-day (2026-08-21): the hysteresis existed only because re-latches zeroed velocity; velocity carry (D9) made it moot |
| `pressDwellTicks` | 3 | new at the calm pass (2026-08-21): persistence before correction; frame-edge and empty-frame escapes bypass it |
| `safeZoneFrac` | 0.92 | owner-judged 2026-08-22 after the Biscuit 2.0 re-census (was 0.88, was 0.80): a tighter clowder puts nearly all five cats in one frame, so the press is persistent and only a wider deadzone answers it |
| `moveMs` | 2000 | owner-judged LIVE at the T026 dial pass (2026-08-21; 700 and 1000 both read too fast) |
| `panMs` | 3000 | owner-judged live with moveMs, same session (was 1100) |
| `fitMarginFrac` | 0.195 | new — replaces `fitMarginTiles` (D4) |
| `aimDeadzoneTiles` | 1.5 | kept — new role: overflow centre tolerance (D8) |
| `floorPx ceilingPx minTiles minZoomVsBase ceilingRows maxFrameMs` | as shipped | kept — 037 bounds, out of scope |
| `fitMarginTiles` | — | REMOVED (D4) |
| `hysteresis` | — | REMOVED (D11) |
| `panRate zoomRate` | — | REMOVED from camera-mode paths (D7) |

Dial-judging protocol per house method: defaults ship to the lab first
(local 5-cat world), owner pastes the judged values, then they bake.
