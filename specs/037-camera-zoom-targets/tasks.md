---

description: "Task list for 037 camera zoom targets"
---

# Tasks: Camera zoom targets

**Input**: Design documents from `/specs/037-camera-zoom-targets/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/zoom.md, quickstart.md

**Tests**: Included. Constitution Article VI makes the suites a CI gate, and
CLAUDE.md rule 6 requires every new check to be watched failing before it is
trusted — predict the assertion and the reason, break the thing it guards,
confirm both, then undo.

**⚠️ Checklist gate**: `checklists/zoom.md` carries **42 unchecked items**, and
`/speckit-implement` reads that state as a gate. Four are already known-live
(CHK001–CHK004, CHK007 were repaired in the 036 annotation pass; CHK020 is the
SC-004/SC-008 scope mismatch, still open). Work or consciously waive the
checklist before implementing.

**Organization**: Tasks are grouped by user story so each ships independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: different files, no dependency on incomplete work
- **[Story]**: US1–US3 from spec.md

## Path Conventions

Flat `client/`, plain scripts, no build step. Two source files carry this
feature — `anim.js` and `render.js` — so genuine parallelism is scarce and is
marked only where it is real.

---

## Phase 1: Setup

- [ ] T001 Record the pre-change baseline: sweep the current camera across `cssWidth` 340→1200 and record the floor tile at each, so SC-001's "against 3.50× today" has a measured before rather than a quoted one. Store under `client-measurements/037-zoom-baseline/`.
- [ ] T002 [P] Confirm the harness baseline: `node client/test-motion.mjs` (206) and `node client/test-meadow.mjs` (85) green on the branch.
- [ ] T003 [P] Record the current ground-bake size at `cssWidth` 1200 in the same measurements file. Research R3 predicts this feature makes it *smaller*; a prediction written down before the change is worth more than one recalled after.

**Checkpoint**: baselines banked, suites green.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: give the camera pixel information and derive the limits from it.
Every user story is arithmetic on what this phase produces.

**⚠️ CRITICAL**: no user story starts until T009 passes.

- [ ] T004 Add `cssWidth` to the options `render.js` passes into `camera.update`, alongside the existing `aspect`. This is the feature's only structural change — the camera has no pixel input today (research R1).
- [ ] T005 Replace the `VIEW.camera` dials in `client/anim.js`: `nominalAcross` and `ceilingFactor` out; `floorPx: 100`, `ceilingPx: 50`, `minTiles: 6` in. Comment that the first two are a **ratio, not two independent numbers** — the zoom range is `floorPx / ceilingPx`, so moving one moves it (checklist CHK036).
- [ ] T006 In `Camera.targetFor` (`client/anim.js`), derive the floor and ceiling tile counts once per frame from `cssWidth` and the dials, and have the fit clamp, the `bound` predicate and the returned frame all read that one pair. Contract invariant 2: if `bound` compares against a different ceiling than the fit clamps to, the anchor engages at a width the camera never reaches.
- [ ] T007 Guard degenerate viewport measurements in `Camera.targetFor`: a `cssWidth` of zero or non-finite must not produce a non-finite frame. This is not hypothetical — the map is zero-width before first layout, and every formula here divides by or multiplies against it (checklist CHK029).
- [ ] T008 Point `bakeTileFor` in `client/render.js` at the camera's floor tile instead of `nominalAcross`. It is the largest tile the camera can ask for, which is what keeps every per-frame blit a downscale (036 research R2).
- [ ] T009 **The gate.** Add checks to `client/test-motion.mjs`: at `cssWidth` 1000 the floor is 10 tiles — *identical* to today's `nominalAcross` — so the floor's arithmetic reproduces the shipped behaviour at that one width. Assert the frame stays finite at `cssWidth` 0, and that the fit, `bound` and bake all read the same derived pair.

**Checkpoint**: the camera takes pixels and derives tiles from them. **Note the anchor is floor-only**: at 1000px the new ceiling is 20 tiles against today's 15, so this phase is *not* a no-op the way 036's Foundational was. Do not expect an identity gate here — expect the floor to match and the ceiling to have deliberately moved.

---

## Phase 3: User Story 1 — Kitties the same size wherever I watch (P1) 🎯 MVP

**Goal**: apparent size sits in a known band, and every viewport that reaches
the target has the same zoom range.

**Independent Test**: sweep `cssWidth` 340→1200; every floor tile is inside the
band, and `ceiling ÷ floor` is equal wherever neither clamp binds.

- [ ] T010 [P] [US1] Size-band check in `client/test-motion.mjs`: sweep `cssWidth` 340→1200 in 20px steps and assert the largest floor tile over the smallest is under 2 (SC-001). Report the measured figure so a regression shows as a number, not a boolean.
- [ ] T011 [P] [US1] Constant-range check in `client/test-motion.mjs`: at every swept width where neither clamp binds, `ceilingTiles / floorTiles` is equal within 1% (SC-004).
- [ ] T012 [P] [US1] Ceiling-crops check in `client/test-motion.mjs`: at every swept width the ceiling frames fewer tiles than the world (SC-006). **Expect this to bind at 1000 and 1200 on a 20-tile world** — that is the Fog dependency, so the check asserts the clamp holds, not that it never fires.
- [ ] T013 [US1] Implement the floor in `client/anim.js`: `cssWidth / floorPx`, feeding the fit's lower clamp.
- [ ] T014 [US1] Implement the ceiling in `client/anim.js`: `cssWidth / ceilingPx`, clamped below the world so the camera always crops (FR-007).
- [ ] T015 [US1] Verify against T001's baseline that the spread moved from 3.50× to under 2, and record the measured value in `client-measurements/037-zoom-baseline/`.

**Checkpoint**: MVP. Size is banded and the range is constant. Deployable.

---

## Phase 4: User Story 2 — A small screen shows a meadow, not a keyhole (P2)

**Goal**: the smallest viewports keep enough world in frame.

**Independent Test**: at `cssWidth` 340 the floor frames at least `minTiles`,
whatever the pixel target asked for.

- [ ] T016 [P] [US2] Minimum-tiles check in `client/test-motion.mjs`: at every swept width the floor frames at least `minTiles`, and where the minimum binds the tile is *smaller* than the target rather than the world being cropped further (FR-006, SC-005).
- [ ] T017 [P] [US2] Inversion check in `client/test-motion.mjs`: `floorTiles ≤ ceilingTiles` at every swept width. They may meet on a tiny viewport; they may never invert (contract invariant 5, checklist CHK030).
- [ ] T018 [US2] Implement the minimum clamp in `client/anim.js`, applied to the floor before the fit reads it.

**Checkpoint**: US1 and US2 both hold across the sweep.

---

## Phase 5: User Story 3 — Fine detail stops flickering (P3)

**Goal**: detail state is constant for a given viewport.

**Independent Test**: at a 640px map — the width that used to straddle the
threshold — the camera's whole range sits above it.

- [ ] T019 [P] [US3] Threshold check in `client/test-motion.mjs`: at every swept width, both the floor tile and the ceiling tile are at or above the fine-detail threshold, with the margin the band is meant to provide (SC-002, SC-003).
- [ ] T020 [US3] Confirm no code change is needed for this story beyond the band itself, and say so in the test's comment. The pop is removed by the band being entirely above the threshold, not by anything detecting or suppressing it — a reader who later "fixes" the flicker elsewhere should find this note first.

**Checkpoint**: all three stories hold.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T021 Confirm the tile-denominated distance dials: sweep `aimDeadzoneTiles × tile` across the range and record the figures. Research R5 predicts they are *identical* wherever the target is reachable and vary only where `minTiles` binds. **SC-008 as written cannot pass** — its scope includes the clamped viewports while SC-004's does not. Record the measurement and take it to the owner; do not narrow the criterion to fit.
- [ ] T022 [P] Verify the ground bake against T003: it should be smaller at `cssWidth` 1200 and display-independent. If it grew, the bake tile stopped being the floor tile.
- [ ] T023 [P] Re-run 036's identity checks in `client/test-meadow.mjs` — the ground still bakes once across a zoom sweep, and the pond layers once (SC-007).
- [ ] T024 [P] Resize-continuity check in `client/test-motion.mjs`: sweep `cssWidth` in 1px steps across both boundaries — where `minTiles` starts binding and where the world clamp starts binding — and assert `across` is continuous (SC-009, checklist CHK031).
- [ ] T025 Add a viewport strip to `client/gallery-meadow.html`: the same cat at each viewport's camera tile, floor and ceiling, so the band is dialled against something visible rather than a table. Follow the meniscus card's pattern — shipped code, real `Camera`, no replica.
- [ ] T026 Dialling session with the owner on `floorPx`, `ceilingPx` and `minTiles`. **They are not three independent dials**: the range is the ratio of the first two, so moving one moves the range. Judge in motion at the live size.
- [ ] T027 [P] Update the `## Unreleased` CHANGELOG entry in `CHANGELOG.md`, in that file's register.
- [ ] T028 Re-check the 036 annotations after dialling: the banner and the ten inline pointers quote "~100px" and "~50px", and would be stale if the session moves them.
- [ ] T029 Deploy, then verify from the running system: fetch `anim.js` and `render.js` from both hosts and confirm the bytes.
- [ ] T030 [P] Work or consciously waive `checklists/zoom.md`. CHK020 (the SC-004/SC-008 scope mismatch) and CHK036 (the dials are a ratio) are the two that change what gets built.

