//! Spec 067 engine tests: the needy law wired into the world — state at
//! generation, the Phase 4 step and onset sweep, the fog blank, the
//! pairing invariant, resume (tasks T004); the apply-slot verdict and its
//! refusal reason (T006) and the integration scenarios (T008) join here.

use std::sync::Arc;

use super::*;
use crate::action::Action;
use crate::config::{Config, WelfareHazardConfig};
use crate::element::{Element, ElementKind};
use crate::grid::Position;
use crate::kitty::Activity;
use crate::seam::JointProposal;
use crate::test_support::test_config;
use crate::world::World;

/// `test_config()` with kitty 1 (Miso) seated on `preset`, acknowledged.
pub(super) fn seated(preset: &str) -> Config {
    let mut c = test_config();
    c.kitties[0].behavior = preset.to_string();
    c.welfare_hazard = Some(WelfareHazardConfig {
        acknowledged: vec![preset.to_string()],
    });
    c.validate().expect("an acknowledged needy seat validates");
    c
}

pub(super) fn kitty_mut(world: &mut World, id: KittyId) -> &mut crate::kitty::Kitty {
    let idx = world.kitty_index(id).expect("rostered");
    &mut world.kitties[idx]
}

pub(super) fn state(world: &World, id: KittyId) -> &NeedyState {
    world
        .kitty(id)
        .and_then(|k| k.needy.as_ref())
        .expect("a needy seat carries state")
}

/// Holds the seat's schedule off (no onset) while a test stages a scene.
pub(super) fn hold_off(world: &mut World, id: KittyId) {
    let s = kitty_mut(world, id).needy.as_mut().expect("needy seat");
    s.phase = Phase::Resting {
        next_onset: u64::MAX,
    };
}

/// Arms the seat to open an episode masking `masked` in the NEXT tick's
/// Phase 4 (the tick about to be published is `world.tick + 1`).
pub(super) fn open_next_tick(world: &mut World, id: KittyId, masked: &[NeedKind]) {
    let next_onset = world.tick + 1;
    let s = kitty_mut(world, id).needy.as_mut().expect("needy seat");
    s.next = NeedSet::from_kinds(masked);
    s.phase = Phase::Resting { next_onset };
}

/// One tick from explicit proposals (absent kitties idle).
pub(super) fn tick_with(world: &mut World, config: &Config, proposals: &[(KittyId, Action)]) {
    let joint = JointProposal::from_actions(proposals.iter().copied());
    world.tick_with_proposals(&joint, config);
}

/// Two kitties side by side at (5, 5) and (5, 6), elements cleared.
pub(super) fn side_by_side(world: &mut World) {
    world.elements.clear();
    kitty_mut(world, 1).pos = Position::new(5, 5);
    kitty_mut(world, 2).pos = Position::new(5, 6);
}

#[test]
fn a_plain_world_carries_no_needy_state() {
    let config = test_config();
    let world = World::generate(&config);
    assert!(
        world.kitties.iter().all(|k| k.needy.is_none()),
        "a plain world carries no needy state"
    );
    let json = serde_json::to_string(&world.snapshot()).unwrap();
    assert!(
        !json.contains("\"needy\""),
        "no needy key in a plain world's snapshot"
    );
}

#[test]
fn a_needy_seat_starts_resting_with_its_first_onset_inside_the_edges() {
    let config = seated(NAME);
    let world = World::generate(&config);
    let s = state(&world, 1);
    assert_eq!(s.ordinal, 0);
    assert!(!s.hold);
    let Phase::Resting { next_onset } = s.phase else {
        panic!("a fresh seat rests: {:?}", s.phase)
    };
    let edges = &crate::config::NeedyConfig::default().onset_levels;
    assert!(
        next_onset >= edges[0] && next_onset < *edges.last().unwrap(),
        "first onset {next_onset} inside the default edges {edges:?}"
    );
    assert_eq!(
        *s,
        NeedyState::new(config.world.seed, 1, false, &Default::default()),
        "the state is the law's, keyed off (world seed, kitty id)"
    );
    assert!(world.kitty(2).unwrap().needy.is_none(), "only the seat");

    let hold = World::generate(&seated(HOLD_NAME));
    assert!(state(&hold, 1).hold, "needy_hold seats the hold variant");
}

#[test]
fn the_onset_opens_on_the_laws_tick_and_ends_a_masked_meal() {
    let config = seated(NAME);
    let mut world = World::generate(&config);
    hold_off(&mut world, 1);
    world.elements.clear();
    kitty_mut(&mut world, 1).pos = Position::new(5, 5);
    kitty_mut(&mut world, 1).needs.add(NeedKind::Eat, 80.0);
    world.push_element(Element {
        id: 900,
        kind: ElementKind::Chow { servings: 50 },
        pos: Position::new(5, 6),
        ttl: None,
    });
    tick_with(&mut world, &config, &[(1, Action::Eat)]);
    assert_eq!(world.kitty(1).unwrap().activity, Activity::Eating, "staged");

    open_next_tick(&mut world, 1, &[NeedKind::Eat]);
    tick_with(&mut world, &config, &[(1, Action::Eat)]);
    let s = state(&world, 1);
    assert_eq!(
        s.phase,
        Phase::Held {
            onset: world.tick,
            masked: NeedSet::from_kinds(&[NeedKind::Eat]),
        },
        "phase is Held on the law's tick"
    );
    assert_eq!(s.ordinal, 1);
    assert_eq!(
        world.kitty(1).unwrap().activity,
        Activity::Idle,
        "the masked meal ended on the onset tick"
    );
}

