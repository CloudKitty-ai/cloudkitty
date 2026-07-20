# Tasks: Graphics Refresh — Vector Cats & Animation

**Input**: Design documents from `/specs/005-graphics-refresh/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R10), data-model.md,
contracts/viewer-contract.md, quickstart.md

**Tests**: No automated test tasks — the feature's acceptance is visual by
design (R10): the US1 gallery gate plus scripted quickstart checks per story.
Pure derivation logic is structured for future unit tests but adding a JS
toolchain is out of scope. The Rust suite must simply stay green and
untouched.

**Organization**: One phase per user story, in spec priority order. **US1
ends in a hard human gate (T006)** — no task after Phase 3 may start until
`gallery-approval.md` records approval (FR-002).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)

## Path Conventions

All implementation lands in `client/` (static files, no build step).
`crates/` and `cloudkitty.toml` are untouched — a non-empty diff there is a
planning bug.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the shared drawing module both the gallery and the
live viewer load — the API surface everything else calls.

- [X] T001 Create `client/cat.js`: module skeleton exposing `PALETTES` (empty
      for now), `POSES` (named list per data-model.md), `appearanceFor(id)`
      (`PALETTES[id % PALETTES.length]`), and
      `drawCat(ctx, {pose, appearance, facing, size, phase})` drawing a
      placeholder blob — plain script (no modules/build), no DOM access
      beyond the `ctx` argument, no fetches (R1/R2 signatures, FR-001).
- [X] T002 Add `<script src="cat.js"></script>` to `client/index.html` ahead
      of `render.js`, and a `reduced-motion` body-class CSS rule stub that
      disables the panel `.bar > span` transitions (groundwork for FR-015).

**Checkpoint**: the live viewer still renders exactly as before (cat.js is
loaded but unused); `client/gallery.html` does not exist yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

No engineering prerequisites beyond Phase 1 — the feature's one true
cross-story blocker is the **US1 approval gate (T006)**, which is a
checkpoint inside Phase 3 rather than a task here. Nothing in US2–US6 may
begin before it passes.

---

## Phase 3: User Story 1 — The Portrait Gallery (Priority: P1) 🎯 MVP

**Goal**: The new cat design, judgeable side by side at world size, with a
minutes-not-days revision loop — retiring the clip-art risk before anything
builds on the look.

**Independent Test**: Open `client/gallery.html` from disk (no server).
Every palette × every pose appears at 22px and 88px; the three defaults are
distinguishable unlabeled; the design reads as cute at 22px.

- [X] T003 [US1] Implement `PALETTES` in `client/cat.js`: ≥ 6 hand-curated
      colorways (`furBase`, `furShade`, `pattern {kind, color}` over
      `solid | tabby-stripes | patches | tuxedo-mask | point-mask`,
      `eyeColor`, `noseColor`), first three tuned maximally distinct at
      22px for the default kitties (R2, FR-003).
- [X] T004 [US1] Implement the drawing vocabulary in `client/cat.js`: chibi
      side-profile primitives (body blob, oversized head, ears with inner
      fill, bezier tail, dot-and-line face, soft dark outlines), pattern
      overlays per kind, horizontal mirroring for `facing`, `phase`-driven
      breathing/tail-sway hooks, and all eight `POSES` (idle standing —
      sitting deliberately skipped, spec clarification 2026-07-19 — walking,
      pouncing, eating, drinking, grooming, loaf, sleep-curl) as parameter
      sets — no per-pose code forks (R1, FR-007 groundwork).
- [X] T005 [P] [US1] Create `client/gallery.html`: standalone page loading
      `cat.js`; grid of every palette × every pose at tile size (22px) and
      inspection size (88px); an unlabeled side-by-side row of the three
      default kitties; works from `file://` and via the server's static
      fallback with zero server changes (R8, FR-001).
- [X] T006 [US1] **CHECKPOINT — the gallery gate.** Present the gallery to
      the owner; iterate `client/cat.js` (palettes/geometry only) until
      judged; record the outcome — approved, or fallback chosen (pixel
      sprites / emoji-faces-on-vector-bodies) — with date and revision notes
      in `specs/005-graphics-refresh/gallery-approval.md` (FR-002, SC-001).
      **HARD STOP: Phases 4–9 wait for "approved" in that file.**

