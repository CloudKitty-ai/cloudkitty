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
use crate::needs::Needs;
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

// ---------------------------------------------------------------- T005

/// Rule 5's wrong-layer guard for the relief tables: they are read off
/// `apply_activity_effects` / `apply_sleep_relief`, so each row is checked
/// against what the effects ACTUALLY move — on the actor and on the kitty
/// the action names — on a probe world where every relief can land (every
/// need at 50, food, water and a bug adjacent, the partner settled so the
/// companion tiers pay their mutual rate).
#[test]
fn the_relief_tables_match_what_the_effects_actually_move() {
    use crate::action::TargetRef;
    use crate::kitty::ActivityClock;
    let rows = [
        Action::Eat,
        Action::Drink,
        Action::Sleep { with: None },
        Action::Sleep { with: Some(2) },
        Action::Rest { with: None },
        Action::Rest { with: Some(2) },
        Action::Groom { target: None },
        Action::Groom { target: Some(2) },
        Action::Play { target: None },
        Action::Play {
            target: Some(TargetRef::Element { id: 902 }),
        },
        Action::Play {
            target: Some(TargetRef::Kitty { id: 2 }),
        },
        Action::Chase(TargetRef::Kitty { id: 2 }),
    ];
    for action in rows {
        let config = test_config();
        let mut world = World::generate(&config);
        side_by_side(&mut world);
        // A settled partner pays the companion tiers' mutual rate (the
        // rest drip is 0 by default), but cannot be conscripted: social
        // play needs an idle partner or `apply` downgrades it to solo.
        let duet = matches!(
            action,
            Action::Play {
                target: Some(TargetRef::Kitty { .. })
            }
        );
        if !duet {
            let partner = kitty_mut(&mut world, 2);
            partner.activity = Activity::Resting { with_friend: None };
            partner.activity_clock = Some(ActivityClock::start(0));
        }
        for id in [1, 2] {
            for kind in NeedKind::ALL {
                kitty_mut(&mut world, id).needs.add(kind, 50.0);
            }
        }
        for (id, kind, x, y) in [
            (900, ElementKind::Chow { servings: 5 }, 4, 5),
            (901, ElementKind::Water, 6, 5),
            (902, ElementKind::Bug, 5, 4),
        ] {
            world.push_element(Element {
                id,
                kind,
                pos: Position::new(x, y),
                ttl: None,
            });
        }
        let before = [world.kitty(1).unwrap().needs, world.kitty(2).unwrap().needs];
        crate::action::apply(&mut world, 1, action, &config);
        let moved = |id: KittyId, before: &Needs| {
            let after = world.kitty(id).unwrap().needs;
            let kinds: Vec<NeedKind> = NeedKind::ALL
                .into_iter()
                .filter(|k| after.get(*k) != before.get(*k))
                .collect();
            NeedSet::from_kinds(&kinds)
        };
        assert_eq!(
            moved(1, &before[0]),
            proposer_relief(&action),
            "proposer needs moved for {action:?}"
        );
        assert_eq!(
            moved(2, &before[1]),
            partner_relief(&action)
                .map(|(_, relief)| relief)
                .unwrap_or_default(),
            "partner needs moved for {action:?}"
        );
    }
}

// ---------------------------------------------------------------- T006

/// A needy world for the verdict tests: kitty 1 seated (release level
/// out of reach so no episode releases mid-test), the pair side by side,
/// food and water beside kitty 1, the schedule held off.
fn verdict_stage() -> (World, Config) {
    let mut config = seated(NAME);
    config.needy = Some(crate::config::NeedyConfig {
        release_level: 99.0,
        ..Default::default()
    });
    let mut world = World::generate(&config);
    hold_off(&mut world, 1);
    side_by_side(&mut world);
    for (id, kind, x, y) in [
        (900, ElementKind::Chow { servings: 50 }, 4, 5),
        (901, ElementKind::Water, 6, 5),
    ] {
        world.push_element(Element {
            id,
            kind,
            pos: Position::new(x, y),
            ttl: None,
        });
    }
    (world, config)
}

