# Tasks: The Wet-Fur Engine Batch

**Input**: Design documents from `/specs/024-wet-fur-batch/`

**Prerequisites**: plan.md, spec.md, research.md (R1–R10), data-model.md, contracts/

**Tests**: Included — the spec demands them explicitly (FR-004's executable
guard, FR-008's equivalence test, SC-005's perturbation check), and
CLAUDE.md's success-criteria-first loop is house law.

**Organization**: Grouped by user story. The three stories are
**deliberately orthogonal** (batch framing in spec.md): none depends on
another, so the Foundational phase is empty and the stories could land in
any order — priority order is the chosen one. The Polish phase is where
the batch's one comparability break is executed and recorded.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Verify the branch base is green: `cargo test --workspace` +
      clippy + fmt on `024-wet-fur-batch` before any change (baseline for
      attributing breakage; long-run tests run foreground with generous
      timeout per house practice)

## Phase 2: Foundational

*(none — the three stories share no prerequisite beyond the green base;
the validation-order fixture update rides US1's config task where it
belongs)*

---

## Phase 3: User Story 1 — Wet fur: water costs bath (P1)

**Goal**: Water-tile occupancy charges the bath need — trait-scaled,
ceiling-gated, safeguard-unreachable by construction (contracts/water-config.md).

**Independent test**: headless worlds on/off water assert the charge law;
hostile swim-forever property proves the guard; scripted skirt-vs-swim
fixtures prove SC-001. No other dynamics change.

- [ ] T002 [US1] Add `WaterConfig` section: struct + `[serde(default)]`
      field on `Config` + `Default` listing in
      crates/cloudkitty-core/src/config/mod.rs; `default_water_bath_gain`
      (1.5) and `default_water_bath_gain_ceiling` (50.0) fns in
      crates/cloudkitty-core/src/config/defaults.rs (spec 020 FR-003
      pattern; doc comments carry the 5×-ambient framing and the
      BACKLOG derivation pointer)
- [ ] T003 [US1] Implement `validate_water` in
      crates/cloudkitty-core/src/config/validate.rs — the four contract
      rules including the roster-arithmetic safeguard bound (R4), errors
      naming the field the user must change; append to the
      spec-contract validation order in `Config::validate`
      (crates/cloudkitty-core/src/config/mod.rs) and update the
      order-guard fixture test in the same commit, documented as a
      deliberate spec-contract extension
- [ ] T004 [P] [US1] Config tests in crates/cloudkitty-core/src/config/mod.rs:
      absent-section defaults (old toml parses), each rejection naming
      its field (non-finite/negative/over-100 gain; ceiling out of
      range; headroom violation showing the arithmetic and offending
      kitty; `[needs] bath = 0` with positive gain), fingerprint
      unchanged by `[water]` (extend the existing
      fingerprint-ignores-tunables test)
- [ ] T005 [US1] Implement the charge in `World::advance_needs`
      (crates/cloudkitty-core/src/world.rs:810-825): collect water
      positions from `self.elements` before the kitty loop (R1 borrow
      note), pre-charge ceiling gate, `bath_gain ×
      need_rate_for(kitty, Bath) / needs.bath` via `Need::add`, before
      the same-tick happiness recompute; no RNG, no phase-order change
- [ ] T006 [P] [US1] Charge-law unit tests in
      crates/cloudkitty-core/src/world.rs: on-water charges (ambient +
      charge additive), off-water doesn't, pre-charge gate at the
      ceiling (overshoot ≤ one scaled charge), trait scaling via
      `[kitty.needs] bath` override, gain 0 disables, charge visible in
      the same tick's happiness; FR-003 explicit assertions — drinking
      from adjacency incurs no bath charge, and a move onto/off water
      remains exactly one tile in one tick (movement untouched)
- [ ] T007 [US1] Scale the scripted surcharge: `water_step_cost ×
      (need_rate_for(me, Bath) / needs.bath)` in
      crates/cloudkitty-core/src/behavior/needs_driven.rs:327-343;
      existing arithmetic tests stay exact at ratio 1.0 (default
      worlds), add one trait-scaled case ("the swimmer" low-bath cat
      pays less, both deciders agree)
