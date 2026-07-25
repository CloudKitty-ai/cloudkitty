# Quickstart: Held-Out Evaluation Suite (spec 017)

Runnable validation scenarios proving the feature end-to-end. Contracts:
[suite-cli.md](contracts/suite-cli.md),
[suite-manifest.md](contracts/suite-manifest.md),
[exam-configs.md](contracts/exam-configs.md); entities:
[data-model.md](data-model.md).

## Prerequisites

```bash
export PATH="$HOME/.cargo/bin:$PATH"
cargo build -p cloudkitty-rl --release   # kitty-eval binary
```

No Python, no artifact required for any scenario below (SC-007).

## 1 — Suite run with a built-in subject (US1, SC-001)

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --brain needs_driven --json /tmp/suite.json
echo "exit: $?"
```

**Expected**: exit 0. Human report shows four exam sections in manifest
order, each with the welfare panel and paired baseline deltas and **no**
"welfare bounds" verdict line; the mixed-roster section shows three cells
with differential tables (≈ 0 everywhere — `needs_driven` guests among
`needs_driven`-bound candidates), least-happy out-group counts under
threshold, duet shares, and a passing verdict. JSON carries
`suite_version: "eval-suite-v1"` and per-exam `config_sha256`.

Cross-check suite-equals-parts on one exam:

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --brain needs_driven --config evals/v1/scale.toml
```

**Expected**: numbers identical to the scale section of the suite run
(same seeds/ticks come from the exam's own `[rl.eval]`).

## 2 — The exam machinery discriminates (US3, SC-007)

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --brain playful --json /tmp/suite-playful.json
echo "exit: $?"
```

**Expected**: runs end-to-end with `playful` aliased as
`policy:candidate`. Differentials are now genuinely informative
(playful-majority cells vs needs_driven-rewritten baselines); exit is 0
or 4 depending on the verdict — either way the verdict block prints every
check with its numbers, and any exploitation signature names cell, kitty,
and differential.

## 3 — Determinism (SC-002)

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --brain needs_driven --json /tmp/a.json
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --brain needs_driven --json /tmp/b.json
diff /tmp/a.json /tmp/b.json && echo "byte-identical"
```

**Expected**: `byte-identical`.

## 4 — The freeze guard bites (US4, SC-003)

```bash
echo "# poke" >> evals/v1/scarcity.toml
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --brain needs_driven; echo "exit: $?"   # expect 1, names scarcity.toml
cargo test -p cloudkitty-rl --test eval_suite freeze      # expect FAIL, names scarcity.toml
git checkout -- evals/v1/scarcity.toml                     # restore; both pass again
```

## 5 — Loud validation, no silent skips (FR-004)

Point a scratch manifest at a config with `width = 0` (or wrong hash):

**Expected**: exit 1 before any scoring, naming the exam file and field
(or the hash mismatch); no partial report.

## 6 — Nothing existing moved (SC-004)

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --brain needs_driven --seeds 1,2 --ticks 1000        # default world
cargo test --workspace
```

**Expected**: single-config output byte-shaped as today (bounds verdict
line included — it is the bar); full workspace suite green, existing
harness tests unmodified.

## Guarding-test map (spec ↔ tests in `crates/cloudkitty-rl/tests/eval_suite.rs`)

| Spec test | Test |
|---|---|
| 1 suite-equals-parts | `a_suite_run_reproduces_each_exams_standalone_numbers` |
| 2 freeze guard | `a_landed_exam_file_cannot_change_without_failing_ci` |
| 3 loud validation | `an_invalid_exam_fails_the_suite_before_any_scoring` |
| 4 reproducibility | `two_suite_runs_produce_identical_json` |
| 5 exam lawfulness | `every_v1_exam_sustains_an_invariant_asserted_run` |
| 6 single-config compatibility | existing tests, unmodified |
| 7 mixed-roster machinery | `a_builtin_candidate_exercises_cells_differentials_and_verdict` + `a_negative_host_differential_renders_the_exploitation_signature` |
| 8 seat binding | `two_subjects_share_the_frozen_exam_without_touching_it` |
| R3 cell siblings | `cell_configs_differ_only_in_behavior` |
| R7 thresholds | `least_happy_thresholds_match_the_binomial_rule` |
| FR-007 distinctness | `no_exam_equals_a_training_or_certification_config` |
| FR-015 k derivation | `sign_test_k_matches_the_fair_coin_rule` |
| FR-015 warn/gate + tighten-only | `a_tripped_sign_test_warns_by_default_and_gates_when_enforced`, `the_sign_test_mode_only_ever_tightens` (suite.rs unit) |
| Review finding 1 regression | `an_artifact_named_candidate_does_not_panic_the_suite` |
