# Phase 0 Research: Camera zoom targets

Read off `client/` on 2026-08-18 at `ecc945b`, not recalled. Line numbers drift;
the named functions do not.

---

## R1 — The camera has no pixel input, and that is the whole change

**Finding**: `Camera.update(world, view, opts)` receives only `{ aspect }`, and
`targetFor(world, view, aspect)` computes `across` from tile counts alone. The
pixel size appears one level up, in the renderer:

```js
cam.update(world, view, { aspect: this.cssHeight / this.cssWidth });
this.tile = this.cssWidth / cam.across;
```

**Decision**: Pass `cssWidth` into `update` alongside `aspect`. The camera then
computes `across = cssWidth / targetPx` instead of reading a tile count.

**Why this is small**: the renderer's `tile = cssWidth / across` line is
unchanged, because `across` is still what the camera reports. Substituting
`cssWidth / targetPx` for `across` makes that line evaluate to `targetPx`
exactly. Everything downstream of the tile — the transform, the 80-odd
`this.tile` reads, `meadow.js` — sees a number arrived at differently and
behaves identically.

**Alternatives considered**: having the renderer convert a pixel target into a
tile count and keep passing tiles (splits one decision across two files, and the
camera could no longer explain its own floor); giving the camera a reference to
the renderer (a cycle, for one number).

---

## R2 — Four call sites read the dials being replaced

`nominalAcross` and `ceilingFactor` are read in exactly four places:

| site | today | becomes |
|---|---|---|
| `targetFor`, the floor | `Math.max(spanX, spanY, d.nominalAcross)` | floor from `cssWidth / floorPx`, clamped up to the minimum tile count |
| `targetFor`, the ceiling | `d.nominalAcross * d.ceilingFactor` | `cssWidth / ceilingPx`, clamped below the world |
| `targetFor`, the `bound` flag | `Math.max(spanX, spanY) > d.nominalAcross * d.ceilingFactor` | compared against the same derived ceiling |
| `bakeTileFor` | `cssWidth / Math.min(d.nominalAcross, world.width)` | the floor tile the camera reports |

**Decision**: all four take their number from one derived pair — the floor and
ceiling in tiles — computed once per frame. The `bound` flag must use the *same*
ceiling the fit is clamped to, or the anchor takes over at a different width
than the camera actually stops at.

---

## R3 — The ground bake gets simpler and smaller

**Finding**: `bakeTileFor` derives the bake from `nominalAcross`, so today it is
`cssWidth / 10` — which on a 1200px map is a 120px bake tile and a 2400 CSS px
offscreen before dpr.

**Decision**: the bake tile becomes the camera's floor tile, which under a pixel
target is the target itself (100px) wherever it is reachable. The bake is then
`world.width × 100` — **display-independent**, and smaller than today's on every
large viewport.

**Consequence worth having**: the `GROUND_BAKE_MAX_PX` clamp added in 036 binds
less often, and `POND_BAKE_MAX_PX` with it. Neither can be removed — a large
world under Fog would push the bake up again — but the pressure moves the right
way, which is the opposite of what a zoom change usually does to a cache.

---

## R4 — The ceiling can exceed the world, and must not

**Finding**: a 50px ceiling asks for `cssWidth / 50` tiles: 20 on a 1000px map
and 24 on a 1200px one. The world is 20 tiles.

**Decision**: clamp the ceiling below the world, so the camera still crops.
Where the clamp binds, that viewport's zoom range is smaller than the constant
2.00× the scheme otherwise guarantees.

**This is the Fog dependency, and it is worth stating plainly**: on today's
world the two largest viewports lose part of the benefit. At 40×40 nothing
clamps. The feature still improves on 3.5× everywhere, so it is worth shipping
first, but its full value on large viewports arrives with the bigger world.

---

## R5 — FR-008 is satisfied by the scheme, and SC-008 cannot pass as written

**Finding**: `aimDeadzoneTiles` (1.5) and `fitMarginTiles` (2.6) are in tiles.
The clarification worried their pixel effect would vary; measured against the
new scheme, it mostly does not:

| viewport | floor tile | 1.5-tile deadzone |
|---|---:|---:|
| phone | 57px | 86px |
| laptop / Retina | 77px | 116px |
| 1080p 27in | 100px | **150px** |
| large monitor | 100px | **150px** |
| at the cap | 100px | **150px** |

Wherever the pixel target is reachable the effect is **identical**, because the
tile is identical. The variation is confined to the viewports where the minimum
tile count binds — the same ones that give up range, for the same reason.

**Decision**: leave both dials in tiles. Tiles are the honest unit for them: the
deadzone exists to ignore a kitty shuffling a tile, which is a world quantity,
not a screen one. Re-expressing them in pixels would make the camera ignore
*more* world movement on a small screen, which is backwards.

**But SC-008 says "across the supported viewport range … within 25%"**, and the
small end is 74% away. SC-004 carries the caveat this needs — "every viewport
that reaches the pixel target" — and SC-008 does not. **Left for the owner
rather than edited**: narrowing a criterion so the implementation passes is what
rule 4 forbids, and this is the third time in this arc that a criterion has
turned out to be scoped differently from its sibling.

---

## R6 — The minimum tile count has no value yet

**Finding**: the spec requires a minimum (FR-005) and names none; the owner's
band is 100/50 with the minimum left open. The modelling used 6.

**Decision**: carry 6 as the starting value and dial it. At 6 a phone's 340px
map gives a 57px tile — above the 44px threshold with 13px of margin — and a
1.13× range. Lowering it buys range and costs framing; raising it does the
reverse. It is the one number in the band with a genuine trade behind it, and
the lab is where that gets seen.

---

## R7 — The `short` viewport case does not interact

**Finding**: `resizeFor` has a documented exception — a viewport under 500px
tall fits the map to its *width* and lets the page scroll, because a square world
in a 280px-tall window is a 12px tile whatever you do.

**Decision**: nothing to change. The camera consumes `cssWidth`, which that
branch sets exactly as the other one does; the branch decides how big the map
is, and the camera only asks how big it turned out.

---

## R8 — `MAP_MAX_PX` caps the largest floor

**Finding**: the map is capped at 1200 CSS px, so at a 100px target the floor
never frames more than 12 tiles no matter how large the viewport.

**Decision**: no upper tile clamp is needed. The cap already provides one, and
it does so in the unit that matters — a viewport bigger than the cap simply gets
the cap's map, so its camera behaves as the cap's does. This is why the maximum
tile count from the spec's first draft was removed rather than given a value.

---

## Open items carried into implementation

Dialling questions, each with a starting value and a way to judge it.

| Item | Start from | Judged by |
|---|---|---|
| Floor pixel target | 100 — what a large monitor shows today at 036's full zoom | SC-001, and every art value already dialled against it |
| Ceiling pixel target | 50 — above the 44px threshold with margin | SC-002, SC-003: detail must not flicker at the widest |
| Minimum tile count | 6 | US2: a phone still shows a scene |
| Whether SC-008 keeps its scope | unchanged | The owner's call, not the plan's |
