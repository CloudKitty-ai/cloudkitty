//! Kitties.
//!
//! Article II is structural: this type has no health, no damage, no despawn, and no
//! removal API. There is deliberately no `Kitty::die`, no `World::remove_kitty`, and
//! no lifecycle state that could stand in for one. A kitty that enters the world
//! stays in it.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::action::Action;
use crate::grid::Position;
use crate::meow::MessageKind;
use crate::needs::{NeedKind, Needs};

pub type KittyId = u32;

/// What a kitty is currently doing. Multi-tick activities carry their context so
/// the engine can keep applying their effects (and drop the partner bonus if the
/// friend wanders off).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum Activity {
    #[default]
    Idle,
    Resting {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        with_friend: Option<KittyId>,
    },
    Sleeping {
        in_sunbeam: bool,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        with_friend: Option<KittyId>,
    },
}

impl Activity {
    pub fn is_sleeping(&self) -> bool {
        matches!(self, Activity::Sleeping { .. })
    }

    pub fn is_resting(&self) -> bool {
        matches!(self, Activity::Resting { .. })
    }

    pub fn partner(&self) -> Option<KittyId> {
        match self {
            Activity::Idle => None,
            Activity::Resting { with_friend } => *with_friend,
            Activity::Sleeping { with_friend, .. } => *with_friend,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Kitty {
    pub id: KittyId,
    pub name: String,
    pub pos: Position,
    pub needs: Needs,
    pub happiness: f32,
    pub activity: Activity,
    /// Name of the behavior strategy deciding for this kitty.
    pub behavior: String,
    /// Earliest tick at which each message kind may be used again.
    #[serde(default)]
    pub meow_cooldowns: BTreeMap<MessageKind, u64>,
    /// Needs currently at or above the distress threshold. Drives edge-triggered
    /// event recording: a need already in this set does not re-record.
    #[serde(default)]
    pub in_distress: BTreeSet<NeedKind>,
    /// Whether happiness went up on the previous tick; one of the two ways a kitty
    /// earns the right to purr.
    #[serde(default)]
    pub happiness_rose: bool,
    /// The action the engine actually applied for this kitty last tick -- the
    /// post-validation one, so an illegal proposal honestly reads as `Idle`.
    /// `None` only before the world's first tick. Feeds the viewer's "doing"
    /// line; defaulted so pre-existing saves still load.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub last_action: Option<Action>,
}

impl Kitty {
    pub fn new(
        id: KittyId,
        name: impl Into<String>,
        pos: Position,
        behavior: impl Into<String>,
    ) -> Self {
        Self {
            id,
            name: name.into(),
            pos,
            needs: Needs::default(),
            happiness: 100.0,
            activity: Activity::Idle,
            behavior: behavior.into(),
            meow_cooldowns: BTreeMap::new(),
            in_distress: BTreeSet::new(),
            happiness_rose: false,
            last_action: None,
        }
    }

    /// Whether `kind` may be meowed at `tick`.
    pub fn can_meow(&self, kind: MessageKind, tick: u64) -> bool {
        match self.meow_cooldowns.get(&kind) {
            Some(&ready_at) => tick >= ready_at,
            None => true,
        }
    }

    pub fn set_meow_cooldown(&mut self, kind: MessageKind, ready_at_tick: u64) {
        self.meow_cooldowns.insert(kind, ready_at_tick);
    }

    /// Drops cooldown entries that have already elapsed, so the map cannot grow
    /// without bound over a long-lived world.
    pub fn prune_meow_cooldowns(&mut self, tick: u64) {
        self.meow_cooldowns.retain(|_, ready_at| *ready_at > tick);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn kitty() -> Kitty {
        Kitty::new(1, "Miso", Position::new(3, 3), "needs_driven")
    }

    #[test]
    fn new_kitties_start_content() {
        let k = kitty();
        assert_eq!(k.happiness, 100.0);
        assert_eq!(k.activity, Activity::Idle);
        assert!(k.in_distress.is_empty());
    }

    #[test]
    fn meow_cooldown_gates_repeats() {
        let mut k = kitty();
        assert!(k.can_meow(MessageKind::WantPlay, 0));

        k.set_meow_cooldown(MessageKind::WantPlay, 15);
        assert!(!k.can_meow(MessageKind::WantPlay, 14));
        assert!(k.can_meow(MessageKind::WantPlay, 15));
        // Other message kinds are unaffected.
        assert!(k.can_meow(MessageKind::WantEat, 0));
    }

    #[test]
    fn elapsed_cooldowns_are_pruned() {
        let mut k = kitty();
        k.set_meow_cooldown(MessageKind::WantEat, 5);
        k.set_meow_cooldown(MessageKind::WantPlay, 20);
        k.prune_meow_cooldowns(10);
        assert!(!k.meow_cooldowns.contains_key(&MessageKind::WantEat));
        assert!(k.meow_cooldowns.contains_key(&MessageKind::WantPlay));
    }

    #[test]
    fn activity_wire_shape_uses_a_state_tag() {
        let sleeping = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(2),
        };
        let json = serde_json::to_value(sleeping).unwrap();
        assert_eq!(json["state"], "sleeping");
        assert_eq!(json["in_sunbeam"], true);
        assert_eq!(json["with_friend"], 2);

        let solo = serde_json::to_value(Activity::Resting { with_friend: None }).unwrap();
        assert_eq!(solo["state"], "resting");
        assert!(solo.get("with_friend").is_none());
    }
}