/// Puts the seat straight into an episode masking `masked`.
pub(super) fn force_held(world: &mut World, id: KittyId, masked: &[NeedKind]) {
    let onset = world.tick;
    let s = kitty_mut(world, id).needy.as_mut().expect("needy seat");
    s.phase = Phase::Held {
        onset,
        masked: NeedSet::from_kinds(masked),
    };
}

fn refusal_at(world: &World, id: KittyId, tick: u64) -> Option<&crate::events::RefusalEvent> {
    world
        .refusal_log
        .events()
        .find(|e| e.kitty_id == id && e.tick == tick)
}

#[test]
fn a_masked_proposer_is_refused_and_the_refusal_names_the_mask() {
    let (mut world, config) = verdict_stage();
    kitty_mut(&mut world, 1).needs.add(NeedKind::Eat, 80.0);
    kitty_mut(&mut world, 1).needs.add(NeedKind::Drink, 80.0);
    force_held(&mut world, 1, &[NeedKind::Eat]);
    let eat_before = world.kitty(1).unwrap().needs.get(NeedKind::Eat);
    let heard = world.tick;
    tick_with(&mut world, &config, &[(1, Action::Eat)]);
    let k = world.kitty(1).unwrap();
    assert_eq!(k.activity, Activity::Idle, "a masked eat resolved to Idle");
    assert!(k.needs.get(NeedKind::Eat) >= eat_before);
    let refusal = refusal_at(&world, 1, heard).expect("the refusal is recorded");
    assert_eq!(refusal.proposed, Action::Eat);
    assert_eq!(
        refusal.reason,
        crate::events::RefusalReason::NeedyMasked,
        "the refusal names the mask (own)"
    );

    tick_with(&mut world, &config, &[(1, Action::Drink)]);
    assert_eq!(
        world.kitty(1).unwrap().activity,
        Activity::Drinking,
        "an unmasked need is serviced"
    );
}

#[test]
fn a_masked_cuddle_refuses_co_sleep_but_not_sleep_alone() {
    let (mut world, config) = verdict_stage();
    kitty_mut(&mut world, 1).needs.add(NeedKind::Sleep, 80.0);
    force_held(&mut world, 1, &[NeedKind::Cuddle]);
    tick_with(&mut world, &config, &[(1, Action::Sleep { with: Some(2) })]);
    assert_eq!(
        world.kitty(1).unwrap().activity,
        Activity::Idle,
        "co-sleep under a cuddle mask resolved to Idle"
    );
    tick_with(&mut world, &config, &[(1, Action::Sleep { with: None })]);
    assert!(
        matches!(
            world.kitty(1).unwrap().activity,
            Activity::Sleeping {
                with_friend: None,
                ..
            }
        ),
        "sleep alone relieves nothing masked and applies"
    );
}

#[test]
fn a_friends_offer_of_masked_relief_is_refused_target_side() {
    use crate::action::TargetRef;
    let cases = [
        (NeedKind::Cuddle, Action::Rest { with: Some(1) }),
        (NeedKind::Bath, Action::Groom { target: Some(1) }),
        (
            NeedKind::Play,
            Action::Play {
                target: Some(TargetRef::Kitty { id: 1 }),
            },
        ),
    ];
    for (masked, offer) in cases {
        let (mut world, config) = verdict_stage();
        force_held(&mut world, 1, &[masked]);
        assert_eq!(
            crate::action::validate(&world, 2, offer, &config),
            offer,
            "validation never reads the mask: {offer:?}"
        );
        let heard = world.tick;
        tick_with(&mut world, &config, &[(2, offer)]);
        assert_eq!(
            world.kitty(2).unwrap().activity,
            Activity::Idle,
            "the friend's offer was refused: {offer:?}"
        );
        assert_eq!(
            refusal_at(&world, 2, heard).map(|e| e.reason),
            Some(crate::events::RefusalReason::NeedyMasked),
            "the refusal names the mask (offered): {offer:?}"
        );

        let (mut open, config) = verdict_stage();
        tick_with(&mut open, &config, &[(2, offer)]);
        assert_ne!(
            open.kitty(2).unwrap().activity,
            Activity::Idle,
            "the same offer applies with no mask: {offer:?}"
        );
    }
}

