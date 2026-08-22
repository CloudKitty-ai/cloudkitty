# Data Model: Bugs 2.0 — the roam-cell tether

The arc's defining property is how little data it adds: one derived
concept, one optional config field, zero persisted state.

## Roam cell (derived, never stored)

- **What**: an axis-aligned region of the world grid. For cell size N,
  the cell of tile (x, y) is the quotient pair (x / N, y / N),
  anchored at the world origin.
- **Identity**: the quotient pair. Every tile maps to exactly one
  cell; interior cells are N×N; when width or height is not a
  multiple of N, the far-edge strips form smaller remainder cells
  (e.g. 26×26, N=4 → 4×4 interior, 4×2 / 2×4 / 2×2 remainders); a
  dimension smaller than N is a single strip.
- **Lifecycle**: none. Not a struct, not persisted, not serialized,
  not visible in any payload — a predicate over positions
  (`same_roam_cell(a, b, n)`), computed on demand in the environment
  phase.
- **Relationships**: constrains Bug movement only (FR-004). No other
  element type, no kitty, no observation reads it.

## ElementRule (config) — one new optional field

- **Field**: `roam_cell: Option<u32>`
  - serde: `default`, `skip_serializing_if = "Option::is_none"`
    (stamp neutrality, research D5)
  - Absent/`None`: unbounded roaming — today's behavior exactly
    (FR-009)
  - `Some(n), n ≥ 2`: bugs confined to cells of size n; values larger
    than the world are legal (whole world = one cell)
- **Validation** (config load, named errors per house shape):
  - `Some(0)` / `Some(1)` → refused: "[elements.bug] roam_cell" with
    the value (a 1-cell tether immobilizes every bug)
  - Set on any element type other than bug → refused, naming the
    offending table (e.g. "[elements.greeble] roam_cell"): the engine
    refuses what it will not honor (research D3)
- **State transitions**: none — config is load-time; a running world
  re-reads nothing.

## Served configuration values (cloudkitty.toml)

| Table | Key | Before | After |
|-------|-----|--------|-------|
| `[elements.bug]` | `roam_cell` | (absent) | `4` |
| `[elements.bug]` | `ttl` | `300` | `600` |
| `[elements.greeble]` | `ttl` | `300` | `600` (symmetry ruling 2026-08-21) |

## Explicitly unchanged (the load-bearing negatives)

- **Element struct** (element.rs): no new fields; a bug's cell is
  implied by `pos`. Snapshot schema untouched; pre-change saves load
  and their bugs adopt the tether at load position (FR-007).
- **Save-compatibility fingerprint**: width/height/seed/kitty-ids
  only — this arc touches none of them.
- **`engine_defaults_sha256`**: unchanged by D4 (defaults keep 300) +
  D5 (skip-if-none); pinned stamp test guards it.
- **Observation/action/mask schemas, reward values, scripted
  behaviors, cat decision rules**: byte-frozen (FR-008); the
  acceptance grid's skill rows depend on the scripted rulers not
  moving.
- **RNG stream shape**: one direction draw per moving bug per moving
  tick, tether or no; outward draws lose the step, never redraw
  (FR-003, research D2).