**Checkpoint**: US1 fully delivered — the look is approved and revisable in
one file, and nothing else has been risked on it.

---

## Phase 4: User Story 2 — Recognizable Kitties in the World (Priority: P2)

**Goal**: The live world draws the approved vector cats with stable per-kitty
identity and facing — still on the existing draw-per-frame pipeline (no
animation clock yet).

**Independent Test**: Live viewer, panel covered: identify each kitty by fur
alone; reload and restart the server — appearances identical; a kitty that
moved west faces left and keeps facing left when it stops; `g` toggle
unchanged.

- [X] T007 [US2] Rework `drawKitty` in `client/render.js`: replace the emoji
      glyph with `drawCat` using `appearanceFor(kitty.id)` and the pose
      selection table from data-model.md (`activity.state` →
      `last_action` → position delta → idle); keep the ground shadow,
      happiness bar, 💤 wisp, cuddle heart, and the greeble rule exactly as
      they are (FR-003, SC-003, US2 acceptance 4).
- [X] T008 [US2] Track facing in `client/app.js`: a per-kitty presentational
      map updated from consecutive frames' position deltas (horizontal
      component only; unchanged on vertical/no movement; default `"left"`;
      rebuilt when the roster changes), passed into the renderer (FR-004).
      Note: this store moves into `anim.js` in T010 — keep it self-contained
      and closure-free so the move is a cut-paste (analyze D1).
- [X] T009 [US2] Verify quickstart §2 end to end: identify each kitty by fur
      alone with the panel covered; reload and server-restart appearance
      stability; facing kept while stationary; `g` toggle unchanged — fix
      until all pass (SC-003, analyze C1).

