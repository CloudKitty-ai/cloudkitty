# Quickstart: validating shallow ground sleep (spec 056)

## Prerequisites

The workspace toolchain (`rust-toolchain.toml` pins it; `cargo` picks it
up). All commands from the worktree root.

## The targeted suites

```bash
cargo test -p cloudkitty-core sleep        # relief + finished-level tests
cargo test -p cloudkitty-core config       # parse default + bounds refusal
cargo test -p cloudkitty-server settings   # the key-settings lists
cargo test --workspace                     # kept behavior (floor-0 world)
```

Expected: all green; the pre-existing sleep/cosleep/conduction tests
pass untouched — they run at floor 0 and are the unit-layer half of the
default-equivalence claim (FR-007).

## The mutation cycle (rule 5)

Each new assertion goes through the house cycle, e.g.:

```bash
scripts/mutate.sh --expect "the_floor_holds_on_plain_ground" -- <mutation>
```

The six planned reds are listed in plan.md §Rule-5/6 test plan; run each
with its predicted failure before trusting the green.

## Seeing the law by hand

In a scratch copy of `cloudkitty.toml` (never the served file), set:

```toml
[actions]
sleep_floor_off_beam = 20.0
```

Run the server on a seeded world and watch a ground nap: the sleeper's
Sleep need falls to exactly 20 and the nap ends there (after the 6-tick
minimum); a cat napping on a sunbeam still reaches 0. Set the floor to
95 and the server must refuse to start, naming the key and the distress
bound.

## Acceptance (Experiments, on the branch)

Their handover list: the four relief tests + early-end with mutate reds,
default-0 equivalence (their pinned-seed action-for-action run against
the served toml), the `[actions]` doc line, the key in `/settings`. Ping
them when CI is green and the branch is mergeable — the eight tier-5
arms run that night.
