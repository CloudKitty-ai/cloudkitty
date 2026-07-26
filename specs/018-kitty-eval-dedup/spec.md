# Feature Specification: Kitty-Eval Dedup — Single-Source the Certification CLI

**Feature Branch**: `018-kitty-eval-dedup`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "Deduplicate the kitty-eval binary against the suite/harness library. The kitty-eval CLI currently re-implements logic the cloudkitty-rl library already owns, and duplicates whole blocks against itself: the --brain/--artifact subject-resolution ladder appears twice within the binary (in run_suite and in main, with error messages duplicated verbatim), the human report rendering mirrors the private suite::print_run_panel line-for-line, the determinism self-check re-implements suite::self_check inline, and the single-config baseline+mode orchestration in main copies the score_standard algorithm from suite.rs. The two report paths (suite mode and single-config mode) are required to render runs identically — during spec 017 this was verified by hand-diffing output bytes; nothing structural prevents drift today. Goal: single-source each of these four concerns so every future CLI-contract or report-format change is one edit site instead of up to four, and report drift between the two modes becomes structurally impossible. This is a behavior-preserving refactor: the CLI's observable contract (flags, exit codes 0-4, JSON report shape, human report bytes, error messages) must not change, verified by byte-identical output against pre-refactor runs of both a suite run and a single-config certification run, plus the existing integration and unit test suites passing unchanged. No new features, no new flags, no report format changes."

## The problem in one paragraph

The certification CLI (`kitty-eval`) and the evaluation library grew the same
logic in parallel: four concerns — how a candidate subject is resolved from
the command line, how a run is rendered for a human, how a run is
double-checked for determinism, and how a subject is scored across roster
modes against its baseline — each exist in two places that must behave
identically. The tool's credibility rests on both of its modes (suite exams
and single-config certification) describing runs the same way; during spec
017 that agreement was verified by hand-comparing output bytes. Discipline is
currently the only thing preventing the copies from drifting apart, and a
drift here would not look like a bug — it would look like a legitimate result
that quietly means something different in one mode than the other. This
refactor removes the copies so agreement is guaranteed by construction, not
by vigilance.

## Clarifications

### Session 2026-07-26

- Q: Should subject resolution move into the library now, anticipating a
  second CLI consumer? → A: Start minimal — it stays binary-local; promote
  into the library later if a second consumer materializes.
- Q: Scattered `pub` promotions, or one gathered support module? → A:
  Gather every promoted item into one documented CLI-support module
  (internal plumbing, not a stability promise); later promotions join it.
- Q: Is the byte-comparison a one-time recorded procedure, permanent
  golden files, or a structural share-guard test? → A: One-time recorded
  procedure plus a permanent structural share-guard test (A + C). Golden
  files (B) are deliberately deferred — reconsider only once the report
  reaches a very stable state.
- Q: Does anything non-human parse the human-readable report? → A: No,
  and none is planned; the machine interface is the JSON report.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run reporting is single-sourced (Priority: P1)

As a maintainer changing how evaluation runs are presented (a new metric
line, a formatting fix, a clarified label), I make the change in one place
and both CLI modes — suite exams and single-config certification — pick it
up identically. It is no longer possible for the two modes to describe the
same run differently, because they share one renderer.

**Why this priority**: This is the drift channel with real stakes — the
human report is what the owner reads before trusting a certification
verdict, and today its two copies agree only because they were hand-diffed
once. Every other duplication is an inconvenience; this one is a
correctness hazard for the project's measurement instrument.

**Independent Test**: Make a trivial formatting change (e.g., add a
trailing marker to the per-run header) at the shared source only; run both
a suite evaluation and a single-config certification; confirm the change
appears identically in both outputs. Revert. Then confirm unmodified
builds produce byte-identical reports to pre-refactor builds.

**Acceptance Scenarios**:

1. **Given** the refactored CLI, **When** a suite run and a single-config
   run render the same underlying run record, **Then** the per-run text is
   produced by the same shared rendering path (identical bytes for
   identical inputs), with the deliberate mode differences (the
   certification mode's additional welfare-bounds detail, which the suite
   deliberately omits) expressed as explicit options of the shared path —
   never as a second copy.
