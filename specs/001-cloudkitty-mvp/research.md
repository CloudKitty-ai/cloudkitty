# Research: CloudKitty MVP

**Date**: 2026-07-18 | **Plan**: [plan.md](./plan.md)

No `NEEDS CLARIFICATION` items remained in Technical Context — the stack was fully
specified by the user and spec ambiguities were resolved in the 2026-07-18
clarification session. This document records the rationale behind each binding
decision and settles the plan-level constants the clarification session deferred.

## R1. Language & runtime: Rust (stable) + tokio

- **Decision**: Rust stable toolchain, Cargo workspace, `tokio` multi-threaded
  runtime in the server crate only.
- **Rationale**: The constitution demands structural guarantees (no code path
  removes a kitty; needs always bounded) — Rust's type system enforces these at
  compile time (no removal API, clamped newtype). Determinism benefits from no GC
  pauses. `tokio` provides interval timers, signal handling, watch channels, and
  the timeout primitive Article IV needs, in one dependency.
- **Alternatives considered**: TypeScript/Node (faster to write, weaker invariant
  enforcement, GC jitter); Python (property testing via hypothesis is excellent but
  10k-tick suites are slow); Go (fine, but weaker enum/exhaustiveness support for
  action validation).

## R2. Web framework: axum + tower-http

- **Decision**: `axum` for REST + WebSocket upgrade, `tower-http` for static file
  serving (client/) and permissive CORS.
- **Rationale**: First-class WebSocket support, tokio-native, minimal boilerplate
  for five read-only JSON endpoints; `ServeDir` eliminates any client build/deploy
  step. Lean dependency tree per the user's "keep it lean" directive.
- **Alternatives considered**: `actix-web` (heavier, own runtime conventions),
  `warp` (filter combinators harder to read), `rocket` (larger, slower-moving).

## R3. RNG: rand_chacha::ChaCha8Rng with serde

- **Decision**: One `ChaCha8Rng` seeded from config; serialized into every snapshot
  (serde feature); per-kitty decision streams derived from it each tick.
- **Rationale**: ChaCha8 is deterministic and portable across platforms/versions
  (unlike `StdRng`, whose algorithm is explicitly not stability-guaranteed), cheap,
  and serde-serializable — the only mainstream choice that makes
  determinism-across-restarts (SC-003/SC-004) trivially correct.
- **Alternatives considered**: `StdRng` (no cross-version stability guarantee —
  disqualifying for persisted determinism); `SmallRng` (same problem); seeding a
  fresh RNG per tick from a counter (workable but loses statistical quality and
  complicates stream derivation).

## R4. Per-kitty decision randomness (determinism under concurrency)

- **Decision**: Before behaviors run each tick, the engine draws a per-kitty seed
  from the master RNG **in stable kitty-id order** and embeds a small derived RNG
  in each `DecisionContext`. Behaviors may only use that RNG.
- **Rationale**: `join_all` completion order and wall-clock timing then cannot
  influence outcomes — same seed, same decisions, regardless of scheduling. This
  satisfies FR-004's "independent of decision completion order" clause without
  locking the master RNG across await points.
- **Alternatives considered**: sharing the master RNG behind a mutex (order of
  acquisition nondeterministic — violates FR-004); deciding sequentially (correct
  but abandons the concurrent-decide design the user specified).

## R5. State sharing: single-owner sim task + tokio::sync::watch

- **Decision**: The sim task exclusively owns `World`. After each tick it publishes
  `Arc<WorldSnapshot>` on a `watch` channel; REST handlers call `borrow()` for the
  latest, WS handlers await `changed()` and forward.
- **Rationale**: No locks on the hot path, no shared mutable state, snapshot
  consistency by construction (Article V: client is a pure view of published
  state). `watch` semantics (latest-value, slow readers skip intermediate states)
  match a "current world" feed exactly.
- **Alternatives considered**: `RwLock<World>` (handlers could observe mid-tick
  state; lock contention); `broadcast` channel (buffers every tick — backpressure
  complexity for zero benefit since only the latest state matters).

## R6. Persistence: atomic JSON snapshot

- **Decision**: `serde_json` the whole `World` (RNG state included) to
  `snapshot.json` every N ticks (default 100) and on ctrl-c; write to
  `snapshot.json.tmp` in the same directory then `rename`. Load-and-validate on
  boot; validation failure aborts startup with a clear message; `--fresh` skips.
- **Rationale**: One file, human-inspectable, no schema migration machinery for an
  MVP; same-directory rename is atomic on POSIX filesystems, so a crash mid-write
  can never tear the snapshot (worst case: the previous save survives, losing at
  most one save interval — accepted in spec Assumptions).
