# Feature Specification: Welfare Cuddle Predicate Correction — Measure Only Lawful Relief

**Feature Branch**: `021-welfare-cuddle-fix`

**Created**: 2026-07-27

**Status**: Draft — **deadline: before the first real certification campaign** (weeks horizon; experiments-session review, 2026-07-27)

**Input**: User description: "Correct the welfare metric's Cuddle relief-availability predicate. The long-run welfare accumulator's zero_distance_relief_exists counts ANY adjacent kitty as available Cuddle relief, but the engine's conscription rule (spec 006) means a kitty mid-activity cannot lawfully be drawn into a cuddle — the built-in behavior correctly declines to conscript a busy friend, yet the metric counts that as refusing available relief and increments the pinned-streak toward the MAX_PINNED_STREAK welfare bound. This is a false positive that could unfairly fail a trained policy's certification. The fix: the Cuddle arm counts only conscriptable (not mid-activity) friends. CRITICAL FRAMING REQUIREMENT: the spec MUST argue this is a semantics CORRECTION, not a loosening of the welfare guarantee."

## The problem in one paragraph

The pinned-streak welfare bound exists to catch a cat that sits beside
available relief and never takes it — a real failure mode worth failing a
certification over. Its availability predicate, written before the
conscription rules had a single authoritative home, asks a simpler
question than the world actually poses: for Cuddle, it counts *any*
adjacent kitty as available relief. But the engine's own law (spec 006)
says a kitty mid-activity cannot be drawn into a cuddle — the invitation
would lawfully bounce. So a cat pinned high on Cuddle beside only busy
friends is counted, tick after tick, as refusing relief *it was never
lawfully offered*, walking its streak toward the certification-failing
bound for behaving exactly correctly. The baseline cat rarely lingers in
that configuration; a trained policy under certification might, and would
be failed for it. This feature corrects the predicate to count only
conscriptable friends — the question the bound always claimed to be
asking.

## Why this is a correction, not a loosening (the load-bearing argument)

The tighten-only doctrine (spec 017) and the never-weaken-tests rule
exist to stop guarantees from eroding by drift. This change survives both
**because the guarantee is not what moves — the measurement is.** The
pinned-streak bound's stated meaning has always been "a kitty must not
refuse *available* relief indefinitely." Under spec 006 conscription, a
busy friend **is not available relief** — no lawful action exists that
extracts cuddle relief from a mid-activity kitty; proposing at one
resolves to Idle. The current predicate therefore counts relief that
does not lawfully exist, which makes the bound *stricter than its own
definition* in exactly the situations where strictness is
meaningless — no policy, however perfect, can take relief the engine
forbids. Correcting the predicate makes the metric measure what it
always claimed to measure; the guarantee — real refusals of real relief
still accumulate streak and still fail the bound — is untouched. This is
a deliberate re-baseline of a mismeasured bound, reconciled with its
guarding tests in the same change (Article VI governance), not a
weakening: every configuration the corrected bound would fail, the old
bound would also fail. The direction of change is one-way — the
corrected predicate counts a strict subset of what the old one counted —
and that subset relationship is the proof this cannot mask any failure
the bound was designed to catch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Certification judges only lawful refusals (Priority: P1)

As the owner certifying a trained policy, the pinned-streak bound fails a
policy only for refusing relief the engine would actually have permitted
it to take. A policy kitty pinned on Cuddle while every neighbor is
mid-scene accrues no streak for those ticks; the moment a neighbor
becomes free and adjacent, the clock runs again.

**Why this priority**: This is the certification-fairness stake — the
reason the deadline exists. A false certification failure would either
block a good policy or, worse, erode trust in the welfare gates
themselves.

**Independent Test**: A constructed scenario with a Cuddle-pinned kitty
adjacent only to mid-activity kitties accrues no pinned-streak for those
ticks under the corrected metric (and did under the old one); the same
scenario with one free adjacent kitty accrues streak identically under
both.

**Acceptance Scenarios**:

1. **Given** a kitty at pinned-level Cuddle pressure adjacent only to
   kitties who are mid-activity, **When** the welfare accumulator
   evaluates relief availability, **Then** no zero-distance Cuddle relief
   is counted and the pinned streak does not increment on that account.
2. **Given** the same kitty with at least one adjacent kitty *not*
   mid-activity, **When** the accumulator evaluates, **Then** relief is
   counted as available exactly as before — the correction changes
   nothing when lawful relief exists.

---

### User Story 2 - The guarding tests state the corrected semantics (Priority: P2)

As a maintainer, the welfare suite's tests express the corrected
predicate deliberately: any test that pinned the old any-adjacent
semantics is re-baselined *in this change* with the correction argument
cited, and a new case pins the busy-friend exclusion so the correction
cannot silently regress.

**Why this priority**: Article VI — the bound and its guarding tests move
together, in one reviewed change, or the never-weaken-tests rule has been
bypassed rather than honored.

