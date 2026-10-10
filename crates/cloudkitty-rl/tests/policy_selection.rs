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
use cloudkitty_rl::codec::{MessageCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::mask::legal_action_mask;
use cloudkitty_rl::mask::MASK_SCHEMA_VERSION;
use cloudkitty_rl::observe::{observation_len, TargetTable, OBSERVATION_SCHEMA_VERSION};
use cloudkitty_rl::policy::{write_artifact, ArtifactHeader, ARTIFACT_VERSION};
use cloudkitty_rl::test_support::write_fixture_artifact_with_output;

fn artifact_path(name: &str, fill: f32) -> PathBuf {
    let dir = std::env::temp_dir().join("ck-policy-selection");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join(format!("{name}.ckpolicy"));
    write_fixture_artifact_with_output(&path, 8, 0, Some(fill));
    path
}

fn context(seed: u64) -> DecisionContext {
    context_at_tick(seed, 0)
}

/// [`context`], on the same generated world advanced to `tick` by the
/// clock alone — nothing else about the world moves, so two contexts
/// differ in exactly the one input the served episode clock derives from.
fn context_at_tick(seed: u64, tick: u64) -> DecisionContext {
    let config = Arc::new(Config::default());
    let mut world = cloudkitty_core::World::generate(&config);
    world.tick = tick;
    let snapshot = world.snapshot();
    let me = snapshot.kitties[0].clone();
    DecisionContext {
        world: Arc::new(snapshot.fog_for(me.id, config.vision.radius)),
        me,
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
    let full = world.snapshot();
    let snapshot = full.fog_for(full.kitties[0].id, config.vision.radius);
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

#[test]
fn the_decision_is_clock_free_and_the_reserve_is_silent() {
    // Spec 058 FR-010 retired the clock cell (this test's predecessor
    // guarded the 0.3.0 served-clock seam; it went red at the v6 wall as
    // rule 6 demands and is replaced by its inverse). The artifact here
    // listens to BOTH dirt-reserve cells (offsets 107-108 — review
    // finding 2: the first cut listened to the vector's last cell, a
    // critter bit, and guarded nothing). Two claims, each with its own
    // teeth: (a) the listener's decision is IDENTICAL to an all-zero
    // network's — a reserve that goes live at ANY constant value moves
    // the growing output row off the tie-break and reds this (the
    // tick-equality alone cannot see a constant signal — found by the
    // fix's own mutate cycle); (b) nothing the policy reads varies with
    // the tick in a still world. Clock-freedom at the cell level stays
    // pinned by clock_and_range.rs; reserve zeroness at the encoding
    // level by dirt_reserve.rs — this is the policy-layer net over both.
    let rl = RlConfig::default();
    let input = observation_len(&rl.observation);
    let menu = ActionCodec::v2(&rl.observation).len() + MessageCodec::LEN;
    let header = ArtifactHeader {
        artifact_version: ARTIFACT_VERSION,
        observation_schema: OBSERVATION_SCHEMA_VERSION,
        action_schema: ACTION_SCHEMA_VERSION,
        mask_schema: MASK_SCHEMA_VERSION,
        layers: vec![[input, 1], [1, menu]],
        activation: "relu".into(),
    };
    let mut w1 = vec![0.0f32; input];
    w1[cloudkitty_rl::observe::offsets::SELF_DIRT_RESERVE] = 1.0;
    w1[cloudkitty_rl::observe::offsets::SELF_DIRT_RESERVE + 1] = 1.0;
    let w2: Vec<f32> = (0..menu).map(|i| i as f32).collect();
    let dir = std::env::temp_dir().join("ck-policy-selection");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("reserve-listener.ckpolicy");
    write_artifact(&path, &header, &[(w1, vec![0.0]), (w2, vec![0.0; menu])])
        .expect("the reserve-listener artifact writes");
    let behavior = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();

    // The all-zero twin: same shape, no listener. Identical decisions
    // prove the reserve contributed nothing at any constant value.
    let zero_path = dir.join("zero-listener.ckpolicy");
    write_artifact(
        &zero_path,
        &header,
        &[
            (vec![0.0f32; input], vec![0.0]),
            ((0..menu).map(|i| i as f32).collect(), vec![0.0; menu]),
        ],
    )
    .expect("the zero-listener artifact writes");
    let zero = PolicyBehavior::from_artifact_path(zero_path.to_str().unwrap(), &rl, false).unwrap();

    let horizon = rl.episode.horizon;
    let at = |tick: u64| behavior.decide_sync(&context_at_tick(1, tick));

    assert_eq!(
        at(0),
        zero.decide_sync(&context_at_tick(1, 0)),
        "the reserve listener decides exactly like an all-zero network: the reserve went live"
    );
    assert_eq!(
        at(0),
        at(horizon / 4),
        "a tick moved the decision through the policy"
    );
    assert_eq!(
        at(horizon / 4),
        at(horizon / 4 + horizon),
        "and it stays still across a full former horizon"
    );
}
