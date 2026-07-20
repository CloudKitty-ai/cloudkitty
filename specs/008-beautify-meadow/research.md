# Research: The Meadow Itself — Beautification II, Step 2

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Eight decisions (R1–R8). Grounded in the shipped client — `render.js`'s
ground cache and element draw path, `anim.js`'s `Presentation` (discontinuity
memory, viewAt), `app.js`'s `g` toggle — and the 2026-07-20 ideation recorded
in BACKLOG.md and the 008 spec. Two engine facts anchor everything: **water
and sunbeams are served *elements*** (they can spawn and expire, with the
established fade-in/fade-out), not static tiles; and the checkerboard lives
in an **offscreen ground cache** built once per resize and blitted per frame.

## R1 — A sibling file, the fourth voice in one vocabulary

**Decision**: the ground lives in a new `client/meadow.js`, loaded after
`props.js` and before `render.js`. It carries the named `MEADOW` palette, the
`tileHash` scatter source, and the draw family (`drawMeadowGround`,
`buildPondPath`/`drawPonds`, `drawWorldEdge`, `drawSunbeamGlow`,
`drawWornPaths`, `drawGridOverlay`). Same conventions as `cat.js`/`props.js`:
plain script in shared lexical scope, `VIEW` read at call time, ctx-only, no
DOM, no fetches.

**Rationale**: the ground is its own judged surface — the FR-014 checkpoint's
revision loop should touch one file, exactly the property that made the 005
and 007 gates fast. `render.js` stays the orchestrator; `anim.js` stays the
home of every clock and memory.

**Alternatives considered**: growing `render.js` (600 lines already; revision
loops would churn the orchestrator); folding into `props.js` (props are
judged in the gallery, the ground is judged live — different gates, different
files).

## R2 — One hash to scatter them all

**Decision**: `tileHash(x, y)` — a small integer bit-mixer over the two
coordinates (multiply by two large odd constants, xor, avalanche, normalize
to [0, 1)) — is the *single* source of all positional variety. Derived
lookups peel independent values from it (tone index, brightness jitter,
flora presence/kind/offset) by remixing with distinct named salts. No
`Math.random`, no seed, no state.

**Rationale**: FR-002/FR-003 verbatim: a pure function of position is
deterministic across reloads and restarts by construction, needs no storage,
and scales to any world size with density naturally proportional to area.
The grass-sway ambient already uses a modulo scatter (`(x*31 + y*17) % 41`)
— this generalizes that idea with better distribution (no diagonal banding,
SC-002) and one named home.

**Alternatives considered**: seeding from the world fingerprint (adds a
dependency for no visible gain — two worlds sharing a decoration layout at
the same coordinates is consistency, not a bug); a precomputed noise texture
(cache invalidation and scaling artifacts for something a hash gives free).

## R3 — The meadow rides the existing ground cache; the grid moves out

**Decision**: `blitGround` keeps its exact caching structure (build once per
resize, blit per frame) but its body becomes `drawMeadowGround` + 
`drawWorldEdge`: per-tile base tone picked from 3–4 close greens by hash,
per-tile brightness jitter as a barely-visible overlay tint, sparse flora
(tufts, clover, three-petal flowers) hash-placed at hash-jittered offsets,
and the fringe frame around the boundary. The grid lines are **removed from
the cache** and become `drawGridOverlay`, drawn per frame only while the new
`showGrid` flag is on (default off, fresh load off).

**Rationale**: the meadow is static per world size — precisely what the
cache exists for; per-frame cost stays one `drawImage` (SC-005). The grid
must leave the cache because a toggle that requires rebuilding an offscreen
canvas on every keypress is backwards; a lattice of lines per frame is cheap
and only debug sessions pay it.

**Alternatives considered**: two cached layers (grid cache is overkill for
line strokes); drawing the meadow per frame (thousands of fills back on the
hot path — the exact thing 005 R7 removed).

## R4 — Ponds: group served water, cache the shoreline, respect the fades

