# Tasks: Bugs 2.0 — the roam-cell tether

**Input**: Design documents from `specs/039-bugs2-tether/`
**Prerequisites**: plan.md, research.md (D1–D7), data-model.md,
contracts/roam-config.md, quickstart.md

**Tests**: Required — constitution Article VI plus CLAUDE.md rule 6
(every new assertion is seen red before it is trusted green). The
red-first steps are written into the tasks, not left to habit.

**Organization**: Tasks grouped by user story. US1 (tether) is the
MVP; US2 (ragged geometry) and US3 (config surface + served package)
complete the arc.

## Phase 1: Setup

- [x] T001 Verify the branch baseline: `cargo test --workspace --release`
      green and clippy clean at the branch point (039-bugs2-tether off
      main 87236c5), so every later red is caused by this arc

## Phase 2: Foundational (blocking prerequisites for all stories)

- [x] T002 [P] Add `same_roam_cell(a: Position, b: Position, n: u32) -> bool`
      to crates/cloudkitty-core/src/grid.rs (quotient-pair equality,
      origin-anchored per research D1) with partition property unit
      tests in the same file: every tile maps to exactly one cell on
      20×20/N=4 (25 cells), 26×26/N=4 (remainder strips 4×2, 2×4,
      2×2), and 5×5/N=8 (whole world one cell)
- [x] T003 [P] Add `roam_cell: Option<u32>` to `ElementRule` in
      crates/cloudkitty-core/src/config/mod.rs with
      `#[serde(default, skip_serializing_if = "Option::is_none")]`
      (research D5); run the pinned `engine_defaults_sha256` test and
      confirm it stays GREEN — if it moves, the serde attributes are
      wrong, fix before proceeding (stamp neutrality is a hard
      constraint, not a preference)
- [x] T004 Add the golden evolution digest test (new file
      crates/cloudkitty-core/tests/evolution_golden.rs): seeded
      default-config world, `roam_cell` absent, 10,000 ticks, sha256
      of the serialized world state equals a pinned constant.
      Generate the constant by running the same harness against main
      @ 87236c5 in a scratch worktree; pin it with a provenance
      comment (research D6). The test must pass on this branch before
      any behavior change lands — that green is the baseline claim.
      Test fn name MUST contain `golden_evolution` (e.g.
      `golden_evolution_flag_absent_10k_ticks`) so quickstart §2's
      filter finds it (analyze C1)

## Phase 3: User Story 1 — A bug keeps to its patch (P1) 🎯 MVP

**Goal**: a bug lives and dies inside the world-aligned cell it was
born in; greebles unaffected; cadence and RNG stream shape unchanged.

**Independent test**: quickstart §1 and §3 — confinement property run
plus cadence count, with the golden digest (§2) proving flag-absent
inertness throughout.

- [x] T005 [US1] Write the confinement property test in
      crates/cloudkitty-core/tests/roam_tether.rs: seeded worlds with
      `roam_cell = Some(4)`, ≥10 seeds, every bug's position checked
      against its birth cell every tick over full lifetimes — zero
      violations (SC-001). Run it and OBSERVE IT RED (the mechanism
      does not exist yet); record the failure line in the task notes.
      Every test fn in this file carries a `roam_` prefix (e.g.
      `roam_tether_confines_bugs_for_life`) so quickstart §1's `roam`
      filter matches — cargo test filters match fn names, not file
      names (analyze C1)
- [x] T006 [US1] Implement the tether in
      crates/cloudkitty-core/src/world.rs `move_critters`, Bug arm
      only: after the existing direction draw, compute the
      destination and skip the step when
      `!same_roam_cell(pos, dest, n)` (research D2 — draw exactly as
      today, outward draw = lost step, no redraw). T005 goes green;
      T004's golden digest stays green (flag-absent path untouched)
- [x] T007 [US1] Add cadence and non-interference tests to
      crates/cloudkitty-core/tests/roam_tether.rs: (a) SC-003 — over
      a seeded tethered run every bug attempts on its every-other-tick
      schedule and attempts = moves + boundary losses + occupancy
      losses, no redraws; (b) greebles under a bug tether visit tiles
      outside any single 4×4 cell (free-range preserved); (c) seed
      determinism — same seed + tether config twice → identical world
      state after 5,000 ticks. Names: (a) contains `cadence` (e.g.
      `roam_cadence_attempts_match_schedule`) for quickstart §3's
      filter; (b)/(c) keep the `roam_` prefix (analyze C1)
