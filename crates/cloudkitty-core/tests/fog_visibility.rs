//! Spec 049 FR-021 / SC-002: the fog view leaks nothing and misses nothing.
//!
//! Over random worlds and radii, every kitty and element reachable through
//! the view a decider is handed (`DecisionContext.world` is an
//! `Arc<FogView>` by type, so this IS the structural guard) lies inside the
//! observer's Euclidean disc, and the set present equals the disc set
//! exactly -- zero misses, zero leaks -- through every accessor a behavior
//! reads: `kitties`, `others`, `elements`, `elements_of`, `critters`,
//! `kitty`, `element_at`.

use std::collections::BTreeSet;
use std::sync::Arc;

use cloudkitty_core::config::KittyConfig;
use cloudkitty_core::element::ElementType;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{Position, World};
use proptest::prelude::*;

fn kitty_positions(width: u32, height: u32) -> impl Strategy<Value = Vec<(u32, u32)>> {
    prop::collection::btree_set((0..width, 0..height), 2..=5).prop_map(|s| s.into_iter().collect())
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]
    #[test]
    fn the_view_is_exactly_the_euclidean_disc(
        width in 16u32..=24,
        height in 16u32..=24,
        seed in 0u64..10_000,
        radius in 2u32..=40,
        positions in (16u32..=24, 16u32..=24).prop_flat_map(|(w, h)| kitty_positions(w, h)),
    ) {
        let mut config = test_config();
        config.world.width = width;
        config.world.height = height;
        config.world.seed = seed;
        config.vision.radius = radius;
        config.kitties = positions
            .iter()
            .filter(|(x, y)| *x < width && *y < height)
            .enumerate()
            .map(|(i, &(x, y))| KittyConfig {
                id: i as u32 + 1,
                name: format!("K{i}"),
                x,
                y,
                behavior: "needs_driven".into(),
                needs: None,
            })
            .collect();
        prop_assume!(config.kitties.len() >= 2);
        config.validate().expect("a random roster inside the world is valid");
        let config = Arc::new(config);
        let world = World::generate(&config);
        let snapshot = world.snapshot();
        let all_ids: BTreeSet<u32> = snapshot.kitties.iter().map(|k| k.id).collect();

        for observer in &snapshot.kitties {
            let view = snapshot.fog_for(observer.id, radius);
            let origin = observer.pos;
            // The oracle is spelled out here, independently of
            // `Position::visible_from`, so a wrong predicate in the engine
            // (a strict `<`, a Manhattan diamond) reddens this guard.
            let inside = |pos: Position| {
                let dx = i64::from(pos.x) - i64::from(origin.x);
                let dy = i64::from(pos.y) - i64::from(origin.y);
                dx * dx + dy * dy <= i64::from(radius) * i64::from(radius)
            };

            // Kitties: the disc set, through every accessor.
            let expected_k: BTreeSet<u32> =
                snapshot.kitties.iter().filter(|k| inside(k.pos)).map(|k| k.id).collect();
            let got_k: BTreeSet<u32> = view.kitties.iter().map(|k| k.id).collect();
            prop_assert_eq!(&got_k, &expected_k, "kitties present == disc set");
            let got_others: BTreeSet<u32> = view.others(observer.id).map(|k| k.id).collect();
            let mut expected_others = expected_k.clone();
            expected_others.remove(&observer.id);
            prop_assert_eq!(got_others, expected_others, "others() is the disc minus me");
            for &id in &all_ids {
                prop_assert_eq!(view.kitty(id).is_some(), expected_k.contains(&id), "kitty({})", id);
            }
            prop_assert!(view.kitty(observer.id).is_some(), "the observer is always in view");
            prop_assert_eq!(view.roster.iter().copied().collect::<BTreeSet<u32>>(), all_ids.clone());

            // Elements: the disc set, through every accessor.
            let expected_e: BTreeSet<u32> =
                snapshot.elements.iter().filter(|e| inside(e.pos)).map(|e| e.id).collect();
            let got_e: BTreeSet<u32> = view.elements.iter().map(|e| e.id).collect();
            prop_assert_eq!(&got_e, &expected_e, "elements present == disc set");
            for kind in ElementType::ALL {
                let got: BTreeSet<u32> = view.elements_of(kind).map(|e| e.id).collect();
                let want: BTreeSet<u32> = snapshot
                    .elements
                    .iter()
                    .filter(|e| e.element_type() == kind && inside(e.pos))
                    .map(|e| e.id)
                    .collect();
                prop_assert_eq!(got, want, "elements_of({:?})", kind);
            }
            let got_c: BTreeSet<u32> = view.critters().map(|e| e.id).collect();
            let want_c: BTreeSet<u32> = snapshot
                .elements
                .iter()
                .filter(|e| e.element_type().is_critter() && inside(e.pos))
                .map(|e| e.id)
                .collect();
            prop_assert_eq!(got_c, want_c, "critters()");
            for e in &snapshot.elements {
                prop_assert_eq!(
                    view.element_at(e.pos).map(|v| v.id),
                    if inside(e.pos) { snapshot.element_at(e.pos).map(|v| v.id) } else { None },
                    "element_at({:?})", e.pos
                );
            }

            // And every entity in the view really is inside the disc (the leak
            // direction stated directly, not only via set equality).
            for k in &view.kitties {
                prop_assert!(inside(k.pos), "kitty {} leaked from outside the disc", k.id);
            }
            for e in &view.elements {
                prop_assert!(inside(e.pos), "element {} leaked from outside the disc", e.id);
            }
            prop_assert_eq!(view.recent_meows.len(), snapshot.recent_meows.len(), "hearing is global");
        }
    }
}
