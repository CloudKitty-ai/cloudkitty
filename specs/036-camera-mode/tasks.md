---

description: "Task list for 036 camera mode"
---

# Tasks: Camera mode

**Input**: Design documents from `/specs/036-camera-mode/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/camera.md, quickstart.md

**Tests**: Included. Constitution Article VI makes the suites a CI gate, CLAUDE.md
requires tests for your own changes, and SC-005 asks for a harness assertion by
name. Extend `client/test-motion.mjs` and `client/test-meadow.mjs`; do not add a
third harness.

**Organization**: Tasks are grouped by user story so each ships independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel — different files, no dependency on incomplete work
- **[Story]**: US1–US4, matching the spec's prioritised stories

## Path Conventions

Flat `client/` layout, plain scripts, fixed load order, no build step. Every path
below is repository-relative and real.

**A note on [P] in this feature.** Five files carry almost all the work, and
`render.js` and `app.js` each carry a lot of it. Genuine parallelism is
therefore scarce, and it is marked only where two tasks truly touch different
files. Do not read the shortage as a mistake — a five-file client is not a
microservice fleet, and marking everything [P] would just invite merge
conflicts.

---

## Phase 1: Setup

**Purpose**: Get the seat in place and capture the baselines that two success
criteria are measured against.

- [X] T001 Merge `origin/client-camera-notes` into `036-camera-mode` to bring the inert control (`#camera-toggle` and `.camera-chip` in `client/index.html`, `initCameraControl` in `client/app.js`, its geometry checks in `client/test-motion.mjs`). Merge, never rebase. Without it the toggle has no seat.
- [ ] T002 Record the pre-change baseline for SC-003 and SC-004: sustained frame rate on a fixed viewport, a full-day ground-cache bake count, and reference screenshots of the whole-world view. Store under `client-measurements/036-camera-baseline/`. **Capture this before any code changes** — both criteria are comparisons against today, and today stops existing after T004. The frame rate and bake count are machine-readable and gate T022; the screenshots are the owner's reference for SC-004 and gate nothing automatically, since the draw-call check in T012 is the real guarantee there.
- [X] T003 [P] Confirm the harness baseline: `node client/test-motion.mjs` (164 checks) and `node client/test-meadow.mjs` (78 checks) both green on the merged branch.

**Checkpoint**: Seat present, baselines banked, suites green.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: All the plumbing a camera needs, landed behind an **identity
camera** that frames the whole world — so this entire phase is provably a no-op.

**⚠️ CRITICAL**: No user story can begin until T012 proves the plumbing changed
nothing. This mirrors the bit-identical methodology from the 018–020 refactor
arc: land the mechanism first and prove it inert, then give it behaviour.

