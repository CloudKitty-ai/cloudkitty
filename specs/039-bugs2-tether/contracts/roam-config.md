# Contract: the roam-cell configuration surface

The tether's one external interface is the world configuration file.
This contract is normative for the config key; the spec's FRs are
normative for behavior.

## Key

```toml
[elements.bug]
roam_cell = 4        # optional; absent = unbounded (pre-039 behavior)
```

- **Type**: positive integer, cell edge length in tiles.
- **Legal values**: `n ≥ 2`. Values exceeding either world dimension
  are legal (the whole world becomes a single cell in that dimension).
- **Refused at load, with field and value named**:
  - `0` or `1` — a one-tile cell silently immobilizes every bug,
    which is a different world than anyone asked for.
  - `roam_cell` on any `[elements.*]` table other than `bug` — the
    engine refuses what it will not honor. Greebles are free-range by
    ruling; there is no greeble tether to configure.
- **Absent**: bugs roam the whole world exactly as before this spec —
  byte-identical evolution from a fixed seed (spec SC-002 pins it).

## Partition semantics

- Cells are axis-aligned, anchored at the world origin: tile (x, y)
  belongs to cell (x ÷ n, y ÷ n) (integer division).
- Interior cells are n×n. When a world dimension is not a multiple of
  n, the far edge holds remainder cells of the leftover width/height
  (26×26 at n=4: 4×4 interior, 4×2 and 2×4 edge strips, one 2×2
  corner). Every tile belongs to exactly one cell.
- A bug never occupies a tile outside the cell containing its current
  position; equivalently, its birth cell (or, for a bug loaded from a
  pre-039 save, the cell it stood in at load) is its cell for life.
- A movement draw whose destination lies outside the cell costs the
  step — identical in kind to a step lost to occupancy. No redraw, no
  compensation, no cadence change.

## Interaction with existing keys (unchanged semantics, restated)

- `ttl` — unchanged mechanics; the served package raises bug and
  greeble lifetimes to 600. `ttl_jitter` applies as today.
- `min`/`max` — unchanged; `min` remains the real population knob.
- Spawn placement (`spread_candidates`, `edge_penalty`) — unchanged;
  a bug's cell is derived from wherever its spawn lands.

## Served package (adopted in the same merge, per clarification 2026-08-21)

```toml
[elements.bug]
min = 3
max = 7
ttl = 600
roam_cell = 4

[elements.greeble]
min = 1
max = 3
ttl = 600
```

The merge carrying this package is gated on Experiments'
pre-registered acceptance grid passing against a build of this branch
(spec SC-004); the deploy to the served box is a separate owner-gated
act.
