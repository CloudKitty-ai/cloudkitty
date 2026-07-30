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
use cloudkitty_core::action::Action;
use cloudkitty_core::behavior::{Behavior, DecisionContext};
use cloudkitty_core::rng::DecisionRng;

use crate::codec::{ActionCodec, ACTION_SCHEMA_VERSION};
use crate::config::RlConfig;
use crate::mask::{legal_action_mask, MASK_SCHEMA_VERSION};
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
        let codec = ActionCodec::v1(&rl.observation);
        SchemaExpectations {
            observation_schema: OBSERVATION_SCHEMA_VERSION,
            action_schema: ACTION_SCHEMA_VERSION,
            mask_schema: MASK_SCHEMA_VERSION,
            observation_len: observation_len(&rl.observation),
            menu_len: codec.len(),
        }
    }

    pub fn new(artifact: PolicyArtifact, rl: RlConfig, sample: bool) -> Self {
        let codec = ActionCodec::v1(&rl.observation);
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
    /// FR-015 pins. Public so selection tests drive it directly.
    pub fn decide_sync(&self, ctx: &DecisionContext) -> Action {
        let observation = encode_observation(
            &ctx.world,
            ctx.me.id,
            &ctx.config,
            &self.rl.observation,
            // No episode runs at deploy; the clock input is pinned to 0.
            0.0,
        );
        let mask = legal_action_mask(
            &ctx.world,
            ctx.me.id,
            &observation.table,
            &self.codec,
            &ctx.config,
        );
        let index = {
            let mut scratch = match self.scratch.lock() {
                Ok(guard) => guard,
                Err(poisoned) => poisoned.into_inner(),
            };
            let logits = self.artifact.forward(&observation.values, &mut scratch);
            select(logits, &mask, self.sample, &ctx.rng)
        };
        self.codec
            .decode(index, &observation.table)
            .expect("selection stays inside the menu")
    }
}

/// Masked selection, total by construction: non-finite logits are excluded;
/// if nothing survives, the lowest masked-in entry wins. Greedy ties go to
/// the lowest index; sampling is a softmax draw from the kitty's stream.
fn select(logits: &[f32], mask: &[bool], sample: bool, rng: &DecisionRng) -> usize {
    let candidates: Vec<usize> = (0..logits.len())
        .filter(|&i| mask[i] && logits[i].is_finite())
        .collect();
    let Some(&first_legal) = candidates.first() else {
        // Garbage logits everywhere: the lowest masked-in entry. The mask
        // is never all-zero (structural, FR-018), so this always exists.
        return mask.iter().position(|&b| b).unwrap_or(0);
    };
    if !sample {
        let mut best = first_legal;
        for &i in &candidates {
            if logits[i] > logits[best] {
                best = i;
            }
        }
        return best;
    }
    // Softmax over the masked, finite logits; drawn from the kitty's own
    // decision stream (FR-015).
    let max = candidates
        .iter()
        .map(|&i| logits[i])
        .fold(f32::NEG_INFINITY, f32::max);
    let weights: Vec<f64> = candidates
        .iter()
        .map(|&i| ((logits[i] - max) as f64).exp())
        .collect();
    let total: f64 = weights.iter().sum();
    let mut draw = rng.gen_f32() as f64 * total;
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
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        self.decide_sync(ctx)
    }
    // is_builtin stays false: the served world's budget, panic isolation,
    // and fallback all apply (FR-014).
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn selection_is_total_under_garbage_logits() {
        let rng = DecisionRng::from_seed(1);
        let mask = vec![false, true, false, true];

        // NaN and infinities: excluded, best finite masked-in wins.
        let logits = vec![f32::NAN, 1.0, f32::INFINITY, 2.0];
        assert_eq!(select(&logits, &mask, false, &rng), 3);

        // All-equal: lowest masked-in index.
        let logits = vec![0.5, 0.5, 0.5, 0.5];
        assert_eq!(select(&logits, &mask, false, &rng), 1);

        // Nothing finite: still an in-range masked-in entry.
        let logits = vec![f32::NAN, f32::NAN, f32::NAN, f32::NEG_INFINITY.sqrt()];
        assert_eq!(select(&logits, &mask, false, &rng), 1);
    }

    #[test]
    fn sampling_is_deterministic_given_the_stream() {
        let mask = vec![true; 4];
        let logits = vec![0.0, 1.0, 2.0, 3.0];
        let a = select(&logits, &mask, true, &DecisionRng::from_seed(7));
        let b = select(&logits, &mask, true, &DecisionRng::from_seed(7));
        assert_eq!(a, b, "same seed, same draw");
    }
}
