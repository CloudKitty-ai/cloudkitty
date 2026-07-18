# Implementation Plan: CloudKitty MVP

**Branch**: `001-cloudkitty-mvp` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-cloudkitty-mvp/spec.md`

## Summary

CloudKitty MVP is a server-authoritative, deterministic, tick-based 2D kitty sandbox
with a read-only web viewer. Implementation is a Rust (stable) Cargo workspace: a pure
simulation crate (`cloudkitty-core`) driven headless by tests, an `axum`/`tokio`
server binary (`cloudkitty-server`) exposing REST + WebSocket and serving a
no-build-step vanilla-JS canvas client (`client/`). All randomness flows through one
serializable `ChaCha8Rng`; the world persists as an atomic JSON snapshot including RNG
state; behaviors implement an async trait so future external behaviors drop in without
engine changes, while built-ins run effectively synchronously and are exempt from the
wall-clock budget (spec clarification, 2026-07-18).

## Technical Context

**Language/Version**: Rust, stable toolchain (2021+ edition)

**Primary Dependencies**: `axum` (HTTP + WebSocket), `tokio` (runtime, timers,
signals, watch channel), `tower-http` (static files + CORS), `serde`/`serde_json`
(state + wire format), `toml` (config), `rand` + `rand_chacha` (seeded ChaCha8Rng
with serde), `async-trait` (behavior trait), `thiserror` (core errors), `anyhow`
(server edge), `tracing` + `tracing-subscriber` (logs); `proptest` (dev-only)

**Storage**: single JSON snapshot file (`snapshot.json`, path configurable), written
atomically (temp file + rename); no database

**Testing**: `cargo test` — unit tests in core, `proptest` invariant suite (≥10,000
ticks headless), one server integration test on an ephemeral port

**Target Platform**: any platform with stable Rust + a modern browser (developed on
macOS; server is a single local process)

**Project Type**: web service (Rust workspace backend) + static single-page viewer

**Performance Goals**: tick work completes comfortably inside the 800 ms default tick
at default scale (32×32, small kitty roster); property suite runs 10,000+ ticks
headless at zero tick delay in seconds, not minutes; WS pushes full snapshots every
tick to a handful of local viewers

**Constraints**: same-seed determinism for built-in behaviors (single RNG, stable
kitty-id ordering, no wall-clock in sim logic); external-behavior time budget default
= 50% of tick (400 ms), always validated < tick duration; snapshot writes must never
tear (atomic rename); viewer is read-only (no simulation logic client-side)

**Scale/Scope**: one world per server process; default 32×32 grid; roster of 2–~10
kitties; local/trusted-network viewers only, unauthenticated read-only API

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Plan compliance |
|---------|------|-----------------|
| I — Kitties Cannot Suffer | Needs bounded 0–100; distress events (edge-triggered) as signal only; safeguard spawning; happiness floor | `Need` type clamps on every mutation; `check_invariants()` asserts bounds each tick; safeguard resolution in environment phase ignores maximums; distress events recorded on threshold crossing only. Covered by unit + proptest suites. **PASS** |
| II — Kitties Cannot Die | No removal code path; expiry only for elements | `World::kitties` exposes no removal API; expiry logic lives on `Element` only; population asserted every tick. Structural + property tests. **PASS** |
| III — Kitties Cannot Be Alone | ≥2 kitties always; config rejection + per-tick assertion | Config validation rejects rosters < 2 at startup with a clear error; `check_invariants()` re-asserts every tick. **PASS** |
| IV — Engine Is the Law | Behaviors propose; engine validates; invalid/late/absent → idle; time budget + fallback | `Behavior` trait returns proposals only; `validate_action()` gates every proposal (invalid → `Idle`); `tokio::time::timeout` wraps external decisions with `NeedsDriven` fallback; built-ins exempt per spec clarification. **PASS** |
| V — Server-Authoritative, Deterministic | All logic server-side; client pure view; same seed → same world; fixed tick order | Client renders pushed snapshots only; one `ChaCha8Rng` (serialized into snapshots); per-kitty decision randomness handed via `DecisionContext` (order-independent); tick phases fixed in `World::tick()`. **PASS** |
| VI — Spec-First, Test-Guarded | Property tests over Articles I–III as CI gate; constants in config with documented defaults | proptest suite (randomized configs + adversarial behaviors, ≥10,000 ticks) wired as required CI gate; every constant lives in `SimConstants` config structs with commented defaults in `cloudkitty.toml`. **PASS** |

**Initial gate result: PASS (no violations, Complexity Tracking not required).**

**Post-design re-check (after Phase 1)**: data model keeps needs as clamped types,
gives kitties no lifecycle states, models expiry only on elements, and the contracts
expose read-only endpoints (greebles included in payloads). Behavior contract is
proposal-only. **PASS.**

## Project Structure

### Documentation (this feature)

```text
specs/001-cloudkitty-mvp/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── http-api.md      # REST + WebSocket wire contract
│   └── behavior.md      # Behavior trait / decision-context contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
Cargo.toml                     # workspace root (members: crates/*)
cloudkitty.toml                # commented default config
crates/
├── cloudkitty-core/           # pure simulation, headless-usable
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── config.rs          # config structs + validation (hard bounds, ≥2 kitties…)
│   │   ├── world.rs           # World, tick loop phases, snapshot (de)serialization
│   │   ├── grid.rs            # Position, adjacency (Chebyshev), bounds
│   │   ├── element.rs         # Water/Chow/Bug/Greeble/Sunbeam, expiry, movement
│   │   ├── kitty.rs           # Kitty, needs, happiness, activity state
│   │   ├── needs.rs           # Need type (clamped 0–100), rates, weights
│   │   ├── action.rs          # Action enum, validation, application effects
│   │   ├── meow.rs            # messages, per-kitty per-type cooldowns
│   │   ├── behavior/
│   │   │   ├── mod.rs         # Behavior trait, DecisionContext, registry, fallback
│   │   │   ├── needs_driven.rs
│   │   │   └── playful.rs
│   │   ├── events.rs          # distress events (edge-triggered), bounded retention
│   │   ├── spawn.rs           # spawn-to-minimum, safeguard spawning
│   │   ├── invariants.rs      # per-tick constitution assertions
│   │   └── rng.rs             # seeded ChaCha8Rng wrapper, per-kitty decision streams
│   └── tests/
│       └── invariants_proptest.rs   # Articles I–III property suite (≥10,000 ticks)
├── cloudkitty-server/
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs            # CLI (--fresh, --config), boot, shutdown handling
│   │   ├── sim_task.rs        # owns World; interval loop; watch publisher; snapshots
│   │   ├── api.rs             # GET /world /kitties /kitties/{id} /events/distress /config
│   │   ├── ws.rs              # /ws upgrade; forwards each watch update
│   │   └── persist.rs         # atomic snapshot.json write / load-and-validate
│   └── tests/
│       └── server_integration.rs    # ephemeral port; GET /world (greebles!); 2 WS frames
client/
├── index.html
├── app.js                     # fetch /world once → subscribe /ws → render
└── render.js                  # canvas renderer; cute style; greeble skip + `g` toggle
```

**Structure Decision**: Cargo workspace with two crates plus a static client
directory. `cloudkitty-core` is pure simulation with no HTTP/async-runtime
dependencies beyond `async-trait` for the behavior trait and serde derives — the
proptest suite drives it headless at zero tick delay. `cloudkitty-server` is the only
binary; it owns I/O concerns (config file, HTTP, WS, static files, snapshots,
signals). `client/` has no build step and is served by `tower-http`'s static-file
service.

## Design Decisions (from user input, binding for implementation)

1. **Behavior trait**: `#[async_trait] pub trait Behavior: Send + Sync { async fn
   decide(&self, ctx: &DecisionContext) -> Action; }`. Built-ins (`NeedsDriven`,
   `Playful`) resolve immediately; the async signature exists so future
   `ScriptBehavior`/`HttpBehavior`/local-service implementations drop in without
   engine changes. The engine gathers all decisions concurrently (`join_all`) against
   the start-of-tick snapshot. External decisions are wrapped in
   `tokio::time::timeout` (default budget 400 ms = 50% of tick, configurable,
   validated < tick duration) and substituted with the `NeedsDriven` decision on
   timeout, panic, or invalid action; built-ins are exempt from the wall-clock budget
   (determinism by construction). Every proposal is validated before application;
   invalid → `Idle`.
2. **Simulation ownership**: a single sim task owns the `World` (no shared mutable
   state). After every tick it publishes an `Arc<WorldSnapshot>` via
   `tokio::sync::watch`; REST handlers read the latest snapshot, WS handlers forward
   each new one. Client-bound serialization is the full snapshot, greebles included —
   invisibility is purely a client rendering rule.
3. **Persistence**: sim task serializes the `World` to `snapshot.json`
   (`serde_json`) every N ticks (default 100) and on graceful shutdown
   (`tokio::signal::ctrl_c` triggers a final save). Writes are atomic: temp file then
   rename — never a torn snapshot. On boot: load-and-validate if present (validation
   failure → clear error, non-zero exit; never silently discard), else generate from
   config; `--fresh` skips loading. RNG state persists via `rand_chacha`'s serde
   feature.
4. **Determinism**: all randomness through one `rand_chacha::ChaCha8Rng` seeded from
   config; stable kitty-id ordering for action application. Built-in behaviors draw
   randomness only from RNG state handed to them in the `DecisionContext` (per-kitty
   streams derived before decisions run, so concurrency and completion order cannot
   affect outcomes).
5. **Config**: single `cloudkitty.toml` parsed with `serde` + `toml` into validated
   config structs. Validation enforces the constitution and spec: ≥2 kitties, element
   min/max within hard bounds (min 1 — greebles may be 0; max `floor(area/32)`),
   safeguard threshold < distress threshold, behavior budget < tick duration,
   positions on-grid and non-duplicate, world large enough. Ship a commented default
   config.
6. **Time**: tick loop uses `tokio::time::interval` at the configured rate (default
   800 ms) with `MissedTickBehavior::Delay`. Core exposes a direct `tick()` so tests
   run headless with zero delay.
7. **Errors**: `thiserror` in core, `anyhow` at the server edge. Config/snapshot
   validation failures print human-friendly messages and exit non-zero.
8. **Client**: one `index.html` + vanilla JS + `<canvas>`; fetch `GET /world` once,
   subscribe to `/ws`, re-render each pushed state. Renderer skips greebles; `g`
   toggles debug-rendering them. Cute: soft colors, rounded look, emoji/simple-shape
   sprites, meow speech bubbles, ZZZ when sleeping, hearts when cuddling.

## Testing Strategy

- **Unit tests (core)**: need math (rise rates, clamping), happiness
  weighting/floor, action validation (legality per state) and effects, meow cooldown
  scaling (15 → 5 ticks at need ≥ 75), expiry/spawn logic (spawn-to-minimum, hard
  bounds), edge-triggered distress recording.
- **proptest invariant suite (core, CI gate)**: randomized valid configs and
  randomized/adversarial behaviors (including an always-invalid-action behavior),
  ≥10,000 ticks headless at zero tick delay; asserts every tick: no kitty removed,
  population ≥ 2, needs within 0–100, happiness ≥ floor, safeguard guarantee
  fulfilled, distress events edge-triggered.
- **Integration test (server)**: boot on an ephemeral port with a test config, `GET
  /world` returns a snapshot **containing greebles**, then receive at least two WS
  frames with increasing tick numbers.
- **Determinism tests**: same seed + config → identical world hash after N ticks;
  save/load snapshot mid-run → identical continuation vs. uninterrupted run.

## Complexity Tracking

No constitution violations — table not required.
