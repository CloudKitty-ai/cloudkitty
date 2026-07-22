# Feature Specification: Multi-Agent RL Readiness

**Feature Branch**: `014-multi-agent-rl`

**Created**: 2026-07-21

**Status**: Draft

**Input**: Owner request: "Spec out the optimal path to make CloudKitty
suitable for multi-agent RL, oriented around cooperation to optimize
collective happiness in an environment with abundant resources." — with the
locked decisions: spec-first (this document precedes all code); training
reaches the engine from Python via native bindings speaking the PettingZoo
parallel-environment convention; trained policies come home through the
existing behavior door; and training runs under the **full constitution** —
no relaxed mode, ever.

## The door being opened

CloudKitty's behaviors have always been untrusted advisors: they propose,
the engine disposes (Article IV). That contract was written for exactly one
future — a brain the engine did not author. This spec opens that door for a
*learned* brain: policies trained by cooperative multi-agent reinforcement
learning to maximize the meadow's **collective happiness** — measured so
that the least happy kitty counts the most (Nash welfare: the geometric
mean of every kitty's happiness, not the plain average), so no kitty is
ever traded away for another.

Nothing about the world changes. Kitties still cannot suffer, die, or be
alone; resources stay abundant (the Article I safeguard spawner runs during
training rollouts exactly as it does in the served world); the engine
remains the only law. What changes is who may sit in the advisor's chair: a
policy is an untrusted advisor twice over — during training, when an
external trainer proposes every kitty's action and the engine validates each
one; and after deployment, when the frozen policy proposes through the same
`Behavior` seam as `needs_driven` and `playful`, under the same time budget
and the same fallback.

**Reward never enters the engine.** The engine does not compute, store, or
consume reward; reward is a property of the training harness, not of the
world. Distress remains what Article I says it is — a signal, never a
punishment: the harness may *read* it as state, and any reward shaping must
be potential-based so the optimal policy remains exactly "maximize
collective happiness" and nothing else.

**No constitutional amendment is required.** Article IV anticipated external
advisors; Article V's determinism only strengthens (seeded rollouts become
bit-reproducible experiments); headless embedding of the engine follows the
precedent the CI welfare suite set long ago. The one clause this spec must
argue rather than silently pass is Article V's "all game logic lives on the
server": the served world is untouched — training embeds the engine in a
separate process the way the test suite always has, and no non-server
process ever mutates the *served* world.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A researcher steps the world with a joint action (Priority: P1)

A researcher advances the world one tick by supplying a proposal for every
kitty at once — no built-in behavior consulted — and receives back the new
state plus an honest per-kitty record of what was proposed, what survived
validation, and what actually applied. The engine runs the same tick it
always runs: fair turn order, validation, duration enforcement, environment,
needs, invariants.

**Why this priority**: this seam is the load-bearing refactor. Every other
story stands on it, and it is independently valuable without any RL at all —
scripted scenarios, replay harnesses, and the backlog's external-plugin work
all want the same door.

**Independent Test**: drive a world for thousands of ticks by externally
feeding it the very decisions its built-in behaviors would have made, and
compare against the behavior-driven run: the two worlds must be identical in
every serialized byte.

**Acceptance Scenarios**:

1. **Given** a seeded world and a complete set of per-kitty proposals,
   **When** the joint-action tick is invoked, **Then** the world advances
   exactly one full tick in constitutional order and reports, per kitty,
   the proposed / validated / applied action triple.
2. **Given** a joint action missing one kitty's proposal (or carrying a
   malformed one), **When** the tick is invoked, **Then** that kitty idles
   (Article IV), every other kitty's action proceeds, and the tick
   completes with all invariants asserted.
3. **Given** the same seed and config, **When** one run uses built-in
   behaviors and another externally feeds the identical decisions,
   **Then** the two runs serialize byte-identically over at least 5,000
   ticks — including every RNG draw.

---

### User Story 2 - A trainer gets cooperative rollouts in Python (Priority: P2)

A trainer imports the environment in Python, resets it with a seed, and
steps it with a dictionary of per-kitty actions, receiving per-kitty
observations and legal-action masks, one shared team reward, and episode
bookkeeping — the PettingZoo parallel-environment convention. Observations
are fixed-size vectors derived from exactly what a behavior is allowed to
know (the frozen start-of-tick snapshot). Actions are a small flat menu
covering everything a kitty can propose. Episodes end only by running out
the clock: kitties cannot die, so termination is constitutionally always
false.

