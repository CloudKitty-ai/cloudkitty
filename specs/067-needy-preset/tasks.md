# Tasks: Needy Behaviour Preset

**Input**: specs/067-needy-preset/ (plan.md, spec.md, research.md,
data-model.md, contracts/needy-law.md, quickstart.md). Rewritten
2026-10-27 after the analyze pass (`analysis-2026-10-26.md`): every
HIGH, MEDIUM and LOW item is folded; the three mutations that record
found vacuous (old T008's ordering, T009's circularity, T010's teacher
read) are replaced.

**Tests**: included — rule 5 red-first via `scripts/mutate.sh --expect
<regex> <file> <mutation-cmd> <test-cmd>` (file clean against HEAD;
prediction declared BEFORE each run; exit 0 red, 5 no-op, 6 VACUOUS, 7
wrong reason; test-cmd pipelines under `bash -o pipefail`). Rule 6: sort
each phase's checks; kept behaviour green, guards of the change red;
mutate CALL SITES as well as helpers, and re-mutate the validators that
sit BEFORE a new one in the chain (#469's two lessons). Hand-rolled
cycles: none planned; construction-only guards are declared as such.
Scratch configs live in the scratchpad, never under the tree.

**Lane**: Product owns every path below except
`experiments/tools/bc-collect/src/main.rs` (T018), which crosses under
`cross-lane:` with Experiments' consent of 2026-10-26 (research D8;
conditions 1, 2, 4 bind T018 and T021). `specs/066-…/contracts/guard-law.md`
is Product's; its §2 touch is recorded in the PR. Rule-3 report to
Harness: CI never runs bc-collect's tests (D8 CI note).

**Branch**: `product/067-needy-preset`, main merged in at 5841a478
(merge, never rebase or reset; `git fetch` before the PR and read
`gh pr view --json files`).

## Phase 1: Setup

- [X] T001 Record the pre-change pins. (a) In the scratchpad
      `<scratchpad>/067/baseline/` with a throwaway `#[test]` (deleted
      before committing): `engine_defaults_sha256()`; the serialized
      JSON of `Config::default()` (grep: no `needy` key); the serialized
      `World` after `World::generate` + 300 `tick`s through
      `BehaviorRegistry::with_builtins()` at seed 20260718 for
      `cloudkitty.toml` and for `Config::default()`; HEAD SHA. (b)
      COMMITTED goldens (research D12): a new integration test
      `crates/cloudkitty-core/tests/preset_traces.rs` with an
      `#[ignore] emit_preset_traces` writer (the `starts_goldens.rs`
      pattern) that records, per existing preset (`needs_driven`,
      `playful`, `teacher`), 200 decisions on `test_support::test_config()`
      worlds at three seeds (the preset's `decide` output per tick, one
      canonical JSON per preset) into
      `crates/cloudkitty-core/tests/goldens/preset-traces.json`, and a
      running test that compares the live traces with the file. Run the
      writer on the BASE tree (before any engine edit), commit the file.
      Mutate (rule 5 for the golden itself): the wander pressure line
      `pressure < 20.0` (teacher.rs:139) → `< 21.0` → predict the trace
      test red (`needs_driven trace`); this proves the golden sees a
      teacher change. Restore.

## Phase 2: Foundational

