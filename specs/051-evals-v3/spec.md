# Feature Specification: evals/v3 — the four wide exams re-cut at roster 5

**Feature Branch**: `051-evals-v3`

**Created**: 2026-09-05

**Status**: Draft

**Input**: BACKLOG P1 entry "`evals/v3`: the four wide exams re-cut at roster 5" (added 2026-09-04 from spec 049's code-review finding 1 / PR flag 5; owner ruled "option 1 is fine" 2026-09-04). Own spec, landing after the 049 and 050 merges and before the step-7 seating smoke. The invocation of `/speckit-specify` in the Product session is the go.

## Problem

Spec 049 gave every kitty a permanent by-id row in the observation, so the observation width is a function of the roster (`kitty_slots = roster − 1`). The frozen `evals/v2` suite (spec 049 FR-033, cut 2026-09-03) kept the eval-suite-v1 designs verbatim: `scale` seats 8 cats and the three `mixed-roster` cells seat 6, so those four exams declare 7 and 5 kitty slots and read 597 and 471 floats wide. A Gen 1 mind is trained at the served roster of 5 (4 slots, 408 floats).

**Plan-time correction (2026-09-05, research R1)**: the BACKLOG entry and the 049 review said the four wide exams *refuse* a served-width mind at artifact load ("dies before a tick"). Measured on main at plan time, they do not: the suite binds the subject artifact once against the compiled-default observation config (4 slots), the exam's own `[rl.observation]` governs only reward and horizon, and the encoder's friend-row builder silently truncates a wider roster to the subject's slot count. The schema-5 oracle artifact sat all six v2 exams to a verdict with zero fallbacks — blind to three of its seven friends on `scale` and one of five in every mixed-roster cell. The failure is silent truncation, not refusal, which is worse: a score is produced, and it measures a mind that cannot see part of the room. The same four files carry a comment block that still says "404 floats" (the width before the sunbeam bit landed on 2026-09-04) and describes the refusal that does not happen. None of this can be corrected in place: the v2 manifest hash-freezes every exam (spec 017 FR-012), a byte edit fails CI and suite startup, and the 049 arc proved it (redden-list §s1: a comment fix reddened three tests and was reverted byte-for-byte).

The fix the owner chose is the suite's own evolution path: a new `evals/v3` beside v2, the same six exam designs with the four wide exams re-cut so a served-width mind can sit them with every friend in view. The alternative — exam-specific minds shaped for 6 and 8 seats — was declined. The plan-time finding adds one small engine item, ruled separately (FR-012): the suite refuses a policy subject whose observation cannot seat an exam's roster, so the silent case can never recur.

## Clarifications

### Session 2026-09-05

- Q: How deep should the standing CI guard for "a served-width mind sits every v3 exam" run? → A: Option A — a load-level guard: the served-width fixture artifact is bound through the real suite load path on each of the six v3 exams, then a short run (hundreds of ticks) goes through the scorer's own entry point; the full `kitty-eval --suite evals/v3` invocation is a quickstart step, not a CI test.
- Q: Should the two carried exams (`scarcity`, `heterogeneity`) be re-headed for v3 or copied byte-for-byte from v2? → A: Option C — re-header (path, suite version, a "carried from eval-suite-v2" line) AND correct any stale note found in the bodies; hashes are new either way. Every body edit beyond the header is a comment correction listed in the spec's records and in the file's own carry line; the design values stay byte-identical.
- Q: Should "the four wide v2 exams refuse a served-width mind" stay as a standing CI assertion, or be proven once as the red-first run and recorded? → A: Option B — proven once: the new v3 guard is first pointed at v2 and seen red on exactly the four wide exams; the run is recorded in the redden-list and the v3 manifest comment; no v2 test remains in CI (v2 is hash-frozen, so the refusal cannot regress).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A served-width Gen 1 mind sits every exam (Priority: P1)

An experimenter points the evaluation binary at the new suite with a policy artifact trained on the served roster, and all six exams run to a verdict. No exam refuses the artifact at load.

**Why this priority**: the whole point — Gen 1 certification reads the suite (spec 049 §"the 3.0 wall"), and the step-7 seating smoke is the first consumer. Today 4 of 6 exams cannot be sat by the mind under test.

**Independent Test**: a fixture artifact at the served observation width (the test-support fixture writer already produces one from the compiled defaults) is bound through the real suite load path on each landed `evals/v3` exam, then a short run of hundreds of ticks goes through the scorer's own entry point; every exam produces a scored outcome, and the guard asserts that every exam's roster fits the subject's slot count (roster ≤ slots + 1), so no friend row is truncated. The same guard pointed at `evals/v2` goes red on exactly the four wide exams (roster 8 and 6 against 4 slots) — that is the guard seen red first. The full-horizon `kitty-eval --suite evals/v3` invocation is a quickstart step (the step-7 smoke performs it), not a CI test.

**Acceptance Scenarios**:

1. **Given** a policy artifact at the served width, **When** the suite run is invoked on `evals/v3`, **Then** all six exams (scale, scarcity, heterogeneity, mixed-roster guest / half / host) load the artifact and score, and the run exits with a lawful suite outcome.
2. **Given** the same artifact, **When** the new guard is pointed at `evals/v2` once, during the red-first cycle, **Then** exactly the four wide exams fail the roster-fit assertion (their rosters exceed the served slot count + 1) and the two narrow ones pass; the run is recorded in the redden-list and the v3 manifest comment, and no v2 assertion stays in CI.
3. **Given** each v3 exam file, **When** it is loaded and validated as any served config is, **Then** it validates, and an all-scripted 2,000-tick run sustains every invariant with zero fallbacks and a positive happiness floor (the existing per-exam guard, retargeted).

---

### User Story 2 - The re-cut keeps each exam's question (Priority: P1)

The four re-cut exams ask what their v1/v2 originals asked, at roster 5, and say so in the file.

**Why this priority**: an exam whose design drifted silently is worse than none; the suite's value is that each file states what it probes and why its numbers are what they are (spec 017 FR-005).

**Independent Test**: read each re-cut file against its v2 original: the same world geometry, element rules, needs, and every non-roster section are unchanged; only the roster (and the slot count it implies) moved, and the head comment names the re-cut and what half of the original axis survives.

**Acceptance Scenarios**:

1. **Given** `scale`, **When** compared with v2, **Then** the world is still 48×48 with the default world's element counts left unscaled (the dilution and travel half of the question), the roster is the five served cats at the four corners plus centre, and the head comment states that the crowd half of the v1 axis ("a roster larger than any the policy trained with") is dropped by the 2026-09-04 ruling.
2. **Given** the three mixed-roster cells, **When** compared with v2, **Then** the world is still 28×28, the five cats are the v2 seats 1–5 at their v2 positions, the `playful` outsider is still seat 2 in every cell, the cells differ only in the behavior column (the existing guard), and the compositions are guest 1 candidate + 4 scripted, half 2 + 3, host 4 + 1.
3. **Given** `scarcity` and `heterogeneity`, **When** compared with v2, **Then** every design value (every key and value, every section) is identical; the head comment names the v3 path and version and carries a "carried from eval-suite-v2" line, and any comment corrected in the body is one the carry line lists (none known today; a body edit that is not a comment fails the review).
4. **Given** every v3 exam, **When** the distinctness guard runs, **Then** no exam byte-equals the served or training config and no exam shares the served world's geometry and roster size (20×20, 5 cats) — held-out by bytes and by axis (spec 017 FR-007).

---

### User Story 3 - v3 is frozen, v2 is the record (Priority: P2)

The new suite is hash-frozen the moment it lands; v2 stays on disk untouched as the 2026-09-03 record, leaves the shipped-config sweep, and every pointer that named v2 as the current suite now names v3.

**Why this priority**: the freeze is the suite's identity (spec 017 FR-012); the pointers are how the next person finds the right door.

**Independent Test**: the freeze guard, the manifest loaders, the threshold and sign-test derivations and the sweep assertion all read v3; `evals/v2` is listed in the sweep exclusions with its rationale; the usage string and the training doc name v3; no byte of `evals/v2` moves.

**Acceptance Scenarios**:

1. **Given** the landed `evals/v3/manifest.toml`, **When** any v3 exam file is edited by one byte, **Then** the freeze guard fails and suite startup refuses the directory.
2. **Given** the v3 manifest, **When** the identity thresholds and the sign-test threshold are recomputed from the rule and the cell rosters, **Then** they match the manifest (guest share 4/5 → 11, still unattainable and said so; half 3/5 → 10; host 1/5 → 6; sign-test k = 10 at ten seeds).
3. **Given** the shipped-config sweep, **When** it runs, **Then** `evals/v3` is in scope and loads on the current engine, and `evals/v2` is excluded by the manifest of exclusions with a one-line rationale, exactly as v1 is.
4. **Given** `git diff` of `evals/v2/` against main, **When** the branch is reviewed, **Then** it is empty.
5. **Given** the evaluation binary's usage text and `docs/rl-training.md`, **When** read, **Then** the suite example names `evals/v3`, and the two stale sentences that still describe "a new evals/v2" as the future are corrected to describe v3 as current and v1/v2 as records.

---

### Edge Cases

- **A roster-4 exam under 4 slots**: `scarcity` seats four cats; the fifth row is vacant and all-zero under schema 5 (spec 049 FR-011). It already sits a served-width mind and is carried, not re-cut.
- **The guest cell's threshold is unattainable**: with four of five cats scripted, chance alone puts the out-group last most days; the derived threshold (11 of 10 seeds) cannot bind and the manifest says so, as v1 and v2 did for 5 of 6.
- **A mind at a different width**: an artifact whose width matches neither 408 nor any exam is refused at load with the existing width error; v3 makes no promise about it.
- **The wide v2 exams stay as they are**: nothing in this change touches v2. Their four-of-six roster overflow is the recorded reason for v3: proven once in the red-first cycle and written down, never fixed and never a standing test (v2 cannot change). With FR-012 landed, a suite run on v2 with a served-width policy subject refuses those four exams loudly instead of scoring a truncated view; with FR-012 declined, v2 keeps scoring silently and the record says so.
- **Held-out doctrine and the fog worlds**: the v3 exam worlds (48×48 × 5 cats; 28×28 × 5 cats; 32×32 scarcity and heterogeneity) must never enter a training or prereg family. Experiments is told the worlds exist; the mechanical guard is distinctness, the rest is doctrine.
- **The mixed-roster exam's fairness precondition**: it is fair only if the training recipe includes mixed-control episodes (spec 017 memory). Experiments answered 2026-09-05: the step-5 PPO recipe has NONE (PREREG Part C, owner ruled 2026-09-05: served composition, all five seats policy, mix 0.0), so the mixed-roster exam is untrained-for by design in the step-5 pass; Experiments is flagging it to the owner as a step-7 certification-training input. Not a gate on this spec; the exam lands as designed.
- **Manifest hashes are last**: the hashes go into the manifest over final bytes (the 017 gotcha); the manifest guards its members, not itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new suite directory `evals/v3` with a manifest (`version = "eval-suite-v3"`) and the six exam files: `scale`, `scarcity`, `heterogeneity`, `mixed-roster-guest`, `mixed-roster-half`, `mixed-roster-host`. `evals/v2` is not modified by any byte.
- **FR-002**: `scale` is re-cut at roster 5: the 48×48 world, the default world's element counts unscaled, the five served cats (ids 1–5, the v2 names) at the four corners and centre, and the slot count the roster implies. The head comment states the question kept (dilution and travel) and the half dropped (the crowd) with the ruling date.
- **FR-003**: The three mixed-roster cells are re-cut at roster 5: the 28×28 world, v2 seats 1–5 at their v2 positions, seat 2 `playful` in every cell, compositions guest 1 + 4, half 2 + 3, host 4 + 1 (candidate + scripted), the cells identical except the behavior column.
- **FR-004**: `scarcity` and `heterogeneity` are carried: every key and value identical to v2, the head comment re-cut to the v3 path and version with a "carried from eval-suite-v2" line, and any stale note found in the body corrected (comments only; each correction named in the carry line). A guard asserts the parsed configs are equal to v2's. Their hashes are new.
- **FR-005**: Every v3 exam validates as a served config does, is a complete 3.0 config (spec 049 FR-030) at the current schema, and sustains an all-scripted invariant-asserted run with zero fallbacks (spec 017 FR-006).
- **FR-006**: A policy artifact at the served observation width loads on every v3 exam, every v3 exam's roster fits the served slot count (roster ≤ slots + 1, so no friend row is truncated), and the suite scores all six. The standing CI guard is load-level: it asserts the roster fit for every exam, binds a served-width fixture artifact through the real suite load path on each v3 exam and ticks a short run (hundreds of ticks) through the scorer's entry point, never the exams' full seed-by-horizon schedule. The same guard is pointed at v2 once, in the red-first cycle, and seen red on exactly the four wide exams; that run is recorded, not kept as a test. The full suite invocation is documented in the quickstart, not run in CI.
- **FR-007**: The v3 manifest carries the identity thresholds derived from the v3 rosters by the existing binomial rule and the sign-test threshold by the fair-coin rule at the exams' seed count; the existing derivation guards recompute them from the file. The guest cell's unattainable threshold is stated as such in the manifest comment.
- **FR-008**: The freeze guard, the manifest loaders, the invariant run, the distinctness guard, the cells-differ-only-in-behavior guard, the two-subjects-share-the-exam guard and the threshold derivations all read `evals/v3`. The distinctness guard additionally asserts no v3 exam shares the served world's geometry and roster size.
- **FR-009**: `evals/v2` is listed in `config-sweep-exclusions.txt` with a one-line rationale as the 2026-09-03 3.0 cut whose four wide exams predate the roster-width ruling; the sweep assertion that the frozen exams are in scope names `evals/v3`.
- **FR-010**: Every pointer that names the current suite is moved to v3: the evaluation binary's usage text, `docs/rl-training.md` (including its two stale "a new evals/v2" sentences), the README's repo map if it names v2, and the spec 017 manifest contract's note on evolution. CHANGELOG Unreleased carries a one-liner. The 049 spec's statement that Gen 1 certification reads v2 is annotated, not rewritten.
- **FR-011**: Every v3 file documents in itself what it probes and why its numbers are chosen (spec 017 FR-005), and the four re-cut files replace the stale "404 floats / refuses to load" note with the current width, the silent-truncation finding, and the reason the roster is 5.
- **FR-012** *(OWNER CALL, raised at plan time — research R1/R8; recommended IN)*: the suite refuses a policy subject whose observation slot count cannot seat an exam's roster (roster > slots + 1), naming the exam, the roster and the slots, before any tick — the loud failure the BACKLOG entry believed already existed. Built-in (scripted) subjects are unaffected. The check sits at the one seam where the suite meets a policy subject, so mixed-roster cells and standard exams read one rule. If declined, the silent truncation stays possible for any future wide suite and the v3 guard (FR-006) is the only protection.

### Key Entities

- **Suite version**: a frozen directory of exam configs plus a manifest naming them by hash and carrying the verdict constants; evolution is a new version beside the old, never an edit.
- **Exam**: one committed, lawful, held-out world with its scoring seeds and horizon; standard exams seat the subject by roster mode, the mixed-roster exam runs three composition cells.
- **Roster width**: the observation width an exam implies through its roster under permanent by-id rows; a mind sits only exams whose width is its own.
- **Record suite**: a landed version no longer current (v1 the 2.x record, v2 the pre-ruling 3.0 record): bytes never move, excluded from the shipped-config sweep, results historical.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A served-width policy artifact loads on all six `evals/v3` exams, every v3 roster fits the served slot count, and a short scored run completes on each. The guard is seen red first, pointed at `evals/v2`, failing the roster fit on exactly the 4 wide exams and passing the 2 narrow ones; that run is recorded in the redden-list and the v3 manifest comment, and no v2 assertion remains in CI. The guard adds no more than a few seconds to the full test suite.
- **SC-002**: Every v3 exam validates and sustains a 2,000-tick all-scripted run with 0 fallbacks and a happiness floor above 0.
- **SC-003**: A one-byte edit to any v3 exam file fails the freeze guard and suite startup; `git diff main -- evals/v2` is empty on the branch.
- **SC-004**: The manifest thresholds equal the rule's recomputation from the v3 rosters (guest 11, half 10, host 6; sign-test k 10) and the derivation guards pass reading v3.
- **SC-005**: The shipped-config sweep loads `evals/v3` on the current engine and skips `evals/v2` by the exclusions manifest; the sweep's "frozen exams are in scope" assertion goes red when pointed at v2 after the exclusion and green at v3.
- **SC-006**: The two carried exams parse to configs equal to their v2 originals (asserted by a guard that loads both and compares), and their textual diff against v2 is the head comment plus any comment corrections the carry line names.
- **SC-007**: The full suite is green after the change with no test weakened; the only guards that moved are the ones this spec names, each seen red for its stated reason.
- **SC-008** *(only if FR-012 is ruled IN)*: a served-width policy subject against a scratch suite whose exam seats 6 cats is refused before any tick with a message naming the exam, roster 6 and slots 4; a built-in subject on the same scratch suite scores it; the refusal guard is seen red on the unchanged engine (the run scores instead of refusing).

## Assumptions

- The roster choices are the owner's 2026-09-04 ruling as recorded in BACKLOG: `scale` = 5 cats on the 48×48 world keeping the dilution half; mixed-roster cells 4 + 1, 3 + 2, 1 + 4 scripted + candidate. Which five cats: the v2 ids 1–5 in every re-cut file (dropping ids 6–8 in `scale`, id 6 in the cells), so the roster is the served five by name and the `playful` outsider stays seat 2.
- Carried exams are re-headed rather than byte-copied: a v3 file whose head comment says "eval-suite-v2" would misname itself. The cost is two new hashes; the parsed configs are asserted equal to v2's, and any body comment corrected is listed in the carry line (Clarifications, Q2).
- The identity thresholds come out unchanged at roster 5 (11 / 10 / 6) by the binomial rule at tail 0.01 and ten seeds; they are re-derived by the guard, not copied.
- The evaluation binary has no default suite (`--suite` is explicit); "default suite → v3" in BACKLOG means the usage text and docs.
- No observation, artifact or wire change: schema 5 stays 408 floats. The suite loader, scorer and verdict code are untouched except for FR-012 if the owner rules it in (one roster-fit check at the subject seam). If the loader needs any other change to run v3, that is a finding to report, not a change to make.
- The plan-time measurement (research R1): the schema-5 oracle fixture artifact against a 40-tick, one-seed scratch copy of v2 scored all six exams with zero fallbacks and exit 4 (the mixed-roster verdict, a fixture mind's ordinary failure), never a load refusal. The BACKLOG entry's "dies before a tick" was the 049 review's inference from the loader's roster check, which only ever reads the exam's own `[rl.observation]`, not the subject's.
- The stronger-counterfactual-baseline design (BACKLOG "Eval-suite v2: a stronger counterfactual baseline", 2026-07-25) stays banked; v3 keeps the `needs_driven` counterfactual.
- Experiments is informed at spec time (suite number, the four roster-5 worlds, the held-out reminder, the mixed-control-episodes question about the step-5 recipe); nothing here waits on their reply. `experiments/` files are not touched.
- Test names that still say "v1" (`every_v1_exam_sustains_an_invariant_asserted_run`) are reported, not renamed (CLAUDE.md rule 3).
