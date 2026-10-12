# Tasks: Empty-Bowl Early End (spec-006 amendment)

**Input**: Design documents from `specs/060-empty-bowl/`

**Prerequisites**: plan.md, spec.md (clarified through 2026-10-11),
research.md (R1-R7), data-model.md, contracts/scene-end.md,
quickstart.md

**Tests**: INCLUDED — house rules 5/6 make them mandatory: every new
or changed assertion goes through `scripts/mutate.sh --expect
<prediction>` red-first, and changed behavior gets its checks sorted
before running (guards red, kept pile green). The file must be clean
vs HEAD when mutate.sh runs — commit first.

**Organization**: by user story. US1 = the early end (the engine
change). US2 = generation-boundary accounting (declared divergence).

## Format: `[ID] [P?] [Story?] Description with file path`

## Phase 1: Setup

- [ ] T001 Record the pre-change baseline in the worktree: `cargo test --workspace` green count at branch HEAD, noted in the eventual PR self-review draft (scratch note is fine); confirm `git status` clean in /Users/elizabethkelly/ai/cloudkitty-empty-bowl

---

## Phase 2: Foundational (rule-6 sort, blocking)

**Purpose**: sort the spec-006 test pile BEFORE touching the engine,
so every red and green is predicted, not discovered.

- [ ] T002 Read and sort the spec-006/056 meal+duration tests per research.md R4 into must-flip vs must-stay-green, READING each must-pass test body (not just running it): crates/cloudkitty-core/src/world.rs tests (:3435, :3470, :3511, :3548, :3571-3672, :3699, :3718, :3751, :3229-3328) and crates/cloudkitty-core/src/action.rs tests (:1103, :1213, :1228, :3542); record the sorted lists with per-test predictions in specs/060-empty-bowl/test-sort.md (committed)
- [ ] T003 Confirm the must-flip pile goes red against the NEW behavior before the engine moves: rewrite is staged in US1; here only verify `an_emptied_bowl_pauses_below_the_minimum_and_ends_at_it` (world.rs:3718) currently passes and `announcing_food_and_eating_it_all_is_lawful` (action.rs:3542) read-through decides whether it joins the must-flip pile; update specs/060-empty-bowl/test-sort.md with the verdict

**Checkpoint**: sorted piles on file — engine work may begin

---

## Phase 3: User Story 1 — The bowl ends the meal when it empties (P1) 🎯 MVP

**Goal**: an eating scene whose feeding condition fails ends at that
tick's resolution, minimum met or not; everything else byte-identical.

**Independent Test**: spec US1 — no eating scene survives a resolution
that finds its feeding condition failed; `need_zero_before_the_minimum_waits_for_the_minimum`
and the rest of the kept pile stay green.

### Tests first (red before the engine edit)

- [ ] T004 [US1] Rewrite `an_emptied_bowl_pauses_below_the_minimum_and_ends_at_it` (crates/cloudkitty-core/src/world.rs:3718, `dinner_table(1)`) as the early-end guard: scene ends at the FIRST `close_tick` whose resolution finds the feeding condition failed, span recorded, kitty clock cleared; rename to say what it now pins. Run it against the unamended engine and CONFIRM RED with the predicted failure (this red is rule 5's red for FR-001)
- [ ] T005 [US1] Add the acceptance-scenario guards in the same world.rs test module, each confirmed RED pre-edit: (a) scenario 1 — below-minimum last serving consumed → end at that resolution, freed kitty decides freely next tick; (b) scenario 4 / FR-004 — two eaters, bowl empties, neither has another feeding read → both end at the same resolution regardless of turn order; (c) scenario 5 both sub-cases — farther bowl empties → scene continues; fed-from bowl empties beside a stocked one → scene ends (nearest-empty geometry, and the id-tiebreak variant); (d) edge case — one-tick meal (start on last serving) → span 1, exactly one serving's relief, minimum never engages
- [ ] T006 [US1] Add the FR-003 guard: an early end writes an activity_log end record and NO refusal_log row (extend beside `duration_enforcement_decides_the_absorbed_flag_never_the_refusal`, world.rs:3273); confirm the new assertion's red via a staged mutation plan (it may be green pre-edit — if so it is a kept-behavior pin, record that in test-sort.md and rely on T009's mutate cycle for its red)

### The engine edit

- [ ] T007 [US1] Amend `resolve_activity_ends` in crates/cloudkitty-core/src/world.rs:736-740: `done_naturally = (elapsed >= bounds.min && governed_done) || out_of_chow;` — touch nothing else (bounds.max cap, end_activity, duration_ruling hold all unchanged); update the function's doc comment at :668-669 to state the amended rule
- [ ] T008 [US1] Run the sorted piles: T004-T006 guards green; the full must-stay-green pile from test-sort.md green (`cargo test -p cloudkitty-core --lib`); any must-fail that stayed green is vacuous — fix or report per rule 6, on record in test-sort.md
- [ ] T009 [US1] Mutate cycles for every new/changed assertion (commit first; file clean vs HEAD): `scripts/mutate.sh --expect <prediction> crates/cloudkitty-core/src/world.rs '<revert the condition to spec-006 grouping>' '<test cmd>'` per guard, plus a mutation making the end ignore the feeding read (e.g. `out_of_chow` forced false) to red the scenario-5 and one-tick guards; record each RED CONFIRMED in test-sort.md

