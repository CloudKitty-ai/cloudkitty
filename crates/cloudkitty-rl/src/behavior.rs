//! The policy behavior (spec 014 FR-014/FR-015): a trained artifact seated
//! in the advisor's chair.
//!
//! `PolicyBehavior` implements the engine's `Behavior` trait as a
//! non-built-in — the served world applies its standing time budget, panic
//! isolation, and fallback; headless drives dispatch it budgetlessly with
//! provenance marking (FR-017). Each decision runs
//! encode → infer → mask → select → decode against the frozen snapshot,
//! with no I/O and nothing awaited, so the budget is never in play on a
//! healthy host.
//!
//! Selection (FR-015): the legal-action mask — the same implementation
//! training used — is applied between inference and selection. Greedy by
//! default (argmax over masked logits, ties to the lowest index); optional
//! sampling draws only from the kitty's own per-tick decision stream, the
//! same stream the training environment surfaces. Selection is total:
//! non-finite logits are excluded, and if none survive, the lowest
//! masked-in entry is chosen — nothing propagates NaN into a proposal.

use std::path::Path;
use std::sync::Mutex;

use async_trait::async_trait;
use cloudkitty_core::behavior::{Behavior, DecisionContext};
use cloudkitty_core::Decision;

use crate::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use crate::config::RlConfig;
use crate::mask::{legal_action_mask, legal_message_mask, MASK_SCHEMA_VERSION};
use crate::observe::{encode_observation, observation_len, OBSERVATION_SCHEMA_VERSION};
use crate::policy::{ArtifactError, PolicyArtifact, SchemaExpectations, Scratch};

pub struct PolicyBehavior {
    artifact: PolicyArtifact,
    rl: RlConfig,
    codec: ActionCodec,
    /// Greedy by default; sampling draws from the kitty's decision stream.
    sample: bool,
    /// Reused inference buffers (FR-014: no per-decision allocation beyond
    /// these). Decisions across kitties serialize briefly on this lock;
    /// the pass itself is microseconds.
    scratch: Mutex<Scratch>,
}

impl PolicyBehavior {
    /// The compiled schema expectations artifacts must match (FR-016).
    pub fn expectations(rl: &RlConfig) -> SchemaExpectations {
        let codec = ActionCodec::v2(&rl.observation);
        SchemaExpectations {
            observation_schema: OBSERVATION_SCHEMA_VERSION,
            action_schema: ACTION_SCHEMA_VERSION,
            mask_schema: MASK_SCHEMA_VERSION,
            observation_len: observation_len(&rl.observation),
            menu_len: codec.len(),
            message_head_len: MessageCodec::LEN,
            observation: rl.observation,
        }
    }

    pub fn new(artifact: PolicyArtifact, rl: RlConfig, sample: bool) -> Self {
        let codec = ActionCodec::v2(&rl.observation);
        PolicyBehavior {
            artifact,
            rl,
            codec,
            sample,
            scratch: Mutex::new(Scratch::default()),
        }
    }

    /// Loads, validates, and seats an artifact. `sample` picks the
    /// selection mode exactly as `[rl.policy.<name>].sample` does at server
    /// startup — the same [`select`] path either way (issue #70).
    pub fn from_artifact_path(
        path: &str,
        rl: &RlConfig,
        sample: bool,
    ) -> Result<Self, ArtifactError> {
        let artifact = PolicyArtifact::load(Path::new(path), &Self::expectations(rl))?;
        Ok(Self::new(artifact, rl.clone(), sample))
    }

    /// The loaded artifact's content hash (FR-016: logged and exposed).
    pub fn content_hash(&self) -> &str {
        &self.artifact.sha256
    }

    pub fn artifact(&self) -> &PolicyArtifact {
        &self.artifact
    }

