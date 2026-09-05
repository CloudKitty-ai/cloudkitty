# Research: evals/v3 (spec 051)

Decisions with rationale and rejected alternatives. R1 is a measurement, not a choice.

## R1 — The wide v2 exams do not refuse a served-width mind; they truncate its view

**Measured 2026-09-05 on main (worktree base 1919891)**: the schema-5 oracle fixture (`crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy`, 408 floats) against a scratch copy of `evals/v2` with `ticks = 40`, `seeds = [1]`:

```text
kitty-eval --suite <scratch-v2> --artifact tests/fixtures/oracle.ckpolicy
-- exam scale --      8 kitties scored, fallbacks 0
-- exam scarcity --   4 kitties scored, fallbacks 0
-- exam heterogeneity -- 5 kitties scored, fallbacks 0
-- exam mixed-roster -- guest / half / host scored, fallbacks 0
mixed-roster verdict: FAIL → exit 4 (a fixture mind's ordinary verdict, not a refusal)
```

Against the real v2 (20,000 ticks × 10 seeds) the same binary was still scoring `scale` after 240 s with no error on stderr.

**Why**: `kitty-eval` resolves a `--artifact` subject once, validating it against `RlConfig::default()` — the doc comment on `resolve_subject` says so: "the suite passes defaults (per-exam RlConfigs govern scoring, not loading)". The `PolicyBehavior` then encodes every observation with its OWN `rl.observation` (4 slots). The harness reads the exam's `rl` only for `reward` (harness.rs:149) and `[rl.eval]`. `FogView::friend_rows(kitty_slots)` (world.rs:1666) does `rows.truncate(kitty_slots)` — a roster of 8 becomes the 4 lowest-id friends; ids 6–8 vanish from the observation. The loader's roster check (config.rs:403, "a roster of N kitties needs at least N−1 kitty slots") reads the exam file's own `[rl.observation] kitty_slots` (7 and 5 in v2), which is why the 049 review inferred a refusal: it never sees the subject's slots.

