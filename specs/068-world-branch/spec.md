# Feature Specification: World Branch API (Snapshot, Restore and a One-Tick Proposal Override from Python)

**Feature Branch**: `product/068-world-branch`

**Created**: 2026-11-05

**Status**: Draft

**Input**: Owner kickoff 2026-11-05, her word in this session: "One
spec", answering Product's shaping question (one spec or two for the
state half and the override half), after her "Let's do it" to
Experiments the same day. The ask and its grounds arrived as
Experiments' relay of 2026-11-05 (recorded on their side in
`experiments/fog-gen2-timeline-2026-10-17.md` and the commit 4464488e
message); a relay is never a kickoff. Grounds verified by Product
against origin/main 87fae11e and 4464488e before this spec was written
(recorded under Assumptions, not redone here).

## Why now

The Gen 2 Phase 2 entry gate — the owner's one-tick counterfactual
screen, frozen in `experiments/gen2-prereg-2026-10-17.md` §A2′ item 2 —
asks, per kitty and per mini: restore a recorded tick, substitute one
kitty's act, step once, read needs and happiness, discard the branch.
The Python binding has no way to put a running world back to a recorded
tick: no snapshot, no clone, no state setter. A recorded world does
replay exactly from its config, seed and recorded covered-seat actions,
at about 20,000 ticks a second, so the gate runs by replay today on the
lab's pinned binding and nothing here is urgent. But a branch API
outlives this one gate: the correction follow-up arm, the F-074 and
F-075 drift monitors on rollouts, the Phase 1f composition question and
Gen 3's "what if she had done X" reads all want the same three moves —
hold a tick, branch it once, throw the branch away. Replay pays the
whole prefix for every branch; a snapshot pays it once.

The second half of the ask closes a gap replay cannot: today only a
policy-controlled seat's act can be substituted (through `step`). A
scripted seat's act — a builtin behaviour's, and the needy seat's in
particular — cannot be, because a needy seat refuses to be taken
external by construction (spec 067: a covered mind under a mask is never
allowed). The branch needs to substitute ONE tick's proposal for such a
seat without changing who controls it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hold a tick, branch it, and the branch continues exactly as the original would (Priority: P1)

An experimenter runs a single-world environment to some tick, takes a
snapshot, and later restores it — into the same environment object or
into a fresh one built from the same config and the same control map.
From that point, given the same actions for the policy seats, the
restored world produces exactly what the original would have: the same
observations, the same rewards, the same per-agent infos (the next
decision seed included), the same serialized world, step after step.
The snapshot carries everything a later step depends on — the world
with its random state, the decision seeds already dealt for the next
tick, the position in the episode and the reward baselines — so nothing
has to be re-derived in a way that could drift.

**Why this priority**: Without byte-identical continuation a branch is a
different world, and every read on it is a read of nothing. This is the
mechanism the Phase 2 gate and every later counterfactual read stand on.

**Independent Test**: Run a world 300 ticks, snapshot, run both the
original and a restored copy 200 further ticks under the same actions,
compare every surface tick by tick. Deliverable on its own: a branch
primitive for policy-only worlds.

**Acceptance Scenarios**:

1. **Given** an environment at tick t with mixed control (policy seats
   and scripted seats, a needy seat among them), **When** a snapshot is
   taken, the environment is stepped n more ticks, and a second
   environment of the same config and control restores the snapshot and
   is stepped the same n ticks with the same policy actions, **Then** the
   two produce identical observations, rewards, infos and serialized
   worlds at every one of the n ticks.
2. **Given** a restored environment, **When** its first per-agent infos
   are read, **Then** each agent's next decision seed equals the one the
   original environment reported at the snapshot tick — the restored
   world will draw exactly what the original drew.
3. **Given** an environment whose last step panicked (a poisoned
   environment that refuses further steps), **When** a valid snapshot is
   restored into it, **Then** it steps again as a healthy environment.
4. **Given** a snapshot taken at the horizon (the truncated tick),
   **When** restored, **Then** the environment is truncated exactly as the
   original was, and a reset is required before stepping, as today.
5. **Given** a snapshot taken between two steps, **When** the original
   environment is stepped once and the snapshot is then restored into
   it, **Then** the environment is back at the snapshot tick, not the
   later one — restore replaces state wholesale.

---

