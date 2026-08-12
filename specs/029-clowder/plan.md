# Implementation Plan: Clowder — viewer load benchmark

**Branch**: `029-clowder` | **Date**: 2026-08-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/029-clowder/spec.md`

## Summary

Clowder is a load-generation CLI that answers "how many concurrent viewers
can this server sustain, and how does it fail past that?" It drives real
viewer traffic (one `GET /world` first paint, then the `/ws` subscription)
in five shapes — ramp, spike, slow-consumer, churn, and a read-only poller
mix — and measures everything from outside: the tick number every payload
already carries gives per-connection skips and lag and the world's observed
tick cadence, with no server or engine change. Runs emit a one-file CSV
record (identity-stamped, 1-second interval rows, derived summaries) and a
human summary that names the ceiling under the FR-016 health definition and
classifies degradation into named signatures.

Technical approach: a new workspace bin crate `crates/clowder` on the
workspace's existing tokio + serde stack, plus `tokio-tungstenite` for the
WebSocket client. One task per connection; a cheap bounded prefix scan
extracts the tick from each payload (it is the third field, within the
first ~40 bytes), validated by one full parse per connection; a 1 Hz
sampler aggregates per-connection counters into interval rows. The
generator watches its own file-descriptor headroom and sampler lag and
invalidates measurements rather than blaming the server (FR-011).

## Technical Context

**Language/Version**: Rust, the workspace's stable toolchain (same policy
as every other crate; no nightly features)

**Primary Dependencies**: `tokio` (workspace), `serde`/`serde_json`
(workspace), `sha2` (already in-tree), `tokio-tungstenite` (new — WS
client), `libc` (getrlimit; already a transitive dependency). No histogram
crate: latency distributions use hand-rolled log-spaced buckets (~30 lines)
per the stdlib-first rule.

**Storage**: files — one CSV record per run at a configurable path
(`#`-prefixed preamble for identity and scenario, interval rows, tagged
summary rows)

**Testing**: `cargo test` — unit tests for the tick scan, FR-016 health
evaluation, degradation classification, target guard, and record schema;
one integration test that boots the real `cloudkitty-server` binary on an
ephemeral port with a tiny fast-tick world and runs a short smoke scenario

**Target Platform**: macOS (development) and Linux (the serving box's
class of hardware); generator and server may be the same or different hosts

**Project Type**: CLI — new workspace member `crates/clowder`

**Performance Goals**: the generator must not become the bottleneck below
5,000 concurrent connections on development hardware: per-payload work is
a bounded prefix scan (no full JSON parse in steady state), and interval
sampling is O(connections) once per second

**Constraints**: zero modifications to existing crates (FR-009, SC-004);
the only file outside `crates/clowder/` that changes is the workspace
manifest gaining the member. Read-only traffic exclusively. Local targets
by default; non-local requires `--allow-remote`; the live world is never a
permitted target (FR-013).

**Scale/Scope**: up to ~10k connections per run (ephemeral-port bounded);
runs are minutes long; records are single-digit MB at 1 s intervals

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Verdict |
|---------|------|---------|
| I–III (kitty welfare, immortality, company) | Feature must not alter engine welfare semantics | PASS — no engine code is touched (FR-009); the diff under existing crates is empty by requirement (SC-004) |
| IV (engine is the law) | No new behavior/advisor surface | PASS — Clowder is a pure external client of read-only endpoints; it proposes nothing |
| V (server-authoritative, deterministic) | Client renders/reads only; no simulation influence | PASS — read-only GET/WS traffic; the one *risk* (load degrading the tick loop) is exactly what the tool measures, against disposable local worlds only (FR-013) |
| VI (spec-first, test-guarded, constants in config) | Spec precedes code; every constant configurable; CI-tested | PASS — this flow is the spec; every threshold and schedule value is a documented CLI parameter with defaults (FR-015, FR-016); unit + integration tests ride the required `cargo test --workspace` gate |

No violations; Complexity Tracking not needed.

**Post-Phase-1 re-check (2026-08-12)**: design artifacts introduce no new
surface on the engine or server; the integration test boots the server
binary unmodified with an ordinary config file. PASS unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/029-clowder/
├── spec.md              # Feature specification (clarified 2026-08-12)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── cli.md           # Command-line contract: modes, flags, defaults, exit codes
│   └── record-format.md # Run-record contract: preamble, columns, summary tagging
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/clowder/
├── Cargo.toml           # bin crate; tokio, serde_json, sha2, tokio-tungstenite, libc
├── src/
│   ├── main.rs          # CLI parsing, mode dispatch, exit codes (FR-014)
│   ├── target.rs        # target URL parsing, local/non-local guard (FR-013),
│   │                    #   identity stamp fetch: GET /config hash + world facts (FR-010)
│   ├── viewer.rs        # one viewer connection: first-paint GET, WS subscribe,
│   │                    #   read loop or deliberate stall (FR-001, FR-004)
│   ├── scan.rs          # bounded prefix tick extraction + per-connection
│   │                    #   full-parse validation (FR-007; edge case: schema drift)
│   ├── modes.rs         # ramp / spike / slow-consumer / churn / poller schedules
│   │                    #   (FR-002..FR-006)
│   ├── metrics.rs       # per-connection counters, 1 Hz interval sampler,
│   │                    #   log-bucket histograms (FR-007, FR-008, FR-010)
│   ├── health.rs        # FR-016 step health + degradation signatures (FR-012)
│   ├── record.rs        # CSV writer: preamble, interval rows, summaries (FR-010)
│   └── selfwatch.rs     # generator bottleneck detection: fd headroom via
│                        #   getrlimit, sampler lag (FR-011)
└── tests/
    └── smoke.rs         # boots cloudkitty-server on an ephemeral port with a
                         #   tiny fast-tick world; asserts a short ramp completes
                         #   healthy and the record parses (SC-005 in miniature)

Cargo.toml               # workspace root: members += "crates/clowder" (only
                         #   change outside the new crate)
```

**Structure Decision**: a new workspace bin crate. Precedent is
`kitty-eval` living inside `cloudkitty-rl`, but Clowder's dependencies
(WebSocket client) belong to no existing crate, and SC-004's "zero changes
under `crates/` outside its own new code" is cleanest when the new code is
its own member. The layout mirrors the tool's pipeline: target → viewers →
scan → metrics → health → record, with modes as the scheduler on top.
