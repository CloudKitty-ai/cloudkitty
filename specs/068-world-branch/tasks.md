# Tasks: World Branch API (spec 068)

**Input**: Design documents from `specs/068-world-branch/` (spec.md,
plan.md, research.md R1–R12, data-model.md, contracts/python-api.md,
quickstart.md).

**Tests**: REQUIRED. Every guard below is written first, seen RED through
`scripts/mutate.sh --expect <regex> <file> <mutation-cmd> <test-cmd>`
against the predicted FIRST assertion the mutant reaches, then kept
green (CLAUDE.md rule 5; a mutation that stays green is vacuous — fix or
report, never cite). The file under mutation must be clean against HEAD:
commit before every cycle; no tree edits while it runs. Rule 6: before
running anything, sort the existing suites into must-pass (every suite
in the workspace — FR-015) and must-fail (none: no behaviour changes
without the API); read the must-pass pile, do not only run it.

**Organization**: by user story, so each is independently testable. All
commands run from the worktree root `/Users/elizabethkelly/ai/cloudkitty-world-branch`
(cwd resets to the native checkout after every Bash call).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Record the baseline: run `cargo test --workspace` and
  `pytest crates/cloudkitty-py/tests -v` (after `VIRTUAL_ENV=$PWD/.venv
  maturin develop --release` in a worktree-local venv, never the native
  checkout's) and note the pass counts and the three Python schema
  constants (`OBSERVATION_SCHEMA_VERSION`, `MASK_SCHEMA_VERSION`,
  `ACTION_SCHEMA_VERSION`) in a scratchpad file — SC-007's comparison
  values. No repo file changes.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: the core seam additions and the error/identity scaffolding
every story needs.

- [ ] T002 `crates/cloudkitty-core/src/seam.rs`: derive `Serialize,
  Deserialize` on `DealtSeeds` (R2) with a doc comment: restoring a
  serialized deal is a deliberate second consumption on a second timeline
  (spec 068), the `#[must_use]` contract unchanged.
- [ ] T003 `crates/cloudkitty-core/src/seam.rs`: add `Provenance::
  OverriddenAct`, `OverriddenMessage`, `OverriddenBoth` (unit variants,
  `snake_case` serde) with doc comments per data-model.md; confirm
  `cargo build --workspace` names every exhaustive match that must grow
  (expected: only `provenance_str` in the py crate).
- [ ] T004 `crates/cloudkitty-py/src/lib.rs`: extend `provenance_str` with
  `"overridden_act"`, `"overridden_message"`, `"overridden_both"`.
- [ ] T005 `crates/cloudkitty-rl/src/episode.rs`: add `EpisodeError::
  SnapshotIdentity { component: &'static str, found: String, expected:
  String }`, `SnapshotMalformed(String)`, `SnapshotUnavailable { reason:
  &'static str }`, `OverrideRefused { kitty: KittyId, reason: String }`
  (R10) with `#[error]` texts matching contracts/python-api.md; add
  `pub fn control(&self) -> &BTreeMap<KittyId, Control>`; add the
  `Identity` struct and `fn identity(&self, engine_commit: &str) ->
  Identity` computing the seed-excluded sha256 digest of
  `(core, rl)` (R3) and the control-map rendering (`"external"` / name).
- [ ] T006 `crates/cloudkitty-py/src/lib.rs`: map the four new variants in
  `episode_err` — `SnapshotIdentity`, `SnapshotMalformed`,
  `SnapshotUnavailable`, `OverrideRefused` → `ValueError` (R10;
  out-of-range stays `IndexError`, poisoned stays `RuntimeError`).
- [ ] T007 Commit Phase 2 (`cargo build --workspace` green; existing
  suites unchanged).

**Checkpoint**: compiles; no behaviour changed; the must-pass pile is
still green.

---

## Phase 3: User Story 1 — Hold a tick, branch it, continue byte-identically (P1) 🎯 MVP

**Goal**: `Episode::snapshot`/`restore` and `ParallelEnv.snapshot/
restore/fork`, byte-identical continuation with the dealt seeds carried.

**Independent Test**: run 300 ticks, snapshot, run original and twin 200
ticks under the same actions, compare every surface tick by tick.

### Guards for US1 (write first; each red via mutate.sh before green)

Test fixture shared by the Rust guards (new file
`crates/cloudkitty-rl/tests/branch.rs`): `Config::default()` with
`kitties[0].behavior = "needy"` and `welfare_hazard = Some(
WelfareHazardConfig { acknowledged: vec!["needy".into()] })` (the pattern
at episode.rs:887-891), `kitties[1]` left external, the rest
`Control::Builtin(k.behavior.clone())`; a fixed external action script
over the menu as in `mixed_control.rs:76`.

- [ ] T008 [P] [US1] G1 `a_restored_episode_continues_byte_identically`
  in `crates/cloudkitty-rl/tests/branch.rs`: 10 seeds × (300 steps,
  snapshot, 200 more steps on original and on a restored never-reset
  twin); assertion order: (1) the twin's restore `EpisodeStep` infos
  `decision_seed` equal the original's last-step infos per agent;
  (2) per tick: `serde_json(world)` equal, observations equal, rewards
  equal, infos (`applied_action`, `applied_message`, `proposed_message`,
  `survived`, `mask`, `decision_seed`, `provenance`) equal. **Red**:
  mutate `restore` to re-deal (`pending_seeds = Some(world.
  deal_decision_seeds())` after assignment) → predicted first failure:
  assertion (1), `--expect "decision_seed"`.
- [ ] T009 [P] [US1] G2 `restore_carries_the_reward_baselines` in
  `branch.rs`: reward mode Delta with shaping on; snapshot after 50
  steps; restored twin's first-step reward equals the original's. **Red**:
  mutate `restore` to set `prev_level = 0.0` → red at the reward
  equality, `--expect "reward"`.
- [ ] T010 [P] [US1] G3 `restore_heals_a_poisoned_episode` as a unit test
  in `crates/cloudkitty-rl/src/episode.rs` `mod tests` (where
  `poison` is reachable): poison, assert `step` is `Err(Panicked)`,
  `restore(snapshot taken earlier)` is `Ok`, `step` is `Ok`. **Red**:
  mutate `restore` to skip clearing `poisoned` → red at the post-restore
  `step().is_ok()`, `--expect "poisoned"`.
- [ ] T011 [P] [US1] G4 `a_truncated_snapshot_restores_truncated` in
  `branch.rs`: `RlConfig` horizon 5; step to truncation; snapshot;
  restore into a fresh twin; `step` is `Err(SteppedAfterTruncation)`;
  `reset` then steps. **Red**: mutate `restore` to set `truncated =
  false` → red at the `SteppedAfterTruncation` assert,
  `--expect "truncat"`.
- [ ] T012 [P] [US1] G5 `restore_replaces_state_wholesale` in
  `branch.rs`: snapshot at tick t, step once, restore into the same
  episode, `serde_json(world)` equals the snapshot-time world and the
  restore `EpisodeStep`'s decision seeds equal the snapshot-time ones.
  **Red**: mutate `restore` to skip assigning `world` → red at the world
  equality, `--expect "world"`.
- [ ] T013 [P] [US1] Python guards in new
  `crates/cloudkitty-py/tests/test_branch.py` (US1 part):
  `test_restore_into_a_never_reset_twin_is_byte_identical` (ParallelEnv,
  200 ticks, obs/rewards/infos equal; the twin never called `reset`);
  `test_snapshot_before_reset_is_refused` (`ValueError`, "reset first");
  `test_fork_continues_identically`. **Red** (after T016): mutate
  `ParallelEnv.restore` to skip setting `live = true` → the twin's `step`
  raises → red at the first twin step, `--expect "reset"`.

### Implementation for US1

- [ ] T014 [US1] `crates/cloudkitty-rl/src/episode.rs`: `EpisodeSnapshot`
  struct (data-model.md) and `pub fn snapshot(&self, engine_commit: &str)
  -> Result<Vec<u8>, EpisodeError>` — refuse while poisoned
  (`SnapshotUnavailable { reason: "episode poisoned ..." }`), serialize
  with `serde_json::to_vec`.
- [ ] T015 [US1] `crates/cloudkitty-rl/src/episode.rs`: `pub fn restore(
  &mut self, engine_commit: &str, bytes: &[u8]) -> Result<EpisodeStep,
  EpisodeError>` — parse (→ `SnapshotMalformed`), compare identity
  component by component (→ `SnapshotIdentity`, environment untouched),
  assign `world`, `tick_in_episode`, `truncated`, `prev_level`,
  `prev_potential`, `pending_seeds`, write `seed` into the config
  (`Arc::new(config)` as `reset` does), clear `poisoned` and
  `pending_overrides` (field lands in T024; add it here as an empty map
  if implementing US1 first), then `collect_step(0.0,
  TickReport::default(), self.world.snapshot())` under the
  `catch_unwind` + poison pattern of `reset_caught` (R4).
- [ ] T016 [US1] `crates/cloudkitty-py/src/lib.rs` `ParallelEnv`: field
  `last_report: TickReport` refreshed by reset/step/restore; methods
  `snapshot()` (pre-reset → `ValueError` "reset first"), `restore(data:
  &[u8])` (sets `live = true`, returns `(obs, infos)` like `reset`),
  `fork()` (new env from `episode.core_config()`, `rl_config()`,
  `control()`; restore). Pass `env!("CLOUDKITTY_ENGINE_COMMIT")` as the
  engine commit. Docstrings per contracts/python-api.md including the
  welfare line and the transient-token line (FR-016/FR-017).
- [ ] T017 [US1] Run the US1 mutate cycles (T008–T013) and record each
  red's exit 0 line in the PR notes; then commit.

**Checkpoint**: US1 deliverable on its own — a branch primitive for
policy-only and mixed worlds.

---

## Phase 4: User Story 2 — One-tick proposal override under the law, honestly marked (P1)

**Goal**: `Episode::override_next` and `ParallelEnv.override` /
`tick_records`, each half independent, three provenance marks, law
untouched.

**Independent Test**: seat a builtin kitty, override its next act, step,
read the record: applied act is the override's, provenance
`overridden_act`; step again: the seat's own decision and `policy`.

### Guards for US2

- [ ] T018 [P] [US2] G7 `an_act_override_applies_for_exactly_one_tick` in
  `branch.rs`: builtin seat (`needs_driven`), decode-able legal act (the
  Idle menu index is always legal), `override_next(id, Some(idx), None)`,
  step; assertion order: (1) record provenance `OverriddenAct`; (2)
  applied == decoded act; (3) next step's provenance `PolicyMade`.
  **Red**: mutate `step_inner` to not clear `pending_overrides` after
  the tick → red at (3), `--expect "PolicyMade|one tick"`.
- [ ] T019 [P] [US2] G8 `a_message_override_leaves_the_act_the_seats_own`
  in `branch.rs`: fork via snapshot/restore; on the branch
  `override_next(id, None, Some(msg_idx))`, step both; assertion order:
  (1) branch provenance `OverriddenMessage`; (2) branch applied act ==
  original applied act; (3) branch `proposed_message` == the named
  message. **Red**: mutate the mark derivation so message-only yields
  `OverriddenAct` → red at (1), `--expect "OverriddenMessage"`.
- [ ] T020 [P] [US2] G9 `both_halves_override_marks_overridden_both` in
  `branch.rs`. **Red**: mutate derivation to `OverriddenAct` when both
  → red at the provenance assert, `--expect "OverriddenBoth"`.
- [ ] T021 [P] [US2] G10 `an_override_cannot_relieve_a_masked_need` in
  `branch.rs`: needy seat masked on a need (read `world.kitty(id).needy`
  mask and phase through the engine; wait until `held`), override with
  the menu index of an act that would relieve it; step; assertion order:
  (1) applied is Idle; (2) `refusal_log` gained an entry for the seat;
  (3) provenance is `OverriddenAct`. **Red**: mutate the needy verdict
  at the apply slot in `crates/cloudkitty-core/src/world.rs` to allow
  the act → red at (1), `--expect "Idle"`. (The law lives in core; this
  is the layer where the bug would occur.)
- [ ] T022 [P] [US2] G11 `an_override_inside_a_scene_minimum_continues_the_scene`
  in `branch.rs`: drive a seat into a multi-tick activity, override with
  a different act on its second tick, step; applied continues the scene.
  **Red**: mutate duration enforcement in `world.rs` to accept the new
  act → red at the applied-continues assert, `--expect "scene|continue"`.
- [ ] T023 [P] [US2] G12 `override_refusals_name_their_cause_and_leave_the_episode_untouched`
  in `branch.rs`: external seat, unknown kitty, empty halves, second
  override, out-of-range act, out-of-range message → each `Err` of the
  documented variant; `serde_json(world)` and `pending_seeds` unchanged
  after every refusal. **Red**: mutate `override_next` to drop the
  double-override check → red at the second-override `is_err`,
  `--expect "already"`.
- [ ] T024a [P] [US2] G13 `reset_and_restore_drop_a_pending_override` in
  `branch.rs`: override, restore an earlier snapshot, step → `PolicyMade`;
  override, reset, step → `PolicyMade`. **Red**: mutate `restore` to not
  clear `pending_overrides` → red at the first `PolicyMade` assert,
  `--expect "PolicyMade"`.
- [ ] T024b [P] [US2] G14 `a_refused_step_leaves_the_override_standing` in
  `branch.rs`: override, step with an out-of-range external index →
  `Err(ActionOutOfRange)`; step legally → `OverriddenAct`. **Red**:
  mutate `step_inner` to take the pending map before decoding externals
  → red at the `OverriddenAct` assert, `--expect "OverriddenAct"`.
- [ ] T025 [P] [US2] Python guards in `test_branch.py` (US2 part):
  `test_override_on_a_builtin_seat_marks_the_record`
  (`control={"kitty_2": "needs_driven"}`, `tick_records()["kitty_2"]
  ["provenance"] == "overridden_act"`, then `"policy"`);
  `test_tick_records_keys_are_the_documented_contract` (exact key set
  from data-model.md for every roster kitty, scripted seats included);
  `test_override_refusals_raise_the_documented_classes` (`ValueError`
  for external/unknown/empty/double, `IndexError` for out-of-range).
  **Red** (after T027): mutate `tick_records` to skip scripted seats →
  red at the roster-coverage assert, `--expect "kitty_2"`.

### Implementation for US2

- [ ] T026 [US2] `crates/cloudkitty-rl/src/episode.rs`: `PendingOverride`
  and `pending_overrides: BTreeMap<KittyId, PendingOverride>`;
  `pub fn override_next(&mut self, kitty: KittyId, action: Option<usize>,
  message: Option<usize>) -> Result<(), EpisodeError>` — refusals in the
  order of data-model.md, decode against the seat's start-of-tick table
  built as `collect_step` builds an external seat's (R5); in `step_inner`
  take the map after the external-decoding loop, and for a `Builtin` seat
  with an entry replace the named halves of the resolver's `Decision`
  and insert the derived mark into `scripted_marks`; clear the map in
  `reset`/`arm` and `restore`.
- [ ] T027 [US2] `crates/cloudkitty-py/src/lib.rs` `ParallelEnv`:
  `override(kitty, action=None, message=None)` (kitty as id or name, the
  `decision_request` parser) and `tick_records()` from `last_report`
  over `episode.roster()` with the data-model.md keys (reuse
  `action_wire_name`, `MessageKind::wire_name`, `provenance_str`);
  docstrings per the contract.
- [ ] T028 [US2] Run the US2 mutate cycles (T018–T025); commit.

**Checkpoint**: US1 + US2 — the gate's full mechanism on the
single-world surface.

---

## Phase 5: User Story 3 — A world that never branches is byte-identical (P1)

**Goal**: prove FR-015 / SC-007 on the feature branch.

- [ ] T029 [US3] Run the must-pass pile: `cargo test --workspace`,
  `pytest crates/cloudkitty-py/tests -v`; compare pass counts and the
  three schema constants with T001's baseline; `git status` shows no
  golden, pin, fixture or `.ckpolicy` change; `git diff --stat
  origin/main -- crates/cloudkitty-server` is empty. Record the counts
  in the PR body. No code task — if anything moved, that is a defect in
  Phases 2–4, fix there.

---

## Phase 6: User Story 4 — Branch one world of a batch (P2)

**Goal**: `VectorEnv.snapshot(i)/restore(i, bytes)/override(i, …)/
tick_records(i)`.

**Independent Test**: two-world batch; snapshot world 0, step both,
restore world 0, step both; world 0 matches the single-world case,
world 1 matches an un-branched run.

### Guards for US4

- [ ] T030 [P] [US4] G15 `a_batched_world_branches_alone` in `branch.rs`
  against `VectorizedEnvironment` directly: assertion order: (1) world 0
  after restore+steps equals a `ParallelEnv`-equivalent single `Episode`
  restored from the same bytes; (2) world 1's `serde_json(world)` equals
  an un-branched twin batch's world 1. **Red**: mutate the per-index
  dispatch to address local index `(i + 1) % len` → red at (1),
  `--expect "world 0"`.
- [ ] T031 [P] [US4] Python guards in `test_branch.py` (US4 part):
  `test_vector_env_restores_one_world_by_index` and
  `test_a_snapshot_is_portable_between_env_objects` (ParallelEnv snapshot
  → `VectorEnv.restore(0, …)` of identical config/control and back).
  **Red**: covered by T030's mutant through the wrapper
  (`--expect "world"`), run once after T033.

### Implementation for US4

- [ ] T032 [US4] `crates/cloudkitty-rl/src/vector.rs`: `Command::
  Snapshot(usize)`, `Restore(usize, String /*engine commit*/, Vec<u8>)`,
  `Override(usize, KittyId, Option<usize>, Option<usize>)`; reply enum
  `Reply { Steps(..), Snapshot(..), Restore(..), Unit(..) }`; worker loop
  arms; `pub fn snapshot(&mut self, i, engine_commit) -> Result<Vec<u8>,
  EpisodeError>`, `restore(&mut self, i, engine_commit, bytes) ->
  Result<EpisodeStep, EpisodeError>`, `override_next(&mut self, i, kitty,
  action, message) -> Result<(), EpisodeError>` sending to the owning
  worker only (R8); `needs_reset` untouched; `Snapshot(..)` also pass
  the engine commit (string) so the worker needs no env!.
- [ ] T033 [US4] `crates/cloudkitty-py/src/lib.rs` `VectorEnv`: field
  `last_reports: Vec<TickReport>` refreshed by reset/step (per world) and
  by restore (that world); `snapshot(i)`, `restore(i, data)` returning
  that world's `(obs, infos)` dicts, `override(i, kitty, action=None,
  message=None)`, `tick_records(i)`; `IndexError` for `i >= num_worlds`;
  docstrings (welfare line; the batch's reset requirement is unaffected).
- [ ] T034 [US4] Run T030/T031 cycles; commit.

---

## Phase 7: User Story 5 — A snapshot is refused where it cannot be honoured (P2)

**Goal**: identity refusals and malformed-bytes refusal, environment
untouched.

### Guards for US5

- [ ] T035 [P] [US5] G16 `restore_refuses_every_identity_mismatch` in
  `branch.rs`: assertion order: (1) different engine-commit literal →
  `SnapshotIdentity { component: "engine_commit", .. }`; (2) an rl
  config differing only in horizon → `component: "config_fingerprint"`;
  (3) a core config differing only in one need rate → the same
  component; (4) a control map with the external seat scripted →
  `component: "control"`; after each, `serde_json(world)` and the
  pending seeds are unchanged. **Red**: mutate the digest to hash the
  core config only → red at (2), `--expect "config_fingerprint"`.
- [ ] T036 [P] [US5] G17 `restore_refuses_bytes_that_are_not_a_snapshot`
  in `branch.rs`: `b"not a snapshot"` → `SnapshotMalformed`; world
  unchanged. **Red**: mutate `restore` to assign `world` before the
  identity check and then fail → the world-unchanged assert goes red
  only if parse succeeded; so instead mutate the error mapping to return
  `SnapshotUnavailable` for a parse failure → red at the variant match,
  `--expect "Malformed"`.
- [ ] T037 [P] [US5] Python guard in `test_branch.py` (US5 part):
  `test_restore_mismatch_errors_name_the_component` (control differs →
  `ValueError` containing "control"; malformed → "not a snapshot").
  **Red**: covered by T035's mutant through the wrapper after T015/T016
  (`--expect "control"`).

### Implementation for US5

- [ ] T038 [US5] Already carried by T005/T015 (identity + refusal order).
  Verify the error texts match contracts/python-api.md; adjust texts
  only. Run T035–T037 cycles; commit.

---

## Phase 8: Polish & cross-cutting

- [ ] T039 [P] G18 `test_branch_docstrings_carry_the_welfare_line` in
  `test_branch.py`: the four docstrings (`snapshot`, `restore`, `fork`,
  `override` on ParallelEnv; the three on VectorEnv) contain "k > 1" and
  "WELFARE-STANDING"; `snapshot`'s contains "transient". Wording IS the
  contract (FR-017, rule 5's exception). **Red**: mutate one docstring
  to drop the line → red at that method's assert, `--expect "snapshot|
  k > 1"`.
