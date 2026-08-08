//! The single source of randomness (Article V).
//!
//! Everything random in CloudKitty flows through one seeded `ChaCha8Rng`, which is
//! serialized into snapshots so determinism survives restarts. ChaCha8 is used
//! rather than `StdRng` because its algorithm is stable across releases — a
//! persisted seed must mean the same thing tomorrow as it does today.
//!
//! Behaviors decide concurrently, so they must not share the master RNG: completion
//! order would leak into the results. Instead the engine draws one seed per kitty
//! **in stable kitty-id order before any decision runs** and hands each behavior its
//! own [`DecisionRng`]. Scheduling can then vary freely without changing outcomes.

use std::sync::Mutex;

use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use serde::{Deserialize, Serialize};

/// The world's master RNG.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimRng {
    inner: ChaCha8Rng,
}

impl SimRng {
    pub fn from_seed(seed: u64) -> Self {
        Self {
            inner: ChaCha8Rng::seed_from_u64(seed),
        }
    }

    pub fn gen_range_u32(&mut self, low: u32, high: u32) -> u32 {
        if low >= high {
            return low;
        }
        self.inner.gen_range(low..high)
    }

    pub fn gen_bool(&mut self, probability: f64) -> bool {
        self.inner.gen_bool(probability.clamp(0.0, 1.0))
    }

    pub fn choose<'a, T>(&mut self, items: &'a [T]) -> Option<&'a T> {
        if items.is_empty() {
            return None;
        }
        let idx = self.inner.gen_range(0..items.len());
        Some(&items[idx])
    }

    pub fn next_u64(&mut self) -> u64 {
        self.inner.gen()
    }

    /// One uniform draw in `[0, 1)` -- the same recipe as
    /// [`DecisionRng::gen_f32`], on the master stream (spec 022: the purr
    /// announce decision and cooldown-factor draw). Always consumes exactly
    /// one draw: probability comparisons against it keep the fixed-shape
    /// rule even at 0 and 1 -- unlike `gen_bool`, whose Bernoulli
    /// short-circuits `p = 1.0` without touching the stream.
    pub fn gen_f32(&mut self) -> f32 {
        self.inner.gen()
    }
}

/// A per-kitty, per-tick RNG handed to a behavior.
///
/// Interior mutability keeps `Behavior::decide(&self, ctx)` ergonomic while the
/// context stays shared-reference-only. Each kitty owns its own stream, so the
/// mutex is never contended and never affects determinism.
#[derive(Debug)]
pub struct DecisionRng {
    inner: Mutex<ChaCha8Rng>,
}

impl DecisionRng {
    pub fn from_seed(seed: u64) -> Self {
        Self {
            inner: Mutex::new(ChaCha8Rng::seed_from_u64(seed)),
        }
    }

    fn with<R>(&self, f: impl FnOnce(&mut ChaCha8Rng) -> R) -> R {
        // A poisoned mutex would mean a behavior panicked mid-draw; recover the
        // stream rather than propagating a panic into the engine.
        let mut guard = match self.inner.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        f(&mut guard)
    }

    /// Restarts this stream from `seed`. Dispatch uses it before running
    /// the fallback (spec 014 review): a failed advisor's partial draws must
    /// never shift the fallback's stream, and the rule must hold identically
    /// on the served and budgetless paths — both restart from the dealt
    /// seed.
    pub fn reseed(&self, seed: u64) {
        self.with(|r| *r = ChaCha8Rng::seed_from_u64(seed));
    }

    pub fn gen_range_usize(&self, low: usize, high: usize) -> usize {
        if low >= high {
            return low;
        }
        self.with(|r| r.gen_range(low..high))
    }

    pub fn gen_bool(&self, probability: f64) -> bool {
        self.with(|r| r.gen_bool(probability.clamp(0.0, 1.0)))
    }

    pub fn gen_f32(&self) -> f32 {
        self.with(|r| r.gen::<f32>())
    }

    /// One raw draw. The seed a plugin decision request carries (spec 016,
    /// research R5): drawn from the kitty's own stream, so it is
    /// deterministic to the world and never synchronized between kitties.
    pub fn gen_u64(&self) -> u64 {
        self.with(|r| r.gen::<u64>())
    }

    pub fn choose<'a, T>(&self, items: &'a [T]) -> Option<&'a T> {
        if items.is_empty() {
            return None;
        }
        let idx = self.with(|r| r.gen_range(0..items.len()));
        Some(&items[idx])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn same_seed_produces_the_same_stream() {
        let mut a = SimRng::from_seed(42);
        let mut b = SimRng::from_seed(42);
        for _ in 0..100 {
            assert_eq!(a.next_u64(), b.next_u64());
        }
    }

    #[test]
    fn different_seeds_diverge() {
        let mut a = SimRng::from_seed(1);
        let mut b = SimRng::from_seed(2);
        let a: Vec<u64> = (0..10).map(|_| a.next_u64()).collect();
        let b: Vec<u64> = (0..10).map(|_| b.next_u64()).collect();
        assert_ne!(a, b);
    }

    #[test]
    fn rng_state_survives_serialization() {
        let mut original = SimRng::from_seed(7);
        for _ in 0..25 {
            original.next_u64();
        }
        let json = serde_json::to_string(&original).expect("serialize");
        let mut restored: SimRng = serde_json::from_str(&json).expect("deserialize");

        // The restored RNG must continue the same stream, not restart it.
        assert_eq!(original.next_u64(), restored.next_u64());
        assert_eq!(original.next_u64(), restored.next_u64());
    }

    #[test]
    fn decision_streams_are_order_independent() {
        // Deriving streams in a fixed order then consuming them in any order must
        // give the same values -- this is what makes concurrent decisions safe.
        let mut master = SimRng::from_seed(99);
        let streams: Vec<DecisionRng> = (0..4)
            .map(|_| DecisionRng::from_seed(master.next_u64()))
            .collect();
        let forward: Vec<f32> = streams.iter().map(|s| s.gen_f32()).collect();

        let mut master2 = SimRng::from_seed(99);
        let streams2: Vec<DecisionRng> = (0..4)
            .map(|_| DecisionRng::from_seed(master2.next_u64()))
            .collect();
        // Consume in reverse order; each stream still yields its own first value.
        let mut backward = vec![0.0; 4];
        for i in (0..4).rev() {
            backward[i] = streams2[i].gen_f32();
        }

        assert_eq!(forward, backward);
    }

    #[test]
    fn master_gen_f32_is_deterministic_in_unit_range_and_always_consumes() {
        // Spec 022: same seed -> same sequence, every value in [0, 1), and
        // exactly one stream consumption per call (proved by the streams
        // staying aligned after equal call counts).
        let mut a = SimRng::from_seed(11);
        let mut b = SimRng::from_seed(11);
        for _ in 0..1_000 {
            let v = a.gen_f32();
            assert!((0.0..1.0).contains(&v));
            assert_eq!(v, b.gen_f32());
        }
        assert_eq!(a.next_u64(), b.next_u64(), "streams still aligned");
    }

    #[test]
    fn choose_on_empty_slice_is_none() {
        let rng = DecisionRng::from_seed(3);
        let empty: [u8; 0] = [];
        assert!(rng.choose(&empty).is_none());
    }
}
