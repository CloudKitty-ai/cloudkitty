# Tasks: Initial-Needs Distribution at World Creation

**Input**: specs/065-initial-needs/ (plan.md, spec.md,
contracts/init-law.md, data-model.md, research.md, quickstart.md)

**Tests**: included — rule 5 red-first via `scripts/mutate.sh --expect`
(prediction declared BEFORE each run, file committed first). Rule 6:
sort each phase's checks; kept behavior green, guards of the change
red. Stage tests on `test_support` builders (jscpd ratchet 3.5 scans
`#[cfg(test)]` in src).

## Phase 1: Setup

- [ ] T001 Record the pre-change baseline: bc-collect (standalone
      workspace, `experiments/tools/bc-collect`) at current HEAD on a
      scratch copy of
      `experiments/world-size-screen-2026-09-24/size100.toml`,
      `--rollouts 1 --ticks 2000 --seed-base 993001`, into
      `<scratchpad>/inw/baseline-pre/`; note HEAD SHA beside it.

## Phase 2: Foundational

- [ ] T002 Config types in `crates/cloudkitty-core/src/config/mod.rs`:
      `NeedInit` (untagged value-or-range per research D2, range struct
      `deny_unknown_fields`), `InitialNeedsSpec` (six `Option<NeedInit>`
      fields, skip-if-none, `deny_unknown_fields`),
      `Config.initial_needs: Option<InitialNeedsSpec>` and
      `KittyConfig.initial_needs: Option<InitialNeedsSpec>` (both with
      the starts serde attrs, doc comments citing spec 065 + the init
      law). Validation per init-law §8 (finite, [0,100], min ≤ max;
      errors name need and kitty). Extend the existing stamp-shape test
      with the new keys (TOML + hashed JSON surfaces must not grow).
- [ ] T003 [P] The law module `crates/cloudkitty-core/src/init_needs.rs`
      (sibling of starts.rs): `INIT_NEEDS_LAW_VERSION = 1`, tag
      `ck-initnd-v1`, sub-stream seed per init-law §3, `resolve` over
      (kitty id ascending × NeedKind::ALL) per §2/§4, mapping per §5.
      Unit tests beside it: precedence (kitty-level beats top-level
      need-by-need), draw consumption (range = one draw even at
      min == max; fixed/ungoverned = zero — assert via two configs
      whose shapes differ only in the probed entry: a consumed draw
      shifts every LATER resolved value, so compare the downstream
      sequences; no rng counter exists),
      per-kitty-per-need independence (two kitties differ; two ranged
      needs on one kitty differ across seeds), determinism (same
      seed+config twice byte-equal), bounds at 0/100 legal, validation
      rejections (out-of-bounds, min > max, non-finite).
- [ ] T004 Mutate reds for T002+T003 (predictions first; line-bounded
      mutations — never rewrite test oracles in the same file): swap
      precedence order (top-level beats kitty) expecting the precedence
      test red; drop the `>> 11` mapping for raw modulo expecting the
      determinism/mapping pin red; make min==max skip its draw
      expecting the draw-count test red; widen validation to accept
      101.0 expecting the rejection test red.

## Phase 3: User Story 1 — inert when absent (P1) 🎯 MVP

- [ ] T005 [US1] Wire application in `crates/cloudkitty-core/src/world.rs`
      `try_generate`: iff the feature is active (init-law §1), apply
      resolved initial needs right after the kitty-creation loop + id
      sort; after the existing happiness recompute, run
      `update_announce_arming(config)` then `record_distress(config)`
      (the Phase-4 order, init-law §6). Inactive: not one line of the
      pre-065 path moves. Comment carries the contract pointer.
- [ ] T006 [US1] Full feature-absent surface: workspace `cargo test`
      green, zero golden movement in `git status`; rebuild bc-collect
      and byte-compare T001's run (all arrays identical, meta delta =
      engine_commit only).
- [ ] T007 [US1] Mutate red (prediction first): make the activation
      predicate always-true (apply path + generation-time needs-phase
      calls run on every config) expecting a flag-off guard red — write
      the guard in T008 first if ordering demands, else name the
      failing existing test (determinism/golden) in the ledger.

