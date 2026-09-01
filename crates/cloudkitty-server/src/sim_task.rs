//! The simulation task: the only thing that owns the world.
//!
//! Article V says the server is authoritative, and this is where that lives. One
//! task holds the `World`; nothing else can touch it. After every tick it publishes
//! an immutable snapshot on a `watch` channel, and readers -- REST handlers, every
//! WebSocket client -- see a consistent picture without a single lock on the
//! simulation itself.
//!
//! `watch` is the right primitive because viewers only ever want the *current*
//! world: a slow client skips intermediate ticks rather than accumulating a backlog
//! the server has to remember.

use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::{
    ActivityEnd, BehaviorRegistry, Config, DistressEvent, RefusalEvent, World, WorldSnapshot,
};
use tokio::sync::{oneshot, watch};
use tokio::time::{interval, Duration, MissedTickBehavior};

use crate::persist;
use crate::watchdog::{AlarmEvent, Watchdog, WelfareStatus};

/// Everything the HTTP layer serves, republished once per tick.
#[derive(Debug, Clone)]
pub struct Published {
    pub snapshot: Arc<WorldSnapshot>,
    /// The snapshot as JSON, serialized here exactly once per tick. Every
    /// WebSocket viewer shares this string; without it, N viewers meant N
    /// identical serializations of the full world per tick, which made open
    /// sockets the cheapest way to burn the host's CPU (2026-07-22 security
    /// assessment). `None` only if serialization failed, which is logged.
    pub snapshot_json: Option<Arc<str>>,
    pub distress: Arc<Vec<DistressEvent>>,
    pub activity_ends: Arc<Vec<ActivityEnd>>,
    /// Refusals (spec 046), oldest first — served on GET /events/refusal.
    pub refusals: Arc<Vec<RefusalEvent>>,
    /// The refusal ring's capacity, served beside the events so a consumer
    /// can tell a wrapped window from a short one (the /welfare threshold
    /// precedent; `/config` omits the knob at its default).
    pub refusal_capacity: usize,
}

impl Published {
    fn from_world(world: &World) -> Self {
        let snapshot = Arc::new(world.snapshot());
        let snapshot_json = match serde_json::to_string(&*snapshot) {
            Ok(json) => Some(Arc::from(json)),
            Err(err) => {
                tracing::error!(%err, "could not serialize the world snapshot");
                None
            }
        };
        Self {
            snapshot,
            snapshot_json,
            distress: Arc::new(world.distress.to_vec()),
            activity_ends: Arc::new(world.activity_log.to_vec()),
            refusals: Arc::new(world.refusal_log.to_vec()),
            refusal_capacity: world.refusal_log.capacity(),
        }
    }
}

pub struct SimTask {
    /// Latest published state; clone freely, one per reader.
    pub receiver: watch::Receiver<Arc<Published>>,
    /// Latest welfare surface (spec 040): refreshed by the watchdog after
    /// every tick, served on GET /welfare.
    pub welfare: watch::Receiver<Arc<WelfareStatus>>,
    pub handle: tokio::task::JoinHandle<()>,
    shutdown: oneshot::Sender<()>,
}

impl SimTask {
    /// Asks the simulation to save and stop, then waits for it to finish.
    pub async fn shutdown(self) {
        // A send error just means the task already exited; either way we wait.
        let _ = self.shutdown.send(());
        if let Err(err) = self.handle.await {
            tracing::error!(%err, "simulation task did not shut down cleanly");
        }
    }
}

/// Starts ticking. Returns immediately with a handle to the running world.
pub fn spawn(
    mut world: World,
    config: Arc<Config>,
    registry: BehaviorRegistry,
    snapshot_path: Option<PathBuf>,
    mut watchdog: Watchdog,
) -> SimTask {
    let (tx, receiver) = watch::channel(Arc::new(Published::from_world(&world)));
    // The first observation happens at spawn: a world loaded mid-streak
    // re-announces it immediately (spec 040 edge case — re-announced beats
    // forgotten), and the endpoint has a real answer before the first tick.
    let (initial_status, initial_events) = watchdog.observe(&world);
    log_alarms(&initial_events);
    let (welfare_tx, welfare) = watch::channel(Arc::new(initial_status));
    let (shutdown_tx, mut shutdown_rx) = oneshot::channel();

    let handle = tokio::spawn(async move {
        let mut ticker = interval(Duration::from_millis(config.world.tick_ms));
        // If the host stalls, take the next tick late rather than sprinting
        // through a burst of catch-up ticks nobody could watch.
        ticker.set_missed_tick_behavior(MissedTickBehavior::Delay);

        let save_every = config.persistence.save_every_ticks;

        loop {
            tokio::select! {
                _ = ticker.tick() => {
                    world.tick(&registry, &config).await;
                    let _ = tx.send(Arc::new(Published::from_world(&world)));
                    // Spec 040: the standing welfare watch. Read-only over
                    // &world; the log lines are a rendering of the returned
                    // events (single source, watchdog.rs plan D2).
                    let (status, events) = watchdog.observe(&world);
                    log_alarms(&events);
                    let _ = welfare_tx.send(Arc::new(status));

                    if world.tick.is_multiple_of(save_every) {
                        save_now(&world, snapshot_path.as_deref(), "periodic");
                    }
                }
                _ = &mut shutdown_rx => {
                    tracing::info!(tick = world.tick, "shutting down; saving the world");
                    save_now(&world, snapshot_path.as_deref(), "shutdown");
                    break;
                }
            }
        }
    });

    SimTask {
        receiver,
        welfare,
        handle,
        shutdown: shutdown_tx,
    }
}

