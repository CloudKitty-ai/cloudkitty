//! Spec 049 US7 / SC-010: the meow law under fog -- the knowledge-gated
//! want tier, the widened here tier, the engine reply stamp -- staged
//! scenario by scenario (US7 1-9) and as properties over random worlds.
//! Every verdict is `message_legal` over the cat's fog view, the ONE
//! predicate the RL mask and the built-in announce share.

use std::sync::Arc;

use cloudkitty_core::config::KittyConfig;
use cloudkitty_core::element::{Element, ElementKind, ElementType};
use cloudkitty_core::kitty::{memory_index, Activity, ActivityClock, MemorySlot};
use cloudkitty_core::meow::{message_legal, reply_condition, Meow, MessageKind, WANT_HERE_PAIRS};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{Config, NeedKind, Position, World};
use proptest::prelude::*;

/// A 20x20 world, r = 5, cat 1 at (10, 10), friends 2..4 far away, no
/// elements, tick 100, every need low and nothing armed.
fn stage() -> (World, Config) {
    let mut config = test_config();
    config.world.width = 20;
    config.world.height = 20;
    config.vision.radius = 5;
    config.kitties = [(1u32, 10u32, 10u32), (2, 0, 0), (3, 19, 19), (4, 0, 19)]
        .iter()
        .map(|&(id, x, y)| KittyConfig {
            id,
            name: format!("K{id}"),
            x,
            y,
            behavior: "needs_driven".into(),
            needs: None,
        })
        .collect();
    config.validate().unwrap();
    let mut world = World::generate(&config);
    world.elements.clear();
    world.tick = 100;
    (world, config)
}

fn place(world: &mut World, id: u32, x: u32, y: u32) {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].pos = Position::new(x, y);
}

fn arm(world: &mut World, id: u32, need: NeedKind, level: f32) {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].needs.add(need, level);
    world.kitties[idx].announce_armed.insert(need);
}

fn element(id: u32, kind: ElementKind, x: u32, y: u32) -> Element {
    Element {
        id,
        kind,
        pos: Position::new(x, y),
        ttl: None,
    }
}

fn legal(world: &World, id: u32, kind: MessageKind, config: &Config) -> bool {
    let view = world.snapshot().fog_for(id, config.vision.radius);
    message_legal(world.kitty(id).unwrap(), kind, world.tick, config, &view)
}

fn meow(kitty_id: u32, kind: MessageKind, tick: u64, x: u32, y: u32) -> Meow {
    Meow {
        kitty_id,
        kind,
        tick,
        intensity: 0.5,
        pos: Position::new(x, y),
        reply: false,
    }
}

/// US7 scenarios 1-2: want_eat is illegal with a bowl in the disc, legal
/// with none visible or remembered, illegal again once remembered.
#[test]
fn want_eat_means_i_cannot_see_or_remember_food() {
    let (mut world, config) = stage();
    arm(&mut world, 1, NeedKind::Eat, 60.0);
    world.push_element(element(900, ElementKind::Chow { servings: 5 }, 13, 10));
    assert!(
        !legal(&world, 1, MessageKind::WantEat, &config),
        "relief visible"
    );
    world.elements.clear();
    assert!(
        legal(&world, 1, MessageKind::WantEat, &config),
        "nothing seen, nothing remembered"
    );
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].memory[memory_index(ElementType::Chow)] = Some(MemorySlot {
        pos: Position::new(2, 2),
        last_seen: 40,
    });
    assert!(
        !legal(&world, 1, MessageKind::WantEat, &config),
        "remembered relief silences"
    );
}

/// US7 scenario 3: only the TOP need's want is legal; `NeedKind::ALL`
/// order breaks exact ties.
#[test]
fn only_the_top_need_may_ask() {
    let (mut world, config) = stage();
    arm(&mut world, 1, NeedKind::Eat, 50.0);
    arm(&mut world, 1, NeedKind::Sleep, 70.0);
    assert!(
        !legal(&world, 1, MessageKind::WantEat, &config),
        "eat is armed but not the top need"
    );
    assert!(
        legal(&world, 1, MessageKind::WantSleep, &config),
        "sleep is the top need"
    );
    // An exact tie: eat precedes sleep in NeedKind::ALL.
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].needs.add(NeedKind::Eat, 20.0);
    assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 70.0);
    assert!(legal(&world, 1, MessageKind::WantEat, &config));
    assert!(!legal(&world, 1, MessageKind::WantSleep, &config));
}