### User Story 2 - Substitute one tick's act for a scripted seat, under the engine's law, honestly marked (Priority: P1)

An experimenter restores a recorded tick and, before stepping, names one
engine-decided seat and the act it should propose this tick. The next
step uses that proposal in place of the seat's own decision, and only
for that step; afterwards the seat decides for itself again. The
proposal is a proposal: the engine's validation, consent verdict, needy
verdict and duration enforcement rule on it exactly as on any other, so
an override can never make an illegal act legal, never make a needy
seat relieve a masked need, never cut a scene short of its minimum. The
record of that tick says plainly that the act was substituted by the
harness, not decided by the seat, so no later reader — a corpus
collector above all — can mistake it for the seat's own.

**Why this priority**: The gate's counterfactual is "the act the mini
predicted, taken by the actual cat". For a scripted friend that act
cannot be injected today at all; without this half the gate can branch
only policy seats.

**Independent Test**: Seat one kitty on a builtin preset, override its
next act with a legal alternative, step, and read that tick's record:
the seat's applied act is the override's, its provenance is the
substitution mark; step again and the seat's own decision is back.

**Acceptance Scenarios**:

1. **Given** a scripted seat whose own decision this tick would be A,
   **When** an override naming legal act B is set and the environment is
   stepped, **Then** the tick applies B for that seat and marks its
   provenance as harness-substituted; **When** the environment is
   stepped once more with no override, **Then** the seat's own decision
   applies with its usual provenance.
2. **Given** a needy seat masked on cuddle, **When** an override proposes
   an act that would relieve its cuddle, **Then** the act resolves to idle
   at the apply slot and is recorded as a refusal, exactly as a friend's
   offer of the same relief is refused today.
3. **Given** a seat mid-scene inside its activity's minimum, **When** an
   override proposes a different act, **Then** duration enforcement
   continues the scene, exactly as it would for any other proposal.
4. **Given** a policy-controlled (external) seat, **When** an override is
   requested for it, **Then** the request is refused with an error that
   says the seat is external and its act is supplied through `step`.
5. **Given** an override already set for a seat, **When** a second
   override is requested for the same seat before a step, **Then** the
   request is refused; the first stands until the step consumes it or a
   restore or reset clears it.
6. **Given** an override set and then a restore or reset, **When** the
   environment is stepped, **Then** no override applies — pending
   overrides belong to the state they were set against and do not
   survive a change of state.

---

### User Story 3 - A world that never branches is byte-identical to today (Priority: P1)

A trainer, a certification run or a served world that never calls
snapshot, restore, fork or override sees nothing new: the same
observations and schema, the same rewards and infos, the same decisions
from every preset, the same seeded draws in the same order, the same
config fingerprint and defaults stamp, the same server behaviour and the
same plugin wire. Every frozen artifact — goldens, pins, fixtures,
recorded corpora — stays valid without a re-cut.

**Why this priority**: Gen 2 is frozen. A feature for reading frozen
worlds must not move them.

**Independent Test**: The existing byte-identity, golden and pin suites
pass unchanged on the feature branch; the observation schema version
and config fingerprint are unchanged.

**Acceptance Scenarios**:

1. **Given** the pre-feature engine and this one, **When** the same
   config and seed are run for the same ticks with no branch call,
   **Then** every readable surface is byte-identical.
2. **Given** the served server, **When** this feature lands, **Then**
   its save format, its endpoints and its boot log are unchanged.

---

### User Story 4 - Branch one world of a batch (Priority: P2)

An experimenter running a batched environment of n worlds snapshots one
world by index and later restores a snapshot into one world by index,
with the same guarantees as the single-world case, while the other
worlds continue untouched.

**Why this priority**: The lab's collectors run batched; the gate's
branch reads will too. It is P2 because the single-world primitive is
sufficient for the gate as declared and the batched surface composes
from it.

**Independent Test**: In a two-world batch, snapshot world 0, step both,
restore world 0, step both again: world 0 matches the single-world
restore case, world 1 matches an un-branched run.

**Acceptance Scenarios**:

1. **Given** a batch of n worlds, **When** world i is snapshotted and
   later restored, **Then** world i continues as in User Story 1 and the
   other n−1 worlds' trajectories are unchanged by either call.
2. **Given** a snapshot taken from a single-world environment, **When**
   it is restored into world i of a batch with identical config and
   control, **Then** it is accepted and continues identically — a
   snapshot is portable across environment objects of the same identity.

