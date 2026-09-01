//! Pluggable behaviors: untrusted advisors to a sovereign engine.
//!
//! Article IV (v1.2.0) in one paragraph: a behavior is handed a read-only view
//! of the world and returns *one proposed action*. It cannot touch the world.
//! A proposal that cannot even be understood -- a failed plugin exchange, an
//! unparseable reply, a panic, a timeout -- resolves to the **default
//! built-in (needs-based) fallback** deciding from the dealt seed; a proposal
//! that parses but is illegal for the current world state is validated down
//! to an **idle turn**. Both are constitutionally safe outcomes, and a
//! behavior that hangs, panics, or returns nonsense costs its kitty a moment
//! of cleverness and nothing more.
//!
//! The `async` signature is deliberate and is the whole extension point:
//! [`ScriptBehavior`] (spec 016) drops in here with no engine changes, and a
//! future `HttpBehavior` will too. Built-in behaviors resolve immediately and
//! are exempt from the wall-clock budget -- that exemption is what keeps
//! Article V's determinism unconditional, since a slow machine can never
//! change what a built-in decides.
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

use crate::config::Config;
use crate::kitty::{Kitty, KittyId};
use crate::meow::MessageKind;
use crate::rng::DecisionRng;
use crate::seam::{Decision, Provenance, ResolvedDecision};
use crate::world::{World, WorldSnapshot};

pub mod needs_driven;
pub mod playful;
mod relief;
pub mod script;
pub mod selection;
pub mod test_behaviors;

pub use needs_driven::NeedsDriven;
pub use playful::Playful;
pub use script::{DecisionRequest, ScriptBehavior};

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
    /// Propose one decision -- an activity plus an optional riding message
    /// (spec 028). Never applied directly: the engine validates the
    /// activity and enforces message legality separately.
    async fn decide(&self, ctx: &DecisionContext) -> Decision;

    /// Propose one action, or nothing. `None` means the advisor has no
    /// intelligible proposal -- a failed plugin exchange, an unparseable
    /// reply -- and dispatch treats it exactly like a crashed advisor: the
    /// fallback decides from the dealt seed (amended Article IV's default
    /// resolution). Built-ins never return `None`; only external advisors,
    /// whose proposals can fail in ways a panic does not express, override
    /// this.
    ///
    /// **Wrapper authors**: dispatch consults `try_decide`, so a delegating
    /// behavior must forward `try_decide` to its inner behavior, not just
    /// `decide` -- a decide-only wrapper around an external advisor would
    /// silently convert "no proposal" into whatever `decide` improvises,
    /// bypassing the uniform fallback rule.
    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Decision> {
        Some(self.decide(ctx).await)
    }

    /// Built-ins run in-process and are exempt from the wall-clock decision
    /// budget. External implementations must leave this as `false`.
    fn is_builtin(&self) -> bool {
        false
    }
}

/// One kitty's circuit-breaker state: its consecutive budget timeouts,
/// and the tick its bench expires if the streak tripped.
#[derive(Default)]
struct BreakerEntry {
    strikes: u32,
    benched_until: Option<u64>,
}

/// Maps configured behavior names to implementations.
///
/// Also carries the served world's circuit breaker (spec 014 reviews): a
/// kitty whose external advisor times out `budget_strikes` decisions in a
/// row is benched for `bench_ticks` — it takes the fallback and no
/// blocking work is spawned for it until the bench expires, bounding the
/// threads a wedged advisor can strand at `budget_strikes` per bench
/// window. Strikes are **per kitty**: one kitty's healthy answers never
/// mask a sibling's wedged stream, and one shared slow tick costs each
/// kitty a single strike, never a whole streak. The breaker lives with
/// the advisors (one per process, shared across clones); the budgetless
/// paths never time out and never consult it.
#[derive(Clone, Default)]
pub struct BehaviorRegistry {
    map: BTreeMap<String, Arc<dyn Behavior>>,
    breaker: Arc<std::sync::Mutex<BTreeMap<KittyId, BreakerEntry>>>,
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

