//! Kitty communication.
//!
//! Six fixed messages, visible to every other kitty and to viewers. Each message
//! type has a per-kitty cooldown that shortens when the related need gets urgent,
//! so a hungry cat may say so more often than a merely chatty one. A meow attempted
//! during cooldown is silently dropped but still costs the kitty its turn.

use serde::{Deserialize, Serialize};

use crate::kitty::KittyId;
use crate::needs::NeedKind;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MessageKind {
    WantEat,
    WantDrink,
    FollowMe,
    WantPlay,
    WantCuddle,
    Purr,
}

impl MessageKind {
    pub const ALL: [MessageKind; 6] = [
        MessageKind::WantEat,
        MessageKind::WantDrink,
        MessageKind::FollowMe,
        MessageKind::WantPlay,
        MessageKind::WantCuddle,
        MessageKind::Purr,
    ];

    /// The need whose urgency shortens this message's cooldown. `FollowMe` and
    /// `Purr` have none, so they always use the base cooldown.
    pub fn related_need(&self) -> Option<NeedKind> {
        match self {
            MessageKind::WantEat => Some(NeedKind::Eat),
            MessageKind::WantDrink => Some(NeedKind::Drink),
            MessageKind::WantPlay => Some(NeedKind::Play),
            MessageKind::WantCuddle => Some(NeedKind::Cuddle),
            MessageKind::FollowMe | MessageKind::Purr => None,
        }
    }

    /// The message a kitty would use to ask for help with `need`, if any.
    pub fn for_need(need: NeedKind) -> Option<MessageKind> {
        match need {
            NeedKind::Eat => Some(MessageKind::WantEat),
            NeedKind::Drink => Some(MessageKind::WantDrink),
            NeedKind::Play => Some(MessageKind::WantPlay),
            NeedKind::Cuddle => Some(MessageKind::WantCuddle),
            NeedKind::Sleep | NeedKind::Bath => None,
        }
    }

    /// Human-facing text, rendered in the viewer's speech bubbles.
    pub fn text(&self) -> &'static str {
        match self {
            MessageKind::WantEat => "I want to eat!",
            MessageKind::WantDrink => "I want to drink!",
            MessageKind::FollowMe => "Follow me!",
            MessageKind::WantPlay => "I want to play!",
            MessageKind::WantCuddle => "I want to cuddle!",
            MessageKind::Purr => "I am happy",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Meow {
    pub kitty_id: KittyId,
    pub kind: MessageKind,
    pub tick: u64,
}

/// How long this kitty must wait before repeating `kind`, given how urgent the
/// related need currently is.
pub fn cooldown_for(
    kind: MessageKind,
    need_value: Option<f32>,
    base_ticks: u64,
    urgent_ticks: u64,
    urgent_threshold: f32,
) -> u64 {
    match (kind.related_need(), need_value) {
        (Some(_), Some(value)) if value >= urgent_threshold => urgent_ticks,
        _ => base_ticks,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn urgent_needs_shorten_the_cooldown() {
        // Below the urgency threshold: base cooldown.
        assert_eq!(
            cooldown_for(MessageKind::WantEat, Some(50.0), 15, 5, 75.0),
            15
        );
        // At or above it: the shortened one.
        assert_eq!(
            cooldown_for(MessageKind::WantEat, Some(75.0), 15, 5, 75.0),
            5
        );
        assert_eq!(
            cooldown_for(MessageKind::WantEat, Some(99.0), 15, 5, 75.0),
            5
        );
    }

    #[test]
    fn messages_without_a_related_need_always_use_the_base_cooldown() {
        assert_eq!(
            cooldown_for(MessageKind::FollowMe, Some(100.0), 15, 5, 75.0),
            15
        );
        assert_eq!(
            cooldown_for(MessageKind::Purr, Some(100.0), 15, 5, 75.0),
            15
        );
        assert_eq!(MessageKind::Purr.related_need(), None);
    }

    #[test]
    fn need_to_message_mapping_round_trips() {
        for need in [
            NeedKind::Eat,
            NeedKind::Drink,
            NeedKind::Play,
            NeedKind::Cuddle,
        ] {
            let msg = MessageKind::for_need(need).expect("mapped message");
            assert_eq!(msg.related_need(), Some(need));
        }
        assert_eq!(MessageKind::for_need(NeedKind::Sleep), None);
        assert_eq!(MessageKind::for_need(NeedKind::Bath), None);
    }
}