**Checkpoint**: US1 complete — engine behavior shipped and guarded

---

## Phase 4: User Story 2 — The change rides the generation boundary (P2)

**Goal**: every moved deterministic pin re-recorded with spec 060
named and first-divergence ticks captured; Gen 1 served world
untouched.

**Independent Test**: spec US2 — divergence declared per fixture in
the 059 artifact style; CHANGELOG carries `[rng-sequence]`; config
sweeps green with zero config edits.

- [ ] T010 [US2] Run `cargo test -p cloudkitty-core --test fog_continuity`; for each red comparison test capture the first-divergence tick BEFORE re-recording, append the justification paragraph naming spec 060 to the re-record history blocks (crates/cloudkitty-core/tests/fog_continuity.rs:203-227 and :476-505, 059 entry at :220 is the pattern), then re-record via the `#[ignore]`d mains (`record_prefog_streams` :441, `record_preladder_r5_streams` :547) and commit the moved fixtures in crates/cloudkitty-core/tests/fixtures/
- [ ] T011 [US2] Run `cargo test -p cloudkitty-core --test evolution_golden`; if the refusal-ring delta moved (absorbed Eat rows vanishing), re-pin with the same declaration style in crates/cloudkitty-core/tests/evolution_golden.rs; if green, record that in test-sort.md (the absorbed-row drop may sit outside the golden window)
- [ ] T012 [US2] Sweep the remaining pin surfaces and re-pin only what reddens, each with a declared reason: core tests snapshot_resume.rs, joint_action_parity.rs, roam_tether.rs, consent_gate.rs, waterline_contagion.rs; rl tests run_json_golden.rs, eval_suite.rs, welfare_longrun.rs, harness_policy.rs, mixed_control.rs, clock_and_range.rs, artifact_v3_parity.rs, vocabulary_flags.rs (`cargo test --workspace` covers all)
- [ ] T013 [US2] SC-003 welfare evidence: a differential recorder (059 fire-counter pattern, `#[ignore]`d recorder test beside the fog_continuity ones or in consent_gate.rs style) counting on the reference config, same seeds, both arms: (a) eating-scene ticks whose resolution-time feeding condition is failed — must be >0 pre-change, 0 post-change; (b) total eat relief delivered — equal across arms; commit the one artifact under crates/cloudkitty-core/tests/fixtures/ with the twin-config/one-data-point caveat stated if it applies
- [ ] T014 [US2] Fresh binding: `maturin develop` with VIRTUAL_ENV set (the pre-059-remediation scratchpad binding is stale), then run the binding pytest including test_reproducibility.py and test_parallel_env.py; record counts
- [ ] T015 [US2] CHANGELOG.md Unreleased: add the `[rng-sequence]` entry naming spec 060 (public-voice at write time, forward-only); confirm shipped-config sweeps green with ZERO config edits (`cargo test -p cloudkitty-core --test shipped_configs`, `cargo test -p cloudkitty-rl --test shipped_configs_rl`)

**Checkpoint**: divergence fully declared and counted

---

## Phase 5: Polish & Cross-Cutting

- [ ] T016 Fix the now-stale comment in cloudkitty.toml:300-304 ("a finished need (or an empty bowl) ends the activity early once `min` is met") to state the amended rule — comment-only recording edit, stated on the PR per the hook-review carve-out; no key or value changes
- [ ] T017 Remove the shelved BACKLOG entry at BACKLOG.md:90-111 ("Spec-006 empty-bowl early end — SHELVED UNTIL GEN 2") so it lands with the merge (FR-007); verify the surrounding entries are untouched
- [ ] T018 Update specs/INDEX.md with the 060 row; verify specs/060-empty-bowl/ package complete (spec, plan, research, data-model, contracts, quickstart, tasks, test-sort)
- [ ] T019 Full verification pass: `cargo fmt --all`, `cargo test --workspace` (record the count against T001's baseline — expected delta is the new guards), quickstart.md steps 1-5 executed as written; assemble the verification record (mutate cycles, sorted piles, fixture declarations, SC counts) for the PR self-review comment

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3 (strict: the sort precedes the edit;
  T004-T006 red before T007; T008-T009 after T007)
- Phase 4 requires Phase 3 (pins move only once the engine moved);
  T010-T012 before T014 (binding pytest sees final fixtures); T013
  anytime after T007
- Phase 5 last; T016/T017/T018 independent of each other ([P]-able
  but trivial); T019 final
- Single-lane work: nearly everything funnels through
  cloudkitty-core/src/world.rs or the one test run, so parallel
  markers are deliberately absent except where files truly disjoint

## Implementation Strategy

MVP = Phases 1-3 (US1): the engine rule, guarded red-first — spec
US1's "everything else is accounting" holds. US2 cannot be skipped
before merge (the shelf ruling's safety is the accounting), but the
checkpoint after Phase 3 is a valid review point. Commit per task or
logical group; mutate.sh requires the clean-file discipline, so
commits precede cycles.
