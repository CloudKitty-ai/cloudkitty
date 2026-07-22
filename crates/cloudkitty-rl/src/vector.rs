//! Vectorized environments (spec 014 FR-012, research.md R6): N fully
//! independent episodes — separate seeds, separate RNGs, zero shared
//! state — stepped as a batch across a scoped thread pool. Results are
//! gathered positionally, so scheduling order can never reorder or alter
//! outputs; per-world determinism is untouched by parallelism.

use std::collections::BTreeMap;

use cloudkitty_core::kitty::KittyId;

use crate::episode::{Episode, EpisodeError, EpisodeStep};

pub struct VectorizedEnvironment {
    episodes: Vec<Episode>,
    workers: usize,
}

impl VectorizedEnvironment {
    /// Wraps N independent episodes. `workers` defaults to one per world.
    pub fn new(episodes: Vec<Episode>, workers: Option<usize>) -> Self {
        let n = episodes.len().max(1);
        VectorizedEnvironment {
            episodes,
            workers: workers.unwrap_or(n).clamp(1, n),
        }
    }

    pub fn len(&self) -> usize {
        self.episodes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.episodes.is_empty()
    }

    pub fn episodes(&self) -> &[Episode] {
        &self.episodes
    }

    /// Resets world i from seeds[i]. Panics if the lengths disagree.
    pub fn reset(&mut self, seeds: &[u64]) -> Vec<EpisodeStep> {
        assert_eq!(seeds.len(), self.episodes.len(), "one seed per world");
        self.fan_out(|episode, i| Ok(episode.reset(seeds[i])))
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
        assert_eq!(
            actions.len(),
            self.episodes.len(),
            "one action map per world"
        );
        self.fan_out(|episode, i| episode.step(&actions[i]))
    }

    /// Scoped-thread fan-out: worlds are distributed in contiguous chunks;
    /// each result lands in its world's slot regardless of scheduling.
    fn fan_out<F>(&mut self, f: F) -> Vec<Result<EpisodeStep, EpisodeError>>
    where
        F: Fn(&mut Episode, usize) -> Result<EpisodeStep, EpisodeError> + Sync,
    {
        let n = self.episodes.len();
        if n == 0 {
            return Vec::new();
        }
        let chunk = n.div_ceil(self.workers.min(n));
        let mut results: Vec<Option<Result<EpisodeStep, EpisodeError>>> =
            (0..n).map(|_| None).collect();

        std::thread::scope(|scope| {
            let mut episode_chunks = self.episodes.chunks_mut(chunk);
            let mut result_chunks = results.chunks_mut(chunk);
            let mut base = 0usize;
            let f = &f;
            for (episodes, results) in std::iter::zip(&mut episode_chunks, &mut result_chunks) {
                let start = base;
                base += episodes.len();
                scope.spawn(move || {
                    for (offset, (episode, slot)) in
                        std::iter::zip(episodes.iter_mut(), results.iter_mut()).enumerate()
                    {
                        *slot = Some(f(episode, start + offset));
                    }
                });
            }
        });

        results
            .into_iter()
            .map(|slot| slot.expect("every world was stepped"))
            .collect()
    }
}
