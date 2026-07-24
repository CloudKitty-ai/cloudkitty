//! Degradation (spec 014 US1, Article IV): joint proposals with absent,
//! malformed, and unknown-id entries never fail the tick — the affected
//! kitties idle (provenance `SubstitutedIdle`), unknown entries are reported
//! unconsumed, everyone else acts, and the invariants hold.

use std::sync::Arc;

use cloudkitty_core::action::Action;
use cloudkitty_core::grid::Direction;
use cloudkitty_core::seam::{JointProposal, Provenance};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;

#[test]
fn absent_malformed_and_unknown_entries_degrade_to_idle_without_failing_the_tick() {
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    let roster: Vec<_> = world.kitties.iter().map(|k| k.id).collect();
    assert!(
        roster.len() >= 3,
        "the default roster covers all three cases"
    );

    // Kitty 0: a well-formed move. Kitty 1: absent (no entry at all).
    // Kitty 2: a malformed wire entry. Plus an entry for a kitty that
    // does not exist.
    let mover = roster[0];
    let absent = roster[1];
    let garbled = roster[2];
    let unknown = 9_999;
    assert!(world.kitty(unknown).is_none());

    let mut proposals = JointProposal::new();
    proposals.propose(
        mover,
        Action::Move {
            direction: Direction::South,
        },
    );
    proposals.propose_malformed(garbled);
    proposals.propose(unknown, Action::Eat);

    let before = world.kitty(mover).unwrap().pos;
    let report = world.tick_with_proposals(&proposals, &config);

    // The well-formed proposal got its normal hearing (a south step from a
    // default starting position is legal).
    let moved = report.record(mover).expect("mover has a record");
    assert_eq!(moved.provenance, Provenance::PolicyMade);
    assert_eq!(
        moved.proposed,
        Action::Move {
            direction: Direction::South
        }
    );
    assert_ne!(world.kitty(mover).unwrap().pos, before, "the mover moved");

    // Absent and malformed both substituted to idle, marked honestly --
    // never FallbackTaken, which is reserved for dispatched decisions.
    for id in [absent, garbled] {
        let record = report.record(id).expect("every kitty has a record");
        assert_eq!(record.provenance, Provenance::SubstitutedIdle);
        assert_eq!(record.proposed, Action::Idle);
        assert_eq!(record.applied, Action::Idle);
    }

    // The unknown id is reported unconsumed, and nobody else lost a turn.
    assert_eq!(report.unconsumed, vec![unknown]);
    assert_eq!(report.records.len(), roster.len());
    assert_eq!(world.tick, 1, "the tick completed");
}

#[test]
fn a_long_all_absent_run_upholds_the_invariants() {
    // A driver that never sends anything: every kitty idles every tick, needs
    // rise, distress is recorded, the safeguard restocks -- and the per-tick
    // invariant assertions (Articles I-III) hold throughout.
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    let empty = JointProposal::new();

    for _ in 0..300 {
        let report = world.tick_with_proposals(&empty, &config);
        assert!(report
            .records
            .iter()
            .all(|r| r.provenance == Provenance::SubstitutedIdle));
    }
    assert_eq!(world.tick, 300);
    assert_eq!(
        world.kitties.len(),
        config.kitties.len(),
        "no kitty ever leaves the world (Article II)"
    );
}

#[test]
fn a_retired_purr_proposal_lawfully_resolves_to_idle() {
    // Purr is retired as an action (spec 011); an external driver proposing
    // it gets Article IV's safe no-op, not an error.
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    let id = world.kitties[0].id;

    let mut proposals = JointProposal::new();
    proposals.propose(id, Action::Purr);
    let report = world.tick_with_proposals(&proposals, &config);

    let record = report.record(id).unwrap();
    assert_eq!(record.proposed, Action::Purr);
    assert_eq!(record.validated, Action::Idle, "validation refused it");
    assert_eq!(record.provenance, Provenance::PolicyMade);
}

#[test]
fn a_duplicate_proposal_resolves_last_write_wins() {
    // Documented at JointProposal::propose since spec 014 FR-001, untested
    // until the round-one review: a second proposal for the same kitty
    // replaces the first, and the record reports the replacement as what
    // was proposed.
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    let kitty = world.kitties[0].id;

    let mut proposals = JointProposal::new();
    proposals.propose(
        kitty,
        Action::Move {
            direction: Direction::South,
        },
    );
    proposals.propose(kitty, Action::Idle);
    assert_eq!(proposals.len(), 1, "one entry per kitty, not per call");

    let report = world.tick_with_proposals(&proposals, &config);
    let record = report.record(kitty).expect("the kitty has a record");
    assert_eq!(record.proposed, Action::Idle, "the last write won");
    assert_eq!(
        record.provenance,
        Provenance::PolicyMade,
        "a replaced proposal is still a made proposal, never a substitution"
    );
}

#[test]
#[should_panic(expected = "dealt for tick")]
fn a_stale_deal_cannot_cross_ticks() {
    // The double-deal footgun (round-one review): seeds dealt for tick T
    // must never apply at any other tick — quietly doing so would desync
    // the master RNG stream (Article V). The engine asserts the deal's
    // tick stamp; this pins the assertion so it cannot regress to a
    // silent acceptance.
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);

    let stale = world.deal_decision_seeds();
    // The world moves on with its own properly-dealt tick...
    world.tick_with_proposals(&JointProposal::new(), &config);
    // ...and the held-over deal is refused loudly, not absorbed.
    world.tick_with_proposals_seeded(&JointProposal::new(), stale, &config);
}
