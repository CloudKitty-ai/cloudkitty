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

pub(super) fn default_meow_courtesy_ticks() -> u64 {
    10
}

pub(super) fn default_meow_urgent_courtesy_ticks() -> u64 {
    5
}

pub(super) fn default_meow_urgent_need_threshold() -> f32 {
    75.0
}

pub(super) fn default_meow_recent_window_ticks() -> u64 {
    10
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