2. **Given** a pre-refactor build and a post-refactor build, **When** both
   run the same suite evaluation and the same single-config certification
   (same config, seeds, subject), **Then** human output and JSON output are
   byte-identical between builds in both modes.

---

### User Story 2 - Subject resolution is single-sourced (Priority: P2)

As a maintainer changing how candidates are named or loaded (a new error
message, a changed rule about built-ins, a future subject source), I edit
one resolution path. Both CLI modes accept exactly the same subject
arguments, enforce exactly the same rules, and speak exactly the same error
messages, because there is only one implementation to consult.

**Why this priority**: The resolution ladder is duplicated verbatim inside
the binary today (including its user-facing error strings); a change that
lands in one copy but not the other splits the CLI's contract in two. High
value, but the failure mode is a visible inconsistency rather than a
silently misleading report — hence below User Story 1.

**Independent Test**: Inspect that exactly one resolution implementation
exists and both modes call it; exercise each user-facing rejection (no
subject given, both subject kinds given, unknown built-in name, unreadable
artifact) in both modes and confirm identical messages and exit behavior,
matching the pre-refactor CLI byte-for-byte.

**Acceptance Scenarios**:

1. **Given** an invalid subject argument combination, **When** it is passed
   to either CLI mode, **Then** the rejection message and exit code are
   identical between modes and unchanged from the pre-refactor CLI.
2. **Given** the suite mode's additional seat-binding behavior (registering
   the candidate under the suite's reserved seat name, including its
   collision guard), **When** subject resolution is single-sourced, **Then**
   that suite-only behavior is preserved exactly, expressed as an explicit
   option of the shared path.

---

### User Story 3 - Scoring orchestration and self-checking are single-sourced (Priority: P3)

As a maintainer changing how a subject is scored across roster modes (the
baseline computation, the per-mode run loop, the first-seed determinism
self-check), I change the library's one implementation and the CLI's
single-config mode follows automatically — because the CLI now consumes the
library's orchestration instead of carrying its own copy.

**Why this priority**: Same single-source principle, but this duplication
lives behind the scenes (identical algorithms, not identical user-facing
output), so drift here would surface through the other two stories'
guarantees. Valuable, lowest urgency.

**Independent Test**: Inspect that the CLI's single-config mode contains no
independent copy of the baseline/mode-loop/self-check algorithm; run a
single-config certification pre- and post-refactor and confirm identical
JSON, human output, exit codes — including a forced determinism failure
still exiting with the determinism exit code and unchanged message.

**Acceptance Scenarios**:

1. **Given** a single-config certification run, **When** it executes
   post-refactor, **Then** its baseline computation, per-mode runs, and
   first-seed determinism self-check are performed by the same library
   implementation the suite uses, and results are byte-identical to the
   pre-refactor CLI.
2. **Given** a determinism divergence (simulated), **When** either mode
   encounters it, **Then** the failure is reported with the same message
   shape and the same exit code as pre-refactor.

---

### Edge Cases

- The two modes differ **deliberately** in places (certification mode
  prints welfare-bounds detail the suite omits by design; suite mode binds
  the candidate seat name and applies its collision guard). The refactor
  must preserve these differences exactly — as explicit, named options of
  the shared implementations, never by keeping a second copy.
- Exit-code semantics are occurrence-based (the run aborts at the exam that
  produced the failure), not a fixed severity order; sharing orchestration
  must not reorder when failures surface.
