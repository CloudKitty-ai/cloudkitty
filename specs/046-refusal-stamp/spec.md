# Feature Specification: Refusal Stamp

**Feature Branch**: `046-refusal-stamp`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Owner-ruled fast-follow (2026-08-28,
`experiments/ROADMAP.md` §pre-fog candidates; unblocked by the 041+bump
soak PASS 2026-09-01, relayed by Experiments): the engine records each
REFUSAL into the event stream — (kitty, proposed action, tick). Additive
API, zero dynamics change, NOT wall-gated, its own small spec/PR. Same
delivery class as 041's FR-011 tier counters: serde-default additive
fields / additive event kind, F-029 emit-proof reading (show it can emit
before anyone reads a zero). Experiments needs per-seat, per-tick
attribution — which kitty was refused, what it proposed, which tick —
for (1) the live post-041 refusal baseline before the step-5 refusal pin
(INVESTIGATE tier: refusal-tax share >10% of a seat's ticks; lab pre-041
read was Biscuit 4.6%, F-033) and (2) the Biscuit 3.0 comfort sweep's
roster-wide refusal rates, replacing the idle_seam.py probe and its
`survived` traps. Sizing caution: refusals are per-tick events, ~4.6% of
a seat's ticks vs one activity-end per finished scene — a 1000-event
ring rolls over in ~4k ticks on a 5-seat roster; ring capacity and the
serving endpoint need their own line. Whether the stamp carries the
proposed TARGET is Product's call; Experiments would use it if present."

## What counts as a refusal *(scope ruling)*

A **refusal** is the Article IV enforcement event: the engine resolving
a non-Idle proposal to Idle because the proposal was illegal against the
live world (`action::validate`, the single enforcement surface). This is
exactly the F-033 tax mechanism — the mask probes the frozen
start-of-tick snapshot, the world moves before the kitty's apply slot,
and the proposal that was legal when scored is refused when heard.

Explicitly **not** refusals:

- A proposed Idle. Idle is always legal; a chosen idle is the 55% side
  of F-033's 55/45 split and must never pollute the 45% side.
- Duration enforcement. Inside a scene's minimum the engine continues
  the scene whatever was proposed; the kitty keeps a serviced scene and
  loses nothing, so no tax accrues and no event is recorded.
- Message downgrades. An illegal message resolves to Silent on a
  separate channel with its own semantics (spec 028); the stamp records
  activity refusals only.

Refusals are recorded for **every kitty on every tick driver** —
behavior-driven serve loop and joint-proposal seam alike, scripted and
policy seats alike. The recording site is the one shared apply pipeline,
so the two drivers can never drift.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Per-tick refusal attribution in the event stream (Priority: P1)

Experiments takes the live post-041 refusal baseline: for each refused
proposal the world records who was refused, what they proposed
(including the proposed partner or target when the action names one),
and on which tick — kept in a bounded ring like distress and
activity-end events, and served at its own endpoint.

