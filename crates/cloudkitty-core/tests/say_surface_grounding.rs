//! Spec 033 SC-002: the grounding invariant, property-tested (T012).
//!
//! Across randomized worlds, positions, cooldowns, and flags:
//! `message_legal(Here*)` holds EXACTLY when (predicate ∧ cooldown ∧ flag) —
//! both directions. The enforcement path filters on this same function
//! (world.rs message application; the mask oracle proves the mask does
//! too), so pinning the function pins the law.

use cloudkitty_core::element::ElementType;
use cloudkitty_core::grid::Position;
use cloudkitty_core::meow::{message_legal, MessageKind};
use cloudkitty_core::rng::SimRng;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::{
    adjacent_critter_in, adjacent_element_in, adjacent_stocked_chow_in, World,
};

#[test]
fn here_legality_is_exactly_predicate_and_cooldown_and_flag() {
    // The crate's own seeded RNG (033 review Finding 7): the same exact
    // replayability the hand-rolled xorshift was for, without its modulo
    // bias or all-zero-seed fixed point.
    let mut rng = SimRng::from_seed(0x2026_0815_0033);
    let mut probes = 0u32;
    let mut legal_seen = 0u32;

    for world_seed in 0..40u64 {
        let mut config = test_config();
        config.world.seed = 20260815 + world_seed;
        let mut world = World::generate(&config);
        world.tick = 100;

        // Randomize the vocabulary flags sometimes (flags are part of the
        // invariant, not a fixed backdrop).
        config.meow.vocabulary.here_food = rng.gen_range_u32(0, 4) != 0;
        config.meow.vocabulary.here_water = rng.gen_range_u32(0, 4) != 0;
        config.meow.vocabulary.here_critter = rng.gen_range_u32(0, 4) != 0;
        config.meow.vocabulary.here_sunbeam = rng.gen_range_u32(0, 4) != 0;

        for _ in 0..60 {
            // Advance the clock so stamped cooldowns expire between probes
            // (a frozen clock would starve the legal side of the property).
            world.tick += 7;
            // Teleport kitty 1: half the time uniformly, half the time
            // BESIDE a random element so the legal side is well-exercised.
            let idx = world.kitty_index(1).unwrap();
            let pos = if rng.gen_bool(0.5) || world.elements.is_empty() {
                Position::new(
                    rng.gen_range_u32(0, world.width),
                    rng.gen_range_u32(0, world.height),
                )
            } else {
                let e = rng.gen_range_u32(0, world.elements.len() as u32) as usize;
                let e = &world.elements[e];
                let dx = [0i64, 1, -1, 0][rng.gen_range_u32(0, 4) as usize];
                let dy = [1i64, 0, 0, -1][rng.gen_range_u32(0, 4) as usize];
                Position::new(
                    (e.pos.x as i64 + dx).clamp(0, world.width as i64 - 1) as u32,
                    (e.pos.y as i64 + dy).clamp(0, world.height as i64 - 1) as u32,
                )
            };
            world.kitties[idx].pos = pos;
            for kind in [
                MessageKind::HereFood,
                MessageKind::HereWater,
                MessageKind::HereCritter,
                MessageKind::HereSunbeam,
            ] {
                if rng.gen_range_u32(0, 3) == 0 {
                    world.kitties[idx].set_meow_cooldown(kind, world.tick + 5);
                }
            }

            let kitty = world.kitty(1).unwrap();
            let cases = [
                (
                    MessageKind::HereFood,
                    adjacent_stocked_chow_in(&world.elements, pos).is_some(),
                    config.meow.vocabulary.here_food,
                ),
                (
                    MessageKind::HereWater,
                    adjacent_element_in(&world.elements, pos, ElementType::Water).is_some(),
                    config.meow.vocabulary.here_water,
                ),
                (
                    MessageKind::HereCritter,
                    adjacent_critter_in(&world.elements, pos),
                    config.meow.vocabulary.here_critter,
                ),
                (
                    MessageKind::HereSunbeam,
                    adjacent_element_in(&world.elements, pos, ElementType::Sunbeam).is_some(),
                    config.meow.vocabulary.here_sunbeam,
                ),
            ];
            for (kind, predicate, flag) in cases {
                let expected = predicate && flag && kitty.can_meow(kind, world.tick);
                let actual = message_legal(kitty, kind, world.tick, &config, &world.elements);
                assert_eq!(
                    actual, expected,
                    "world {world_seed}, {kind:?} at {pos:?}: legality must be \
                     exactly predicate({predicate}) && flag({flag}) && cooldown"
                );
                probes += 1;
                if actual {
                    legal_seen += 1;
                }
            }
        }
    }

    assert!(
        probes >= 9_000,
        "the property ran at scale: {probes} probes"
    );
    assert!(
        legal_seen > 100,
        "the property exercised the LEGAL side too, not just refusals: {legal_seen}"
    );
}

#[test]
fn the_free_register_is_refused_only_by_cooldown_or_flag() {
    // SC-002's second clause, for the sound-named tier: no world state can
    // refuse a free word -- only its cooldown or its flag.
    let mut rng = SimRng::from_seed(0xE4E4 ^ 0x2026_0815); // ekekek, as close as hex allows
    for world_seed in 0..10u64 {
        let mut config = test_config();
        config.world.seed = 30260815 + world_seed;
        config.meow.vocabulary.trill = rng.gen_bool(0.5);
        config.meow.vocabulary.ekekek = rng.gen_bool(0.5);
        let mut world = World::generate(&config);
        world.tick = 100;
        for _ in 0..40 {
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(
                rng.gen_range_u32(0, world.width),
                rng.gen_range_u32(0, world.height),
            );
            for kind in [
                MessageKind::Mew,
                MessageKind::Chirp,
                MessageKind::Trill,
                MessageKind::Ekekek,
            ] {
                let kitty = world.kitty(1).unwrap();
                let expected =
                    config.meow.vocabulary.enabled(kind) && kitty.can_meow(kind, world.tick);
                assert_eq!(
                    message_legal(kitty, kind, world.tick, &config, &world.elements),
                    expected,
                    "{kind:?}: a sound-named word answers to nothing but cooldown and flag"
                );
            }
        }
    }
}
