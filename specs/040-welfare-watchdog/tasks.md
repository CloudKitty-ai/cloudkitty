# Tasks: Serving welfare watchdog

**Input**: spec.md + plan.md (D1–D5). Tests required, red-first (rule 6).

## Phase 1: Setup

- [x] T001 Baseline: `cargo test --workspace --release` green at the
      branch point (040-welfare-watchdog off main e39079e)

## Phase 2: Foundational

- [x] T002 `WatchdogConfig` in crates/cloudkitty-server/src/watchdog.rs:
      `from_toml_str` parsing the `[watchdog]` table alone (mirror
      RlConfig::from_toml_str), defaults threshold=150
      remind_every=150, unknown keys refused. Red-first tests: 0
      refused naming "[watchdog] threshold"/"[watchdog] remind_every"
      and the value; absent table = defaults; unknown key refused

## Phase 3: US1 — the standing watch (P1) 🎯 MVP

- [x] T003 [US1] Red-first alarm tests in watchdog.rs: synthetic
      worlds with hand-set `distress_since` driving a fake tick
      forward — (a) SC-001: a 200-tick streak at threshold 150 yields
      exactly one crossing event (age exactly 150, kitty/need named),
      reminders on cadence, one recovery event with final length;
      (b) below-threshold distress yields zero events; (c) SC-002:
      an F-027-shaped 2331-tick streak fires its crossing at age 150
      and 15 total alarms at defaults; (d) two simultaneous streaks
      are independent events. OBSERVE RED (no Watchdog exists)
- [x] T004 [US1] Implement `Watchdog::observe(&World) ->
      (WelfareStatus, Vec<AlarmEvent>)` per D2/D4/D5; T003 goes
      green. Mutation pass: threshold comparison inverted → (a)
      fails; reminder cadence ignored → (a)'s reminder count fails;
      recovery suppressed → (a)'s recovery assertion fails; each
      reverted, suite green after
- [x] T005 [US1] Wire the serving path in sim_task.rs + main.rs:
      parse WatchdogConfig beside RlConfig, pass into spawn, observe
      after each tick, log events (ERROR crossing/reminder, INFO
      recovery), publish status on a watch channel. FR-006 test:
      seeded run observed-every-tick serializes identically to an
      unobserved run

## Phase 4: US2 — the pollable surface (P2)

- [x] T006 [US2] `GET /welfare` in lib.rs + api.rs serving the latest
      WelfareStatus (entries, threshold, alarm_live). Integration
      test both shapes: healthy world (empty, clear) and distressed
      world (entries present, alarm live) — red-first on the route's
      absence (404 observed before the route exists)

## Phase 5: Polish

- [x] T007 [P] cloudkitty.toml gains the documented `[watchdog]`
      table (threshold = 150, remind_every = 150, comments naming the
      F-027 provenance and the certification bound); CHANGELOG
      Unreleased entry, no markers (server-only, engine provably
      untouched — SC-004 cites the default-serialization assertion
      and the identical-snapshot test)
- [x] T008 Full gate: workspace suite (read the count) + clippy
      clean; verify SC-004's engine-untouched claims: default Config
      serialization test unchanged, zero diffs outside
      cloudkitty-server + toml + docs/spec files

## Deviations (recorded at implementation)

- **FR-004's "engine Config untouched" needed one letter-level
  amendment**: `deny_unknown_fields` means the engine parser must
  RECOGNIZE any new top-level table or the served toml refuses to
  load — a gap in the spec's letter. The `[watchdog]` table joins
  `rl`/`plugins` as a recognized-and-discarded `ForeignTable`
  (zero-sized, `skip_serializing`). The FR's actual obligation holds
  and is verified twice: the foreign-tables-never-serialize test now
  asserts no `watchdog` key, and the default-config serialization
  hashes byte-identical to main (`ab08eb8c…`, the same stamp-input
  check 039 used).
- **T003(a)** ran at streak length 500 rather than 200 so the same
  scenario exercises the reminder cadence (crossing 150, reminders
  300/450, recovery 500); the 200-length claim is subsumed.
- **T006's red** was observed as a JSON-decode failure on the 404
  empty body rather than a bare status check — same absence, noisier
  proof.
