//! Kitty communication.
//!
//! Eight announceable kinds plus the engine's patience word, visible to every
//! other kitty and to viewers. Spec 028 ended the courtesy era: emission
//! stamps a per-kind cooldown of one audibility window, and (once the message
//! channel lands) legality is engine law -- a want-kind may be spoken only
//! while its need is armed and that kind's cooldown has cleared.

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

/// Engine law (spec 028): may `kitty` speak `kind` at `tick`? Silence is
/// the absence of a message and needs no ruling -- this covers the spoken
/// kinds. The RL message mask derives from here by probing, exactly as the
/// activity mask probes `validate` (the no-carve-outs doctrine).
///
/// Skeleton form (T005): grounding for the want-kinds (announce arming +
/// per-kind cooldown as law) lands with the arming state (T010); until
/// then they are unconditionally legal, as they were.
pub fn message_legal(
    kitty: &crate::kitty::Kitty,
    kind: MessageKind,
    tick: u64,
    config: &crate::config::Config,
) -> bool {
    match kind {
        // Earned-only, byte-faithful to the retiring purr-meow's validate
        // gate: a deliberate purr mid-purr stays a lawful no-op, and no
        // cooldown clause sneaks in.
        MessageKind::Purr => kitty.purr_earned(config.thresholds.purr),
        // Today's voluntary check in wait_for_them, made law -- this is
        // what lets the engine-proposed yield word survive enforcement.
        // Head-excluded: policies cannot express it (no codec index).
        MessageKind::WaitForMe => kitty.can_meow(MessageKind::WaitForMe, tick),
        _ => true,
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wait_for_me_is_a_patience_word() {
        // Spec 012: in the vocabulary, no related need (urgency never
        // touches a word whose meaning is patience), wire name stable.
        assert!(MessageKind::ALL.contains(&MessageKind::WaitForMe));
        assert_eq!(MessageKind::WaitForMe.related_need(), None);
        assert_eq!(
            serde_json::to_string(&MessageKind::WaitForMe).unwrap(),
            "\"wait_for_me\""
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
