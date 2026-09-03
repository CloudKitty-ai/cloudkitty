# Contract: 3.0 configuration break — the migration note (spec 049, FR-029–FR-034)

3.0 breaks compatibility with every pre-3.0 configuration, saved world and policy artifact (owner-ruled 2026-08-26; cutover `update.sh --fresh`). This note is the record a maintainer needs to bring a config forward. Historical TOMLs stay valid for their pinned commits (F-028 provenance rides `git checkout`, never HEAD forward-compat).

## New keys (required unless marked optional)

| key | type | served value | note |
|---|---|---|---|
| `[vision] radius` | u32 ≥ 2 | 5 (placeholder; step-5 prereg screens) | vision disc radius for everyone |
| `[vision] memory_timeout_ticks` | u64 | 0 (= never) | element-memory expiry |
| `[meow] digest_window_ticks` | u64, positive multiple of `recent_window_ticks` | 30 | audibility window and rate denominator |
| `[behavior] reply_intensity_floor` | f32 in [0,1], **optional** | absent on the served config (replies off); **0.30 provisional** on the corpus-collection config Experiments cut at step 5 (a commented line in `cloudkitty.toml` records it); revisited at the speaker-floor screen | scripted reply listener floor (T066) |
| `[rl.observation] kitty_slots` | usize | 4 (default moved from 3) | roster ≤ kitty_slots + 1 enforced |

## Sections that are now REQUIRED (absence is a load error naming the section)

Top-level (13): `persistence`, `kitty` (the roster array), `needs`, `happiness`, `thresholds`, `elements`, `actions`, `meow`, `behavior`, `purr`, `water`, `events`, `viewer` — plus the new `vision`. Nested tables (3): `happiness.weights`, `actions.durations` (with its per-activity sub-tables), `meow.vocabulary`. Still optional (foreign tables kept only so `deny_unknown_fields` holds): `rl`, `plugins`, `watchdog`. Per-field defaults on inert launch dials (the stamp discipline) are unchanged — `[water] contagion_factor` AND `[water] contagion_membership` (a key, not a section; the plan's "fourth nested shim" was a miscount, recorded in `redden-list.md` Phase 10) keep their `off` defaults and stay skipped from serialization at those values.

Guards: `config::tests::missing_section_is_named` (every section absent one at a time from the serialised defaults, refused naming it) and `retired_key_is_unknown` (the seven keys below). Test fragments that name only what they are about are completed with `cloudkitty_core::test_support::complete_toml` (a recursive merge over the serialised `Config::default()`); parser tests use raw text.

## Retired keys — no longer known (the seven 2.x parse-then-reject maps)

| key | retired by | 2.x message pointed to | 3.0 |
|---|---|---|---|
| `[purr] cooldown_ticks` | spec 022 | `cooldown_factor_min/max` | unknown key |
| `[meow] cooldown_ticks` | spec 028 | `recent_window_ticks` | unknown key |
| `[meow] urgent_cooldown_ticks` | spec 028 | `recent_window_ticks` | unknown key |
| `[meow] courtesy_ticks` | spec 028 | (courtesy era ended) | unknown key |
| `[meow] urgent_courtesy_ticks` | spec 028 | (courtesy era ended) | unknown key |
| `[meow] urgent_need_threshold` | spec 028 | `announce_threshold` | unknown key |
| `[actions] cuddle_relief` | spec 041 | `rest_cuddle_relief` / `groom_cuddle_relief` (the split) | unknown key |

Not in the set: the spec-025 play-key wording on the live chain link stays.

## Kept

`[elements.<kind>] max` — KEPT (owner 2026-09-02): it sets the density ceiling in validation and the critic's chow-remaining scale; the doc comment at `config/mod.rs` that called it validation-only is corrected in this change.

## Saved worlds

Pre-3.0 snapshots do not load: the seven kitty restore shims, `Pursuit.improved_at`'s default, the eighth shim (`Meow.intensity`'s serde default), the pre-041 duet fixture and the two fixture-loading `snapshot_resume` tests (`a_pre_041_bound_rest_duet_resumes_as_synchronized_resters`, `a_pre_028_world_resumes_and_runs`) are deleted; the pre-028 meow-entry test becomes its inverse (a missing `intensity`, `pos` or `reply` is refused by name). New kitty fields `memory`, `explore_heading`; new meow fields `pos`, `reply`.

## Policy artifacts

Observation schema 5: every schema-4 (and earlier) `.ckpolicy` is refused at load naming the schema. No expansion map across this wall (spec 035's tool keeps its source generation).

## Exams

`evals/v1` → `config-sweep-exclusions.txt` (frozen 2.x record). `evals/v2` = the same six designs as complete 3.0 configs with a new manifest; `kitty-eval --suite` reads v2; the sweeps assert v2 is present.

## Migration count at the step-3 HEAD (2026-09-02)

65 in-scope TOMLs lacked `[water]` (served config included); 8 lacked ten or more sections (`training.toml`, clowder's `tiny-world.toml`, exp-004 pilot/rebaseline families). Live tooling configs are completed in this change (hand edits for the served, training and clowder files; the completion script for generated families); result-backing families join the exclusions file with a reason each.

## Migration record at the step-4 landing (2026-09-03, T072/T075)

- **Tool**: `experiments/tools/complete_config_3.py` (appends every missing top-level table from `experiments/tools/config-3.0-defaults.toml` = the serialised `Config::default()`; `--require` / `--set` for keys; `--check` reports and exits 1). Nested tables under an existing section were appended by hand from the same defaults file.
- **In scope after exclusions**: 52 TOMLs; `--check` is clean and every nested table is present (verified at this landing).
- **Completed in this arc**: 43 exp-006 character-gen TOMLs + `specs/004-fix-happiness-lockin/stuck-state-config.toml` (`[vision]`, `[meow] digest_window_ticks`, the arc-temporary world-covering radius); `evals/v2` cut as complete 3.0 configs (7 files); at the wall landing: `cloudkitty.toml` and `crates/clowder/tests/tiny-world.toml` (+`[water]`), `training.toml` (+10 sections), `tiny-world.toml` and the spec-004 config (+`[meow.vocabulary]`, the spec-004 config also +`[actions.durations.*]`).
- **Excluded**: 18 directories in `config-sweep-exclusions.txt` (9 added at the wall, each with its reason: 2.x records whose bytes must not move).
- **Served values** at the wall: `[vision] radius` is ARC-TEMPORARY world-covering (40 served, 64 compiled) until T080 flips every radius to the 5 placeholder; `memory_timeout_ticks = 0`; `[meow] digest_window_ticks = 30`; `[behavior] reply_intensity_floor` unset (a commented `0.30` line records the provisional corpus-collection value); `[rl.observation] kitty_slots = 4`.
- **Saved worlds**: `Meow.intensity` is required (the eighth shim deleted at T071); the inverse guard names each of `intensity`, `pos`, `reply`.

## Changelog markers

`[obs-schema]` `[world-fresh]` `[stamp]`; `[rng-sequence]` only if SC-004's byte-identity fails at a world-covering radius (not expected).
