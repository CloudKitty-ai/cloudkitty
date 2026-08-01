# Implementation Plan: Meow Channel Economics — Retire the Engine-Enforced Meow Cooldown

**Branch**: `022-deliberate-purr` (shared batch-sitting branch) | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/023-retire-meow-cooldown/spec.md`

## Summary

Delete the swallow: `emit_meow` loses its `can_meow` early-return, so every
validated meow action emits; the per-kind bookkeeping stamp survives
unchanged as record-keeping. The timing keys rename in place with loud
retirement (`courtesy_ticks` 10 / `urgent_courtesy_ticks` 5, old names →
load error via deserialize-only sentinels, per the 022 mechanism), and
`MeowConfig` gains per-field serde defaults so partial tables load like
`[purr]`'s documented posture. Third scripted emitter fixed (the plan-phase
correction now in the spec): `selection::wait_for_them` gains the courtesy
consult and yields as a silent stand (`Idle`) on courtesy — the anti-orbit
guarantee is the stand, not the meow. Doctrine strengthening + swallow-test
re-baselines land in the same change; served `cloudkitty.toml` `[meow]`
section renames with it. Builds directly on 022's implementation (purr paths
already stamp nothing).

## Technical Context

**Language/Version**: Rust, workspace toolchain (stable, as pinned by CI)

**Primary Dependencies**: existing only — `serde`, `toml`. No new crates.

**Storage**: TOML config (rename with loud retirement); world snapshots
untouched (bookkeeping map unchanged; restored stamps stay harmless)

**Testing**: `cargo test` — unit re-baselines beside the code, the SC-003
spacing-invariant property test, `cloudkitty-rl` suite unchanged (SC-004)

**Target Platform**: server binary + headless eval path

**Project Type**: Rust workspace — engine crate only (`cloudkitty-core`);
RL crate is a pass-unchanged gate

**Performance Goals**: strictly less work per meow (one gate removed);
no complexity change anywhere

**Constraints**: Article V determinism (no draws added or removed by the
enforcement removal; the courtesy retune shifts which ticks reach playful's
announce coin — config-behavior change, recert-scoped, stated in the spec);
schema invariance (FR-009: digest layout, menu, mask untouched — values
shift only)

**Scale/Scope**: 3 engine source files + config module + 2 spec-doc
amendments + served config; smallest change of the batch

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-Phase-1 — PASS, no
violations, both times.*

- **Article I (no suffering)**: meows never touch needs; removing a
  message gate cannot create distress. The urgent-meow relief signalling
  gets *more* reliable (no swallowed urgent announcements). PASS.
- **Article II (no death)**: untouched. PASS.
- **Article III (never alone)**: untouched. PASS.
- **Article IV (engine is the law)**: the law shrinks by one rule but
  validation still governs every proposal; nothing reshapes a legal
  action — a legal meow now simply *happens*. The yield's silent stand is
  a behavior-layer choice of `Idle`, one of the two named safe outcomes.
  PASS.
- **Article V (deterministic)**: no new randomness; all changes flow
  through existing seeded draws; the spacing property test and the
  existing determinism suite guard it. Client stays a pure view. PASS.
- **Article VI (spec-first, test-guarded)**: renamed knobs keep documented
  defaults + validation rows; doctrine amendments (spec 001, spec 012) and
  swallow-test re-baselines land in the same change (FR-008); the
  reward-structure dependency is recorded durably (FR-011). PASS.

## Project Structure

### Documentation (this feature)

```text
specs/023-retire-meow-cooldown/
├── spec.md              # clarified + plan-phase correction (2026-07-31)
├── plan.md              # this file
├── research.md          # Phase 0 — decisions D1–D7
├── data-model.md        # Phase 1 — config schema, bookkeeping semantics
├── quickstart.md        # Phase 1 — build/verify guide
├── contracts/
│   └── meow-channel.md  # Phase 1 — emission/courtesy contract
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── action.rs            # emit_meow: delete the can_meow early-return
│                        # (swallow); stamp stays; re-baseline
│                        # meows_on_cooldown_are_silently_dropped → emitted
├── behavior/
│   ├── selection.rs     # wait_for_them(ctx): courtesy consult, silent
│   │                    # stand on courtesy (third emitter, FR-004)
│   └── needs_driven.rs  # call-site update for wait_for_them(ctx)
├── meow.rs              # cooldown_for: docs only (stamp-time semantics);
│                        # tests keep pinning the arithmetic
└── config/
    ├── mod.rs           # MeowConfig: courtesy_ticks/urgent_courtesy_ticks
    │                    # + per-field serde defaults + two retirement
    │                    # sentinels (deserialize-only Options)
    ├── defaults.rs      # default fns: 10 / 5 (one findable home)
    └── validate.rs      # rows: non-negative, urgent ≤ base; sentinel
                         # rejection naming replacements

specs/001-cloudkitty-mvp/data-model.md   # cooldown-audibility clause deleted
                                          # (shared amendment with 022 T024)
specs/012-approach-etiquette/spec.md      # "lawfully silent" clause amended
                                          # (yield = courtesy + silent stand)
docs/rl-training.md                       # FR-011: reward-structure
                                          # dependency recorded
cloudkitty.toml                           # [meow] rename + new comments
                                          # (same change — must keep loading)
```

**Structure Decision**: engine-crate-only change on the shared sitting
branch, sequenced after 022's implementation (022 already removed purr-path
stamping; this spec removes the swallow and generalizes courtesy). The
served-config `[meow]` edit is bound to the schema commit for the same
reason as 022's `[purr]` edit: the repo config must always load with the
repo binary.

## Complexity Tracking

No constitution violations — table intentionally empty.
