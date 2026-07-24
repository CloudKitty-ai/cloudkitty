# Feature Specification: Proposal Boundary Hardening & External Behavior Plugins

**Feature Branch**: `016-behavior-plugins`

**Created**: 2026-07-23

**Status**: Draft

**Input**: User description: "Harden the whole proposal boundary + external behavior
plugins (ScriptBehavior / HttpBehavior), as one feature — the hardening is the
prerequisite half of the plugin work, not a separate spec." (Combined from the two
BACKLOG P2 entries: *Harden the whole proposal boundary* and *External behavior
plugins*.)

## Overview

This is the payoff of Article IV's design: behaviors are untrusted advisors, and
everything the engine needs to survive a hostile one — the time budget, panic
isolation, the circuit breaker, the `NeedsDriven` fallback — already exists. What
does not exist is any way for an advisor to live *outside the process*, and the
moment one does, untrusted bytes touch the action-proposal wire for the first
time. Today only one action shape (Play) parses that wire strictly; the rest have
never been asked what they do with a missing field, a wrong type, an unknown
value, or an extra key.

So this feature has two halves that only make sense together:

1. **Harden the proposal boundary.** Pin down exactly what the action wire
   accepts, shape by shape, and guarantee that anything malformed is rejected —
   resolving to the kitty's fallback decision, never silently reshaped into a
   legal (and possibly *rewarded*) action.
2. **Open the door.** Let an operator attach an out-of-process brain to a kitty —
   a local program or a remote service — speaking that now-hardened wire, with
   every existing Article IV protection applying unchanged. This is the door to
   "an LLM decides what the kitty does."

## Clarifications

### Session 2026-07-23

- Q: Is the HTTP transport in scope to build this sitting? → A: No — build
  ScriptBehavior only; HttpBehavior stays specced (User Story 3, FR-007) but is
  explicitly deferred to a future sitting, to begin once the script transport is
  satisfying in practice.
- Q: Does Article IV get a wording amendment in this change? → A: Yes — amend
  (constitution v1.2.0, same change per Governance). The amended article
  recognizes **both** safe resolutions for a failed or illegal proposal — the
  default built-in fallback behavior *and* the idle no-op — as constitutionally
  valid, since there are scenarios where each makes sense. The default
  resolution is the needs-based fallback behavior.
- Q: What is the script plugin's process lifecycle? → A: Long-running — the
  program is launched once, speaks one request/response exchange per decision
  (so it may keep state between decisions), and is relaunched if it exits.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A malformed proposal is never mistaken for a legal one (Priority: P1)

An operator (or a buggy external brain) sends the engine an action proposal that
is *almost* right: a chase with no target id, a meow with an unknown message
kind, a move with an extra unexpected field, a groom whose target is a string
instead of a number. The engine treats every such proposal as a failed proposal:
the kitty takes its fallback decision for that tick, exactly as if the advisor
had crashed. No malformed proposal is ever quietly coerced into a different,
legal action.

**Why this priority**: This is the prerequisite half. The plugin transport is the
first place untrusted bytes ever reach the action wire; writing the transport
before pinning down what the wire accepts is how the Play flatten bug happens in
five more places. It is also independently valuable — it turns the action wire
into a documented, tested contract.

**Independent Test**: Can be fully tested with no plugin code at all: a
round-trip and rejection test suite over the action wire, one per action shape,
proving well-formed proposals parse to exactly what was sent and malformed
variants are rejected (never reshaped).

**Acceptance Scenarios**:

1. **Given** any action shape, **When** a well-formed proposal for it is
   serialized and parsed back, **Then** the result is identical to what was sent
   (round-trip identity).
2. **Given** a proposal with an unknown action kind, a missing required field, a
   wrong-typed field, an unrecognized enum value, or an extra unknown field,
   **When** it is parsed, **Then** parsing fails — it does not produce any legal
   action.
3. **Given** an advisor whose proposal failed to parse, **When** the tick
   resolves, **Then** the kitty's turn is taken by its fallback decision (the
   same path as a crashed advisor), the tick completes normally, and the outcome
   is observable as a fallback in the decision's provenance.
