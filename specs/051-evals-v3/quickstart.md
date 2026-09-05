# Quickstart: validating evals/v3 (spec 051)

Worktree `~/ai/cloudkitty-evals`, branch `051-evals-v3`. Merge `origin/main` in first (main moved to 30eb469 after the branch point). Repoint `scratchpad/cycle.sh` at this worktree.

## 0. Baseline

```bash
scratchpad/cycle.sh c0          # full workspace suite; read the count (expected ≈ 894 / 0 / 6 at 050's merge)
```

## 1. The premise, reproduced (research R1) — before any file is written

```bash
cargo build -p cloudkitty-rl --bin kitty-eval
# a 40-tick / 1-seed scratch copy of evals/v2 (the scratch builder's shape, in python or by hand)
target/debug/kitty-eval --suite <scratch-v2> --artifact crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy
```

Expected: all six exams SCORE (fallbacks 0), exit 4 on the fixture's mixed-roster verdict — no refusal. `scale` lists 8 kitties while the subject saw 4. This is the record for the v3 manifest comment and the redden-list.

## 2. Red-first on the new guard

1. Write `a_served_width_mind_sits_every_exam` pointed at `evals/v2` (temporarily) → expect RED on `scale`, `mixed-roster-{guest,half,host}` at the roster-fit assertion, GREEN on `scarcity`, `heterogeneity`. Record.
2. Point it at `evals/v3` (files written, manifest hashes not yet final) → GREEN.
3. `carried_exams_parse_equal_to_v2`: bump one value in `evals/v3/scarcity.toml` → RED naming the file; restore → GREEN.
4. Freeze guard: after the hashes are written last, edit one byte of any v3 file → RED (guard + `load_suite`); restore → GREEN.
5. Sweep: add `evals/v2` to `config-sweep-exclusions.txt` BEFORE flipping `shipped_configs_rl.rs` → RED ("the frozen exams … are in the sweep"); flip to v3 → GREEN.
6. Distinctness axis: temporarily append `cloudkitty.toml` to the exam list → RED at (20, 20, 5); remove → GREEN.
7. FR-012: the 6-cat scratch exam with a 4-slot fixture subject → on the unchanged engine it SCORES (RED for the new assertion); with the check landed it REFUSES naming exam / roster 6 / slots 4 → GREEN; a built-in subject on the same scratch suite still scores.

Every step goes in `redden-list.md` with the prediction written before the run.

## 3. Full validation

```bash
scratchpad/cycle.sh final       # expect the baseline count + the new tests, 0 failures
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings
git diff main -- evals/v2       # expect EMPTY
git diff main --stat            # the files the plan names and nothing else
```

## 4. The full-horizon run (not CI; the step-7 smoke's step)

```bash
target/debug/kitty-eval --suite evals/v3 --brain needs_driven --json /tmp/v3-nd.json      # minutes
target/debug/kitty-eval --suite evals/v3 --artifact <seated mind> --json /tmp/v3-mind.json
```

Expected: six exams to a verdict; `scale` reports five kitties; two runs produce identical JSON (determinism guard).

## 5. Records

CHANGELOG Unreleased one-liner; `docs/rl-training.md` and README examples read v3; `config-sweep-exclusions.txt` carries v2 with its rationale; the redden-list closes with the final count.
