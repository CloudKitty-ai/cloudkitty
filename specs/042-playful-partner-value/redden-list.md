# The sorted test list (T003 — rule 6)

Sorted BEFORE running anything. Base: main b48c264 lineage, 62/62
workspace binaries green.

## Must stay GREEN throughout (the headline pile — this feature is a no-op at defaults)

- `golden_evolution_flag_absent_10k_ticks` (pin 7b361b2a) — HALT on red
- `engine_defaults_sha256` unchanged (continuity-baseline.md) — HALT on move
- Full `behavior/selection.rs` battery (`miso_ctx` suite :401+ incl.
  nearest-playmate, viability, exclusion, solo backstop cases)
- Full `behavior/playful.rs` battery (incl.
  `a_playful_cat_chases_a_bug_it_has_no_need_to_chase` — mild hunger
  below comfort stays playful)
- `approach_etiquette.rs`, behavior_variation.rs
- Both shipped-config sweeps (no toml keys added — comments only)
- Stamp tests: `the_engine_defaults_stamp_is_stable_and_well_formed`,
  `any_default_moving_moves_the_stamp` (probes rest_mutual_relief — a
  live dial, untouched here)
- Article I–V property suites; determinism/joint-parity/turn-order

## New guards, red-first (predictions per task; record OBSERVED below)

Commit 1 (config): validation table entries for all 12 dials — red =
compile error on missing fields, then poison-accepted before the
validate.rs entries.

Commit 2 (behavior), per tasks T011–T015 (a)–(l): value ranking (red:
adjacent wins), t_partner (red: friend bothered), t_self (red),
eligibility-filter semantics (red), wait cost (red), busy admission
default pin (green-on-arrival witness), seriousness-excludes-play
(red), standalone appeal (red), busy-adjacent fallback (red), FR-010
re-selection (green-on-arrival pin), FR-008 exclusion-under-score
(red if admission skips is_viable bookkeeping), comfort weights both
directions (red both ways), all-1.0 identity pin + trigger-only pin
(green-on-arrival).

## Coupling watch (observe, don't touch)

- `solo_play_reach` + urgent solo rule in `play_action_with` :344-350
- `should_wait_for` etiquette on chase paths
- opportunism pass (`take_what_is_here` → `adjacent_playmate` :371) —
  pre-existing busy-adjacency semantics, OUT OF SCOPE (rule 3)

## OBSERVED (2026-08-29 — running is not reading)

Commit 1: `the_playful2_dials_reject_negative_and_non_finite_values`
red TWICE as predicted (E0609 missing fields, then "poison must be
rejected" before the validate entries) → green. Stamp compare:
IDENTICAL (6c73f894…) after all 12 fields — skip-at-identity works.

Commit 2, guards (a)–(l): 9 red / 3 green-on-arrival, every one
matching its prediction —
- red: value ranking, t_partner, t_self, filter semantics, wait cost,
  busy admission (w_value>0 half), seriousness-excludes-play,
  standalone appeal, busy-adjacent fallback, FR-010 redirect (its red
  half: the defaults branch), comfort weights both directions,
  trigger-only pin (red until the weighted check existed);
- green-on-arrival pins as designed: identity pick (a), wait-cost
  free-wins (f, busy not yet admitted), exclusion-under-score (l),
  all-1.0 weights identity (c).
- One test-side correction: the US2 `is_serious` heuristic missed
  that a serious BATH cat grooms on the spot (`Action::Groom`) — the
  heuristic was wrong, not the trigger; fixed and both directions
  then behaved exactly as predicted.

Implementation flipped everything in ONE pass: 393→397 core tests
green, zero regressions in the existing selection/playful/etiquette
battery. Golden digest GREEN ×3 after commit 1 and ×3 after commit 2
(never moved — the inert-launch claim held). Workspace 62/62, clippy
clean, both config sweeps green (comments only in the served toml).

Smoke (T025): scripted world with w_value 1.0 / w_busy 2.0 /
t_partner 20 / critter_appeal 5 / eat-weight 1.5 / bath-weight 0.7 —
validated, served, ran ~2,000 ticks at 25ms; playful seat living a
full life (sunbeam co-sleep at sample time), all seats normal.
