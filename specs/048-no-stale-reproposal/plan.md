# Implementation Plan: No Stale Re-Proposal

**Branch**: `048-no-stale-reproposal` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/048-no-stale-reproposal/spec.md`

## Summary

`finish_what_you_started` (the shared scene-commitment helper) currently proposes an
activity's continuation whenever its governing need is still positive, without checking
whether the scene's counterpart is still there. The engine's `prune_dead_activity` then
ends the dead scene at the apply slot and the stale proposal validates to Idle — one
wasted tick and a spurious refusal row per occurrence (measured 2026-09-02: 554–788
critter-play rows per 20k-tick reference run, 0% ever rescued; 54–100 groom rows, ~10%
rescued; duets and drinking structurally zero).

Fix: factor the counterpart-gone match out of `prune_dead_activity` into one shared
`World` predicate, and have `finish_what_you_started` consult it against the decision
snapshot — counterpart gone means return `None`, falling through to a fresh decision the
same tick. One definition, two consumers (FR-002); no config knob (FR-006); all
behaviors move (FR-005).

## Technical Context

**Language/Version**: Rust (workspace-pinned toolchain, `rust-toolchain.toml`)

**Primary Dependencies**: none new — `cloudkitty-core` internals only

**Storage**: N/A

**Testing**: `cargo test --workspace`; mutation cycles with `--no-fail-fast` (047 standard); red-first per CLAUDE.md rules 5/6 with cycles recorded in `specs/048-no-stale-reproposal/redden-list.md`

**Target Platform**: server crate consumer; no API surface change

**Project Type**: engine behavior fix inside the existing `cloudkitty-core` crate

**Performance Goals**: N/A (the predicate is a handful of comparisons already run every tick at the apply slot; running it once more at decide time is negligible)

**Constraints**: defaults stamp byte-identical (FR-006/SC-004); golden evolution pin MOVES and is re-pinned with changelog marker (FR-008); refusal stream keeps race rows (SC-005)

**Scale/Scope**: 2 source files touched (`world.rs`, `behavior/needs_driven.rs`), plus tests and CHANGELOG

## Constitution Check

*GATE: evaluated 2026-09-02 pre-Phase-0; re-evaluated post-Phase-1 — PASS both.*

- **Article I (no suffering)**: untouched — no need semantics, thresholds, or relief change. PASS.
- **Article II (no death)**: untouched — no removal path added or altered. PASS.
- **Article III (never alone)**: untouched. PASS.
- **Article IV (engine is the law)**: strengthened in spirit — the behavior stops proposing an action the engine was always going to refuse; validation and enforcement are unchanged, and the engine still hears whatever is proposed. PASS.
- **Article V (deterministic, fixed tick order)**: preserved — the decision still reads only the start-of-tick snapshot (the predicate consults nothing else), no new randomness, tick phases untouched. The same-tick race class exists *because* we honor this article; the spec pins it out of scope rather than bending phase order. PASS.
- **Article VI (spec-first, test-guarded)**: this plan; scenario guards red-first; no new constants (there is deliberately no knob — nothing to move to config). PASS.

## Project Structure

### Documentation (this feature)

```text
specs/048-no-stale-reproposal/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── stale-scene-rule.md
├── redden-list.md       # red-first cycle record (implementation phase)
└── tasks.md             # /speckit-tasks output
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── world.rs                    # factor counterpart_gone() out of prune_dead_activity()
└── behavior/needs_driven.rs    # finish_what_you_started() consults the predicate

CHANGELOG.md                    # Unreleased entry + golden re-pin marker
```

**Structure Decision**: engine-internal fix in the existing crate; no new modules,
no API surface change (the predicate is `pub(crate)`).

## Design Decisions

- **D1 — one shared predicate**: `World::counterpart_gone(&self, kitty_id) -> bool`,
  factored verbatim from `prune_dead_activity`'s match (world.rs:476–512).
  `prune_dead_activity` becomes `if self.counterpart_gone(id) { self.end_activity(id) }`
  plus its existing early-outs — a behavior-identical refactor, guarded by the existing
  prune tests. `finish_what_you_started` is the second consumer. FR-002's no-drift
  doctrine: a mutation of the shared predicate must red both a prune witness and a
  behavior witness (test design, not new code).
- **D2 — check placement**: in `finish_what_you_started`, after the governing-need
  short-circuits (`governing_need()?`, `remaining <= 0.0`), consult
  `ctx.world.counterpart_gone(ctx.me.id)`; gone → `None`. The spec pins no ordering
  requirement (edge case: need-empty and counterpart-gone the same tick both yield a
  fresh decision); need-first keeps the hot path's existing shape.
- **D3 — no knob, identity story**: no config field at all — the defaults stamp cannot
  move (SC-004 witnessed by the existing stamp test untouched). The golden evolution
  pin moves at the first artifact tick; re-pin with the 039-style changelog marker
  (FR-008).
- **D4 — refusal stream semantics**: stale rows vanish because the proposal is never
  made; the recording site (`run_applied_phases_from_decisions`) is untouched, so race
  rows and genuine refusals stamp exactly as today (FR-007/SC-005).
- **D5 — verification instruments**: in-tree, staged scenario tests per user story
  (US1: critter moved/expired; US2: friend unavailable; plus live-counterpart
  must-stay-green pins). Out-of-tree, the 2026-09-02 probe (local branch
  `probe-reproposal-rate`, commit 275896e) re-runs on the fixed build and must report
  dead-at-snapshot re-proposals = 0 across all classes — SC-001/SC-002's end-to-end
  check on the exact reference arms.

## Complexity Tracking

No constitution violations; table not required.
