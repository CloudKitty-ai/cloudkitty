# Implementation Plan: Welfare-Hazard Acknowledgement Guard

**Branch**: `product/066-welfare-hazard` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/066-welfare-hazard-guard/spec.md`
(clarified 2026-10-26: exact acknowledgement; widest predicate; bare
server switch; teacher-eligibility flag deferred to the needy spec).

## Summary

One optional top-level `[welfare_hazard]` table holding
`acknowledged = [<mode names>]`. The engine keeps a closed registry of
hazardous modes (one entry today: `initial_needs`, active when any
governing initial-need setting at either level has a value or range
upper bound above zero). `Config::validate` fails unless the
acknowledged set equals the active set exactly, with an error that names
the mode, the activating entry, and the line to add. Both shipped-config
sweeps fail any tracked config outside `experiments/` with an active
mode. The server refuses an acknowledged config unless started with the
bare `--allow-welfare-hazard` switch, and when it serves one it says so
in one boot line, on `GET /config` (the section serializes when
present), and as one conditional key-settings row. Absent, every surface
is byte-identical to today; the fingerprint never reads the section. The
seven committed spec-065 configs get the exact acknowledgement table
appended at EOF in the same PR, under `cross-lane:`.

## Technical Context

**Language/Version**: Rust, workspace toolchain pin (`rust-toolchain`).
Crates touched: `cloudkitty-core` (config types, registry, validator,
sweep), `cloudkitty-rl` (sweep only), `cloudkitty-server` (switch,
gate, boot line, settings row).

**Primary Dependencies**: serde + toml (config), anyhow (server), the
existing `tracing` boot-log path. No new dependencies.

**Storage**: TOML config in; no world-state or snapshot schema change.
The section is NOT part of `Config::fingerprint()`.

**Testing**: `cargo test` (core unit tests on the validator and
registry; the two sweeps' in-file self-tests on a scratch tree; server
unit tests on the gate and the settings row; a serialization test on the
defaults stamp). Every assertion goes red first through
`scripts/mutate.sh --expect`; the one hand-rolled cycle (a tree-state
mutation for the sweep, as in #468) states its reason in the PR.

**Target Platform**: engine library + server binary; the Python
environment, `kitty-eval`, and every experiments tool reach the guard
through `Config::validate` without changes.

**Project Type**: single workspace change across three crates.

**Performance Goals**: load-time only; zero per-tick cost in either
state.

**Constraints**: section absent = byte-identical on every readable
surface (FR-002); defaults stamp and `GET /config` must not grow when
absent; zero golden/pin re-cuts beyond the seven migration appends;
`experiments/` files edited only by the exact EOF append (Experiments'
provenance strip, main 304221b1).

**Scale/Scope**: ~5 source files + 2 sweep files + tests; 7 config
appends; CHANGELOG + INDEX; the deploy script untouched.

## Constitution Check

*GATE: passed pre-Phase-0; re-checked post-design — no violations.*

- **Article I (no suffering)**: the guard adds no need, state or
  mechanic; it makes the constitutional default the only thing that
  can load by accident. Relief guarantees are untouched (FR-008).
- **Article II (no death)**: untouched.
- **Article III (never alone)**: untouched; the roster rule runs in the
  same `validate` chain, before this check.
- **Article IV (engine is the law)**: no behavior-API surface; the
  registry is engine-side and read only at validation.
- **Article V (server-authoritative, deterministic)**: the serve-time
  gate lives in the server's boot path before any world exists; no RNG
  draw is added or moved in either state.
- **Article VI (spec-first, test-guarded)**: this pipeline; the mode
  names and the switch name are documented constants, not magic.

## Project Structure

### Documentation (this feature)

```text
specs/066-welfare-hazard-guard/
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D12
├── data-model.md        # Phase 1: config entity, registry, errors
├── quickstart.md        # Phase 1: validation scenarios
├── contracts/
│   └── guard-law.md     # The acknowledgement law: predicate, exactness,
│                        #   error text, sweep rule, server gate, surfaces
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/config/
├── mod.rs               # WelfareHazardConfig; Config.welfare_hazard (optional,
│                        #   skip-if-none); validate() chain gains one call
├── validate.rs          # validate_welfare_hazard: registry → active set →
│                        #   check_acknowledgement (pure, unit-tested)
└── welfare_hazard.rs    # NEW: HazardMode registry (closed enum), activity
                         #   predicate for initial_needs, mode-name constants
crates/cloudkitty-core/tests/shipped_configs.rs      # outside-experiments rule + self-test
crates/cloudkitty-rl/tests/shipped_configs_rl.rs     # same rule, same self-test shape
crates/cloudkitty-server/src/
├── main.rs              # --allow-welfare-hazard (bare), HELP line; gate call
│                        #   right after config.validate(), before any world
├── welfare_hazard.rs    # NEW: gate(config, allowed) + log_boot(config)
└── settings.rs          # conditional welfare_hazard.acknowledged row (last)
experiments/minifriend-phase1-2026-10-22/g2leg-20-{W,G}.toml   # exact EOF append
experiments/minifriend-phase1b-2026-10-23/g2leg-20-P{1..5}.toml # exact EOF append
CHANGELOG.md, specs/INDEX.md
```

**Structure Decision**: mirror spec 065's shape — the registry in its
own module beside `validate.rs` with a porting-grade contract doc; the
server gate in its own module like `stuck::log_boot`; the sweeps gain a
helper with an in-file self-test on a scratch tree, the shape
`collect_never_follows_a_symlink` already uses.

## Complexity Tracking

No constitution violations; table not needed.
