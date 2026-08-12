# Data Model: Clowder — viewer load benchmark

Phase 1 output. Entities, fields, and state transitions. Wire-level layout
of the record lives in [contracts/record-format.md](contracts/record-format.md).

## Scenario

The complete description of one run (FR-015: same scenario = same config).

| Field | Type | Notes |
|-------|------|-------|
| `mode` | enum: `ramp` \| `spike` \| `slow-consumer` \| `churn` \| `soak` | `soak` is the fixed-N shape the poller mix and SC-005 smoke use |
| `target` | URL | server base; local unless `allow_remote` |
| `allow_remote` | bool | FR-013 acknowledgment flag |
| `viewers` | u32 | target concurrency (per step-schedule in ramp) |
| `step`, `step_interval`, `hold` | u32, secs, secs | ramp schedule (FR-002) |
| `stall_fraction`, `stall_after` | f32, secs | slow-consumer mix (FR-004) |
| `churn_rate` | conns/sec | churn mode (FR-005) |
| `poll_rate`, `poll_endpoints` | reqs/sec, list | poller mix (FR-006) |
| `duration` | secs | run bound for non-ramp modes |
| `interval` | secs (default 1) | record row granularity (clarify #2) |
| `repeat` | u32 (default 1) | scenario repetitions; n>1 emits the SC-003 agreement check |
| `health` | thresholds struct | FR-016: `max_skips` (0), `cadence_tolerance` (0.05), `max_handshake_failures` (0), `max_unexpected_ends` (0) |
| `out` | path | record file destination |

Validation: zero/absent counts, rates, or durations are rejected at startup
naming the field (spec edge case; matches the server's config-rejection
convention).

## TargetIdentity

Fetched once at run start (research R5); stamps the record.

| Field | Source |
|-------|--------|
| `config_sha256` | hash of `GET /config` response body |
| `tick_ms` | parsed from `/config` |
| `roster_size` | parsed from `/config` |
| `world_dims` | parsed from `/config` |
| `first_payload_bytes` | byte length of the run's first `GET /world` body |
| `tool_version` | Clowder crate version + git describe when available |
| `nofile_limit` | generator's `RLIMIT_NOFILE` (FR-011 context) |
| `started_at` | UTC timestamp |

## ConnectionObservation

Per-connection lifetime measurement set (FR-007).

| Field | Type | Notes |
|-------|------|-------|
| `id` | u32 | |
| `class` | enum: `viewer` \| `stalled` \| `poller` | `stalled` from the moment reads stop (research R8) |
| `handshake_ms` | f64 | first-paint GET + WS upgrade, measured separately |
| `updates` | u64 | payloads received |
| `skips` | u64 | sum of gaps in consecutive tick numbers |
| `last_tick` | u64 | |
| `bytes` | u64 | |
| `end` | enum: `open` \| `closed_by_run` \| `server_closed` \| `error(kind)` \| `refused` | "unexpected" for FR-016 = `server_closed`, `error`, `refused` |

State transitions: `connecting → open → (stalled ↔︎ never returns) → ended`.
A viewer selected for stalling transitions `viewer → stalled` exactly once,
at `stall_after`; measurements before the transition count in the healthy
class (SC-006's separation).

## IntervalRow

One row per interval per class (clarify #2; FR-010). Shared schema across
modes — columns that don't apply hold empty values, never mode-specific
columns.

| Column | Notes |
|--------|-------|
| `t` | seconds since run start |
| `scope` | `interval` here; `step`/`run` on summary rows |
| `step` | ramp step ordinal (empty outside ramp) |
| `class` | `viewer` / `stalled` / `poller` / `all` |
| `conns_target`, `conns_open` | schedule vs reality |
| `updates`, `skips`, `bytes` | this interval |
| `handshake_p50_ms`, `handshake_p99_ms` | connections established this interval |
| `gap_p50_ms`, `gap_p99_ms` | inter-update arrival gaps |
| `cadence_ms` | observed tick cadence (FR-008), from a designated healthy reference connection |
| `poll_p50_ms`, `poll_p99_ms`, `poll_errors` | poller mix |
| `errors`, `unexpected_ends` | this interval |
| `gen_fd_headroom` | remaining descriptors (FR-011) |
| `gen_lag_ms` | sampler lateness — nonzero means generator strain |
| `valid` | bool; false when FR-011 invalidates the interval |

## StepSummary / RunSummary

Derived from interval rows (never measured independently), emitted as
`scope=step` / `scope=run` rows plus the human summary.

- Step: healthy bool per FR-016 at the run's thresholds; per-measure
  aggregates; `first_degraded_measure` when unhealthy.
- Run: ceiling (last healthy step), classification list (see below), and
  outcome ∈ `completed` | `invalidated` | `interrupted` (maps to FR-014
  exit codes).

## DegradationSignature (FR-012)

Closed enum shared by summaries, records, and the human report:

`skipped_updates` · `rising_lag` · `unstable_cadence` ·
`handshake_failures` · `connection_drops` · `server_unresponsive` ·
`generator_bottleneck` (invalidating, never attributed to the server)

## Exit codes (FR-014)

| Code | Meaning |
|------|---------|
| 0 | run completed (healthy or degradation measured — both are successful measurements) |
| 1 | usage or configuration error |
| 2 | run completed but invalidated by a generator-side bottleneck |
| 3 | run interrupted by target failure (server died/restarted mid-run) |
