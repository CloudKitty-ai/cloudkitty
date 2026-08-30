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

    /// Oldest first, newest last.
    pub fn events(&self) -> impl Iterator<Item = &T> {
        self.events.iter()
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
