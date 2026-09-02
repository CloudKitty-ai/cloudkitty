# Contract: Refusal event + endpoint (spec 046)

## Endpoint

`GET /events/refusal` → `{"capacity": N, "events": [...]}` — the full
ring under `events`, **oldest first, newest last** (ring order), no
pagination, beside the ring's own `capacity` (envelope added at the
review-medium pass, 2026-09-01: a consumer must be able to tell a
wrapped window from a short history without hard-coding the knob's
default — the `/welfare` threshold precedent; `/config` omits
`refusal_retention` at its default, so the endpoint is the served
source of the bound).

## Event wire shape

The `proposed` field is the standard `Action` serialization (the wire
shape plugins and replays already speak) — targets ride exactly as the
action carries them:

```json
{"kitty_id": 1, "proposed": {"action": "move", "direction": "east"}, "tick": 0, "absorbed": false}
```

```json
{"kitty_id": 2, "proposed": {"action": "play", "target": "kitty", "id": 1}, "tick": 125350, "absorbed": true}
```

(The first example is the REAL payload recorded by a driven world on
2026-09-01 and pinned by `a_refusal_event_serializes_the_proposal_verbatim`;
the internally-tagged key is `action`, and `Play`'s target flattens —
exactly the proposal wire shape plugins already speak.)

`absorbed` is always present: `false` = the turn resolved Idle (a taxed
tick — the F-033/step-5 count is the `absorbed == false` filter);
`true` = the kitty was MID-SCENE and the scene continued, minimum met
or not (Experiments ruling (a), 2026-09-01: the taxed count reproduces
F-033's idle-tick definition — a past-minimum refusal kept a
need-relieving scene, so its cost is proposal quality, which is what
absorbed rows are retained as step-4/H6 evidence for; report-only until
baselined). Agreed census definition: refusal-tax share =
`absorbed == false` events / ticks. Known blind spot, report-only by
the same ruling: a mid-scene refusal inside an already-satisfied scene
is absorbed yet relieves nothing — F-033 did not count those either.

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
3. Bounded: at most `[events] refusal_retention` events (default 6,000
   — re-sized at the review-medium pass: taxed and absorbed refusals
   share the slots at ~0.38/tick combined on the scripted world, so
   6,000 covers a ~15k-tick census window); oldest dropped first; the
   bound is served as `capacity`.
4. Deterministic: same seed + same decisions → same stream, either tick
   driver.
5. Additive: pre-046 world saves load (ring starts empty at configured
   capacity via the load-path re-stamp); the deployed config parses
   unchanged; `engine_defaults_sha256` unmoved.
6. Consumers reading an empty array may treat it as "no refusals in
   the window" only because the emit-proof tests exist (F-029).
