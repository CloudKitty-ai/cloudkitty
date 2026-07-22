# Implementation Plan: Multi-Agent RL Readiness

**Branch**: `014-multi-agent-rl` | **Date**: 2026-07-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-multi-agent-rl/spec.md`

## Summary

Open the engine's advisor door to learned brains, in six independently
valuable slices: (1) a **joint-action tick seam** in the engine that advances
the world one constitutional tick from externally supplied per-kitty
proposals, byte-identical to the behavior-driven tick from the same seed;
(2) versioned **observation / action / mask / global-state encodings**
implemented exactly once, in Rust, in a new `cloudkitty-rl` crate; (3) a
**Nash-welfare team reward** and truncation-only episodes computed entirely
outside the engine; (4) a **Python surface** (PyO3 bindings, PettingZoo
parallel convention, vectorized) in a new `cloudkitty-py` crate; (5) an
**evaluation harness** that scores any brain against the existing long-run
welfare bar; (6) a **policy behavior** that seats a validated, content-hashed
artifact in the existing `Behavior` seam for deployment.

The load-bearing research decision (owner-requested, carried from spec
review): the never-all-zero mask guarantee moves from FR-018's idle-bit
exception to **partner-priority slot ordering** — the duet partner is
guaranteed a kitty slot, making the guarantee structural. FR-018 and its
property-test language are amended in this same change (Article VI); see
[research.md](research.md) R1.

## Technical Context

**Language/Version**: Rust 2021 edition (existing workspace toolchain);
Python ≥ 3.9 for the training surface (abi3 wheels)

**Primary Dependencies**: existing workspace deps only for the engine
(serde, rand_chacha, tokio, async-trait, proptest for tests). New, confined
to the new crates: PyO3 + maturin (bindings), `numpy` crate (array interop).
Deliberately **no** ML runtime — v1 inference is a hand-rolled MLP forward
pass (research.md R3); the trainer itself is out of scope.

**Storage**: N/A — episodes are ephemeral by spec (never persisted); policy
artifacts are content-hashed files referenced from `cloudkitty.toml`.

**Testing**: `cargo test` + proptest (golden parity, codec totality,
encoder determinism, mask soundness as a pure oracle test, reproducibility);
existing CI suites (welfare, determinism, invariants, fairness) re-run with
a policy kitty; pytest smoke tests for the Python surface (PettingZoo
package at most an optional test dependency).

**Target Platform**: macOS + Linux (dev and CI, matching the server today);
per-platform Python wheels; bit-exact inference guaranteed per platform,
cross-platform best-effort (spec assumption).

**Project Type**: multi-crate Rust workspace gaining two crates
(`cloudkitty-rl`, `cloudkitty-py`) beside the untouched-semantics engine
and server.

**Performance Goals**: SC-003 — ≥ 5,000 environment steps/second
single-threaded on the default 32×32 4-kitty world, near-linear scaling to
8 vectorized workers; SC-005 — policy p99 decision latency < 10% of the
decision budget.

**Constraints**: bit-reproducibility on every headless path (FR-017:
budgetless dispatch); Python's GIL released during engine work (FR-012);
reward never enters the engine (FR-008, FR-021); served world semantics,
client, persistence, and constitution untouched (FR-021); every new
constant in configuration (Article VI).

**Scale/Scope**: 4-kitty default roster (one schema serves any roster —
partial observability by design); 40-entry action menu v1; ~160–200-value
observation vector; global state ~ full roster + bounded element summary;
20,000-tick evaluation runs over ≥ 10 seeds.

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design. Result:
**PASS** both times — no violations, no Complexity Tracking entries.*

- **Article I (no suffering)** — PASS. The engine is untouched during
  rollouts: clamps, happiness floor, and safeguard spawner run inside the
  joint-action tick because it *is* the tick. Reward lives in
  `cloudkitty-rl`/the harness; no code path feeds it back. The design adds
  no new need, no negative state, no punishment mechanic.
- **Article II (no death)** — PASS. Terminations constitutionally always
  false; the agent set is fixed for an environment's life; no removal path
  is added anywhere (the seam bypasses only behavior dispatch).
- **Article III (never alone)** — PASS. Environment construction runs the
  same config validation (≥ 2 kitties); per-tick invariant assertions run
  inside the joint-action tick unchanged.
- **Article IV (engine is the law)** — PASS. External proposals traverse
  the same validate → duration-enforce → apply gauntlet in the same fair
  order; malformed/absent entries resolve to idle. At deploy the policy is
  a non-built-in under budget, panic isolation, and fallback. Headless
  drives dispatch without the wall-clock budget (FR-017) under the
  time-budget clause's purpose reading argued in the spec — panic isolation
  and fallback stay in force headlessly, and every headless decision is
  marked policy-made or fallback-taken.
- **Article V (server-authoritative, deterministic)** — PASS. The served
  world and server semantics are untouched (the server gains only the
  ability to *construct* a policy behavior from config, exactly like
  naming `playful`). Training embeds the engine headlessly per the CI
  precedent. The seam preserves the master RNG's draw shape (FR-002), so
  determinism strengthens rather than bends.
- **Article VI (spec-first, test-guarded, no magic numbers)** — PASS. This
  plan follows the merged spec; the one design decision that changes spec
  text (partner-priority slot ordering, research.md R1) amends FR-018 and
  its property-test language **in this same change**, keeping spec and
  design agreed. Every guard named in the spec (parity, codec totality,
  encoder determinism, mask oracle, reproducibility, welfare with a policy
  kitty) is assigned a home in the contracts and joins CI. All new
  constants (slot counts, normalization, reward p and ε, horizons, artifact
  paths) live in configuration with documented defaults.

## Project Structure

### Documentation (this feature)

```text
specs/014-multi-agent-rl/
├── plan.md              # This file
├── research.md          # Phase 0 output — all decisions resolved
├── data-model.md        # Phase 1 output — entities, layouts, state rules
├── quickstart.md        # Phase 1 output — end-to-end validation guide
├── contracts/
│   ├── joint-action-seam.md   # Engine seam API + tick report + parity capture
│   ├── encodings.md           # Observation v1, 40-entry menu, mask, global state
│   ├── python-env.md          # PettingZoo parallel surface + vectorized form
│   ├── policy-artifact.md     # Artifact format, validation, config wiring
│   └── evaluation-harness.md  # Scorer CLI, output schema, failure modes
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
crates/
├── cloudkitty-core/           # Engine — gains ONLY the seam, no RL vocabulary
│   └── src/
│       ├── world.rs           # tick_with_proposals(), shared phase pipeline
│       ├── behavior/          # headless budgetless dispatch, proposal capture
│       └── ...                # (everything else untouched)
├── cloudkitty-rl/             # NEW — everything that knows what "RL" means
│   └── src/
│       ├── observe.rs         # observation encoder + target table (v1 schema)
│       ├── codec.rs           # 40-entry action codec, total both directions
│       ├── mask.rs            # legal-action mask (partner-priority guarantee)
│       ├── global_state.rs    # privileged critic view (v1 schema)
│       ├── reward.rs          # unclamped happiness → power-mean welfare
│       ├── episode.rs         # reset/step/truncation, mixed control
│       ├── vector.rs          # N-world batch stepping
│       ├── policy.rs          # artifact load/validate/hash + MLP forward pass
│       ├── behavior.rs        # PolicyBehavior: encode → infer → mask → select
│       ├── welfare.rs         # long-run welfare metrics (shared with CI suite)
│       └── bin/
│           └── kitty-eval.rs  # evaluation harness binary
├── cloudkitty-py/             # NEW — thin PyO3 layer, zero logic of its own
│   └── src/lib.rs             # ParallelEnv, VectorEnv wrappers; GIL release
└── cloudkitty-server/         # Gains one dependency: registers PolicyBehavior
                               # from config; otherwise untouched
```

**Structure Decision**: two new crates beside the engine (research.md R7).
`cloudkitty-core` stays pure — it gains the joint-action seam, the tick
report, budgetless headless dispatch, and nothing that names observations,
rewards, or policies. `cloudkitty-rl` holds the single Rust implementation
of every encoding (FR-007) plus reward, episodes, evaluation, and the
policy behavior, so training, evaluation, and deployment all link the same
code. `cloudkitty-py` wraps `cloudkitty-rl` with PyO3 and contains no
logic, so there is nothing in Python to drift. The server's only change is
constructing `PolicyBehavior` when config names one — the same doctrine as
any behavior name, with startup failure on a bad artifact (FR-016).

## Complexity Tracking

No constitutional violations to justify — table intentionally empty.
