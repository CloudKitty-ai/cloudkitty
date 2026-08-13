//! Spec 030 US1 (T010): a v3 entity-attention artifact loads and serves, and
//! a v2 artifact still loads and serves in the same binary (SC-001, SC-004).

use std::path::PathBuf;

use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::observe::observation_len;
use cloudkitty_rl::policy::Scratch;
use cloudkitty_rl::test_support::{write_fixture_artifact, write_v3_fixture_artifact};

fn scratch_dir(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join("ck-artifact-v3-load").join(name);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

#[test]
fn a_v3_artifact_loads_and_serves_a_full_width_logit_vector() {
    let rl = RlConfig::default();
    let path = scratch_dir("v3").join("policy.ckpolicy");
    write_v3_fixture_artifact(&path, 3);

    let beh = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    assert_eq!(beh.content_hash().len(), 64, "the file is hashed at load");

    let out_len = ActionCodec::v2(&rl.observation).len() + MessageCodec::LEN;
    let obs = vec![0.0f32; observation_len(&rl.observation)];
    let mut scratch = Scratch::default();
    let logits = beh.artifact().forward(&obs, &mut scratch);
    assert_eq!(logits.len(), out_len, "menu + message head width");
    assert!(
        logits.iter().all(|x| x.is_finite()),
        "no NaN/inf out of the forward"
    );
}

#[test]
fn a_v2_artifact_still_loads_and_serves_beside_v3() {
    let rl = RlConfig::default();
    let path = scratch_dir("v2").join("policy.ckpolicy");
    // The existing v2 fixture writer (obs → 16 → menu), untouched by v3.
    write_fixture_artifact(&path, 16, 5);

    let beh = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    let out_len = ActionCodec::v2(&rl.observation).len() + MessageCodec::LEN;
    let obs = vec![0.0f32; observation_len(&rl.observation)];
    let mut scratch = Scratch::default();
    let logits = beh.artifact().forward(&obs, &mut scratch);
    assert_eq!(logits.len(), out_len, "the v2 path is unchanged");
    assert!(logits.iter().all(|x| x.is_finite()));
}
