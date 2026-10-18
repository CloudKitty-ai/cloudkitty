# Quickstart: validating friend-ward drift

Runnable end-to-end checks for the landed feature. Law details live in
[contracts/drift-law.md](contracts/drift-law.md); field shapes in
[data-model.md](data-model.md).

## Prerequisites

- This worktree (`product/friend-ward-drift`), pinned toolchain.
- Local gate: `cargo fmt` + `cargo clippy --all-targets` +
  `cargo test` from the workspace root.

## 1. Flag-off byte-identity (FR-002 / SC-001)

```sh
cargo test -p cloudkitty-core            # goldens + determinism all run flag-off
```

Expected: entire suite green with ZERO golden, pin, or fixture
re-cuts in the diff (`git diff --stat` shows no changes under
`tests/` fixtures or `specs/*/contracts/` goldens). The config
surface check: `GET /config` serialization tests pass unchanged —
the three new fields never appear when absent.

## 2. Staged drift scenarios (SC-002 / SC-003)

```sh
cargo test -p cloudkitty-core friend_ward
```

Expected: the new unit tests cover — friend-ward pick inside the band;
cheapest wins beyond the band; friend-within-gate and no-known-friend
decide exactly as flag-off; the want/here fence (a fresher
free-register stamp neither places nor hides); the sunbeam reach cap
(a beyond-reach beam never promoted); potter steers when fired,
uniform otherwise; identical contexts choose identically with the flag
on. Each assertion has a declared-prediction `scripts/mutate.sh
--expect` red on record (commit first; the cycle needs a clean file).

## 3. Potter cadence (SC-004)

```sh
cargo test -p cloudkitty-core potter_cadence
```

Expected: over a fixed window, the potter's firing rate with the flag
on matches flag-off within binomial tolerance (direction differs, rate
does not).

## 4. Validation (SC-005)

```sh
cargo test -p cloudkitty-core validate
```

Expected: gate 0 and negative/NaN detour rejected with errors naming
`[behavior] friend_ward_gate` / `[behavior] friend_ward_detour`;
flag-on with absent dials loads defaults (10 / 4.0).

## 5. Flag-on smoke (SC-006 interface)

Derive a scratch copy of a size100 config with the flag on — in the
scratchpad, NEVER committed under `experiments/` (knob-on tomls stay
out; the shipped-config sweep loads every experiments toml):

```sh
# from experiments/tools/bc-collect (standalone workspace):
cargo run --release -- --config <scratch>/size100-drift-on.toml \
  --rollouts 1 --ticks 2000 --seed-base 993001 --out-dir <scratch>/smoke
```

Expected: run completes; arrays well-formed. The seed-paired
happiness/clustering A/B on the g2cmp band is Experiments' screen,
run on the landed binary in their lane — not reproduced here.

## 6. Full local gate before PR

```sh
cargo fmt && cargo clippy --all-targets && cargo test
```

CI must additionally show the shipped-config sweep green (SC-001's
"zero config surface change").
