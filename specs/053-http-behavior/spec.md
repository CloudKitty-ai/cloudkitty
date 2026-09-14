# Feature Specification: HttpBehavior — the remote plugin transport

**Feature Branch**: `053-http-behavior`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "HttpBehavior — the remote plugin transport deferred from spec 016 (User Story 3 / FR-007). A thin second speaker of the existing transport-agnostic plugin contract: the same decision request and correlated reply envelope, carried to a configured remote endpoint instead of a local program's stdin/stdout. Everything hard already exists — the hardened proposal wire, the decision-context format, the budget/breaker/fallback stack — and was kept transport-agnostic on purpose. Start from specs/016-behavior-plugins/, not from scratch. Candidate fold-in: the three ScriptBehavior transport residuals from the 016 review (BACKLOG)."

## Clarifications

### Session 2026-09-11

- Q: Does this sitting take the ScriptBehavior transport residuals from the
  016 review, and which? → A: Fold all three (owner ruling A): fix
  residual 1 (process-group kill), doc-note residual 3 (exec-bit meaning),
  and disposition residual 2 (shared-plugin mutex burst) by explicit
  re-acceptance with its mitigation documented. The BACKLOG entry closes
  entirely with this feature.

### Session 2026-09-13 (design-doctrine check, CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md` (all ten rules banked
@ 30b6d54). Rules 6 and 10 change choices; recorded per rule 8:

- Q: Doctrine rule 6 classifies every seat as scripted (a rule a person
  wrote) or a mind (a trained policy or an LLM) — but remote code cannot
  be read. Where is the class declared? → A: In the plugin entry itself:
  a remote entry MUST declare scripted-vs-mind, no default (FR-015).
- Q: Do a mind seat's Article IV fallback turns count as the mind's own
  rows (rules 6/10 — the fallback rule deciding from the dealt seed is a
  rule a person wrote)? → A: No. Fallback turns are scripted rows
  regardless of the seat's declared class and are excluded from a mind
  seat's lineage rows; the FR-008 provenance distinction is the marker
  (FR-016).
- Q: Does 053 fold the three-tier fallback chain (LLM → local model →
  scripted)? → A: No (owner ruling 2026-09-13, relayed): the chain is
  deferred, bundled with the distress-gated intervention spec, to the
  LLM-seat sitting after the Gen 1 reseat. 053 keeps the existing
  Article IV budget/breaker/scripted-fallback shape (see Assumptions).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A remote service drives a kitty (Priority: P1)

An operator points a kitty's behavior at a remote endpoint instead of a local
program — through configuration alone, no engine changes, no recompilation.
Each decision travels as a request carrying exactly the context a local
program would receive; the response is one proposed action on the same wire,
in the same correlated envelope. When the endpoint answers well-formed, legal
proposals within budget, the kitty follows them and provenance attributes
them to the external advisor — indistinguishable, from the world's point of
view, from the same brain attached as a local script.

This discharges spec 016's deferred User Story 3 / FR-007: the second
transport, begun now that the script transport has proven satisfying in
practice (the condition the 2026-07-23 clarification set).

**Why this priority**: This is the feature. It turns "external brain" from
"a program on the server's own disk" into "any service the operator can
reach" — an LLM harness on another machine, a policy server with a GPU, a
teammate's experiment — without touching the engine or the box.

**Independent Test**: Attach a stub HTTP server that proposes actions;
observe the kitty following them, with provenance attributing each applied
decision to the advisor. Detach the plugin from the config; observe the
world byte-identical to a plugin-free run.

**Acceptance Scenarios**:

1. **Given** a kitty configured with a remote behavior and a healthy
   endpoint, **When** the endpoint replies with well-formed, legal proposals
   within budget, **Then** those actions are applied and attributed to the
   external advisor in provenance.
2. **Given** a config declaring a remote plugin, **When** the server starts,
   **Then** startup succeeds with no engine recompilation and the plugin is
   selectable as a behavior name exactly like a script plugin (same
   collision rule: a plugin may not shadow a builtin or policy name).
