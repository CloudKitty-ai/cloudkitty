# Tasks: Fair Turn Order

**Input**: Design documents from `/specs/013-fair-turn-order/`

**Tests**: included — the guarding property test IS the amendment's Article
VI half.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Baseline green at main (`1d4fe2d`, verified at PR #17 merge)

## Phase 2: The amendment ceremony (one change, Governance clause)

- [X] T002 Amend `.specify/memory/constitution.md`: Article V clause (2) →
      the fairness principle (owner-approved wording), version 1.1.0, Last
      Amended 2026-07-20, sync-impact report updated
- [X] T003 [US1] In `crates/cloudkitty-core/src/world.rs`: Fisher–Yates the
      gathered decisions from `self.rng` at the top of the apply phase
      (n−1 `gen_range_u32` draws, state-independent count); update the
      module doc's tick list and the Phase 2 comment to the fair-order
      wording (plan R1/R2)
- [X] T004 [US1] New `crates/cloudkitty-core/tests/turn_order_fairness.rs`:
      over ≥ 10,000 ticks of the default world, tally which kitty acts
      first each tick (via a pub(crate)-exposed draw or an observable
      proxy); assert every kitty's first-slot share within the > 6σ bounds
      (SC-001) and that id order would fail the same bounds
- [X] T005 [P] Update README.md's Article V row to the fair-turn-order
      wording

## Phase 3: Verification

- [X] T006 [US2] Full suite: `cargo test --workspace` — determinism replay
      and save/restore (FR-002/SC-002), welfare bounds and all 009–012
      guards (SC-003)
- [X] T007 Gates: clippy `-D warnings`, fmt, `node client/test-meadow.mjs`

## Dependencies

```text
T001 → T002 → T003 → T004, T005 [P] → T006 → T007
```
