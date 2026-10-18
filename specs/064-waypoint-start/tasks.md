# Tasks: Waypoint Start-Index by Position

**Input**: specs/064-waypoint-start/ (plan.md, spec.md,
contracts/seeding-law.md, quickstart.md)

**Tests**: included — rule 5 red-first via `scripts/mutate.sh --expect`
(prediction declared BEFORE each run, file committed first). Rule 6:
sort each phase's checks; kept behavior green, guards of the change
red.

## Phase 1: Setup

- [X] T001 Record the pre-change baseline: bc-collect (standalone
      workspace, `experiments/tools/bc-collect`) at current HEAD on a
      scratch copy of
      `experiments/world-size-screen-2026-09-24/size100.toml`,
      `--rollouts 1 --ticks 2000 --seed-base 993001`, into
      `<scratchpad>/wps/baseline-pre/`; note HEAD SHA beside it.

## Phase 2: Foundational

- [X] T002 Add `waypoint_start_by_position: bool` to `BehaviorConfig`
      in `crates/cloudkitty-core/src/config/mod.rs` (`#[serde(default,
      skip_serializing_if = "std::ops::Not::not")]`, Default impl
      false, doc comment citing spec 064 + the seeding-law contract).
      Extend the existing `friend_ward_keys_default_off...` stamp test
      shape with the new key (TOML + hashed JSON surfaces).
- [X] T003 Add `Lattice::nearest_index(&self, pos: Position) -> u32` in
      `crates/cloudkitty-core/src/explore.rs`: linear
      `min_by_key((manhattan(waypoint(i), pos), i))` over the cycle.
      Unit tests beside the existing lattice tests: nearest beats
      id-law on a staged big lattice; equidistant tie → lower index;
      one-waypoint lattice → 0; agreement with `waypoint()` geometry
      across the existing (w, h, r) test matrix.
- [X] T004 Mutate reds for T002+T003 (predictions first): flip the
      serde default to true expecting the stamp test red; `min_by_key`
      → `max_by_key` in `nearest_index` expecting the nearest test
      red; drop the index tiebreak expecting the tie test red.

## Phase 3: User Story 1 — inert when off (P1) 🎯 MVP

- [X] T005 [US1] Wire the branch at the seeding loop in
      `crates/cloudkitty-core/src/world.rs` (`World::generate`): flag
      off → `lattice.start_index(kitty.id)` exactly as today; flag on
      → `lattice.nearest_index(kitty.pos)`. Comment carries the
      contract pointer and the no-RNG constraint.
- [X] T006 [US1] Full flag-off surface: workspace `cargo test` green,
      zero golden movement in `git status`; rebuild bc-collect and
      byte-compare T001's run (all arrays identical, meta delta =
      engine_commit only).
- [X] T007 [US1] Mutate red (prediction first): make the branch ignore
      the flag (always positional) expecting the flag-off id-law test
      (T008's, written first if ordering demands — else the goldens'
      determinism test names) red; state the actual observed failing
      test in the ledger.

## Phase 4: User Story 2 — the tour starts where the cat is (P2)

- [X] T008 [US2] World-generation tests in `world.rs` test module
      (stage on `test_support` builders — jscpd: no fresh staging
      clones): flag-on disagreement world (id-law ≠ nearest) seeds
      nearest for every cat; flag-off seeds id-law; equidistant start
      ties to the lower index; one-waypoint world → 0 both flags;
      composition with `[starts]` (062) — drawn positions seed their
      nearest waypoint, and the 062 golden-draw suite stays green
      untouched.
- [X] T009 [US2] Flag-on determinism: same seed+config twice →
      byte-equal `explore_waypoint` vectors and world state (extend
      the existing determinism test shape, not a new clone).
- [X] T010 [US2] Mutate reds (predictions first): seed from the
      PRE-placement position (ignore `kitty.pos`) expecting the
      062-composition test red. DROPPED, with reason recorded in
      explore.rs: the Chebyshev-swap red is vacuous by mathematics on
      an axis-aligned waypoint grid (the two metrics' unique argmins
      always coincide; a 100x100 brute scan finds no disagreeing tile),
      so no guard is owed for a mutation with no behavior.

## Phase 5: Polish

- [X] T011 Flag-on smoke per quickstart (scratch toml, scratchpad only,
      deleted after); CHANGELOG Unreleased entry (public voice); spec
      INDEX line for 064.
- [X] T012 Local gate (`fmt`, `clippy --all-targets`, full `cargo
      test`) + local jscpd at threshold 3.5; SC-001..005 verified
      against reality; mutate ledger (predictions + outcomes) in the
      PR body.

## Dependencies

T001 first (baseline predates changes). T002/T003 parallel-safe
(different files) → T004 → T005 → T006/T007 → US2 → polish.
mutate.sh: commit before each cycle; no tree edits mid-cycle.

## Implementation strategy

MVP = Phases 1–3 (landed, validated, provably-inert flag). US2 is the
candidate itself. Each checkpoint re-proves flag-off identity.
