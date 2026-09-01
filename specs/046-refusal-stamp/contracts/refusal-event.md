# Contract: Refusal event + endpoint (spec 046)

## Endpoint

`GET /events/refusal` → JSON array of refusal events, **oldest first,
newest last** (ring order), full ring, no pagination — the exact shape
discipline of `GET /events/activity`.

## Event wire shape

The `proposed` field is the standard `Action` serialization (the wire
shape plugins and replays already speak) — targets ride exactly as the
action carries them:

```json
{"kitty_id": 3, "proposed": {"kind": "play", "target": {"kitty": 1}}, "tick": 125349, "absorbed": false}
```

```json
{"kitty_id": 2, "proposed": {"kind": "move", "direction": "north"}, "tick": 125350, "absorbed": true}
```

`absorbed` is always present: `false` = the turn resolved Idle (a taxed
tick — the F-033/step-5 count is the `absorbed == false` filter);
`true` = duration enforcement continued the kitty's scene (refusal
heard, nothing lost; report-only until baselined). Agreed census
definition: refusal-tax share = `absorbed == false` events / ticks.

(Field names/tagging follow the existing `Action` serde derives
verbatim — the contract is "the proposal as proposed", not a bespoke
shape. Exact tag spelling is pinned by the emit-proof test against a
REAL recorded payload, per CLAUDE.md rule 5's fixture discipline.)

## Guarantees

1. One event per refusal: a non-Idle proposal resolved to Idle by
   validation, on the tick it was heard, in turn order within the tick,
   `absorbed` set from the enforcement outcome.
2. No event for: chosen Idle, duration-overridden *legal* proposals,
   message downgrades.
3. Bounded: at most `[events] refusal_retention` events (default 4000);
   oldest dropped first.
4. Deterministic: same seed + same decisions → same stream, either tick
   driver.
5. Additive: pre-046 world saves load (ring starts empty at configured
   capacity via the load-path re-stamp); the deployed config parses
   unchanged; `engine_defaults_sha256` unmoved.
6. Consumers reading an empty array may treat it as "no refusals in
   the window" only because the emit-proof tests exist (F-029).
