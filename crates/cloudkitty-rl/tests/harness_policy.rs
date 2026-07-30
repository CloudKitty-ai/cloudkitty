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
use cloudkitty_rl::test_support;

fn fixture_artifact() -> PathBuf {
    test_support::fixture_artifact("ck-harness-policy", "fixture", 8, 3)
}

#[test]
fn both_roster_modes_score_with_the_same_scorecard_shape() {
    let path = fixture_artifact();
    let core = Config::default();
    let rl = RlConfig::default();
    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
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

// --sample (issue #70): sampled artifact seating through the real CLI.
// The fixture's output layer is flooded with 0.0, so its logits are
// constant — greedy degenerates into a first-legal-action bot while
// sampling is uniform over legal actions (the Arm 0 shape). The two modes
// must produce different runs, each labeled, and sampled runs must be
// exactly reproducible (the in-run determinism self-check exits 3 on any
// disagreement, so exit 0 also certifies requirement 2).
#[test]
fn the_sample_flag_routes_labels_and_stays_deterministic() {
    let dir = std::env::temp_dir().join("ck-harness-policy-sample");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("uniform.ckpolicy");
    cloudkitty_rl::test_support::write_fixture_artifact_with_output(&path, 8, 0, Some(0.0));

    let run = |label: &str, sample: bool| {
        let json = dir.join(format!("{label}.json"));
        let mut args = vec![
            "--artifact",
            path.to_str().unwrap(),
            "--seeds",
            "1",
            "--ticks",
            "60",
            "--json",
        ];
        let json_arg = json.to_str().unwrap().to_string();
        args.push(&json_arg);
        if sample {
            args.push("--sample");
        }
        let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
            .args(&args)
            .output()
            .expect("kitty-eval runs");
        assert!(
            output.status.success(),
            "{label}: exit {:?}\n{}",
            output.status,
            String::from_utf8_lossy(&output.stderr)
        );
        (
            String::from_utf8_lossy(&output.stdout).into_owned(),
            std::fs::read_to_string(&json).unwrap(),
        )
    };

    let (sampled_stdout, sampled_json) = run("sampled", true);
    let (_, sampled_again) = run("sampled-again", true);
    let (greedy_stdout, greedy_json) = run("greedy", false);

    // Requirement 4: both records state their distribution, everywhere a
    // certification line could be quoted from.
    assert!(
        sampled_stdout.contains("sampled selection"),
        "{sampled_stdout}"
    );
    assert!(
        greedy_stdout.contains("greedy selection"),
        "{greedy_stdout}"
    );
    assert!(sampled_json.contains("\"selection\": \"sampled\""));
    assert!(greedy_json.contains("\"selection\": \"greedy\""));

    // Requirement 2: a --sample run with fixed --seeds is exactly
    // reproducible.
    assert_eq!(
        sampled_json, sampled_again,
        "sampled runs reproduce byte-identically"
    );

    // Requirement 1: the flag genuinely routes — constant logits under
    // greedy and under sampling are different policies.
    assert_ne!(
        sampled_json.replace("\"sampled\"", "\"greedy\""),
        greedy_json,
        "sampled and greedy runs of a constant-logit artifact must differ"
    );
}

// Requirement 5 (issue #70): --sample without --artifact is a usage
// error, never silently ignored.
#[test]
fn the_sample_flag_without_an_artifact_is_a_usage_error() {
    for args in [
        vec!["--sample", "--brain", "needs_driven"],
        vec!["--sample"],
    ] {
        let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
            .args(&args)
            .output()
            .expect("kitty-eval runs");
        assert_eq!(output.status.code(), Some(1), "{args:?}");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(
            stderr.contains("--sample applies to artifact seating only"),
            "{args:?}: {stderr}"
        );
    }
}

// The other silent-loss route (issue #70 requirement 5): a flag sitting
// where a value belongs must be a usage error, or `--json --sample`
// swallows the sampling request and certifies a greedy run with exit 0.
#[test]
fn a_flag_where_a_value_belongs_is_a_usage_error() {
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
        .args([
            "--artifact",
            "p.ckpolicy",
            "--seeds",
            "1",
            "--json",
            "--sample",
        ])
        .output()
        .expect("kitty-eval runs");
    assert_eq!(output.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("--json requires a value, got flag '--sample'"),
        "{stderr}"
    );
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