- [X] T002 Config section in `crates/cloudkitty-core/src/config/needy.rs`
      (new; `pub mod needy;` in config/mod.rs) + `Config.needy:
      Option<NeedyConfig>` directly after `welfare_hazard` with
      `#[serde(default, skip_serializing_if = "Option::is_none")]` +
      `validate_needy` in `validate.rs` called at position 22 (after
      `validate_welfare_hazard()?`). Shape per data-model.md: `mix:
      Vec<f32>`, `release_level`, `hold_ticks`, `gap {min,max}`,
      `onset_levels: Vec<u64>`, `onset_weights: Vec<f32>`, `onset_draw:
      Flat|LogUniform`; NO floors. `NeedyConfig::default()` = research
      D7's coverage design with `mix` sized by `NeedKind::ALL.len()`
      (never a literal 6) and edges `[0, 2, 10, 50, 200, 20000]`.
      Errors per needy-law §8 (field `[needy].<key>`; the mix-length
      message built from `NeedKind::ALL.len()`). Tests in config/mod.rs
      `mod tests` beside `welfare_hazard_defaults_absent_…`: default
      JSON/TOML lack `needy`; a written section round-trips and
      serializes; every §8 shape through `complete_toml` (wrong-length
      mix names N; negative weight; all-zero; release at the sleep
      floor; hold 0; gap inverted; 5 edges; non-increasing edges;
      weights length mismatch); the defaults validate;
      `fingerprint_ignores_the_needy_section`.
      Mutate A: drop `skip_serializing_if` → predict the absent test red
      (`no needy key`). Mutate B: delete the mix-length check → predict
      the wrong-length test red. Mutate C: `release_level > floor` →
      `>=` → predict the sleep-floor test red. Mutate D: delete the
      `validate_needy()?` CALL at position 22 → predict the wrong-length
      test red again (call site, lesson 2 of #469). Mutate E (re-mutate
      the validator before it in the chain): `validate_welfare_hazard`
      body returns `Ok(())` → predict 066's missing-acknowledgement test
      red (its name quoted in the ledger).
      FR-016 guard: CONSTRUCTION ONLY — a mutation hard-coding `6`
      stays green while N == 6; declared VACUOUS by nature in the ledger
      and covered by a self-review grep for `\b6\b` in the new files.
- [X] T003 The schedule law in `crates/cloudkitty-core/src/needy.rs`
      (new; `pub mod needy;` in lib.rs): `NAME`, `HOLD_NAME`,
      `is_needy_name`; `NeedSet` (bitset over `NeedKind::ALL`, serde as
      sorted need names); `Phase { Resting{next_onset}, Held{onset,
      masked} }`; `ReleaseBy { Level, Limit }`; `Release { tick, by }`;
      `NeedyState { hold, rng: ChaCha8Rng, ordinal, phase, next,
      last_release }`; `sub_stream_seed(world_seed, kitty_id)` tag
      `ck-needy-v1` (bytes 8..12 the kitty id); `uniform(rng) -> f64`
      (the init-law §5 recipe); `NeedyState::new(world_seed, kitty_id,
      hold, &NeedyConfig)` (draws §3.1 then §3.2); `NeedyState::step(&mut
      self, needs: &Needs, t: u64, cfg: &NeedyConfig) ->
      Option<Transition>` (needy-law §4; `Transition { Onset{masked},
      Release{by} }`); `mask()`, `phase_name(t)`;
      `proposer_relief(&Action) -> NeedSet`, `partner_relief(&Action) ->
      NeedSet` (the §5a tables).
      Unit tests: same (seed, id) → identical 10-episode sequence; kitty
      id 2 vs 3 → different; world seed differs → different; level
      release at `>=` (a need exactly at L releases); limit release at
      `t − onset >= hold_ticks`; `hold = true` never releases by level;
      ordinal 0 before the first onset then 1, 2, …; an onset of 0 opens
      at t = 1 (H7) and a gap of 1 opens the next episode at release +
      1; a drawn set has exactly m distinct needs; SC-004's reachability
      over 10,000 draws (every non-zero-weight m and level hit, zero
      weights never, every need appears, proportions within 2 points);
      log-uniform stays inside the level; the draw ORDER and conversion
      are pinned by a recorded trace (the first 20 uniforms and the
      first 3 episodes for seed 1 / kitty 1 under the default config,
      recorded on first implementation and asserted — porting-grade);
      the relief tables' rows as a table test.
      Mutate A: `>=` → `>` in the level check → predict the exactly-at-L
      test red. Mutate B: `hold` branch honours the level → predict the
      hold test red. Mutate C: seed bytes 8..12 dropped → predict the
      id-differs test red. Mutate D: ordinal increments at release
      instead of onset → predict the ordinal test red. Mutate E: swap
      §3.2's draw order (set before m) → predict the pinned-trace test
      red. Mutate F: onset test `>=` → `==` → predict the onset-0 test
      red.
