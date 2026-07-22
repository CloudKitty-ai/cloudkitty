# Phase 0 Research: Multi-Agent RL Readiness

All Technical Context unknowns resolved. Each decision below records what
was chosen, why, and what else was weighed. R1 is the owner-requested
decision carried from spec review (2026-07-22): partner-priority slot
ordering versus FR-018's idle-bit mask exception.

## R1 — Never-all-zero mask: target-priority slot ordering (spec amendment)

**Decision**: Adopt **target-priority slot ordering**. The slot fill rule
becomes: slots are filled by the nearest eligible entities,
distance-ordered, ties broken by id — **except that the entity a kitty's
ongoing activity references is always guaranteed a slot in its table**
(the referenced kitty of a cuddle, co-sleep, groom, or social play in a
kitty slot; a played-with critter in a critter slot), displacing the
farthest otherwise-eligible occupant. The slot carries an
`is-activity-target` feature bit. FR-018's idle-bit exception is thereby
vacuous and is removed: the mask's never-all-zero guarantee becomes
**structural** — inside any activity's minimum the exact continuation is
always expressible in the menu, so the strict "applies as proposed" bit
for it is always set (untargeted continuations — eat, drink, solo
rest/sleep/play, self-groom — are untargeted menu entries and need no
guarantee). FR-018, the crowded-continuation edge case, and the
property-test carve-out language are amended in this same change
(Article VI: spec and design must agree).

**Post-plan verification (analysis finding I1, 2026-07-22)**: reading the
engine settled why the guarantee must be wider than duets. Inside the
minimum, `enforce_durations` (`world.rs`) rewrites *every* validated
proposal — including same-kind proposals with a different partner, which
`is_continued_by` accepts but normalization rewrites — to the exact
`Activity::continuation()`, and continuations carry their references
verbatim (`kitty.rs`): `Sleep{with: Some(X)}` for a co-sleep,
`Groom{target: Some(X)}`, `Play{target: Element{id}}` for critter play.
So the mid-minimum mask is exactly one entry, and the inexpressible
corner exists for co-sleeping and grooming friends (same
crowded-adjacency geometry as duets, roster ≥ 5) **and for a played-with
critter crowded off the four critter slots — reachable at the default
element population (5 critters, 4 slots)**. Keying the guarantee on the
engine's `duet_partner()` (cuddle and social play only) would have left
those corners open; `partner()`-plus-play-target is the correct key.

**Rationale**:

- *Structural beats exceptional.* The merged spec's idle-bit exception
  handled the crowded-out corner by special-casing mask semantics.
  Target-priority removes the corner instead of documenting it: the
  guarantee holds by construction at any roster or population size,
  including future kittens.
- *The property test becomes a pure oracle.* FR-018's guard — mask verdict
  equals the engine's validate-plus-enforcement verdict for every menu
  entry — no longer needs a carved, asserted exception. A test with no
  carve-outs is strictly stronger and simpler to trust.
- *The target stays observable exactly when it matters.* The
  continue-or-end decision mid-activity needs the referenced entity's
  state (a friend's needs, a critter's position); the idle-bit design
  could crowd it out of view at precisely that moment. Target-priority
  keeps the policy's input aligned with its most consequential
  in-activity choice, and the `is-activity-target` bit lets a
  parameter-shared policy identify which slot the continuation targets.
- *Training labels stay consistent.* Under the exception, idle sometimes
  meant "continue the activity" — an aliased label a policy must
  disentangle. Under target-priority, continue is always the activity's
  own entry.
- *The choice is free right now.* Nothing is trained yet; changing the
  slot rule later would be an observation-schema version bump
  invalidating artifacts. (The kitty-side corners need a ≥ 5 roster, but
  the critter-side corner is reachable at the default config — the
  verification note above — so the guarantee is not merely
  future-proofing.)

**Costs accepted**: the slot rule loses its "nearest K, ties by id"
one-liner (the exception moves from mask semantics into the slot rule —
but the slot rule is the right home: it is encoding policy, not a
falsified engine verdict); one extra feature bit per kitty and critter
slot; slot contents may reshuffle at activity start when a distant
target is promoted (acceptable — slots are distance-ordered and already
reshuffle on every movement tick).

**Alternatives considered**: (a) *Idle-bit exception* (the merged spec's
answer) — works, and is honest about being an exception, but bakes a
special case into mask semantics, the property test, and the training
labels, and can hide the activity's target from observation exactly
mid-activity; the verification note shows the exception would also have
had to widen beyond duets to stay sound. Rejected as the weaker of two
correct designs. (b) *Duet-only partner-priority* (this decision's first
draft) — leaves the co-sleep, groom, and played-with-critter corners
open; falsified by the engine reading above. Superseded. (c) *Pin the
target to slot 0* — stronger than needed; makes slot 0's meaning
mode-dependent and reshuffles all other slots on every transition.
Rejected. (d) *Grow slot counts with roster/population* — abandons the
fixed-size schema and the partial-observability-by-design doctrine.
Rejected.

