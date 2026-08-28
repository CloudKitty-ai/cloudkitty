//! Golden-file guard on the evaluation run JSON wire shape.
//!
//! **Why this exists** (BACKLOG "Refactoring targets" runners-up, the
//! RosterMode-fold definition-of-done ask, 2026-07-27): longitudinal
//! comparability of evaluation reports is the one thing the eval-suite
//! doctrine cannot lose — results recorded against past runs must stay
//! readable against future ones. This golden pins the serialized shape of
//! `RunOutcome` (in every `RosterMode`, so all three wire tags are
//! covered) and `PairedDelta`. It is the agreed exception to the standing
//! goldens-deferred ruling (spec 018 clarifications), landed *before* the
//! RosterMode fold so that refactor's wire-shape care is mechanically
//! checked rather than eyeballed.
//!
//! **On failure**: an *unintentional* diff is a wire-shape regression —
//! fix the code, not the golden. An *intentional* wire change regenerates
//! the golden in the same PR with the justification alongside
//! (`UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test run_json_golden`)
//! and must reckon with every stored report the change orphans.
//!
//! The runs are tiny (default world, 120 ticks) — this guards the
//! *shape*, not the values; the values being deterministic is what makes
//! byte-comparison usable as the instrument.
//!
//! Regenerated at spec 041's engine-sibling commit (2026-08-28): the
//! availability legality changes what scripted kitties do, so the runs'
//! deterministic welfare VALUES moved (shape untouched — verified by
//! diff). Stored pre-041 reports remain readable (the shape is the
//! contract); their numeric comparability against post-041 runs was
//! already surrendered by the arc's design — SC-007 re-baselines before
//! any bar, and eval-suite v2 rides the wall.

use std::path::PathBuf;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::harness::{pair_runs, run_one, EvalRequest, RosterMode};
use serde::Serialize;

fn golden_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/goldens/run-json.golden.json")
}

#[derive(Serialize)]
struct GoldenDoc {
    all_subject: cloudkitty_rl::harness::RunOutcome,
    mixed: cloudkitty_rl::harness::RunOutcome,
    from_config: cloudkitty_rl::harness::RunOutcome,
    paired: Vec<cloudkitty_rl::harness::PairedDelta>,
}

#[test]
fn run_json_wire_shape_matches_the_golden() {
    let core = Config::default();
    let rl = RlConfig::default();
    let registry = BehaviorRegistry::with_builtins();
    let base = EvalRequest {
        core: &core,
        rl: &rl,
        registry: &registry,
        subject: Some("needs_driven"),
        roster: RosterMode::AllSubject,
        seed: 7,
        ticks: 120,
    };

    let all_subject = run_one(&base);
    let mixed = run_one(&EvalRequest {
        roster: RosterMode::Mixed,
        ..base.clone()
    });
    let from_config = run_one(&EvalRequest {
        subject: None,
        roster: RosterMode::FromConfig,
        ..base.clone()
    });
    let paired = pair_runs(
        std::slice::from_ref(&all_subject),
        std::slice::from_ref(&all_subject),
    );

    let doc = GoldenDoc {
        all_subject,
        mixed,
        from_config,
        paired,
    };
    let rendered = serde_json::to_string_pretty(&doc).expect("run JSON serializes");

    let path = golden_path();
    if std::env::var_os("UPDATE_GOLDENS").is_some() {
        std::fs::write(&path, format!("{rendered}\n")).expect("write golden");
        eprintln!("golden regenerated at {}", path.display());
        return;
    }
    let golden = std::fs::read_to_string(&path)
        .unwrap_or_else(|e| panic!("missing golden {} ({e}); see module docs", path.display()));
    assert_eq!(
        format!("{rendered}\n"),
        golden,
        "run JSON wire shape diverged from the golden — unintentional: fix \
         the code; intentional: regenerate with UPDATE_GOLDENS=1 and justify \
         the change (and its effect on stored reports) in the same PR"
    );
}
