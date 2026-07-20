# Meadow Approval — the FR-014 checkpoint (SC-008)

**Feature**: [spec.md](./spec.md) · [plan.md](./plan.md) | **Gate**: judged
live by the owner, all layers on and off, at two world sizes, before the
feature ships as the default view.

## Status: ⏳ PENDING

| Field | Value |
|---|---|
| Judged by | Elizabeth Kelly |
| Date | — |
| Demo worlds | 32×32 at http://127.0.0.1:8090 (`/tmp/meadow-demo.json`) · 64×64 run on request (port 8091) |
| Layers judged | meadow scatter · ponds/lily · world edge · sunbeam glow · worn paths (`p`) · grid overlay (`l`) |
| Revision rounds | — |
| Decisions | — |

## Revision log

*(recorded as they happen; loops touch `client/meadow.js` palette/tunables
only)*

- **Round 1 (2026-07-20)** — owner feedback: sunbeams, tone variation, and
  64×64 scaling approved as-is; grass detail and edge too sparse/odd;
  water indistinguishable from before; worn paths invisible.
  - *Worn paths*: root cause was display normalization by the memory cap
    (12) — one pass drew at 3% alpha. Added `pathFullHeat` (3) as the
    display saturation point, raised `pathTintAlpha` to 0.5, half-life to
    60s, bigger blobs. (`anim.js` normalization + tunables.)
  - *Water*: served water is mostly isolated single tiles, and a rounded
    single-tile "pond" looked like the old rounded square. Added
    deterministic shoreline wobble (`shoreWobble`, subdivided + hash-
    displaced) and a pale shallows band inside the shore (`pondShallow`,
    clipped inner stroke).
  - *Grass*: flora bigger (~1.6×), denser (0.06 → 0.13), weighted kinds
    (tufts common, flowers a treat), clover gained a stem, flowers now
    five-petaled.
  - *Edge*: one sparse blade row → continuous hem (baseline band + two
    dense staggered rows in two greens, `edgeFringeDeep`), depth 0.38.

- **Round 2 (2026-07-20)** — owner verdicts on revision 1: **worn paths
  and water approved**. Grass detail (flora) and the edge still not
  landing → **scrapped at the owner's call** and returned to BACKLOG.md
  for a proper art pass later. Code, tunables, palette entries, spec
  language, and tests for flora + edge all removed in the same change
  (Article VI: spec, code, and tests move together). What ships as the
  ground: tone-varied grass + brightness jitter (approved as "new
  tiles"), ponds, glow, paths, grid toggle. A 16×16 demo world (45px
  tiles) was added on port 8092 for the small-world look.

---

Nothing past this gate ships as the default view until this file says
**APPROVED**.