**Why this priority**: this is the training loop itself — the reason the
door exists. It depends on the P1 seam plus the observation/action encodings
and the reward channel.

**Independent Test**: run a random-policy rollout from Python: shapes,
bounds, and bookkeeping match the contract; the same seed and action
sequence reproduce bit-identical observation and reward streams across
processes; a vectorized batch of worlds steps in parallel.

**Acceptance Scenarios**:

1. **Given** a reset with a seed, **When** the trainer steps with any
   in-range action per kitty, **Then** it receives per-kitty observations
   of the documented fixed size and bounds, one identical team-reward
   scalar per kitty, terminations all false, truncations all false until
   the horizon tick, and per-kitty info including the applied action,
   whether the proposal survived validation, and the legal-action mask
   for the next decision.
2. **Given** the same seed, config, and action sequence in two separate
   processes, **When** both rollouts complete, **Then** observations,
   masks, global states, and rewards are bit-identical.
3. **Given** a vectorized environment of N independent worlds, **When**
   stepped with a batch of joint actions, **Then** each world advances
   independently and the batch step releases Python's interpreter lock
   while the engine works.
4. **Given** an action that names an empty target slot (nothing there to
   chase or cuddle), **When** the tick runs, **Then** the proposal reaches
   the engine and lawfully resolves to idle — never a crash, never a
   skipped tick.
5. **Given** an environment where some kitties are driven by built-in
   behaviors, **When** the trainer steps only the remaining kitties,
   **Then** the scripted kitties act deterministically from their own
   decision streams and the team reward still counts the full roster.

---

### User Story 3 - A researcher scores any brain against the welfare bar (Priority: P2)

A researcher points the evaluation harness at any brain — a built-in
behavior name or a trained policy artifact — and gets the long-run welfare
scorecard the repository already trusts: mean happiness, low-streaks, floor
touches, distress ages, over 20,000 ticks under the full constitution, plus
a same-seed comparison against the `needs_driven` baseline.

**Why this priority**: the welfare bounds in the existing long-run suite
*are* the product's definition of a good life; a learned policy must clear
the same bar the hand-written cats clear, on the same seeds. Valuable before
any training exists (it baselines the built-ins under the exact metric a
policy will chase).

**Independent Test**: run the harness on `needs_driven` and on `playful`;
the reported metrics must reproduce the welfare suite's numbers for the same
seeds, and the paired-seed comparison must be stable across repeat runs.

**Acceptance Scenarios**:

1. **Given** a behavior name or policy artifact, **When** the harness runs
   20,000 ticks on a set of ≥ 10 fixed seeds, **Then** it reports every
   welfare metric the long-run suite guards, per seed and aggregated.
2. **Given** two brains evaluated on the same seeds, **When** results are
   compared, **Then** the comparison is paired per seed and reproducible
   run to run.
3. **Given** a policy artifact whose inference panics, **When** a scoring
   run is attempted, **Then** the harness reports the fallback count and
   fails the run — the fallback's welfare is never mistaken for the
   policy's.
4. **Given** a policy kitty evaluated among `needs_driven` kitties,
   **Then** the same welfare scorecard and paired-seed comparison are
   produced for the mixed roster.

---

### User Story 4 - An owner gives a kitty a trained mind (Priority: P3)

An owner assigns a trained policy to a kitty in the config file the same way
they pick `playful` today, restarts the server, and watches — nothing about
the world looks unusual. The policy proposes; the engine validates; if the
artifact is missing or corrupt the server refuses to start with a clear
config error; if inference is ever slow or broken at runtime, that kitty
gracefully falls back to `needs_driven` for the tick, exactly like any other
external advisor.

**Why this priority**: deployment is the payoff, but it is only safe after
training and evaluation exist; and by construction it is the smallest step —
the policy walks in through a door the engine already guards.

**Independent Test**: a config naming a policy behavior boots the server
with a policy kitty in the roster; the full existing CI suite (welfare,
determinism, invariants, fairness) passes with that kitty present; a
deliberately corrupted artifact fails at startup with an error naming the
offending config field.

**Acceptance Scenarios**:

1. **Given** a config assigning a policy to a kitty, **When** the server
   starts, **Then** the artifact is loaded and validated (schema version,
   content hash logged) before any tick runs.
