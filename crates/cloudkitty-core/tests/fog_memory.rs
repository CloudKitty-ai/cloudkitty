//! Spec 049 FR-006–FR-008 / SC-003: the element memory's law, as a
//! property over random driven worlds and as the US1 scenarios staged by
//! hand. `World::update_memories` runs last in every environment phase;
//! the property test checks the post-tick state it leaves after each real
//! tick, and the scenarios step it directly on a staged world.

use std::sync::Arc;

use cloudkitty_core::config::KittyConfig;
use cloudkitty_core::element::{Element, ElementKind, ElementType};
use cloudkitty_core::kitty::{memory_index, MemorySlot};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, Config, Position, World};
use proptest::prelude::*;

fn nearest_visible(
    world: &World,
    origin: Position,
    kind: ElementType,
    radius: u32,
) -> Option<Position> {
    world
        .elements
        .iter()
        .filter(|e| e.element_type() == kind && origin.visible_from(&e.pos, radius))
        .min_by_key(|e| (origin.manhattan_distance(&e.pos), e.id))
        .map(|e| e.pos)
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(24))]
    /// SC-003 over 80 real ticks of a random world at a random radius: a
    /// present slot is only ever the nearest visible element of its kind
    /// at its `last_seen` tick; a remembered tile inside the disc that
    /// holds none of the kind reads cleared that tick; nothing else clears
    /// at timeout 0; staleness is monotone between sightings.
    #[test]
    fn memory_is_the_nearest_sighting_refuted_on_sight_and_never_forgotten_otherwise(
        seed in 0u64..10_000,
        radius in 2u32..=12,
    ) {
        let mut config = test_config();
        config.world.seed = seed;
        config.vision.radius = radius;
        config.vision.memory_timeout_ticks = 0;
        // Several of every kind, so "nearest wins" is exercised (with the
        // test world's single element per kind the farthest-wins bug went
        // unnoticed -- redden cycle 12).
        for rule in [
            &mut config.elements.water,
            &mut config.elements.chow,
            &mut config.elements.bug,
            &mut config.elements.greeble,
            &mut config.elements.sunbeam,
        ] {
            rule.min = 3;
            rule.max = 3;
        }
        config.validate().unwrap();
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let runtime = tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
        let mut previous: Vec<_> = world.kitties.iter().map(|k| (k.id, k.memory)).collect();

        for _ in 0..80 {
            runtime.block_on(world.tick(&registry, &config));
            let tick = world.tick; // the snapshot tick just published
            for kitty in &world.kitties {
                let before = previous.iter().find(|(id, _)| *id == kitty.id).map(|(_, m)| *m).unwrap();
                for kind in ElementType::ALL {
                    let slot = memory_index(kind);
                    let now = kitty.memory[slot];
                    match nearest_visible(&world, kitty.pos, kind, radius) {
                        Some(pos) => prop_assert_eq!(
                            now,
                            Some(MemorySlot { pos, last_seen: tick }),
                            "kitty {} {:?}: a visible kind is remembered as its nearest sighting, now",
                            kitty.id,
                            kind
                        ),
                        None => match before[slot] {
                            Some(old) if kitty.pos.visible_from(&old.pos, radius) => prop_assert_eq!(
                                now, None,
                                "kitty {} {:?}: the remembered tile is in view and empty -- refuted",
                                kitty.id,
                                kind
                            ),
                            Some(old) => {
                                prop_assert_eq!(
                                    now,
                                    Some(old),
                                    "kitty {} {:?}: out of view, nothing clears at timeout 0",
                                    kitty.id,
                                    kind
                                );
                                prop_assert!(old.last_seen < tick, "staleness grows by exactly one per tick");
                            }
                            None => prop_assert_eq!(now, None, "never seen stays empty"),
                        },
                    }
                }
            }
            previous = world.kitties.iter().map(|k| (k.id, k.memory)).collect();
        }
    }
}

