# Contract: the Playful 2.0 behavior dials

The `[behavior]` config surface after spec 042. Consumers: the engine
(`Config`), Experiments' comfort × score × weights sweep configs, the
Biscuit 3.0 demonstration configs. No wire, event, or snapshot
surface changes.

## Fields

Six score/gate dials on `[behavior]` and six weights under
`[behavior.comfort_weight]` — identity defaults and validation per
data-model.md §5 (the single source for the table).

## Guarantees

1. **Inert launch**: with every dial absent (or at its identity
   value), world evolution is byte-identical to the pre-042 build —
   the golden evolution digest (pin `7b361b2a…`) stays green, and the
   critter-beats-friend distance tie is preserved.
2. **Stamp stability**: all twelve fields are skip-serialized at
   identity, so `engine_defaults_sha256` does not move. Measurements
   and baselines pinned to the current stamp remain comparable — this
   feature creates no re-baseline debt.
3. **One dial, one effect**: `w_value` scales only friend valuation
   (and switches busy-friend admission); `critter_appeal` moves only
   critters; `t_self`/`t_partner` only filter; the comfort weights
   touch only the playful get-serious trigger. Each is
   independently settable and independently guarded by a red-first
   test.
4. **No new refusal exposure**: at any dial values, play proposals
   are only ever emitted toward free adjacent partners; a
   busy-adjacent pick resolves to solo play for the tick. The
   engine's validation rules are untouched.
5. **Validation**: non-finite values are config errors on every
   field; negatives are errors on all fields except `critter_appeal`;
   comfort weights are strictly positive (zero would disable a
   need's get-serious trigger); errors name the field
   (`[behavior] w_value`, `[behavior.comfort_weight] eat`, …).
6. **Served config untouched**: `cloudkitty.toml` documents the dials
   in comments only; sweep and demo configs set them explicitly.

## Sweep guidance (2026-08-30, review #3)

Raise `w_busy` alongside `w_value`: with `w_busy = 0` waiting is
free, and an adjacent mid-scene friend can absorb the game
(solo-play-beside for its whole scene) while a free friend nearby
goes unchased. This is dial-space behavior the sweep prices, not a
bug — but an arm that moves `w_value` alone should expect it.
Comfort weights are strictly positive (> 0): down-weighting defers a
need, disabling its trigger is not on the dial.

## Sequencing contract

Must land (inert) before Experiments' joint sweep begins; the sweep
prices all twelve dials in one lab campaign, and served/demo values
are the owner's pin as always.
