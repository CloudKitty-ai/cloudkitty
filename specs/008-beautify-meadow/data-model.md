# Data Model: The Meadow Itself — Beautification II, Step 2

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Everything here is presentational. No entity below exists on the wire, in a
snapshot, or in the engine — each is derived in the viewer from position,
served elements, or served kitty movement (research R2/R4/R6).

## Derived entities

### MeadowTile (derived, per tile, stateless)

| Field | Type | Derivation | Rule |
|---|---|---|---|
| `tone` | index into `MEADOW.grassTones` | `tileHash(x, y)` remixed with the tone salt | 3–4 close greens (`VIEW.meadow.toneCount`); adjacent equal tones are fine — variety comes from the mix, not alternation |
| `jitter` | small alpha tint | hash remixed with the jitter salt | amplitude `VIEW.meadow.jitterAlpha`, barely visible (FR-001) |
| `flora` | none \| tuft \| clover \| flower | hash remixed with the flora salt vs `VIEW.meadow.floraDensity`; kind + sub-tile offset from further remixes | sparse; drawn into the ground cache; never on a tile currently under a pond body (checked at cache build against nothing — flora is static, ponds are elements — so flora simply draws first and ponds paint over it) |

Stateless and identical on every reload/restart of any world (FR-002); no
storage anywhere (SC-001).

### Pond (derived, per contiguous water group, cached)

| Field | Type | Derivation | Rule |
|---|---|---|---|
| `tiles` | set of positions | 4-adjacency grouping of served water elements | membership is *exactly* the served water tiles (FR-006) |
| `signature` | string | sorted tile positions | cache key; shoreline rebuilt only when it changes |
| `outline` | `Path2D` | marching squares over `tiles`, corners rounded by `VIEW.meadow.shoreRounding` | no straight seams interior to the pond (SC-003); clipped nowhere — border ponds meet the edge frame cleanly |
| `lilyPad` | position \| none | present iff `tiles.size >= VIEW.meadow.lilyPadMinTiles`; placed by hash of the anchor (lowest x,y) tile | one per pond; stable across reloads |

Water spawn/expiry fades: a fading element renders as its own small rounded
pool at the element alpha (the pre-008 visual); the pond body always renders
the stable set (research R4).

### WorldEdge (derived, per world size, cached)

| Field | Type | Derivation | Rule |
|---|---|---|---|
| `frame` | fringe drawing | world width/height + `VIEW.meadow.edgeDepth` | wraps all four sides + corners; drawn into the ground cache; must never cover a kitty or prop — it decorates the outer margin of boundary tiles only (FR-007) |

### SunbeamGlow (derived, per served sunbeam element, per frame)

| Field | Type | Derivation | Rule |
|---|---|---|---|
| `center` | pixel point | element tile center | — |
| `radius` | px | `VIEW.meadow.glowRadiusTiles × tile` | bleeds past tile bounds (FR-008) |
| `alpha` | 0..1 | `VIEW.meadow.glowAlpha × element alpha × pulse` | pulse/motes are the existing 005 ambient, unchanged; overlaps blend by gradient accumulation, no compositing modes |

### WornPathTrace (session-local, in `Presentation`)

| Field | Type | Derivation | Rule |
|---|---|---|---|
| `heat` | number, 0..`VIEW.meadow.pathHeatCap` | +1 per kitty per continuous served tick on that kitty's tile | accumulates regardless of toggle state (visibility ≠ memory) |
| `stampedAt` | ms timestamp | time of last bump | decay applied at read: `heat × 0.5^((now − stampedAt)/pathHalfLifeMs)` |
| lifecycle | — | cleared wherever `Presentation` clears facing/one-shot memory | reload and every discontinuity start blank (FR-009); never serialized, never transmitted |

Read surface: `viewAt` exposes a decayed snapshot filtered by
`VIEW.meadow.pathVisibilityFloor`; the renderer draws it only while
`showPaths` is on.

## Renderer state (in the `showGreebles` mold)

| Flag | Default | Key | Footer note |
|---|---|---|---|
| `showGreebles` | `false` | `g` | existing, unchanged |
| `showGrid` | `false` | `l` | new — "press l for grid lines" hint + visible-state note |
| `showPaths` | `false` | `p` | new — "press p for worn paths" hint + visible-state note |

Fresh loads always start with all three off (FR-004, FR-009). Toggle keys
redraw immediately (the `g` pattern: flip flag, sync note, `anim.redraw()`).

## Named homes (Article VI)

- **`MEADOW` palette** (`client/meadow.js`): `grassTones[]`, `jitterTint`,
  `jitterShade`, `floraTuft`, `floraClover`, `floraPetal`, `floraCenter`,
  `pondWater`, `pondShallow`, `pondRim`, `lilyPad`, `lilyPadRim`,
  `edgeFringe`, `edgeFringeDeep`, `glowCore`/`glowMid`/`glowFade`,
  `pathTint`, `gridLine`.
- **`VIEW.meadow` tunables** (`client/anim.js`): layer flags (`scatter`,
  `ponds`, `edge`, `glow`, `paths`, `gridOverlay`) + `toneCount`,
  `jitterAlpha`, `floraDensity`, `shoreRounding`, `shoreWobble`,
  `lilyPadMinTiles`, `glowRadiusTiles`, `glowAlpha`, `edgeDepth`,
  `pathHeatCap`, `pathFullHeat`, `pathHalfLifeMs`, `pathVisibilityFloor`,
  `pathTintAlpha`. Display saturation (`pathFullHeat`) is deliberately
  separate from the memory cap (`pathHeatCap`) — gate revision 1.
- `TILE_COLORS` in `render.js` shrinks to surviving entries or retires.
