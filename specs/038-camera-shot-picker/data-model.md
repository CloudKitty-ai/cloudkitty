# Data Model: Camera shot picker (Phase 1)

All entities are view-side, per-session, never persisted, never serialized,
never sent (Constitution V). 036's two persisted keys (camera mode, follow
id) are the only camera storage and are unchanged.

## Group *(per-tick reading, immutable)*

Derived fresh each tick from drawn kitty positions.

| Field | Type | Notes |
|---|---|---|
| `members` | kitty ids | connected component at `linkTiles` (research D3) |
| `bbox` | {minX, minY, maxX, maxY} | of drawn centres (`pos + 0.5`) |
| `widthNeeded` | tiles | `max(spanX, spanY/aspect) / (1 - 2·fitMarginFrac)` |

No identity of its own — identity is the Chain's job.

## Chain *(persistent across ticks)*

The continuity of a group over time; the unit dwell evidence attaches to.

| Field | Type | Notes |
|---|---|---|
| `members` | kitty ids | this tick's group |
| `nearTicks` | int | consecutive ticks admissible-near (disjoint from shot, union fits) |
| `farTicks` | int | consecutive ticks strictly-bigger far rival |

**Matching rule**: a group continues a chain iff they share ≥ half of the
larger's members (research D5); an unmatched chain dies (counters discarded);
an unmatched group starts a fresh chain. A chain that stops qualifying for a
counter's condition resets that counter to 0.

**State transitions**: fresh → counting (near or far, mutually exclusive by
geometry) → consumed (admitted at `nearDwellTicks` / pan target at
`farDwellTicks`) or reset.

## Shot *(the incumbent subject)*

| Field | Type | Notes |
|---|---|---|
| `members` | kitty ids | union of its groups' members; drifts kitty-by-kitty |
| `fitWidth` | tiles | widthNeeded of the member set, clamped to `limitsFor` |
| `overflow` | bool | true when unclamped widthNeeded > ceiling (FR-007a mode) |

**Lifecycle** (once per tick, in order — contracts/shot-grammar.md §2):
follow-pin → membership follow → shed if unfit → break if <2 (group mode) →
admissions → far-rival pan. Ties keep the incumbent; cold start takes the
maximal-count window, lowest-id tiebreak (research D6).

## Episode *(one at a time; the only mover of the camera)*

| Field | Type | Notes |
|---|---|---|
| `kind` | correction \| widen \| shed \| break \| pan | precedence in research D9 |
| `from` / `goal` | {aimX, aimY, across} | LATCHED at start; goal exact, snapped to on arrival |
| `startedAt` / `duration` | ms | cubic ease-in-out on `t = elapsed/duration` |
| `committed` | bool | true only for pan: runs to completion, no re-latch (FR-013) |

**States**: REST → (trigger) → EASING → (t ≥ 1: snap to goal, exact) → REST.
Reduced motion: duration 0 (arrive). `view.still` frames: no progress (same
moment). Non-pan episodes may re-latch once per new trigger; each re-latch
counts as an event for SC-003.

## Evidence window *(the 032 seam)*

Today: the chains' counters, accumulated over lived ticks — one function
(research D10) consumes per-tick chains and yields `{nearTicks, farTicks}`
per chain; thresholds compared outside it. Under spec 032: same signature
reading the lookahead buffer. No other code knows which direction time runs.

## Removed

`anchorFor` + `hysteresis` (research D11), `fitMarginTiles` (D4),
`panRate`/`zoomRate` (D7). `anchorId` survives as followed-id-or-null.
