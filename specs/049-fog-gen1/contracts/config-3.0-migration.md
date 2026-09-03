# Contract: 3.0 configuration break — the migration note (spec 049, FR-029–FR-034)

3.0 breaks compatibility with every pre-3.0 configuration, saved world and policy artifact (owner-ruled 2026-08-26; cutover `update.sh --fresh`). This note is the record a maintainer needs to bring a config forward. Historical TOMLs stay valid for their pinned commits (F-028 provenance rides `git checkout`, never HEAD forward-compat).

## New keys (required unless marked optional)

| key | type | served value | note |
|---|---|---|---|
| `[vision] radius` | u32 ≥ 2 | 5 (placeholder; step-5 prereg screens) | vision disc radius for everyone |
| `[vision] memory_timeout_ticks` | u64 | 0 (= never) | element-memory expiry |
| `[meow] digest_window_ticks` | u64, positive multiple of `recent_window_ticks` | 30 | audibility window and rate denominator |
| `[behavior] reply_intensity_floor` | f32 in [0,1], **optional** | absent on the served config (replies off); 0.30 on corpus-collection configs | scripted reply listener floor |
| `[rl.observation] kitty_slots` | usize | 4 (default moved from 3) | roster ≤ kitty_slots + 1 enforced |

## Sections that are now REQUIRED (absence is a load error naming the section)

Top-level (13): `persistence`, `kitty` (the roster array), `needs`, `happiness`, `thresholds`, `elements`, `actions`, `meow`, `behavior`, `purr`, `water`, `events`, `viewer` — plus the new `vision`. Nested (4): `happiness.weights`, `actions.durations`, `meow.vocabulary`, `water.contagion_membership`. Still optional (foreign tables kept only so `deny_unknown_fields` holds): `rl`, `plugins`, `watchdog`. Per-field defaults on inert launch dials (the stamp discipline) are unchanged.

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

Pre-3.0 snapshots do not load: the seven kitty restore shims, `Pursuit.improved_at`'s default, the pre-041 duet fixture and both wall-marked `snapshot_resume` tests are deleted. New kitty fields `memory`, `explore_heading`; new meow fields `pos`, `reply`.

## Policy artifacts

Observation schema 5: every schema-4 (and earlier) `.ckpolicy` is refused at load naming the schema. No expansion map across this wall (spec 035's tool keeps its source generation).

## Exams

`evals/v1` → `config-sweep-exclusions.txt` (frozen 2.x record). `evals/v2` = the same six designs as complete 3.0 configs with a new manifest; `kitty-eval --suite` reads v2; the sweeps assert v2 is present.

## Migration count at the step-3 HEAD (2026-09-02)

65 in-scope TOMLs lacked `[water]` (served config included); 8 lacked ten or more sections (`training.toml`, clowder's `tiny-world.toml`, exp-004 pilot/rebaseline families). Live tooling configs are completed in this change (hand edits for the served, training and clowder files; the completion script for generated families); result-backing families join the exclusions file with a reason each.

## Changelog markers

`[obs-schema]` `[world-fresh]` `[stamp]`; `[rng-sequence]` only if SC-004's byte-identity fails at a world-covering radius (not expected).
