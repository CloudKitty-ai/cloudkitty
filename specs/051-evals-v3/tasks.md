# Tasks: evals/v3 — the four wide exams re-cut at roster 5 (spec 051)

**Input**: Design documents from `/specs/051-evals-v3/` — plan.md, spec.md (§Clarifications 2026-09-05; §Problem plan-time correction; FR-012 ruled in), research.md (R1–R9), data-model.md, contracts/evals-v3.md, quickstart.md.

**Tests**: REQUIRED — every success criterion is a guard seen red first (CLAUDE.md rules 5/6). Every mutate/revert cycle is recorded in `redden-list.md` with the prediction written BEFORE the run and the count re-read after. Commit before every destructive check.

**Organization**: by user story. US1 (P1) is the MVP: the seven v3 files exist, a served-width mind sits every exam with every friend in view, and the suite refuses a subject that cannot (FR-012). US2 (P1) proves the designs are the v2 designs. US3 (P2) freezes v3, records v2, and moves every pointer.

**House rules in force**: worktree `~/ai/cloudkitty-evals`, branch `051-evals-v3`; NEVER edit `evals/v2/*` or `evals/v1/*`; never edit `experiments/*`; nothing deploys, no tag; long jobs foreground via `scratchpad/cycle.sh LABEL`; manifest hashes written LAST over final bytes; `sign_test*` keys above `[verdict.least_happy_threshold]`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3

---

## Phase 1: Setup

- [ ] T001 Repoint `scratchpad/cycle.sh`'s `cd` line to `~/ai/cloudkitty-evals`; in the worktree run `git fetch origin && git merge --no-edit origin/main` (main moved to 30eb469+ after the branch point; merge IN, never rebase); commit the merge if any.
- [ ] T002 Create `specs/051-evals-v3/redden-list.md` in the 050 format (standard paragraph; baseline count from `scratchpad/cycle.sh c0` on the merged, otherwise untouched branch — expected ≈ 894 / 0 / 6 ignored, RE-READ; fmt + clippy clean); commit.
- [ ] T003 Record research R1 as redden-list §R1 (the premise, reproduced): build `kitty-eval`, build a 40-tick / 1-seed scratch copy of `evals/v2` under the scratchpad (the `build_scratch_suite` shape: replace `ticks = 20000` and the seed list, recompute each sha256 into a copied manifest with `sign_test_k = 2`), run `target/debug/kitty-eval --suite <scratch> --artifact crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy`; predict: all six exams SCORE with fallbacks 0, `scale` lists 8 kitties, exit 4 (fixture verdict), no refusal; paste the exam headers and exit code into the redden-list; commit.

---

## Phase 2: Foundational — the seven v3 files exist and the test file reads them

