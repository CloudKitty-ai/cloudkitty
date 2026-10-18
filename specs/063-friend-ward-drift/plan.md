# Implementation Plan: Friend-Ward Drift (bounded-detour social bias)

**Branch**: `product/friend-ward-drift` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/063-friend-ward-drift/spec.md`

## Summary

A toggleable teacher-side bias, default off and byte-inert when off:
when the nearest KNOWN friend (visible, or freshest audible want/here
stamp in the digest window) is farther than a config gate, (a) the
shared priced-element selection picks, among candidates within a config
detour bound of the cheapest priced cost, the one closest to that
friend, and (b) the idle potter steps toward that friend instead of a
uniform random direction, cadence unchanged. Two hook sites, one new
knowledge helper, three `[behavior]` config fields — no schema change,
no new validation position, no golden re-cuts.

## Technical Context

**Language/Version**: Rust (workspace-pinned toolchain; see
`rust-toolchain.toml` — no new root toml in this feature)

**Primary Dependencies**: `cloudkitty-core` only (serde for config;
the engine's own RNG plumbing). No new crates.

**Storage**: N/A (config in toml; no persistence change)

**Testing**: `cargo test` (unit tests in `selection.rs` /
`needs_driven.rs` / `config`; integration goldens in
`crates/cloudkitty-core/tests/`); `scripts/mutate.sh --expect` for
every rule-5 red; local gate includes `cargo fmt` and
`cargo clippy --all-targets`

**Target Platform**: server engine (darwin dev, linux CI)

**Project Type**: existing multi-crate Rust workspace; all changes in
`crates/cloudkitty-core`

**Performance Goals**: no measurable tick-cost regression; the drift
adds one knowledge scan + one band re-rank only when the flag is on
and a need's selection runs

**Constraints**: FR-002 flag-off byte-identity on every readable
surface (decisions, RNG consumption, serialized config echoes);
FR-010 determinism with the flag on

**Scale/Scope**: two decision sites in the teacher; three config
fields; ~6 files touched (selection.rs, needs_driven.rs, world.rs,
config/mod.rs, config/defaults.rs, config/validate.rs) plus tests

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, both.*

- **Article I (no suffering)**: untouched — the drift reorders target
  choices; relief availability and the safeguard spawn rule are not in
  its path (spec FR-009, edge-case reach cap).
- **Article II (no death)**: untouched.
- **Article III (never alone)**: untouched; the drift's "friend" read
  relies on roster members existing, which Article III guarantees.
- **Article IV (engine is law)**: the drift lives inside the built-in
  teacher (an advisor); it proposes Moves/activities exactly as today
  and the engine's validation path is unchanged.
- **Article V (deterministic, server-authoritative)**: FR-010;
  flag-off consumes RNG identically to today, flag-on consumes
  deterministically per seed+config (the potter's direction draw is
  skipped when the drift steers — a config-keyed, attributable
  divergence; spec edge case declares it).
- **Article VI (spec-first, no magic numbers)**: this plan follows the
  committed spec; gate and detour are config dials with documented
  defaults (data-model.md), never constants in code.

## Project Structure

### Documentation (this feature)

```text
specs/063-friend-ward-drift/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── drift-law.md     # Phase 1 output — the selection law Experiments reads
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── behavior/
│   ├── selection.rs     # band re-rank in priced_nearest_element;
│   │                    #   nearest_known_friend(); drift-fires gate
│   ├── needs_driven.rs  # wander() friend-ward arm
│   └── teacher.rs       # (no change expected: cadence draw stays put)
├── world.rs             # FogView: kind-fenced freshest-stamp query
│                        #   (sibling of heard_unseen, existing method untouched)
└── config/
    ├── mod.rs           # BehaviorConfig: 3 fields, serde-skipped when absent
    ├── defaults.rs      # default gate 10, detour 4.0
    └── validate.rs      # validate_behavior additions (position 7, no new position)

crates/cloudkitty-core/tests/   # flag-off byte-identity rides existing goldens;
                                 # one new integration test for flag-on determinism
```

**Structure Decision**: single existing workspace; every change lands
in `cloudkitty-core` behind the flag. No bc-collect, server, or client
change — collection picks the flag up through the config it is handed.

## Complexity Tracking

No constitution violations; table not needed.
