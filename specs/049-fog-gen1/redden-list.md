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

(dispositions recorded at T086)

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