    /// One decision against a frozen snapshot: the deterministic pipeline
    /// FR-015 pins, two-headed since spec 028. Public so selection tests
    /// drive it directly.
    pub fn decide_sync(&self, ctx: &DecisionContext) -> Decision {
        let observation = encode_observation(
            &ctx.world,
            ctx.me.id,
            &ctx.config,
            &self.rl.observation,
            // Serve the clock as trained (owner 2026-09-15): the minds saw
            // tick_in_episode / horizon cycling in every training and
            // certification tick, and pinning it to 0 at deploy re-opens a
            // greedy limit cycle the drifting clock breaks
            // (experiments/fog-gen1-cert/RESULTS.md §"The clock input").
            // Gen 2 removes the dependence (GEN2-INPUTS).
            served_clock(ctx.world.tick, self.rl.episode.horizon),
        );
        let activity_mask = legal_action_mask(
            &ctx.world,
            ctx.me.id,
            &observation.table,
            &self.codec,
            &ctx.config,
        );
        let message_mask = legal_message_mask(&ctx.world, ctx.me.id, &ctx.config);
        let (activity_index, message_index) = {
            let mut scratch = match self.scratch.lock() {
                Ok(guard) => guard,
                Err(poisoned) => poisoned.into_inner(),
            };
            let logits = self.artifact.forward(&observation.values, &mut scratch);
            let menu = self.codec.len();
            // The fixed-shape rule (Article V): greedy draws nothing;
            // sampling draws exactly ONE u64 and splits it -- hi u32 seeds
            // the activity head's uniform, lo u32 the message head's.
            let (u_act, u_msg) = if self.sample {
                let bits = ctx.rng.gen_u64();
                (
                    Some(uniform_from_u32((bits >> 32) as u32)),
                    Some(uniform_from_u32(bits as u32)),
                )
            } else {
                (None, None)
            };
            (
                select(&logits[..menu], &activity_mask, u_act),
                select(&logits[menu..], &message_mask, u_msg),
            )
        };
        let activity = self
            .codec
            .decode(activity_index, &observation.table)
            .expect("selection stays inside the menu");
        let message = MessageCodec::decode(message_index).expect("selection stays inside the head");
        Decision { activity, message }
    }
}

/// The served episode clock: `(world tick mod horizon) / horizon`, the same
/// cycling value training's `tick_in_episode / horizon` produced (episodes
/// truncate AT the horizon, so training never saw 1.0). Serving stays below
/// 1.0 too at any realistic horizon; a horizon above 2^24 could round the
/// f32 ratio up to exactly 1.0 (`encode_observation` clamps to [0, 1], so
/// nothing escapes range either way — the served horizon is 2,000). A
/// deliberate stopgap: Gen 2 removes the clock dependence entirely
/// (GEN2-INPUTS, ruled 2026-09-15), retiring this function with it.
/// `[rl.episode] horizon` is validated ≥ 1, and the served world's tick
/// counter persists across restarts, so the modulus is well defined on a
/// continuing world.
fn served_clock(tick: u64, horizon: u64) -> f32 {
    (tick % horizon) as f32 / horizon as f32
}

/// Maps a u32 onto [0, 1): the per-head uniform derived from one split
/// `DecisionRng` draw (spec 028 R10). Stays f64: bits/2^32 is exact
/// there (32 bits fit the 53-bit mantissa), so the result tops out at
/// 1 - 2^-32. A cast to f32 would round the top 128 values to exactly
/// 1.0 and degenerate the softmax draw to the last legal candidate.
fn uniform_from_u32(bits: u32) -> f64 {
    bits as f64 / (u32::MAX as f64 + 1.0)
}

/// Masked selection for one head, total by construction: non-finite
/// logits are excluded; if nothing survives, the lowest masked-in entry
/// wins. `uniform` None is greedy (ties to the lowest index, no draw);
/// Some(u) is a softmax draw positioned by the caller-supplied uniform --
/// the per-head half of one split u64 (spec 028 R10).
fn select(logits: &[f32], mask: &[bool], uniform: Option<f64>) -> usize {
    let candidates: Vec<usize> = (0..logits.len())
        .filter(|&i| mask[i] && logits[i].is_finite())
        .collect();
    let Some(&first_legal) = candidates.first() else {
        // Garbage logits everywhere: the lowest masked-in entry. Neither
        // mask is ever all-zero (structural), so this always exists.
        return mask.iter().position(|&b| b).unwrap_or(0);
    };
    let Some(uniform) = uniform else {
        let mut best = first_legal;
        for &i in &candidates {
            if logits[i] > logits[best] {
                best = i;
            }
        }
        return best;
    };
    // Softmax over the masked, finite logits.
    let max = candidates
        .iter()
        .map(|&i| logits[i])
        .fold(f32::NEG_INFINITY, f32::max);
    let weights: Vec<f64> = candidates
        .iter()
        .map(|&i| ((logits[i] - max) as f64).exp())
        .collect();
    let total: f64 = weights.iter().sum();
    let mut draw = uniform * total;
    for (&index, weight) in candidates.iter().zip(&weights) {
        if draw < *weight {
            return index;
        }
        draw -= weight;
    }
    *candidates.last().unwrap_or(&first_legal)
}

