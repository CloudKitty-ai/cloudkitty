//! Spec 024 US3: the welfare ↔ validation equivalence guardrail.
//!
//! `zero_distance_relief_exists` (the welfare layer's zero-travel relief
//! predicate) and `action::validate` (Article IV's enforcement surface)
//! encode the same law in two places, and only the latter is
//! authoritative. This suite asserts, for every need kind over a fixture
//! matrix, that the metric never imagines relief the engine would refuse
//! and never denies relief the engine would grant — so any future drift
//! between the layers becomes a red test instead of silent certification
//! skew (the spec 021 detour's salvage; `mask_oracle.rs` precedent:
//! engine as oracle, no carve-outs).
//!
//! The relieving-action set per need is spec knowledge (spec 019's
//! need→relief pairing, restated here from the public record), NOT an
//! import from the behavior layer — the measuring layer must not know how
//! the built-in behaviors think, only what the engine allows:
//!   Eat → `Eat` · Drink → `Drink` · Bath → solo `Groom` ·
//!   Sleep → solo `Sleep` · Play → solo `Play` ·
//!   Cuddle → `Sleep { with }` or `Groom { target }` at an adjacent
//!   kitty (adjacency alone suffices — busy neighbors ARE lawful relief,
//!   docs/cuddle-relief-semantics.md; only `Rest { with }` conscripts).

use std::sync::Arc;

use cloudkitty_core::action::{self, Action};
use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::Position;
use cloudkitty_core::kitty::{Activity, ActivityClock};
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{Config, World};
use cloudkitty_rl::welfare::zero_distance_relief_exists;

const SUBJECT: u32 = 1;

#[derive(Debug, Clone, Copy)]
enum Neighbor {
    AdjacentFree,
    AdjacentBusy,
    Absent,
}

/// The relief-element axis. `None` is the bare-tile case; consumed chow
/// (zero servings) is the cell that caught the pre-024 eat divergence.
/// Water/sunbeam have no "consumed" state — the impossible cells are
/// skipped by not existing in this enumeration.
#[derive(Debug, Clone, Copy)]
enum ReliefElement {
    None,
    StockedChow,
    ConsumedChow,
    Water,
}

fn build(neighbor: Neighbor, relief: ReliefElement) -> (World, Arc<Config>) {
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    world.elements.clear();

    let s = world.kitty_index(SUBJECT).unwrap();
    world.kitties[s].pos = Position::new(10, 10);

    let n = world.kitty_index(2).unwrap();
    match neighbor {
        Neighbor::Absent => world.kitties[n].pos = Position::new(25, 25),
        Neighbor::AdjacentFree => {
            world.kitties[n].pos = Position::new(10, 11);
            world.kitties[n].activity = Activity::Idle;
            world.kitties[n].activity_clock = None;
        }
        Neighbor::AdjacentBusy => {
            world.kitties[n].pos = Position::new(10, 11);
            world.kitties[n].activity = Activity::Resting { with_friend: None };
            world.kitties[n].activity_clock = Some(ActivityClock::start(0));
        }
    }
    // The third default-roster cat watches from afar in every cell.
    let t = world.kitty_index(3).unwrap();
    world.kitties[t].pos = Position::new(27, 27);

    let kind = match relief {
        ReliefElement::None => None,
        ReliefElement::StockedChow => Some(ElementKind::Chow { servings: 3 }),
        ReliefElement::ConsumedChow => Some(ElementKind::Chow { servings: 0 }),
        ReliefElement::Water => Some(ElementKind::Water),
    };
    if let Some(kind) = kind {
        world.push_element(Element {
            id: 700,
            kind,
            pos: Position::new(11, 10),
            ttl: None,
        });
    }
    (world, config)
}

/// "At least one lawful action relieving `kind` validates" — through the
/// public `validate` only, with the spec-019 relieving sets above.
fn lawful_relief_exists(world: &World, config: &Config, kind: NeedKind) -> bool {
    let validates = |a: Action| action::validate(world, SUBJECT, a.clone(), config) == a;
    match kind {
        NeedKind::Eat => validates(Action::Eat),
        NeedKind::Drink => validates(Action::Drink),
        NeedKind::Bath => validates(Action::Groom { target: None }),
        NeedKind::Sleep => validates(Action::Sleep { with: None }),
        NeedKind::Play => validates(Action::play_solo()),
        NeedKind::Cuddle => world
            .kitties
            .iter()
            .filter(|k| k.id != SUBJECT)
            .any(|k| {
                validates(Action::Sleep { with: Some(k.id) })
                    || validates(Action::Groom { target: Some(k.id) })
            }),
    }
}

#[test]
fn the_metric_and_the_law_agree_on_every_cell() {
    let neighbors = [
        Neighbor::AdjacentFree,
        Neighbor::AdjacentBusy,
        Neighbor::Absent,
    ];
    let reliefs = [
        ReliefElement::None,
        ReliefElement::StockedChow,
        ReliefElement::ConsumedChow,
        ReliefElement::Water,
    ];
    for neighbor in neighbors {
        for relief in reliefs {
            let (world, config) = build(neighbor, relief);
            let idx = world.kitty_index(SUBJECT).unwrap();
            for kind in NeedKind::ALL {
                let metric = zero_distance_relief_exists(&world, idx, kind);
                let law = lawful_relief_exists(&world, &config, kind);
                assert_eq!(
                    metric, law,
                    "divergence at {neighbor:?} x {relief:?} for {kind:?}: \
                     the metric says {metric}, the engine says {law}"
                );
            }
        }
    }
}

#[test]
fn the_busy_neighbor_cell_pins_the_cuddle_doctrine_on_true() {
    // Spec 021's lesson, held against regression in EITHER layer: a busy
    // adjacent neighbor is lawful cuddle relief (Sleep-with and
    // Groom-target need adjacency alone), and the metric agrees. A future
    // change that narrows either side turns this red.
    let (world, config) = build(Neighbor::AdjacentBusy, ReliefElement::None);
    let idx = world.kitty_index(SUBJECT).unwrap();
    assert!(zero_distance_relief_exists(&world, idx, NeedKind::Cuddle));
    assert!(lawful_relief_exists(&world, &config, NeedKind::Cuddle));
}

#[test]
fn the_consumed_bowl_cell_pins_the_eat_reconciliation() {
    // The divergence the guardrail caught before it was written: an empty
    // adjacent bowl is relief to neither layer now.
    let (world, config) = build(Neighbor::Absent, ReliefElement::ConsumedChow);
    let idx = world.kitty_index(SUBJECT).unwrap();
    assert!(!zero_distance_relief_exists(&world, idx, NeedKind::Eat));
    assert!(!lawful_relief_exists(&world, &config, NeedKind::Eat));

    let (world, config) = build(Neighbor::Absent, ReliefElement::StockedChow);
    let idx = world.kitty_index(SUBJECT).unwrap();
    assert!(zero_distance_relief_exists(&world, idx, NeedKind::Eat));
    assert!(lawful_relief_exists(&world, &config, NeedKind::Eat));
}
