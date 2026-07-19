//! Actions: what a kitty does with its tick.
//!
//! Article IV: behaviors *propose*, the engine disposes. Every proposal passes
//! through [`validate`], which returns the action to actually apply --
//! [`Action::Idle`] whenever the proposal is illegal for the current world state.
//! Nothing here can return an error, because an advisor's mistake must never
//! become a kitty's problem.

use serde::{Deserialize, Serialize};

use crate::config::Config;
use crate::element::{ElementId, ElementKind, ElementType};
use crate::grid::Direction;
use crate::kitty::{Activity, KittyId};
use crate::meow::{cooldown_for, Meow, MessageKind};
use crate::needs::NeedKind;
use crate::world::World;

/// What a `chase` or `play` action is aimed at.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "target", rename_all = "snake_case")]
pub enum TargetRef {
    Element { id: ElementId },
    Kitty { id: KittyId },
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
pub enum Action {
    Move {
        direction: Direction,
    },
    Rest {
        #[serde(default)]
        with: Option<KittyId>,
    },
    Sleep {
        #[serde(default)]
        with: Option<KittyId>,
    },
    Groom {
        #[serde(default)]
        target: Option<KittyId>,
    },
    Eat,
    Drink,
    Chase(TargetRef),
    Play(TargetRef),
    Purr,
    Meow {
        message: MessageKind,
    },
    Idle,
}

impl Action {
    pub fn move_to(direction: Direction) -> Self {
        Action::Move { direction }
    }

    /// Play and chase -- the actions a cat takes purely for fun. Used to tell
    /// personalities apart.
    pub fn is_playful(&self) -> bool {
        matches!(self, Action::Play(_) | Action::Chase(_))
    }
}

/// Returns the action the engine will actually apply: the proposal if it is legal,
/// otherwise `Idle`. This is the whole of Article IV's enforcement surface.
pub fn validate(world: &World, kitty_id: KittyId, proposal: Action, config: &Config) -> Action {
    let Some(kitty) = world.kitty(kitty_id) else {
        return Action::Idle;
    };

    let legal = match proposal {
        Action::Idle | Action::Meow { .. } => true,

        // A meow that is on cooldown is still a legal action -- it just produces
        // silence. Purring, however, has to be earned.
        Action::Purr => kitty.happiness > config.thresholds.purr || kitty.happiness_rose,

        Action::Move { direction } => match kitty.pos.step(direction, world.width, world.height) {
            Some(dest) => world.kitty_at(dest).is_none(),
            None => false,
        },

        Action::Rest { with } | Action::Sleep { with } => match with {
            None => true,
            Some(friend_id) => world.is_available_friend(kitty_id, friend_id),
        },

        Action::Groom { target } => match target {
            None => true,
            Some(friend_id) => world.is_available_friend(kitty_id, friend_id),
        },

        Action::Eat => world
            .adjacent_element(kitty.pos, ElementType::Chow)
            .map(|e| matches!(e.kind, ElementKind::Chow { servings } if servings > 0))
            .unwrap_or(false),

        Action::Drink => world
            .adjacent_element(kitty.pos, ElementType::Water)
            .is_some(),

        // Chasing is for things that run away: bugs, greebles and friends. Walking
        // to a food bowl is a `Move`, not a chase.
        Action::Chase(target) => match target {
            TargetRef::Element { id } => world
                .element(id)
                .map(|e| e.element_type().is_critter())
                .unwrap_or(false),
            TargetRef::Kitty { id } => id != kitty_id && world.kitty(id).is_some(),
        },

        Action::Play(target) => match target {
            TargetRef::Element { id } => world
                .element(id)
                .map(|e| e.element_type().is_critter() && kitty.pos.is_adjacent(&e.pos))
                .unwrap_or(false),
            TargetRef::Kitty { id } => world.is_available_friend(kitty_id, id),
        },
    };

    if legal {
        proposal
    } else {
        Action::Idle
    }
}

/// Applies an already-validated action. Every need change goes through the clamped
/// `Need` type, so Article I holds no matter what magnitudes the config carries.
pub fn apply(world: &mut World, kitty_id: KittyId, action: Action, config: &Config) {
    let effects = config.actions;
    let tick = world.tick;

    match action {
        Action::Idle => continue_current_activity(world, kitty_id, config),

        Action::Move { direction } => {
            let Some(kitty) = world.kitty(kitty_id) else {
                return;
            };
            if let Some(dest) = kitty.pos.step(direction, world.width, world.height) {
                if let Some(idx) = world.kitty_index(kitty_id) {
                    world.kitties[idx].pos = dest;
                    world.kitties[idx].activity = Activity::Idle;
                }
            }
        }

        Action::Rest { with } => {
            let partner = with.filter(|f| world.is_available_friend(kitty_id, *f));
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Resting {
                    with_friend: partner,
                };
            }
            if let Some(friend) = partner {
                lower_need(world, kitty_id, NeedKind::Cuddle, effects.cuddle_relief);
                lower_need(world, friend, NeedKind::Cuddle, effects.cuddle_relief);
            }
        }

        Action::Sleep { with } => {
            let partner = with.filter(|f| world.is_available_friend(kitty_id, *f));
            let in_sunbeam = world
                .kitty(kitty_id)
                .map(|k| {
                    world.element_at(k.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam)
                })
                .unwrap_or(false);
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Sleeping {
                    in_sunbeam,
                    with_friend: partner,
                };
            }
            apply_sleep_relief(world, kitty_id, in_sunbeam, partner, config);
        }

