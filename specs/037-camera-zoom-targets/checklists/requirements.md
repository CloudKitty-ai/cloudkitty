# Specification Quality Checklist: Camera zoom targets

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-18
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

Two passes. What the first caught:

- **FR-007 did not exist.** The spec fixed apparent size and said nothing about
  the dials denominated in tiles that govern *distance* — the aim deadzone and
  the fit margin. Today the camera always frames 10–15 tiles, so their pixel
  effect is near-constant; widening that band makes a 1.5-tile deadzone mean 86px
  on a phone and 135px on WQHD. A spec that made size consistent while quietly
  making responsiveness inconsistent would have moved the problem rather than
  solved it. Added with SC-007.
- **The ceiling had no floor of its own.** Nothing said it must stay narrower
  than the world, and a pixel-led floor on a large display can push a
  multiple-of-the-floor ceiling out to the world's own width — which would make
  camera-on and camera-off identical at full zoom-out and silently retire 036's
  FR-005. Added as FR-005 here, with SC-005.

**No clarification markers, deliberately.** Three questions were candidates and
each had a defensible default recorded in Assumptions instead: the supported
display range (measured, not chosen), the "factor of 2" bar (a judgement, stated
as one, revisitable once dialled), and whether the ceiling should also become
pixel-aware (no — how much world to keep does not depend on pixels).

**The numbers are deliberately absent.** The target, the band and the ceiling are
dialled with the owner against the lab, as every art value in this client is.
The spec fixes what they mean; a spec that also fixed what they are would be
baking values nobody has looked at yet — and the checklist item this most risks
("requirements are testable") is satisfied by the criteria being expressed
against the fine-detail threshold and the measured display range rather than
against invented constants.

### Re-validated after clarification, 2026-08-18

All 16 items still pass. The clarification changed the feature's shape rather
than filling a gap, and three things in the spec contradicted it afterwards:

- **The Overview still said the ceiling was an absolute tile count**, which is
  the opposite of what was settled. Rewritten, and the Input line is annotated
  rather than edited — it records what was asked for, not what was decided.
- **A maximum tile count existed and no longer should.** With the ceiling
  expressed in pixels, a larger viewport framing more tiles at the same legible
  size is the *wanted* answer, not a case to guard. The requirement, the user
  story scenario and the edge case all went.
- **An Assumption argued against exactly what was chosen** — that the ceiling
  should stay a tile count because "how much world to keep does not depend on
  pixels". Replaced with why that reasoning failed: once range became the
  priority, the ceiling's job is to widen until the kitties stop being legible,
  which is a pixel question.

Also added a Fog Generation dependency. On today's 20×20 world the largest
viewports clamp the ceiling against the world's edge and lose part of their
range; at 40×40 nothing clamps. The feature is still worth shipping first —
it improves on 3.5× either way — but that is a conditional benefit and the spec
now says so rather than quietly assuming the world grows.

**One item is a qualified pass.** "No implementation details" — the Overview
carries a table of measured pixel sizes per display. Those are the evidence the
feature exists at all, and without them the problem statement is an assertion.
They describe the current *behaviour*, not the intended implementation.
