# Tasks: The wire's DecisionRequest on the lab binding

**Input**: Design documents from `/specs/055-lab-decision-request/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/render-surface.md

**Tests**: required — every new behavioral claim carries a mutate.sh red
(house rule 5; spec FR-006). Red-first: the guard is written and RED (or
its mutation red is run) before the claim is trusted.

## Phase 1: Setup

- [x] T001 Confirm clean baseline: `cargo test --workspace` green at HEAD (fa6678c, post-main-merge) in /Users/elizabethkelly/ai/cloudkitty-lab-request

## Phase 2: Foundational (blocking prerequisites)

- [x] T002 Add `DecisionRequest::for_context(ctx: &DecisionContext, seed: u64) -> DecisionRequest<'_>` — the one construction (v = PROPOSAL_WIRE_VERSION, tick = ctx.world.tick, kitty_id = ctx.me.id, me = &ctx.me, world = &ctx.world.snapshot, seed, config = &ctx.config); doc comment states the seed-parameter rationale (R1: the callers' only lawful difference), in crates/cloudkitty-core/src/behavior/script.rs
- [x] T003 Refactor `try_decide` to `DecisionRequest::for_context(ctx, ctx.rng.gen_u64())` — the draw stays exactly where it is (Article V comment kept verbatim), serialization stays after the liveness check; kept pile: the full 18-test http_plugin suite green, in crates/cloudkitty-server/src/http_behavior.rs

## Phase 3: User Story 1 — The lab prompt is the served prompt (P1) [US1]

**Goal**: `Episode::decision_request(kitty)` renders the wire's own line, byte-equal to the served path, fog view only.

**Independent test**: same world/tick/kitty/dealt seed/config through both paths → identical bytes.

- [x] T004 [US1] Implement `pub fn decision_request(&self, kitty: KittyId) -> Result<String, …>` on Episode: valid while `pending_seeds` is Some and the episode is not truncated/poisoned; renders on demand (snapshot → `fog_for(kitty, radius)`, me from the snapshot, seed = first `gen_u64()` of a LOCAL `DecisionRng::from_seed(dealt.seed_for(kitty))` — nothing stored, nothing consumed), `serde_json::to_string` of `for_context`'s struct, in crates/cloudkitty-rl/src/episode.rs
- [x] T005 [US1] The byte test (analyze C1: a sweep, not one decision): over several ticks of a stepped episode × the FULL roster, render each decision through the server-path construction and through `Episode::decision_request` and compare the full strings byte for byte; also assert the seven documented fields, `v == PROPOSAL_WIRE_VERSION`, and that `world` blanks an out-of-disc friend (FR-004, US1 scenario 2), in crates/cloudkitty-rl/src/episode.rs (or tests/)
- [x] T006 [US1] Mutation cycle, ledger item 1 (as actually run — review corrected the planned tick mutation, which co-moves both sides of a shared body and is core e2e's guard): render the raw dealt seed instead of the first draw → the byte sweep AND the real-advisor capture test red; `scripts/mutate.sh --expect`, prediction first, in /Users/elizabethkelly/ai/cloudkitty-lab-request

## Phase 4: User Story 2 — Policy seats pay nothing (P2) [US2]

**Goal**: rendering is pull-only and side-effect-free: no call, no cost; any number of calls, same trajectory.

**Independent test**: identical seeded episodes with and without per-tick `decision_request` calls produce identical trajectories.

- [x] T007 [US2] The no-consume test (FR-005/SC-002): two episodes, same seeds and actions; one calls `decision_request` for every roster kitty every tick, the other never — assert identical observations, positions, and actions end to end; plus same-tick double-call returns identical bytes, in crates/cloudkitty-rl/src/episode.rs (or tests/)
- [x] T008 [US2] Mutation cycle, ledger item 2: make the render draw from a stored/kitty stream instead of a local one → the no-consume test reds (prediction stated first), in /Users/elizabethkelly/ai/cloudkitty-lab-request
- [x] T009 [US2] Loud errors (owner-confirmed): unknown kitty id, and a call after the episode ends, each error naming the kitty and the reason — never None/placeholder; mutation cycle, ledger item 3 (placeholder render on unknown id → error test reds), in crates/cloudkitty-rl/src/episode.rs

## Phase 5: User Story 3 — Lab users can find it (P3) [US3]

**Goal**: the binding serves the method; the docs point at it; the wire text is untouched.

**Independent test**: pytest drives `env.decision_request` through the built binding; plugins.md gains exactly one sentence.

- [x] T010 [US3] `ParallelEnv#decision_request(kitty_id: int) -> str` — thin PyO3 wrapper, engine error → `ValueError` with the engine's message verbatim (R3); VectorEnv deliberately not touched (R4), in crates/cloudkitty-py/src/lib.rs
- [x] T011 [US3] Python-surface test: reset → `decision_request(id)` parses as JSON with the seven fields; unknown id raises `ValueError` naming it, in crates/cloudkitty-py/tests/test_parallel_env.py (analyze U1: the existing ParallelEnv suite)
- [x] T012 [US3] One sentence at the end of docs/plugins.md §"The request" pointing lab users at `decision_request(kitty_id)` (contract wording from contracts/render-surface.md); no other wire doc text changes, in docs/plugins.md

## Phase 6: Polish & cross-cutting

- [x] T013 [P] Changelog one-liner under `## Unreleased` (public-voice at write time; no compatibility marker — no wire, config, or world change; PR number stamped at PR-open time), in CHANGELOG.md
- [x] T014 Full sweep: `cargo fmt --check`, clippy clean, `cargo test --workspace`, and the binding build + pytest (VIRTUAL_ENV set before `maturin develop` — house gotcha); quickstart hand-check (call the method, read the line, trigger the ValueError), in /Users/elizabethkelly/ai/cloudkitty-lab-request
- [x] T015 Push branch, open the PR (house body: summary, three-item red ledger with predictions, the three owner confirmations cited, generated-with + session lines), CI green, ping Experiments mergeable (their first lab read — 5 seeds × 5000 ticks, tier 2 package world — runs the day the surface lands) — merge on the owner's word, in /Users/elizabethkelly/ai/cloudkitty-lab-request

## Dependencies

- T001 → all. T002 → T003 (caller) and T004 (renderer).
- US1 (T004–T006) → US2 (T007–T009): the no-consume test calls the US1
  surface. US3 (T010–T012) needs T004 only; T010/T012 can run parallel
  to US2 once T004 lands.
- T013 [P] with US3; T014 → T015 last.

## Implementation strategy

MVP = Phases 1–3 (the byte-equal render on Episode — the whole seam
lesson). US2 makes its safety claims proven, US3 makes it reachable
from Python; all three ship in this one PR. No deploy rides the arc;
nothing served changes.
