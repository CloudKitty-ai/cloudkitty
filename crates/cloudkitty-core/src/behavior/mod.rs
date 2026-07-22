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
//!
//! **Multi-agent livelock warning for behavior authors.** All kitties decide
//! against the same start-of-tick snapshot, so two deterministic behaviors
//! reacting to each other can mirror one another indefinitely: each steps
//! toward where the other *was*, forever. Three such dances were found and
//! fixed in one day (2026-07-20): a head-on corridor mirror (spec 010), a
//! corner orbit between mutual approachers (spec 012's "Wait for me!"
//! etiquette), and a lockstep convoy sidestep (spec 012 FR-008). The pattern
//! to copy: when your behavior has no progressing move, break symmetry with
//! `ctx.rng` (seeded and per-kitty -- deterministic to the world, never
//! synchronized between kitties) or with an asymmetric rule such as
//! kitty-id right-of-way. A fixed fallback that two kitties can compute
//! identically will eventually dance.

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
use crate::seam::{Provenance, ResolvedDecision};
use crate::world::{World, WorldSnapshot};

pub mod needs_driven;
pub mod playful;
pub mod selection;
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

/// One kitty's pending decision: everything dispatch needs, however it is
/// then driven (with the served world's budget, or budgetless — spec 014).
struct DecisionJob {
    id: KittyId,
    seed: u64,
    behavior: Option<Arc<dyn Behavior>>,
    ctx: DecisionContext,
}

