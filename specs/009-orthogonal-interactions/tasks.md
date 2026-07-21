# Tasks: Orthogonal-Only Interactions

**Input**: Design documents from `/specs/009-orthogonal-interactions/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/interaction-range-contract.md, quickstart.md

**Tests**: included — Article VI makes the amended tests part of the change
itself (spec FR-007, plan R7), and the property suite is SC-001/SC-002's
star witness.

**Organization**: grouped by user story. Note the deliberate inversion of the
usual independence rule: US1's *enforcement* mostly falls out of the
Foundational phase (R1's redefinition), so its tasks are largely guards and
the walk fix; US2 is the metric sweep; US3 is verification. Stories remain
independently *testable* in that order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (reach matches walk), US2 (honest travel judgment),
  US3 (constitution still holds)

## Phase 1: Setup

**Purpose**: a trustworthy baseline — this branch also carries the owner's
staged config tuning (cloudkitty.toml, cloudkitty16/48.toml), which must be
known-green before the feature starts changing behavior.

- [X] T001 Run `cargo test --workspace` on the branch as-is and confirm green
      (baseline including the owner's staged config changes; fix nothing yet —
      if red, stop and report before any feature work)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: R1 — the single redefinition every story inherits. No user story
may start before this lands, because all three depend on the new meaning of
`is_adjacent`.

- [X] T002 In `crates/cloudkitty-core/src/grid.rs`: add
      `Position::manhattan_distance` (`dx + dy` via `abs_diff`), redefine
      `is_adjacent` to `manhattan_distance <= 1`, scope `chebyshev_distance`'s
      doc comment to its remaining consumer (spawn spreading), and rewrite the
      module doc comment (which still documents Chebyshev adjacency as the
      spec's rule)
- [X] T003 In `crates/cloudkitty-core/src/grid.rs` tests: rewrite the
      adjacency truth table per data-model.md (same tile ✓, orthogonal
      neighbor ✓, diagonal ✗, farther ✗), add `manhattan_distance` arithmetic
      cases, keep the Chebyshev tests (still a shipped metric for spawn);
      `cargo test -p cloudkitty-core grid` green

**Checkpoint**: interaction range is orthogonal engine-wide (validation,
world helpers, counterpart checks all inherit). Expect distant test fallout —
that is the stories' work, not a regression to fix here.

---

## Phase 3: User Story 1 — Reach matches walk (P1) 🎯 MVP

**Goal**: kitties interact only from their own tile or the four compass
neighbors, and walk that final diagonal step instead of stalling (FR-001,
FR-002, FR-004; contract table in
contracts/interaction-range-contract.md).

**Independent Test**: diagonal proposals validate to Idle; a kitty diagonal
to chow repositions and eats; the long-run records zero diagonal
interactions (SC-001, SC-006).

- [X] T004 [US1] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      collapse `step_toward`'s two-part progress score `(chebyshev, manhattan)`
      to plain Manhattan, and change the sidestep fallback condition from
      `current.0 > 1` to `current > 1` so a kitty diagonal to its target
      (Manhattan 2) keeps maneuvering rather than idling (plan R3)
- [X] T005 [P] [US1] In `crates/cloudkitty-core/src/action.rs` tests: add
      diagonal-refusal validation cases per the contract — `Eat`, `Drink`, and
      `Play { target: element }` proposed by a kitty exactly diagonal to the
      element resolve to `Idle`; the same positions moved orthogonal validate
      through (FR-002)
- [X] T006 [US1] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`
      tests: add the walk-around case — a hungry kitty at `(5,5)` with chow at
      `(6,6)` proposes a Move to an orthogonal neighbor of the bowl (never
      Idle, never Eat), and from `(6,5)` or `(5,6)` proposes Eat; re-verify
      `a_blocked_cat_routes_around_a_friend_instead_of_freezing` still derives
      under the Manhattan score (FR-004). Also add the crowded-bowl case
      (analyze M1, spec Edge Cases "Crowded targets"): a hungry kitty two
      steps from a bowl whose four orthogonal neighbors are all occupied
      proposes only legal actions while crowded out (Moves/sidesteps — never
      Eat from out of range, never an illegal Move), and — driven over a
      bounded run in a world with a second bowl a few tiles off — ends up
      eating from *some* bowl within that bound. Do not assert it eats from
      the contested bowl: at one serving per eater per tick a crowded bowl
      drains before the waiter's turn; retarget-and-respawn is the designed
      relief path (owner decision 2026-07-20: no new contention mechanics)
- [X] T007 [US1] Sweep every existing test fixture in
      `crates/cloudkitty-core/src/` (action.rs, world.rs, kitty.rs,
      needs_driven.rs test modules) whose positions rely on diagonal
      adjacency, and re-derive positions or expectations under the orthogonal
      rule — `cargo test -p cloudkitty-core --lib` green at the end of this
      task
