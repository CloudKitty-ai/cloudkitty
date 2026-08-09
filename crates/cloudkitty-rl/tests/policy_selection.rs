//! Policy selection (spec 014 FR-015, T042): same artifact + same
//! observation + same decision seed → the same action, however many times
//! the artifact is re-loaded (the decision is a pure function of the file
//! bytes, the snapshot, and the seed — process boundaries hold nothing);
//! and garbage logits (NaN, ±inf, all-equal) still select a masked-in
//! action.

use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::behavior::DecisionContext;
use cloudkitty_core::rng::DecisionRng;
use cloudkitty_core::Config;
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::codec::ActionCodec;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::mask::legal_action_mask;
use cloudkitty_rl::observe::TargetTable;
use cloudkitty_rl::test_support::write_fixture_artifact_with_output;

fn artifact_path(name: &str, fill: f32) -> PathBuf {
    let dir = std::env::temp_dir().join("ck-policy-selection");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join(format!("{name}.ckpolicy"));
    write_fixture_artifact_with_output(&path, 8, 0, Some(fill));
    path
}

fn context(seed: u64) -> DecisionContext {
    let config = Arc::new(Config::default());
    let world = cloudkitty_core::World::generate(&config);
    let snapshot = Arc::new(world.snapshot());
    DecisionContext {
        me: snapshot.kitties[0].clone(),
        world: snapshot,
        rng: DecisionRng::from_seed(seed),
        config,
    }
}

#[test]
fn the_same_artifact_observation_and_seed_select_the_same_action() {
    let path = artifact_path("deterministic", 0.2);
    let rl = RlConfig::default();

    // Greedy: two independent loads decide identically (seed-independent).
    let a = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    let b = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    assert_eq!(a.decide_sync(&context(1)), b.decide_sync(&context(2)));

    // Sampling: deterministic given the kitty's decision seed, and only
    // that seed (FR-015 — one stochasticity mechanism).
    let sampling = PolicyBehavior::new(a.artifact().clone(), rl.clone(), true);
    let first = sampling.decide_sync(&context(7));
    let second = sampling.decide_sync(&context(7));
    assert_eq!(first, second, "same stream, same draw");
}

#[test]
fn garbage_logits_still_select_a_masked_in_action() {
    let rl = RlConfig::default();
    let config = Arc::new(Config::default());
    let world = cloudkitty_core::World::generate(&config);
    let snapshot = world.snapshot();
    let codec = ActionCodec::v2(&rl.observation);

    for (name, fill) in [
        ("nan", f32::NAN),
        ("plus-inf", f32::INFINITY),
        ("minus-inf", f32::NEG_INFINITY),
        ("all-equal", 0.0),
    ] {
        let path = artifact_path(name, fill);
        let behavior =
            PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
        let decision = behavior.decide_sync(&context(3));
        let action = decision.activity;

        // The selected activity decodes from a masked-in entry: encode it
        // back through the kitty's table and check the mask bit. The
        // message head is checked against its own oracle (spec 028).
        let table = TargetTable::build(&snapshot, snapshot.kitties[0].id, &rl.observation);
        let mask = legal_action_mask(&snapshot, snapshot.kitties[0].id, &table, &codec, &config);
        let index = codec
            .encode(&action, &table)
            .unwrap_or_else(|| panic!("{name}: {action:?} is not expressible"));
        assert!(mask[index], "{name}: selected an illegal entry {index}");
        let message_mask =
            cloudkitty_rl::mask::legal_message_mask(&snapshot, snapshot.kitties[0].id, &config);
        let head_index = cloudkitty_rl::codec::MessageCodec::encode(decision.message)
            .expect("selected messages are head-expressible");
        assert!(
            message_mask[head_index],
            "{name}: selected an illegal message {head_index}"
        );
    }
}
