# Phase 1 Data Model: Camera zoom targets

No stored state. This feature changes arithmetic that already runs once per
frame; 036's two `localStorage` keys are untouched.

---

## Dials: what changes

| dial | today | becomes |
|---|---|---|
| `nominalAcross` | 10 tiles | **gone** — replaced by `floorPx` |
| `ceilingFactor` | 1.5× the floor | **gone** — replaced by `ceilingPx` |
| `floorPx` | — | 100. The tile size the camera zooms in to. |
| `ceilingPx` | — | 50. The smallest tile it will widen to. |
| `ceilingRows` | — | 6. The most world-ROWS the ceiling may frame, and the only limit stated on the vertical. **Binds only where `aspect < 1`** — a letterboxed canvas, i.e. a phone held sideways. Added 2026-08-20. |
| `minTiles` | — | 7. The fewest tiles the floor may frame. **6 as shipped in #246; raised 2026-08-19** so the phone frames more meadow. |
| `fitMarginTiles` | 2.6 tiles | unchanged, and still in tiles (research R5) |
| `aimDeadzoneTiles` | 1.5 tiles | unchanged, and still in tiles (research R5) |
| `hysteresis`, `panRate`, `zoomRate`, `maxFrameMs`, `hitRadiusFloorPx` | — | untouched |

---

## The sizing arithmetic

Computed once per frame, from `cssWidth` and the world:

```
floorTiles   = max(minTiles, cssWidth / floorPx)
ceilingTiles = min(cssWidth / ceilingPx, world.width - epsilon)
across       = clamp(fit, floorTiles, ceilingTiles)
```

`fit` is 036's bounding box plus `fitMarginTiles`, unchanged. The renderer then
computes `tile = cssWidth / across` exactly as it does today, which is why
nothing downstream of the tile changes.

**Three properties fall out, and each is a success criterion:**

- **The zoom range is `floorPx ÷ ceilingPx`** — a constant 2.00×, on every
  viewport where neither clamp binds. SC-004 asserted this and was withdrawn; it
  is still true, and still worth recording as a number.
- **Every tile the camera can draw lies in `[ceilingPx, floorPx]`.** This used to
  be how detail was kept from flickering. Since 2026-08-18 there is no threshold
  to flicker across, and the band's lower end rests on the 47px portrait cards
  instead (SC-003).
- **`floorTiles ≤ ceilingTiles` must hold.** With `floorPx > ceilingPx` it does
  wherever the minimum does not bind; where it does, the two can meet on a very
  small viewport and the camera simply has no zoom range. It must never invert.

---

## What each clamp costs, and where

| clamp | binds on | costs |
|---|---|---|
| `minTiles` | small viewports (map < `minTiles × floorPx`) | apparent size and zoom range — pinch zoom is the accepted answer |
| world edge | large viewports on a 20-tile world | zoom range only; Fog removes it |
| `MAP_MAX_PX` | viewports past the 1200px map cap | nothing — the map stops growing, so the camera behaves as it does at the cap (research R8) |

---

## What 036 keeps

Everything that is not the two limits. Named explicitly because a plan that
touches the camera's core arithmetic is where they would get disturbed by
accident:

- the fit from the bounding box, and `fitMarginTiles`
- the anchor, its centrality rule and its hysteresis
- the aim deadzone
- the centre-of-mass aim below the ceiling, and the anchor aim once it binds
- the frame-rate-corrected easing, and the still-frame hold
- the world clamp (036 FR-029), following, persistence and the card mark

The `bound` predicate — which decides when the anchor takes over from the centre
of mass — must compare against **the same ceiling the fit is clamped to**. It
reads a recomputed number rather than a dial, and if the two ever disagree the
anchor takes over at a width the camera never actually reaches.
