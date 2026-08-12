# Tasks: Clowder — viewer load benchmark

**Input**: Design documents from `/specs/029-clowder/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: included — Article VI (test-guarded) and the spec's own SC/FR
acceptance make them part of the feature, riding the required
`cargo test --workspace` gate.

**Organization**: by user story; US1 (ramp) is the MVP and each later
story is an independent increment on the shared foundation.

## Format: `[ID] [P?] [Story] Description`

All paths are repo-relative; the crate root is `crates/clowder/`.

---

## Phase 1: Setup

**Purpose**: the crate exists, builds empty, and the disposable target
world is committed.

- [ ] T001 Create `crates/clowder/Cargo.toml` (bin crate; deps: workspace `tokio`, `serde`, `serde_json`, `sha2`; new `tokio-tungstenite` with rustls feature; `libc`) and a `src/main.rs` stub that prints usage and exits 1
- [ ] T002 Add `crates/clowder` to the workspace `members` in root `Cargo.toml` (the only edit outside the new crate) and verify `cargo build -p clowder` and `cargo test --workspace` still pass
- [ ] T003 [P] Commit the disposable target world `crates/clowder/tests/tiny-world.toml`: minimum roster (2 kitties), small grid, **scripted-only cats — no `[rl.policy.*]` blocks and no `behavior = "policy:..."` seats** (policy seats resolve artifact paths relative to the working directory — verified 2026-08-12: the served config boots from the repo root but not elsewhere — and a load test should not couple to artifact loading at all), `tick_ms` ≈ 200 (fast enough for a seconds-long run, slack enough not to flake skip counts), loopback `bind = "127.0.0.1:0"` (port 0 confirmed to bind and log the chosen port)

---

## Phase 2: Foundational (blocking all stories)

**Purpose**: one viewer connection measured end to end, the guard rails,
and the record file — everything every mode reuses.

- [ ] T004 [P] Implement `crates/clowder/src/target.rs`: target URL parsing (http→ws derivation), the loopback-only default with `--allow-remote` override (FR-013, research R9), and the identity-stamp fetch — `GET /config` body sha256 + extracted `tick_ms`/roster/dims, first `/world` payload byte length (FR-010, research R5)
- [ ] T005 [P] Implement `crates/clowder/src/scan.rs`: bounded prefix extraction of `"tick":` (research R3), full-parse validation via a minimal serde struct for a connection's first payload, and the scan-miss → schema-drift abort path
- [ ] T006 [P] Implement `crates/clowder/src/metrics.rs`: per-connection atomic counters (updates, skips, bytes, last tick), log-spaced bucket histograms with p50/p90/p99 readout (research R4), the 1 Hz interval sampler emitting `IntervalRow`s per data-model.md (including `gen_lag_ms`), and the **cadence reference connection** (FR-008): designate one healthy connection as the `cadence_ms` source, promote the next healthy viewer when it is lost, and emit the `# note: cadence reference promoted at t=...` line per contracts/record-format.md
- [ ] T007 Implement `crates/clowder/src/viewer.rs` (uses T004/T005/T006): one viewer's lifecycle — first-paint `GET /world`, WS subscribe, read loop feeding metrics, handshake timing split (GET vs upgrade), end-reason classification per data-model.md's `end` enum (FR-001, FR-007)
- [ ] T008 [P] Implement `crates/clowder/src/selfwatch.rs`: `RLIMIT_NOFILE` via libc at startup and per interval, 80%-headroom flagging, EMFILE and sampler-lag invalidation of intervals (FR-011, research R6)
- [ ] T009 [P] Implement `crates/clowder/src/record.rs` per contracts/record-format.md: `#` preamble writer (identity, scenario, thresholds with non-default marking), header row, interval/step/run rows with the `scope` column, end-of-run `# outcome:` / `# classification:` lines (FR-010)
- [ ] T010 Implement `crates/clowder/src/main.rs` CLI per contracts/cli.md: subcommand + flag parsing with defaults, startup rejection naming flag/value/range (spec edge case), exit codes 0/1/2/3 (FR-014), and the usage-text obligations including the never-the-live-world sentence (FR-013)
- [ ] T011 [P] Unit tests `crates/clowder/src/scan.rs` (in-module `#[cfg(test)]`): tick extraction against a real serialized `WorldSnapshot` JSON sample, scan-miss abort, first-payload validation
- [ ] T012 [P] Unit tests for `target.rs` (loopback vs non-local vs `--allow-remote`) and `record.rs` (preamble round-trip, every row has every column, summaries recomputable from interval rows)

