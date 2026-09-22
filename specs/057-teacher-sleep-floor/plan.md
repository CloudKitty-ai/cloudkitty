# Implementation Plan: Teacher sleep rule reads the floor

**Branch**: `057-teacher-sleep-floor` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/057-teacher-sleep-floor/spec.md`

## Summary

The scripted `needs_driven` teacher's sleep pressure becomes the
relief a nap would deliver — `max(need − sleep_floor_off_beam, 0)`
when no warm option is in play, the raw need otherwise — with a
zero-pressure skip so worthless naps neither win nor start by default.
One substitution point in `selection.rs::scored()` (research D3), one
composed predicate from three existing helpers (D4), one skip gate
mirroring the engine's own floor gate (D5). Floor 0 is byte-identical;
nothing deploys.

## Technical Context

**Language/Version**: Rust, repo-pinned toolchain (see rust-toolchain)

**Primary Dependencies**: none new — `cloudkitty-core` internals only

**Storage**: N/A (pure decision-time function; no state, no schema)

**Testing**: `cargo test -p cloudkitty-core`; `scripts/mutate.sh --expect`
for the rule-5 red; cert leg `kitty-eval --brain needs_driven` on
`anchor-b3.toml`; Experiments' tier 5 comparator leg off-repo

**Target Platform**: engine crate (server + lab both consume it)

**Project Type**: single Rust workspace, existing layout

**Performance Goals**: N/A — three O(1)/already-computed checks per
sleep score; no new scans

**Constraints**: floor-0 byte equivalence including RNG draw order and
tie-breaks (FR-004); no observation/schema change (FR-005); no config
key added (056's key is read, not defined)

**Scale/Scope**: two functions in `selection.rs`, one helper use in
`needs_driven.rs` scope check, fixtures in both test modules; est.
< 100 lines of non-test diff

## Constitution Check

*GATE: evaluated pre-Phase 0; re-checked post-Phase 1 — PASS both.*

- **Article I (no suffering)**: needs stay bounded; the rule changes
  proposals, not need dynamics. CORRECTED at review round 2: the
  original claim here ("the safeguard guarantees a reachable sleep
  resource") was FALSE — `spawn.rs` safeguard-spawns Eat and Drink
  only, and nothing ever spawns a sunbeam on demand. Under a floor,
  sleep welfare rides beam density (the owner's 2026-09-20 caveat),
  and the urgency knee for off-beam sleep sits at safeguard + floor
  (90 at the ruled floor 15 — exactly the distress line). The
  empirical check is SC-003 on the ruled package world (passed:
  happiness up, zero distress seeds); the structural bound
  (floor vs safeguard) is an OPEN OWNER CALL recorded at review,
  deferred by validate.rs's own comment. PASS on the ruled world,
  conditional on that call for other floors.
- **Article II (no death)**: untouched. PASS.
- **Article III (never alone)**: untouched. PASS.
- **Article IV (engine is law)**: the teacher is the built-in advisor;
  it still proposes only legal actions, and the skip gate falls
  through to existing behavior, never to an error. PASS.
- **Article V (deterministic)**: FR-004 pins RNG consumption; the new
  predicate reads state, draws nothing. PASS.
- **Article VI (spec-first, test-guarded)**: this plan follows spec
  057; fixtures + mutate red + the 056 pin guard it in CI. PASS.

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/057-teacher-sleep-floor/
├── plan.md              # This file
├── research.md          # D3 substitution point, D4 predicate, D5 skip gate
├── data-model.md        # Inputs, derived values, invariants (no new state)
├── quickstart.md        # Validation runbook (unit, pin, cert leg, mutate)
├── contracts/
│   └── sleep-pressure.md  # The promise Experiments reads against (P1–P4)
└── tasks.md             # /speckit-tasks output (not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/behavior/
├── selection.rs     # scored(): effective-pressure binding + skip gate;
│                    # new warm_option_in_play() beside sunbeam_worth_walking()
└── needs_driven.rs  # no logic change expected; fixtures live in its
                     # test module beside the existing sleep tests

crates/cloudkitty-core/src/action.rs  # READ-ONLY reference: the engine
                                      # floor gate this mirrors (l.919/925)
```

**Structure Decision**: existing single-workspace layout; the change
is confined to the behavior module the spec names. No new files
outside tests.

## Phase 0 → research.md

No NEEDS CLARIFICATION existed; research.md records D3 (substitution
point: `scored()`'s pressure binding, urgency rides along), D4 (warm
option = three existing helpers composed; cuddle-cosleep walk is
deliberately not one), D5 (zero-pressure skip returns `None`, gated
`floor > 0` to keep floor-0 byte-identical).

## Phase 1 → data-model.md, contracts/, quickstart.md

Generated. Key points: no new state or config; derived values are
decision-time only; contract promises P1 (floor-0 pin), P2 (discount
never ban), P3 (no new reads), P4 (scope); quickstart maps each SC to
a runnable check and names Experiments' off-repo legs.