- [ ] T008 [P] [US1] NEW crates/cloudkitty-core/tests/water_safeguard.rs
      — the runtime half of FR-004 (R10): directed swim-forever hostile
      behavior over thousands of ticks asserts zero Bath distress
      events and bath never crossing safeguard via water, with
      `[water]` values **randomized through `validate`** so the guard
      holds at every legal dial (SC-002's letter), and roster bath-rise
      variance included; plus a lounging fixture (accrues to ceiling,
      then stops); plus a chase-or-sidestep-onto-water fixture
      asserting the occupancy charge applies that tick (no special
      case); plus SC-001 skirt-vs-swim scripted fixtures (1-tile
      puddle with short detour → skirts; long detour → swims)
- [ ] T009 [US1] Re-verify dynamics-sensitive behavioral suites under
      wet fur: crates/cloudkitty-core/tests/stuck_state_regression.rs
      and crates/cloudkitty-core/tests/welfare_longrun.rs (R8 items
      4–5). If any bound fails, STOP and surface — bounds are never
      weakened to pass (CLAUDE.md #4); expected result is green (the
      fixture worlds' cats have no reason to camp on water)

**Checkpoint**: US1 alone = a shippable wet-fur engine (MVP).

---

## Phase 4: User Story 2 — Chases route around friends (P2)

**Goal**: Blocked chase steps sidestep deterministically instead of
stalling (contracts/chase-sidestep.md); patience bookkeeping unchanged.

**Independent test**: blocked-lane fixture advances; boxed-in fixture
stalls exactly as today; same seed → identical runs; mirrored chasers
decorrelate.

- [ ] T010 [US2] Implement the sidestep in the Chase apply arm
      (crates/cloudkitty-core/src/action.rs:494-522): candidate pool =
      lawful steps (`Position::step` + `world.kitty_at`) with
      Manhattan-to-target ≤ current, minus the blocked straight step;
      uniform `world.rng` choice (master RNG at apply time, R5); empty
      pool → today's stall; rewrite the 505-512 stall comment to record
      the new law and the BACKLOG item's retirement
- [ ] T011 [P] [US2] Unit tests in crates/cloudkitty-core/src/action.rs:
      blocked→sidesteps to a non-retreating lawful tile (first direct
      coverage of the stall branch), fully-boxed→stalls, sidestep
      never increases Manhattan distance, same seed twice → same
      sidestep, a draw happens only when blocked (stream-shape sanity)
- [ ] T012 [US2] Mirrored two-chaser decorrelation fixture (integration,
      crates/cloudkitty-core/tests/approach_etiquette.rs or sibling):
      two kitties chasing across one lane for 1,000+ ticks, asserting
      the operational lockstep definition — no window of 8+ consecutive
      ticks in which both chasers' per-tick displacement vectors are
      mirror images while neither closes distance; deterministic across
      reruns
- [ ] T013 [US2] FR-007 re-baseline: run
      crates/cloudkitty-core/tests/behavior_variation.rs and the
      selection staleness expectations
      (crates/cloudkitty-core/src/behavior/selection.rs tests) under
      the sidestep; document every expectation that legitimately
      shifts (stall-fed abandonment drops) in the commit message as a
      deliberate re-baseline — never a silent number change
- [ ] T014 [US2] Verify crates/cloudkitty-core/tests/joint_action_parity.rs
      stays green unmodified (shared apply-arm code ⇒ parity and
      draw-shape hold by construction; a failure here means the
      implementation leaked asymmetry — STOP and fix)

**Checkpoint**: US1 + US2 = the batch's complete dynamics change.

---

## Phase 5: User Story 3 — Welfare↔validation equivalence guardrail (P3)

**Goal**: The two encodings of relief law can never silently diverge
again (contracts/equivalence-matrix.md); the eat-side divergence found in
planning is reconciled (owner-approved).

**Independent test**: it is a test; matrix passes on the shipped law,
goes red under deliberate perturbation of either side.

- [ ] T015 [US3] Reconcile the Eat predicate: tighten
      `zero_distance_relief_exists` (crates/cloudkitty-rl/src/welfare.rs:57-60)
      to adjacent **stocked** chow, matching `validate`'s
      `adjacent_stocked_chow` (crates/cloudkitty-core/src/action.rs:366);
      ensure the stocked-chow query is a public core API the rl crate
      can call (promote `World::adjacent_stocked_chow` to `pub` with a
      doc comment if it is `pub(crate)` today); document the
      pinned-streak semantic correction at the change site
- [ ] T016 [P] [US3] NEW crates/cloudkitty-rl/tests/welfare_validate_equivalence.rs
      (mask_oracle.rs precedent): matrix builder over need kind ×
      neighbor state × relief-element state (impossible cells skipped
      with documented reasons), asserting predicate ⇔ some lawful
      relieving action validates, public APIs only; the adjacent-busy
      cuddle cell pins the spec-021 doctrine on the *true* side
- [ ] T017 [US3] SC-005 perturbation check: temporarily loosen the
      predicate, observe red; temporarily carve out a validate arm,
      observe red; remove both perturbations; record the check in the
      commit message (no perturbation code ships)
- [ ] T018 [US3] Verify pinned-streak accounting under the honest
      predicate: crates/cloudkitty-rl/tests/welfare_longrun.rs
      violations report — expected effect is *fewer or equal*
      false-positive pinned streaks, bounds untouched (tighten-only
      floors are compile-guarded; any bound failure is STOP-and-surface)

---

## Phase 6: Polish — executing the comparability break, exactly once

- [ ] T019 Regenerate the values golden once:
      `UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test run_json_golden`,
      with the justification (this batch = the exp-002 generation's
      designed break) in the commit message per the golden doctrine
      (crates/cloudkitty-rl/tests/run_json_golden.rs:14-18)
- [ ] T020 Re-clear the 20k constitutional bar on the new dynamics:
      `cargo test -p cloudkitty-rl --test welfare_longrun` (foreground,
      generous timeout); bounds constants untouched
- [ ] T021 [P] Migrate the screen config
      (experiments/exp-001-bc-mappo/configs/cloudkitty-24x24-screen.toml):
      explicit `[water]` block at engine defaults with a provenance
      comment noting pre-batch captures were made under no-water-cost
      dynamics (R9); `cargo test -p cloudkitty-core --test shipped_configs`
      green (frozen exams untouched by construction)
- [ ] T022 [P] Confirm the no-schema-change constraint held: existing
      length asserts green (`codec.len() == 40`
      crates/cloudkitty-rl/src/codec.rs:235; 182-value layout test
      crates/cloudkitty-rl/src/observe.rs:467) and
      `engine_defaults_sha256` moved from b0865884… (the designed mark
      — record old→new in the PR body)
- [ ] T023 Python surface unaffected: `maturin develop --release` +
      `python -m pytest tests/` in crates/cloudkitty-py (18 tests,
      incl. reproducibility) — no schema, no API change
- [ ] T024 Snapshot compatibility: a pre-batch `snapshot.json` from the
      served world shape resumes on the new engine (fingerprint covers
      only shape — verified R8; test via the existing persist tests +
      one manual load if practical)
- [ ] T025 BACKLOG bookkeeping in BACKLOG.md: mark the wet-fur entry
      shipped (retain the derivation pointer to specs/024), retire the
      "Chases route around friends" entry (its design detail now lives
      in the spec + contract), leave the parked schema-v2 wishlist and
      swim-pose entries untouched
- [ ] T026 Delete HANDOFF-2026-08-01-wet-fur-batch.md (consumed — its
      instruction; items 0 and the baseline gate are long done, the
      batch is this spec, the client track is parked in BACKLOG)
- [ ] T027 Full gate: `cargo test --workspace` + `cargo clippy
      --workspace --all-targets -- -D warnings` + `cargo fmt --all --
      check` + `node client/test-meadow.mjs` (untouched client, cheap
      confirmation) — all green before review

## Dependencies

```
T001 ──► US1 (T002→T003→T004,T005→T006,T007,T008 ; T009 last)
     ──► US2 (T010→T011,T012,T013,T014)          (independent of US1)
     ──► US3 (T015→T016→T017,T018)               (independent of US1, US2)
US1+US2+US3 ──► Polish (T019…T027; T019/T020 after all dynamics land)
```

Stories are orthogonal — any order works; P1→P2→P3 is the chosen order.
Within Polish, T019 and T020 MUST run after every dynamics change is in
(the golden and the 20k bar capture the batch's final physics); T021,
T022 are parallel-safe; T027 is always last.

## Parallel opportunities

- Inside US1: T004 ∥ T006 ∥ T008 (three different test files) once
  T002/T003/T005 land.
- US2 and US3 can be built entirely in parallel with US1 by separate
  sittings if desired (different files end-to-end) — this batch plans
  one sitting, sequential.
- Inside Polish: T021 ∥ T022 ∥ T023.

## Implementation strategy

MVP = US1 (wet fur alone is a shippable engine change and the batch's
reason to exist). But the batch merges as one PR regardless — the
one-break rule means partial landings would spend the comparability
break twice. Implement sequentially US1→US2→US3→Polish, commit per
task-cluster (the 022 batch's granularity), never push without
confirmation, and the merge additionally waits on nothing external —
the Experiments baseline gate is already cleared (`e144867`).