/// A staged 20x20 world: one cat, no elements, r = 5.
fn stage() -> (World, Arc<Config>) {
    let mut config = test_config();
    config.world.width = 20;
    config.world.height = 20;
    config.vision.radius = 5;
    config.kitties = vec![
        KittyConfig {
            id: 1,
            name: "Miso".into(),
            x: 10,
            y: 10,
            behavior: "needs_driven".into(),
            needs: None,
        },
        KittyConfig {
            id: 2,
            name: "Biscuit".into(),
            x: 0,
            y: 0,
            behavior: "needs_driven".into(),
            needs: None,
        },
    ];
    config.validate().unwrap();
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    world.elements.clear();
    (world, config)
}

fn chow(id: u32, x: u32, y: u32) -> Element {
    Element {
        id,
        kind: ElementKind::Chow { servings: 5 },
        pos: Position::new(x, y),
        ttl: None,
    }
}

fn place(world: &mut World, id: u32, pos: Position) {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].pos = pos;
}

fn chow_memory(world: &World, id: u32) -> Option<MemorySlot> {
    world.kitty(id).unwrap().memory[memory_index(ElementType::Chow)]
}

/// US1 scenario 3: walk past a bowl and out of range -- present, the
/// remembered tile, and a `last_seen` that dates the sighting.
#[test]
fn a_bowl_walked_past_is_remembered_where_it_was_with_its_sighting_tick() {
    let (mut world, config) = stage();
    world.push_element(chow(900, 13, 10));
    world.tick = 100;
    world.update_memories(&config); // seen at (13, 10), distance 3
    assert_eq!(
        chow_memory(&world, 1),
        Some(MemorySlot {
            pos: Position::new(13, 10),
            last_seen: 101
        })
    );
    // Walk west, out of range (18 tiles away), for ten ticks: unchanged.
    place(&mut world, 1, Position::new(0, 10));
    for t in 101..111 {
        world.tick = t;
        world.update_memories(&config);
        assert_eq!(
            chow_memory(&world, 1),
            Some(MemorySlot {
                pos: Position::new(13, 10),
                last_seen: 101
            }),
            "out of view at tick {t}: the memory holds and only ages"
        );
    }
}

/// US1 scenario 4: the bowl is eaten away while the cat is out of range;
/// on the first tick the tile re-enters the disc the memory is all zero.
#[test]
fn a_remembered_bowl_that_is_gone_clears_on_first_sight_of_its_tile() {
    let (mut world, config) = stage();
    world.push_element(chow(900, 13, 10));
    world.update_memories(&config);
    assert!(chow_memory(&world, 1).is_some());
    place(&mut world, 1, Position::new(0, 10));
    world.elements.clear(); // eaten away while out of range
    world.tick += 1;
    world.update_memories(&config);
    assert!(
        chow_memory(&world, 1).is_some(),
        "still out of sight: still remembered"
    );
    // Walk back until the tile (13, 10) is just inside the disc: from
    // (8, 10) the offset is (5, 0) -> 25 <= 25.
    place(&mut world, 1, Position::new(7, 10)); // (6, 0) -> 36: not yet
    world.tick += 1;
    world.update_memories(&config);
    assert!(
        chow_memory(&world, 1).is_some(),
        "one tile short of sight: still remembered"
    );
    place(&mut world, 1, Position::new(8, 10));
    world.tick += 1;
    world.update_memories(&config);
    assert_eq!(
        chow_memory(&world, 1),
        None,
        "refuted on the first tick the tile is in view"
    );
}

