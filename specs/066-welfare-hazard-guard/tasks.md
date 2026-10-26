# Tasks: Welfare-Hazard Acknowledgement Guard

**Input**: specs/066-welfare-hazard-guard/ (plan.md, spec.md,
contracts/guard-law.md, data-model.md, research.md, quickstart.md)

**Tests**: included — rule 5 red-first via `scripts/mutate.sh --expect
<regex> <file> <mutation-cmd> <test-cmd>` (file clean against HEAD;
prediction declared BEFORE each run; exit 0 red, 5 no-op, 6 VACUOUS,
7 wrong reason). Rule 6: sort each phase's checks; kept behaviour
green, guards of the change red. One hand-rolled cycle is planned (the
migration's red is a tree state, T021) and states its reason in the PR
body. Scratch configs live in the scratchpad, never under the tree.

**Lane**: Product owns every path below except the seven
`experiments/` tomls (T017), which cross under `cross-lane:` with
Experiments' consent and main 304221b1 cited.

**Branch base**: ad16a681, which predates 304221b1 and ce379470. Anything
those two commits added (`gen2-deviations.md` entry 14, the tolerant
`check_set`) is read with `git show origin/main:<path>` after a
`git fetch`; the branch is never reset onto moved main.

## Phase 1: Setup

- [ ] T001 Record the pre-change pins in `<scratchpad>/066/baseline.txt`:
      `engine_defaults_sha256()` (no shipped test prints it —
      `the_engine_defaults_stamp_is_stable_and_well_formed` checks
      length, hex and self-equality only — so run a throwaway
      `#[test] fn print_stamp() { eprintln!(...) }` with `--nocapture`
      and delete it before committing), the serialized JSON of
      `Config::default()` (no `welfare_hazard` key — grep it), the
      `Config::fingerprint()` of each of the seven migration files, the
      seven paths from `git grep -l initial_needs -- '*.toml'`, and
      HEAD SHA. These are the before-values T010 and T019 compare
      against.

## Phase 2: Foundational

- [ ] T002 Config type in `crates/cloudkitty-core/src/config/mod.rs`:
      `pub struct WelfareHazardConfig { pub acknowledged: Vec<String> }`
      (`deny_unknown_fields`, Serialize + Deserialize, `acknowledged`
      required — no `#[serde(default)]` on it; doc comment citing spec
      066 + guard-law §1) and
      `pub welfare_hazard: Option<WelfareHazardConfig>` on `Config` with
      `#[serde(default, skip_serializing_if = "Option::is_none")]`
      placed directly after `initial_needs` (mod.rs:111). Test beside
      `initial_needs_keys_default_absent_and_leave_the_stamp_unmoved`
      (mod.rs:2534): `welfare_hazard_defaults_absent_and_leaves_the_stamp_unmoved`
      — default is `None`; serialized default JSON and TOML lack the
      key; a parsed `[welfare_hazard] acknowledged = []` serializes WITH
      the key (present-serializes, guard-law §1); an unknown key inside
      the table is rejected; a bare `[welfare_hazard]` table with no
      `acknowledged` is rejected (the field is required).
      Mutate A: drop `skip_serializing_if` → predict the "lacks the key"
      assertion red (`welfare_hazard.*null|"welfare_hazard"`). Mutate B:
      add `#[serde(default)]` to `acknowledged` → predict the bare-table
      assertion red (`should reject.*bare|is_err`).
- [ ] T003 Registry module `crates/cloudkitty-core/src/config/welfare_hazard.rs`
      (declared in mod.rs as `pub mod welfare_hazard`, every item below
      `pub` so the `tests/` sweeps reach them through the crate's public
      API): `pub enum HazardMode { InitialNeeds }`, `pub const ALL:
      &[HazardMode]`, `pub fn name(&self) -> &'static str` →
      `"initial_needs"`, `pub fn activation(&self, &Config) ->
      Option<String>` per guard-law §2 (roster-wide table first, then
      kitties in config order, needs in `NeedKind::ALL` order; active
      iff `Value(v) > 0.0` or `Range(r).max > 0.0`; site text in the
      `validate_initial_needs` home format with the setting rendered as
      that validator renders its error value: `92`, `min = 0, max = 90`),
      and `pub fn active_hazards(&self) -> Vec<(HazardMode, String)>` on
      `Config`.
      Unit tests in the module: pre-feature config → empty; roster-wide
      `cuddle = 92` → one entry with site `[initial_needs].cuddle = 92`;
      per-kitty override only (the P-shape) → site names the kitty;
      everything at zero (`eat = 0`, `drink = { min = 0, max = 0 }`) →
      empty; range `{ min = 0, max = 90 }` → active with site ending
      `= min = 0, max = 90`; ordering (roster table beats a kitty entry
      for the site; eat before cuddle).
      Mutate A: `> 0.0` → `>= 0.0` → predict the all-zero test red
      (`expected.*empty|len.*0`). Mutate B: drop the per-kitty loop →
      predict the P-shape test red.

**Checkpoint**: the type parses and serializes; the registry answers
active/inactive; nothing validates yet.

---

## Phase 3: User Story 1 — a hazardous mode cannot be activated by accident (P1) 🎯 MVP

**Goal**: `Config::validate` enforces exactness with the contract's
error text on every load path.

**Independent Test**: quickstart §2 — the seven scratch variants
through `load_configs_from_str`.

- [ ] T004 [US1] Pure exactness check in
      `crates/cloudkitty-core/src/config/validate.rs`:
      `pub(super) fn check_acknowledgement(acknowledged: Option<&[String]>,
      active: &[(&str, String)], known: &[&str]) -> Result<(), ConfigError>`
      in guard-law §3 order (unknown → duplicate → missing → stale),
      every error `ConfigError::invalid("[welfare_hazard] acknowledged",
      <list as written | "absent">, <§4 expected text>)`; the missing
      text lists EVERY missing mode with its site and ends with the
      exact two-line table naming the FULL active set in `known` order.
      Unit tests go in mod.rs's `mod tests` (mod.rs:1824 — validate.rs
      has no test module; `pub(super)` is visible there as
      `super::validate::check_acknowledgement`), with a synthetic
      two-mode `active`/`known` set (`"initial_needs"`,
      `"needy_preset"`): exact-two → Ok; empty-empty → Ok; absent with
      two active → missing text names both sites and the line
      `acknowledged = ["initial_needs", "needy_preset"]`; partial (one
      of two) → missing names only the absent one but the line names
      both; stale; unknown (and unknown wins over missing when both
      apply); duplicate. Assert on the `Display` string containing the
      site and the line — the wording IS the contract (§4).
      Mutate, one per shape (five cycles): delete the stale branch →
      predict stale test red (`should fail.*stale|Ok`); delete the
      duplicate branch → predict duplicate test red; delete the unknown
      branch → predict unknown test red; make the missing branch list
      only the first missing mode → predict the absent-two-active test
      red (`needy_preset`); drop the line-to-add from the message →
      predict the partial test red (`acknowledged = \[`).