/// US7 scenarios 7-9: the social gate is "no idle friend IN VIEW"; a
/// heard friend never gates; a known critter is known play relief.
#[test]
fn the_social_words_read_idle_friends_in_view_only() {
    let (mut world, config) = stage();
    arm(&mut world, 1, NeedKind::Cuddle, 60.0);
    arm(&mut world, 1, NeedKind::Play, 55.0);
    // Nobody in view: cuddle (the top need) is legal.
    assert!(legal(&world, 1, MessageKind::WantCuddle, &config));
    // A friend only HEARD (a meow from outside the disc) never silences.
    world.recent_meows.push(meow(2, MessageKind::Mew, 95, 0, 0));
    assert!(
        legal(&world, 1, MessageKind::WantCuddle, &config),
        "heard friends drive targeting, not the gate"
    );
    // A visible friend mid-scene or asleep is not idle.
    place(&mut world, 2, 12, 10);
    let f = world.kitty_index(2).unwrap();
    world.kitties[f].activity = Activity::Grooming { target: None };
    world.kitties[f].activity_clock = Some(ActivityClock::start(90));
    assert!(
        legal(&world, 1, MessageKind::WantCuddle, &config),
        "a busy friend in view is not relief"
    );
    // An idle friend in view, adjacent or not: illegal.
    world.kitties[f].activity = Activity::Idle;
    world.kitties[f].activity_clock = None;
    assert!(
        !legal(&world, 1, MessageKind::WantCuddle, &config),
        "an idle friend in view is known relief"
    );
    place(&mut world, 2, 14, 13); // 16 + 9 = 25: on the edge, not adjacent
    assert!(
        !legal(&world, 1, MessageKind::WantCuddle, &config),
        "adjacency is not required"
    );
    // Play: same friend clause, plus the critter clause.
    let (mut world, config) = stage();
    arm(&mut world, 1, NeedKind::Play, 60.0);
    assert!(
        legal(&world, 1, MessageKind::WantPlay, &config),
        "nothing better than solo is known"
    );
    world.push_element(element(901, ElementKind::Bug, 12, 12));
    assert!(
        !legal(&world, 1, MessageKind::WantPlay, &config),
        "a visible critter is known play relief"
    );
    world.elements.clear();
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].memory[memory_index(ElementType::Greeble)] = Some(MemorySlot {
        pos: Position::new(3, 3),
        last_seen: 60,
    });
    assert!(
        !legal(&world, 1, MessageKind::WantPlay, &config),
        "a remembered critter too"
    );
    world.kitties[idx].memory[memory_index(ElementType::Greeble)] = None;
    world
        .recent_meows
        .push(meow(3, MessageKind::WantEat, 96, 19, 19));
    assert!(
        legal(&world, 1, MessageKind::WantPlay, &config),
        "scenario 8: a heard friend never gates"
    );
}

/// Owner ruled 2026-09-03 (spec 049 T087, FR-036 amended): `want_bath` is
/// an ASK, not an announcement. Its relief source is in-place self-grooming;
/// the partnered groom only a GROOMER can start, and the groom response
/// starts it on hearing the word -- so an idle friend in view is not relief
/// the caller can execute, it is a groomer who has to be asked. The word is
/// armed-only: no top-need clause, no idle-friend-in-view gate. Cuddle keeps
/// both (its relief the caller executes itself: walk over and rest).
#[test]
fn want_bath_is_armed_only_an_ask_not_an_announcement() {
    let (mut world, config) = stage();
    arm(&mut world, 1, NeedKind::Bath, 40.0);
    arm(&mut world, 1, NeedKind::Cuddle, 70.0); // cuddle is the top need
    place(&mut world, 2, 11, 10); // an idle friend in view, adjacent
    assert!(
        legal(&world, 1, MessageKind::WantBath, &config),
        "bath: armed suffices -- not the top need, an idle friend in view"
    );
    assert!(
        !legal(&world, 1, MessageKind::WantCuddle, &config),
        "cuddle keeps the friend clause"
    );
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].announce_armed.remove(&NeedKind::Bath);
    assert!(
        !legal(&world, 1, MessageKind::WantBath, &config),
        "unarmed: silent"
    );
}