## Phase 4: User Story 2 — a world starts where configured (P2)

- [ ] T008 [US2] World-generation tests in `world.rs` test module
      (stage on `test_support` builders): fixed value lands exactly for
      every kitty with happiness = engine function of the vector;
      ranged need draws inside bounds with kitties differing (seeded
      staging assert: the chosen seed actually produces ≥2 distinct
      values); unspecified needs at zero; per-kitty override precedence
      (scenario US2-5: override kitty gets its cuddle, its OTHER needs
      follow roster-wide; all other kitties roster-wide); feature-absent
      world generates all-zero needs (the US1/T007 guard).
- [ ] T009 [US2] Composition + determinism tests in `world.rs`: with
      `[starts]` (062) also on — drawn positions per the 062 law
      (golden-draw suite untouched), needs identical to the
      no-`[starts]` case at the same seed (staging assert: both laws
      produce nontrivial outcomes); same seed+config twice → byte-equal
      need vectors and world state (extend the existing determinism
      test shape).
- [ ] T010 [US2] Mutate reds (predictions first): draw needs from the
      MASTER stream (`world.rng`) instead of the sub-stream expecting
      the 062-composition test red; apply needs AFTER the happiness
      recompute expecting the happiness-derivation test red.

## Phase 5: User Story 3 — register-real distressed starts (P2)

- [ ] T011 [US3] Tick-0 distress tests in `world.rs` test module: a
      need initialized ≥ `thresholds.distress` yields a tick-0
      DistressLog event per affected (kitty, need), `in_distress`
      containing it, and `distress_since == 0` BEFORE any tick runs; a
      need ≥ announce arm_at has `announce_armed` set at tick 0; needs
      below both thresholds add zero records (the no-fabrication
      guard); first tick after a distressed start does NOT re-record
      (edge-trigger preserved); safeguard case — SAME-NEED PARITY, the
      FR-007 oracle: a SPAWNABLE need (eat or drink) initialized above
      the safeguard threshold produces, after the first environment
      phase, the same observable relief state as the same need RISEN to
      the same value in a pre-065 world (resource present/reachable per
      the existing machinery); never an absolute resource claim for
      social needs (cuddle relief is another kitty, not a spawn).
- [ ] T012 [US3] Mutate reds (predictions first): skip the
      generation-time `record_distress` call expecting the tick-0-event
      test red; seed `distress_since` by hand with tick 1 (simulating a
      parallel path) expecting the `distress_since == 0` pin red; make
      the first-tick re-record happen (clear `in_distress` after
      generation) expecting the edge-trigger test red.

## Phase 6: Polish

- [ ] T013 Feature-on smoke per quickstart scenarios 2/3/5 (scratch
      tomls in the scratchpad only, deleted after; NEVER under
      experiments/ — the shipped-config sweep); verify no served or
      committed config carries the section (FR-009 grep).
- [ ] T014 CHANGELOG.md Unreleased entry (public voice, forward-only);
      specs/INDEX.md line for 065.
- [ ] T015 Local gate (`cargo fmt`, `cargo clippy --all-targets`, full
      `cargo test`) + local jscpd at threshold 3.5; SC-001..005
      verified against reality; FR-008 verified by inspection (no
      behavior-API or observation surface touched — name it in the PR
      body, it has no build task); mutate ledger (predictions +
      outcomes) in the PR body.

## Dependencies

T001 first (baseline predates changes). T002 → T003 (types first;
different concerns, same crate — T003 [P] against nothing else) →
T004 → T005 → T006/T007 → US2 (T008 → T009 → T010) → US3 (T011 →
T012) → polish. mutate.sh: commit before each cycle; no tree edits
mid-cycle; one filter per `cargo test -p` invocation.

## Implementation strategy

MVP = Phases 1–3 (landed, validated, provably-inert knob). US2 is the
mechanism; US3 is the welfare-practice guarantee. Each checkpoint
re-proves feature-absent identity.