3. **Given** a config with a malformed endpoint declaration (unparseable
   address, both-or-neither transport fields), **When** the server starts,
   **Then** startup fails with a clear error naming the plugin entry
   (spec 016 FR-011: startup-detectable errors fail startup).
4. **Given** the same brain logic reachable both as a local script and as a
   remote endpoint, **When** each drives a kitty, **Then** both speak the
   identical documented contract — same request content, same reply
   envelope, same proposal wire — with no transport-specific dialect.

---

### User Story 2 - A failing endpoint costs one kitty a moment of cleverness, nothing more (Priority: P2)

The endpoint becomes unreachable, slow, hostile, or confused mid-run. Every
affected decision falls back within the standing budget; the tick loop never
stalls; the other kitties and every constitutional invariant are untouched;
the per-kitty circuit breaker benches repeat offenders exactly as it does
for any external advisor. Recovery is automatic when the endpoint returns —
no restart, no operator action.

**Why this priority**: Article IV containment is the license for having
plugins at all, and the network multiplies the failure modes (DNS, refused
connections, half-open sockets, slow bodies, proxies answering with the
wrong thing). Spec 016 FR-009/FR-010 demand these protections apply
"unchanged and without new code paths per transport" — this story proves it.

**Independent Test**: Drive a kitty from a stub server; stop the server
mid-run; observe fallback within the same tick and the world continuing
uninterrupted. Restart the stub; observe the kitty's cleverness return
(after any bench expires) with no engine intervention.

**Acceptance Scenarios**:

1. **Given** the endpoint becomes unreachable, slow, or hostile mid-run,
   **When** decisions are gathered, **Then** the affected kitty takes its
   fallback decision within the standing budget, the tick loop never
   stalls, and the circuit breaker benches repeat offenders exactly as for
   a script advisor.
2. **Given** an endpoint answering with garbage — non-JSON bytes, a
   mismatched envelope echo, an error status, an oversized body — **When**
   a decision is gathered, **Then** each such reply is a failed proposal
   resolving per Article IV (fallback), each observable in provenance and
   logs with its reason.
3. **Given** an endpoint that answers correctly but after the exchange
   deadline, **When** the reply arrives late, **Then** the fallback has
   already taken the turn and the late answer is discarded — never applied
   to a later tick.
4. **Given** a hostile endpoint misbehaving on every decision for 1,000+
   consecutive ticks, **When** the world runs, **Then** every tick
   completes, every constitutional invariant holds, and every affected
   decision is recorded as a fallback.

---

### User Story 3 - A plugin author targets the remote transport from the docs alone (Priority: P3)

Someone with the plugin documentation and no engine source builds a working
remote brain: the docs tell them how to declare the endpoint in config, what
each request contains, what shape the reply must take (the same envelope and
proposal wire the script transport documents), the budget/bench/failure
semantics, and the multi-agent livelock warning — extended, not duplicated:
one contract, two transports.

**Why this priority**: Documentation turns the mechanism into a feature
other people can use, and can only be finished when the transport's config
surface is settled. Spec 016 FR-015/SC-007 set the bar: every documented
example is verified by a test.

**Independent Test**: The shipped documentation covers the remote transport
end-to-end (declaration, request, reply, failure semantics, worked example)
and every example in it parses/behaves exactly as documented under test.

**Acceptance Scenarios**:

1. **Given** the shipped documentation, **When** a reader follows the remote
   transport section, **Then** the config declaration, request content,
   reply envelope, and failure semantics are each specified with examples,
   and each documented example is covered by a test.
2. **Given** the config reference table, **When** a reader looks up the
   remote transport, **Then** every remote-transport key appears with its
   default and meaning, alongside the existing `[plugins]`/`[behavior]`
   rows.

---

### User Story 4 - The script transport's accepted residuals are settled at this sitting (Priority: P4)

All three residuals from the 016 review's BACKLOG entry are in scope
(clarified 2026-09-11, owner ruling A). The operator who kills a wedged script plugin gets their OS thread back even
when a grandchild inherited the plugin's stdout; the operator reading the
startup validation docs learns the exec-bit check means "executable by
someone", not "by us"; the shared-plugin mutex burst is either re-accepted
with its mitigation documented or scheduled — the three 016-review residuals
stop being an open BACKLOG entry.

