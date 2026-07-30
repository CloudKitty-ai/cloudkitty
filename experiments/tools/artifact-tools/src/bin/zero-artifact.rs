//! Writes the Arm 0 artifact: an all-zero MLP in the exp-001 shape
//! (182→256→256→40). Constant logits make masked SAMPLING exactly uniform
//! over legal actions — Arm 0 as pre-registered, seated via
//! `kitty-eval --artifact <path> --sample` (flag landed in PR #71 /
//! issue #70). Under greedy selection (the default) the same artifact
//! degenerates to a first-legal-action policy: still a valid end-to-end
//! plumbing probe for the artifact → PolicyBehavior → kitty-eval chain,
//! but NOT Arm 0.
//!
//! Usage: zero-artifact <out.ckpolicy>

use cloudkitty_rl::policy::{write_artifact, ArtifactHeader};
use std::path::Path;

fn main() {
    let out = std::env::args()
        .nth(1)
        .expect("usage: zero-artifact <out.ckpolicy>");
    let shapes = [[182usize, 256], [256, 256], [256, 40]];
    let header = ArtifactHeader {
        artifact_version: 1,
        observation_schema: 1,
        action_schema: 1,
        mask_schema: 1,
        layers: shapes.to_vec(),
        activation: "relu".into(),
    };
    let layers: Vec<(Vec<f32>, Vec<f32>)> = shapes
        .iter()
        .map(|&[i, o]| (vec![0.0; i * o], vec![0.0; o]))
        .collect();
    write_artifact(Path::new(&out), &header, &layers).expect("writing artifact");
    println!("wrote {out} (182->256->256->40, all zeros)");
}
