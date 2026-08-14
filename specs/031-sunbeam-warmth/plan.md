# Implementation Plan: Shared Sunbeam Warmth

**Branch**: `031-sunbeam-warmth` | **Date**: 2026-08-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/031-sunbeam-warmth/spec.md`

## Summary

One engine rule in one function: when a Sleeping kitty's direct cosleep
partner is mutual (Sleeping or Resting, the FR-014/15 predicate the code
already computes) and the partner's tile holds a sunbeam, the sleeper's
Sleep relief runs at `sleep_relief_sunbeam` instead of `sleep_relief`. The
change lands entirely inside `apply_sleep_relief`
(`crates/cloudkitty-core/src/action.rs:777`), which already receives the
partner and the own-tile sunbeam flag and already computes the mutual
predicate three lines below where the rate is chosen. No new config, no
schema change of any kind, no RNG-sequence change; the test battery extends
the existing cosleep/sunbeam tests in the same module.

## Technical Context

**Language/Version**: Rust (workspace, existing toolchain).

**Primary Dependencies**: None — `cloudkitty-core` only, no new crates.

**Storage**: N/A — no persisted state; the rule reads live world state.

**Testing**: `cargo test -p cloudkitty-core` unit tests in the `action.rs`
test module (direct precedents: `sleeping_in_a_sunbeam_is_more_restful`,
`cosleep_pays_the_tier_the_partners_presence_earns`,
`cosleep_dials_never_touch_the_duet_or_the_groomer`); the existing engine
property suites and `cloudkitty-rl` welfare suites as regression gates.

**Target Platform**: Wherever the engine runs; no platform-specific code.

**Performance Goals**: Negligible — at most two additional read-only
lookups (`world.kitty(partner)` for pos, `world.element_at(partner_pos)`)
per serviced tick of a Sleeping-with-partner kitty, on a path that already
does equivalent lookups.

**Constraints**: Deterministic — reads only start-of-tick state already
consulted by the relief path; no new randomness. Relief only increases
where the rule fires (constitution posture).

**Scale/Scope**: One function body (~6 lines), one helper predicate at
most, ~5 new unit tests. The smallest spec-first change this repo has
shipped in a while, deliberately.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1 — no change.*

- **Article I (kitties cannot suffer)**: Relief only increases where the
  rule fires; needs stay bounded through the existing `lower_need` clamp.
  No new need pressure, no distress mechanics touched. **PASS.**
- **Article II (kitties cannot die)** / **Article III (never alone)**: Not
  touched. **PASS.**
- **Article IV (engine is the law)**: The rule lives in the engine's
  relief application, not in any behavior; no proposal or validation
  change. Scripted decision paths untouched (`sunbeam_worth_walking` is
  distance-gated, not relief-derived). **PASS.**
- **Article V (deterministic simulation)**: The rule reads partner
  activity/position and element type from the same start-of-tick world
  state the relief path already consults; no RNG draw is added, moved, or
  reordered. Same seed + config → same world, except where the rule
  lawfully changes relief amounts — which is the feature, applied
  deterministically. **PASS.**
- **Article VI (spec-first, test-guarded, no magic numbers)**: This spec
  precedes the code; every acceptance scenario becomes a unit test
  (FR-009); the rate is the existing `sleep_relief_sunbeam` config dial —
  no new constants anywhere. **PASS.**

No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/031-sunbeam-warmth/
├── plan.md              # This file
├── research.md          # Phase 0: decisions (no open unknowns)
├── data-model.md        # Phase 1: the rule's inputs and predicate
├── quickstart.md        # Phase 1: validation scenarios
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

No `contracts/` directory: the rule is internal engine behavior with no
external interface — no wire format, no API, no artifact. The spec's FRs
are the contract.

### Source Code (repository root)

```text
crates/cloudkitty-core/
├── src/
│   └── action.rs        # CHANGED: apply_sleep_relief (line ~777) — the
│                        #   rate choice gains the conduction arm; the
│                        #   mutual predicate (computed ~line 797 for the
│                        #   cuddle tier) is hoisted so both the rate
│                        #   choice and the cuddle tier read ONE
│                        #   evaluation of it (never two potentially
│                        #   divergent copies)
└── (tests in the same file's test module — the house pattern for
     action-effect tests)
```

**Structure Decision**: Single-file change. `apply_sleep_relief` already
has every input in scope (`world`, `partner`, `in_sunbeam`, `config`); the
conduction check is `partner`'s activity (the existing `mutual` predicate)
plus `world.element_at(world.kitty(partner).pos)`. Hoisting the `mutual`
computation above the rate choice keeps one evaluation feeding both the
Sleep rate and the Cuddle tier, so the two can never disagree about
whether the pile is mutual.

## Complexity Tracking

No constitution violations to justify.
