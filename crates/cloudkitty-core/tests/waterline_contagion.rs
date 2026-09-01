//! Spec 044: waterline contagion — the armed half.
//!
//! `[water] contagion_factor` at 0.0 is proven inert by the stamp guard,
//! golden and determinism suites. This file pins what a nonzero factor
//! DOES: a dry cat whose own activity names a partner standing in water
//! accrues `factor * bath_gain * bath_ratio(self)` per tick, gated by the
//! same pre-charge ceiling as occupancy — and everything the charge must
//! NOT touch (the wet member, referenced-but-not-naming cats, solo and
//! critter scenes, the RNG stream).
//!
//! Harness: the `water_safeguard.rs` pinned-world idiom. Both cats wear
//! `always_invalid` so the engine converts every proposal to an idle turn
//! and the only activities in play are the ones a test sets directly;
//! generated water is stripped so the single wet tile is the one the test
//! placed. Activities are set with their governing need mid-range so the
//! scene survives the tick's end-resolution phase.

use std::sync::Arc;

use cloudkitty_core::behavior::test_behaviors::AlwaysInvalid;
use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::Position;
use cloudkitty_core::kitty::{Activity, ActivityClock};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, Config, ElementType, KittyId, NeedKind, TargetRef, World};

/// The dry cat (test_config's Miso, id 1) and the wet cat (Biscuit, id 2).
const DRY_CAT: KittyId = 1;
const WET_CAT: KittyId = 2;
const WET_TILE: Position = Position { x: 8, y: 8 };
const DRY_TILE: Position = Position { x: 8, y: 9 };

fn registry() -> BehaviorRegistry {
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("always_invalid", Arc::new(AlwaysInvalid));
    registry
}

/// A controlled world: both cats idle-locked and adjacent, one permanent
/// water tile under the wet cat's paws, no other water anywhere. The
/// pushed tile satisfies the element rule's min of 1 on its own, so the
/// spawner never mints a second wet tile under the dry cat mid-test.
fn contagion_world(factor: f32) -> (World, Arc<Config>) {
    let mut config = test_config();
    config.kitties[0].behavior = "always_invalid".into();
    config.kitties[1].behavior = "always_invalid".into();
    config.water.contagion_factor = factor;
    config.validate().expect("test config must be legal");
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    world
        .elements
        .retain(|el| el.element_type() != ElementType::Water);
    world.elements.push(Element {
        id: 9_900,
        kind: ElementKind::Water,
        pos: WET_TILE,
        ttl: None,
    });
    place(&mut world, WET_CAT, WET_TILE);
    place(&mut world, DRY_CAT, DRY_TILE);
    (world, config)
}

fn place(world: &mut World, id: KittyId, pos: Position) {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].pos = pos;
}

fn set_need(world: &mut World, id: KittyId, kind: NeedKind, value: f32) {
    let idx = world.kitty_index(id).unwrap();
    let current = world.kitties[idx].needs.get(kind);
    world.kitties[idx].needs.add(kind, value - current);
}

fn need(world: &World, id: KittyId, kind: NeedKind) -> f32 {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].needs.get(kind)
}

/// Start `activity` on `id` this tick, clock and governing need arranged
/// so the scene survives into the needs phase.
fn set_scene(world: &mut World, id: KittyId, activity: Activity) {
    if let Some(kind) = activity.governing_need() {
        set_need(world, id, kind, 50.0);
    }
    let tick = world.tick;
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].activity = activity;
    world.kitties[idx].activity_clock = Some(ActivityClock::start(tick));
}

/// The contagion charge the spec promises `id` per tick (FR-003).
fn charge(config: &Config, id: KittyId) -> f32 {
    config.water.contagion_factor * config.water.bath_gain * config.bath_ratio(id)
}

async fn tick_once(world: &mut World, config: &Arc<Config>) {
    world.tick(&registry(), config).await;
}

const TOL: f32 = 1e-4;

