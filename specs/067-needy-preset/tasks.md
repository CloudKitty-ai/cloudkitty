# Tasks: Needy Behaviour Preset

**Input**: specs/067-needy-preset/ (plan.md, spec.md, research.md,
data-model.md, contracts/needy-law.md, quickstart.md)

**Tests**: included — rule 5 red-first via `scripts/mutate.sh --expect
<regex> <file> <mutation-cmd> <test-cmd>` (file clean against HEAD;
prediction declared BEFORE each run; exit 0 red, 5 no-op, 6 VACUOUS, 7
wrong reason). Rule 6: sort each phase's checks; kept behaviour green,
guards of the change red; mutate CALL SITES as well as helpers, and
re-mutate the validators that sit BEFORE a new one in the chain (the two
lessons of #469). No hand-rolled cycle is planned; one construction-only
guard is declared as such (FR-016, T002). Scratch configs live in the
scratchpad, never under the tree.

**Lane**: Product owns every path below except
`experiments/tools/bc-collect/src/main.rs` (T018), which crosses under
`cross-lane:` with Experiments' consent of 2026-10-26 (research D8;
their three standing conditions bind T018 and T021). `specs/066-…/
contracts/guard-law.md` is Product's; its §2 touch is recorded in the
PR.

**Branch base**: d7917b01 (main moved past it: #470's bench fix may
land first; never reset onto moved main; `git fetch` before the PR and
read `gh pr view --json files`).

## Phase 1: Setup

