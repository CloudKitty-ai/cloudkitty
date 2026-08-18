# Phase 0 Research: Camera mode

Every finding below was read off the code in `client/` on 2026-08-17, not
recalled. Line numbers are from `036-camera-mode` at that date and will drift;
the named functions will not.

---

## R1 — How the camera reaches the renderer

**Decision**: Scale by setting `this.tile` to the camera's tile each frame. Pan
by `ctx.translate` at the top of the draw, reset each frame. Do not use
`ctx.scale`.

**Rationale**: `this.tile` is not merely a multiplier, it is the number every
art decision keyed to apparent size reads. `cat-v2.js` computes `fine = size >=
44` from the size it is drawn at, and that size is `this.tile`. Camera mode
exists to raise apparent size, so the tile is exactly the value that should
move. Setting it means all 83 `this.tile` references in `render.js` and all 152
tile references in `meadow.js` draw natively at camera scale with no edits.

A `ctx.scale` would magnify the finished picture instead. The cats would appear
larger while `this.tile` still read 31, so `fine` would never fire, hairlines
authored in pixels would thicken, and the art would be an upscale of the
small-size drawing rather than the large-size drawing. That inverts the point of
the feature.

Pan is the opposite case. It is a pure offset with no bearing on apparent size,
and `tileOrigin(pos)` is `{ x: pos.x * this.tile, y: pos.y * this.tile }` with no
origin term. Adding the offset there would cover its three call sites but miss
the places that multiply directly — `render.js:1379` computes `(fpos.x + 0.5) *
this.tile` inline, and it is not the only one. A translate on the context covers
every site, including ones added later, and cannot be forgotten at a new call
site.

**Alternatives considered**: `ctx.scale` for zoom (breaks `fine` and every
size-keyed art threshold). Threading a camera offset through `tileOrigin` and
each direct-math site (235 sites, and silently wrong at any site missed).

---

## R2 — The ground cache: bake at the largest tile, blit downscaled

**Decision**: Bake the ground once at `bakeTile`, the tile the camera produces
at its *narrowest* frame — nominal, 10 across — which is the largest tile the
camera can ever ask for. Each frame, draw the visible sub-rectangle with the
nine-argument `drawImage(cache, sx, sy, sw, sh, 0, 0, dw, dh)` form. The scale
factor `this.tile / bakeTile` is then at most 1, always a downscale.

**Rationale**: This is what keeps SC-003 reachable. Per-frame ground cost stays
one `drawImage`, which is what it is today. Rebake triggers stay exactly today's
set — canvas resize, dpr change, palette step, world change — and camera
movement adds none of them. Zooming and panning change only the source
rectangle.

Downscale-only matters for appearance. A cache baked at the whole-world tile and
magnified 2× would put a soft ground under crisp vector cats, which reads as a
rendering fault. Baking at the largest tile means the ground is never magnified.

**The failure mode this avoids is not hypothetical.** `render.js:507-513`
documents a prior incident in this exact code: a negative height budget produced
a CSS width the CSSOM rejected, so the resize guard mismatched every frame and
"rebakes the whole ground cache at 60fps". The comment exists because someone
shipped that once. A camera that keyed the bake to a per-frame tile would
reproduce it by design.

**Memory, and why it needs a cap**: the offscreen is `world.width × bakeTile ×
dpr` square, roughly twice the map's linear size and four times today's cache in
pixels. On a 620px map at dpr 2 that is about 2480² ≈ 6.1M device pixels, near
24MB — acceptable. On a 1200px map at dpr 2 it is 4800² ≈ 23M pixels, near 92MB,
and mobile Safari caps total canvas area well below what a desktop tolerates.
So `bakeTile` must be clamped by a device-pixel budget, with magnification
accepted past the clamp. Choose the budget explicitly rather than discovering it
as a blank canvas on an iPad.

**A consequence worth having**: because the bake covers the whole world rather
than the visible window, `driftField(width, height, t)` keeps receiving world
dimensions with no change. See R8.

**Alternatives considered**: rebake per frame at the live tile (the incident
above, by construction). Bake at the world tile and magnify (soft ground under
crisp cats). Bake per-tile into a sprite sheet and draw the visible tiles
individually (100–225 `drawImage` calls a frame instead of one, and it loses the
half-pixel overdraw that hides tile seams).

---

## R3 — The pond cache has a latent staleness bug the camera would trigger

**Finding**: `drawPondLayer` keys `this.pondCache` on `signature`, which is
built from the stable water tiles' positions and nothing else:

```js
const signature = stable.map((p) => `${p.x},${p.y}`).sort().join(';');
```

But the cached content is built at the current tile and canvas size —
`buildPondPath(tiles, this.tile)`, and `buildPondLayers({ tile, widthPx:
this.canvas.width, heightPx: this.canvas.height, dpr })`. Neither the tile nor
the canvas size appears in the key.

Today this is safe only by accident of another mechanism: `resizeFor` explicitly
nulls `pondCache` whenever the canvas is resized, so the two ways the tile can
change today both go through a resize. A camera changes the tile with no canvas
resize at all, so nothing would fire, the signature would match, and the ponds
would draw with the previous tile's geometry — shorelines at the wrong scale,
lily pads adrift, and no error anywhere.

**Decision**: Bake pond paths and layers at the same `bakeTile` as the ground
and scale them by the same factor, and add `bakeTile` to the signature so the
omission cannot bite again even if the scaling is later changed.
`buildPondLayers` must take the bake dimensions rather than `this.canvas.width`
and `this.canvas.height`, since the bake is larger than the canvas.