- [ ] T040 [P] SC-006 in `test_branch.py`: `test_restore_plus_one_step_is_far_cheaper_than_replay`
  (loose 0.1 ratio); run the quickstart §6 script on the reference
  machine and fill its table (bar 0.01). **Red**: mutate `restore` to
  replay from the seed instead of parsing (or simply assert the ratio
  with a `> 1.0` bound in the mutant) → red at the ratio assert,
  `--expect "ratio"`.
- [ ] T041 [P] `docs/howto-rl.md`: add a short "Branching a world"
  section after §2 (snapshot/restore/fork/override/tick_records, the
  transient-token note, the k > 1 line, the needy seat cannot be taken
  external — override instead). Shared doc; Product may edit.
- [ ] T042 [P] `CHANGELOG.md` Unreleased: one entry in public voice (what
  it means: a running world can be held, branched once and the branch
  read; the one-tick override is a proposal the engine still judges and
  the record says who proposed it), PR cited, NO compatibility marker —
  and say so: byte-identical without the API.
- [ ] T043 `cargo fmt --all`, `cargo clippy --workspace --all-targets`
  clean (the CI warnings gate), `pytest` green; run quickstart.md §1–§6.
- [ ] T044 PR: push `product/068-world-branch`; `gh pr view --json files`
  against `scripts/lanes.txt` (expected lane: crates/, specs/, docs/
  howto-rl.md + CHANGELOG.md shared; no cross-lane); body with the SC
  table, the mutate red lines (exit 0 per guard), and the T029 counts;
  self-review comment; CI green via `gh pr checks` + job logs; subagent
  review on her word; merge on her word with `gh pr merge N --merge`.

