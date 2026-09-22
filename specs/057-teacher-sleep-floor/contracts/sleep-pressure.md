# Contract: the teacher's sleep pressure under a floor

The behavior contract Experiments reads against (their harness runs
the acceptance legs; this file is the promise the code keeps).

## The rule

At a decision point, for the scripted `needs_driven` teacher:

1. If a warm option is in play — the kitty stands on a sunbeam, a
   settled mutual partner is warm beside it (spec 031 conduction), or
   a sunbeam is within `sunbeam_reach` (priced) — the sleep score's
   pressure is the raw need. Identical to today on every input.
2. Otherwise the pressure is `max(need − sleep_floor_off_beam, 0)`,
   and the urgency term derives from that same value.
3. If additionally `sleep_floor_off_beam > 0` and the pressure is 0,
   sleep is skipped this tick: no sleep scene begins from the scored
   pass, and the teacher falls through to its existing behavior.

## Promises

- **P1 (floor-0 pin)**: with `sleep_floor_off_beam = 0`, every
  decision, action, and RNG draw is identical to the pre-057 binary
  on every seed and configuration. Checked by the spec 056 floor-0
  regression pin and the all-scripted cert leg on `anchor-b3.toml`
  vs `kitty-eval --brain needs_driven` (exact match).
- **P2 (no ban)**: a positive effective pressure competes normally; a
  kitty with nothing better to do still ground-naps (D2). Only
  zero-relief naps are skipped.
- **P3 (no new reads)**: inputs are the kitty's own need, tile
  contents, partner adjacency, priced beam distance — which includes
  the kitty's own element-memory cells, carried in the observation
  (doctrine rule 5's parenthetical) — and two global config
  constants. Nothing outside the observation, no observation change.
  Corollary: a stale remembered beam keeps full pressure until the
  memory is gone, same as sleep pursuit.
- **P4 (scope)**: `pursue`'s sleep arm, cosleep routing (028 FR-020),
  scene endings (056), announcements, and the served config are
  untouched.

## Verification hooks

- Unit fixtures per spec stories 1–3 and both edge cases (at-floor,
  under-floor), in `needs_driven.rs`/`selection.rs` test modules.
- `scripts/mutate.sh --expect` red: mutate the pressure binding back
  to the raw need — red on a floor-15 fixture, green at floor 0
  (SC-005).
- Experiments' legs (SC-002..004): tier 5 comparator,
  30 × 20k, on the floor-15 count-6 package world.
