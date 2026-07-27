# Quickstart: Config Restructure (spec 020) — validation guide

How to prove the rules didn't move. Results recorded in the "Record"
blocks at implementation time. Baseline = main @ `33f69df`.

## Prerequisites

```sh
export PATH="$HOME/.cargo/bin:$PATH"
```

Foreground with generous timeouts; temp files under the job tmp dir,
not shared `/tmp`.

## 1. Suite + zero test changes (FR-007, SC-004-part)

```sh
cargo test --workspace
git diff 33f69df --stat -- 'crates/cloudkitty-core/tests' 'crates/cloudkitty-rl' \
                           'crates/cloudkitty-server' 'crates/cloudkitty-py' 'client'
```

Workspace green; the diff outside the config module is EMPTY (FR-006:
no consumer changed). For the moved tests module: confirm the split's
diff shows the `#[cfg(test)]` content relocating without modification
(compare `git show 33f69df:crates/cloudkitty-core/src/config.rs`'s test
region against `config/mod.rs`'s — a pure move).

> **Record:** totals + both confirmations.

## 2. The enumerated rejection-path sweep (FR-008, SC-003) — one-time

Throwaway harness (never landed): for each rejection rule, one minimal
TOML mutation of the default config tripping exactly that rule.

```sh
# Rule inventory: every ConfigError::invalid site + table rows
grep -c "ConfigError::invalid" crates/cloudkitty-core/src/config/validate.rs crates/cloudkitty-core/src/config/mod.rs
# Baseline worktree
git worktree add "$CLAUDE_JOB_DIR/tmp/ck-020-base" 33f69df
# Harness shape (implementation writes it in both trees, e.g. examples/sweep.rs
# or a #[ignore] test invoked explicitly): for each (rule, toml-mutation):
#   parse default TOML + mutation → validate() → print "rule\tmessage"
# Run in both trees, sort, diff:
diff "$CLAUDE_JOB_DIR/tmp/ck-020-verify/base-sweep.txt" \
     "$CLAUDE_JOB_DIR/tmp/ck-020-verify/new-sweep.txt" && echo "ALL REJECTION PATHS BYTE-IDENTICAL"
git worktree remove "$CLAUDE_JOB_DIR/tmp/ck-020-base"
```

Coverage bar: the harness's rule count matches the `ConfigError::invalid`
site count (~46 at baseline) — every rule fires exactly once; any rule
that cannot be tripped by a parseable TOML is enumerated and explained
in the Record. Multi-fault tiebreaks across the old interleave are
excluded from the diff (amended FR-004) and instead spot-asserted
against the data-model.md sequence (two or three representative pairs).

> **Record:** rule count, coverage confirmation, diff verdict, the
> multi-fault spot-assertions, and deletion of the harness.

## 3. Serde-behavior spot-set (FR-005)

```sh
# Default config parses + validates identically; unknown-field handling unchanged
# (existing unit tests cover these — name the tests that pin them here at T-time)
cargo test -p cloudkitty-core config
```

Plus: `Config::default()` debug-printed in both trees, diffed (defaults
byte-identical).

> **Record:** test names + the defaults-diff verdict.

## 4. US1 walkthrough — one table row (done once, reverted; FR-009)

Add a throwaway bounded field (struct field + `defaults::` fn + ONE table
row); confirm an out-of-bounds TOML rejects with a correctly-formatted
message and an in-bounds one accepts; revert. Nothing lands.

> **Record:** the row, both outcomes, clean-tree confirmation.

## 5. SC-001/SC-002 review sweep

Reviewer confirms: zero mechanical-guard if/return copies remain (every
such rule is a table row); no validator touches another section's
fields; the catch-all is gone; `mod.rs`/`defaults.rs`/`validate.rs` each
contain what data-model.md says and nothing else.

> **Record:** confirmation.

## 6. Optional belt-and-suspenders (not required — research D5)

The 018/019-style four-way `kitty-eval` byte comparison. Validation
cannot alter simulation behavior, so this is optional; run it if any
doubt emerges during implementation.
