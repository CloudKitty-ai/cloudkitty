# CLI Contract: clowder

The command-line surface is the tool's public interface; this contract is
what `--help`, the tests, and the quickstart all agree on. One binary, one
subcommand per traffic shape.

```
clowder <MODE> --target <URL> [mode flags] [common flags]
```

Modes: `ramp`, `spike`, `slow-consumer`, `churn`, `soak`. (`soak` is the
fixed-concurrency shape; the `--hold` flag under `ramp` is unrelated —
it is a ramp step's dwell time, not a mode.)

## Modes and their flags

### `clowder ramp`

| Flag | Default | Meaning |
|------|---------|---------|
| `--to <N>` | required | target concurrency |
| `--step <N>` | 25 | viewers added per step |
| `--step-interval <secs>` | 5 | pause between establishing steps |
| `--hold <secs>` | 30 | how long each step must stay healthy (FR-016) |

Stops at `--to` or at the first unhealthy step; either way exit 0 — a
measured degradation is a successful measurement.

### `clowder spike`

| Flag | Default | Meaning |
|------|---------|---------|
| `--viewers <N>` | required | connections issued as fast as possible |
| `--duration <secs>` | 60 | observation window after the spike |

### `clowder slow-consumer`

| Flag | Default | Meaning |
|------|---------|---------|
| `--viewers <N>` | required | total connections |
| `--stall-fraction <f>` | 0.1 | fraction that stops reading |
| `--stall-after <secs>` | 10 | healthy period before the stall |
| `--duration <secs>` | 120 | run length |

### `clowder churn`

| Flag | Default | Meaning |
|------|---------|---------|
| `--viewers <N>` | required | steady-state concurrency |
| `--churn-rate <conns/sec>` | 5 | arrivals (and departures) per second |
| `--duration <secs>` | 120 | run length |

### `clowder soak`

| Flag | Default | Meaning |
|------|---------|---------|
| `--viewers <N>` | required | fixed concurrency held for the duration (SC-005 smoke shape) |
| `--duration <secs>` | 120 | run length |

## Common flags (all modes)

| Flag | Default | Meaning |
|------|---------|---------|
| `--target <URL>` | `http://127.0.0.1:8090` | server base URL; `ws(s)://` derived |
| `--allow-remote` | off | required for any non-loopback target (FR-013) |
| `--poll-rate <reqs/sec>` | 0 | read-only poller mix alongside viewers (FR-006) |
| `--poll-endpoints <list>` | `/world,/kitties,/config` | endpoints the pollers rotate through |
| `--interval <secs>` | 1 | record row granularity |
| `--repeat <n>` | 1 | run the scenario n times into suffixed records; with n>1, print the ceiling agreement check against SC-003's ±10% tolerance |
| `--out <path>` | `clowder-<mode>-<timestamp>.csv` | record destination (a `--repeat` run suffixes `-1`, `-2`, …) |
| `--max-skips <N>` | 0 | FR-016 threshold |
| `--cadence-tolerance <f>` | 0.05 | FR-016 threshold |
| `--max-handshake-failures <N>` | 0 | FR-016 threshold |
| `--max-unexpected-ends <N>` | 0 | FR-016 threshold |

Non-default health thresholds are stamped in the record preamble and named
in the human summary (FR-016: "a record produced under non-default
thresholds says so").

## Usage text obligations

`--help` MUST state: targets are local by default; `--allow-remote` exists
for servers you own; **the live world is never a permitted target** (FR-013).

## Exit codes

`0` completed · `1` usage/config error · `2` completed but invalidated by a
generator-side bottleneck · `3` interrupted by target failure (FR-014;
see data-model.md).

## Rejection behavior

Invalid values (zero counts, zero durations, fractions outside (0,1],
unparseable URLs) are rejected at startup with a message naming the flag,
its value, and the allowed range — the server's config-rejection
convention, applied to the tool.
