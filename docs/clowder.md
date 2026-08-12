# Clowder: the viewer load benchmark

Clowder answers two questions about a running CloudKitty server: how many
concurrent viewers it can sustain, and how it behaves once you push past that.
It lives in `crates/clowder` and drives real viewer traffic (a first-paint
`GET /world`, then the `/ws` subscription) while measuring everything from
outside the server. The tick number in every payload gives per-connection
skipped updates, inter-update lag, and the world's observed tick cadence, so
the tool needs no change to the server or the engine.

The full specification is in [`specs/029-clowder/`](../specs/029-clowder/);
this page is the operator's guide.

## Quick start

Build the release binaries and point Clowder at a local server:

```bash
cargo build --release -p cloudkitty-server -p clowder

# a disposable local world in one terminal
cargo run --release -p cloudkitty-server -- --config cloudkitty.toml \
  --snapshot /tmp/clowder-target.json --fresh

# the benchmark in another
./target/release/clowder soak --viewers 100 --duration 120
```

A run prints a short summary and writes one CSV record. The `soak` above holds
100 viewers for two minutes and reports whether the world stayed healthy the
whole time.

## The five traffic shapes

Each mode is a subcommand that probes a different question.

| Mode | Question it answers | Key flags (defaults) |
|------|---------------------|----------------------|
| `ramp` | How many viewers before something breaks? | `--to N` (required), `--step 25`, `--step-interval 5`, `--hold 30` |
| `soak` | Does a fixed load stay healthy over time? | `--viewers N` (required), `--duration 120` |
| `spike` | How does the handshake path handle a thundering herd? | `--viewers N` (required), `--duration 60` |
| `slow-consumer` | Does a stalled viewer harm the healthy ones? | `--viewers N` (required), `--stall-fraction 0.1`, `--stall-after 10`, `--duration 120` |
| `churn` | What does constant connect/disconnect cost? | `--viewers N` (required), `--churn-rate 5`, `--duration 120` |

`ramp` is the one that finds the ceiling. It grows concurrency a step at a
time, holds each step long enough to judge, and stops at the target or at the
first step that fails the health definition below. Either outcome is exit 0: a
measured degradation is a result, not an error.

`slow-consumer` is worth calling out. A configured fraction of viewers stop
reading partway through, letting their sockets back up, and the report keeps
their measurements separate from the healthy viewers'. That separation is the
point: it shows whether the server sheds a slow client without making its
neighbors skip.

A read-only poller mix can ride alongside any shape. Pass `--poll-rate 50` to
add 50 requests/sec across `/world`, `/kitties`, and `/config` (set
`--poll-endpoints` to change them), and the record gains poller latency and
error columns beside the viewer measures. Without `--poll-rate`, no pollers run
and those columns stay empty.

## What "healthy" means

A ramp step is healthy when, for its whole hold, healthy viewers skip nothing,
the observed tick cadence stays within tolerance of the world's nominal rate,
no handshake fails, and no established connection drops. Every threshold is a
flag, and the defaults define the published ceiling:

| Flag | Default |
|------|---------|
| `--max-skips` | 0 |
| `--cadence-tolerance` | 0.05 (±5%) |
| `--max-handshake-failures` | 0 |
| `--max-unexpected-ends` | 0 |

A record produced under non-default thresholds says so in its preamble, so a
looser run can never be mistaken for the strict ceiling. When a step is not
healthy, the report classifies the failure into a named signature:
`skipped_updates`, `rising_lag`, `unstable_cadence`, `handshake_failures`,
`connection_drops`, `server_unresponsive`, or `generator_bottleneck`.

That last signature is the safeguard against lying about the server. Clowder
watches its own file-descriptor headroom and sampler lag, and when the
generator is the bottleneck it marks those measurements invalid rather than
blaming the server for the load tool's own exhaustion.

## The record

Every run writes one CSV file. A `#`-prefixed preamble carries the identity of
what was measured and what it ran against: the tool version, the served
config's sha256, its tick rate, roster size, and world dimensions, the
generator's descriptor limit, and (written at the end) the outcome and
classification. Two runs of the same scenario against the same server carry
matching stamps, and editing the world config visibly changes the sha256, so
records stay comparable across engine changes and hardware.

After the preamble comes one header row and then the data. Rows share a single
schema across all modes, distinguished by a `scope` column: `interval` rows at
the sampling granularity (`--interval`, default 1s), then `step` summaries
(ramp only) and `run` summaries derived from them. Columns that do not apply to
a row are empty, never dropped, so every row has all 23 columns.

Two columns read as blank more often than people expect, both by design:

- Handshake latency (`handshake_p50_ms`, `handshake_p99_ms`) is a connect-time
  measurement, recorded once per connection. It appears in the intervals where
  connections established (row one of a soak, each step's establishment phase
  in a ramp) and is blank during a steady hold, since nothing new is
  handshaking then.
- Poller columns are blank unless the run used `--poll-rate`.

The column list and its semantics are the contract in
[`specs/029-clowder/contracts/record-format.md`](../specs/029-clowder/contracts/record-format.md).

## Exit codes

For scripted use, the exit code distinguishes the four outcomes:

| Code | Meaning |
|------|---------|
| 0 | completed (healthy or a degradation was measured — both are successful measurements) |
| 1 | usage or configuration error |
| 2 | completed but invalidated by a generator-side bottleneck |
| 3 | interrupted by target failure (the server died or restarted mid-run) |

## Targets and safety

Clowder targets `http://127.0.0.1:8090` by default and refuses any non-loopback
host unless you pass `--allow-remote`. **The live world is never a permitted
target.** `--allow-remote` exists for a server you own and can afford to
degrade for real viewers, such as a throwaway world you have stood up for the
test. The server's API is read-only (Article V), so a load test cannot corrupt
a world; the risk `--allow-remote` guards is service degradation for the people
watching, not data.

## Comparing across machines

Because each record stamps the served config's identity, a run on one machine
compares cleanly with a run of the same scenario on another. To size a server
against a laptop, run the same ramp against both using the same
`cloudkitty.toml`, confirm the `config_sha256` matches in both records, and
read the ceilings against each other. The honest comparison for a deployed box
runs through its reverse proxy rather than straight at the bind address, since
the proxy and TLS are part of what real viewers pay for.