2. **Given** a missing, corrupt, or schema-mismatched artifact, **When**
   the server starts, **Then** startup fails with a config error naming
   the policy — the same doctrine as an unknown behavior name today.
3. **Given** a policy kitty in a running world, **When** inference exceeds
   the decision budget or panics, **Then** the engine falls back to the
   default behavior for that kitty's turn and the world is otherwise
   unaffected.
4. **Given** a policy kitty, **When** the viewer is watched, **Then**
   nothing distinguishes it from a built-in kitty except how it lives.

---

### Edge Cases

- **Absent, late, duplicate, or malformed joint entries**: each resolves to
  idle for that kitty alone (Article IV); the tick never fails, never
  blocks, never skips another kitty.
- **Vacant target slot**: an action naming an empty observation slot decodes
  to a proposal the engine lawfully rejects to idle — validation absorbs the
  whole failure surface; decoding itself never errors.
- **More kitties than observation slots**: the nearest fill the slots
  (ties broken by id); farther kitties are unobserved but fully simulated —
  the engine acts for every kitty regardless of who fits in whose view.
- **Config immutability per episode**: the environment's config is fixed at
  construction; mid-episode mutation is not offered. New config → new
  environment.
- **RNG stream discipline**: the joint-action seam consumes the master RNG
  identically to a behavior-driven tick (the per-kitty decision-seed draws
  ride the same stream in the same order), so behavior-driven and
  externally-driven futures from one seed are the same world. The trainer's
  own exploration randomness lives entirely outside the engine; the
  per-kitty decision seeds are surfaced to it for exactly that purpose.
- **Meow on cooldown**: validates as legal but produces silence today; the
  per-kitty info marks the proposal as applied — the trainer sees aliasing
  honestly rather than mysteriously.
- **Duration enforcement rewrites proposals**: inside an activity's minimum
  the engine continues the scene whatever was proposed; the info triple
  (proposed / validated / applied) makes the rewrite visible to the trainer.
- **Horizon of zero**: rejected at environment construction — an episode
  must contain at least one tick.
- **Persistence never meets training**: episodes are ephemeral; the training
  environment neither reads nor writes world snapshots. The served world's
  save/restore is untouched.
- **A masked-in action can still idle**: the mask speaks to the
  start-of-tick snapshot; within-tick contention — two kitties reaching
  one last serving — is resolved by the engine's fair turn order.
  Trainers treat the mask as necessary, not sufficient.
- **A kitty at zero unclamped happiness**: the reward's configured offset
  ε keeps the fairness aggregate finite and its gradient defined; the
  score stays dominated by the least happy kitty without becoming
  degenerate.
- **NaN or infinite policy outputs**: action selection is total — garbage
  logits still select some in-range action (worst case idle); nothing
  propagates NaN into a proposal.
