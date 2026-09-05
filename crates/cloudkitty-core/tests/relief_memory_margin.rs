//! Spec 050 SC-004 / US1 scenarios 5-6: on the SERVED roster at r = 5 the
//! drink channel of the meow law is alive. `want_drink` was structurally
//! silent under the unbounded memory rule (F-040: pools are permanent and
//! never forgotten, so the first sight of any pool silenced the word for
//! the rest of the run); the served `[meow] relief_memory_margin = 0`
//! revives it. The counts are READINGS beside the pin (F-040 predicts ~12
//! drink calls and +10-13 eat calls per 1,000 ticks); the gate is > 0.
//!
//! Two runs: the served `cloudkitty.toml` VERBATIM for the drink count
//! (1,000 ticks -- a few hundred could legitimately read 0 on a bad seed);
//! and the same config with a reply floor set IN THE TEST ONLY for the
//! `here_water` reply count -- any value > 0 (clarification 1,
//! 2026-09-05): the claim is "the reply path fires on a want_drink", not
//! "at 0.30", so the provisional declaration-time pin never ripples into
//! this guard. The served config keeps the floor unset.

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::Arc;

use cloudkitty_core::{BehaviorRegistry, Config, MessageKind, World};

const TICKS: u64 = 1_000;

fn served_all_scripted() -> Config {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml"))
        .expect("the served config is readable");
    let mut config: Config = toml::from_str(&text).expect("the served config parses");
    for kitty in &mut config.kitties {
        kitty.behavior = "needs_driven".into();
    }
    assert_eq!(config.vision.radius, 5, "the served FR-002 placeholder");
    config.validate().expect("the served config validates");
    config
}

/// Per kind: (calls, of which stamped `reply`). The tick is captured
/// BEFORE the world advances -- meows are stamped with the tick they were
/// spoken in, and `World::tick` moves the clock on.
fn count_calls(config: Config) -> BTreeMap<MessageKind, (usize, usize)> {
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    let mut counts: BTreeMap<MessageKind, (usize, usize)> = BTreeMap::new();
    for _ in 0..TICKS {
        let tick = world.tick;
        runtime.block_on(world.tick(&registry, &config));
        for m in world.recent_meows.iter().filter(|m| m.tick == tick) {
            let entry = counts.entry(m.kind).or_insert((0, 0));
            entry.0 += 1;
            if m.reply {
                entry.1 += 1;
            }
        }
    }
    counts
}

#[test]
fn the_served_roster_asks_for_water() {
    let config = served_all_scripted();
    assert_eq!(
        config.meow.relief_memory_margin,
        Some(0),
        "the served key is this guard's precondition (spec 050 FR-007)"
    );
    let counts = count_calls(config);
    let calls = |kind| counts.get(&kind).map_or(0, |c| c.0);
    println!(
        "F-040 reading (served, r = 5, margin 0, {TICKS} ticks): want_drink {} want_eat {} want_play {}",
        calls(MessageKind::WantDrink),
        calls(MessageKind::WantEat),
        calls(MessageKind::WantPlay)
    );
    assert!(
        calls(MessageKind::WantDrink) > 0,
        "want_drink must be said on the served config: {counts:?}"
    );
}

#[test]
fn a_want_drink_gets_a_here_water_reply() {
    let mut config = served_all_scripted();
    assert!(
        config.behavior.reply_intensity_floor.is_none(),
        "the served floor stays unset; this test sets its own"
    );
    config.behavior.reply_intensity_floor = Some(0.01);
    config.validate().expect("a floor > 0 is valid");
    let counts = count_calls(config);
    let replies = counts.get(&MessageKind::HereWater).map_or(0, |c| c.1);
    println!("here_water replies with a test-only floor of 0.01: {replies}");
    assert!(
        replies > 0,
        "a here_water stamped reply must answer some want_drink: {counts:?}"
    );
}
