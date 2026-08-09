//! Kitty communication.
//!
//! Six fixed messages, visible to every other kitty and to viewers. The engine
//! never blocks one (spec 023): every meow a kitty spends its turn on is heard.
//! Each message type keeps a per-kitty *courtesy* record -- an interval that
//! shortens when the related need gets urgent -- which the scripted behaviors
//! consult voluntarily before repeating themselves. Manners, not law: learned
//! agents are governed by the turn cost alone.

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
    /// Approach etiquette (spec 012): the yielding kitty of a mutual
    /// approach holds its corner and asks its partner to close the gap.
    /// Emitted by the yield rule only -- nothing else may spend it.
    WaitForMe,
    /// Spec 028: the two silent needs get their words. Appended so the
    /// existing six keep their normative positions.
    WantBath,
    WantSleep,
}

impl MessageKind {
    pub const ALL: [MessageKind; 9] = [
        MessageKind::WantEat,
        MessageKind::WantDrink,
        MessageKind::FollowMe,
        MessageKind::WantPlay,
        MessageKind::WantCuddle,
        MessageKind::Purr,
        MessageKind::WaitForMe,
        MessageKind::WantBath,
        MessageKind::WantSleep,
    ];

    /// The need this message asks about. `FollowMe`, `Purr` and `WaitForMe`
    /// have none -- they are social words, not requests.
    pub fn related_need(&self) -> Option<NeedKind> {
        match self {
            MessageKind::WantEat => Some(NeedKind::Eat),
            MessageKind::WantDrink => Some(NeedKind::Drink),
            MessageKind::WantPlay => Some(NeedKind::Play),
            MessageKind::WantCuddle => Some(NeedKind::Cuddle),
            MessageKind::WantBath => Some(NeedKind::Bath),
            MessageKind::WantSleep => Some(NeedKind::Sleep),
            MessageKind::FollowMe | MessageKind::Purr | MessageKind::WaitForMe => None,
        }
    }

    /// The message a kitty uses to ask for help with `need`. Total since
    /// spec 028: every need is announceable.
    pub fn for_need(need: NeedKind) -> MessageKind {
        match need {
            NeedKind::Eat => MessageKind::WantEat,
            NeedKind::Drink => MessageKind::WantDrink,
            NeedKind::Play => MessageKind::WantPlay,
            NeedKind::Cuddle => MessageKind::WantCuddle,
            NeedKind::Bath => MessageKind::WantBath,
            NeedKind::Sleep => MessageKind::WantSleep,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Meow {
    pub kitty_id: KittyId,
    pub kind: MessageKind,
    pub tick: u64,
    /// Spec 028: the grounding need's value at emission, /100 (want-kinds);
    /// 0.0 for the social words. Pre-028 snapshots read 0.0.
    #[serde(default)]
    pub intensity: f32,
}

/// The courtesy interval stamped when `kind` is emitted, given how urgent
/// the related need currently is (spec 023: record-keeping the scripted
/// behaviors consult -- the engine enforces nothing with it).
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
    fn wait_for_me_is_a_patience_word() {
        // Spec 012: in the vocabulary, base cooldown class (urgency never
        // shortens a word whose meaning is patience), wire name stable.
        assert!(MessageKind::ALL.contains(&MessageKind::WaitForMe));
        assert_eq!(MessageKind::WaitForMe.related_need(), None);
        assert_eq!(
            serde_json::to_string(&MessageKind::WaitForMe).unwrap(),
            "\"wait_for_me\""
        );
        assert_eq!(
            cooldown_for(MessageKind::WaitForMe, None, 15, 5, 75.0),
            15,
            "always the base cooldown"
        );
    }

    #[test]
    fn need_to_message_mapping_round_trips() {
        // Spec 028: total both ways -- every need has its word, and every
        // want-kind points back at its need.
        for need in NeedKind::ALL {
            let msg = MessageKind::for_need(need);
            assert_eq!(msg.related_need(), Some(need));
        }
        assert_eq!(
            serde_json::to_string(&MessageKind::WantBath).unwrap(),
            "\"want_bath\""
        );
        assert_eq!(
            serde_json::to_string(&MessageKind::WantSleep).unwrap(),
            "\"want_sleep\""
        );
    }
}