#[test]
fn the_apply_slot_verdict_agrees_with_the_served_path() {
    use crate::action::TargetRef;
    let cases = [
        (NeedKind::Eat, 1, Action::Eat),
        (NeedKind::Cuddle, 1, Action::Sleep { with: Some(2) }),
        (NeedKind::Cuddle, 2, Action::Rest { with: Some(1) }),
        (NeedKind::Bath, 2, Action::Groom { target: Some(1) }),
        (
            NeedKind::Play,
            2,
            Action::Play {
                target: Some(TargetRef::Kitty { id: 1 }),
            },
        ),
    ];
    for (masked, proposer, proposal) in cases {
        let (mut world, config) = verdict_stage();
        force_held(&mut world, 1, &[masked]);
        assert_eq!(
            world
                .clone()
                .apply_slot_verdict(proposer, proposal, &config),
            Action::Idle,
            "apply_slot_verdict agrees with the served path: {proposal:?} is refused"
        );
        let (mut open, config) = verdict_stage();
        assert_eq!(
            open.apply_slot_verdict(proposer, proposal, &config),
            proposal,
            "and passes it with no mask"
        );
    }
}

// ------------------------------------------------- T008, T009, T016

/// The short-horizon instrument: kitty 1 on `preset`, first onsets inside
/// 200 ticks, a 200-tick hold, 20–40-tick rests, release at 60 — so with
/// the default rise rates eat, drink, sleep and play reach the level
/// inside the hold and cuddle and bath do not: both release kinds occur.
fn short_horizon(preset: &str) -> Arc<Config> {
    let mut c = seated(preset);
    c.needy = Some(crate::config::NeedyConfig {
        onset_levels: vec![0, 5, 20, 50, 100, 200],
        hold_ticks: 200,
        gap: crate::config::GapRange { min: 20, max: 40 },
        release_level: 60.0,
        ..Default::default()
    });
    c.validate().expect("valid");
    Arc::new(c)
}

/// One driven tick: kitty 1 decides through `decide` on its own fog view
/// and its dealt seed; kitty 2 offers to rest beside it every tick.
fn drive(
    world: &mut World,
    config: &Arc<Config>,
    decide: &dyn Fn(&crate::behavior::DecisionContext) -> crate::seam::Decision,
) -> crate::seam::TickReport {
    let seeds = world.deal_decision_seeds();
    let snapshot = world.snapshot();
    let ctx = crate::behavior::DecisionContext {
        me: snapshot.kitty(1).unwrap().clone(),
        world: Arc::new(snapshot.fog_for(1, config.vision.radius)),
        rng: crate::rng::DecisionRng::from_seed(seeds.seed_for(1).unwrap()),
        config: config.clone(),
    };
    let mut joint = JointProposal::new();
    joint.propose(1, decide(&ctx));
    joint.propose(2, Action::Rest { with: Some(1) });
    world.tick_with_proposals_seeded(&joint, seeds, config)
}

#[derive(Debug, Default)]
struct Ledger {
    by_level: usize,
    by_limit: usize,
    own_refusals: usize,
    friend_refusals: usize,
    messages: usize,
}