/// US7 scenarios 4-6: the widened here law and the reply stamp -- an
/// audible matching want plus a visible referent make a here legal
/// without adjacency and stamp reply = 1; an adjacency here with no want
/// audible is legal and stamped 0; nothing answers on the same tick.
#[test]
fn a_here_can_answer_an_audible_want_it_can_see_the_referent_of() {
    let (mut world, config) = stage();
    world.push_element(element(700, ElementKind::Water, 13, 10)); // visible, not adjacent
    assert!(
        !legal(&world, 1, MessageKind::HereWater, &config),
        "not adjacent, nothing audible: illegal"
    );
    // B says want_drink at tick 99 from far away; at tick 100 A sees a pond.
    world
        .recent_meows
        .push(meow(2, MessageKind::WantDrink, 99, 0, 0));
    assert!(
        legal(&world, 1, MessageKind::HereWater, &config),
        "the widened law: audible want + visible referent"
    );
    let view = world.snapshot().fog_for(1, config.vision.radius);
    assert!(reply_condition(MessageKind::HereWater, &view, &config));
    assert!(
        !reply_condition(MessageKind::HereFood, &view, &config),
        "no chow visible, no want_eat audible"
    );
    // The engine stamps the emission: reply = 1.
    let mut proposals = cloudkitty_core::JointProposal::new();
    proposals.propose(
        1,
        cloudkitty_core::Decision {
            activity: cloudkitty_core::Action::Idle,
            message: Some(MessageKind::HereWater),
        },
    );
    world.tick_with_proposals(&proposals, &config);
    let stamped = world
        .recent_meows
        .iter()
        .find(|m| m.kitty_id == 1 && m.kind == MessageKind::HereWater)
        .expect("emitted");
    assert!(stamped.reply, "stamped as a reply");
    assert_eq!(stamped.pos, Position::new(10, 10), "and where it was said");

    // Scenario 5: adjacency alone -- legal, stamped 0.
    let (mut world, config) = stage();
    world.push_element(element(700, ElementKind::Water, 11, 10));
    assert!(legal(&world, 1, MessageKind::HereWater, &config));
    let mut proposals = cloudkitty_core::JointProposal::new();
    proposals.propose(
        1,
        cloudkitty_core::Decision {
            activity: cloudkitty_core::Action::Idle,
            message: Some(MessageKind::HereWater),
        },
    );
    world.tick_with_proposals(&proposals, &config);
    let stamped = world
        .recent_meows
        .iter()
        .find(|m| m.kitty_id == 1 && m.kind == MessageKind::HereWater)
        .expect("emitted");
    assert!(!stamped.reply, "adjacency alone is no reply");

    // Scenario 6: a same-tick want is never audible -- the reply floor is
    // one tick, and id order never matters.
    let (mut world, config) = stage();
    world.push_element(element(700, ElementKind::Water, 13, 10));
    world
        .recent_meows
        .push(meow(2, MessageKind::WantDrink, 100, 0, 0));
    assert!(
        !legal(&world, 1, MessageKind::HereWater, &config),
        "same tick: not yet audible"
    );
    // A want that was audible in the earlier tick makes it legal at the next.
    world.tick = 101;
    assert!(legal(&world, 1, MessageKind::HereWater, &config));
    // Cuddle and bath have no here-word at all.
    assert!(WANT_HERE_PAIRS
        .iter()
        .all(|(w, _)| *w != MessageKind::WantCuddle && *w != MessageKind::WantBath));
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(48))]

    /// Spec 050 FR-002 / FR-004 / FR-006 (prereg A14): the memory REACH
    /// over random worlds and margins, derived independently -- the oracle
    /// computes reach from the cat's position, the remembered tile, the
    /// radius and the margin with its own Manhattan arithmetic, never from
    /// `known_relief`. The remembered tile is drawn AT the bound and one
    /// tile either side of it (a uniform tile hits the bound too rarely:
    /// the first cut of this property stayed green under a `<=` -> `<`
    /// mutation, redden-list U3), and the tested kind's need is made the
    /// top need, so every case is a live verdict. Eat, drink and play read
    /// the one rule; cuddle, bath and sleep never read the margin.
    /// `u32::MAX` exercises the saturating add (>= width + height is the
    /// key-absent rule). The key-absent property below is untouched
    /// (SC-003).
    #[test]
    fn the_reach_rule_holds_over_random_worlds_and_margins(
        seed in 0u64..5_000,
        radius in 2u32..=8,
        margin in prop::option::of(prop_oneof![0u32..=4, Just(u32::MAX)]),
        kind_ix in 0usize..4,
        at_bound in -1i64..=1,
        free_walk in 0u32..=12,
        split in 0.0f64..1.0,
        flip in (any::<bool>(), any::<bool>()),
        others in prop::collection::vec(0f32..50.0, 6),
    ) {
        let kind = [ElementType::Chow, ElementType::Water, ElementType::Bug, ElementType::Greeble][kind_ix];
        let (want, need) = match kind {
            ElementType::Chow => (MessageKind::WantEat, NeedKind::Eat),
            ElementType::Water => (MessageKind::WantDrink, NeedKind::Drink),
            _ => (MessageKind::WantPlay, NeedKind::Play),
        };
        // The walk to the remembered tile: at the bound (+/- 1) when the
        // margin is small; a free short walk when the reach is unbounded.
        let walk: i64 = match margin {
            Some(m) if m <= 4 => i64::from(radius + m) + at_bound,
            _ => i64::from(free_walk),
        };
        prop_assume!(walk >= 0);
        let dx = (walk as f64 * split).round() as i64;
        let dy = walk - dx;
        let (x, y) = (10 + if flip.0 { dx } else { -dx }, 10 + if flip.1 { dy } else { -dy });
        prop_assume!((0..20).contains(&x) && (0..20).contains(&y));
        let tile = Position::new(x as u32, y as u32);

        let mut config = test_config();
        config.world.width = 20;
        config.world.height = 20;
        config.world.seed = seed;
        config.vision.radius = radius;
        config.meow.relief_memory_margin = margin;
        config.kitties = [(1u32, 10u32, 10u32), (2, 3, 4), (3, 15, 15), (4, 8, 12)]
            .iter()
            .map(|&(id, x, y)| KittyConfig { id, name: format!("K{id}"), x, y, behavior: "needs_driven".into(), needs: None })
            .collect();
        config.validate().unwrap();
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        world.tick = 100;
        {
            let idx = world.kitty_index(1).unwrap();
            for (k, level) in NeedKind::ALL.iter().zip(others.iter()) {
                world.kitties[idx].needs.add(*k, *level);
                world.kitties[idx].announce_armed.insert(*k);
            }
            world.kitties[idx].needs.add(need, 60.0);
            for slot in world.kitties[idx].memory.iter_mut() {
                *slot = None;
            }
            world.kitties[idx].memory[memory_index(kind)] = Some(MemorySlot { pos: tile, last_seen: 90 });
        }
        let me = world.kitty(1).unwrap().clone();
        prop_assert_eq!(me.needs.highest_pressure().0, need, "the tested need is top");
        let view = world.snapshot().fog_for(1, radius);
        // The oracle's reach: Manhattan from the cat to the remembered tile,
        // against radius + margin, inclusive; absent = every slot counts.
        let manhattan = me.pos.x.abs_diff(tile.x) + me.pos.y.abs_diff(tile.y);
        prop_assert_eq!(i64::from(manhattan), walk);
        let within = margin.is_none_or(|m| manhattan <= radius.saturating_add(m));
        let visible = |k: ElementType| view.elements_of(k).next().is_some();
        let idle_in_view = view.others(1).any(|k| k.activity_clock.is_none());
        let relief = match kind {
            ElementType::Chow => visible(ElementType::Chow) || within,
            ElementType::Water => visible(ElementType::Water) || within,
            _ => idle_in_view || view.critters().next().is_some() || within,
        };
        let expected = !relief && config.meow.vocabulary.enabled(want);
        prop_assert_eq!(message_legal(&me, want, 100, &config, &view), expected, "{:?}: walk {}, radius {}, margin {:?}, relief {}", want, walk, radius, margin, relief);
        // The social words never read the margin: same verdict as key-absent.
        let mut unbounded = (*config).clone();
        unbounded.meow.relief_memory_margin = None;
        for social in [MessageKind::WantCuddle, MessageKind::WantBath, MessageKind::WantSleep] {
            prop_assert_eq!(
                message_legal(&me, social, 100, &config, &view),
                message_legal(&me, social, 100, &unbounded, &view),
                "{:?}: the margin moved a social verdict", social
            );
        }
    }

    #[test]
    fn the_law_holds_over_random_worlds(
        seed in 0u64..5_000,
        radius in 2u32..=8,
        needs in prop::collection::vec(0f32..100.0, 6),
        heard_call in prop::option::of((2u32..=4, 0u64..30, 0u32..20, 0u32..20)),
    ) {
        let mut config = test_config();
        config.world.width = 20;
        config.world.height = 20;
        config.world.seed = seed;
        config.vision.radius = radius;
        config.kitties = [(1u32, 10u32, 10u32), (2, 3, 4), (3, 15, 15), (4, 8, 12)]
            .iter()
            .map(|&(id, x, y)| KittyConfig { id, name: format!("K{id}"), x, y, behavior: "needs_driven".into(), needs: None })
            .collect();
        config.validate().unwrap();
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        world.tick = 100;
        {
            let idx = world.kitty_index(1).unwrap();
            for (kind, level) in NeedKind::ALL.iter().zip(needs.iter()) {
                world.kitties[idx].needs.add(*kind, *level);
                world.kitties[idx].announce_armed.insert(*kind);
            }
        }
        // A random friend calls from a random tile at a random age.
        if let Some((who, age, x, y)) = heard_call {
            world.recent_meows.push(meow(who, MessageKind::WantEat, 100 - age.min(99), x, y));
        }
        let me = world.kitty(1).unwrap().clone();
        let view = world.snapshot().fog_for(1, radius);
        let (top, _) = me.needs.highest_pressure();
        let visible = |kind: ElementType| view.elements_of(kind).next().is_some();
        let remembered = |kind: ElementType| me.memory[memory_index(kind)].is_some();
        let idle_in_view = view.others(1).any(|k| k.activity_clock.is_none());

        for want in [MessageKind::WantEat, MessageKind::WantDrink, MessageKind::WantPlay, MessageKind::WantCuddle, MessageKind::WantBath, MessageKind::WantSleep] {
            let need = want.related_need().unwrap();
            let relief = match want {
                MessageKind::WantEat => visible(ElementType::Chow) || remembered(ElementType::Chow),
                MessageKind::WantDrink => visible(ElementType::Water) || remembered(ElementType::Water),
                MessageKind::WantCuddle => idle_in_view,
                MessageKind::WantPlay => idle_in_view || view.critters().next().is_some() || remembered(ElementType::Bug) || remembered(ElementType::Greeble),
                _ => false,
            };
            let verdict = message_legal(&me, want, 100, &config, &view);
            let expected = match want {
                // An ask: armed (staged for every kind above), no top-need
                // clause, no relief gate.
                MessageKind::WantBath => config.meow.vocabulary.enabled(want),
                _ => need == top && !relief && config.meow.vocabulary.enabled(want),
            };
            prop_assert_eq!(verdict, expected, "{:?}: top {:?}, relief {}", want, top, relief);
            // A heard-unseen friend never changes a want verdict: drop the
            // call and re-judge.
            let mut quiet = world.snapshot();
            quiet.recent_meows.clear();
            let quiet_view = quiet.fog_for(1, radius);
            prop_assert_eq!(message_legal(&me, want, 100, &config, &quiet_view), verdict, "{:?}: hearing moved the want gate", want);
        }
        for (want, here) in WANT_HERE_PAIRS {
            let adjacent = match here {
                MessageKind::HereFood => cloudkitty_core::world::adjacent_stocked_chow_in(&view.elements, me.pos).is_some(),
                MessageKind::HereWater => cloudkitty_core::world::adjacent_element_in(&view.elements, me.pos, ElementType::Water).is_some(),
                MessageKind::HereSunbeam => cloudkitty_core::world::adjacent_element_in(&view.elements, me.pos, ElementType::Sunbeam).is_some(),
                _ => cloudkitty_core::world::adjacent_critter_in(&view.elements, me.pos),
            };
            let audible_want = view.recent_meows.iter().any(|m| m.kind == want && m.kitty_id != 1 && view.audible(m, config.meow.digest_window_ticks));
            let referent = cloudkitty_core::meow::referent_visible(here, &view);
            let expected = (adjacent || (audible_want && referent)) && config.meow.vocabulary.enabled(here);
            prop_assert_eq!(message_legal(&me, here, 100, &config, &view), expected, "{:?}", here);
            prop_assert_eq!(reply_condition(here, &view, &config), audible_want && referent);
        }
        // Heard rows point at the freshest audible stamp.
        for (id, pos, tick) in view.heard_unseen(config.meow.digest_window_ticks) {
            let freshest = view.recent_meows.iter().filter(|m| m.kitty_id == id && view.audible(m, config.meow.digest_window_ticks)).max_by_key(|m| m.tick).unwrap();
            prop_assert_eq!((pos, tick), (freshest.pos, freshest.tick));
            prop_assert!(view.kitty(id).is_none());
        }
    }
}
