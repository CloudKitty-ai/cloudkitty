# Data model: The wire's DecisionRequest on the lab binding (spec 055)

## The rendered request (existing shape, unchanged)

One JSON line, the spec 053 wire document, serialized by the engine's
own serde derivation with its existing field order:

| Field | Source at render time |
|---|---|
| `v` | `PROPOSAL_WIRE_VERSION` (currently 3) |
| `tick` | the upcoming decision's tick (`ctx.world.tick`) |
| `kitty_id` | the asked-for kitty |
| `me` | that kitty's full state from the start-of-tick snapshot |
| `world` | the kitty's fog view of that snapshot (spec 049 FR-048; doctrine rule 5) |
| `seed` | the first draw of the kitty's per-decision stream, derived WITHOUT consuming (D1) |
| `config` | the sim config, resent per request (spec 053 statelessness) |

No new fields, no lab-only extras, no version bump.

## The render window (new, per episode)

Valid exactly while the episode holds the upcoming tick's dealt seeds:
after `reset`/`step` returns, before the next `step`. Outside it —
truncated, poisoned, or pre-arm — the call errors. No state is added:
the window IS `pending_seeds`' lifetime.

## Error cases (owner-confirmed: always loud)

| Call | Result |
|---|---|
| Unknown kitty id | error naming the id |
| Episode over (truncated/poisoned) | error naming the kitty and "episode over" |
| No decision window (pre-arm) | error naming the kitty and "no decision window" |
| Valid | the JSON line, byte-equal to what the wire would send |

Python side: `ValueError` carrying the engine's message verbatim.

## Explicitly not changed

The wire (bytes, order, version), the server's draw position (Article V),
the observation encoding, every existing env method, the config schema.
