# Tasks: Per-Target Play Relief

**Input**: Design documents from `/specs/025-play-relief-split/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R6), data-model.md,
contracts/play-relief-split.md

**Tests**: Included — FR-011 demands the battery explicitly, and the
guards ARE tests (executable validators). CLAUDE.md's
success-criteria-first loop is house law.

**Organization**: Grouped by user story. Unlike 024's orthogonal batch,
US1 (routing) and US2 (guards) share one prerequisite: the two config
fields must exist. That's the whole Foundational phase. After it, the
stories are independent and could land in any order; priority order is
the chosen one. Polish executes and records the comparability break.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Verify the branch base is green: `cargo test --workspace` +
      clippy + fmt on `025-play-relief-split` (base `8bed190`) before
      any change — baseline for attributing breakage; long tests run
      foreground with generous timeout (house practice)

## Phase 2: Foundational

- [ ] T002 Add `play_relief_bug` and `play_relief_greeble` to
      `ActionEffects` in crates/cloudkitty-core/src/config/mod.rs
      (`#[serde(default = ...)]` each, `Default` impl entries 25.0/35.0)
      and re-scope `play_relief`'s doc comment to the kitty/duet value
      (R1 — name kept deliberately; the comment carries the why);
      `default_play_relief_bug` (25.0) and `default_play_relief_greeble`
      (35.0) fns in crates/cloudkitty-core/src/config/defaults.rs
      beside `default_solo_play_relief`

---

## Phase 3: User Story 1 — The play economy gets a value gradient (P1)

**Goal**: Per-target routing in the one effect body: bug 25, greeble 35,
duet 20 each (unchanged mechanics), solo 10, vanished/non-critter target
→ solo (the pinned despawn edge).

**Independent test**: headless worlds place one kitty into each play
form; serviced-tick relief magnitudes match the contract table exactly;
the duet still relieves both parties and stamps the partner.

