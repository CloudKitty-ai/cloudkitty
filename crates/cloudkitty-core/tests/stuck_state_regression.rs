//! SC-005: the world that motivated spec 004, resumed under the fix.
//!
//! `stuck-state-tick1465.json` is the live snapshot from 2026-07-18: Miso
//! (kitty 1) pinned at bath 100.0 and play 100.0 with sleep oscillating just
//! below the cap, in unresolved play distress since tick 1249, happiness 39.3.
//! The config fixture beside it is a frozen copy of the cloudkitty.toml that
//! world ran under -- deliberately NOT the live repo config, which the
//! operator tunes.

use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{BehaviorRegistry, World};

const SNAPSHOT: &str =
    include_str!("../../../specs/004-fix-happiness-lockin/stuck-state-tick1465.json");
const CONFIG: &str =
    include_str!("../../../specs/004-fix-happiness-lockin/stuck-state-config.toml");

const MISO: u32 = 1;

fn load() -> (World, Arc<Config>) {
    let config: Config = toml::from_str(CONFIG).expect("the frozen config parses");
    config.validate().expect("the frozen config is valid");
    let world: World = serde_json::from_str(SNAPSHOT).expect("the archived snapshot parses");
    assert_eq!(
        world.config_fingerprint,
        config.fingerprint(),
        "the frozen config must be the one the stuck world ran under"
    );
    assert_eq!(world.tick, 1465);
    (world, Arc::new(config))
}

#[tokio::test]
async fn the_stuck_kitty_unpins_and_recovers() {
    let (mut world, config) = load();
    let registry = BehaviorRegistry::with_builtins();

    let miso = world.kitty(MISO).expect("Miso is in the archive");
    assert_eq!(
        miso.needs.get(NeedKind::Bath),
        100.0,
        "the fixture is the stuck one"
    );
    assert!(miso.needs.get(NeedKind::Play) >= 100.0 - f32::EPSILON);
    assert!(miso.happiness < 40.0);

    let mut min_bath = f32::MAX;
    let mut min_sleep = f32::MAX;
    let mut recovered_at = None;

    for step in 1..=300u64 {
        world.tick(&registry, &config).await;
        let miso = world.kitty(MISO).unwrap();
        if step <= 25 {
            min_bath = min_bath.min(miso.needs.get(NeedKind::Bath));
            min_sleep = min_sleep.min(miso.needs.get(NeedKind::Sleep));
        }
        if recovered_at.is_none() && miso.happiness > 60.0 {
            recovered_at = Some(step);
        }
    }

    // The zero-distance needs must unpin almost immediately -- this is the
    // relief that must never wait on play luck.
    assert!(
        min_bath < 80.0,
        "bath never unpinned in the first 25 ticks (min {min_bath}); the lock is back"
    );
    assert!(
        min_sleep < 95.0,
        "sleep never got a real nap in the first 25 ticks (min {min_sleep})"
    );
    assert!(
        recovered_at.is_some(),
        "Miso's happiness never exceeded 60 within 300 ticks of the resume (SC-005)"
    );
    println!(
        "recovered past 60 happiness after {} ticks; first-25 minima: bath {:.1}, sleep {:.1}",
        recovered_at.unwrap(),
        min_bath,
        min_sleep
    );
}

#[tokio::test]
async fn solo_play_carries_the_play_need_down_even_with_critters_far_away() {
    // The "no lucky spawn" variant: every critter is moved to the far corner,
    // well past solo_play_reach from Miso at (21,30), and the other kitties
    // already sit ~16 tiles off. Play relief can then only come from solo
    // play -- and it must still arrive.
    let (mut world, config) = load();
    let registry = BehaviorRegistry::with_builtins();

    let mut corner = 0u32;
    for el in &mut world.elements {
        if el.element_type().is_critter() {
            el.pos = cloudkitty_core::grid::Position::new(corner, 0);
            corner += 2; // distinct tiles, all >= 19 tiles from Miso
        }
    }

    let mut min_play = f32::MAX;
    let mut solo_seen = false;
    for _ in 0..40 {
        world.tick(&registry, &config).await;
        let miso = world.kitty(MISO).unwrap();
        min_play = min_play.min(miso.needs.get(NeedKind::Play));
        if miso.last_action == Some(cloudkitty_core::action::Action::play_solo()) {
            solo_seen = true;
        }
    }

    assert!(solo_seen, "Miso never once pounced at nothing");
    assert!(
        min_play < 90.0,
        "play stayed pinned (min {min_play}) despite the solo backstop"
    );
}
