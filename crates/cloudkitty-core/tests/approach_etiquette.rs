//! Spec 012: the corner-dance regressions, pinned from the verified
//! 2026-07-20 reproduction. Two kitties approaching each other used to orbit
//! a corner at Manhattan 2 -- each stepping toward where the other just was
//! -- for as long as the urgent-meow lottery stayed quiet (145 ticks in the
//! silenced probe). Approach etiquette resolves the same worlds in a handful
//! of ticks, announced by a "Wait for me!".

use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::grid::Position;
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, World};

fn cuddle_pair_world(config: &Arc<Config>, silence_need_meows: bool) -> World {
    let mut world = World::generate(config);
    for (i, pos) in [(5u32, 5u32), (6, 6)].iter().enumerate() {
        world.kitties[i].pos = Position::new(pos.0, pos.1);
        world.kitties[i].behavior = "needs_driven".into();
        world.kitties[i].needs.add(NeedKind::Cuddle, 90.0);
        if silence_need_meows {
            // Every need meow spent -- the etiquette must not depend on them.
            for kind in [
                MessageKind::WantEat,
                MessageKind::WantDrink,
                MessageKind::WantPlay,
                MessageKind::WantCuddle,
            ] {
                world.kitties[i].set_meow_cooldown(kind, u64::MAX);
            }
        }
    }
    world
}

async fn resolves_into_a_cuddle(mut world: World, config: Arc<Config>, bound: u64) {
    let registry = BehaviorRegistry::with_builtins();
    let mut waited = false;
    for _ in 0..bound {
        world.tick(&registry, &config).await;
        waited |= world
            .recent_meows
            .iter()
            .any(|m| m.kind == MessageKind::WaitForMe);
        let resting = world.kitties.iter().any(|k| {
            matches!(
                k.activity,
                Activity::Resting {
                    with_friend: Some(_)
                }
            )
        });
        if resting {
            assert!(
                waited,
                "the dance should have broken on a \"Wait for me!\", not luck"
            );
            return;
        }
    }
    panic!(
        "no cuddle within {bound} ticks; positions: {:?}",
        world
            .kitties
            .iter()
            .map(|k| (k.name.clone(), k.pos))
            .collect::<Vec<_>>()
    );
}

#[tokio::test]
async fn the_corner_dance_resolves_into_a_cuddle_within_six_ticks() {
    // SC-001: previously 145 ticks with meows silenced, lottery-bound live.
    let config = Arc::new(test_config());
    let world = cuddle_pair_world(&config, false);
    resolves_into_a_cuddle(world, config, 6).await;
}

#[tokio::test]
async fn the_etiquette_works_with_every_need_meow_on_cooldown() {
    // FR-003 via the dedicated word: "Wait for me!" is never spent by other
    // behavior, so the dance breaks identically when the need meows cannot
    // fire.
    let config = Arc::new(test_config());
    let world = cuddle_pair_world(&config, true);
    resolves_into_a_cuddle(world, config, 6).await;
}

#[tokio::test]
async fn a_mutual_play_chase_lands_its_pounce() {
    // The same geometry through the play path: two playful kitties chasing
    // each other must reach orthogonal range and play, not orbit.
    let mut config = test_config();
    for kitty in config.kitties.iter_mut() {
        kitty.behavior = "playful".into();
    }
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    world.elements.clear(); // no critters to steal the game
    for (i, pos) in [(5u32, 5u32), (6, 6)].iter().enumerate() {
        world.kitties[i].pos = Position::new(pos.0, pos.1);
        world.kitties[i].needs.add(NeedKind::Play, 60.0);
    }

    for _ in 0..10 {
        world.tick(&registry, &config).await;
        let playing_together = world.kitties.iter().any(|k| {
            matches!(
                k.activity,
                Activity::Playing {
                    target: Some(cloudkitty_core::action::TargetRef::Kitty { .. })
                }
            )
        });
        if playing_together {
            return;
        }
    }
    panic!(
        "no game within 10 ticks; positions: {:?}",
        world
            .kitties
            .iter()
            .map(|k| (k.name.clone(), k.pos))
            .collect::<Vec<_>>()
    );
}
