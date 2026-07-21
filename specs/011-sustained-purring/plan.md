# Implementation Plan: Sustained Purring

**Branch**: `009-orthogonal-interactions` (shared batch branch) | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-sustained-purring/spec.md`

## Summary

Purring stops being a single-tick action and becomes engine-managed kitty
state: a `purr_phase` in the tick (running right after needs and happiness
settle, in stable kitty-id order) starts a purr when it is earned (the
existing rule, unchanged) and the cooldown has passed, draws its duration
from the world's seeded RNG between the configured min and max, emits the
purr meow exactly once at start, ends the purr when its clock runs out, and
starts the cooldown. Two serde-defaulted fields on `Kitty`
(`purring_until`, `purr_cooldown_until`) carry the state through snapshots
and the API; old saves load quiet and immediately eligible. The behaviors'
purr proposals are deleted — no turn is ever spent purring — and the `Purr`
action retires: the enum variant survives *only* because `last_action` is
serialized in old snapshots (wire compatibility), but validation now
resolves it to Idle unconditionally. The viewer appends a gentle
`· purring 💕` to a rumbling kitty's card line.

## Technical Context

**Language/Version**: Rust, stable toolchain; vanilla JS viewer (one-line cue)

**Primary Dependencies**: none new

**Storage**: snapshots gain the two kitty fields, `#[serde(default)]` both
ways — pre-011 saves load with every kitty quiet (FR-007); the existing
old-JSON kitty fixture test proves it

**Testing**: unit tests for the phase, config, retired action; a purr-rhythm
property run in `welfare_longrun.rs`; existing determinism/replay suites
cover the new RNG draw and state round-trip

**Target Platform**: unchanged

**Project Type**: engine tick-phase + config + one-line client change

**Performance Goals**: O(kitties) per tick, one RNG draw per purr start

**Constraints**: determinism (draws in stable id order from the world RNG);
Article I/II untouched (purring is pure charm — zero effect on needs,
happiness, or welfare arithmetic); zero required config edits

**Scale/Scope**: config.rs, kitty.rs, world.rs, action.rs,
behavior/needs_driven.rs, behavior/playful.rs, client/app.js, 3 tomls, tests

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design. PASS on both.*

| Article | Check | Verdict |
|---------|-------|---------|
| I — Cannot Suffer | Purring changes no need or happiness arithmetic; it reads happiness, never writes it. Welfare suite re-run. | ✅ PASS |
| II — Cannot Die | Untouched. | ✅ PASS |
| III — Cannot Be Alone | Untouched. | ✅ PASS |
| IV — Engine Is Law | Strengthened: purring moves *inside* the engine; behaviors can no longer propose it, and a stale/external `purr` proposal validates to Idle like any illegal proposal (FR-006). | ✅ PASS |
| V — Deterministic | Duration draws flow through the single world RNG in stable kitty-id order within a fixed-position phase; state serializes; the 5k-replay and save/restore suites re-verify. | ✅ PASS |
| VI — Spec-First | Spec approved first; three named tunables in config (`[purr] min_ticks / max_ticks / cooldown_ticks` — the spec's `purr_*_ticks` names, spelled as a table; spec FR-004 reconciled in the same change), validated, documented in the shipped worlds, tests amended together. | ✅ PASS |

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-sustained-purring/
├── spec.md          # approved (FR-004 spelling reconciled at implement time)
├── plan.md          # this file
├── research.md      # R1–R7
├── data-model.md    # PurrConfig + the two Kitty fields
├── quickstart.md    # validation guide
├── contracts/
│   └── purr-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config.rs                  # [purr] table: min_ticks/max_ticks/cooldown_ticks,
│                              # serde-defaulted whole-table, validated
├── kitty.rs                   # purring_until: Option<u64>, purr_cooldown_until: u64
├── world.rs                   # purr_phase in the tick (after advance_needs);
│                              # purr meow recorded at start, bypassing the
│                              # proposal cooldown gate (state announcement)
├── action.rs                  # Purr validates to Idle (variant kept for old
│                              # last_action wire compat); apply arm now a no-op
└── behavior/
    ├── needs_driven.rs        # purr proposal block deleted
    └── playful.rs             # purr proposal block deleted

client/app.js                  # ` · purring 💕` appended to the card line when
                               # purring_until is set (old 'purr' case kept for
                               # restored last_action frames)
cloudkitty.toml (+16/48)       # documented [purr] section
crates/cloudkitty-core/tests/welfare_longrun.rs   # purr-rhythm property run
```

**Structure Decision**: the engine owns purring end to end; behaviors lose
code, gain nothing — the cleanest possible Article IV posture.

## Phase 0 → Phase 1 artifacts

- Research decisions (R1–R7): [research.md](./research.md)
- State + config model: [data-model.md](./data-model.md)
- Config/API/wire contract: [contracts/purr-contract.md](./contracts/purr-contract.md)
- Runnable validation: [quickstart.md](./quickstart.md)
