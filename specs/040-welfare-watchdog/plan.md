# Implementation Plan: Serving welfare watchdog

**Branch**: `040-welfare-watchdog` | **Date**: 2026-08-21 | **Spec**: [spec.md](spec.md)

## Summary

A server-side standing watch over the engine's existing
`distress_since` records: one module computing distress ages each
tick, emitting crossing/reminder/recovery alarms into the log, and
publishing current welfare state to a new endpoint. Zero engine
changes; configuration rides a server-owned `[watchdog]` toml table
(the foreign-table pattern), so the defaults stamp provably cannot
move.

## Technical Context

**Language**: Rust, `cloudkitty-server` crate only.
**Dependencies**: none new — axum routes, tokio watch channels, serde,
toml, tracing all in place.
**Storage**: none; alarm bookkeeping is in-memory and rebuilds from
the world's own `distress_since` after restart (spec edge case).
**Testing**: cargo test; unit tests on the watchdog module with
synthetic worlds (constructing `distress_since` directly, the
`kitty.rs` test precedent); red-first per rule 6.
**Constraints**: FR-006 — read-only observer, `observe(&World)`; a
watched and an unwatched world produce identical snapshots. Engine
`Config` untouched (SC-004 asserts default serialization).

## Constitution Check

- **Articles I–III**: PASS — read-only; welfare *observation* in
  service of Article I's distress-event purpose ("a signal for the
  world", now actually listened to).
- **Article IV**: PASS — no behavior surface; the watchdog is not an
  advisor and proposes nothing.
- **Article V**: PASS — no RNG, no mutation, no tick-order change;
  the observer runs after the tick completes on the serving task.
- **Article VI**: PASS — spec-first; threshold/cadence are configured
  constants with documented defaults (150/150), not magic numbers.

## Design decisions

- **D1 — module `crates/cloudkitty-server/src/watchdog.rs`**:
  `WatchdogConfig::from_toml_str` mirrors `RlConfig::from_toml_str`
  (parse `[watchdog]` alone, unknown keys refused, 0 refused naming
  field and value; absent table = defaults 150/150 — on by default,
  no off switch to forget).
- **D2 — single source for alarms**: `Watchdog::observe(&World)`
  returns `(WelfareStatus, Vec<AlarmEvent>)`; the caller logs the
  events (ERROR crossing/reminder, INFO recovery) and publishes the
  status. Tests assert the returned events — the log lines are a thin
  rendering of the same data, so asserting events IS asserting alarms.
- **D3 — serving integration**: `sim_task::spawn` gains the watchdog
  and a `watch::channel<Arc<WelfareStatus>>` (the `Published` pattern
  beside it); after each `world.tick`, observe → log → send. The API
  handler (`GET /welfare`) serves the latest status; healthy shape =
  empty entries, alarm clear.
- **D4 — recovery length**: alarm state stores the last observed age
  per streak, so the recovery line reports the streak's final length
  without touching the world.
- **D5 — restart semantics**: alarm state is empty at boot; a live
  streak past threshold re-fires its crossing on the first observed
  tick (spec edge case: re-announced beats forgotten).

## Project Structure

```text
crates/cloudkitty-server/src/
├── watchdog.rs          # NEW: config, state machine, observe()
├── sim_task.rs          # observe + publish after each tick
├── lib.rs               # route GET /welfare; wire the channel
├── main.rs              # parse WatchdogConfig from the config text
└── api.rs               # the /welfare handler

cloudkitty.toml          # [watchdog] table, documented defaults
CHANGELOG.md             # Unreleased entry (no markers — server-only)
specs/040-welfare-watchdog/  # this arc
```

## Phase 0/1 notes (inline — the arc is small)

Research questions were all settled by reconnaissance: the tick loop
lives in `sim_task.rs` (`world.tick` → publish, the exact insertion
seam), `RlConfig::from_toml_str` (config.rs:253) is the foreign-table
parser to mirror, `/events/distress` (lib.rs:297) shows the route
pattern, and `kitty.distress_since` is directly constructible in
tests (kitty.rs test precedent). Contract = the `[watchdog]` table +
`GET /welfare` shape, documented in the spec's FR-003/FR-004;
quickstart = the test battery plus one live-server curl, folded into
tasks (T-final) rather than a separate file — the arc is one
module.