**Decision**: each frame's water elements are grouped into ponds by
4-adjacency over their tile positions. The pond outline is traced by
marching squares over the group's tile set, with corners rounded by
quadratic curves at a named shore-rounding radius, into a `Path2D` cached
under the pond set's sorted-position signature — rebuilt only when the
water set actually changes (spawn/expiry are rare environment events). Fill
+ rim stroke in the water hues; ponds at or above `lilyPadMinTiles` get one
lily pad, hash-placed from the pond's anchor (lowest x,y) tile. The
existing shimmer ambient plays over pond surfaces unchanged. Spawn/expiry
fades keep the established per-element behavior: a fading water element is
drawn as its own small rounded pool at the element alpha (today's visual),
joining or leaving the merged pond body when the set-change rebuild happens
at full presence — the pond body itself always draws the stable tiles.

**Rationale**: FR-005/FR-006 — the seam-free shoreline is the whole point
(SC-003), and keying the cache on the position signature makes the common
frame free while staying honest about water being expirable elements, not
terrain. Marching squares is the smallest algorithm that handles every blob
shape, holes included, without special cases.

**Alternatives considered**: per-tile rounded rects with neighbor-aware
corner radii (leaves visible seams at concave junctions — fails SC-003);
metaball blobs (organic but shape drifts off the true tile footprint,
risking a kitty drinking from dry land — fails FR-006's honesty).

## R5 — Sunbeams: the square becomes light

**Decision**: `drawSunbeamGlow` replaces the rounded-rect body of
`drawSunbeam` with a radial gradient centered on the tile — warm core
fading to transparent at a named radius of ~1.4 tiles — under the exact
pulse and dust motes the 005 ambient already provides (their code paths and
flags untouched). Overlapping glows draw with default compositing at a low
named alpha, so adjacency blends by natural gradient accumulation without
banding.

**Rationale**: FR-008 verbatim — the bleed past tile bounds is what turns
"tinted tile" into "light on grass", and reusing the existing
pulse/mote/alpha plumbing means the only change is the body of one draw
call. Low-alpha default compositing is the no-surprises blend: `lighter`
would blow out the cream palette where beams overlap.

**Alternatives considered**: compositing modes (`lighter`, `overlay`) —
oversaturate against the pastel meadow; pre-rendered glow sprite (cache
machinery for a gradient the GPU fills trivially).

## R6 — Worn paths: memory lives with the other memories

**Decision**: worn-path accumulation lives in `Presentation`: on each
*continuous* `pushState`, every kitty's served tile position bumps a heat
entry (`Map` keyed `"x,y"` → `{heat, stampedAt}`), clamped at a named cap;
heat decays at read time by a wall-clock half-life (no per-frame writes);
the existing discontinuity branch clears the map exactly where it clears
facings, one-shots and sleep memory. `viewAt` exposes a path snapshot
(decayed entries above a visibility floor); `render.js` draws it between
ground and elements — soft rounded tints per warm tile, opacity scaled by
heat — only while the new `showPaths` flag is on. The toggle controls
visibility only: accumulation runs regardless (spec US5 scenario 4).
Under reduced motion the overlay still draws when toggled (it is state, not
motion) from the same snapshot path.

**Rationale**: FR-009's clearing rule is exactly the discontinuity contract
`Presentation` already enforces — putting the memory anywhere else would
duplicate that logic and drift. Decay-at-read keeps the store pure and
testable headlessly (times injected, like every Presentation test), and
read-time decay makes "fades gradually" free of timers.

**Alternatives considered**: accumulating in the renderer (no discontinuity
knowledge, untestable without DOM); a per-frame decay pass (busywork and a
hidden clock; read-time decay is equivalent and pure); per-pixel trail
canvas (prettier smearing, but resolution-dependent, expensive to clear,
and impossible to unit test — tile-grained heat matches the world's own
granularity).

## R7 — Tunables, palette, and two new keys

**Decision**: all numbers join the frozen `VIEW` under a `meadow` sub-object
— per-layer enable flags (`scatter`, `ponds`, `edge`, `glow`, `paths`
availability, `gridOverlay` availability) in the `VIEW.ambient` mold, plus
`toneCount`, `jitterAlpha`, `floraDensity`, `shoreRounding`,
`lilyPadMinTiles`, `glowRadiusTiles`, `glowAlpha`, `edgeDepth`,
`pathHeatCap`, `pathHalfLifeMs`, `pathVisibilityFloor`. Colors live in a
named `MEADOW` palette block in `meadow.js` (grass tones, jitter tint,
flora hues, pond water/rim/lily, edge fringe, glow warm, path tint, grid
line). `TILE_COLORS` in `render.js` shrinks to whatever remains in use, or
retires if nothing does. Keys: **`l`** toggles grid lines, **`p`** toggles
worn paths — both in the `g` mold (window keydown, renderer flag, footer
note, redraw), chosen to avoid `g` and each other and to read mnemonically
(*lines*, *paths*).

**Rationale**: FR-010 and Article VI — one tunables home, one palette-with-
the-drawings home, the split 005 established and 007 confirmed. Runtime
toggle *state* stays on the renderer (like `showGreebles`) because `VIEW`
is frozen; `VIEW` carries whether a layer exists at all.

**Alternatives considered**: a separate `MEADOW_TUNABLES` in `meadow.js`
(splits the Article VI audit surface — rejected for props in 007 R7,
rejected again); `w` for paths ("worn") — collides with no one but reads
worse than `p`.

## R8 — Verification without new machinery

**Decision**: the established three tiers, with the human gate moved where
the ground can actually be judged: (1) the **live checkpoint** (FR-014) on
demo worlds at default and ≥4× area, recorded in `meadow-approval.md`,
revision loops confined to `meadow.js`; (2) quickstart visual checks per
story (meadow variety and reload-stability, pond seam sweep, edge at three
sizes, glow under reduced motion, path accumulate/fade/clear, toggle
defaults and footer hints, legibility sweep); (3) headless node harnesses:
`tileHash` determinism + distribution (no visible banding statistics, e.g.
tone-run lengths), pond grouping and `buildPondPath` over crafted sets
(single tile, 2×2, L/U/ring shapes, border-touching), `Presentation` path
memory (accumulate, cap, decay, clear-on-discontinuity, toggle-independent
accumulation), and mock-ctx sweeps of every draw function across sizes and
world dims with the non-finite guard. The Rust suite must pass untouched
and `git diff --stat crates/ cloudkitty.toml` must be empty (SC-007).

**Rationale**: acceptance is visual by nature; the automatable core — the
hash, the grouping, the memory — is exactly the derivation logic, same
shape as 005/007. No JS test toolchain (standing decision 005 R10).

**Alternatives considered**: pixel-snapshot tests (flaky cross-platform —
unchanged verdict); a gallery page for ground swatches (the ground only
reads in context at world scale; the live checkpoint *is* its gallery).