**Why this priority**: Housekeeping that shares this sitting's exchange
machinery; valuable but strictly severable from the transport itself.

**Independent Test**: Kill a wedged script plugin whose grandchild holds the
stdout pipe; observe no stranded I/O thread. Docs state the exec-bit check's
actual meaning.

**Acceptance Scenarios**:

1. **Given** a script plugin killed on timeout while a grandchild holds its
   stdout open, **When** the engine reaps the exchange, **Then** no I/O
   thread outlives the kill (the whole process group dies), across repeated
   relaunch cycles.
2. **Given** the plugin documentation, **When** a reader checks startup
   validation, **Then** the exec-bit note states the check is
   "executable by anyone", not "executable by the server's user".

---

### Edge Cases

- An endpoint that is down, unresolvable, or refusing connections at a
  decision → per-tick failed proposal and fallback, never a startup error
  and never a stall (runtime-only conditions per spec 016 FR-011).
- A reply with an error status, or a success status with an empty or
  non-JSON body → failed proposal, fallback decides.
- A reply whose envelope does not echo the decision it answers (wrong tick
  or wrong kitty — a proxy cache, a confused load balancer, a stale
  worker) → failed proposal; a stale-but-legal proposal is never applied to
  the wrong tick or kitty. One decision, one reply — same rule as spec 016.
- A redirect answer → treated as a failed proposal, not followed; the
  configured address is the contract, and silently following redirects
  would move the trust boundary.
- A reply body that exceeds the documented size bound, or that trickles in
  slowly past the exchange deadline → failed proposal at the bound or
  deadline; a remote brain cannot exhaust engine memory or time by talking
  too much or too slowly.
- A well-formed proposal that is illegal for the current world state →
  resolves to idle through engine validation, unchanged — the two layers
  (parse vs validation) stay distinct and observable, exactly as today.
- The same plugin name declared with both a local program and a remote
  endpoint, or with neither → startup error; one entry is exactly one
  transport.
- A world with only script plugins configured → behaves exactly as before
  this feature; a world with no plugins → byte-identical to the pre-feature
  build, zero network activity.
- A declared-mind remote seat spends a stretch benched by the circuit
  breaker → every turn in the bench window is a fallback row: scripted,
  never lineage; the seat's declaration does not launder them (FR-016).
- Worlds with remote plugins are outside the Article V determinism
  guarantee, exactly as script-plugin worlds already are; everything around
  the advisor (seeds dealt, fallbacks, resolution) stays deterministic.

## Requirements *(mandatory)*

### Functional Requirements

**The second transport (User Story 1)**

- **FR-001**: An operator MUST be able to attach a remote HTTP endpoint as a
  kitty's behavior through configuration alone — a plugin entry declaring an
  endpoint address in the same family as today's program-path entries, with
  no engine changes and no recompilation. This discharges spec 016 FR-007.
- **FR-002**: One plugin entry MUST declare exactly one transport: a local
  program (as today) or a remote endpoint — never both, never neither.
  Violations are startup errors naming the offending entry.
- **FR-003**: The remote transport MUST speak the identical contract as the
  local transport: the same documented decision request (wire version, tick,
  kitty identity, the kitty's own state, the start-of-tick snapshot, the
  private per-tick randomness, the served simulation config), the same
  strict reply envelope echoing the decision it answers, and the same
  hardened proposal wire. No transport-specific dialect on either side.
- **FR-004**: Remote plugins MUST register as behavior names under the same
  rules as script plugins: selectable by any kitty via the existing
  behavior-name selection, collision with a builtin or policy name refused
  at startup.
- **FR-005**: What is startup-detectable MUST fail startup with a clear
  error (an unparseable or unsupported endpoint address, a malformed entry);
  what is only discoverable at runtime (an endpoint that is down or
  unresolvable) MUST be a per-tick fallback, never a startup error
  (spec 016 FR-011 applied to this transport).