- [ ] T003 [US1] Split the `Activity::Playing { Element }` arm in
      `apply_activity_effects`, crates/cloudkitty-core/src/action.rs:712-714:
      look the element up by id at effect time, route
      `ElementType::Bug` → `play_relief_bug`, `ElementType::Greeble` →
      `play_relief_greeble`, and lookup miss or non-critter →
      `solo_play_relief`; doc comment records the despawn pin ("the
      critter is gone; the kitty is pouncing at nothing") and that the
      duet/solo arms are deliberately untouched (spec 025 R2/R4)
- [ ] T004 [US1] Routing tests in the crates/cloudkitty-core/src/action.rs
      test module: one serviced tick pays exactly 25 (adjacent bug), 35
      (adjacent greeble), 20 to BOTH duet partners + partner serviced
      stamp, 10 (solo) at defaults; despawn fallback — start a greeble
      scene, remove the element mid-scene (`world.elements.retain`
      pattern, world.rs:2350 precedent), assert the next serviced tick
      pays 10, not 35, and the scene's clock/ending is otherwise
      undisturbed; check the existing solo-vs-play expectation test
      (action.rs:1746-1753) still holds unchanged

**Checkpoint**: `cargo test -p cloudkitty-core --lib action` green —
US1 fully functional at defaults.

---

## Phase 4: User Story 2 — The guards are executable, not prose (P2)

**Goal**: `validate_actions` enforces the strict chain and the duet
ceiling with errors that teach; misconfiguration is impossible, not
discouraged.

**Independent test**: hostile configs at every boundary (including
equality) are rejected naming their keys and values; defaults and the
served config's values pass.

- [ ] T005 [US2] Grow `validate_actions` in
      crates/cloudkitty-core/src/config/validate.rs:542-562: extend the
      finite/≥0 check to all four keys; replace the solo-vs-play guard
      (:551) with the strict chain `solo < play_relief < bug < greeble`
      (each violation names both colliding keys and values; the
      solo/kitty error keeps the "playing together must stay the better
      deal" phrase); add the ceiling `greeble < 2 × play_relief` with
      the economics in the message (a duet relieves both cats — 2×kitty
      per tick team-side; at or above the ceiling solo greeble-hunting
      dominates and meow recruitment loses its value). Order: finiteness,
      then chain, then ceiling (data-model.md)
- [ ] T006 [US2] Guard tests in crates/cloudkitty-core/src/config/mod.rs:
      each chain boundary rejected including exact equality (solo==kitty,
      kitty==bug, bug==greeble), ceiling rejected at exactly
      `greeble == 2 × play_relief` while a greeble just under the
      ceiling passes;
      negative/non-finite rejected for both new keys; defaults
      (10/20/25/35) pass including ceiling margin (35 < 40); update the
      existing `solo_play_relief_may_not_beat_social_play` test
      (mod.rs:1417) to the new error text if it changed (tighten-only —
      the assertion set may grow, never shrink); reconcile the old-shape
      fixture `play_relief = 25.0 → 20.0` (mod.rs:~1469, R3 — value
      arbitrary to the test's intent, recorded in research)

**Checkpoint**: `cargo test -p cloudkitty-core --lib config` green —
the contract's validation table is fully enforced.

---

## Phase 5: User Story 3 — Existing configs keep their meaning (P3)

**Goal**: Every config in the wild parses with today's meaning; the new
keys default in; frozen surfaces are untouched; `/config` changes
additively only.

**Independent test**: today's-keys-only TOML parses with defaulted new
fields and validates; repo diff shows no `.toml`/`evals/` changes
outside test fixtures.

- [ ] T007 [P] [US3] Extend the old-shape/durationless config tests in
      crates/cloudkitty-core/src/config/mod.rs (the T006-reconciled
      fixture and mod.rs:~1520): assert `play_relief_bug == 25.0` and
      `play_relief_greeble == 35.0` default in when absent from the
      TOML, and the config validates
- [ ] T008 [P] [US3] Extend the `/config` payload assertions in
      crates/cloudkitty-server/tests/server_integration.rs:370 area:
      `config["actions"]["play_relief_bug"] == 25.0`,
      `["play_relief_greeble"] == 35.0`, and `["play_relief"] == 20.0`
      still present under its original name (the additive-only wire
      promise, contracts/play-relief-split.md)
- [ ] T009 [US3] Frozen-surface sweep: `git diff main --stat` shows no
      `.toml` outside crate test fixtures, no `evals/` changes, served
      cloudkitty.toml untouched (FR-009 — the file is EXCLUDED from any
      prose sweep; its "must not exceed play_relief" comment is one word
      stale vs the strict guard, left as-is and flagged for a future
      owner-side touch); grep docs/ and in-crate doc comments for
      `play_relief` statements whose meaning the re-scope touches and
      update prose ONLY there (analyze pass verified docs/ currently has
      zero mentions) — report, don't fix, anything unrelated found on
      the way (CLAUDE.md #3)

**Checkpoint**: back-compat proven by tests and by diff inspection.

---

## Phase 6: Polish — executing the break

- [ ] T010 Regenerate crates/cloudkitty-rl/tests/goldens/run-json.golden.json
      (`UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test harness_policy`),
      inspect the diff tells the expected story (play-scene needs fall
      faster where element play occurs; no unrelated drift), then full
      `cargo test -p cloudkitty-rl` green with the moved
      `engine_defaults_sha256` (no pin to edit — plan.md Structure
      Decision)
- [ ] T011 Re-verify crates/cloudkitty-core/tests/welfare_longrun.rs
      foreground with generous timeout: floors hold (play services
      faster → happiness up → more margin expected); bounds are
      tighten-only — if any bound FAILS, stop and report per CLAUDE.md
      #4, never loosen
- [ ] T012 Full gate + quickstart walk: `cargo test --workspace`,
      `cargo fmt --check`, `cargo clippy --workspace -- -D warnings`,
      then each quickstart.md step in order; mark spec checklists
      complete in specs/025-play-relief-split/
- [ ] T013 Record the break for the PR: draft PR body noting (a) the
      `engine_defaults_sha256` move as the generation's second and
      FINAL planned break, (b) the despawn-pin semantics delta (10 not
      20 on the vanished-target tail — spec Edge Cases), (c) the ping
      to Experiments on merge: re-run the measurement stack (~1 hr),
      registered falsifiable prediction "play/chase probe class rises
      off its 0.1× floor", prereg freezes after, (d) delete
      HANDOFF-2026-08-02-play-relief-split.md (consumed). Push and PR
      only on owner confirmation (house rule)

## Dependencies

```text
T001 (green base)
  └── T002 (config fields — the one shared prerequisite)
        ├── US1: T003 → T004          (action.rs)
        ├── US2: T005 → T006          (validate.rs, config/mod.rs tests)
        └── US3: T007, T008 [P]       (after T002; T007 also after T006's
              └── T009                 fixture reconciliation)
                    └── Polish: T010 → T011 → T012 → T013
```

- US1 and US2 are file-disjoint after T002 and can proceed in parallel
  (T003/T004 in action.rs; T005/T006 in config/).
- T007 shares config/mod.rs with T006 — sequential after it. T008 is a
  different crate, parallel with anything post-T002.
- Polish is strictly last: goldens regenerate only once, after all
  dynamics and validation changes are final (one-break discipline).

## Parallel example

After T002 lands: open T003+T004 (action.rs) and T005+T006 (config/*)
as two independent tracks; T008 (server test) can ride either. Converge
at T009, then Polish serially.

## Implementation strategy

MVP is US1 + the Foundational fields: the gradient exists and is
testable at defaults even before the guards land. But this spec ships
as one PR (mini batch, one break) — incremental delivery here means
commit-by-commit reviewability, not staged merges. Speed matters more
than polish (handoff sequencing): the change is four keys, one arm, two
validators, and its test battery.
