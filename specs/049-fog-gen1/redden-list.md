# 049 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast`; predictions written BEFORE the run;
restore verified by RE-READING THE COUNT. Commit before every
mutate-then-revert cycle (checkout-trap rule, five occurrences on record).
Any mutation that can move a live trajectory predicts ALL golden-family pins
(evolution golden, strip witness, run_json golden, joint parity only if the
drivers diverge) or names why not (048 cycle-A lesson).

Baseline count (branch tip `8bf9ed8`, before any engine change, 2026-09-03):
**818/0, 1 ignored** (the rl 20k welfare longrun), 64 test binaries;
`cargo fmt --all -- --check` clean; `cargo clippy --workspace --all-targets
-- -D warnings` clean. Toolchain 1.97.1 per `rust-toolchain.toml`.

FINAL count: recorded at T085.

| # | Task | Mutation / staging | Prediction (exact reds) | Observed | Restored + count re-read |
|---|------|--------------------|-------------------------|----------|--------------------------|
| 0 | T001 | none (baseline) | — | 818/0, 1 ignored | — |
| 1 | T008 (rule-6 sort) | `kitty_slots` default 3 → 4 with the old guard left in place | `rl config::tests::an_empty_file_yields_the_documented_defaults` red (`left: 4, right: 3`) | that red PLUS, at the full-suite run, 15 more: every schema-4 derived literal in rl/server (`the_default_layout_is_225_values`, `the_default_menu_has_exactly_thirty_four_entries…`, `…23_tokens`, `the_logit_budget_is_fifty`, `the_schema_four_numbers_match_the_contract`, 2 mask, 2 codec/episode vacant-slot, `the_forward_matches_the_numpy_oracle…`, `all_three_committed_artifacts_expand…`, `every_index_decodes…`, 2 `policy_kitty`) — the T025/T029/T031 must-fail set, one phase early | **DEFERRED**: default restored to 3, roster check + test withdrawn to the head of Phase 4 (T008 re-lands with T024); the 3-guard re-observed then. Suite re-read below. |
| 2 | T006 (rule-6 sort) | `[meow] digest_window_ticks` made REQUIRED (no serde default) | 4 core config tests that asserted the 028 "partial `[meow]` fills from defaults" posture red: `meow_dial_defaults_land_and_the_rows_hold`, `the_retired_courtesy_trio_is_rejected_loudly`, `the_retired_meow_cooldown_knobs_are_rejected_loudly`, `an_omitted_vocabulary_table_means_the_documented_defaults` | exactly those 4 (94/4 in `config::`) | each re-pointed to carry the required key (the two rejector tests die at T069 anyway); `a_meow_section_without_the_digest_window_is_refused` is the new guard; `config::` 98/0 |
| 3 | T011 (rule-6 sort) | `recent_meows` retention → `digest_window_ticks` (30) | `per_tick_meowing_stays_bounded_by_the_pruning_window` red (31 entries for window 10); `recent_meows_stay_bounded` red only if the 60-tick test world meows at all (uncertain) | both red exactly as predicted (the second: meows do exist by tick 60) | both re-pointed at the digest window; `fog_continuity` guard green at the served digest 30 = retention proven inert for actions AND messages over 20k ticks (the built-ins and the schema-4 digest filter to the cooldown until T054/T024) |
| 4 | T012/T070 (rule-6 sort) | `memory`/`explore_heading` required; seven shims + `improved_at` default deleted; always-serialized | 6 `kitty::tests` shim tests red (`a_pursuit_saved_before_improved_at…`, `a_pre_006…`, `a_pre_004…`, `a_pre_028…`, `empty_bookkeeping_stays_off_the_wire`, `restored_meow_bookkeeping…`); server `behavior_descriptions_serve_per_seat_kind…` red (plugin seat: absent → `null`); the two ruled fixture tests + the spec-004 stuck-state replay red (pre-3.0 records) | exactly those (6 + 1 + 2 + 2) | shim tests re-pointed to 3.0 records / refusals; server guard re-pointed to `null`; the two ruled tests + fixtures DELETED, inverse guards `a_pre_3_0_meow_entry_is_refused` + `a_pre_3_0_kitty_record_is_refused_naming_the_missing_field` green; spec-004 fixture completed mechanically (not a run record — a regression stage); core lib 472/0 |
| 5 | T014 (golden regeneration) | fog view as the only decider world, at the world-covering compiled radius (64 = 32 + 32; served 40 = 20 + 20) | evolution golden + strip witness red (serialized bytes: new fields, always-serialized shims, 30-tick buffer); NOT the run_json golden; NOT the byte-identity guard | exactly the 2 goldens; 827/2 | regenerated from one run with the justification in the doctrine comment; continuity witness = `world_covering_radius_reproduces_pre_fog_actions` green at the served digest window; suite re-read below |
| 6 | T005 | `visible_from`: `≤` → `<` (the edge unseen) | 3 reds: `grid::…the_vision_disc_is_euclidean_and_closed_on_its_edge`, `world::…fog_for_keeps_the_disc_and_blanks_friends_minds`, `fog_visibility::the_view_is_exactly_the_euclidean_disc` (inline oracle); goldens/continuity/plugin green (world-covering radii) | exactly those 3 — PLUS a standing red shared with 7a: `script::tests::a_decision_request_serializes_with_the_documented_shape` (asserted `v == 2`; the T015 kept-behaviour guard I had not re-run after the bump) | restored (`git checkout`), 0 dirty; the standing red re-pointed at 3 and committed (`b8e3cf8`) before cycle 7b |
| 7a | T007 | `validate_vision`: `radius < 2` → `< 1` | 1 red: `config::…vision_radius_below_two_is_refused_naming_the_key` | exactly that (+ the same standing red as cycle 6) | restored, 0 dirty |
| 7b | T007 | `validate_meow`: `is_multiple_of` → `<` (25 accepted) | 1 red: `config::…digest_window_must_be_a_positive_multiple_of_the_cooldown` | exactly that; 830/1 | restored, 0 dirty |
| 7c | T007 | `validate_behavior`: floor range `..=1.0` → `..1.0` (1.0 refused) | 1 red: `config::…reply_intensity_floor_outside_the_unit_interval_is_refused` | exactly that; 830/1 | restored, 0 dirty |
| 8 | T015 | `PROPOSAL_WIRE_VERSION` 3 → 2 | 3–4 reds: `plugin_e2e::the_request_carries_wire_v3_and_a_fogged_world`, `…a_well_behaved_plugin_drives_kitties_for_a_full_day`, `…a_plugin_that_dies_mid_run…` (uncertain: the fixture refuses before its first reply), `script::…a_decision_request_serializes…` | exactly 4 (the uncertain one red); 827/4; the tick loop untouched in every case (SC-013's fallback path) | restored, 0 dirty |
| 9 | T016 | `fog_for`: the element filter dropped | 3 reds: `fog_visibility`, `world::…fog_for_keeps…` (element 902 present), `plugin_e2e::the_request_carries_wire_v3…` (a leaked element at r = 2 → the fixture exits 4 → fallback provenance) | exactly those 3; 828/3 | restored, 0 dirty (the proptest regressions file the induced failure wrote was deleted, not committed) |
| 10 | T016 | `visible_from`: Euclidean → Manhattan | 3 reds: `grid::…edge` ((3,4) at Manhattan 7 unseen), `world::…fog_for_keeps…`, `fog_visibility` (inline oracle); plugin v3 green (the diamond is a subset of the disc: no leak); goldens/continuity green | exactly those 3; 828/3 | restored, 0 dirty |
| 11 | T019 | `update_memories`: the refute branch skipped (`if false`) | property `memory_is_the_nearest_sighting…` + scenario `a_remembered_bowl_that_is_gone_clears…` red; goldens red (state) | exactly the 2 memory guards; goldens GREEN — at the world-covering compiled radius the refute arm is dead (every element is always visible, the first arm always fires), so the mutation cannot move state there: over-predicted, recorded | restored, 0 dirty; 839/2 |
| 12 | T019 | `update_memories`: nearest → farthest (`min_by_key` → `max_by_key`) | property red, `two_visible_bowls…` red, `a_world_covering_radius_mirrors…` red, goldens red (state) | `two_visible_bowls…` + 2 goldens ONLY (838/3): the PROPERTY stayed green and so did the mirror test — the test world spawns ONE element per kind, so "nearest" is never contested. A vacuous guard (rule 6): fixed, not excused → cycle 12b | restored, 0 dirty |
| 12b | T019 | same mutation after the property test stages THREE of every kind (`6c32b80`) | property red, `two_visible_bowls…` red, goldens red | exactly those 4 (837/4); the mirror test stays green (the compiled world's spawn happens to place one per kind — noted, its nearest clause is covered by the property now) | restored, 0 dirty |
| 13 | T019 | `update_memories`: clear on every tick out of view (`if true \|\|`) | property red; `a_bowl_walked_past…`, `a_remembered_bowl…`, `a_positive_timeout…` red; determinism `the_same_seed_produces_the_same_memory_under_fog` red (its ≥ 2 populated precondition); mid-run restore uncertain; goldens green (nothing is ever out of view at the covering radius) | exactly 5: the 4 memory guards + the determinism precondition; restore green; goldens green as predicted | restored, 0 dirty; 836/5 |
| 14 | T021 | `#[serde(skip)]` on `Kitty.memory` (zero memory on restore) | `a_mid_run_save_restores_memory…`, `a_pre_3_0_kitty_record_is_refused…`, `empty_bookkeeping…wall_fields_always_on_it`, server `kitties_on_the_world_payload_carry_memory…`, goldens ×2 = 6 | 9: the 6 PLUS 3 `plugin_e2e` (the well-behaved fixture exits 4 on a `me` without `memory` — the T015 fogged-world check, consistent, under-enumerated) | restored, 0 dirty; 832/9 |
| 15 | T008/T024/T025 (rule-6 sort) | `kitty_slots` 3 → 4 with the schema-5 constants (SELF 85, KITTY 62, digest deleted) | every schema-4 literal red: the 16 of cycle 1 (`the_default_layout_is_225_values`, `…thirty_four_entries…`, `…23_tokens`, `the_logit_budget_is_fifty`, `the_schema_four_numbers…`, 2 mask, 2 codec/episode, oracle parity, 3 expansion, 2 `policy_kitty`) PLUS the six global-digest tests, which cannot compile once `MEOW_DIGEST` is gone | as predicted: the 16 observed red at cycle 1 (recorded there); at this landing the digest tests failed at COMPILE (the loudest red) and the rest at run | all re-pointed or replaced: `schema_five_pins.rs` (404/4/39/20/8/55/55/7/5/3/3/1/15/16/24/40), menu indices at k = 4, token layout 16/7, `oracle.ckpolicy` regenerated (numpy-only generator `make_oracle_v5.py`, sha 8c1691b4…; the schema-4 oracle kept as the refusal witness), expansion → target-pin refusal, served seats parked; 835/0 |
| 16 | T025 | `SELF_BLOCK` + 1 | class: the schema-5 pin (404), `the_default_layout_is_404_values`, `the_self_block_is_carried…` (85), the parity fixture (405 ≠ 404), AND every test that encodes an observation (the encoder's `debug_assert_eq!(v.len(), observation_len)` fires) | 36 reds = exactly that class (observe, episode, harness, policy, py-side rl, the parity + the server oracle boot); 802/36 | restored, 0 dirty |
| 17a | T027 | kitty rows filled nearest-first (the schema-4 rule) instead of by id | 4: `kitty_rows_are_by_id…`, `rows_are_permanent…`, `a_heard_row_points…`, `a_distant_groom_target_keeps…` | exactly 4; 834/4 | restored |
| 17b | T027 | needs + happiness zeroed on SEEN rows | 1: `rows_are_permanent…` (happiness shown) | exactly 1; 837/1 | restored |
| 17c | T027 | "use the live position on heard rows" — CANNOT be staged: the view holds no live position for an unseen friend (there is nothing to leak from); the structural proof is the T016 leak guard + `a_heard_row_points…` asserting the meow's stamped tile | — | — | recorded per rule 3 |
| 17d | T027 | staleness normaliser derived from the world (width + height) instead of the frozen 40 | 1: `the_memory_cells_read…` (staged on a 24×24 world so 48 ≠ 40) | exactly 1; 837/1 | restored |
| 18 | T028 | loader roster check `>` → `>=` | class: every test loading a 5-cat config at 4 slots (both sweeps, harness served, eval_suite ×9, `policy_kitty` served, rl `roster_above…`); the server 6-cat test stays green | 16 reds, exactly the class; 822/16 | restored |
| 19 | T030 | "compute one entry on the full snapshot" — CANNOT be staged: `legal_action_mask` takes only the `FogView` (no full snapshot in scope). The R2 guard in `mask_oracle` compares the fogged verdict at r ∈ {2, 3, 5, 40} against the world-covering view with the same table and named the two exceptions above; cycle 9/10's fog_for mutations are what redden it | — | — | recorded per rule 3 |
| 20 | T031 | MLP (v2) loader's pin compare skipped | `schema_four_artifact_is_refused` etc. | 3 reds, NONE of them the new witnesses: the schema-4 oracle is a v3 artifact gated by the attention loader (`attn.rs:324`), not `policy.rs:259`. Wrong layer — re-run as 20b | restored |
| 20b | T031 | attention (v3) loader's pin compare skipped; the witnesses first tightened to the gate's own words (`4c98a0e`) | 5: `schema_four_artifact_is_refused`, server `a_schema_four_artifact_fails_startup…`, `policy_kitty::the_shipped_config_parks…`, `each_rejection_class_fails_by_name…`, expansion `the_serving_loader_still_refuses…` | exactly 5; 833/5 | restored, 0 dirty |
| 21a | T037 | rate denominator = the window (not window / cooldown) | 1: `per_speaker_recency_and_rate_cells…` | 2: that + `the_observers_own_block…` (its rate 1/3 too — under-enumerated); 841/2 | restored |
| 21b | T037 | intensity cells zeroed | 1: `want_intensity_cells_carry_the_last_stamp…` | exactly 1; 842/1 | restored |
| 21c | T037 | a call at age == window counted (`<` → `<=`) in the block's own audibility closure | 1: `per_speaker…` (friend 4's edge-of-window call) | ZERO — the row STATE comes from `FogView::heard_unseen` (strict `<`, untouched), so friend 4 stayed silent whatever the block counted: two definitions of audibility, one guard. Fixed at `192d90f`: `FogView::audible` is THE rule, used by the heard rows and the message cells | restored |
| 21c′ | T037 | the same edge, on the one definition (`world.rs`) | 2: `per_speaker…` (friend 4 becomes heard), `world::tests::heard_unseen…` (age-30 excluded) | exactly 2; 841/2 | restored |
| 22a | T041 | scene age normaliser "derived" (12, a table value) instead of the frozen 24 | 1: `scene_age_reads_elapsed_over_a_frozen_twenty_four` | exactly 1; 842/1 | restored |
| 22b | T041 | the water bit computed on HEARD rows from the stamped tile | 1: `the_neighbour_in_water_bit_and_scene_age_are_seen_only` | ZERO — the staging had walked the pond OUT of the disc with the friend, so nothing was in view to leak (vacuous). Re-staged at `11b82a1`: the pond stays inside the disc at the friend's meow tile, the friend outside | restored |
| 22b′ | T041 | the same, pond in view | 1 | exactly 1; 842/1 | restored |
| 23 | T049 (rule-6 sort) | the law landed (want tier armed ∧ top ∧ no known relief; here tier adjacent ∨ reply) | must-fail: `a_grounded_clear_message_emits_and_records` (want_eat beside a visible bowl), `a_want_word_outranks_a_here_word`, `needs_driven::…a_grounded_cat_announces_its_highest_pressure_legal_want` (idle friend in view), `…announcing_never_alters_the_chosen_activity` (bowl in view at r = 64); goldens (the want law moves the buffer and — via the groom response — the trajectory); `fog_continuity` (actions diverge where a silenced `want_bath` no longer draws a groom) | exactly those 7 (836/7) | the four re-pointed (WantSleep = the ungated kind; the bowl out of sight at r = 5; the friend busy vs idle), goldens re-pinned (an intentional move), `fog_continuity` AMENDED: identical up to the first divergence, which must be a silenced-want_bath groom response, messages before it only silenced wants or calls a silenced predecessor's cooldown freed — OWNER FLAG (SC-004 as written cannot hold with FR-036; the visibility filter's byte-identity stands at the pre-law commits) |
| 23a | T048 | the top-need clause dropped | `only_the_top_need_may_ask`, property, goldings? | 4: both law guards + 2 goldens (846/4); continuity green (at r = 64 only sleep wants are ever legal, so the clause rarely bites there) | restored |
| 23b | T048 | the memory clause dropped (eat/drink) | 1 scenario; the property stages no memory (recorded) | exactly 1 (849/1) | restored |
| 23c | T048 | the critter clause dropped (play) | 1–2 | 1: the scenario; the property's friend clause masks its critter clause at most radii (recorded) | restored |
| 23d | T048 | a heard-unseen friend silences the social words | 2 | script mismatch — ran UNMUTATED (850/0 = the true count); redone as 23d′ | — |
| 23d′ | T048 | same | 2: `the_social_words…`, property (the "hearing moved the gate" check) | exactly 2 (848/2) | restored |
| 23e | T048 | a mid-scene visible friend counts as idle (`idle_friend_in_view` ignores the clock) | scenario, property?, goldens, `a_grounded_cat_announces…` | 5: scenario, `a_grounded_cat_announces…`, `groom_kitty_appears_in_a_seeded_scripted_run` (fewer want_bath → no groom), 2 goldens (845/5); the property's stagings have no busy friends (recorded) | restored |
| 23f | T046 | reply stamped on adjacency alone | 1: `a_here_can_answer…` (scenario 5's `!reply`) | exactly 1 (849/1) | restored |
| 23g | T045/T048 | same-tick calls audible (`FogView::audible`: `<` → `<=`) | ≥ 4 | 4: `a_here_can_answer…` (scenario 6), `a_here_after_my_want…` ("three ticks at best"), `the_observers_own_block…`, `world::…heard_unseen…` (846/4) | restored |
| 23h | T050 | answers-me ignores the want-before-here order | 1: `a_here_before_my_want…` | exactly 1 (849/1) | restored |

## Phase 7 checkpoint (T052, 2026-09-03)

Count at `a8ad22c`: **850/0, 2 ignored** (843 + 5 `meow_law_fog` + 2
answers-me). The plan's `LawView` is the `FogView` itself: `fog_for` builds
it for the mask AND the enforcement seam, so the two cannot disagree except
by the documented mid-tick element divergence. Three property weaknesses
recorded rather than papered over (23b/23c/23e): the random stagings never
contest memory, the critter clause under an idle friend, or busy friends —
the scenario tests carry those clauses.

## Phases 5–6 checkpoint (T039/T042, 2026-09-03)

Count at `11b82a1`: **843/0, 2 ignored** (838 + 5: three US3 and two US4
scenario tests). Two vacuous first cycles (21c, 22b) caught by reading the
count: a guard whose staging cannot see the mutation is not a guard —
both fixed at the source (one audibility definition; the pond in view)
and re-proven.

## Phase 4 checkpoint (T035, 2026-09-03)

Count at `4c98a0e`: **838/0, 2 ignored** (841 at Phase 3 − the 6 global-
digest tests − the spec-035 map-running expansion tests + the pins /
row / refusal / boot guards; cycle 17b/17d read 837 + 1 induced). Python
surface: 18 passed, 1 skipped (PettingZoo conformance without gymnasium,
as in CI). Lessons banked: cycle 20 — mutate the layer the FIXTURE goes
through (the v3 gate, not the v2 one); cycles 17c/19 — a mutation the
type system makes unspeakable is recorded, not faked.

## §phase-4 notes (schema-5 landing, 2026-09-03)

- **Served seats parked**: `register_policy_behaviors` opens every seated
  artifact and schema 5 refuses all five 2.x minds, so `cloudkitty.toml`'s
  five seats are `needs_driven` on this branch (the step-5 shakeout /
  corpus state) with the `[rl.policy.*]` blocks kept as the record;
  `policy_kitty.rs` now asserts SC-008 on the REAL artifacts (found 4 /
  expected 5, before any tick) — the "fourth tour" the third-tour test's
  own doc asked for. OWNER FLAG: the served file cannot boot policy seats
  until Gen 1 minds exist (step 7).
- **Mask under fog, two exact statements** (`mask_oracle.rs`): (1) a
  kitty-targeted entry whose row names a friend outside the disc is fog-
  silenced (a pursuit would step on the friend's live position); (2) a
  scene whose critter counterpart hopped outside the disc but still lives is
  undecidable — the fogged probe prunes it (unseen = gone, the 048 rule) and
  releases the non-continuation set, the full world continues the scene; no
  mask is right for both alive and dead, and releasing is the benign choice
  (a duration override, never a refusal). Everywhere else the fogged mask
  equals the full-world mask at every radius ≥ 2, with the table built from
  that radius's view. Quickstart §3's expectation carries this wording.
- **Expansion tool (T032 choice)**: `TARGET_PINS` (4/3/3) added; a
  well-formed pre-wall source is refused at this binary naming both surfaces
  (`UnmappedTarget`); the spec-035 placement / attestation / deaf-mute guards
  ran the map for real and cannot execute at schema 5 — deleted, restorable
  from history when a 3.0 map is ruled; the source-shaped refusals keep their
  names.
- **Oracle fixture (T031 choice)**: numpy-only generator (no venv here has
  torch); seeded synthetic weights at the schema-5 layout; the numpy forward
  is the independent reference the parity test needs. `tensor_sizes` and the
  loader no longer assume eight embeddings (a phantom bias for the deleted
  message group would have broken every blob length).
- **Mask-oracle rosters clamped to 5**: rosters above `kitty_slots + 1` are
  refused at load (FR-011), and a sixth cat with no row makes a partnered
  continuation inexpressible (all-zero) — exactly the state the rule forbids.

## Phase 3 checkpoint (T023, 2026-09-03)

Count at `6c32b80`: **841/0, 2 ignored** (cycle 11's 839 + its 2 induced
reds; 831 + 10 Phase-3 guards: 7 `fog_memory`, mid-run restore, memory
determinism, `/world` memory fields). Goldens re-pinned once (T018: memory
populated in serialized state; byte-identity guard green). Lesson banked
from cycle 12: a property guard whose staging never CONTESTS the rule it
guards is vacuous — stage the contest.

## Phase 2 checkpoint (T017, 2026-09-03)

Count at `b8e3cf8`: **831/0, 2 ignored** (baseline 818 + 13 new guards −
1 deleted fixture test + …: the exact ledger is the sum of the rows above;
re-read from cycle 7b/7c's 830 + the one induced red). Wall ≈ 100–150 s per
full-suite cycle. T008 (deferred) lands at the head of Phase 4 with its own
row.

## §phase-2 notes (T014 checkpoint)

- **Compiled default radius is ARC-TEMPORARY 64** (T006 amended at T014):
  every golden, determinism and welfare guard runs on `Config::default()`
  (a 32×32 world), so a compiled placeholder 5 would have moved the goldens
  the moment the fog view landed — the plan conflated the served TOML's 40
  with the compiled default. Rule: ARC-TEMPORARY radius = width + height of
  that world (always ≥ the diagonal): compiled 64, served 40, training 48,
  tiny-world 24, exp-006 families 44/52/56, scale exam 96. T080 flips every
  one to 5; T078's stamp diff is taken AFTER T080 (the stamp moves twice,
  nothing pins it).
- **Golden regeneration is per intentional move, not once**: T081's "ONCE"
  would leave the continuity witness dark for ~60 tasks; regenerating at
  each predicted, justified move (T014 now; the want law; fog-era
  targeting/exploration; r = 5) keeps it armed between them. Each is a
  redden-list row.
- **Built-in audibility stays the cooldown until T054**: `groom_response`
  reads the buffer through an age ≤ `recent_window_ticks` filter (and the
  schema-4 digest likewise, until schema 5 replaces it), so the retention
  move alone is inert — the FR-017 audibility widening for scripted cats is
  T054's deliberate change, with its own golden row.

## §phase-2 notes (T009 checkpoint)

- **`evals/v2` front-loaded from T073**: `evals/v1` is hash-frozen (manifest
  sha256 + `eval_suite.rs` freeze guard) and cannot carry `[vision]`, so the
  moment the section became required (T006) the v1 exams stopped loading and
  `eval_suite.rs` (which builds scratch suites from the exam files) went
  red. The v2 cut (six complete 3.0 configs via `complete_config_3.py`,
  radius ARC-TEMPORARY 40, new manifest hashes), `evals/v1` → exclusions, and
  the `eval_suite.rs` / `shipped_configs_rl.rs` / `kitty-eval` retargets
  landed at T009.
- **OWNER FLAG (FR-011 consequence the plan did not price)**: with permanent
  by-id rows the loader refuses roster > `kitty_slots + 1`, so `scale` (8
  cats) and the three `mixed-roster` cells (6 cats) now carry
  `[rl.observation] kitty_slots = roster − 1` (7 / 5) to load at all — and
  therefore a different observation width (85 + 7×62 + … / 85 + 5×62 + …),
  which a 404-wide Gen 1 mind cannot sit. Certification at step 6 needs
  either minds shaped per exam roster or an exam redesign; recorded in each
  exam's `[rl.observation]` comment and raised in the PR. Reversible: the
  four exams are the only live configs with rosters above five.
- **Record classification (T072's, taken early)**: nine 2.x directories
  joined `config-sweep-exclusions.txt` with reasons (exp-004 families /
  pilot / rebaseline, here-word-screen arms, sunbeam screen, attn-ppo test
  worlds, tail-benchmarks, exp-005-leash, evals/v1); the live set = served,
  training, clowder tiny-world, the spec-004 stuck-state fixture, and the
  43 exp-006 cert/collect/family configs (FR-034's "cert, collect, lab
  families"). T072 re-runs the script in `--check` mode and reviews.
- `experiments/tools/config-3.0-defaults.toml` is GENERATED from
  `Config::default()` (T009); regenerate when a compiled default moves.

## Standing-reds ledger

Reds present at a HEAD that are NOT the cycle under test (so they are never
evidence). Must be empty at T085.

- (none)

## §stamp-before (T003)

`engine_defaults_sha256()` at `8bf9ed8` =
`6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`.
The serialized defaults it hashes are captured beside this file, pretty-
printed, in `stamp-before/core-defaults.json` (3,706 bytes) and
`stamp-before/rl-defaults.json` (630 bytes) — the R13 diff basis for T078.
Note for T078: the stamp test (`suite.rs::the_engine_defaults_stamp_is_stable_and_well_formed`)
pins no hex value — it checks shape, stability and sensitivity — so there is
no pinned hash to update; the proof is the JSON diff showing exactly the new
keys, recorded here at T078.

## §prefog-streams (T002)

Recorded at `8bf9ed8` by `fog_continuity.rs::record_prefog_streams` (ignored;
run once): served config, all five seats `needs_driven`, served seed
20260718, `announce_here` 0, 20,000 ticks.

- `tests/fixtures/prefog-actions-20k.digest`: 20,000 lines, one per tick,
  one short code per kitty in id order (M{n,e,s,w} move · R/S/G{-|id} rest,
  sleep, groom · E · D · C{e|k}{id} chase · P{-|e|k…} play · U purr ·
  W{kind} meow-action · I idle · `_` no action yet).
- `tests/fixtures/prefog-messages-20k.digest`: 4,137 rows
  `tick kitty kind intensity`, sorted (kitty, kind) within a tick. Kind
  census: wait_for_me 1,212 · want_cuddle 990 · want_eat 731 · want_sleep
  452 · want_drink 448 · want_play 205 · want_bath 99 · no here-words (ambient
  off), no purr meows recorded in this run.

## §consumers (T004) — schema-4 / wire-v2 literals outside the engine

Live tooling (fix in the named task):

| hit | what | task |
|---|---|---|
| `docs/encodings.md:34` | "CURRENT: schema 4 … = **225**" section | T034 (rewrite; schema-4 table → historical) |
| `docs/encodings.md:109,141,149` | menu 34 / 50 logits / kitty-pointer 15 in the action + v3 output sections | T034 (note menu 39 / 55 at `kitty_slots` 4) |
| `docs/encodings.md:197` | §bc-collect: "a v4-observation dataset is 225/34/16-shaped" | T079 |
| `docs/howto-rl.md:46` | "the first 34 entries mark …" (mask split) | T086 |
| `docs/rl-training.md:136` | comment "(… the vector to 225)" | T086 |
| `docs/plugins.md:61` | `"v": 2` wire example | T015 |
| `crates/cloudkitty-py/tests/test_parallel_env.py:54` | `mask.shape == (50,)` literal | T033 (→ 55); obs shape is asserted `> 100` only (derived) |
| `experiments/exp-006-character-gen/cert_harness6.py:55-56,227` | `N_ACT, N_MSG = 34, 16`; asserts `(w, mw) == (225, N_HEADS)` — **imported by `binding_continuity.py`** (`SEATINGS`, `load_model`), and `N_ACT` slices the mask | T083 (the re-baseline cannot run against 34/50 literals; decision recorded there — Experiments' file, touched only as the cutover housekeeping the wall PR owns) |
| `experiments/attn-oracle-2026-08-15/{make_oracle_v4,obs_tokens_v4,numpy_forward_v4}.py` | the schema-4 oracle generator behind `crates/cloudkitty-rl/tests/fixtures/oracle.{ckpolicy,parity}` (`OBS_DIM == 225`, msg token group) | T031 (a schema-5 fixture needs a generator; choice recorded at T031) |

Derived, no literal (checked, nothing to do): `experiments/tools/bc-collect`
and `artifact-tools/zero-artifact` read `observation_len(&rl.observation)`
and `OBSERVATION_SCHEMA_VERSION` from the crate; the py binding exports the
crate constants and derives the space from `observation_len`.

2.x records (leave; the schema they name is the one their runs were made under):

- `docs/model-atlas.html` (225 ×4): the atlas of the 2.x roster's surface.
- `experiments/exp-001-bc-mappo/trainer/forensics_replay.py` (`MEOW_DIGEST = 18`, schema 3).
- `experiments/exp-004-meow-channel/{check_v4.py, trainer/data.py}` (schema-4 / `kitty_slots 3` menu tables of a closed experiment); `verdicts_v4.py:25` "225" is an incident bar, unrelated.
- `experiments/exp-004-meow-channel/trainer/train_ppo_v4.py`, `exp-005-leash/trainer/*` (`"msg"` buffers — the message head, not the digest group).
- `experiments/attn-clone-2026-08-12/model_attn_policy.py`, `attn-meow-econ-2026-08-14/*` (schema-4 token groups of closed arcs).
- `experiments/here-word-screen/arm-A1.toml`, `arm-A3.toml`: the only `announce_here = 1` configs — Experiments' frozen screen arms (T066 records why no corpus-collection config carries the reply floor yet).

## §review

`/code-review medium 049` (2026-09-03, eight finder angles over the
37-commit branch) returned eight findings plus follow-ups. Every finding
was re-verified against the tree before its disposition; fixes landed
red-first (cycles R1–R4 below), four commits f645286 · 18241c2 · eaf961e ·
88b3cf7. Suite after: **869/0, 5 ignored** (cycle review3); `cargo fmt
--check` + `clippy -D warnings` clean; pytest 18 passed / 1 skipped on the
binding rebuilt from this tree; `binding_continuity.py` CONTINUOUS (the
3.0 reference digest `cf0cfede…` reproduced by the rebuilt binding).

| # | finding | verdict | disposition |
|---|---|---|---|
| 1 | `attn.rs:530` pad rule `feats[0] <= 0.0` masks every HEARD kitty row (present 0, ~58 live cells) — attention minds hear nothing; the numpy oracle agreed with the bug | CONFIRMED, defect (mine, T031) | FIXED @ f645286: a token is padding iff its whole row is zero (a heard row always carries a recency > 0 inside the window; silent/vacant rows and absent element slots are all zero as before). Same rule in `numpy_forward_v5.py`; oracle fixture regenerated with eight every-kitty-row-HEARD rows (152 rows, sha `2658886d…`; artifact bytes unchanged). Cycle R1. |
| 2 | FR-023's heading rule never enters the interior of a world wider than ~4r; compiled 32×32 r = 5 fails the 2.x bounds | CONFIRMED (the ruled rule) | OWNER FLAG 1 stands, unchanged. The served world's own reading is finding 3. |
| 3 | the only enforcing welfare gate was retargeted to r = 64; nothing enforces at the shipped radius; stale expect message | CONFIRMED | Message fixed (eaf961e). A gate at r = 5 on the SERVED world was tried (cycle R4) and FAILS the 2.x bounds — 9 violations — by a mechanism that is not coverage (the sunbeam standoff, **OWNER FLAG 10**), so it landed as an ignored READING beside the compiled one (88b3cf7), the same world at r = 64 as its control (1 violation: Clementine's 33-tick streak vs the 20 limit — the served world under global vision was never gated before; a reading for the owner). |
| 4 | `test_config` pins r = 64, so the inherited suite exercises the FogView seam unfogged | ACCEPTED (design) | The inherited assertions prove the seam re-routes without moving what they pinned (the T-baseline doctrine); fog claims live in `fog_*.rs`, `meow_law_fog.rs`, the observe/mask fog tests and `plugin_e2e`. Finding 1 is the review's counter-example; its guard now exists at the parity layer. No change. |
| 5 | `World::generate` never seeds memory: every reset observation is memory-blind; the pytest was re-pointed around it | CONFIRMED, defect (mine) | FIXED @ 18241c2: generation refreshes memory stamped 0 from the stocked world (the tick phase's body with `seen_at = tick + 1`; `update_memories` delegates). Cycle R2. No golden moved; the binding reference reproduces. |
| 6 | `mask_oracle.rs:154`: the message half compares `message_legal` to itself | CONFIRMED, pre-existing (2.x wrote it so) | REPORTED, not fixed (rule 3). The 049 want gate and reply stamp have their own oracles (`meow_law_fog.rs` US4/US7, the mask fog tests). BACKLOG candidate: an independent message oracle. |
| 7 | `a_malformed_v3_header_is_refused_not_panicked_on` vacuous behind the T032 target gate (the hyperparameter guards deletable, test green) | CONFIRMED (mine) | FIXED @ eaf961e: `expand::tests::the_v3_hyperparameter_guard_names_each_refusal` at the guard's own layer; the integration test re-documented as the gate's pin. Mutation R3. |
| 8 | T083 ticked while `cert_harness6.py` keeps `N_ACT 34` / `(225, 50)`: every model-backed seating breaks | CONFIRMED as stated | T083's scope was the all-scripted re-baseline the step-3 doc assigned; `binding_continuity.py` now REFUSES a model-backed seat by name before the first tick (never a wrong-width row). The cert_harness6 cutover is Experiments' housekeeping — OWNER FLAG 8 sharpened to say so. |

Follow-ups from the review: `referent_visible` / `known_relief` `_ => false`
→ exhaustive matches (FIXED); `docs/rl-training.md` `# 34` and `evals/v1`
×2 (FIXED); `groom_response`'s heard-unseen branch returns before the
spec-045 exposure gate → inert at the served default, and the unseen
groomee's bath pressure is masked so any stand-in is a ruling — **OWNER
FLAG 11** (Gen 2 contagion input, with F-035); `snapshot().fog_for` per
emitted message in the enforcement loop and the reply stamp → REPORTED:
bounded by messages per tick (≤ roster), the mid-tick view is the
documented semantics; measure before touching; `blind_price` through
`Position::visible_from` (FIXED); `HERE_KINDS_LEN` derived (FIXED);
Bug/Greeble → `is_critter` (FIXED); `toml` as a core runtime dependency →
ACCEPTED (server and rl already carry toml 0.8; a feature gate is plumbing
for nothing); ARC-TEMPORARY leftovers, two detached doc comments, `let _ =
window` (FIXED). Cleared by the reviewer, nothing to do: retired keys still
refused per section; roster > kitty_slots + 1 refused in the shared loader;
the mid-tick enforcement view only ever silences.

**OWNER FLAG 10 — the sunbeam standoff (served world, r = 5).** Miso,
sleep at the cap, sees ONE sunbeam: adjacent, occupied by Clementine,
cuddle at the cap, who is resting "with" Miso. `sunbeam_worth_walking`
prices the occupied beam cheapest (1 tile); `step_toward` an adjacent
occupied tile has no improving step and yields Idle; Miso proposes Idle
every tick (probed from the proposals). Clementine's partnered rest with
an Idle partner pays only the drip, below her cuddle rise, so she never
leaves. Both paths are 2.x code; fog makes the geometry likelier (one
beam in view, cats cluster round what they know). Held 406 ticks in
20,000 on the served world at r = 5; not seen at r = 64 in 20,000. The
candidate fix — skip beams another cat occupies in
`priced_nearest_element` — was measured and REVERTED: served r = 5 10
violations, the r = 64 control 5 (from 1), the compiled r = 5 reading
unchanged at 13. The Gen 1 welfare bar is the step-5 prereg's; the
standoff itself is a scripted-dynamics ruling.

### Review cycles

| cycle | mutation / red | predicted | observed | restore |
|---|---|---|---|---|
| R1 | oracle fixture gains 8 every-kitty-row-HEARD rows + the numpy pad rule "all zero"; Rust rule unchanged | parity RED (greedy argmax mismatch on the heard rows) | RED at the argmax assertion; GREEN after the attn fix, max abs error ≤ 1e-4 | fix landed (f645286) |
| R2 | `a_generated_world_is_remembered_before_the_first_tick` on the old engine | RED (a slot None while an element is in the disc) | RED (Water at r = 5); GREEN after the fix. The full cycle then read 862/7: five selection stagings, SC-012's blind world and one observe staging carried seeded memory of elements they had stripped → `test_support::forget_everything` at the staging layer (before `setup`); 869/0 | fix landed (18241c2) |
| R3 | `check_v3_hyper`'s positivity guard deleted | unit test RED (`unwrap_err` on Ok); gate test GREEN | exactly that | `git checkout -- crates/`, 0 dirty; unit GREEN |
| R4 | served world at r = 5 held to the 2.x bounds (probe) | unknown | 9 violations (above); control r = 64: 1; the standoff probed and the candidate fix measured (above) | ignored reading landed (88b3cf7); the probe file deleted, the candidate reverted |

Final count after the review: **869 passed / 0 failed / 5 ignored**
(cycle review3, 88b3cf7).

## Phase 8 (US5: scripted cats under the same fog) — cycles 24a–24f

Landing note: the Phase-8 guards caught that the exploration step was
UNREACHABLE — need selection priced an unseen, unremembered kind `None`
and skipped it (the 004 "no path" rule, written under global vision), so
a blind hungry cat slept. `selection::blind_price`: `radius + 1` while
the disc leaves part of the world unseen, `None` at a covering radius
(so FR-024's world-covering identity and the 004 skip doctrine both keep
their proof); cuddle prices visible ∪ heard (the walk's candidate).
Second slip: the blind-price unit test was committed without a green run
(the filter missed its module); its arithmetic was wrong, fixed @ 8bf7ec6.

OWNER FLAG (FR-023 / SC-012): the ruled redraw rule (turn when the wall
ahead ≤ radius) never brings the disc over the ten tiles per corner
farther than r from the inner square — 40 of 400 tiles at 20×20, r = 5.
A bowl there is found only by the safeguard. Pinned by
`the_corner_pockets_are_outside_the_sweep`; SC-012 (worst 36 ticks over
24 seeds) is stated over the sweepable tiles.

| cycle | mutation | predicted red | observed | restore |
|---|---|---|---|---|
| 24a | explore redraws every tick | scenario-6 holds/zero-draw test, first-heading draw count, SC-012 | RED 5: scenario 6, blind-hungry (redraw at tick 1), SC-012, the blind-price test (then wrong, see 8bf7ec6), `voluntary_swimming…` at the r = 5 dial (exploration variants reach bath distress in the flooded world) | 857/5 → clean 0 dirty |
| 24b | the reverse allowed in both pools | boxed-in never-reverses, scenario 6, SC-012 | RED 5: as predicted + the (then wrong) blind-price test + `voluntary_swimming…` r = 5 | 857/5 → clean |
| 24c | heard candidates dropped | heard-friend cuddle, playful heard-only scan | RED 3: both + the (then wrong) blind-price test | 859/3 → clean |
| 24d | Friend arm keeps busy/asleep friends | arrived-asleep assertion | RED 5: it + BOTH goldens + wire golden + `world_covering_radius_reproduces_pre_fog_actions` — the idle filter is load-bearing in the pre-fog stream | 857/5 → clean |
| 24e | blind price → `None` (the pre-fix engine) | blind-hungry, refuted-memory explore, SC-012, blind-price test | RED 4: exactly those | 858/4 → clean |
| 24f | blind price without the covering gate | blind-price test; fog_continuity predicted GREEN (served minimums keep every kind visible at r = 40) | RED 2: the test + `an_unrelievable_need_is_skipped_not_priced` (004 doctrine); continuity GREEN as predicted | 860/2 → clean |

Phase-8 checkpoint: **862/0, 3 ignored** (861 + the arithmetic-fixed
blind-price test), fmt + clippy clean. T060's 20k reading lives in
`crates/cloudkitty-rl/tests/welfare_longrun.rs` (beside the 2.x bounds
run it mirrors; ignored, prints, asserts invariants only) — the task
named the core file, whose doc says the 20k run moved to rl at spec 014.

## Phase 9 (US8: the scripted reply ladder) — cycles 25a–25e

Order kept: T065's fixtures (`preladder-r5-20k.{actions,messages}.digest`)
were recorded and committed @ f34ecf7 BEFORE the ladder landed @ a90f2fe.
The Phase-9 landing suite read **871/0, 4 ignored** (the commit message
says 870 — a miscount, the log says 871). Scenario 8 (ambient here
stamped reply 1) is the engine stamp's own guard in `meow_law_fog.rs`,
not duplicated. `NeedsDriven::decide_action` opened to the crate for the
sibling module's tests.

| cycle | mutation | predicted red | observed | restore |
|---|---|---|---|---|
| 25a | the LOWEST intensity answered (`max_by` → `min_by`) | loudest-want test | RED 1: exactly it | 870/1 → clean |
| 25b | the floor ignored | at/above-floor test (0.29 answered) | RED 1: exactly it | 870/1 → clean |
| 25c | the here law bypassed (cooldown, referent, flag) | cooling-here test | RED 1: exactly it | 870/1 → clean |
| 25d | replies fire with the floor unset (`?` → `unwrap_or(0.0)`) | floor-unset unit test; SC-011 `reply_floor_unset_is_byte_identical`; possibly goldens | RED 4: both + `world_covering_radius_reproduces_pre_fog_actions` + the 043 `gate_zero_speech_never_moves_action`; goldens GREEN (the golden run's roster does not meet a reply condition) — SC-011 is NOT vacuous: replies fire in the served-roster r = 5 stream | 867/4 → clean |
| 25e | ties go to the own want (`>` → `>=`) | own-need-vs-intensity test (the 45 tie) | RED 1: exactly it | 870/1 → clean |

Phase-9 checkpoint: 871/0, 4 ignored, fmt + clippy clean.

## Phase 10 (US6: the 3.0 config hygiene) — rule-6 sort BEFORE the landing

Landing = T068 (13 top-level + 3 nested-TABLE section-absence shims deleted;
`kitties` keeps only its rename) + T069 (seven retired `Option` fields,
their rejectors and four rejector tests deleted; `deny_unknown_fields`
refuses the keys) + T071 (`Meow.intensity` default deleted).

DEVIATION (reversible, recorded): `[water] contagion_membership` is a KEY,
not a section; its sibling `contagion_factor` keeps its per-field default
under FR-030's inert-launch-dial clause and the 039-D5 stamp discipline
(skipped at `option_a`), so the membership key keeps its default too. The
three nested TABLE shims (`happiness.weights`, `actions.durations`,
`meow.vocabulary`) are deleted.

Must-fail pile (predicted RED, then re-pointed or deleted):
- the four rejector tests — OBSERVED RED first (rejectors deleted, fields
  kept: 4 failed / 1 passed in the `retired` filter), then deleted
- `purr_table_defaults_when_absent_and_rejects_bad_bounds`,
  `water_section_defaults_when_absent_and_old_configs_keep_parsing` (the
  section-absence subject itself → their inverse is `missing_section_is_named`)
- the "old-shape / durationless [actions] parses" pair (2677, 2751) — the
  `durations` table is now required
- `the_rl_and_plugins_tables_belong_to_other_parsers_and_still_load`,
  the `[vision]` trio (3353–3375 "with" arm), the contagion absent/explicit
  quartet (3060–3164), the three misspelt/wrong-table/invented-section
  guards (2851–2867) — partial literals → completed with
  `test_support::complete_toml` (parser tests keep raw text)
- other crates' partial literals (server lib.rs, policy tests,
  waterline_contagion, rl config/eval_suite) — expect RED, complete them
Must-pass pile: every test that already loads a full config or a
sub-struct whose fields carry per-field defaults (PurrConfig from "",
MeowConfig dials) — MeowConfig-from-fragment tests will go RED on the
now-required `vocabulary` table and are re-pointed by adding it.

### Phase 10 — observed after the landing (@ 2f87357) and cycles 26a–26c

Observed red after the landing (13 config unit tests): the predicted set,
except `purr_table_defaults_when_absent…` stayed GREEN (it parses the
`PurrConfig` sub-struct from "", whose fields carry per-field defaults —
a key-default subject, kept) and the three misspelt/wrong-table/invented-
section guards stayed GREEN (the unknown-field error surfaces first).
Two tests deleted as the section-absence subject (`a_toml_without_durations…`,
`water_section_defaults_when_absent…`), the vocabulary test inverted, the
vision test rebuilt from the full defaults, nine completed. Other crates:
14 red (server policy/integration fixtures, rl config + suite fixtures),
all partial literals, completed with `complete_toml`. `--check` clean over
52 in-scope TOMLs; nested tables complete. No separate "nan table" test
exists — the finiteness table lives in `validate_actions` and the two
shipped-config sweeps exercise it (T074).

| cycle | mutation | predicted red | observed | restore |
|---|---|---|---|---|
| 26a | `#[serde(default)]` back on `[water]` | `missing_section_is_named` | RED 1: exactly it | 866/1 → clean |
| 26b | `[purr] cooldown_ticks: Option<u64>` re-admitted (first attempt did not compile — the Default arm; re-run compiling) | `retired_key_is_unknown` | RED 1: exactly it | 866/1 → clean |
| 26c | `Meow.intensity` serde default back | `a_pre_3_0_meow_entry_is_refused` | RED 1: exactly it | 866/1 → clean |

Phase-10 checkpoint: **867/0, 4 ignored** (871 − 6 deleted + 2 inverse
guards), fmt + clippy clean.

## Phase 11 — T077 merge, the T080 flip and its predicted reds (written BEFORE the run)

T077: `origin/main` merged IN @ c2b2bc1 (three docs commits: the step-5
training pass, the shakeout PREREG draft, the radius-set ruling); suite
after the merge **867/0, 4 ignored**.

T060 reading BEFORE the flip (rl `fog_r5_twenty_thousand_ticks_welfare_reading`,
compiled 32×32 world, all scripted, r = 5): means 77.6 / 69.3 / 77.9,
below-45 shares 4.3 / 4.7 / 2.6 % (streaks 106 / 186 / 103), max distress
age **3,477** ticks; 13 violations of the 2.x bounds. Census: eat distress
4,033 / 3,533 / 3,746 ticks in 3 / 7 / 7 episodes; sleep pinned streaks
326 / 396 / 246. **OWNER FLAG (mechanism)**: the ruled FR-023 heading rule
("redraw when the wall ahead ≤ r") walks the inner square `[r, w−1−r]²`
and never leaves its band, so on a world wider than ~4r the centre (a
10×10 core at 32×32, r = 5) and the corner pockets are never inside any
disc; the safeguard is existence-based (FR-047) and never puts food in
view; a blind cat can starve for thousands of ticks. On the served 20×20
world the band covers everything but the 40 pocket tiles (SC-012 holds,
worst 36 ticks). Decision for the arc (reversible, hers to overrule): the
compiled default flips to 5 as the contract says; the rl welfare GATE pins
radius 64 (its bounds are global-vision bounds) and the r = 5 READING
stays beside it, ignored, for the prereg.

T080 landed: 53 TOMLs `radius = 5` (served, training, tiny-world, spec-004,
43 exp-006, evals/v2 ×7 re-hashed, config-3.0-defaults); compiled default
5; `test_support::test_config` pins 64 (its 16×16 stage was written under
global vision); rl welfare gate pins 64; water_safeguard dial table keeps a
64 entry beside the default.

Predicted RED after the flip (the T081 set): `golden_evolution_flag_absent_10k_ticks`,
`golden_strip_witness_refusal_ring_is_the_only_delta` (core goldens on the
served config), `run_json_wire_shape_matches_the_golden` (rl run-json
golden). Predicted GREEN: fog_continuity (forces 40), determinism, joint-
action parity (both drivers at the same radius), snapshot_resume (explicit
r 8), mask_oracle (explicit radii), SC-012 / the same-fog witness (explicit
5), pytest (shapes unchanged).

### T080 observed, T078 stamp proof, T083 record

Observed after the flip: **7 red** — the 3 predicted goldens + 4
unpredicted, each a global-vision doctrine test that ran on
`Config::default()`:
- `default_ring_covers_the_baseline_window_under_absorbed_load`: at r = 5,
  20,000 ticks do NOT saturate the 6,000 ring (fewer refusals under fog) →
  the window measure is vacuous there; pinned at 64, the fog-era refusal
  density noted as the refusal baseline's re-run item.
- `gate_zero_speech_never_moves_action` (043): projections diverge at tick
  119 — a Here* word from an unseen friend is a heard target under FR-022
  (owner ruled). Pinned at 64; **OWNER FLAG**: 043's gate-zero doctrine
  and 049's hearing are in tension by design under fog.
- `the_mask_is_a_pure_oracle_and_never_all_zero`,
  `a_default_population_critter_cluster_keeps_an_ongoing_play_expressible`
  (rl mask_oracle): `Chase(Kitty 9)` fog-silenced for kitty 3 with kitty 9
  outside its disc while the engine accepts — the documented fog exception,
  proved by the fog guard in the same file; both pinned at 64.
No test weakened: each pin keeps the claim at the radius it was made under.

T078 (R13, `[stamp]`): `stamp-after/{core,rl}-defaults.json` dumped from
`Config::default()` / `RlConfig::default()` after the flip and diffed
key-by-key against T003's capture: core **added** exactly
`vision.radius`, `vision.memory_timeout_ticks`, `meow.digest_window_ticks`;
rl **changed** exactly `observation.kitty_slots` 3 → 4; nothing removed,
nothing else changed; `[behavior] reply_intensity_floor` absent (skipped
at None) as predicted. `engine_defaults_sha256()` before
`6c73f894…f07687` → after `babc2c5417e6143ebd1f7805c103fcbed7557a4b3730d7c43af7356a5aa22c18`.
The stamp test pins no hex (shape/stability/sensitivity), so nothing to
re-point.

T083 (SC-009): `binding_continuity.py` could not run an all-scripted
seating (it called the `None` model) and sliced masks with cert_harness6's
2.x literals (menu 34 of 39); as the cutover housekeeping the wall PR owns
it now derives the head split from the binding's mask width and skips
model-less seats (cert_harness6 untouched). Reference record:
`specs/049-fog-gen1/binding-continuity/reference-3.0-val-scripted.json`
(served config, `val-scripted`, seed 870001, 2,000 ticks, digest
`cf0cfede…`); the plain run reproduces it byte for byte. Note: the
seating's "scripted" seats are zero-logit first-legal-pair seats (the 2.x
instrument's own convention), a continuity trace, not a welfare measure.

### T081 observed, T082, T084, T085 — the arc's close

T081: after the four pins the flip's red set was exactly the predicted
three goldens; regenerated ONCE from one run: evolution `eaba8138…`, strip
pin `0bbb577f…`, rl run-json golden (`UPDATE_GOLDENS=1`), doctrine
paragraphs in each file. Suite after: **867/0, 4 ignored**; clippy
`-D warnings` clean; `cargo fmt --check` clean.

T082: CHANGELOG Unreleased carries the 3.0 wall entry with
`[obs-schema] [world-fresh] [stamp] [rng-sequence]` — the fourth marker by
the 048 precedent (consequence: the pre-fog action stream is reproduced
only up to the first widened groom response, tick 549, and every seeded
evolution diverges under fog). Never tagged here.

T084: `cargo fmt --all -- --check` OK; `cargo clippy --workspace
--all-targets -- -D warnings` OK; `maturin develop --release` + `pytest`
in the scratch venv (python 3.14): 18 passed, 1 skipped (PettingZoo
conformance without gymnasium, as CI) after one re-point —
`test_unseeded_reset_gives_fresh_reproducible_episodes` compared reset
OBSERVATIONS, which under fog are byte-identical across seeds (an empty
first view); it now compares the global state, the subject unchanged.

T085: quickstart §1–§12 walked top to bottom; every engine section green;
seven command lines named tests by stale names / a missing `--dry-run`
flag and were corrected in place (the guide describes what exists). The
standing-reds ledger is empty. Final COUNT READ recorded below at the
last commit.

### Final COUNT READ (T085)

At `45c1582` (the last engine/test commit): `cargo test --workspace
--no-fail-fast` = **867 passed, 0 failed, 4 ignored** (the four ignored:
the two stream recorders, the r = 5 welfare reading, one pre-existing).
Baseline at the branch base was 818; the difference is the new guards
this file enumerates phase by phase, minus the deletions it records
(schema-4 pins, the spec-035 map tests, the section-absence and rejector
tests, the two fixture-loading resume tests). fmt --check, clippy
`-D warnings`, pytest 18/1 skipped. Binding-continuity reference re-taken
at the clean `45c1582` (digest unchanged, `cf0cfede…`).

## Phase 12 (convergence) — T087: the FR-036 social clause, SC-004 split, the groom-response rules

Owner ruled 2026-09-03 (four rulings, hashed out with Experiments over the
measurements below; relayed by Experiments and confirmed by the owner in
the Product session): (1) `want_bath` armed-only — an ASK, no top-need
clause, no idle-friend gate; cuddle and play as ruled; (2) SC-004 split
into 4a (plumbing, byte-identical under a test-side pre-fog law switch)
and 4b (the named-cause law); (3) the groom response acts only on an ask
aged ≤ cooldown, inclusive (2.x-matching; audibility stays the digest
window); (4) on sight it declines a caller whose bath is below the
announce threshold. Mechanism for 4a: `MeowConfig.want_law: WantLaw
{Fog, PreFog}`, `#[serde(skip)]` (no TOML sets it, the stamp does not
carry it), read by the want tier and the rung's on-sight rule.

Measurements behind the rulings (served roster, all `needs_driven`, one
seed, 20,000 ticks; "dirty" = target bath ≥ announce_threshold 30 at
scene start; `groom_cuddle_relief` = the served 2.0, the #332 bump):

| law | rung as landed, r=40 | with rules 3+4, r=40 | rung as landed, r=5 | with rules 3+4, r=5 |
|---|---|---|---|---|
| pre-fog armed-only | 2.35 dirty / 24.25 clean, simul 13.45 | 2.00 / 0.00, simul 0.30 | 3.80 / 30.85, simul 18.05 | 3.70 / 0.00, simul 0.50 |
| FR-036 as first landed | 0.10 / 0.25 | 0.00 / 0.00 | 0.50 / 7.70, simul 4.20 | 0.25 / 0.00 |
| bath armed-only | 2.80 / 23.95, simul 14.15 | 3.10 / 0.00, simul 0.70 | 2.40 / 22.00, simul 15.35 | 4.80 / 0.00, simul 0.85 |

(grooms per 1k ticks; "simul" = ticks per 1k with two groomers on one
cat.) ~90% of the 2.x partnered grooms started on an already-clean cat
(the first responder cleans the caller in a few ticks and the same ask
keeps drawing groomers for the rest of the window); rules 3+4 remove the
clean-target grooms and the pile-on at every radius and law; on the dirty
number the first-landed law killed the social groom (0.0–0.25/1k) and
armed-only restores it at or above the pre-fog rate. `want_bath` volume
4.8 → 4.9/1k at r=40 under the rules (no spam). Probe of the tick-559
pile-on: a second responder's `Groom{target}` is APPLIED (validation is
adjacency-only by the 041 design), never refused — so it never reaches
T093's `reason`.

| cycle | guard / mutation | predicted | observed | restore |
|---|---|---|---|---|
| R5 | six guards written before the engine moved: `want_bath_is_armed_only…`, the SC-010 property re-pointed (bath armed-only), groom-response freshness (age 11 and 25 declined, 10 answered), on-sight decline (bath 10 declined, 60 groomed), SC-004a under `PreFog`, SC-004b with the named-cause classifier | all six RED | all six RED exactly (4a diverged at 549 with the switch unwired; 4b's 549 unexplained) | — |
| R6 | the law + the two rules landed | six GREEN; 4a full 20k identity uncertain (stop and report if not) | 4a GREEN — actions AND messages byte-identical over all 20,000 ticks under `PreFog` (the plumbing proof now lives on the engine); 4b RED at tick 550: the pre-fog cats WALK toward a clean caller (`Mn` vs `Me` for kitties 2 and 5), the classifier named only the groom | classifier widened to the errand (walk or groom) toward a fresh ask from a clean caller — 4b GREEN, first divergence tick 550, exemption set 38/72 pre-fog rows silenced (cuddle 13, drink 6, eat 19), 1 freed |
| R7 | full cycle t087a | goldens ×2 RED, SC-011 preladder RED, stagings unknown | 867/5: the two goldens, SC-011, and two groom stagings (a caller staged at bath 0 / 10 is now declined on sight) | stagings re-pointed (caller bath 40; the 045 test announces at 10 so its bath-10 arithmetic stands), goldens re-pinned ONCE (evolution `14b946af…`, strip `408dc1a7…`), preladder r=5 streams re-recorded (the SC-011 identity was proven at a90f2fe; the fixture now pins the ruled floor-unset streams) |
| R8 | full cycle t087b | 872/0/5, fmt + clippy clean | 872/0/5, fmt clean, clippy RED on a dead test helper (`config_digest_window`, orphaned by the classifier rewrite) → deleted; pytest 18/1 on the rebuilt binding; binding continuity CONTINUOUS (`cf0cfede…` reproduced — the val-scripted seats are first-legal-pair seats, untouched by the bath clause) | — |

Landed: `meow.rs` (two word classes; `known_relief(WantBath)` = false, the
arm kept for exhaustiveness), `needs_driven.rs::groom_response` (freshness
+ on-sight; `PreFog` keeps the 2.x rung), `config/mod.rs` (`WantLaw`),
`fog_continuity.rs` (SC-004a + SC-004b, the clean-set stream), spec FR-022
/ FR-024 / FR-036 / SC-004a-b / US5-4 / key entity / edge case / a
Clarifications session, `docs/meows.md`, `contracts/meow-law-v5.md`,
CHANGELOG. Final count after T087: **872 passed / 0 failed / 5 ignored**.

### T089 / T091 (owner ruled 2026-09-03, no engine change)

T089: generation-time memory seeding KEPT — recorded in data-model.md
(memory entity) and docs/encodings.md (self-memory row). T091: the served
seats are `needs_driven` for every cat but Biscuit, who sits on the new
`playful` (the 3.0 anchor) — `cloudkitty.toml` updated, CHANGELOG line
amended; every served-config consumer green (server 40+3+4+4+1, core
shipped_configs 18, rl shipped/eval/harness 16+10+1).

### T088 — the lattice serpentine tour (owner ruled 2026-09-03 in the Experiments session, confirmed here)

The heading rule's coverage was a function of r versus world size (single
loop at threshold t = r: 20×20 unswept 40/36/56 tiles at r = 5/4/6; 32×32
the whole 10×10 core; computed table in the scratchpad `sweep_geometry.py`
run), which would have made the step-5 radius screen measure the sweep
instead of vision. Replaced by `crate::explore::Lattice`: waypoints inset
floor(r/√2), spacing ≤ floor(r√2), boustrophedon and back (cycle 2N−2, no
crossing legs); one engine-owned index per cat `explore_waypoint` (u32,
set at generation to id mod cycle, advanced in the environment phase on
reach or beside a held waypoint), no RNG draw; `explore_heading` deleted
(nothing else read it; the wire/API field is now `explore_waypoint`).

| cycle | guard / mutation | predicted | observed | restore |
|---|---|---|---|---|
| R9 | `explore::tests::coverage_is_complete_by_construction` (every tile of 8 world shapes × r = 2..8 inside some waypoint's disc); mutation: inset = r (the old rule's wall distance) | RED at the first corner | RED: 20×20 r=2 tile (0,0) outside every disc | inset restored (the file was untracked: restored by sed, verified by grep) |
| R10 | field swap + engine + behaviour + 20 sites; full cycle t088a | goldens ×2, preladder, run-json golden RED; others unknown | 868/7: the four predicted + the ladder test that pinned the heading (re-pointed to a waypoint), the spec-004 archived snapshot (`explore_heading` → `explore_waypoint: 0` in the fixture) | goldens re-pinned ONCE (evolution `f2dc24d9…`, strip `dc480760…`), preladder r=5 streams re-recorded, run-json golden regenerated |
| R11 | SC-012 over every tile (399 trials: every non-visible tile once, the corners and (16,10) from all 16 indices) | within the computed bound 144 | worst 108 (bowl at (19,19) from index 10), median 28, mean 35 | bound pinned as the tour cycle + approach; the measurement printed |
| R12 | full cycle t088b | 875/0/5 | 875/0/5; fmt clean; clippy one `is_multiple_of` lint → fixed, clean; pytest 18/1 on the rebuilt binding; binding continuity CONTINUOUS | — |

Welfare readings after T087 + T088 (ignored tests, for the owner and the
prereg): compiled 32×32 r=5: **1 violation** (Miso's 48-tick streak; was 13
with a 3,477-tick distress — the coverage failure is gone, max distress
age 103). Served 20×20 r=5: 6 violations (was 9) — Miso streak 124,
Clementine streak 201 + 1.0% share, distress age 369, sleep pinned 238 /
cuddle pinned 288: the sunbeam standoff (T092). Served r=64 control: 5
violations (was 1 before T087): the same standoff now arises at global
vision too (sleep pinned 202 / cuddle 119, Clementine 174 + 1.2%) — the
groom rules changed the served world's cuddle economy enough to expose it;
T092 is the fix on both.

### T090 (owner ruled 2026-09-04, no engine change)

The blind price ratified as implemented; the doctrine sentence (a need is priced at the cheapest walk the cat's knowledge cannot exclude; r + 1 is the exact greatest lower bound of Manhattan travel outside a Euclidean disc; covering radius → `None`) recorded in research.md R9 and docs/meows.md, with the two notes (memory beats the bound; sensitivity `tile_cost × (r + 1)`).

### T092 — the sunbeam standoff (owner ruled 2026-09-03; picks confirmed 2026-09-04)

Picks: a SETTLED occupant (resting/asleep) on a beam beside the cat →
cosleep at cost 0 (`needs_driven::warm_friend_beside`, shared by the arm
and `sleep_travel_distance`); an AWAKE occupant → the beam is excluded
from `priced_nearest_element(Sunbeam)` and the cat naps on the spot
(beside the friend, the nap rung's old behaviour) rather than wait; both
gated under `LawEra::Fog` (`WantLaw` renamed `LawEra`: it now holds the
whole 2.x scripted package for SC-004a's replay).

| cycle | guard / mutation | predicted | observed | restore |
|---|---|---|---|---|
| R13 | `a_sleeper_naps_beside_a_settled_friend_on_a_beam_instead_of_waiting` (settled → `Sleep{with: 2}` and travel 0; awake → a `Sleep`, travel 0; `PreFog` → not the cosleep) | RED (Idle, travel 1) | RED exactly (Idle) | rule landed → GREEN |
| R14 | SC-004a/4b after the rule | 4a GREEN; 4b RED until the T092 cause is named | 4a byte-identical over 20k; 4b: first divergence moved to tick 119 (`S5` vs `I`, kitty 2 beside a held beam) — classifier gained cause (ii) (our `S…` where pre-fog `I`/`M…` with a friend on a beam beside the cat), GREEN; `record_streams` now returns a `Streams` struct with the per-tick clean set, beam-blocked set and roster | — |
| R15 | full cycle t092a | goldens ×2 + preladder RED | 873/3 exactly those | goldens re-pinned ONCE (evolution `13d22603…`, strip `6d1acfe0…`), preladder r=5 streams re-recorded |

Welfare readings after T092: **served 20×20 r=5: 0 violations** (was 9 →
6); **served r=64 control: 0** (was 1 → 5 after T087); compiled 32×32 r=5:
4 (Miso/Biscuit/Pumpkin streaks 30/74/29, a distress of 260; was 13 → 1
after T088 — a different seed path on a world that is not the served one;
the coverage failure stays gone). The 2.x welfare bounds hold on the world
that ships, at the radius that ships.

### T093 — `RefusalEvent.reason` (owner ruled 2026-09-03; shape sent to Experiments 2026-09-04, prereg row written against it @ main 844f7f8)

`RefusalReason { PartnerAbsent, PartnerBusy, Other }` (snake_case on the
wire), a REQUIRED field on the event, derived at the stamp site by
`action::refusal_reason` from the same predicates `validate` uses
(kitty-targeted rest/sleep/groom/play: target exists and not adjacent →
absent; adjacent yet refused, i.e. social play at a mid-scene or asleep
friend → busy; everything else → other). `/events/refusal` rows carry it;
README row, api doc, CHANGELOG line.

| cycle | guard / mutation | predicted | observed | restore |
|---|---|---|---|---|
| R16 | `a_refusal_names_absent_busy_or_other` (absent for four targeted kinds two tiles away; busy for play at a mid-scene and at an asleep neighbour; other for a missing/self/element target, an occupied move, a meal, a chase; the three wire names); mutation: the classifier returns Other for every kind | RED on absent + busy | RED | `git checkout` on the COMMITTED file (a first attempt checked out an uncommitted action.rs and wiped the new code — re-applied, then committed BEFORE the mutation), 0 dirty, GREEN |
| R17 | ring-layer pins from real events gained `"reason"` (`other` for the occupied move, `partner_busy` for the play at a sleeping partner); the endpoint test asserts the vocabulary on every row | — | the ring test RED until re-pinned (the field is required); evolution golden RED (the serialized world moved by the ring alone — the strip witness did NOT move) → re-pinned `ae534fd1…` | — |
| R18 | full cycle t093c | 877/0/6 | 877/0/6; fmt + clippy clean; pytest 18/1 on the rebuilt binding; binding continuity CONTINUOUS | — |

Reading (`refusal_reasons.rs`, ignored): served roster all scripted, 20k
ticks, (reason, absorbed) → count. r=5: absent 1,096 taxed / 2,197
absorbed (Rest 2,596, Play 366, Sleep 323, Groom 8); busy 294 / 1,685
(Play 1,979); other 2,152 / 823 (Move 2,437, Eat 538). r=40: absent 1,116
/ 2,236; busy 328 / 1,882; other 2,253 / 821. Experiments' expectation
(scripted partner refusals ≈ 0) does not hold: the cats propose at a
friend adjacent in the start-of-tick snapshot who moved first in the fair
turn order — the same-tick ordering tax, ~4% of decisions, radius-flat
(fog adds nothing to it at these radii). Reported to Experiments as the
calibration number.

## Phase 12 closed — 2026-09-04

T087–T093 all LANDED (T087 at 6895774, T089/T091 c8a3737, T088 5caad4c,
T090 2b0b94d, T092 7bf937f, T093 below). Final count **877 passed / 0
failed / 6 ignored**; fmt + clippy clean; pytest 18/1; binding continuity
CONTINUOUS (`cf0cfede…` reproduced throughout). The served world holds
the 2.x welfare bounds at r = 5 and at global vision. Next: the owner
re-runs `/speckit-converge`, then a high-effort review in another
session; the PR waits on her go.

## Phase 13 (converge rerun 2026-09-04) — text sync only, no engine change

The rerun found no engine gap: three artifact-text findings (tasks
T094–T096, appended at 48b45de). No guard moved and no test reads the
spec, plan or quickstart text, so there is no red-first cycle to record;
the suite count stands at the Phase 12 close (877 / 0 / 6, tree at
ce910c5 + docs).

- **T094** (MEDIUM, contradicts): FR-024(b) and SC-004b still named the
  groom response as the only action cause and tick 550 as the first
  divergence; the guard has named TWO causes since R14 (on-sight decline;
  the T092 warm-beam nap) and the first divergence is tick 119. Spec text
  re-pointed to what the guard asserts.
- **T095** (LOW, unrequested → RATIFIED, owner ruled 2026-09-04
  "Agreed"): `World::generate` runs the reach rule once after seeding the
  tour index, so a cat spawned on its waypoint starts past it. Recorded in
  FR-023, the spec Clarifications, and data-model.md; the pin
  `a_cat_spawned_on_its_waypoint_starts_past_it` was already in place.
- **T096** (LOW, partial): T088/T092 leftovers — quickstart §6 (heading
  bar, 24 seeds, pockets, 13 violations → every-tile trial, bound 144,
  worst 108 / 399, served 0 / compiled 4), data-model's "Explore heading"
  transitions → the waypoint's, plan.md's Storage / Constraints / Article V
  / Project Structure / test-plan row (`explore_heading`, `DecisionRng`
  redraws → `explore_waypoint`, `explore.rs`, no draw).

## Review 2 — `/code-review high 049` (run from the Client thread at the owner's request, 2026-09-04; write-up at the Client scratchpad `review-049-2026-09-04.md`)

Ten findings, read-only from their side; dispositioned here. One engine
change (finding 4, red-first below), five comment/doc fixes, one backlog
entry, two owner calls, one finding corrected.

| # | Finding | Disposition |
|---|---|---|
| 1 | MEDIUM — four `evals/v2` exams carry `kitty_slots` 7/5, so `observation_len` is 590/466 and `policy.rs` refuses a 404-wide artifact at load; `kitty-eval --suite evals/v2 --artifact` dies before a tick on 4 of 6 exams | OWNER FLAG 5 reaffirmed with the concrete failure mode. Not 049's to fix (the exams' rosters are the exam designs); options for the owner post-049: re-cut `scale`/`mixed-roster-*` at roster 5 so a served-width mind sits them, or accept exam-specific minds. Recorded in the PR body. |
| 2 | MEDIUM — the one enforced welfare gate pins r = 64; the r = 5 readings are `#[ignore]`d, so a blind-cat-only regression lands green | OWNER CALL. SC-005 rules the r = 5 welfare a reading, not a gate (the Gen 1 bar is step 5's). Since T092 the SERVED world holds the 2.x bounds at r = 5 AND r = 64 (0 / 0, re-read this sitting, 6.7 s for both runs), so promoting `served_world_fog_r5_welfare_reading_with_global_vision_control` to enforced is cheap and would be a kept-behaviour guard, not a Gen 1 bar. Recommended; needs an SC-005 amendment. The gate's stale comment (13 violations, the heading rule) rewritten to the T088/T092 numbers @ c51189c. |
| 3 | LOW — mid-tick element consumption can un-silence a want; the "only ever silences" comment is false | PARTLY WRONG as stated, comment fixed @ c51189c. The chow example cannot occur: memory covers everything visible at the tick's start (FR-007 refresh at the previous environment phase), and an emptied bowl stays an element until `expire_elements`, so the element clauses only ever silence. The social clause (a friend that entered a scene or left the disc earlier in the apply order) and the top-need clause (own relief) DO move both ways — unobservable for a mask-respecting proposer (a word the mask forbade is never proposed), a downgrade-to-Silent otherwise. The mid-tick seam is the 2.x design (activity, then message, over the live world); no change. |
| 4 | LOW — `referent_visible(HereFood)` reads presence while the adjacency arm reads stocked; mid-tick an emptied bowl makes `here_food` legal via the reply arm and stamped `reply = 1` | REAL; FIXED red-first (cycle hr4 below). The spec's own edge case ("Stocked is struck") assumed the adjacency rule handled the mid-tick empty bowl; the reply arm is a second door. `referent_visible(HereFood)` now requires `servings > 0`. Start-of-tick verdicts unchanged (no snapshot holds an empty bowl), so the mask, goldens and stream pins are unmoved — predicted and observed. |
| 5 | LOW — `mask.rs` doc claims fog verdicts equal the full snapshot's and cites `mask_oracle`, which carves out `unseen_target` | REAL; doc rewritten to what the oracle proves @ c51189c (equal for targets in view; unseen-friend targets fog-silenced; out-of-view counterpart the skipped corner). |
| 6 | LOW — `needs_driven.rs` test comment cites the retired heading draw | REAL; comment rewritten @ c51189c (two contexts kept: they still decouple the calls through any other rung's draw). |
| 7 | LOW — README repo map + "three worlds" name `evals/v1` as the exam room | REAL; → `evals/v2`, v1 named as the 2.x record @ c51189c. |
| 8–10 | LOW efficiency — two whole-world clones per speaking cat per tick (enforcement + reply stamp); ~100 meow-buffer scans per observation; `groom_response` clones the buffer per cat | BACKLOG P2 "Fog hot-loop allocations in the training tick" with the fix shapes and a measure-first bill; the plan's "no per-tick allocation growth beyond the views" goal is cited as the reason it is on record. Not fixed here (unmeasured; small absolute buffers). |

### Cycle hr4 — finding 4, `here_food` referent = stocked bowl

| cycle | guard | prediction | observed | restore | count |
|---|---|---|---|---|---|
| hr4 | `meow::tests::here_food_needs_a_stocked_bowl_in_view` (kitty 2's `want_eat` audible; a bowl in view, not adjacent — the reply arm is the only door; empty then stocked) | RED on the unchanged engine at the first assertion ("an emptied bowl is not food in view"): presence-only reads the empty bowl as the referent, and `here_food` comes out legal | RED exactly there (0 passed / 1 failed) | `referent_visible(HereFood)` → `servings > 0`; targeted GREEN; full suite **878 / 0 / 6** (877 + this guard; every golden, the SC-004a/4b pins, the preladder streams and the mask oracle unmoved, as predicted: those runs never emit a here-word or never meet an empty bowl); fmt + clippy clean | 878 / 0 / 6 |

Checked-and-cleared list from the reviewer (lattice coverage incl. the
narrow-axis collapse, `advance_tours` ordering, `blind_price`'s corner
maximum, `euclid_sq` saturation, `seen_at = tick + 1`, `refusal_reason`
vs `validate`, the 404 sum, `prune_transient` ⊇ audibility, the reply
tie-break, the attention pad rule vs heard rows, `deny_unknown_fields`
everywhere, every swept TOML carrying `[vision]`) — all consistent with
this ledger; nothing to add.