/// Runs the instrument until `episodes` episodes have opened and closed
/// (or `cap` ticks), checking every tick: a masked need never falls while
/// masked; the needy kitty's applied action never relieves a masked need;
/// the engine's schedule equals the law replayed on the recorded needs; a
/// friend's offer is refused (as `needy_masked`) only while cuddle is
/// masked; the needy kitty speaks law-named words only.
fn run_instrument(
    label: &str,
    config: &Arc<Config>,
    decide: &dyn Fn(&crate::behavior::DecisionContext) -> crate::seam::Decision,
    episodes: u32,
    cap: u64,
) -> (World, Ledger) {
    use crate::events::RefusalReason;
    use crate::meow::MessageKind;
    let mut world = World::generate(config);
    let params = params(config).into_owned();
    let mut replay = state(&world, 1).clone();
    let mut ledger = Ledger::default();
    for _ in 0..cap {
        let mask = state(&world, 1).mask();
        let before = world.kitty(1).unwrap().needs;
        let heard = world.tick;
        let report = drive(&mut world, config, decide);
        let after = world.kitty(1).unwrap().needs;
        for kind in mask.iter() {
            assert!(
                after.get(kind) >= before.get(kind),
                "a masked need never fell while masked [{label}]: {kind:?} at tick {heard}"
            );
        }
        let record = report.record(1).expect("kitty 1 decided");
        assert!(
            !proposer_relief(&record.applied).meets(mask),
            "the needy kitty's applied action never relieves a masked need [{label}]: {:?} at tick {heard}",
            record.applied
        );
        if let Some(kind) = record.applied_message {
            ledger.messages += 1;
            assert!(
                kind.related_need().is_some()
                    || MessageKind::HERE_KINDS.contains(&kind)
                    || matches!(kind, MessageKind::Purr | MessageKind::WaitForMe),
                "law-named words only over the run [{label}]: {kind:?} at tick {heard}"
            );
        }
        match replay.step(&after, world.tick, &params) {
            Some(Transition::Release {
                by: ReleaseBy::Level,
            }) => ledger.by_level += 1,
            Some(Transition::Release {
                by: ReleaseBy::Limit,
            }) => ledger.by_limit += 1,
            _ => {}
        }
        assert_eq!(
            &replay,
            state(&world, 1),
            "the engine's schedule equals the law replayed on the recorded needs [{label}] (tick {})",
            world.tick
        );
        for e in world.refusal_log.events().filter(|e| e.tick == heard) {
            if e.reason != RefusalReason::NeedyMasked {
                continue;
            }
            if e.kitty_id == 2 {
                assert!(
                    mask.contains(NeedKind::Cuddle),
                    "a friend's offer is refused only while cuddle is masked [{label}] (tick {heard})"
                );
                ledger.friend_refusals += 1;
            } else {
                ledger.own_refusals += 1;
            }
        }
        let s = state(&world, 1);
        if s.ordinal >= episodes && matches!(s.phase, Phase::Resting { .. }) {
            break;
        }
    }
    (world, ledger)
}

fn preset_decides(ctx: &crate::behavior::DecisionContext) -> crate::seam::Decision {
    use crate::behavior::Behavior;
    futures::executor::block_on(crate::behavior::needy::Needy.decide(ctx))
}

/// SC-003 / quickstart §2: ten episodes of the `needy` instrument behave
/// per the law, both release kinds occur, the gate fires on a friend's
/// offers, and the seat still services its needs.
#[test]
fn ten_needy_episodes_run_per_the_law() {
    let config = short_horizon(NAME);
    let (world, ledger) = run_instrument("needy", &config, &preset_decides, 10, 6000);
    let s = state(&world, 1);
    assert!(s.ordinal >= 10, "ten episodes ran: {ledger:?}");
    assert!(
        ledger.by_level >= 1 && ledger.by_limit >= 1,
        "staged: both release kinds occur (else the ordering guard is vacuous): {ledger:?}"
    );
    assert!(
        ledger.friend_refusals >= 1,
        "the gate fired on a friend's offer: {ledger:?}"
    );
    assert!(ledger.messages >= 1, "the needy kitty called: {ledger:?}");
    let k = world.kitty(1).unwrap();
    for kind in NeedKind::ALL {
        assert!(
            k.last_relief.contains_key(&kind),
            "every need was relieved at least once over the run (the seat still services): {kind:?}"
        );
    }
}

