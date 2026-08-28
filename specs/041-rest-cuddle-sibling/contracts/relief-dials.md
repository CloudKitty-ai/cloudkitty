# Contract: the cuddle relief dial family

The `[actions]` config surface after spec 041. Consumers: the engine
(`Config`), every committed toml, HEAD tooling that loads historical
configs (twin-probe, census re-cuts), and the lab bindings
(`deny_unknown_fields` both directions after the 3.0 wall).

## Fields

| key | type | engine default | meaning |
|---|---|---|---|
| `rest_mutual_relief` | f32 | 15.0 | per serviced tick, both parties, partnered rest when the partner is itself sleeping/resting |
| `rest_drip_relief` | f32 | 0.0 | per serviced tick, both parties, partnered rest when the partner is merely present |
| `groom_cuddle_relief` | f32 | 15.0 | per serviced tick, groomer's own cuddle relief while grooming a friend |
| `cosleep_mutual_relief` | f32 | existing | unchanged semantics (spec 028) |
| `cosleep_drip_relief` | f32 | existing | unchanged semantics (spec 028) |
| `cuddle_relief` | f32 | 15.0 | **deprecated, inert** — parsed, nan-validated, feeds nothing |

## Guarantees

1. **Back-compat**: any config valid before this feature remains
   valid; `cuddle_relief` is accepted and ignored. Genuinely unknown
   keys are still rejected (strictness unchanged). The 181 committed
   historical tomls load with HEAD tools (SC-002).
2. **Behavior preservation at the split**: with the new dials at the
   classic value and drip at 0.0, world evolution is byte-identical
   to pre-split (SC-001). All observable change arrives with the
   engine-sibling commit (legality/binding/events) and the reprice
   diff (values).
3. **Convention, not validation**: `*_drip_relief <
   *_mutual_relief` within each activity is documented in the toml
   comments and nowhere enforced (owner-ratified).
4. **Nan safety**: all six keys appear in the nan-validation table;
   `nan` anywhere is a config error, inert key included.
5. **The 3.0 wall** (out of this feature's scope, recorded for the
   config-hygiene sweep): `cuddle_relief` is deleted there, along
   with the pre-041 bound-duet snapshot tolerance.

## Served 2.x values

Commit 1 (split): `rest_mutual_relief = 8.0`,
`groom_cuddle_relief = 8.0`, `rest_drip_relief = 0.0`, cosleep pair
untouched, `cuddle_relief` left in place (inert).

Commit 3 (reprice): `cosleep_drip_relief = 0.25`,
`cosleep_mutual_relief = 0.6`, `groom_cuddle_relief = 0.5`,
`rest_drip_relief = 0.25`; `rest_mutual_relief` stays 8.0. Comment
fixes ride this diff: the stale "mean cuddle need of 11.6" (measured
5.1 mean / 2.8 median), both saturating-delivery cosleep tier
comments (rewritten to riders-partial), the per-scene-not-per-pair
note; the play ladder comment untouched.
