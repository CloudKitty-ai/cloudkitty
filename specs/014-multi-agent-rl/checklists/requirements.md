# Specification Quality Checklist: Multi-Agent RL Readiness

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-21
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details beyond deliberate Assumptions notes (crate
      layout, slot/menu defaults, inference posture — recorded as decided
      defaults, adjustable at review; mechanisms otherwise left to plan.md)
- [x] Focused on user value and business needs (researcher, trainer, owner
      journeys; the welfare bar as the product's definition of success)
- [x] Written for non-technical stakeholders (constitutional framing carries
      the argument; RL terms introduced where unavoidable and explained)
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (throughput and parity are
      stated as observable outcomes with the measurement method to be
      documented alongside)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded (FR-021 scope guard; "Not in this feature"
      assumptions)
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows (seam → rollouts → evaluation →
      deployment)
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No constitutional amendment required; compliance argued article by
      article in the spec

## Notes

- The direction-setting decisions were made by the owner in conversation:
  spec-kit deliverable, spec-only pass, Python-via-native-bindings
  PettingZoo stack, and training under the full constitution (2026-07-20);
  inequality-averse team reward — Nash welfare (geometric mean) by
  default, generalized to a configurable power mean — so raising a
  less-happy kitty's happiness is worth more than the same gain for a
  happier one (2026-07-21). Remaining technical defaults (2,000-tick
  training horizon, slot counts, 40-entry action menu, greedy selection,
  per-platform bit-exact inference) are recorded in Assumptions with
  rationale and are open to revision during spec review.
- The one constitutional clause requiring explicit argument — Article V's
  "all game logic lives on the server" — is resolved in the spec's opening
  and compliance sections: training embeds the engine headlessly per the
  CI precedent; the served world is never touched by a non-server process.
- Spec-review revisions (2026-07-21, PR #19 review): budgetless headless
  dispatch made an explicit requirement (FR-017 — the wall-clock budget
  applies only in the served world, so SC-002/SC-005 are achievable as
  written; scope guard renumbered to FR-018); SC-003 corrected to the
  4-kitty default roster; SC-004's bound list completed with pinned
  streaks ≤ 25; observation slot rationale restated (sized to what a
  kitty can act on — nearest-plus-alternative for contended elements,
  partial observability by design for larger rosters and future kittens)
  with sunbeam slots 1 → 2; action-menu extensibility doctrine recorded
  (growth only by codec version bump, no repurposed or reserved indices).
- Cooperative-training amendment (2026-07-21, PR #19 review discussion):
  four training-fidelity gaps closed — legal-action masks exposed to
  trainers (advisory against the frozen snapshot; within-tick contention
  stays the engine's, FR-018); a privileged global state for centralized
  critics, never given to deployed behaviors (FR-019); per-kitty static
  trait features in the observation so a parameter-shared policy serves
  heterogeneous kitties (FR-005); and mixed-control training/evaluation —
  policy kitties among built-in kitties, reward always counting the full
  roster (FR-020, FR-013, SC-004). Two review findings folded in:
  headless dispatch marks every decision policy-made or fallback-taken
  and the harness fails scoring runs with a nonzero fallback count, so a
  broken artifact can never ride the fallback through SC-004 (FR-017,
  FR-013); and the Article IV compliance argument now covers the
  time-budget clause's purpose reading explicitly. Scope guard
  renumbered FR-018 → FR-021.
- Amendment review fixes (2026-07-21, second review round): deployed
  selection operates over the masked menu — the same mask implementation
  training used — closing the train/deploy action-distribution skew
  (FR-015); mask semantics pinned to one bit per entry, "would apply as
  proposed" (validation passes, no duration rewrite), with a guarding
  property test against the engine's own validate-plus-enforcement
  verdict (FR-018, Article VI list); SC-002 and US2 reproducibility
  widened to mask and global-state streams; FR-007's consumers clause
  rephrased so the global state's training/evaluation-only life (FR-019)
  no longer contradicts it; FR-013's dual-roster duty scoped to policy
  scoring. Owner decision: neighbors' trait features in the kitty slots
  are out of scope until the trained meadow is proven — recorded in "Not
  in this feature" and on the backlog (anticipatory cooperation).
- Never-all-zero mask guarantee (2026-07-21, second-round follow-up): the
  strict "applies as proposed" bit could go all-zero in one corner — a
  duet partner crowded off the slot table in a ≥ 5-kitty roster leaves
  the continuation inexpressible — which would NaN masked softmax in
  training and empty FR-015's masked selection at deploy. FR-018 now
  sets the idle bit as the documented exception (harmless: mid-activity
  the engine continues the scene whatever is proposed), the guarding
  property test asserts that carve-out explicitly, and a matching edge
  case names the corner.
- Plan-phase amendment (2026-07-22, /speckit-plan research decision R1,
  owner-requested revisit): the never-all-zero guarantee moves from the
  idle-bit exception to **partner-priority slot ordering** — a kitty's
  current duet partner is always granted a kitty slot (displacing the
  farthest otherwise-eligible, flagged is-my-partner), making the
  guarantee structural at any roster size and the FR-018 property test a
  pure oracle with no carve-outs. FR-018, the crowded-duet and
  more-kitties-than-slots edge cases, FR-005's slot description, and the
  Assumptions slot rationale amended in the same change (Article VI);
  full weighing in plan-phase research.md R1.
