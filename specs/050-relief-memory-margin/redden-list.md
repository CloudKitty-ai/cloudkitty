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
| U2a (T011) | `relief_memory_margin.rs` run with the served key ABSENT | both tests RED: the `Some(0)` precondition; replies 0 | RED as predicted (0.12 s) | committed at its red state |
| U2b (T011) | the precondition replaced by `margin = None` (the old rule) | `the_served_roster_asks_for_water` RED at "must be said" with drink 0 | RED: want_drink 0, want_eat 5 (F-040's structural silence reproduced on served) | `git checkout` of the test; re-read on the next run |
| U2c (T013) | served key landed (T012) | both green, drink ~5–25 / 1,000 | **WRONG PREDICTION**: drink 0 at 1,000 ticks on served verbatim (reply run green: 16 replies). Scratch measurement over 1k / 5k / 20k ticks, margin 0 vs None vs floor 0.01: served verbatim 0 / 3 / 23 drink calls (first at tick 1,610; ~1.2 per 1,000); margin None 0 / 0 / 0 at every horizon; floor 0.01 2 / 8 / 35 calls and 16 / 73 / 273 here_water replies. Cat-ticks with drink top+armed 1,021 per 20k, of which want_drink legal at start-of-tick 25: a thirsty served cat almost always has a pool in view. F-040's ~12 per 1,000 is the ANCHOR config's rate (floor 0.30, announce_here 1, groom 0.5), not the served one. **Horizon raised to 20,000** (the house stream horizon; ~4 s) — the guard measures the mechanism (0 → 23), not the seed. Spec US1-5/6, SC-004, quickstart, research, contract, tasks amended; FLAGGED to the owner in the implement report. | re-run below |
| u2 (T015) | served key landed + T014; whole suite | RED only `fog_continuity::reply_floor_unset_is_byte_identical`; SC-004b (r = 40) green; goldens / stamp / sweeps green; 889 / 1 / 6 | 889 / 1 / 6, 84 s — exactly the predicted red. ACTIONS diverge first, at tick 128 (kitty 4 Idle → Move West), not at the first drink call: scratch diff of the two 130-tick streams shows kitty 3's `want_eat` at tick 118 is the first new call (remembered bowl beyond reach at margin 0), and kitty 4 (cuddle top) then walks toward the heard friend (R10 targeting). No RNG involved. First `want_drink` at tick 1,610. | — |
| T016 | `record_preladder_r5_streams` re-run ONCE; fixtures re-recorded (actions 39,734 lines changed, messages 3,653) | fog_continuity 3 / 0 / 2 green | green as predicted; doc comment names the cause and ticks | — |
| T017 | served diff = one key + comment block + head-comment phrase (verified by `git diff origin/main -- cloudkitty.toml`); stamp test green; `relief_memory_margin` appears nowhere under `evals/` or `training.toml` (only `experiments/FINDINGS.md`, Experiments' F-040 text — untouched) | — | verified | — |
| U1 (T007→T009) | the r + 1 fixture (`want_drink_reads_remembered_water_only_within_reach`) against the UNCHANGED predicate | RED at the margin-0 arm ("the cat may ask"); `water_in_view_silences_want_drink_at_every_margin` green | RED at meow.rs:937 exactly as predicted (20 / 1 in `meow::`); after T008 (the reach in `known_relief`) 21 / 0 green; `meow_law_fog` 6 / 0 green (key absent — SC-003) | the red test committed at its red state; closed green on the change |
