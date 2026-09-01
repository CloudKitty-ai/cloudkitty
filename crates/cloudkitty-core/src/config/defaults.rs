//! Default values for every configurable tunable (spec 020 FR-003):
//! the one findable home for what an omitted field becomes. Bodies are
//! unchanged from their pre-split homes beside their structs.

use super::DurationBounds;

pub(super) fn default_purr_min_ticks() -> u64 {
    8
}

pub(super) fn default_purr_max_ticks() -> u64 {
    13
}

pub(super) fn default_purr_cooldown_factor_min() -> f32 {
    1.75
}

pub(super) fn default_purr_cooldown_factor_max() -> f32 {
    2.75
}

pub(super) fn default_purr_announce_probability() -> f32 {
    0.0
}

pub(super) fn default_meow_recent_window_ticks() -> u64 {
    10
}

// Spec 028: the announce band, derived from the needs analysis (2026-08-08)
// -- 30 sits inside every cat's lived range and stays top-1%-informative;
// 5 of hysteresis keeps the mask steady across an errand.
pub(super) fn default_meow_announce_threshold() -> f32 {
    30.0
}

pub(super) fn default_meow_announce_hysteresis() -> f32 {
    5.0
}

// Spec 028: cosleep priced by presence, behavior-preserving at launch --
// both tiers equal the classic cuddle_relief until the pilot re-prices them.
pub(super) fn default_cosleep_relief() -> f32 {
    15.0
}

// Spec 041: the classic shared dial split at its ENGINE-DEFAULT value
// (spec 028's launch pattern). The silent-default edge the cosleep pair
// carries does not exist here: a config still carrying the old
// cuddle_relief key fails validation loudly with the migration map
// (owner's full-compatibility-break ruling, 2026-08-28), so nothing can
// reach these defaults through an unmigrated override.
pub(super) fn default_cuddle_split_relief() -> f32 {
    15.0
}

// Spec 041: rest's drip tier launches at 0.0 so the engine-sibling
// commit is a legality-and-binding change only; the reprice sets it.
pub(super) fn default_rest_drip_relief() -> f32 {
    0.0
}

// Spec 028: what "real cuddle need" means to the scripted responders
// (groom-response and cosleep-routing share the one gate).
pub(super) fn default_cuddle_real_threshold() -> f32 {
    15.0
}

pub(super) fn default_bind() -> String {
    "127.0.0.1:8090".to_string()
}

pub(super) fn default_solo_play_relief() -> f32 {
    10.0
}

// The per-target play values (spec 025): the gradient solo < kitty <
// bug < greeble is what makes "which play" a real decision. Sized by
// the exp-002 chase census (owner-fixed 2026-08-02): greebles are
// 1.5-2.9x harder per catch than bugs and 4x scarcer, so 35 is an
// in-the-moment temptation with no grind exploit, while a duet's team
// total (2 x 20) still beats it.
pub(super) fn default_play_relief_bug() -> f32 {
    25.0
}

pub(super) fn default_play_relief_greeble() -> f32 {
    35.0
}

pub(super) fn default_short_activity() -> DurationBounds {
    DurationBounds::new(2, 5)
}

pub(super) fn default_long_activity() -> DurationBounds {
    // Min raised 2 -> 3 once the 005 animations made durations visible:
    // a nap or cuddle worth watching holds for at least three ticks
    // (owner tuning, 2026-07-20; spec 006 defaults amended in step).
    DurationBounds::new(3, 8)
}

pub(super) fn default_playful_comfort() -> f32 {
    55.0
}

pub(super) fn default_urgency_weight() -> f32 {
    2.0
}

pub(super) fn default_tile_cost() -> f32 {
    1.0
}

pub(super) fn default_water_step_cost() -> f32 {
    4.0
}

pub(super) fn default_spread_candidates() -> usize {
    8
}

pub(super) fn default_ttl_jitter() -> u64 {
    100
}

pub(super) fn default_edge_penalty() -> f32 {
    2.0
}

pub(super) fn default_water_bath_gain() -> f32 {
    3.5
}

pub(super) fn default_water_bath_gain_ceiling() -> f32 {
    60.0
}

pub(super) fn default_worth_a_detour() -> f32 {
    30.0
}

pub(super) fn default_chase_patience_ticks() -> u64 {
    12
}

pub(super) fn default_chase_exclusion_ticks() -> u64 {
    60
}

pub(super) fn default_solo_play_reach() -> u32 {
    8
}

pub(super) fn default_sunbeam_reach() -> u32 {
    8
}

pub(super) fn default_budget_strikes() -> u32 {
    5
}

pub(super) fn default_bench_ticks() -> u64 {
    300
}

pub(super) fn default_reply_max_bytes() -> usize {
    65536
}

pub(super) fn default_relaunch_cooldown_ticks() -> u64 {
    20
}

pub(super) fn default_exchange_timeout_ms() -> u64 {
    1000
}

pub(super) fn default_activity_retention() -> usize {
    1000
}

/// Spec 046 FR-004, re-sized at the review-medium pass (2026-09-01):
/// absorbed refusals share the ring's slots with taxed ones, so the window
/// is set by COMBINED density — measured at ~0.38/tick on the scripted
/// default world (taxed 1,586 / absorbed 2,414 over a saturated ring;
/// see `default_ring_covers_the_baseline_window_under_absorbed_load`).
/// 15,000-tick census window × ~0.38 ≈ 5,760, rounded up. Still a floor:
/// Experiments re-derives the knob by config at the first live baseline.
pub(super) fn default_refusal_retention() -> usize {
    6000
}
