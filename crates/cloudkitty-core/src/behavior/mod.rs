//! Pluggable behaviors: untrusted advisors to a sovereign engine.
//!
//! Article IV in one paragraph: a behavior is handed a read-only view of the world
//! and returns *one proposed action*. It cannot touch the world. Whatever it
//! returns is validated before it is applied, and anything illegal becomes an idle
//! turn. A behavior that hangs, panics, or returns nonsense costs its kitty a
//! moment of cleverness and nothing more.
//!
//! The `async` signature is deliberate and is the whole extension point: a future
//! `ScriptBehavior`, `HttpBehavior`, or local-service behavior drops in here with
//! no engine changes. Built-in behaviors resolve immediately and are exempt from
//! the wall-clock budget -- that exemption is what keeps Article V's determinism
//! unconditional, since a slow machine can never change what a built-in decides.

use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::Duration;

use async_trait::async_trait;
use futures::future::join_all;
use futures::FutureExt;

use crate::action::Action;
use crate::config::Config;
use crate::kitty::{Kitty, KittyId};
use crate::rng::DecisionRng;
use crate::world::{World, WorldSnapshot};

pub mod needs_driven;
pub mod playful;
pub mod test_behaviors;

pub use needs_driven::NeedsDriven;
pub use playful::Playful;

/// Everything a behavior is allowed to know. Read-only by construction.
pub struct DecisionContext {
    /// The deciding kitty's own full state.
    pub me: Kitty,
    /// The start-of-tick world: every kitty, every element (greebles included --
    /// cats can always perceive them), and recent meows.
    pub world: Arc<WorldSnapshot>,
    /// This kitty's private randomness for this tick. The only randomness a
    /// behavior may use; anything else would break determinism.
    pub rng: DecisionRng,
    pub config: Arc<Config>,
}

#[async_trait]
pub trait Behavior: Send + Sync {
    /// Propose one action. Never applied directly -- the engine validates first.
    async fn decide(&self, ctx: &DecisionContext) -> Action;

    /// Built-ins run in-process and are exempt from the wall-clock decision
    /// budget. External implementations must leave this as `false`.
    fn is_builtin(&self) -> bool {
        false
    }
}

/// Maps configured behavior names to implementations.
#[derive(Clone, Default)]
pub struct BehaviorRegistry {
    map: BTreeMap<String, Arc<dyn Behavior>>,
}

impl BehaviorRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    /// The behaviors CloudKitty ships with.
    pub fn with_builtins() -> Self {
        let mut registry = Self::new();
        registry.register("needs_driven", Arc::new(NeedsDriven));
        registry.register("playful", Arc::new(Playful));
        registry
    }

    pub fn register(&mut self, name: impl Into<String>, behavior: Arc<dyn Behavior>) {
        self.map.insert(name.into(), behavior);
    }

    pub fn get(&self, name: &str) -> Option<Arc<dyn Behavior>> {
        self.map.get(name).cloned()
    }

    pub fn names(&self) -> Vec<String> {
        self.map.keys().cloned().collect()
    }
}

impl std::fmt::Debug for BehaviorRegistry {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("BehaviorRegistry")
            .field("behaviors", &self.names())
            .finish()
    }
}