**Consequence for the spec**: the deliverable is unchanged (v3 at roster 5 fits 4 slots, every friend in view); the guard is reshaped (R3); the exam comment blocks describe the real failure (FR-011); FR-012 is raised as the loud check (R8). The BACKLOG entry and the 049 redden-list flag 1 are corrected by reference in the PR body, not edited in place (`experiments/` is not touched; BACKLOG's P1 entry is removed on merge per its own convention).

## R2 — What the seven v3 files are

**Decision**: `scale` = the v2 file with `[[kitty]]` ids 6–8 removed and `kitty_slots = 4`; every other key byte-identical; head comment re-cut (path, version, the roster-5 ruling, the dilution half kept, the crowd half dropped, the R1 finding replacing the "404 floats / refuses to load" note). Mixed-roster cells = the v2 files with id 6 removed, `kitty_slots = 4`, behavior columns: guest `[candidate, playful, nd, nd, nd]`, half `[candidate, playful, candidate, nd, nd]`, host `[candidate, playful, candidate, candidate, candidate]`; head comments re-cut likewise (compositions 1+4 / 2+3 / 4+1). `scarcity`, `heterogeneity` = body identical, head re-cut with a "carried from eval-suite-v2" line (Clarification Q2, option C: any stale body comment corrected and named in that line; none found at plan time — both bodies were scanned). Manifest = v2's with the version, the roster shares in the comment, and the hashes.

**Rationale**: the owner's ruling fixed the rosters; keeping ids 1–5 keeps the served names and the `playful` outsider at seat 2, so the existing "cells differ only in behavior" guard and the identity-count logic read unchanged. `kitty_slots = 4` is stated (not defaulted) because a 3.0 config states every section (spec 049 FR-030) and the number is the exam's width contract.

**Alternatives**: new positions for a 5-cat spread on 48×48 — rejected; the four corners plus centre are already the v2 positions of ids 1–5 and are the maximal-dilution placement. Dropping different ids — rejected; ids 6–8 are the "extra" cats in every v2 design.

## R3 — The standing guard: roster fit + load + short run (Clarification Q1, option A)

**Decision**: one new test in `eval_suite.rs`, `a_served_width_mind_sits_every_exam`: for every v3 exam file, load it, assert `core.kitties.len() <= ObservationConfig::default().kitty_slots + 1` (the roster-fit assertion that R1 shows is the real property); write the served-width fixture artifact (`test_support::write_fixture_artifact`, which derives its width from the compiled defaults — 408), bind it as `policy:candidate` through `PolicyBehavior::from_artifact_path` with default `RlConfig` exactly as `kitty-eval` does, and run `run_one` for 200 ticks, seed 1, `RosterMode::AllSubject` on standard exams and the cell's own roster on mixed-roster cells; assert `fallback_count == 0` and a finite team welfare.

**Red-first**: point the same function at `evals/v2` (a local const swap) — the roster-fit assertion fails on `scale` (8 > 5) and the three cells (6 > 5), passes on `scarcity` and `heterogeneity`. Recorded in the redden-list and the v3 manifest comment; the v2 pointing is not kept (Clarification Q3, option B).

**Alternatives**: full suite run in CI — rejected (minutes per cycle; Q1). `#[ignore]`d full run — rejected (Q1, option B declined). Load-only without ticks — rejected: the short run is what proves the seat is playable, and it costs under a second per exam.

## R4 — Carried exams: parsed-equality guard

**Decision**: `carried_exams_parse_equal_to_v2`: for `scarcity` and `heterogeneity`, `load_configs_from_path` on both `evals/v2/<f>` and `evals/v3/<f>` and assert the `(Config, RlConfig)` pairs are equal (both derive `PartialEq`, or compare via their serialized TOML values if not). This is the permanent form of "carried unchanged" that survives comment corrections (Q2 option C).

**Red-first**: change one value in the v3 draft (e.g. a `hard_min`) → the guard names the file.

## R5 — Thresholds: derived, identical numbers

At ten seeds and tail 0.01 the binomial rule gives guest (share 4/5) → 11, half (3/5) → 10, host (1/5) → 6 — the v2 numbers exactly (5/6 → 11, 3/6 → 10, 1/6 → 6). The manifest states the new shares in its comment; `least_happy_thresholds_match_the_binomial_rule` recomputes from the file. Sign-test k stays 10 (n = 10, tail 0.001). No red-first cycle is possible on a number that does not move; the guard's own mutation (edit `guest = 11` → `10` in a scratch manifest) is the proof it reads the file, and the existing test already has that shape.

## R6 — Retargeting the existing guards

`eval_suite.rs` reaches v2 through `evals_v2()` and `V2_EXAM_FILES` only. Rename both to v3 (one helper, one const), and every guard — freeze (`a_landed_exam_file_cannot_change_without_failing_ci`), invariant run, distinctness, two-subjects, cells-differ-only-in-behavior, thresholds, sign-test k, scratch-suite builder — reads v3. The scratch builder's `replace("ticks = 20000", ...)` and seed-list replacement must still match the v3 files (they carry the v2 `[rl.eval]` block verbatim). Names such as `every_v1_exam_sustains_an_invariant_asserted_run` are reported, not renamed (CLAUDE.md rule 3).

**Distinctness gains an axis**: no v3 exam has `(width, height, roster) == (20, 20, 5)` — the served and anchor shape. Red-first: a scratch copy of the served config dropped into the exam list trips it.

## R7 — Records and pointers

`config-sweep-exclusions.txt` += `evals/v2` with the rationale ("eval-suite-v2: the 2026-09-03 3.0 cut; its four wide exams predate the roster-width ruling (spec 051); v3 is current"). `shipped_configs_rl.rs:85` flips to `evals/v3` — this is the must-go-red guard: after the exclusion and before the flip, it fails ("the frozen exams … are in the sweep"). Usage string, README (two sites), `docs/rl-training.md` (example + the two stale sentences at ~248/252), the 017 manifest contract's evolution line, one annotation in the 049 spec, CHANGELOG Unreleased (no marker: nothing saved or trained moves).

## R8 — FR-012: refuse a subject that cannot seat the roster (OWNER CALL, recommended IN)

**Where**: `suite.rs` at the point the policy subject meets an exam (the `SuiteSubject { is_policy: true, .. }` branch in `score_suite`, before the first `run_one`): if `is_policy` and `cell/exam core.kitties.len() > ObservationConfig::default().kitty_slots + 1`, return `SuiteRunError` naming the exam, the roster and the slots. The subject's slot count is the compiled default because that is what `kitty-eval` binds against (R1); if a later spec lets a suite subject carry its own `RlConfig`, the check reads that instead.

**Why in**: it is the exact mechanical guarantee the BACKLOG entry believed existed; without it, any future wide suite silently scores a truncated view again. ~15 lines plus a unit test on a scratch suite with a 6-cat exam (SC-008). **Why it might stay out**: it is an engine touch inside a config-file arc, and the owner may prefer it as its own one-liner spec. Either way v3 lands; the plan carries it as a separate task group that is skipped if declined.

## R9 — Hand-off

Experiments (2026-09-05): no v3 world is in any training or prereg family; the step-5 recipe has no mixed-control episodes (a step-7 input they are raising with the owner). After merge, the step-7 seating smoke runs `kitty-eval --suite evals/v3 --artifact <the seated mind>`; the R1 finding is worth a line in their smoke plan (a scored result on a wide exam is not evidence the mind saw the room).
