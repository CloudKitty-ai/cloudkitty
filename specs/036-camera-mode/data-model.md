# Phase 1 Data Model: Camera mode

Nothing here reaches the server. Every entity is view state, derived each frame
from the world snapshot the client already holds plus two viewer choices.

---

## Stored state — the only state that outlives a frame

| Field | Type | Storage key | Default |
|---|---|---|---|
| `cameraOn` | boolean | `cloudkitty-camera` | `false` |
| `followId` | kitty id, or none | `cloudkitty-follow` | none |

Both follow the `THEME_KEY` / `CARDS_KEY` pattern: read once at startup inside a
`try`, written on change. `localStorage` throws rather than returning null in
some privacy modes, so an unreadable store must fall back to the defaults and
leave the feature working.

`followId` is the kitty's authored id from `cloudkitty.toml`, not an array
index. Ids are copied through `World::generate` and never derived from order,
and the roster only ever grows or shrinks at its top end, so an id is present or
absent and never means a different kitty. A restored id that matches no kitty is
dropped (FR-020).

---

## Derived state — recomputed every frame, never stored

| Field | Meaning |
|---|---|
| `anchor` | The kitty the camera aims at. The followed kitty when there is one, otherwise the kitty nearest the group's centre of mass. |
| `targetAcross` | Frame width in tiles the fit currently wants, before easing. Clamped to `[nominal, nominal × 1.5]` = `[10, 15]`. |
| `across` | The eased frame width actually drawn this frame. Fractional. |
| `aim` | The eased aim point in world tile coordinates. Fractional. |
| `tile` | `mapCssWidth / across`. Becomes `renderer.tile` for the frame. |

`anchor` is chosen from **drawn** positions (`view.posFor`), not served ones, so
the camera does not lead the cats by up to a tick. See research R6.

---

## The follow lifecycle

One table, because the interaction between the toggle and the follow is where
this feature's only real ambiguity lived.

| Current | Event | Result |
|---|---|---|
| any | toggle | `cameraOn` flips. `followId` **unchanged** (FR-027). |
| off, no follow | click kitty *k* | on, following *k* (FR-012) |
| off, following *f* | click kitty *k* | on, following *k* |
| on, no follow | click kitty *k* | following *k* |
| on, following *f* | click kitty *f* | follow released (FR-011) |
| on, following *f* | click kitty *k* ≠ *f* | following *k* |
| any, following *f* | click anything not a kitty | follow released (FR-026) |
| any, no follow | click anything not a kitty | nothing |
| any, following *f* | *f* leaves the roster | follow released (FR-020) |

Two readings of the rules had to be settled to make this table total, and both
are decisions taken here rather than restatements of the spec:

**The release gestures are not conditioned on camera mode.** FR-026 says
releasing leaves camera mode on, which reads as a precondition but is a
statement about what release does *not* change. Making release work whenever a
follow exists gives one rule instead of a mode-conditional pair, and it has
visible feedback in either mode because of the decision below.

**The card marking shows a dormant follow.** FR-017 does not condition the
marking on camera mode, and showing it while the camera is off is the more
honest of the two options: it makes the stored follow visible, and it explains
in advance what the toggle is about to do. Hiding it would mean toggling camera
mode on produces a jump to a kitty the viewer had no way to know was still
selected. This is the one place the plan chooses a user-visible behaviour the
spec left open, and it is cheap to reverse.

---

## The transform, both directions

Derive the inverse from the forward transform in code rather than writing it
twice. Two independently-written transforms drift, and the symptom is clicks
landing on the wrong kitty only at certain zooms.

**Frame geometry.** With aim `(ax, ay)` in world tiles and width `across`:

```
left = clamp(ax - across / 2,  0,  world.width  - across)
top  = clamp(ay - across / 2,  0,  world.height - across)
tile = mapCssWidth / across
```

**The clamp is a decision, not a detail.** Without it, following a kitty at the
world's edge shows several tiles of void, which reads as a rendering fault. With
it, an edge kitty sits off-centre but every pixel is meadow. The world is 20
tiles and the frame is 10 to 15, so the clamp is active often rather than
rarely. It does not conflict with SC-005: the *anchor* is still a kitty, and the
clamp is a later step that may offset the frame's centre from the anchor.

**Forward** — applied once per frame in the renderer, then all existing drawing
code runs untouched:

```
renderer.tile = tile                      // scale  (research R1)
ctx.translate(-left * tile, -top * tile)  // pan    (research R1)
```

**Inverse** — for hit testing. `rect` is the canvas's measured
`getBoundingClientRect()`, which is not `cssWidth`: `resizeFor` applies a display
scale, so the canvas's layout size and its drawing size differ.

```
cssX    = (clientX - rect.left) * (cssWidth / rect.width)
worldX  = left + cssX / tile
```

**Hit test.** Take the frontmost kitty — the last in the renderer's depth sort —
whose drawn position lies within the hit radius of the world point. The radius
is `max(0.5 tiles, floorPx / tile)`, so a kitty stays tappable at the zoom
ceiling on a phone where she is roughly 23px. Anything else, including elements
and decoration, is "not a kitty" and releases.

---

## What the ground and pond caches key on

Recorded here because the camera changes what invalidates them, and because one
of them is currently keyed on a subset of its inputs.

| Cache | Keyed on today | After this feature |
|---|---|---|
| `groundCache` | dpr + `canvas.width` | unchanged, plus `bakeTile` |
| `pondCache` | water tile positions only | **plus `bakeTile`** — see below |

`pondCache` is built at `this.tile` and at canvas pixel size but keys on neither.
It is safe today only because `resizeFor` nulls it on canvas resize, and every
way the tile can change today goes through a resize. The camera changes the tile
with no resize, so the guard would never fire and ponds would silently draw at
the previous tile's geometry. Adding `bakeTile` to the signature closes it.

Both caches bake at `bakeTile` — the tile at the narrowest frame, the largest
the camera can ask for — so every per-frame blit is a downscale and camera
movement triggers no rebake at all (research R2).