- [X] T004 World wiring in `crates/cloudkitty-core/src/kitty.rs`,
      `world.rs`, `invariants.rs`: `Kitty.needy: Option<NeedyState>`
      with `#[serde(default, skip_serializing_if = "Option::is_none")]`
      (`Kitty::new` sets `None`); `World::try_generate` creates the
      state for every kitty whose configured `behavior`
      `is_needy_name` using `config.needy` or `NeedyConfig::default()`;
      `advance_needy(config)` in Phase 4 directly after
      `self.advance_needs(config)` (world.rs:492) with `t = self.tick +
      1`: `step` each kitty with state; on `Onset` run the ONSET SWEEP
      (data-model: own activity through `end_activity` when its
      continuation's proposer relief meets the mask; other kitties'
      Grooming/Playing on it ended, Resting/Sleeping with it dropped to
      solo); `fog_for` blanks `needy` on every kitty but the observer
      (H4); `invariants::check` asserts `needy.is_some() ==
      is_needy_name(&behavior)` (H3).
      Tests in world.rs tests: a plain config → every `kitty.needy` is
      `None`, the snapshot JSON has no `needy` key; a needy seat → `Some`
      with ordinal 0 and the first onset inside the configured edges;
      after ticking to the onset the phase is `Held` on exactly the
      law's tick and an eating kitty's activity ended on that tick; a
      friend's in-progress co-sleep with the needy kitty stops lowering
      its cuddle from the onset tick while the friend's own sleep relief
      continues (stage with cuddle masked); a friend's groom of it ends
      on the onset tick (bath masked); `fog_for(friend)` shows the needy
      kitty with `needy == None` while `fog_for(self)` keeps it; a
      needy kitty whose `behavior` is edited to `teacher` fails
      `invariants::check` naming it; the state survives a
      serialize/deserialize round trip mid-`Held` and the resumed world
      ticks identically to the uninterrupted one for 100 ticks.
      Mutate A: `advance_needy` call deleted → predict the onset test
      red (`Held on the law's tick`). Mutate B: the own-activity arm of
      the sweep deleted → predict the eating test red. Mutate C: the
      companion-drop arm deleted → predict the co-sleep test red
      (`cuddle unchanged`). Mutate D: the groom arm deleted → predict
      the groom-ends test red. Mutate E: `fog_for`'s blank deleted →
      predict the fog test red. Mutate F: the invariant deleted →
      predict the invariant test red. Mutate G: `try_generate` creates
      state for every kitty → predict the plain-config test red (`no
      needy key`).

**Checkpoint**: the state exists, advances deterministically, hides
from friends, serializes only when present; the sweep holds; nothing
yet judges proposals or chooses under the mask.

---

## Phase 3: User Story 1 — a scripted seat drives needs up mid-world on a declared schedule (P1) 🎯 MVP

**Goal**: the mask is engine law at the apply slot; the two presets
choose sensibly under it; ten episodes behave per needy-law §4–§6.

**Independent Test**: quickstart §2 on a scratch needy config at a fixed
seed.

- [X] T005 [P] [US1] Relief-table cross-check (rule 5's "wrong layer"
      guard) in `crates/cloudkitty-core/src/action.rs` tests: on a probe
      world with every need at 50, a partner adjacent and settled, chow
      and water adjacent, apply each §5a row for one tick; assert the
      set of the ACTOR's needs that moved equals `proposer_relief` and
      the PARTNER's equals `partner_relief`, row by row (Chase and
      Rest{None} move nothing).
      Mutate (in needy.rs): `Groom{Some}`'s proposer row → `Bath` →
      predict the cross-check red (`proposer needs moved`); `Sleep{Some}`'s
      partner row → `Sleep` → predict red (`partner needs moved`).
