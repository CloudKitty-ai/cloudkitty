# Tasks: The Meadow Itself — Beautification II, Step 2

**Input**: Design documents from `/specs/008-beautify-meadow/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/meadow-contract.md, quickstart.md

**Tests**: included — the spec/plan define the three-tier verification
pattern (headless harnesses + quickstart visual checks + the FR-014 live
checkpoint), matching the shipped 005/007 practice.

**Organization**: grouped by user story, in spec priority order. Every story
is independently shippable and visible live. **The FR-014 human checkpoint
(T030) closes the feature — nothing ships as the default view before its
record says approved** (see plan.md "The FR-014 checkpoint").

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on incomplete tasks)
- **[Story]**: US1 (meadow), US2 (ponds), US3 (edge), US4 (glow), US5 (paths)

## Phase 1: Setup

**Purpose**: the new file, its palette, and its tunables home.

- [X] T001 Create `client/meadow.js` — file header comment (the ground
      vocabulary, pure-view note), the named `MEADOW` palette block per
      data-model.md (grassTones[], jitterTint, flora hues, pondWater,
      pondRim, lilyPad, edgeFringe, glowWarm, pathTint, gridLine — hues
      chosen close to the shipped cream/pastel world) — and add the
      `<script src="meadow.js">` tag to `client/index.html` after props.js,
      before render.js
- [X] T002 [P] Add the frozen `VIEW.meadow` tunables sub-object to
      `client/anim.js` per data-model.md: layer flags (scatter, ponds, edge,
      glow, paths, gridOverlay) plus toneCount, jitterAlpha, floraDensity,
      shoreRounding, lilyPadMinTiles, glowRadiusTiles, glowAlpha, edgeDepth,
      pathHeatCap, pathHalfLifeMs, pathVisibilityFloor — each with a
      one-line comment, in the `VIEW.ambient`/`VIEW.props` mold

---

## Phase 2: Foundational

**Purpose**: the one deterministic scatter source everything else consumes.

**⚠️ CRITICAL**: no user story work until this phase is complete.

- [X] T003 Implement `tileHash(x, y)` in `client/meadow.js` — integer
      bit-mixer (multiply by two large odd constants, xor, avalanche,
      normalize to [0,1)) plus the salt-remix helper for derived lookups
      (tone/jitter/flora salts as named constants), per research R2
- [X] T004 Create the headless harness `client/test-meadow.mjs` — the
      established `eval(src + ';({ exports })')` + mock-ctx `Proxy`
      (non-finite guard) pattern — with the tileHash suite: determinism
      (same inputs → same outputs across two evals), range [0,1),
      distribution sanity (tone-run lengths over a 64×64 sweep show no
      diagonal banding; salts decorrelated)

**Checkpoint**: hash proven stable — story work can begin.

---

## Phase 3: User Story 1 — An organic meadow replaces the checkerboard (Priority: P1) 🎯 MVP

**Goal**: the checkerboard becomes a meadow (tones + jitter + flora) in the
existing ground cache; grid lines demoted to a debug toggle (`l`).

**Independent Test**: quickstart §1 — meadow variety, reload/restart
identity, grid toggle defaults, no banding at 64×64.

- [X] T005 [US1] Implement `drawMeadowGround(ctx, {width, height, tile})` in
      `client/meadow.js` — per-tile tone from tileHash + tone salt,
      barely-visible brightness jitter overlay (jitterAlpha), sparse
      hash-placed flora (tuft, clover, three-petal flower) at hash-jittered
      sub-tile offsets, honoring `VIEW.meadow.scatter` and floraDensity
- [X] T006 [P] [US1] Implement `drawGridOverlay(ctx, {width, height, tile})`
      in `client/meadow.js` — the demoted lattice, MEADOW.gridLine hue,
      same 0.5px alignment the old cache used
- [X] T007 [US1] Swap `blitGround` in `client/render.js`: cache body becomes
      `drawMeadowGround` (grid lines removed from the cache); add
      `showGrid = false` to the constructor beside `showGreebles`; in
      `draw()`, call `drawGridOverlay` right after `blitGround` when
      `showGrid` is on; retire the now-unused `TILE_COLORS.grass/grassAlt/
      gridLine` entries
- [X] T008 [US1] Wire the `l` toggle in `client/app.js` (the `g` mold:
      keydown, flip `renderer.showGrid`, sync note, `anim.redraw()`) and in
      `client/index.html` add the footer hint (`press l for grid lines`)
      plus a hidden `#grid-note` visible-state span
- [X] T009 [US1] Extend `client/test-meadow.mjs`: mock-ctx sweep of
      drawMeadowGround + drawGridOverlay across world dims (2×2, 32×32,
      64×64, 1×8) and tile sizes (8, 22); determinism check — two runs
      capture identical draw-command streams