- [x] T008 [US1] Rule-6 mutation pass, aimed and verified: (1) invert
      `same_roam_cell` → T005 fails and names the violation (that
      assertion, not a neighbour); (2) delete the Bug-arm check →
      T005 fails; (3) apply the check to the Greeble arm → T007(b)
      fails; each mutation reverted, suite green after. Confirm T004
      stayed green through every mutation (the tether cannot reach
      the flag-absent world even when broken)

**Checkpoint**: US1 is a complete, independently testable increment —
tether works on 20×20, nothing else moved.

## Phase 4: User Story 2 — Worlds that don't divide evenly (P2)

**Goal**: ragged and undersized geometries get well-defined cells with
no special-case code paths.

**Independent test**: quickstart §1's geometry cases.

- [x] T009 [P] [US2] Extend crates/cloudkitty-core/tests/roam_tether.rs
      with geometry-parametrized confinement: 26×26/N=4 (bugs born in
      remainder strips confine to the smaller cells — seed the world
      until births land there, or place elements directly via the
      test-support constructors), and a world smaller than the cell
      in one dimension (bug roams that whole strip; behavior equals
      untethered within it). Partition-level properties are already
      covered by T002; this task proves the *runtime* honors them

**Checkpoint**: geometry generality proven; still config-driven only
in tests.

## Phase 5: User Story 3 — The operator chooses the ecology (P2)

**Goal**: the config surface exists, validates strictly, and the
served world adopts the ratified package.

**Independent test**: quickstart §4 and §5.

- [x] T010 [US3] Validation in
      crates/cloudkitty-core/src/config/validate.rs: refuse
      `roam_cell` of 0 or 1 naming "[elements.bug] roam_cell" and the
      value (existing ttl-zero refusal shape); refuse `roam_cell` set
      on any non-bug element table naming that table (research D3's
      deliberate divergence from the silent `servings` precedent).
      Tests red-first in config/mod.rs's test module: each refusal
      observed failing before the validation exists, message content
      asserted, and legal values (2, 4, 64) observed loading. Test fn
      names contain `roam_cell_validation` (quickstart §4's filter,
      analyze C1)
- [x] T011 [US3] The served package in cloudkitty.toml:
      `[elements.bug]` gains `roam_cell = 4` and `ttl` 300 → 600;
      `[elements.greeble]` `ttl` 300 → 600 (owner's symmetry ruling,
      Clarifications 2026-08-21); update the comment block (the
      tether in one sentence, greebles-free-range unchanged, pointer
      to specs/039-bugs2-tether/contracts/roam-config.md). The
      shipped-config tests (policy_kitty.rs successor,
      server_integration.rs description test, docs_examples) stay
      green
- [x] T012 [US3] Old-save adoption test in
      crates/cloudkitty-core/tests/roam_tether.rs (FR-007): run a
      flag-absent world (== pre-039 by T004's proof), serialize the
      snapshot mid-life, reload it under a tether config — loads
      without migration, `Config::fingerprint()` identical, existing
      bugs confine from their load-position cells thereafter, ttl
      countdowns continue uninterrupted

**Checkpoint**: the full ratified package is in the repo; every FR has
a guarding test.

## Phase 6: Polish & handoff

- [x] T013 [P] CHANGELOG.md Unreleased entry: the tether + lifetimes
      story in house register, NO compatibility markers, with the
      neutrality proofs cited in prose (stamp test pinned, golden
      digest pinned, fingerprint untouched) per research D7 and
      changelog practice ("a missing marker is a claim")
- [x] T014 Full gate: `cargo test --workspace --release` (read the
      count) and `cargo clippy --workspace --release --all-targets`
      clean; walk quickstart §§1–6 end to end and fix any drift
      between the guide and reality. This gate IS FR-008's guard
      (analyze E1): the untouched existing suite staying green —
      scripted-behavior anchors, schema pins, reward-shape tests —
      is the assertion that nothing outside the tether moved; a
      dedicated "nothing changed" test would just duplicate it
- [x] T015 Handoff per FR-010/SC-004: send Experiments the branch
      head for the pre-registered acceptance grid (their census tool
      with expiry-abandon tagging landed at e39079e). Record in the
      message: merge waits on grid-pass AND the phase-1 --fresh
      having run, then carries the served package per the same-PR
      clarification; the deploy remains separately owner-gated. Name
      SC-005's definition-of-done in the message (anchors, zero-play
      baseline, divergence + confound notes): it is Experiments' work
      by the spec's own scoping and deliberately has no Product task
      (analyze E2)