- [X] T006 [US1] Engine law in `crates/cloudkitty-core/src/world.rs`,
      `action.rs`, `events.rs`: `needy_verdict(proposer, validated,
      config) -> Action` (needy-law §5a) called directly after
      `consent_verdict` at BOTH sites (world.rs:419 served loop; :662
      `apply_slot_verdict`), first line the inert path;
      `World::needy_refuses(proposer, action) -> bool` shared by the
      verdict and `refusal_reason`; `RefusalReason::NeedyMasked` (wire
      `needy_masked`, events.rs) with every exhaustive match extended
      (compiler-found: `cloudkitty-rl` census, server rendering);
      `refusal_reason` (action.rs:442) asks, when `validate` passes the
      proposal, consent first then needy (D15).
      Tests in world.rs tests on a staged world with one needy kitty
      forced into `Held{masked}`: proposer masked on Eat proposes Eat →
      Idle, a refusal record exists for that tick with reason
      `NeedyMasked`; proposer masked on Eat proposes Drink → applies;
      proposer masked on Cuddle proposes Sleep{with} → Idle (relief set
      includes cuddle) and Sleep{None} → applies; a friend proposes
      Rest{with: needy} while Cuddle masked → Idle with reason
      `NeedyMasked` (not PartnerBusy); Groom{target} while Bath masked →
      Idle; Play{Kitty needy} while Play masked → Idle; the same
      proposals with the mask lifted → apply; `apply_slot_verdict`
      agrees with the served path on every case; the friend's legal
      mask (`cloudkitty-rl` mask replay) for Rest{with: needy} is
      LEGAL while masked (hidden state never enters validation).
      Mutate A: delete the `needy_verdict` call at the served site →
      predict the proposer-masked test red (`resolved to Idle`). Mutate
      B: delete the partner clause → predict the friend-Rest test red.
      Mutate C: delete the call at `apply_slot_verdict` → predict the
      agreement test red. Mutate D: `refusal_reason`'s needy check
      deleted → predict the reason test red (`needy_masked`).
- [X] T007 [US1] The presets in `crates/cloudkitty-core/src/behavior/needy.rs`
      (new) + registration in `behavior/mod.rs` `with_builtins` under
      `needy::NAME` / `needy::HOLD_NAME` + `DecisionRng::fork()` in
      rng.rs: `pub struct Needy { hold: bool }`; `decide`: mask empty →
      `Teacher::GEN2.decide(ctx).await`; else masked `me` + `rng.fork()`
      → `Teacher::GEN2.decide_action` → post-filter (relief meets mask
      or Chase under Play mask → `Sleep{Some}`→`Sleep{None}` under a
      cuddle-only mask, else Idle) → message `super::announce(ctx)` on
      the UNMASKED ctx; `is_builtin() = true`; `teaches() = false` (the
      trait method lands in T017; T007 carries it — T017 is folded here
      for the trait line, its registry method and tests stay T017).
      Tests in the module: with `me.needy` absent or `Resting`, `decide`
      equals `Teacher::GEN2.decide` on 200 seeded contexts (byte-equal,
      including the rng draws: same seed, same decision); with Play
      masked and a comfortable kitty, the chosen action is never Play or
      Chase (luxury filtered); with Eat masked and eat at 95, the action
      is not Eat and the serious choice falls to the next need; with
      Cuddle masked, an adjacent friend and sleep high, the action is
      `Sleep{None}`; with Cuddle masked and cuddle above the want line,
      the message may be WantCuddle and is never a sound-named kind
      (FR-007, predicate: `related_need().is_some() || HERE_KINDS || Purr
      || WaitForMe`); registry `names()` is `["needs_driven", "needy",
      "needy_hold", "playful", "teacher"]` (BTreeMap order; update
      `builtins_are_registered_and_marked` and any pinned name list;
      `every_builtin_declines_a_snapshot_dead_scene` passes because the
      stateless path delegates).
      Mutate A: post-filter deleted → predict the luxury test red
      (`never Play under a Play mask`). Mutate B: masked view deleted →
      predict the eat-95 test red (`falls to the next need`). Mutate C:
      `announce` fed the MASKED ctx → predict the WantCuddle test red.
      Mutate D: the delegate branch replaced by the masked path with an
      empty mask → predict the byte-equal test red (the fork is a
      different stream object but the same state — if it stays green
      the test is VACUOUS: then compare the rng state after decide
      instead).