- The fallback gate (a policy run that ever took a fallback action must
  fail rather than report the fallback's welfare) exists in both modes with
  identical wording today; it must remain identical after single-sourcing.
- JSON report writing appears in both modes with identical error wording
  for unwritable paths; the shared implementation must preserve the exact
  message.
- The `--enforce` flag is rejected without `--suite` today; argument
  validation behavior must be unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The subject-resolution contract (which subject arguments are
  accepted, how they resolve, every user-facing rejection message) MUST
  exist as exactly one implementation, consumed by both CLI modes; the
  suite mode's seat-binding and collision-guard behavior MUST be an
  explicit option of that one implementation.
- **FR-002**: Per-run human rendering MUST exist as exactly one
  implementation shared by both CLI modes; deliberate mode differences MUST
  be expressed as explicit options of that implementation, not as copies.
- **FR-003**: The first-seed determinism self-check MUST exist as exactly
  one implementation, consumed by both the suite scoring path and the
  single-config certification path.
- **FR-004**: The baseline-plus-roster-mode scoring orchestration MUST
  exist as exactly one implementation; the CLI's single-config mode MUST
  consume it rather than carry an equivalent algorithm.
- **FR-005**: The CLI's observable contract MUST NOT change: accepted flags
  and their validation, exit codes 0–4 and their occurrence-based
  precedence, JSON report shapes, human report bytes, and every
  user-facing message (including error and warning text) remain exactly as
  they are.
- **FR-006**: The refactor MUST NOT add new user-facing capability: no new
  flags, no new report content, no new configuration. Any newly shared
  internal surface is limited to what single-sourcing requires; every item
  promoted for the CLI's benefit MUST be gathered into one documented
  CLI-support module (marked as internal plumbing, not a stability
  promise), and subject resolution MUST remain local to the CLI (promoted
  into the library only if a second consumer materializes — out of scope
  here).
- **FR-007**: All existing automated tests MUST pass without modification
  to their assertions; no test may be weakened or deleted to accommodate
  the refactor.
- **FR-008**: The refactor MUST be verified by byte-comparison of complete
  outputs (human and JSON) between pre- and post-refactor builds, for at
  least one full suite evaluation and one single-config certification run
  with identical inputs, and the comparison procedure and result MUST be
  recorded in the feature's quickstart validation document. This is a
  one-time procedure; committed golden-output files are deliberately out
  of scope (deferred until the report format reaches a very stable state).
- **FR-009**: A permanent structural share-guard test MUST land with the
  refactor: it asserts both CLI modes render the same run record through
  the shared path to identical output — locking the modes-agree invariant
  without freezing report bytes against future intentional change.

### Key Entities

- **Run record**: the per-seed result of evaluating a subject (welfare
  aggregate, per-kitty means, fallback events); the unit both renderers
  currently describe independently.
- **Subject**: the policy or built-in behavior under evaluation, named on
  the command line; resolution turns CLI arguments into a registered,
  runnable subject.
- **Certification report**: the machine-readable and human-readable outputs
  of a run; the artifact whose byte-stability defines success here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each of the four concerns (subject resolution, per-run
  rendering, determinism self-check, baseline/mode orchestration), exactly
  one implementation exists in the codebase; a reviewer can point to the
  single site, and to zero remaining copies, for each.
- **SC-002**: A suite evaluation and a single-config certification executed
  with identical inputs produce byte-identical human and JSON output on
  pre-refactor and post-refactor builds (four comparisons, all identical).
- **SC-003**: The full existing automated test suite passes with zero
  assertion changes.
- **SC-004**: A formatting change made at the shared rendering source
  appears identically in both modes' output with no other edit (verified
  once during development, then reverted).
- **SC-005**: The certification binary's production line count decreases;
  no duplicated block of the four concerns remains (the duplication list in
  the 2026-07-26 survey reads as fully resolved).

## Assumptions

- The deliberate mode differences (certification-mode welfare-bounds
  detail; suite-mode seat binding and collision guard) are the only
  intentional divergences between the two paths; everything else that
  differs is drift and must not survive the refactor.
- Byte-identical output between builds is achievable because evaluation is
  deterministic by construction (seeded RNG, no wall-clock in reports);
  any timestamp-like content discovered in reports would be a spec 017
  regression to surface, not to accommodate.
- Reorganizing the evaluation library's own internal layout (e.g. splitting
  its large module into submodules) is out of scope — this feature moves
  duplicated logic to the library's existing homes, nothing more.
- The separately recorded roster-mode/subject type-safety refactor (the
  017-deferred "fold subject into the roster mode" change) is out of scope
  here; if the orchestration sharing touches the same seams, it must not
  change the serialized shapes that refactor is concerned with.
- The behavior-preservation bar (byte-identical outputs plus unchanged
  tests) stands in for broad new test development; the one required piece
  of new automated coverage is the FR-009 share-guard test. The human
  report has no non-human consumers (clarified 2026-07-26), so its bytes
  are verified for this refactor but are not promised stable beyond it.
