//! Spec 049 SC-012: a blind exploring cat first sights a bowl within one
//! world crossing (≤ 40 ticks at 20×20) in every seeded trial with at
//! least one bowl present on a tile the FR-023 sweep can reach. The
//! persistent heading is what bounds the tail: the redraw rule (turn when
//! the wall ahead is within `radius`) walks the cat round the inner
//! square `[r, w−1−r]²`, whose discs cover every tile except a pocket of
//! ten in each corner (pinned below, OWNER FLAG). The per-step scenarios
//! and the draw-count rule live beside the behaviour (`needs_driven.rs`).

use std::sync::Arc;

use cloudkitty_core::config::{Config, KittyConfig};
use cloudkitty_core::element::{Element, ElementKind, ElementType};
use cloudkitty_core::kitty::memory_index;
use cloudkitty_core::test_support::{forget_everything, test_config};
use cloudkitty_core::{BehaviorRegistry, NeedKind, Position, World};

const R: u32 = 5;
const W: u32 = 20;
const START: Position = Position { x: 10, y: 10 };

/// Two cats far apart (no idle friend in view), kitty 1 the blind hungry
/// explorer at the centre of a 20×20 world at r = 5.
fn blind_world(seed: u64) -> (World, Arc<Config>) {
    let mut config = test_config();
    config.world.width = W;
    config.world.height = W;
    config.world.seed = 1000 + seed;
    config.vision.radius = R;
    config.kitties = vec![
        KittyConfig {
            id: 1,
            name: "Miso".into(),
            x: START.x,
            y: START.y,
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
    // No bowl but the one each test places; hungry, but below the pressure
    // at which the safeguard (75) would drop a bowl beside the cat inside
    // the window -- the sighting must be exploration's own.
    world
        .elements
        .retain(|e| e.element_type() != ElementType::Chow);
    forget_everything(&mut world);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].needs.add(NeedKind::Eat, 55.0);
    assert!(world.kitties[idx].memory[memory_index(ElementType::Chow)].is_none());
    (world, config)
}

fn bowl(pos: Position) -> Element {
    Element {
        id: 9000,
        kind: ElementKind::Chow { servings: 5 },
        pos,
        ttl: None,
    }
}

/// The tiles the FR-023 sweep can bring into view: within the disc of
/// some tile of the inner square's perimeter.
fn sweepable(t: Position) -> bool {
    let lo = R;
    let hi = W - 1 - R;
    (lo..=hi).any(|x| {
        [lo, hi]
            .iter()
            .any(|&y| Position::new(x, y).visible_from(&t, R))
            || [lo, hi]
                .iter()
                .any(|&x2| Position::new(x2, x).visible_from(&t, R))
    })
}

async fn first_sight(world: &mut World, config: &Arc<Config>, budget: u64) -> Option<u64> {
    let registry = BehaviorRegistry::with_builtins();
    for t in 1..=budget {
        world.tick(&registry, config).await;
        if world.kitty(1).unwrap().memory[memory_index(ElementType::Chow)].is_some() {
            return Some(t);
        }
    }
    None
}

#[tokio::test(flavor = "current_thread")]
async fn first_sight_within_one_crossing() {
    let candidates: Vec<Position> = (0..W)
        .flat_map(|x| (0..W).map(move |y| Position::new(x, y)))
        .filter(|t| !START.visible_from(t, R) && sweepable(*t))
        .collect();
    let mut worst = 0u64;
    for seed in 0..24u64 {
        let (mut world, config) = blind_world(seed);
        // A seed-chosen sweepable tile out of the starting disc, spread
        // across the candidate ring.
        let target = candidates[(seed as usize * 37) % candidates.len()];
        world.push_element(bowl(target));
        let t = first_sight(&mut world, &config, 40)
            .await
            .unwrap_or_else(|| {
                panic!("seed {seed}: bowl at {target:?} not sighted within 40 ticks")
            });
        worst = worst.max(t);
    }
    eprintln!("SC-012: worst first sight over 24 seeded blind trials = {worst} ticks");
    assert!(worst <= 40);
}

/// OWNER FLAG (spec 049 FR-023 / SC-012): the redraw rule as ruled --
/// turn when the wall ahead is within `radius` -- never brings a cat
/// closer than `radius` to any wall, so the disc never reaches the ten
/// tiles in each corner farther than `radius` from the inner square. A
/// bowl there is found only by the safeguard's rescue, not by
/// exploration. Pinned so the pocket is a recorded fact and this test
/// goes red the day the rule changes (then delete it and widen SC-012).
#[tokio::test(flavor = "current_thread")]
async fn the_corner_pockets_are_outside_the_sweep() {
    let pocket: Vec<Position> = (0..W)
        .flat_map(|x| (0..W).map(move |y| Position::new(x, y)))
        .filter(|t| !sweepable(*t))
        .collect();
    assert_eq!(
        pocket.len(),
        40,
        "ten tiles per corner at 20×20, r = 5: {pocket:?}"
    );
    assert!(pocket.contains(&Position::new(0, 0)));
    assert!(pocket.contains(&Position::new(4, 0)));
    assert!(
        !pocket.contains(&Position::new(1, 2)),
        "(1, 2) is seen from (5, 5)"
    );

    let (mut world, config) = blind_world(3);
    world.push_element(bowl(Position::new(0, 0)));
    let sighted = first_sight(&mut world, &config, 45).await;
    assert_eq!(
        sighted, None,
        "a corner bowl is not sighted by one full sweep (45 ticks > the 37-step loop)"
    );
}
