# Implementation Plan: The Meadow Itself — Beautification II, Step 2

**Branch**: `008-beautify-meadow` | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-beautify-meadow/spec.md`

## Summary

Give the world a ground worthy of its residents: an organic meadow (close
grass tones, brightness jitter, scattered flora) replacing the checkerboard,
contiguous water merged into smooth-shored ponds with lily pads, a grass-fringe
world edge, sunbeams rendered as radial pools of warm light, and a session-local
worn-paths overlay behind a new keyboard toggle — with the tile grid demoted to
a debug-only overlay behind another. Technically: one new `client/meadow.js`
(palette, per-tile hash, and the ground/pond/edge/glow/path drawing family),
consumed by `render.js` (whose checkerboard, square water, and square sunbeam
call sites are swapped out); worn-path accumulation joins `Presentation` in
`anim.js`, where discontinuity handling already lives; all tunables join the
frozen `VIEW`. The anchoring principle from the spec: **every decoration is a
deterministic function of position** — a pure per-tile hash, no randomness, no
new served data. Zero engine or server changes.

## Technical Context

**Language/Version**: Vanilla JavaScript (ES2020+, browser-native, no build
step), HTML5 Canvas 2D — identical to the shipped 005/007 client.

**Primary Dependencies**: none. Plain scripts sharing top-level lexical scope;
`meadow.js` loads after `props.js` and before `render.js`, reads `VIEW` at
draw time exactly as `props.js` does (call-time lookup, load order
irrelevant).

**Storage**: n/a — the meadow derives from position, ponds/glows from served
elements, worn paths from session-local viewer memory that is never persisted
or transmitted.

**Testing**: the established three-tier pattern: (1) a recorded human approval
checkpoint judged in the live viewer at two world sizes (FR-014), (2)
quickstart visual checks per story, (3) headless node harnesses via the
mock-ctx pattern — hash determinism/distribution, pond grouping and shoreline
path construction, worn-path accumulate/decay/clear in `Presentation`, and
draw-function sweeps over sizes × states with the non-finite guard. Rust
suite green with an empty `crates/` + `cloudkitty.toml` diff (SC-007).

**Target Platform**: modern desktop browsers, retina-aware, as 005/007.

**Project Type**: web client (static files served by the existing fallback).

**Performance Goals**: no regression to the shipped smoothness (SC-005). The
meadow ground and edge render once into the existing offscreen ground cache
(same blit-per-frame cost as today); pond shorelines are cached `Path2D`
objects rebuilt only when the water-tile set changes; the glow is one radial
gradient per sunbeam; worn paths draw at most one soft rect per warm tile,
only while toggled on.

**Constraints**: pure view (Article V) — decoration derives from position and
served state only; worn paths are local presentational memory in the mold of
facing memory and one-shots (derived from served positions, cleared on
discontinuity, never sent); named palette + named tunables (Article VI);
reduced motion keeps all static decoration (FR-012); kitty/prop legibility
outranks decoration (FR-011); greeble secrecy untouched; zero engine/server
diff (FR-013).

**Scale/Scope**: 1 new file (`client/meadow.js`), 3 extended
(`client/render.js`, `client/anim.js`, `client/app.js`), 1 touched for the
script tag + footer hints (`client/index.html`); ~1 `VIEW` sub-object of
tunables; 5 user stories with one recorded live approval checkpoint.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Articles I–III** — PASS. No simulation contact; kitty welfare, lifecycle
  and company are untouched.
- **Article IV** — PASS. Nothing proposes; the viewer stays read-only.
- **Article V** — PASS. Every layer is presentational: the meadow is a pure
  function of tile coordinates; ponds are a redrawing of exactly the served
  water elements (membership, spawning, expiry, and pathing unchanged); the
  glow redraws served sunbeams; worn paths are session-local view memory
  derived from served kitty positions — the same lawful category as facing
  memory and one-shot beats, cleared on every discontinuity, never
  transmitted. Nothing is predicted, invented, or sent back; the server never
  learns where cats walked.
- **Article VI** — PASS. All colors in one named `MEADOW` palette block
  (mirroring `PALETTES`/`PROPS`); every number (tone count, jitter amplitude,
  flora density, shore rounding, lily-pad threshold, glow radius/alpha, path
  heat cap, path fade half-life, edge depth) is a named `VIEW.meadow` entry;
  layer flags are individually toggleable like `VIEW.ambient`. Spec-first:
  this plan follows the 008 spec; the look is approved at the recorded live
  checkpoint (FR-014, SC-008) in [meadow-approval.md](./meadow-approval.md).

*Post-design re-check (after Phase 1)*: PASS — the design below adds no wire
surface, no simulation contact, no unnamed values. Complexity Tracking stays
empty.

## Project Structure

### Documentation (this feature)

```text
specs/008-beautify-meadow/
├── plan.md              # This file
├── research.md          # Phase 0 output (R1–R8)
├── data-model.md        # Phase 1 output (layers, palette, state mapping)
├── quickstart.md        # Phase 1 output (visual validation guide)
├── meadow-approval.md   # FR-014 gate record — created by the approval task
├── contracts/
│   └── meadow-contract.md  # served-data ↔ decoration mapping; unchanged rules
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
client/
├── meadow.js       # NEW — the ground vocabulary: MEADOW palette (named
│                   # grass/flora/pond/glow/edge/path/grid hues), tileHash(x,y)
│                   # (the one deterministic scatter source), and the draw
│                   # family: drawMeadowGround (tones + jitter + flora, into
│                   # the ground cache), buildPondPath / drawPonds (contiguous
│                   # water -> smooth shoreline Path2D, lily pads),
│                   # drawWorldEdge (fringe frame), drawSunbeamGlow (radial
│                   # warm light), drawWornPaths (heat -> soft trail tint),
│                   # drawGridOverlay (the demoted debug lattice). No DOM
│                   # beyond ctx, no fetches.
├── render.js       # SWAPPED — blitGround paints the meadow + edge into the
│                   # existing offscreen cache (grid lines removed from it);
│                   # water elements route through the pond layer (grouping +
│                   # cached Path2D keyed by the water-position signature);
│                   # drawSunbeam's rounded square becomes the glow (pulse and
│                   # motes unchanged on top); new showGrid / showPaths flags
│                   # in the showGreebles mold; worn paths drawn between
│                   # ground and elements when toggled.
├── anim.js         # EXTENDED — VIEW gains the frozen `meadow` tunables
│                   # sub-object (incl. per-layer flags); Presentation gains
│                   # worn-path memory: accumulate per served kitty position
│                   # on each continuous pushState, wall-clock decay at read,
│                   # cleared in the existing discontinuity branch; viewAt
│                   # exposes the path-heat snapshot.
├── app.js          # EXTENDED — two new keydown toggles beside `g`
│                   # (grid + paths), wired to renderer flags + footer notes.
└── index.html      # script tag for meadow.js (after props.js, before
                    # render.js); footer hints for the two new keys.

crates/            # UNTOUCHED — an explicit quickstart/tasks check
cloudkitty.toml    # UNTOUCHED
```

**Structure Decision**: a sibling `meadow.js` rather than growing `render.js`
— the ground is its own judged surface (the FR-014 checkpoint revises this
one file, exactly the single-file revision loop the two gallery gates
proved), while `render.js` keeps orchestration and `anim.js` keeps every
Article V-sensitive decision (clocks, memory, discontinuities), where 005 put
them.

## The FR-014 checkpoint (sequencing constraint for /speckit-tasks)

The five stories are built in priority order and each is independently
visible live. The recorded human checkpoint happens **before the feature
lands as the default view** (i.e., before push/PR): Elizabeth judges the full
look in the live viewer on demo worlds at default size and at least one
larger size — never her real save — decides any revisions (loops touch only
`client/meadow.js` and its palette/tunables), and the outcome is recorded in
`meadow-approval.md` (FR-014, SC-008). Mid-build story-by-story looks are
welcome but only the recorded checkpoint closes the gate.

## Complexity Tracking

No constitution violations to justify — table intentionally empty.
