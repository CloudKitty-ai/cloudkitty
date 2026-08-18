# Implementation Plan: Camera mode

**Branch**: `036-camera-mode` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/036-camera-mode/spec.md`

## Summary

Camera mode turns the meadow from a map into a window: a nominal 10 tiles
across, widening to at most 15, aimed at the kitty nearest the group's centre of
mass, and aimed at one particular kitty when the viewer clicks her.

The technical approach rests on one decision that makes the rest small. **The
camera sets `this.tile` and pans with a canvas translate.** Scale arrives by
changing the tile, so all 83 `this.tile` sites in `render.js` and all 152 in
`meadow.js` draw natively at camera scale with no edits, and every art threshold
keyed to drawn size — `fine` above all — stays honest. Pan arrives by
`ctx.translate`, so coordinate math needs no offset threaded through it,
including the several sites that bypass `tileOrigin` and multiply directly.

The one genuinely large piece of work is the ground cache, and the research
phase found a way to make it cost nothing per frame: bake at the camera's
*largest* tile once and blit a downscaled sub-rectangle each frame. Camera
movement then triggers no rebakes at all. That investigation also turned up a
latent staleness bug in the pond cache that the camera would have triggered
silently.

## Technical Context

**Language/Version**: Browser JavaScript, ES2020+, plain scripts with no build
step. Fixed load order: `cat.js → cat-v2.js → props.js → meadow.js → render.js →
anim.js → app.js`.

**Primary Dependencies**: None. Canvas 2D, `localStorage`, `matchMedia`,
`ResizeObserver`, `requestAnimationFrame`. No framework and no bundler, which is
a deliberate property of this client rather than an accident.

**Storage**: `localStorage`, following the existing `THEME_KEY` / `CARDS_KEY`
pattern. Two new keys.

**Testing**: `node client/test-motion.mjs` (164 checks) and `node
client/test-meadow.mjs` (78 checks). Both eval the plain scripts into one shared
scope and assert against a mock context that throws on non-finite draw
arguments. Extend these; do not add a third harness.

**Target Platform**: Evergreen desktop and mobile browsers. Mobile Safari is the
binding constraint for canvas memory.

**Project Type**: Static client for a server-authoritative simulation. View-only.

**Performance Goals**: 60fps sustained, within 10% of the whole-world view's
frame rate on the same display (SC-003).

**Constraints**: No build step. Per-frame ground cost must stay at one
`drawImage`. Offscreen canvases must respect mobile Safari's canvas area cap.
Reduced motion must skip easing entirely and still track on served ticks, where
the rAF loop is not running.

**Scale/Scope**: 20×20 world, 3–5 kitties, camera tile spanning roughly 23px to
120px depending on display and zoom. Five client files touched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Bearing on this feature | Verdict |
|---|---|---|
| I — Kitties cannot suffer | No needs, thresholds, or welfare logic touched. | Not engaged |
| II — Kitties cannot die | No lifecycle touched. A kitty leaving the *frame* is a drawing outcome and has no bearing on the world. | Not engaged |
| III — Kitties cannot be alone | Roster untouched. The camera reads the roster and never changes it. | Not engaged |
| IV — Engine is law, behaviors are advisors | No behaviors, no proposals. | Not engaged |
| **V — Server-authoritative, client is a pure view** | **Directly engaged.** The camera derives every value from state the client already receives, writes nothing back, and sends nothing. Two viewers at different zooms see the same world. | **PASS**, guarded by FR-021 and SC-011 |
| VI — Spec-first, test-guarded | Spec written and clarified before this plan. Every new behaviour lands with checks in the existing harnesses. Camera dials live in `VIEW` in `anim.js`, the house home for presentation constants, not as magic numbers at their use sites. | **PASS** |

**Post-Phase-1 re-check**: unchanged. The design adds no server call, no
simulation read beyond the existing world snapshot, and no stored state other
than two view preferences in `localStorage`. Article V holds by construction:
the camera is a pure function of the world snapshot plus two viewer choices.

No violations. Complexity Tracking is therefore empty and omitted.

## Project Structure

### Documentation (this feature)

```text
specs/036-camera-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── camera.md        # Phase 1 output — the camera's internal surface
├── checklists/
│   └── requirements.md  # From /speckit-specify, re-validated by /speckit-clarify
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
client/
├── index.html        # #camera-toggle markup + CSS already built, inert
│                     #   (arrives from branch client-camera-notes)
├── app.js            # camera + follow state, persistence, canvas hit testing,
│                     #   card follow marking, initCameraControl gains behaviour
├── anim.js           # VIEW.camera dials, per-frame easing with dt, the
│                     #   reduced-motion path, camera update in both the rAF
│                     #   loop and the redraw path
├── render.js         # this.tile from the camera, ctx.translate pan, ground
│                     #   bake at bakeTile with a source-rect blit, pond cache
│                     #   signature fix, screen->world helper for hit testing
├── meadow.js         # buildPondLayers gains bake dimensions; drift field
│                     #   keeps receiving WORLD dimensions
├── test-motion.mjs   # camera geometry, anchor choice, hysteresis, easing,
│                     #   follow lifecycle, hit testing
└── test-meadow.mjs   # ground bake and pond cache invalidation
```

**Structure Decision**: The existing flat `client/` layout is kept. This is a
plain-script client with a fixed load order and no build step; introducing a
module directory would mean either a bundler or a load-order change, and neither
is warranted by one feature. The camera is new state and new geometry inside
files that already own those concerns: `anim.js` owns presentation dials and the
frame loop, `render.js` owns the transform and the caches, `app.js` owns
viewer-facing state and persistence.

## Phase 0 — Research

See [research.md](./research.md). Nine decisions, of which three matter most:

- **The transform split** — scale via `this.tile`, pan via `ctx.translate`. Keeps
  `fine` honest and needs no edits to 235 coordinate sites.
- **The ground cache** — bake at the camera's largest tile, blit a downscaled
  source rectangle. Camera movement causes zero rebakes.
- **The pond cache's staleness key omits the tile**, a latent bug the camera
  would trigger silently. Found by reading the code, not predicted.

## Phase 1 — Design

- [data-model.md](./data-model.md) — camera state, its transitions, and the
  transform maths in both directions.
- [contracts/camera.md](./contracts/camera.md) — the camera's internal surface:
  what it consumes, what it exposes to the renderer, the two storage keys, and
  the invariants a change must not break.
- [quickstart.md](./quickstart.md) — how to run and validate, mapped to the
  spec's success criteria.

## What this plan deliberately does not decide

- **The card indicator's position** beside or beneath the name. The spec calls it
  a layout judgement to be tried both ways, and it is dialled with the owner
  rather than chosen here.
- **The exact easing rates.** kitten.me uses 0.06 pan and 0.05 zoom; those are a
  starting point to be judged in motion, not a result. They land in `VIEW.camera`
  where they can be dialled.
- **Whether the `fine` pop is tolerable.** The owner accepted it for this
  release specifically so it could be judged in motion rather than predicted.