- **Slow host at deploy time**: a budget-triggered fallback costs one kitty
  one turn of cleverness (Article IV's standing bargain) and is lawful
  degradation of an external advisor — the served world's correctness and
  the engine's determinism guarantees are never conditioned on inference
  speed. Reproducible evaluation uses the headless path, which dispatches
  without the wall-clock budget (FR-017).

## Requirements *(mandatory)*

### Functional Requirements

**The joint-action seam (US1)**

- **FR-001**: The engine MUST offer a way to advance the world exactly one
  tick from an externally supplied set of per-kitty proposals, running the
  same constitutional tick order as today — fair turn order, validation,
  duration enforcement, environment phase, needs, distress, purr,
  invariants — with behavior dispatch as the only step bypassed.
- **FR-002**: The behavior-driven tick and the joint-action tick MUST share
  one implementation of the applied phases (the engine is the law by
  construction, not by duplication), and the joint-action path MUST consume
  the master RNG with the identical draw shape — including the per-kitty
  decision-seed draws in stable id order — so same-seed futures coincide.
- **FR-003**: The per-kitty decision seeds MUST be obtainable by the
  external driver, and each joint-action tick MUST report, per kitty, the
  proposed action, the validated action, and the action actually applied,
  plus any distress events and activity endings the tick produced.
- **FR-004**: A run driven by built-in behaviors and a run externally fed
  those same decisions MUST serialize byte-identically over at least 5,000
  ticks; this parity MUST be a guarding test in CI (Article VI).

**Observation and action encodings (US2)**

- **FR-005**: A fixed-size per-kitty observation MUST be derivable from the
  frozen start-of-tick snapshot alone — the same information a behavior's
  decision context exposes, nothing more — covering the kitty's own state
  (needs, happiness, position, activity and its progress, distress,
  pursuit) **and its static traits** (the configured per-need rise rates,
  normalized — so one parameter-shared policy can serve heterogeneous
  kitties, and a fast-metabolism eater is never failed by a brain tuned to
  the average cat), the nearest other kitties and relevant elements in a
  fixed number of distance-ordered slots, recent meows, and episode
  progress. All values normalized; slot counts and normalization constants
  in configuration; encoding deterministic (same snapshot → identical
  vector).
- **FR-006**: A flat, finite action menu MUST cover every proposable kitty
  action, with targeted actions (chasing, playing with, grooming, cuddling
  a specific other) expressed by reference to the observation's own slots;
  decoding MUST be total — every menu index decodes to a proposal, vacant
  or stale slots decoding to proposals the engine resolves to idle.
- **FR-007**: Exactly one implementation of the observation encoding, the
  action codec, the legal-action mask, and the global-state encoding MUST
  exist, in the engine's language, and MUST be shared verbatim by every
  surface that consumes them — training, evaluation, and deployment (the
  global state, per FR-019, is consumed by training and evaluation
  only). A parallel reimplementation in Python is expressly forbidden —
  encoder drift between training and deployment is the failure mode this
  requirement exists to prevent. All carry schema versions; artifacts
  record the versions they were trained against.

**Reward and episodes (US2)**

- **FR-008**: The team reward MUST be computed entirely outside the engine,
  from each kitty's happiness recomputed *unclamped* from needs and the
  configured weights — so the training signal keeps its gradient below the
  engine's display floor (the engine's clamped happiness remains
  authoritative for everything the engine and its viewers do). The
  aggregation MUST be **inequality-averse**: strictly increasing in every
  kitty's happiness (helping any kitty always helps the score — no credit
  for leveling down) and concave (the same gain is worth more to a
  less-happy kitty). The default aggregate is **Nash welfare** — the
  geometric mean of the roster's normalized happiness — generalized in
  configuration as a power mean with exponent p ≤ 1: p = 1 the plain
  average, p = 0 Nash (the default), large negative p approaching the
  least-happy kitty's score. A small configured offset ε keeps the
  aggregate and its gradient finite at zero happiness. Level reward is the
  default; a delta mode MAY be offered in configuration.
- **FR-009**: Reward shaping, if enabled, MUST be potential-based (so the
  optimal policy is provably unchanged), MUST default to off, and every
  coefficient MUST live in configuration. Distress MAY inform a potential
  as observed state; no reward term may ever flow back into the engine.
- **FR-010**: Episodes MUST end only by truncation at a configured horizon;
  termination MUST be constitutionally always false, and the set of agents
  MUST be constant for the life of the environment (Articles II and III as
  API guarantees).

**The Python surface (US2)**

- **FR-011**: A Python-importable environment MUST speak the PettingZoo
  parallel-environment convention — reset with seed, step with a per-agent
  action mapping, returning per-agent observations, rewards (the one team
  scalar, broadcast), terminations, truncations, and infos — with seeded
  bit-reproducible rollouts. The contract is duck-typed; the PettingZoo
  package itself is at most an optional test dependency.
- **FR-012**: A vectorized form MUST step N independent worlds in parallel
  with Python's interpreter lock released during engine work; worlds MUST
  be fully independent (separate seeds, separate RNGs, no shared state).

**Evaluation (US3)**

- **FR-013**: An evaluation harness MUST score any behavior name or policy
  artifact over 20,000-tick runs under the full constitution, reporting the
  existing long-run welfare metrics (mean happiness, low-happiness streaks
  and share, floor touches, pinned streaks, distress age), the configured
  team-welfare aggregate with the plain mean and the least-happy kitty's
  mean reported beside it (fairness visible, not just scored), and a
  paired same-seed comparison against the `needs_driven` baseline over
  ≥ 10 seeds. When scoring a policy, the harness MUST evaluate both
  roster modes — every kitty policy-driven, and the deployment reality
  of a policy kitty among `needs_driven` kitties — and MUST count
  decisions taken by the fallback: a scoring run with a nonzero fallback
  count fails rather than silently reporting the fallback's welfare as
  the policy's.