4. **Given** a *well-formed* proposal that is illegal for the current world state
   (e.g., chasing an element that no longer exists), **When** it is validated,
   **Then** it resolves to an idle turn, exactly as today (the two layers stay
   distinct: unparseable → fallback decides; well-formed-but-illegal → idle).

---

### User Story 2 - A local program drives a kitty (Priority: P2)

An operator writes a small program in any language — a script, a compiled tool,
an LLM harness — and attaches it to one kitty via configuration. Each decision,
the program receives everything a built-in behavior may know (the kitty's own
state, the start-of-tick world snapshot, the kitty's private deterministic
randomness for the tick, relevant configuration) and replies with one proposed
action on the hardened wire. The kitty comes alive under external control; the
other kitties and the world notice nothing unusual.

**Why this priority**: This is the feature's reason to exist and the reference
transport. A local program is the simplest possible external brain: no network,
no service to stand up, trivially demonstrable.

**Independent Test**: Attach a sample program that proposes sensible actions;
observe the kitty following them across a sustained run, with the decisions
attributed to the plugin. Attach a garbage-emitting program; observe the kitty
falling back every tick while the world runs on undisturbed.

**Acceptance Scenarios**:

1. **Given** a kitty configured to use a local-program behavior, **When** the
   program replies with well-formed, legal proposals, **Then** those actions are
   applied to the kitty and attributed to the external advisor.
2. **Given** the same kitty, **When** the program replies with garbage
   (malformed bytes, unknown shapes, oversized output) or crashes or hangs,
   **Then** the kitty takes its fallback decision, the tick loop is never
   stalled beyond the standing budget, and the world's invariants all hold.
3. **Given** a configuration whose plugin definition is detectably broken at
   startup (e.g., the program does not exist), **When** the server starts,
   **Then** startup fails with a clear error naming the problem — a config
   error, not a per-tick surprise.
4. **Given** a world with no plugin configured, **When** it runs, **Then**
   nothing external is ever launched and behavior is identical to today.

---

### User Story 3 - A remote service drives a kitty (Priority: P3 — deferred, not built this sitting)

An operator points a kitty's behavior at a remote HTTP endpoint instead of a
local program. Each decision is a request carrying the same context a local
program would receive; the response is one proposed action on the same wire. All
the same protections apply: an unreachable, slow, or garbage-speaking endpoint
costs its kitty a moment of cleverness and nothing more.

**Why this priority**: The second transport. It shares the entire contract,
hardening, and failure model with User Story 2 and differs only in how the
bytes travel. **Deferred by clarification (2026-07-23)**: this sitting builds
the script transport only; the remote transport is implemented in a future
sitting once the script transport is satisfying in practice. The story remains
in the spec because the contract and failure model below MUST NOT assume a
local process — nothing designed now may block this transport later.

**Independent Test**: Attach a stub HTTP server that proposes actions; observe
the kitty following them. Stop the server mid-run; observe the kitty falling
back within the same tick and the world continuing without interruption.

**Acceptance Scenarios**:

1. **Given** a kitty configured with a remote behavior and a healthy endpoint,
   **When** the endpoint replies with well-formed, legal proposals within
   budget, **Then** those actions are applied and attributed to the external
   advisor.
2. **Given** the endpoint becomes unreachable, slow, or hostile mid-run,
   **When** decisions are gathered, **Then** the kitty takes its fallback
   decision within the standing budget, the tick loop never stalls, and the
   circuit breaker benches repeat offenders exactly as it does for any external
   advisor.

---

### User Story 4 - A plugin author succeeds from the docs alone (Priority: P4)

Someone who has never read the engine source sits down with the plugin
documentation and writes a working brain. The docs give them the complete wire
contract (every action shape's accepted form, with examples of accepted and
rejected proposals), the decision context they will receive, the lifecycle and
budget rules, and — prominently — the multi-agent livelock warning: all kitties
decide against the same start-of-tick snapshot, so a deterministic external
brain that mirrors another kitty's moves can dance with it forever; break
symmetry with the per-kitty randomness or an id-based right-of-way rule, as the
built-ins do.