**Why this class of bug is worth naming in the plan**: it is a cache whose key
is a subset of its inputs, made safe by an invalidation elsewhere. The camera
breaks the elsewhere. Any other cache in the client with the same shape is
suspect for the same reason, which is what R9 checks.

---

## R4 — Frame-rate-corrected easing needs a `dt` the loop does not thread

**Finding**: the loop calls `performance.now()` fresh at each use —
`this.pump(performance.now())`, `p.viewAt(performance.now(), false)` — and no
field carries the previous frame's timestamp. There is no `dt` to correct with.

**Decision**: Keep one `lastFrameAt` on the animation object and derive `dt`.
Ease with `1 - (1 - rate) ** (dt / 16.67)`, so a rate authored per-frame at 60Hz
produces the same real-time settle at 120Hz. Clamp `dt` — a backgrounded tab
returning after 30 seconds must not produce an easing factor of 1 that reads as
the cut FR-008 forbids.

**Rationale**: without correction a 120Hz display eases twice as fast, which is
the bug kitten.me's own comment calls out. Their rates (0.06 pan, 0.05 zoom) are
a starting point for dialling, not a result to copy.

---

## R5 — Reduced motion is two paths, not one

**Finding**: when reduced motion is set, `startLoop()` is skipped entirely —
`if (!this.reduced) this.startLoop()` — and drawing happens only through
`redraw()` when a new state arrives. So there is no rAF loop to hang per-frame
camera easing on.

**Decision**: The camera's target is computed in both paths, and applied
instantly in the reduced path. FR-010 and SC-009 require exactly that, so the
requirement and the architecture agree: with no easing there is nothing for a
frame loop to do, and the served-tick redraw is sufficient.

**Trap**: this means the camera update cannot live only inside `startLoop`'s rAF
callback. A camera written there alone would work perfectly in testing and be
frozen for every viewer with reduced motion set.

---

## R6 — The camera must aim at drawn positions, not served ones

**Decision**: Aim at `view.posFor(kitty)`, the eased presentational position,
not `kitty.pos` from the snapshot.

**Rationale**: `anim.js` runs a `Pacer` that pays served states out on its own
clock and eases between them, so a kitty's drawn position lags her served
position by up to a tick. A camera aiming at served positions would jump forward
each tick and ease back, giving a visible per-tick pulse — the camera leading
the cats it is supposed to be following. `drawnPosOf` already wraps this for the
renderer's own use and is the pattern to follow.

---

## R7 — Hit testing is entirely new

**Finding**: no click, pointer, or touch handler is bound to the canvas anywhere
in the client. The only canvas interactions are a `ResizeObserver` and a
`getBoundingClientRect` read for scroll centring on short viewports. Existing
click handling is all panel and footer DOM.

**Decision**: One pointer handler on the canvas, converting client coordinates
to world tiles, then selecting the frontmost kitty within a hit radius.

**Two traps in the conversion.** First, `resizeFor` applies a display `scale`,
so the canvas's CSS size is not its layout size; the conversion must divide by
the measured `rect.width`, never by `this.cssWidth`. Second, the pan translate
from R1 must be undone — screen to world is the inverse of the draw transform,
and writing it independently is how the two drift apart. Derive one from the
other.

**Overlap and small targets**: kitties are depth-sorted sprites and overlap
freely, so a hit must resolve to the frontmost — the one the viewer sees — which
is the last drawn in sort order. And a kitty at the zoom ceiling on a phone is
roughly 23px, so the hit radius needs a floor in CSS pixels rather than being
one tile. This is the same problem FR-026 addresses from the other side, and it
is why clicking away from the kitties had to become a release gesture.

---

## R8 — The drift normaliser stays world-scoped for free

**Finding**: `driftField(width, height, t)` in `meadow.js` takes world
dimensions, and the drift normaliser is solved per world against the realised
count. If it were ever handed the visible window instead, decoration density
would change as the camera zoomed, violating FR-024 and SC-012.

**Decision**: No change needed, and R2 is why. Because the ground bakes the
whole world rather than the visible window, the normaliser continues to receive
world dimensions with nothing threaded through. A window-sized bake would have
forced this question and probably got it wrong.

---

## R9 — Fractional tiles are acceptable; the integer was for canvas sizing

**Finding**: `this.tile` is `Math.floor(...)` today and the comment beside it
says "integer tiles keep the art crisp". A camera easing continuously produces a
fractional tile, so this needs checking rather than assuming.

Searching the drawing code for integer assumptions on tile-derived values turns
up one, and it is not a geometry site: `meadow.js:2161` rounds a caustic *line
count*, which is a count and correctly rounded. The ground's tile seams are
already handled by drawing each tile half a pixel oversized rather than by
integer alignment.

**Decision**: Allow a fractional camera tile. Keep the integer floor for the
canvas backing-store sizing, which is what the comment is actually protecting —
the canvas is still sized from the world and the viewport, and only the camera's
drawing tile is fractional.

---

## Open items carried into implementation

These are dialling questions, not unknowns. Each has a starting value and a way
to judge it.

| Item | Start from | Judged by |
|---|---|---|
| Pan and zoom easing rates | 0.06 / 0.05, kitten.me's | In motion, at 3 and 5 kitties |
| Anchor hysteresis margin | 1.5× real distance (FR-007) | SC-006, at most 3 anchor changes a minute |
| Fit margin around outermost | 2.6 tiles, kitten.me's | FR-004, no kitty touching the frame edge |
| Hit radius floor | Enough for a phone at the ceiling | SC-013 |
| `bakeTile` device-pixel budget | Set below mobile Safari's cap | A 4K display and an iPad, both |
