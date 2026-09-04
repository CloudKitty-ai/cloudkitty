//! Spec 049 T093: the refusal `reason` on the served roster, all scripted --
//! a READING for the step-5 refusal-tax instrument (Experiments' expectation
//! on record: scripted seats walk before proposing, so their partner
//! refusals should be ~0; whatever is measured here is the number the
//! instrument calibrates against, ordering effects included). Ignored:
//! `cargo test -p cloudkitty-core --test refusal_reasons -- --ignored --nocapture`.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::{BehaviorRegistry, Config, RefusalReason, World};

fn served_all_scripted(radius: u32) -> Config {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml")).unwrap();
    let mut config: Config = toml::from_str(&text).unwrap();
    for kitty in &mut config.kitties {
        kitty.behavior = "needs_driven".into();
    }
    config.vision.radius = radius;
    config.behavior.reply_intensity_floor = None;
    config.events.refusal_retention = 100_000;
    config.validate().unwrap();
    config
}

#[tokio::test(flavor = "current_thread")]
#[ignore]
async fn refusal_reasons_on_the_served_scripted_roster() {
    for radius in [5u32, 40] {
        let config = Arc::new(served_all_scripted(radius));
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        for _ in 0..20_000u64 {
            world.tick(&registry, &config).await;
        }
        let mut counts: BTreeMap<(RefusalReason, bool), usize> = BTreeMap::new();
        let mut by_action: BTreeMap<String, usize> = BTreeMap::new();
        for e in world.refusal_log.events() {
            *counts.entry((e.reason, e.absorbed)).or_default() += 1;
            let variant = format!("{:?}", e.proposed);
            let variant = variant.split([' ', '(', '{']).next().unwrap().to_string();
            *by_action
                .entry(format!("{:?}/{variant}", e.reason))
                .or_default() += 1;
        }
        eprintln!(
            "REFUSALS r={radius} over 20k ticks (reason, absorbed) -> count: {counts:?}; by reason/action: {by_action:?}"
        );
    }
}