- [ ] T010 [US1] Visual validation per quickstart §1 on the live demo world
      (never the owner's save): variety, reload/restart identity, toggle
      defaults + footer, 64×64 banding sweep

**Checkpoint**: the world is a meadow — independently shippable.

---

## Phase 4: User Story 2 — Water gathers into ponds (Priority: P2)

**Goal**: contiguous served water renders as one smooth-shored pond (cached
Path2D), lily pads on larger ponds; pathing and fades unchanged.

**Independent Test**: quickstart §2 — seam-free shorelines for every blob
shape, single-tile pool, lily pad stability, drink positions unchanged.

- [X] T011 [US2] Implement pond geometry in `client/meadow.js`:
      `groupWaterTiles(positions)` (4-adjacency grouping) and
      `buildPondPath(tiles, tile)` (marching squares over the tile set,
      corners rounded by `VIEW.meadow.shoreRounding`, returns Path2D),
      per research R4
- [X] T012 [US2] Implement `drawPonds(ctx, {ponds, tile})` in
      `client/meadow.js` — fill + rim stroke in MEADOW.pondWater/pondRim,
      one lily pad (MEADOW.lilyPad) on ponds ≥ lilyPadMinTiles, hash-placed
      from the pond's anchor (lowest x,y) tile
- [X] T013 [US2] Route water through the pond layer in `client/render.js`:
      group current water elements per frame, cache Path2D under the
      sorted-position signature (rebuild only on change). Pond body = the
      served water tiles minus any still mid fade-in (`newElementIds`); a
      mid-fade-in tile — and an expiring one taking its bow via the
      `view.expired` path — draws through a surviving small-rounded-pool
      branch in `drawElement` at the element alpha (the pre-008 pool look),
      joining/leaving the merged body once fully present/gone. Keep the
      shimmer ambient over pond surfaces; only the default-path square
      rendering of at-full-presence water is deleted (and
      `TILE_COLORS.water/waterRim` once unused)
- [X] T014 [P] [US2] Extend `client/test-meadow.mjs`: grouping + path cases
      — single tile, 2×2, L-shape, U-shape, ring (hole), border-touching
      set; assertions: one group per blob, path command stream closed and
      finite, signature stability across element order permutations
- [ ] T015 [US2] Visual validation per quickstart §2 (seams, pool, lily
      pad, shimmer, fades, drink positions, boundary pond)

**Checkpoint**: US1 + US2 ship together or separately.

---

## Phase 5: User Story 3 — The world has an edge (Priority: P3)

**Goal**: a grass-fringe frame wraps any world size; never covers residents.

**Independent Test**: quickstart §3 — frame + corners at 32×32 and 64×64,
outermost-tile kitties fully legible.

- [X] T016 [US3] Implement `drawWorldEdge(ctx, {width, height, tile})` in
      `client/meadow.js` — fringe strokes in MEADOW.edgeFringe along all
      four sides + corners, depth `VIEW.meadow.edgeDepth`, hash-varied blade
      spacing, confined to the outer margin of boundary tiles (FR-007)
- [X] T017 [US3] Call `drawWorldEdge` at the end of the ground-cache build
      in `client/render.js` `blitGround` (drawn over meadow, under
      everything dynamic)
- [ ] T018 [US3] Validate: extend the T009 sweep to assert edge drawing
      stays within the boundary-tile margin for 2×2 / 1×8 / 64×64 worlds;
      visual validation per quickstart §3

**Checkpoint**: any size world reads as a garden.

---

## Phase 6: User Story 4 — Sunbeams become light (Priority: P4)

**Goal**: the rounded-square sunbeam becomes a radial warm glow; pulse and
motes unchanged on top.

**Independent Test**: quickstart §4 — soft bleed past tile bounds, ambience
intact, adjacent beams blend, reduced-motion static glow reads clearly.

- [X] T019 [US4] Implement `drawSunbeamGlow(ctx, {cx, cy, tile, alpha})` in
      `client/meadow.js` — radial gradient MEADOW.glowWarm core → 
      transparent at `VIEW.meadow.glowRadiusTiles × tile`, base alpha
      `VIEW.meadow.glowAlpha`, default compositing (research R5)
- [X] T020 [US4] Swap the body of `drawSunbeam` in `client/render.js`: glow
      replaces the roundRect + rim; the pulse multiplier, element alpha,
      and dust motes keep their exact existing code paths and flags; retire
      `TILE_COLORS.sunbeam/sunbeamRim` once unused
- [ ] T021 [US4] Validate: mock-ctx sweep of drawSunbeamGlow (gradient args
      finite at tile 8/22, alphas clamped); visual validation per
      quickstart §4 including reduced-motion emulation and two adjacent
      beams

**Checkpoint**: light, not tiles.

---

## Phase 7: User Story 5 — Worn paths, revealed on request (Priority: P5)

**Goal**: session-local trail memory in `Presentation`, drawn behind a `p`
toggle; fades with time, clears on discontinuity, never served.

**Independent Test**: quickstart §5 — accumulate/strengthen/fade, toggle =
visibility only, reload/discontinuity clears, footer hint.

- [X] T022 [US5] Add worn-path memory to `Presentation` in `client/anim.js`
      per research R6: `pathHeat` Map (`"x,y"` → {heat, stampedAt}) bumped
      +1 per kitty tile on each *continuous* pushState (clamped at
      `VIEW.meadow.pathHeatCap`), cleared in the existing discontinuity
      branch beside facings/oneShots; `viewAt` exposes `wornPaths()` — the
      decayed snapshot (half-life `VIEW.meadow.pathHalfLifeMs`, filtered by
      `pathVisibilityFloor`), available in still frames too (state, not
      motion)
- [X] T023 [P] [US5] Implement `drawWornPaths(ctx, {entries, tile})` in
      `client/meadow.js` — soft rounded tint per warm tile, MEADOW.pathTint,
      opacity scaled by decayed heat
- [X] T024 [US5] Wire rendering in `client/render.js`: `showPaths = false`
      in the constructor; in `draw()`, call `drawWornPaths` with
      `view.wornPaths()` between ground blit and elements when `showPaths`
      is on
- [X] T025 [US5] Wire the `p` toggle in `client/app.js` (the `g` mold) and
      the footer hint + hidden `#paths-note` span in `client/index.html`
- [X] T026 [P] [US5] Extend `client/test-meadow.mjs` with the
      `Presentation` path-memory suite (eval anim.js alongside meadow.js;
      inject times) — accumulation on continuous ticks, cap, read-time decay with injected
      times, clear on every discontinuity flavor (first paint, generation
      bump, tick gap, roster change, teleport), accumulation independent of
      any toggle
- [ ] T027 [US5] Visual validation per quickstart §5 (accumulate, fade,
      toggle on/off/on, reload clear, restart clear, footer)

**Checkpoint**: all five stories live.

---

## Phase 8: Polish, hygiene & the FR-014 checkpoint

- [ ] T028 Legibility + toggle sweep per quickstart §6: every kitty/prop
      locatable in two seconds against the new ground; `g`/`l`/`p`
      independent with correct fresh-load defaults and footer hints; one
      minute at default size with all layers on, no perceptible stutter
- [X] T029 Hygiene: `cargo fmt --all -- --check`, `cargo clippy --workspace
      --all-targets -- -D warnings`, `cargo test --workspace` all green;
      `git diff --stat crates/ cloudkitty.toml` empty (SC-007); full
      `node client/test-meadow.mjs` run green
- [ ] T030 **The FR-014 checkpoint (SC-008)**: run the two demo worlds
      (32×32 and 64×64 per quickstart), present the full look to Elizabeth
      live with layers on and off; loop revisions through
      `client/meadow.js` (palette/tunables) until approved; record the
      outcome, revision rounds, and any layer decisions in
      `specs/008-beautify-meadow/meadow-approval.md`. **Blocks shipping.**
- [ ] T031 Update `BACKLOG.md`: remove the shipped "Beautification II,
      step 2: the meadow itself" entry (shipped P2 items follow the P1
      convention — removed once merged, per the file's own note), leaving
      day–night and the other entries untouched

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** → **Foundational (Phase 2)** → user stories.
- **US1 (Phase 3)** first — it rebuilds the ground cache every later layer
  draws against.
- **US2–US5 (Phases 4–7)**: after US1. US2, US3, US4 are mutually
  independent (different draw sites); US5 is independent of US2–US4.
  Priority order is the default; parallel work is safe across stories
  except where two tasks touch `render.js` (serialize those).
- **Phase 8** last; T030 gates the ship.

### Within stories

- meadow.js drawing before its render.js call site (T005→T007, T011/T012→
  T013, T016→T017, T019→T020, T022/T023→T024).
- app.js/index.html wiring after the renderer flag exists (T007→T008,
  T024→T025).

### Parallel opportunities

- T001 ∥ T002 (different files).
- T005 ∥ T006 within US1; T014 ∥ T015 prep; T023 ∥ T022; T026 ∥ T027 prep.
- Across stories (after US1): US2 (T011–T015), US3 (T016–T018), US4
  (T019–T021) touch disjoint functions — serialize only their render.js
  edits (T013, T017, T020).

## Implementation Strategy

MVP is **US1 alone**: the meadow ground + grid demotion is the single
biggest visual win and every later layer builds on its cache. Then deliver
in priority order (each checkpoint is demo-able live), finishing with the
recorded FR-014 approval before push/PR — revision loops confined to
`client/meadow.js`, exactly the single-file loop the 005/007 gates proved.