---

### User Story 5 - A snapshot is refused where it cannot be honoured (Priority: P2)

A snapshot restored into an environment whose config fingerprint,
control map or episode settings differ from the ones it was taken
under, or built by a different engine, is refused with an error naming
what differed — never silently accepted into a world that would then
diverge or misread.

**Why this priority**: The lab's binding discipline (every new binding
first proves it reproduces the recorded worlds) only works if the
engine refuses to pretend. P2 because it guards the P1 stories rather
than adding a capability.

**Independent Test**: Take a snapshot; attempt restores into
environments differing in one identity component each; each is refused
with the differing component named.

**Acceptance Scenarios**:

1. **Given** a snapshot, **When** restored into an environment whose
   config fingerprint differs, **Then** the restore is refused and the
   error names the found and expected fingerprints.
2. **Given** a snapshot, **When** restored into an environment whose
   control map differs (a seat external here that was scripted there,
   or a different preset name), **Then** the restore is refused and the
   error names the seat.
3. **Given** a snapshot, **When** restored under a binding built from a
   different engine commit, **Then** the restore is refused and the error
   names both commits.
4. **Given** bytes that are not a snapshot, **When** restored, **Then**
   the restore is refused with a parse error and the environment is left
   exactly as it was.

---

### Edge Cases

- A snapshot can only be taken and restored between steps; the tick is
  atomic and there is no mid-tick state to capture.
- A snapshot taken before the first reset (no world yet) is refused.
- Restoring a snapshot replaces every piece of episode state, including
  the dealt decision seeds; it never re-deals them (re-dealing would
  consume different random draws and the branch would diverge from the
  original).
- Restore into a poisoned environment heals it; the poison belongs to
  the state that was replaced.
- A snapshot taken at the truncated tick restores truncated; stepping it
  is refused until reset, as today.
- Fork is restore into a fresh environment of the same identity; it has
  no semantics of its own and inherits every refusal above.
- The snapshot bytes contain a needy seat's private schedule and every
  kitty's full state. They are harness-side data, never an observation:
  no mind reads them, no observation is encoded from them, no decision
  request carries them.
- An override for a kitty not in the roster is refused.
- An override set and never stepped is dropped by the next reset or
  restore; it is never carried into the new state.
- An override's proposal is decoded in the same vocabulary `step`
  accepts for policy seats (a menu index against the seat's
  start-of-tick target table), so an index the table cannot express is
  refused as out of range exactly as a policy seat's would be.
- The overridden seat's dealt decision seed is consumed by the tick as
  always and simply unused by the seat, as a policy seat's is today;
  the next tick's deal is unaffected.
- A served world has no snapshot, restore or override surface; the
  server is untouched.
- The per-tick decision seed in Experiments' recorded streams (part 3
  of the ask) is already emitted in per-agent infos and batched arrays;
  writing it into the raws is the recorder's job, in Experiments' lane
  (`experiments/tools/bc-collect` and the needy-set scripts). This spec
  requires only what makes it a usable branch-integrity check: FR-004.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The single-world environment MUST offer `snapshot()`,
  returning the complete episode state between steps as an opaque byte
  string, and `restore(bytes)`, replacing the environment's episode
  state with the snapshot's. Both are refused mid-step (structurally
  impossible from Python) and `snapshot()` is refused before the first
  reset.
- **FR-002**: A snapshot MUST carry every piece of episode state on
  which any later observation, reward, info or serialized world depends:
  the world including its random-number state, the decision seeds
  already dealt for the next tick, the tick position within the
  episode, the truncation flag, the reward baselines, and whatever else
  the proof in FR-003 shows to be load-bearing. It MUST NOT carry the
  config, the control map or the episode settings as state; those are
  identity (FR-006).
- **FR-003**: A restored environment MUST continue byte-identically with
  the original: for every later step under the same policy actions,
  observations, rewards, per-agent infos and the serialized world are
  equal. The guard is the existing mid-run save-and-continue contract
  (`crates/cloudkitty-core/tests/snapshot_resume.rs`) lifted to the
  episode surface, over worlds with mixed control including a needy
  seat.
- **FR-004**: The first per-agent infos of a restored environment MUST
  report, for every agent, the same next decision seed the original
  reported at the snapshot tick, so a recorded `decision_seed` column is
  a sufficient check that a branch started from the right state.