---

## Dependencies & Execution Order

- Phase 2 blocks everything (T002–T006 are small; T003→T004 and
  T005→T006 are ordered; T002 ∥ T003 ∥ T005).
- US1 (Phase 3) is the MVP; US2 (Phase 4) depends on T015's
  `pending_overrides` hook only; US4 (Phase 6) depends on US1 (restore)
  and US2 (override) Rust methods; US5 (Phase 7) depends on T005/T015.
  US3 (Phase 5) runs after every code phase and again before the PR.
- Within each story: guards first (RED via mutate.sh after the
  implementation exists — write the test, implement, then run the
  mutant cycle; a guard that cannot compile before its subject exists is
  written first and cycled right after), then commit.

## Parallel opportunities

- T008–T012 (five Rust guards, one file — write in one pass, cycle
  sequentially; mutate.sh refuses a dirty file, so commit between
  cycles).
- T018–T024b likewise; T030 ∥ T035 ∥ T036 after their implementations.
- T039 ∥ T040 ∥ T041 ∥ T042.

## Implementation strategy

MVP = Phase 2 + Phase 3 (US1): a branch primitive. Then US2 (the gate's
scripted-seat half), US3 proof, US4 batched, US5 refusals, polish, PR.
Stop at each checkpoint; commit after every task group; never cite a
guard green that has not been seen red.