#[test]
fn an_onset_drops_a_friends_cosleep_companion_and_its_own_sleep_goes_on() {
    let config = seated(NAME);
    let mut world = World::generate(&config);
    hold_off(&mut world, 1);
    side_by_side(&mut world);
    kitty_mut(&mut world, 1).needs.add(NeedKind::Cuddle, 50.0);
    kitty_mut(&mut world, 2).needs.add(NeedKind::Sleep, 80.0);
    tick_with(
        &mut world,
        &config,
        &[
            (1, Action::Rest { with: None }),
            (2, Action::Sleep { with: Some(1) }),
        ],
    );
    assert!(
        matches!(
            world.kitty(2).unwrap().activity,
            Activity::Sleeping {
                with_friend: Some(1),
                ..
            }
        ),
        "staged: the friend co-sleeps with the needy kitty"
    );

    open_next_tick(&mut world, 1, &[NeedKind::Cuddle]);
    tick_with(&mut world, &config, &[]);
    let cuddle_before = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
    let sleep_before = world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
    tick_with(&mut world, &config, &[]);
    assert!(
        world.kitty(1).unwrap().needs.get(NeedKind::Cuddle) > cuddle_before,
        "the masked cuddle only rose after the onset"
    );
    assert!(
        world.kitty(2).unwrap().needs.get(NeedKind::Sleep) < sleep_before,
        "the friend's own sleep relief goes on"
    );
    assert!(matches!(
        world.kitty(2).unwrap().activity,
        Activity::Sleeping {
            with_friend: None,
            ..
        }
    ));
}

#[test]
fn an_onset_ends_a_friends_groom_of_the_needy_kitty() {
    let config = seated(NAME);
    let mut world = World::generate(&config);
    hold_off(&mut world, 1);
    side_by_side(&mut world);
    kitty_mut(&mut world, 1).needs.add(NeedKind::Bath, 60.0);
    tick_with(
        &mut world,
        &config,
        &[(2, Action::Groom { target: Some(1) })],
    );
    assert_eq!(
        world.kitty(2).unwrap().activity,
        Activity::Grooming { target: Some(1) },
        "staged: the friend grooms the needy kitty"
    );

    open_next_tick(&mut world, 1, &[NeedKind::Bath]);
    tick_with(&mut world, &config, &[]);
    let bath_before = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
    tick_with(&mut world, &config, &[]);
    assert!(
        world.kitty(1).unwrap().needs.get(NeedKind::Bath) > bath_before,
        "the masked bath only rose after the onset"
    );
    assert_eq!(world.kitty(2).unwrap().activity, Activity::Idle);
}

#[test]
fn no_friend_sees_a_needy_kittys_state() {
    let config = seated(NAME);
    let world = World::generate(&config);
    let snapshot = world.snapshot();
    let friend_view = snapshot.fog_for(2, config.vision.radius);
    let seen = friend_view
        .kitties
        .iter()
        .find(|k| k.id == 1)
        .expect("the test world's radius covers the map");
    assert!(seen.needy.is_none(), "a friend never sees the needy state");
    let own_view = snapshot.fog_for(1, config.vision.radius);
    assert!(
        own_view
            .kitties
            .iter()
            .find(|k| k.id == 1)
            .unwrap()
            .needy
            .is_some(),
        "the needy kitty's own view keeps its state"
    );
}

#[test]
fn the_pairing_invariant_refuses_state_and_behaviour_out_of_step() {
    let config = seated(NAME);
    let mut world = World::generate(&config);
    crate::invariants::check(&world, &config).expect("a needy world is lawful");

    kitty_mut(&mut world, 1).behavior = "teacher".to_string();
    let err = crate::invariants::check(&world, &config)
        .expect_err("needy state on a teacher seat must be refused")
        .to_string();
    assert!(err.contains("carries needy state"), "{err}");

    kitty_mut(&mut world, 1).behavior = NAME.to_string();
    kitty_mut(&mut world, 1).needy = None;
    let err = crate::invariants::check(&world, &config)
        .expect_err("a needy seat without state must be refused")
        .to_string();
    assert!(err.contains("lacks needy state"), "{err}");
}

#[tokio::test]
async fn a_resumed_needy_world_ticks_identically() {
    let mut config = seated(NAME);
    config.needy = Some(crate::config::NeedyConfig {
        onset_levels: vec![0, 5, 20, 50, 100, 200],
        hold_ticks: 50,
        gap: crate::config::GapRange { min: 10, max: 30 },
        ..Default::default()
    });
    let config = Arc::new(config);
    let registry = crate::behavior::BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    // Run to a rest AFTER at least one episode, so the private stream's
    // position, the ordinal and the pending set all carry the future.
    for _ in 0..2000 {
        world.tick(&registry, &config).await;
        let s = state(&world, 1);
        if s.ordinal >= 1 && matches!(s.phase, Phase::Resting { .. }) {
            break;
        }
    }
    assert!(state(&world, 1).ordinal >= 1, "staged: one episode ran");
    let mut resumed: World = serde_json::from_str(&serde_json::to_string(&world).unwrap()).unwrap();
    for _ in 0..150 {
        world.tick(&registry, &config).await;
        resumed.tick(&registry, &config).await;
    }
    assert!(
        serde_json::to_string(&world).unwrap() == serde_json::to_string(&resumed).unwrap(),
        "the resumed world ticks identically"
    );
}