/// Builds every kitty's decision job against one shared snapshot. The
/// per-kitty seeds are drawn from the master RNG here, **in stable id order
/// before any decision runs**, so however dispatch later interleaves, the
/// randomness each kitty sees is the same. Both dispatch paths — the served
/// world's budgeted one and the budgetless headless one — start here, which
/// is what keeps their RNG draw shape identical (spec 014 FR-002).
fn decision_jobs(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> Vec<DecisionJob> {
    let snapshot = Arc::new(world.snapshot());
    let seeds = world.deal_decision_seeds();
    let mut jobs = Vec::with_capacity(world.kitties.len());
    for (id, seed) in seeds.iter() {
        let Some(kitty) = world.kitty(id).cloned() else {
            continue;
        };
        let behavior = registry.get(&kitty.behavior);
        let ctx = DecisionContext {
            me: kitty,
            world: snapshot.clone(),
            rng: DecisionRng::from_seed(seed),
            config: config.clone(),
        };
        jobs.push(DecisionJob {
            id,
            seed,
            behavior,
            ctx,
        });
    }
    jobs
}

/// Phase 1 of the tick, as the **served world** runs it: everyone decides,
/// concurrently, each non-built-in under the wall-clock budget with fallback.
/// Behavior is unchanged from before the spec 014 split — this is the
/// budgetless resolver's decision logic wrapped in `tokio::time::timeout`.
pub async fn gather_decisions(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> Vec<(KittyId, Action)> {
    let budget = Duration::from_millis(config.behavior.budget_ms(config.world.tick_ms));
    let jobs = decision_jobs(world, registry, config);

    let decisions = jobs
        .into_iter()
        .map(|job| async move { (job.id, decide_one(job, budget).await) });

    join_all(decisions).await
}

/// The pure budgetless decision resolver (spec 014 FR-017, research.md R5):
/// every behavior runs against the frozen snapshot with panic isolation and
/// `needs_driven` fallback, but **no wall clock** — reproducibility can never
/// depend on host speed. Every decision is provenance-marked, and the
/// dispatched proposals plus their decision seeds are returned to the caller
/// (the parity capture, research.md R4) — never stored in world state.
///
/// Behaviors resolve without awaiting anything real (FR-014), so driving
/// them to completion with a blocking executor is immediate.
pub fn resolve_decisions(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> Vec<ResolvedDecision> {
    decision_jobs(world, registry, config)
        .into_iter()
        .map(|job| {
            let (action, provenance) = resolve_one(job.behavior, &job.ctx);
            ResolvedDecision {
                kitty_id: job.id,
                action,
                seed: job.seed,
                provenance,
            }
        })
        .collect()
}

/// Resolves a single decision budgetlessly: panic isolation and fallback
/// stay in force, the wall clock does not exist. Public so mixed-control
/// drivers (spec 014 FR-020) can deal a scripted kitty its decision from the
/// stream the engine dealt it.
pub fn resolve_one(
    behavior: Option<Arc<dyn Behavior>>,
    ctx: &DecisionContext,
) -> (Action, Provenance) {
    match behavior {
        // A name that resolves to nothing is a config error caught at startup;
        // if one somehow reaches here, the kitty still gets a sensible turn --
        // marked honestly as the fallback's, not the named advisor's.
        None => (
            futures::executor::block_on(fallback(ctx)),
            Provenance::FallbackTaken,
        ),
        Some(b) => match futures::executor::block_on(run_catching(b.as_ref(), ctx)) {
            Some(action) => (action, Provenance::PolicyMade),
            None => (
                futures::executor::block_on(fallback(ctx)),
                Provenance::FallbackTaken,
            ),
        },
    }
}

async fn decide_one(job: DecisionJob, budget: Duration) -> Action {
    match job.behavior {
        // A name that resolves to nothing is a config error caught at startup; if
        // one somehow reaches here, the kitty still gets a sensible turn.
        None => NeedsDriven.decide(&job.ctx).await,

        Some(b) if b.is_builtin() => match run_catching(b.as_ref(), &job.ctx).await {
            Some(action) => action,
            None => fallback(&job.ctx).await,
        },

        // Non-built-ins run on the blocking pool. This is what makes the
        // budget real (spec 014 review): `tokio::time::timeout` only fires
        // at await points, and an advisor that computes synchronously (a
        // policy's MLP pass, a hot loop) never yields -- wrapped directly,
        // the timer could never preempt it and a slow advisor would stall
        // the tick loop. On the blocking pool the tick loop keeps its
        // budget: on timeout the JoinHandle is dropped, the stray
        // computation finishes harmlessly on its detached thread, and the
        // fallback (rebuilt from the same decision seed, since the context
        // moved into the task) takes the turn.
        Some(b) => {
            let me = job.ctx.me.clone();
            let world = job.ctx.world.clone();
            let config = job.ctx.config.clone();
            let seed = job.seed;
            let ctx = job.ctx;
            let handle = tokio::task::spawn_blocking(move || {
                futures::executor::block_on(run_catching(b.as_ref(), &ctx))
            });
            match tokio::time::timeout(budget, handle).await {
                Ok(Ok(Some(action))) => action,
                // Timed out, panicked, or otherwise failed: the default
                // behavior takes this kitty's turn, on the very decision
                // stream the advisor was dealt.
                _ => {
                    let ctx = DecisionContext {
                        me,
                        world,
                        rng: DecisionRng::from_seed(seed),
                        config,
                    };
                    fallback(&ctx).await
                }
            }
        }
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
    use super::test_behaviors::{AlwaysInvalid, BusySpin, Panicky, SleepySlow};
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

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn the_budget_preempts_a_synchronous_never_yielding_advisor() {
        // Spec 014 review: tokio's timeout only fires at await points, so a
        // synchronously-computing advisor (a policy MLP, a hot loop) wrapped
        // directly could stall the tick loop for its full run time. Dispatch
        // runs non-built-ins on the blocking pool, so the budget is real:
        // the tick proceeds with the fallback while the stray computation
        // finishes harmlessly on its detached thread.
        let mut config = test_config();
        config.world.tick_ms = 20; // a 10ms budget
        config.kitties[0].behavior = "busy_spin".into();
        let config = Arc::new(config);

        let registry = registry_with("busy_spin", Arc::new(BusySpin::new(500)));
        let mut world = World::generate(&config);

        let started = std::time::Instant::now();
        let decisions = gather_decisions(&mut world, &registry, &config).await;
        let elapsed = started.elapsed();

        assert_eq!(decisions.len(), world.kitties.len(), "nobody lost a turn");
        assert!(
            elapsed < Duration::from_millis(400),
            "the tick was held hostage by synchronous compute: {elapsed:?}"
        );
    }

    // ---- the budgetless resolver (spec 014 T004/T005) ---------------------

    #[tokio::test]
    async fn the_resolver_and_the_served_path_decide_identically() {
        // Same world, same seed: the budgetless resolver must dispatch the
        // exact decisions the served path gathers, drawing the identical RNG
        // stream while it does (FR-002's shared draw shape).
        let config = Arc::new(test_config());
        let registry = BehaviorRegistry::with_builtins();
        let mut served = World::generate(&config);
        let mut headless = World::generate(&config);

        let gathered = gather_decisions(&mut served, &registry, &config).await;
        let resolved = resolve_decisions(&mut headless, &registry, &config);

        assert_eq!(
            gathered,
            resolved
                .iter()
                .map(|r| (r.kitty_id, r.action))
                .collect::<Vec<_>>()
        );
        assert_eq!(
            serde_json::to_string(&served.rng).unwrap(),
            serde_json::to_string(&headless.rng).unwrap(),
            "both paths consume the master RNG with the identical draw shape"
        );
        assert!(resolved
            .iter()
            .all(|r| r.provenance == crate::seam::Provenance::PolicyMade));
    }

    #[test]
    fn the_resolver_marks_a_panicking_behavior_fallback_taken() {
        let mut config = test_config();
        config.kitties[0].behavior = "panicky".into();
        let config = Arc::new(config);
        let registry = registry_with("panicky", Arc::new(Panicky));
        let mut world = World::generate(&config);

        let previous = std::panic::take_hook();
        std::panic::set_hook(Box::new(|_| {}));
        let resolved = resolve_decisions(&mut world, &registry, &config);
        std::panic::set_hook(previous);

        let broken = resolved
            .iter()
            .find(|r| r.kitty_id == config.kitties[0].id)
            .expect("the kitty with the broken advisor still decided");
        assert_eq!(broken.provenance, crate::seam::Provenance::FallbackTaken);
        let healthy = resolved
            .iter()
            .find(|r| r.kitty_id == config.kitties[1].id)
            .unwrap();
        assert_eq!(healthy.provenance, crate::seam::Provenance::PolicyMade);
    }

    #[test]
    fn the_resolver_reports_the_seeds_it_dealt() {
        // The seeds in the resolver's report are the very ones the decisions
        // consumed: re-deriving each kitty's stream from the reported seed
        // reproduces its decision.
        let config = Arc::new(test_config());
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let snapshot = Arc::new(world.snapshot());

        let resolved = resolve_decisions(&mut world, &registry, &config);
        for r in &resolved {
            let kitty = snapshot.kitty(r.kitty_id).unwrap().clone();
            let behavior = registry.get(&kitty.behavior);
            let ctx = DecisionContext {
                me: kitty,
                world: snapshot.clone(),
                rng: DecisionRng::from_seed(r.seed),
                config: config.clone(),
            };
            let (action, _) = resolve_one(behavior, &ctx);
            assert_eq!(
                action, r.action,
                "kitty {} replays its decision",
                r.kitty_id
            );
        }
    }
}
