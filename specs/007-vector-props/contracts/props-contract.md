# Props Contract: Vector Props

**Base contract**: [005 viewer-contract.md](../../005-graphics-refresh/contracts/viewer-contract.md)
— every pure-view rule there (render only what was served, never
extrapolate, newest wins, send nothing, snap across discontinuities)
carries over unchanged and governs this feature too.

This feature changes **no wire surface**: no new endpoints, fields, or
requests. The contract is, as in 005, about what the viewer may do with
served data — plus the specific continuity promises this feature makes.

## Served field → prop mapping

| Prop / behavior | Served evidence | Notes |
|-----------------|-----------------|-------|
| Bowl + kibble mound | `element.kind == "chow"`, `element.servings` | the mound *is* the servings display; 0 draws an empty bowl (FR-004) |
| Butterfly drawing | `element.kind == "bug"` | "bug" remains the wire name; butterfly is presentation (spec assumption) |
| Butterfly colorway | `element.id` | `id % 3` over three curated colorways; stable per individual (FR-005) |
| Butterfly panic flap | any `kitty.pursuit.target == {element, id}` in the newest state | sustained while served, recomputed per frame, no store (FR-006) |
| Greeble wisp | `element.kind == "greeble"` + the debug toggle | drawn only under the toggle, at the existing alpha — behavior unchanged (FR-007) |
| Sleep Zs | `kitty.activity.state == "sleeping"` | same anchor as the emoji it replaces (FR-008) |
| Heart | the existing cuddle-partner rule | same eased midpoint (FR-008) |
| Thought icons | the 005 thought-bubble machinery (`distress_since` + served patience) | icon becomes a drawn mini-prop; threshold logic untouched (FR-009) |
| Critter glide | `element.pos` in the two newest states | eased like kitty motion for moves ≤ 2 tiles; spawns and larger jumps snap (post-approval refinement, 2026-07-20 — the hover-bob alone left hops jerky) |
| Hover/flap/pulse/drift phases | local animation clock via the view layer | `propPhaseFor(id, periodMs)` over element *or* kitty ids — 0 under reduced motion / still frames (FR-013) |

Absence of any optional field renders normally with no effect — unchanged
from 005.

## Continuity promises

- **Greeble secrecy**: what changed is how the greeble looks, never when
  it is shown. Toggle key, default-hidden state, translucency: identical.
- **The imaginary plaything stays the star** (005 FR-009 / 007 FR-011):
  with real butterflies in the world, the solo-play conjured plaything
  remains the golden twinkling star and shares no silhouette with any real
  prop.
- **Zero emoji on the world canvas** (FR-010): after this feature the
  world-canvas draw path contains no platform emoji glyphs — structurally
  enforced by deleting the `emoji()` helper. The panel's prose emoji are
  out of scope and unchanged.
- **Reduced motion** (FR-013): every prop animation stops (flap, bob,
  pulse, drift); every prop *state* (mound level, colorway, wisp under
  toggle, icons) remains fully readable. Informational content is never
  motion-gated.
- **Older servers** (FR-014 / SC-007): props consume only fields every
  server since 001/004 serves (`kind`, `servings`, `id`, `pursuit`,
  `activity`, `distress_since`); the feature degrades not at all against
  any of them, and ships an empty diff outside `client/` and `specs/`.
