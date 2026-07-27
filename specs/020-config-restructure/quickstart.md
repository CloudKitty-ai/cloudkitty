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

> **Record (2026-07-26):** workspace green at every checkpoint (T004,
> T007, T009, final). Diff outside the config module vs `33f69df`: empty.
> Tests module: byte-identical pure move (diffed against
> `git show 33f69df:…/config.rs`'s test region).

## 2. The enumerated rejection-path sweep (FR-008, SC-003) — one-time

Throwaway harness (never landed): for each rejection rule, one minimal
TOML mutation of the default config tripping exactly that rule.

```sh
# Rule inventory: every ConfigError::invalid site (+ table rows)
# — grep config.rs before the split; the config/ files after:
grep -c "ConfigError::invalid" crates/cloudkitty-core/src/config.rs 2>/dev/null \
  || grep -c "ConfigError::invalid" crates/cloudkitty-core/src/config/validate.rs crates/cloudkitty-core/src/config/mod.rs
# Baseline worktree
git worktree add "$CLAUDE_JOB_DIR/tmp/ck-020-base" 33f69df
# Harness: crates/cloudkitty-core/examples/config_sweep.rs (working-tree only,
# copied into the worktree, deleted before landing). Base config pinned at
# T001 (committed cloudkitty.toml, or empty TOML iff it parses with full
# defaults — record which); mutations are structural toml::Value path-sets,
# never text append. For each (rule, mutation): parse → validate() → print
# "rule\tmessage", sorted.
OUT="$CLAUDE_JOB_DIR/tmp/ck-020-verify" && mkdir -p "$OUT"
(cd "$CLAUDE_JOB_DIR/tmp/ck-020-base" && cargo run -p cloudkitty-core --example config_sweep) > "$OUT/base-sweep.txt"
cargo run -p cloudkitty-core --example config_sweep > "$OUT/new-sweep.txt"
diff "$OUT/base-sweep.txt" "$OUT/new-sweep.txt" && echo "ALL REJECTION PATHS BYTE-IDENTICAL"
git worktree remove "$CLAUDE_JOB_DIR/tmp/ck-020-base"
```

Coverage bar: the harness's rule count matches the `ConfigError::invalid`
site count (~46 at baseline) — every rule fires exactly once; any rule
that cannot be tripped by a parseable TOML is enumerated and explained
in the Record. Multi-fault tiebreaks across the old interleave are
excluded from the diff (amended FR-004) and instead spot-asserted
against the data-model.md sequence (two or three representative pairs).

> **Record (2026-07-26):** base pinned = the committed `cloudkitty.toml`
> (tracked, identical both trees). 46 rejection rules exercised —
> matching the 46 `ConfigError::invalid` sites, with 3 documented as
> untrippable-by-design in the harness header (both capacity rules are
> pigeonhole/arithmetic-shadowed defense in depth; `validate_behavior_names`
> is registry-time). Sweep run at T002 (self-consistency: identical
> pre-change), T004, T007, and T009 — byte-identical every time. Three
> multi-fault spot-assertions: the interleave-spanning pair
> (`purr.min_ticks=0` + `sunbeam_reach=0`) reports `[behavior]` first per
> the amended FR-004; the two non-spanning pairs report unchanged order.
> Harness deleted before landing; worktree removed.

## 3. Serde-behavior spot-set (FR-005)

```sh
# Default config parses + validates identically; unknown-field handling unchanged
# (existing unit tests cover these — name the tests that pin them here at T-time)
cargo test -p cloudkitty-core config
```

Plus: `Config::default()` debug-printed in both trees, diffed (defaults
byte-identical).

> **Record (2026-07-26):** the config test module (43 tests) passes
> unmodified — it pins invalid-config rejections, default fallbacks
> (`zero_sunbeam_reach_is_rejected_and_the_default_stands_in` and kin),
> and TOML round-trips. `Config::default()` debug-printed in both trees:
> byte-identical.

## 4. US1 walkthrough — one table row (done once, reverted; FR-009)

Add a throwaway bounded field (struct field + a `default_*` fn in its
then-current home — plain `config.rs` when run at US1, `defaults.rs`
after the split — + ONE table row); confirm an out-of-bounds TOML
rejects with a correctly-formatted message and an in-bounds one accepts;
revert. Nothing lands.

> **Record (2026-07-26):** throwaway `[behavior] walkthrough_ticks`
> (field + default fn + one table row): out-of-bounds TOML rejected with
> `config error: [behavior] walkthrough_ticks is 0; must be at least 1
> tick (walkthrough)` — cluster-consistent format from the shared row
> shape; in-bounds accepted. Reverted; clean tree confirmed.

## 5. SC-001/SC-002 review sweep

Reviewer confirms: zero mechanical-guard if/return copies remain (every
such rule is a table row); no validator touches another section's
fields; the catch-all is gone; `mod.rs`/`defaults.rs`/`validate.rs` each
contain what data-model.md says and nothing else.

> **Record (2026-07-26):** confirmed — zero repeated guard copies (the
> two remaining single-field `== 0` ifs are one-per-section, not
> duplicates); no validator touches another section's fields; the
> catch-all no longer exists; the three files match data-model.md.

## 6. Optional belt-and-suspenders (not required — research D5)

The 018/019-style four-way `kitty-eval` byte comparison. Validation
cannot alter simulation behavior, so this is optional; run it if any
doubt emerges during implementation.
