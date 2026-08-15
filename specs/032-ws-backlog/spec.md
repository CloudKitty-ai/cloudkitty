# Feature Specification: Connect-Time Frame Backlog

**Feature Branch**: `032-ws-backlog`

**Created**: 2026-08-15

**Status**: Draft — PARKED by owner decision 2026-08-15 (spec now, implement later)

**Input**: User description: "The viewer's anticipatory-gaze work (deepening its
delay line from ~1 tick to ~5 so buffered frames become a lookahead) needs the
recent past at connect time. Today buffer depth can only be accumulated by
slowing playback, so every page load opens with ~15 seconds of visible slow
motion (measured: depth 5 fills after 14.6s at 39% slowdown). Hand a connecting
viewer the last few published frames and it starts at steady state instantly.
Requirements arrived from the Client thread 2026-08-14 (relayed for Elizabeth);
the owner directed Product to treat them as a user story and design the
mechanism freely, provided the required state reaches the client."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A fresh viewer starts at full depth (Priority: P1)

A person opens the meadow page. The viewer connects to the live stream and asks
for a short backlog of the most recent world states. The stream delivers those
states first (oldest first), then continues with live states. The viewer's
delay line is full from the first paint: the world appears at its normal pace,
already carrying the lookahead the anticipation features need — no slow-motion
warmup, no frozen first seconds, no blank wait.

**Why this priority**: This is the entire point of the feature. The measured
alternative is ~15 seconds of visibly wrong pacing on every page load, or
anticipation features that stay dark until the buffer fills.

**Independent Test**: Connect a viewer that requests a backlog of 5 against a
server that has been running longer than 5 ticks. It receives 5 historical
states followed by live states, all in one stream, ticks strictly increasing;
the first live state arrives within one tick interval of connecting.

**Acceptance Scenarios**:

1. **Given** a server that has published at least 5 states, **When** a viewer
   connects requesting a backlog of 5, **Then** it receives exactly 5 states
   older than the live stream's first state, oldest first, followed by the
   live stream, with every tick strictly greater than the one before it.
2. **Given** a connected viewer that requested a backlog, **When** the
   simulation continues ticking, **Then** live delivery is indistinguishable
   from today's stream (latest-wins pacing for slow consumers included).
3. **Given** a viewer that requests no backlog, **When** it connects, **Then**
   the stream behaves exactly as it does today: current state immediately,
   then one state per tick.

---

### User Story 2 - Reconnects heal at full depth (Priority: P2)

A viewer's connection drops (network blip, relay hiccup, laptop lid). On
reconnect it asks for the backlog again and resumes at full depth immediately —
the warmup ramp is gone from reconnects, not just first loads. States from
before the viewer's gap and after it are never interleaved: the backlog is
whatever the server most recently published, delivered before the live stream,
in order.

