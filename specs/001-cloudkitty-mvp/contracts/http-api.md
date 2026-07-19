# Contract: HTTP API & WebSocket

**Feature**: CloudKitty MVP | **Date**: 2026-07-18
**Server**: `cloudkitty-server` (axum), default bind `127.0.0.1:8090` (configurable)

All endpoints are read-only, unauthenticated (trusted local network — spec
assumption), and return `application/json`. Greebles appear in every payload that
contains elements — invisibility is a client rendering rule, never an API filter.

## REST endpoints

### GET /world

Full world snapshot (wire form of `World`, RNG state omitted).

```json
{
  "width": 32, "height": 32, "tick": 1234,
  "kitties": [ { …see /kitties/{id}… } ],
  "elements": [
    { "id": 7, "kind": "water",   "pos": {"x": 3, "y": 10} },
    { "id": 9, "kind": "chow",    "pos": {"x": 20, "y": 4}, "servings": 3 },
    { "id": 12, "kind": "bug",     "pos": {"x": 15, "y": 15}, "ttl": 88 },
    { "id": 13, "kind": "greeble", "pos": {"x": 8, "y": 22}, "ttl": 41 },
    { "id": 14, "kind": "sunbeam", "pos": {"x": 27, "y": 9},  "ttl": 120 }
  ],
  "recent_meows": [ { "kitty_id": 1, "kind": "want_play", "tick": 1230 } ]
}
```

- `200 OK` always (server refuses to boot without a valid world).

### GET /kitties

`200 OK` → JSON array of all kitties (same shape as below), ordered by id.

### GET /kitties/{id}

```json
{
  "id": 1, "name": "Miso", "pos": {"x": 5, "y": 6},
  "needs": { "eat": 42.5, "drink": 10.0, "sleep": 77.0,
             "play": 30.0, "cuddle": 55.0, "bath": 12.0 },
  "happiness": 61.4,
  "activity": { "state": "sleeping", "in_sunbeam": true, "with_friend": 2 },
  "behavior": "needs_driven",
  "last_action": { "action": "sleep", "with": 2 }
}
```

`activity.state` ∈ `idle | resting | sleeping`; `with_friend`/`in_sunbeam` present
only when applicable. `last_action` is the action the engine actually applied last
tick (post-validation — an illegal proposal reads as `{"action":"idle"}`); absent
only before the world's first tick. Action shapes are internally tagged on
`action`, e.g. `{"action":"chase","target":"element","id":12}`,
`{"action":"meow","message":"want_play"}`, `{"action":"move","direction":"north"}`.
`{"action":"play"}` with no target is solo play (feature 004).

Feature 004 adds three optional kitty fields — `distress_since`, `pursuit`,
`abandoned_chases` — each omitted when empty; see the
[004 API delta](../../004-fix-happiness-lockin/contracts/http-api-delta.md).

- `200 OK`; `404 Not Found` with `{ "error": "no kitty with id 99" }` for unknown ids.

### GET /events/distress

`200 OK` → most recent distress events (bounded retention, default 1,000),
newest last:

```json
[ { "kitty_id": 2, "need": "drink", "tick": 981 } ]
```

Events are edge-triggered: one entry per threshold crossing (clarification
2026-07-18).

### GET /config

`200 OK` → the active validated configuration (world size, tick_ms, seed, roster,
element rules, all simulation constants). Mirrors `cloudkitty.toml` structure.

### GET / (and static assets)

Serves `client/` (index.html, app.js, render.js) via tower-http `ServeDir`.

## WebSocket: /ws

- Upgrade at `GET /ws`. No client→server messages are processed (read-only viewer);
  any received message is ignored.
- After each simulation tick the server pushes one text frame containing the **same
  JSON document as `GET /world`** (full snapshot, greebles included).
- Slow consumers receive the latest state (watch-channel semantics): intermediate
  ticks may be skipped, frames are never delivered out of order.
- Client contract: fetch `GET /world` once for initial paint, then subscribe to
  `/ws` and re-render on every frame; on disconnect, reconnect and repeat
  (snapshot → subscribe). The simulation is unaffected by client connects/drops.

## Error shape

All error responses: `{ "error": "<human-readable message>" }` with an appropriate
4xx status. The API has no 5xx-producing mutation paths; internal errors log via
`tracing` and never crash the sim task.

## Contract tests (server integration)

1. Boot on an ephemeral port with a test config (2 kitties, ≥1 greeble forced).
2. `GET /world` → 200; payload parses; `elements[]` contains `kind == "greeble"`.
3. Open `/ws`; receive ≥2 frames; assert `tick` strictly increases across frames.
4. `GET /kitties/{unknown}` → 404 with error shape.