- [X] T004 Add the `VIEW.camera` dial block to `client/anim.js` beside the existing `VIEW` groups: `nominalAcross: 10`, `ceilingFactor: 1.5`, `fitMarginTiles: 2.6`, `panRate: 0.06`, `zoomRate: 0.05`, `hysteresis: 1.5`, `hitRadiusFloorPx`. Values are starting points for the dialling session in T045, not results.
- [X] T005 Add per-frame `dt` to the animation object in `client/anim.js`: keep `lastFrameAt`, derive `dt`, and clamp it so a backgrounded tab returning after 30s cannot produce an easing factor of 1, which would read as the cut FR-008 forbids.
- [X] T006 Create the camera object in `client/anim.js` with the surface from `contracts/camera.md`: `update(world, view, now)`, `tile`, `left`, `top`, `anchorId`, `toWorld()`. For this phase `update` returns the whole-world frame, so the camera is an identity.
- [X] T007 Apply the camera in `client/render.js`'s draw entry: set `this.tile = camera.tile` for scale, then `ctx.translate(-camera.left * tile, -camera.top * tile)` for pan, resetting the transform each frame. **Do not use `ctx.scale`** — `this.tile` is what `fine = size >= 44` reads, and the whole feature depends on that staying honest.
- [X] T008 Rework the ground cache in `client/render.js` `blitGround`: bake at `bakeTile` (the tile at the narrowest frame, the largest the camera can ask for) into an offscreen sized to the whole world, and blit the visible sub-rectangle with the nine-argument `drawImage`. Add `bakeTile` to the staleness check beside dpr and canvas width.
- [X] T009 Clamp `bakeTile` by a device-pixel budget in `client/render.js` so the offscreen stays under mobile Safari's canvas area cap, accepting magnification past the clamp. An unclamped bake is a blank canvas on an iPad, not a slow one.
- [X] T010 Fix the pond cache in `client/render.js` `drawPondLayer`: add `bakeTile` to `signature`, and bake paths and layers at `bakeTile`. Today the signature is the water tile positions alone and is safe only because `resizeFor` nulls the cache on canvas resize — a camera changes the tile with no resize, so ponds would draw at the previous zoom's geometry, silently.
- [X] T011 Update `buildPondLayers` in `client/meadow.js` to take the bake dimensions rather than reading `canvas.width` / `canvas.height`, since the bake is larger than the canvas. Leave `driftField(width, height, t)` receiving **world** dimensions — window dimensions there would change decoration density with zoom (FR-024).
- [X] T012 **The gate, mechanical.** Add the identity-camera checks to `client/test-motion.mjs` and `client/test-meadow.mjs`: with the identity camera the draw-call sequence is command-for-command what it was before this phase, the ground bakes once over a full world day, the pond cache invalidates on a `bakeTile` change, and `world` is never mutated (Article V, FR-021). All four run in the existing harnesses, and all four block.
- [X] T012a **Confirmation, owner-run, does not block.** Compare the rendered page against the T002 reference screenshots. No headless browser is available here, so this is the owner's eye. Keep it out of the gate — the draw-call check in T012 is the stronger guarantee anyway. **Confirmed by the owner 2026-08-17**, side by side on two servers running the same seed and config at the same tick: indistinguishable.

**Checkpoint**: The client looks and performs exactly as it did at T003, with a
camera underneath it. If anything moved, stop here — every later phase assumes
this one is inert.

---

## Phase 3: User Story 1 — See the kitties at a size worth looking at (P1) 🎯 MVP

**Goal**: The control turns the camera on, and it holds the group at a legible
scale, easing and never cutting.

**Independent Test**: Turn the control on with a 5-kitty roster and watch several
hundred ticks. Kitties are visibly larger, the frame tracks them, motion never
cuts, and turning it off returns the view from T002.

### Tests for User Story 1

- [X] T013 [P] [US1] Frame geometry checks in `client/test-motion.mjs`: nominal is a floor a huddled group cannot pass (FR-004), the ceiling binds at 1.5× nominal (FR-005), no kitty is drawn touching the frame edge when the fit binds (FR-004), and the frame clamps to the world so no void is ever shown, including a kitty followed into a corner (FR-029).
- [X] T014 [P] [US1] Anchor checks in `client/test-motion.mjs`: the anchor is always a kitty id present in the roster and never a computed midpoint (FR-006, SC-005), it is the kitty nearest the centre of mass, and ties resolve deterministically rather than alternating between frames.
- [X] T015 [P] [US1] Hysteresis check in `client/test-motion.mjs`: the anchor changes only when another kitty is at least 1.5× more central (FR-007), driven by a scripted 5-kitty walk that would flick without it.
- [X] T016 [P] [US1] Easing checks in `client/test-motion.mjs`: with a synthetic `dt`, a 120Hz frame sequence settles in the same real time as a 60Hz one (FR-009), aim settles slightly faster than width, no frame moves further than the rate allows (SC-002), and a clamped huge `dt` still does not cut. With `reduced` set, the camera reaches its target in a single update with no intermediate frames (FR-010, SC-009). Add a **source-shape assertion that `camera.update` is reached from the redraw path and not only from the rAF callback** — this is the one failure in the feature that looks perfect in testing and is frozen for every reduced-motion viewer, and the harness already catches dropped wiring this way.

### Implementation for User Story 1

