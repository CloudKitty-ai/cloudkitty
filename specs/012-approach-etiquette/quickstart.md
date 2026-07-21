# Quickstart: Approach Etiquette

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

## 1. The suite

```bash
cargo test --workspace   # incl. tests/approach_etiquette.rs regressions
cargo clippy --workspace --all-targets -- -D warnings && cargo fmt --all -- --check
node client/test-meadow.mjs
```

Expected: the pinned dance world resolves ≤ 6 ticks (was 145 silenced /
lottery-dependent live), identical with need-meows on cooldown; the
play-chase variant lands its pounce; vocabulary and yield-guard units green;
all prior suites untouched.

## 2. Watch it (SC-004)

Demo world on `127.0.0.1:8093` (throwaway snapshot). Watch two kitties head
for each other: a beat of approach, one "Wait for me!" bubble from the
yielding kitty, and the cuddle or game begins — no more corner dancing.
