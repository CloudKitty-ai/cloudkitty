//! Distress events.
//!
//! Article I: distress is a *signal*, never a punishment. A need crossing the
//! threshold records one event; nothing else in the engine reads it to make a
//! kitty's life worse. The world and future cooperative gameplay use it to know
//! where help is wanted.
//!
//! Recording is edge-triggered: one event per crossing, re-armed only once the need
//! drops back below the threshold. A kitty sitting at 95 for a thousand ticks
//! produces one event, not a thousand.

use std::collections::VecDeque;

use serde::{Deserialize, Serialize};

use crate::kitty::KittyId;
use crate::needs::NeedKind;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DistressEvent {
    pub kitty_id: KittyId,
    pub need: NeedKind,
    pub tick: u64,
}

/// A bounded ring of the most recent distress events.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct DistressLog {
    events: VecDeque<DistressEvent>,
    capacity: usize,
}

impl DistressLog {
    pub fn new(capacity: usize) -> Self {
        Self {
            events: VecDeque::new(),
            capacity: capacity.max(1),
        }
    }

    pub fn record(&mut self, event: DistressEvent) {
        if self.events.len() >= self.capacity {
            self.events.pop_front();
        }
        self.events.push_back(event);
    }

    /// Oldest first, newest last.
    pub fn events(&self) -> impl Iterator<Item = &DistressEvent> {
        self.events.iter()
    }

    pub fn to_vec(&self) -> Vec<DistressEvent> {
        self.events.iter().cloned().collect()
    }

    pub fn len(&self) -> usize {
        self.events.len()
    }

    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }

    pub fn capacity(&self) -> usize {
        self.capacity
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
    }
}
