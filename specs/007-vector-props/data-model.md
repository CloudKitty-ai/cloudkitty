# Data Model: Vector Props — Retire the Remaining Emoji

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

All presentational, page-local — nothing serialized, nothing served, no new
wire fields. Served types are consumed as-is; see
[contracts/props-contract.md](./contracts/props-contract.md) for the exact
fields each prop reads.

## PROPS palette (props.js)

The curated, named color block all props draw from (FR-012) — world-adjacent
hues so one hand appears to have drawn everything:

| Name | Role |
|------|------|
| `bowlClay`, `bowlRim` | terracotta pair (kin to the existing kibble-brown) |
| `kibble` | the mound dots |
| `ink` | outline/Z/icon stroke tone (kin to the world's `--ink`) |
| `blush` | the heart (kin to the cats' nose pinks) |
| `soap` | bath bubbles (kin to the water rim blue) |
| `shadow` | the butterfly's detached ground shadow |

## BUTTERFLY_COLORWAYS (props.js)

Three curated entries — `{ name, wing, wingShade, body }` — in hues absent
from the rest of the world: soft lavender, pale lemon, peachy-white.

- Derivation: `butterflyColorwayFor(elementId) =
  BUTTERFLY_COLORWAYS[elementId % 3]` — pure and total; stable for the
  element's lifetime, across frames, reloads and restarts (FR-005).
- Validation (gallery + headless): pairwise distinguishable at 22px; the
  derivation is deterministic and covers every id.

## The prop draw family (props.js)

Named functions, one per prop — same unit-box, outline-first, `fine = size
>= 44` conventions as `drawCat`:

| Function | Options | Notes |
|----------|---------|-------|
| `drawBowl` | `servings`, `size`, `x`, `y` | mound of dots maps servings (visual clamp 5); `0` = empty bowl, still drawn; fish decal at fine |
| `drawButterfly` | `colorway`, `phase`, `agitated`, `size`, `x`, `y` | wings flap by width-scale on the flap cycle; `agitated` multiplies flap rate by `VIEW.props.panicMultiplier`; hover-bob offset + non-bobbing detached shadow; antennae at fine |
| `drawGreebleWisp` | `face` (`'blank'\|'grin'`), `phase`, `size`, `x`, `y` | teardrop + wavy skirt + hollow eyes; softer dashed outline (named dash pattern, reset after); caller applies the existing 0.55 alpha and `showGreebles` gate |
| `drawSleepZs` | `phase`, `size`, `x`, `y` | three rounded Zs, staggered, drifting up + fading on phase; static ladder at phase 0 |
| `drawHeart` | `phase`, `size`, `x`, `y` | plump heart, blush, one highlight; scale pulse on phase |
| `drawNeedIcon` | `need`, `size`, `x`, `y` | dispatch: eat→mini bowl (reuses `drawBowl`, fixed mound), drink→drop, sleep→Zs (static), play→yarn ball, cuddle→heart (static), bath→three glinting soap bubbles |

## Prop state mapping (render.js consumes, never invents)

| Prop | Served evidence | Rule |
|------|-----------------|------|
| Bowl mound | `element.servings` | mound size = clamp(servings, 0..5); meter deleted |
| Butterfly colorway | `element.id` | `butterflyColorwayFor(id)` |
| Butterfly agitation | any `kitty.pursuit.target` naming this element | `agitatedIds` set derived once per frame from `curr`; sustained while present (pursuit-face precedent) |
| Greeble wisp visibility | debug toggle only | unchanged gate, unchanged 0.55 alpha (FR-007) |
| Sleep Zs | `kitty.activity.state == "sleeping"` | replaces the 💤 emoji at the same anchor |
| Heart | cuddle partner present (existing rule) | replaces 💗 at the eased midpoint |
| Thought icon | the long-wanted need (005 FR-012 machinery) | `drawNeedIcon(need)` replaces `NEED_ICONS[need]` |

## VIEW additions (anim.js — FR-012)

`VIEW.props`, frozen with the rest: `flapPeriodMs`, `panicMultiplier`,
`bobPeriodMs`, `bobAmplitude`, `wispBobMs` (the greeble wisp's slower
bob), `heartPulseMs`, `zDriftMs` (+ any dash pattern named in `props.js`
as a const). No inline literals in drawing or render code.

`viewAt` gains `propPhaseFor(id, periodMs)`: a wall-clock phase over the
named period, seeded by `id` — which may be an **element or kitty id**
(analyze remediation U1: the Zs and heart are kitty-anchored, so the one
phase source serves both worlds; the heart uses the drawn kitty's own id,
so a cuddling pair shares no state). Returns `0` when `still`, so reduced
motion gets static props with full state (FR-013) through the same
one-draw-path rule as everything else.

## Gallery states matrix (US1)

What the props section must show, each at 22px and 88px:

- Bowl at servings 5 / 3 / 1 / 0
- Butterfly: all three colorways × two flap positions (+ one agitated
  sample at 88px)
- Greeble wisp: **both faces side by side** at the in-world alpha — the
  gate decides (recorded in gallery-approval.md)
- Sleep Zs (static ladder), heart, and all six thought icons at their
  bubble scale

## Deleted

`render.js`: the `emoji()` helper, `NEED_ICONS` emoji map, the chow meter
bars, and the `🍥 🐛 👻 💤 💗` call sites — after which no `fillText` of an
emoji glyph exists on the world-canvas draw path (FR-010, structurally
checkable).