/// US1 scenario 5: two bowls visible -- the nearer wins; ties to the
/// lower id. Most-recent-wins: a later nearer sighting overwrites.
#[test]
fn two_visible_bowls_remember_the_nearer_ties_to_the_lower_id() {
    let (mut world, config) = stage();
    world.push_element(chow(950, 12, 10)); // distance 2
    world.push_element(chow(901, 10, 13)); // distance 3
    world.update_memories(&config);
    assert_eq!(
        chow_memory(&world, 1).unwrap().pos,
        Position::new(12, 10),
        "the nearer wins"
    );
    // An equidistant pair: (12, 10) id 950 vs (8, 10) id 902 -> lower id.
    world.push_element(chow(902, 8, 10));
    world.elements.retain(|e| e.id != 901);
    world.tick += 1;
    world.update_memories(&config);
    assert_eq!(
        chow_memory(&world, 1).unwrap().pos,
        Position::new(8, 10),
        "ties to the lower id"
    );
    assert_eq!(
        chow_memory(&world, 1).unwrap().last_seen,
        world.tick + 1,
        "the newest sighting"
    );
}

/// US1 scenario 6: a world-covering radius -- every slot mirrors a visible
/// element with staleness 0; global vision is a radius setting.
#[test]
fn a_world_covering_radius_mirrors_every_visible_kind_now() {
    let mut config = test_config();
    config.vision.radius = 40;
    config.validate().unwrap();
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    world.update_memories(&config);
    for kitty in &world.kitties {
        for kind in ElementType::ALL {
            let expected = nearest_visible(&world, kitty.pos, kind, 40).map(|pos| MemorySlot {
                pos,
                last_seen: world.tick + 1,
            });
            assert_eq!(
                kitty.memory[memory_index(kind)],
                expected,
                "{kind:?} mirrors the nearest element"
            );
            if world.elements.iter().any(|e| e.element_type() == kind) {
                assert!(expected.is_some(), "{kind:?} exists, so it is seen");
            }
        }
    }
}

/// FR-008: a positive timeout forgets a memory older than it -- and only
/// then; `0` never forgets.
#[test]
fn a_positive_timeout_forgets_and_zero_never_does() {
    let (mut world, config) = stage();
    let mut timed = (*config).clone();
    timed.vision.memory_timeout_ticks = 5;
    timed.validate().unwrap();
    world.push_element(chow(900, 13, 10));
    world.tick = 10;
    world.update_memories(&timed); // last_seen 11
    place(&mut world, 1, Position::new(0, 10));
    world.elements.clear();
    for t in 11..=15 {
        world.tick = t;
        world.update_memories(&timed);
        assert!(
            chow_memory(&world, 1).is_some(),
            "age {} <= 5 keeps it",
            t + 1 - 11
        );
    }
    world.tick = 16; // seen_at 17: age 6 > 5
    world.update_memories(&timed);
    assert_eq!(
        chow_memory(&world, 1),
        None,
        "older than the timeout: forgotten"
    );

    // The same walk at timeout 0 keeps it for ever.
    let (mut world, config) = stage();
    world.push_element(chow(900, 13, 10));
    world.update_memories(&config);
    place(&mut world, 1, Position::new(0, 10));
    world.elements.clear();
    for t in 1..5_000 {
        world.tick = t;
        world.update_memories(&config);
    }
    assert!(chow_memory(&world, 1).is_some(), "0 = never");
}

/// US1 scenario 7 / FR-005: own-tile facts are never fogged -- a cat
/// standing in water knows it at any radius (the memory of water is
/// simply "here", staleness 0), and so does the encoder's own-tile bit.
#[test]
fn own_tile_water_is_known_at_any_radius() {
    for radius in [2u32, 5, 40] {
        let (mut world, config) = stage();
        let mut cfg = (*config).clone();
        cfg.vision.radius = radius;
        world.push_element(Element {
            id: 700,
            kind: ElementKind::Water,
            pos: Position::new(10, 10),
            ttl: None,
        });
        world.update_memories(&cfg);
        let water = world.kitty(1).unwrap().memory[memory_index(ElementType::Water)].unwrap();
        assert_eq!(
            water.pos,
            Position::new(10, 10),
            "r = {radius}: the own tile is inside every disc"
        );
        assert_eq!(
            water.last_seen,
            world.tick + 1,
            "staleness 0: here means now"
        );
    }
}