- **Alternatives considered**: SQLite (transactional but adds a database the user
  explicitly excluded); append-only event log (enables replay but is a later
  feature); bincode (compact but not inspectable, and JSON size is trivial here).

## R7. Config: TOML via serde + validated structs

- **Decision**: `cloudkitty.toml` → raw serde structs → `validate()` producing
  typed, checked config. Validation errors name the offending field, its value,
  and the allowed range. Ship a fully commented default config at repo root.
- **Rationale**: TOML fits comments (Article VI: documented defaults live in the
  shipped config); two-stage parse-then-validate cleanly separates "malformed"
  from "invalid" errors (FR-007's error catalogue).
- **Alternatives considered**: JSON (no comments — conflicts with "documented
  defaults"); YAML (indentation footguns, heavier parser); CLI-flags-only
  (unmanageable for ~40 constants).

## R8. Property testing: proptest

- **Decision**: `proptest` (dev-dependency of core) generating random valid
  configs and behavior assignments — including an adversarial always-invalid-action
  behavior and a chaos behavior proposing random (often illegal) actions — driving
  ≥10,000 headless ticks with per-tick invariant assertions.
- **Rationale**: proptest's integrated shrinking + persisted failure seeds
  (`proptest-regressions/`) pairs with the determinism guarantee to make any CI
  failure locally reproducible — exactly the property Article VI's gate needs.
- **Alternatives considered**: `quickcheck` (less flexible generators, weaker
  shrinking); hand-rolled fuzz loop (no shrinking, no seed persistence).

## R9. Client: no-build-step vanilla JS + canvas

- **Decision**: `client/index.html` + `app.js` + `render.js`; canvas renderer with
  emoji/simple-shape sprites, soft rounded style; meow speech bubbles, ZZZ during
  sleep, hearts when cuddling; greebles skipped unless the `g` debug toggle is on.
- **Rationale**: Zero build tooling (user constraint: no framework, no bundler);
  a 32×32 grid at ~1.25 fps effective update rate is trivial for canvas; all
  simulation intelligence stays server-side (Article V).
- **Alternatives considered**: DOM-grid rendering (simpler but janky for bubbles/
  overlays); any framework/bundler (excluded by user).

## R10. Behavior interface: async trait now, external implementations later

- **Decision**: `#[async_trait] trait Behavior { async fn decide(&self, ctx:
  &DecisionContext) -> Action; }` — built-ins return immediately (no awaiting, no
  wall-clock dependence, exempt from timeout per spec clarification); the engine
  applies `tokio::time::timeout` only to non-built-in implementations and falls
  back to `NeedsDriven` on timeout/panic/invalid proposal.
- **Rationale**: The async signature is the extension point Article IV requires
  (script/HTTP/local-service behaviors drop in without engine changes); exempting
  built-ins keeps Article V's determinism unconditional. The timeout path is
  exercised in tests via a deliberately slow test-only behavior.
- **Alternatives considered**: sync trait + adapter layer later (would require
  engine changes when externals arrive — violates FR-029); making everything
  subject to timeout (rejected in clarification: breaks determinism).

## R11. Deferred constants — now settled (documented defaults)

These were flagged as plan-level in the clarification session. Defaults below go in
`cloudkitty.toml` (all configurable):

| Constant | Default | Rationale |
|----------|---------|-----------|
| Chow servings | 5 per element | ~2 kitties eating twice before respawn cycle; keeps chow turnover visible |
| Chow TTL | none (permanent until empty) | servings already bound its life; timer optional in config |
| Bug lifetime | 120 ticks (~96 s) | long enough to be chased, short enough to see turnover |
| Greeble lifetime | 90 ticks | erratic + short-lived reads as "mysterious" |
| Sunbeam TTL | 150 ticks (~2 min), respawns elsewhere | slow, cozy drift across the world |
| Water | permanent | per spec default |
| Snapshot path | `./snapshot.json` (next to process CWD; `--snapshot` flag overrides) | obvious, inspectable |
| Recent-meow window | 10 ticks | per spec assumption |
| Distress event retention | 1,000 most recent | per spec assumption |
| Greeble direction-change probability | 60% per tick, 1–2 tiles | "fast and erratic" per spec |
| Bug movement | 1 tile every 2 ticks, uniform random direction | per spec |

## R12. CI gate

- **Decision**: GitHub Actions workflow running `cargo fmt --check`, `cargo clippy
  -- -D warnings`, and `cargo test --workspace` (which includes the proptest
  invariant suite and the server integration test) on every push/PR to `main`.
- **Rationale**: Article VI requires the property suite as a required CI gate;
  one workspace test command keeps the gate simple and unskippable.
- **Alternatives considered**: separate nightly long-run fuzz job (nice-to-have
  later; the 10k-tick suite must stay in the merge gate regardless).
