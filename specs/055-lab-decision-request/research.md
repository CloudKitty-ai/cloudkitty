# Research: The wire's DecisionRequest on the lab binding (spec 055)

No NEEDS CLARIFICATION remained after the owner's clarify pass
(2026-09-20: D1 render-without-consume, the pull method, loud errors).
Decisions below close the plan-level choices.

## R1 — The shared constructor takes the seed as a parameter

- **Decision**: `DecisionRequest::for_context(ctx, seed)` builds
  everything from the context except the seed, which each caller
  supplies: the server its consumed `ctx.rng.gen_u64()` (Article V
  unchanged), the lab the identical value derived on a local stream.
- **Rationale**: the seed is the ONLY lawful difference between the
  callers; parameterizing exactly that difference makes every other
  field's drift structurally impossible and keeps the server's draw
  position byte-for-byte where it is today.
- **Alternatives considered**: constructor draws internally from
  `ctx.rng` — rejected: forces the lab to consume (contradicts D1) or
  to fake a context rng (a second seed path, the drift the feature
  exists to kill).

## R2 — The render window is `pending_seeds`' lifetime

- **Decision**: `Episode::decision_request` is valid exactly while the
  episode holds dealt seeds for the upcoming tick (`pending_seeds`
  `Some`, not truncated, not poisoned) — i.e. after `reset`/`step`
  returns, before the next `step`.
- **Rationale**: `pending_seeds` is dealt at `arm()` (reset) and at the
  end of every `step` (`episode.rs:249/408`), which is precisely "the
  next decision's inputs exist"; the served request for that tick is a
  pure function of that state. No new state, no staleness.
- **Alternatives considered**: caching the render per tick — rejected,
  a cache is state that can go stale and the pull call is already the
  opt-in; rendering the PREVIOUS tick's request post-step — rejected,
  stale bytes are the exact failure mode the spec forbids.

## R3 — Binding error mapping

- **Decision**: the Episode error becomes a Python `ValueError` whose
  message is the engine's own wording (kitty id + reason: unknown id /
  no decision window / episode over).
- **Rationale**: matches the binding's existing error style (PyErr
  wrapping engine messages); the loud-error rule is owner-confirmed and
  the message text is asserted by test, so the wording is the contract.
- **Alternatives considered**: a custom exception class — rejected,
  nothing in the harness dispatches on type; None-return — owner-ruled
  out.

## R4 — VectorEnv is out of scope

- **Decision**: the method lands on `ParallelEnv` only.
- **Rationale**: the harness that consumes prompts (the LLM lab seat)
  drives the parallel env; vectorized training envs read tensors, not
  request text. Adding the same thin wrapper to `VectorEnv` later is
  mechanical and needs no new spec.
- **Alternatives considered**: both now — rejected as speculative
  (CLAUDE.md rule 2).

## R5 — The doc sentence's home

- **Decision**: one sentence at the end of `docs/plugins.md`
  §"The request", saying the lab binding serves the same line via
  `decision_request(kitty_id)` so harnesses never re-derive it.
- **Rationale**: the handover's acceptance list names this file; the
  wire text itself does not change (no version bump).
