//! Vectorized environments (spec 014 FR-012, research.md R6): N fully
//! independent episodes — separate seeds, separate RNGs, zero shared
//! state — stepped as a batch across a thread pool.
//!
//! The pool is **persistent**: each worker thread owns its contiguous chunk
//! of worlds for the environment's life, and batch calls broadcast commands
//! and gather results positionally over channels. (A naive scoped spawn per
//! step was measured at ~100µs of thread setup against ~10µs of work per
//! world — the pool exists so parallelism pays for itself.) Ownership per
//! world is exclusive and results land by position, so scheduling order can
//! never reorder or alter outputs; per-world determinism is untouched by
//! parallelism.

use std::collections::BTreeMap;
use std::ops::Range;
use std::panic::AssertUnwindSafe;
use std::sync::mpsc;
use std::thread::JoinHandle;

use cloudkitty_core::kitty::KittyId;

use crate::episode::{Episode, EpisodeError, EpisodeStep};

/// One world as its worker owns it. A panic mid-operation (an engine
/// invariant assertion, an internal expect) poisons the world — its state
/// may be mid-tick inconsistent, so it is never touched again — while the
/// sibling worlds and the environment stay usable, and the original panic
/// message is what callers see (spec 014 review: the old scoped-spawn
/// design killed the whole environment with a generic message).
enum WorldSlot {
    Live(Box<Episode>),
    Poisoned(String),
}

fn panic_message(payload: Box<dyn std::any::Any + Send>) -> String {
    if let Some(text) = payload.downcast_ref::<&str>() {
        (*text).to_string()
    } else if let Some(text) = payload.downcast_ref::<String>() {
        text.clone()
    } else {
        "non-string panic payload".to_string()
    }
}

fn run_slot(
    slot: &mut WorldSlot,
    op: impl FnOnce(&mut Episode) -> Result<EpisodeStep, EpisodeError>,
) -> Result<EpisodeStep, EpisodeError> {
    match slot {
        WorldSlot::Poisoned(message) => Err(EpisodeError::Panicked {
            message: message.clone(),
        }),
        WorldSlot::Live(episode) => {
            match std::panic::catch_unwind(AssertUnwindSafe(|| op(episode))) {
                Ok(result) => result,
                Err(payload) => {
                    let message = panic_message(payload);
                    *slot = WorldSlot::Poisoned(message.clone());
                    Err(EpisodeError::Panicked { message })
                }
            }
        }
    }
}

enum Command {
    /// One seed per owned world, in chunk order.
    Reset(Vec<u64>),
    /// One action map per owned world, in chunk order.
    Step(Vec<BTreeMap<KittyId, usize>>),
}

struct Worker {
    /// `Some` while the worker is live; taken in Drop to close the channel
    /// and end the worker's loop.
    tx: Option<mpsc::Sender<Command>>,
    rx: mpsc::Receiver<Vec<Result<EpisodeStep, EpisodeError>>>,
    /// The global world indices this worker owns.
    range: Range<usize>,
    handle: Option<JoinHandle<()>>,
}

pub struct VectorizedEnvironment {
    workers: Vec<Worker>,
    n_worlds: usize,
    external: Vec<KittyId>,
    roster: Vec<KittyId>,
    menu_len: usize,
}

impl VectorizedEnvironment {
    /// Wraps N independent episodes. `workers` defaults to one per world.
    pub fn new(episodes: Vec<Episode>, workers: Option<usize>) -> Self {
        let n = episodes.len();
        let external = episodes
            .first()
            .map(|e| e.external_agents())
            .unwrap_or_default();
        let roster = episodes.first().map(|e| e.roster()).unwrap_or_default();
        let menu_len = episodes.first().map(|e| e.codec().len()).unwrap_or(0);
        let worker_count = workers.unwrap_or(n).clamp(1, n.max(1));
        let chunk = n.div_ceil(worker_count.max(1)).max(1);

        let mut pool = Vec::new();
        let mut episodes = episodes.into_iter();
        let mut start = 0usize;
        while start < n {
            let take = chunk.min(n - start);
            let mut owned: Vec<WorldSlot> = Vec::with_capacity(take);
            for _ in 0..take {
                owned.push(WorldSlot::Live(Box::new(episodes.next().expect("counted"))));
            }
            let (cmd_tx, cmd_rx) = mpsc::channel::<Command>();
            let (result_tx, result_rx) = mpsc::channel();
            let handle = std::thread::spawn(move || {
                while let Some(command) = recv_spinning(&cmd_rx) {
                    let results: Vec<Result<EpisodeStep, EpisodeError>> = match command {
                        Command::Reset(seeds) => owned
                            .iter_mut()
                            .zip(seeds)
                            .map(|(slot, seed)| run_slot(slot, |episode| Ok(episode.reset(seed))))
                            .collect(),
                        Command::Step(actions) => owned
                            .iter_mut()
                            .zip(actions)
                            .map(|(slot, map)| run_slot(slot, |episode| episode.step(&map)))
                            .collect(),
                    };
                    if result_tx.send(results).is_err() {
                        break;
                    }
                }
            });
            pool.push(Worker {
                tx: Some(cmd_tx),
                rx: result_rx,
                range: start..start + take,
                handle: Some(handle),
            });
            start += take;
        }

        VectorizedEnvironment {
            workers: pool,
            n_worlds: n,
            external,
            roster,
            menu_len,
        }
    }

