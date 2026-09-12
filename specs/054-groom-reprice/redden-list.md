# Redden list — spec 054 groom-other reprice

The running rule-5/rule-6 argument for this arc: every assertion added or
re-pointed either began red for its predicted reason (logged here) or is
listed with why not. Mutation cycles run through `scripts/mutate.sh
--expect <prediction>`; no tree edits while it runs; `--no-fail-fast`.

## Cycle 0 — baseline (clean branch @ e6246a7)

`cargo test --workspace --no-fail-fast`: **906 passed, 0 failed,
6 ignored** across 71 suites. All green.

## Rule-6 sort — changed behavior, checks sorted before running

Must go RED (guards of the flat price), each with its predicted reason:

| # | Test | Predicted red reason | Observed |
|---|---|---|---|
| R1 | `config::tests::the_remaining_relief_dials_reject_negative_and_non_finite_values` | the `groom_cuddle_relief` sweep entry poisons a field validation no longer reads — `expect_err` panics ("poison must be rejected") | ✅ RED as predicted: panic "poison must be rejected" at the legacy entry; re-pointed to the three curve dials |
| R2 | `action::…::each_split_dial_moves_only_its_own_site` (case 2) | groomer pay is the curve now: bath-60 target ⇒ delivered 20, x=1, pay 2.0 ⇒ cuddle 48.0, not the flat-15 35.0 — assert `(a_cuddle - 35.0) < 0.01` fails with 48.0 | ✅ RED as predicted: "got 48"; re-pointed to 48.0 |
| R2b | `action::tests::grooming_a_friend_cleans_them_and_comforts_the_groomer` | **missed in the pre-run sort** (rule 6 reporting): same cause as R2 — flat-35 pin vs curve 48 | ✅ RED for R2's exact reason; re-pointed to 48.0 |
| R2c | `action::…::cosleep_dials_never_touch_the_duet_or_the_groomer` | **missed in the pre-run sort**: same cause as R2 ("paid by cuddle_relief" 35-pin) | ✅ RED for R2's exact reason ("got 48"); re-pointed to 48.0 + curve wording |
| R3 | `needs_driven::tests::a_wet_groomer_declines_only_a_net_negative_groom` (generous case) | the seam no longer reads the flat dial: cranking legacy `groom_cuddle_relief` to 130 moves nothing, scene value stays 10 + c(0.5)=2.0 = 12 < exposure 120, decline stands — `assert_eq!(Groom)` fails | ✅ RED as predicted (left: Drink, right: Groom); generous case re-pointed to crank slope 260 / ceiling 130 ⇒ value 140 > 120, proposes again |
| R4 | `settings::tests::the_key_names_are_pinned` | golden list gains 3 dial names, loses 1 flat name (19 → 21) | ✅ RED as predicted (golden diff = exactly −1 flat +3 dials); golden updated |
| R5 | `settings::tests::no_config_file_means_every_source_is_default` | `entries.len()` 18 → 20 | ✅ RED as predicted (left: 20, right: 18); re-pointed |
| R6 | `settings::tests::a_minimal_config_plus_one_written_key_sources_exactly_that_key` | the written-at-default key it plants is the retired flat key — no such entry to source | ✅ RED as predicted; plants `groom_cuddle_floor` at its default now |
| R7 | `settings::tests::render_text_follows_the_line_grammar` | the `actions.groom_cuddle_relief = ` line no longer renders — `.find()` unwrap panics | ✅ RED as predicted; finds `groom_cuddle_floor` line now |
| R8 | `settings::tests::f32_dials_print_as_written` | the flat-dial line assertion fails (entry gone) | ✅ RED as predicted; pins `actions.groom_cuddle_floor = 0.5 (default: 0.25) [default]` |
| R9 | `server_integration::settings_endpoint_lists_every_key_on_a_minimal_config` | `actions.groom_cuddle_relief` missing from wanted list | ✅ RED as predicted; wanted list carries the three dials |
| R10 | `shipped_configs::the_served_cuddle_riders_are_partial_and_tier_ordered` | goes red when T019 scrubs the served toml: parsed `groom_cuddle_relief` falls to the serde default (0.0), the exact 2.0 pin fails | ✅ RED as predicted ("groom_cuddle_relief is 0"); replaced with scrub guard + curve-defaults pins + the groom charm-floor rider row (discharges the handoff's restore note) |

### World-evolution goldens (intentional dynamics move — not in the spec's SC-001 enumeration, reported per rule 6/3)

The reprice changes scripted world dynamics, so the four evolution
witnesses went red — their own doctrine (in-file) is "an intentional
change regenerates the golden in the same PR with the justification
alongside":

| # | Witness | Red observed | Disposition |
|---|---|---|---|
| G1 | `evolution_golden::golden_evolution_flag_absent_10k_ticks` | digest a5091adf… → a3fd38e5… | re-pinned, history note in-file (first kitty-directed groom at tick 119 on the default seed) |
| G2 | `evolution_golden::golden_strip_witness_refusal_ring_is_the_only_delta` | strip pin 7918bb21… → 3c4e86cd… | re-pinned from the same run as G1 |
| G3 | `fog_continuity::world_covering_radius_under_the_pre_fog_law_is_byte_identical` | first action divergence tick 562 (downstream of the tick-550 `G4` groom scene; first groom tick 119) | prefog fixtures re-recorded; the recorder body aligned with the post-T087 practice (it still carried its branch-base form — records the SC-004a control config now) |
| G4 | `fog_continuity::reply_floor_unset_is_byte_identical` | first action divergence tick 1,436 (a cat rests with a friend where it walked west — repriced cuddle pressure's first visible fork) | preladder fixtures re-recorded with justification note |

CHANGELOG carries `[stamp]` + `[rng-sequence]` (by consequence — the
spec-048 owner precedent).

**Cycle-1 note**: a fifth red appeared mid-Phase-2
(`config::tests::default_ring_covers_the_baseline_window_under_absorbed_load`,
window 14,832 < 15,000) while the Default impl carried the inert 0.0 but
`action.rs` still read the flat field — i.e. groomers paid NOTHING. It
went green the moment T008 wired the curve; no dial moved. Recorded here
so nobody chases it.

Must stay GREEN (kept behavior, re-read before running): groomee bath
relief (case-2 target side), solo groom (no cuddle pay), cosleep tiers
(`each_split_dial…` case 1; cosleep tests), rest duet ignores groom dials
(case 3 — re-pointed from the inert legacy key to the curve dials, still
must-pass), `option_a` gate-off seam case, evals/v2 + v3 loading, schema-5
(408-float) assertions.

## Predicted-red ledger (rule 5, one row per new/re-pointed assertion)

| Task | Mutation (`--expect`) | Prediction | Observed |
|---|---|---|---|
| T007 | pending | | |
| T011 | pending | | |
| T014 | pending | | |
| T022 | pending | | |

## Cycle records

(appended as cycles run)
