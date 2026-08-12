# Feature Specification: Clowder — viewer load benchmark

**Feature Branch**: `029-clowder`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "Clowder: a load-generation and benchmark tool that measures how many concurrent viewers the CloudKitty server can handle and characterizes its failure behavior under excessive traffic. WebSocket viewer swarm plus REST-poller mix, with ramp, spike, slow-consumer, and churn modes; measures tick-rate stability, per-connection lag, skipped ticks, handshake latency, and error/disconnect rates entirely from outside the server (tick numbers parsed from payloads); CSV and summary output. No engine or server changes. Never run against the live world."

## Clarifications

### Session 2026-08-12

- Q: What makes a ramp step "healthy"? → A: Strict compound default,
  per-run configurable: zero skipped updates among healthy viewers, observed
  tick cadence within ±5% of the world's nominal rate, zero handshake
  failures, and zero unexpected disconnects — sustained for the whole hold
  (recorded as FR-016).
- Q: How fine-grained are the run records? → A: Fixed-interval rows
  (default 1 second) on one schema across all modes; per-step and per-run
  summaries are derived from the interval rows and included in the record.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find the ceiling (Priority: P1)

The operator points Clowder at a locally running CloudKitty server and asks
one question: how many concurrent viewers can this server sustain while the
world stays healthy? Clowder ramps viewer connections upward in steps, holds
each step long enough to judge it, and reports the largest concurrency at
which the world's tick cadence stayed stable and no viewer fell behind —
plus the full curve of how each measure changed as the load grew.

**Why this priority**: This is the question that motivated the tool. A single
unattended run that answers "how many viewers, on this hardware" is the MVP;
every other mode refines the picture around that number.

**Independent Test**: Start a local server, run a ramp to a modest target
(for example 200 viewers), and confirm the run completes unattended,
reports a ceiling (or reports that the target was reached without
degradation), and writes both a human-readable summary and a machine-readable
record.

**Acceptance Scenarios**:

1. **Given** a healthy local server, **When** the operator runs a ramp with a
   step size, hold duration, and target count, **Then** Clowder adds viewers
   on that schedule, holds each step for the configured duration, and reports
   per-step measurements up to the target or the first degraded step.
2. **Given** a ramp that reaches degradation, **When** the run ends, **Then**
   the report names the last healthy step, the first degraded step, and which
   measure degraded first (tick cadence, viewer lag, skipped updates,
   handshake failures, or disconnects).
3. **Given** a completed run, **When** the operator inspects the output,
   **Then** a summary is printed and a machine-readable record exists with
   fixed-interval rows (default 1 second) plus derived per-step and
   per-run summaries.

---

### User Story 2 - Characterize the failure (Priority: P2)

The operator wants to know not just where the server degrades but how.
Clowder's other traffic shapes each probe a distinct failure hypothesis:
a spike (all connections arriving at once) probes the handshake path; a
slow-consumer mix (some viewers reading slowly or not at all) probes whether
stalled viewers harm healthy ones; churn (constant connect/disconnect,
including the initial full-world fetch each new viewer performs) probes
setup/teardown cost; and a read-only poller mix probes the request path
alongside the push path.

**Why this priority**: "What are the failure characteristics" is the second
half of the original question. Each shape is independently valuable, and all
reuse the P1 machinery.

**Independent Test**: Run each mode against a local server at a fixed,
modest concurrency and confirm each produces a report with the same measures
as the ramp plus the mode's own specifics (for example: healthy-viewer lag
while stalled viewers are present).

**Acceptance Scenarios**:

1. **Given** a spike run of N connections, **When** the run completes,
   **Then** the report includes handshake latency distribution and the count
   of connections that failed to establish.
2. **Given** a slow-consumer run where a configured fraction of viewers stops
   reading, **When** the run completes, **Then** the report separates the
   measurements of healthy viewers from stalled ones, so harm to bystanders
   is directly visible.
3. **Given** a churn run at a configured connect/disconnect rate, **When**
   the run completes, **Then** the report includes connection setup cost over
   time and any drift in the world's tick cadence.
