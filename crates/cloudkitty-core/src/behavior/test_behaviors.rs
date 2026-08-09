//! Deliberately badly-behaved behaviors.
//!
//! These exist to prove Article IV holds under hostility: the engine must survive
//! advisors that lie, stall, panic, or flail, and no kitty may suffer for it. They
//! are public so the property suite and integration tests can use them, and so
//! anyone writing an external behavior has adversaries to test against.

use async_trait::async_trait;

use super::{Behavior, DecisionContext};
use crate::seam::Decision;
use crate::action::{Action, TargetRef};
use crate::grid::Direction;
use crate::meow::MessageKind;

/// Proposes actions that are always illegal for the current state. Every turn
/// should be converted to `Idle` by the engine.
pub struct AlwaysInvalid;

#[async_trait]
impl Behavior for AlwaysInvalid {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        // Target an element id that cannot exist, and a kitty that is itself.
        if ctx.rng.gen_bool(0.5) {
            Action::play_with(TargetRef::Element { id: u32::MAX }).into()
        } else {
            Action::Chase(TargetRef::Kitty { id: ctx.me.id }).into()
        }
    }
}

/// Flails: any action at all, legal or not, chosen at random.
pub struct Chaos;

#[async_trait]
impl Behavior for Chaos {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
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

        let action = match pick {
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
        };
        action.into()
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
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        tokio::time::sleep(std::time::Duration::from_millis(self.delay_ms)).await;
        Action::Purr.into()
    }
}

/// Burns CPU synchronously without ever yielding — the shape of a slow
/// synchronous advisor or a hot loop. Exists to prove the budget preempts
/// advisors that never hit an await point (spec 014 review): a timeout
/// wrapped directly around such a future could never fire.
pub struct BusySpin {
    delay_ms: u64,
}

impl BusySpin {
    pub fn new(delay_ms: u64) -> Self {
        Self { delay_ms }
    }
}

#[async_trait]
impl Behavior for BusySpin {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        let start = std::time::Instant::now();
        while start.elapsed() < std::time::Duration::from_millis(self.delay_ms) {
            std::hint::spin_loop();
        }
        Action::Purr.into()
    }
}

/// Draws from its decision stream, then panics. Exists to prove the
/// fallback rule (spec 014 second review): the fallback restarts from the
/// dealt seed on every dispatch path, so a failed advisor's partial draws
/// never shift the fallback's stream — served and budgetless worlds stay
/// byte-identical even while surviving a broken advisor.
pub struct DrawsThenPanics;

#[async_trait]
impl Behavior for DrawsThenPanics {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        // Consume a few draws so a fallback on the *consumed* stream would
        // visibly diverge from one restarted at the seed.
        let _ = ctx.rng.gen_bool(0.5);
        let _ = ctx.rng.gen_f32();
        panic!("drew twice, then broke");
    }
}

/// Panics instead of deciding.
pub struct Panicky;

#[async_trait]
impl Behavior for Panicky {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        panic!("this behavior is deliberately broken");
    }
}

/// A well-behaved external behavior: not a builtin (so it *is* budgeted), but fast
/// and legal. Useful for testing the external path without hostility.
pub struct QuietExternal;

#[async_trait]
impl Behavior for QuietExternal {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        Action::Idle.into()
    }
}

/// Never produces an intelligible proposal: `try_decide` is `None` every
/// turn -- the shape of an external advisor whose reply failed to parse
/// (spec 016). Proves that "no proposal" rides the crashed-advisor path:
/// fallback from the dealt seed, `FallbackTaken` provenance, and never a
/// reshaped legal action.
pub struct Unintelligible;

#[async_trait]
impl Behavior for Unintelligible {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        unreachable!("dispatch consults try_decide; Unintelligible never decides")
    }

    async fn try_decide(&self, _ctx: &DecisionContext) -> Option<Decision> {
        None
    }
}