**Why this priority**: This is the feature. The step-5 refusal pin
(INVESTIGATE at >10% of a seat's ticks) needs a live baseline the seam
probe cannot honestly provide, and the Biscuit 3.0 comfort sweep reads
roster-wide refusal rates off this stream.

**Independent Test**: Drive a world into a known refusal (two kitties
proposing moves into the same cell; the second in turn order is
refused) and read the event back with the correct kitty, proposal, and
tick — first from the world's ring, then over the serving endpoint.

**Acceptance Scenarios**:

1. **Given** a kitty whose non-Idle proposal is refused by validation,
   **When** the tick completes, **Then** the refusal ring holds one new
   event carrying that kitty's id, the proposed action verbatim, and
   the tick number.
2. **Given** a kitty that proposes Idle, **When** the tick completes,
   **Then** no refusal event is recorded for it.
3. **Given** a kitty inside a scene's minimum whose different-action
   proposal is overridden by duration enforcement, **When** the tick
   completes, **Then** no refusal event is recorded for it.
4. **Given** a refused partnered proposal (e.g. Play naming a partner),
   **When** the event is read back, **Then** the proposed action carries
   the named partner — per-seat attribution includes who was asked.
5. **Given** the same seeded world driven once by the behavior loop and
   once through the joint-proposal seam with identical decisions,
   **When** both runs complete, **Then** their refusal streams are
   identical.
6. **Given** a freshly booted world in which no refusal has occurred,
   **When** the stream is read, **Then** it is empty — and the F-029
   emit-proof scenario (scenario 1) is what licenses reading that zero
   as evidence.

---

### User Story 2 - A ring sized for the live baseline window (Priority: P2)

Refusals are far denser than any existing event kind: the pre-041 lab
read was ~4.6% of a seat's ticks (F-033), so a 5-seat roster produces
roughly 0.23 refusals per tick — a 1000-event ring (the distress and
activity default) would roll over in ~4,300 ticks. The refusal ring gets
its own retention knob with a default sized so a census polling at the
established cadences loses nothing.

**Why this priority**: Without the sizing line the stamp silently
undercounts at exactly the density it was built to measure — the F-029
lesson (an instrument must be shown able to hold what it claims to
count) applied to capacity instead of emission.

**Independent Test**: Configure a small retention, drive more refusals
than it holds, and verify the ring keeps the most recent events, oldest
dropped first; verify the default retention holds a ≥15,000-tick window
at the measured density.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** refusals accrue at the
   measured roster density (~0.23/tick), **Then** the ring retains at
   least a 15,000-tick window before the oldest event is dropped.
2. **Given** a config that sets the refusal retention explicitly,
   **When** the world records past capacity, **Then** the ring holds
   exactly the configured count, newest kept.
3. **Given** a config with retention 0, **When** the config loads,
   **Then** it is rejected with the same row-shaped error as the other
   retention knobs (spec 020 D2).

---

### User Story 3 - Additive delivery: nothing else moves (Priority: P1)

The stamp is an observation, not a rule change. Dynamics, masks,
selection, needs, and the served visual world are byte-identical to the
pre-stamp build; old snapshots and configs load unchanged; the config
stamp does not move.

**Why this priority**: The soak just passed and the fog timeline rides
on this roster's stability — the stamp lands only because it provably
changes nothing a kitty can feel. Co-P1 with US1: emit-proof and
no-dynamics-change are jointly the acceptance bar.

**Independent Test**: Seeded twin runs on the pre- and post-stamp build
(or with the ring field ignored) produce identical need traces,
positions, actions, and messages; a pre-046 world save and the served
config both parse and resume.

**Acceptance Scenarios**:

1. **Given** the same seed and config, **When** a world runs with the
   stamp present, **Then** every kitty's needs, position, activity, and
   message trace is identical to the pre-stamp build's — the recording
   site only observes.
2. **Given** a pre-046 world save (no refusal ring in the payload),
   **When** it is loaded, **Then** it parses and resumes; the ring
   starts empty with a bounded default capacity (degrading to a ring of
   one like the other logs' serde-default, never unbounded).
3. **Given** the served config file as deployed today, **When** parsed
   by the new build, **Then** it loads without edits and the config
   stamp is unchanged (the new retention knob is serde-defaulted and
   absent-at-default from serialized form).
4. **Given** the RL feature/mask surface, **When** the stamp is present,
   **Then** no observation, mask, or action-space shape changes — no
   policy reads refusal events in this spec.

---

### Edge Cases

- A proposal refused for a *dead* counterpart (partner despawned
  mid-scene) records the refusal like any other — the proposed action
  still names the departed partner, which is honest attribution.
- Multiple kitties refused on the same tick each record their own
  event; ring order within a tick follows the tick's turn order (the
  order refusals were heard).
- A stray legacy proposal (Meow-as-activity, Purr) that validation
  resolves to Idle **is** a refusal and is recorded — the stamp reports
  the enforcement surface faithfully rather than special-casing
  variants; consumers filter by action kind if they wish.
- World saved mid-window then resumed: the ring round-trips through
  persistence so the census does not lose the window across a restart.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The world MUST record one refusal event per validation
  refusal — a non-Idle proposal resolved to Idle by the enforcement
  surface — carrying the refused kitty's id, the proposed action
  verbatim (any `with`/`target` the proposal named included), and the
  tick. No other pathway (chosen Idle, duration enforcement, message
  downgrade) may emit one.
- **FR-002**: Recording MUST happen at the shared apply pipeline so the
  behavior-driven and joint-proposal tick drivers produce identical
  streams for identical decisions.
- **FR-003**: Refusal events MUST live in a bounded ring (newest kept,
  oldest dropped) with its own retention knob in the events
  configuration, serde-defaulted so every existing config parses
  unchanged and the config stamp does not move. Retention 0 MUST be
  rejected at load with the spec 020 D2 row shape.
- **FR-004**: The default retention MUST hold at least a 15,000-tick
  window at the measured roster density (~0.23 refusals/tick on 5
  seats), i.e. at least 3,500 events; the spec's sizing line is
  **4,000** unless the plan surfaces a cost that forces revisiting.
- **FR-005**: The server MUST serve the ring at its own endpoint
  (`/events/refusal`), mirroring the activity-end endpoint's shape:
  full ring, oldest first.
- **FR-006**: The refusal ring MUST ride the persisted world save
  additively: serde-default on read (pre-046 saves load, ring empty,
  capacity degrading to one like the sibling logs), present on write,
  so a saved-and-resumed world keeps its window. The served
  `WorldSnapshot` payload (`/world`, websocket frames) carries no event
  rings today and gains none — the endpoint is the only serving
  surface, matching the distress and activity-end pattern.
- **FR-007**: The stamp MUST NOT change dynamics: no need, position,
  activity, message, mask, observation, or selection behavior differs
  from the pre-stamp build under any config. It is not wall-gated and
  has no on/off switch — recording is unconditional, bounded by
  retention.
- **FR-008**: Emit-proof (F-029): the test suite MUST demonstrate the
  stream emitting at every layer a consumer reads — the engine ring and
  the serialized event payload — before any test or census asserts on
  an empty stream.

### Key Entities

- **Refusal event**: (kitty id, proposed action — verbatim, targets
  included —, tick). The honest record of one enforcement act.
- **Refusal ring**: bounded, config-sized event log of the most recent
  refusals, a sibling of the distress and activity-end rings.
- **Events configuration**: gains one retention knob for the refusal
  ring; existing knobs untouched.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A census can attribute every refusal in a 15,000-tick
  window to a seat, a proposed action, and a tick — per-seat refusal-tax
  share (the step-5 INVESTIGATE metric) is computable from the served
  stream alone, no seam probe.
- **SC-002**: A refused partnered proposal is attributable to the
  partner that was asked in 100% of cases where the proposal named one.
- **SC-003**: Seeded twin runs with and without the stamp code path
  active produce byte-identical kitty traces (needs, positions,
  actions, messages) for the full run.
- **SC-004**: The deployed config and a pre-046 world save both load
  without edits; the config stamp hash is unchanged.
- **SC-005**: At default sizing, polling the endpoint once per 10,000
  ticks observes every refusal at the measured density (no rollover
  loss).

## Assumptions

- The pre-041 density read (Biscuit 4.6% of ticks, F-033) is the best
  available sizing input; post-041 density is expected lower (rest's
  share of the tax was deleted), so 4,000 events is conservative in the
  safe direction. If the live baseline shows materially higher density,
  retention is a config knob — no code change needed.
- Serving and persisting a 4,000-event ring (~a few hundred KB) is
  acceptable at the established poll and persist cadences; the plan
  verifies against the actual persist path.
- The proposed target rides free because the proposed action is
  recorded verbatim (`Action` already carries `with`/`target`) — this is
  the Product call the relay asked for: **yes, the target is included**.
- No viewer/client work: the endpoint is a lab instrument; the client
  never reads it in this spec.
- The stamp does not record *why* a proposal was refused (which
  validation arm). Attribution of cause stays derivable from the world
  state at the tick; adding a reason code would be a follow-up if the
  census actually needs one.
