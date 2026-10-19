# Implementation Plan: Initial-Needs Distribution at World Creation

**Branch**: `product/initial-needs` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/065-initial-needs/spec.md`

## Summary

One optional `[initial_needs]` config table (roster-wide, per-need
fixed value or inclusive range) plus an optional per-kitty
`initial_needs` field on `[[kitty]]` entries (need-by-need precedence,
the house per-kitty override idiom). Applied in `World::try_generate`
after kitty creation and before the existing generate-time happiness
recompute; ranged needs draw from a new domain-separated ChaCha8
sub-stream (the 062 starts law pattern — master stream untouched).
When the feature is active, generation then runs the engine's OWN
needs-phase state family — `update_announce_arming` and
`record_distress` — so a distressed-created world is register-real at
tick 0 through the one existing definition, never a parallel path.
Absent, nothing runs: byte-inert.

## Technical Context

**Language/Version**: Rust (workspace toolchain pin; see
rust-toolchain) — `cloudkitty-core` crate only.

**Primary Dependencies**: serde (config), rand + rand_chacha
(ChaCha8Rng, already used by starts.rs). No new dependencies.

**Storage**: TOML config in; world state as today (no schema change —
`in_distress`/`distress_since` already serialize when non-empty).

**Testing**: cargo test (unit + the standing golden/determinism
suites); `scripts/mutate.sh --expect` for every rule-5 red; bc-collect
byte-identity for flag-absent proof.

**Target Platform**: engine library; server/bc-collect consume it
unchanged.

**Project Type**: single workspace crate change (cloudkitty-core).

**Performance Goals**: generation-time only — O(kitties × 6) applies;
no per-tick cost either state.

**Constraints**: section absent = byte-identical on every readable
surface (FR-002); defaults stamp and `GET /config` must not grow;
zero golden/pin re-cuts; no draw-order change to master stream or any
existing sub-stream (FR-005).

**Scale/Scope**: 3 source files (config/mod.rs, needs or new
init module, world.rs) + tests; spec docs; CHANGELOG + INDEX.

## Constitution Check

*GATE: passed pre-Phase-0; re-checked post-design — no violations.*

- **Article I (no suffering)**: initial values validated to need
  bounds [0, 100]; happiness derives via the engine's one floored
  function (FR-004); distress events/records are the standing signal
  mechanism, fed through `record_distress` itself; the safeguard
  relief guarantee applies to initialized needs on the first
  environment phase exactly as to risen ones (FR-007) — no new rule,
  no carve-out. Values at 100 are legal need pressure, not a new
  negative state.
- **Article II (no death)**: untouched — no removal path added.
- **Article III (never alone)**: untouched — roster rules unchanged.
- **Article IV (engine is the law)**: no behavior-API surface; only
  initial values of existing engine state move (FR-008).
- **Article V (server-authoritative, deterministic)**: generation
  stays server-side; determinism per seed+config via the
  domain-separated sub-stream (FR-005); tick order untouched.
- **Article VI (spec-first, test-guarded)**: this pipeline; constants
  in config with documented defaults; property/invariant suites must
  stay green from tick 0 (SC-005).

## Project Structure

### Documentation (this feature)

```text
specs/065-initial-needs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── init-law.md      # The draw/application law (porting-grade)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # InitialNeedsSpec + NeedInit types; Config.initial_needs;
│                        #   KittyConfig.initial_needs; validation
├── init_needs.rs        # NEW: the draw law (sub-stream seed, resolve order) —
│                        #   sibling of starts.rs, same shape
└── world.rs             # try_generate: apply after kitty creation; gated
                         #   update_announce_arming + record_distress after the
                         #   existing happiness recompute
```

**Structure Decision**: mirror spec 062 exactly — law in its own
module with a versioned domain tag and a porting-grade contract doc;
config types beside the other sections; one application site in
`World::try_generate`.

## Complexity Tracking

No constitution violations; table not needed.