- [ ] T005 [US1] `validate_welfare_hazard()` in validate.rs wiring the
      registry into T004 (acknowledged from `self.welfare_hazard`,
      active from `self.active_hazards()`, known from
      `HazardMode::ALL`), returning Ok immediately when the section is
      absent and nothing is active; called in `Config::validate`
      (mod.rs:1725) directly after `self.validate_initial_needs()?`.
      Integration tests in mod.rs's `mod tests` using
      `test_support::complete_toml`: the seven quickstart §2 variants
      with the real mode (missing/absent, exact, unknown, duplicate,
      stale, all-zero-no-ack Ok, all-zero-with-ack stale), asserting
      the error names `initial_needs` and, for missing, the site
      `[initial_needs].cuddle = 92` and the line. Plus the P-shape (one
      kitty's inline `initial_needs`, no roster table) without an
      acknowledgement → missing, site names the kitty.
      Mutate: remove the `validate_welfare_hazard()?` call from
      `Config::validate` → predict every failing-shape test red
      (`expected Err|is_err`), the two Ok tests green (rule 6 sort:
      those are kept behaviour and must stay green).
- [ ] T006 [US1] Prove the error reaches every load path: a test in
      `crates/cloudkitty-rl/src/config.rs` tests module —
      `load_configs_from_str` on the missing-ack variant errs with a
      message containing `initial_needs` and `[welfare_hazard]`
      (the Python environment, kitty-eval and the census tools all
      call this). Mutate: none of its own — it is a wiring assertion
      covered by T005's mutation (state so in the ledger); run it under
      T005's cycle and record it going red there, or it is vacuous.

**Checkpoint**: US1 complete — every load path refuses an
unacknowledged distressed start with the contract's text.

---

## Phase 4: User Story 2 — absent means inert (P1)

**Goal**: pre-feature configs are byte-identical on every surface; the
fingerprint never reads the section; the generated world never reads
it either.

**Independent Test**: quickstart §1 and §5.

- [ ] T007 [P] [US2] Fingerprint pin in mod.rs tests beside
      `fingerprint_ignores_the_new_behavior_tunables` (mod.rs:3513):
      `fingerprint_ignores_the_welfare_hazard_section` — a config with
      `[initial_needs] cuddle = 92` + acknowledgement and the same
      config with neither fingerprint equal.
      Mutate: append `{:?}` of `self.welfare_hazard` to the format
      string in `fingerprint()` → predict red (`assertion.*left.*right`).
- [ ] T008 [P] [US2] Stamp pin: in `crates/cloudkitty-rl/src/suite.rs`
      tests, sibling of `any_default_moving_moves_the_stamp`:
      `a_written_acknowledgement_moves_the_stamp` — `defaults_stamp` of
      `Config::default()` differs from the stamp of a clone with
      `welfare_hazard = Some(WelfareHazardConfig { acknowledged:
      vec!["initial_needs".into()] })` (present-serializes at the stamp
      layer). The absent half (default stamp unmoved) is NOT asserted
      here against a recomputed baseline — that would compare the
      function with itself and go VACUOUS under any mutation; it is
      T002's "lacks the key" assertion plus T010's recorded-value
      comparison across commits.
      Mutate: add `#[serde(skip)]` to the `welfare_hazard` field →
      predict the differs assertion red (`assertion.*left.*right|equal`).
- [ ] T009 [US2] World-identity pin (US1 scenario 2, US2 scenario 2,
      SC-001) in mod.rs tests: `the_acknowledgement_never_reaches_the_world`
      — the compared pair is a pre-feature config (no section, no
      initial_needs) and the same config plus `[welfare_hazard]
      acknowledged = []` (exact, validates, present-serializes); fixed
      seed; `serde_json::to_string(&World::generate(&a)) ==
      serde_json::to_string(&World::generate(&b))` (`World` is
      `Serialize`; the RNG is inside it, so this compares every draw).
      Mutate: in `World::generate` add `+ config.welfare_hazard.is_some()
      as u64` to the seed → predict red (`assertion.*left.*right`).
- [ ] T010 [US2] Byte-identity run: `cargo test --workspace` green
      with zero golden/pin/fixture diffs (`git status` shows only source
      and spec files changed); compare T001's recorded stamp with the
      post-change stamp (same throwaway print) — equal. Record both in
      the PR body. No code; this is SC-001's evidence.

**Checkpoint**: US2 complete — inert when absent is measured, not
argued.

---

## Phase 5: User Story 3 — the served world and the frozen exams can never be hazardous (P2)

**Goal**: both sweeps fail any tracked config outside `experiments/`
with an active mode; the seven migrated files pass.

**Independent Test**: quickstart §3.

- [ ] T011 [P] [US3] Core sweep rule in
      `crates/cloudkitty-core/tests/shipped_configs.rs`: helper
      `fn hazard_outside_experiments(root: &Path, file: &Path, config:
      &Config) -> Option<String>` (guard-law §5 message), called in
      `every_shipped_toml_loads_through_validation` after `validate()`,
      panicking on `Some`. Self-test `hazardous_configs_are_refused_outside_experiments`
      in the shape of `collect_never_follows_a_symlink` (scratch dir
      `cloudkitty-core-sweep-hazard-selftest-{pid}` with the Drop
      cleanup): writes `complete_toml` + `[initial_needs] cuddle = 92`
      + the acknowledgement under `scratch/specs/x.toml` and
      `scratch/experiments/x.toml`; the helper returns `Some` naming
      the file and `initial_needs` for the first, `None` for the
      second; a third file under `scratch/specs/` with no hazard →
      `None`.
      Mutate: make the helper ignore the path (always check) → predict
      the experiments-side `None` assertion red; make it always `None`
      → predict the specs-side assertion red (two cycles).
- [ ] T012 [P] [US3] RL sweep rule in
      `crates/cloudkitty-rl/tests/shipped_configs_rl.rs`: same helper
      and self-test (scratch dir
      `cloudkitty-rl-sweep-hazard-selftest-{pid}`), the helper taking
      the `Config` half of `load_configs_from_str`'s result, called in
      `every_shipped_toml_loads_through_both_config_surfaces`. Same two
      mutations, same predictions. (Mirror discipline from #468: the
      two files stay logic-parallel — crate names and the loader call
      differ, the rule and the self-test do not.)
- [ ] T013 [US3] Run both sweeps on the branch BEFORE the migration:
      `cargo test -p cloudkitty-core --test shipped_configs` and
      `cargo test -p cloudkitty-rl --test shipped_configs_rl` are RED
      with the missing-acknowledgement error (FR-004 through the load —
      this is FR-009's reason). Each sweep panics on its FIRST failing
      file, so one run shows one path: record that path and the error
      text for both sweeps. "Exactly the seven" is read in T017's
      stepwise appends. No code.

**Checkpoint**: US3 complete except for the migration (Phase 7), which
turns T013's red green.

---

## Phase 6: User Story 4 — a hazardous world is served only on purpose, and is visible (P2)

**Goal**: the bare switch, the gate before any world, the boot line,
`GET /config`, the key-settings row.

**Independent Test**: quickstart §4.

- [ ] T014 [P] [US4] Gate module `crates/cloudkitty-server/src/welfare_hazard.rs`
      (`pub mod welfare_hazard` in lib.rs): `pub const SWITCH: &str =
      "--allow-welfare-hazard"`; `pub fn acknowledged(config: &Config)
      -> &[String]` (empty when absent); `pub fn gate(config: &Config,
      allowed: bool) -> anyhow::Result<()>` erring per guard-law §6
      when non-empty and `!allowed`; `pub fn log_boot(config: &Config)`
      emitting the §7 line only when non-empty. Unit tests: gate on
      acknowledged + false → Err naming `initial_needs` and the switch;
      acknowledged + true → Ok; non-hazardous ± switch → Ok; `log_boot`
      captured with a module-local copy of the `Captured` writer
      pattern (settings.rs:794 — it is private to settings.rs, so copy
      the ~20 lines, do not widen its visibility) — one line containing
      `welfare-hazardous world served on purpose` and `initial_needs`
      when acknowledged; zero lines (empty capture) on
      `Config::default()`.
      Mutate: gate ignores `allowed` → predict the acknowledged+true
      test red; gate always Ok → predict the acknowledged+false test
      red; `log_boot` unconditional → predict the empty-capture test
      red (three cycles).
- [ ] T015 [US4] Key-settings row in
      `crates/cloudkitty-server/src/settings.rs` `build` (after T014 —
      it calls `welfare_hazard::acknowledged`): after the last stuck
      row, `if !acknowledged.is_empty()` push
      `Entry { group: "welfare_hazard", key: "acknowledged", value:
      json!(list), default: None, source: Source::Toml }` (source is
      presence by construction — the list is only non-empty when
      written). Tests: `the_key_names_are_pinned` untouched and green
      (kept behaviour, rule 6); new `the_welfare_hazard_row_appears_last_only_when_acknowledged`
      — minimal config → no `welfare_hazard.*` name; acknowledged
      config → `names().last() == "welfare_hazard.acknowledged"` and
      `render_text()` ends with
      `welfare_hazard.acknowledged = ["initial_needs"] [toml]\n`; a
      present-but-empty list → no row.
      Mutate: push unconditionally → predict the minimal-config
      assertion red; push before the stuck rows → predict the `last()`
      assertion red (two cycles).
- [ ] T016 [US4] Wire the server in `crates/cloudkitty-server/src/main.rs`:
      `Args.allow_welfare_hazard: bool` (default false), the match arm
      `"--allow-welfare-hazard" => args.allow_welfare_hazard = true`,
      and a HELP entry under `--no-backup` in the const's own layout
      (eight-space indent, description column 29; the flag is 22
      characters and overruns the column, so the description wraps to
      its own line like `--fresh`'s continuation):
      ```
              --allow-welfare-hazard
                                   Serve a config that acknowledges a
                                   welfare-hazardous mode (spec 066);
                                   refused without it
      ```
      In `run()`: `cloudkitty_server::welfare_hazard::gate(&config,
      args.allow_welfare_hazard)?;` on the line after
      `config.validate()?;` (main.rs:236; before the registry, before
      `load_or_generate_world`); `cloudkitty_server::welfare_hazard::log_boot(&config);`
      after `stuck::log_boot` and before `settings.announce()`.
      Verify by hand per quickstart §4 against a scratch config with a
      scratch `snapshot_path`: refusal exits non-zero and leaves no
      snapshot or `.bak`; with the switch it boots, `GET /config` shows
      the section, `GET /settings` text ends with the row; the served
      `cloudkitty.toml` with the switch boots byte-identically (diff
      the boot logs minus timestamps). Record the three outputs in the
      PR body. (The gate's rule-5 red is T014's; main.rs is wiring. The
      "before any world" ordering is proven by the no-snapshot check:
      state, not wording.)

**Checkpoint**: US4 complete.

---

## Phase 7: The migration (FR-009, cross-lane)

- [ ] T017 Append the acknowledgement table to the seven files ONE AT A
      TIME, re-running `cargo test -p cloudkitty-core --test
      shipped_configs` after each append and recording the next failing
      path, in the order the sweep names them: exactly
      `printf '\n[welfare_hazard]\nacknowledged = ["initial_needs"]\n' >> "$f"`
      (quickstart §6) for `experiments/minifriend-phase1-2026-10-22/g2leg-20-W.toml`,
      `g2leg-20-G.toml`, `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P1.toml`
      … `P5.toml`. Seven runs name seven distinct paths, matching T001's
      grep set; the eighth run is green. `git diff --stat` = seven
      files, +3 each, nothing else.
- [ ] T018 Read-only shape check (Experiments' contract, main
      304221b1): for each file, `python3` — bytes before the trailing
      `b"\n[welfare_hazard]\n"` sha256 == the pre-retrofit hash in
      `experiments/gen2-deviations.md` entry 14. Entry 14 is not on
      the branch (base ad16a681): read the seven hashes with
      `git show origin/main:experiments/gen2-deviations.md` after a
      `git fetch`; do not retype them. All seven equal. Record in the
      PR body.
- [ ] T019 Fingerprint check for SC-005: `Config::fingerprint()` of
      each migrated file equals T001's recorded value (a one-line test
      print or the T007 helper on the real files). Record.
- [ ] T020 Re-run both sweeps: GREEN. This is the migration's red→green
      (T013 red before any append, T017's seven intermediate reds, T020
      green with all seven).
- [ ] T021 Hand-rolled red record for the migration, stated reason:
      the red is a TREE STATE (files without the table), not a code
      mutation `mutate.sh` can apply and revert — T013's and T017's
      outputs ARE the red, T020 the green; the PR ledger says so with
      both commands and the seven file names in failure order.

---

## Phase 8: Polish & cross-cutting

- [ ] T022 `CHANGELOG.md` `## Unreleased`: one public-voice entry
      above the spec-065 entry — a welfare-hazardous mode now has to be
      acknowledged by name in the config to load, both config sweeps
      keep every such mode out of the served world and the exams, and
      the server serves one only with `--allow-welfare-hazard`, saying
      so at boot and on its config surfaces; absent, nothing changes;
      no compatibility marker (stamp, obs-schema, fingerprint, draw
      order unmoved). `specs/INDEX.md` is script-generated and the 066
      row exists; the spec's `Status: Draft` stays (house practice,
      064 and 065) — neither is touched.
- [ ] T023 Full `cargo test --workspace` + `cargo clippy --workspace
      --all-targets -- -D warnings` + `cargo fmt --check`; jscpd ratchet
      if the sweep self-tests push `tests/` duplication (the two sweep
      files are deliberate mirrors — if the ratchet trips, say so in
      the PR rather than de-duplicating across crates).
- [ ] T024 PR: push, open `product/066-welfare-hazard` → main with
      `gh pr view --json files` read first against `scripts/lanes.txt`;
      body: summary, the rule-5 ledger (every cycle: test, mutation,
      prediction, observed; T021's stated reason; T006's wiring note;
      T008's absent-half note), the quickstart §4 outputs, T018/T019
      results, and the `cross-lane:` line quoting Experiments' consent
      ("loud load failure, not a one-release warning", 2026-10-26;
      owner's "Option 1 for the retrofit") and citing 304221b1 as the
      commit that makes `check_set` / `check_P` / `test_phase1b`
      tolerant of the trailing table. Self-review comment;
      medium-effort subagent review on her word; merge only on her word
      (`gh pr merge N --merge`, never `--delete-branch`).
- [ ] T025 After merge: message Experiments (section name unchanged,
      PR number, landed sha — their post-retrofit hash record and
      three-check run are theirs); delete the remote branch; `git
      status --ignored` then `git worktree remove` from outside; anchor
      + MEMORY.md line.

---

## Dependencies

- Phase 2 (T002, T003) blocks everything; T002 ∥ T003 after the enum
  is declared (T003 needs no T002 type, T002's test needs no registry).
- US1 (T004 → T005 → T006) needs Phase 2. T004 is pure and can start
  with T002/T003 in flight.
- US2 (T007 ∥ T008, then T009, then T010) needs T002; T009 needs T005
  (the acknowledged config must validate); T010 needs US1 landed (the
  whole workspace green).
- US3 (T011 ∥ T012, then T013) needs T005 (the sweeps red through the
  load) and T003 (the helper's `active_hazards`).
- US4 (T014 → T015, then T016) needs T002 (the type) and T005 (a
  served hazardous config must validate first); T015 calls T014's
  `acknowledged`, so it is not parallel with it.
- Phase 7 needs T013 (the red exists before the fix) and T005.
- Phase 8 needs everything.

## Parallel execution examples

- After Phase 2: T004 + T007 + T008 + T011 + T012 + T014 all touch
  different files and can be written together; their mutate cycles
  run one at a time (no tree edits while a cycle runs).
- T022 can be written while T023 runs.

## Implementation strategy

MVP = Phase 2 + US1 (the guard exists and refuses). Then US2 (prove
inert), US3 (sweeps, which go red on the seven files), US4 (server),
Phase 7 (migration turns the sweeps green), Phase 8. The PR is one unit
— FR-009 forbids landing the validator without the migration — so the
increments are commits on the branch, not merges.
