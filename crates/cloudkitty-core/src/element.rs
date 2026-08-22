//! Environment elements: the things kitties eat, drink, chase and nap in.
//!
//! Article II: expiry applies to elements *only*. Nothing in this module has an
//! analogue for kitties.

use serde::{Deserialize, Serialize};

use crate::grid::{Direction, Position};
use crate::needs::NeedKind;

pub type ElementId = u32;

/// Reserved: the element allocator never issues this id (spec 014).
/// Downstream encodings use it to mean "no element"; see
/// [`crate::kitty::RESERVED_KITTY_ID`].
pub const RESERVED_ELEMENT_ID: ElementId = ElementId::MAX;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ElementType {
    Water,
    Chow,
    Bug,
    Greeble,
    Sunbeam,
}

impl ElementType {
    pub const ALL: [ElementType; 5] = [
        ElementType::Water,
        ElementType::Chow,
        ElementType::Bug,
        ElementType::Greeble,
        ElementType::Sunbeam,
    ];

    pub fn as_str(&self) -> &'static str {
        match self {
            ElementType::Water => "water",
            ElementType::Chow => "chow",
            ElementType::Bug => "bug",
            ElementType::Greeble => "greeble",
            ElementType::Sunbeam => "sunbeam",
        }
    }

    /// Whether a kitty can perceive this element as a play target.
    pub fn is_critter(&self) -> bool {
        matches!(self, ElementType::Bug | ElementType::Greeble)
    }

    /// The element type that relieves `need`, when relief requires an element.
    /// Used by the Article I safeguard: only eat and drink depend on a *scarce*
    /// resource, so only those can ever leave a kitty without relief. Play is
    /// satisfiable by any critter or friend, cuddle by any friend (there are
    /// always >= 2 kitties), bath by self-grooming, and sleep anywhere (a
    /// sunbeam only makes it faster).
    pub fn for_need(need: NeedKind) -> Option<ElementType> {
        match need {
            NeedKind::Eat => Some(ElementType::Chow),
            NeedKind::Drink => Some(ElementType::Water),
            _ => None,
        }
    }
}

/// Per-kind payload. Serialized flattened onto `Element` with a `kind` tag, so the
/// wire shape is `{"id":9,"kind":"chow","pos":{..},"servings":3}`.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ElementKind {
    Water,
    Chow { servings: u32 },
    Bug,
    Greeble { heading: Direction },
    Sunbeam,
}

impl ElementKind {
    pub fn element_type(&self) -> ElementType {
        match self {
            ElementKind::Water => ElementType::Water,
            ElementKind::Chow { .. } => ElementType::Chow,
            ElementKind::Bug => ElementType::Bug,
            ElementKind::Greeble { .. } => ElementType::Greeble,
            ElementKind::Sunbeam => ElementType::Sunbeam,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Element {
    pub id: ElementId,
    #[serde(flatten)]
    pub kind: ElementKind,
    pub pos: Position,
    /// Ticks remaining before expiry; `None` means permanent.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ttl: Option<u64>,
}

impl Element {
    pub fn element_type(&self) -> ElementType {
        self.kind.element_type()
    }

    /// True once a timed element has run out, or a chow has no servings left.
    pub fn is_expired(&self) -> bool {
        if let ElementKind::Chow { servings } = self.kind {
            if servings == 0 {
                return true;
            }
        }
        matches!(self.ttl, Some(0))
    }

    pub fn tick_ttl(&mut self) {
        if let Some(ttl) = self.ttl.as_mut() {
            *ttl = ttl.saturating_sub(1);
        }
    }

    /// The critter rest-tick schedule: move every second tick. Bugs always
    /// live on it; greebles join it under `dart` (spec 039 third
    /// amendment). Deriving the schedule from `(tick + id)` keeps it
    /// stateless and deterministic, and staggers the population so they
    /// don't all move in lockstep.
    pub fn critter_moves_this_tick(&self, tick: u64) -> bool {
        (tick.wrapping_add(self.id as u64)).is_multiple_of(2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn chow(servings: u32) -> Element {
        Element {
            id: 1,
            kind: ElementKind::Chow { servings },
            pos: Position::new(0, 0),
            ttl: None,
        }
    }

    #[test]
    fn chow_expires_when_emptied() {
        assert!(!chow(1).is_expired());
        assert!(chow(0).is_expired());
    }

    #[test]
    fn timed_elements_expire_at_zero() {
        let mut bug = Element {
            id: 2,
            kind: ElementKind::Bug,
            pos: Position::new(1, 1),
            ttl: Some(2),
        };
        assert!(!bug.is_expired());
        bug.tick_ttl();
        assert!(!bug.is_expired());
        bug.tick_ttl();
        assert!(bug.is_expired());
        // Saturating: ticking past zero stays at zero rather than wrapping.
        bug.tick_ttl();
        assert_eq!(bug.ttl, Some(0));
    }

    #[test]
    fn permanent_elements_never_expire() {
        let water = Element {
            id: 3,
            kind: ElementKind::Water,
            pos: Position::new(2, 2),
            ttl: None,
        };
        assert!(!water.is_expired());
    }

    #[test]
    fn only_food_and_water_are_safeguard_resources() {
        assert_eq!(
            ElementType::for_need(NeedKind::Eat),
            Some(ElementType::Chow)
        );
        assert_eq!(
            ElementType::for_need(NeedKind::Drink),
            Some(ElementType::Water)
        );
        for need in [
            NeedKind::Play,
            NeedKind::Cuddle,
            NeedKind::Sleep,
            NeedKind::Bath,
        ] {
            assert_eq!(ElementType::for_need(need), None);
        }
    }

    #[test]
    fn bugs_move_every_other_tick() {
        let bug = Element {
            id: 0,
            kind: ElementKind::Bug,
            pos: Position::new(0, 0),
            ttl: Some(10),
        };
        assert!(bug.critter_moves_this_tick(0));
        assert!(!bug.critter_moves_this_tick(1));
        assert!(bug.critter_moves_this_tick(2));
    }

    #[test]
    fn wire_shape_flattens_kind() {
        let json = serde_json::to_value(chow(3)).unwrap();
        assert_eq!(json["kind"], "chow");
        assert_eq!(json["servings"], 3);
        assert!(json.get("ttl").is_none(), "permanent elements omit ttl");
    }
}
