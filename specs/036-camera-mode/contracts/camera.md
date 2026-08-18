# Contract: the camera's internal surface

CloudKitty's client exposes no network or public API — it is a pure view over a
server-authoritative world. The contract that matters is therefore internal: the
boundary between the camera and the code that already exists, and the invariants
a later change must not quietly break.

---

## What the camera consumes

| Input | Source | Note |
|---|---|---|
| Kitty drawn positions | `view.posFor(kitty)` | Eased, not served. Aiming at served positions pulses once per tick. |
| Roster | `world.kitties` | Read only. The camera never filters or reorders it. |
| World dimensions | `world.width`, `world.height` | For the frame clamp. |
| Map CSS width | `renderer.cssWidth` | The camera divides it; it never sets it. |
| Reduced motion | `anim.reduced` | Existing flag. |
| Frame timestamp | `performance.now()` | For `dt`. |

**The camera consumes no server call, no new endpoint, and no field the client
does not already receive.** This is Article V holding by construction, and it is
what SC-011 tests: two viewers at different zooms must see the same world.

---

## What the camera exposes

```
camera.update(world, view, now)     // advance easing; call from BOTH paths
camera.tile                         // CSS px per world tile this frame
camera.left, camera.top             // frame origin in world tiles, clamped
camera.anchorId                     // which kitty is aimed at, or none
camera.toWorld(clientX, clientY)    // inverse transform, for hit testing
```

`update` must be called from the rAF loop **and** from the served-tick redraw.
Reduced motion skips `startLoop` entirely, so a camera advanced only in the rAF
callback is frozen for every viewer with reduced motion set (research R5).

---

## The renderer boundary

The camera reaches the drawing code through exactly two assignments per frame,
and nothing else:

```
renderer.tile = camera.tile                                     // scale
ctx.translate(-camera.left * tile, -camera.top * tile)          // pan
```

Everything downstream is untouched: 83 `this.tile` sites in `render.js`, 152
tile references in `meadow.js`, `tileOrigin`, and the sites that multiply by the
tile inline without going through it.

**Do not replace the tile assignment with `ctx.scale`.** `this.tile` is the size
every art threshold reads, including `fine = size >= 44`, which is the detail
camera mode exists to reveal. A `ctx.scale` magnifies the small-size drawing
instead of producing the large-size drawing, and `fine` never fires.

---

## Storage

| Key | Values | Written |
|---|---|---|
| `cloudkitty-camera` | `'on'` \| `'off'` | On toggle |
| `cloudkitty-follow` | kitty id as a string, or absent | On follow and release |

Read once at startup inside a `try`. `localStorage` throws rather than returning
null in some privacy modes; an unreadable store falls back to defaults and the
feature still works. Same shape as `THEME_KEY` and `CARDS_KEY`.

A stored id matching no kitty in the world is dropped, and camera mode is
unaffected (FR-020).

---

## Invariants a change must not break

1. **The camera never writes to the world.** No mutation of `world`, no field
   added to a kitty, nothing sent to the server. (Article V, FR-021, SC-011)
2. **The inverse transform is derived from the forward one**, not written
   separately. Two hand-written transforms drift, and the symptom is clicks
   landing on the wrong kitty at some zooms and not others.
3. **`bakeTile` is the largest tile the camera can ask for**, so every baked
   blit is a downscale. If a change makes the camera zoom in past nominal, the
   bake must move with it or the ground goes soft.
4. **Camera movement triggers no cache rebake.** The rebake triggers are canvas
   resize, dpr change, palette step, and world change — today's set, unchanged.
   A guard that mismatches every frame rebakes the ground at 60fps; this has
   happened once already in this file and the comment at `render.js:507` records
   it.
5. **Any cache built at the tile must key on the tile.** `pondCache` did not, and
   was safe only because `resizeFor` nulled it on resize. The camera removes that
   protection.
6. **The drift field receives WORLD dimensions**, never the visible window, or
   decoration density changes with zoom. (FR-024, SC-012)
7. **The camera-mode control stays keyboard-operable** with a visible focus
   state. Following is pointer-only by decision; the control must not lose
   keyboard access alongside it. (FR-028, SC-014)
8. **The camera aims at a kitty, never at empty ground** — not the bounding-box
   midpoint, not the centre of mass. Both are usually grass. (FR-006, SC-005)
