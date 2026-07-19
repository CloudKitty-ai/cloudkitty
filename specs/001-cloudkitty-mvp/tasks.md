# Tasks: CloudKitty MVP

**Input**: Design documents from `/specs/001-cloudkitty-mvp/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED — the constitution (Article VI) mandates test-guarded development
and a property-test CI gate; the spec's SC-002 makes the invariant suite a required
merge gate. Write each phase's tests first and watch them fail before implementing.

**Organization**: Tasks are grouped by user story (spec.md priorities). The simulation
domain lives in Phase 2 (Foundational) because every story exercises it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 Living World · US2 Safety · US3 Personalities · US4 Restart ·
  US5 Configuration · US6 Greebles

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Cargo workspace skeleton, dependencies, CI gate scaffold

- [X] T001 Create Cargo workspace: root `Cargo.toml` (members `crates/*`), empty
      `crates/cloudkitty-core/src/lib.rs`, `crates/cloudkitty-server/src/main.rs`,
      `client/` directory; `cargo build` succeeds
- [X] T002 [P] Declare core dependencies in `crates/cloudkitty-core/Cargo.toml`
      (serde, serde_json, rand, rand_chacha +serde, async-trait, thiserror,
      tokio [time, macros — for decision timeout], futures; dev: proptest,
      tokio [rt, test-util])
- [X] T003 [P] Declare server dependencies in `crates/cloudkitty-server/Cargo.toml`
      (axum +ws, tokio [full], tower-http [fs, cors], serde, serde_json, toml,
      anyhow, tracing, tracing-subscriber; dev: reqwest or hyper client,
      tokio-tungstenite)
- [X] T004 [P] Add CI workflow `.github/workflows/ci.yml`: `cargo fmt --check`,
      `cargo clippy --workspace -- -D warnings`, `cargo test --workspace` on
      push/PR to main (Article VI required gate; research.md R12)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The pure simulation domain in `cloudkitty-core` — every user story
drives this code. Data shapes per data-model.md.

**⚠️ CRITICAL**: No user story phase can begin until this phase is complete.

- [X] T005 [P] Implement `crates/cloudkitty-core/src/grid.rs`: `Position`,
      `Direction (N|E|S|W)`, bounds checks, Chebyshev adjacency (`dist ≤ 1`)
- [X] T006 [P] Implement `crates/cloudkitty-core/src/needs.rs`: `Need` newtype
      clamped to [0,100] on all mutation, `NeedKind` (eat, drink, sleep, play,
      cuddle, bath), per-need rise rates, happiness = 100 − weighted avg with
      configurable weights and floor (default 5)
- [X] T007 [P] Implement `crates/cloudkitty-core/src/rng.rs`: `ChaCha8Rng` wrapper
      seeded from config, serde-serializable, per-kitty per-tick decision streams
      derived in stable kitty-id order (research.md R4)
- [X] T008 Write failing unit tests (`#[cfg(test)]` in each module) for need
      math/clamping, happiness weighting + floor, adjacency, RNG stream
      determinism — commit failing, then make T005–T007 pass (Article VI order)
- [X] T009 [P] Implement `crates/cloudkitty-core/src/element.rs`: `Element`,
      `ElementKind` (water, chow+servings, bug, greeble, sunbeam), TTL expiry,
      bug movement (1 tile / 2 ticks random), greeble movement (1–2 tiles/tick,
      ~60% direction change), defaults per research.md R11
- [X] T010 [P] Implement `crates/cloudkitty-core/src/kitty.rs`: `Kitty` (id, name,
      pos, needs, happiness, `Activity` state machine idle/resting/sleeping with
      context, behavior name, meow cooldowns, `in_distress` set); **no removal or
      health API exists on this type** (Article II)
- [X] T011 [P] Implement `crates/cloudkitty-core/src/meow.rs`: `MessageKind` (6
      kinds), `Meow`, per-kitty per-kind cooldown (15 ticks; 5 while related need
      ≥ 75; FollowMe/Purr flat 15), silently-dropped-but-turn-consumed semantics
- [X] T012 [P] Implement `crates/cloudkitty-core/src/events.rs`: `DistressEvent`,
      edge-triggered recording (crossing ≥ 90 only, re-armed below), bounded
      retention (default 1,000)
- [X] T013 Implement `crates/cloudkitty-core/src/config.rs`: TOML-shaped serde
      structs + `validate()` → typed config; enforce ≥2 kitties, unique ids,
      on-grid non-duplicate positions, element min/max within hard bounds (min 1,
      greebles 0; max `floor(area/32)`), min ≤ max, safeguard < distress, budget
      fraction < 1 tick, weights sum to 1, world large enough; errors name field,
      value, allowed range (`thiserror`)
- [X] T014 Implement `crates/cloudkitty-core/src/action.rs`: `Action` enum +
      `TargetRef`, validation table (legality per world state; blocked/illegal →
      `Idle`), application effects (eat −40 +serving consumption, drink −40,
      sleep −5/−8 sunbeam, groom −30 bath + cuddle transfer, play −25 both
      kitties, rest/co-activity cuddle effects, purr gating happiness > 70 or
      rose, meow via T011) — all magnitudes from config
- [X] T015 Implement `crates/cloudkitty-core/src/behavior/mod.rs`: `Behavior`
      trait (`async fn decide`, `is_builtin`), read-only `DecisionContext` (me,
      snapshot, per-kitty rng, constants), name→behavior registry (unknown name =
      config error), concurrent gather via `join_all` with
      `tokio::time::timeout` on non-builtins only + `NeedsDriven` fallback on
      timeout/panic (contracts/behavior.md)
- [X] T016 Implement `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      built-in fallback strategy — target highest-pressure need, move-toward then
      satisfy, mild ctx-RNG randomness; total over all context states
- [X] T017 [P] Implement `crates/cloudkitty-core/src/spawn.rs`: spawn-to-minimum
      at random element-unoccupied tiles, deferred-when-full, safeguard spawning
      (eat→chow, drink→water) ignoring maximums (Article I)
- [X] T018 [P] Implement `crates/cloudkitty-core/src/invariants.rs`:
      `check_invariants(&World)` asserting population ≥ 2, needs bounds,
      happiness ≥ floor, positions in-bounds/non-overlapping, safeguard
      obligations met (panics in debug/test; tracing error in release)
- [X] T019 Implement `crates/cloudkitty-core/src/world.rs`: `World` aggregate,
      generation from config, and `tick()` executing the five fixed phases —
      snapshot+decide → apply in kitty-id order → environment phase → needs
      rise/happiness/distress/invariants → return published snapshot (FR-003);
      wire-form `WorldSnapshot` view omitting RNG state
- [X] T020 Write failing unit tests then make T009–T019 pass: action validation
      matrix, cooldown scaling, expiry/spawn-to-minimum, edge-triggered distress,
      config validation error catalogue, tick phase ordering (in-module
      `#[cfg(test)]` blocks)

**Checkpoint**: `cargo test -p cloudkitty-core` green; a headless world ticks
deterministically.

---

## Phase 3: User Story 1 — Watch a Living Kitty World (Priority: P1) 🎯 MVP

**Goal**: `cargo run` starts the server; the browser shows ≥2 kitties living their
lives (move/eat/drink/sleep/play/groom/meow/purr) with cute rendering.

**Independent Test**: Start server, open viewer, observe per quickstart.md V1;
server integration test passes.

### Tests for User Story 1 (write first, watch fail)

- [X] T021 [P] [US1] Server integration test in
      `crates/cloudkitty-server/tests/server_integration.rs`: boot on ephemeral
      port with test config, `GET /world` → 200 + parses, open `/ws`, receive ≥2
      frames with strictly increasing `tick`, `GET /kitties/{unknown}` → 404
      error shape (contracts/http-api.md)

### Implementation for User Story 1

- [X] T022 [US1] Implement `crates/cloudkitty-server/src/sim_task.rs`: single
      owner of `World`; `tokio::time::interval` at configured tick_ms with
      `MissedTickBehavior::Delay`; publishes `Arc<WorldSnapshot>` via
      `tokio::sync::watch` after every tick
- [X] T023 [P] [US1] Implement `crates/cloudkitty-server/src/api.rs`: `GET
      /world`, `GET /kitties`, `GET /kitties/{id}` (404 shape) reading the watch
      channel's latest snapshot; serde wire shapes per contracts/http-api.md
- [X] T024 [P] [US1] Implement `crates/cloudkitty-server/src/ws.rs`: `/ws`
      upgrade; forward each watch update as a text frame (same JSON as /world);
      ignore inbound messages; drop cleanly on disconnect
- [X] T025 [US1] Implement `crates/cloudkitty-server/src/main.rs`: CLI
      (`--config`, default `cloudkitty.toml`), tracing-subscriber init, config
      load/validate (human-friendly error + non-zero exit via anyhow), spawn sim
      task, axum router (api + ws + tower-http `ServeDir` for `client/`, CORS),
      bind default `127.0.0.1:8090`
- [X] T026 [P] [US1] Create `client/index.html`: canvas, minimal soft-styled
      layout, kitty status panel, script tags (no build step)
- [X] T027 [P] [US1] Implement `client/app.js`: fetch `GET /world` once →
      connect `/ws` → re-render each frame; reconnect with snapshot re-fetch on
      drop
- [X] T028 [US1] Implement `client/render.js`: canvas tile grid, emoji/simple
      shapes for kitties + water/chow/bug/sunbeam, meow speech bubbles, ZZZ
      overlay while sleeping, hearts while cuddling, per-kitty happiness
      indicator; soft colors, rounded look
- [X] T029 [US1] Ship commented default `cloudkitty.toml` at repo root: 32×32,
      800 ms tick, seed, 3-kitty roster (mixed behaviors), element rules and all
      constants with research.md R11 defaults — documented with comments
      (Article VI)

**Checkpoint**: quickstart.md V1 passes — the MVP is watchable. T021 green.

---

## Phase 4: User Story 2 — Kitties Are Always Safe (Priority: P1)

**Goal**: The constitution's Articles I–III are enforced at runtime and guarded by
the property-test CI gate.

**Independent Test**: `cargo test -p cloudkitty-core --test invariants_proptest`
(quickstart.md V2).

### Tests for User Story 2 (the story IS its tests — write first)

- [X] T030 [P] [US2] Add test-only adversarial behaviors in
      `crates/cloudkitty-core/src/behavior/test_behaviors.rs` (cfg(test)/
      feature-gated): `always_invalid` (illegal proposals every tick), `chaos`
      (random possibly-illegal actions from ctx.rng)
- [X] T031 [US2] Write proptest invariant suite in
      `crates/cloudkitty-core/tests/invariants_proptest.rs`: strategies for
      random valid configs (sizes, rosters 2–8, element rules within hard
      bounds) and random behavior assignment (incl. adversarial); drive ≥10,000
      ticks headless; assert every tick: no kitty removed, population ≥ 2, needs
      ∈ [0,100], happiness ≥ floor, safeguard guarantee, edge-triggered distress
      (SC-002)

### Implementation for User Story 2

- [X] T032 [US2] Fix everything the property suite finds in
      `crates/cloudkitty-core/src/` until the 10,000-tick suite is green (this
      task is done only when T031 passes repeatedly)
- [X] T033 [P] [US2] Add `GET /events/distress` endpoint in
      `crates/cloudkitty-server/src/api.rs` returning bounded recent events
      (contracts/http-api.md) + integration assertion in
      `crates/cloudkitty-server/tests/server_integration.rs`

**Checkpoint**: The CI gate protects Articles I–III from here on.

---

## Phase 5: User Story 3 — Different Kitties, Different Personalities (Priority: P2)

**Goal**: Per-kitty pluggable behaviors observably differ; the engine survives
hostile/slow behaviors (Article IV machinery proven).

**Independent Test**: Behavior-variation test comparing 1,000-tick action
histories; timeout/fallback tests (quickstart.md V3).

### Tests for User Story 3 (write first)

- [X] T034 [P] [US3] Write failing behavior tests in
      `crates/cloudkitty-core/src/behavior/mod.rs` tests +
      `test_behaviors.rs`: add `sleepy_slow` (sleeps past budget) and
      `panicky` test behaviors; assert timeout → NeedsDriven substitution, panic
      → fallback without crash, tick cadence unaffected, invalid → Idle
      (contracts/behavior.md tests 2–4)
- [X] T035 [P] [US3] Write failing variation test in
      `crates/cloudkitty-core/tests/behavior_variation.rs`: same world, kitty A
      `needs_driven` vs kitty B `playful`, 1,000 ticks → B's play+chase count ≥
      1.5× A's (SC-005)

### Implementation for User Story 3

- [X] T036 [US3] Implement `crates/cloudkitty-core/src/behavior/playful.rs`:
      over-weights Play/Chase targets (bugs, greebles, friends), reverts to
      needs-driven choices at extreme need pressure; deterministic given ctx
- [X] T037 [US3] Harden the timeout/fallback path in
      `crates/cloudkitty-core/src/behavior/mod.rs` until T034 passes (panic
      catching via spawned task join, budget from config, builtin exemption)

**Checkpoint**: Two kitties visibly live different lives; hostile behaviors can't
hurt anyone.

---

## Phase 6: User Story 4 — The World Survives a Restart (Priority: P2)

**Goal**: Snapshot persistence with RNG state; determinism across restarts;
`--fresh` escape hatch.

**Independent Test**: quickstart.md V4/V5 — stop/restart resumes identically;
determinism tests green.

### Tests for User Story 4 (write first)

- [X] T038 [P] [US4] Write failing determinism tests in
      `crates/cloudkitty-core/tests/determinism.rs`: (a) same seed+config, two
      worlds, N ticks → identical serialized state (SC-004); (b) serialize at
      tick k, deserialize, continue to N → equals uninterrupted run (SC-003)
- [X] T039 [P] [US4] Write failing persistence tests in
      `crates/cloudkitty-server/src/persist.rs` test module: atomic write leaves
      no torn file (tmp+rename), load-validate rejects invariant-violating and
      config-incompatible snapshots with clear errors

### Implementation for User Story 4

- [X] T040 [US4] Implement `crates/cloudkitty-server/src/persist.rs`: serialize
      full `World` (RNG state included) to `snapshot.json` via temp-file+rename;
      load-and-validate (constitution invariants + config fingerprint); typed
      errors surfaced human-friendly
- [X] T041 [US4] Wire persistence into
      `crates/cloudkitty-server/src/sim_task.rs` and `main.rs`: save every N
      ticks (default 100), `tokio::signal::ctrl_c` → final save then exit;
      boot order = `--fresh` ? generate : (snapshot exists ? load-validate-or-
      die : generate); add `--fresh` and `--snapshot <path>` CLI flags

**Checkpoint**: Ctrl-C and restart resumes the same world; `--fresh` starts anew.

---

## Phase 7: User Story 5 — Shape the World Through Configuration (Priority: P3)

**Goal**: Every constant tunable via `cloudkitty.toml`; every invalid config
rejected with a named-field error.

**Independent Test**: quickstart.md V6 — bad configs exit non-zero with actionable
messages; valid edits change the simulation.

### Tests for User Story 5 (write first)

- [X] T042 [P] [US5] Write failing config rejection tests in
      `crates/cloudkitty-core/src/config.rs` test module covering the full
      FR-007 catalogue: <2 kitties, duplicate ids/positions, off-grid, min/max
      outside hard bounds, min > max, safeguard ≥ distress, budget ≥ tick,
      weights not summing to 1, world too small — each asserting the error names
      field, value, and allowed range (SC-006)

### Implementation for User Story 5

- [X] T043 [US5] Polish validation messages in
      `crates/cloudkitty-core/src/config.rs` until T042 passes verbatim; ensure
      `main.rs` prints them without backtrace noise and exits non-zero
- [X] T044 [P] [US5] Add `GET /config` endpoint in
      `crates/cloudkitty-server/src/api.rs` returning the active validated
      config (contracts/http-api.md) + integration assertion

**Checkpoint**: Operators can safely tune everything; the constitution is
unbreakable via config.

---

## Phase 8: User Story 6 — The Greeble Mystery (Priority: P3)

**Goal**: Greebles in every payload, never rendered by default, revealed by `g`.

**Independent Test**: quickstart.md V7 — `curl /world | grep greeble` hits; viewer
shows kitties chasing nothing; `g` reveals.

### Tests for User Story 6 (write first)

- [X] T045 [P] [US6] Extend
      `crates/cloudkitty-server/tests/server_integration.rs`: test config forces
      ≥1 greeble; assert `GET /world` payload and a WS frame contain
      `"kind":"greeble"` (SC-007 API half)

### Implementation for User Story 6

- [X] T046 [US6] Implement greeble render-skip + debug toggle in
      `client/render.js` and keybinding in `client/app.js`: greebles never drawn
      by default; `g` keypress toggles debug rendering (distinct ghost style);
      toggle state shown subtly in the UI

**Checkpoint**: Kitties visibly chase "nothing"; all six stories complete.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T047 [P] Update `README.md`: what CloudKitty is, quickstart (run/fresh/
      config), API summary, link to constitution and spec
- [X] T048 [P] Add tracing spans/events across
      `crates/cloudkitty-server/src/` (tick timing, save/load, ws
      connect/disconnect) at sensible levels
- [X] T049 Run full quickstart.md validation V1–V8 against a release build; fix
      anything observed; record results in `specs/001-cloudkitty-mvp/quickstart.md`
      checkboxes or notes
- [X] T050 Final `cargo fmt`, `cargo clippy --workspace -- -D warnings`, and a
      cute-pass on `client/` styling (colors, rounded corners, emoji choice)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** → nothing
- **Foundational (Phase 2)** → Setup. **BLOCKS all stories.** Internal order:
  T005–T007 [P] → T008 → T009–T012 [P] + T013 → T014 → T015–T016 → T017–T018 [P]
  → T019 → T020
- **US1 (Phase 3)** → Foundational. T021 first; T022 → T023/T024 [P] → T025;
  T026/T027 [P] → T028; T029 anytime after T013
- **US2 (Phase 4)** → Foundational (not US1 — headless). T030 → T031 → T032; T033
  needs US1's api.rs (T023)
- **US3 (Phase 5)** → Foundational. T034/T035 [P] → T036/T037
- **US4 (Phase 6)** → Foundational + US1's sim_task (T022). T038/T039 [P] →
  T040 → T041
- **US5 (Phase 7)** → Foundational (T013); T044 needs T023. T042 → T043
- **US6 (Phase 8)** → US1 client (T026–T028) + integration test (T021). T045 →
  T046
- **Polish (Phase 9)** → all desired stories

### Story Independence Notes

- US2 runs entirely headless against core — it can proceed in parallel with US1
  (except T033).
- US3, US5 are core-heavy and parallel-friendly with US1's server/client work.
- US4 and US6 touch US1 files (sim_task.rs, render.js) — schedule after US1 or
  coordinate carefully.

### Parallel Example: after Foundational completes

```text
Developer A (US1): T021 → T022 → T023/T024 → T025 → T026–T029
Developer B (US2): T030 → T031 → T032 (headless; no server files)
Developer C (US3): T034/T035 → T036/T037 (core behavior files only)
```

Within Foundational: T005, T006, T007 in parallel; then T009, T010, T011, T012,
T017, T018 in parallel once their prerequisites land.

---

## Implementation Strategy

**MVP first**: Phases 1 → 2 → 3 (US1) → STOP and validate quickstart V1. That's a
demoable kitty world. Then Phase 4 (US2) immediately — the constitution's CI gate
should exist before any further feature work. Then US3 → US4 → US5 → US6
incrementally, validating each story's checkpoint before moving on; Polish last.

**Constitution note**: T004 (CI) lands in Setup so every subsequent merge runs the
growing test suite; the suite becomes the full Article VI gate when T031 lands.