/// Renders alarm events into the log: ERROR for crossings and reminders
/// (the welfare incident classes), INFO for recoveries.
fn log_alarms(events: &[AlarmEvent]) {
    for event in events {
        match event {
            AlarmEvent::Crossing {
                kitty_id,
                kitty_name,
                need,
                age,
            } => tracing::error!(
                kitty = *kitty_id,
                name = %kitty_name,
                need = ?need,
                age_ticks = *age,
                "WELFARE ALARM: sustained distress crossed the line"
            ),
            AlarmEvent::Reminder {
                kitty_id,
                kitty_name,
                need,
                age,
            } => tracing::error!(
                kitty = *kitty_id,
                name = %kitty_name,
                need = ?need,
                age_ticks = *age,
                "WELFARE ALARM (still): the distress streak continues"
            ),
            AlarmEvent::Recovery {
                kitty_id,
                kitty_name,
                need,
                final_age,
            } => tracing::info!(
                kitty = *kitty_id,
                name = %kitty_name,
                need = ?need,
                final_age_ticks = *final_age,
                "welfare recovered: the distress streak ended"
            ),
        }
    }
}

fn save_now(world: &World, path: Option<&std::path::Path>, reason: &str) {
    let Some(path) = path else {
        return;
    };
    match persist::save(world, path) {
        Ok(()) => tracing::info!(tick = world.tick, reason, path = %path.display(), "world saved"),
        // A failed save must never take the world down with it.
        Err(err) => tracing::error!(%err, reason, "could not save the world"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::test_support::test_config;

    #[test]
    fn published_refusals_are_the_ring_verbatim_and_a_fresh_world_serves_none() {
        // Spec 046 US1-6: what /events/refusal serves IS the ring --
        // byte-equal, oldest first -- and a fresh world publishes an empty
        // list (readable as "no refusals" only because the emit-proof
        // tests exist, F-029).
        use cloudkitty_core::action::Action;
        use cloudkitty_core::grid::{Direction, Position};
        use cloudkitty_core::seam::JointProposal;

        let config = test_config();
        let fresh = World::generate(&config);
        assert!(
            Published::from_world(&fresh).refusals.is_empty(),
            "a fresh world has refused nothing"
        );

        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0);
        world.kitties[1].pos = Position::new(1, 0);
        let mut p = JointProposal::new();
        p.propose(1, Action::move_to(Direction::East)); // occupied: refused
        world.tick_with_proposals(&p, &config);

        let published = Published::from_world(&world);
        assert!(!published.refusals.is_empty(), "the refusal was published");
        assert_eq!(
            *published.refusals,
            world.refusal_log.to_vec(),
            "the served list is the ring verbatim"
        );
        assert_eq!(
            published.refusal_capacity,
            world.refusal_log.capacity(),
            "the published capacity is the ring's own bound"
        );
        assert_eq!(
            published.refusal_capacity, config.events.refusal_retention,
            "which on a generated world is the configured retention"
        );
    }

    #[tokio::test]
    async fn the_world_ticks_and_publishes() {
        let mut config = test_config();
        config.world.tick_ms = 5;
        let config = Arc::new(config);
        let world = World::generate(&config);

        let sim = spawn(
            world,
            config,
            BehaviorRegistry::with_builtins(),
            None,
            crate::watchdog::Watchdog::new(Default::default()),
        );
        let mut rx = sim.receiver.clone();

        rx.changed().await.expect("a tick was published");
        let first = rx.borrow_and_update().snapshot.tick;
        rx.changed().await.expect("another tick");
        let second = rx.borrow_and_update().snapshot.tick;

        assert!(second > first, "the clock moves forward");
        sim.shutdown().await;
    }

    #[tokio::test]
    async fn the_published_json_is_the_snapshot_serialized() {
        // Every WebSocket viewer shares this one string, so it must be exactly
        // what serializing the snapshot per viewer used to produce.
        let mut config = test_config();
        config.world.tick_ms = 5;
        let config = Arc::new(config);
        let world = World::generate(&config);

        let sim = spawn(
            world,
            config,
            BehaviorRegistry::with_builtins(),
            None,
            crate::watchdog::Watchdog::new(Default::default()),
        );
        let mut rx = sim.receiver.clone();
        rx.changed().await.expect("a tick was published");

        let published = rx.borrow_and_update().clone();
        let json = published
            .snapshot_json
            .as_deref()
            .expect("a serialized world");
        assert_eq!(
            json,
            serde_json::to_string(&*published.snapshot).unwrap(),
            "the shared string and a fresh serialization must not diverge"
        );
        sim.shutdown().await;
    }

    #[tokio::test]
    async fn shutdown_saves_the_world() {
        let dir = std::env::temp_dir().join("cloudkitty-test-sim-shutdown");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("snapshot.json");

        let mut config = test_config();
        config.world.tick_ms = 5;
        let config = Arc::new(config);
        let world = World::generate(&config);

        let sim = spawn(
            world,
            config.clone(),
            BehaviorRegistry::with_builtins(),
            Some(path.clone()),
            crate::watchdog::Watchdog::new(Default::default()),
        );
        let mut rx = sim.receiver.clone();
        rx.changed().await.unwrap();
        sim.shutdown().await;

        assert!(path.exists(), "ctrl-c leaves a saved world behind");
        persist::load_and_validate(&path, &config).expect("and it is loadable");
    }
}