#[test]
fn needy_hold_releases_only_at_the_limit() {
    let config = short_horizon(HOLD_NAME);
    let (world, ledger) = run_instrument("needy_hold", &config, &preset_decides, 10, 6000);
    assert!(state(&world, 1).ordinal >= 10, "{ledger:?}");
    assert_eq!(
        ledger.by_level, 0,
        "needy_hold never releases by level: {ledger:?}"
    );
    assert!(ledger.by_limit >= 10, "{ledger:?}");
}

#[test]
fn two_needy_seats_carry_their_own_schedules() {
    let mut c = test_config();
    c.kitties[0].behavior = NAME.to_string();
    c.kitties[1].behavior = NAME.to_string();
    c.welfare_hazard = Some(WelfareHazardConfig {
        acknowledged: vec![NAME.to_string()],
    });
    c.validate().unwrap();
    let world = World::generate(&c);
    let params = params(&c).into_owned();
    for id in [1, 2] {
        assert_eq!(
            *state(&world, id),
            NeedyState::new(c.world.seed, id, false, &params),
            "seat {id} runs the schedule keyed off its own id"
        );
    }
    assert_ne!(
        state(&world, 1),
        state(&world, 2),
        "two seats, two schedules"
    );
}

/// Research D14, the recorded redundancy: the engine is the law, the
/// preset's masked view and filter are advice. With the preset's half
/// taken away (the plain teacher deciding for the needy seat) the masked
/// needs still never fall — the verdict and sweep hold the line — and the
/// seat is refused more often than with its own half in place.
#[test]
fn the_engine_holds_the_mask_without_the_presets_help() {
    let config = short_horizon(NAME);
    let teacher_decides = |ctx: &crate::behavior::DecisionContext| {
        use crate::behavior::Behavior;
        futures::executor::block_on(crate::behavior::teacher::Teacher::GEN2.decide(ctx))
    };
    let (_, without) = run_instrument("teacher-decided", &config, &teacher_decides, 6, 3000);
    let (_, with) = run_instrument("preset-decided", &config, &preset_decides, 6, 3000);
    assert!(
        without.own_refusals > with.own_refusals,
        "the filter is advice quality: refused turns without it ({}) exceed those with it ({})",
        without.own_refusals,
        with.own_refusals
    );
}