**Independent Test**: The welfare test suite passes; the diff shows any
re-baselined assertion accompanied by the correction rationale; a
busy-friend-exclusion case exists and fails against the old predicate.

**Acceptance Scenarios**:

1. **Given** the corrected implementation, **When** the full welfare
   suite (unit + long-run property tests) runs, **Then** it passes, with
   any assertion changes traceable to the audited old-semantics cases and
   none weakening what the bound guards.

---

### Edge Cases

- **The subset property is the safety argument**: every world state the
  corrected predicate counts as available relief, the old predicate also
  counted. The reverse direction (old counts, corrected does not) is
  exactly the false-positive class being removed. No new failure mode can
  be introduced, only spurious ones removed.
- Self-exclusion is unchanged: a kitty is never its own cuddle relief.
- The other need arms of the availability predicate (Eat/Drink adjacency,
  Sleep/Play/Bath always-true backstops) are out of scope and must be
  byte-untouched — this is the Cuddle arm only.
- "Mid-activity" must mean exactly what the behavior stack's free-friend
  rule means (the conscription-eligibility test), so the metric and the
  behavior judge availability identically — the same
  single-source-of-truth principle spec 019 established for the behavior
  stack now extends to the measurement that judges it. (The metric lives
  in a different crate than `behavior/relief.rs`; the *rule* is shared,
  the code cannot be — mirror it with a comment naming the source, per
  the crate-boundary note in BACKLOG.)
- A duet in progress: both participants are mid-activity and correctly
  count as unavailable to a third kitty — cuddle puddles do not exist
  (BACKLOG P3), so pairwise busy is simply busy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The welfare availability predicate's Cuddle arm MUST count
  an adjacent kitty as available relief only when that kitty is
  conscriptable under the engine's rules (not mid-activity) — the same
  eligibility the built-in behavior's free-friend rule applies.
- **FR-002**: All other arms of the availability predicate MUST be
  unchanged, byte-for-byte.
- **FR-003**: The correction argument (semantics correction, not
  loosening: the bound was measuring relief that did not lawfully exist
  under spec 006 conscription; the corrected predicate counts a strict
  subset of the old one, so no genuine failure the bound guards can be
  masked) MUST be stated in this spec — this section and "Why this is a
  correction" ARE that statement — and summarized at the predicate's
  code site.
- **FR-004**: The existing welfare test suite MUST be audited for cases
  pinning the old any-adjacent semantics; any such case MUST be
  re-baselined in this same change with the correction cited, and a new
  case MUST pin the busy-friend exclusion (failing against the old
  predicate). No test may be deleted or weakened beyond the audited
  re-baseline.
- **FR-005**: A `needs_driven` certification rerun MUST be byte-identical
  to a pre-change baseline (the healthy baseline never trips the
  pinned-streak bound, so the correction is invisible there) — proving
  the change has no collateral effect on any currently-passing
  measurement.
- **FR-006**: No behavior, engine rule, configuration surface, or other
  welfare bound may change; simulation determinism is untouched (the
  metric is an observer).

### Key Entities

- **Availability predicate**: the per-tick, per-kitty judgment "does
  zero-distance relief for this need exist right now" feeding the
  pinned-streak accumulator; the Cuddle arm is the one being corrected.
- **Pinned streak**: consecutive ticks a need stays at pinned pressure
  while relief is judged available; bounded by the certification welfare
  gate.
- **Conscriptable friend**: an adjacent kitty not mid-activity — the only
  kind the engine permits drawing into a cuddle (spec 006).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The busy-friend scenario (pinned Cuddle, only mid-activity
  neighbors) accrues zero pinned-streak under the corrected metric and
  demonstrably accrued streak under the old one (the new guarding test
  fails against the old predicate).
- **SC-002**: The free-friend scenario is measured identically pre- and
  post-change.
- **SC-003**: The `needs_driven` certification rerun is byte-identical to
  the pre-change baseline (human and machine-readable outputs).
- **SC-004**: The full workspace test suite passes; the only assertion
  changes are the audited re-baselines plus the new exclusion case, each
  carrying the correction rationale.
- **SC-005**: The subset property is stated at the code site: a reviewer
  can point to the comment carrying the correction argument and the
  spec-006 rule it mirrors.

## Assumptions

- The conscription-eligibility test ("not mid-activity") is the complete
  lawful-availability condition for Cuddle under spec 006 — approach
  etiquette (spec 012) governs *how* a kitty closes distance, not whether
  an adjacent free kitty can be conscripted, so it does not enter the
  predicate.
- The metric's crate cannot consume `behavior/relief.rs` (crate boundary,
  by design — policy knowledge stays out of the measuring layer); the
  shared *rule* is mirrored with a comment naming spec 006 and the
  free-friend rule as the source, accepted as the correct altitude.
- The pre-change baseline for FR-005 is main at the commit this feature
  branches from; the 018-established byte-comparison procedure applies.
- This is certification-gating work: it lands before any trained-policy
  certification campaign, and the experiments session is notified on
  merge (their prereg §8 relies on these bounds).