- [X] T008 [US1] Integration scenarios (quickstart §2; SC-003) in
      `crates/cloudkitty-core/src/world.rs` tests with a short-horizon
      `[needy]` (edges `[0, 5, 20, 50, 100, 200]`, hold 200, gap 20–40,
      release 60 — rates 0.5/0.7/0.3/0.4/0.25/0.2 per tick make eat,
      drink, sleep and play reach 60 inside 200 ticks and cuddle and
      bath not, so BOTH release kinds occur; the test asserts at least
      one of each or fails as vacuous — analyze M4) and `test_config()`
      + one `needy` seat: run 10 episodes through `tick` with the
      registry; per tick assert the masked needs are non-decreasing
      apart from the Article I safeguard's relief (FR-013, the WORLD's;
      T016 proves it still fires); the needy kitty's APPLIED action's
      proposer relief never meets the mask; the onset and release ticks
      equal `NeedyState`'s own law replayed on the recorded needs;
      unmasked needs are relieved at least once per episode; a friend
      adjacent proposing Rest{with: needy} every tick is refused exactly
      while Cuddle is masked; the `needy_hold` variant releases only
      `by_limit`; two needy seats (ids 1 and 2) carry different
      schedules and swapping their ids swaps the schedules.
      Mutate: `advance_needy` moved BEFORE `advance_needs` → predict the
      replay test red (`release tick`; the level check reads pre-rise
      needs so a level release lands one tick late — the staging above
      guarantees a level release exists).
- [X] T009 [US1] The recorded redundancy (research D14) in needy.rs
      behaviour tests: with T007's masked view and post-filter disabled
      by a test-only switch (`Needy::decide_unmasked_for_test`), run 300
      ticks on T008's staging and assert the masked needs never
      DECREASE during `Held` except by the safeguard (the engine verdict
      is the law) and that the count of refused turns is strictly higher
      than with the filter on (the filter is advice quality). Mutation:
      the `needy_verdict` served-site call deleted → predict red
      (`masked need decreased`) — this is T006 Mutate A's second
      witness, at the integration layer; say so in the ledger.

**Checkpoint**: US1 complete — the instrument exists and the engine is
its law.

---

## Phase 4: User Story 2 — a world without a needy seat is byte-identical to today (P1)

**Goal**: inert when absent on every surface; the three presets
byte-equal; the swap comparison (SC-002).

**Independent Test**: quickstart §1 against T001's pins.

