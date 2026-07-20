# Data Model: Graphics Refresh — Vector Cats & Animation

**Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Everything here is **presentational, page-local state** — none of it is
serialized, sent to the server, or read by the simulation. Served types
(`WorldSnapshot`, `Kitty`, `Config`) are consumed as-is; see
[contracts/viewer-contract.md](./contracts/viewer-contract.md) for the exact
served fields each visual reads.

## CatAppearance (cat.js)

The per-kitty visual identity (FR-003).

| Field | Type | Notes |
|-------|------|-------|
| `furBase` | color | main coat fill |
| `furShade` | color | darker companion (outline tint, shading) |
| `pattern` | `{ kind, color }` | `kind ∈ {solid, tabby-stripes, patches, tuxedo-mask, point-mask}` |
| `eyeColor` | color | |
| `noseColor` | color | |

- Derivation: `appearanceFor(id) = PALETTES[id % PALETTES.length]` — pure and
  total; every u32 id maps to an appearance, identical across sessions.
- Validation (gallery-checked): `PALETTES.length ≥ 6`; the first three
  entries pairwise distinguishable at 22px (SC-001/SC-003).
- Future: `appearanceFor` is the single override point when served
  appearance data exists (P2 backlog item); callers never index `PALETTES`
  directly.

## Pose (cat.js)

A named static body configuration — the shared vocabulary of gallery and
live view (FR-001, FR-007).

`POSES`: `idle` (standing — the sitting pose is deliberately skipped for
now, spec clarification 2026-07-19), `walking`, `pouncing` (anticipation +
squash-and-stretch keyed by `phase`), `eating` (head down), `drinking`
(head down + lap), `grooming` (head to flank), `loaf` (resting),
`sleep-curl` (+ breathing via `phase`). Each pose is a parameter set the
drawing primitives consume — no per-pose drawing code forks.

Pose selection (pure function of one served kitty + its position delta):

| Served evidence (priority order) | Pose |
|---|---|
| `activity.state == "sleeping"` | `sleep-curl` (held; transition beat plays only on the tick it begins) |
| `activity.state == "resting"` | `loaf` |
| `activity.state == "eating"` / `"drinking"` / `"grooming"` | matching pose |
| `last_action.action == "play"` or `"chase"` | `pouncing` |
| position changed this pair | `walking` |
| otherwise | `idle` |

## Facing (anim.js, per kitty)

| Field | Type | Notes |
|-------|------|-------|
| `facing` | `"left" \| "right"` | last horizontal component of movement; unchanged when movement is purely vertical or absent (FR-004) |

Transitions: derived from served position deltas only. Initial value:
`"left"` (named default). Survives across ticks; reset only on
discontinuity rebuild.

## BeatStore (anim.js, per kitty)

Short-lived presentational state derived **once per frame arrival** by
diffing `prev → curr` (R5), cleared wholesale on discontinuity.

| Field | Type | Trigger (served evidence) | Lifetime |
|-------|------|--------------------------|----------|
| `oneShot` | `{ kind, t0, duration } \| null` | `sad-beat`: new entry in `abandoned_chases` · `relief-sparkle`: any need dropped ≥ `VIEW.reliefSparkleDrop` · `plaything`: `last_action` is targetless play | one slot; newest wins; expires at `t0 + duration` |
| `fellAsleepAt` | tick \| null | `activity.state` became `"sleeping"` | until state leaves sleeping (gates the fall-asleep transition vs held curl) |

Speech-bubble pop-in is deliberately **not** a beat: it is derived in the
juice layer (US6) from `meow.tick == curr.tick` (a meow stamped with the
newest closed tick is new) eased on the progress clock — self-contained, so
US6 truly depends only on US3 (analyze remediation I2).

Sustained overlays are *not* stored — they are pure functions of `curr`:

| Overlay | Served evidence | Rule |
|---------|-----------------|------|
| focused eyes | `pursuit` present | shown while present |
| thought bubble | max `(tick − distress_since[need])` ≥ patience threshold | at most one (longest-running need); icon = need; gone when resolved |

Layering (documented rule for "two beats at once"): base pose ← action
animation ← eye/expression overlay ← the single `oneShot` particle ←
speech bubble ← thought bubble. One occupant per layer; no flicker.

## StatePair + InterpolatedFrame (anim.js)

| Field | Type | Notes |
|-------|------|-------|
| `prev`, `curr` | served `WorldSnapshot` | the two newest states; `prev == null` at first paint |
| `currArrivedAt` | DOMHighResTimeStamp | wall-clock arrival of `curr` |
| `generation` | integer | bumped on reconnect and hidden→visible; pairs across a bump are discontinuous |
| `tickMs` | number | from `config.world.tick_ms`; stand-in `VIEW.tickMsFallback = 800` |

**InterpolatedFrame** (computed per rAF, never stored): for each kitty,
`pos = lerp(prevPos, currPos, ease(progress))` where
`progress = min(1, (now − currArrivedAt) / tickMs)` — clamped, never
extrapolating (FR-005/FR-019); plus pose, facing, overlays, active oneShot
with its own local progress. Elements: position always from `curr`;
spawn/expiry fade via presence diff. Bars: eased by the same progress.

**Discontinuity** (any of → snap + clear BeatStores, R4):
first paint · `generation` changed · `curr.tick ≠ prev.tick + 1` · kitty id
set changed · a kitty moved >1 tile on either axis. Per-element: critters
moving >2 tiles don't ease (they fade-step).

## ViewerConfig (app.js)

| Field | Source | Stand-in (named) |
|-------|--------|------------------|
| `tickMs` | `config.world.tick_ms` | `VIEW.tickMsFallback = 800` |
| `distressPatienceTicks` | `config.viewer.distress_patience_ticks` | `VIEW.distressPatienceFallback = 60` |

Fetched once at start (existing pattern); failures keep stand-ins; no new
served keys (FR-018).

## VIEW tunables (anim.js, frozen object — FR-017)

One named home for every new number: easing curve + duration scale, idle
motion frequency/amplitudes, per-beat durations, `reliefSparkleDrop = 15`,
particle sizes, ambient amplitudes and per-effect enable flags
(`waterShimmer`, `sunbeamPulse`, `dustMotes`, `grassSway`, `cloudShadows` —
FR-013), fade durations, the two stand-ins above. No inline literals in
drawing or animation code.

## Mode flags (anim.js)

| Flag | Source | Effect |
|------|--------|--------|
| `reducedMotion` | `matchMedia('(prefers-reduced-motion: reduce)')`, live | rAF never runs; draw once per WS frame, static poses, no one-shots/idle/ambient; sustained informational cues still drawn; panel CSS transitions off (FR-015) |
| `hidden` | `visibilitychange` | rAF cancelled; WS stays open; on return bump `generation` and resume (FR-016) |
