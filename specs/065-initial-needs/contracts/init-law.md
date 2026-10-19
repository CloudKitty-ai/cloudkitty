# The Initial-Needs Law, v1 (porting-grade)

Spec 065. The one place the draw and application semantics are pinned;
`init_needs.rs` implements it. Any change bumps
`INIT_NEEDS_LAW_VERSION` and the domain tag in the same commit (the
062 versioning rule).

## §1 Activation

The law runs iff the config carries a top-level `[initial_needs]`
table OR any `[[kitty]]` entry carries an `initial_needs` field.
Otherwise `World::try_generate` is the pre-065 function byte-for-byte:
no sub-stream is created, no needs-phase calls run at generation.

## §2 Resolution

For each kitty, for each need kind, the governing setting is: the
kitty's own `initial_needs` entry for that need if set; else the
top-level table's entry if set; else none (the need starts at 0.0,
today's value). Precedence is per NEED, never per table: a kitty
override for `cuddle` alone leaves its other five needs governed by
the top-level table.

## §3 Sub-stream seed

32 bytes: world seed as little-endian u64 in bytes 0..8; the 12-byte
ASCII domain tag `ck-initnd-v1` in bytes 8..20; zeros in 20..32.
ChaCha8. (The 062 recipe with this law's own tag.)

## §4 Draw order and consumption

Kitties in id-ascending order (the config roster's sort key); within a
kitty, needs in `NeedKind::ALL` order (eat, drink, sleep, play,
cuddle, bath). For each (kitty, need) whose GOVERNING setting is a
range: exactly one `u64` draw (`next_u64`), even when `min == max`
(the fixed-shape rule: draw count depends only on config shape, never
on values — the purr-duration precedent). A fixed governing value, and
an ungoverned need, consume zero draws (the starts explicit-kitty
precedent).

## §5 Value mapping

For a range `{min, max}` and draw `d: u64`:

```
u     = (d >> 11) as f64 * 2^-53        // uniform in [0, 1)
value = (min + u * (max - min)) as f32  // both endpoints attainable
```

The f64 → f32 cast at the boundary can round the product up to `max`
exactly (verified at review: `[0, 100]` with `u = 1 − 2⁻⁵³` yields
100.0), and can never exceed it — so the range is inclusive at both
ends, with `max` additionally guaranteed when `min == max`. A fixed
setting applies its value exactly. Applied values are set on the
kitty's needs (the `Need` type's clamp is belt-and-braces; validation
already bounds every configured number to [0, 100]).

The two spellings above are the ONLY wire forms: the deserializer is
hand-written (review F4) so a sequence (`[1.0, 2.0]`) is rejected, and
configs round-trip by VALUE, not by text (`cuddle = 80` re-serializes
as `80.0`).

## §6 Application site and the tick-0 state family

In `World::try_generate`: needs are applied immediately after the
kitty-creation loop and id sort, before explore-waypoint seeding. The
existing end-of-generate happiness recompute derives tick-0 happiness
from the applied needs (never configured directly). After it, iff the
law is active (§1), generation runs — in this order, the engine's
Phase-4 order —

1. `update_announce_arming(config)`
2. `record_distress(config)`   // at self.tick == 0

so announce arming, `in_distress`, `distress_since` (anchored 0), and
the distress log's tick-0 events all come from the engine's one
definition of entering distress. No parallel seeding path exists.
`purr_phase` does not run at generation.

Two declared consequences (review F5/F6d): the generation-time events
land in the distress LOG (the ring the server serves); no `TickReport`
ever carries them, since reports are per-tick captures and the edge
has already fired by tick 1 — a report-based counter undercounts
manufactured distress by exactly the tick-0 events. And a need BORN at
or above the threshold carries the same `since = 0` stamp as one that
crossed during the first tick's needs phase, so the register cannot
distinguish the two (distress age undercounts the born case by one
tick). Both conform to the spec; welfare readers take note here.

## §7 Invariants carried

- Master stream (`World.rng`) and every other sub-stream: untouched —
  active or not, their draw sequences are the pre-065 sequences.
- Composition with `[starts]` (062): position draws and need draws
  live in different domain-separated streams; neither moves the other.
- Determinism: (seed, config) fixes every applied value.
- Same-roster worlds differing only in this section byte-diverge ONLY
  through applied needs and their downstream consequences.

## §8 Validation (startup, before any world builds)

Reject with a clear error naming the need (and, for overrides, the
kitty by name AND id — the law keys by id):
non-finite numbers; any value, min, or max outside [0, 100];
min > max. (Overrides for un-rostered kitties are inexpressible: the
override is a field on the roster entry itself.)