- **FR-005**: `restore` MUST accept a snapshot into any environment
  object of the same identity (FR-006), not only the one that took it;
  `fork()` MAY be offered as a convenience that builds a fresh
  environment of the same identity and restores into it.
- **FR-006**: A snapshot MUST carry its identity — the engine commit,
  the config fingerprint, the control map and the episode settings that
  shape outputs (horizon, observation configuration) — and `restore`
  MUST refuse, with an error naming the differing component and both
  values, any environment whose identity differs in any component.
  Refusal MUST leave the environment exactly as it was.
- **FR-007**: `restore` MUST heal a poisoned environment (one refusing
  steps after an engine panic) and MUST restore a truncated snapshot as
  truncated.
- **FR-008**: The batched environment MUST offer the same snapshot and
  restore per world index, with FR-002 through FR-007 holding for the
  addressed world and no effect on any other world.
- **FR-009**: The single-world environment MUST offer a one-tick
  proposal override for an engine-decided seat: `override(kitty, action
  [, message])` records a proposal that the NEXT step uses in place of
  that seat's own decision, after which it is cleared. Builtin presets
  and both needy presets are engine-decided seats. The batched
  environment MUST offer the same per world index.
- **FR-010**: The override substitutes the seat's PROPOSAL only. The
  engine's law — validation, the consent verdict, the needy verdict and
  duration enforcement — MUST rule on it at the apply slot exactly as
  on any other proposal; nothing about the override may reach the
  verdicts.
- **FR-011**: A tick in which a seat's proposal was overridden MUST mark
  that seat's record with a provenance distinct from every existing
  mark (the seat's own decision, dispatch fallback, substituted idle),
  readable on the per-agent info and the recorded streams, so that a
  corpus collector can refuse the row as a teacher's act and a reader
  can separate substituted acts from decided ones.
- **FR-012**: The override MUST be refused for a policy-controlled
  (external) seat, for a kitty not in the roster, for a second override
  of the same seat before a step, and for a proposal the seat's
  start-of-tick target table cannot express; each refusal names its
  cause and leaves the environment as it was. A pending override MUST be
  dropped by reset and by restore.
- **FR-013**: The override's proposal vocabulary MUST be the one `step`
  accepts for policy seats (menu index, and message index where a
  message is given), so the gate can inject a mini's predicted menu
  action without translation.
- **FR-014**: The message half of an overridden decision is governed by
  [NEEDS CLARIFICATION: with no message given, does the seat's own
  behaviour still supply its message for that tick (the activity is
  substituted, the calling stays the seat's — the doctrine-safe
  default), is the message Silent, or must the caller always supply a
  law-named message? The free register (meow/purr) is never scripted by
  the harness in any reading].
- **FR-015**: With no call to snapshot, restore, fork or override, the
  engine MUST be byte-identical to the pre-feature engine on every
  readable surface: observation schema and encoding, rewards and infos,
  every preset's decisions, every seeded draw and its order, the config
  fingerprint and defaults stamp, the server's save format, endpoints
  and boot log, and the plugin wire's decision request. Zero golden,
  pin or fixture re-cuts.
- **FR-016**: The snapshot format MUST be treated as [NEEDS
  CLARIFICATION: a transient in-process token valid only for the binding
  that produced it (recommended: the raws are the durable artifact and
  any snapshot is re-derivable by replay), or a versioned on-disk
  artifact with a compatibility promise across engine commits?]. Under
  either reading, FR-006's engine-commit refusal holds by default.
- **FR-017**: The Python docstrings of snapshot, restore, fork and
  override MUST carry the welfare line: branch depth k > 1, where a
  component's predictions drive successive branch states, is a named
  marker-review trigger (`experiments/WELFARE-STANDING.md` text (b);
  `experiments/gen2-prereg-2026-10-17.md` §A2′ item 5); the API is
  depth-unlimited and the doctrine, not the API, caps its use.

### Key Entities

- **Branch snapshot**: an opaque byte string holding one environment's
  complete episode state between steps (world with random state, dealt
  decision seeds, episode position, truncation, reward baselines)
  together with its identity stamps. Harness-side data; never an
  observation.
- **Environment identity**: the engine commit, config fingerprint,
  control map (which seats are external, which builtin and on which
  preset) and output-shaping episode settings. Two environments of
  equal identity accept each other's snapshots; any difference refuses.
- **Proposal override**: a pending substitution (seat, activity,
  optional message) consumed by exactly one step, ruled on by the
  engine's law like any proposal, marked by a distinct provenance in
  that tick's record. Cleared by step, reset or restore.
- **Provenance mark**: the per-tick, per-seat record of how a decision
  came to be. Gains one value for harness substitution; existing values
  keep their meaning.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Over at least 200 ticks after a restore, for at least ten
  seeds and a config with mixed control including a needy seat,
  observations, rewards, per-agent infos and serialized worlds of the
  restored environment equal the original's at every tick (zero
  differing bytes).
