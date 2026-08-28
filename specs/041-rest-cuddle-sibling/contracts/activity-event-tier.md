# Contract: tier counters on the activity-end event

The additive change to `ActivityEnd` (`/events/activity`, and the
same struct wherever snapshots or tools carry it). Consumers: the
server API's JSON, F-031 span instruments, Experiments' censuses
(SC-004's emit-proof), any future viewer.

## Shape

Existing (unchanged): one event per finished scene —
`{ kitty_id, activity, started, ended }`, inclusive span
`ended − started + 1`.

Added: two counters, present on every event in memory, serialized
only when nonzero:

```json
{
  "kitty_id": 3,
  "activity": { "resting": { "with_friend": 1 } },
  "started": 120410,
  "ended": 120421,
  "mutual_ticks": 9,
  "drip_ticks": 2
}
```

A walk, a meal, or a solo nap serializes exactly as today (both
counters zero → both fields absent).

## Guarantees

1. **One event per scene** — a mid-scene tier flap changes counter
   values, never event count. Span semantics and scene counting are
   untouched (F-031).
2. **Deserialization is total**: absent fields read as 0
   (`serde(default)`); pre-change snapshots, recorded JSON, and
   existing consumers load unchanged (FR-009).
3. **Invariant**: `mutual_ticks + drip_ticks ≤ span()`. The
   shortfall counts the scene's solo (posture-only or partner-less)
   serviced ticks and is itself informative.
4. **Which activities count**: partnered rest and co-sleep serviced
   ticks increment exactly one counter each (mutual xor drip, by the
   shared predicate at that tick). All other activities never
   increment — a nonzero counter on any other activity kind is a
   bug.
5. **Emit-proof reading** (SC-004): a nonzero `drip_ticks` (resp.
   `mutual_ticks`) anywhere in a census window proves that tier can
   emit; both nonzero somewhere in the window is the acceptance
   condition. Instruments keep counting scenes, not relief events —
   reciprocal pairs double relief events but not events.
