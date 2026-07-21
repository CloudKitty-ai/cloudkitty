# Quickstart: Water-Averse Pathing

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## 1. The suite (SC-001, SC-002, SC-004)

```bash
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```

Expected green, including:
- `needs_driven` stepper tests — dry beats wet, wade when wet is the only way,
  dry-preferring fallback, a soggy kitty steps out of the puddle;
- `selection` pricing tests — L-path arithmetic, the 4-across-water bowl
  losing to the 6-dry bowl, the only-option bowl still chosen;
- `config` tests — default 4.0 when absent, invalid values rejected naming
  the field;
- the crafted skirt/wade run and the full welfare/property suite
  (`welfare_longrun.rs`).

## 2. Nothing else moved (FR-008, plan R5)

```bash
git diff e9a9772 -- client/ crates/cloudkitty-server/ \
  crates/cloudkitty-core/src/action.rs crates/cloudkitty-core/src/world.rs \
  crates/cloudkitty-core/src/spawn.rs crates/cloudkitty-core/src/invariants.rs
```

Expected: empty (diff base = the 009 feature commit). Config diffs are
exactly one documented `water_step_cost` line per shipped world file.

## 3. Zero-edit compatibility (SC-005)

```bash
git stash -- cloudkitty.toml   # temporarily hide the documented line
cargo run -- --config cloudkitty.toml --help >/dev/null && echo "old config loads"
git stash pop
```

(Any pre-010 config parses and runs with the default in force.)

## 4. Watch it (SC-003) — throwaway world, never the live save

The 009 demo world on `127.0.0.1:8093` serves for this gate too: its config
carries the new documented default. Watch a kitty whose errand passes a
pond: with both axes open it walks the dry corner around the water; only a
target dead across the water produces a wade. Toggle `l` (grid) to read the
geometry. For a denser look, the 16×16 world (45 px tiles) makes individual
steps easiest to see.