**Why this priority**: Documentation is what turns a mechanism into a feature
other people can use — but it can only be finished last, when the contract it
documents is settled.

**Independent Test**: The documentation exists, covers every action shape and
the full decision context, includes at least one worked end-to-end example, and
carries the livelock warning with the symmetry-breaking advice.

**Acceptance Scenarios**:

1. **Given** the shipped documentation, **When** a reader follows it, **Then**
   every accepted proposal shape is specified with examples, and each documented
   example parses exactly as documented (docs examples are covered by tests).
2. **Given** the shipped documentation, **When** a reader looks for guidance on
   multi-kitty coordination, **Then** the livelock warning and symmetry-breaking
   advice are present.

---

### Edge Cases

- A proposal that is valid JSON but not an object (a bare string, number, or
  array), an empty reply, or bytes that are not JSON at all → failed proposal,
  fallback decides.
- A proposal with a correct shape but an out-of-range or unknown-entity id →
  parses (the wire cannot know the world), then resolves to idle at validation,
  exactly as today.
- A `purr` proposal: purring was retired as an action (spec 011). The shape is
  still recognized on the wire, and validation resolves it to idle — a stale or
  confused advisor is not a parse error.
- A reply that does not belong to the request it answers — an extra line, a
  stale answer, a reply meant for another kitty on a shared advisor → every
  reply must echo which decision it answers; a mismatch is a failed proposal
  and resynchronizes the advisor (restart), so a stale-but-legal proposal can
  never be applied to the wrong tick or the wrong kitty. One decision means
  one reply.
- An absurdly large reply → treated as a failed proposal at a documented size
  bound; an external brain cannot exhaust the engine's memory by talking too
  much.
- A reply that arrives after the budget has expired → already handled: the
  fallback has taken the turn; the late answer is discarded.
- A plugin process that dies mid-run, or an endpoint that disappears → every
  affected decision falls back; the world never stalls or crashes; recovery is
  automatic — the engine relaunches an exited long-running program, and the
  circuit breaker's bench expires on its own. A program crash-looping at launch
  must not become a spawn storm: relaunch attempts are bounded in frequency
  (the bench already provides this shape).
- Two external brains mirroring each other → the engine cannot prevent a
  livelock dance any more than it can for adversarial built-ins; the docs carry
  the warning and the symmetry-breaking pattern (this is a documentation
  requirement, not an engine guarantee).
- A world with plugins is **not** covered by the determinism guarantee — Article
  V promises determinism for built-in behaviors, and external processes are
  outside it by nature. Worlds with no plugins configured must remain exactly as
  deterministic as before.

## Requirements *(mandatory)*

### Functional Requirements

**The hardened wire (User Story 1)**

- **FR-001**: The action-proposal wire MUST have a documented contract covering
  every action shape: exactly which fields each accepts, which are required,
  and what values are recognized. The contract is the single source of truth
  for what external advisors may send.
- **FR-002**: The wire MUST reject malformed proposals for **every** action
  shape — not just Play. Rejected forms include, at minimum: an unknown action
  kind, a missing required field, a wrong-typed field, an unrecognized value
  for a closed set (direction, meow kind, target kind), an incomplete target,
  and an unknown or extra field. Rejection means parsing fails; a malformed
  proposal MUST NOT parse into any legal action.
- **FR-003**: A proposal that fails to parse MUST resolve to a
  constitutionally safe outcome — never to a reshaped legal action, never an
  error state, never a stalled tick. Two safe outcomes exist (per the amended
  Article IV): the kitty's **fallback decision** (the default built-in,
  needs-based behavior deciding from the kitty's dealt seed) and the **idle
  no-op**. The default for an unparseable proposal is the fallback decision —
  the same path as a crashed or absent advisor.
