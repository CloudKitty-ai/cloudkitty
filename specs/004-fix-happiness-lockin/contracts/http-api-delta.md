# HTTP API Contract Delta: Fix Low-Happiness Lock-In

**Base contract**: [001 http-api.md](../../001-cloudkitty-mvp/contracts/http-api.md).
Endpoints, methods, and status codes are unchanged; this delta covers payload
additions only. All additions are backward compatible — existing consumers
that ignore unknown fields keep working.

## Kitty object (in `GET /world` and WS `world` frames)

Three additive fields:

```jsonc
{
  "id": 1,
  "name": "Miso",
  // ... existing fields unchanged ...

  // NEW — tick each currently-active distress began. Key set matches
  // in_distress. Omitted when empty. Viewers derive the age as
  // world.tick - distress_since[need].
  "distress_since": { "play": 1249, "sleep": 1279, "bath": 1375 },

  // NEW — engine bookkeeping of the current chase, if any. Omitted when
  // absent. started = tick the pursuit began; closest = best distance
  // achieved; improved_at = tick that best was last bettered (patience runs
  // from there, so a chase that is still closing never expires).
  "pursuit": {
    "target": { "target": "element", "id": 102 },
    "started": 1461, "closest": 3, "improved_at": 1466
  },

  // NEW — targets excluded after a futile chase, until the given tick.
  // Engine-pruned; omitted when empty.
  "abandoned_chases": [ { "target": { "target": "element", "id": 105 }, "until": 1520 } ],

  // NEW — tick each need last received relief. Omitted when empty
  // (fresh worlds before any relief).
  "last_relief": { "eat": 1396, "drink": 1421, "play": 1033 }
}
```

## `last_action` play shapes

`Play`'s target is now optional:

```jsonc
{ "action": "play", "target": "kitty", "id": 2 }   // social play (unchanged shape)
{ "action": "play", "target": "element", "id": 102 } // critter play (unchanged shape)
{ "action": "play" }                                // NEW: solo play (pouncing at nothing)
```

Viewers should render targetless play as solo play (e.g. "pouncing at
nothing 🎈"); the greeble-secrecy rule (FR-033/FR-037) is unaffected because
solo play has no target to conceal.

A target must be complete or absent: `{"action":"play","target":"element"}`
with no `id`, or an unrecognized kind, is rejected rather than read as solo
play. Producers must not emit half a target.

## `GET /config`

The echoed config gains the new keys (see
[data-model.md](../data-model.md#config-extended)):
`behavior.urgency_weight`, `behavior.tile_cost`, `behavior.worth_a_detour`,
`behavior.chase_patience_ticks`, `behavior.chase_exclusion_ticks`,
`behavior.solo_play_reach`, `behavior.sunbeam_reach` (post-merge review
amendment, 2026-07-19), `actions.solo_play_relief`, and the new
`viewer.distress_patience_ticks`.

The client reads `viewer.distress_patience_ticks` to decide when a kitty's
card shows the gentle long-distress cue; it must not hard-code the threshold.

## `GET /events/distress`

Unchanged. `distress_since` complements the event log (which remains bounded
at its configured retention); the per-kitty field is the authoritative source
for "how long has this been going on", immune to log rotation.