/// One scene per paired activity kind where the DRY cat's own activity
/// names the wet partner: bath rises by ambient + the scaled charge
/// (FR-003, SC-002). Grooming is the kind whose relief touches bath, but
/// it touches the TARGET's — the dry groomer's own bath sees only
/// ambient + charge.
#[tokio::test(flavor = "current_thread")]
async fn a_dry_cat_naming_a_wet_partner_pays_the_charge_in_every_paired_kind() {
    let scenes: [(&str, Activity); 4] = [
        (
            "resting",
            Activity::Resting {
                with_friend: Some(WET_CAT),
            },
        ),
        (
            "co-sleeping",
            Activity::Sleeping {
                in_sunbeam: false,
                with_friend: Some(WET_CAT),
            },
        ),
        (
            "playing",
            Activity::Playing {
                target: Some(TargetRef::Kitty { id: WET_CAT }),
            },
        ),
        (
            "grooming",
            Activity::Grooming {
                target: Some(WET_CAT),
            },
        ),
    ];
    for (name, activity) in scenes {
        let (mut world, config) = contagion_world(1.0);
        set_scene(&mut world, DRY_CAT, activity);
        if matches!(activity, Activity::Playing { .. }) {
            // Play is reciprocal by construction (spec 009): both members
            // hold the duet or the invariants refuse the world.
            set_scene(
                &mut world,
                WET_CAT,
                Activity::Playing {
                    target: Some(TargetRef::Kitty { id: DRY_CAT }),
                },
            );
        }
        set_need(&mut world, DRY_CAT, NeedKind::Bath, 10.0);
        let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
        let before = need(&world, DRY_CAT, NeedKind::Bath);
        tick_once(&mut world, &config).await;
        let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
        let expected = ambient + charge(&config, DRY_CAT);
        assert!(
            (delta - expected).abs() < TOL,
            "{name}: dry member's bath moved {delta}, expected ambient + \
             charge = {expected}"
        );
    }
}

/// FR-005: the wet member pays occupancy, never contagion on top — its
/// rise is exactly ambient + the occupancy charge even while its own
/// activity names the dry partner (a scene, but the partner is not in
/// water, and a wet cat is exempt regardless).
#[tokio::test(flavor = "current_thread")]
async fn the_wet_member_pays_occupancy_and_nothing_more() {
    let (mut world, config) = contagion_world(1.0);
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    set_scene(
        &mut world,
        WET_CAT,
        Activity::Resting {
            with_friend: Some(DRY_CAT),
        },
    );
    set_need(&mut world, WET_CAT, NeedKind::Bath, 10.0);
    let ambient = config.need_rate_for(WET_CAT, NeedKind::Bath);
    let occupancy = config.water.bath_gain * config.bath_ratio(WET_CAT);
    let before = need(&world, WET_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, WET_CAT, NeedKind::Bath) - before;
    let expected = ambient + occupancy;
    assert!(
        (delta - expected).abs() < TOL,
        "wet member's bath moved {delta}, expected exactly ambient + \
         occupancy = {expected} (never + contagion)"
    );
}

/// Review finding 1: the factor is a real multiplier, not a switch. The
/// rest of this suite runs at 0.0 (arm off) or 1.0 (the identity), so
/// only this scene notices a charge line that drops or hardcodes the
/// factor. 2.0 is legal on the test world: 60 + 2 x 3.5 = 67 < 75.
#[tokio::test(flavor = "current_thread")]
async fn the_factor_scales_the_charge() {
    let (mut world, config) = contagion_world(2.0);
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let expected = ambient + charge(&config, DRY_CAT);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - expected).abs() < TOL,
        "at factor 2.0 the charge must double: moved {delta}, expected \
         ambient + 2 x gain x ratio = {expected}"
    );
}

/// FR-004: the ceiling gates the PRE-charge value, same as occupancy. At
/// the ceiling the dry member accrues ambient only; just below it, one
/// full scaled charge still lands (overshoot bounded by one charge).
#[tokio::test(flavor = "current_thread")]
async fn the_ceiling_gates_the_charge_on_the_pre_charge_value() {
    // At the ceiling — EXACTLY at it. The gate reads after this tick's
    // ambient rise, so the seed is walked by ulps until seeding + ambient
    // reproduces the ceiling bit-for-bit (review finding 5: a seed OF the
    // ceiling reads ceiling + ambient at the gate, which both `<` and
    // `<=` refuse — the boundary itself was unpinned). With the read
    // exactly on the line, only strict `<` refuses the charge.
    let (mut world, config) = contagion_world(1.0);
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    let ceiling = config.water.bath_gain_ceiling;
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let mut seed = ceiling - ambient;
    for _ in 0..8 {
        set_need(&mut world, DRY_CAT, NeedKind::Bath, seed);
        let stored = need(&world, DRY_CAT, NeedKind::Bath);
        let at_gate = stored + ambient;
        if at_gate == ceiling {
            break;
        }
        seed = if at_gate < ceiling {
            f32::from_bits(stored.to_bits() + 1)
        } else {
            f32::from_bits(stored.to_bits() - 1)
        };
    }
    assert_eq!(
        need(&world, DRY_CAT, NeedKind::Bath) + ambient,
        ceiling,
        "the harness must land the gate read exactly on the ceiling"
    );
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - ambient).abs() < TOL,
        "at the ceiling the charge must be off: moved {delta}, ambient is \
         {ambient}"
    );

    // Just below it: the gate reads the pre-charge value, so the full
    // charge lands and the overshoot past the ceiling is bounded by
    // exactly one scaled charge (plus this tick's ambient rise, which
    // lands before the gate reads).
    let (mut world, config) = contagion_world(1.0);
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    // The gate reads AFTER this tick's ambient rise (the occupancy
    // semantics it mirrors), so start far enough under the ceiling that
    // ambient cannot cross it first.
    let just_under =
        config.water.bath_gain_ceiling - config.need_rate_for(DRY_CAT, NeedKind::Bath) - 0.1;
    set_need(&mut world, DRY_CAT, NeedKind::Bath, just_under);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    let expected = config.need_rate_for(DRY_CAT, NeedKind::Bath) + charge(&config, DRY_CAT);
    assert!(
        (delta - expected).abs() < TOL,
        "just under the ceiling the full charge lands: moved {delta}, \
         expected {expected}"
    );
}

