//! Engine events: things that happened, kept in bounded rings for whoever is
//! watching.
//!
//! Distress (Article I): distress is a *signal*, never a punishment. A need
//! crossing the threshold records one event; nothing else in the engine reads
//! it to make a kitty's life worse. Recording is edge-triggered: one event per
//! crossing, re-armed only once the need drops back below the threshold. A
//! kitty sitting at 95 for a thousand ticks produces one event, not a thousand.
//!
//! Activity ends (spec 006): every activity that ends records exactly one
//! event carrying its true span. The engine clears an activity's clock on the
//! same tick it last services it, so that final tick is invisible in served
//! snapshots -- the event log is the honest record, for tests and for viewers
//! that want to say "ate for 4 ticks".

use std::collections::VecDeque;

use serde::{Deserialize, Serialize};

use crate::action::Action;
use crate::kitty::{Activity, KittyId};
use crate::needs::NeedKind;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DistressEvent {
    pub kitty_id: KittyId,
    pub need: NeedKind,
    pub tick: u64,
}

/// An activity that ran its course (spec 006): who, what, and the inclusive
/// tick span it actually covered. `ended` is the last tick the activity was
/// serviced, so its length is `ended - started + 1`.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ActivityEnd {
    pub kitty_id: KittyId,
    pub activity: Activity,
    pub started: u64,
    pub ended: u64,
    /// Serviced ticks the scene's partner was itself settled (spec 041
    /// FR-011): the mutual tier's emit-proof. Zero -- and absent from the
    /// serialized form -- on every non-tiered activity; absent fields read
    /// as zero, so pre-041 payloads and consumers are untouched. Invariant:
    /// `mutual_ticks + drip_ticks <= span()`, the shortfall being exactly
    /// the scene's solo (posture-only) serviced ticks.
    #[serde(default, skip_serializing_if = "tier_count_is_zero")]
    pub mutual_ticks: u32,
    /// Serviced ticks the partner was merely present -- the drip tier's
    /// emit-proof (F-029: a tier is only claimable once shown able to
    /// emit). Same defaults and absence rules as `mutual_ticks`.
    #[serde(default, skip_serializing_if = "tier_count_is_zero")]
    pub drip_ticks: u32,
}

fn tier_count_is_zero(n: &u32) -> bool {
    *n == 0
}

/// A refusal (spec 046): a non-Idle proposal that `action::validate`
/// resolved to Idle, recorded on the tick it was heard. Article I: the stamp
/// is a signal, never a punishment -- nothing in the engine reads this ring.
///
/// `absorbed` reads the enforcement outcome: `false` means the turn resolved
/// Idle (a taxed tick -- the census filter), `true` means duration
/// enforcement continued the kitty's scene (refusal heard, nothing lost).
/// Always serialized: the census filters on it, and an absent-key convention
/// would re-create the F-029 reading trap.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct RefusalEvent {
    pub kitty_id: KittyId,
    /// The proposal verbatim -- `with`/`target` ride exactly as proposed.
    pub proposed: Action,
    pub tick: u64,
    pub absorbed: bool,
}

impl ActivityEnd {
    /// How many ticks the activity was serviced, inclusive of both ends.
    pub fn span(&self) -> u64 {
        self.ended.saturating_sub(self.started) + 1
    }
}

/// A bounded ring of the most recent events, oldest first.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventLog<T> {
    events: VecDeque<T>,
    capacity: usize,
}

// Manual so the events themselves need no Default (the derive would demand
// one). A defaulted log has capacity 0, which `record` treats as 1.
impl<T> Default for EventLog<T> {
    fn default() -> Self {
        Self {
            events: VecDeque::new(),
            capacity: 0,
        }
    }
}

/// The distress ring (Article I signal).
pub type DistressLog = EventLog<DistressEvent>;

/// The activity-end ring (spec 006 span record).
pub type ActivityLog = EventLog<ActivityEnd>;

/// The refusal ring (spec 046 stamp).
pub type RefusalLog = EventLog<RefusalEvent>;

impl<T> EventLog<T> {
    pub fn new(capacity: usize) -> Self {
        Self {
            events: VecDeque::new(),
            capacity: capacity.max(1),
        }
    }

    pub fn record(&mut self, event: T) {
        while self.events.len() >= self.capacity.max(1) {
            self.events.pop_front();
        }
        self.events.push_back(event);
    }

