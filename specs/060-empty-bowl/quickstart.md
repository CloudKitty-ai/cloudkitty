# Quickstart: validating spec 060

Prerequisites: this worktree (`~/ai/cloudkitty-empty-bowl`), Rust
toolchain per repo pin. All commands from the worktree root.

## 1. The amended rule, unit level

```sh
cargo test -p cloudkitty-core --lib -- resolve_activity_ends \
  an_emptied_bowl need_zero_before_the_minimum
```

Expected: the rewritten empty-bowl guard (early end at first
resolution, `dinner_table(1)`) passes; `need_zero_before_the_minimum_waits_for_the_minimum`
still passes (the kept clause). Every new/changed assertion goes
through `scripts/mutate.sh --expect <prediction>` red-first — e.g.
mutate the amended condition back to spec 006's grouping and predict
the early-end guard's exact failure.

## 2. Kept behavior, workspace level

```sh
cargo fmt --all && cargo test --workspace
```

Expected: green at the same count discipline as 059 (record the
number); the only test-file diffs are the rule-6 sorted changes and
re-pinned fixtures, each with a declared reason.

## 3. Stream divergence accounting (US2)

```sh
cargo test -p cloudkitty-core --test fog_continuity
```

If red before re-record: capture first-divergence ticks, append the
justification paragraph naming spec 060, then re-record via the
`#[ignore]`d mains:

```sh
cargo test -p cloudkitty-core --test fog_continuity -- --ignored record_
```

Same pattern for `evolution_golden` if the refusal-ring delta moved.

## 4. Config and binding surfaces

```sh
cargo test -p cloudkitty-core --test shipped_configs
cargo test -p cloudkitty-rl --test shipped_configs_rl
```

Expected: green with ZERO config edits. Py binding: fresh
`maturin develop` (VIRTUAL_ENV set — the existing scratchpad binding
is stale), then the binding pytest.

## 5. Welfare direction (SC-003)

Deterministic run on the reference config: count eating-scene ticks
whose resolution-time feeding condition is false (must be 0 post-change,
>0 pre-change on the same seeds) and total eat relief delivered (equal
across arms). Implementation chooses the recorder (the 059
fire-counter/differential pattern); one committed artifact.
