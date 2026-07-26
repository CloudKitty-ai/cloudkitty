# Quickstart: Kitty-Eval Dedup (spec 018) — validation guide

How to prove the refactor moved nothing. Results are recorded in the
"Record" blocks at implementation time (FR-008).

## Prerequisites

```sh
export PATH="$HOME/.cargo/bin:$PATH"
```

Run long steps in the foreground with a generous timeout (standing
environment note: background jobs on this machine are sometimes killed).

## 1. The byte-comparison (FR-008, SC-002) — one-time procedure

Baseline build comes from tag `v2.3` via a throwaway worktree; identical
inputs for both builds. Golden files are deliberately NOT committed
(owner ruling 2026-07-26).

```sh
# Baseline binary (pre-refactor)
git worktree add /tmp/ck-v23 v2.3
cargo build --release --manifest-path /tmp/ck-v23/Cargo.toml -p cloudkitty-rl --bin kitty-eval

# Feature binary (post-refactor)
cargo build --release -p cloudkitty-rl --bin kitty-eval

OUT=/tmp/ck-018-verify && mkdir -p $OUT
BASE=/tmp/ck-v23/target/release/kitty-eval
NEW=target/release/kitty-eval

# Comparison 1+2: suite mode, human + JSON (~1 min per build)
$BASE --suite evals/v1 --brain needs_driven --json $OUT/base-suite.json > $OUT/base-suite.txt
$NEW  --suite evals/v1 --brain needs_driven --json $OUT/new-suite.json  > $OUT/new-suite.txt

# Comparison 3+4: single-config certification mode, human + JSON
# (reduced scale — identical inputs is what byte-equality needs; the run
# must still produce every report section: per-run panels incl. the
# bounds block, paired block, aggregates)
$BASE --brain needs_driven --seeds 1,2,3 --ticks 2000 --json $OUT/base-cert.json > $OUT/base-cert.txt
$NEW  --brain needs_driven --seeds 1,2,3 --ticks 2000 --json $OUT/new-cert.json  > $OUT/new-cert.txt

diff $OUT/base-suite.txt $OUT/new-suite.txt && cmp $OUT/base-suite.json $OUT/new-suite.json \
  && diff $OUT/base-cert.txt $OUT/new-cert.txt && cmp $OUT/base-cert.json $OUT/new-cert.json \
  && echo "ALL FOUR BYTE-IDENTICAL"

git worktree remove /tmp/ck-v23
```

Also confirm exit codes match per invocation (`echo $?` after each run;
expected 0 for all of the above).

> **Record (2026-07-26):** baseline = tag `v2.3` worktree (temp dirs
> under the session job dir rather than shared `/tmp`; commands otherwise
> as above). Baseline exits 0/0; feature exits 0/0. All four comparisons
> **byte-identical** — verified three times (after US1, after US2, and
> final after US3).

## 2. Error-path spot checks (US2)

Each rejection must produce the identical message and exit code in both
modes and both builds:

```sh
$NEW --suite evals/v1                                  # no subject
$NEW --suite evals/v1 --brain needs_driven --artifact x.ckpolicy   # both kinds
$NEW --brain no_such_brain                             # unknown built-in
$NEW --artifact /nonexistent.ckpolicy                  # unreadable artifact
$NEW --enforce sign-test                               # --enforce without --suite
```

Compare stderr/stdout text against the baseline binary for each.

> **Record (2026-07-26):** seven rejection paths compared (the five
> above plus `--brain X --artifact Y` and the no-arguments case): all
> MATCH on message bytes and exit code (all exit 1).

## 3. The share-guard test (FR-009) — permanent

```sh
cargo test -p cloudkitty-rl --test eval_suite share_guard
```

Asserts both modes render the same `RunOutcome` through
`cli_support` to identical bytes for the shared portion, with exactly the
documented bounds-block divergence. This test stays in the tree.

## 4. Full suite, unchanged assertions (FR-007, SC-003)

```sh
cargo test --workspace
git diff v2.3 -- 'crates/**/tests' ':!crates/cloudkitty-rl/tests/eval_suite.rs'
```

The diff over pre-existing test files must show no assertion changes;
`eval_suite.rs` may only gain the share-guard test.

## 5. SC-004 walkthrough — one edit site (done once, then reverted)

Add a trailing marker to the shared panel header in `cli_support`; run
one suite exam and one certification run; confirm the marker appears in
both outputs; revert the edit. Do not land the marker.

> **Record (2026-07-26):** ` ###` marker added to the shared panel header
> only; appeared identically in certification-mode and suite-mode output;
> reverted via `git checkout` — clean tree confirmed, marker never
> committed. Also exercised (T014): a forced self-check failure exits 3
> in both modes with the pre-refactor message shapes
> (`(AllSubject)` / `(exam scale (AllSubject))`).

## 6. SC-001/SC-005 review sweep

Reviewer confirms against the survey's duplication list (BACKLOG
2026-07-26 entry / research.md line references): the two subject ladders,
two JSON-write blocks, two fallback-gate blocks, the binary-side panel
renderer, inline self-check, and orchestration copy are all gone; binary
production line count decreased.
