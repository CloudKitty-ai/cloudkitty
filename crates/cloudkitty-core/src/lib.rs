//! CloudKitty's simulation engine: the law of the kitty world.
//!
//! This crate is pure simulation. It has no HTTP, no filesystem, and no wall-clock
//! dependence in its logic, so tests can drive thousands of ticks headless in
//! milliseconds and the server crate stays a thin shell around [`World::tick`].
//!
//! The constitution (`.specify/memory/constitution.md`) is enforced here:
//!
//! - **Article I** — [`needs::Need`] clamps to `[0, 100]` on every mutation,
//!   [`needs::happiness`] applies a floor, and [`spawn::safeguard`] guarantees
//!   relief exists for any need past the safeguard threshold.
//! - **Article II** — [`kitty::Kitty`] has no health, damage or despawn concept, and
//!   [`World`] exposes no API that removes a kitty.
//! - **Article III** — [`config::Config::validate`] rejects rosters under two, and
//!   [`invariants::check`] re-asserts the population every tick.
//! - **Article IV** — [`behavior::Behavior`] implementations only *propose*;
//!   [`action::validate`] is the sole gate into [`action::apply`].
//! - **Article V** — one seeded [`rng::SimRng`], a fixed tick order in
//!   [`World::tick`], and per-kitty decision streams derived before any decision
//!   runs, so concurrency cannot leak into outcomes.

pub mod action;
pub mod behavior;
pub mod config;
pub mod element;
pub mod events;
pub mod grid;
pub mod invariants;
pub mod kitty;
pub mod meow;
pub mod needs;
pub mod rng;
pub mod spawn;
pub mod test_support;
pub mod world;

pub use action::{Action, TargetRef};
pub use behavior::{Behavior, BehaviorRegistry, DecisionContext};
pub use config::{Config, ConfigError};
pub use element::{Element, ElementId, ElementKind, ElementType};
pub use events::{DistressEvent, DistressLog};
pub use grid::{Direction, Position};
pub use invariants::Violation;
pub use kitty::{Activity, Kitty, KittyId};
pub use meow::{Meow, MessageKind};
pub use needs::{Need, NeedKind, Needs};
pub use world::{World, WorldSnapshot};