- **FR-004**: Well-formed proposals that are illegal for the current world
  state MUST continue to resolve to idle through engine validation, unchanged —
  the scenario where the idle no-op is the right safe outcome. The two layers
  MUST remain distinct and each observable: parse rejection in decision
  provenance and the rejection log (with the parse error), validation
  rejection as the applied idle turn (validation runs after dispatch and is
  outside provenance's view — the existing engine behavior).
- **FR-005**: Every action shape MUST be covered by automated round-trip tests
  (a well-formed proposal parses back to exactly what was sent) and rejection
  tests (each malformed variant class from FR-002 fails to parse). The
  existing Play tests are the template.

**External advisors (User Stories 2 & 3)**

- **FR-006**: An operator MUST be able to attach an external local program as a
  kitty's behavior through configuration alone — no engine changes, no
  recompilation. The program is **long-running**: launched once, it answers one
  request/response exchange per decision and may keep state between decisions
  (an LLM harness keeps its conversation; a policy keeps its weights loaded).
  If it exits, its kitty's decisions fall back and the engine relaunches it;
  recovery is automatic, and a program that dies repeatedly costs its kitty
  cleverness — never the tick loop.
- **FR-007** *(deferred — future sitting)*: An operator MUST be able to attach
  a remote HTTP endpoint as a kitty's behavior through configuration alone,
  speaking the same contract as a local program. Not built this sitting; the
  contract, decision-context format, and failure model delivered now MUST be
  transport-agnostic so this drops in later without reworking either.
- **FR-008**: An external advisor MUST receive, for each decision, the same
  information a built-in behavior may know and no more: the deciding kitty's
  own state, the start-of-tick world snapshot, the kitty's private
  deterministic randomness for the tick, and the relevant configuration — in a
  documented format. External advisors MUST NOT receive any channel for
  mutating the world; their only output is one proposed action.
- **FR-009**: Every existing Article IV protection MUST apply to external
  advisors unchanged and without new code paths per transport: the wall-clock
  decision budget, panic/crash isolation, the per-kitty circuit breaker with
  expiring bench, and the fallback rule (fallback decides from the kitty's
  dealt seed).
- **FR-010**: No failure mode of an external advisor — crash, hang, garbage
  output, oversized output, unreachable endpoint, slow endpoint, death
  mid-run — may affect anything beyond the advised kitty's cleverness on the
  affected ticks. The tick loop, the other kitties, and every constitutional
  invariant MUST be unaffected. External advisor replies MUST be read under a
  documented size bound; an oversized reply is a failed proposal.
- **FR-011**: Plugin configuration errors that are detectable at startup (a
  program that does not exist, an unparseable endpoint definition) MUST fail
  startup with a clear error. Conditions only discoverable at runtime (an
  endpoint that is down) are per-tick fallbacks, not startup errors.
- **FR-012**: Worlds with no external advisor configured MUST behave exactly as
  today: nothing external is launched, no network activity occurs, and the
  determinism guarantee for built-in behaviors is byte-for-byte unaffected.
- **FR-013**: Whether an external advisor's proposal was applied, fell back at
  parse, fell back at budget/crash, or was idled at validation MUST be
  observable by the operator (provenance and logs), so a misbehaving plugin is
  diagnosable without reading engine source.
- **FR-014**: External advisor configuration (program paths, endpoint
  addresses) MUST NOT be exposed through the public read-only API, matching
  the existing treatment of RL policy configuration.

**Documentation (User Story 4)**

- **FR-015**: Plugin documentation MUST ship with the feature and cover: the
  full wire contract with accepted and rejected examples per action shape, the
  decision context format, lifecycle and budget/bench rules, failure semantics
  (what happens to a bad proposal), and a worked end-to-end example.
- **FR-016**: The documentation MUST carry the multi-agent livelock warning:
  that all kitties decide against the same start-of-tick snapshot, that
  deterministic mutually-reacting brains can mirror each other indefinitely,
  and that authors should break symmetry via the per-kitty seeded randomness
  or an id-based right-of-way rule.

**Governance (Clarifications 2026-07-23)**

- **FR-017**: Article IV MUST be amended in this same change (per Governance:
  constitution, spec, and guarding tests together) to state the resolution
  rule explicitly: an invalid, malformed, late, or absent proposal resolves
  safely to either the default built-in fallback behavior or the idle no-op —
  both constitutionally safe outcomes — with the needs-based fallback as the
  default resolution. Never an error state, never a rule violation, never a
  reshaped legal action.

### Key Entities

- **Proposal**: the wire form of one intended action, produced by an advisor for
  one kitty for one tick. Either parses to exactly one action or fails.
- **Wire contract**: the documented set of accepted proposal shapes — the
  boundary between the untrusted outside and the sovereign engine.
- **External advisor (plugin)**: an out-of-process decision-maker attached to a
  kitty by configuration; a local program or a remote service. Untrusted by
  design.
- **Decision context**: the read-only information handed to an advisor for one
  decision: own state, world snapshot, per-tick private randomness, config.
- **Fallback decision**: the built-in default behavior's choice for the tick,
  taken from the kitty's dealt seed whenever the advisor's proposal fails.
- **Provenance**: the per-decision record of who actually decided (advisor,
  fallback) and, with this feature, why.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The entire pre-existing automated test suite (welfare property
  tests, determinism suite, fairness tests) passes unchanged with the feature
  merged.
- **SC-002**: Every action shape has passing round-trip and rejection coverage;
  across the full malformed-variant matrix (unknown kind, missing field, wrong
  type, unrecognized value, incomplete target, extra field — per shape), zero
  malformed proposals parse into a legal action.
- **SC-003**: A hostile external advisor emitting malformed output every
  decision for at least 1,000 consecutive ticks: every tick completes, every
  constitutional invariant holds, and every affected decision is recorded as a
  fallback.
- **SC-004**: A well-behaved reference plugin drives a kitty for at least one
  full in-world day with its proposals applied and attributed to it in
  provenance.
- **SC-005**: Killing an external advisor mid-run (process killed, endpoint
  stopped) causes zero missed ticks and zero invariant violations; the advised
  kitty's decisions fall back within the standing budget from the first
  affected tick.
- **SC-006**: With no plugins configured, a fixed seed and configuration
  produce a world state identical to the pre-feature build at the same tick
  count.
- **SC-007**: The shipped documentation specifies the accepted wire form of
  every action shape, and every example in it is verified by a test.

## Assumptions

- **Plugins are exempt from the determinism guarantee.** Article V scopes
  determinism to built-in behaviors; an external process's answers are
  inherently outside the seed. What this feature preserves is determinism of
  everything *around* the advisor (seeds dealt, fallback decisions, engine
  resolution) and byte-identical behavior for plugin-free worlds.
- **Plugins run with the operator's own privileges.** Article IV protects the
  *world* from a hostile advisor; it does not sandbox the advisor's process
  from the host machine. Operators attach programs they trust to run — same
  stance as any other program they choose to execute. OS-level sandboxing is
  out of scope.
- **Two transports are specified; only the local program is built this
  sitting.** Clarified 2026-07-23: the remote (HTTP) transport is deferred to a
  future sitting, to begin once the script transport is satisfying in practice.
  Its story and requirement stay in this spec as the transport-agnosticism
  constraint on what is built now.
- **The RL path is untouched.** Spec 014's integer action codec remains the RL
  control surface; this feature's JSON wire is for out-of-process advisors,
  not for training. Nothing in this feature changes the codec, the budgetless
  resolver's semantics, or the Python surface frozen in spec 015.
- **The serving deployment is unaffected by default.** The public viewer
  deployment runs no plugins; with none configured, no new processes, sockets,
  or dependencies are active (and FR-014 keeps plugin config out of the public
  API).
- **One kitty, one advisor.** An advisor is attached per kitty via the existing
  behavior-name selection; orchestrating multiple kitties from one external
  brain is possible (attach it to each) but no new coordination surface is
  introduced.
- **Reasonable resource bounds are defaults, not new configuration surface
  area** unless the design phase finds they must be tunable; if made
  configurable they follow Article VI (documented defaults in configuration,
  no magic numbers).
