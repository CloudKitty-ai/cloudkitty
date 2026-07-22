//! Action codec v1 (spec 014 FR-006): the versioned bijection between the
//! flat action menu and engine proposals, total in both directions.
//!
//! With the default slot counts (3 kitty, 4 critter) the menu is the
//! normative 40-entry table from contracts/encodings.md:
//!
//! | Index | Proposal |
//! |-------|----------|
//! | 0–3   | Move North / East / South / West |
//! | 4     | Rest (solo) |
//! | 5–7   | Rest with kitty slot 0 / 1 / 2 (cuddle) |
//! | 8     | Sleep (solo) |
//! | 9–11  | Sleep with kitty slot 0 / 1 / 2 |
//! | 12    | Groom (self) |
//! | 13–15 | Groom kitty slot 0 / 1 / 2 |
//! | 16    | Eat |
//! | 17    | Drink |
//! | 18–21 | Chase critter slot 0 / 1 / 2 / 3 |
//! | 22–24 | Chase kitty slot 0 / 1 / 2 |
//! | 25    | Play (solo pounce) |
//! | 26–29 | Play with critter slot 0 / 1 / 2 / 3 |
//! | 30–32 | Play with kitty slot 0 / 1 / 2 |
//! | 33–38 | Meow: want-eat / want-drink / follow-me / want-play / want-cuddle / purr |
//! | 39    | Idle |
//!
//! **Totality**: every in-range index decodes to a proposal — a vacant or
//! stale slot decodes to a proposal naming an entity that does not exist,
//! which the engine lawfully resolves to idle (Article IV); never a decode
//! error. Every proposable action *expressible through the table* encodes to
//! an index (`encode` returns None for actions the menu cannot express —
//! e.g. a target outside every slot, or the retired Purr action).
//!
//! **Extensibility**: the menu grows only by codec version bump; indices are
//! never repurposed; there are no reserved indices.

use cloudkitty_core::action::{Action, TargetRef};
use cloudkitty_core::element::ElementId;
use cloudkitty_core::grid::Direction;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::meow::MessageKind;
use thiserror::Error;

use crate::config::ObservationConfig;
use crate::observe::{TargetTable, LEARNED_MEOWS};

/// Version pinned into policy artifacts (FR-007/FR-016). The mask schema is
/// versioned with the codec.
pub const ACTION_SCHEMA_VERSION: u32 = 1;

/// The id a vacant slot decodes to: no kitty or element ever carries it, so
/// the resulting proposal fails validation and lawfully resolves to idle.
pub const VACANT_KITTY: KittyId = KittyId::MAX;
pub const VACANT_ELEMENT: ElementId = ElementId::MAX;

#[derive(Debug, Error, Clone, Copy, PartialEq, Eq)]
pub enum CodecError {
    #[error("action index {index} out of range: the menu has {len} entries")]
    OutOfRange { index: usize, len: usize },
}

/// One menu entry, slot references unresolved.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MenuEntry {
    Move(Direction),
    RestSolo,
    RestWithKitty(usize),
    SleepSolo,
    SleepWithKitty(usize),
    GroomSelf,
    GroomKitty(usize),
    Eat,
    Drink,
    ChaseCritter(usize),
    ChaseKitty(usize),
    PlaySolo,
    PlayCritter(usize),
    PlayKitty(usize),
    Meow(MessageKind),
    Idle,
}

/// The versioned menu for a slot configuration.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActionCodec {
    entries: Vec<MenuEntry>,
}

impl ActionCodec {
    /// Builds menu v1 for the configured slot counts. The default
    /// configuration yields the normative 40-entry menu.
    pub fn v1(cfg: &ObservationConfig) -> Self {
        use MenuEntry::*;
        let k = cfg.kitty_slots;
        let c = cfg.critter_slots;
        let mut entries = Vec::with_capacity(4 + 3 * (1 + k) + 2 + c + k + 1 + c + k + 7);
        entries.extend(Direction::ALL.into_iter().map(Move));
        entries.push(RestSolo);
        entries.extend((0..k).map(RestWithKitty));
        entries.push(SleepSolo);
        entries.extend((0..k).map(SleepWithKitty));
        entries.push(GroomSelf);
        entries.extend((0..k).map(GroomKitty));
        entries.push(Eat);
        entries.push(Drink);
        entries.extend((0..c).map(ChaseCritter));
        entries.extend((0..k).map(ChaseKitty));
        entries.push(PlaySolo);
        entries.extend((0..c).map(PlayCritter));
        entries.extend((0..k).map(PlayKitty));
        entries.extend(LEARNED_MEOWS.into_iter().map(Meow));
        entries.push(Idle);
        ActionCodec { entries }
    }