    /// Registers a behavior under `name`. Names are unique by construction:
    /// a duplicate registration is a programmer error and panics -- silent
    /// last-write-wins once let a same-named plugin shadow a builtin with
    /// no warning (review 2026-07-23). Callers whose names come from config
    /// (plugin registration) check first and return a proper startup error;
    /// this panic is the backstop for every future registration source.
    pub fn register(&mut self, name: impl Into<String>, behavior: Arc<dyn Behavior>) {
        let name = name.into();
        let previous = self.map.insert(name.clone(), behavior);
        assert!(
            previous.is_none(),
            "behavior {name:?} registered twice; names must be unique"
        );
    }

    pub fn get(&self, name: &str) -> Option<Arc<dyn Behavior>> {
        self.map.get(name).cloned()
    }

    pub fn names(&self) -> Vec<String> {
        self.map.keys().cloned().collect()
    }

    fn breaker(&self) -> std::sync::MutexGuard<'_, BTreeMap<KittyId, BreakerEntry>> {
        match self.breaker.lock() {
            Ok(guard) => guard,
            Err(poisoned) => poisoned.into_inner(),
        }
    }

    /// Records a budget timeout for `kitty`'s dispatch at `now`; returns
    /// whether this strike tripped the bench.
    fn record_timeout(
        &self,
        kitty: KittyId,
        now: u64,
        budget_strikes: u32,
        bench_ticks: u64,
    ) -> bool {
        let mut breaker = self.breaker();
        let entry = breaker.entry(kitty).or_default();
        entry.strikes = entry.strikes.saturating_add(1);
        if entry.strikes >= budget_strikes {
            entry.strikes = 0;
            entry.benched_until = Some(now.saturating_add(bench_ticks));
            return true;
        }
        false
    }

    /// An in-budget answer clears the kitty's own streak: a
    /// slow-but-recovering advisor is never benched on history alone.
    fn clear_timeouts(&self, kitty: KittyId) {
        self.breaker().remove(&kitty);
    }

    /// Whether `kitty`'s external dispatch is benched at `now_tick`
    /// (spec 014 review). Public so operators and tests can observe it.
    /// An expired bench clears itself here — recovery needs no other path.
    pub fn is_benched(&self, kitty: KittyId, now_tick: u64) -> bool {
        let mut breaker = self.breaker();
        let Some(entry) = breaker.get_mut(&kitty) else {
            return false;
        };
        match entry.benched_until {
            Some(until) if now_tick < until => true,
            Some(_) => {
                breaker.remove(&kitty);
                false
            }
            None => false,
        }
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
) -> Vec<(KittyId, Decision)> {
    let budget = Duration::from_millis(config.behavior.budget_ms(config.world.tick_ms));
    let jobs = decision_jobs(world, registry, config);

    let decisions = jobs
        .into_iter()
        .map(|job| async move { (job.id, decide_one(job, budget, registry).await) });

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
            let (decision, provenance) = resolve_one(job.behavior, &job.ctx, job.seed);
            ResolvedDecision {
                kitty_id: job.id,
                decision,
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
///
/// `seed` is the decision seed the context's stream was built from. The
/// fallback rule is uniform across every dispatch path (spec 014 review):
/// **the fallback always decides on a stream restarted from the dealt
/// seed**, never on whatever remains after a failed advisor's partial
/// draws — otherwise the served path (which must rebuild the context after
/// moving it to the blocking pool) and this budgetless path would diverge
/// on the very tick a broken advisor is survived.
pub fn resolve_one(
    behavior: Option<Arc<dyn Behavior>>,
    ctx: &DecisionContext,
    seed: u64,
) -> (Decision, Provenance) {
    match behavior {
        // A name that resolves to nothing is a config error caught at startup;
        // if one somehow reaches here, the kitty still gets a sensible turn --
        // marked honestly as the fallback's, not the named advisor's.
        None => {
            ctx.rng.reseed(seed);
            (
                futures::executor::block_on(fallback(ctx)),
                Provenance::FallbackTaken,
            )
        }
        Some(b) => match futures::executor::block_on(run_catching(b.as_ref(), ctx)) {
            Some(decision) => (decision, Provenance::PolicyMade),
            None => {
                ctx.rng.reseed(seed);
                (
                    futures::executor::block_on(fallback(ctx)),
                    Provenance::FallbackTaken,
                )
            }
        },
    }
}

async fn decide_one(job: DecisionJob, budget: Duration, registry: &BehaviorRegistry) -> Decision {
    match job.behavior {
        // A name that resolves to nothing is a config error caught at startup; if
        // one somehow reaches here, the kitty still gets a sensible turn.
        None => NeedsDriven.decide(&job.ctx).await,

        Some(b) if b.is_builtin() => match run_catching(b.as_ref(), &job.ctx).await {
            Some(decision) => decision,
            None => {
                // The uniform fallback rule (see resolve_one): restart from
                // the dealt seed, identically on every dispatch path.
                job.ctx.rng.reseed(job.seed);
                fallback(&job.ctx).await
            }
        },

        // Non-built-ins run on the blocking pool. This is what makes the
        // budget real (spec 014 review): `tokio::time::timeout` only fires
        // at await points, and an advisor that computes synchronously (a
        // hot compute loop) never yields -- wrapped directly, the timer
        // could never preempt it and a slow advisor would stall the tick
        // loop. On the blocking pool the tick loop keeps its budget; on
        // timeout the JoinHandle is dropped and the stray computation
        // finishes on its detached thread. An arbitrary external advisor
        // might *never* finish, so consecutive per-kitty timeouts bench the
        // kitty's dispatch (the registry's circuit breaker); ScriptBehavior
        // additionally carries its own per-exchange deadline
        // (exchange_timeout_ms), so its strays always finish within one
        // deadline -- the pool can never fill with permanently blocked
        // plugin threads (review 2026-07-23).
        Some(b) => {
            let now = job.ctx.world.tick;
            if registry.is_benched(job.id, now) {
                job.ctx.rng.reseed(job.seed);
                return fallback(&job.ctx).await;
            }

            let id = job.id;
            let seed = job.seed;
            let name = job.ctx.me.behavior.clone();
            let world = job.ctx.world.clone();
            let config = job.ctx.config.clone();
            let ctx = job.ctx;
            let handle = tokio::task::spawn_blocking(move || {
                futures::executor::block_on(run_catching(b.as_ref(), &ctx))
            });
            match tokio::time::timeout(budget, handle).await {
                Ok(Ok(Some(decision))) => {
                    registry.clear_timeouts(id);
                    decision
                }
                // The advisor panicked (or the task was cancelled) but the
                // thread came back: not a wedge, so the streak clears; the
                // fallback takes the turn from the dealt seed (the uniform
                // rule).
                Ok(_) => {
                    registry.clear_timeouts(id);
                    fallback_from_seed(id, seed, world, config).await
                }
                Err(_elapsed) => {
                    let behavior = &config.behavior;
                    if registry.record_timeout(
                        id,
                        now,
                        behavior.budget_strikes,
                        behavior.bench_ticks,
                    ) {
                        tracing::warn!(
                            kitty = id,
                            advisor = %name,
                            strikes = behavior.budget_strikes,
                            bench_ticks = behavior.bench_ticks,
                            "kitty's advisor benched after consecutive budget timeouts; \
                             it takes the fallback until the bench expires"
                        );
                    }
                    fallback_from_seed(id, seed, world, config).await
                }
            }
        }
    }
}

/// The fallback for a context that moved to the blocking pool: rebuilt from
/// the snapshot and the dealt seed — the same stream restart every other
/// fallback arm applies.
async fn fallback_from_seed(
    id: KittyId,
    seed: u64,
    world: Arc<WorldSnapshot>,
    config: Arc<Config>,
) -> Decision {
    let me = world
        .kitty(id)
        .cloned()
        .expect("the deciding kitty is in its own snapshot");
    let ctx = DecisionContext {
        me,
        world,
        rng: DecisionRng::from_seed(seed),
        config,
    };
    fallback(&ctx).await
}

/// Runs a behavior, converting a panic -- or the advisor's own `None` from
/// [`Behavior::try_decide`] -- into `None` rather than unwinding into the
/// tick loop. Every dispatch path funnels through here, so "no proposal" and
/// "crashed" are one and the same fallback downstream.
async fn run_catching(behavior: &dyn Behavior, ctx: &DecisionContext) -> Option<Decision> {
    std::panic::AssertUnwindSafe(behavior.try_decide(ctx))
        .catch_unwind()
        .await
        .ok()
        .flatten()
}

/// `NeedsDriven` is total: it always returns something sensible, so it is the one
/// behavior the engine can rely on when another fails.
async fn fallback(ctx: &DecisionContext) -> Decision {
    NeedsDriven.decide(ctx).await
}

/// The deterministic announce rule (spec 028 FR-018), shared by every
/// scripted decider: say the highest-pressure need whose want-kind is
/// legal right now -- "meow whenever legal" is the honest broadcast, and
/// the mask (grounding + per-kind cooldown) is the whole restraint.
/// Equal pressures tie-break in `NeedKind::ALL` order (the selection
/// precedent). Computed after and independent of the activity: announcing
/// never displaces the turn (the imitability principle's source-side
/// half). No RNG -- the announce lotteries died with the courtesy era.
pub(crate) fn announce(ctx: &DecisionContext) -> Option<MessageKind> {
    let mut best: Option<(f32, MessageKind)> = None;
    for need in crate::needs::NeedKind::ALL {
        let want = MessageKind::for_need(need);
        if !crate::meow::message_legal(
            &ctx.me,
            want,
            ctx.world.tick,
            &ctx.config,
            &ctx.world.elements,
        ) {
            continue;
        }
        let pressure = ctx.me.needs.get(need);
        // Strictly greater: on a tie the earlier kind in ALL order stays.
        if best.is_none_or(|(top, _)| pressure > top) {
            best = Some((pressure, want));
        }
    }
    if let Some((_, want)) = best {
        return Some(want);
    }
    announce_here(ctx)
}

/// The here path (spec 043): fills a slot the want loop left Silent —
/// never sooner, so the precedence ladder (WaitForMe > want > here >
/// Silent, owner ruling 2026-08-23) holds by construction. Knob off
/// (`announce_here` 0) is a constant `None`: today's behavior,
/// byte-identical. Knob on, a cat speaks only on its phase ticks,
/// `(tick + kitty_id) % period == 0` (the `critter_moves_this_tick`
/// idiom), choosing among the LEGAL here-kinds — `message_legal`'s own
/// adjacency/vocabulary/cooldown ruling, unchanged law — by the
/// speaking-tick counter `((tick + kitty_id) / period) % n_legal` over
/// `HERE_KINDS` order. NOT the handoff's literal `(tick + kitty_id) %
/// n_legal`: on speaking ticks the sum is a multiple of the period, so
/// that index only reaches multiples of gcd(period, n_legal) — at
/// period 4 with 2 or 4 legal words it is pinned to HereFood forever
/// (research D3; amendment accepted by Experiments 2026-08-30). The
/// counter derives from (tick, kitty_id) alone: stateless, no RNG, and
/// a resumed run speaks identically to an unbroken one.
fn announce_here(ctx: &DecisionContext) -> Option<MessageKind> {
    let period = ctx.config.behavior.announce_here;
    if period == 0 {
        return None;
    }
    let counter = ctx.world.tick + ctx.me.id as u64;
    if !counter.is_multiple_of(period) {
        return None;
    }
    let legal: Vec<MessageKind> = MessageKind::HERE_KINDS
        .into_iter()
        .filter(|&kind| {
            crate::meow::message_legal(
                &ctx.me,
                kind,
                ctx.world.tick,
                &ctx.config,
                &ctx.world.elements,
            )
        })
        .collect();
    if legal.is_empty() {
        return None;
    }
    Some(legal[((counter / period) % legal.len() as u64) as usize])
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

    #[test]
    #[should_panic(expected = "registered twice")]
    fn a_duplicate_registration_is_a_programmer_error() {
        // Review 2026-07-23: silent last-write-wins let a same-named plugin
        // shadow a builtin. The registry itself is the backstop now.
        let mut r = BehaviorRegistry::with_builtins();
        r.register("playful", Arc::new(AlwaysInvalid));
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
    async fn consecutive_timeouts_bench_a_wedged_kittys_dispatch() {
        // Spec 014 reviews: a wedged advisor may never return its blocking
        // thread, so the leak must be bounded — after budget_strikes
        // consecutive timeouts the kitty's dispatch is benched and no
        // further work is spawned for it until the bench expires.
        let mut config = test_config();
        config.world.tick_ms = 20; // a 10ms budget
        config.behavior.budget_strikes = 2;
        config.kitties[0].behavior = "busy_spin".into();
        let config = Arc::new(config);
        let wedged = config.kitties[0].id;

        let registry = registry_with("busy_spin", Arc::new(BusySpin::new(200)));
        let mut world = World::generate(&config);

        assert!(!registry.is_benched(wedged, world.tick));
        gather_decisions(&mut world, &registry, &config).await;
        assert!(!registry.is_benched(wedged, world.tick));
        gather_decisions(&mut world, &registry, &config).await;
        assert!(
            registry.is_benched(wedged, world.tick),
            "two strikes bench the kitty's dispatch"
        );

        // Benched: the next gather goes straight to the fallback — no
        // budget wait, no new blocking work.
        let started = std::time::Instant::now();
        gather_decisions(&mut world, &registry, &config).await;
        assert!(
            started.elapsed() < Duration::from_millis(8),
            "a benched dispatch must not spend the budget: {:?}",
            started.elapsed()
        );
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn an_in_budget_answer_clears_the_timeout_streak() {
        let mut config = test_config();
        config.world.tick_ms = 20;
        config.behavior.budget_strikes = 2;
        config.kitties[0].behavior = "quiet".into();
        let config = Arc::new(config);
        let quiet = config.kitties[0].id;
        let registry = registry_with("quiet", Arc::new(super::test_behaviors::QuietExternal));
        let mut world = World::generate(&config);

        // Manufacture one strike, then let the healthy advisor answer.
        registry.record_timeout(quiet, world.tick, 2, 300);
        gather_decisions(&mut world, &registry, &config).await;
        registry.record_timeout(quiet, world.tick, 2, 300);
        assert!(
            !registry.is_benched(quiet, world.tick),
            "the in-budget answer between strikes reset the streak"
        );
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn one_slow_tick_never_benches_kitties_sharing_an_advisor() {
        // Third-review regression: strikes are per kitty and per decision
        // streak, so a single shared slow tick (a host hiccup timing out
        // every kitty at once) costs each kitty one strike — never a whole
        // streak, never an instant bench.
        let mut config = test_config();
        config.world.tick_ms = 20;
        config.behavior.budget_strikes = 2;
        for kitty in &mut config.kitties {
            kitty.behavior = "busy_spin".into();
        }
        let config = Arc::new(config);

        let registry = registry_with("busy_spin", Arc::new(BusySpin::new(200)));
        let mut world = World::generate(&config);

        gather_decisions(&mut world, &registry, &config).await;
        for kitty in &config.kitties {
            assert!(
                !registry.is_benched(kitty.id, world.tick),
                "kitty {} was benched by a single shared slow tick",
                kitty.id
            );
        }
    }

    #[test]
    fn another_kittys_answer_never_clears_a_wedged_streak() {
        // Third-review regression: the old name-keyed breaker let a healthy
        // kitty's answers reset a wedged sibling's streak every tick, so
        // the wedged dispatch was never benched and leaked a thread per
        // tick. Per-kitty streaks make the sibling's answers irrelevant.
        let registry = BehaviorRegistry::with_builtins();
        let (wedged, healthy): (KittyId, KittyId) = (7, 8);

        assert!(!registry.record_timeout(wedged, 0, 2, 100));
        registry.clear_timeouts(healthy);
        assert!(
            registry.record_timeout(wedged, 1, 2, 100),
            "the second strike benches despite the sibling's answers"
        );
        assert!(registry.is_benched(wedged, 50));
    }

    #[test]
    fn a_bench_expires_and_the_streak_starts_fresh() {
        // Third-review regression: the old bench was permanent (once
        // benched, nothing spawned, so nothing could ever clear it). A
        // bench now expires after bench_ticks, and the streak restarts
        // from zero — a recovered advisor comes back on its own.
        let registry = BehaviorRegistry::with_builtins();
        let kitty: KittyId = 3;

        assert!(registry.record_timeout(kitty, 10, 1, 5), "one strike trips");
        assert!(registry.is_benched(kitty, 14));
        assert!(!registry.is_benched(kitty, 15), "the bench expired");
        assert!(
            !registry.record_timeout(kitty, 15, 2, 5),
            "the streak restarted from zero after the bench"
        );
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn the_budget_preempts_a_synchronous_never_yielding_advisor() {
        // Spec 014 review: tokio's timeout only fires at await points, so a
        // synchronously-computing advisor (a hot compute loop) wrapped
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
                .map(|r| (r.kitty_id, r.decision))
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
    fn an_unintelligible_advisor_falls_back_never_reshapes() {
        // Spec 016 FR-003: an advisor with no intelligible proposal (a failed
        // plugin exchange) resolves to the fallback deciding from the dealt
        // seed -- the crashed-advisor path -- never to some reshaped action.
        let mut config = test_config();
        config.kitties[0].behavior = "unintelligible".into();
        let config = Arc::new(config);
        let registry = registry_with(
            "unintelligible",
            Arc::new(super::test_behaviors::Unintelligible),
        );
        let mut world = World::generate(&config);
        let snapshot = Arc::new(world.snapshot());

        let resolved = resolve_decisions(&mut world, &registry, &config);
        let broken = resolved
            .iter()
            .find(|r| r.kitty_id == config.kitties[0].id)
            .expect("the kitty with no proposal still decided");
        assert_eq!(broken.provenance, crate::seam::Provenance::FallbackTaken);

        // The fallback decided from the dealt seed: replaying the default
        // built-in on that seed reproduces the action exactly.
        let me = snapshot.kitty(broken.kitty_id).unwrap().clone();
        let ctx = DecisionContext {
            me,
            world: snapshot.clone(),
            rng: DecisionRng::from_seed(broken.seed),
            config: config.clone(),
        };
        let expected = futures::executor::block_on(fallback(&ctx));
        assert_eq!(broken.decision, expected);
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn the_served_path_survives_an_unintelligible_advisor() {
        // The same guarantee on the budgeted path: no proposal, no lost turn,
        // no stalled tick.
        let mut config = test_config();
        config.kitties[0].behavior = "unintelligible".into();
        let config = Arc::new(config);
        let registry = registry_with(
            "unintelligible",
            Arc::new(super::test_behaviors::Unintelligible),
        );
        let mut world = World::generate(&config);

        let decisions = gather_decisions(&mut world, &registry, &config).await;
        assert_eq!(decisions.len(), world.kitties.len(), "nobody loses a turn");
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
            let (decision, _) = resolve_one(behavior, &ctx, r.seed);
            assert_eq!(
                decision, r.decision,
                "kitty {} replays its decision",
                r.kitty_id
            );
        }
    }

    // ---- spec 043: the announce_here here path (T009–T013) ----

    use crate::config::Config;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::needs::NeedKind;

    /// A hand-built stage for driving `announce` directly: kitty 1 parked
    /// mid-meadow on a cleared board at `tick`, under `config`.
    fn here_ctx_with(config: Config, tick: u64, setup: impl FnOnce(&mut World)) -> DecisionContext {
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        world.tick = tick;
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(8, 8);
        setup(&mut world);
        let me = world.kitty(1).unwrap().clone();
        DecisionContext {
            me,
            world: Arc::new(world.snapshot()),
            rng: DecisionRng::from_seed(9876),
            config,
        }
    }

    fn here_ctx(period: u64, tick: u64, setup: impl FnOnce(&mut World)) -> DecisionContext {
        let mut config = test_config();
        config.behavior.announce_here = period;
        here_ctx_with(config, tick, setup)
    }

    fn adjacent_chow(world: &mut World) {
        world.push_element(Element {
            id: 950,
            kind: ElementKind::Chow { servings: 2 },
            pos: Position::new(8, 9),
            ttl: None,
        });
    }

    fn adjacent_chow_and_water(world: &mut World) {
        adjacent_chow(world);
        world.push_element(Element {
            id: 951,
            kind: ElementKind::Water,
            pos: Position::new(7, 8),
            ttl: None,
        });
    }

    #[test]
    fn a_want_word_outranks_a_here_word() {
        // T009 / FR-004 (owner precedence ruling 2026-08-23): armed want +
        // adjacent referent + knob on + phase tick → the want speaks; the
        // here path fills only a slot that would otherwise be Silent.
        let ctx = here_ctx(1, 51, |w| {
            adjacent_chow(w);
            let idx = w.kitty_index(1).unwrap();
            w.kitties[idx].announce_armed.insert(NeedKind::Eat);
            w.kitties[idx].needs.add(NeedKind::Eat, 60.0);
        });
        assert_eq!(announce(&ctx), Some(MessageKind::WantEat));
    }

    #[test]
    fn the_phase_gate_holds_the_tongue_off_phase() {
        // T010 / FR-005: knob on, referent adjacent, but
        // (tick + kitty_id) % period != 0 → Silent. The sanity arm proves
        // the same stage speaks ON phase — off-phase silence is the gate,
        // not a missing here path.
        let off = here_ctx(4, 52, adjacent_chow); // (52 + 1) % 4 == 1
        assert_eq!(announce(&off), None);
        let on = here_ctx(4, 51, adjacent_chow); // (51 + 1) % 4 == 0
        assert_eq!(announce(&on), Some(MessageKind::HereFood));
    }

    #[test]
    fn the_selection_cycles_every_legal_kind_in_here_kinds_order() {
        // T011 / FR-006 AS AMENDED (research D3): with two legal kinds at
        // period 4 the speaking-tick counter ((tick + id) / period) %
        // n_legal walks BOTH kinds. Under the handoff's literal
        // (tick + id) % n_legal this guard reds: on speaking ticks
        // tick + id is a multiple of the period, so with gcd(4, 2) = 2 the
        // index is pinned to 0 and only HereFood is ever spoken.
        let mut spoken = Vec::new();
        for tick in [3u64, 7, 11, 15] {
            // (tick + 1) % 4 == 0: all speaking ticks for kitty 1.
            let ctx = here_ctx(4, tick, adjacent_chow_and_water);
            spoken.push(announce(&ctx));
        }
        assert_eq!(
            spoken,
            vec![
                Some(MessageKind::HereWater), // counter 1
                Some(MessageKind::HereFood),  // counter 2
                Some(MessageKind::HereWater), // counter 3
                Some(MessageKind::HereFood),  // counter 4
            ],
            "both legal kinds must be reached, in HERE_KINDS order"
        );
    }

    #[test]
    fn no_adjacent_referent_means_silence_even_on_phase() {
        // T012 / FR-007: a phase tick on bare grass proposes nothing —
        // legality is unchanged law and adjacency is its floor.
        let ctx = here_ctx(4, 51, |_| {});
        assert_eq!(announce(&ctx), None);
    }

    #[test]
    fn a_cooled_kind_drops_out_and_the_index_re_derives() {
        // T012 / FR-007 edge: HereWater's cooldown is stamped, so the
        // legal set is [HereFood] alone and EVERY speaking tick picks it —
        // n_legal is the live survivor count, never the family size.
        for tick in [3u64, 7] {
            let ctx = here_ctx(4, tick, |w| {
                adjacent_chow_and_water(w);
                let idx = w.kitty_index(1).unwrap();
                w.kitties[idx].set_meow_cooldown(MessageKind::HereWater, tick + 5);
            });
            assert_eq!(announce(&ctx), Some(MessageKind::HereFood));
        }
    }

    #[test]
    fn a_disabled_vocabulary_flag_silences_the_kind() {
        // T013 / FR-007, US1-5: the knob cannot speak a word the world's
        // vocabulary has off — with here_food disabled and only chow
        // adjacent, a phase tick stays Silent.
        let mut config = test_config();
        config.behavior.announce_here = 4;
        config.meow.vocabulary.here_food = false;
        let ctx = here_ctx_with(config, 51, adjacent_chow);
        assert_eq!(announce(&ctx), None);
    }
}
