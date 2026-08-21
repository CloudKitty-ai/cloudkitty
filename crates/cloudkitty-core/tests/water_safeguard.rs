//! The runtime half of spec 024 FR-004's executable guard.
//!
//! `validate_water` already makes the hazard unrepresentable at load time
//! (ceiling + largest trait-scaled charge < safeguard). This suite proves
//! the running engine honors the same law: bath moves in gated steps —
//! water may charge only below the ceiling, so no charge can ever jump a
//! cat across the safeguard line. Whatever crosses a threshold crosses it
//! at ambient pace, water contributing nothing from the ceiling up.

use std::sync::Arc;

use cloudkitty_core::behavior::test_behaviors::AlwaysInvalid;
use cloudkitty_core::config::NeedRateOverrides;
use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::Position;
use cloudkitty_core::{BehaviorRegistry, Config, NeedKind, World};

fn registry() -> BehaviorRegistry {
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("always_invalid", Arc::new(AlwaysInvalid));
    registry
}

/// Pin `kitty_id` back onto `wet` — unless a companion happens to be
/// standing there this tick (teleporting onto it would fake a two-cats-
/// one-tile state no real walk can produce; skipping a tick keeps the
/// scenario honest and the pin resumes as soon as the tile clears).
fn pin(world: &mut World, kitty_id: u32, wet: Position) {
    let occupied_by_other =
        world.kitty_at(wet).map(|k| k.id) != Some(kitty_id) && world.kitty_at(wet).is_some();
    if !occupied_by_other {
        let idx = world.kitty_index(kitty_id).unwrap();
        world.kitties[idx].pos = wet;
    }
}

/// A small controlled world: kitty 1 wears `behavior`, kitty 2 keeps the
/// default; one permanent water tile sits under kitty 1's paws.
fn pinned_world(mut config: Config, behavior: &str) -> (World, Arc<Config>, Position) {
    config.kitties[0].behavior = behavior.to_string();
    config.validate().expect("test config must be legal");
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let wet = world.kitties[0].pos;
    world.elements.push(Element {
        id: 9_900,
        kind: ElementKind::Water,
        pos: wet,
        ttl: None,
    });
    (world, config, wet)
}

/// The dial table: every corner of the legal `[water]` space the guard
/// must hold in, including a near-limit gain and a doubled trait. Each
/// entry must pass `validate` — the table exercises SC-002's "every legal
/// dial" clause at its extremes rather than sampling politely.
fn dial_table() -> Vec<Config> {
    let mut table = Vec::new();

    // The shipped defaults.
    table.push(Config::default());

    // Near the validation limit: 60 + 14 = 74 < 75.
    let mut hot = Config::default();
    hot.water.bath_gain = 14.0;
    table.push(hot);

    // A tiny ceiling: charges stop almost immediately.
    let mut low = Config::default();
    low.water.bath_gain_ceiling = 5.0;
    table.push(low);

    // A doubled bath trait riding a gain sized so the scaled charge still
    // clears validation: 60 + 7x2 = 74 < 75.
    let mut fussy = Config::default();
    fussy.water.bath_gain = 7.0;
    fussy.kitties[0].needs = Some(NeedRateOverrides {
        bath: Some(fussy.needs.bath * 2.0),
        ..Default::default()
    });
    table.push(fussy);

    table
}

/// Mechanism guard: a cat that idles forever on a water tile (the engine
/// converts `AlwaysInvalid`'s proposals to idle turns, so it never grooms
/// and never leaves) has its bath walk upward in gated steps. From the
/// ceiling up, every step is ambient-sized: the charge is provably off.
#[tokio::test]
async fn bath_moves_in_gated_steps_at_every_legal_dial() {
    for config in dial_table() {
        let (mut world, config, wet) = pinned_world(config, "always_invalid");
        let registry = registry();
        let kitty_id = world.kitties[0].id;

        let ratio = config.bath_ratio(kitty_id);
        let ambient = config.need_rate_for(kitty_id, NeedKind::Bath);
        let charge = config.water.bath_gain * ratio;
        let ceiling = config.water.bath_gain_ceiling;
        let safeguard = config.thresholds.safeguard;
        assert!(
            ceiling + charge < safeguard,
            "the table entry must be legal by the validation arithmetic"
        );

        let mut crossed_at_ambient_pace = true;
        let mut reached_ceiling = false;
        for _ in 0..2_000 {
            pin(&mut world, kitty_id, wet); // the most hostile swimmer
            let idx = world.kitty_index(kitty_id).unwrap();
            let before = world.kitties[idx].needs.get(NeedKind::Bath);
            world.tick(&registry, &config).await;
            let idx = world.kitty_index(kitty_id).unwrap();
            let after = world.kitties[idx].needs.get(NeedKind::Bath);
            let delta = after - before;

            // One tick can never add more than ambient + one charge.
            assert!(
                delta <= ambient + charge + 1e-3,
                "delta {delta} exceeds ambient {ambient} + charge {charge}"
            );
            // From the ceiling up, water contributes nothing.
            if before >= ceiling {
                reached_ceiling = true;
                assert!(
                    delta <= ambient + 1e-3,
                    "above the ceiling ({before}) only ambient may apply, got {delta}"
                );
            }
            // A threshold crossing is therefore always ambient-paced.
            if before < safeguard && after >= safeguard && delta > ambient + 1e-3 {
                crossed_at_ambient_pace = false;
            }
        }
        assert!(
            crossed_at_ambient_pace,
            "no charge may carry a cat across the safeguard line"
        );
        assert!(
            reached_ceiling,
            "the scenario must actually exercise the ceiling to prove anything"
        );
    }
}

