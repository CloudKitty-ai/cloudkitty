# Quickstart: Sustained Purring

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## 1. The suite (SC-001..SC-004)

```bash
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```

Expected green, including: the `purr_phase` unit tests (earned start with
in-bounds duration and exactly one meow; cooldown respected; scheduled end;
a purring kitty still eats), config default/validation tests,
`purring_is_no_longer_an_action`, the 2,000-tick purr-rhythm property run,
and the untouched welfare/determinism suites.

## 2. Zero-edit compatibility (SC-003, SC-005)

The old-JSON kitty fixture (`kitty.rs` tests) deserializes a pre-011 kitty
— no purr fields — and must come up quiet and eligible. The whole-table
`[purr]` serde default covers configs the same way.

## 3. Watch it (SC-005) — throwaway world, never the live save

```bash
# restart the demo with the new build; same throwaway pattern as 009/010
curl -s http://127.0.0.1:8093/kitties | python3 -m json.tool | grep -A1 purring
```

In the viewer, a contented kitty's card line gains `· purring 💕` while it
rumbles — including mid-walk, mid-meal, and mid-cuddle (the point of the
feature). Purrs come in waves: rumble, rest, rumble.
