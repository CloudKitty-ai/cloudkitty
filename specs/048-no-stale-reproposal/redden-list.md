# 048 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast`; predictions written BEFORE the run;
restore verified by RE-READING THE COUNT. Commit before every
mutate-then-revert cycle (checkout-trap rule, five occurrences on record).

Baseline count (branch tip before implementation): recorded at cycle 0.

| # | Task | Mutation / staging | Prediction (exact reds) | Observed | Restored + count re-read |
|---|------|--------------------|-------------------------|----------|--------------------------|

(rows appended as cycles run)

## probe-after (T014 results)

(recorded at T014)