    /// Re-stamp the ring's capacity (spec 046 research R3): capacity is
    /// configuration, not world state, so the load path re-applies it to a
    /// deserialized ring. Floors at 1 like `new`; trims oldest-first when the
    /// ring already holds more than the new capacity.
    pub fn set_capacity(&mut self, capacity: usize) {
        self.capacity = capacity.max(1);
        while self.events.len() > self.capacity {
            self.events.pop_front();
        }
    }

    /// The ring's own bound — how many events it can hold before dropping
    /// oldest-first. Served beside the events (spec 046 review): a consumer
    /// reading a full window cannot otherwise tell "short history" from
    /// "wrapped ring" (the F-029 absent-key trap, one struct up).
    pub fn capacity(&self) -> usize {
        self.capacity
    }

    /// Oldest first, newest last.
    pub fn events(&self) -> impl Iterator<Item = &T> {
        self.events.iter()
    }

    /// The most recent event, if any (O(1)).
    pub fn newest(&self) -> Option<&T> {
        self.events.back()
    }

    pub fn len(&self) -> usize {
        self.events.len()
    }

    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }
}

impl<T: Clone> EventLog<T> {
    pub fn to_vec(&self) -> Vec<T> {
        self.events.iter().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn event(tick: u64) -> DistressEvent {
        DistressEvent {
            kitty_id: 1,
            need: NeedKind::Eat,
            tick,
        }
    }

    #[test]
    fn log_keeps_the_most_recent_events() {
        let mut log = DistressLog::new(3);
        for tick in 0..5 {
            log.record(event(tick));
        }
        let ticks: Vec<u64> = log.events().map(|e| e.tick).collect();
        assert_eq!(ticks, vec![2, 3, 4], "oldest events are dropped first");
        assert_eq!(log.len(), 3);
    }

    #[test]
    fn capacity_is_never_zero() {
        let mut log = DistressLog::new(0);
        log.record(event(1));
        assert_eq!(log.len(), 1);

        // A serde-defaulted log (capacity 0, e.g. a field added to an older
        // snapshot) degrades to a ring of one rather than growing unbounded.
        let mut defaulted = ActivityLog::default();
        for started in 0..5 {
            defaulted.record(ActivityEnd {
                kitty_id: 1,
                activity: Activity::Eating,
                started,
                ended: started + 1,
                mutual_ticks: 0,
                drip_ticks: 0,
            });
        }
        assert_eq!(defaulted.len(), 1);
    }

    #[test]
    fn set_capacity_trims_oldest_first_and_floors_at_one() {
        let mut log = DistressLog::new(5);
        for tick in 0..5 {
            log.record(event(tick));
        }
        log.set_capacity(3);
        let ticks: Vec<u64> = log.events().map(|e| e.tick).collect();
        assert_eq!(
            ticks,
            vec![2, 3, 4],
            "shrinking the ring keeps the newest events, dropping oldest first"
        );

        // Growing never loses anything.
        log.set_capacity(10);
        assert_eq!(log.len(), 3);
        log.record(event(5));
        assert_eq!(log.len(), 4, "the grown ring accepts more events");

        // A zero re-stamp floors at one, matching `new` and `record`.
        log.set_capacity(0);
        let ticks: Vec<u64> = log.events().map(|e| e.tick).collect();
        assert_eq!(ticks, vec![5], "capacity 0 degrades to a ring of one");
        log.record(event(6));
        assert_eq!(log.len(), 1);
    }

    #[test]
    fn a_counterless_activity_end_serializes_exactly_as_before_041() {
        // The pinned payload is a REAL event recorded from a default-config
        // run on the pre-041 build (2026-08-28), not a hand-written
        // fixture: a walk, a meal, or a solo nap must serialize today
        // exactly as it did then -- the tier counters ride only when
        // nonzero (spec 041 FR-011, contract activity-event-tier.md).
        let end = ActivityEnd {
            kitty_id: 1,
            activity: Activity::Sleeping {
                in_sunbeam: false,
                with_friend: None,
            },
            started: 0,
            ended: 2,
            mutual_ticks: 0,
            drip_ticks: 0,
        };
        assert_eq!(
            serde_json::to_string(&end).unwrap(),
            r#"{"kitty_id":1,"activity":{"state":"sleeping","in_sunbeam":false},"started":0,"ended":2}"#,
        );
        // And the counters round-trip when present, absent fields read 0.
        let with: ActivityEnd = serde_json::from_str(
            r#"{"kitty_id":3,"activity":{"state":"resting","with_friend":1},"started":10,"ended":21,"mutual_ticks":9,"drip_ticks":2}"#,
        )
        .unwrap();
        assert_eq!((with.mutual_ticks, with.drip_ticks), (9, 2));
        let without: ActivityEnd = serde_json::from_str(
            r#"{"kitty_id":1,"activity":{"state":"eating"},"started":0,"ended":2}"#,
        )
        .unwrap();
        assert_eq!(
            (without.mutual_ticks, without.drip_ticks),
            (0, 0),
            "pre-041 payloads deserialize with zero counters"
        );
    }

    #[test]
    fn a_refusal_event_serializes_the_proposal_verbatim() {
        // Spec 046 FR-008 emit-proof at the ring layer, both flag values,
        // from REAL recorded events (rule 5: no hand-written fixtures) --
        // the instrument is shown able to emit before any zero is read
        // (F-029). Taxed: a move into an occupied cell, no scene to absorb
        // it. Absorbed: an illegal Purr inside a sleep minimum.
        use crate::action::Action;
        use crate::grid::{Direction, Position};
        use crate::seam::JointProposal;
        use crate::test_support::test_config;
        use crate::world::World;

        let config = test_config();
        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0); // kitty 1
        world.kitties[1].pos = Position::new(1, 0); // kitty 2, blocking east

        // Tick 0, the taxed event: kitty 1's move east is refused.
        let mut p = JointProposal::new();
        p.propose(1, Action::move_to(Direction::East));
        world.tick_with_proposals(&p, &config);
        // Tick 1: kitty 2 starts a solo sleep. Tick 2, the absorbed event:
        // its Purr is refused inside the minimum, scene continues.
        let mut p = JointProposal::new();
        p.propose(2, Action::Sleep { with: None });
        world.tick_with_proposals(&p, &config);
        let mut p = JointProposal::new();
        p.propose(2, Action::Purr);
        world.tick_with_proposals(&p, &config);

        // Tick 3, a target-carrying refusal: kitty 2 is mid-scene, so kitty
        // 1's social play is refused (partner not conscriptable).
        let mut p = JointProposal::new();
        p.propose(
            1,
            Action::play_with(crate::action::TargetRef::Kitty { id: 2 }),
        );
        world.tick_with_proposals(&p, &config);

        let events = world.refusal_log.to_vec();
        assert_eq!(
            events.len(),
            3,
            "taxed, absorbed, and target-carrying: {events:?}"
        );
        let (taxed, absorbed) = (&events[0], &events[1]);
        assert!(!taxed.absorbed);
        assert!(absorbed.absorbed, "the sleep minimum absorbed the purr");

        // The taxed event's wire shape, pinned against the payload a real
        // driven world produced on 2026-09-01: `proposed` is the standard
        // internally-tagged Action serialization, `absorbed` ALWAYS present
        // (no skip-at-false -- an absent-key convention would re-create the
        // reading trap the census filters on this key).
        assert_eq!(
            serde_json::to_string(taxed).unwrap(),
            r#"{"kitty_id":1,"proposed":{"action":"move","direction":"east"},"tick":0,"absorbed":false}"#,
        );

        // The target flattens into the play object -- the proposal wire
        // shape plugins already speak (pinned for the endpoint contract).
        assert_eq!(
            serde_json::to_string(&events[2]).unwrap(),
            r#"{"kitty_id":1,"proposed":{"action":"play","target":"kitty","id":2},"tick":3,"absorbed":false}"#,
        );

        // All round-trip losslessly, target-carrying proposals included.
        for e in &events {
            let back: RefusalEvent =
                serde_json::from_str(&serde_json::to_string(e).unwrap()).unwrap();
            assert_eq!(&back, e);
        }
    }

    #[test]
    fn an_activity_end_knows_its_inclusive_span() {
        let end = ActivityEnd {
            kitty_id: 1,
            activity: Activity::Eating,
            started: 10,
            ended: 12,
            mutual_ticks: 0,
            drip_ticks: 0,
        };
        assert_eq!(end.span(), 3, "ticks 10, 11 and 12 were all serviced");
    }
}
