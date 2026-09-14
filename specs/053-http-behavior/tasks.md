# Tasks: HttpBehavior — the remote plugin transport

**Input**: Design documents from `specs/053-http-behavior/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/http-transport.md, quickstart.md

**Tests**: included — the spec's SC bars and house rules 5/6 demand them.
Every new assertion gets a `scripts/mutate.sh --expect <prediction>` cycle
(commit first; `--no-fail-fast` under it; BSD sed `-i ''`). Log each cycle
(prediction → observed) in `specs/053-http-behavior/redden-list.md` (the
049/054 precedent). Rule 6: changed-behavior checks are sorted
(must-go-red vs must-stay-green) before running — T024 is that sort for
the one behavior change to existing code.

**Organization**: by user story; US1 is the MVP increment.

## Phase 1: Setup

**Purpose**: dependencies and the pre-feature baseline SC-004 is measured
against.

- [ ] T001 Capture the pre-feature determinism baseline (016 method):
      fixed seed + config, N ticks, world-state hash from the branch point
      → `specs/053-http-behavior/baseline.txt`; commit it before any code
      change so the Polish post-check diffs against recorded truth.
- [ ] T002 [P] Promote reqwest in `crates/cloudkitty-server/Cargo.toml`:
      move `reqwest = { version = "0.12" }` from `[dev-dependencies]` to
      `[dependencies]` with the `blocking` feature (drop `json` unless a
      test needs it); `cargo check -p cloudkitty-server`.
- [ ] T003 [P] Add `[target.'cfg(unix)'.dependencies] libc = "0.2"` to
      `crates/cloudkitty-core/Cargo.toml` (already in Cargo.lock
      transitively); `cargo check -p cloudkitty-core`.

**Checkpoint**: workspace builds, lockfile settles, baseline banked.

---

## Phase 2: Foundational (blocking all stories)

**Purpose**: the one shared contract parser both transports speak
(research R5) — FR-003's "no dialect" by construction.

- [ ] T004 Create `crates/cloudkitty-core/src/behavior/exchange.rs`: move
      `ReplyEnvelope` (strict, `deny_unknown_fields`) from `script.rs` and
      add `pub fn parse_reply_line(bytes: &[u8], expect_tick: u64,
      expect_kitty: KittyId) -> Result<Action, ReplyRejection>` (envelope
      decode → correlation check → `parse_proposal_value`), with
      `ReplyRejection { BadEnvelope, Desynced{got_tick, got_kitty},
      Rejected }`; re-export from `behavior/mod.rs`.
- [ ] T005 Rewire `ScriptBehavior::exchange` in
      `crates/cloudkitty-core/src/behavior/script.rs` to call
      `parse_reply_line`, mapping `ReplyRejection` onto the existing
      `ExchangeFailure` variants; behavior-preserving — the whole core
      suite and the 016 round-trip tests stay green untouched (rule 6
      must-pass pile: re-read them, don't just run them). Also update the
      `DecisionRequest.config` doc comment: the send-once v2 handshake
      was considered and DEFERRED at this sitting (point at 053
      research.md R10), no longer "noted for the HttpBehavior sitting".
- [ ] T006 Mutate cycle proving the moved code is still guarded: commit
      T004–T005, then `scripts/mutate.sh --expect` (a) invert the
      correlation check in `exchange.rs` → predict the script desync test
      red; (b) drop `deny_unknown_fields` → predict the 016 strict-envelope
      test red. Log both in redden-list.md.

**Checkpoint**: one parser, both future callers; suite green.

---

## Phase 3: User Story 1 — a remote service drives a kitty (P1) 🎯 MVP

**Goal**: `url` + `class` config attaches a remote endpoint as a behavior;
healthy-endpoint proposals are applied and attributed; startup validation
per FR-002/FR-005/FR-015.

**Independent Test**: stub endpoint proposes actions → kitty follows them
with `PolicyMade` provenance; detach the plugin → world byte-identical to
plugin-free.

- [ ] T007 [US1] In `crates/cloudkitty-server/src/lib.rs`: add
      `enum SeatClass { Scripted, Mind }` (serde lowercase) and extend
      `PluginEntry` with `url: Option<String>` and
      `class: Option<SeatClass>`; make `command` `Option<String>`;
      `deny_unknown_fields` stays.
- [ ] T008 [US1] Startup validation in `register_plugin_behaviors`
      (`crates/cloudkitty-server/src/lib.rs`), each error naming the
      entry: exactly one of `command`/`url` (FR-002); `args` nonempty with
      `url`; `url` must parse via `reqwest::Url` with scheme http/https;
      `class` required when `url` set, defaulted `Scripted` when `command`
      set (FR-015); existing command-path checks unchanged; collision rule
      applies to both transports.
- [ ] T009 [US1] Startup-validation unit tests beside the existing ones in
      `crates/cloudkitty-server/src/lib.rs` tests mod: both transports
      declared / neither / args-with-url / relative URL / `ftp://` scheme /
      missing class on url entry / class accepted on command entry /
      url-entry name collision — each asserts the error names the entry.