/// Behavior guard — the spec's own wording: no *voluntary* sequence of
/// moves ever produces Bath distress. Free-roaming default-ladder cats in
/// a deliberately flooded world (water at its config hard cap) cross and
/// lounge as their own pricing dictates, at every dial in the table, and
/// Bath distress never occurs: grooming is bath's relief and works
/// anywhere, so a cat that can move can always groom long before the
/// distress line. (A teleport-pinned cat is deliberately NOT this test:
/// pinning revokes the mobility the relief guarantee assumes, starves
/// every location-based need to 100, and produces distress that has
/// nothing to do with water — the mechanism test above covers hostile
/// occupancy instead.)
#[tokio::test]
async fn voluntary_swimming_in_a_flooded_world_never_reaches_bath_distress() {
    use cloudkitty_core::config::ElementRule;

    for mut config in dial_table() {
        // Flood the meadow: water at the hard cap for the default world
        // area, permanent, so dry detours are often expensive and real
        // crossings actually happen.
        let area = config.world.width * config.world.height;
        let cap = cloudkitty_core::config::ElementsConfig::hard_max(area).max(1);
        config.elements.water = ElementRule {
            min: cap,
            max: cap,
            ttl: None,
            servings: None,
            roam_cell: None,
        };
        config.validate().expect("flooded config is legal");
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        let registry = registry();

        for _ in 0..5_000 {
            world.tick(&registry, &config).await;
            assert!(
                !world.distress.events().any(|e| e.need == NeedKind::Bath),
                "no voluntary swim may produce Bath distress (tick {})",
                world.tick
            );
        }
    }
}

/// The lounging picture, in one fixture: bath accrues to the ceiling and
/// the charges stop — priced, never punished (spec 024 US1, Article I).
#[tokio::test]
async fn lounging_accrues_to_the_ceiling_then_stops() {
    let (mut world, config, wet) = pinned_world(Config::default(), "always_invalid");
    let registry = registry();
    let kitty_id = world.kitties[0].id;
    let ceiling = config.water.bath_gain_ceiling;
    let charge = config.water.bath_gain;

    let mut first_at_or_above = None;
    for _ in 0..200 {
        pin(&mut world, kitty_id, wet);
        world.tick(&registry, &config).await;
        let idx = world.kitty_index(kitty_id).unwrap();
        let bath = world.kitties[idx].needs.get(NeedKind::Bath);
        if bath >= ceiling {
            first_at_or_above = Some(bath);
            break;
        }
    }
    let arrived = first_at_or_above.expect("a lounging cat reaches the ceiling");
    assert!(
        arrived <= ceiling + charge + config.needs.bath + 1e-3,
        "overshoot is bounded by one charge: arrived at {arrived}"
    );
}

/// However a cat arrives on water — walked, chased, sidestepped — standing
/// there pays the same occupancy charge: the mechanic keys on position,
/// never on the action that produced it (spec 024 edge case).
#[tokio::test]
async fn a_chase_that_lands_on_water_pays_like_any_lounger() {
    use cloudkitty_core::action::{self, Action, TargetRef};

    let mut config = Config::default();
    config.kitties[0].behavior = "always_invalid".to_string();
    config.validate().expect("legal");
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let registry = registry();
    let kitty_id = world.kitties[0].id;

    // The lane: cat at P, water one step east, a bug beyond it.
    let p = world.kitties[0].pos;
    let wet = Position::new(p.x + 1, p.y);
    let bug_pos = Position::new(p.x + 3, p.y);
    if let Some(blocker) = world.kitty_at(wet).map(|k| k.id) {
        let idx = world.kitty_index(blocker).unwrap();
        world.kitties[idx].pos = Position::new(p.x, p.y + 2);
    }
    world.elements.push(Element {
        id: 9_901,
        kind: ElementKind::Water,
        pos: wet,
        ttl: None,
    });
    world.elements.push(Element {
        id: 9_902,
        kind: ElementKind::Bug,
        pos: bug_pos,
        ttl: None,
    });

    // The chase step itself lands the cat on the water tile.
    action::apply(
        &mut world,
        kitty_id,
        Action::Chase(TargetRef::Element { id: 9_902 }),
        &config,
    );
    let idx = world.kitty_index(kitty_id).unwrap();
    assert_eq!(world.kitties[idx].pos, wet, "the chase stepped onto water");

    // The next tick's needs phase charges it exactly like a lounger
    // (the always-idle mind guarantees it is still standing there).
    let before = world.kitties[idx].needs.get(NeedKind::Bath);
    world.tick(&registry, &config).await;
    let idx = world.kitty_index(kitty_id).unwrap();
    let after = world.kitties[idx].needs.get(NeedKind::Bath);
    let expected = config.needs.bath + config.water.bath_gain;
    assert!(
        (after - before - expected).abs() < 1e-3,
        "chased-onto water pays ambient + charge: delta {}",
        after - before
    );
}
