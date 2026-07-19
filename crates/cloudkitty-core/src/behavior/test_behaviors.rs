//! Deliberately badly-behaved behaviors.
//!
//! These exist to prove Article IV holds under hostility: the engine must survive
//! advisors that lie, stall, panic, or flail, and no kitty may suffer for it. They
//! are public so the property suite and integration tests can use them, and so
//! anyone writing an external behavior has adversaries to test against.

use async_trait::async_trait;

use super::{Behavior, DecisionContext};
use crate::action::{Action, TargetRef};
use crate::grid::Direction;
use crate::meow::MessageKind;

/// Proposes actions that are always illegal for the current state. Every turn
/// should be converted to `Idle` by the engine.
pub struct AlwaysInvalid;

#[async_trait]
impl Behavior for AlwaysInvalid {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // Target an element id that cannot exist, and a kitty that is itself.
        if ctx.rng.gen_bool(0.5) {
            Action::play_with(TargetRef::Element { id: u32::MAX })
        } else {
            Action::Chase(TargetRef::Kitty { id: ctx.me.id })
        }
    }
}

/// Flails: any action at all, legal or not, chosen at random.
pub struct Chaos;

#[async_trait]
impl Behavior for Chaos {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        let pick = ctx.rng.gen_range_usize(0, 11);
        let random_kitty = ctx
            .world
            .kitties
            .get(ctx.rng.gen_range_usize(0, ctx.world.kitties.len().max(1)))
            .map(|k| k.id)
            .unwrap_or(0);
        let random_element = ctx
            .world
            .elements
            .get(ctx.rng.gen_range_usize(0, ctx.world.elements.len().max(1)))
            .map(|e| e.id)
            .unwrap_or(u32::MAX);
        let direction = ctx
            .rng
            .choose(&Direction::ALL)
            .copied()
            .unwrap_or(Direction::North);

        match pick {
            0 => Action::move_to(direction),
            1 => Action::Rest {
                with: Some(random_kitty),
            },
            2 => Action::Sleep {
                with: Some(random_kitty),
            },
            3 => Action::Groom {
                target: Some(random_kitty),
            },
            4 => Action::Eat,
            5 => Action::Drink,
            6 => Action::Chase(TargetRef::Element { id: random_element }),
            7 => Action::play_with(TargetRef::Element { id: random_element }),
            8 => Action::Purr,
            9 => Action::Meow {
                message: MessageKind::FollowMe,
            },
            _ => Action::Idle,
        }
    }
}

/// Takes longer than any sane decision budget. Used to prove the timeout path.
pub struct SleepySlow {
    delay_ms: u64,
}

impl SleepySlow {
    pub fn new(delay_ms: u64) -> Self {
        Self { delay_ms }
    }
}

#[async_trait]
impl Behavior for SleepySlow {
    async fn decide(&self, _ctx: &DecisionContext) -> Action {
        tokio::time::sleep(std::time::Duration::from_millis(self.delay_ms)).await;
        Action::Purr
    }
}

/// Panics instead of deciding.
pub struct Panicky;

#[async_trait]
impl Behavior for Panicky {
    async fn decide(&self, _ctx: &DecisionContext) -> Action {
        panic!("this behavior is deliberately broken");
    }
}

/// A well-behaved external behavior: not a builtin (so it *is* budgeted), but fast
/// and legal. Useful for testing the external path without hostility.
pub struct QuietExternal;

#[async_trait]
impl Behavior for QuietExternal {
    async fn decide(&self, _ctx: &DecisionContext) -> Action {
        Action::Idle
    }
}
