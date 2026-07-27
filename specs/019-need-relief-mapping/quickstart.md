# Quickstart: Need→Relief Mapping (spec 019) — validation guide

How to prove the baseline cat did not change. Results are recorded in
the "Record" blocks at implementation time.

## Prerequisites

```sh
export PATH="$HOME/.cargo/bin:$PATH"
```

Run long steps in the foreground with a generous timeout (standing
environment note). Baseline = main at `c6fbeae` (pre-refactor).

## 1. Bit-identical decisions (FR-004/FR-005, SC-002/SC-004)

The whole existing suite is the instrument — determinism tests, long-run
welfare gates, behavior property tests:

```sh
cargo test --workspace
# Integration-test dirs: must produce NO output (zero test changes)
git diff c6fbeae -- 'crates/cloudkitty-core/tests' 'crates/cloudkitty-rl/tests' \
                    'crates/cloudkitty-server/tests' 'crates/cloudkitty-py'
```

Every test passes and the diff above is empty. Inline `#[cfg(test)]`
modules cannot be separated by pathspec: additionally review
`git diff c6fbeae -- crates/cloudkitty-core/src/behavior` and confirm no
hunk falls inside a `#[cfg(test)]` module (the rewires touch production
functions only).

> **Record (2026-07-26):** full workspace green at every checkpoint
> (T005, T007, final). Tests-dir diff vs `c6fbeae`: empty. Behavior-file
> hunks all fall in production regions (largest hunk start line 185;
> inline test modules begin past line 360 in both files) — zero test
> changes anywhere.

## 2. The eval-instrument recheck (FR-006, SC-003) — four-way byte comparison

The default cat is the suite's counterfactual anchor; these four
comparisons prove the measuring stick didn't move. Same procedure 018
proved out:

```sh
# Baseline binary (pre-refactor main)
git worktree add "$CLAUDE_JOB_DIR/tmp/ck-019-base" c6fbeae   # or any tmp path
cargo build --release --manifest-path "$CLAUDE_JOB_DIR/tmp/ck-019-base/Cargo.toml" -p cloudkitty-rl --bin kitty-eval
# Feature binary
cargo build --release -p cloudkitty-rl --bin kitty-eval

OUT="$CLAUDE_JOB_DIR/tmp/ck-019-verify" && mkdir -p "$OUT"   # job tmp, not shared /tmp
BASE="$CLAUDE_JOB_DIR/tmp/ck-019-base/target/release/kitty-eval"
NEW=target/release/kitty-eval

$BASE --suite evals/v1 --brain needs_driven --json $OUT/base-suite.json > $OUT/base-suite.txt
$NEW  --suite evals/v1 --brain needs_driven --json $OUT/new-suite.json  > $OUT/new-suite.txt
$BASE --brain needs_driven --seeds 1,2,3 --ticks 2000 --json $OUT/base-cert.json > $OUT/base-cert.txt
$NEW  --brain needs_driven --seeds 1,2,3 --ticks 2000 --json $OUT/new-cert.json  > $OUT/new-cert.txt

diff $OUT/base-suite.txt $OUT/new-suite.txt && cmp $OUT/base-suite.json $OUT/new-suite.json \
  && diff $OUT/base-cert.txt $OUT/new-cert.txt && cmp $OUT/base-cert.json $OUT/new-cert.json \
  && echo "ALL FOUR BYTE-IDENTICAL"
```

Note the suite run exercises the mixed-roster cells too — `needs_driven`
seats, `playful` seats, and the derived all-scripted baseline all flow
through the refactored stack, so this one command covers every built-in
consumer including `playful`'s shared opportunism.

> **Record (2026-07-26):** baseline built from the branch base (code
> verified identical to `c6fbeae`: `git diff c6fbeae -- crates/` empty at
> capture time — no separate worktree needed). Exits 0/0 both builds.
> All four comparisons **byte-identical**, verified three times (after
> US1, after US2, and final).

## 3. Single-definition review sweep (SC-001, FR-002)

Reviewer confirms against the survey's mirror list (BACKLOG 2026-07-26
entry item 2): `distance_given` holds no need→resource pairing of its
own; `pursue` holds none; `take_what_is_here`'s three same-shaped blocks
are gone; the retired mirror comments no longer exist
(`grep -rn "Mirrors" crates/cloudkitty-core/src/behavior/` returns
nothing for the retired pair); `relief()` is the only site pairing a
need with its relief.

> **Record (2026-07-26):** "Mirrors `pursue`'s sleep arm exactly" — zero
> hits; the 004-mirror phrasing survives only inside the reworded
> historical attribution on `sunbeam_worth_walking` (which now points at
> the `relief` module's invariant). Remaining `ElementType::Chow/Water`
> references in the behavior stack are terrain/pricing knowledge
> (spec 010 water surcharge, seek/wander mechanics) and test fixtures —
> none pairs a need with its relief. `relief()` is the sole pairing site.

## 4. The new-need walkthrough (SC-005, FR-003) — recorded, not landed

Enumerate the edit sites a hypothetical `NeedKind::Bask` (relieved by an
existing shape, say `Sunbeam`) would require:

- **Before** (at `c6fbeae`): `NeedKind` + `ALL` (needs.rs),
  `distance_given` arm, `pursue` arm, optionally a `take_what_is_here`
  block, plus every exhaustive `match` over `NeedKind` elsewhere.
- **After**: `NeedKind` + `ALL`, one `relief()` arm — the consumers'
  shape arms already handle it; omitting the `relief()` arm is a
  compile error.

Confirm by briefly adding the variant, observing the compiler's error
list names exactly `relief()` (plus any engine-side exhaustive matches
outside this feature's scope — enumerate them honestly), then revert.
Nothing lands (spec 019 FR-008).

> **Record (2026-07-26):** hypothetical `NeedKind::Bask` added; the
> compiler forced exactly four sites: `behavior/relief.rs:57` (the
> correspondence — the **only** behavior-stack site), plus three
> pre-existing definitional/engine sites outside this feature's scope
> (`needs.rs` — the `ALL` const and the enum's own definitional impls —
> and `meow.rs:54`, the meow-vocabulary mapping). The three consumer
> steps (`distance_given`, `pursue`, `take_what_is_here`) did **not**
> appear — pre-refactor, each would have. Downstream-crate sites were
> not reached (core fails first); the RL observation encoder iterates
> `NeedKind::ALL` rather than matching, by 014 design. Variant reverted;
> tree clean; nothing landed.
