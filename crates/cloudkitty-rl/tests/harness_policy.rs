//! Harness policy scoring (spec 014 FR-013, T043): artifacts score in both
//! roster modes with the same scorecard shape, and fallback-taken decisions
//! are counted and reported — a run that needed the fallback must fail
//! rather than report the fallback's welfare as the policy's.

use std::path::PathBuf;
use std::sync::Arc;

use async_trait::async_trait;
use cloudkitty_core::action::Action;
use cloudkitty_core::behavior::{Behavior, BehaviorRegistry, DecisionContext};
use cloudkitty_core::Config;
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::harness::{run_one, EvalRequest, RosterMode};
use cloudkitty_rl::observe::observation_len;
use cloudkitty_rl::policy::{write_artifact, ArtifactHeader, ARTIFACT_VERSION};

fn fixture_artifact() -> PathBuf {
    let dir = std::env::temp_dir().join("ck-harness-policy");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("fixture.ckpolicy");
    let rl = RlConfig::default();
    let input = observation_len(&rl.observation);
    let header = ArtifactHeader {
        artifact_version: ARTIFACT_VERSION,
        observation_schema: 1,
        action_schema: 1,
        mask_schema: 1,
        layers: vec![[input, 8], [8, 40]],
        activation: "relu".into(),
    };
    let w1: Vec<f32> = (0..input * 8)
        .map(|i| ((i % 13) as f32 - 6.0) * 0.02)
        .collect();
    let w2: Vec<f32> = (0..8 * 40).map(|i| ((i % 9) as f32 - 4.0) * 0.05).collect();
    write_artifact(&path, &header, &[(w1, vec![0.0; 8]), (w2, vec![0.0; 40])]).unwrap();
    path
}

#[test]
fn both_roster_modes_score_with_the_same_scorecard_shape() {
    let path = fixture_artifact();
    let core = Config::default();
    let rl = RlConfig::default();
    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl).unwrap();
    registry.register("policy:fixture", Arc::new(behavior));

    let mut outcomes = Vec::new();
    for roster in [RosterMode::AllSubject, RosterMode::Mixed] {
        let outcome = run_one(&EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some("policy:fixture"),
            roster,
            seed: 1,
            ticks: 300,
        });
        assert_eq!(outcome.report.ticks, 300);
        assert_eq!(outcome.report.kitties.len(), core.kitties.len());
        assert_eq!(
            outcome.fallback_count, 0,
            "a healthy policy never takes the fallback ({roster:?})"
        );
        assert!(outcome.aggregates.team_welfare.is_finite());
        assert!(
            outcome.aggregates.least_happy_mean
                <= outcome
                    .report
                    .kitties
                    .iter()
                    .map(|k| k.mean_happiness)
                    .fold(f64::INFINITY, f64::min)
                    + 1e-9
        );
        outcomes.push(outcome);
    }
    // Same shape, different rosters: the two runs genuinely differ.
    assert_ne!(outcomes[0].report, outcomes[1].report);
}

/// A deliberately panicking advisor: the stand-in for a broken artifact
/// runtime (the v1 MLP itself cannot panic — selection is total — but the
/// accounting must catch anything that ever can).
struct ExplodingPolicy;

#[async_trait]
impl Behavior for ExplodingPolicy {
    async fn decide(&self, _ctx: &DecisionContext) -> Action {
        panic!("deliberately broken policy");
    }
}

#[test]
fn a_panicking_policy_is_counted_kitty_and_ticks_named() {
    let core = Config::default();
    let rl = RlConfig::default();
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("policy:broken", Arc::new(ExplodingPolicy));

    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let outcome = run_one(&EvalRequest {
        core: &core,
        rl: &rl,
        registry: &registry,
        subject: Some("policy:broken"),
        roster: RosterMode::Mixed,
        seed: 1,
        ticks: 25,
    });
    std::panic::set_hook(previous);

    // Every one of the policy kitty's decisions fell back — counted, with
    // the kitty and its first ticks named (FR-013's report clause). The
    // kitty-eval binary turns any nonzero count on a policy run into a
    // nonzero exit.
    assert_eq!(outcome.fallback_count, 25);
    assert_eq!(outcome.fallbacks.len(), 1);
    let record = &outcome.fallbacks[0];
    assert_eq!(record.kitty_id, core.kitties[0].id, "the policy kitty");
    assert_eq!(record.count, 25);
    assert!(!record.first_ticks.is_empty());
}

#[test]
fn the_kitty_eval_binary_scores_an_artifact_in_both_modes_and_exits_zero() {
    let path = fixture_artifact();
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
        .args([
            "--artifact",
            path.to_str().unwrap(),
            "--seeds",
            "1",
            "--ticks",
            "60",
        ])
        .output()
        .expect("kitty-eval runs");
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        output.status.success(),
        "exit: {:?}\n{stdout}",
        output.status
    );
    assert!(stdout.contains("[AllSubject]"), "{stdout}");
    assert!(stdout.contains("[Mixed]"), "{stdout}");
    assert!(stdout.contains("fallbacks 0"), "{stdout}");
}

#[test]
fn the_kitty_eval_binary_refuses_a_corrupt_artifact() {
    let dir = std::env::temp_dir().join("ck-harness-policy");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("corrupt.ckpolicy");
    std::fs::write(&path, b"definitely not a policy").unwrap();
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
        .args(["--artifact", path.to_str().unwrap()])
        .output()
        .expect("kitty-eval runs");
    assert_eq!(output.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("artifact validation failed"), "{stderr}");
}
