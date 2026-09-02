# Quickstart: validating spec 048 (no stale re-proposal)

Prerequisites: this worktree (`~/ai/cloudkitty-reproposal`, branch
`048-no-stale-reproposal`), pinned toolchain via `rust-toolchain.toml`.

## 1. Scenario guards (fast, targeted)

```sh
cargo test -p cloudkitty-core stale_scene -- --nocapture
```

Expected: the spec-048 test group green — US1 (critter moved / expired → fresh action,
no refusal row), US2 (groomed friend unavailable → fresh action), live-counterpart
continuation pins (FR-004), the shared-predicate doctrine pair (contract invariant 1),
and the personality doctrine test (invariant 3).

## 2. Full suite + identity witnesses

```sh
cargo test --workspace --no-fail-fast
cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings
```

Expected: suite green END COUNT READ; the defaults-stamp test green untouched
(SC-004). The golden evolution pin is EXPECTED to move exactly once during
implementation — re-pinned in the same change with the CHANGELOG marker (FR-008);
after re-pin, green.

## 3. End-to-end on the reference arms (SC-001/SC-002/SC-005)

The 2026-09-02 measurement probe re-runs on the fixed build. It lives on the local
throwaway branch `probe-reproposal-rate` (commit 275896e, never merged):

```sh
git cherry-pick -n 275896e   # probe test rides along, uncommitted
python3 experiments/biscuit3-comfort-sweep-2026-09-01/gen_configs.py <scratch> --consent
PROBE_CONFIG_DIR=<scratch>/configs \
  cargo test -p cloudkitty-core --lib reproposal_probe -- --ignored --nocapture
git restore --source=HEAD --staged --worktree crates/cloudkitty-core/src/lib.rs
git clean -f crates/cloudkitty-core/src/reproposal_probe.rs
```

Expected after the fix, per arm: every class reports `reproposed 0` on dead-at-snapshot
scenes (the counters themselves remain — dead scenes still occur, the behavior just no
longer proposes into them); `same-tick race refusals` for PlayDuet stays in the
2,600–3,400 band (SC-005). Baseline (pre-fix) numbers for comparison are recorded in
[research.md](research.md) §R2.

⚠ The cherry-pick/cleanup step touches `lib.rs`: run it only on a CLEAN tree (commit
first — house rule). Note the cleanup uses `git restore --staged --worktree`, NOT
`git checkout --`: after `cherry-pick -n` the changes sit in the index, and
`checkout --` restores *from* the index — it would silently keep them.

## 4. Red-first record

Every guard's red cycle is recorded in `redden-list.md` (prediction → observed reds →
restore → count re-read), `--no-fail-fast`, per CLAUDE.md rules 5/6 and the 047
standard.
