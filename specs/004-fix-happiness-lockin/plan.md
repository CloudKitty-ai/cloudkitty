# Implementation Plan: Fix Low-Happiness Lock-In

**Branch**: `004-fix-happiness-lockin` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-fix-happiness-lockin/spec.md`

## Summary

Kitties get stuck in long low-happiness episodes because built-in need
selection locks onto a single most-pressing need above the safeguard
threshold, play relief is nearly unattainable for an isolated kitty, and the
fixed tie-break order starves the last need at the 100-cap. The fix replaces
two-mode selection with a single urgency-weighted, distance-aware score;
raises play throughput (opportunistic play, distance-based targeting across
critters *and* friends, engine-tracked chase give-up); adds a solo-play
backstop so every need is self-satisfiable in the limit; breaks score ties by
longest-since-relief; and surfaces per-need distress age through the API and
a gentle viewer cue. All new constants are configuration with validation
(Article VI). Engine tick order, the safeguard spawner, and determinism are
untouched; all new per-kitty state is engine-maintained, serialized, and
serde-defaulted so existing snapshots resume cleanly.

## Technical Context

**Language/Version**: Rust, stable toolchain via rustup (workspace already pinned by Cargo.lock; no new toolchain requirements)

**Primary Dependencies**: Existing only — `serde`/`serde_json` (state + wire), `rand`/`rand_chacha` (ChaCha8, unchanged), `axum` + `tokio` (server, unchanged), `async-trait` (behavior trait, unchanged). No new crates.

**Storage**: JSON world snapshot (unchanged mechanism); three additive serde-defaulted `Kitty` fields, one widened `Action` variant

**Testing**: `cargo test --workspace` — unit tests beside code, integration + property suites in `crates/cloudkitty-core/tests/`, server integration in `crates/cloudkitty-server/tests/`; new long-run welfare test and stuck-state regression test

**Target Platform**: Same as MVP — server on macOS/Linux, no-build browser client

**Project Type**: Cargo workspace (`cloudkitty-core` pure sim + `cloudkitty-server` axum host) + static `client/`

**Performance Goals**: Selection scoring is O(needs × elements) per kitty per tick, same complexity class as today; 20,000-tick welfare test must run inside normal `cargo test` time (seconds)

**Constraints**: Determinism (Article V) — no wall-clock, no unseeded randomness in any new logic; snapshot backward compatibility — worlds saved by the current release must resume; behavior contract stability — external-behavior door (P2 backlog) must not be narrowed

**Scale/Scope**: 3-kitty default world, 32×32; changes confined to `cloudkitty-core` behavior/selection/bookkeeping, one server payload addition, one client panel cue

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design — PASS (both).*

| Article | Gate | Status |
|---------|------|--------|
| I — Kitties Cannot Suffer | Needs stay clamped 0–100; happiness floor untouched; feature *strengthens* Article I by making the kitty-side of relief reliable (solo play restores "play is always satisfiable"); distress stays a signal, and the new viewer cue must stay gentle | ✅ PASS |
| II — Kitties Cannot Die | No new removal/health paths; pursuit memory and relief recency are bookkeeping only | ✅ PASS |
| III — Kitties Cannot Be Alone | Untouched; ≥2 kitties is what makes friend-play and cuddle always nominally available | ✅ PASS |
| IV — Engine Is the Law | Behaviors still only propose; new per-kitty facts (pursuit, relief recency, distress age) are recorded by the **engine** from *applied* actions, so no behavior can forge them; solo play validates like any proposal | ✅ PASS |
| V — Server-Authoritative, Deterministic | No new RNG draws in selection (scoring is pure arithmetic); tick order unchanged; all new state serializes with the world; client cue is pure rendering of served data | ✅ PASS |
| VI — Spec-First, Test-Guarded | This plan follows spec 004; every new constant lands in `cloudkitty.toml` with validation ([research.md §R8](./research.md)); welfare bounds become tests (SC-001–006), property suite extended and remains the CI gate | ✅ PASS |

Two pre-existing Article VI violations (`WORTH_A_DETOUR`, `TILE_COST` hard-coded in `needs_driven.rs`) are *remediated* by this feature (FR-003).

## Project Structure

### Documentation (this feature)

```text
specs/004-fix-happiness-lockin/
├── spec.md                      # Feature specification
├── plan.md                      # This file
├── research.md                  # Phase 0 output — decisions R1–R10
├── data-model.md                # Phase 1 output — state & config deltas
├── quickstart.md                # Phase 1 output — validation guide
├── stuck-state-tick1465.json    # Archived stuck world (SC-005 regression fixture)
├── checklists/requirements.md   # Spec quality checklist (complete)
├── contracts/
│   ├── http-api-delta.md        # Wire additions: distress_since, solo play shape, /config
│   └── behavior-delta.md        # DecisionContext & Action changes for behaviors
└── tasks.md                     # Phase 2 output (/speckit-tasks — NOT created by plan)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config.rs        # [behavior] + [actions] + [viewer] additions, validation (R8)
├── kitty.rs         # + pursuit, abandoned_chases, last_relief, distress_since (R2, R3, R6)
├── action.rs        # Play target becomes optional (solo play); validation + apply (R5)
├── needs.rs         # highest_pressure loses tie-break duty (selection owns it now)
├── world.rs         # engine bookkeeping: pursuit tracking, relief recency,
│                    #   distress_since maintenance in the needs phase (R2, R3, R6)
└── behavior/
    ├── selection.rs # NEW: shared urgency-weighted scoring + tie-break (R1, R3)
    ├── needs_driven.rs  # uses selection.rs; opportunistic play; viable-target
    │                    #   play pursuit with give-up + solo backstop (R2, R4, R5)
    └── playful.rs   # same selection when getting serious; same play pursuit (R7)

crates/cloudkitty-core/tests/
├── welfare_longrun.rs       # NEW: 20k-tick SC-001..004 bounds (R10)
├── stuck_state_regression.rs# NEW: SC-005 against the archived fixture (R10)
├── behavior_variation.rs    # extended: both profiles immune to lock-in
└── invariants_proptest.rs   # extended: new fields respect invariants

crates/cloudkitty-server/
├── src/main.rs      # no changes expected (config plumbing only if needed)
└── tests/server_integration.rs  # payload includes distress_since; old-snapshot resume

client/
├── app.js           # distress-age cue on kitty cards (pure view, /config-driven)
└── index.html       # .kitty-card .patience style

cloudkitty.toml      # new keys with documented defaults (R8)
```

**Structure Decision**: Existing two-crate workspace plus static client is
retained; the only new module is `behavior/selection.rs`, extracted so both
built-in profiles share one scored selection (FR-014) instead of duplicating
it.

## Complexity Tracking

No constitution violations to justify — table intentionally empty.
