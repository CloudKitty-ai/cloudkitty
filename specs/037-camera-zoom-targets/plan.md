# Implementation Plan: Camera zoom targets

**Branch**: `037-camera-zoom-targets` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/037-camera-zoom-targets/spec.md`

## Summary

The camera's floor and ceiling become pixel targets — zoom in until a tile is
about 100px, widen until one would fall below 50px — with a minimum tile count
protecting the smallest viewports. The zoom range is then the ratio of the two,
constant by construction.

**The whole change is one new input.** The camera works entirely in tiles today:
`update(world, view, { aspect })` decides `across`, and the renderer then
computes `tile = cssWidth / across`. Give the camera `cssWidth` as well and it
can compute `across = cssWidth / targetPx` itself — after which the renderer's
line is unchanged, and so is everything downstream of it. The camera is the only
file that needs to think differently.

Four call sites read the two dials being replaced: the fit's floor and ceiling,
the `bound` predicate that decides when the anchor takes over, and the ground
bake's tile. All four are arithmetic on numbers the camera will already have.

## Technical Context

**Language/Version**: Browser JavaScript, ES2020+, plain scripts, no build step.
Fixed load order `cat.js → cat-v2.js → props.js → meadow.js → render.js →
anim.js → app.js`.

**Primary Dependencies**: None. Canvas 2D. The camera is a plain class in
`anim.js`.

**Storage**: None. This feature adds no persisted state; 036's two keys are
untouched.

**Testing**: `node client/test-motion.mjs` (206 checks) and
`node client/test-meadow.mjs` (85). Extend both; do not add a third harness.

**Target Platform**: Evergreen desktop and mobile browsers. The binding
constraint is the **CSS viewport**, not the display's resolution — `resizeFor`
reads `documentElement.clientHeight`/`clientWidth`, and `dpr` only sizes the
canvas backing store.

**Project Type**: Static client for a server-authoritative simulation.
View-only.

**Performance Goals**: No regression against 036's SC-003. The ground bake gets
*smaller* on large viewports under this change, so the budget moves the right
way.

**Constraints**: The map is capped at 1200 CSS px (`MAP_MAX_PX`), so the largest
floor is 12 tiles at a 100px target. The world is 20×20 today, which is what
makes the ceiling clamp on the largest viewports — see the Fog dependency.

**Scale/Scope**: Two files carry the change: `anim.js` (the camera's arithmetic
and its dials) and `render.js` (one extra argument, and the bake's tile). Two
harnesses extend.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Bearing | Verdict |
|---|---|---|
| I — Kitties cannot suffer | No needs or welfare logic touched. | Not engaged |
| II — Kitties cannot die | No lifecycle touched. | Not engaged |
| III — Kitties cannot be alone | Roster untouched. | Not engaged |
| IV — Engine is law | No behaviors. | Not engaged |
| **V — Client is a pure view** | The camera reads the viewport and the world snapshot and writes nothing back. This feature only changes arithmetic already happening inside the view. | **PASS** |
| VI — Spec-first, test-guarded | Spec written and clarified before this plan. The dials stay in `VIEW.camera`, the house home for presentation constants. Every new behaviour lands with checks in the existing harnesses. | **PASS** |

**Post-Phase-1 re-check**: unchanged. Nothing here reaches the server, the
snapshot, or storage.

No violations. Complexity Tracking omitted.

## Project Structure

### Documentation (this feature)

```text
specs/037-camera-zoom-targets/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── zoom.md          # Phase 1 — the camera's sizing contract
├── checklists/
│   └── requirements.md  # From /speckit-specify, re-validated by /speckit-clarify
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
client/
├── anim.js           # VIEW.camera dials swap units; Camera.targetFor takes
│                     #   cssWidth and derives `across` from a pixel target
├── render.js         # passes cssWidth into camera.update; bakeTileFor keys on
│                     #   the floor tile instead of nominalAcross
├── test-motion.mjs   # the band, the constant range, the minimum-tile clamp,
│                     #   fine at both ends, the resize continuity
└── test-meadow.mjs   # the bake still bakes once, and gets no larger
```

**Structure Decision**: Unchanged from 036 — flat `client/`, plain scripts. The
camera stays a class in `anim.js` because that is where presentation state and
the frame loop already live, and the renderer stays the only thing that turns
its numbers into a transform.

## Phase 0 — Research

See [research.md](./research.md). Eight findings, of which three shape the work:

- **The camera has no pixel input at all.** Adding `cssWidth` to `update` is the
  whole structural change; every consumer downstream is arithmetic.
- **The ground bake gets simpler and smaller.** `bakeTileFor` currently derives
  the bake from `nominalAcross`; under a pixel floor the bake tile *is* the floor
  tile, which is display-independent and smaller than today's on large
  viewports.
- **FR-008 is satisfied by the scheme, not by re-expressing the dials** — but
  SC-008's scope does not match SC-004's, and as written it cannot pass.

## Phase 1 — Design

- [data-model.md](./data-model.md) — the sizing arithmetic in both directions,
  and which of 036's numbers survive.
- [contracts/zoom.md](./contracts/zoom.md) — what the camera consumes, what it
  must keep true, and the invariants a later change must not break.
- [quickstart.md](./quickstart.md) — how to validate, mapped to the criteria.

## What this plan deliberately does not decide

- **The final numbers.** 100 and 50 are the owner's first pass, explicitly to be
  tuned. The minimum tile count has no agreed value yet and wants one from the
  lab.
- **Whether SC-008 gets its scope corrected.** It is a criterion, and narrowing
  one so the implementation passes is the trap rule 4 names. Flagged for the
  owner in research R5, not edited.
- **Anything about Fog.** The spec records the dependency; this plan assumes
  today's 20×20 world and accepts that the largest viewports clamp.