- [X] T008 [US1] In `crates/cloudkitty-core/tests/welfare_longrun.rs`: add the
      per-tick assertion that every kitty in an Eating or Drinking scene has
      an element of the matching type within Manhattan 1 of its position
      (SC-001's "zero diagonal interactions", enforced over the suite's
      randomized hostile runs)

**Checkpoint**: US1 fully testable — diagonal interactions impossible, walks
finish beside the target, unit tests and long-run green.

---

## Phase 4: User Story 2 — Honest travel judgment (P2)

**Goal**: every decision distance and the chase-progress tracker measure
walking steps (FR-005, FR-006; plan R2/R4). Config untouched.

**Independent Test**: nearest-target choices order by Manhattan with fixed
tie-breaks; a diagonal→orthogonal conversion resets chase patience;
selection's exact-score tests re-derive and pass.

- [X] T009 [US2] In `crates/cloudkitty-core/src/world.rs`: switch every
      decision-path `chebyshev_distance` to `manhattan_distance` —
      `adjacent_element` tie-break, both `nearest_element`s (World and
      WorldSnapshot), `nearest_critter`, `nearest_friend`, and
      `update_pursuit`'s closing distance (plan R2, R4); tie-break shapes
      `(distance, [tag,] id)` unchanged
- [X] T010 [US2] In `crates/cloudkitty-core/src/world.rs` tests: add the
      pursuit-progress case — a chase whose target goes from diagonal offset
      (1,1) (Manhattan 2) to orthogonal (0,1) (Manhattan 1) counts as gaining
      ground and resets the patience clock (spec US2 scenario 2); re-derive
      any pursuit-test distances that were Chebyshev by construction
- [X] T011 [P] [US2] In `crates/cloudkitty-core/src/behavior/selection.rs`:
      switch all distances to `manhattan_distance` — `distance_given`'s
      nearest lookups, `sleep_travel_distance`, `play_travel_distance`,
      `nearest_viable_playmate` ordering, `play_action_with`'s reach test,
      `adjacent_playmate` tie-breaks; update the module doc's scoring formula
      comment if it names a metric
- [X] T012 [US2] In `crates/cloudkitty-core/src/behavior/selection.rs` tests:
      re-derive every exact-score and distance expectation under Manhattan
      (the `miso_ctx` worked example 150/147/146.7, `sleep_is_priced_at_the_
      walk` distance 8, playmate orderings, `pursuing_ctx` geometry) — keep
      the *properties* identical, recompute the numbers, and update the R1
      worked-example comment to match. Execution note (analyze L2): the
      miso runner-up ordering *flips* — the bug at (22,27) from (21,30) is
      Manhattan 4 (was Chebyshev 3), so play = 100 + 50 − 4 = 146, dropping
      below sleep 146.7; bath still wins at 150. Expected, not a regression:
      assert the new trio 150/146.7/146 and that bath is chosen
- [X] T013 [P] [US2] In `crates/cloudkitty-core/src/behavior/needs_driven.rs`:
      switch the remaining decision distances to `manhattan_distance` — the
      sunbeam-reach test in the sleep arm, the free-friend ordering in the
      cuddle arm, `seek_element`'s usable tie-break — and re-derive any
      distance-dependent expectations in this file's tests

**Checkpoint**: one metric everywhere a decision looks; `cargo test -p
cloudkitty-core` fully green; `grep -n chebyshev` in `src/` matches only
`grid.rs` and `spawn.rs`.

---

## Phase 5: User Story 3 — The constitution still holds (P3)

**Goal**: Article I re-verified under the stricter range; old saves resume
gracefully; determinism intact (FR-003, FR-007, FR-008; plan R6/R7).

**Independent Test**: full property suite green with tightened assertions; a
constructed stranded-diagonal scene ends within one tick; save/restore
determinism tests pass.

