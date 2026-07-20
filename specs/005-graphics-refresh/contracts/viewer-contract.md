# Viewer Contract: Graphics Refresh

**Base contracts**: [001 http-api.md](../../001-cloudkitty-mvp/contracts/http-api.md),
[004 http-api-delta.md](../../004-fix-happiness-lockin/contracts/http-api-delta.md),
[006 http-api-delta.md](../../006-action-durations/contracts/http-api-delta.md).

This feature changes **no wire surface**: no new endpoints, fields, or config
keys, and no request the viewer didn't already make (`GET /world`,
`GET /config`, `WS /ws`). The contract here runs the other direction — it
pins down *what the viewer may do with served data*, so the pure-view
guarantee (Article V) stays auditable.

## The pure-view rules

1. **Render only what was served.** Every visual is a function of: the two
   newest served states, differences between them, `GET /config` values, and
   a local wall clock used solely for easing/beat phase.
2. **Never extrapolate.** Interpolation progress clamps at the newest state;
   a late next tick means the world holds still, never a predicted step.
3. **Newest wins** (FR-019). A newly arrived state preempts any in-flight
   animation; the viewer may cut or shorten a beat, never show state older
   than `prev`.
4. **Send nothing.** The viewer's outputs are pixels. (Unchanged, restated
   because animation state is new.)
5. **Snap across discontinuities.** First paint, reconnect, hidden-tab
   return, non-consecutive ticks, roster change, >1-tile kitty jump: render
   `curr` directly, clear presentational stores.

## Served field → visual mapping

Every new visual, with the exact fields it consumes. Absence of any optional
field renders normally with no beat (edge case: "absence of drama is not an
error").

| Visual | Served evidence | Notes |
|--------|-----------------|-------|
| Cat appearance | `kitty.id` | `PALETTES[id % len]`; stable across sessions (FR-003) |
| Facing | `kitty.pos` deltas between consecutive states | horizontal component only; kept while stationary (FR-004) |
| Glide | `kitty.pos` in `prev` + `curr`, `config.world.tick_ms` | eased ≤1-tile moves only (FR-005) |
| Pose | `kitty.activity.state`, `kitty.last_action`, pos delta | table in [data-model.md](../data-model.md#pose-catjs) (FR-007) |
| Idle motion | local clock only | never implies an action (FR-008) |
| Imaginary plaything | `last_action == {"action":"play"}` (no target) | visually unlike every real element kind; greeble rule untouched (FR-009) |
| Focused eyes | `kitty.pursuit` present | sustained while present (FR-010) |
| Sad beat | new entry in `kitty.abandoned_chases` vs `prev` | brief one-shot (FR-010) |
| Relief sparkle | any `kitty.needs[k]` drop ≥ `VIEW.reliefSparkleDrop` vs `prev` | brief one-shot (FR-011) |
| Thought bubble | `kitty.distress_since`, `world.tick`, `config.viewer.distress_patience_ticks` | same threshold as the panel cue; at most one; longest-running need (FR-012) |
| Kibble level | `element.servings` | replaces/extends the pip row (FR-014) |
| Bubble pop-in, bar easing | `world.recent_meows`, `kitty.happiness` | eased on the same clock (FR-014) |
| Ambient effects | none (local clock + element positions) | subtle, individually toggleable (FR-013) |

Explicit non-dependencies: `GET /events/activity` (exists since the 006
loose-ends work; deliberately unused here — no US needs it, and FR-018 keeps
the viewer independent of newer surfaces), `activity_clock` (poses come from
`activity.state` / `last_action`, which older servers also serve).

## Unchanged viewer obligations

- **Greeble secrecy**: greebles stay undrawn by default; the `g` toggle
  reveals them; chase-target narration keeps the secret. The refresh changes
  how things look, never what is shown or hidden.
- **Panel**: cards, bars, mood/doing/patience lines unchanged (cards keep
  their emoji face for now — spec assumption). The patience cue and the new
  thought bubble share one threshold value.
- **Reconnect loop**: unchanged (`/world` snapshot then `/ws`), now bumping
  the presentation `generation` so re-entry snaps.

## Accessibility / hygiene contract

- `prefers-reduced-motion: reduce` ⇒ motion-equivalent to the pre-005
  viewer: per-tick redraw, static poses, no continuous/idle/ambient motion,
  no one-shot particles; sustained informational cues (thought bubble,
  focused eyes, speech bubble text) still shown; all panel information
  unchanged (FR-015, SC-007).
- Hidden page ⇒ zero rendering work; return snaps to newest state (FR-016).

## Compatibility

- Works against any server version ≥ 001: no new served data is required;
  `world.tick_ms` and `viewer.distress_patience_ticks` both fall back to
  named stand-ins when unavailable (FR-018, SC-008).
- `gallery.html` requires no server at all (opens from disk); when a server
  runs, the existing static-file fallback serves it — again, no server
  change.
