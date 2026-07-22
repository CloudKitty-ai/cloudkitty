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
use std::sync::mpsc;
use std::thread::JoinHandle;

use cloudkitty_core::kitty::KittyId;

use crate::episode::{Episode, EpisodeError, EpisodeStep};

enum Command {
    /// One seed per owned world, in chunk order.
    Reset(Vec<u64>),
    /// One action map per owned world, in chunk order.
    Step(Vec<BTreeMap<KittyId, usize>>),
}

struct Worker {
    tx: mpsc::Sender<Command>,
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
            let mut owned: Vec<Episode> = Vec::with_capacity(take);
            for _ in 0..take {
                owned.push(episodes.next().expect("counted"));
            }
            let (cmd_tx, cmd_rx) = mpsc::channel::<Command>();
            let (result_tx, result_rx) = mpsc::channel();
            let handle = std::thread::spawn(move || {
                while let Some(command) = recv_spinning(&cmd_rx) {
                    let results: Vec<Result<EpisodeStep, EpisodeError>> = match command {
                        Command::Reset(seeds) => owned
                            .iter_mut()
                            .zip(seeds)
                            .map(|(episode, seed)| Ok(episode.reset(seed)))
                            .collect(),
                        Command::Step(actions) => owned
                            .iter_mut()
                            .zip(actions)
                            .map(|(episode, map)| episode.step(&map))
                            .collect(),
                    };
                    if result_tx.send(results).is_err() {
                        break;
                    }
                }
            });
            pool.push(Worker {
                tx: cmd_tx,
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
            // Closing the command channel ends the worker's loop.
            let (dead_tx, _) = mpsc::channel();
            let _ = std::mem::replace(&mut worker.tx, dead_tx);
            if let Some(handle) = worker.handle.take() {
                let _ = handle.join();
            }
        }
    }
}

/// A bounded spin before parking on the channel: batch steps arrive in
/// tight succession, and a parked thread's wake-up latency would otherwise
/// dominate sub-50µs world steps (measured: scoped spawns 0.85x, parked
/// pool ~2x, spinning pool the rest of the way). The spin is bounded, so an
/// idle environment still parks its workers instead of burning a core.
fn recv_spinning<T>(rx: &mpsc::Receiver<T>) -> Option<T> {
    for _ in 0..20_000 {
        match rx.try_recv() {
            Ok(value) => return Some(value),
            Err(mpsc::TryRecvError::Empty) => std::hint::spin_loop(),
            Err(mpsc::TryRecvError::Disconnected) => return None,
        }
    }
    rx.recv().ok()
}