/// FR-013: the mask governs only the kitty's choices. The world's welfare
/// law acts on a needy kitty's masked need exactly as on any kitty's: the
/// distress record names it on the same tick, and the Article I safeguard
/// spawns food on the same tile, as in the same world with a teacher seat.
#[test]
fn the_worlds_welfare_law_acts_on_a_masked_need_as_on_any_need() {
    let stage = |preset: &str, eat: f32| -> (World, Config) {
        let mut config = test_config();
        config.kitties[0].behavior = preset.to_string();
        if preset == NAME {
            config.welfare_hazard = Some(WelfareHazardConfig {
                acknowledged: vec![NAME.to_string()],
            });
            config.needy = Some(crate::config::NeedyConfig {
                release_level: 99.5,
                ..Default::default()
            });
        }
        config.validate().unwrap();
        let mut world = World::generate(&config);
        if preset == NAME {
            hold_off(&mut world, 1);
            force_held(&mut world, 1, &[NeedKind::Eat]);
        }
        world.elements.clear();
        let k = kitty_mut(&mut world, 1);
        let current = k.needs.get(NeedKind::Eat);
        k.needs.add(NeedKind::Eat, eat - current);
        (world, config)
    };

    // Distress: from just under the line, the crossing tick is the same.
    let distress_tick = |preset: &str| -> Option<u64> {
        let line = test_config().thresholds.distress;
        let (mut world, config) = stage(preset, line - 1.2);
        (0..20).find_map(|_| {
            let report = world.tick_with_proposals(&JointProposal::new(), &config);
            report
                .distress_events
                .iter()
                .find(|e| e.kitty_id == 1 && e.need == NeedKind::Eat)
                .map(|e| e.tick)
        })
    };
    assert!(
        distress_tick("teacher").is_some(),
        "staged: the line is crossed"
    );
    assert_eq!(
        distress_tick(NAME),
        distress_tick("teacher"),
        "the distress record names the masked need on the same tick as for any kitty"
    );

    // The safeguard: past its line with no food anywhere, food appears on
    // the same tile in both worlds.
    let chow_after = |preset: &str| -> Vec<Position> {
        let line = test_config().thresholds.safeguard;
        let (mut world, config) = stage(preset, line + 5.0);
        world.tick_with_proposals(&JointProposal::new(), &config);
        world
            .elements
            .iter()
            .filter(|e| matches!(e.kind, ElementKind::Chow { .. }))
            .map(|e| e.pos)
            .collect()
    };
    let needy = chow_after(NAME);
    assert!(
        !needy.is_empty(),
        "the safeguard spawned food for the masked need"
    );
    assert_eq!(
        needy,
        chow_after("teacher"),
        "the safeguard spawns food for a masked need exactly as for any kitty"
    );
}

// ---------------------------------------------------------------- T010

async fn serialized_after(config: Config, ticks: u64) -> serde_json::Value {
    let config = Arc::new(config);
    let registry = crate::behavior::BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    for _ in 0..ticks {
        world.tick(&registry, &config).await;
    }
    serde_json::to_value(&world).unwrap()
}

/// FR-002 / US2 scenario 3: a WRITTEN `[needy]` table with no needy seat
/// is inert — 300 ticks of the default world serialize identically with
/// and without it, and no needy key appears.
#[tokio::test]
async fn the_needy_table_alone_never_reaches_a_plain_world() {
    let mut base = Config::default();
    base.world.seed = 20260718;
    let mut written = base.clone();
    written.needy = Some(crate::config::NeedyConfig {
        release_level: 70.0,
        ..Default::default()
    });
    written.validate().expect("the table alone validates");
    let a = serialized_after(base, 300).await;
    let b = serialized_after(written, 300).await;
    assert!(
        !a.to_string().contains("\"needy\""),
        "no needy key in a plain world"
    );
    assert!(
        a == b,
        "a written [needy] table with no seat changes nothing in the world"
    );
}

/// SC-002 (research D17): one seat swapped from `teacher` to `needy`, the
/// roster fixed, the first onset out of reach — until that onset the two
/// worlds tick identically on every surface except the seat's behaviour
/// string and needy state: the schedule's draws reach nothing shared.
#[tokio::test]
async fn swapping_a_teacher_seat_for_needy_moves_nothing_shared_before_the_onset() {
    let mut teacher = test_config();
    teacher.kitties[0].behavior = "teacher".to_string();
    let mut needy = seated(NAME);
    needy.needy = Some(crate::config::NeedyConfig {
        onset_levels: vec![500, 501, 502, 503, 504, 505],
        ..Default::default()
    });
    needy.validate().unwrap();
    let strip = |mut v: serde_json::Value| {
        for k in v["kitties"].as_array_mut().unwrap() {
            if k["id"] == 1 {
                let k = k.as_object_mut().unwrap();
                k.remove("behavior");
                k.remove("needy");
            }
        }
        v
    };
    let a = strip(serialized_after(teacher, 200).await);
    let b = strip(serialized_after(needy, 200).await);
    assert!(
        a == b,
        "identical until the first onset apart from the seat's behaviour and needy state"
    );
}
