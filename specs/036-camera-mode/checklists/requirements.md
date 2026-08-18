# Specification Quality Checklist: Camera mode

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-17
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

Two passes were run. What the first pass caught, and what changed:

- **FR-004 named a margin without saying what it buys.** "A margin around the
  outermost" cannot be tested. Rewritten so the observable consequence is the
  requirement: when the fit binds, no kitty is drawn touching the frame's edge.
- **FR-022 said the camera must "read well" at 3, 4, and 5 kitties.** That is
  taste, not a requirement. Rewritten as coverage — every requirement here holds
  at each of the three rosters — with the aesthetic judgement left where it
  belongs, in SC-010.
- **SC-003 led with frame rate**, which is a machine measure. Reordered to lead
  with the outcome, motion staying as smooth as it is today, and keep the frame
  rate as how that gets measured.
- **FR-021 and FR-024 had no matching success criterion**, so two requirements
  carried no way to fail. Added SC-011 (two viewers at different zooms see the
  same world) and SC-012 (decoration is identical at every camera width).

Two deliberate exceptions to "no implementation details", both confined to the
Out of Scope and Dependencies sections and neither reaching a requirement:

1. **The control's geometry is quoted exactly** — the four percentages and the
   shared pin. Those were dialled with the owner on a real page over two rounds,
   and the notes recording them sit on an unmerged branch. Quoting them here is
   what stops the plan re-deriving them and spending those rounds again.
2. **The inert control is named by file.** It is a real dependency that has to
   be found, and naming it is how the plan finds it.

**FR-012 was the one inferred requirement** — that clicking a kitty while camera
mode is off turns camera mode on and follows her. The owner confirmed it on
2026-08-17, so it moved out of Assumptions and into the requirement itself.
Every rule in this spec is now settled rather than deduced.

### Re-validated after clarification, 2026-08-17

All 16 items still pass. The clarification session found one hole this checklist
had missed and closed it, and added one requirement that needed a criterion:

- **The follow lifecycle had a hole.** FR-011 through FR-020 said how a follow
  begins, how it is released by clicking the kitty again, and how it survives a
  reload, but never what the camera-mode control does to a live follow. Both
  readings were defensible and they ship different behaviour. Now closed by
  FR-027, with FR-026 adding a second release gesture so the control never needs
  to serve as one. "Requirements are testable and unambiguous" passed before
  this and should not have.
- **FR-028 arrived without a criterion**, which would have regressed "all
  functional requirements have clear acceptance criteria". Added SC-014.

### Re-validated after /speckit-analyze remediation, 2026-08-17

All 16 items still pass. The analysis pass found six issues at MEDIUM or above
across spec, plan and tasks; all six were remediated. Two changed the spec:

- **FR-029 was missing entirely.** The frame clamps to the world so a kitty
  followed into a corner is never shown against void — a decision taken in
  `data-model.md` during planning and never promoted to a requirement. An
  implementer reading only this spec would have built an unclamped camera and
  passed every stated criterion. Requirements-completeness passed before this
  and should not have, for the same reason it passed over the follow-lifecycle
  hole at clarify time: a decision recorded in a downstream artifact reads as
  settled without being *required*.
- **FR-017 did not say what the build does.** The card marking shows a dormant
  follow, which was a plan-level call. Now stated, with T045 free to overturn it.

The remaining four were task-coverage rather than spec defects: reduced motion
had an implementation task and no verification, three success criteria were
named in no task, Article V was verified only in the final phase, and the
Foundational gate depended half on a screenshot comparison this environment
cannot run.

One question in the queue was dissolved by reading the client rather than by
asking. SC-007 promises the restored view is in place before the first painted
frame, which looked unsatisfiable because there is nothing to aim at before the
first world update. The meadow already paints nothing until a world state exists
(`anim.js:2036` guards on `presentation.curr`), so the first painted frame has
kitties in it. The criterion stands and the edge case now records why.

SC-010 is a judgement criterion rather than a measurement, which is correct for
an art feature but means it cannot be automated. It needs the owner's eye at
each of the three roster sizes.