- [ ] T001 Record the pre-change pins in `<scratchpad>/067/baseline/`
      with a throwaway `#[test]` (deleted before committing; `git
      status` clean after): `engine_defaults_sha256()`; the serialized
      JSON of `Config::default()` (grep: no `needy` key); the serialized
      `World` after `World::generate` + 300 `tick`s through
      `BehaviorRegistry::with_builtins()` at seed 20260718 for
      `cloudkitty.toml` and for `Config::default()` (two files); a
      200-decision trace per existing preset (`needs_driven`,
      `playful`, `teacher`) on `test_support::test_config()` worlds at
      three seeds (the preset's `decide` output per tick, JSON); HEAD
      SHA. T010 compares against these.

## Phase 2: Foundational

- [ ] T002 Config section in `crates/cloudkitty-core/src/config/needy.rs`
      (new; `pub mod needy;` in mod.rs) + `Config.needy:
      Option<NeedyConfig>` directly after `welfare_hazard` with
      `#[serde(default, skip_serializing_if = "Option::is_none")]` +
      `validate_needy` in `validate.rs` called at position 22 (after
      `validate_welfare_hazard()?`). Shape per data-model.md: `mix:
      Vec<f32>`, `release_level`, `hold_ticks`, `gap {min,max}`,
      `onset_levels: Vec<u64>`, `onset_weights: Vec<f32>`, `onset_draw:
      Flat|LogUniform`, `floors: BTreeMap<String, f32>`;
      `NeedyConfig::default()` = research D7's coverage design with
      `mix` sized by `NeedKind::ALL.len()` (never a literal 6). Errors
      per needy-law §8 (field `[needy].<key>`; the mix-length message
      built from `NeedKind::ALL.len()`). Tests in mod.rs `mod tests`
      beside `welfare_hazard_defaults_absent_…`: default JSON/TOML lack
      `needy`; a written section round-trips and serializes; every §8
      shape through `complete_toml` (wrong-length mix names N; negative
      weight; all-zero; release below the sleep floor; hold 0; gap
      inverted; 5 edges; weights length mismatch; unknown floor key
      names it; floor out of range); the defaults validate.
      Mutate A: drop `skip_serializing_if` → predict the absent test red
      (`no 067 key`). Mutate B: delete the mix-length check → predict
      the wrong-length test red (`expected Err for a wrong-length mix`).
      Mutate C: `release_level > floor` → `>=` → predict the sleep-floor
      test red. Mutate D: delete the unknown-floor-key check → red.
      FR-016 guard: CONSTRUCTION ONLY — a mutation hard-coding `6`
      stays green while N == 6; declared VACUOUS by nature in the ledger
      and covered by a self-review grep for `\b6\b` in the new files.
- [ ] T003 The schedule law in `crates/cloudkitty-core/src/needy.rs`
      (new; `pub mod needy;` in lib.rs): `NeedSet` (bitset over
      `NeedKind::ALL`, rendered as names), `Phase`, `NeedyState { hold,
      rng: ChaCha8Rng, ordinal, phase, next }`, `sub_stream_seed(world_seed,
      kitty_id)` with tag `ck-needy-v1` (starts.rs:94 / init_needs.rs:40
      shape + kitty id at bytes 8..12), `NeedyState::new(world_seed,
      kitty_id, hold, &NeedyConfig)` (draws §3.1 then §3.2),
      `NeedyState::advance(&mut self, needs: &Needs, tick: u64, cfg:
      &NeedyConfig) -> Option<Transition>` (needy-law §4; `Transition
      { Onset { masked }, Release { by } }`), `mask(&self) -> NeedSet`.
      Unit tests: same (seed, id) → identical 10-episode sequence;
      kitty id 2 vs 3 → different; world seed differs → different;
      level release at `>=` (a need exactly at L releases); limit
      release at `tick − onset >= hold_ticks`; `hold = true` never
      releases by level; ordinal 0 before the first onset then 1, 2, …;
      a drawn set has exactly m distinct needs and m's frequency over
      10,000 draws matches `mix` within 2%; first onsets over 10,000
      seeds land in every level with non-zero weight in weight
      proportion and never in a zero-weight level; log-uniform stays
      inside the level; the draw ORDER is pinned by a recorded trace
      (the first 20 draws for seed 1/kitty 1 under the default config,
      recorded on first implementation and asserted).
      Mutate A: `>=` → `>` in the level check → predict the exactly-at-L
      test red. Mutate B: `hold` branch honours the level → predict the
      hold test red. Mutate C: seed bytes 8..12 dropped → predict the
      id-differs test red. Mutate D: ordinal increments at release
      instead of onset → predict the ordinal test red. Mutate E: swap
      §3.2's draw order (set before m) → predict the trace test red.
- [ ] T004 World wiring in `crates/cloudkitty-core/src/kitty.rs` and
      `world.rs`: `Kitty.needy: Option<NeedyState>` with
      `#[serde(default, skip_serializing_if = "Option::is_none")]`;
      `World::try_generate` creates the state for every kitty whose
      `behavior` is `needy::NAME` or `needy::HOLD_NAME` (constants from
      T007's module — declare them in `core/src/needy.rs` so T004 does
      not wait on T007) using `config.needy` or `NeedyConfig::default()`;
      `advance_needy(config)` in Phase 4 directly after
      `self.advance_needs(config)` (world.rs:492): for each kitty with
      state, `advance`; on `Onset` end the kitty's own activity if its
      `governing_need()` is masked (the existing `end_activity` path).
      Tests in world.rs tests: a plain config → every `kitty.needy` is
      `None` and the snapshot JSON has no `needy` key; a needy seat →
      `Some` with ordinal 0 and the first onset inside the configured
      edges; after ticking to the onset the phase is `Held` and an
      eating kitty's activity ended on that tick; the state survives a
      serialize/deserialize round trip and continues identically (resume).
      Mutate A: `advance_needy` call deleted → predict the onset test
      red (`phase is Held at onset`). Mutate B: the activity-ending
      branch deleted → predict the activity test red. Mutate C: the
      `None` default made `Some(..)` for every kitty → predict the
      plain-config test red (`no needy key`).

**Checkpoint**: the state exists, advances deterministically, serializes
only when present; nothing yet enforces or chooses under the mask.

---

## Phase 3: User Story 1 — a scripted seat drives needs up mid-world on a declared schedule (P1) 🎯 MVP

**Goal**: the mask is engine law at the apply slot and in partner
availability; the two presets choose sensibly under it; ten episodes
behave per needy-law §4–§6.

**Independent Test**: quickstart §2 on a scratch needy config at a fixed
seed.

- [ ] T005 [P] [US1] `pub fn partner_relief(action: &Action) ->
      Option<NeedKind>` in `crates/cloudkitty-core/src/action.rs`
      (Groom{target: Some} → Bath; Play{target: Kitty} → Play;
      Rest{with: Some} → Cuddle; Sleep{with: Some} → Cuddle; else
      None) and `pub fn governing_need_of(action: &Action) ->
      Option<NeedKind>` (through `Activity::governing_need`, kitty.rs:152).
      Cross-check test (rule 5's "wrong layer" guard): on a probe world,
      apply each partnered action for one tick with the partner adjacent
      and settled; assert the set of the PARTNER's needs that moved is
      exactly `{partner_relief(action)}`.
      Mutate: Sleep's row → `Sleep`'s partner relief returned as `Sleep`
      → predict the cross-check red (`partner needs moved`).
- [ ] T006 [US1] Engine law in `crates/cloudkitty-core/src/world.rs`:
      `needy_verdict(proposer, validated, config) -> Action` (needy-law
      §5) called directly after `consent_verdict` at BOTH sites
      (world.rs:419 served loop; :662 `apply_slot_verdict`) — returns
      the input immediately when neither party carries state (the inert
      path); `available_friend_in` returns false when the friend's mask
      contains the duet's partner-relief need (Resting/Sleeping with →
      Cuddle; Grooming target → Bath). Tests in world.rs tests on a
      staged world with one needy kitty forced into `Held{masked}`:
      proposer masked on Eat proposes Eat → Idle and a refusal record
      exists for that tick; proposer masked on Eat proposes Drink →
      Drink applies; a friend proposes Rest{with: needy} while Cuddle
      masked → Idle; Groom{target} while Bath masked → Idle; the same
      proposals with the mask lifted → apply; an in-progress cosleep
      with the needy partner stops lowering the needy kitty's cuddle on
      the onset tick (apply one tick, cuddle unchanged) while the friend's
      own sleep relief continues; `apply_slot_verdict` agrees with the
      served path on every case.
      Mutate A: delete the `needy_verdict` call at the served site →
      predict the proposer-masked test red (`resolved to Idle`). Mutate
      B: delete the partner clause → predict the friend-Rest test red.
      Mutate C: `available_friend_in`'s mask rule deleted → predict the
      in-progress-cosleep test red (`cuddle unchanged`). Mutate D:
      delete the call at `apply_slot_verdict` → predict the agreement
      test red.
- [ ] T007 [US1] The presets in `crates/cloudkitty-core/src/behavior/needy.rs`
      (new) + registration in `behavior/mod.rs` `with_builtins` after
      `teacher`: `pub struct Needy { hold: bool }`, `pub const NEEDY:
      Needy`, `pub const NEEDY_HOLD: Needy`; `decide`: masked view (clone
      `ctx` with `me.needs` set to 0 for masked kinds) →
      `Teacher::GEN2.decide_action(&masked)` → post-filter (if
      `governing_need_of(action)` ∈ mask → `wander(ctx)` or Idle) →
      message `super::announce(ctx)` on the UNMASKED ctx; `is_builtin()
      = true`; `teaches() = false` (T017 adds the trait method; T007 may
      land after it or carry the default). Tests in the module: with
      `me.needy` absent or `Resting`, `decide` equals
      `Teacher::GEN2.decide` on 200 seeded contexts (byte-equal trace);
      with Play masked and a comfortable kitty, the chosen action is
      never Play (luxury filtered); with Eat masked and eat at 95, the
      action is not Eat and the serious choice falls to the next need;
      with Cuddle masked and cuddle above the want line, the message may
      be WantCuddle and is never a sound-named kind (FR-007); registry
      names are `["needs_driven", "playful", "teacher", "needy",
      "needy_hold"]` (update `the_registry_lists_the_builtins` test and
      any pinned name list).
      Mutate A: post-filter deleted → predict the luxury test red
      (`never Play under a Play mask`). Mutate B: masked view deleted →
      predict the eat-95 test red (`falls to the next need`). Mutate C:
      `announce` fed the MASKED ctx → predict the WantCuddle test red.
- [ ] T008 [US1] Integration scenarios (quickstart §2; SC-003) in
      `crates/cloudkitty-core/src/world.rs` tests with a short-horizon
      `[needy]` (edges `[0, 5, 20, 50, 100, 200]`, hold 150, gap 20–40,
      release 80) and `test_config()` + one `needy` seat: run 10
      episodes through `tick` with the registry; per tick assert the
      masked needs are non-decreasing apart from `sleep_floor_off_beam`
      and the Article I safeguard's relief (which is the WORLD's, FR-013
      — assert it still fires: a masked need past the safeguard line
      spawns its resource, and the distress record names it); the needy
      kitty's APPLIED action never carries a masked governing need; the
      onset and release ticks equal `NeedyState`'s own law replayed on
      the recorded needs; unmasked needs are relieved at least once per
      episode; a friend adjacent proposing Rest{with: needy} every tick
      is refused exactly while Cuddle is masked; the `needy_hold`
      variant releases only `by_limit`; two needy seats (ids 1 and 2)
      carry different schedules and swapping their ids swaps the
      schedules.
      Mutate: `advance_needy` placed BEFORE `advance_needs` → predict the
      onset/release-tick test red (the law replay disagrees by one tick:
      `release tick`).