**Deployment (US4)**

- **FR-014**: A policy behavior MUST implement the existing behavior
  contract as a non-built-in — the standing time budget, panic isolation,
  and default-behavior fallback all apply — and MUST resolve its decision
  without waiting on anything (no I/O, no network) so the budget is never
  in play on a healthy host.
- **FR-015**: Policy action selection MUST be deterministic given the
  kitty's per-tick decision randomness: greedy selection by default, with
  optional sampling drawn only from the kitty's own decision stream — the
  same stream the training environment surfaces, making train-time and
  deploy-time stochasticity one mechanism. Selection MUST operate over
  the masked menu, using the same legal-action mask implementation
  training used (FR-018), applied between inference and selection — so
  the deployed action distribution is the trained one, never a skewed
  cousin free to land on entries training never allowed.
- **FR-016**: Policy artifacts MUST be referenced from configuration
  (per-kitty behavior naming a configured policy), validated at startup
  (missing, corrupt, or schema-mismatched artifacts fail startup with an
  error naming the config field), and content-hashed, with the hash logged
  and exposed for reproducibility.

**Headless determinism (US2, US3, US4)**

- **FR-017**: Headless drives of the engine — training rollouts, the
  evaluation harness, and the CI parity and determinism suites — MUST
  dispatch decisions without the wall-clock budget, so reproducibility
  never depends on host speed. The budget and its fallback apply in the
  served world, where a slow advisor may cost a kitty a turn of
  cleverness but never the world its correctness; the bit-exactness
  guarantees (SC-002) and suite passes with a policy kitty (SC-005) are
  claims about this budgetless path. Panic isolation and the fallback
  remain in force headlessly — but never silently: every headlessly
  dispatched decision MUST be marked as policy-made or fallback-taken, so
  a broken artifact cannot ride the fallback through an evaluation
  (FR-013).

**Cooperative training fidelity (US2, US3)**

- **FR-018**: Alongside each per-kitty observation, a legal-action mask
  MUST be derivable from the same frozen snapshot and exposed to
  trainers with every reset and step. The mask carries one bit per menu
  entry: whether that entry, proposed as the world stood at the start of
  the tick, would be applied *as proposed* — it passes validation and
  duration enforcement would not rewrite it. Inside an activity's
  minimum the mask therefore reduces to the activity's continuations.
  The mask is advisory by design: legality speaks to the frozen
  snapshot, and within-tick contention is still resolved by the engine's
  fair order — the mask is necessary, never sufficient, and a masked-in
  action that loses a contest lawfully idles. A property test MUST guard
  the mask against the engine's own judgment (Article VI): for every
  menu entry, the mask's verdict equals the verdict of validation plus
  duration enforcement run against a world in the snapshot's state.
- **FR-019**: For centralized training, a fixed-size privileged global
  state MUST be derivable from the same frozen snapshot — every kitty's
  full state without slot truncation, a bounded configured summary of the
  element population, and the episode clock — and exposed through the
  Python surface alongside per-agent observations (the
  parallel-environment state convention). It exists for critics, not
  actors:
  deployed behaviors never receive it (decentralized execution), and its
  layout is versioned like the observation schema.
- **FR-020**: The training environment MUST support mixed control: any
  subset of kitties driven by named built-in behaviors while the rest
  take external actions. Scripted kitties decide from the same per-kitty
  decision streams the engine would deal them, so mixed rollouts remain
  bit-reproducible; and the team reward always counts the full roster,
  scripted kitties included — a policy is trained to raise everyone's
  happiness, not just its own faction's.

**Scope guard**

- **FR-021**: This feature MUST NOT change the served world's semantics,
  the client, persistence formats, existing behaviors, or the constitution;
  MUST NOT introduce any reward concept into the engine; and every new
  constant it adds MUST live in configuration with documented defaults
  (Article VI).

### Key Entities

- **Joint Proposal**: one tick's worth of per-kitty proposed actions,
  supplied by an external driver in place of behavior dispatch.
- **Tick Report**: the honest record of one tick — per kitty, the proposed
  / validated / applied action triple, plus new distress events and
  activity endings.
- **Observation Schema**: the fixed-size, versioned layout of a kitty's
  view — self block, kitty slots, element slots, meow digest, episode
  clock — with its normalization and slot counts in configuration.