/// The nothing-cases: scenes and states the charge must ignore. Each
/// measured cat accrues ambient exactly (or, for the both-wet pair,
/// ambient + occupancy exactly — the else-if arm can never stack
/// contagion on occupancy).
#[tokio::test(flavor = "current_thread")]
async fn no_charge_without_a_wet_named_partner() {
    // Both dry: a scene with nobody in water prices nothing.
    let (mut world, config) = contagion_world(1.0);
    place(&mut world, WET_CAT, Position { x: 9, y: 9 }); // off the water
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    set_need(&mut world, DRY_CAT, NeedKind::Bath, 10.0);
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - ambient).abs() < TOL,
        "both dry: moved {delta}, expected ambient {ambient}"
    );

    // Both wet: each pays occupancy once; the mutually-exclusive arm can
    // never add contagion on top (the structural no-double-pay pin).
    let (mut world, config) = contagion_world(1.0);
    world.elements.push(Element {
        id: 9_901,
        kind: ElementKind::Water,
        pos: DRY_TILE,
        ttl: None,
    });
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Resting {
            with_friend: Some(WET_CAT),
        },
    );
    set_scene(
        &mut world,
        WET_CAT,
        Activity::Resting {
            with_friend: Some(DRY_CAT),
        },
    );
    for id in [DRY_CAT, WET_CAT] {
        set_need(&mut world, id, NeedKind::Bath, 10.0);
    }
    let before: Vec<f32> = [DRY_CAT, WET_CAT]
        .iter()
        .map(|&id| need(&world, id, NeedKind::Bath))
        .collect();
    tick_once(&mut world, &config).await;
    for (i, id) in [DRY_CAT, WET_CAT].into_iter().enumerate() {
        let delta = need(&world, id, NeedKind::Bath) - before[i];
        let expected = config.need_rate_for(id, NeedKind::Bath)
            + config.water.bath_gain * config.bath_ratio(id);
        assert!(
            (delta - expected).abs() < TOL,
            "both wet, cat {id}: moved {delta}, expected occupancy only \
             ({expected}) — contagion must never stack"
        );
    }

    // Critter play beside a wet cat: the target is an element, not a
    // partner, and partner() is None (FR-003 reads the named KITTY).
    let (mut world, config) = contagion_world(1.0);
    world.elements.push(Element {
        id: 9_902,
        kind: ElementKind::Bug,
        pos: Position { x: 7, y: 9 },
        ttl: Some(300),
    });
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Playing {
            target: Some(TargetRef::Element { id: 9_902 }),
        },
    );
    set_need(&mut world, DRY_CAT, NeedKind::Bath, 10.0);
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - ambient).abs() < TOL,
        "critter play: moved {delta}, expected ambient {ambient}"
    );

    // Solo activity beside a wet cat: no partner, no price.
    let (mut world, config) = contagion_world(1.0);
    set_scene(
        &mut world,
        DRY_CAT,
        Activity::Sleeping {
            in_sunbeam: false,
            with_friend: None,
        },
    );
    set_need(&mut world, DRY_CAT, NeedKind::Bath, 10.0);
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - ambient).abs() < TOL,
        "solo sleep: moved {delta}, expected ambient {ambient}"
    );
}