## Rule-5 red predictions (summary)

| Guard | Mutant (file) | Predicted first failing assertion |
|-------|---------------|-----------------------------------|
| G1 | re-deal on restore (episode.rs) | restore infos `decision_seed` ≠ original |
| G2 | `prev_level = 0.0` on restore (episode.rs) | first-step reward ≠ |
| G3 | poison not cleared (episode.rs) | post-restore `step().is_ok()` |
| G4 | `truncated = false` on restore (episode.rs) | `SteppedAfterTruncation` expected |
| G5 | world not assigned (episode.rs) | world JSON ≠ snapshot-time |
| G7 | pending map not cleared (episode.rs) | next tick provenance ≠ `PolicyMade` |
| G8 | message-only → `OverriddenAct` (episode.rs) | provenance ≠ `OverriddenMessage` |
| G9 | both → `OverriddenAct` (episode.rs) | provenance ≠ `OverriddenBoth` |
| G10 | needy verdict allows relief (world.rs) | applied ≠ Idle |
| G11 | duration enforcement accepts the new act (world.rs) | scene not continued |
| G12 | double-override check removed (episode.rs) | second override not `Err` |
| G13 | restore keeps pending map (episode.rs) | provenance ≠ `PolicyMade` after restore |
| G14 | pending map taken before external decode (episode.rs) | provenance ≠ `OverriddenAct` |
| G15 | per-index dispatch off by one (vector.rs) | world 0 ≠ single-episode restore |
| G16 | digest hashes core only (episode.rs) | rl-horizon mismatch not refused |
| G17 | parse failure mapped to another variant (episode.rs) | variant ≠ `SnapshotMalformed` |
| G18 | docstring line removed (lib.rs) | that method's docstring assert |
| py-US1 | `live` not set on restore (lib.rs) | twin's first `step` raises |
| py-US2 | scripted seats skipped in `tick_records` (lib.rs) | `kitty_2` missing |
| SC-006 | ratio bound loosened in the mutant (test_branch.py) | ratio assert |
