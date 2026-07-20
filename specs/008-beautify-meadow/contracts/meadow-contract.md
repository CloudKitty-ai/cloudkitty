# Contract: Served Data ↔ Meadow Decoration

**Date**: 2026-07-20 | **Spec**: [../spec.md](../spec.md) | **Model**: [../data-model.md](../data-model.md)

The viewer-side contract for spec 008. The wire contract is **unchanged**:
this feature consumes only fields every current server already serves, and
sends nothing. Companion to 005's viewer-contract (animation rules) and
007's props-contract (prop mapping), both still in force.

## Inputs consumed (all pre-existing)

| Served field | Consumer | Use |
|---|---|---|
| `world.width`, `world.height` | ground cache, edge frame | meadow extent, fringe placement |
| tile coordinates (implicit) | `tileHash(x, y)` | all positional scatter |
| `world.elements[kind=water]` | pond layer | grouping, shoreline, lily pads; spawn/expiry fades per the 005 element-fade rules |
| `world.elements[kind=sunbeam]` | glow layer | center/alpha; pulse + motes unchanged (005 ambient) |
| `world.kitties[].pos` + tick continuity | worn-path memory | heat accumulation on continuous ticks only |

## Decoration mapping

| Visual | Source of truth | Never |
|---|---|---|
| Grass tone / jitter / flora per tile | `tileHash(x, y)` + `MEADOW` palette + `VIEW.meadow` | random per session; stored; served |
| Pond shape | exactly the served water tiles, 4-adjacent groups | invented water; a shoreline covering a non-water tile's center or missing a water tile |
| Lily pad | pond size ≥ `lilyPadMinTiles`, hash-placed | on tiny pools; moving between reloads |
| Edge frame | world dimensions only | covering a kitty or prop (outer margin only) |
| Sunbeam glow | served sunbeam elements | glow without a served beam; hard square edges |
| Worn paths | session-local heat from served kitty positions | persisted; transmitted; surviving a discontinuity |
| Grid lines | debug overlay behind `showGrid` | drawn by default |

## Unchanged rules (regression guards)

- **Pathing and interaction honesty (FR-006)**: which tiles are water,
  where kitties stop to drink, and every served behavior are byte-identical
  — the pond is a *redrawing* of the same tiles.
- **Element fades (005)**: spawning/expiring water and sunbeams keep the
  established fade-in/brief-bow behavior.
- **Ambient rules (005 US6)**: shimmer, sunbeam pulse, dust motes, grass
  sway, cloud shadows keep their flags and behavior, now over the new
  ground.
- **Greeble secrecy**: untouched; `g` behaves exactly as shipped.
- **Reduced motion (FR-012)**: static decoration (meadow, ponds, edge,
  glow, revealed paths, grid overlay) renders; decorative motion obeys the
  existing ambient stills; the path *overlay* is state, not motion, and
  remains available.
- **Discontinuity contract (005)**: the same events that snap animation
  (first paint, generation bump, tick gap, roster change, teleport) clear
  worn-path memory — one branch, one rule.
- **Toggle mold (`g`)**: `l` and `p` are window keydown toggles flipping a
  renderer flag, syncing a footer note, and redrawing; all default off on
  every fresh load.
- **Zero wire surface (FR-013)**: no new endpoints, requests, fields, or
  config; `crates/` and `cloudkitty.toml` diffs are empty.

## Determinism guarantee (SC-001/SC-002)

For any world dimensions and any tile `(x, y)`:
`tileHash(x, y)` — and every value remixed from it — is a pure function.
Reload, restart, and a different machine produce the identical meadow.
The only decoration that varies between sessions is the worn-path overlay,
which is *defined* as session memory and starts blank by contract.