**Checkpoint**: the world shows identifiable vector cats; motion still snaps
per tick (that's US3).

---

## Phase 5: User Story 3 — Cats That Glide, Not Teleport (Priority: P3)

**Goal**: The interpolation clock — smooth easing between the two newest
served states, with disciplined snapping at every discontinuity, reduced
motion, and hidden-tab hygiene. This is the Article V heart of the feature.

**Independent Test**: quickstart §3 — visible tile traversal; reconnect
snaps; hidden-tab return snaps within a tick; reduced-motion emulation
restores per-tick snapping.

- [X] T010 [US3] Create `client/anim.js`: frozen `VIEW` tunables object
      (every new duration/easing/frequency/amplitude/threshold named here —
      FR-017); `StatePair` store (`prev`, `curr`, `currArrivedAt`,
      `generation`); discontinuity detection (first paint, generation bump,
      `curr.tick ≠ prev.tick + 1`, roster change, >1-tile kitty move — R4);
      eased-progress computation clamped at 1 (never extrapolates — FR-005);
      the per-kitty presentational store (absorbing T008's facing map);
      `prefers-reduced-motion` live media query and `visibilitychange`
      handling (rAF cancelled while hidden, generation bump + snap on
      return — R6, FR-015/016); and the rAF loop that drives the renderer.
- [X] T011 [US3] Wire `client/app.js` and `client/index.html`: WS frames and
      first snapshots feed `anim.js` instead of drawing directly; reconnect
      bumps `generation`; `fetchViewerConfig` also reads
      `config.world.tick_ms` into the easing duration with named stand-in
      `VIEW.tickMsFallback = 800` (R3, FR-005); add the `anim.js` script
      tag; toggle the `reduced-motion` body class from the media query.
- [X] T012 [US3] Rework `client/render.js` to draw an interpolated frame:
      kitty positions lerped with the eased progress; elements always at
      `curr` positions with brief spawn/expiry fades (never gliding from
      nowhere); the static ground checkerboard + grid cached to an offscreen
      canvas per resize and blitted per frame (R7, SC-006); one draw path
      where reduced/static mode is simply progress = 1, phase = 0, beats
      off.
- [X] T013 [US3] Verify quickstart §3 end to end: glide at default tick
      rate, reconnect snap, hidden-tab return, reduced-motion equivalence —
      fix until all four pass.

**Checkpoint**: the world glides; every discontinuity snaps; hidden tabs do
no work.

---

## Phase 6: User Story 4 — Expressive Actions and Idle Life (Priority: P4)

**Goal**: Every action looks like something; idle cats are never statues.

**Independent Test**: quickstart §4 — each action distinguishable without
the panel within a tick; fall-asleep transition plays once; idle motion
present but never action-like; reduced motion shows static poses.

- [X] T014 [US4] Add action animation curves to `client/cat.js`: pounce with
      anticipation and squash-and-stretch, eating chomp, drinking lap,
      grooming licks, fall-asleep curl transition, held-sleep breathing —
      all as `phase`-driven parameter modulation on the existing poses, no
      new drawing pipeline (FR-007). Optional flourish, freely droppable
      (analyze U1): a drink-triggered ripple on the adjacent water tile
      (lands in `client/render.js` if taken — distinguishability is the
      requirement, the lap alone satisfies it).
- [X] T015 [US4] Extend `client/anim.js`: per-kitty animation phase derived
      from the interpolation clock; `fellAsleepAt` tracking so the curl
      transition plays only on the tick sleeping begins (US4 acceptance 3);
      an idle-motion scheduler (tail flick, ear twitch, blink) firing at
      `VIEW.idleMotionFrequency` from the local clock only, suppressed
      whenever a non-idle pose is active (FR-008).
- [X] T016 [US4] Wire `client/render.js`: pass animation phase and idle
      motions into `drawCat`; under reduced motion render the static pose
      for the state with no transitions (FR-015).
- [X] T017 [US4] Verify quickstart §4: all listed actions distinguishable,
      sleep transition vs held curl, one-minute idle watch, reduced-motion
      static poses — fix until all pass (SC-004).

**Checkpoint**: cute is now alive; the animation vocabulary exists for US5.

---

## Phase 7: User Story 5 — The Stories the Data Already Tells (Priority: P5)

**Goal**: Perform the drama the server already serves — beats derived from
served fields and state diffs, never invented.

**Independent Test**: quickstart §5 — each beat appears when its served
condition holds (panel as ground truth) and never otherwise.

- [X] T018 [US5] Implement beat derivation in `client/anim.js`, run once per
      frame arrival by diffing `prev → curr` (R5): sad-beat on a new
      `abandoned_chases` entry; relief-sparkle on any need drop ≥
      `VIEW.reliefSparkleDrop` (default 15); plaything on targetless play
      (speech-bubble pop-in is deliberately NOT a beat — it lives
      self-contained in T022, analyze I2); one one-shot slot per kitty,
      newest wins, cleared on discontinuity; plus the pure
      sustained-overlay functions (focused eyes while `pursuit` present;
      thought bubble for the longest-running `distress_since` age `>=` the
      served patience threshold — the panel cue's exact comparison, analyze
      A1 — at most one) — layering rule exactly as documented in
      contracts/viewer-contract.md (FR-010/011/012).
- [X] T019 [US5] Draw the beats in `client/render.js` + `client/cat.js`:
      imaginary plaything (sparkle/butterfly visually unlike every real
      element kind — FR-009), sit + ear-droop sad beat, focused-eye variant
      in `drawCat`, relief sparkle particle, and the in-world thought bubble
      with the wanted need's icon (sharing the panel's threshold value;
      speech bubble stacking rule); sustained informational cues still
      render under reduced motion (R6).
- [X] T020 [US5] Verify quickstart §5: all five beats appear on their
      conditions and never otherwise; a kitty with no drama shows no beats
      (SC-005) — fix until all pass.

**Checkpoint**: the viewer performs everything the wire already tells it.

---

## Phase 8: User Story 6 — Ambient Life and Polish (Priority: P6)

**Goal**: The world breathes; the furniture gets its juice. Every piece
individually droppable.

**Independent Test**: quickstart §6 — ambient present but subtle; kibble
level tracks servings; bubbles pop in; bars ease; reduced motion removes all
of it.

- [X] T021 [P] [US6] Ambient effects in `client/render.js`: water shimmer,
      sunbeam warm pulse + drifting dust motes, occasional grass sway, soft
      drifting cloud shadows — drawn above the cached ground layer, each
      behind its own named `VIEW` flag, amplitudes tuned subtle, absent
      under reduced motion (FR-013).
- [X] T022 [P] [US6] Element juice in `client/render.js`: chow bowl kibble
      fill level scaled by `servings` (extending today's pip row), speech
      bubble pop-in ease derived self-contained from `meow.tick ==
      curr.tick - 1` on the progress clock (meow stamps trail the published
      tick by one — post-implementation review fix; no beat store — US6
      depends only on US3, analyze I2), over-cat happiness bar easing on
      the same clock
      (never CSS timers — FR-019 applies), instant under reduced motion
      (FR-014).
- [X] T023 [US6] Verify quickstart §6: subtlety, kibble tracking, pop-in,
      bar easing, reduced-motion absence — fix until all pass.

**Checkpoint**: all six stories delivered.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T024 [P] Optional (droppable) panel unification in `client/app.js`:
      replace the card's emoji face with a small `drawCat` portrait canvas
      using the kitty's palette — the spec-assumption nice-to-have; skip
      without ceremony if it fights the card layout.
- [X] T025 Performance and hygiene pass per quickstart §7: one-minute FPS
      observation at default world size (<1% dropped frames, SC-006),
      profiler confirmation of zero rAF work while hidden, offscreen ground
      cache confirmed effective; tune `VIEW` values if needed.
- [X] T026 [P] Update `BACKLOG.md`: trim the shipped "Graphics refresh"
      P2 entry per the shipped-items convention (leave the deferred items —
      day–night, ear/tail affect — pointing at their own entries).
- [X] T027 Final validation: quickstart §8 (blocked `/config` → named
      stand-ins, no console errors — SC-008) and §9 (fmt + clippy + full
      workspace suite green, `git diff --stat crates/ cloudkitty.toml`
      empty); confirm every task above is checked off.

---

## Dependencies & Execution Order

```text
Phase 1 (Setup: T001–T002)
        ↓
Phase 3 (US1: T003–T005 → T006 GATE) ── hard stop until approved
        ↓
Phase 4 (US2: T007–T009)
        ↓
Phase 5 (US3: T010–T013)
        ├──────────────────────────────┐
        ↓                              ↓
Phase 6 (US4: T014–T017)        Phase 8 (US6: T021–T023, needs only US3)
        ↓                              │
Phase 7 (US5: T018–T020)               │
        └──────────────┬───────────────┘
                       ↓
Phase 9 (Polish: T024–T027)
```

- **US1 → everything**: the gate (T006) blocks all later phases (FR-002).
- **US2 → US3**: interpolation lerps the vector cats US2 put on screen.
- **US3 → US4 → US5**: beats need the vocabulary; the vocabulary needs the
  clock.
- **US6 needs only US3** (ambient runs on the clock; juice barely needs
  that) — it may run in parallel with US4/US5 after Phase 5.

## Parallel Opportunities

- T005 (gallery page) alongside T003/T004 (it consumes their exports; build
  the scaffold while palettes are tuned).
- After Phase 5: US6 (T021–T022, themselves parallel — different concerns in
  render.js, coordinate on merge) in parallel with US4/US5.
- Phase 9: T024 and T026 parallel with T025.

## Implementation Strategy

**MVP = Phase 1 + Phase 3 (US1)**: the gallery alone is a complete,
shippable increment — the look exists, is judgeable, and has a minutes-long
revision loop. It is also deliberately the *only* thing at risk until the
gate passes.

Then deliver story by story in priority order — each checkpoint leaves the
live viewer working and visibly better (identity → glide → alive →
storytelling → ambience). Commit per story phase; the owner's gate at T006
is the one place the flow stops and waits by design. If the gallery cannot
beat the emoji after honest iteration, the recorded fallback decision ends
the feature at minimal cost with the gallery as the artifact of record.
