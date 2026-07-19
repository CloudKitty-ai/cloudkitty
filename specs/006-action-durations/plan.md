# Implementation Plan: Action Durations

**Branch**: `006-action-durations` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-action-durations/spec.md`

## Summary

Every need-relieving action (eat, drink, sleep, play, cuddle, bath) becomes an
engine-enforced multi-tick activity with configurable min/max duration
(defaults: min 2 everywhere; max 5 for eat/drink/play/bath; max 8 for
sleep/cuddle), full per-tick relief, need-zero early termination after the
minimum, and shared-clock duets for cuddle and social play. Technically: the
existing `Activity` state machine (today only `Resting`/`Sleeping`) is
extended to all six activities plus an `activity_clock` bookkeeping field on
`Kitty`; enforcement wraps the existing validate→apply pipeline in the apply
phase (a duration-enforcement step before apply, an end-resolution step after
all applies), exactly where `update_pursuit` already lives. No behavior
(selection) changes; no viewer changes; additive API and config only.

## Technical Context

**Language/Version**: Rust (stable, 2021 edition; workspace toolchain unchanged)

**Primary Dependencies**: serde/serde_json (state + wire), rand_chacha (seeded RNG, untouched), axum (server, untouched), proptest (property suite)

**Storage**: JSON snapshot file (`snapshot.json`); pre-006 snapshots are not supported (strict load validation, clean refusal — backwards compatibility waived 2026-07-19)

**Testing**: cargo test --workspace; property tests (invariants_proptest), long-run welfare suite (welfare_longrun), frozen-state regression (stuck_state_regression), server integration tests; CI gate: fmt + clippy -D warnings + full suite

**Target Platform**: server binary (macOS/Linux); client static files unchanged by this feature

**Project Type**: Rust workspace — `crates/cloudkitty-core` (engine) + `crates/cloudkitty-server` (HTTP/WS); all 006 work lands in core, plus server contract tests

**Performance Goals**: no regression to tick throughput (bookkeeping is O(kitties) per tick); 20k-tick test runs stay in CI budget (~1 min total suite)

**Constraints**: determinism (same seed+config+ticks → identical world, including activity timelines); additive-only API (the in-repo viewer needs zero changes); no backwards compatibility required (pre-006 snapshots refused cleanly; frozen test fixtures migrated as assets)

**Scale/Scope**: 3 kitties / 32×32 default world; ~6 files touched in core (`kitty.rs`, `action.rs`, `world.rs`, `config.rs`, `invariants.rs`, behavior context read-only), test suites, `cloudkitty.toml`, spec-001/004 doc pointers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I (Kitties Cannot Suffer)** — PASS, strengthened. Per-tick full
  relief raises total relief per undertaking; need-zero termination frees
  time for other needs. The only new latency is the minimum lock: a newly
  urgent need can be deferred at most `min` ticks (default 2) while an
  activity finishes its floor — bounded, small, and far below distress
  timescales (safeguard 75 → distress 90 takes many ticks at configured
  need-growth rates). Safeguard spawner, distress events, happiness floor
  untouched. Welfare suite re-baselined, never loosened below 004 bounds.
- **Article II (Cannot Die)** — PASS. No removal path added; expiry still
  applies only to elements (an expired element *ends an activity*, never
  harms a kitty).
- **Article III (Cannot Be Alone)** — PASS. Untouched.
- **Article IV (Engine Is the Law)** — PASS, strengthened. Duration floors
  and caps are engine-enforced facts, not behavior courtesy: proposals
  during the minimum are superseded by continuation; the cap ends activities
  regardless of proposals; the duet conscription is the engine recording a
  lawful shared action for both participants. Malformed/invalid proposals
  still resolve to Idle — and Idle during an activity continues it, exactly
  as today.
- **Article V (Server-Authoritative, Deterministic)** — PASS. The four-phase
  tick order is unchanged; duration enforcement and end-resolution are
  bookkeeping inside phase 2 (apply), the same slot `update_pursuit`
  occupies. All new state (`activity_clock`, extended `Activity`) is part of
  the serialized world, so save/resume mid-activity is exact. No new
  randomness.
- **Article VI (Spec-First, Test-Guarded)** — PASS. All bounds live in
  `[actions.durations]` config with documented defaults and startup
  validation; property suite extended to guard min/max/need-zero invariants;
  spec + code + tests move together (001/004 contract docs get pointers).

*Post-design re-check (after Phase 1)*: PASS — no violations introduced by
the design below; Complexity Tracking stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/006-action-durations/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── behavior-delta.md   # what behaviors see / how proposals are treated
│   └── http-api-delta.md   # additive wire changes
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── kitty.rs         # Activity gains Eating/Drinking/Playing/Grooming variants;
│                    # Kitty gains activity_clock: Option<ActivityClock>
├── action.rs        # apply() starts/continues activities; continue_current_activity
│                    # generalized to all six; duet start conscription
├── world.rs         # tick(): duration enforcement before apply, end-resolution
│                    # after applies (beside update_pursuit); availability split
│                    # (is_conscriptable_friend)
├── config.rs        # [actions.durations] DurationBounds × 6, defaults + validation
├── invariants.rs    # clock sanity, duet symmetry, cap adherence
└── behavior/        # NO selection changes; reads activity_clock via ctx only

crates/cloudkitty-core/tests/
├── welfare_longrun.rs        # re-baselined bounds (SC-003)
├── stuck_state_regression.rs # still green (faster recovery expected)
├── invariants_proptest.rs    # mid-activity round-trip + strict legacy refusal
├── behavior_variation.rs     # unchanged expectations re-verified
└── activity_durations.rs     # NEW: SC-001/002/004/005/006 instrumented runs

crates/cloudkitty-server/tests/
└── server_integration.rs     # additive wire assertions (activity_clock, new
                              # activity states, durations in /config echo)

cloudkitty.toml               # [actions.durations] defaults with comments
specs/001-cloudkitty-mvp/     # data-model / behavior / http-api pointers to 006
specs/004-fix-happiness-lockin/ # note: welfare baselines superseded by 006
```

**Structure Decision**: single-workspace layout as shipped by 001/004; all
simulation changes in `cloudkitty-core`, contract-surface tests in
`cloudkitty-server`, zero client changes.

## Complexity Tracking

No constitution violations to justify — table intentionally empty.