4. **Given** a mixed run with read-only pollers alongside viewers, **When**
   the run completes, **Then** poller request latency and error rates are
   reported beside the viewer measures.

---

### User Story 3 - Compare across versions (Priority: P3)

The operator keeps run records and wants tomorrow's numbers to be comparable
with today's: after an engine change, a config change, or new hardware, a
re-run of the same scenario should be attributable — same scenario, same
world shape, different engine — so a performance regression is visible as a
regression and not as noise.

**Why this priority**: Records that cannot be compared are screenshots, not
measurements. This is the house measurement discipline applied to load: every
report stamps what it measured and what it ran against.

**Independent Test**: Run the same scenario twice against the same server and
confirm the records carry identical identity stamps and agree on the ceiling
within the documented repeatability tolerance; alter the world config and
confirm the stamp visibly changes.

**Acceptance Scenarios**:

1. **Given** any completed run, **When** the record is inspected, **Then** it
   carries the target's world identity as served (world config identity,
   roster size, tick rate), the full scenario configuration, the tool's
   version, and the generator host's resource limits.
2. **Given** two runs of the same scenario against the same server and
   hardware, **When** their ceilings are compared, **Then** they agree within
   the documented repeatability tolerance.

---

### Edge Cases

- The server dies or restarts mid-run: tick numbers reset or the socket
  drops. The run must detect this, mark the run as interrupted, and preserve
  the measurements taken up to that point rather than reporting them as a
  degradation the traffic caused.
- The generator gives out before the server: file-descriptor limits, CPU, or
  bandwidth on the machine running Clowder. The run must detect its own
  bottlenecks and mark affected measurements as invalid, never attributing
  them to the server.
- A payload that cannot be parsed for a tick number (schema drift): the run
  aborts with an error naming the payload shape rather than recording
  garbage.
- The operator points Clowder at a remote host: refused unless an explicit
  acknowledgment flag is given; local targets are the default and require
  nothing. The live world is never a permitted target under any flag; this
  rule is stated in the tool's own documentation and usage text.
- A viewer connection is refused or drops mid-run at low concurrency (below
  any plausible ceiling): counted and reported as an anomaly, not silently
  retried.
- Zero-duration or zero-count configurations: rejected at startup with a
  message naming the field, matching the project's config-rejection
  convention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Clowder MUST establish and hold a configurable number of
  concurrent viewer connections, each behaving like the real viewer: one
  initial full-world fetch, then a subscription receiving the world after
  every tick.
- **FR-002**: Clowder MUST provide a ramp mode: concurrency grows by a
  configured step every configured interval, holding each step, up to a
  target or until a step fails the step-health definition (FR-016).
- **FR-003**: Clowder MUST provide a spike mode: N connections established as
  fast as the generator can issue them, measuring the handshake path.
- **FR-004**: Clowder MUST provide a slow-consumer mode: a configured
  fraction of viewers read slowly or stop reading entirely, while the
  remaining healthy viewers are measured separately.
- **FR-005**: Clowder MUST provide a churn mode: connections arrive and leave
  continuously at a configured rate, each arrival paying the real viewer's
  full setup cost.
- **FR-006**: Clowder MUST support a read-only poller mix: a configured rate
  of requests against the server's read endpoints running alongside any
  viewer scenario, with request latency and errors reported separately.
- **FR-007**: For every viewer connection, Clowder MUST measure: time to
  establish (handshake latency), updates received, skipped updates (derived
  from gaps in the tick numbers carried by consecutive payloads),
  inter-update arrival distribution, bytes received, and the reason the
  connection ended.
- **FR-008**: From any healthy connection, Clowder MUST derive the observed
  tick cadence of the world and report its stability over the run — the
  primary signal that traffic is harming the simulation itself.
- **FR-009**: All measurements MUST derive from what the server already
  serves. Clowder requires no server or engine modification, and this
  feature makes none.
- **FR-010**: Every run MUST produce a human-readable summary and a
  machine-readable record (one file per run) carrying: the full scenario
  configuration, the target's served world identity (world config identity,
  roster size, tick rate), the tool version, the generator host's resource
  limits, and a timestamp. Measurements are recorded as fixed-interval rows
  (default 1 second, configurable) on a single schema shared by every mode;
  per-step and per-run summaries are derived from the interval rows and
  included.
