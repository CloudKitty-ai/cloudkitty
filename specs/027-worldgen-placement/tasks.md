# Tasks: Worldgen Placement — Guaranteed Lake and Edge-Avoiding Spawns

**Input**: Design documents from `/specs/027-worldgen-placement/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/worldgen-guarantees.md, quickstart.md

**Tests**: requested (house practice); each unit lands with its tests.

**Organization**: config first (both features read it), then the two
placement stories, then the riding documentation.

## Phase 1: Setup

No setup tasks — worktree, stacked branch, and design artifacts exist.

## Phase 2: Foundational — the dials move to config

Blocking: US1 samples `spread_candidates` and US2 reads
`edge_penalty`, so the keys exist first. This is also FR-006's
behavior-preserving half: at defaults, nothing observable changes.

- [X] T001 Add `spread_candidates: usize` (8), `ttl_jitter: u64`
  (100), `edge_penalty: f32` (2.0) to `ElementsConfig` in
  `crates/cloudkitty-core/src/config/mod.rs` (serde-defaulted,
  documented per data-model §1), with default fns in
  `crates/cloudkitty-core/src/config/defaults.rs` and bounds in
  `crates/cloudkitty-core/src/config/validate.rs` (`spread_candidates
  >= 1`; `edge_penalty` finite `>= 0`; `ttl_jitter` unbounded — the
  floor-at-1 math is total). Wire `crates/cloudkitty-core/src/spawn.rs`
  to read them: `pick_spread_tile` takes the config (already in
  `spawn_one`'s scope), the candidate array becomes a Vec sized by the
  knob, `jittered_ttl` takes the jitter as a parameter; delete the two
  `const`s (:93, :104).
- [X] T002 Tests for the move in
  `crates/cloudkitty-core/src/config/mod.rs` (defaults land: a
  `[elements]`-scalar-free config reads 8/100/2.0; bad values refused
  naming the field) and `crates/cloudkitty-core/src/spawn.rs` (the
  existing spread/TTL tests pass unmodified — they are the
  behavior-preservation proof at defaults); run
  `cargo test -p cloudkitty-core`.

**Checkpoint**: core green; `spawn.rs` contains no numeric simulation
constants.

## Phase 3: User Story 1 — Every well-watered world has a lake (P1) 🎯 MVP

**Goal**: 2×2 all-water square guaranteed at water-min ≥ 4, maintained
by restock, invisible below the threshold.

**Independent Test**: seeded-sample generation test + frozen-scarcity
shape test, per quickstart SC-001.

- [X] T003 [US1] Implement the lake obligation in
  `crates/cloudkitty-core/src/spawn.rs` per research R1: a water-first
  step in `ensure_minimums` active iff `config.elements.water.min >= 4`
  — short-circuit if a 2×2 all-water square exists; else collect valid
  anchors (2×2 in-bounds, every tile water-or-free), sample
  `spread_candidates` anchors via the master RNG, score by (fewest
  missing tiles, then fewer perimeter tiles, ties earliest-drawn),
  spawn ordinary water onto the winner's free tiles (TTL per the water
  rule, jittered as usual); no valid anchor → carry over exactly like
  an unmet minimum. `safeguard` (:35) byte-untouched.
- [X] T004 [US1] Lake tests in `crates/cloudkitty-core/src/spawn.rs`:
  (a) seeded sample (≥ 50 seeds) at `Config::default()` — every world
  holds a 2×2 all-water square; (b) water.min < 4 (the frozen-scarcity
  shape) → validates, generates, no lake required, no error; (c)
  re-formation — build a world with a lake, expire one tile (TTL'd
  water), run the environment phase, assert the square completes in
  place (anchor reuse beats fresh placement); (d) carry-over — a board
  too full for any valid anchor defers without evicting or stacking;
  (e) determinism — same seed + config twice → identical worlds, lake
  position included; (f) `water.min == 4` boundary — the standing
  water population is exactly the lake.

**Checkpoint**: `cargo test -p cloudkitty-core spawn` green.

## Phase 4: User Story 2 — Spawns prefer the interior (P2)

**Goal**: perimeter candidates penalized by `edge_penalty` in scoring;
0 restores today exactly; never a constraint.

**Independent Test**: aggregate perimeter-share test + penalty-0
identity, per quickstart SC-002.

- [X] T005 [US2] Implement the scoring penalty in
  `crates/cloudkitty-core/src/spawn.rs` per research R2/data-model §3:
  `best_spread` scores `gap − edge_penalty·is_perimeter(candidate)`;
  the no-same-type early return (:132-135) joins the same scoring with
  gap equal-for-all, so penalty 0 keeps earliest-draw-wins and a
  positive penalty prefers the first interior draw. Draw count and
  order untouched (the :117 unconditional-draw comment stays true and
  stays present). Tie rule unchanged: earliest drawn wins among equal
  scores.
- [X] T006 [US2] Preference tests in
  `crates/cloudkitty-core/src/spawn.rs`: (a) penalty-0 identity — the
  two existing `best_spread` tests pass unmodified, plus an explicit
  fixture where a perimeter candidate with the best gap wins at 0 and
  loses at a penalty exceeding its gap margin; (b) preference never
  prohibition — all-perimeter free set still spawns; (c) aggregate —
  over a seeded sample at defaults, perimeter element share is below
  the perimeter area share, and at `edge_penalty = 0` the share
  matches the no-penalty regime (same-seed world equality with a
  0-penalty config vs. a pre-lake baseline is impossible — the lake
  moved the sequence — so the identity claim is about selection logic,
  pinned by (a), and the aggregate is the distribution evidence).

**Checkpoint**: core green; SC-002's aggregate demonstrably moves.

## Phase 5: User Story 3 — Config documentation truths (P3, remainder)

- [X] T007 [US3] Documentation corrections: `cloudkitty.toml` — fix
  the stale cap comment above `[elements.water]` (:97-99) to state the
  arithmetic and the true value (floor(area/32) = 18 at 24×24), note
  that `rule.max` is read only by validation (population stands at the
  minimums; `min` is the real knob), and document the three new keys
  at their defaults in the `[elements]` commentary (values stay
  engine-default, not written); mirror the `rule.max` note on
  `ElementRule.max`'s doc in `crates/cloudkitty-core/src/config/mod.rs`.

**Checkpoint**: an operator reading the shipped config learns the
true knobs.

## Phase 6: Polish & Cross-Cutting

- [X] T008 Full verification: `cargo fmt --check`, `cargo clippy`
  workspace-clean, `cargo test --workspace` (foreground, generous
  timeout); quickstart SC-002/SC-003 live checks on a scratch port;
  capture the post-027 `engine_defaults_sha256` for the PR body;
  retire BACKLOG.md's "wet-fur companion" lake entry (it shipped
  here) and mark `HANDOFF-2026-08-05-pre-exp-003-world-batch.md` for
  the consume-and-delete step once both specs merge.

## Dependencies & Execution Order

- Phase 2 (T001→T002) blocks everything (both stories read the keys).
- US1 (T003→T004) then US2 (T005→T006): sequential — same file, and
  US2's aggregate test regenerates worlds that include the lake step.
- T007 [US3] is independent after Phase 2 (comments only) but lands
  before polish for one clean docs commit.
- T008 gates.

## Implementation Strategy

MVP is Phase 2 + US1 (a guaranteed lake on config-fed dials). US2
follows in the same file; US3 is comment truth; polish gates. Commits
per phase, tree green at every checkpoint.
