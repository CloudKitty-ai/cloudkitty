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

use cloudkitty_core::{BehaviorRegistry, Config, DistressEvent, World, WorldSnapshot};
use tokio::sync::{oneshot, watch};
use tokio::time::{interval, Duration, MissedTickBehavior};

use crate::persist;

/// Everything the HTTP layer serves, republished once per tick.
#[derive(Debug, Clone)]
pub struct Published {
    pub snapshot: Arc<WorldSnapshot>,
    pub distress: Arc<Vec<DistressEvent>>,
}

impl Published {
    fn from_world(world: &World) -> Self {
        Self {
            snapshot: Arc::new(world.snapshot()),
            distress: Arc::new(world.distress.to_vec()),
        }
    }
}

pub struct SimTask {
    /// Latest published state; clone freely, one per reader.
    pub receiver: watch::Receiver<Arc<Published>>,
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
) -> SimTask {
    let (tx, receiver) = watch::channel(Arc::new(Published::from_world(&world)));
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
        handle,
        shutdown: shutdown_tx,
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

    #[tokio::test]
    async fn the_world_ticks_and_publishes() {
        let mut config = test_config();
        config.world.tick_ms = 5;
        let config = Arc::new(config);
        let world = World::generate(&config);

        let sim = spawn(world, config, BehaviorRegistry::with_builtins(), None);
        let mut rx = sim.receiver.clone();

        rx.changed().await.expect("a tick was published");
        let first = rx.borrow_and_update().snapshot.tick;
        rx.changed().await.expect("another tick");
        let second = rx.borrow_and_update().snapshot.tick;

        assert!(second > first, "the clock moves forward");
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
        );
        let mut rx = sim.receiver.clone();
        rx.changed().await.unwrap();
        sim.shutdown().await;

        assert!(path.exists(), "ctrl-c leaves a saved world behind");
        persist::load_and_validate(&path, &config).expect("and it is loadable");
    }
}