- [X] T010 [US2] Pins in world.rs / behavior tests / `tests/snapshot_resume.rs`:
      `the_needy_state_never_reaches_a_plain_world` (300 ticks at seed
      20260718 of `Config::default()` with and without a WRITTEN
      `[needy]` section and no needy seat → serialized worlds equal, and
      no `needy` key); the SC-002 swap test (research D17: kitty k on
      `teacher` vs on `needy` with a late first onset, tick 100, strip
      k's `behavior` and `needy`, byte-equal); the decision request to
      an external advisor for a plain config lacks `needy` inside `me`
      and inside `config` (the 066 wire test's shape, behavior/script.rs);
      the preset-traces golden (T001b) still green.
      Mutate A: `try_generate` seeds the master rng with `seed ^
      needy.is_some() as u64` → predict the plain-world test red.
      Mutate B: `NeedyState::new` draws one `u` from the MASTER rng
      (`world.rng`) before its own stream → predict the swap test red
      (`identical until the first onset`). Mutate C: `fingerprint()`
      appends `needy.is_some()` → predict `fingerprint_ignores_the_needy_section`
      red (T002's test; the call-site witness here).
- [ ] T011 [US2] Byte-identity run: `cargo test --workspace` green with
      zero golden/pin/fixture diffs beyond the new goldens file (`git
      status` shows source, tests, specs, CHANGELOG, the collector file
      only); T001's stamp, default JSON and serialized worlds equal the
      post-change values (the same throwaway print); record in the PR
      body. No code.

**Checkpoint**: US2 complete.

---

## Phase 5: User Story 3 — a needy seat is a welfare-hazardous mode (P2)

**Goal**: `needy` and `needy_hold` are 066 modes; sweeps and server
treat them as such.

**Independent Test**: quickstart §5.

- [X] T012 [US3] Registry in `crates/cloudkitty-core/src/config/welfare_hazard.rs`:
      `HazardMode::{InitialNeeds, Needy, NeedyHold}`, `ALL` in that
      order, `name()` → `"initial_needs"` / `needy::NAME` /
      `needy::HOLD_NAME`, `activation()` for the two new modes = the
      first kitty in config order with that behavior, site `[[kitty]]
      '<name>' (id <id>) behavior = "<name>"`; the N4 test
      `all_lists_every_variant_once`: an exhaustive `match` over every
      variant pushes it into a Vec compared with `ALL`. Rows added to
      `specs/066-welfare-hazard-guard/contracts/guard-law.md` §2; 066's
      `the_registry_names_are_unique_and_in_all` and every test pinning
      the `known:` text re-pinned to `initial_needs, needy, needy_hold`
      (rule 6: they go red for the right reason first — record them).
      Tests in config/mod.rs tests: the seven 066 shapes with `needy` as
      the mode (missing names the kitty; exact; unknown; duplicate;
      stale; both presets seated → line `acknowledged = ["needy",
      "needy_hold"]`; with a raised distressed start → `["initial_needs",
      "needy", "needy_hold"]`); `needy_hold` alone.
      Mutate A: `Needy`'s activation returns None → predict the missing
      test red. Mutate B: `ALL` loses `NeedyHold` → predict the N4 test
      red. Mutate C: order swapped (`NeedyHold` before `Needy`) →
      predict the both-seated line test red.
- [X] T013 [US3] Sweep self-tests in
      `crates/cloudkitty-core/tests/shipped_configs.rs` and
      `crates/cloudkitty-rl/tests/shipped_configs_rl.rs` (after T012):
      the existing `hazardous_configs_are_refused_outside_experiments`
      gains a needy file (`complete_toml` + one kitty `behavior =
      "needy"` + acknowledgement): refused under `scratch/specs/` naming
      `needy`, passes under `scratch/experiments/`, refused inside
      `experiments/` when unacknowledged (through the load). No new
      helper; the rule is 066's.
      Mutate (each file): `hazard_outside_experiments` filters the
      active list to `initial_needs` only → predict the needy specs-side
      case red (`names needy`).
- [ ] T014 [US3] Server hand check (quickstart §5) with a scratch needy
      config and scratch port/snapshot: refusal without the switch names
      `needy`; with it the boot line, `GET /config` and the settings row
      name `needy`; both presets seated → both names. Record the three
      outputs in the PR body. Resume guard (D16, code in
      `crates/cloudkitty-server/src/persist.rs`): after the behaviour
      re-stamp, a saved world whose needy state disagrees with the
      configured roster is refused with a `PersistError` naming the
      kitty; test in persist.rs beside
      `a_resumed_world_takes_its_behaviors_from_the_config`: save a
      teacher world, edit the seat to `needy` → refused; save a needy
      world, edit to `teacher` → refused; unchanged → resumes.
      Mutate: the resume check deleted → predict the refused test red
      (`needy seat on resume`).

**Checkpoint**: US3 complete.

---

## Phase 6: User Story 4 — the pattern is observable; welfare law untouched (P2)

**Goal**: mask/ordinal/phase readable per tick; calling on; the world's
law unchanged; the binding's door guarded.

**Independent Test**: quickstart §4 and the FR-013 half of §2.

- [ ] T015 [US4] Binding accessor in `crates/cloudkitty-py/src/lib.rs`
      beside `recent_meows` (:494): `fn needy(&self) ->
      Vec<(u32, Vec<String>, u32, String)>` over the episode world's
      kitties with `needy = Some`, phase names per needy-law §7; the
      Python-side doc line. Control guard (D16) in
      `crates/cloudkitty-rl/src/episode.rs` `Episode::new`: a control
      entry disagreeing with the config seat about needy-ness →
      `EpisodeError::Config` naming the kitty; Rust tests there (needy
      config seat + `External` → refused; teacher seat + `Builtin("needy")`
      → refused; needy seat unnamed → fine). Python test in
      `crates/cloudkitty-py/tests/test_parallel_env.py`: a plain config
      → `env.needy() == []` and `infos` keys unchanged; a needy-seat
      config (acknowledged, short edges) → one tuple whose ordinal is 0
      at reset and whose sequence over 200 steps is self-consistent
      (ordinal non-decreasing by at most 1 per step, masked empty iff
      phase is resting, held set constant within an episode, a
      `released_*` phase appears exactly on the step the ordinal's
      episode ends); `needy_hold` → every released phase is
      `released_limit`; a control override of the needy seat → raises.
      Mutate (Rust, `mutate.sh` with `maturin develop` + pytest as the
      test-cmd under the repo `.venv`): the accessor filters `hold ==
      false` only → predict the needy_hold case red; the control guard
      deleted → predict the override test red (`raises`).
- [X] T016 [US4] Welfare-law and register tests in world.rs tests (share
      T008's staging): with every chow removed and Eat masked past the
      safeguard threshold, the next environment phase spawns a chow
      exactly as for a non-needy kitty forced to the same need (paired
      assertion, same seed) — the safeguard acts on eat/drink only when
      none exist, spawn.rs:179–192, so the staging empties the world;
      the distress record names the needy kitty's masked need at the
      crossing tick; the needy kitty's emitted messages over 300 ticks
      are all law-named kinds (the FR-007 predicate from T007).
      Mutate: `advance_needy` clamps masked needs just below the
      safeguard line → predict the safeguard test red (`chow spawned`).

**Checkpoint**: US4 complete.

---

## Phase 7: User Story 5 — a needy seat can never teach (P2)

**Goal**: the flag exists and the collector refuses, with its own red.

**Independent Test**: quickstart §6.

- [X] T017 [P] [US5] `Behavior::teaches(&self) -> bool { true }` in
      `crates/cloudkitty-core/src/behavior/mod.rs` (landed with T007),
      `BehaviorRegistry::teaches(&self, name: &str) -> Option<bool>`,
      `Needy::teaches() = false`. Tests: the three presets `Some(true)`,
      both needy presets `Some(false)`, unknown `None`, a script/plugin
      behaviour `Some(true)` (the default).
      Mutate A: `Needy::teaches` deleted (default true) → predict red
      (`needy must not teach`). Mutate B: registry returns `Some(true)`
      for unknown → predict the `None` test red.
- [ ] T018 [US5] Collector refusal in
      `experiments/tools/bc-collect/src/main.rs` (CROSS-LANE, Experiments'
      consent 2026-10-26, research D8; conditions 1, 2, 4): a pure
      `fn teachers_refused(registry, config) -> Vec<KittyId>` (seats
      with `registry.teaches(&k.behavior) == Some(false)`; `None` keeps
      today's needs_driven fallback — condition 3 withdrawn); the
      recording loop skips those seats' rows; one `eprintln!` per run
      naming them; the provenance meta gains `"teachers_refused": [ids]`
      (empty array when none). Unit tests in main.rs's test module
      (`cd experiments/tools/bc-collect && cargo test`): a roster with
      one `needy` seat → that id and only that id; a plain roster →
      empty; an unknown behaviour → empty (fallback kept). Then a hand
      run of the binary on a scratch acknowledged needy config: rows for
      the needy seat absent, the other seats' row counts equal a run
      with that seat on `teacher`, the log line present, the meta field
      present — recorded in the PR body with the hunk's commit sha for
      Experiments' read (condition 4). CI never runs these tests (D8 CI
      note): the red is local evidence, said so in the ledger.
      Mutate (test-cmd `cd experiments/tools/bc-collect && cargo test`):
      `teachers_refused` filters `== Some(true)` → predict the needy
      case red (`refuses the needy seat`); the `None` arm treated as
      refused → predict the unknown case red.

**Checkpoint**: US5 complete.

---

## Phase 8: Polish & cross-cutting

- [ ] T019 [P] `CHANGELOG.md` `## Unreleased`: one public-voice entry
      above the 066 entry — two research-only scripted presets that
      stop servicing chosen needs on a seeded schedule so a hidden need
      can be watched arriving mid-world; refused as teachers by
      construction; welfare-hazardous modes under the 066 guard; a new
      refusal reason `needy_masked`; no compatibility marker (stamp,
      obs-schema, fingerprint, draw order unmoved; a needy seat exists
      only in acknowledged research configs).
- [ ] T020 Full `cargo test --workspace` + `cargo clippy --workspace
      --all-targets -- -D warnings` + `cargo fmt --check` + `cd
      experiments/tools/bc-collect && cargo test && cargo clippy -- -D
      warnings` + the binding pytest via `maturin develop --release` in
      the repo `.venv` (`VIRTUAL_ENV` set; ci.yml:114–128 is the
      recipe); jscpd ratchet read; the FR-016 grep (`\b6\b` in the new
      files).
- [ ] T021 PR: `git fetch`; `gh pr view --json files` against
      `scripts/lanes.txt`; open `product/067-needy-preset` → main; body:
      summary, the rule-5 ledger (every cycle; T002's FR-016
      construction-only note; T009's second-witness note; T011's and
      T014's hand-check records; T018's local-only CI note), the T011
      pins, the T014 server outputs, the T018 hand run, and the
      `cross-lane:` paragraph quoting Experiments' consent (2026-10-26,
      option (a), their grounds) with conditions 1, 2, 4 and the
      withdrawn 3; message Experiments the PR number and the T018 hunk's
      commit sha (condition 4) and WAIT for their read before asking
      her to merge; rule-3 report to Harness (bc-collect tests not in
      CI; the two #470 doc-comment items stay for their own touch).
      Self-review comment; fresh subagent review on her word; merge only
      on her word (`gh pr merge N --merge`, never `--delete-branch`).
- [ ] T022 After merge: message Experiments (landed sha; the needy set's
      declaration is theirs on her word); delete the remote branch;
      `git status --ignored` then `git worktree remove` from outside;
      anchor + MEMORY line; note the N4 registry test and the FR-016
      grep for the seventh-need round.

---

## Dependencies

- Phase 1: T001b (the goldens) BEFORE any engine edit.
- Phase 2: T002 ∥ T003 (different files); T004 needs both.
- US1: T005 needs T003 (the tables); T006 needs T005 and T004; T007
  needs T003 and T004 (the state on `me`) and carries the `teaches`
  trait line; T008 needs T006 and T007; T009 needs T008.
- US2: T010 needs T007 and T004; T011 runs last before polish.
- US3: T012 needs T003's name constants; T013 needs T012 (the mode
  must exist for the needy file to be refused by name); T014 needs
  T012 and T004.
- US4: T015 needs T004 and T003; T016 needs T008's staging.
- US5: T017 needs T007 (the trait line lands there); T018 needs T017.
- Phase 8 needs everything; T021 waits for Experiments' read of T018's
  hunk.

## Parallel execution examples

- After Phase 2: T005 + T007 together (different files); their mutate
  cycles one at a time (no tree edits while one runs).
- T015 (binding) alongside T012 (registry).
- T019 while T020 runs.

## Implementation strategy

MVP = Phase 2 + US1 (the instrument exists and the engine is its law).
Then US2 (prove inert), US3 (hazard), US4 (observable + welfare law +
the binding door), US5 (eligibility + collector), Phase 8. One PR:
FR-011 forbids a landed preset the collector can still record, which is
why the collector half rides along (Experiments' grounds for option
(a)).