**Containment (User Story 2)**

- **FR-006**: Every Article IV protection MUST apply to remote advisors
  unchanged and without new per-transport code paths: the wall-clock
  decision budget, failure isolation, the per-kitty circuit breaker with
  expiring bench, and the fallback rule deciding from the kitty's dealt
  seed (spec 016 FR-009).
- **FR-007**: No failure mode of a remote endpoint — unreachable, refusing,
  slow, hung, garbage-speaking, oversized, mis-correlated, redirecting,
  error-answering, dying mid-run — may affect anything beyond the advised
  kitty's cleverness on the affected ticks (spec 016 FR-010). Replies MUST
  be read under the existing documented size bound and the existing
  exchange deadline; recovery when the endpoint returns MUST be automatic.
- **FR-008**: Whether a remote advisor's proposal was applied, fell back at
  parse/transport failure, fell back at budget, or was idled at validation
  MUST be observable in provenance and logs exactly as for script advisors
  (spec 016 FR-013), with transport failures carrying a diagnosable reason.

**Boundaries (both stories)**

- **FR-009**: Endpoint addresses and all plugin declarations MUST remain
  outside the public read-only API, the served `/config` document, and the
  engine-defaults stamp — the existing `[plugins]` server-owned treatment
  (spec 016 FR-014) extended to the new fields. The `/settings` block
  (spec 052) is likewise unaffected: no plugin key is a key setting.
- **FR-010**: Worlds with no plugins configured MUST behave byte-for-byte
  as today — nothing launched, zero network activity, determinism for
  built-in behaviors unaffected (spec 016 FR-012). Worlds with only script
  plugins MUST behave exactly as before this feature. No engine semantic,
  RNG draw, reward term, or served-config byte moves: the fog shakeout,
  goldens, corpus, and clone streams are unaffected by construction.

**Documentation (User Story 3)**

- **FR-011**: The plugin documentation MUST gain the remote transport as an
  extension of the one contract — declaration and config reference, request
  and reply semantics, failure semantics, budget/bench interaction, and a
  worked end-to-end example — without duplicating the shared contract
  sections. Every documented example MUST be verified by a test
  (spec 016 FR-015/SC-007 bar).

**Script-transport residuals (User Story 4)**

- **FR-012**: Killing a script plugin on timeout MUST end
  its whole process group, so a grandchild holding the plugin's stdout
  cannot strand the engine's I/O thread; the lifecycle documentation and
  code commentary MUST stop claiming the thread is freed the moment the
  stream closes. Lifecycle only — no decision semantics change.
- **FR-013**: The startup exec-bit validation MUST be
  documented as checking "executable by anyone", not "executable by the
  server's user"; a program executable only by another user passes startup
  and fails at spawn, which the docs must say out loud.
- **FR-014**: The shared-plugin mutex burst residual is dispositioned as
  re-accepted (clarified 2026-09-11): its mitigation (`exchange_timeout_ms`
  tuning for shared processes) MUST be documented where operators will find
  it, and no code change is made for it — so the BACKLOG entry closes with
  this feature.

**Seat classification (design doctrine rules 6 & 10; User Stories 1–2)**

