# Research: No Stale Re-Proposal (spec 048)

No NEEDS CLARIFICATION markers remained after `/speckit-clarify` (FR-003 owner-ruled
full coverage). This file records the design research already performed in-session
(2026-09-02) that the plan's decisions rest on.

## R1 — Where the artifact lives (mechanism verification)

- **Decision**: fix at the behavior's decision side (`finish_what_you_started`),
  testing the decision snapshot.
- **Rationale**: verified in code — the behavior decides against the start-of-tick
  snapshot (Article V phase 1); `prune_dead_activity` runs at the top of the apply
  slot (world.rs:476, deliberate: "its proposal … still gets a normal hearing"). The
  counterpart's death is already visible in the snapshot whenever it crossed a tick
  boundary, so the behavior has everything it needs to decide fresh.
- **Alternatives considered**: fixing at validate/apply (rejected: the engine already
  handles it correctly; the waste is the behavior's, and reshaping proposals engine-side
  violates Article IV's "never a reshaped legal action"); re-deciding at apply time
  (rejected: breaks the Article V decide/apply split).

## R2 — Measured stakes (probe, 2026-09-02, branch `probe-reproposal-rate` @ 275896e)

Replayed the four Addendum 2 reference arms through the real pipeline
(`gather_decisions` + `run_applied_phases_from_decisions`), trajectory-exact
(row-count match with Experiments' census: 554 = 554). Window 1500–21500 per run:

| Class | dead-at-snapshot | re-proposed | refused | rescued |
|---|---|---|---|---|
| Critter play | 554–788 | 100% | 100% | 0 |
| Duet play | 0 | — | — | — |
| Groom | 54–100 | 100% | ~85% | ~10% (6–9/run) |
| Drink | 0 | — | — | — |

Same-tick race refusals (duet partner interrupts after this cat decided): 2,600–3,400
per run — structurally unreachable from decision time; spec pins them out of scope.

Consequences baked into the spec: SC-001 (critter rows → 0, nothing forgone),
US2's accepted groom-rescue trade-off, FR-003's full coverage costing nothing for
duets/drink (never fire), SC-005 (races persist).

## R3 — One definition vs a second predicate

- **Decision**: factor `prune_dead_activity`'s match into shared
  `World::counterpart_gone`; both consumers call it (plan D1).
- **Rationale**: FR-002 — the decision-side check and the engine's ending rule must
  mean the same thing forever. House precedent: 047's FR-009 (one `top_non_play`
  fold for the 042 score and the consent gate).
- **Alternatives considered**: duplicating the four checks in the behavior (rejected:
  silent drift is exactly the bug class FR-002 exists to prevent); a trait/method on
  `Activity` (rejected: the checks need world state — adjacency, availability,
  reciprocity — which lives on `World`).

## R4 — Scope of scene shapes

- **Decision**: full coverage — every arm of the engine's rule (owner-ruled 2026-09-02,
  spec Clarifications).
- **Rationale**: sharing the predicate wholesale is the no-drift shape; drink is
  defensively covered but unreachable (water permanent — element.rs pins
  `permanent_elements_never_expire`); duet coverage is free (probe: zero occurrences,
  because duets end both sides in one slot); groom is the same failure at lower volume.
- **Alternatives considered**: play-only (rejected by owner: option B at clarify).

## R5 — No configuration knob

- **Decision**: unconditional fix, no `[behavior]` field (FR-006).
- **Rationale**: this is a bug-shaped waste with a measured 0% upside in its dominant
  class — there is no meaningful world where an operator wants the stale proposal back.
  No knob means the defaults stamp cannot move and 039-D5 serialization discipline is
  moot here.
- **Alternatives considered**: a dial for A/B measurement (rejected: Experiments
  measures across binaries — their Addendum 3 re-baseline — not across a runtime flag;
  a knob would also force a stamp/serialization story for nothing).

## R6 — Behavior scope (which personalities)

- **Decision**: all personalities that continue scenes — `finish_what_you_started` is
  shared by needs_driven and playful, and stays shared (FR-005).
- **Rationale**: the helper's own doc comment: finishing what you started is "good
  sense, not a personality trait"; the artifact is not personality-specific (probe
  arms are 4/5 needs_driven seats). Playful-scoping (047-style parameterized variants)
  exists as a pattern but would preserve the waste for the majority of seats and
  complicate FR-002's one-definition story.
- **Alternatives considered**: playful-scoped variant (rejected as above); the
  scripted-teacher ripple is accepted the same way finding 1 was in 047 — retraining
  against the fixed teacher is already planned.