- [X] T014 [US3] In `crates/cloudkitty-core/src/world.rs` (or action.rs,
      wherever the counterpart-end tests live) add the old-snapshot
      compatibility case: construct a kitty mid-Eating whose only bowl sits
      diagonal (a pre-009 save's legal state), advance one tick, assert the
      scene ends via the counterpart-gone rule and the kitty re-plans — no
      panic, no stuck activity (FR-003, SC-003)
- [X] T015 [US3] In `crates/cloudkitty-core/tests/welfare_longrun.rs`: review
      the relief/companionship assertions that inherit `is_adjacent` (chow/
      water/friend "nearby" checks) and confirm they assert the intended
      orthogonal meaning; then run the full property suite and the
      persistence/determinism tests — `cargo test --workspace` green,
      including save/restore determinism (SC-002, SC-004)

**Checkpoint**: all three stories verified; constitution gates green.

---

## Phase 6: Polish & Cross-Cutting

- [X] T016 Comment sweep across `crates/cloudkitty-core/src/`: `grep -rn
      -i "chebyshev\|diagonal\|king-move"` and update every stale prose
      mention of the old geometry (selection.rs module doc, needs_driven.rs
      step_toward comment, kitty.rs pursuit docs if any) so no comment
      describes the pre-009 rules as current
- [X] T017 Scope check per quickstart §2: `git diff main -- client/
      crates/cloudkitty-server/ crates/cloudkitty-core/src/spawn.rs` is empty,
      and the feature added zero lines to any `cloudkitty*.toml` (the owner's
      staged tuning is the only config diff on the branch) (plan R8, SC-005,
      FR-009)
- [X] T018 Full gates: `cargo test --workspace`, `cargo clippy --workspace
      --all-targets -- -D warnings`, `cargo fmt --all -- --check`,
      `node client/test-meadow.mjs` — all green
- [X] T019 Watchable proof (SC-006): launch a throwaway demo world per
      quickstart §3 (config copy in `$CLAUDE_JOB_DIR/tmp`, snapshot in /tmp —
      never the live save) and confirm kitties take up orthogonal positions
      beside bowls/puddles/friends before interacting; leave it running and
      offer it to the owner to watch

---

## Dependencies & Execution Order

```text
Phase 1 (T001)          baseline
   ↓
Phase 2 (T002 → T003)   the redefinition everything inherits — BLOCKS all stories
   ↓
Phase 3 (US1)           T004 → T006 (same file);  T005 [P] alongside T004
                        T007 after T004–T006 (sweeps whole crate)
                        T008 after T007 (long-run needs green lib tests)
   ↓
Phase 4 (US2)           T009 → T010 (same file);  T011 → T012 (same file);
                        T013 [P] with T009/T011 chains (different file);
                        T009/T011/T013 chains mutually parallel
   ↓
Phase 5 (US3)           T014 → T015 (T015 runs the whole workspace)
   ↓
Phase 6                 T016 → T017 → T018 → T019
```

US2 could technically start immediately after Phase 2, but running it after
US1's crate-wide fixture sweep (T007) avoids re-deriving the same tests
twice — the order above is the low-churn order.

## Parallel Opportunities

- **US1**: T005 (action.rs tests) alongside T004 (needs_driven.rs)
- **US2**: three same-file chains in parallel — T009→T010 (world.rs),
  T011→T012 (selection.rs), T013 (needs_driven.rs)
- Everything else is intentionally sequential (same files, or
  whole-workspace verification steps)

## Implementation Strategy

**MVP = Phase 1–3 (US1)**: after T008 the feature's visible promise holds —
no diagonal interactions, walks finish beside targets — even before the
scoring sweep. **Incremental delivery**: US2 makes the choices honest, US3
certifies the constitution, Polish proves the clean diff. Ship as one commit
series on this branch (per the owner: one branch for the 009/010/011 batch),
`/speckit-implement` next.

## Implementation notes (2026-07-20, all tasks complete)

- **T008 refined during implementation**: the per-tick *Eating* assertion as
  written is unsound post-tick — the suite's own determinism proved it twice
  (tick 134: a lawful meal begun on a bowl's last serving, bowl consumed and
  expired the same tick; tick 2343: `ensure_minimums` respawned a bowl
  diagonal to the eater in the same environment phase). Post-tick element
  positions cannot identify a meal's bowl, so the long-run asserts what is
  soundly observable — Drinking (permanent, stationary water) and conscripted
  duets (both clocked) every tick — while the meal-range rule is enforced at
  its true seam: `validate` + `adjacent_stocked_chow` gate entry and every
  serving through orthogonal `is_adjacent`, unit-tested in `action.rs`
  (diagonal-refusal) and exercised by the crowded-bowl run. Rationale
  recorded in `assert_orthogonal_scenes`'s doc comment.
- **T014 landed in `welfare_longrun.rs`** (not world.rs/action.rs): posing a
  mid-scene world and driving a real tick needs the registry + async driver
  that file already owns.
- **One ripple beyond the plan's file list**: `invariants.rs`'s pursuit
  plausibility bound was Chebyshev-derived (`max(width, height)`); a lawful
  Manhattan distance of 34 tripped it at tick 12197. Bound is now
  `width + height`. Constitution-check verdicts unchanged.
- **Checkpoint evidence**: mid-migration (US1 done, US2 pending) the welfare
  suite flagged Pumpkin below happiness 45 for 37 consecutive ticks — the
  predicted score/walk disagreement; it vanished exactly when US2 made
  scoring honest. The full suite (20k-tick bounds, determinism, crowded
  bowl, stranded scenes) is green, as are clippy, fmt, and the meadow
  harness.
