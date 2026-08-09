//! Spec 028: message cadence is law, observed from the outside.
//!
//! Successor to spec 023's courtesy property test (which watched a
//! *voluntary* consult): the per-kind cooldown is enforced in
//! `message_legal` now, so same-kind spacing is a structural guarantee —
//! strictly stronger than the courtesy it replaces (the urgent carve-out
//! that allowed 5-tick repeats is gone; the floor is the full window for
//! every kind). The enforcement witnesses below drive the public proposal
//! seam directly: an on-cooldown or ungrounded message downgrades to
//! Silent in the record, and the paired activity is untouched.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::config::Config;
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::world::World;
use cloudkitty_core::{Action, Decision, JointProposal};

#[tokio::test]
async fn same_kind_emissions_keep_the_window_spacing_by_law() {
    for seed in [7u64, 91, 402] {
        let mut config = Config::default();
        config.world.seed = seed;
        config.validate().expect("valid");
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);

        let mut last_emit: BTreeMap<(u32, MessageKind), u64> = BTreeMap::new();
        let mut seen: BTreeSet<(u32, MessageKind, u64)> = BTreeSet::new();
        let mut total = 0u64;

        for _ in 0..1_500 {
            world.tick(&registry, &config).await;
            for m in &world.recent_meows {
                if !seen.insert((m.kitty_id, m.kind, m.tick)) {
                    continue;
                }
                total += 1;
                let key = (m.kitty_id, m.kind);
                if let Some(prev) = last_emit.get(&key) {
                    let gap = m.tick.saturating_sub(*prev);
                    let min_gap = config.meow.recent_window_ticks;
                    assert!(
                        gap >= min_gap,
                        "seed {seed}: kitty {} repeated {:?} after {gap} ticks \
                         (the window floor is {min_gap}, and it is law now)",
                        m.kitty_id,
                        m.kind
                    );
                }
                let entry = last_emit.entry(key).or_insert(m.tick);
                if m.tick > *entry {
                    *entry = m.tick;
                }
            }
        }
        assert!(total > 0, "seed {seed}: a living meadow meows sometimes");
    }
}

#[test]
fn an_on_cooldown_message_downgrades_to_silent() {
    // Spec 028 US2 scenario 3 / SC-005: the same kind again inside the
    // window is masked -- proposed != applied (Silent), activity untouched,
    // nothing emitted. Driven through the public proposal seam, so the
    // whole enforcement path is the one under test.
    let config = Config::default();
    let mut world = World::generate(&config);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx]
        .announce_armed
        .insert(cloudkitty_core::NeedKind::Eat);
    let tick = world.tick;
    world.kitties[idx]
        .meow_cooldowns
        .insert(MessageKind::WantEat, tick + 5); // mid-window

    let mut proposals = JointProposal::new();
    proposals.propose(
        1,
        Decision {
            activity: Action::Idle,
            message: Some(MessageKind::WantEat),
        },
    );
    let before = world.recent_meows.len();
    let report = world.tick_with_proposals(&proposals, &config);
    let record = report.record(1).expect("kitty 1 is in the roster");
    assert_eq!(record.proposed_message, Some(MessageKind::WantEat));
    assert_eq!(record.applied_message, None, "downgraded to Silent");
    assert_eq!(record.applied, Action::Idle, "the activity is untouched");
    assert_eq!(world.recent_meows.len(), before, "nothing emitted");
}

#[test]
fn an_ungrounded_want_kind_downgrades_to_silent() {
    // Grounded legality (FR-005): an unarmed want-kind may not be spoken,
    // cooldown or no cooldown. Same downgrade, same untouched activity.
    let config = Config::default();
    let mut world = World::generate(&config);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].announce_armed.clear();
    assert!(world.kitties[idx].meow_cooldowns.is_empty());

    let mut proposals = JointProposal::new();
    proposals.propose(
        1,
        Decision {
            activity: Action::Rest { with: None },
            message: Some(MessageKind::WantBath),
        },
    );
    let before = world.recent_meows.len();
    let report = world.tick_with_proposals(&proposals, &config);
    let record = report.record(1).expect("kitty 1 is in the roster");
    assert_eq!(record.applied_message, None, "ungrounded -> Silent");
    assert_eq!(
        record.applied,
        Action::Rest { with: None },
        "the paired activity applies as proposed"
    );
    assert_eq!(world.recent_meows.len(), before);
}

#[test]
fn a_grounded_clear_message_emits_and_records() {
    // The positive half, same seam: armed + cooldown clear emits, records
    // proposed == applied, stamps the window.
    let config = Config::default();
    let mut world = World::generate(&config);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx]
        .announce_armed
        .insert(cloudkitty_core::NeedKind::Eat);

    let mut proposals = JointProposal::new();
    proposals.propose(
        1,
        Decision {
            activity: Action::Idle,
            message: Some(MessageKind::WantEat),
        },
    );
    let before = world.recent_meows.len();
    let report = world.tick_with_proposals(&proposals, &config);
    let record = report.record(1).expect("kitty 1 is in the roster");
    assert_eq!(record.applied_message, Some(MessageKind::WantEat));
    assert_eq!(world.recent_meows.len(), before + 1, "heard by everyone");
    let stamp = world.kitty(1).unwrap().meow_cooldowns[&MessageKind::WantEat];
    assert_eq!(
        stamp,
        // The emission tick (tick advanced by one inside the tick).
        world.tick - 1 + config.meow.recent_window_ticks,
        "emission stamps the window"
    );
}
