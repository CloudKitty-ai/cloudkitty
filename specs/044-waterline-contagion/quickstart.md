# Quickstart validation: Waterline Contagion (spec 044)

All commands from the worktree root (`~/ai/cloudkitty-waterline`).

## 1. Inert launch (SC-001)

```sh
cargo test --workspace
```

Expect: full suite green with **zero modified existing tests** — in
particular `evolution_golden` (unregenerated golden = byte-identical
default stream), `determinism`, and the config stamp guard, which now
also asserts `contagion_factor` stays out of the default serialization.

## 2. Armed behavior (SC-002, SC-003, SC-005)

```sh
cargo test --test waterline_contagion
```

Expect: per-kind accrual tests (rest, co-sleep, social play, groom)
match the hand-computed `ambient + factor × gain × ratio`; wet-member
exemption; ceiling gate; both-dry / both-wet / critter-play /
asymmetric-reference nothing-cases; armed same-seed determinism.

## 3. Validation budget (SC-004)

```sh
cargo test -p cloudkitty-core config::validate
```

Expect: boundary accept/reject exactly per
[contracts/config-surface.md](contracts/config-surface.md).

## 4. Served config + sweeps (SC-006)

```sh
cargo test --test shipped_configs
cargo test -p cloudkitty-rl --test shipped_configs_rl
```

Expect: both sweeps green with no config edits.

## Reference

- Mechanism and invariants: [data-model.md](data-model.md)
- Design decisions D1–D7: [research.md](research.md)
- NOT in this delivery: the flip to 1.0 (its own config-only deploy +
  soak, after the 041 soak), the KITTY_SLOT observation float (fog
  wall), any RL retrain.
