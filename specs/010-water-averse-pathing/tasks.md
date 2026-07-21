# Tasks: Water-Averse Pathing

**Input**: Design documents from `/specs/010-water-averse-pathing/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/water-cost-contract.md, quickstart.md

**Tests**: included (Article VI; the stepper ordering and the pricing
arithmetic are the automatable core, plan R7).

**Organization**: US1 (kitties skirt their ponds) is the stepper; US2
(distant targets priced honestly) is the estimate; US3 (never stuck) is
verification. The config field is foundational to both stories.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Confirm the branch baseline is green (`cargo test --workspace`) —
      the 009 completion state, with both batch commits (`0eb812c`,
      `e9a9772`) in

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T002 In `crates/cloudkitty-core/src/config.rs`: add
      `water_step_cost: f32` to `BehaviorConfig` in the established mold —
      doc comment, `#[serde(default = "default_water_step_cost")]` → 4.0,
      entry in the `Default` impl, and validation rejecting non-finite or
      negative values with the standard naming-the-field error (plan R4,
      contract)
- [X] T003 In `crates/cloudkitty-core/src/config.rs` tests: the default
      applies when the key is absent (parse a `[behavior]` table without it),
      and a negative value is rejected with an error naming
      `water_step_cost`
- [X] T004 [P] Document the new key in all three shipped world files
      (`cloudkitty.toml`, `cloudkitty16.toml`, `cloudkitty48.toml`): the
      contract's commented line under `[behavior]`, value 4.0 — the only
      config diff this feature makes

## Phase 3: User Story 1 — Kitties skirt their ponds (P1) 🎯 MVP

**Goal**: dry improving steps beat wet ones; wading only when wet is the
only way forward; a soggy kitty gets out (FR-001, FR-002, FR-005; plan R1/R2).

**Independent Test**: stepper unit cases plus a crafted world where the
skirt and the wade are both observed deterministically.

- [X] T005 [US1] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      re-order `step_toward` among improving steps by
      `distance + water_step_cost × is_water(dest)` (ties to direction order),
      and make the sidestep fallback prefer the first *dry* free direction
      before any free direction — same candidate set as 009, new ordering
      only (plan R1). Add an `is_water(world, pos)` lookup local to the
      behavior layer if none exists
- [X] T006 [US1] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`
      tests: four stepper cases — (a) dry and wet both improve → dry chosen;
      (b) only wet improves → wade (never Idle); (c) nothing improves,
      fallback prefers the dry free tile; (d) kitty standing on water with an
      equal dry option steps off (FR-005)
- [X] T007 [US1] In `crates/cloudkitty-core/tests/welfare_longrun.rs`: the
      crafted skirt/wade run (plan R7.4) — one posed world where an off-axis
      approach yields a dry walk around the pond (assert: target reached, no
      tick on a water tile), one where the target sits dead across a strip
      (assert: target reached, wading observed); both deterministic, bounded
      tick budgets

## Phase 4: User Story 2 — Distant targets priced honestly (P2)

**Goal**: one `priced_travel` estimate shared by score and walk; the bowl
chosen is the bowl walked to (FR-003 default in force, FR-004; plan R3).

**Independent Test**: pricing arithmetic unit cases; the 4-across-water bowl
loses to the 6-dry bowl; an only-option bowl is still chosen.

- [X] T008 [US2] In `crates/cloudkitty-core/src/behavior/selection.rs`: add
      `priced_travel(from, to, world, config)` — Manhattan + water_step_cost
      per water tile on the dominant-axis-first L-path, endpoint excluded —
      and switch `distance_given`'s eat/drink arms to choose the element
      minimizing `(priced_travel, id)` (returning that priced distance as the
      score's travel term); price the sleep estimate through the same helper
- [X] T009 [US2] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      make `seek_element` walk toward the *same* priced choice `selection`
      makes (shared helper, no second arithmetic), and keep `pursue`'s
      sunbeam-reach comparison the mirror of the priced sleep estimate (the
      004 agreement rule); cuddle's travel estimate prices through the helper
      too, playmates stay unpriced (plan R3 scope decision, comment it)
- [X] T010 [US2] In `crates/cloudkitty-core/src/behavior/selection.rs` tests:
      L-path arithmetic incl. endpoint exclusion and a dogleg with water on
      one leg; the US2 acceptance case (bowl at priced 4+2×4 loses to dry
      bowl at 6 under default cost); the only-option case (bowl across water
      is still selected and pursued); score/walk agreement (chosen element ==
      walked-toward element)

## Phase 5: User Story 3 — Never stuck, never trapped (P3)

**Goal**: constitution re-verified with the preference live (FR-006, FR-007).

- [X] T011 [US3] Full suite: `cargo test --workspace` — welfare 20k-tick
      bounds, orthogonal-scene assertions, determinism replay, crowded bowl,
      stranded scenes, all green with `water_step_cost` at its default in the
      test/default configs
- [X] T012 [US3] Scope check per quickstart §2: zero diff vs `e9a9772` in
      `client/`, `crates/cloudkitty-server/`, and engine files (action.rs,
      world.rs, spawn.rs, invariants.rs); config diffs are exactly the three
      documented lines (T004)

## Phase 6: Polish & Cross-Cutting

- [X] T013 Gates: `cargo clippy --workspace --all-targets -- -D warnings`,
      `cargo fmt --all -- --check`, `node client/test-meadow.mjs`
- [X] T014 Watchable check (SC-003): the demo world on `127.0.0.1:8093`
      picks up the new stepper on restart (rebuild + relaunch with the same
      throwaway config); note for the owner where to look (quickstart §4)

## Dependencies & Execution Order

```text
T001 → T002 → T003, T004 [P]
     → US1: T005 → T006 → T007
     → US2: T008 → T009 → T010   (US2 starts after T005 lands to share the
                                  is_water helper; T008 [P] with T006/T007)
     → US3: T011 → T012
     → T013 → T014
```

## Implementation Strategy

**MVP = through T007**: the visible skirting ships with US1 alone. US2 makes
target *choice* match the walk's taste; US3 certifies. One commit on the
shared batch branch when green.

## Implementation notes (2026-07-20, all tasks complete)

- **`priced_travel` follows the dominant-axis staircase, not a strict L**:
  it steps with the existing `Direction::toward` primitive (the exact path a
  naive walk would take), which is the same deterministic straight-line
  proxy R3 intended, reusing a tested primitive instead of new geometry.
- **The welfare gate caught a latent livelock, fixed here**: with the 010
  trajectory shuffle, the 20k-tick run found Miso and Pumpkin locked in a
  mirrored period-2 shuffle in the row-0 corridor for ~60 ticks (probe log:
  ticks 16221–16280) — Miso's equal-cost tie between North and East kept
  resolving to fixed-order North, steering it back into the contested lane.
  Root cause predates 010 (any trajectory could hit it); fix is in the same
  stepper this feature touches: candidate directions are now tried
  **dominant-axis first** (the `Direction::toward` rule), so equal-cost ties
  close the larger gap and keep both axes improvable — which also gives the
  water surcharge dry alternatives to pick. Two direction-expectation tests
  re-derived (`crowded bowl` shuffle West, `fallback prefers dry` North).
- **T006's fallback test geometry adjusted** to stay discriminating under
  the new preference order (water on the first-in-order sidestep, dry
  expectation on the second).
- **Verification evidence**: full workspace suite green (215 lib + 6
  welfare/crafted runs incl. skirt-with-dry-paws and wade-when-dead-ahead),
  clippy, fmt, meadow harness; engine files zero-diff vs the 009 commit;
  demo world relaunched on :8093 serving `water_step_cost = 4.0`.
