# Contract: the camera's sizing

CloudKitty's client exposes no network API. The contract is internal: what the
camera needs in order to size itself, and what must stay true afterwards.

---

## What the camera consumes

| input | source | note |
|---|---|---|
| `cssWidth` | `renderer.cssWidth` | **New.** The map's width in CSS pixels. The camera had no pixel input before this feature. |
| `aspect` | `cssHeight / cssWidth` | Unchanged, for the vertical fit. |
| kitty drawn positions | `view.posFor` | Unchanged, and still eased rather than served. |
| world dimensions | `world.width`, `world.height` | Unchanged, for the fit and the clamps. |

`cssWidth` is a **CSS pixel** measurement, sized from
`documentElement.clientHeight`/`clientWidth`. It is not the device resolution
and it is not affected by `dpr`, which only sharpens the canvas. A
high-resolution display at default scaling reports a *smaller* `cssWidth` than a
large low-resolution monitor.

---

## What must stay true

1. **`tile = cssWidth / across`** stays the renderer's line. The camera reports
   tiles; the pixel target is how it decides them. Anything that made the camera
   report pixels directly would move the transform's definition into two places.
2. **The floor and ceiling are computed once per frame and shared.** The fit's
   clamp, the `bound` predicate and the ground bake must read the same pair, or
   the anchor engages at a width the camera never reaches and the bake is keyed
   to a tile that is never drawn.
3. **Every drawable tile lies in `[ceilingPx, floorPx]` — across the supported
   viewport range, and only there.** The band originally had to clear the 44px
   fine-detail threshold with margin; that threshold was deleted on 2026-08-18,
   so the lower end now rests on the 47px portrait cards the art is tuned
   against. **The scope is load-bearing and was missing until review of PR
   #246**: below a `minTiles × ceilingPx` map the `minTiles` clamp forces both
   limits together and the tile falls under `ceilingPx` — which is FR-006
   working as specified, not a violation. **That threshold is 350px as of
   `minTiles: 7` (2026-08-19), against 300px before**, so it now reaches inside
   the verified range: a **340px map has no zoom range at all**, floor and
   ceiling both at 7 tiles and a 48.6px tile. That map pans and never zooms.
   Accepted — the owner's ruling of 2026-08-19 is that zoom range is
   instrumental, not a goal. Nothing in the code enforces
   the 340px lower bound; the range is where the feature is *verified*, not a
   gate it refuses to run below.
4. **The ceiling always frames less than the world.** Otherwise camera-on and
   camera-off are identical at full zoom-out and 036's FR-005 is silently
   retired.
5. **`floorTiles ≤ ceilingTiles`, always.** They may meet on a very small
   viewport; they may never invert.
6. **The bake tile is the floor tile**, which is the largest the camera can ask
   for — so the per-frame blit is a downscale **wherever `GROUND_BAKE_MAX_PX`
   does not bind** (036's research R2). Deriving it any other way reopens that.
   **The caveat is real, not theoretical**: that budget is in DEVICE px
   (`4096 / dpr`), so above dpr ≈ 2.05 with a 100px floor tile on a 20-tile
   world the bake is clamped BELOW the floor tile and the blit becomes a 1.28×
   to 1.46× upscale in steady state. That predates 037 — see the correction in
   `client-measurements/037-zoom-baseline/after-2026-08-18.md` — and the
   remedy is parked in `BACKLOG.md`.
7. **`fitMarginTiles` and `aimDeadzoneTiles` stay in tiles.** They describe world
   movement, not screen movement. Their pixel effect is already constant
   wherever the target is reachable; making them pixels would have the camera
   ignore *more* world on a small screen, which is backwards.
8. **Camera off is untouched.** This feature changes only the two limits.