- [ ] T010 [US1] Create `crates/cloudkitty-server/src/http_behavior.rs`:
      `HttpBehavior { name, url, class, state: Mutex<ExchangeState> }`
      implementing core `Behavior` per data-model.md — lifecycle enum
      `NotSpawned/Running/Dead{since_tick}`; dedicated I/O thread owning
      one `reqwest::blocking::Client` (redirects `Policy::none()`,
      request timeout = `exchange_timeout_ms`); request channel +
      `recv_timeout` authoritative deadline; body read via
      `Read::take(reply_max_bytes + 1)`; **unconditional**
      `ctx.rng.gen_u64()` seed draw before liveness check (Article V —
      copy script.rs's ordering comment); serialize request only after
      liveness settled; replies validated by
      `cloudkitty_core::behavior::parse_reply_line`; `Ok` →
      `Decision::silent`; failures logged with a diagnosable reason
      (`seat_class` arrives via T011's span, not a field here); taint
      table per data-model.md (timeout/oversized/desync tear down +
      `relaunch_cooldown_ticks`; status/refused/garbage don't);
      `decide()` = the same `unreachable!` contract as ScriptBehavior.
- [ ] T011 [US1] Seat-class wrapper (owner ruled option A) + registration
      in `crates/cloudkitty-server/src/lib.rs` (or beside
      `http_behavior.rs`): a wrapper behavior holding
      `(inner: Arc<dyn Behavior>, seat_class)` that enters a
      `tracing` span carrying `seat_class` around the inner `try_decide`
      via `.instrument()` — MUST forward `try_decide` and the
      budget-exemption flag (the `behavior/mod.rs` wrapper-author
      contract; forwarding only `decide` silently turns every plugin
      decision into a fallback). Wrap BOTH transports with it at
      registration in `register_plugin_behaviors`; registration log line
      carries `seat_class`. No class field enters core.
- [ ] T012 [US1] Stub-endpoint test helper in
      `crates/cloudkitty-server/tests/http_plugin.rs`: raw
      `std::net::TcpListener` on 127.0.0.1:0, scripted per-connection
      responses (arbitrary bytes possible); happy path = parse the POSTed
      `DecisionRequest`, echo `tick`/`kitty_id` around a legal proposal.
- [ ] T013 [US1] Happy-path integration tests in `tests/http_plugin.rs`:
      (a) proposals applied with `PolicyMade` provenance over a full
      in-world day of ticks (SC-002); (b) contract parity — byte-compare a
      captured `DecisionRequest` line against the script transport's for
      the same world state, and one reply body accepted identically by
      both (FR-003/US1-AS4); (c) served-surface secrecy — `GET /config`
      and `GET /settings` byte-identical with and without a remote plugin
      declared; no `url`/`class` string in any served byte (SC-005/FR-009).
- [ ] T014 [US1] Mutate cycles (commit first, predictions logged):
      (a) sed the unconditional seed draw behind the liveness check →
      predict the determinism/parity test red; (b) neuter a startup
      validation arm (`if false`) → predict its T009 test red; (c) point
      registration at `ScriptBehavior` for url entries → predict T013(a)
      red at spawn; (d) make the T011 wrapper forward only `decide` (drop
      the `try_decide` forwarding) → predict T013(a) red — dispatch takes
      the crashed-advisor path and no proposal is ever applied.

**Checkpoint**: MVP — a remote brain demonstrably drives a kitty; startup
surface locked.

---

## Phase 4: User Story 2 — a failing endpoint costs one moment of cleverness (P2)

**Goal**: every remote failure mode is a per-tick fallback inside the
standing Article IV stack; recovery automatic; stale replies structurally
discarded.

**Independent Test**: kill the stub mid-run → same-tick fallback, tick
loop uninterrupted; restart stub → cleverness returns unaided.

- [ ] T015 [US2] Hostile-endpoint tests in
      `crates/cloudkitty-server/tests/http_plugin.rs`, one per contract
      table row (contracts/http-transport.md): non-200 status; 3xx
      redirect (not followed); connection refused (unbound port);
      connection reset mid-body; 200 with non-JSON garbage; 200 with a
      wrong-tick/wrong-kitty envelope; body over `reply_max_bytes`; silent
      wedge past `exchange_timeout_ms` — each yields fallback
      (`FallbackTaken` provenance where dispatched), tick completes,
      other kitties' decisions unaffected.
- [ ] T016 [US2] Lifecycle tests in `tests/http_plugin.rs`: (a) taint
      teardown + cooldown — after a timeout, no exchange is attempted for
      `relaunch_cooldown_ticks`, then a fresh thread exchanges again
      (automatic recovery, US2-AS1); (b) late-reply discard — stub answers
      correctly but after the deadline; assert the late bytes are never
      applied to any later tick (fresh channels make them unreadable,
      US2-AS3); (c) clean failures (refused/non-200) do NOT enter cooldown
      — the next decision exchanges immediately (data-model taint table).
- [ ] T017 [US2] SC-003 soak test in `tests/http_plugin.rs`: a hostile
      stub misbehaving every decision for 1,000+ consecutive ticks —
      every tick completes, constitutional invariants assert clean, every
      affected decision recorded as fallback, fallback latency within the
      standing budget from the first affected tick.
- [ ] T018 [US2] Breaker interaction test in `tests/http_plugin.rs`: with
      served-path budget config, repeated remote timeouts bench the kitty
      per `budget_strikes`/`bench_ticks` exactly as a script advisor —
      zero edits to `behavior/mod.rs` (FR-006's "no new code paths" is
      literal; the test only observes).
- [ ] T019 [US2] Mutate cycles: (a) make timeout NOT taint (skip teardown)
      → predict late-reply-discard red; (b) drop the `take` cap → predict
      oversized red; (c) accept any 2xx → predict the non-200 test red;
      (d) follow redirects (Policy default) → predict redirect test red.

**Checkpoint**: US1+US2 = the transport is safe to point at anything.

---

## Phase 5: User Story 3 — docs alone suffice (P3)

**Goal**: one contract, two transports, documented; every example
test-verified (FR-011, 016 FR-015/SC-007 bar).

**Independent Test**: the remote section of `docs/plugins.md` covers
declaration → request → reply → failure semantics → worked example, each
example exercised by a test.

- [ ] T020 [US3] Extend `docs/plugins.md`: remote transport as an
      extension of the one contract — `url`/`class` declaration, POST
      request/response semantics, the failure table, budget/bench
      interaction, worked end-to-end example (stub responder), livelock
      warning pointer; seat-class meaning and the fallback-lineage note
      (fallback rows are scripted rows, excluded from a mind seat's
      lineage — FR-015/FR-016) — extend shared sections, don't duplicate.
      Include the LLM-shaped operator guidance (research R10): one entry
      per kitty for slow advisors (a shared entry serializes exchanges —
      the FR-014 burst); internal harness retries within
      `exchange_timeout_ms` are the endpoint's business, invisible to the
      wire — one request, one reply, and the engine's validation stays
      authoritative; auxiliary model output (e.g. train of thought) is
      logged harness-side and stripped before replying — the strict
      envelope refuses unknown fields by design.
- [ ] T021 [US3] Config reference rows in `docs/plugins.md` (and wherever
      the `[plugins]`/`[behavior]` reference table lives): `url` (no
      default; selects the remote transport), `class` (required for url
      entries; default `scripted` for command entries) — SC-006.
- [ ] T022 [US3] Docs-example verification tests (016 pattern) in
      `crates/cloudkitty-server/tests/http_plugin.rs`: the documented TOML
      declaration parses and registers; the documented request/reply
      example bytes round-trip through `parse_reply_line`; the worked
      example's responder drives a kitty.
- [ ] T023 [US3] Mutate cycle: corrupt the documented example TOML in the
      test fixture (wrong key name) → predict the docs test red for the
      documented reason.

**Checkpoint**: a plugin author needs no engine source.

---

## Phase 6: User Story 4 — script-transport residuals settled (P4)

**Goal**: residual 1 fixed (process-group kill), residual 3 documented
(exec-bit), residual 2 re-accepted with mitigation documented; BACKLOG
entry closes.

**Independent Test**: kill a wedged plugin whose grandchild holds its
stdout → no stranded I/O thread; docs state the exec-bit's real meaning.

- [ ] T024 [US4] Rule-6 sort, recorded in redden-list.md before running:
      must-go-red — the new grandchild test (T025) against today's
      single-`kill()` path; must-stay-green — every existing script.rs
      test and the 016 suite (re-read the pile, then run).
- [ ] T025 [US4] Write the red test first in
      `crates/cloudkitty-core/src/behavior/script.rs` tests:
      `the_kill_ends_the_whole_process_group` — plugin
      `sh -c 'sleep 600 & read line'` (grandchild inherits stdout);
      after `drop(child)`, the reply channel must disconnect promptly
      (bounded wait), proving the pipe closed. Predict and observe RED
      under the current kill path (hand-rolled red with stated reason if
      the failure mode is a hang mutate.sh can't classify — the (e)
      precedent).
- [ ] T026 [US4] Implement in `script.rs`: `CommandExt::process_group(0)`
      on spawn; kill path `libc::killpg(child_pid, SIGKILL)` + reap under
      `cfg(unix)` (non-unix keeps `child.kill()`); update the
      `Drop for PluginChild` comment — the thread frees because the group
      dies and the pipes close, not "a grandchild could hold it open".
      T025 green; whole must-stay-green pile green.
- [ ] T027 [US4] Docs in `docs/plugins.md`: exec-bit check means
      "executable by anyone", not "by the server's user" — a program
      executable only by another user passes startup and fails at spawn
      (FR-013); shared-plugin mutex burst re-accepted with the
      `exchange_timeout_ms` mitigation documented where operators tune
      shared processes (FR-014); update the lifecycle wording per T026.
- [ ] T028 [US4] Close the "ScriptBehavior transport residuals" entry in
      `BACKLOG.md` (all three residuals land/disposition here — spec
      clarification 2026-09-11, owner ruling A).

**Checkpoint**: 016's review ledger is empty.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T029 SC-004 post-check: re-run the T001 baseline command on the
      finished branch → `specs/053-http-behavior/post-check.txt`; hashes
      byte-identical (no plugins configured). Also `cargo test -p
      cloudkitty-core` unchanged-script-transport confirmation.
- [ ] T030 Full gates: `cargo fmt --check`, `cargo clippy --workspace
      --all-targets -- -D warnings` (blocking gate), `cargo test
      --workspace` (SC-001), plus `env PATH=/var/empty`-style hermetic
      sanity if any test shells out.
- [ ] T031 CHANGELOG.md: one-liner under `## Unreleased` (house practice —
      feature marker: server-owned config surface addition, no engine
      semantic, no served-config byte; PR number at merge time).
- [ ] T032 Fresh-eyes review before merge (house pattern, the 371/372
      precedent): adversarial review agent on the full diff; record
      defects + fixes as a PR comment; then CI green and hold for the
      owner's merge word.

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2 → user stories**: T001 must precede any code change
  (baseline honesty); T004–T006 block every story (shared parser).
- **US1 (Phase 3)**: blocks US2/US3 test surfaces (they drive
  `HttpBehavior`); T007→T008→T009; T010 after T004; T011 after T008+T010;
  T012→T013→T014.
- **US2 (Phase 4)**: after US1 checkpoint; T015/T016 share
  `tests/http_plugin.rs` with T012+ (sequential, no [P] across them);
  T017–T018 after T015–T16; T019 last.
- **US3 (Phase 5)**: T020–T021 can start once US1's config surface is
  locked (after T008); T022 needs US1 complete; docs tasks touch
  `docs/plugins.md` — serialize with T027.
- **US4 (Phase 6)**: independent of US1–US3 (core-only + docs); may run
  any time after Phase 2, but T027 serializes on `docs/plugins.md` with
  T020/T021.
- **Polish**: after all stories.

### Parallel opportunities

- T002 ∥ T003 (different Cargo.tomls).
- After Phase 2: US4's core work (T024–T026) ∥ US1's server work
  (T007–T013) — different crates, different files.
- T020/T021 drafting ∥ US2 test work (docs vs tests).

---

## Implementation Strategy

MVP = Phases 1–3 (US1): a remote brain drives a kitty, startup surface
locked, secrecy proven. US2 makes it safe, US3 makes it usable by others,
US4 clears the 016 ledger. Single branch, one PR at the end (house shape);
commit after each task or logical group — mutate.sh refuses dirty files,
so commits gate every rule-5 cycle. Nothing deploys, never tag.
