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
3. **Every drawable tile lies in `[ceilingPx, floorPx]`.** The band originally
   had to clear the 44px fine-detail threshold with margin; that threshold was
   deleted on 2026-08-18, so the lower end now rests on the 47px portrait cards
   the art is tuned against — the camera's smallest tile is never smaller than
   what was dialled.
4. **The ceiling always frames less than the world.** Otherwise camera-on and
   camera-off are identical at full zoom-out and 036's FR-005 is silently
   retired.
5. **`floorTiles ≤ ceilingTiles`, always.** They may meet on a very small
   viewport; they may never invert.
6. **The bake tile is the floor tile.** It is the largest the camera can ask
   for, which is what keeps every per-frame blit a downscale (036's research
   R2). Deriving it any other way reopens that.
7. **`fitMarginTiles` and `aimDeadzoneTiles` stay in tiles.** They describe world
   movement, not screen movement. Their pixel effect is already constant
   wherever the target is reachable; making them pixels would have the camera
   ignore *more* world on a small screen, which is backwards.
8. **Camera off is untouched.** This feature changes only the two limits.