## Dependencies

- T001 → everything (baseline)
- T002, T003, T004 (Foundational) → T005+ ; T002/T003 parallel, T004
  independent of both but must be green before T006 lands behavior
- US1 (T005→T006→T007→T008, strictly ordered) → US2, US3 runtime
  tasks
- T009 [US2] parallel with Phase 5 after US1
- T010 → T011 (validation before the served toml claims legality);
  T012 after T006
- Phase 6 last; T013 parallel with T014's first run

## Parallel example

After T008: `T009 [US2]` + `T010 [US3]` + `T013` touch disjoint files
(tests file geometry section, validate.rs, CHANGELOG.md) and can run
as one batch; T011 waits only on T010.

## Implementation strategy

MVP = Phase 3 (US1) on top of Foundational: tether working and proven
inert, mergeable in principle at that point if the arc were cut short.
US2 and US3 are small, independent completions. The real long pole is
outside this file: Experiments' grid on the branch build (T015), which
gates the merge together with the phase-1 --fresh.

## Deviations (recorded at implementation)

- **T003/research D5**: the "pinned stamp test" the plan cited does not
  exist — `engine_defaults_sha256` is computed, never asserted against
  a constant. Replaced by two stronger guards: a neutrality test
  (`roam_cell_stays_out_of_the_default_serialization`, red if the
  skip attribute is dropped) and an empirical comparison — the stamp's
  input (default Config JSON) hashes `ab08eb8c…` identically on this
  branch and on main @ 87236c5.
- **T005 red observation**: bug 11 born (5,16) escaped to (8,18) at
  tick 18 (seed 900000) — the confinement assertion itself, before the
  mechanism existed.
- **T007**: the tick counter increments AFTER the environment phase
  (world.rs:374), so movement observed at `world.tick` maps to the
  schedule at `world.tick − 1`; the cadence test documents this rather
  than working around it silently.
- **T008 mutation 1 caveat**: test and engine share `same_roam_cell`,
  so inverting it fails the test partly through the test's own use;
  mutation 2 (engine check deleted, test predicate intact) is the
  load-bearing kill and produced the identical genuine escape as the
  original red.
- **T013**: the CHANGELOG PR reference is `#pending` until the PR
  exists (same flow as #280's).

## Phase 7: Fallback — the final pounce (FR-011/FR-012, fired 2026-08-21)

- [x] T016 Spec amendment recorded (FR-011 pounce, FR-012 gating,
      SC-006 re-grid) per the owner's pre-authorized fallback ruling
      and the grid verdict in experiments/bugs2-grid-2026-08-21.md
- [x] T017 Red-first pounce tests in
      crates/cloudkitty-core/tests/roam_tether.rs (roam_pounce_*
      names): (a) chase from distance 3 with pounce on → post-tick
      distance 1 (step + pounce); (b) distance 2 start → step to 1,
      NO second step past adjacency; (c) distance 4+ → single step
      only; (d) kitty target at post-step distance 2 → never pounces;
      (e) blocked pounce leg (kitty on the lunge tile) → step lost,
      cat at distance 2; (f) pounce off → today's single-step chase.
      OBSERVE RED, then implement in action.rs Chase arm after the
      movement resolution; mutations: fire at distance 3 → (a)/(c)
      catch it; pounce kitties → (d) catches it
- [x] T018 `pounce: bool` on the behavior config table (serde default
      false + skip-if-false), validation-free (a bool), stamp
      neutrality re-verified (default serialization test extended to
      assert no `pounce` key), golden digest still green flag-off;
      cloudkitty.toml `[behavior] pounce = true` with the fallback
      provenance comment
- [x] T019 Full gate + push; notify Experiments for the SC-006
      re-grid; CHANGELOG entry updated to carry the pounce in the
      same story

## Phase 8: The sticker (FR-013, the owner's pre-merge ask)

- [x] T020 Served toml gains `[actions] play_relief_bug = 28.0` (engine
      key exists since the dial-pricing arc, default 25; pure config
      value, stamp untouched by construction). Spec second amendment +
      CHANGELOG updated; Experiments re-confirms the exact shipped
      toml before the PR goes to the owner. The "no reward-value
      changes" constraint is revised by its own author: a value from a
      pre-registered measured sweep is what the constraint was
      protecting FOR, not against