- **FR-015**: Every remote plugin entry MUST declare whether the advisor
  behind the endpoint is scripted (a rule a person wrote) or a mind (a
  trained policy or an LLM), with no default — remote code cannot show
  which it is, so an undeclared remote entry is a startup error naming the
  entry. A script plugin entry MAY carry the same declaration and defaults
  to scripted (today's presumption; existing configs stay valid unchanged).
  The declared class MUST be observable wherever the advisor's decisions
  are attributed, so corpus and lineage tooling can classify rows without
  reading the server's config; the declaration is a server-owned plugin
  field like the rest of the entry (FR-009 — never served).
- **FR-016**: An Article IV fallback turn is a scripted turn regardless of
  the seat's declared class: the fallback rule deciding from the kitty's
  dealt seed is a rule a person wrote. Fallback rows are therefore excluded
  from a mind seat's lineage rows, and the seat's declaration never
  reclassifies them. The FR-008 provenance distinction (applied vs
  fallback vs idled) is the marker this exclusion keys on; no new marking
  surface is introduced.

### Key Entities

- **Remote plugin entry**: a plugin declaration whose transport is an
  endpoint address rather than a program path; same name-registration,
  same secrecy (never served), same one-kitty-one-advisor attachment.
- **Decision exchange**: one request/one correlated reply per decision —
  the transport-agnostic unit both transports speak; over the remote
  transport, one request to the configured endpoint and its one response.
- **Failed proposal**: any exchange outcome that is not a well-formed,
  correctly-correlated, within-bounds reply — resolved per Article IV,
  identically across transports.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The entire pre-existing automated test suite passes unchanged
  with the feature merged.
- **SC-002**: A well-behaved stub endpoint drives a kitty for at least one
  full in-world day with its proposals applied and attributed to it in
  provenance (spec 016 SC-004, remote analog).
- **SC-003**: A hostile or absent endpoint (garbage replies, error statuses,
  refused connections, mid-run shutdown) across at least 1,000 consecutive
  affected ticks: every tick completes, every constitutional invariant
  holds, every affected decision is recorded as a fallback, and fallback
  latency stays within the standing budget from the first affected tick
  (spec 016 SC-003/SC-005, remote analog).
- **SC-004**: With no plugins configured, a fixed seed and configuration
  produce a world state identical to the pre-feature build at the same tick
  count; with only script plugins configured, script-transport behavior is
  unchanged (spec 016 SC-006 extended).
- **SC-005**: The public read-only API and the served config document are
  byte-identical before and after a remote plugin is declared in the
  server's TOML; no endpoint address is recoverable from any served
  surface.
- **SC-006**: Every remote-transport example in the shipped documentation is
  verified by a test; the config reference covers every new key with its
  default.
- **SC-007**: Killing a wedged script plugin whose
  grandchild holds its stdout leaves zero stranded engine threads, across
  repeated relaunch cycles.

## Assumptions

- **The config surface extends the existing `[plugins.<name>]` family** — a
  remote entry is the same kind of block with an endpoint address in place
  of a program path, keeping one declaration surface, one collision rule,
  and one secrecy rule. The exact key name and accepted address forms are
  design-phase decisions.
- **Existing knobs govern; no new tunables unless design finds they must
  exist.** The exchange deadline (`exchange_timeout_ms`), reply size bound
  (`reply_max_bytes`), budget, strikes, and bench are transport-agnostic
  `[behavior]` settings and apply to the remote transport as-is — same
  stance as spec 016's resource-bounds assumption. If any remote-only knob
  proves necessary it follows Article VI (documented default, no magic
  numbers).
- **Trust stance unchanged.** Operators attach endpoints they trust to
  answer, exactly as they attach programs they trust to run (spec 016's
  operator-privileges assumption). No authentication, credential, or
  header-injection surface is introduced this sitting; an operator needing
  auth fronts the endpoint themselves. Plain and secured endpoints are both
  acceptable address forms if the design supports them cheaply.
- **One decision, one exchange, no pipelining.** The engine issues one
  request per decision and reads its one response; correlation is still
  verified by the envelope echo even where the transport appears to
  guarantee it — proxies and middleboxes are why the rule exists.
- **Article IV's shape is frozen this sitting.** The three-tier fallback
  chain (LLM → local model → scripted) and the distress-gated intervention
  spec are deferred, bundled together, to the LLM-seat sitting after the
  Gen 1 reseat (owner ruling 2026-09-13; evidence and design note in
  `BACKLOG.md` §Distress-gated intervention). 053 extends who can speak to
  the existing budget/breaker/scripted-fallback stack; it does not reshape
  it.
- **Nothing deploys from this arc.** The serving deployment runs no
  plugins; the fog shakeout, its arms, and the box are untouched (house
  rule: nothing deploys, never tag).
- **Determinism exemption carries over.** Worlds with remote plugins are
  outside the Article V guarantee exactly as script-plugin worlds are;
  plugin-free determinism is preserved byte-for-byte.
