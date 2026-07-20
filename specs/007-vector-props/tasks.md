# Tasks: Vector Props — Retire the Remaining Emoji

**Input**: Design documents from `/specs/007-vector-props/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R8), data-model.md,
contracts/props-contract.md, quickstart.md

**Tests**: No automated test tasks — acceptance is visual (R8), gated like
005: the props gallery gate plus scripted quickstart checks, with headless
node sweeps over the pure drawing/derivation logic as a polish-phase
validation. The Rust suite's job is to stay green with an empty `crates/`
diff.

**Organization**: One phase per user story, priority order. **US1 ends in
a hard human gate (T006)** — no live emoji is replaced until
`gallery-approval.md` records approval, greeble face included (FR-003).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US3)

## Path Conventions

All implementation lands in `client/` (static files, no build step).
`crates/` and `cloudkitty.toml` are untouched — a non-empty diff there is
a planning bug (FR-014, SC-007).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the prop vocabulary file both the gallery and the
live renderer load.

- [X] T001 Create `client/props.js`: module skeleton exposing the `PROPS`
      named palette block (empty for now), `BUTTERFLY_COLORWAYS` (empty),
      `butterflyColorwayFor(id)` (`BUTTERFLY_COLORWAYS[id %
      BUTTERFLY_COLORWAYS.length]`), and stub draw functions `drawBowl`,
      `drawButterfly`, `drawGreebleWisp`, `drawSleepZs`, `drawHeart`,
      `drawNeedIcon` — plain script sharing `cat.js`'s conventions
      (unit-box scaled by `size`, `TAU`/`OUTLINE_W` from shared script
      scope, `fine = size >= 44`), no DOM beyond `ctx`, no fetches
      (R1, FR-001).
- [X] T002 Add `<script src="props.js"></script>` to `client/index.html`
      after `cat.js` and before `render.js`.

**Checkpoint**: the live viewer renders exactly as before (props.js loaded
but unused).

---

## Phase 2: Foundational (Blocking Prerequisites)

No engineering prerequisites beyond Phase 1 — the cross-story blocker is
the **US1 approval gate (T006)**, a checkpoint inside Phase 3. Nothing in
US2–US3 may begin before it passes.

---

## Phase 3: User Story 1 — The Props Gallery (Priority: P1) 🎯 MVP

**Goal**: Every prop judgeable beside the approved cats, states included,
with a minutes-long revision loop — and the greeble face decided where
taste is judged.

**Independent Test**: Open `client/gallery.html` from disk. Every prop ×
state appears at 22px and 88px; props read as the cats' drawing hand; the
greeble shows both candidate faces.

- [X] T003 [US1] Implement `PROPS` and `BUTTERFLY_COLORWAYS` in
      `client/props.js`: the named world-adjacent palette (bowlClay,
      bowlRim, kibble, ink, blush, soap, shadow) and three curated
      butterfly colorways (soft lavender / pale lemon / peachy-white:
      wing, wingShade, body), pairwise distinguishable at 22px
      (R2, FR-005, FR-012).
- [X] T004 [US1] Implement the six draw functions in `client/props.js`:
      `drawBowl` (squat terracotta trapezoid, rim band, kibble mound of
      dots mapping `servings` clamped at 5, empty-not-absent at 0, fish
      decal at fine — R4, FR-004); `drawButterfly` (two chubby upper
      wings + small lower lobes flapping by width-scale on `phase`, dash
      body, antennae at fine, hover-bob offset above a non-bobbing
      detached `shadow` ellipse, `agitated` multiplying the flap cycle —
      R3, FR-006); `drawGreebleWisp` (teardrop, wavy skirt, hollow eyes,
      slow bob, softer dashed outline via a named dash constant with the
      dash reset after, `face: 'blank'|'grin'` — R6); `drawSleepZs`
      (three staggered rounded Zs drifting/fading on `phase`, static
      ladder at 0); `drawHeart` (plump blush heart, one highlight, scale
      pulse on `phase`); `drawNeedIcon` (eat→mini bowl reusing
      `drawBowl`, drink→drop, sleep→static Zs, play→yarn ball with wrap
      arcs and trailing thread, cuddle→static heart, bath→three glinting
      soap bubbles — R5, FR-008/009).
- [X] T005 [P] [US1] Extend `client/gallery.html` with the props section
      (adding the `<script src="props.js"></script>` tag after `cat.js` —
      analyze U3):
      bowl at 5/3/1/0, three butterfly colorways × two flap positions
      plus one agitated sample at 88px, **both greeble faces side by
      side** at the in-world 0.55 alpha, Zs (static ladder), heart, and
      all six thought icons at bubble scale — each at 22px and 88px,
      placed within visual reach of the cat portraits (FR-002,
      data-model gallery matrix).
- [X] T006 [US1] **CHECKPOINT — the props gate.** Present the gallery to
      the owner; iterate `client/props.js` until judged; record the
      outcome including the greeble face decision in
      `specs/007-vector-props/gallery-approval.md` (FR-003, SC-001).
      **HARD STOP: Phases 4–6 wait for "approved" in that file.**

**Checkpoint**: US1 delivered — the look is approved, the face is chosen,
and no live pixel has been risked on either.

---

## Phase 4: User Story 2 — Bowl and Butterfly in the World (Priority: P2)

**Goal**: The two data-carrying ground props go live: the mound is the
servings display; butterflies fly, keep their colors, and panic under
pursuit.

**Independent Test**: quickstart §2 — bowls orderable by mound; meter
gone; butterflies distinguishable and reload-stable; panic flap tracks
served pursuit; reduced motion static with state intact.

- [X] T007 [US2] Extend `client/anim.js`: add the frozen `VIEW.props`
      tunables (`flapPeriodMs`, `panicMultiplier`, `bobPeriodMs`,
      `bobAmplitude`, `wispBobMs`, `heartPulseMs`, `zDriftMs` — analyze
      U2) and give `viewAt` a `propPhaseFor(id, periodMs)` — wall-clock
      phase over the named period, seeded by an element *or* kitty id
      (analyze U1), returning 0 when `still` so reduced motion gets
      static props through the one draw path (R3, R7, FR-012/013).
- [X] T008 [US2] Swap the ground props in `client/render.js`: the chow
      arm calls `drawBowl` with served `servings` and deletes the meter
      bars; the bug arm calls `drawButterfly` with
      `butterflyColorwayFor(el.id)`, `view.propPhaseFor(el.id,
      VIEW.props.flapPeriodMs)`, and an
      `agitated` flag from an `agitatedIds` set derived once per frame
      from every `kitty.pursuit.target` naming an element — preserving
      the existing spawn/expiry alpha handling around both
      (FR-004/005/006, contract mapping).
- [X] T009 [US2] Verify quickstart §2 end to end (bowl ordering and
      shrinking mound, butterfly distinguishability and reload/restart
      stability, hover/shadow read, panic-flap onset and calm within a
      tick, reduced-motion staticness) — fix until all pass
      (SC-002/003/004).

**Checkpoint**: the ground props are live; overlays still emoji (that's
US3).

---

## Phase 5: User Story 3 — Overlays, Wisps, and Thought Icons (Priority: P3)

**Goal**: The consistency sweep that ends with zero emoji on the world
canvas.

**Independent Test**: quickstart §3 — wisp under `g` unchanged in
behavior; Zs drift; heart pulses; six drawn thought icons; the star stays
imaginary; no emoji glyph anywhere on the canvas.

- [X] T010 [US3] Swap the overlay props in `client/render.js`: the
      greeble arm calls `drawGreebleWisp` with the gate-chosen face —
      same `showGreebles` gate, same 0.55 alpha, nothing about *when*
      changes (FR-007), bobbing on `propPhaseFor(el.id,
      VIEW.props.wispBobMs)`; the sleeping kitty's 💤 becomes
      `drawSleepZs` on `propPhaseFor(kitty.id, VIEW.props.zDriftMs)` at
      the same anchor; the cuddle 💗 becomes `drawHeart` on
      `propPhaseFor(kitty.id, VIEW.props.heartPulseMs)` at the eased
      midpoint (FR-008, analyze U1).
- [X] T011 [US3] Swap the thought icons and close the emoji path in
      `client/render.js`: `drawThought` renders `drawNeedIcon(need)` in
      place of the emoji glyph; delete the `NEED_ICONS` map and the
      `emoji()` helper entirely so no canvas call site can draw a glyph
      (FR-009/010, data-model "Deleted" list).
- [X] T012 [US3] Verify quickstart §3 end to end (wisp
      behavior-identical, Zs/heart under motion and reduced motion, all
      six icons legible, solo-play star never mistakable for a
      butterfly, the zero-emoji sweep both visual and structural) — fix
      until all pass (SC-005/006).

**Checkpoint**: all three stories delivered; the world canvas is
emoji-free.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T013 [P] Headless validation sweep (node, mock-ctx harness as in
      005): every prop × meaningful state × {22, 88} × several phases ×
      agitated/still draws without exceptions or non-finite coordinates;
      `butterflyColorwayFor` is deterministic, total, and pairwise
      distinct over the three colorways; `grep` confirms `client/render.js`
      has no `emoji(` call sites and no emoji glyphs in canvas draw code
      (R8).
- [X] T014 Final validation per quickstart §4: one-minute smoothness
      spot-check, `git diff --stat crates/ cloudkitty.toml` empty, `cargo
      fmt --check` + `clippy -D warnings` + full workspace suite green;
      confirm every task above is checked off (SC-006/007).
- [X] T015 [P] Update `BACKLOG.md`: retire the shipped "Beautification II,
      step 1" entry per the shipped-items convention, leaving step 2 (the
      meadow) pointing at its own entry.

---

## Dependencies & Execution Order

```text
Phase 1 (Setup: T001–T002)
        ↓
Phase 3 (US1: T003–T005 → T006 GATE) ── hard stop until approved
        ↓
Phase 4 (US2: T007–T009)
        ↓                (US3 follows US2: both rework render.js —
Phase 5 (US3: T010–T012)  file-based coordination, not a logical dependency)
        ↓
Phase 6 (Polish: T013–T015)
```

- **US1 → everything**: the gate (T006) blocks all later phases (FR-003).
- **US2 before US3**: sequential only because both edit `client/render.js`;
  T007 (anim.js) could proceed in parallel with late US1 revisions if
  needed, but the gate's hard stop keeps the simple order simpler.
- **Polish**: T013 and T015 are parallel with each other and with T014's
  Rust-side checks.

## Parallel Opportunities

- T005 (gallery section) alongside T003/T004 — it consumes their exports;
  scaffold while palette and geometry are tuned.
- T013 ∥ T015 ∥ T014 in the polish phase.

## Implementation Strategy

**MVP = Phase 1 + Phase 3 (US1)**: the props gallery alone is a complete,
shippable increment — the look exists, is judgeable beside the cats, and
costs minutes to revise or reject. Nothing else is at risk until the gate
passes (and the greeble's face is decided there, not in prose).

Then US2 (the data-carrying ground props) and US3 (the consistency sweep)
land as separate visible increments, each ending in its quickstart
verification; commit per story phase. The zero-emoji claim is made
structural in T011 by deleting the helper, then double-checked in T013.