**Why this priority**: Reconnects are more frequent than first loads for a
long-lived ambient page, and the previously proposed fetch-based design
explicitly gave up on them (its correctness rule was "discard history if
anything was already drawn").

**Independent Test**: Kill a viewer's connection mid-session, reconnect with a
backlog request, and verify the received sequence is monotone in tick and
resumes full-depth playback with no slow-motion segment.

**Acceptance Scenarios**:

1. **Given** a viewer that was connected and then dropped, **When** it
   reconnects requesting a backlog, **Then** the new connection's states are
   strictly increasing in tick from its own first state, and full anticipation
   depth is available from the first paint after reconnect.
2. **Given** the server restarted while the viewer was away (world resumed
   from its save), **When** the viewer reconnects, **Then** it receives only
   states published since the restart — never states retained from the
   previous server process — even if fewer than requested.

---

### User Story 3 - The unadorned stream is untouched (Priority: P3)

Anything that connects to the live stream without asking for a backlog — an
older viewer build, a load-test harness, a curious `websocat` — sees exactly
today's behavior. The feature is invisible until asked for.

**Why this priority**: The clowder load benchmark and any cached client build
must keep meaning what they meant. Deployment order between server and client
becomes irrelevant in both directions.

**Independent Test**: Connect without a backlog request; capture the stream;
verify it is behaviorally identical to the pre-feature server (current state
immediately on subscribe, then per-tick states).

**Acceptance Scenarios**:

1. **Given** a consumer that does not request a backlog, **When** it connects,
   **Then** it receives the current state immediately and live states
   thereafter, with no additional frames.

---

### Edge Cases

- **Young server**: fewer published states exist than the viewer asked for
  (including zero, immediately after boot). The server sends what it has,
  oldest first. Fewer-than-requested is a lawful, expected answer; the viewer
  falls back to accumulating the remainder the slow way.
- **Ask beyond the cap**: a request larger than the server's retention cap is
  answered with at most the cap. The connection is never refused over the size
  of the ask.
- **Malformed ask**: an unparseable or negative backlog request is treated as
  absent (zero backlog). A read-only viewer connection is never failed over a
  bad query parameter.
- **Serialization gap**: if a published state failed to serialize (logged,
  never yet observed), the retained sequence has a gap at that tick. The
  contract is therefore *strictly increasing* ticks, not *consecutive* ones;
  consumers must key on tick numbers, never on array adjacency.
- **Restart**: retention is process memory only. After any restart the backlog
  starts empty and refills over the next cap-worth of ticks. Pre-restart states
  are never served, so two serving regimes can never splice on one connection.
- **Mass reconnect**: if every viewer drops and reconnects while the server
  stays up (relay hiccup), each reconnect carries at most cap × frame-size of
  backlog. The worst-case burst is bounded and calculable; immediately after a
  server restart it is near zero because the ring is empty (US2 scenario 2).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The live update stream MUST accept, at connect time, a request
  for up to N of the most recently published world states (the *backlog*), and
  MUST deliver them before any live state, oldest first.
- **FR-002**: A connection that requests no backlog MUST behave exactly as the
  stream behaves today: the current state immediately upon subscribing, then
  one state per published tick, latest-wins for slow consumers.
- **FR-003**: Within a single connection, every delivered state MUST carry a
  tick strictly greater than the previously delivered state's tick — across
  the backlog, across the backlog/live seam, and across the live stream. No
  duplicate ticks, ever. (Ticks may skip; see the serialization-gap edge case.)
- **FR-004**: Backlog states MUST be identical in shape and content to live
  states and to the standalone world snapshot — the same document a live push
  carries. The viewer keeps exactly one shape to render.
- **FR-005**: The server MUST retain a bounded number of the most recently
  published states. The retention capacity MUST be a configured value with a
  documented default (default: 16), validated at startup and echoed by the
  configuration endpoint, per Article VI (no magic numbers) and the
  `events.activity_retention` precedent.
- **FR-006**: A backlog request exceeding what is retained (by youth or by
  cap) MUST be answered with everything retained, in order — never an error,
  never a refused connection.
- **FR-007**: Retention MUST be in-process memory only: never persisted with
  the world's save, empty after every restart, pre-restart states never
  served.
- **FR-008**: Retaining and serving the backlog MUST NOT add per-tick
  serialization or other per-viewer work that scales with viewer count: the
  states retained are the same once-per-tick serialized documents the live
  stream shares (the 2026-07-22 one-serialization-per-tick posture is a
  standing constraint, not an optimization to rediscover).
- **FR-009**: The simulation MUST be unaffected: no engine change, no change
  to randomness, tick order, observation or action schemas, the world save, or
  the engine-defaults stamp. This feature lives entirely in the serving layer.
- **FR-010**: The standalone snapshot endpoint (`GET /world`) MUST remain
  available and unchanged — it leaves the viewer's boot path but stays the
  right tool for tooling, captures, and one-shot inspection.

### Key Entities

- **Published state**: one tick's full world document, serialized once at
  publish time; the unit both the live stream and the backlog deliver.
- **Retention ring**: the server's bounded, tick-ordered memory of the most
  recent published states; capacity configured (FR-005), contents reset by
  restart (FR-007).
- **Backlog request**: a viewer's connect-time ask for up to N retained states;
  absent by default (FR-002), clamped by retention (FR-006).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A fresh page load reaches full anticipation depth (delay line of
  5) at first paint — replacing the measured 14.6-second fill at 39% visible
  slowdown with zero seconds of ramp.
- **SC-002**: A reconnect after a connection drop resumes full-depth playback
  immediately: no slow-motion segment is observable after any reconnect
  against a server that has been up longer than the requested depth.
- **SC-003**: A consumer that does not request a backlog receives a stream
  behaviorally identical to the pre-feature server (verifiable by capture
  comparison over any interval).
- **SC-004**: Steady-state server memory attributable to the feature is
  bounded by cap × frame size (≈70KB at the default cap and today's ~4.2KB
  frames) regardless of uptime or viewer count, and per-tick publish work does
  not grow with the feature enabled but unused.
- **SC-005**: The worst-case connect-time payload is bounded by cap × frame
  size per viewer (≈70KB at defaults; ≈21KB at the viewer's intended depth 5),
  and is near zero for the reconnect storm that follows a server restart.

## Assumptions

- The shipped viewer is the only written consumer of the live stream (owner,
  2026-08-15), so compatibility properties (US3, deployment-order freedom) are
  design niceties rather than obligations — kept because they cost one default.
- The viewer's intended ask is depth 5; its own arrival sizing (85.3% of
  arrivals within 5 ticks, 94.4% within 8) says asks beyond 8 are waste. The
  default cap of 16 leaves headroom without inviting abuse.
- Client-side changes ride separately (Client thread's queue): flushing the
  delay line on reconnect (already implied by its snap-don't-ease doctrine)
  and optionally dropping the initial snapshot fetch from its boot path. This
  spec's scope is the serving side only.
- A `GET /history` REST endpoint was considered and dropped (owner,
  2026-08-15): delivering the backlog on the stream itself makes the
  fetch/socket race unrepresentable and deletes the client-side seeding and
  dedupe rules the two-channel design would have required.
- The Client thread's related ask for a served *travel goal* (a far-away gaze
  target) is explicitly out of scope: for policy-driven cats no ground-truth
  goal exists to serve (chase pursuits are already on the wire as `pursuit`),
  and anything more would be the engine inferring intent, against its
  facts-only doctrine. The demand is logged in this spec's design notes.
- Design analysis (cost walk-through, mass-reconnect interaction, client
  simplification) is preserved in `design-inputs.md` beside this spec; the
  implementation plan should start there rather than re-deriving.