/// THE Option A pin (clarified 2026-08-31): scene membership is read from
/// a cat's OWN activity. A cat merely referenced by a wet cat's activity
/// pays nothing.
#[tokio::test(flavor = "current_thread")]
async fn a_referenced_cat_whose_own_activity_names_nobody_pays_nothing() {
    // Direct reading: the wet cat rests naming the dry cat; the dry cat
    // is idle. Rest touches cuddle only, so the dry cat's bath must move
    // by ambient exactly.
    let (mut world, config) = contagion_world(1.0);
    set_scene(
        &mut world,
        WET_CAT,
        Activity::Resting {
            with_friend: Some(DRY_CAT),
        },
    );
    set_need(&mut world, DRY_CAT, NeedKind::Bath, 10.0);
    let ambient = config.need_rate_for(DRY_CAT, NeedKind::Bath);
    let before = need(&world, DRY_CAT, NeedKind::Bath);
    tick_once(&mut world, &config).await;
    let delta = need(&world, DRY_CAT, NeedKind::Bath) - before;
    assert!(
        (delta - ambient).abs() < TOL,
        "referenced-only cat moved {delta}, expected ambient {ambient}"
    );

    // The groomee form, differentially: grooming relieves the TARGET's
    // bath, so instead of predicting the relief arithmetic, run the
    // identical wet-groomer/idle-groomee tick at factor 0.0 and 1.0 —
    // nobody in this scene qualifies for contagion under Option A, so
    // the two worlds must not differ anywhere.
    let mut fingerprints = Vec::new();
    for factor in [0.0, 1.0] {
        let (mut world, config) = contagion_world(factor);
        set_scene(
            &mut world,
            WET_CAT,
            Activity::Grooming {
                target: Some(DRY_CAT),
            },
        );
        set_need(&mut world, DRY_CAT, NeedKind::Bath, 30.0);
        tick_once(&mut world, &config).await;
        fingerprints.push(serde_json::to_string(&world).expect("worlds serialize"));
    }
    assert_eq!(
        fingerprints[0], fingerprints[1],
        "an idle groomee of a wet groomer pays nothing: factor 1.0 must \
         change NOTHING about this scene vs factor 0.0"
    );
}

/// FR-008 / SC-005, the armed half of Article V: the charge draws no RNG
/// and reads pre-loop snapshots, so a factor-1.0 world is as reproducible
/// as a silent one — and an explicit `contagion_factor = 0.0` config is
/// byte-identical to one that never wrote the key (spec US1 scenario 2:
/// explicit zero ≡ absent, everywhere).
#[tokio::test(flavor = "current_thread")]
async fn armed_runs_are_deterministic_and_explicit_zero_is_absent() {
    async fn run(config: &Arc<Config>, ticks: u64) -> String {
        let registry = registry();
        let mut world = World::generate(config);
        for _ in 0..ticks {
            world.tick(&registry, config).await;
        }
        serde_json::to_string(&world).expect("worlds serialize")
    }

    // Two same-seed runs at the Gen 1 factor, real behaviors, 500 ticks.
    let mut armed = test_config();
    armed.water.contagion_factor = 1.0;
    armed.validate().expect("armed test config must be legal");
    let armed = Arc::new(armed);
    assert_eq!(
        run(&armed, 500).await,
        run(&armed, 500).await,
        "two same-seed factor-1.0 runs diverged"
    );

    // Explicit zero ≡ absent: parse both shapes from TOML (the surface
    // every real world config comes through) and run them.
    let absent_toml = toml::to_string(&test_config()).expect("configs serialize");
    assert!(
        !absent_toml.contains("contagion_factor"),
        "the default serialization must not carry the key: {absent_toml}"
    );
    let zero_toml = absent_toml.replace("[water]\n", "[water]\ncontagion_factor = 0.0\n");
    assert_ne!(
        absent_toml, zero_toml,
        "the explicit arm must differ on disk"
    );
    let absent: Config = toml::from_str(&absent_toml).expect("absent arm parses");
    let zero: Config = toml::from_str(&zero_toml).expect("explicit-zero arm parses");
    assert_eq!(
        absent, zero,
        "explicit 0.0 and absent must be the same config"
    );
    let absent = Arc::new(absent);
    let zero = Arc::new(zero);
    assert_eq!(
        run(&absent, 500).await,
        run(&zero, 500).await,
        "explicit contagion_factor = 0.0 must be byte-identical to the \
         key-absent world"
    );
}