    /// The menu length (40 with default slots).
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    pub fn entries(&self) -> &[MenuEntry] {
        &self.entries
    }

    /// Decodes a menu index into an engine proposal through the table.
    /// Total over the in-range menu: vacant slots decode to proposals naming
    /// [`VACANT_KITTY`]/[`VACANT_ELEMENT`], which validation resolves to
    /// idle. Errors only on an out-of-range index (a caller error).
    pub fn decode(&self, index: usize, table: &TargetTable) -> Result<Action, CodecError> {
        let entry = self.entries.get(index).ok_or(CodecError::OutOfRange {
            index,
            len: self.entries.len(),
        })?;
        let kitty = |slot: usize| table.kitties.get(slot).copied().flatten();
        let critter = |slot: usize| table.critters.get(slot).copied().flatten();
        Ok(match *entry {
            MenuEntry::Move(direction) => Action::Move { direction },
            MenuEntry::RestSolo => Action::Rest { with: None },
            MenuEntry::RestWithKitty(s) => Action::Rest {
                with: Some(kitty(s).unwrap_or(VACANT_KITTY)),
            },
            MenuEntry::SleepSolo => Action::Sleep { with: None },
            MenuEntry::SleepWithKitty(s) => Action::Sleep {
                with: Some(kitty(s).unwrap_or(VACANT_KITTY)),
            },
            MenuEntry::GroomSelf => Action::Groom { target: None },
            MenuEntry::GroomKitty(s) => Action::Groom {
                target: Some(kitty(s).unwrap_or(VACANT_KITTY)),
            },
            MenuEntry::Eat => Action::Eat,
            MenuEntry::Drink => Action::Drink,
            MenuEntry::ChaseCritter(s) => Action::Chase(TargetRef::Element {
                id: critter(s).unwrap_or(VACANT_ELEMENT),
            }),
            MenuEntry::ChaseKitty(s) => Action::Chase(TargetRef::Kitty {
                id: kitty(s).unwrap_or(VACANT_KITTY),
            }),
            MenuEntry::PlaySolo => Action::Play { target: None },
            MenuEntry::PlayCritter(s) => Action::Play {
                target: Some(TargetRef::Element {
                    id: critter(s).unwrap_or(VACANT_ELEMENT),
                }),
            },
            MenuEntry::PlayKitty(s) => Action::Play {
                target: Some(TargetRef::Kitty {
                    id: kitty(s).unwrap_or(VACANT_KITTY),
                }),
            },
            MenuEntry::Meow(message) => Action::Meow { message },
            MenuEntry::Idle => Action::Idle,
        })
    }

