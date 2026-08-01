# Implementation Plan: Deliberate Purring & the Quiet Motor

**Branch**: `022-deliberate-purr` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/022-deliberate-purr/spec.md`

## Summary

Menu row 38 (`Meow(Purr)`) becomes the deliberate purr: earned-gated in
`validate()` (so the RL mask picks it up with no carve-out), applied as a
turn-consuming purr-phase start with the duration drawn at apply time and a
direct-recorded announcement. The spontaneous motor keeps its cadence but
announces only per `announce_probability` (default 0) and stops stamping the
Purr message cooldown (deleted outright — the 023 handoff). Purr ends stamp a
motor cooldown of ⌈drawn factor × duration⌉ with the factor drawn per end
from `[cooldown_factor_min, cooldown_factor_max]` (1.75/2.75); duration
bounds retune to 8/13; `[purr] cooldown_ticks` is retired loudly via a
deserialize-only sentinel field. One new `Kitty` field (`purring_duration`,
serde-defaulted so old snapshots restore under the min_ticks convention) and
one new master-RNG primitive (`gen_f32`, mirroring the decision-RNG recipe)
are the only structural additions. No codec, observation, or mask-shape
change anywhere.

## Technical Context

**Language/Version**: Rust, workspace toolchain (stable, as pinned by CI)

**Primary Dependencies**: existing only — `serde`/`serde_json` (snapshots &
API), `toml` (config). No new crates.

**Storage**: JSON world snapshots via serde (additive optional field);
TOML config (schema change with loud retirement)

**Testing**: `cargo test` — unit tests beside the code (action.rs, world.rs,
config), property-style long-run tests (SC-003/SC-004), RL-side shape guards
in `cloudkitty-rl` (existing tests must pass unchanged per SC-005)

**Target Platform**: server binary (macOS dev / Linux deploy), headless eval
path

**Project Type**: Rust workspace — engine crate (`cloudkitty-core`) + RL
crate (`cloudkitty-rl`, test-side only for this spec)

**Performance Goals**: no tick-loop regression — all additions are O(kitties)
per tick with constant-work draws (unchanged complexity class)

**Constraints**: Article V determinism (all randomness via the master seeded
RNG, draw shape/order pinned per FR-011); schema invariance (FR-014: no
codec bump, no observation change, no mask width change); RNG stream shift
vs the current engine is expected and recert-scoped (no byte-diff claims)

**Scale/Scope**: worlds of 2–8 kitties; ~6 source files in
`cloudkitty-core`, test re-baselines, 3 doctrine annotations, served-config
update

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-Phase-1 — PASS, no
violations, both times.*

- **Article I (no suffering)**: purring still never changes a need or
  happiness; the deliberate purr spends a turn and nothing else. No new
  negative states. PASS.
- **Article II (no death)**: untouched. PASS.
- **Article III (never alone)**: untouched. PASS.
- **Article IV (engine is the law)**: the earned gate lives in engine
  validation; an unearned purr proposal resolves to the idle no-op — one of
  the two constitutionally named safe outcomes (well-formed but illegal).
  Advisors' proposal surface is otherwise unchanged. PASS.
- **Article V (deterministic, server-authoritative)**: every new draw
  (deliberate duration at apply, announce decision and factor at purr
  phase) flows through the master seeded RNG with pinned order and
  config-independent draw shape (FR-011); the client remains a pure view
  (no client change rides this spec). Same seed + config + ticks → same
  world, guarded by new determinism tests including mid-purr save/restore.
  PASS.
- **Article VI (spec-first, test-guarded)**: this plan follows the spec;
  every new tunable is named config with a documented default and a
  validation row (FR-010); the spec-011/spec-001/spec-014 doctrine
  amendments land with their re-baselined guarding tests in the same
  change (FR-015). PASS.

## Project Structure

### Documentation (this feature)

```text
specs/022-deliberate-purr/
├── spec.md              # Feature spec (clarified 2026-07-31)
├── plan.md              # This file
├── research.md          # Phase 0 — decisions D1–D10
├── data-model.md        # Phase 1 — purr state machine, config schema
├── quickstart.md        # Phase 1 — build/verify guide
├── contracts/
│   └── deliberate-purr.md   # Phase 1 — row-38 + purr-phase contract
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── action.rs            # validate(): earned gate for Meow(Purr);
│                        # apply(): deliberate purr start (draw, announce,
│                        # no-op case); test re-baselines (FR-015)
├── world.rs             # purr_phase(): announce-probability draw, stamp
│                        # removal, factor draw + ceil cooldown at purr end;
│                        # purring_duration bookkeeping
├── kitty.rs             # new field purring_duration: Option<u64>
│                        # (serde default — old snapshots → None)
├── rng.rs               # SeededRng::gen_f32 (mirrors DecisionRng recipe)
└── config/
    ├── mod.rs           # PurrConfig: announce_probability,
    │                    # cooldown_factor_min/max, retirement sentinel
    ├── defaults.rs      # 8 / 13 / 0.0 / 1.75 / 2.75
    └── validate.rs      # new rows + retired-knob loud rejection

crates/cloudkitty-rl/
├── src/mask.rs          # tests only: row-38 earned-gating assertions
│                        # (mask itself derives from validate — no carve-out)
└── tests/               # existing shape/harness guards pass unchanged (SC-005)

specs/011-sustained-purring/spec.md        # dated doctrine amendment (FR-015)
specs/001-cloudkitty-mvp/data-model.md     # dated doctrine amendment (FR-015)
specs/014-multi-agent-rl/contracts/encodings.md  # mask-doctrine annotation

cloudkitty.toml          # [purr] rewrite: 8/13, factor bounds, announce
                         # probability, new comments (must land same change —
                         # the retired key would otherwise fail repo loads)
```

**Structure Decision**: single Rust workspace, existing layout; all engine
changes in `cloudkitty-core`, RL crate touched only by tests. The
served-config edit is part of this change-set because the loud retirement
(FR-010) would otherwise break every bare `kitty-eval` and server start from
the repo root — the repo's `cloudkitty.toml` must always load with the
repo's binary (the world-identity stamp from issue #76 hashes it).

## Complexity Tracking

No constitution violations — table intentionally empty.
