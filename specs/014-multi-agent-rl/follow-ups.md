# Follow-ups: deliberate deferrals from the third review (2026-07-22)

Three findings were judged real but wrong to fix now — each needs a design
decision or a trigger that does not exist yet. Everything else the review
surfaced was fixed in the round-3 pass.

## 1. Provenance-carrying proposals

**Trigger: the next consumer of the joint-action seam** (a replay tool, a
server joint-action endpoint, a second harness).

`World::tick_with_proposals_seeded` marks every present proposal
`PolicyMade` — it cannot know a scripted proposal came from the fallback —
and `Episode::step` restores the honest dispatch provenance into the
report after the fact (episode.rs, the `scripted_marks` overwrite). Today
the episode is the seam's only mixed-control consumer, so FR-017 holds;
a second consumer would silently report `FallbackTaken` decisions as
`PolicyMade`.

The deeper mechanism is a provenance-carrying `ProposalEntry` (the seam
records truth at the source; no consumer rewrites reports). The trade-off
that kept it out of round 3: provenance at the seam would become
**driver-asserted** rather than seam-observed — the report would trust
callers to mark their own fallbacks — which weakens the honesty story the
seam currently owns, and it changes `JointProposal`'s serde shape. Decide
deliberately when the second consumer arrives.

**Trigger bookkeeping (2026-07-27):** the stated trigger has technically
fired — the counterfactual twin probe (`experiments/tools/twin-probe`,
2026-07-25) is a second seam consumer — and it fired *benignly*: the
probe reads only applied actions and rewards from its `TickReport`s,
never provenance, so no `FallbackTaken` decision can be misreported
through it and no action is needed. The trigger is re-scoped
accordingly: the real decision point is the **first consumer that reads
provenance from raw seam `TickReport`s** (without the episode layer's
`scripted_marks` restoration).

## 2. One first-reset semantic across the three surfaces

**Trigger: the first support question about seeds, or the next surface.**

The surfaces disagree about what the first unseeded reset means, each
conforming to its own documented contract:

- `VectorEnv` (Python): constructor `seeds=` replay verbatim, once.
- `ParallelEnv` (Python): no constructor-seed notion; the first bare
  `reset()` advances the episode's fresh-seed chain past the config seed.
- `VectorizedEnvironment` (Rust): no constructor-seed notion at all.

Nothing is broken, but the same trainer loop gets two different
first-reset behaviors depending on the surface. The unifying fix is a
pending-first-seed notion on `Episode` itself (consumed by the first
`reset_fresh`), inherited by all three surfaces; it touches the contract
doc and all three layers, so it should land as one deliberate change, not
a ride-along.

## 3. Cancellation semantics for stateful external advisors

**Trigger: building `HttpBehavior` (or any request/response advisor).**

The served dispatch runs non-builtin advisors to completion on a detached
blocking thread when they exceed the budget (`behavior/mod.rs`,
`spawn_blocking` + dropped `JoinHandle`) — necessary to preempt
synchronous compute, but it means a timed-out advisor's side effects land
*after* the tick already took the fallback. A stateful request/response
advisor would go off-by-one: every later decision would answer the
previous tick's observation. Today no such advisor exists (policies are
pure functions of the observation). Whoever builds the first one must
design for cancellation — e.g. a request id echoed in the response, or an
explicit abort channel — rather than assuming the engine cancels work at
the budget boundary.
