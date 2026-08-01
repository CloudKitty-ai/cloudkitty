//! Spec 023 SC-003: the scripted rate limit, observed from the outside.
//!
//! With the engine swallow retired, nothing *enforces* meow spacing -- the
//! courtesy consult in the scripted behaviors is the whole rate limit. This
//! property test watches full engine ticks and asserts no scripted kitty
//! ever repeats a message kind faster than the courtesy its stamp recorded:
//! at least the urgent interval for need-backed kinds (their stamps shorten
//! when the need is urgent), at least the base interval for the rest
//! (follow-me and the approach-etiquette "Wait for me!", which spec 023
//! taught to consult -- the third emitter). A path that skips the consult
//! fails here loudly, which is exactly how spec 023 keeps scripted spam
//! structurally impossible with no baseline to compare against.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::config::Config;
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::world::World;

#[tokio::test]
async fn scripted_meows_keep_courtesy_spacing_without_the_engine_swallow() {
    for seed in [7u64, 91, 402] {
        let mut config = Config::default();
        config.world.seed = seed;
        config.validate().expect("valid");
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);

        let mut last_emit: BTreeMap<(u32, MessageKind), u64> = BTreeMap::new();
        let mut seen: BTreeSet<(u32, MessageKind, u64)> = BTreeSet::new();
        let mut total = 0u64;

        for _ in 0..1_500 {
            world.tick(&registry, &config).await;
            for m in &world.recent_meows {
                if !seen.insert((m.kitty_id, m.kind, m.tick)) {
                    continue;
                }
                total += 1;
                let key = (m.kitty_id, m.kind);
                if let Some(prev) = last_emit.get(&key) {
                    let gap = m.tick.saturating_sub(*prev);
                    let min_gap = if m.kind.related_need().is_some() {
                        // Need-backed kinds may stamp the urgent interval.
                        config.meow.urgent_courtesy_ticks
                    } else {
                        config.meow.courtesy_ticks
                    };
                    assert!(
                        gap >= min_gap,
                        "seed {seed}: kitty {} repeated {:?} after {gap} ticks \
                         (courtesy floor {min_gap})",
                        m.kitty_id,
                        m.kind
                    );
                }
                let entry = last_emit.entry(key).or_insert(m.tick);
                if m.tick > *entry {
                    *entry = m.tick;
                }
            }
        }
        assert!(total > 0, "seed {seed}: a living meadow meows sometimes");
    }
}
