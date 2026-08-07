//! Writes the Arm 0 artifact: an all-zero MLP in the exp-001 shape
//! (obs→256→256→menu). Constant logits make masked SAMPLING exactly uniform
//! over legal actions — Arm 0 as pre-registered, seated via
//! `kitty-eval --artifact <path> --sample` (flag landed in PR #71 /
//! issue #70). Under greedy selection (the default) the same artifact
//! degenerates to a first-legal-action policy: still a valid end-to-end
//! plumbing probe for the artifact → PolicyBehavior → kitty-eval chain,
//! but NOT Arm 0.
//!
//! Widths and schema stamps come from the compiled engine, not from
//! literals. This wrote 182/schema-1 for a fortnight after the engine
//! moved to 183/schema-2, which would have made the one artifact whose
//! entire job is to prove the loading path works the one artifact that
//! could not load.
//!
//! Usage: zero-artifact <out.ckpolicy>

use cloudkitty_rl::codec::{ActionCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::mask::MASK_SCHEMA_VERSION;
use cloudkitty_rl::observe::{observation_len, OBSERVATION_SCHEMA_VERSION};
use cloudkitty_rl::policy::{write_artifact, ArtifactHeader};
use std::path::Path;

fn main() {
    let out = std::env::args()
        .nth(1)
        .expect("usage: zero-artifact <out.ckpolicy>");
    let obs_cfg = ObservationConfig::default();
    let obs = observation_len(&obs_cfg);
    let menu = ActionCodec::v1(&obs_cfg).len();
    let shapes = [[obs, 256], [256, 256], [256, menu]];
    let header = ArtifactHeader {
        artifact_version: 1,
        observation_schema: OBSERVATION_SCHEMA_VERSION,
        action_schema: ACTION_SCHEMA_VERSION,
        mask_schema: MASK_SCHEMA_VERSION,
        layers: shapes.to_vec(),
        activation: "relu".into(),
    };
    let layers: Vec<(Vec<f32>, Vec<f32>)> = shapes
        .iter()
        .map(|&[i, o]| (vec![0.0; i * o], vec![0.0; o]))
        .collect();
    write_artifact(Path::new(&out), &header, &layers).expect("writing artifact");
    println!("wrote {out} ({obs}->256->256->{menu}, all zeros, observation schema {OBSERVATION_SCHEMA_VERSION})");
}