- **SC-002**: The first infos after a restore report the same next
  decision seed per agent as the original did at the snapshot tick, in
  100% of the SC-001 trials.
- **SC-003**: Every identity mismatch class (config fingerprint, control
  map, episode settings, engine commit, malformed bytes) is refused in
  100% of attempts, with the error naming the differing component, and
  the environment's next step is unaffected by the refused call.
- **SC-004**: An override applies for exactly one step: the overridden
  tick's record for that seat carries the substituted proposal and the
  substitution provenance; the following tick's record carries the
  seat's own decision and provenance, in 100% of trials over every
  builtin and needy preset.
- **SC-005**: An override cannot bypass the law: for a needy seat masked
  on a need, an override proposing relief of that need resolves to idle
  and is recorded as a refusal in 100% of trials; for a seat inside its
  scene minimum, an override of a different act continues the scene in
  100% of trials.
- **SC-006**: Branching costs less than replaying: restore plus one step
  from a snapshot at tick 10,000 of a served-size world (20×20, five
  kitties) completes in under one hundredth of the time replaying 10,000
  ticks takes on the same machine (at the lab's measured 20,000 ticks a
  second, under 5 milliseconds).
- **SC-007**: With no branch call, the existing byte-identity, golden,
  pin and fixture suites pass unchanged, the observation schema version
  is unchanged, and the config fingerprint of every shipped config is
  unchanged.
- **SC-008**: Overridden rows are refusable downstream: a reader given
  the recorded provenance column can separate substituted from decided
  acts with zero misclassification on a world where overrides were
  applied at known ticks.

