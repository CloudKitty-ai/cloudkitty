<!--
Sync Impact Report
==================
Version change: 1.1.0 → 1.2.0
Rationale: Amendment ratified by the owner (2026-07-23, spec 016): Article IV's
first clause said failed proposals "resolve to a safe no-op (idle)" while its
second clause promised "automatic fallback to the default built-in behavior" —
and the engine has always delivered the fallback for failed advisors. The
clause now names BOTH constitutionally safe resolutions — the default built-in
(needs-based) fallback behavior, which is the default resolution, and the idle
no-op — since there are scenarios where each is right (unintelligible proposal
→ fallback; well-formed but illegal proposal → idle). Guarded by spec 016's
round-trip/rejection suite and dispatch fallback tests per Article VI.

Modified principles: Article IV, clause (1) (proposal resolution outcomes)
Added sections: none
Removed sections: none

Templates requiring updates: none (plan-time Constitution Check gates derive
from this file automatically)

Follow-up TODOs: none.

Previous report (1.0.0 → 1.1.0, spec 013): Article V's tick-order clause (2)
restated as a fairness principle rather than a stable-id mechanism, guarded by
a fairness property test. Initial ratification note: the user-authored document
superseded a generic placeholder constitution that was never adopted and does
not count toward version history.
-->

# CloudKitty Constitution

CloudKitty is a cute, safe sandbox. Every technical decision serves that identity. The
articles below are inviolable: no feature, refactor, optimization, or behavior plugin may
violate them, and each must be guarded by automated tests that run in CI.

## Article I — Kitties Cannot Suffer (NON-NEGOTIABLE)

- Needs are bounded values (0–100). There is no concept of pain, injury, sickness,
  starvation, or any negative state beyond need pressure.
- A **distress threshold** exists (default 90). Any need crossing it is recorded as a
  *distress event* (kitty id, need, tick) and exposed via the API. Distress events are a
  signal for the world and for behaviors — never a punishment mechanic.
- The world guarantees relief: whenever any kitty's need exceeds the **safeguard
  threshold** (default 75), at least one resource capable of satisfying that need must
  exist and be reachable. If none exists, the environment must spawn one on the next
  environment phase.
- Happiness has a floor (default 5) and can never reach zero.

## Article II — Kitties Cannot Die (NON-NEGOTIABLE)

- No death, despawn, removal, health, or damage mechanic exists for kitties — not as a
  capped state, not as an edge case. This is enforced structurally: no code path in the
  engine removes a kitty from the world.
- Expiration applies only to environment elements (chow, bugs, greebles, sunbeams,
  temporary water). It must never apply to kitties.

## Article III — Kitties Cannot Be Alone (NON-NEGOTIABLE)

- Every world contains a minimum of 2 kitties at all times.
- Configuration specifying fewer than 2 kitties is invalid and must be rejected at
  startup with a clear error. A runtime assertion re-verifies the invariant every tick.

## Article IV — The Engine Is the Law; Behaviors Are Untrusted Advisors

- Kitty behaviors (including external scripts, APIs, or local services) only
  *propose* actions. The engine validates every proposed action against the rules and
  current world state. Invalid, malformed, late, or absent proposals resolve safely to
  one of two constitutionally safe outcomes: the **default built-in (needs-based)
  fallback behavior** — the default resolution — or the **idle no-op**. Never an error
  state, never a rule violation, never a reshaped legal action.
- Every behavior decision is subject to a time budget with automatic fallback to the
  default built-in behavior. A slow or failed behavior can degrade one kitty's
  cleverness, never the tick loop or the constitution.

## Article V — Server-Authoritative, Deterministic Simulation

- All game logic lives on the server. The client is a pure view: it renders state and
  never computes or mutates simulation outcomes.
- The simulation is deterministic given a seed and configuration (for built-in
  behaviors): same seed + config + tick count → same world state. All randomness flows
  through a single seeded RNG.
- Tick order is fixed: (1) all kitties decide against the same start-of-tick snapshot,
  (2) actions are applied in a per-tick order that is **fair**: every kitty has an
  equal, reproducible chance to act first, and no kitty is ever systematically
  favored, (3) the environment resolves (movement of bugs/greebles, expiry, spawning,
  safeguard checks), (4) invariants are asserted.

## Article VI — Spec-First, Test-Guarded

- Features are specified before they are implemented. The spec is the source of truth;
  code that disagrees with the spec is a bug in one of them and must be reconciled.
- Articles I–III are covered by property-based tests (thousands of ticks, randomized
  configs and behaviors) and the suite is a required CI gate.
- Simulation constants (thresholds, rates, weights, bounds) live in configuration with
  documented defaults — never as magic numbers in code.

## Governance

- Amending an article requires updating this constitution, the spec, and the guarding
  tests in the same change.
- The "Later features" list in the spec is explicitly out of scope for the MVP; MVP
  design decisions should avoid *blocking* them but must not implement them.

**Version**: 1.2.0 | **Ratified**: 2026-07-18 | **Last Amended**: 2026-07-23
