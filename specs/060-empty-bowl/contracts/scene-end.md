# Contract: Eating scene-end resolution (spec 060)

The externally observable contract of the amended rule. Consumers:
engine tests, the activity log / `/events/activity` surface, RL mask
oracle, stream-pin fixtures.

## C1 — The end condition

At each tick's scene-end resolution (`resolve_activity_ends`, after
every apply slot, before the environment phase), an `Activity::Eating`
scene ends iff:

```
elapsed >= bounds.max
  || (elapsed >= bounds.min && governing need == 0)
  || adjacent_stocked_chow(eater.pos).is_none()      // NEW: min-independent
```

and continues otherwise. Every other activity's end condition is
byte-identical to spec 006 (SC-002).

## C2 — Observable guarantees

1. **No meal held past a failed resolution** (SC-001/SC-003): a scene
   never survives a resolution at which the per-tick eat effect could
   not have fed it — the end rule and the effect read the same
   predicate. (Not "no zero-relief tick": a bowl drained under an
   earlier eater, or removed by the environment after a resolution,
   still buys one in-tick lick before the resolution that sees it.)
2. **Span accounting**: an early end writes an ordinary activity-log
   end record; a meal started on a last serving records span 1 and
   delivers exactly one serving's relief.
3. **No refusal surface** (FR-003): ends route through `end_activity`
   only; `refusal_log` writes happen only in apply slots. The count of
   absorbed Eat refusal rows DROPS (the paused-meal continuation rows
   vanish); none are added.
4. **Shared-bowl ends** (FR-004): evaluated per seat position after
   all consumption this tick — every eater whose feeding condition
   fails ends on the same resolution, whoever drew the last serving.
5. **Freed next tick**: the ended eater has no activity clock next
   tick; it decides through normal machinery (no held proposal, no
   teacher continuation — `governing_need()` is None).
6. **Mask coherence**: the RL legality mask moves with the engine
   automatically (it replays validate + enforcement); mid-meal
   Eat-legal-while-absorbed shrinks to the same-tick window.

## C3 — Stream-pin obligations (US2 / FR-005)

- Any deterministic fixture whose stream drains a bowl mid-scene below
  `min` MAY diverge; each re-recorded pin names spec 060 and its
  first-divergence tick in the fixture file's re-record history (the
  059 artifact pattern), captured BEFORE re-recording.
- CHANGELOG Unreleased carries `[rng-sequence]` naming this spec.
- Shipped tomls: zero edits; both shipped-config sweeps green
  unchanged.
- BACKLOG.md:90-111 (the shelf entry) removed at merge (FR-007).
