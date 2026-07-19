//! The welfare bounds of spec 004, as permanent regression guards.
//!
//! The 2026-07-18 RCA measured the broken world: low-happiness episodes of
//! 200-500 ticks, every kitty touching the happiness floor, 14-22% of time
//! below happiness 45, needs pinned at the cap for 90+ ticks beside free
//! relief. This test runs the default-shaped world for 20,000 ticks and holds
//! the fixed behavior to the spec's success criteria (SC-001..004), then runs
//! it again from the same seed to prove determinism survived (SC-006).

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::element::ElementType;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{BehaviorRegistry, World};

const TICKS: u64 = 20_000;
const LOW_HAPPINESS: f32 = 45.0;
/// SC-001: no low-happiness stretch may exceed this many consecutive ticks.
const MAX_LOW_STREAK: u64 = 100;
/// SC-002: at most this share of ticks below LOW_HAPPINESS, per kitty.
const MAX_LOW_SHARE: f64 = 0.05;
/// SC-003: no need this close to its cap for more than 25 consecutive ticks
/// while zero-distance relief for it exists.
const NEAR_CAP: f32 = 99.0;
const MAX_PINNED_STREAK: u64 = 25;
/// SC-004: no distress older than this, and mean happiness at least 65.
const MAX_DISTRESS_AGE: u64 = 150;
const MIN_MEAN_HAPPINESS: f32 = 65.0;

/// SC-003's definition of "relief at zero travel distance" for `kind`.
fn zero_distance_relief_exists(world: &World, kitty_idx: usize, kind: NeedKind) -> bool {
    let kitty = &world.kitties[kitty_idx];
    match kind {
        // Grooming and napping happen anywhere; solo play makes play the same.
        NeedKind::Bath | NeedKind::Sleep | NeedKind::Play => true,
        NeedKind::Cuddle => world
            .kitties
            .iter()
            .any(|other| other.id != kitty.id && kitty.pos.is_adjacent(&other.pos)),
        NeedKind::Eat => world
            .elements
            .iter()
            .any(|e| e.element_type() == ElementType::Chow && kitty.pos.is_adjacent(&e.pos)),
        NeedKind::Drink => world
            .elements
            .iter()
            .any(|e| e.element_type() == ElementType::Water && kitty.pos.is_adjacent(&e.pos)),
    }
}

#[tokio::test]
async fn twenty_thousand_ticks_stay_within_the_welfare_bounds() {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let floor = config.happiness.floor;
    let kitty_count = world.kitties.len();

    let mut low_streak = vec![0u64; kitty_count];
    let mut max_low_streak = vec![0u64; kitty_count];
    let mut low_ticks = vec![0u64; kitty_count];
    let mut happiness_sum = vec![0f64; kitty_count];
    let mut floor_touches = vec![0u64; kitty_count];
    let mut max_distress_age = 0u64;
    let mut pinned_streaks: BTreeMap<(usize, NeedKind), u64> = BTreeMap::new();
    let mut max_pinned: BTreeMap<(usize, NeedKind), u64> = BTreeMap::new();

    for _ in 0..TICKS {
        world.tick(&registry, &config).await;

        for idx in 0..kitty_count {
            let kitty = &world.kitties[idx];
            happiness_sum[idx] += kitty.happiness as f64;

            if kitty.happiness <= floor {
                floor_touches[idx] += 1;
            }
            if kitty.happiness < LOW_HAPPINESS {
                low_ticks[idx] += 1;
                low_streak[idx] += 1;
                max_low_streak[idx] = max_low_streak[idx].max(low_streak[idx]);
            } else {
                low_streak[idx] = 0;
            }

            for since in kitty.distress_since.values() {
                max_distress_age = max_distress_age.max(world.tick.saturating_sub(*since));
            }
        }

        // SC-003 needs positions, so it reads the world after the kitty pass.
        for idx in 0..kitty_count {
            for kind in NeedKind::ALL {
                let key = (idx, kind);
                let pinned = world.kitties[idx].needs.get(kind) >= NEAR_CAP
                    && zero_distance_relief_exists(&world, idx, kind);
                let streak = pinned_streaks.entry(key).or_insert(0);
                if pinned {
                    *streak += 1;
                    let best = max_pinned.entry(key).or_insert(0);
                    *best = (*best).max(*streak);
                } else {
                    *streak = 0;
                }
            }
        }
    }

    let names: Vec<_> = world.kitties.iter().map(|k| k.name.clone()).collect();
    for idx in 0..kitty_count {
        let mean = happiness_sum[idx] / TICKS as f64;
        let low_share = low_ticks[idx] as f64 / TICKS as f64;
        println!(
            "{}: mean {:.1}, below-45 {:.1}% (longest streak {}), floor touches {}",
            names[idx],
            mean,
            low_share * 100.0,
            max_low_streak[idx],
            floor_touches[idx],
        );

        assert!(
            max_low_streak[idx] <= MAX_LOW_STREAK,
            "SC-001: {} was below {LOW_HAPPINESS} happiness for {} consecutive ticks (limit {MAX_LOW_STREAK})",
            names[idx],
            max_low_streak[idx]
        );
        assert_eq!(
            floor_touches[idx], 0,
            "SC-002: {} touched the happiness floor",
            names[idx]
        );
        assert!(
            low_share <= MAX_LOW_SHARE,
            "SC-002: {} spent {:.1}% of ticks below {LOW_HAPPINESS} (limit {:.0}%; baseline was 14-22%)",
            names[idx],
            low_share * 100.0,
            MAX_LOW_SHARE * 100.0
        );
        assert!(
            mean >= MIN_MEAN_HAPPINESS as f64,
            "SC-004: {}'s mean happiness {:.1} fell short of {MIN_MEAN_HAPPINESS}",
            names[idx],
            mean
        );
    }

    assert!(
        max_distress_age <= MAX_DISTRESS_AGE,
        "SC-004: a distress went unresolved for {max_distress_age} ticks (limit {MAX_DISTRESS_AGE}; baseline was 216+)"
    );

    for ((idx, kind), streak) in max_pinned {
        assert!(
            streak <= MAX_PINNED_STREAK,
            "SC-003: {}'s {} need sat within 1.0 of the cap for {} consecutive ticks \
             while zero-distance relief existed (limit {MAX_PINNED_STREAK})",
            names[idx],
            kind.as_str(),
            streak
        );
    }
}

#[tokio::test]
async fn the_same_seed_replays_the_same_five_thousand_ticks_exactly() {
    // SC-006. 5,000 ticks is plenty to catch a stray source of nondeterminism
    // without doubling the suite's runtime.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();

    let run = || async {
        let mut world = World::generate(&config);
        for _ in 0..5_000 {
            world.tick(&registry, &config).await;
        }
        serde_json::to_string(&world).expect("worlds serialize")
    };

    let first = run().await;
    let second = run().await;
    assert_eq!(
        first, second,
        "two runs from the same seed and config diverged (Article V)"
    );
}