- [X] T017 [US1] Implement the fit in the camera's `update` in `client/anim.js`: bounding box of drawn kitty positions plus `fitMarginTiles`, floored at `nominalAcross` and ceilinged at `nominalAcross × ceilingFactor`. Read positions via `view.posFor(kitty)`, never `kitty.pos` — served positions make the camera lead the cats and pulse once per tick.
- [X] T018 [US1] Implement the anchor in `client/anim.js`: the kitty nearest the group's centre of mass, with the 1.5× hysteresis holding the current one. Not the bounding-box midpoint and not the centre of mass, both of which are usually grass.
- [X] T019 [US1] Implement frame-rate-corrected easing on aim and width in `client/anim.js` using `1 - (1 - rate) ** (dt / 16.67)`, and the world clamp from `data-model.md`.
- [X] T020 [US1] Wire the reduced-motion path in `client/anim.js`: snap instead of easing, and call `camera.update` from the served-tick redraw as well as the rAF loop. `startLoop` is skipped entirely under reduced motion, so a camera advanced only in the rAF callback is frozen for those viewers.
- [X] T021 [US1] Give `initCameraControl` in `client/app.js` its behaviour: flip `cameraOn`, drive the camera, keep `aria-pressed` in sync. The control's placement, geometry and hit area are settled — change none of them.
- [X] T050 [US1] Fix `drawGroundAmbient` in `client/render.js` to derive the world's drawn extent from `world.width * this.tile`, not `cssWidth`/`cssHeight`. Review finding F2: it is the one place the "everything downstream goes through `this.tile`" audit is wrong, and it is harmless only while `targetFor` returns the whole world — which this phase changes. At `across = 10` on a 620px map both cloud shadows crowd into the top 36% of the meadow. Correct `contracts/camera.md`, which currently claims the opposite.
- [ ] T051 [US1] Give the pond layers a source rectangle in `client/meadow.js` `drawPonds`, as `blitGround` has. Review finding F8: with no source rect, camera scale downscales a 4x-larger image every frame of which most pixels are off-frame, and the fills, clips and caustics run over every pond in the world whether visible or not.
- [ ] T052 [US1] Bound the pond layers' total allocation in `client/render.js`. Review finding F6: `buildPondLayers` allocates FOUR canvases at bake size, so camera mode quadruples each. `GROUND_BAKE_MAX_PX` bounds one canvas's side while mobile Safari caps total canvas memory — the budget guards the wrong quantity, on the platform it was added for.
- [ ] T053 [US1] Round the ground blit's source rectangle against the rounded bake dimensions in `client/render.js`. Review finding F9: `bakeW` is `Math.round`ed and the source rect is not, so on fractional dpr the source can exceed the image and `drawImage` clips source and destination together, leaving a sub-pixel unpainted strip at the right and bottom.
- [ ] T022 [US1] Verify SC-003 against the T002 baseline: sustained frame rate within 10%, and the ground-cache bake count over a full world day still bounded. If the frame rate regressed, read the bake count first — a count is diagnostic where fps is only a symptom.

**Checkpoint**: MVP. Camera mode works end to end with no clicking, no selection,
and nothing to learn. Deployable on its own.

---

## Phase 4: User Story 2 — Watch one kitty in particular (P2)

**Goal**: Clicking a kitty follows her; clicking her again, or clicking away,
releases her.

**Independent Test**: With camera mode on, click each kitty in turn and confirm
the camera aims at her and stays through her whole activity including sleep.
Release both ways.

### Tests for User Story 2

- [X] T023 [P] [US2] Transform round-trip check in `client/test-motion.mjs`: `toWorld(forward(p)) === p` across the whole zoom range and at several pan offsets. This is the highest-value new check — it is what stops the forward and inverse transforms drifting apart, whose only symptom is clicks landing on the wrong kitty at some zooms.
- [X] T024 [P] [US2] Follow lifecycle checks in `client/test-motion.mjs` covering every row of the table in `data-model.md`, including the two that are decisions rather than restatements: the toggle never releases a follow (FR-027), and release works whenever a follow exists regardless of camera mode.
- [X] T025 [P] [US2] Hit-test checks in `client/test-motion.mjs`: overlapping kitties resolve to the frontmost in depth order, the hit radius floor keeps a kitty selectable at the zoom ceiling on a phone-sized canvas, and anything that is not a kitty counts as a release.
- [X] T026 [P] [US2] Follow-behaviour checks in `client/test-motion.mjs`: a followed kitty is the anchor unconditionally with no hysteresis (FR-015), following does not narrow the frame (FR-014), and a sleeping followed kitty is never auto-released (FR-016).

