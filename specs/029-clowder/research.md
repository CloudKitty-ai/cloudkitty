# Research: Clowder — viewer load benchmark

Phase 0 output. Every Technical Context unknown resolved; each decision
records what was chosen, why, and what was rejected. Code references were
verified against `origin/main` on 2026-08-12.

## R1. Where Clowder lives

- **Decision**: new workspace bin crate `crates/clowder`.
- **Rationale**: the WebSocket client dependency belongs to no existing
  crate; a separate member keeps SC-004 ("zero changes under `crates/`
  outside its own new code") trivially auditable, and the tool versions
  with the repo so records can cite a commit.
- **Alternatives considered**: a second bin in `cloudkitty-server`
  (rejected: pollutes the server's dependency tree with a WS *client* and
  weakens the SC-004 boundary); a standalone repo (rejected: the tool must
  track the payload schema and deserves the same CI).

## R2. WebSocket client library

- **Decision**: `tokio-tungstenite`, with its rustls feature enabled so
  `wss://` targets (a local reverse-proxy shape) work.
- **Rationale**: the workspace already runs on tokio; tungstenite is the
  de-facto client pairing, small, and maintained.
- **Alternatives considered**: raw hyper upgrade handling (rejected: hand
  rolling the WS protocol buys nothing here); `async-tungstenite`
  (rejected: same library behind a runtime-agnostic wrapper we don't need).

## R3. Extracting the tick without parsing the world

- **Decision**: bounded prefix scan for the `"tick":` field, which is the
  third field of `WorldSnapshot` (`crates/cloudkitty-core/src/world.rs:68`
  — `width`, `height`, `tick`, …) and therefore lands within the first
  ~40 bytes of every payload. Each connection full-parses its first
  payload (and any payload where the scan misses) with a minimal serde
  struct to validate the schema; a scan miss after a clean first parse
  aborts the run per the schema-drift edge case.
- **Rationale**: full JSON parsing of ~100 KB payloads across thousands of
  connections would make the generator the bottleneck it is required to
  detect (FR-011); the prefix scan is O(40 bytes) per update. serde field
  order is declaration order, so the position is stable unless the struct
  changes — which the per-connection validation parse catches.
- **Alternatives considered**: full parse per payload (rejected: generator
  becomes the bottleneck); regex (rejected: heavier than a memchr-style
  scan, same fragility); asking the server for a lighter endpoint
  (rejected: FR-009 forbids server changes).

## R4. Latency distributions

- **Decision**: hand-rolled log-spaced fixed buckets (~30 lines), reporting
  p50/p90/p99 per interval.
- **Rationale**: the stdlib-first house rule; bucket percentiles are
  plenty for a load report, and one less dependency to audit.
- **Alternatives considered**: `hdrhistogram` (rejected: precision beyond
  need, new dependency); storing raw samples (rejected: memory grows with
  viewers × ticks — the exact failure FR-011 exists to avoid).

## R5. The identity stamp (deferred item from clarify)

- **Decision**: at run start, fetch `GET /config` (the server serves its
  active, validated config — `api.rs:91`) and stamp the record with the
  sha256 of the response body plus extracted facts: `tick_ms`, roster
  size, world dimensions; also record the byte size of the first `/world`
  payload as the payload-weight fact of the run.
- **Rationale**: FR-010 needs "world identity as served" without server
  changes; the served config *is* that identity, and hashing the body
  makes drift visible even for fields Clowder doesn't model.
- **Alternatives considered**: a server-side identity endpoint (rejected:
  FR-009); hashing the config *file* (rejected: the tool may not run on
  the server's host — clarify session deferred exactly this, resolved by
  reading everything over the wire).

## R6. File-descriptor headroom detection

- **Decision**: `libc::getrlimit(RLIMIT_NOFILE)` at startup and per
  interval; the record carries the limit, and a run that needs more than
  ~80% of headroom is flagged; EMFILE during a run marks affected
  intervals invalid (FR-011).
- **Rationale**: `libc` is already a transitive dependency; `getrlimit` is
  portable across macOS and Linux, the two platforms in scope.
- **Alternatives considered**: the `rlimit` crate (rejected: wraps one
  syscall); parsing `ulimit -n` output (rejected: shell dependency).

## R7. Record format

- **Decision**: one CSV file per run — `#`-prefixed preamble lines carry
  the identity stamp and full scenario config as `# key: value`; then a
  single header row; interval rows and derived summary rows share the
  schema, distinguished by a `scope` column (`interval` / `step` / `run`).
- **Rationale**: FR-010 says one file; CSV drops into spreadsheets and
  `awk`; the `scope` column keeps one schema across all five modes per the
  clarify decision.
- **Alternatives considered**: JSON lines (rejected: worse for the
  spreadsheet/plot workflow this exists for); CSV + sidecar meta JSON
  (rejected: FR-010's one-file requirement).

## R8. Slow-consumer mechanics

- **Decision**: a stalled viewer stops reading from its socket entirely
  (after a configurable healthy period), letting kernel buffers fill —
  and its measurements move to the `stalled` class from that moment.
- **Rationale**: a full stall is the strongest test of the server's
  slow-client design (`ws.rs`: a `watch` channel means a slow client
  "skips to the newest world") and of TCP backpressure; SC-006 needs the
  healthy/stalled separation to show bystander harm or its absence.
- **Alternatives considered**: throttled reads (deferred: expressible
  later as a parameter without schema change; the stall is the sharper
  hypothesis).

## R9. The non-local guard

- **Decision**: a target is local iff its host resolves to a loopback
  address (or is `localhost`); anything else requires `--allow-remote`.
  Usage text and README state the live world is never a permitted target.
- **Rationale**: FR-013 wants a default that cannot accidentally point at
  production, without pretending a denylist is enforcement; loopback is
  checkable without DNS games.
- **Alternatives considered**: hostname denylist for the live world
  (rejected: brittle, false confidence — the box has an IP too);
  no guard, documentation only (rejected: FR-013 requires the flag).

## R10. Integration test strategy

- **Decision**: `crates/clowder/tests/smoke.rs` builds/boots the real
  `cloudkitty-server` binary (via `cargo run -p cloudkitty-server` /
  `CARGO_BIN_EXE`-style resolution) with `--config tests/tiny-world.toml
  --fresh`, binding `127.0.0.1:0`, then **reads the chosen port from the
  server's startup log line** (`local_addr()` is logged as
  `http://127.0.0.1:<port>`; there is no address endpoint — verified
  2026-08-12). It runs a seconds-long micro-ramp and asserts: exit code 0,
  record file parses per the contract, and outcome `completed`. Runtime
  budget: under ~10 s so it rides the required CI gate.
- **Rationale**: the tool's entire value is measuring the real server;
  mocking would test nothing (and Article VI wants real guards). The
  server binary is exercised unmodified, preserving FR-009. Port 0 was
  confirmed to bind and log correctly, so the test needs no fixed port.
- **Verified environment facts (2026-08-12)**: (a) the server binds
  `127.0.0.1:0` and logs the concrete port; (b) `tick` is the third field
  of the `/world` payload (`{"width":..,"height":..,"tick":..}`), backing
  R3; (c) the *served* `cloudkitty.toml` seats a policy artifact
  (`policies/e004-a1-s2.ckpolicy`) and therefore FAILS to boot from a bare
  checkout with a missing-artifact error — so `tiny-world.toml` MUST be
  **scripted-only** (no `[rl.policy.*]`, no `behavior = "policy:..."`),
  not merely a smaller world.
- **Assertion scope (revised from "zero skips")**: the smoke test asserts
  exit code, record validity, and `completed` outcome — NOT zero skips. A
  fast test tick on a shared CI runner can drop an update to an ordinary
  scheduler stall, which would flake a zero-skip assertion; skip-behavior
  is exercised deliberately in the slow-consumer path (SC-006), not
  incidentally here. The test world's tick is set to ~200 ms for the same
  reason (fast enough for a seconds-long run, slack enough not to flake).
- **Alternatives considered**: a mock WS server (rejected: tests the mock);
  marking the test `#[ignore]` (rejected: an unexercised tool rots — keep
  it small instead); a fixed port (rejected: port 0 works and avoids
  collisions on shared runners).
