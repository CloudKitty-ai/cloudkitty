# Quickstart: validating Clowder end to end

Runnable scenarios proving the feature works, from a fresh checkout.
Contracts referenced, not duplicated: [contracts/cli.md](contracts/cli.md),
[contracts/record-format.md](contracts/record-format.md).

## Prerequisites

- Stable Rust toolchain (the workspace's usual requirement)
- Nothing else: the target is a local server from this same checkout

## 1. Boot a disposable local world

```bash
cargo run --release -p cloudkitty-server -- --config crates/clowder/tests/tiny-world.toml \
  --snapshot /tmp/clowder-target.json --fresh
```

`tiny-world.toml` is the committed test config: a small world, minimum
roster, **scripted-only cats (no policy seats)** so booting never depends
on the working directory or artifact loading, and a moderate tick
(~200 ms) so a seconds-long run measures quickly without flaking on
skips. Note the `bind` it prints; the examples
below assume `127.0.0.1:8090`. (The automated test in step 7 binds
`127.0.0.1:0` and reads the chosen port from the server's startup log.)

## 2. The smoke scenario (SC-005)

```bash
cargo run --release -p clowder -- soak --viewers 100 --duration 120
```

Expected: exit 0; summary reports `healthy` under default FR-016
thresholds — zero skips, cadence within ±5%, zero handshake failures or
unexpected ends; a record file `clowder-soak-<timestamp>.csv` whose
preamble carries the target's `config_sha256`, `tick_ms`, and roster, and
whose `scope=run` rows show `valid=true` throughout.

## 3. Find a ceiling (User Story 1)

```bash
cargo run --release -p clowder -- ramp --to 2000 --step 50 --hold 20
```

Expected: unattended run; per-step progress on stderr; at the end either
"reached 2000 healthy" or the last healthy step, the first degraded step,
and which measure degraded first, with the same conclusion recoverable
from the record's `scope=step` rows.

## 4. Failure characterization (User Story 2)

```bash
cargo run --release -p clowder -- spike --viewers 1000
cargo run --release -p clowder -- slow-consumer --viewers 200 --stall-fraction 0.2
cargo run --release -p clowder -- churn --viewers 200 --churn-rate 20
cargo run --release -p clowder -- soak --viewers 200 --poll-rate 50
```

Expected, respectively: a handshake-latency distribution and
failed-connection count; healthy-class rows showing zero skips while
stalled-class rows accumulate them (SC-006 — if healthy viewers *do* skip,
that is a finding, and the summary says so); setup-cost-over-time without
cadence drift; poller latency/error columns populated beside viewer
measures.

## 5. Guard rails

```bash
cargo run -p clowder -- soak --viewers 10 --target http://192.0.2.7:8090
```

Expected: refused before any connection, naming `--allow-remote`; usage
text states the live world is never a permitted target (FR-013).

```bash
cargo run -p clowder -- soak --viewers 0
```

Expected: rejected at startup naming the flag and allowed range.

## 6. Interrupted-target behavior

Start a `soak` run, then `Ctrl-C` the server. Expected: Clowder exits 3
(`interrupted`), the record's `# outcome:` says `interrupted`, and rows up
to the interruption are preserved and marked valid.

## 7. The automated version

```bash
cargo test -p clowder            # unit + the smoke integration test
cargo test --workspace           # proves SC-004: nothing else changed
```

The integration test (`tests/smoke.rs`) performs a miniature of steps 1–2
on an ephemeral port and asserts the record parses per the contract.