        Action::Groom { target } => match target {
            None => {
                lower_need(world, kitty_id, NeedKind::Bath, effects.groom_relief);
                set_idle(world, kitty_id);
            }
            Some(friend) => {
                // Grooming a friend cleans them and satisfies the groomer's own
                // need for closeness.
                lower_need(world, friend, NeedKind::Bath, effects.groom_relief);
                lower_need(world, kitty_id, NeedKind::Cuddle, effects.cuddle_relief);
                set_idle(world, kitty_id);
            }
        },

        Action::Eat => {
            let Some(pos) = world.kitty(kitty_id).map(|k| k.pos) else {
                return;
            };
            if let Some(id) = world.adjacent_element(pos, ElementType::Chow).map(|e| e.id) {
                if let Some(el) = world.element_mut(id) {
                    if let ElementKind::Chow { servings } = &mut el.kind {
                        *servings = servings.saturating_sub(1);
                    }
                }
                lower_need(world, kitty_id, NeedKind::Eat, effects.eat_relief);
            }
            set_idle(world, kitty_id);
        }

        Action::Drink => {
            lower_need(world, kitty_id, NeedKind::Drink, effects.drink_relief);
            set_idle(world, kitty_id);
        }

        Action::Chase(target) => {
            let Some(kitty_pos) = world.kitty(kitty_id).map(|k| k.pos) else {
                return;
            };
            let target_pos = match target {
                TargetRef::Element { id } => world.element(id).map(|e| e.pos),
                TargetRef::Kitty { id } => world.kitty(id).map(|k| k.pos),
            };
            if let Some(target_pos) = target_pos {
                if let Some(dir) = Direction::toward(kitty_pos, target_pos) {
                    if let Some(dest) = kitty_pos.step(dir, world.width, world.height) {
                        // A chase that runs into another kitty simply stalls; the
                        // spec turns blocked movement into idling, never an error.
                        if world.kitty_at(dest).is_none() {
                            if let Some(idx) = world.kitty_index(kitty_id) {
                                world.kitties[idx].pos = dest;
                            }
                        }
                    }
                }
            }
            set_idle(world, kitty_id);
        }

        Action::Play(target) => {
            lower_need(world, kitty_id, NeedKind::Play, effects.play_relief);
            if let TargetRef::Kitty { id } = target {
                // Play is shared: both cats get the fun.
                lower_need(world, id, NeedKind::Play, effects.play_relief);
            }
            set_idle(world, kitty_id);
        }

        Action::Purr => {
            emit_meow(world, kitty_id, MessageKind::Purr, config, tick);
        }

        Action::Meow { message } => {
            emit_meow(world, kitty_id, message, config, tick);
        }
    }
}