## Design-doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md` rules 1–12 before
`/speckit-plan`. This spec observes (reads needs and happiness on a
branch) and scripts (substitutes a seat's act for one tick), so the
check binds.

**Rules that moved a choice.**

- **Rule 2 (prices are physics, not nudges) → FR-010, SC-005.** The
  override proposes; the law rules. No branch bypasses validation, the
  consent verdict, the needy verdict or duration enforcement, so a
  counterfactual act is priced exactly as the real one would be.
- **Rule 5 (a teacher may only act on what the student can see) →
  FR-011, SC-008.** A harness-substituted act is not the seat's
  decision and must never enter a corpus as a teacher's act; the
  distinct provenance is what lets a collector refuse it. The needy seat
  stays teacher-ineligible (spec 067); the override does not change who
  controls a seat.
- **Rule 6 (the free register is never scripted) → FR-014.** The
  activity half is the counterfactual; the message half must not become
  a channel for the harness to put free-register words in a scripted
  cat's mouth. The clarification fixes which doctrine-safe reading
  applies; all three candidate readings keep the free register
  unscripted.
- **Rule 9 (frozen models cannot answer a reprice) → FR-015, SC-007.**
  No observation change, no reprice, no change to any preset; a world
  without a branch call is byte-identical, so every frozen artifact and
  the Gen 2 freeze stand.
- **Rule 10 (two-layer welfare gates; gates live with the consumer's
  declaration).** The Phase 2 gate's four pins, its margins and its
  bars stay in the frozen prereg. This spec supplies mechanism only and
  declares no bar.
- **Rule 12 (relief is always available; own state visible, others'
  hidden) → Edge Cases, FR-006.** The snapshot bytes hold every kitty's
  state and the needy seat's private schedule, but they are harness-side
  and never reach an observation, a decision request or a mask; no mind
  learns anything from them. The branch reads engine ground truth.

**Rules checked that moved nothing.** Rule 1 (reward is team welfare
only): no reward term touched. Rule 3 (side relief): no relief changed.
Rule 4 (unfarmable, prosocial, charm): no pricing. Rule 7 (build a
behaviour when the world values it): no behaviour built. Rule 8 (design
scarcity of information): no information made scarcer or richer to any
mind. Rule 11 (invalidation domain): this spec declares no finding and
no invalidation clause.

**Welfare line (frozen; carried, not negotiated here).** Branch depth
k > 1, where a component's predictions drive successive counterfactual
world states in a rolled branch, is a named marker-review trigger:
`experiments/WELFARE-STANDING.md` text (b), "no branch of depth k > 1
… runs before the standing review has ruled on it", with the flow
trigger beside it (any architecture in which reward or a decision is
computed from a mini's predictions, at any depth, convenes the review);
`experiments/gen2-prereg-2026-10-17.md` §A2′ item 5. The API is
depth-unlimited; the doctrine, not the API, caps its use (FR-017). The
worked check already on record covers the intended first use: the
one-tick counterfactual screen trips neither marker — the branch is
computed by the harness and the state belongs to a seated kitty. The
welfare-cost line of any set built with this API lives in Experiments'
declaration of that set; this spec points at it and supplies nothing
that changes a covered mind's experience: a branch is discarded, and a
covered seat in a branch is never trained on it under this spec (any
policy-side use of branches — planning, Dyna — is out of scope and
doctrine-gated).

## Assumptions

- **Grounds verified 2026-11-05 against origin/main 87fae11e /
  4464488e** (scoping facts, not design): the world serializes whole
  with its random state and a mid-run save continues byte-identically
  (`crates/cloudkitty-core/tests/snapshot_resume.rs:100`); the server's
  persistence checks the world's config fingerprint on load
  (`crates/cloudkitty-server/src/persist.rs`), server-only; the Python
  crate depends on the core and RL crates only, so that check is
  mirrored, not imported. The episode owns its world behind a read-only
  getter and is not clonable; it also holds the next tick's dealt
  decision seeds, the episode tick, the truncation flag and the reward
  baselines — the state FR-002 names. A needy config seat refuses
  external control at construction (spec 067 research D16), which is
  why the override is a one-tick proposal substitution and never a
  control change. The engine commit is already exposed to Python.
- **Portability is the default.** A snapshot is accepted by any
  environment of equal identity (FR-005); "origin environment only" was
  considered and rejected because the gate's branch runs beside the
  original, not in its place, and the identity check (FR-006) is what
  makes portability safe.
- **Identity, not state.** Config, control map and episode settings are
  checked, never restored; an experimenter who wants a different
  control map builds a different environment, and a needy seat cannot
  be taken external that way either (spec 067 D16 stands).
- **Engine-commit mismatch refuses by default.** The lab's binding
  discipline (`experiments/needy-set-2026-10-28/BINDING.md`: a new
  binding first proves it reproduces the recorded worlds) governs
  cross-build reads; a snapshot does not try to.
- **The override's vocabulary is `step`'s.** The gate injects a mini's
  predicted menu action; a wire-named engine action would need a
  translation the spec would then have to pin.
- **The dealt seed of an overridden seat is consumed and unused**, as a
  policy seat's is today; one draw per kitty per tick keeps same-seed
  futures coincident (spec 014).
- **Part 3 of the ask (decision seeds in the raws)** is the recorder's,
  in Experiments' lane; FR-004 is the engine's whole contribution.
- **No urgency.** The Phase 2 gate runs by replay on the pinned binding
  (engine 5928b7ca) until Experiments, on the owner's word, adopts this
  API with a binding check first.
- **Out of scope**: the server's save format and endpoints; observation
  emission for builtin seats; any policy-side use of a branch (planning,
  Dyna, any decision computed from a mini's predictions) — doctrine-
  gated by WELFARE-STANDING text (b) and not asked; recorder changes in
  Experiments' lane.
- **Dependencies**: spec 014 (the joint-proposal seam, dealt seeds,
  tick report and provenance), spec 046 (the refusal stamp), spec 059
  and ruling eb9e860b (the consent verdict at the apply slot), spec 067
  (the needy verdict and the needy seat's control rule).
- **FINDINGS read (CLAUDE.md rule 7)**: F-074 and F-075 (the act head's
  drift monitors want rollouts — the API's second consumer); F-033 (the
  proposed/validated/applied seam and `survived` as the honest-
  bookkeeping precedent FR-011 follows).