- **FR-011**: Clowder MUST detect generator-side bottlenecks (at minimum:
  file-descriptor exhaustion and inability to keep up with arriving data)
  and mark measurements taken under them as invalid in both outputs.
- **FR-012**: A run's report MUST classify observed degradation into named
  signatures — at minimum: skipped updates (graceful shedding), rising
  viewer lag, unstable tick cadence, handshake failures, connection drops,
  and server unresponsive.
- **FR-013**: Clowder MUST default to local targets. A non-local target
  requires an explicit acknowledgment flag. The tool's usage text MUST state
  that the live world is never a permitted target.
- **FR-014**: Clowder MUST exit with distinct codes for: run completed,
  run completed but invalidated by a generator-side bottleneck, run
  interrupted by target failure, and usage/configuration error — so
  scripted use can tell these apart.
- **FR-015**: A run MUST be fully described by its configuration: the same
  configuration against the same target and hardware is the same scenario,
  and the record contains everything needed to repeat it.
- **FR-016**: A ramp step is healthy iff, for the entire hold: healthy
  viewers record zero skipped updates, the observed tick cadence stays
  within a tolerance (default ±5%) of the world's nominal rate, no
  handshake fails, and no connection ends unexpectedly. Every threshold is
  a run parameter; the defaults define the published ceiling, and a record
  produced under non-default thresholds says so.

### Key Entities

- **Scenario**: a complete run configuration — mode, concurrency schedule,
  durations, fractions, poller rates, and target.
- **Run record**: the machine-readable output of one run — identity stamps,
  fixed-interval measurement rows (one schema for all modes), and the
  derived per-step and per-run summaries.
- **Connection observation**: the per-viewer measurement set (handshake
  latency, updates, skips, lag, bytes, end reason).
- **Degradation signature**: a named, reportable failure pattern (see
  FR-012) that summaries and records reference consistently.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single unattended ramp run against a local server answers
  "how many concurrent viewers, on this hardware" — reporting either the
  ceiling with the measure that gave out first, or that the target was
  reached healthy.
- **SC-002**: Each of the four traffic shapes (ramp, spike, slow-consumer,
  churn) and the poller mix produces a report classifying degradation into
  the named signatures; no run ends with an unclassified failure.
- **SC-003**: Two runs of the same scenario against the same server and
  hardware agree on the ceiling within ±10%.
- **SC-004**: The feature ships with zero changes under `crates/` outside
  its own new code: engine, server, and existing test suites are untouched.
- **SC-005**: A baseline sanity scenario — 100 concurrent viewers against
  the default local world for two minutes — completes healthy under the
  FR-016 definition at default thresholds on development hardware, and this
  scenario is documented as the tool's smoke test.
- **SC-006**: A stalled viewer harms only itself: in the slow-consumer
  scenario at baseline concurrency, healthy viewers show zero skipped
  updates while stalled viewers show skips — demonstrating (or refuting,
  reportably) the server's slow-client shedding design.

## Assumptions

- Every world payload carries the current tick number, and tick numbers
  increase monotonically while a single world runs. A reset is treated as a
  server restart (edge case above), not as data.
- The tool is target-shape agnostic: it measures whatever URL it is pointed
  at (bare server or behind a reverse proxy), and the difference between
  those two shapes is itself a thing operators will measure. Environment
  discipline (which targets are appropriate) is enforced by FR-013's
  local-default plus documentation, not by network heuristics beyond
  local/non-local.
- The generator machine is expected to sustain more connections than the
  server's ceiling; when it cannot, FR-011's self-detection governs and the
  run says so.
- Results storage is the operator's choice: records are written to a
  configurable path, and committing them to the repository is a workflow
  decision outside this spec.
- Pass/fail gating is out of scope: Clowder is an instrument, not a gate.
  (If a future release process wants a load gate, it builds on Clowder's
  records; nothing here precludes that.)
- The read-only nature of the server's API (Article V) means load testing
  cannot corrupt a world; the risk being managed by FR-013 is service
  degradation for real viewers, not data integrity.