**Checkpoint**: `cargo test -p clowder` green; a hand-run single viewer
against a local server prints ticks arriving.

---

## Phase 3: User Story 1 — Find the ceiling (P1, MVP)

**Goal**: one unattended ramp answers "how many viewers on this hardware,"
with the curve and the first-degraded measure.

**Independent test**: quickstart §3 — `clowder ramp --to 2000 --step 50
--hold 20` against the tiny world completes unattended and reports either
"reached healthy" or last-healthy/first-degraded with the failing measure;
same conclusion recoverable from the record's `scope=step` rows.

- [ ] T013 [US1] Implement the ramp scheduler in `crates/clowder/src/modes.rs`: step/step-interval/hold schedule, per-step viewer cohort management, stop-on-unhealthy-step (FR-002)
- [ ] T014 [US1] Implement `crates/clowder/src/health.rs`: FR-016 step-health evaluation over valid interval rows (zero skips among healthy class, cadence within tolerance, zero handshake failures, zero unexpected ends, whole-hold sustainment), `first_degraded_measure`, and the ceiling determination
- [ ] T015 [US1] Implement degradation classification (FR-012) in `crates/clowder/src/health.rs`: the closed signature enum from data-model.md, mapped from step/run evidence, `generator_bottleneck` overriding attribution (FR-011)
- [ ] T016 [US1] Wire ramp end-to-end in `crates/clowder/src/main.rs` + `record.rs`: `scope=step`/`scope=run` summary rows derived from interval rows, human summary naming ceiling and first-degraded measure, stderr per-step progress
- [ ] T017 [P] [US1] Unit tests for `health.rs`: healthy/unhealthy step tables across each FR-016 threshold, non-default threshold marking, classification mapping including generator-bottleneck override
- [ ] T018 [US1] Integration test `crates/clowder/tests/smoke.rs` (research R10): boot the real `cloudkitty-server` with `--config tests/tiny-world.toml --fresh` binding `127.0.0.1:0`, **read the chosen port from the server's startup log line** (no address endpoint exists), run a micro-ramp (e.g. `--to 20 --step 10 --hold 2`), and assert exit 0, record parses per contract, and outcome `completed` — **not** zero skips (a fast tick on a shared runner can drop an update to a scheduler stall; skip behavior is exercised in the slow-consumer path, not here). Budget ≤ 10 s
- [ ] T019 [US1] Interrupted-target behavior (quickstart §6): detect tick-number reset and socket loss as target failure, exit 3, `# outcome: interrupted`, rows preserved and valid (edge case + FR-014); covered in `smoke.rs` by killing the server mid-hold

**Checkpoint**: MVP — quickstart §§1–3 work as written.

---

## Phase 4: User Story 2 — Characterize the failure (P2)

**Goal**: spike, slow-consumer, churn, and the poller mix each probe their
hypothesis and report on the shared schema.

**Independent test**: quickstart §4 — all four commands complete against
the tiny world with mode-appropriate reports (handshake distribution +
failed count; healthy/stalled separation; setup-cost-over-time; poller
columns beside viewer measures).