- [ ] T004 [P] Create `evals/v3/scale.toml` from `evals/v2/scale.toml`: delete the three `[[kitty]]` tables with ids 6, 7, 8 (Mochi, Marmalade, Noodle); set `[rl.observation] kitty_slots = 4`; every other key and value byte-identical; rewrite the head comment: path `evals/v3/scale.toml`, "FROZEN at landing: eval-suite-v3", "Re-cut from eval-suite-v2 at roster 5 (spec 051, owner ruling 2026-09-04)", the question kept (2.25× the default area, default element counts unscaled — dilution and travel) and the half dropped (the v1 crowd axis, "a roster larger than any the policy trained with"); replace the `# Spec 049 FR-011 ... (404 floats) ... refuses to load` block above `[rl.observation]` with the R1 truth: permanent by-id rows make width = f(roster); the suite binds a policy subject at the compiled default 4 slots (408 floats) and the encoder truncates a wider roster silently, so roster 5 here is what keeps every friend in view; spec 051 FR-012 refuses a subject that cannot seat the roster.
- [ ] T005 [P] Create `evals/v3/mixed-roster-guest.toml`, `evals/v3/mixed-roster-half.toml`, `evals/v3/mixed-roster-host.toml` from their v2 files: delete the `[[kitty]]` table with id 6 (Mochi) in each; set `kitty_slots = 4`; behavior columns — guest: 1 `policy:candidate`, 2 `playful`, 3/4/5 `needs_driven` (1 + 4); half: 1 `policy:candidate`, 2 `playful`, 3 `policy:candidate`, 4 `needs_driven`, 5 `needs_driven` (2 + 3 per FR-003 — NOTE id 5 flips from v2's candidate to `needs_driven`, otherwise the cell would be 3 + 2); host: 1/3/4/5 `policy:candidate`, 2 `playful` (4 + 1); every other value byte-identical across the three and to v2; head comments re-cut (path, version, "Re-cut from eval-suite-v2 at roster 5 (spec 051)", the composition line "one candidate seat among four scripted cats" / "two among three" / "four with one scripted"), the `Identical to mixed-roster-{...}.toml except the behavior column` sentence kept; the FR-011 block replaced as in T004 ("5 cats here").
- [ ] T006 [P] Create `evals/v3/scarcity.toml` and `evals/v3/heterogeneity.toml` from their v2 files: body byte-identical; head comment lines 1–6 re-cut to the v3 path, "FROZEN at landing: eval-suite-v3", and "Carried from eval-suite-v2 unchanged (spec 051): every key and value identical; header only. Body comment corrections: none." — if any stale body comment IS found while carrying, correct it and name it on that line (Clarification Q2, option C).
- [ ] T007 Create `evals/v3/manifest.toml` from `evals/v2/manifest.toml`: `version = "eval-suite-v3"`; head comment "eval-suite-v3, cut 2026-09-05 (spec 051)" + the R1 paragraph (v2's four wide exams seated 8 and 6 cats; a served-width mind scored them with friends silently dropped from its observation — measured on the oracle fixture 2026-09-05; v3 re-cuts them at roster 5 so every friend is in view; v2 is the record) + "Evolution = a new evals/v4/ alongside"; identity-threshold comment updated to the v3 shares (guest 4/5 → 11, still unattainable and said so; half 3/5 → 10; host 1/5 → 6; n_seeds = 10); thresholds and `sign_test*` values unchanged (11 / 10 / 6; warn / 0.001 / 10); every `sha256 = "..."` set to a placeholder `"0000…"` (64 zeros) — the real hashes land in T023, LAST.
- [ ] T008 In `crates/cloudkitty-rl/tests/eval_suite.rs` rename `evals_v2()` → `evals_v3()` (path `evals/v3`), `V2_EXAM_FILES` → `V3_EXAM_FILES`, and update every reference (the scratch builder's doc comment says "the real v3 suite (spec 051 …)"); leave every test's name and body otherwise untouched.
- [ ] T009 Run `cargo test -p cloudkitty-rl --test eval_suite`; predict: the freeze guard and both manifest loaders RED (placeholder hashes ≠ bytes; `load_suite` refuses the directory — every test that loads the real suite fails with it), everything reading files directly GREEN; record as cycle F0 in `redden-list.md` (this is the freeze guard seen red on a wrong manifest, for free); commit the drafts.

**Checkpoint**: seven files on disk, the test file points at them, the suite refuses to load until the hashes are real.

---

## Phase 3: User Story 1 — A served-width Gen 1 mind sits every exam (P1) 🎯 MVP

**Goal**: every v3 roster fits the served slot count; a served-width fixture artifact loads and completes a short scored run on all six exams; the suite refuses a policy subject that cannot seat an exam's roster (FR-012).

**Independent test**: the new guard red on v2 (4 of 6) and green on v3; the FR-012 unit test red on the unchanged engine and green with the check.

- [ ] T010 [US1] Add test `a_served_width_mind_sits_every_exam` to `crates/cloudkitty-rl/tests/eval_suite.rs`: `let slots = RlConfig::default().observation.kitty_slots;` for each file in a local `const FILES` (start it as the v2 list: `repo_root().join("evals/v2")` — the red-first pointing), `load_configs_from_path`, `assert!(core.kitties.len() <= slots + 1, "{file}: roster {} needs {} slots, the served subject has {slots}", ...)`; then write the fixture artifact via `cloudkitty_rl::test_support::write_fixture_artifact(&dir.join("candidate"), 8, 7)` into a scratch dir, `PolicyBehavior::from_artifact_path(path, &RlConfig::default(), false)` (the `kitty-eval` binding exactly), register it under `suite::CANDIDATE_BEHAVIOR` AND under a plain name in a `BehaviorRegistry::with_builtins()`, then `run_one(&EvalRequest { core, rl, registry, subject: Some(plain_name), roster: RosterMode::AllSubject, seed: 1, ticks: 200 })` for standard exams and `subject: None, roster: RosterMode::FromConfig` for the three cells (the candidate seats resolve through the registry); assert `fallback_count == 0` and `aggregates.team_welfare.is_finite()` — the fields as named in `harness::RunOutcome`.
- [ ] T011 [US1] Run `cargo test -p cloudkitty-rl --test eval_suite a_served_width_mind_sits_every_exam` with `FILES` pointed at `evals/v2`; predict RED at the roster-fit assertion on `scale.toml` (8 > 5) — the loop panics at the first wide file; then temporarily reorder the list to confirm each of the four wide files trips it and `scarcity` / `heterogeneity` pass (or assert per-file in a collected Vec so one run names all four); record as cycle U1 in `redden-list.md` AND paste the four names into the v3 manifest head comment (T007's R1 paragraph gains "guard seen red on exactly those four, 2026-09-05"); point `FILES` at `evals/v3` / `V3_EXAM_FILES`; predict GREEN (the manifest is not read by this test); commit.
- [ ] T012 [US1] Add test `a_policy_subject_that_cannot_seat_the_roster_is_refused` to `crates/cloudkitty-rl/tests/eval_suite.rs` (SC-008): build a scratch suite from v3 via `build_scratch_suite` but with `scale.toml`'s text given a sixth `[[kitty]]` (id 6, "Mochi", x 24, y 6, `needs_driven`) and `kitty_slots = 5` (rehash that file); bind the T010 fixture artifact as a policy subject (`SuiteSubject { is_policy: true, .. }`); `score_suite(&suite, &subject, false)` → `assert!(matches!(err, SuiteRunError::RosterOverflow { roster: 6, slots: 4, .. }))` and the message names "scale"; then the same scratch suite with `registry_with_candidate("needs_driven")`, `is_policy: false` → `Ok(_)` (a built-in scores it). The variant does not exist yet: the test is written against the name T013 introduces and committed red (it will not compile until T013 adds the variant — record the compile failure as cycle U2's first half, then the RED run on the variant-only engine as its second half; see T014).
- [ ] T013 [US1] Add `SuiteRunError::RosterOverflow { exam: String, roster: usize, slots: usize }` in `crates/cloudkitty-rl/src/suite.rs` with a Display line "exam '{exam}': a roster of {roster} kitties needs {roster-1} kitty slots; the policy subject observes {slots} (spec 051 FR-012) — a wider roster would be truncated silently from its view". Land the VARIANT FIRST (no check yet) so T012 compiles and runs red; then in `score_suite`, BEFORE the scoring loop and only when `subject.is_policy`, walk every `LoadedExam::Standard` core and every `LoadedExam::MixedRoster` cell core and return the error on the first `core.kitties.len() > RlConfig::default().observation.kitty_slots + 1` (doc comment: the subject is bound at the compiled default by `kitty-eval`'s `resolve_subject`; if a suite subject ever carries its own `RlConfig`, read that). In `crates/cloudkitty-rl/src/bin/kitty-eval.rs` there is NO match to extend: `determinism_exit` (L386) destructures the single variant with an irrefutable `let` and is called from both modes (L437, L521). Rename it `suite_error_exit` and make it a `match`: `Determinism` keeps its exact message and exit 3; `RosterOverflow` prints `kitty-eval: {err}` and returns exit 1 (a load failure). Update its doc comment ("exit-3 arm" → "the suite-error arms").
- [ ] T014 [US1] Cycle U2: (a) with T012 committed and only the variant from T013 landed, run `cargo test -p cloudkitty-rl --test eval_suite a_policy_subject_that_cannot_seat_the_roster_is_refused`; predict RED — `score_suite` returns `Ok` (the run scores the truncated view); record. (b) Land the check and the kitty-eval arm; predict GREEN on T012, and `an_artifact_named_candidate_does_not_panic_the_suite` still GREEN (its scratch suite is v3, rosters ≤ 5); run `cargo test -p cloudkitty-rl`; record. (c) Binary-level close of R1 (spec Edge Case "the wide v2 exams … refuse loudly"): rebuild `kitty-eval`; re-run T003's scratch v2 with the oracle → predict exit 1, stderr naming `scale`, roster 8, slots 4, no exam scored; then a 40-tick / 1-seed scratch copy of v3 (same builder shape; the scratch manifest recomputes its own hashes, so T023 need not have landed) with the oracle → predict all six exams score, `scale` lists 5 kitties, fallbacks 0, exit 0 or 4. Paste both headers into the redden-list under §R1 as its closing entry; commit.
- [ ] T015 [US1] Run `cargo test -p cloudkitty-rl --test eval_suite every_v1_exam_sustains_an_invariant_asserted_run` — the retargeted invariant run on all six v3 files (FR-005 / SC-002); predict GREEN, 0 fallbacks, floor > 0 (this test reads files directly, not the manifest); report — do not rename — the "v1" in the test's name (rule 3); record; commit.

**Checkpoint**: US1 complete — a served-width mind sits all six v3 exams; the suite refuses a subject that would be blinded.

---

## Phase 4: User Story 2 — The re-cut keeps each exam's question (P1)

**Goal**: the re-cut files are the v2 designs at roster 5 and the carried files are the v2 designs verbatim; every exam is held out by bytes and by axis.

**Independent test**: the carried-equality guard red on one changed value; the distinctness axis red on the served config; the cells guard green on the three v3 cells.

- [ ] T016 [US2] Add test `carried_exams_parse_equal_to_v2` to `crates/cloudkitty-rl/tests/eval_suite.rs`: for `["scarcity.toml", "heterogeneity.toml"]` load `evals/v2/<f>` and `evals/v3/<f>` with `load_configs_from_path` and `assert_eq!((core2, rl2), (core3, rl3), "{f}: carried unchanged (spec 051 FR-004)")` (`Config` and `RlConfig` derive `PartialEq`); red-first: temporarily change `hard_min` of one element in `evals/v3/scarcity.toml`, predict RED naming `scarcity.toml`, restore byte-for-byte (keep a copy), predict GREEN; record as cycle U3; commit.
- [ ] T017 [US2] Extend `no_exam_equals_a_training_or_certification_config` in `crates/cloudkitty-rl/tests/eval_suite.rs` with the axis assertion: for every v3 exam, `assert!((core.width, core.height, core.kitties.len()) != (20, 20, 5), "{file}: the served / anchor shape is not held out")`; red-first: temporarily push `repo_root().join("cloudkitty.toml")` into the iterated list, predict RED at the axis line (byte-distinctness still passes since the file differs from itself only if compared — compare against the exam list, not `others`), restore, predict GREEN; record as cycle U4; commit.
- [ ] T018 [US2] Run `cargo test -p cloudkitty-rl --test eval_suite cell_configs_differ_only_in_behavior` on the three v3 cells; predict GREEN (T005 kept every non-behavior value identical); if RED, the diff names the drifted key — fix the cell file, never the test; record; commit.
- [ ] T019 [US2] Re-read the four re-cut files' head comments against spec FR-002/FR-003/FR-011 (what the exam probes, why roster 5, the R1 truth, the dropped half for `scale`, the composition for each cell) and the two carried files' carry line (T006); fix wording only; commit.

**Checkpoint**: US2 complete — six designs, held out, documented.

---

## Phase 5: User Story 3 — v3 is frozen, v2 is the record (P2)

**Goal**: real hashes freeze v3; v2 leaves the sweep with its rationale; every pointer names v3.

**Independent test**: one byte edited in a v3 file fails the freeze guard; the sweep assertion red between the exclusion and the flip; `git diff main -- evals/v2` empty.

- [ ] T020 [US3] Add `evals/v2` to `config-sweep-exclusions.txt` under the 3.0-wall block: `evals/v2                                         eval-suite-v2: the 2026-09-03 3.0 cut; its four wide exams seat 8/6 cats and predate the roster-width ruling (spec 051); v3 is current` (format: path, then rationale, matching the `evals/v1` line).
- [ ] T021 [US3] Run `cargo test -p cloudkitty-rl --test shipped_configs_rl` BEFORE touching the assertion; predict RED at "the frozen exams (evals/v2, the 3.0 cut) are in the sweep" (v2 now excluded, v3 not yet asserted); record as cycle U5 (the must-go-red guard of the changed behavior, rule 6); then in `crates/cloudkitty-rl/tests/shipped_configs_rl.rs` change the `ends_with("evals/v2")` to `ends_with("evals/v3")` and the message to "the frozen exams (evals/v3, spec 051) are in the sweep", and the module doc's `evals/v2` mention to v3; predict GREEN; commit.
- [ ] T022 [US3] Update pointers: `crates/cloudkitty-rl/src/bin/kitty-eval.rs` usage string `--suite evals/v2` → `evals/v3`; `README.md` repo-map line (`evals/v3/ the exam room … ; evals/v1/ and evals/v2/ are records, excluded from the sweeps`), the "Three worlds" paragraph (`evals/v3/`), the example command, and the "evolving it means a new `evals/v2/` alongside" → `evals/v4/`; `docs/rl-training.md` example → `evals/v3`, the sentence "evolution is a new `evals/v2/` alongside" → `evals/v4/`, and the trailing paragraph "Read suite scores as archaeology until an `evals/v2` recalibrates …" rewritten to: v1 and v2 are records (v2's wide exams seated more cats than a served-width mind can see — spec 051), `evals/v3` is current; `specs/017-eval-suite/contracts/suite-manifest.md` line 13's "Evolution = a new evals/v2/ alongside" → note "(v3 current since spec 051; each version's manifest names the next)"; one annotation in `specs/049-fog-gen1/spec.md` §"the 3.0 wall" after "Gen 1 certification reads `evals/v2`": "*(superseded: `evals/v3`, spec 051 — v2's wide exams seat more cats than a served-width mind observes)*".
- [ ] T023 [US3] Write the REAL hashes into `evals/v3/manifest.toml` LAST: `for f in evals/v3/*.toml (not manifest); shasum -a 256` → replace each placeholder; run `cargo test -p cloudkitty-rl --test eval_suite`; predict GREEN across the file (F0's reds close: freeze guard, both loaders, thresholds, sign-test k, two-subjects, scratch-suite tests); record as cycle U6; commit "hashes last".
- [ ] T024 [US3] Freeze proof (SC-003): append one space to a comment line in `evals/v3/heterogeneity.toml` (commit first); run the freeze guard + `two_subjects_share_the_frozen_exam_without_touching_it`; predict RED at `a_landed_exam_file_cannot_change_without_failing_ci` naming the file and `load_suite` refusing; `git checkout -- evals/v3/heterogeneity.toml`; predict GREEN; record as cycle U7.
- [ ] T025 [US3] `CHANGELOG.md` Unreleased: one entry "The exam room re-cut for the served roster — `evals/v3` (spec 051)": v2's four wide exams seated 8 and 6 cats; a served-width mind scored them with friends silently dropped from its view (measured 2026-09-05); v3 re-cuts them at roster 5, carries scarcity/heterogeneity, derives the same thresholds; the suite now refuses a policy subject that cannot seat an exam's roster (FR-012); v2 joins the sweep exclusions as a record. No compatibility marker.

**Checkpoint**: US3 complete — v3 frozen, v2 recorded, pointers moved.

---

## Phase 6: Polish & cross-cutting

- [ ] T026 `git diff main -- evals/v2 evals/v1` → expect EMPTY (SC-003); `git diff main --stat` → only the files plan.md names; `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; record.
- [ ] T027 `scratchpad/cycle.sh final`; predict: baseline count + 3 new tests (T010, T012, T016), 0 failures, 6 ignored; READ the count; close `redden-list.md` with the final table (cycles F0, U1–U7, final) and the R1 record; commit.
- [ ] T028 Remove the `evals/v3` P1 entry from `BACKLOG.md` (the section's own convention: shipped P1 items are removed once merged — do it in the PR so the merge is the removal) and add a one-line pointer under the closed-items comment if the file keeps one; commit.
- [ ] T029 Draft the PR body in the scratchpad (`pr-body-051.md`): the R1 finding first (with the oracle run and the "dies before a tick" correction to the BACKLOG entry and 049 review flag 1), the seven files, FR-012, the must-go-red guards each with its cycle, `evals/v2` untouched, the full-suite count, the step-7 hand-off line for Experiments (a scored result on a wide exam is not evidence the mind saw the room); end with the Claude Code footer and the session URL. Open the PR only on the owner's go.

---

## Dependencies

- Phase 1 → Phase 2 → US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → Polish. US2's guards need the v3 files (Phase 2); US3's hashes (T023) must be the last edit to any exam file, so T019's wording fixes precede T023; T024 follows T023.
- FR-012 (T012–T014; the test is T012, the check T013) is independent of the exam files and may run before T010 if convenient, but T012's scratch suite reads v3 (Phase 2 done).

## Parallel opportunities

- T004, T005, T006 (different files) in one pass; T007 after them (it reads nothing yet).
- T016 and T017 touch the same test file — sequential. T020 (exclusions) and T022 (pointers) are different files and may be edited together, but T021's red run MUST happen between T020 and the `shipped_configs_rl.rs` flip.

## Implementation strategy

MVP = Phase 1 + 2 + US1: the files exist, a served-width mind sits every exam, the suite refuses one that cannot. US2 adds the design-fidelity guards; US3 freezes and records. Nothing is a PR until Phase 6 closes and the owner says go.