- [ ] T009 [US1] The recorded redundancy (research D14) in needy.rs
      behaviour tests: with T007's masked view and post-filter disabled
      by a test-only switch (`Needy::decide_unmasked_for_test`), run 300
      ticks and assert every APPLIED action is still legal under the
      mask (the engine verdict is the law) and that the count of
      refused turns is strictly higher than with the filter on (the
      filter is advice quality). No mutation of its own: it is the
      reading of T006's law against T007's advice; say so in the ledger.

**Checkpoint**: US1 complete — the instrument exists and the engine is
its law.

---

## Phase 4: User Story 2 — a world without a needy seat is byte-identical to today (P1)

**Goal**: inert when absent on every surface; the three presets
byte-equal.

**Independent Test**: quickstart §1 against T001's pins.

- [ ] T010 [US2] Pins in mod.rs / world.rs / behavior tests:
      `fingerprint_ignores_the_needy_section` (a config with `[needy]`
      and a needy seat vs the bare config — note the SEAT changes a
      kitty's behavior string, which the fingerprint never read; assert
      equal); `the_needy_state_never_reaches_a_plain_world` (300 ticks
      at seed 20260718 of `Config::default()` with and without a WRITTEN
      `[needy]` section and no needy seat → serialized worlds equal;
      and the T001-recorded serialized world equals the branch's,
      compared in T011); the three presets' 200-decision traces equal
      T001's recordings (recorded files read from the scratchpad in a
      `#[ignore]`-free test that takes the path from an env var and
      skips with a printed notice when unset — the PR body records the
      run); the decision request to an external advisor for a plain
      config lacks `needy` inside `me` and inside `config` (the 066
      wire test's shape).
      Mutate A: `fingerprint()` appends `needy.is_some()` → red
      (`orphan`). Mutate B: `try_generate` seeds the master rng with
      `seed ^ needy.is_some() as u64` → predict the plain-world test red.
      Mutate C: `Teacher::decide_action` gains a read of `ctx.me.needy`
      that changes a rung → predict the trace test red (D12).
- [ ] T011 [US2] Byte-identity run: `cargo test --workspace` green with
      zero golden/pin/fixture diffs (`git status` shows source, tests,
      specs, CHANGELOG, the collector file only); T001's stamp, default
      JSON and serialized worlds equal the post-change values (the same
      throwaway print); record in the PR body. No code.

**Checkpoint**: US2 complete.

---

## Phase 5: User Story 3 — a needy seat is a welfare-hazardous mode (P2)

**Goal**: `needy` and `needy_hold` are 066 modes; sweeps and server
treat them as such.

**Independent Test**: quickstart §5.

- [ ] T012 [US3] Registry in `crates/cloudkitty-core/src/config/welfare_hazard.rs`:
      `HazardMode::{InitialNeeds, Needy, NeedyHold}`, `ALL` in that
      order, `name()` → `"initial_needs"` / `needy::NAME` /
      `needy::HOLD_NAME`, `activation()` for the two new modes = the
      first kitty in config order with that behavior, site `[[kitty]]
      '<name>' (id <id>) behavior = "<name>"`; the N4 test
      `all_lists_every_variant_once`: an exhaustive `match` over every
      variant pushes it into a Vec compared with `ALL` (a new variant
      fails to compile until placed). Rows added to
      `specs/066-welfare-hazard-guard/contracts/guard-law.md` §2.
      Tests in mod.rs tests: the seven 066 shapes with `needy` as the
      mode (missing names the kitty; exact; unknown; duplicate; stale;
      both presets seated → line `acknowledged = ["needy",
      "needy_hold"]`; with a raised distressed start → `["initial_needs",
      "needy", "needy_hold"]`); `needy_hold` alone.
      Mutate A: `Needy`'s activation returns None → predict the missing
      test red. Mutate B: `ALL` loses `NeedyHold` → predict the N4 test
      red. Mutate C: order swapped (`NeedyHold` before `Needy`) →
      predict the both-seated line test red.
- [ ] T013 [P] [US3] Sweep self-tests in
      `crates/cloudkitty-core/tests/shipped_configs.rs` and
      `crates/cloudkitty-rl/tests/shipped_configs_rl.rs`: the existing
      `hazardous_configs_are_refused_outside_experiments` gains a needy
      file (`complete_toml` + one kitty `behavior = "needy"` +
      acknowledgement): refused under `scratch/specs/` naming `needy`,
      passes under `scratch/experiments/`, refused inside
      `experiments/` when unacknowledged (through the load). No new
      helper; the rule is 066's.
      Mutate (each file): `hazard_outside_experiments` filters the
      active list to `initial_needs` only → predict the needy specs-side
      case red (`names needy`).
- [ ] T014 [US3] Server hand check (quickstart §5) with a scratch needy
      config and scratch port/snapshot: refusal without the switch names
      `needy`; with it the boot line, `GET /config` and the settings row
      name `needy`; both presets seated → both names. Record the three
      outputs in the PR body. No code (the gate's red is 066's).

**Checkpoint**: US3 complete.

---

## Phase 6: User Story 4 — the pattern is observable; welfare law untouched (P2)

**Goal**: mask/ordinal/phase readable per tick; calling on; the world's
law unchanged.

**Independent Test**: quickstart §4 and the FR-013 half of §2.

- [ ] T015 [US4] Binding accessor in `crates/cloudkitty-py/src/lib.rs`
      beside `recent_meows` (:494): `fn needy(&self) ->
      Vec<(u32, Vec<String>, u32, String)>` over
      `self.episode.world().kitties` with `needy = Some`, phase names
      per needy-law §7; the Python-side doc line. Test in
      `crates/cloudkitty-py/tests/test_parallel_env.py`: a plain config
      → `env.needy() == []` and `infos` keys unchanged; a needy-seat
      config (acknowledged) → one tuple whose ordinal is 0 at reset and
      whose phase/masked set at each of 200 steps equals the law replay
      (replayed in Python from the same seed via the tuple sequence's
      own consistency: ordinal non-decreasing, masked empty iff phase
      is resting, held set constant within an episode).
      Mutate (Rust, `mutate.sh` with `maturin develop` + pytest as the
      test-cmd): the accessor filters `hold == false` only → predict the
      needy_hold case red; the accessor returns `[]` always → predict
      the needy case red.
- [ ] T016 [US4] Welfare-law and register tests in world.rs tests (may
      share T008's staged world): a masked need crossing the safeguard
      threshold spawns its resource on the next environment phase
      exactly as for a non-needy kitty (paired assertion, same seed,
      needy vs forced-high needs_driven); the distress record names the
      needy kitty's masked need at the crossing tick; the needy kitty's
      emitted messages over 300 ticks are all law-named kinds
      (`MessageKind::is_law_named()` or the equivalent predicate — find
      the one home); every other kitty's per-tick record in the
      `TickReport` is byte-identical between a world with a needy seat
      REPLACED by a `teacher` seat at the SAME decisions (not required —
      drop if no fair construction exists; say so).
      Mutate: `advance_needy` skips the safeguard by clamping masked
      needs below the line → predict the safeguard test red (`resource
      spawned`).

**Checkpoint**: US4 complete.

---

## Phase 7: User Story 5 — a needy seat can never teach (P2)

**Goal**: the flag exists and the collector refuses, with its own red.

**Independent Test**: quickstart §6.

- [ ] T017 [P] [US5] `Behavior::teaches(&self) -> bool { true }` in
      `crates/cloudkitty-core/src/behavior/mod.rs`,
      `BehaviorRegistry::teaches(&self, name: &str) -> Option<bool>`,
      `Needy::teaches() = false`. Tests: the three presets `Some(true)`,
      both needy presets `Some(false)`, unknown `None`, a plugin/script
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
      (empty array when none, so every corpus after this says which).
      Unit tests in main.rs's test module (`cd experiments/tools/bc-collect
      && cargo test`): a roster with one `needy` seat → that id and only
      that id; a plain roster → empty; an unknown behaviour → empty
      (fallback kept). Then a hand run of the binary on a scratch
      acknowledged needy config: rows for the needy seat absent, the
      other seats' row counts equal a run with that seat on `teacher`,
      the log line present, the meta field present — recorded in the PR
      body with the hunk's commit sha for Experiments' read (condition
      4).
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
      construction; welfare-hazardous modes under the 066 guard; no
      compatibility marker (stamp, obs-schema, fingerprint, draw order
      unmoved; a needy seat exists only in acknowledged research configs).
- [ ] T020 Full `cargo test --workspace` + `cargo clippy --workspace
      --all-targets -- -D warnings` + `cargo fmt --check` + `cd
      experiments/tools/bc-collect && cargo test && cargo clippy -- -D
      warnings` + the binding pytest via `maturin develop` in the lab
      venv (`VIRTUAL_ENV` set); jscpd ratchet read.
- [ ] T021 PR: `git fetch`; `gh pr view --json files` against
      `scripts/lanes.txt`; open `product/067-needy-preset` → main; body:
      summary, the rule-5 ledger (every cycle; T002's FR-016
      construction-only note; T009's and T014's no-mutation notes), the
      T011 pins, the T014 server outputs, the T018 hand run, and the
      `cross-lane:` paragraph quoting Experiments' consent (2026-10-26,
      option (a), their grounds) with conditions 1, 2, 4 and the
      withdrawn 3; message Experiments the PR number and the T018 hunk's
      commit sha (condition 4) and WAIT for their read before asking
      her to merge. Self-review comment; medium/high-effort fresh
      subagent review on her word; merge only on her word (`gh pr merge
      N --merge`, never `--delete-branch`).
- [ ] T022 After merge: message Experiments (landed sha; the needy set's
      declaration is theirs on her word); delete the remote branch;
      `git status --ignored` then `git worktree remove` from outside;
      anchor + MEMORY line; note the N4 registry test and the FR-016
      grep for the seventh-need round.

---

## Dependencies

- Phase 2: T002 ∥ T003 (different files); T004 needs both (the state
  type and the config).
- US1: T005 ∥ T007 after Phase 2; T006 needs T005 (the relief table) and
  T004; T008 needs T006 and T007; T009 needs T008's staging.
- US2: T010 needs T007 (preset traces) and T004; T011 needs everything
  in US1–US5 that changes code (run last before polish).
- US3: T012 needs T007's name constants (declared in `core/src/needy.rs`
  by T003/T004, so T012 can start after Phase 2); T013 ∥ T012; T014
  needs T012.
- US4: T015 needs T004 (the state in the snapshot) and T003; T016 needs
  T008's staging.
- US5: T017 ∥ T005 (different files); T018 needs T017.
- Phase 8 needs everything; T021 waits for Experiments' read of T018's
  hunk.

## Parallel execution examples

- After Phase 2: T005 + T007 + T013 + T017 together (four files); their
  mutate cycles one at a time.
- T015 (binding) alongside T012 (registry).
- T019 while T020 runs.

## Implementation strategy

MVP = Phase 2 + US1 (the instrument exists and the engine is its law).
Then US2 (prove inert), US3 (hazard), US4 (observable + welfare law),
US5 (eligibility + collector), Phase 8. One PR: FR-011 forbids a landed
preset the collector can still record, which is why the collector half
rides along (Experiments' grounds for option (a)).
