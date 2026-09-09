# 052 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs the suite that
exercises the guard (`cargo test -p cloudkitty-server` for the crate guards,
`bash docs/deploy/test-update-tail.sh` for the script, the whole workspace at
cycle 0 and the final cycle); predictions written BEFORE the run; restore
verified by RE-READING THE COUNT. Every red goes through
`scripts/mutate.sh --expect <prediction>` (it refuses a dirty file, a mutation
that stays green or fails for another reason, and a restore that moves the
count). Commit before every cycle. No mutation in this arc can move a live
trajectory (the engine crate is untouched), so the golden-family pins are
predicted unmoved once, at the final cycle, not per red.

Baseline count (branch tip `a757595`, before any change, 2026-09-09):
**897 / 0, 6 ignored**, wall 4 min 19 s including the worktree's first build;
`cargo fmt --all -- --check` clean; `cargo clippy --workspace --all-targets
-- -D warnings` clean. Toolchain 1.97.1 per `rust-toolchain.toml`.

SC-003 evidence plan: `/config` on the served toml captured from the
pre-change server code (`config-before.json`, session scratchpad) and again at
T016; the stamp read through the new block at F0 and again at the final
cycle; and `git diff main --stat -- crates/cloudkitty-core crates/cloudkitty-rl`
empty at every commit (the stamp hashes those two crates' defaults and
nothing else).

## Cycles

| cycle | mutation | prediction | result | restored (count re-read) |
|---|---|---|---|---|
| c0 | none (baseline) | — | 897 / 0 / 6, 4:19 (71 test binaries) | — |
