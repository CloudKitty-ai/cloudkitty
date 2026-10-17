# Implementation Plan: Randomized Starts

**Branch**: `product/randomized-starts` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/062-randomized-starts/spec.md`

## Summary

Engine-native per-seed randomized kitty start positions behind a new optional
`[starts]` config table carrying the category shares. The draw happens in
`World::generate` (the one site every consumer already goes through), consumes
a domain-separated ChaCha8 sub-stream keyed off (world seed, fixed tag) — never
the master world stream — and follows a versioned, porting-grade documented
draw law over the coverage instrument's geometry. `KittyConfig.x/y` become
optional so a knob-on config can mix drawn and pinned kitties; knob-off configs
are byte-identical in behavior and serialization. bc-collect's meta.json gains
an engine-identity stamp and a per-kitty draw echo.

## Technical Context

**Language/Version**: Rust (workspace pinned toolchain — no new root `.toml`;
the rust-toolchain pin reddens two config sweeps if one appears)

**Primary Dependencies**: `rand`/`rand_chacha` 0.3 (`ChaCha8Rng`, already the
engine's only RNG), `serde`/`toml` (config), `sha2` (bc-collect already)

**Storage**: N/A (config-file knob; collection metadata is bc-collect's
meta.json)

**Testing**: `cargo test` (workspace), `cargo clippy --all-targets`, rule-5
red-first via `scripts/mutate.sh --expect`; shipped-config sweep and goldens
must stay green untouched (SC-004)

**Target Platform**: wherever the engine builds (macOS dev, Linux CI/lab) —
the draw law must be bit-identical across platforms (integer/IEEE-754
arithmetic only)

**Project Type**: Rust workspace — engine crate (`cloudkitty-core`) + one
experiments tool (`experiments/tools/bc-collect`, cross-lane per spec
Assumptions)

**Performance Goals**: draw cost is one-time at world build, O(roster ×
category tiles); immaterial against tick simulation. No tick-path change at
all.

**Constraints**:
- Knob-off byte-identity (FR-001): no serialization change for existing
  configs (serde `Option` + `skip_serializing_if`), `engine_defaults_sha256`
  stamp unchanged, `Config::fingerprint()` unchanged (it reads only
  w/h/seed/ids — verified).
- `World::generate(&Config) -> Self` has 68 call sites; its signature does
  not change. Fallibility lands as `try_generate` (research R5).
- `Config::validate()` section order is spec-contract (spec 020): new checks
  append as position 19; the roster slot only gains checks for configs that
  could not previously parse (research R8).

**Scale/Scope**: one new core module (`starts.rs`), config struct + validation
edits, one hook in `World::generate`, bc-collect meta extension + `build.rs`,
tests. No client, no server-endpoint, no RL-crate behavior change.

## Constitution Check

*GATE: evaluated pre-Phase 0 and re-checked post-Phase 1 design. All pass.*

- **Article I (Kitties Cannot Suffer) — PASS.** Start placement is world
  setup before tick 0. Needs, distress, relief guarantee, and happiness floor
  are untouched; the safeguard-spawn guarantee is position-independent (it
  spawns reachable relief wherever kitties are).
- **Article II (Kitties Cannot Die) — PASS.** No removal path is added; the
  draw only chooses tick-0 positions.
- **Article III (Kitties Cannot Be Alone) — PASS.** Roster size and its ≥2
  validation are untouched; the draw places the configured roster, never
  shrinks it. Exhaustion fails the whole world build loudly (no kitty is ever
  silently dropped).
- **Article IV (Engine Is the Law) — PASS.** No behavior/proposal surface is
  touched; placement is engine-side world generation.
- **Article V (Deterministic Simulation) — PASS, with a documented reading.**
  "All randomness flows through a single seeded RNG": the draw adds a second
  `ChaCha8Rng` instance, but it is a pure function of the one world seed (plus
  a fixed constant tag) and consumes nothing from the master stream. The
  article's operative guarantee — same seed + config + tick count → same world
  state — holds exactly (FR-003), and the engine already derives per-kitty
  `DecisionRng` sub-streams from the master (rng.rs). The alternative (drawing
  from the master stream) is the baseline-attribution trap the spec's FR-004
  and doctrine rule 9 forbid: it would shift every downstream element spawn.
  The single ROOT of randomness remains the world seed.
- **Article VI (Spec-First, Test-Guarded) — PASS.** This plan follows the
  spec; shares live in config (no magic numbers); every new rule gets a guard
  run red-first (mutate.sh). The design-doctrine check (CLAUDE.md rule 8) is
  in the spec, pre-plan, as required.

## Project Structure

### Documentation (this feature)

```text
specs/062-randomized-starts/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── config-surface.md   # [starts] table, optional x/y, validation errors
│   ├── draw-law-v1.md      # porting-grade sub-stream + algorithm (FR-011)
│   └── provenance.md       # bc-collect meta.json fields (FR-009/010/012)
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── starts.rs            # NEW: StartCategory, DrawnStart, STARTS_LAW_VERSION,
│                        #   draw(config) -> Result<Vec<DrawnStart>, StartsError>
│                        #   (the versioned pure law; the ONE sampler)
├── config/mod.rs        # StartsConfig (Option on Config, skip-if-none);
│                        #   KittyConfig x/y -> Option<u32>; validate_starts()
│                        #   appended position 19; roster checks for the newly
│                        #   parseable missing-x/y space
├── world.rs             # World::generate resolves positions via starts::draw
│                        #   (knob on) / explicit (knob off); try_generate
├── rng.rs               # untouched (sub-stream built directly from
│                        #   ChaCha8Rng::from_seed in starts.rs)
└── lib.rs               # pub mod starts

experiments/tools/bc-collect/
├── build.rs             # NEW: embed git commit (+dirty marker) at build time
└── src/main.rs          # meta.json: engine_commit, starts_law_version,
                         #   per-kitty "starts" echo (cross-lane: Experiments'
                         #   requirements note asks for exactly this)

crates/cloudkitty-core/   # tests: unit in starts.rs/config; integration test
                          #   for SC-003 byte-identity + SC-001/002 sweep +
                          #   golden draw vectors (SC-005 enabler)
```

**Structure Decision**: single new core module plus edits in place. The law
lives in `cloudkitty-core::starts` so `World::generate` (engine), bc-collect
(echo), and tests all read the same pure function; no second home exists to
drift.

## Complexity Tracking

No constitution violations to justify. (Article V's second RNG instance is a
documented reading, not a violation — the root of randomness stays the world
seed; see Constitution Check.)