#[async_trait]
impl Behavior for PolicyBehavior {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        self.decide_sync(ctx)
    }
    // is_builtin stays false: the served world's budget, panic isolation,
    // and fallback all apply (FR-014).
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::rng::DecisionRng;

    #[test]
    fn the_served_clock_cycles_through_the_trained_horizon() {
        // Owner ruling 2026-09-15: the seam serves (tick mod horizon) /
        // horizon, matching training's tick_in_episode / horizon. The value
        // stays in [0, 1) — episodes truncate AT the horizon, so training
        // never saw 1.0.
        assert_eq!(served_clock(0, 2_000), 0.0);
        assert_eq!(served_clock(500, 2_000), 0.25);
        assert_eq!(served_clock(1_999, 2_000), 1_999.0 / 2_000.0);
        assert_eq!(served_clock(2_000, 2_000), 0.0, "the clock wraps");
        assert_eq!(served_clock(2_500, 2_000), 0.25, "and keeps cycling");
        // A continuing world far past any episode length stays in range.
        let long = served_clock(u64::MAX - 3, 2_000);
        assert!((0.0..1.0).contains(&long), "{long} escaped [0, 1)");
    }

    #[test]
    fn selection_is_total_under_garbage_logits() {
        let mask = vec![false, true, false, true];

        // NaN and infinities: excluded, best finite masked-in wins.
        let logits = vec![f32::NAN, 1.0, f32::INFINITY, 2.0];
        assert_eq!(select(&logits, &mask, None), 3);

        // All-equal: lowest masked-in index.
        let logits = vec![0.5, 0.5, 0.5, 0.5];
        assert_eq!(select(&logits, &mask, None), 1);

        // Nothing finite: still an in-range masked-in entry.
        let logits = vec![f32::NAN, f32::NAN, f32::NAN, f32::NEG_INFINITY.sqrt()];
        assert_eq!(select(&logits, &mask, None), 1);
    }

    #[test]
    fn sampling_is_deterministic_given_the_stream() {
        // The two-head draw shape (spec 028 R10): ONE u64 from the stream,
        // hi u32 for one head, lo for the other -- same seed, same split,
        // same picks.
        let mask = vec![true; 4];
        let logits = vec![0.0, 1.0, 2.0, 3.0];
        let draw = |seed: u64| {
            let bits = DecisionRng::from_seed(seed).gen_u64();
            (
                select(&logits, &mask, Some(uniform_from_u32((bits >> 32) as u32))),
                select(&logits, &mask, Some(uniform_from_u32(bits as u32))),
            )
        };
        assert_eq!(draw(7), draw(7), "same seed, same draws");
    }

    #[test]
    fn the_top_of_the_uniform_range_never_degenerates_the_draw() {
        // Regression: casting the uniform to f32 rounded the top 128 u32
        // values to exactly 1.0, making `draw < weight` never fire and
        // handing the pick to the LAST legal candidate regardless of
        // weight. With the mass overwhelmingly on index 0, bits at the
        // very top of the range must still land there.
        let mask = vec![true; 4];
        let logits = vec![40.0, 0.0, 0.0, 0.0];
        for bits in [u32::MAX, u32::MAX - 127] {
            let uniform = uniform_from_u32(bits);
            assert!(uniform < 1.0, "the uniform stays inside [0, 1)");
            assert_eq!(
                select(&logits, &mask, Some(uniform)),
                0,
                "bits {bits:#x}: the near-total-mass candidate wins"
            );
        }
    }
}
