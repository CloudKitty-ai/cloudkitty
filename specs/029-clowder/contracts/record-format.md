# Record Format Contract: the Clowder run record

One file per run (FR-010). CSV, three layers: a commented preamble, one
header row, then data rows distinguished by a `scope` column. Everything a
comparison or plot needs is in this one file.

## Preamble

`#`-prefixed `key: value` lines, before the header row. Keys, in order:

```
# clowder: <tool version> (<git describe, when available>)
# started_at: <UTC ISO-8601>
# mode: <ramp|spike|slow-consumer|churn|hold>
# scenario: <every flag and its effective value, one flag per line>
# health_thresholds: <effective FR-016 values> [non-default marked "(non-default)"]
# target: <URL>
# config_sha256: <hash of GET /config body>
# tick_ms: <from /config>
# roster_size: <from /config>
# world_dims: <WxH from /config>
# first_payload_bytes: <byte length of first GET /world body>
# nofile_limit: <generator RLIMIT_NOFILE>
# outcome: <completed|invalidated|interrupted>   (written at run end)
# classification: <comma-separated DegradationSignature list, or "healthy">
```

Parsers MUST ignore unknown `#` keys (the preamble may grow; the data
schema is the stable part).

## Header and data rows

One header row, columns exactly as in
[data-model.md § IntervalRow](../data-model.md): `t, scope, step, class,
conns_target, conns_open, updates, skips, bytes, handshake_p50_ms,
handshake_p99_ms, gap_p50_ms, gap_p99_ms, cadence_ms, poll_p50_ms,
poll_p99_ms, poll_errors, errors, handshake_failures, unexpected_ends,
gen_fd_headroom, gen_lag_ms, valid`.

`handshake_failures` counts connections that never established (a handshake
failure — FR-016's `max_handshake_failures` gate keys on this); `errors` is
the raw error-event count including mid-stream and schema-drift errors, kept
for diagnosis only; `unexpected_ends` counts drops of *established* streams
(FR-012 `connection_drops`). Latency percentiles (`handshake_*`, `gap_*`,
`poll_*`) are quantized down to powers of two — a value of 256 means "in
[256, 512) ms".

- `scope=interval`: one row per interval per active class, in time order.
- `scope=step`: one row per ramp step per class, aggregated over the
  step's hold; `t` is the step's end. Non-ramp modes emit none.
- `scope=run`: one row per class over the whole run; last rows in the file.

Columns that do not apply to a row's mode or scope are empty, never
omitted — every row has every column (one schema across all modes, per
the 2026-08-12 clarification).

## Semantics that MUST hold

- `skips` is derived from gaps in consecutive tick numbers on each
  connection, summed per class per interval (FR-007).
- `cadence_ms` comes from a designated healthy reference connection
  (FR-008); if the reference is lost, the next healthy viewer is promoted
  and the promotion is recorded as a `# note: cadence reference promoted
  at t=<secs>` line appended after the last data row. (`#`-prefixed lines
  may appear both before the header and after the final row; a parser
  skips every `#` line wherever it sits.)
- `valid=false` rows are excluded from step/run summaries and from any
  ceiling claim (FR-011); if any step contains an invalid interval, the
  run outcome is `invalidated` unless the step still fails healthily on
  valid rows alone.
- Summary rows are derived from interval rows and never measured
  independently — recomputing them from the file must reproduce them.

## Compatibility

The column list above is schema v1 and is append-only: new columns go on
the end, existing columns never reorder or change meaning. The preamble
carries no schema version; the header row *is* the schema declaration.