/// Phase 1 of the tick: everyone decides, concurrently, against one shared
/// snapshot.
///
/// Per-kitty RNG streams are drawn here in stable id order *before* any decision
/// runs, so however the futures interleave, the randomness each kitty sees is the
/// same. That is what makes concurrency safe for determinism.
pub async fn gather_decisions(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> Vec<(KittyId, Action)> {
    let snapshot = Arc::new(world.snapshot());
    let budget = Duration::from_millis(config.behavior.budget_ms(config.world.tick_ms));

    let ids: Vec<KittyId> = world.kitties.iter().map(|k| k.id).collect();
    let mut jobs = Vec::with_capacity(ids.len());
    for id in ids {
        let Some(kitty) = world.kitty(id).cloned() else {
            continue;
        };
        let behavior = registry.get(&kitty.behavior);
        let ctx = DecisionContext {
            me: kitty,
            world: snapshot.clone(),
            rng: world.rng.derive_decision_rng(),
            config: config.clone(),
        };
        jobs.push((id, behavior, ctx));
    }

    let decisions = jobs
        .into_iter()
        .map(|(id, behavior, ctx)| async move { (id, decide_one(behavior, &ctx, budget).await) });

    join_all(decisions).await
}

async fn decide_one(
    behavior: Option<Arc<dyn Behavior>>,
    ctx: &DecisionContext,
    budget: Duration,
) -> Action {
    match behavior {
        // A name that resolves to nothing is a config error caught at startup; if
        // one somehow reaches here, the kitty still gets a sensible turn.
        None => NeedsDriven.decide(ctx).await,

        Some(b) if b.is_builtin() => match run_catching(b.as_ref(), ctx).await {
            Some(action) => action,
            None => fallback(ctx).await,
        },

        Some(b) => match tokio::time::timeout(budget, run_catching(b.as_ref(), ctx)).await {
            Ok(Some(action)) => action,
            // Timed out, panicked, or otherwise failed: the default behavior takes
            // this kitty's turn.
            _ => fallback(ctx).await,
        },
    }
}

/// Runs a behavior, converting a panic into `None` rather than unwinding into the
/// tick loop.
async fn run_catching(behavior: &dyn Behavior, ctx: &DecisionContext) -> Option<Action> {
    std::panic::AssertUnwindSafe(behavior.decide(ctx))
        .catch_unwind()
        .await
        .ok()
}

/// `NeedsDriven` is total: it always returns something sensible, so it is the one
/// behavior the engine can rely on when another fails.
async fn fallback(ctx: &DecisionContext) -> Action {
    NeedsDriven.decide(ctx).await
}

#[cfg(test)]
mod tests {
    use super::test_behaviors::{AlwaysInvalid, Panicky, SleepySlow};
    use super::*;
    use crate::test_support::test_config;
    use crate::world::World;

    fn registry_with(name: &str, behavior: Arc<dyn Behavior>) -> BehaviorRegistry {
        let mut r = BehaviorRegistry::with_builtins();
        r.register(name, behavior);
        r
    }

    #[test]
    fn builtins_are_registered_and_marked() {
        let r = BehaviorRegistry::with_builtins();
        assert_eq!(r.names(), vec!["needs_driven", "playful"]);
        assert!(r.get("needs_driven").unwrap().is_builtin());
        assert!(r.get("playful").unwrap().is_builtin());
        assert!(r.get("nonexistent").is_none());
    }

    #[test]
    fn external_behaviors_are_not_builtin_by_default() {
        assert!(!SleepySlow::new(50).is_builtin());
        assert!(!AlwaysInvalid.is_builtin());
    }

    #[tokio::test]
    async fn a_slow_external_behavior_is_replaced_by_the_fallback() {
        let mut config = test_config();
        // A 20ms tick gives a 10ms budget; the behavior sleeps far past it.
        config.world.tick_ms = 20;
        config.kitties[0].behavior = "sleepy_slow".into();
        let config = Arc::new(config);

        let registry = registry_with("sleepy_slow", Arc::new(SleepySlow::new(500)));
        let mut world = World::generate(&config);

        let started = std::time::Instant::now();
        let decisions = gather_decisions(&mut world, &registry, &config).await;
        let elapsed = started.elapsed();

        assert_eq!(
            decisions.len(),
            world.kitties.len(),
            "nobody loses their turn"
        );
        assert!(
            elapsed < Duration::from_millis(400),
            "the tick was not held hostage: {elapsed:?}"
        );
    }

    #[tokio::test]
    async fn a_panicking_behavior_does_not_crash_the_world() {
        let mut config = test_config();
        config.kitties[0].behavior = "panicky".into();
        let config = Arc::new(config);
        let registry = registry_with("panicky", Arc::new(Panicky));
        let mut world = World::generate(&config);

        // Silence the panic backtrace this test deliberately provokes.
        let previous = std::panic::take_hook();
        std::panic::set_hook(Box::new(|_| {}));
        let decisions = gather_decisions(&mut world, &registry, &config).await;
        std::panic::set_hook(previous);

        assert_eq!(decisions.len(), world.kitties.len());
        // The kitty whose advisor exploded still got a turn, courtesy of the
        // fallback -- and crucially, the panic did not escape into the tick loop.
        assert!(
            decisions.iter().any(|(id, _)| *id == config.kitties[0].id),
            "the kitty with the broken behavior still decided"
        );
    }

    #[tokio::test]
    async fn an_unknown_behavior_name_still_yields_a_turn() {
        let mut config = test_config();
        config.kitties[0].behavior = "not_registered".into();
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);

        let decisions = gather_decisions(&mut world, &registry, &config).await;
        assert_eq!(decisions.len(), world.kitties.len());
    }

    #[tokio::test]
    async fn decisions_come_back_for_every_kitty_in_id_order() {
        let config = Arc::new(test_config());
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);

        let decisions = gather_decisions(&mut world, &registry, &config).await;
        let ids: Vec<KittyId> = decisions.iter().map(|(id, _)| *id).collect();
        let mut sorted = ids.clone();
        sorted.sort();
        assert_eq!(ids, sorted, "stable kitty-id order");
    }
}
