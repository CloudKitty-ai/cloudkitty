# 050 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast` (`scratchpad/cycle.sh LABEL`); predictions
written BEFORE the run; restore verified by RE-READING THE COUNT. Commit before
every mutate-then-revert cycle. Any mutation that can move a live trajectory
predicts ALL golden-family pins (evolution golden, strip witness, run_json
golden, joint parity) or names why not (048 cycle-A lesson).

Baseline count (branch tip `5e5803f`, before any engine change, 2026-09-05):
**884 / 0, 6 ignored**, wall 78 s; `cargo fmt --all -- --check` clean;
`cargo clippy --workspace --all-targets -- -D warnings` clean. Toolchain
1.97.1 per `rust-toolchain.toml`.

FINAL count: recorded at T026.

## Cycles

| cycle | mutation | prediction | result | restored (count re-read) |
|---|---|---|---|---|
| c0 | none (baseline) | 884 / 0 / 6 | 884 / 0 / 6, 78 s | — |
| F1 (T003) | `skip_serializing_if` dropped from `relief_memory_margin` | `roam_cell_stays_out_of_the_default_serialization` RED "relief_memory_margin leaked into the stamp" | RED as predicted (`"relief_memory_margin":null` in the JSON) | restored via `git checkout`; 1 / 0 green re-read |
| f0 (T005) | key landed, inert (T002–T004) | 885 / 0 / 6; goldens, stamp, streams unmoved | 885 / 0 / 6, 81 s — as predicted | — |