- [ ] T020 [P] [US2] Implement spike mode in `crates/clowder/src/modes.rs`: connections issued as fast as the generator allows, observation window, failed-establishment counting (FR-003)
- [ ] T021 [P] [US2] Implement slow-consumer mode in `crates/clowder/src/modes.rs` + `viewer.rs`: stall selection at `--stall-fraction`, read stop at `--stall-after`, `viewer → stalled` class transition with pre-stall measurements staying in the healthy class (FR-004, research R8, SC-006)
- [ ] T022 [P] [US2] Implement churn mode in `crates/clowder/src/modes.rs`: steady-state N with `--churn-rate` arrivals/departures, every arrival paying the real first-paint cost (FR-005)
- [ ] T023 [US2] Implement the poller mix in `crates/clowder/src/modes.rs` + a small `poller` path in `viewer.rs`: `--poll-rate` across `--poll-endpoints`, latency/error columns, composable with every mode (FR-006)
- [ ] T024 [US2] Per-mode human-summary specifics in `main.rs`: spike handshake distribution, slow-consumer healthy-vs-stalled verdict (SC-006 stated explicitly, including the refutation case), churn setup-cost trend, poller latency table
- [ ] T025 [P] [US2] Extend `crates/clowder/tests/smoke.rs`: one short run per mode against the tiny world asserting record validity, expected populated columns, and clean exit — keep the whole file inside the CI budget by using seconds-scale durations

**Checkpoint**: all five traffic shapes runnable; SC-002's "no unclassified
failure" holds across them.

---

## Phase 5: User Story 3 — Compare across versions (P3)

**Goal**: records are comparable artifacts — identity-stamped, repeatable,
self-describing.

**Independent test**: quickstart §2 twice — two records of the same
scenario carry identical identity stamps (modulo timestamp) and agree on
outcome; editing the world config visibly changes `config_sha256`.

- [ ] T026 [P] [US3] Complete stamp coverage in `record.rs` + `target.rs`: tool version + git describe when available, `nofile_limit`, effective-scenario echo (every flag, one per line), non-default FR-016 thresholds marked `(non-default)` per contract
- [ ] T027 [P] [US3] Repeatability support in `main.rs`: the `--repeat <n>` flag (contracts/cli.md common flags) that runs the scenario n times into `-1`/`-2`/… suffixed records and prints the ceiling agreement check against SC-003's ±10% tolerance
- [ ] T028 [US3] Unit test for preamble/schema stability in `crates/clowder/src/record.rs` tests: unknown-`#`-key tolerance documented by test, column list asserted against the contract's schema v1 (append-only guard)

**Checkpoint**: SC-003 measurable with one command; records self-describe.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T029 [P] Run quickstart §§1–7 end to end as written against a local server and fix any drift between the doc and the tool (per the run-for-real doc rule); record actual smoke numbers in quickstart expected-output notes if they differ
- [ ] T030 [P] Add the one-line `crates/clowder` entry to the repo `README.md` Layout block and a `## Unreleased` line to `CHANGELOG.md` (public-voice applies to both)
- [ ] T031 Verify SC-004 mechanically: `git diff origin/main --stat -- crates/ ':!crates/clowder'` is empty; `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, full `cargo test --workspace` green
- [ ] T032 Confirm FR/SC coverage against spec.md checklist-style (each FR-001..FR-016 and SC-001..SC-006 mapped to code or test) and note any deliberate deviations in plan.md

---

## Dependencies

- Phase 1 → Phase 2 → US1 (T013–T019) — strictly ordered.
- US2 (T020–T025) depends on Phase 2 + T014/T015 (health + classification); not on the rest of US1.
- US3 (T026–T028) depends on Phase 2 only; can run parallel to US2.
- Phase 6 last.

Within phases, `[P]` tasks touch disjoint files and can proceed together;
unmarked tasks integrate prior work (`viewer.rs` after target/scan/metrics;
`main.rs` wiring after the parts it wires).

## Parallel execution examples

- Phase 2: T004, T005, T006, T008, T009 in parallel; then T007, then T010; T011/T012 alongside T010.
- US2: T020, T021, T022 in parallel after T014/T015; T023 after T020–T022 land in `modes.rs` (same file — sequential with them if one worker).
- US3 can start (T026/T027 in parallel) while US2 is in flight.

## Implementation strategy

MVP first: Phases 1–3 deliver the tool that answers the motivating
question (a ceiling with a curve, honestly invalidated when the generator
is at fault). US2 adds the failure characterization shapes, US3 the
comparability conveniences; each checkpoint is independently
demonstrable via its quickstart section.
