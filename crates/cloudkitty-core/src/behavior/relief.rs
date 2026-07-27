//! The need→relief correspondence (spec 019): the one authoritative
//! definition, within the built-in behavior stack, of what relieves each
//! need. (The RL crate's welfare metric keeps its own cross-crate
//! zero-distance encoding of relief availability — `welfare.rs`,
//! unreachable from here by design; its known Cuddle divergence is
//! recorded in BACKLOG.)
//!
//! Three decision steps consume this pairing — target-selection scoring
//! (`selection::distance_given`), pursuit (`needs_driven::pursue`), and
//! opportunistic grabbing (`needs_driven::take_what_is_here`). Before this
//! module they each encoded it independently, kept in agreement by
//! comments and reviewer vigilance (the mirror the 004 review demanded).
//! Now the pairing exists once: what gets scored, what gets walked to,
//! and what gets grabbed can never disagree, because all three derive it
//! from [`NeedKind::relief`], and a new need without a correspondence is
//! a compile error.
//!
//! This centralizes the *knowledge*, not the logic: each shape's
//! mechanics stay with their single owners — element pricing and
//! tie-breaks in [`selection::priced_nearest_element`], the sunbeam
//! walk-vs-nap rule in [`selection::sunbeam_worth_walking`], playmate
//! targeting in [`selection::play_action_with`] /
//! [`selection::adjacent_playmate`] — so within-shape score/walk
//! agreement continues to rest on those shared helpers, exactly as
//! before.
//!
//! [`selection::priced_nearest_element`]: super::selection::priced_nearest_element
//! [`selection::sunbeam_worth_walking`]: super::selection::sunbeam_worth_walking
//! [`selection::play_action_with`]: super::selection::play_action_with
//! [`selection::adjacent_playmate`]: super::selection::adjacent_playmate

use crate::action::Action;
use crate::element::ElementType;
use crate::needs::NeedKind;

/// The shape of a need's relief: what kind of thing in the world relieves
/// it, and — where the relief is a single action — which action.
pub(crate) enum ReliefSource {
    /// A consumable world element: walk to the nearest (priced), use it
    /// when adjacent.
    Element { kind: ElementType, use_it: Action },
    /// Sunbeam terrain: nap in one when standing in it, walk to one only
    /// within `sunbeam_reach`, otherwise nap on the spot.
    Sunbeam,
    /// A playmate (critter or kitty): targeting, give-up, and the solo
    /// backstop are owned by `selection` and deliberately unpriced.
    Playmate,
    /// A fellow kitty for company: nearest *free* friend, conscription
    /// etiquette applies.
    Friend,
    /// Relieved wherever the cat is standing.
    InPlace { use_it: Action },
}

impl NeedKind {
    /// The one authoritative need→relief pairing (spec 019 FR-001).
    /// Exhaustive over `NeedKind`: a new need compiles only once its
    /// relief is defined here, and every consumer handles it through the
    /// shape arms above.
    pub(crate) fn relief(self) -> ReliefSource {
        match self {
            NeedKind::Eat => ReliefSource::Element {
                kind: ElementType::Chow,
                use_it: Action::Eat,
            },
            NeedKind::Drink => ReliefSource::Element {
                kind: ElementType::Water,
                use_it: Action::Drink,
            },
            NeedKind::Sleep => ReliefSource::Sunbeam,
            NeedKind::Play => ReliefSource::Playmate,
            NeedKind::Cuddle => ReliefSource::Friend,
            NeedKind::Bath => ReliefSource::InPlace {
                use_it: Action::Groom { target: None },
            },
        }
    }
}
