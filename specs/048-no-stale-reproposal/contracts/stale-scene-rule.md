# Contract: the stale-scene rule (spec 048)

## The rule

A cat MUST NOT propose the continuation of an ongoing scene when the decision snapshot
already shows the scene's counterpart gone; it makes a fresh decision that tick.
"Gone" is defined once — the same predicate the engine's dead-scene ending rule uses
(table in [data-model.md](../data-model.md)).

## Invariants

1. **One definition (FR-002)**: `prune_dead_activity` and `finish_what_you_started`
   consult the same predicate. Guard: a mutation weakening one arm of the predicate
   must red at least one prune witness AND at least one behavior witness.
2. **Live scenes untouched (FR-004/SC-003)**: counterpart present ⇒
   `finish_what_you_started` returns exactly what it returns today. Guard:
   must-stay-green continuation pins per shape.
3. **All personalities (FR-005)**: the helper stays shared; no personality-scoped
   variant. Guard: doctrine test that needs_driven and playful both fall through on a
   staged dead scene.
4. **No knob (FR-006/SC-004)**: no config field; defaults stamp byte-identical.
   Guard: existing stamp test, untouched.
5. **Refusal stream (FR-007/SC-005)**: stale-continuation rows vanish (no proposal is
   made); genuine refusals — including same-tick duet races — stamp exactly as today.
   Guard: staged e2e — dead-scene tick produces no refusal row; a staged race still
   does.
6. **Golden pin moves (FR-008)**: re-pin justified by the changelog entry + marker.

## Public surface

None. The predicate is `pub(crate)`; no API, event schema, or config change. Consumers
of `/events/refusal` see fewer rows (the artifact class), same shape.

## Out of scope (pinned)

Same-tick races: a duet partner interrupting in an earlier apply slot of the same tick
after this cat decided. Structurally invisible at decision time (Article V phase
order); measured 2,600–3,400 rows per reference run; they remain in the refusal
stream.
