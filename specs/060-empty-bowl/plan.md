# Implementation Plan: Empty-Bowl Early End (spec-006 amendment)

**Branch**: `product/empty-bowl` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/060-empty-bowl/spec.md`
(clarified 2026-10-10, Q1 ruled A)

## Summary

Amend spec 006's meal-end rule so an eating scene ends at scene-end
resolution on any tick whose feeding condition fails (the engine's own
meal predicate, `adjacent_stocked_chow`, returns nothing), even before
the scene minimum. Need-0-before-minimum still licks to the minimum.
The whole change is one condition in `World::resolve_activity_ends`
plus the rule-6 test sort and the Gen 2 stream-pin re-record it drags
along ([rng-sequence], 059 artifact pattern). Research: [research.md](research.md).

## Technical Context

**Language/Version**: Rust (workspace pin via rust-toolchain; stable)

**Primary Dependencies**: none new — `cloudkitty-core` only; `cloudkitty-rl`
and the py binding move only through re-recorded pins

**Storage**: N/A (deterministic in-memory sim; fixtures under
`crates/cloudkitty-core/tests/fixtures/`)

**Testing**: `cargo test --workspace`; red-first via
`scripts/mutate.sh --expect <prediction>`; binding pytest after a
fresh `maturin develop`

**Target Platform**: server engine (macOS dev, Linux CI)

**Project Type**: single Rust workspace, existing layout

**Performance Goals**: no new per-tick work — `out_of_chow` is already
computed in `resolve_activity_ends`; the edit re-parenthesizes it

**Constraints**: deterministic streams move ONLY inside the declared
Gen 2 `[rng-sequence]` boundary; the deployed 0.3.0 Gen 1 world and all
shipped tomls untouched (zero config edits); scene end writes no
refusal row

**Scale/Scope**: 1 engine line + ~6 test files touched/re-pinned;
1 BACKLOG entry removed at merge (FR-007)

## Constitution Check

*GATE: evaluated against constitution v1.2.0 — PASS, pre- and
post-design.*

- **Art I (no suffering)**: welfare-positive by construction — removes
  the only ticks where a held scene delivers zero relief; needs
  bounds, distress events, safeguard spawning untouched. The safeguard
  respawn path (`ensure_minimums`) is what feeds the freed cat next
  tick.
- **Art II (no death)**: expiry stays element-only; this spec reads
  element state, removes nothing.
- **Art III (never alone)**: untouched.
- **Art IV (engine is the law)**: strengthened — the end is an engine
  scene rule at resolution; no advisor can propose into or around it
  (spec US1). Behavior layer gets zero edits.
- **Art V (deterministic, fair)**: tick order unchanged;
  `resolve_activity_ends` already runs after all apply slots, so the
  rule sees post-consumption bowl state regardless of turn order.
  Stream divergence is declared, first-divergence ticks recorded,
  `[rng-sequence]` in CHANGELOG.
- **Art VI (spec-first, test-guarded)**: this plan follows the
  clarified spec; changed behavior gets red-first guards (research R4);
  no new constants (existing `[actions.durations]` bounds only, no
  magic numbers).

No violations; Complexity Tracking stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/060-empty-bowl/
├── spec.md              # clarified 2026-10-10
├── plan.md              # this file
├── research.md          # Phase 0 (R1-R7)
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── scene-end.md     # Phase 1
└── tasks.md             # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── world.rs             # THE edit: resolve_activity_ends :736-740;
│                        #   its #[cfg(test)] module: rule-6 sort
└── (action.rs, kitty.rs read-only context: validate :397,
     eat effect :792-803, bounds/clock :132-239)

crates/cloudkitty-core/tests/
├── fog_continuity.rs    # re-record declaration + fixtures
├── fixtures/*.digest    # re-recorded pins
├── evolution_golden.rs  # refusal-ring delta check, re-pin if red
└── (sweep: snapshot_resume, joint_action_parity, roam_tether,
     consent_gate, waterline_contagion)

crates/cloudkitty-rl/tests/   # sweep-only (pins may move)
bindings/ pytest              # fresh maturin develop, then run
BACKLOG.md                    # entry :90-111 out at merge (FR-007)
CHANGELOG.md                  # Unreleased + [rng-sequence]
```

**Structure Decision**: existing workspace layout; no new files outside
`specs/060-empty-bowl/` except test additions in already-existing test
modules.

## Design notes (what Phase 1 pins down)

- **The edit** (research R1): `done_naturally = (elapsed >= bounds.min
  && governed_done) || out_of_chow;` — `bounds.max` cap, `end_activity`
  routing, `duration_ruling` mid-slot hold all untouched.
- **Predicate** (R2, ⚠ owner flag): reuse `adjacent_stocked_chow`
  as-is (nearest-adjacent-then-stocked). The end rule, validate, and
  the per-tick effect must agree or SC-003 fails. Spec wording for the
  nearest-empty-beside-stocked geometry is adjusted on her word
  (research R2 states the catch).
- **No refusal interaction** (FR-003): scene ends route through
  `end_activity` only; refusal writes live only in the apply slot
  (world.rs:374-383). Pinned today by
  `duration_enforcement_decides_the_absorbed_flag_never_the_refusal`.
- **Teacher rows** (R6): absorbed Eat-over-empty-bowl refusal rows
  disappear as a consequence; no behavior edit. SC-003's zero-relief
  count and the absorbed-row drop are the welfare evidence.

## Complexity Tracking

(empty — no constitution violations to justify)
