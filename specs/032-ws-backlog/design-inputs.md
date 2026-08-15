# Design inputs: connect-time frame backlog

Settled in conversation between the owner and the Product thread, 2026-08-14
→ 15, from requirements relayed by the Client thread. This file exists so the
implementation plan starts from these decisions instead of re-deriving them.
The spec is the contract; this is the reasoning.

## Provenance

Client's measurements (668-tick capture of the live world, plus driving the
real `Pacer` at 800ms/tick):

- Deepening the delay line by playback slowdown alone: depth 1 full after
  8.8s (9% slow), depth 3 after 12.0s (24% slow), depth 5 after 14.6s (39%
  slow). Every page load would open with ~15s of visible slow motion.
- Frame size ≈ 4.2KB. Arrival timing: within 5 ticks 85.3%, within 8 ticks
  94.4% — asks past 8 are waste.
- `ws.rs` pushes from a `watch` channel holding only the latest
  `snapshot_json`; no existing ring to expose.

Client originally asked for `GET /history?n=5` plus two client-side
correctness rules (seed only if nothing drawn; tick-keyed dedupe). The owner
re-scoped the request as a user story and freed the mechanism.

## The decisions, and why

**Backlog on the socket, not a second endpoint.** The two proposed client
rules exist only because a fetch would race the socket. Same channel → the
race is unrepresentable → both rules disappear, replaced by the server-side
guarantee of strictly increasing ticks per connection. The fetch design also
silently degrades to the 15s ramp exactly when the fetch loses the race (slow
connections), and gives up on reconnects entirely; the socket design has no
losing branch and heals reconnects too. `/history` was dropped rather than
kept as a rider (owner call, 2026-08-15).

**Opt-in, client-sized ask** (`?backlog=n` on the upgrade, default 0):

- Unused, the stream is byte-identical to today — the clowder benchmark and
  any cached client build keep meaning what they meant, and server/client can
  deploy in either order (old server ignores the param; old client omits it).
- The client asks for the 5 it wants, not the 16 the ring holds — cuts the
  worst-case mass-reconnect burst by two-thirds.
- If a reconnect storm ever hurts, the server can clamp the answered depth
  without breaking anyone: fewer-than-requested is already lawful (it is the
  answer right after boot, too).

**Ring inside `Published`, not beside it in `AppState`.** Store
`(tick, Arc<str>)` pairs sharing the same allocations the watch channel
already carries; rebuild per tick by cloning the previous ring (16 refcount
bumps + one small allocation), push new, pop old, ship through the existing
channel. Consequences:

- Zero new serialization — the load-bearing invariant. An implementation that
  re-serialized per ring entry would multiply the per-viewer-serialization
  cost the 2026-07-22 security pass removed, by the cap. Guard this in review.
- No new lock, no torn reads: the ring is immutable per publish, so the ws
  handler sees an atomic snapshot of it for free.
- Storing the tick beside the string means the backlog sender never parses
  JSON to learn a frame's tick.

**Costs, quantified** (so nobody re-measures):

- Memory: frames now live ~cap ticks instead of ~1 → ≈63KB extra resident at
  cap 16 × 4.2KB. Scales linearly with frame size; a 10× world is still
  <1MB. Bounded absolutely by the cap.
- CPU: sub-microsecond per 800ms tick (refcount bumps + one VecDeque
  allocation). Publisher hot path unchanged.
- The one real interaction: **connect burst × viewer count**. Server restart
  is safe by construction (ring empty → herd gets ~1 frame each — the
  empty-after-restart choice accidentally buys herd protection). The residual
  case is a mass client drop with the server up (relay hiccup at clowder
  scale ~965 viewers): ≈965 × 21KB ≈ 20MB egress in the reconnect window at
  depth 5 (65MB at cap). Loopback/Caddy fine; WAN spike lands when the
  network is already unhappy. Mitigations already in the shape: opt-in
  default-0, client asks 5 not 16, server may clamp under pressure.

**Edge semantics:**

- `snapshot_json` is an `Option` (serialization failure is logged, never yet
  seen) → the ring can have a tick gap → the contract says *strictly
  increasing*, never *consecutive*; consumers key on tick numbers, not array
  adjacency.
- Restart: ring is process memory; persisting it into the world save would
  bloat the save and splice serving regimes. Empty-after-restart, by design.
- Cap: config dial per the `events.activity_retention` precedent (Article
  VI). Default 16. Socket-side asks beyond it clamp (a viewer connection is
  never refused over a query param); this is deliberately laxer than the
  REST-side strictness posture because the failure mode of refusing is a dark
  viewer, not a misconfigured operator.

## Client-side simplification that falls out (Client thread's queue, not ours)

Today's boot (`client/app.js` ~1351): await `GET /world` → first paint →
subscribe. With backlog on the socket: fire-and-forget config fetch, then
subscribe with `?backlog=5`. Deletions: `fetchSnapshot()`, the awaited
two-step, the second retry path (socket close becomes the only failure
signal), the duplicate first frame (fetch and first push are usually the same
tick today), and both proposed correctness rules. Addition: flush the delay
line on socket `open` — which the existing snap-don't-ease reconnect doctrine
(`bumpGeneration`) already implies. The Pacer needs zero changes: a 5-frame
connect burst is exactly the bursty-arrival input it was built to buffer
(pace self-measures from promotions, not arrivals). Reconnects — not just
first loads — resume at full depth.

`GET /world` stays served: it leaves the viewer's boot path but remains right
for curl, captures, and tooling.

## Logged demand, out of scope here

A served **travel goal** (a far gaze target: "heading to X") is worth more to
the anticipation work than the buffer — Client measured that adjacent targets
have no horizontal gaze component 58% of the time vs 9.7% at 4–7 tiles. But:

- Chases already serve their far target: the optional `pursuit` kitty field
  (spec 004: `{target, started, closest, improved_at}`). Client should wire
  gaze to it before anything new is specced — 19% of chase runs go past 4
  tiles.
- Beyond chases there is no ground truth to serve for policy cats: the policy
  emits one move per tick; the engine records facts, never inferred intent
  (`update_pursuit`'s own doctrine). A served goal becomes honest the day a
  policy generation *declares* one (an output head — connects to the Gen-B
  need-estimator ideas in `experiments/comms-generations-brainstorm-2026-08-13.md`).
  Until then, don't fake it.
