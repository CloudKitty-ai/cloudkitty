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

/// Resets one worker-owned world through the shared panic guard
/// ([`Episode::reset_caught`], which owns the catch/poison/heal story —
/// since the round-one review the Python surface's solo reset shares it,
/// so no reset path is bare). A failed world stays refused with the
/// original message while the sibling worlds and the environment stay
/// usable; any later successful reset heals.
fn reset_slot(episode: &mut Episode, seed: Option<u64>) -> Result<EpisodeStep, EpisodeError> {
    episode.reset_caught(seed)
}

enum Command {
    /// One seed per owned world, in chunk order; `None` advances the
    /// world's own deterministic fresh-seed chain ([`Episode::reset_fresh`]
    /// — the chain has exactly one owner).
    Reset(Vec<Option<u64>>),
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
    /// Batch coherence (third review), owned by the layer that owns the
    /// batch: `Some(why)` while stepping would be wrong — from construction
    /// (every world starts from the same config seed; reset gives each its
    /// own) and after any partial failure (survivors advanced while their
    /// transitions were discarded, skewing the batch a tick). `step`
    /// refuses with the reason until a fully successful reset clears it.
    needs_reset: Option<&'static str>,
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
            let mut owned: Vec<Box<Episode>> = Vec::with_capacity(take);
            for _ in 0..take {
                owned.push(Box::new(episodes.next().expect("counted")));
            }
            let (cmd_tx, cmd_rx) = mpsc::channel::<Command>();
            let (result_tx, result_rx) = mpsc::channel();
            let handle = std::thread::spawn(move || {
                while let Some(command) = recv_spinning(&cmd_rx) {
                    let results: Vec<Result<EpisodeStep, EpisodeError>> = match command {
                        Command::Reset(seeds) => owned
                            .iter_mut()
                            .zip(seeds)
                            .map(|(episode, seed)| reset_slot(episode, seed))
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
            needs_reset: Some("the worlds are unseeded until the first reset()"),
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

    /// Resets world i from seeds[i]. A successful reset also revives a
    /// world poisoned by an earlier panic (the fresh world re-establishes
    /// every invariant); an error is only possible if world generation
    /// itself panics. A fully successful reset restores batch coherence.
    /// Panics if the lengths disagree.
    pub fn reset(&mut self, seeds: &[u64]) -> Vec<Result<EpisodeStep, EpisodeError>> {
        assert_eq!(seeds.len(), self.n_worlds, "one seed per world");
        let results =
            self.dispatch(|range| Command::Reset(seeds[range].iter().map(|&s| Some(s)).collect()));
        self.settle_after_reset(&results);
        results
    }

    /// Resets every world along its own deterministic fresh-seed chain
    /// ([`Episode::reset_fresh`]): new episodes each call, the sequence
    /// reproducible, the chain owned by each episode — no shadow seed
    /// state anywhere else. Revives poisoned worlds like [`Self::reset`].
    pub fn reset_fresh(&mut self) -> Vec<Result<EpisodeStep, EpisodeError>> {
        let results = self.dispatch(|range| Command::Reset(vec![None; range.len()]));
        self.settle_after_reset(&results);
        results
    }

    /// Steps every world with its own action map, in parallel, gathered
    /// positionally. Refuses (every world `ResetRequired`) while the batch
    /// needs a reset — before the first reset, and after any partial
    /// failure left the batch desynchronized.
    pub fn step(
        &mut self,
        actions: &[BTreeMap<KittyId, usize>],
    ) -> Vec<Result<EpisodeStep, EpisodeError>> {
        assert_eq!(actions.len(), self.n_worlds, "one action map per world");
        if let Some(reason) = self.needs_reset {
            return (0..self.n_worlds)
                .map(|_| Err(EpisodeError::ResetRequired { reason }))
                .collect();
        }
        let results = self.dispatch(|range| Command::Step(actions[range].to_vec()));
        if results.iter().any(|r| r.is_err()) {
            self.needs_reset = Some(
                "a partial step failure desynchronized the batch; reset() revives \
                 the failed worlds and resynchronizes",
            );
        }
        results
    }

    fn settle_after_reset(&mut self, results: &[Result<EpisodeStep, EpisodeError>]) {
        self.needs_reset = if results.iter().all(|r| r.is_ok()) {
            None
        } else {
            Some("a failed world reset left the batch incoherent; reset() again")
        };
    }

    /// Broadcasts one command per worker, then gathers the results in
    /// worker order — worker ranges are contiguous and ascending by
    /// construction, so concatenation is global order.
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
        let mut results = Vec::with_capacity(self.n_worlds);
        for worker in &self.workers {
            results.extend(worker.rx.recv().expect("worker thread alive"));
        }
        assert_eq!(results.len(), self.n_worlds, "every world was processed");
        results
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
    // Measured on the reference machine (spec 014 second review): the
    // inter-batch gap under a Python driver is dominated by GIL-side
    // marshaling (~40-60µs on the default world), so a worker that parks
    // every batch pays the wake-up latency every time — capping yields at
    // 20 measured 0.86-1.03x scaling versus 1.17-1.33x at 200. Yielding is
    // not a burn: yield_now cedes the core to whoever is runnable (the
    // trainer included) and only its ~1-5µs syscall cost is real, so ~200
    // yields (~0.2-1ms) bridges realistic trainer gaps before parking for
    // genuinely idle environments.
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

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::Config;

    fn episode() -> Episode {
        crate::episode::Episode::new(
            Config::default(),
            crate::config::RlConfig::default(),
            BTreeMap::new(),
        )
        .unwrap()
    }

    #[test]
    fn a_poisoned_world_refuses_steps_and_reset_slot_revives_it() {
        // The poison state machine itself lives in Episode (see its own
        // tests); this covers the slot-level reset path that heals it.
        let mut episode = Box::new(episode());
        episode.poison("simulated engine panic".into());
        assert!(matches!(
            episode.step(&BTreeMap::new()),
            Err(EpisodeError::Panicked { .. })
        ));
        let revived = reset_slot(&mut episode, Some(4)).expect("reset revives");
        assert!(!revived.truncated);
        episode
            .step(&BTreeMap::new())
            .expect("stepping works again");
    }

    #[test]
    fn a_fresh_batch_refuses_to_step_until_reset() {
        // Third review: batch coherence is enforced by the layer that owns
        // the batch. A freshly built environment holds N config-seed clones
        // of one world — stepping them as "independent" worlds would be a
        // silent lie, so step refuses until reset deals real seeds.
        let mut env = VectorizedEnvironment::new(vec![episode(), episode()], Some(2));
        let refused = env.step(&[BTreeMap::new(), BTreeMap::new()]);
        assert!(
            refused
                .iter()
                .all(|r| matches!(r, Err(EpisodeError::ResetRequired { .. }))),
            "an unseeded batch must not step"
        );

        for result in env.reset(&[1, 2]) {
            result.expect("reset succeeds");
        }
        let stepped = env.step(&[BTreeMap::new(), BTreeMap::new()]);
        assert!(stepped.iter().all(|r| r.is_ok()), "reset arms the batch");
    }

    #[test]
    fn unseeded_batch_reset_advances_each_worlds_own_chain() {
        let mut env = VectorizedEnvironment::new(
            vec![
                crate::episode::Episode::new(
                    Config::default(),
                    crate::config::RlConfig::default(),
                    BTreeMap::new(),
                )
                .unwrap(),
                crate::episode::Episode::new(
                    Config::default(),
                    crate::config::RlConfig::default(),
                    BTreeMap::new(),
                )
                .unwrap(),
            ],
            Some(2),
        );
        let first: Vec<_> = env
            .reset(&[7, 8])
            .into_iter()
            .map(|r| r.unwrap().global_state)
            .collect();
        let fresh: Vec<_> = env
            .reset_fresh()
            .into_iter()
            .map(|r| r.unwrap().global_state)
            .collect();
        assert_ne!(first, fresh, "fresh episodes genuinely differ");
        // Reproducible: the same explicit seeds then fresh-chain replay.
        let again_first: Vec<_> = env
            .reset(&[7, 8])
            .into_iter()
            .map(|r| r.unwrap().global_state)
            .collect();
        let again_fresh: Vec<_> = env
            .reset_fresh()
            .into_iter()
            .map(|r| r.unwrap().global_state)
            .collect();
        assert_eq!(first, again_first);
        assert_eq!(fresh, again_fresh, "the chain replays exactly");
    }
}
