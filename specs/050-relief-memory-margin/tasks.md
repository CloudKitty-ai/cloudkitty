# Tasks: Relief Memory Margin (spec 050)

**Input**: Design documents from `/specs/050-relief-memory-margin/` — plan.md, spec.md (§Clarifications 2026-09-05), research.md (R1–R8), data-model.md, contracts/relief-memory-margin.md, quickstart.md.

**Tests**: REQUIRED — the spec's success criteria are guards seen red first (CLAUDE.md rules 5/6; SC-001 names "a guard seen red on the unchanged engine"). Every mutate/revert cycle is recorded in `redden-list.md` with the prediction written BEFORE the run and the count re-read after. Commit before every destructive check.

**Organization**: by user story. US1 (P1) is the MVP: the key, the predicate, the drink fixture, the served-roster count. US2 (P2) proves nothing else moved and re-pins the one stream the served key moves. US3 (P3) extends the fixture to eat/play and pins the social words' indifference.

**House rules in force**: worktree `~/ai/cloudkitty-relief`, branch `050-relief-memory-margin`; never touch `evals/v2`; never edit `experiments/FINDINGS.md`, `experiments/fog-gen1-shakeout/*` (Experiments' files); nothing deploys, no tag; long jobs foreground via `scratchpad/cycle.sh LABEL`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3

---

## Phase 1: Setup

- [X] T001 Create `specs/050-relief-memory-margin/redden-list.md` in the 049 format (standard paragraph; baseline count from a fresh `scratchpad/cycle.sh c0` on the untouched branch — expected 884 / 0 / 6 ignored, re-read; fmt + clippy clean; toolchain from `rust-toolchain.toml`); commit.

---

## Phase 2: Foundational — the key exists and is inert

- [X] T002 Add `pub relief_memory_margin: Option<u32>` to `MeowConfig` in `crates/cloudkitty-core/src/config/mod.rs` with `#[serde(default, skip_serializing_if = "Option::is_none")]` and a doc comment (spec 050: remembered relief within `[vision] radius + margin` Manhattan tiles; absent = unbounded; served 0; 039-D5 skip); set `relief_memory_margin: None` in `impl Default for MeowConfig` (same file).
- [X] T003 Extend `roam_cell_stays_out_of_the_default_serialization` in `crates/cloudkitty-core/src/config/mod.rs` with `assert!(!json.contains("relief_memory_margin"), ...)` (spec 050 comment); red-first: temporarily drop the skip attribute, predict "leaked into the stamp", see red, restore, see green — record as cycle F1 in `redden-list.md`.
- [X] T004 Add a `MeowConfig` parse test in `crates/cloudkitty-core/src/config/mod.rs` tests: `relief_memory_margin = 0` parses to `Some(0)`, absent parses to `None`, `relief_memory_margin = -1` fails to parse with an error naming the key (FR-001 negative refused); no `validate.rs` change (no upper bound).
- [X] T005 Run `cargo test -p cloudkitty-core --lib config::` and `scratchpad/cycle.sh f0`; predict: all green, count = baseline + 1 (T004); goldens and stamp unmoved (key absent from `Config::default()`); record in `redden-list.md`; commit.

**Checkpoint**: the key parses, is skip-serialized, and nothing reads it.

---

## Phase 3: User Story 1 — A thirsty cat out of sight of water may ask (P1) 🎯 MVP

**Goal**: `want_drink` is legal at margin 0 when the only water the cat knows is a remembered tile beyond reach; the served config sets 0 and the served roster says `want_drink` and gets `here_water` replies.

**Independent test**: the axis-aligned r + 1 fixture (margin 0 legal / margin 1 silent / absent silent, asserted outside the disc) and the 1,000-tick served-roster count.

- [X] T006 [US1] Write the fixture helper and drink tests in the `#[cfg(test)]` module of `crates/cloudkitty-core/src/meow.rs`: helper `remembered_beyond_the_disc(world, kind, r)` places kitty 1 at (8, 8) with a `MemorySlot` for `kind` at `(8 + r + 1, 8)` (`last_seen` 40) and asserts `!Position::new(8,8).visible_from(&slot, r)`; test `want_drink_reads_remembered_water_only_within_reach`: `config.vision.radius = 5`, drink armed (`announce_armed` + need top via `needs.add`), `forget_everything`, elements cleared, then `config.meow.relief_memory_margin = Some(0)` → legal; `Some(1)` → silent; `None` → silent. Test `water_in_view_silences_want_drink_at_every_margin`: a water element at (11, 8), margins `Some(0)`, `Some(1)`, `Some(8)`, `None` → all silent (SC-002).
- [X] T007 [US1] Run `cargo test -p cloudkitty-core --lib meow::` on the unchanged predicate; predict RED at exactly the `Some(0)` → legal assertion of T006 ("remembered relief silences" — today's rule) and green elsewhere; record as cycle U1 in `redden-list.md`; commit the red test.
- [X] T008 [US1] Change `known_relief` in `crates/cloudkitty-core/src/meow.rs` to `known_relief(want, kitty, view, margin: Option<u32>)`: replace the `remembered` closure with `|kind| kitty.memory[memory_index(kind)].is_some_and(|slot| margin.is_none_or(|m| kitty.pos.manhattan_distance(&slot.pos) <= view.radius.saturating_add(m)))` (or the equivalent match if `is_none_or` is below the pinned toolchain); update the doc comment (spec 050, the reach rule, "one rule for eat/drink/play"); `message_legal` passes `config.meow.relief_memory_margin`; update the two existing test callers (`known_relief(MessageKind::WantEat, ..., &view)` → add `None`).
- [X] T009 [US1] Run `cargo test -p cloudkitty-core --lib meow::`; predict GREEN including T006 (cycle U1 closed: red → green on the change); run `cargo test -p cloudkitty-core --test meow_law_fog` — predict green (key absent in `test_config`; SC-003); record; commit.
- [X] T010 [US1] Create `crates/cloudkitty-core/tests/relief_memory_margin.rs`: `served_all_scripted()` loader (the `fog_continuity.rs:29` pattern: read `cloudkitty.toml` from `CARGO_MANIFEST_DIR/../..`, retarget every kitty to `needs_driven`, `assert_eq!(config.vision.radius, 5)`, validate); helper `count_calls(config, ticks) -> BTreeMap<MessageKind, (usize, usize)>` driving `World::tick` × 20,000 (horizon raised from 1,000 at implement time — the served seed reads 0 at 1,000; see redden-list §U2) with `BehaviorRegistry::with_builtins()` and counting, each iteration, `let tick = world.tick;` captured BEFORE `drive_tick`, then the meows in `world.recent_meows` whose `m.tick == tick` (the `record_streams` pattern in `fog_continuity.rs:129`; the clock advances inside `drive_tick`, so a post-call `world.tick` match counts nothing) — calls per kind, and those with `reply == true`; test `the_served_roster_asks_for_water`: served verbatim → `assert!(drink_calls > 0)`, `assert!(config.meow.relief_memory_margin == Some(0))` (the served key is the precondition, named); print drink and eat counts "F-040 reading"; test `a_want_drink_gets_a_here_water_reply`: same config with `behavior.reply_intensity_floor = Some(0.01)` (test-only; any > 0 — clarification 1) → `assert!(here_water_replies > 0)`.
- [X] T011 [US1] Run `cargo test -p cloudkitty-core --test relief_memory_margin -- --nocapture` BEFORE editing the served TOML; predict RED at the `Some(0)` precondition assertion (the served key is absent) — record as cycle U2a; then temporarily set `config.meow.relief_memory_margin = None` in the test's loader and re-run: predict RED at `drink_calls > 0` with drink = 0 (F-040: structurally silent) — cycle U2b, the guard proven to see the old engine; restore the test; commit.
- [X] T012 [US1] Edit the served `cloudkitty.toml` `[meow]` section: after `announce_hysteresis = 5.0` add `relief_memory_margin = 0` with the FR-007 comment block (what: remembered relief counts only within `[vision] radius + margin` Manhattan tiles of the cat; why 0: Manhattan ≤ r is inside the disc, so memory never silences a want and the served law is "visible relief only" — F-040: water is permanent and never forgotten, so the old rule silenced `want_drink` for good; key absent = the unbounded rule; the step-5 prereg screens 0 and 1); amend the `[meow]` head comment's "(nothing visible or remembered; ...)" to "(nothing visible, nothing remembered within reach; ...)". No other TOML changes (SC-005).
- [X] T013 [US1] Run `cargo test -p cloudkitty-core --test relief_memory_margin -- --nocapture`; predict GREEN, drink calls in the ~5–25 range over 1,000 ticks (F-040 ~12; RECORD the number, not gated), `here_water` replies > 0; record in `redden-list.md` beside the F-040 numbers; commit.

**Checkpoint**: US1 complete — the drink channel is alive on the served config; the fixture pins the inclusive Manhattan bound at margin 0 / 1.

---

## Phase 4: User Story 2 — Nothing moves until a config asks for it (P2)

**Goal**: with the key absent every existing guard is untouched and green; the served key moves exactly the named pins; `PreFog` reads no margin.

**Independent test**: `git diff origin/main -- cloudkitty.toml` is one key + comments; `cargo test --workspace` shows only the predicted movers.

- [X] T014 [US2] Add test `the_pre_fog_law_reads_no_margin` in `crates/cloudkitty-core/src/meow.rs` tests: same fixture as T006 with `config.meow.law_era = LawEra::PreFog`; `want_drink` verdict identical at `Some(0)`, `Some(1)`, `None` (armed-only law; FR-008 / US2 scenario 3).
- [X] T015 [US2] Run `scratchpad/cycle.sh u2` (whole suite) with the served key landed; predict: RED only at `fog_continuity::reply_floor_unset_is_byte_identical` (messages diverge at the first `want_drink` row; note whether the ACTION stream also diverges and at which tick); GREEN at `world_covering_radius_diverges_only_by_the_named_causes` (r = 40: every tile within Manhattan 38 ≤ 40 + 0 — R5), the evolution golden, strip witness, run_json golden, joint parity, the config sweeps, `fog_visibility`, `refusal_reasons`, `shipped_configs`; count = baseline + new tests − 1 failed; record the exact divergence tick(s) as the SC-011 re-pin justification in `redden-list.md`.
- [X] T016 [US2] Re-record ONCE: `cargo test -p cloudkitty-core --test fog_continuity -- --ignored record_preladder`; then `cargo test -p cloudkitty-core --test fog_continuity` → predict green; update the doc comment on `reply_floor_unset_is_byte_identical` in `crates/cloudkitty-core/tests/fog_continuity.rs` (re-recorded for spec 050: the served `relief_memory_margin = 0` revives `want_drink`; first divergence tick N; actions moved / unmoved); commit the two fixtures `crates/cloudkitty-core/tests/fixtures/preladder-r5-20k.{actions,messages}.digest` with the comment.
- [X] T017 [US2] Verify SC-005: `git diff origin/main -- cloudkitty.toml` shows exactly the new key, its comment block and the amended head comment; `cargo test -p cloudkitty-core --lib config::tests::roam_cell_stays_out_of_the_default_serialization` green; `grep -rn relief_memory_margin evals/ training.toml experiments/` shows NO hit under `evals/` (frozen) — record in `redden-list.md`.

**Checkpoint**: US2 complete — one stream re-pinned with its cause named; everything default-keyed unmoved.

---

## Phase 5: User Story 3 — One rule for every remembered relief (P3)

**Goal**: eat and play read the same reach; cuddle, bath, sleep never read the margin; a random-world property derives the verdict independently (A14).

**Independent test**: the same fixture for chow and bug; the new property in `meow_law_fog.rs`.

- [X] T018 [P] [US3] Add tests in `crates/cloudkitty-core/src/meow.rs` using the T006 helper: `want_eat_reads_remembered_chow_only_within_reach` (Eat armed and top; slot Chow at (8 + r + 1, 8); `Some(0)` legal, `Some(1)` silent, `None` silent) and `want_play_reads_remembered_critters_only_within_reach` (Play armed and top; no critter, no idle friend in view — park the other kitties beyond the disc or give them an `activity_clock`; slot Bug at the fixture tile; same three verdicts; repeat with Greeble); `the_social_words_never_read_the_margin`: cuddle / bath / sleep verdicts equal across `Some(0)`, `Some(1)`, `Some(8)`, `None` with a remembered water/chow/bug slot present (SC-006).
- [X] T019 [P] [US3] Add property `the_reach_rule_holds_over_random_worlds_and_margins` to the `proptest!` block in `crates/cloudkitty-core/tests/meow_law_fog.rs` (do NOT edit `the_law_holds_over_random_worlds`): strategies `seed 0..5_000`, `radius 2..=8`, `margin in prop::option::of(prop_oneof![0u32..=4, Just(u32::MAX)])` (u32::MAX exercises the saturating add and the "≥ width + height ≡ absent" edge case), `needs vec(0..100, 6)`, `slots in vec(prop::option::of((0u32..20, 0u32..20)), 5)` written into kitty 1's memory in `ElementType::ALL` order (`last_seen` 90); `config.meow.relief_memory_margin = margin`; oracle: `within(kind) = slot.is_some_and(|(x,y)| margin.map_or(true, |m| (10u32.abs_diff(x) + 10u32.abs_diff(y)) <= radius + m))` with kitty 1 at (10, 10); relief per kind = visible ∨ within; `prop_assert_eq!(message_legal(...), need == top && !relief && vocabulary.enabled)` for eat / drink / play; cuddle / bath / sleep verdicts unchanged by `margin` (re-judge with `relief_memory_margin = None` on a cloned config).
- [X] T020 [US3] Red-first for T018/T019 against the predicate: temporarily change `<=` to `<` in `known_relief` (`crates/cloudkitty-core/src/meow.rs`); predict RED at the `Some(1)` → silent arm of every fixture (the bound at exactly r + 1 = r + margin is the inclusive case) and at the property; restore; re-run `cargo test -p cloudkitty-core --lib meow:: --test meow_law_fog`; predict green; record as cycle U3 in `redden-list.md`; commit.

**Checkpoint**: US3 complete — one closure, one rule, independently derived.

---

## Phase 6: Polish, records, readings

- [X] T021 [P] Update the known-relief table in `specs/049-fog-gen1/contracts/meow-law-v5.md`: eat / drink / play rows gain "∨ `memory[kind]` present **within reach** — Manhattan(pos, tile) ≤ `[vision] radius` + `[meow] relief_memory_margin`, unbounded when the key is absent (spec 050; served 0 = visible relief only)"; one sentence under the table pointing at `specs/050-relief-memory-margin/contracts/relief-memory-margin.md`.
- [X] T022 [P] Add the new-keys row to `specs/049-fog-gen1/contracts/config-3.0-migration.md`: `[meow] relief_memory_margin` | non-negative integer, **optional** | absent (= the unbounded rule) | served 0 (spec 050; the step-5 prereg screens 0 and 1) | the want law's memory reach.
- [X] T023 [P] Amend the law paragraph in `docs/meows.md` (lines ~55–60): "a bowl visible or remembered **within reach**", "water visible or remembered within reach", "a critter visible or remembered within reach", plus one sentence: reach = `[vision] radius + [meow] relief_memory_margin` Manhattan tiles from the cat; absent = any remembered tile; served 0 (visible relief only). Do not restructure the section (preserve-user-authored-docs).
- [X] T024 [P] Add the `CHANGELOG.md` Unreleased one-liner after the 049 entry: `[meow] relief_memory_margin` (spec 050) — a remembered element is known relief only within radius + margin Manhattan tiles; served 0 revives `want_drink` (F-040); key absent = the old rule; the served r = 5 stream pins re-recorded. Re-read the marker legend at the top of the file first; apply the marker that names a served-dynamics move (no `[stamp]`, no `[obs-schema]`).
- [X] T025 Re-take the served welfare readings: `cargo test -p cloudkitty-rl --test welfare_longrun -- --ignored served_world_fog_r5 --nocapture`; write the r = 5 and r = 64 violation counts into the gate comment in `crates/cloudkitty-rl/tests/welfare_longrun.rs` ("after spec 050 (served margin 0): r = 5 N, r = 64 M — readings, not gates") and into `redden-list.md` (SC-007).
- [X] T026 Final cycle: `cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings`, then `scratchpad/cycle.sh final`; predict: 0 failed, 6 ignored, count = baseline + (T004 1 + T006 2 + T010 2 + T014 1 + T018 3–4 + T019 1); `git status` shows nothing under `evals/`; record the FINAL count in `redden-list.md`; commit.
- [X] T027 Update memory files (`spec-050-relief-memory-margin-arc.md`, `MEMORY.md`): implement DONE, counts, divergence tick, welfare numbers; NEXT = PR on the owner's go, then the Experiments ping (R8: `anchor.toml` margin 0, schema_check A1/A9 re-smoke, relief sweep, drop `want_drink` from `declared_constant.json`, PREREG config rule gains the key).

---

## Dependencies

- Phase 1 → Phase 2 → US1 (T006–T013 strictly in order: red test before the predicate; integration red before the served key).
- US2 depends on US1 (T012's served key is what moves the T015/T016 pin). T014 can be written any time after T008.
- US3 depends on T008 (the predicate) only; T018 and T019 are parallel with each other and with US2's T014–T017 (different files).
- Phase 6: T021–T024 parallel (four different files), any time after T012; T025 after T012; T026 after everything; T027 last.

## Parallel examples

- After T008: T014 (meow.rs tests) with T019 (meow_law_fog.rs) — different files. T018 shares `meow.rs` with T014; sequence those two.
- After T012: T021, T022, T023, T024 together; T025 alongside (a ~7 s ignored run).

## Implementation strategy

MVP = Phase 1 + Phase 2 + US1 (T001–T013): the key, the predicate, the inclusive-Manhattan fixture the owner asked to see red, and the served-roster proof that `want_drink` and `here_water` are alive. US2 then names the one pin that moves and re-records it once. US3 closes "one rule" with the eat/play fixtures and the independent property. Polish writes the four records and the welfare readings. PR only on the owner's go; after merge, ping Experiments.