/// Sleeping and resting persist across ticks: a kitty that proposes nothing keeps
/// doing what it was doing (and keeps getting the benefit). A partner who wandered
/// off is quietly dropped rather than continuing to grant cuddles from afar.
fn continue_current_activity(world: &mut World, kitty_id: KittyId, config: &Config) {
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    match kitty.activity {
        Activity::Idle => {}
        Activity::Resting { with_friend } => {
            let partner = with_friend.filter(|f| world.is_available_friend(kitty_id, *f));
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Resting {
                    with_friend: partner,
                };
            }
            if let Some(friend) = partner {
                lower_need(
                    world,
                    kitty_id,
                    NeedKind::Cuddle,
                    config.actions.cuddle_relief,
                );
                lower_need(
                    world,
                    friend,
                    NeedKind::Cuddle,
                    config.actions.cuddle_relief,
                );
            }
        }
        Activity::Sleeping { with_friend, .. } => {
            let partner = with_friend.filter(|f| world.is_available_friend(kitty_id, *f));
            // Re-check the sunbeam: it may have drifted away while the cat slept.
            let pos = kitty.pos;
            let in_sunbeam =
                world.element_at(pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam);
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Sleeping {
                    in_sunbeam,
                    with_friend: partner,
                };
            }
            apply_sleep_relief(world, kitty_id, in_sunbeam, partner, config);
        }
    }
}

fn apply_sleep_relief(
    world: &mut World,
    kitty_id: KittyId,
    in_sunbeam: bool,
    partner: Option<KittyId>,
    config: &Config,
) {
    let relief = if in_sunbeam {
        config.actions.sleep_relief_sunbeam
    } else {
        config.actions.sleep_relief
    };
    lower_need(world, kitty_id, NeedKind::Sleep, relief);
    if let Some(friend) = partner {
        lower_need(
            world,
            kitty_id,
            NeedKind::Cuddle,
            config.actions.cuddle_relief,
        );
        lower_need(
            world,
            friend,
            NeedKind::Cuddle,
            config.actions.cuddle_relief,
        );
    }
}

fn emit_meow(
    world: &mut World,
    kitty_id: KittyId,
    message: MessageKind,
    config: &Config,
    tick: u64,
) {
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    // A meow on cooldown is swallowed, but the kitty still spent its turn saying
    // nothing -- exactly as the spec requires.
    if !kitty.can_meow(message, tick) {
        return;
    }
    let need_value = message.related_need().map(|n| kitty.needs.get(n));
    let cooldown = cooldown_for(
        message,
        need_value,
        config.meow.cooldown_ticks,
        config.meow.urgent_cooldown_ticks,
        config.meow.urgent_need_threshold,
    );
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].set_meow_cooldown(message, tick + cooldown);
    }
    world.recent_meows.push(Meow {
        kitty_id,
        kind: message,
        tick,
    });
}

fn lower_need(world: &mut World, kitty_id: KittyId, need: NeedKind, amount: f32) {
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].needs.add(need, -amount.abs());
    }
}