- **Target Table**: the per-observation mapping from slot indices to the
  concrete kitty/element identities that filled them, built from the same
  frozen snapshot; the bridge that lets a flat action menu name a specific
  neighbor.
- **Action Codec**: the versioned bijection between the flat action menu
  and engine proposals, total in both directions.
- **Episode**: a seed, a horizon, and the rollout between reset and
  truncation; never persisted, never terminated.
- **Team Reward**: the inequality-averse aggregate of the roster's
  unclamped happiness — Nash welfare (geometric mean) by default, a
  configurable power mean in general — computed by the harness; optionally
  accompanied by a potential-based shaping term.
- **Policy Artifact**: the frozen trained policy — weights, observation and
  action schema versions, content hash.
- **Policy Behavior**: the artifact seated in the advisor's chair — a
  non-built-in behavior wrapping encode → infer → select → decode.
- **Vectorized Environment**: N independent worlds stepped as a batch for
  training throughput.
- **Legal-Action Mask**: the per-observation marking of which menu entries
  would apply as proposed against the frozen snapshot — advisory
  (within-tick contention stays the engine's to resolve), versioned with
  the codec.
- **Global State**: the fixed-size privileged view for centralized
  critics — full roster, bounded element summary, episode clock; never
  given to a deployed behavior.

## Constitutional compliance *(Articles I–VI)*

- **Article I (no suffering)**: the engine is untouched; need clamps, the
  happiness floor, and the safeguard spawner hold during rollouts exactly
  as in the served world — training is resource-abundant by the same law
  that makes the meadow so. Reward lives outside the engine and no code
  path feeds it back in. Distress remains a signal: the harness reads it,
  potential-based form keeps it from becoming a de-facto punishment
  objective.
- **Article II (no death)**: episodes end only by truncation; termination
  is always false; the agent roster never shrinks. No removal path is
  added anywhere.
- **Article III (never alone)**: environment configs pass the same
  validation (≥ 2 kitties) and the per-tick invariant assertions run inside
  the joint-action tick, because it *is* the tick.
- **Article IV (engine is the law)**: the seam bypasses behavior dispatch,
  never validation — every proposal, human-written or learned, traverses
  the same validate → enforce → apply gauntlet in the same fair order. At
  deploy, the policy is a non-built-in advisor under budget, panic
  isolation, and fallback. The learned brain is untrusted twice over.
  Article IV's time-budget clause reads on what it protects — the paced
  tick loop: that purpose reading is already the law's practice (built-ins
  are exempt precisely so determinism is unconditional), and headless
  drives have no tick loop to protect and no wall clock to race (FR-017).
  Validation, panic isolation, and the fallback hold everywhere a
  behavior is dispatched — and headless fallbacks are counted, never
  silent.
- **Article V (server-authoritative, deterministic)**: the served world and
  its server are untouched; training embeds the engine headlessly exactly
  as the CI suites always have, and no non-server process mutates the
  served world. Determinism strengthens: seed + config + action sequence →
  bit-identical trajectories, and the seam preserves the master RNG's draw
  shape so behavior-driven and joint-driven futures from one seed are the
  same world.
- **Article VI (spec-first, test-guarded, no magic numbers)**: this spec
  precedes all code; the parity, codec-totality, encoder-determinism,
  mask-soundness, reproducibility, and welfare guards named in the
  requirements and Success Criteria join CI;
  every new constant lives in configuration with documented defaults.

**Amendment required: none.** The constitution stays at v1.1.0.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Golden parity — a behavior-driven run and a joint-action run
  fed the same decisions serialize byte-identically over ≥ 5,000 ticks on
  the default world, as a CI guard.
- **SC-002**: Reproducibility — identical seed, config, and action sequence
  produce bit-identical observation, legal-action-mask, global-state, and
  reward streams across two runs in separate processes.
- **SC-003**: Throughput — ≥ 5,000 environment steps per second
  single-threaded on the default 32×32, 4-kitty world (measurement method
  documented alongside the number), with near-linear scaling to 8
  vectorized workers.
