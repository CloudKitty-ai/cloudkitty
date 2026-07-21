# Tasks: Approach Etiquette ("Wait for me!")

**Input**: Design documents from `/specs/012-approach-etiquette/`

**Tests**: included (the dance regression is the point).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Baseline green at HEAD `edc7d33` (verified at 011 completion)

## Phase 2: Foundational

- [X] T002 In `crates/cloudkitty-core/src/meow.rs`: add
      `MessageKind::WaitForMe` — variant, `ALL` (now 7), `related_need` →
      `None`, `text()` → "Wait for me!"; extend the vocabulary tests (wire
      name `wait_for_me`, base cooldown class)
- [X] T003 [P] In `client/render.js`: add `wait_for_me: 'Wait for me!'` to
      `MEOW_TEXT` (bubbles and the card meow line both read this map)

## Phase 3: US1+US2 — the yield rule (P1/P2)

- [X] T004 [US1] In `crates/cloudkitty-core/src/behavior/selection.rs`: add
      `should_wait_for(ctx, friend_id, friend_pos) -> bool` (kitty target at
      exactly Manhattan 2 ∧ my id higher ∧ even world tick, plan R1/R4) and
      consult it in `play_action_with` before returning `Chase(kitty)` —
      yielding proposes `Meow { WaitForMe }`
- [X] T005 [US1] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      consult the same helper in the cuddle arm before `step_toward`
- [X] T006 [US1] Unit tests (selection.rs / needs_driven.rs): higher id at
      d2 on an even tick yields WaitForMe; odd tick steps; lower id steps;
      d≠2 untouched — for both the cuddle and play paths
- [X] T007 [US1] New `crates/cloudkitty-core/tests/approach_etiquette.rs`:
      the pinned reproduction — mutual cuddle pair (diagonal start) reaches
      Resting ≤ 6 ticks with ≥ 1 WaitForMe recorded; same with every
      need-meow cooldown maxed (FR-003); mutual play-chase pair lands its
      pounce; passive-partner approach arrives within 1 tick of the direct
      walk (FR-004)

## Phase 4: US3 — nothing new stalls (P3)

- [X] T008 [US3] Full suite: `cargo test --workspace` — welfare bounds,
      determinism replay, 009/010/011 guards all green

## Phase 5: Polish

- [X] T009 Gates: clippy `-D warnings`, fmt, `node client/test-meadow.mjs`
- [X] T010 Demo: rebuild + relaunch `:8093`; watch for the bubble (SC-004)

## Dependencies

```text
T001 → T002 → T003 [P] → T004 → T005 → T006 → T007 → T008 → T009 → T010
```

## Implementation notes (2026-07-20, all tasks complete)

- **FR-008 added mid-implementation**: the welfare gate surfaced the
  etiquette's sibling — three kitties in head-on transit (different targets,
  opposing directions) sidestepping N/S in lockstep for 47 ticks (probe:
  ticks 1329–1365). The id/parity rule cannot reach it (the dancers are not
  each other's targets), so the sidestep fallback now draws from the kitty's
  own seeded decision RNG among free (dry-preferred) tiles — deterministic
  per Article V, never synchronized between kitties. Spec amended (FR-008 +
  edge case) in the same change; `the_sidestep_fallback_prefers_a_dry_tile`
  re-asserted as a property (dry legal Move) rather than a pinned direction.
- **Verification evidence**: 224 lib tests + all suites green — the pinned
  reproduction resolves ≤ 6 ticks (was 145 silenced) in both meow flavors,
  the mutual play-chase lands ≤ 10, the 20k welfare bounds pass with both
  fixes live, determinism replay green, clippy/fmt/meadow green. Demo
  relaunched on :8093.