### Implementation for User Story 2

- [X] T027 [US2] Implement `camera.toWorld` in `client/anim.js` as the derived inverse of the draw transform, not a separately written one. Divide by the measured `rect.width`, never `this.cssWidth` — `resizeFor` applies a display scale, so the canvas's layout size and drawing size differ.
- [X] T028 [US2] Add the canvas pointer handler in `client/app.js`. No click handling exists on the canvas today, so this is new: convert to world coordinates, pick the frontmost kitty within the hit radius, and treat everything else as a release.
- [X] T029 [US2] Implement the follow state and its full lifecycle in `client/app.js` per the `data-model.md` table, including FR-012 (a click while off enables and follows) and FR-026 (clicking away releases).
- [X] T030 [US2] Make the followed kitty the unconditional anchor in `client/anim.js`, bypassing the hysteresis that governs group mode.
- [X] T031 [US2] Drop the follow when the followed kitty leaves the roster while the page is open, holding the group and leaving camera mode untouched (FR-020). This path is needed here, not only at restore.

**Checkpoint**: US1 and US2 both work independently.

---

## Phase 5: User Story 3 — The meadow remembers how I was watching it (P3)

**Goal**: Camera mode and the followed kitty both survive a reload.

**Independent Test**: Set each of the three states, reload, confirm each returns.
Then remove the followed kitty from the roster, reload, confirm the view opens
holding the group.

### Tests for User Story 3

- [X] T032 [P] [US3] Persistence checks in `client/test-motion.mjs`: both keys round-trip, a restored id matching no kitty is dropped while camera mode is unaffected (FR-020), and an unreadable store falls back to defaults with the feature still working.

### Implementation for User Story 3

- [X] T033 [US3] Add `cloudkitty-camera` and `cloudkitty-follow` to `client/app.js` following the `THEME_KEY` / `CARDS_KEY` pattern: read once at startup inside a `try`, write on change. `localStorage` throws rather than returning null in some privacy modes.
- [X] T034 [US3] Restore both at startup in `client/app.js`, dropping a followed id that matches no kitty in the world.
- [X] T035 [US3] Confirm SC-007 by inspection and by reload: the restored view is in place on the first painted frame. The meadow already paints nothing until a world state exists (`anim.js` guards redraw on `presentation.curr`), so there is no default position to travel from — verify that guard still holds rather than adding a second one.

**Checkpoint**: All three states survive a reload.

---

## Phase 6: User Story 4 — Know which kitty I am following (P4)

**Goal**: The followed kitty's card is marked, and no other card is.

**Independent Test**: Follow each kitty in turn, confirm exactly one card is
marked and it is the right one. Release, confirm none is.

### Tests for User Story 4

- [X] T036 [P] [US4] Card marking checks in `client/test-motion.mjs`: exactly one card carries the marking while a kitty is followed, none after release, and the marking survives a card rebuild.

### Implementation for User Story 4

- [X] T037 [US4] Add the follow marking to the card build in `client/app.js`: an indicator around the card plus *following* in italics near the name.
- [X] T038 [US4] Add the marking's styles to `client/index.html`, both themes, respecting `prefers-reduced-motion` on any transition.
- [X] T039 [US4] Show the marking for a dormant follow — one held while camera mode is off. This is the plan's call rather than the spec's: hiding it would mean toggling camera mode on jumps to a kitty the viewer had no way to know was still selected. Flag it to the owner at T045; it is cheap to reverse.