## R2 — Python bindings: PyO3 + maturin, abi3, GIL released in step

**Decision**: `cloudkitty-py` is a `cdylib` built with **PyO3** and
packaged by **maturin** as abi3 wheels (`abi3-py39`). Observations, masks,
global states, and rewards cross the boundary as NumPy arrays via the
`numpy` crate. Every call that steps the engine (single or vectorized)
wraps the work in `Python::allow_threads` so the GIL is released while
Rust runs (FR-012's letter).

**Rationale**: PyO3 + maturin is the settled path for Rust-backed Python
packages (polars, pydantic-core, tokenizers); abi3 gives one wheel per
platform across Python versions; `allow_threads` is the standard,
well-audited GIL-release mechanism. The bindings stay logic-free — they
call `cloudkitty-rl` functions and copy fixed-size vectors out — so FR-007
(no Python reimplementation) holds by construction.

**Alternatives considered**: hand-rolled C FFI via cbindgen + ctypes
(error-prone, no packaging story); a socket/gRPC bridge (kills SC-003
throughput, adds nondeterministic transport); rust-cpython (unmaintained).

## R3 — Inference and artifact format: hand-rolled MLP, single-file artifact

**Decision**: v1 policies are small feed-forward MLPs (observation vector →
hidden layers with ReLU → 40 logits). Inference is a hand-rolled `f32`
forward pass in `cloudkitty-rl::policy` with a fixed, documented
evaluation order (no SIMD dispatch, no BLAS) so it is bit-exact per
platform. The artifact is a single file: a JSON header (artifact format
version, observation/action/mask schema versions, layer shapes,
activation) followed by a little-endian `f32` weight blob; the SHA-256
content hash of the whole file is computed at load, logged, and exposed
(FR-016). Startup validation checks magic, versions against the compiled
schemas, shape consistency, and hash integrity; any failure names the
offending config field and refuses to start.

**Rationale**: the spec's own assumption — no heavyweight runtime in v1.
A dense MLP forward pass is ~40 lines of Rust; owning it makes bit-exact
determinism trivial (fixed accumulation order) where BLAS backends and
ONNX runtimes make it a fight. Trainers export from any framework by
writing the documented format (a short reference exporter ships as
documentation with the training script).

**Alternatives considered**: ONNX Runtime (anticipated extension,
explicitly out of v1 per spec); candle/burn (large dependency surface,
backend-dependent numerics); NPZ/pickle artifacts (Python-native formats
would tempt Python-side loading, against FR-007's grain).

## R4 — Golden parity: the headless driver exposes each tick's proposals

**Decision**: the behavior-driven headless driver returns, per tick, the
**proposals it dispatched** (pre-validation, per kitty) alongside the tick
report — they are already in hand at dispatch. The parity suite (FR-004 /
SC-001) drives world A behavior-driven for ≥ 5,000 ticks collecting each
tick's proposals, replays them into world B via the joint-action seam from
the same seed, and asserts byte-identical serialization (periodic
checkpoints plus final full compare, including RNG state via the
serializable `SimRng`).

**Rationale**: the engine records only the *enforced* action today
(`last_action`), so proposal capture must be a new facility — but at the
dispatch seam it is a return value, not a hook: `gather_decisions` already
holds every proposal before handing them to the tick. No engine-state
change, no test-only cfg.

**Alternatives considered**: a capture callback threaded through the tick
(more machinery, same information); recording proposals into world state
(pollutes snapshots and persistence — rejected outright).

## R5 — Headless budgetless dispatch (FR-017): split decide from budget

**Decision**: core's dispatch splits into (a) a pure decision resolver —
runs each behavior against the frozen snapshot with panic isolation and
fallback, no wall clock — and (b) the **served-world wrapper** that adds
`tokio::time::timeout` around non-built-ins, exactly today's behavior. The
served tick loop uses (b); every headless driver (training, evaluation,
CI parity/determinism) uses (a), driven to completion with a blocking
executor (behaviors resolve without awaiting anything real; FR-014 keeps
the policy behavior I/O-free, so blocking on it is immediate). Each
resolved decision carries a provenance mark: `policy-made` or
`fallback-taken` (panic or, in the served world only, timeout), which the
harness counts and fails on (FR-013).

**Rationale**: this is the smallest refactor that makes SC-002/SC-005
claims true — reproducibility can never depend on host speed if no
headless path owns a clock. It also matches the constitutional argument
already in the spec: the budget protects the paced tick loop, and headless
drives have no tick loop to protect.

**Alternatives considered**: a very large headless budget (still a clock —
a loaded CI host could fire it; rejected); making built-in-style exemption
apply to policies (wrong at deploy — the served world must keep its
budget; the split keeps both worlds honest).

## R6 — Vectorization: thread-pool fan-out over independent worlds

**Decision**: the vectorized environment owns N fully independent worlds
(separate seeds, separate RNGs, zero shared state). A batch step fans the
N single-world steps across a scoped thread pool (`std::thread::scope`;
worker count configurable, default = worlds), inside `allow_threads`.
Results are gathered positionally, so scheduling order cannot affect
outputs — determinism per world is untouched by parallelism.

**Rationale**: worlds are embarrassingly parallel; scoped threads need no
new dependency and no unsafe. Near-linear scaling to 8 workers (SC-003)
is realistic because a single step is pure compute on small state.

**Alternatives considered**: rayon (fine, but a new dependency for a
20-line fan-out); Python-side multiprocessing (IPC overhead, per-process
interpreter cost, wheel complexity); async stepping (nothing to await).

## R7 — Crate layout: engine stays pure; one RL crate; zero-logic bindings

**Decision**: as in plan.md's structure. `cloudkitty-core` gains only the
seam, tick report, decision-seed exposure, and budgetless dispatch — no RL
vocabulary. `cloudkitty-rl` holds encodings, codec, mask, global state,
reward, episodes, vectorization, welfare metrics, the evaluation binary,
and the policy behavior — the single implementation FR-007 demands, linked
by every consumer. `cloudkitty-py` is a logic-free PyO3 wrapper over
`cloudkitty-rl`. `cloudkitty-server` adds a dependency on `cloudkitty-rl`
solely to construct `PolicyBehavior` when config names one.

**Rationale**: FR-021's engine purity and FR-007's single-implementation
rule fall directly out of the dependency graph; the server keeps serving
the same world. The long-run welfare metric computation currently lives
inside the CI test — it moves to `cloudkitty-rl::welfare` and the test
consumes it from there, so the harness and the CI gate score with
literally the same code (welfare accounting is state observation, not
reward; nothing feeds back into the engine).

**Alternatives considered**: encodings inside core (pollutes the engine
with RL vocabulary; rejected); separate crates per concern (dependency
ceremony without benefit at this size); metrics duplicated between test
and harness (drift risk — the exact failure FR-007 exists to prevent,
applied to metrics).

## R8 — Reward: recomputed unclamped, normalized power mean in `cloudkitty-rl`

**Decision**: `cloudkitty-rl::reward` recomputes each kitty's happiness
**unclamped** from the snapshot's needs and the configured weights
(`100 − Σ need×weight`, no floor), normalizes to [0, 1], and aggregates
with the configured power mean over the **full roster** (scripted kitties
included, FR-020): `p = 0` Nash (geometric mean, the default), `p = 1`
plain average, strongly negative `p` → max-min; offset `ε = 0.01` keeps
value and gradient finite at zero. Level reward by default; delta mode a
config option. Shaping defaults off; if enabled it must be potential-based
with coefficients in config (FR-009). Config block: `[rl.reward]` with
`p`, `epsilon`, `mode`, shaping table.

**Rationale**: direct transcription of FR-008; recomputation from needs is
a pure function of the snapshot, so the engine's clamped happiness stays
authoritative for everything the engine does while training keeps its
gradient below the display floor.

**Alternatives considered**: reading the engine's clamped happiness
(loses gradient at the floor — exactly what FR-008 forbids); per-kitty
individual rewards (abandons the cooperative objective; the team scalar
broadcast to every agent is the spec's design).

## R9 — Evaluation harness: a Rust binary in `cloudkitty-rl`

**Decision**: `kitty-eval`, a cargo binary in `cloudkitty-rl`. Input: a
behavior name (`needs_driven`, `playful`) **or** a policy artifact path;
a config; a seed list (default ≥ 10 fixed seeds); tick count (default
20,000). Output: JSON (machine) + table (human) reporting every long-run
welfare metric per seed and aggregated, the configured welfare aggregate
with plain mean and least-happy-kitty mean beside it, and the paired
same-seed delta against the `needs_driven` baseline. Policy scoring runs
both roster modes (all-policy; one policy among `needs_driven`) and
reports fallback counts; **any nonzero fallback count exits nonzero**
(FR-013). Runs on the budgetless headless path (R5).

**Rationale**: US3 is valuable before any training exists — baselining
built-ins must not require Python. A Rust binary shares `welfare.rs` and
the seam directly; the Python surface can still invoke it for trainer
workflows.

**Alternatives considered**: Python CLI (needs wheels to score built-ins;
metric code would sit behind bindings for no benefit); folding evaluation
into the test suite only (tests gate, but researchers need an invocable
tool with artifacts as input).

## R10 — PettingZoo conformance: duck-typed, optionally verified

**Decision**: the Python `ParallelEnv` implements the parallel-environment
convention duck-typed (`reset(seed)`, `step(actions)`, `agents`,
`possible_agents`, `observation_space`/`action_space` accessors, `state()`
for the global state, per-agent infos carrying applied action, survival
flag, mask, and decision seed). The `pettingzoo` package is an optional
test extra; when present, CI runs its API-conformance test on the wrapper.

**Rationale**: FR-011 names the convention, not the dependency; trainers
that want strict PettingZoo objects get a passing conformance check
without the package ever becoming a runtime requirement.

**Alternatives considered**: hard dependency on pettingzoo (needless
coupling for a convention); Gymnasium single-agent flattening (loses the
per-agent structure cooperative trainers consume).
