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
use cloudkitty_core::{BehaviorRegistry, Position, World};
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

/// Spec 049 US5 scenario 5 / T058: adjacency is inside every disc of
/// radius ≥ 1 -- no scene can run with an unseen partner. Arithmetic on
/// the five adjacent offsets at every radius the config accepts.
#[test]
fn an_adjacent_partner_is_inside_every_disc() {
    let me = Position::new(10, 10);
    for radius in 2u32..=40 {
        for (dx, dy) in [(0i64, 0i64), (1, 0), (-1, 0), (0, 1), (0, -1)] {
            let there = Position::new((10 + dx) as u32, (10 + dy) as u32);
            assert!(me.is_adjacent(&there));
            assert!(
                me.visible_from(&there, radius),
                "r = {radius}: an adjacent partner is seen"
            );
        }
    }
}

/// Spec 049 US5 (the same-fog structural witness at run scale, T059):
/// the served roster, all scripted, 5,000 ticks at r = 5 -- every target
/// any built-in proposes was inside the deciding cat's disc, or a friend
/// it could hear (at that friend's stamped position). Memory carries no
/// ids, so the element half is the disc alone. The structural guard
/// (`the_view_is_exactly_the_euclidean_disc`) is the primary proof; this
/// is the run that shows the built-ins live inside it.
#[test]
fn every_scripted_proposal_names_something_in_the_deciders_view() {
    use cloudkitty_core::action::TargetRef;
    use cloudkitty_core::behavior::resolve_decisions;
    use cloudkitty_core::{Action, JointProposal};
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml")).unwrap();
    let mut config: cloudkitty_core::Config = toml::from_str(&text).unwrap();
    for kitty in &mut config.kitties {
        kitty.behavior = "needs_driven".into();
    }
    config.vision.radius = 5;
    config.validate().unwrap();
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let window = config.meow.digest_window_ticks;
    let mut checked = 0usize;
    for _ in 0..5_000 {
        let snapshot = world.snapshot();
        let resolved = resolve_decisions(&mut world, &registry, &config);
        let mut proposals = JointProposal::new();
        for r in &resolved {
            let view = snapshot.fog_for(r.kitty_id, 5);
            let known_kitties: BTreeSet<u32> = view
                .kitties
                .iter()
                .map(|k| k.id)
                .chain(view.heard_unseen(window).into_iter().map(|(id, _, _)| id))
                .collect();
            let known_elements: BTreeSet<u32> = view.elements.iter().map(|e| e.id).collect();
            let (kitty_target, element_target) = match r.decision.activity {
                Action::Rest { with: Some(id) }
                | Action::Sleep { with: Some(id) }
                | Action::Groom { target: Some(id) }
                | Action::Chase(TargetRef::Kitty { id })
                | Action::Play {
                    target: Some(TargetRef::Kitty { id }),
                } => (Some(id), None),
                Action::Chase(TargetRef::Element { id })
                | Action::Play {
                    target: Some(TargetRef::Element { id }),
                } => (None, Some(id)),
                _ => (None, None),
            };
            if let Some(id) = kitty_target {
                assert!(
                    known_kitties.contains(&id),
                    "tick {}: kitty {} proposed {:?} at a friend outside its disc and hearing",
                    world.tick,
                    r.kitty_id,
                    r.decision.activity
                );
                checked += 1;
            }
            if let Some(id) = element_target {
                assert!(
                    known_elements.contains(&id),
                    "tick {}: kitty {} proposed {:?} at an element outside its disc",
                    world.tick,
                    r.kitty_id,
                    r.decision.activity
                );
                checked += 1;
            }
            proposals.propose(r.kitty_id, r.decision);
        }
        world.tick_with_proposals(&proposals, &config);
    }
    assert!(checked > 100, "the run named targets: {checked}");
    eprintln!("same-fog witness: {checked} targeted proposals over 5,000 ticks, all inside disc ∪ hearing");
}
