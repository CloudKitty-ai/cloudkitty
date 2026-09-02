# Redden list: spec 047 consent_line

Every guard shown red first (CLAUDE.md rules 5/6). Format per cycle:
prediction → observed red → revert/implement → green. Suite counts READ
after every run.

## Baseline (T002)

- Branch tip at baseline: 26c9c23 (spec artifacts only).
- `cargo test --workspace`: **793 passed / 0 failed** (64 suites) — the
  post-046 main count, as expected.
- Evolution golden + defaults stamp: green (inside the 793).

| # | Guard | Injected bug / staged state | Predicted red | Observed | Green after |
|---|-------|-----------------------------|---------------|----------|-------------|
| 1 | T005 tie pins (predicate) | both `>` mutated to `>=` in `consent_blocks` | exactly the two tie pins (at-the-line, play-ties-top); blocked + default pins stay green | as predicted: 2 failed, 2 passed | mutation reverted, 4/4 green |
