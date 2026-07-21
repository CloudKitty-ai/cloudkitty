# Quickstart: Orthogonal-Only Interactions

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

How to prove the feature works, end to end. Prerequisites: stable Rust
toolchain (`export PATH="$HOME/.cargo/bin:$PATH"` on this machine).

## 1. The suite is the star witness (SC-001, SC-002, SC-004)

```bash
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```

Expected: green, including
- `grid::tests` — the rewritten adjacency truth table (diagonal excluded),
- `action` validation tests — diagonal Eat/Drink/Play proposals resolve to Idle,
- `needs_driven` — a kitty diagonal to chow steps orthogonal, then eats,
- `world` pursuit tests — diagonal→orthogonal conversion counts as chase progress,
- `welfare_longrun` — the new per-tick assertion: every eating/drinking kitty's
  element is within Manhattan 1, over tens of thousands of randomized ticks.

## 2. Nothing else moved (SC-005, FR-009, R8)

```bash
git diff --stat main -- client/ cloudkitty.toml crates/cloudkitty-server/
git diff main -- crates/cloudkitty-core/src/spawn.rs
```

Expected: both empty. (`cloudkitty.toml`, `cloudkitty16.toml`,
`cloudkitty48.toml` carry the owner's own staged tuning on this branch —
the check above scopes to what *this feature* may not touch; the feature
itself adds zero config lines.)

## 3. Watch it (SC-006) — throwaway world, never the live save

```bash
sed -e 's/^snapshot_path = .*/snapshot_path = "\/tmp\/ck-009-demo.json"/' \
    cloudkitty.toml > "$CLAUDE_JOB_DIR/tmp/ck-009-demo.toml"
cargo run -- --config "$CLAUDE_JOB_DIR/tmp/ck-009-demo.toml" --fresh --no-backup
open http://127.0.0.1:8090
```

Watch for: a kitty approaching a bowl or puddle always takes up a position
directly beside it (never corner-to-corner) before its eating/drinking bubble
appears; cuddling and grooming pairs sit side-by-side or stacked, never
diagonal. Press `l` (grid lines) to make the geometry easy to read.

## 4. Old saves resume cleanly (SC-003)

```bash
# On main: run a world a few hundred ticks, Ctrl-C (it saves on shutdown).
# On this branch: start again with the same config/snapshot.
cargo run -- --config "$CLAUDE_JOB_DIR/tmp/ck-009-demo.toml"
```

Expected: clean startup, no errors; any scene that was mid-flight across a
diagonal ends within a tick and the kitty re-plans. Determinism within the
new rules: two runs from the same restored snapshot stay identical (the
existing save/restore determinism test covers this headlessly).