- **SC-004**: A policy trained with a standard cooperative algorithm meets
  **every** existing long-run welfare bound over 20,000 ticks — mean
  happiness ≥ 70, low streaks ≤ 20 ticks, low share ≤ 1%, zero floor
  touches, pinned streaks ≤ 25 ticks, distress age ≤ 150 — **and**
  achieves collective happiness (the configured welfare aggregate, Nash
  by default) at least equal to the `needs_driven` baseline on ≥ 10
  paired seeds, with its least-happy kitty's mean happiness no lower than
  the baseline's least-happy kitty. The criterion applies in both roster
  modes — all kitties policy-driven, and the policy kitty deployed among
  `needs_driven` kitties — and scoring runs record zero fallback-taken
  decisions.
- **SC-005**: Deployment safety — the policy behavior's 99th-percentile
  decision latency is under 10% of the default decision budget on the
  reference machine, and the entire existing CI suite (welfare,
  determinism, invariants, fairness) passes with a policy kitty in the
  roster.
- **SC-006**: Constitutional cleanliness — the constitution is untouched at
  v1.1.0, the engine gains no reward concept, and zero new constants exist
  outside configuration.

## Assumptions

- **Phasing**: the work lands in independently valuable slices in this
  order — joint-action seam; encodings; reward + episodes; Python surface;
  evaluation harness; policy behavior. The seam alone is worth shipping
  (scripted scenarios, replay tooling, the backlog's plugin door).
- **Where code lives**: the engine crate stays pure; encodings, reward,
  episodes, evaluation, and the policy behavior live in a new RL crate
  beside it, and the Python surface in a bindings crate beside that. The
  server is untouched.
- **Observation defaults**: 3 kitty slots, 4 critter slots, 2 chow, 2
  water, 2 sunbeam — sized to what a kitty can act on, not to the world's
  element populations: full visibility of the default roster (3 = roster
  − 1), and for anything contended — chow with its finite servings,
  sunbeams whose single tile one napping kitty occupies entirely — the
  nearest plus an alternative, which is what lets a policy learn to yield
  a contested resource and take the next one. Kitty slots need not equal
  roster − 1: larger rosters are partially observed by design (the
  nearest fill the slots, meows carry need signals world-wide, and the
  reward always counts the full roster), so one schema can serve worlds
  of any roster size — including a future where kittens grow it
  mid-world. Roughly a 160–200-value vector. An egocentric map patch is a
  config-off extension, not v1.
- **Action menu defaults**: with those slot counts the flat menu has 40
  entries (movement, solo and social rest/sleep/groom, eat, drink, chase
  and play by slot, six meow kinds, idle) — element slots are
  observation-only, so the menu size depends only on the kitty and
  critter slot counts. The "wait for me" meow stays reserved for the
  engine's approach etiquette (spec 012) and is not in the learned
  vocabulary. The menu grows only by codec version bump: indices are
  never repurposed and no reserved indices are held — artifacts are
  pinned to the schema versions they were trained against (FR-016), and a
  mismatch fails loudly at startup rather than quietly misbehaving.
- **Reward default**: level form of Nash welfare — the geometric mean of
  the roster's unclamped happiness, normalized to 0–1 with offset ε = 0.01
  (one happiness point) — not delta. The power-mean exponent defaults to
  p = 0 (Nash); p = 1 recovers the plain average, and strongly negative p
  approaches the least-happy kitty's score (max-min), all one config knob.
  Horizon default 2,000 ticks for training episodes, 20,000 for evaluation
  runs.
- **Inference**: v1 policies are small feed-forward networks executed by a
  minimal native forward pass — no heavyweight runtime; an ONNX-backed
  extension is anticipated but out of v1. Bit-exact inference is guaranteed
  per platform; cross-platform bit-exactness is best-effort.
- **Trainer**: out of scope. Any PettingZoo-compatible cooperative trainer
  (e.g., parameter-shared PPO variants) should work; one reference training
  script ships as documentation, not as a supported surface.
- **Not in this feature**: learned communication (meows keep their fixed
  meanings), neighbors' trait features in the kitty slots (anticipatory
  cooperation from a friend's metabolism is a backlog item, deferred
  until the trained meadow is proven — the slots' current needs carry
  the live form of the same signal, and adding traits later is an
  observation-schema version bump under this spec's own doctrine),
  self-play population dynamics, reward of any kind inside the engine,
  changes to the viewer, and the backlog's script/HTTP plugin transports
  (this feature's encoder and seam are deliberately reusable for them,
  but they remain their own backlog items).
- **Spec-only pass**: this document is the deliverable of the current pass;
  planning and task breakdown follow the standard spec-kit flow.