fn set_idle(world: &mut World, kitty_id: KittyId) {
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].activity = Activity::Idle;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::element::Element;
    use crate::grid::Position;
    use crate::test_support::test_world;

    #[test]
    fn blocked_moves_become_idle() {
        let (mut world, config) = test_world();
        // Put kitty 1 in the top-left corner and try to walk off the edge.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(0, 0);

        let validated = validate(&world, 1, Action::move_to(Direction::North), &config);
        assert_eq!(validated, Action::Idle, "walking off the grid is illegal");
    }

    #[test]
    fn moving_onto_another_kitty_is_illegal() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        let b = world.kitty_index(2).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[b].pos = Position::new(5, 4); // directly north

        let validated = validate(&world, 1, Action::move_to(Direction::North), &config);
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn eating_requires_nearby_chow() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);

        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Idle);

        world.push_element(Element {
            id: 900,
            kind: ElementKind::Chow { servings: 2 },
            pos: Position::new(5, 6),
            ttl: None,
        });
        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Eat);
    }

    #[test]
    fn empty_chow_cannot_be_eaten() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Chow { servings: 0 },
            pos: Position::new(5, 5),
            ttl: None,
        });
        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Idle);
    }

    #[test]
    fn eating_consumes_one_serving_and_relieves_hunger() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
        world.push_element(Element {
            id: 902,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(5, 5),
            ttl: None,
        });

        apply(&mut world, 1, Action::Eat, &config);

        let kitty = world.kitty(1).unwrap();
        assert!(
            (kitty.needs.get(NeedKind::Eat) - 40.0).abs() < 0.01,
            "80 - 40 relief"
        );
        let chow = world.element(902).unwrap();
        assert!(matches!(chow.kind, ElementKind::Chow { servings: 2 }));
    }

    #[test]
    fn playing_with_a_friend_delights_them_both() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[a].needs.add(NeedKind::Play, 60.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(5, 6);
        world.kitties[b].needs.add(NeedKind::Play, 60.0);

        apply(
            &mut world,
            1,
            Action::Play(TargetRef::Kitty { id: 2 }),
            &config,
        );

        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Play) - 35.0).abs() < 0.01);
        assert!(
            (world.kitty(2).unwrap().needs.get(NeedKind::Play) - 35.0).abs() < 0.01,
            "the friend has fun too"
        );
    }

    #[test]
    fn playing_with_a_distant_friend_is_illegal() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(1, 1);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);

        let validated = validate(&world, 1, Action::Play(TargetRef::Kitty { id: 2 }), &config);
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn purring_must_be_earned() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = false;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);

        // Either a high happiness...
        world.kitties[idx].happiness = 80.0;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Purr);

        // ...or an improving one.
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = true;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Purr);
    }

    #[test]
    fn grooming_a_friend_cleans_them_and_comforts_the_groomer() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Bath, 60.0);

        apply(&mut world, 1, Action::Groom { target: Some(2) }, &config);

        assert!((world.kitty(2).unwrap().needs.get(NeedKind::Bath) - 30.0).abs() < 0.01);
        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Cuddle) - 30.0).abs() < 0.01);
    }

    #[test]
    fn sleeping_in_a_sunbeam_is_more_restful() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(6, 6);
        world.kitties[idx].needs.add(NeedKind::Sleep, 90.0);

        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        let plain = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);

        let idx2 = world.kitty_index(2).unwrap();
        world.kitties[idx2].pos = Position::new(2, 2);
        world.kitties[idx2].needs.add(NeedKind::Sleep, 90.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(2, 2),
            ttl: Some(50),
        });
        apply(&mut world, 2, Action::Sleep { with: None }, &config);
        let sunny = 90.0 - world.kitty(2).unwrap().needs.get(NeedKind::Sleep);

        assert!(sunny > plain, "sunbeam {sunny} should beat plain {plain}");
    }

    #[test]
    fn meows_on_cooldown_are_silently_dropped() {
        let (mut world, config) = test_world();
        apply(
            &mut world,
            1,
            Action::Meow {
                message: MessageKind::FollowMe,
            },
            &config,
        );
        assert_eq!(world.recent_meows.len(), 1);

        // Immediately again: cooldown swallows it, but it was still a legal action.
        apply(
            &mut world,
            1,
            Action::Meow {
                message: MessageKind::FollowMe,
            },
            &config,
        );
        assert_eq!(world.recent_meows.len(), 1, "second meow was dropped");
    }

    #[test]
    fn idling_keeps_a_sleeping_kitty_asleep() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Sleep, 80.0);
        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        assert!(world.kitty(1).unwrap().activity.is_sleeping());

        let before = world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        apply(&mut world, 1, Action::Idle, &config);
        let after = world.kitty(1).unwrap().needs.get(NeedKind::Sleep);

        assert!(world.kitty(1).unwrap().activity.is_sleeping());
        assert!(after < before, "sleep continues to restore");
    }

    #[test]
    fn a_departed_partner_stops_granting_cuddles() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(3, 3);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(3, 4);

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(world.kitty(1).unwrap().activity.partner(), Some(2));

        // The friend wanders off.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);
        apply(&mut world, 1, Action::Idle, &config);

        assert_eq!(
            world.kitty(1).unwrap().activity.partner(),
            None,
            "resting continues, but alone"
        );
    }

    #[test]
    fn chasing_a_vanished_target_is_illegal() {
        let (world, config) = test_world();
        let validated = validate(
            &world,
            1,
            Action::Chase(TargetRef::Element { id: 99_999 }),
            &config,
        );
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn only_critters_can_be_chased() {
        let (mut world, config) = test_world();
        world.elements.clear();
        world.push_element(Element {
            id: 910,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(7, 7),
            ttl: None,
        });
        world.push_element(Element {
            id: 911,
            kind: ElementKind::Bug,
            pos: Position::new(8, 8),
            ttl: Some(50),
        });

        // Food does not flee.
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Element { id: 910 }),
                &config
            ),
            Action::Idle
        );
        // Bugs do.
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Element { id: 911 }),
                &config
            ),
            Action::Chase(TargetRef::Element { id: 911 })
        );
    }

    #[test]
    fn a_kitty_cannot_target_itself() {
        let (world, config) = test_world();
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Kitty { id: 1 }),
                &config
            ),
            Action::Idle
        );
        assert_eq!(
            validate(&world, 1, Action::Play(TargetRef::Kitty { id: 1 }), &config),
            Action::Idle
        );
    }
}