    /// Encodes an engine action back to its menu index, when the table can
    /// express it: targeted actions encode iff their target holds a slot.
    /// Returns None for the inexpressible (a target outside every slot, the
    /// retired `Purr` action, the engine-reserved wait-for-me meow).
    pub fn encode(&self, action: &Action, table: &TargetTable) -> Option<usize> {
        let kitty_slot = |id: KittyId| table.kitties.iter().position(|s| *s == Some(id));
        let critter_slot = |id: ElementId| table.critters.iter().position(|s| *s == Some(id));
        let want = |target: MenuEntry| self.entries.iter().position(|e| *e == target);
        match *action {
            Action::Move { direction } => want(MenuEntry::Move(direction)),
            Action::Rest { with: None } => want(MenuEntry::RestSolo),
            Action::Rest { with: Some(id) } => want(MenuEntry::RestWithKitty(kitty_slot(id)?)),
            Action::Sleep { with: None } => want(MenuEntry::SleepSolo),
            Action::Sleep { with: Some(id) } => want(MenuEntry::SleepWithKitty(kitty_slot(id)?)),
            Action::Groom { target: None } => want(MenuEntry::GroomSelf),
            Action::Groom { target: Some(id) } => want(MenuEntry::GroomKitty(kitty_slot(id)?)),
            Action::Eat => want(MenuEntry::Eat),
            Action::Drink => want(MenuEntry::Drink),
            Action::Chase(TargetRef::Element { id }) => {
                want(MenuEntry::ChaseCritter(critter_slot(id)?))
            }
            Action::Chase(TargetRef::Kitty { id }) => want(MenuEntry::ChaseKitty(kitty_slot(id)?)),
            Action::Play { target: None } => want(MenuEntry::PlaySolo),
            Action::Play {
                target: Some(TargetRef::Element { id }),
            } => want(MenuEntry::PlayCritter(critter_slot(id)?)),
            Action::Play {
                target: Some(TargetRef::Kitty { id }),
            } => want(MenuEntry::PlayKitty(kitty_slot(id)?)),
            Action::Meow { message } => {
                if LEARNED_MEOWS.contains(&message) {
                    want(MenuEntry::Meow(message))
                } else {
                    None
                }
            }
            Action::Purr => None,
            Action::Idle => want(MenuEntry::Idle),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn table() -> TargetTable {
        TargetTable {
            kitties: vec![Some(2), Some(3), None],
            critters: vec![Some(11), None, None, Some(14)],
        }
    }

    #[test]
    fn the_default_menu_has_exactly_forty_entries_in_normative_order() {
        let codec = ActionCodec::v1(&ObservationConfig::default());
        assert_eq!(codec.len(), 40);
        let t = table();
        // Spot-check the normative index table.
        assert_eq!(
            codec.decode(0, &t).unwrap(),
            Action::Move {
                direction: Direction::North
            }
        );
        assert_eq!(codec.decode(4, &t).unwrap(), Action::Rest { with: None });
        assert_eq!(codec.decode(5, &t).unwrap(), Action::Rest { with: Some(2) });
        assert_eq!(codec.decode(8, &t).unwrap(), Action::Sleep { with: None });
        assert_eq!(
            codec.decode(12, &t).unwrap(),
            Action::Groom { target: None }
        );
        assert_eq!(codec.decode(16, &t).unwrap(), Action::Eat);
        assert_eq!(codec.decode(17, &t).unwrap(), Action::Drink);
        assert_eq!(
            codec.decode(18, &t).unwrap(),
            Action::Chase(TargetRef::Element { id: 11 })
        );
        assert_eq!(
            codec.decode(22, &t).unwrap(),
            Action::Chase(TargetRef::Kitty { id: 2 })
        );
        assert_eq!(codec.decode(25, &t).unwrap(), Action::Play { target: None });
        assert_eq!(
            codec.decode(29, &t).unwrap(),
            Action::Play {
                target: Some(TargetRef::Element { id: 14 })
            }
        );
        assert_eq!(
            codec.decode(33, &t).unwrap(),
            Action::Meow {
                message: MessageKind::WantEat
            }
        );
        assert_eq!(
            codec.decode(38, &t).unwrap(),
            Action::Meow {
                message: MessageKind::Purr
            }
        );
        assert_eq!(codec.decode(39, &t).unwrap(), Action::Idle);
    }

    #[test]
    fn vacant_slots_decode_to_engine_rejectable_proposals_never_errors() {
        let codec = ActionCodec::v1(&ObservationConfig::default());
        let t = table();
        // Kitty slot 2 and critter slots 1/2 are vacant.
        assert_eq!(
            codec.decode(7, &t).unwrap(),
            Action::Rest {
                with: Some(VACANT_KITTY)
            }
        );
        assert_eq!(
            codec.decode(19, &t).unwrap(),
            Action::Chase(TargetRef::Element { id: VACANT_ELEMENT })
        );
        // Out of range is the one caller error.
        assert!(matches!(
            codec.decode(40, &t),
            Err(CodecError::OutOfRange { index: 40, len: 40 })
        ));
    }

    #[test]
    fn encode_inverts_decode_for_expressible_actions() {
        let codec = ActionCodec::v1(&ObservationConfig::default());
        let t = table();
        for index in 0..codec.len() {
            let action = codec.decode(index, &t).unwrap();
            // Vacant-slot decodes name nonexistent entities; those are not
            // expressible back (their target holds no slot), by design.
            let names_vacant = matches!(
                action,
                Action::Rest {
                    with: Some(VACANT_KITTY)
                } | Action::Sleep {
                    with: Some(VACANT_KITTY)
                } | Action::Groom {
                    target: Some(VACANT_KITTY)
                } | Action::Chase(TargetRef::Kitty { id: VACANT_KITTY })
                    | Action::Chase(TargetRef::Element { id: VACANT_ELEMENT })
                    | Action::Play {
                        target: Some(TargetRef::Kitty { id: VACANT_KITTY })
                    }
                    | Action::Play {
                        target: Some(TargetRef::Element { id: VACANT_ELEMENT })
                    }
            );
            if names_vacant {
                assert_eq!(codec.encode(&action, &t), None);
            } else {
                assert_eq!(codec.encode(&action, &t), Some(index), "{action:?}");
            }
        }
    }

    #[test]
    fn the_inexpressible_encode_to_none() {
        let codec = ActionCodec::v1(&ObservationConfig::default());
        let t = table();
        // A target outside every slot.
        assert_eq!(codec.encode(&Action::Rest { with: Some(99) }, &t), None);
        // The retired action and the engine-reserved meow.
        assert_eq!(codec.encode(&Action::Purr, &t), None);
        assert_eq!(
            codec.encode(
                &Action::Meow {
                    message: MessageKind::WaitForMe
                },
                &t
            ),
            None
        );
    }
}
