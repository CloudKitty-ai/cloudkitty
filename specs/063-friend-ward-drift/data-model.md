# Data Model: Friend-Ward Drift

No persistent entities; the feature adds config fields and one derived
quantity. No observation-schema change (rule 5: the knowledge base is
the fogged view and digest the observation already carries).

## Config fields (`[behavior]`, `BehaviorConfig`)

| Field | Type | Default (absent) | Serialization | Validation |
|-------|------|------------------|---------------|------------|
| `friend_ward_drift` | bool | `false` | skipped when false (`GET /config` must not grow) | none (any bool) |
| `friend_ward_gate` | Option\<u32\> (Manhattan tiles) | accessor → 10 | skipped when absent | present ⇒ > 0, error names `[behavior] friend_ward_gate` |
| `friend_ward_detour` | Option\<f32\> (priced-cost tiles) | accessor → 4.0 | skipped when absent | present ⇒ finite and ≥ 0, error names `[behavior] friend_ward_detour` |

Validation runs in `validate_behavior` (existing position 7); both
dial checks apply whether or not the flag is on. Dials may be set with
the flag off (inert but lawful — the A/B flips one key).

## Derived quantity

**Nearest known friend** — `Option<(KittyId, Position)>`, computed per
decision from the start-of-tick fogged snapshot:

- Sources: visible roster members (any activity state, position only)
  ∪ unseen roster members at the freshest audible stamp whose kind is
  a law-named want or here word, within `meow.digest_window_ticks`.
- Pick: `min_by_key((manhattan(me.pos, pos), id))`.
- `None` ⇒ every drift site is inert.

**Drift fires** ⇔ flag on ∧ nearest known friend = `Some((id, pos))`
∧ `manhattan(me.pos, pos) > friend_ward_gate`.

## State transitions

None. The drift is stateless per decision (no counters, no routes, no
memory beyond what the snapshot and digest already hold — rule 5's
private-state bar).

## Relationships

- Reuses: `FogView` visibility, the meow digest audibility rule
  (start-of-tick, age within window), `priced_travel` physics,
  `step_toward` step rule, `sunbeam_reach` acceptance bound.
- Adds: one kind-fenced FogView query (sibling of `heard_unseen`);
  `selection::nearest_known_friend`.
- Does not touch: `heard_unseen` / `heard_unseen_targets` and their
  consumers (cuddle walk, play scan) — banked Candidate 2's surface.