---

## Dependencies & Execution Order

- **Setup (T001–T003)**: no dependencies. T001 and T003 must precede any code change — both are comparisons against today.
- **Foundational (T004–T009)**: blocks every story. T004 first (nothing else has pixels without it), then T005–T008 in any order, T009 last.
- **US1 (T010–T015)**: needs Foundational. No story dependencies.
- **US2 (T016–T018)**: needs Foundational. Independently testable, though in practice judged with US1.
- **US3 (T019–T020)**: needs US1's band to exist; it asserts a property of it rather than adding behaviour. The one real cross-story dependency.
- **Polish (T021–T030)**: after the stories being shipped. T026 gates T028.

### Parallel opportunities

Real ones, given two source files: the test blocks T010–T012, T016–T017 and T019 are independent assertions over the same sweep and can be written together. T022, T023, T024, T027 and T030 in Polish are genuinely separate activities.

Not parallel: anything touching `anim.js` during Foundational, which is most of it.

---

## Implementation Strategy

### MVP

Phases 1–3. The band and the constant range are the feature; the minimum clamp
protects small viewports and the flicker story asserts a property the band
already provides.

### The risk to watch

**The `bound` predicate reading a different ceiling from the fit.** Cheap to
assert, invisible to the eye, and it would make the anchor take over at a width
the camera never reaches. T006 and T009 exist for it.

### Notes

- One branch, one worktree. Merge `origin/main` in; never rebase.
- Per CLAUDE.md rule 6, no new check is trusted until it has been watched
  failing for the predicted reason — and note that a *sweep* check can pass
  vacuously if the sweep is empty, so assert the sample count too.
- The numbers are dialled with the owner and pasted, per house practice.
