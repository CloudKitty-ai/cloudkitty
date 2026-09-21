# Research: teacher sleep rule reads the floor

No NEEDS CLARIFICATION markers existed; this file records the three
implementation decisions the code reconnaissance settled.

## D3 — the substitution point is `scored()`'s pressure binding

- **Decision**: in `selection.rs::scored()` the sleep pressure binding
  becomes the effective pressure — `max(need − floor, 0)` when
  `kind == Sleep` and no warm option is in play — and the existing
  formula is otherwise untouched. Because `urgency` is derived from
  the `pressure` variable (line 106), the urgency term shifts with it.
- **Rationale**: one substitution point, smallest diff, and honest:
  urgency is urgency about relief the cat can actually get. At floor 0
  the binding is bit-for-bit today's (`need − 0 = need`), so FR-004
  holds with zero arithmetic reordering. Keeping urgency on the raw
  need would need a second variable and would score panic about
  relief that cannot arrive.
- **Alternatives considered**: (a) raw-need urgency + floored pressure
  — rejected, two bindings and a nudge-shaped inconsistency; (b) a
  separate sleep-score function — rejected, duplicates the formula
  the module keeps in one place.
- **Constitution note (Article I)**: above the safeguard threshold
  (75) the world guarantees a reachable sleep resource, so the floored
  branch describes low-stakes pressure only; SC-003's
  zero-distress-crossings bound is the check.

## D4 — the warm-option predicate composes three existing helpers

- **Decision**: `warm_option_in_play(ctx)` =
  standing on a Sunbeam (`world.element_at(me.pos)`) OR
  `warm_friend_beside(ctx).is_some()` (T092/spec 031 conduction) OR
  `sunbeam_worth_walking(ctx).is_some()` (priced reach ≤
  `sunbeam_reach`). One helper, used by the score; `pursue`'s arm is
  unchanged (it already walks only when these hold).
- **Rationale**: FR-002 verbatim; every input observation-derived or a
  global constant (doctrine rule 5). The cuddle-gated cosleep walk
  (spec 028 FR-020) is deliberately NOT a warm option: a plain-tile
  cosleep relieves sleep only to the floor (031 conduction requires
  the beam), and cosleep routing is out of scope — the cuddle need
  scores that walk, not sleep.
- **Alternatives considered**: folding the check into
  `sleep_travel_distance` — rejected, that function prices distance,
  not relief, and the score must not conflate them.

## D5 — zero pressure skips the need, gated exactly like the engine

- **Decision**: when the floor is active (`floor > 0.0`), no warm
  option is in play, and the effective pressure is 0, the sleep score
  returns `None` — the need is skipped this tick, the module's
  existing "a skipped need is skipped under every configuration"
  shape. Gate mirrors `action.rs:925`
  (`warm || floor <= 0.0 || relief > 0.0`).
- **Rationale**: FR-003's "MUST NOT begin a scene when nothing
  competes" cannot ride on scoring alone — a zero score can still be
  the maximum when everything else is quiet. `floor > 0.0` in the gate
  keeps floor-0 behavior byte-identical even at need 0 (today's code
  path for a zero need is preserved untouched).
- **Alternatives considered**: score 0.0 and rely on competition —
  rejected, fails FR-003 scenario 2; a new "resting idle" state —
  rejected, FR spec says fall through to existing idle/wander.