    pub fn len(&self) -> usize {
        self.n_worlds
    }

    pub fn is_empty(&self) -> bool {
        self.n_worlds == 0
    }

    /// The externally controlled agents (identical across worlds).
    pub fn external_agents(&self) -> Vec<KittyId> {
        self.external.clone()
    }

    /// The full roster (identical across worlds).
    pub fn roster(&self) -> Vec<KittyId> {
        self.roster.clone()
    }

    /// The menu length of the shared codec.
    pub fn menu_len(&self) -> usize {
        self.menu_len
    }

    /// Resets world i from seeds[i]. Panics if the lengths disagree.
    pub fn reset(&mut self, seeds: &[u64]) -> Vec<EpisodeStep> {
        assert_eq!(seeds.len(), self.n_worlds, "one seed per world");
        self.dispatch(|range| Command::Reset(seeds[range].to_vec()))
            .into_iter()
            .map(|r| r.expect("reset is infallible"))
            .collect()
    }

    /// Steps every world with its own action map, in parallel, gathered
    /// positionally.
    pub fn step(
        &mut self,
        actions: &[BTreeMap<KittyId, usize>],
    ) -> Vec<Result<EpisodeStep, EpisodeError>> {
        assert_eq!(actions.len(), self.n_worlds, "one action map per world");
        self.dispatch(|range| Command::Step(actions[range].to_vec()))
    }

    /// Broadcasts one command per worker, then gathers each worker's results
    /// into their worlds' global positions.
    fn dispatch(
        &mut self,
        command_for: impl Fn(Range<usize>) -> Command,
    ) -> Vec<Result<EpisodeStep, EpisodeError>> {
        for worker in &self.workers {
            worker
                .tx
                .as_ref()
                .expect("workers are live until Drop")
                .send(command_for(worker.range.clone()))
                .expect("worker thread alive");
        }
        let mut slots: Vec<Option<Result<EpisodeStep, EpisodeError>>> =
            (0..self.n_worlds).map(|_| None).collect();
        for worker in &self.workers {
            let results = worker.rx.recv().expect("worker thread alive");
            for (offset, result) in results.into_iter().enumerate() {
                slots[worker.range.start + offset] = Some(result);
            }
        }
        slots
            .into_iter()
            .map(|slot| slot.expect("every world was processed"))
            .collect()
    }
}

impl Drop for VectorizedEnvironment {
    fn drop(&mut self) {
        for worker in &mut self.workers {
            // Dropping the sender closes the channel and ends the worker's
            // loop.
            drop(worker.tx.take());
            if let Some(handle) = worker.handle.take() {
                let _ = handle.join();
            }
        }
    }
}

/// A bounded backoff before parking on the channel: batch steps arrive in
/// tight succession, and a parked thread's wake-up latency would otherwise
/// dominate sub-50µs world steps (measured: scoped spawns 0.85x, parked
/// pool ~2x, a spinning pool the rest of the way). The backoff is
/// two-phase — a short hot spin for the back-to-back case, then yielding
/// to the scheduler — so a worker waiting while the trainer computes cedes
/// its core quickly instead of burning it (spec 014 review), and an idle
/// environment parks.
fn recv_spinning<T>(rx: &mpsc::Receiver<T>) -> Option<T> {
    const HOT_SPINS: u32 = 1_000;
    const YIELDS: u32 = 200;
    for phase in 0..(HOT_SPINS + YIELDS) {
        match rx.try_recv() {
            Ok(value) => return Some(value),
            Err(mpsc::TryRecvError::Empty) => {
                if phase < HOT_SPINS {
                    std::hint::spin_loop();
                } else {
                    std::thread::yield_now();
                }
            }
            Err(mpsc::TryRecvError::Disconnected) => return None,
        }
    }
    rx.recv().ok()
}