**Checkpoint**: All four stories independently functional.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T040 Run the full `quickstart.md` validation sweep at 3, 4 and 5 kitties (FR-022, SC-010), recording results per roster size rather than in aggregate, and explicitly sweeping SC-001 (apparent size at nominal and at the ceiling, measured against the T002 baseline) and SC-008 (one action from the whole-world view to following a chosen kitty).
- [ ] T041 [P] Verify SC-011 and SC-012: two browsers on one world at different zooms show identical positions, activities and needs at the same tick, and ground decoration is identical tile for tile at every camera width.
- [ ] T042 [P] Verify SC-014 and FR-028: the control is reachable and operable by keyboard alone with a visible focus state. Following stays pointer-only by decision, so this is the accessibility property that must not regress.
- [ ] T043 [P] Check the phone at the zoom ceiling, the worst case for every interaction number in the feature: a kitty near 23px, moving, possibly overlapped. SC-013 exists because of it.
- [ ] T044 [P] Add the `## Unreleased` CHANGELOG entry in `CHANGELOG.md`, in the register that file keeps.
- [ ] T045 Dialling session with the owner on the values this plan deliberately left open: easing rates, fit margin, hysteresis margin, the card indicator's position beside or beneath the name, and whether the dormant-follow marking from T039 is right. Judge in motion, at the live size — not in the gallery, and not from screenshots.
- [ ] T046 Judge the `fine` pop in motion on a 1080p display, where the camera crosses the 44px threshold within the 10–15 tile band. The owner accepted it for this release specifically so it could be judged rather than predicted; record the verdict for the follow-up rather than acting on it here.
- [ ] T047 Deploy, then verify from the running system: fetch `render.js` and `anim.js` from both `kitties.ai` and `cloudkitty.ai` and confirm the bytes. Never take the deploy report's word for it.
- [ ] T048 [P] Update `BACKLOG.md` with what this arc parked: the ear and eye magnitudes, the gaze sources, the `MENISCUS` dials, and whiskers at camera scale — all deferred to this moment and now judgeable at the camera's size.
- [ ] T049 Measure SC-006: run 5 kitties for 10 minutes with camera mode on and count anchor changes, which must be at most 3 a minute. Instrument the count rather than watching for it — a restless camera is easier to measure than to notice — and judge the hysteresis dial from T045 against this number.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (T001–T003)**: no dependencies. T002 must precede any code change.
- **Foundational (T004–T012a)**: blocks every story. **T012 is the gate; T012a is confirmation and does not block** — it needs a browser this environment does not have.
- **US1 (T013–T022)**: needs Foundational. No story dependencies.
- **US2 (T023–T031)**: needs Foundational. Independently testable, though in
  practice it is judged with US1 running.
- **US3 (T032–T035)**: needs Foundational. Persists whatever state exists, so it
  is testable with US1 alone if US2 has not landed.
- **US4 (T036–T039)**: needs US2, since there is nothing to mark without a
  follow. The one genuine cross-story dependency.
- **Polish (T040–T049)**: after the stories being shipped. T049 needs US1 only, so it can run early if the hysteresis dial wants evidence sooner.

### Within Foundational

T004 and T005 are independent. T006 needs both. T007 needs T006. T008 and T010
both touch `render.js` and should be sequential. T011 pairs with T010. T012 gates
everything; T012a runs alongside it without blocking.

### Parallel opportunities

Real ones, given five files:

- T013–T016 (all in `test-motion.mjs`, but independent blocks — write together, land together)
- T023–T026, same
- T041, T042, T043, T044, T048 in Polish — different files and different activities entirely

Not parallel, despite appearances: anything touching `render.js` during
Foundational, and anything touching `app.js` during US2 and US4.

---

## Implementation Strategy

### MVP

Phases 1–3. Camera mode holds the group and the toggle works. No clicking, no
selection, nothing to learn, and the whole of the feature's value. Ship and
judge it before building follow.

### Increments

1. Setup + Foundational → the client is unchanged, with a camera underneath it
2. US1 → **MVP, deployable**
3. US2 → follow, the reason to look at one kitty
4. US3 → the meadow remembers
5. US4 → the card says which one

### The risk to watch

SC-003. If the frame rate regresses, the cause is almost certainly a rebake
happening per frame rather than per palette step — `render.js:507` records an
incident in this exact code where a guard mismatched every frame and rebaked the
ground at 60fps. Instrument the bake count before trusting an fps reading.

### Notes

- One branch, one worktree. Merge `origin/main` in; never rebase.
- Commit per task or per logical group, and check `main..HEAD` before the first push.
- Every dialled value is judged in motion at the live size and pasted by the owner, per house practice.
