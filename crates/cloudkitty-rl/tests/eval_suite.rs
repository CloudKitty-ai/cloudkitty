//! Guarding tests for the held-out evaluation suite (spec 017, Article VI).
//! The spec-test → test-name map lives in specs/017-eval-suite/quickstart.md.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::Config;
use cloudkitty_rl::config::load_configs_from_path;
use cloudkitty_rl::harness::{run_many, run_one, EvalRequest, RosterMode, RunOutcome};
use cloudkitty_rl::suite::{
    all_scripted_config, evaluate_verdict, load_suite, score_suite, sha256_hex, CellOutcome,
    ExamOutcome, KittyDifferential, SignTestMode, SuiteSubject, VerdictConstants,
    CANDIDATE_BEHAVIOR,
};
use cloudkitty_rl::welfare::{KittyWelfare, WelfareReport};

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .unwrap()
}

fn evals_v1() -> PathBuf {
    repo_root().join("evals/v1")
}

const V1_EXAM_FILES: [&str; 6] = [
    "scale.toml",
    "scarcity.toml",
    "heterogeneity.toml",
    "mixed-roster-guest.toml",
    "mixed-roster-half.toml",
    "mixed-roster-host.toml",
];

/// A short-tick copy of the real v1 suite: same worlds, same structure,
/// `[rl.eval]` shrunk so integration tests stay fast. Hashes are computed
/// over the rewritten bytes, so the scratch suite is internally frozen.
fn build_scratch_suite(name: &str, ticks: u64, seeds: &str) -> PathBuf {
    let dir = std::env::temp_dir().join("ck-eval-suite").join(name);
    std::fs::create_dir_all(&dir).unwrap();
    // Scratch seed sets are tiny, so the fair-coin sign-test threshold is
    // honestly unattainable (n + 1): no n-seed count can clear a 0.1% tail
    // below n = 10. Trigger-level sign-test behavior is unit-tested on
    // synthetic outcomes in suite.rs.
    let k = seeds.matches(',').count() + 2;
    let mut hashes = BTreeMap::new();
    for file in V1_EXAM_FILES {
        let text = std::fs::read_to_string(evals_v1().join(file)).unwrap();
        let text = text
            .replace("ticks = 20000", &format!("ticks = {ticks}"))
            .replace("seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]", seeds);
        hashes.insert(file, sha256_hex(text.as_bytes()));
        std::fs::write(dir.join(file), text).unwrap();
    }
    let manifest = format!(
        r#"version = "scratch-{name}"

[verdict]
differential_tolerance = 0.0
tail_probability = 0.01
sign_test = "warn"
sign_test_tail = 0.001
sign_test_k = {k}

[verdict.least_happy_threshold]
guest = 11
half = 10
host = 6

[[exam]]
name = "scale"
kind = "standard"
config = "scale.toml"
sha256 = "{}"

[[exam]]
name = "scarcity"
kind = "standard"
config = "scarcity.toml"
sha256 = "{}"

[[exam]]
name = "heterogeneity"
kind = "standard"
config = "heterogeneity.toml"
sha256 = "{}"

[[exam]]
name = "mixed-roster"
kind = "mixed-roster"

[[exam.cell]]
name = "guest"
config = "mixed-roster-guest.toml"
sha256 = "{}"

[[exam.cell]]
name = "half"
config = "mixed-roster-half.toml"
sha256 = "{}"

[[exam.cell]]
name = "host"
config = "mixed-roster-host.toml"
sha256 = "{}"
"#,
        hashes["scale.toml"],
        hashes["scarcity.toml"],
        hashes["heterogeneity.toml"],
        hashes["mixed-roster-guest.toml"],
        hashes["mixed-roster-half.toml"],
        hashes["mixed-roster-host.toml"],
    );
    std::fs::write(dir.join("manifest.toml"), manifest).unwrap();
    dir
}

/// A registry with the given built-in aliased as the candidate seat
/// (research.md R4 — the exam machinery needs no trained artifact).
fn registry_with_candidate(brain: &str) -> BehaviorRegistry {
    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = registry.get(brain).expect("built-in exists");
    registry.register(CANDIDATE_BEHAVIOR, behavior);
    registry
}

// Spec guarding test 1 (SC-001): zero aggregation drift.
#[test]
fn a_suite_run_reproduces_each_exams_standalone_numbers() {
    let dir = build_scratch_suite("equals-parts", 150, "seeds = [1, 2]");
    let suite = load_suite(&dir).unwrap();
    let registry = registry_with_candidate("needs_driven");
    let subject = SuiteSubject {
        registry: &registry,
        name: "needs_driven",
        is_policy: false,
        selection: None,
    };
    let report = score_suite(&suite, &subject, false).unwrap();

    // Standalone: the scarcity exam scored exactly as a single-config run.
    let (core, rl) = load_configs_from_path(dir.join("scarcity.toml").to_str().unwrap()).unwrap();
    let standalone: Vec<RunOutcome> = run_many(
        &EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            seed: 0,
            ticks: rl.eval.ticks,
        },
        &rl.eval.seeds,
    );
    let scarcity = report
        .exams
        .iter()
        .find_map(|exam| match exam {
            ExamOutcome::Standard(e) if e.name == "scarcity" => Some(e),
            _ => None,
        })
        .expect("scarcity exam scored");
    assert_eq!(
        scarcity.runs, standalone,
        "suite numbers equal standalone numbers on the same seeds"
    );
}

// Spec guarding test 3 (FR-004): loud validation, nothing scored.
#[test]
fn an_invalid_exam_fails_the_suite_before_any_scoring() {
    let dir = build_scratch_suite("invalid", 150, "seeds = [1, 2]");
    // Invalidate one exam *and* recompute its hash, so validation (not the
    // freeze guard) is what trips.
    let path = dir.join("scarcity.toml");
    let broken = std::fs::read_to_string(&path)
        .unwrap()
        .replace("width = 32", "width = 0");
    std::fs::write(&path, &broken).unwrap();
    let manifest_path = dir.join("manifest.toml");
    let manifest = std::fs::read_to_string(&manifest_path).unwrap();
    let old_line = manifest
        .lines()
        .filter(|l| l.starts_with("sha256"))
        .nth(1)
        .unwrap()
        .to_string();
    let manifest = manifest.replace(
        &old_line,
        &format!("sha256 = \"{}\"", sha256_hex(broken.as_bytes())),
    );
    std::fs::write(&manifest_path, manifest).unwrap();

    let Err(err) = load_suite(&dir) else {
        panic!("an invalid exam config must fail the load");
    };
    let message = err.to_string();
    assert!(
        message.contains("scarcity.toml"),
        "names the file: {message}"
    );
    assert!(message.contains("width"), "names the field: {message}");

    // The wrong-hash variant names the file too.
    let dir = build_scratch_suite("wrong-hash", 150, "seeds = [1, 2]");
    std::fs::write(
        dir.join("scale.toml"),
        std::fs::read_to_string(dir.join("scale.toml")).unwrap() + "# poke\n",
    )
    .unwrap();
    let Err(err) = load_suite(&dir) else {
        panic!("a hash mismatch must fail the load");
    };
    assert!(
        err.to_string().contains("scale.toml"),
        "names the file: {err}"
    );
}

// Spec guarding test 4 (SC-002): byte-identical JSON.
#[test]
fn two_suite_runs_produce_identical_json() {
    let dir = build_scratch_suite("repro", 120, "seeds = [1, 2]");
    let suite = load_suite(&dir).unwrap();
    let registry = registry_with_candidate("needs_driven");
    let subject = SuiteSubject {
        registry: &registry,
        name: "needs_driven",
        is_policy: false,
        selection: None,
    };
    let a = serde_json::to_string_pretty(&score_suite(&suite, &subject, false).unwrap()).unwrap();
    let b = serde_json::to_string_pretty(&score_suite(&suite, &subject, false).unwrap()).unwrap();
    assert_eq!(a, b, "two suite runs serialize byte-identically");
}

// Spec guarding test 5 (FR-006): every v1 exam is a lawful world. The
// per-tick invariant assertions run inside the engine; a completed run is
// the proof. Expected numbers ≈ the measured baselines recorded in
// contracts/exam-configs.md.
#[test]
fn every_v1_exam_sustains_an_invariant_asserted_run() {
    let registry = BehaviorRegistry::with_builtins();
    for file in V1_EXAM_FILES {
        let path = evals_v1().join(file);
        let (core, rl) = load_configs_from_path(path.to_str().unwrap())
            .unwrap_or_else(|e| panic!("{file} must load and validate: {e}"));
        // Cells carry candidate seats; normalize them the same way the
        // all-scripted baseline does, so built-ins drive every seat.
        let core = all_scripted_config(&core);
        let outcome = run_one(&EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: None,
            roster: RosterMode::AllSubject,
            seed: 1,
            ticks: 2_000,
        });
        assert_eq!(
            outcome.fallback_count, 0,
            "{file}: built-ins never fall back"
        );
        assert!(
            outcome.aggregates.least_happy_mean > 0.0,
            "{file}: the happiness floor holds"
        );
    }
}

// Spec FR-007 + SC-005: held-out means distinct — by bytes and by axis.
#[test]
fn no_exam_equals_a_training_or_certification_config() {
    let root = repo_root();
    let others = [
        "cloudkitty.toml",
        "training.toml",
        "cloudkitty16.toml",
        "cloudkitty48.toml",
    ];
    for file in V1_EXAM_FILES {
        let exam_bytes = std::fs::read(evals_v1().join(file)).unwrap();
        for other in others {
            let other_bytes = std::fs::read(root.join(other)).unwrap();
            assert_ne!(
                exam_bytes, other_bytes,
                "{file} must not byte-equal {other}"
            );
        }
    }

    // Axis assertions, parsed. Rate spread = max/min effective per-need
    // rise rate across the roster.
    fn spread(core: &Config) -> f32 {
        let mut min = f32::INFINITY;
        let mut max = 0.0f32;
        for kitty in &core.kitties {
            for kind in cloudkitty_core::needs::NeedKind::ALL {
                let rate = core.need_rate_for(kitty.id, kind);
                min = min.min(rate);
                max = max.max(rate);
            }
        }
        max / min
    }
    let load = |path: PathBuf| load_configs_from_path(path.to_str().unwrap()).unwrap().0;
    let bar = load(root.join("cloudkitty.toml"));
    let gym = load(root.join("training.toml"));
    let scale = load(evals_v1().join("scale.toml"));
    let scarcity = load(evals_v1().join("scarcity.toml"));
    let heterogeneity = load(evals_v1().join("heterogeneity.toml"));
    let mixed = load(evals_v1().join("mixed-roster-guest.toml"));

    let tiles = |c: &Config| c.world.width * c.world.height;
    assert!(
        tiles(&scale) >= 2 * tiles(&bar),
        "scale: >= 2x the bar's tiles"
    );
    assert!(
        scale.kitties.len() > gym.kitties.len(),
        "scale: roster larger than training's"
    );

    for kind in cloudkitty_core::element::ElementType::ALL {
        assert_eq!(
            scarcity.elements.rule(kind).min,
            cloudkitty_core::config::ElementsConfig::hard_min(kind),
            "scarcity: {kind:?} minimum sits at the validation floor"
        );
    }

    assert!(
        spread(&heterogeneity) > spread(&bar) && spread(&heterogeneity) > spread(&gym),
        "heterogeneity: trait spread exceeds both other worlds'"
    );

    let geometry = |c: &Config| (c.world.width, c.world.height, c.kitties.len());
    assert_ne!(
        geometry(&mixed),
        geometry(&bar),
        "mixed-roster: not the bar's shape"
    );
    assert_ne!(
        geometry(&mixed),
        geometry(&gym),
        "mixed-roster: not the gym's shape"
    );
}

// Spec guarding test 7a (SC-007): the machinery needs no trained artifact.
#[test]
fn a_builtin_candidate_exercises_cells_differentials_and_verdict() {
    let dir = build_scratch_suite("playful-candidate", 150, "seeds = [1, 2]");
    let suite = load_suite(&dir).unwrap();
    let registry = registry_with_candidate("playful");
    let subject = SuiteSubject {
        registry: &registry,
        name: "playful",
        is_policy: false,
        selection: None,
    };
    let report = score_suite(&suite, &subject, false).unwrap();
    let mixed = report
        .exams
        .iter()
        .find_map(|exam| match exam {
            ExamOutcome::MixedRoster(e) => Some(e),
            _ => None,
        })
        .expect("the mixed-roster exam scored");
    assert_eq!(mixed.cells.len(), 3, "guest, half, host");
    for cell in &mixed.cells {
        assert!(
            !cell.differentials.is_empty(),
            "{}: scripted differentials",
            cell.name
        );
        assert_eq!(
            cell.duet_shares.len(),
            6,
            "{}: every kitty's duet share",
            cell.name
        );
        assert_eq!(cell.runs.len(), cell.baseline_runs.len());
    }
    assert_eq!(
        mixed.verdict.checks.len(),
        12,
        "four checks per cell — a verdict was rendered"
    );
    assert_eq!(
        mixed.verdict.sign_test_mode,
        SignTestMode::Warn,
        "the effective mode is stamped (FR-015)"
    );
}

// Spec guarding test 7b (FR-010): the exploitation signature, named.
#[test]
fn a_negative_host_differential_renders_the_exploitation_signature() {
    let run = |welfare: f64, least_happy: &str| RunOutcome {
        seed: 1,
        ticks: 10,
        roster: RosterMode::AllSubject,
        report: WelfareReport {
            ticks: 10,
            kitties: vec![
                KittyWelfare {
                    kitty_id: 1,
                    name: "Miso".into(),
                    mean_happiness: if least_happy == "Miso" { 70.0 } else { 90.0 },
                    max_low_streak: 0,
                    low_share: 0.0,
                    floor_touches: 0,
                },
                KittyWelfare {
                    kitty_id: 2,
                    name: "Biscuit".into(),
                    mean_happiness: if least_happy == "Biscuit" { 70.0 } else { 90.0 },
                    max_low_streak: 0,
                    low_share: 0.0,
                    floor_touches: 0,
                },
            ],
            max_distress_age: 0,
            pinned: Vec::new(),
        },
        aggregates: cloudkitty_rl::harness::WelfareAggregates {
            team_welfare: welfare,
            plain_mean: welfare,
            least_happy_mean: 70.0,
        },
        fallback_count: 0,
        fallbacks: Vec::new(),
    };
    // Healthy team aggregate (cell 0.91 vs baseline 0.90), scripted Biscuit
    // worse off by 3.2 points and negative in every paired seed: the
    // exploitation signature (FR-015: the signature IS the sign-test
    // trigger).
    let cell = CellOutcome {
        name: "host".into(),
        config_sha256: "0".repeat(64),
        runs: vec![run(0.91, "Biscuit")],
        baseline_runs: vec![run(0.90, "Miso")],
        paired: Vec::new(),
        differentials: vec![KittyDifferential {
            kitty_id: 2,
            name: "Biscuit".into(),
            cell_mean: 82.3,
            baseline_mean: 85.5,
            differential: -3.2,
            negative_seeds: 10,
        }],
        least_happy_out_group_seeds: 1,
        baseline_least_happy_out_group_seeds: 0,
        duet_shares: Vec::new(),
    };
    let constants = VerdictConstants {
        differential_tolerance: 0.0,
        tail_probability: 0.01,
        least_happy_threshold: [("host".to_string(), 6u32)].into_iter().collect(),
        sign_test: SignTestMode::Warn,
        sign_test_tail: 0.001,
        sign_test_k: 10,
    };
    let verdict = evaluate_verdict(&[cell], &constants, SignTestMode::Warn);
    assert!(!verdict.passed, "the exam fails (exit 4 in the binary)");
    let signature = &verdict.exploitation_signatures[0];
    assert_eq!(signature.cell, "host", "names the cell");
    assert_eq!(signature.kitty, "Biscuit", "names the kitty");
    assert!(
        (signature.differential - -3.2).abs() < 1e-12,
        "names the differential"
    );
    assert_eq!(signature.negative_seeds, 10, "names the seed count");
    assert!(
        signature.cell_aggregate_healthy,
        "healthy aggregate (0.91 vs 0.90): labeled as the masking case"
    );
}

// Spec guarding test 8 (FR-011): the artifact is bound at invocation; the
// frozen files never change. Plus the outside-suite clause: an unbound
// candidate fails behavior-name validation loudly.
#[test]
fn two_subjects_share_the_frozen_exam_without_touching_it() {
    let real_hashes: Vec<String> = V1_EXAM_FILES
        .iter()
        .map(|f| sha256_hex(&std::fs::read(evals_v1().join(f)).unwrap()))
        .collect();

    let dir = build_scratch_suite("two-subjects", 100, "seeds = [1]");
    let scratch_hash = |dir: &Path| -> Vec<String> {
        V1_EXAM_FILES
            .iter()
            .map(|f| sha256_hex(&std::fs::read(dir.join(f)).unwrap()))
            .collect()
    };
    let before = scratch_hash(&dir);
    let suite = load_suite(&dir).unwrap();
    for brain in ["needs_driven", "playful"] {
        let registry = registry_with_candidate(brain);
        let subject = SuiteSubject {
            registry: &registry,
            name: brain,
            is_policy: false,
            selection: None,
        };
        score_suite(&suite, &subject, false).unwrap();
        assert_eq!(scratch_hash(&dir), before, "scoring {brain} wrote nothing");
    }

    let after: Vec<String> = V1_EXAM_FILES
        .iter()
        .map(|f| sha256_hex(&std::fs::read(evals_v1().join(f)).unwrap()))
        .collect();
    assert_eq!(real_hashes, after, "the committed exam files are untouched");

    // Outside a suite run, the placeholder is an ordinary policy name and
    // an unbound registry rejects it, naming the kitty and the behavior.
    let (core, _) =
        load_configs_from_path(evals_v1().join("mixed-roster-guest.toml").to_str().unwrap())
            .unwrap();
    let unbound = BehaviorRegistry::with_builtins();
    let Err(err) = core.validate_behavior_names(&unbound.names()) else {
        panic!("an unbound candidate must fail behavior-name validation");
    };
    let message = err.to_string();
    assert!(message.contains("Miso"), "names the kitty: {message}");
    assert!(
        message.contains("policy:candidate"),
        "names the behavior: {message}"
    );
}

// Research.md R3: the three cells can never drift apart.
#[test]
fn cell_configs_differ_only_in_behavior() {
    let strip_behaviors = |file: &str| -> toml::Value {
        let text = std::fs::read_to_string(evals_v1().join(file)).unwrap();
        let mut value: toml::Value = toml::from_str(&text).unwrap();
        for kitty in value
            .get_mut("kitty")
            .and_then(|k| k.as_array_mut())
            .unwrap()
        {
            kitty.as_table_mut().unwrap().remove("behavior");
        }
        value
    };
    let guest = strip_behaviors("mixed-roster-guest.toml");
    let half = strip_behaviors("mixed-roster-half.toml");
    let host = strip_behaviors("mixed-roster-host.toml");
    assert_eq!(guest, half, "guest and half agree on everything but seats");
    assert_eq!(guest, host, "guest and host agree on everything but seats");

    // And the seat maps are exactly the contract's (contracts/exam-configs.md).
    let seats = |file: &str| -> Vec<String> {
        let (core, _) = load_configs_from_path(evals_v1().join(file).to_str().unwrap()).unwrap();
        core.kitties.iter().map(|k| k.behavior.clone()).collect()
    };
    let c = CANDIDATE_BEHAVIOR;
    assert_eq!(
        seats("mixed-roster-guest.toml"),
        vec![
            c,
            "playful",
            "needs_driven",
            "needs_driven",
            "needs_driven",
            "needs_driven"
        ]
    );
    assert_eq!(
        seats("mixed-roster-half.toml"),
        vec![c, "playful", c, "needs_driven", c, "needs_driven"]
    );
    assert_eq!(
        seats("mixed-roster-host.toml"),
        vec![c, "playful", c, c, c, c]
    );
}

/// P(X >= k) for X ~ Binomial(n, p), exact. The one implementation both
/// threshold-derivation guards recompute against — two tails would let a
/// boundary fix in one silently leave the other validating different math.
fn binomial_tail(n: u32, p: f64, k: u32) -> f64 {
    let mut tail = 0.0;
    for i in k..=n {
        let mut c = 1.0;
        for j in 0..i {
            c = c * (n - j) as f64 / (j + 1) as f64;
        }
        tail += c * p.powi(i as i32) * (1.0 - p).powi((n - i) as i32);
    }
    tail
}

// Research.md R7: thresholds stay derivable, never folklore. Every input is
// read from the manifest and the cell configs.
#[test]
fn least_happy_thresholds_match_the_binomial_rule() {
    let suite = load_suite(&evals_v1()).unwrap();
    let cells = suite
        .exams
        .iter()
        .find_map(|exam| match exam {
            cloudkitty_rl::suite::LoadedExam::MixedRoster { cells, .. } => Some(cells),
            _ => None,
        })
        .unwrap();
    for cell in cells {
        let n = cell.rl.eval.seeds.len() as u32;
        let scripted = cell
            .core
            .kitties
            .iter()
            .filter(|k| k.behavior != CANDIDATE_BEHAVIOR)
            .count();
        let share = scripted as f64 / cell.core.kitties.len() as f64;
        let derived = (0..=n + 1)
            .find(|&k| k > n || binomial_tail(n, share, k) <= suite.verdict.tail_probability)
            .unwrap();
        assert_eq!(
            suite.verdict.least_happy_threshold[&cell.name], derived,
            "cell {}: threshold follows the binomial rule",
            cell.name
        );
    }
}

// Spec guarding test 2 (SC-003, FR-012): frozen means frozen, forever, for
// every landed suite version in the repository.
#[test]
fn a_landed_exam_file_cannot_change_without_failing_ci() {
    let evals = repo_root().join("evals");
    let mut versions = 0;
    for entry in std::fs::read_dir(&evals).unwrap() {
        let dir = entry.unwrap().path();
        let manifest_path = dir.join("manifest.toml");
        if !manifest_path.is_file() {
            continue;
        }
        versions += 1;
        let manifest: toml::Value =
            toml::from_str(&std::fs::read_to_string(&manifest_path).unwrap()).unwrap();
        let check = |config: &str, recorded: &str| {
            let bytes = std::fs::read(dir.join(config))
                .unwrap_or_else(|e| panic!("{}: {config} missing: {e}", dir.display()));
            assert_eq!(
                sha256_hex(&bytes),
                recorded,
                "{}/{config} changed after landing — a frozen exam never changes; \
                 land a new suite version alongside instead (spec 017 FR-012)",
                dir.display()
            );
        };
        for exam in manifest.get("exam").and_then(|e| e.as_array()).unwrap() {
            if let (Some(config), Some(sha)) = (
                exam.get("config").and_then(|v| v.as_str()),
                exam.get("sha256").and_then(|v| v.as_str()),
            ) {
                check(config, sha);
            }
            if let Some(cells) = exam.get("cell").and_then(|c| c.as_array()) {
                for cell in cells {
                    check(
                        cell.get("config").and_then(|v| v.as_str()).unwrap(),
                        cell.get("sha256").and_then(|v| v.as_str()).unwrap(),
                    );
                }
            }
        }
    }
    assert!(
        versions >= 1,
        "at least eval-suite-v1 is landed and guarded"
    );
}

// FR-015 / R12: the sign-test threshold stays derivable from the fair-coin
// rule — every input read from the manifest and the exam configs. The
// suite-level k must be valid for EVERY cell of EVERY mixed exam: a single
// constant applied to divergent seed counts would be mis-calibrated for
// some cells while a first-cell-only guard stayed green (second review,
// finding 6), so every cell's seed count must derive the same k.
#[test]
fn sign_test_k_matches_the_fair_coin_rule() {
    let suite = load_suite(&evals_v1()).unwrap();
    let mut cells_checked = 0;
    for exam in &suite.exams {
        let cloudkitty_rl::suite::LoadedExam::MixedRoster { name, cells } = exam else {
            continue;
        };
        for cell in cells {
            cells_checked += 1;
            let n = cell.rl.eval.seeds.len() as u32;
            let derived = (0..=n + 1)
                .find(|&k| k > n || binomial_tail(n, 0.5, k) <= suite.verdict.sign_test_tail)
                .unwrap();
            assert_eq!(
                suite.verdict.sign_test_k, derived,
                "exam {name}, cell {}: the suite-level sign_test_k must follow the \
                 fair-coin rule for this cell's n = {n} seeds — a divergent seed \
                 count needs per-exam constants, not a silently mis-calibrated k",
                cell.name
            );
        }
    }
    assert!(cells_checked > 0, "the guard checked at least one cell");
}

// Review finding 1: an artifact path literally named `candidate` collides
// with the policy:candidate alias; the binary must degrade gracefully,
// never panic on the duplicate registration.
#[test]
fn an_artifact_named_candidate_does_not_panic_the_suite() {
    let dir = std::env::temp_dir()
        .join("ck-eval-suite")
        .join("candidate-artifact");
    std::fs::create_dir_all(&dir).unwrap();
    cloudkitty_rl::test_support::write_fixture_artifact(&dir.join("candidate"), 8, 7);
    let scratch = build_scratch_suite("candidate-collision", 30, "seeds = [1]");
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
        .current_dir(&dir)
        .args([
            "--suite",
            scratch.to_str().unwrap(),
            "--artifact",
            "candidate",
        ])
        .output()
        .expect("binary runs");
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        !stderr.contains("registered twice"),
        "no duplicate-registration panic: {stderr}"
    );
    let code = output
        .status
        .code()
        .expect("clean exit, not a signal/abort");
    assert!(
        [0, 2, 4].contains(&code),
        "a lawful suite outcome (0/2/4), got {code}; stderr: {stderr}"
    );
}

// --sample in suite mode (issue #70 requirement 4): the selection mode is
// a subject property, and the suite record — human header and JSON — must
// state which distribution was evaluated.
#[test]
fn a_sampled_suite_run_stamps_its_selection_mode() {
    let artifact = cloudkitty_rl::test_support::fixture_artifact_with_output(
        "ck-eval-suite-sampled",
        "uniform",
        8,
        0,
        Some(0.0),
    );
    let dir = artifact.parent().unwrap().to_path_buf();
    let json = dir.join("report.json");
    let scratch = build_scratch_suite("sampled-subject", 30, "seeds = [1]");
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_kitty-eval"))
        .args([
            "--suite",
            scratch.to_str().unwrap(),
            "--artifact",
            artifact.to_str().unwrap(),
            "--sample",
            "--json",
            json.to_str().unwrap(),
        ])
        .output()
        .expect("binary runs");
    let stderr = String::from_utf8_lossy(&output.stderr);
    let code = output
        .status
        .code()
        .expect("clean exit, not a signal/abort");
    assert!(
        [0, 2, 4].contains(&code),
        "a lawful suite outcome (0/2/4), got {code}; stderr: {stderr}"
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("(sampled selection)"), "{stdout}");
    let report = std::fs::read_to_string(&json).unwrap();
    assert!(
        report.contains("\"selection\": \"sampled\""),
        "JSON lacks the selection stamp"
    );
}

/// The one sample run every share-guard test renders: a single simulation
/// pins the tests to literally the same run, so FR-009's "both modes
/// render the same run" property cannot be un-pinned by fixture drift.
fn share_guard_sample_run() -> &'static RunOutcome {
    static RUN: std::sync::OnceLock<RunOutcome> = std::sync::OnceLock::new();
    RUN.get_or_init(|| {
        let core = Config::default();
        let rl = cloudkitty_rl::config::RlConfig::default();
        let registry = BehaviorRegistry::with_builtins();
        run_one(&EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            seed: 7,
            ticks: 120,
        })
    })
}

/// Spec 018 FR-009 share-guard: both CLI modes render a run through
/// `cli_support::print_run_panel`, and the two modes' outputs differ by
/// exactly the documented bounds-block option — nothing else.
#[test]
fn share_guard_panel_modes_differ_only_by_the_bounds_block() {
    let run = share_guard_sample_run();

    let mut suite_bytes = Vec::new();
    cloudkitty_rl::cli_support::print_run_panel(&mut suite_bytes, run, false).unwrap();
    let mut cert_bytes = Vec::new();
    cloudkitty_rl::cli_support::print_run_panel(&mut cert_bytes, run, true).unwrap();
    let suite_text = String::from_utf8(suite_bytes).unwrap();
    let cert_text = String::from_utf8(cert_bytes).unwrap();

    let suite_lines: Vec<&str> = suite_text.lines().collect();
    let cert_lines: Vec<&str> = cert_text.lines().collect();
    let distress = suite_lines
        .iter()
        .position(|l| l.starts_with("  max distress age"))
        .expect("panel always renders the distress line");
    // Identical up to and including the distress line...
    assert_eq!(cert_lines[..=distress], suite_lines[..=distress]);
    // ...then certification mode inserts only bounds lines...
    let extra = cert_lines.len() - suite_lines.len();
    assert!(extra >= 1, "bounds block must add at least one line");
    for line in &cert_lines[distress + 1..distress + 1 + extra] {
        assert!(
            line.starts_with("  welfare bounds:") || line.starts_with("  BOUND VIOLATED:"),
            "non-bounds line inside the divergence window: {line}"
        );
    }
    // ...and the tails agree again byte-for-byte.
    assert_eq!(
        cert_lines[distress + 1 + extra..],
        suite_lines[distress + 1..]
    );
}

/// Spec 018 FR-009 share-guard, paired block: the prefix parameter is the
/// only divergence between the suite's indented lines and the
/// certification mode's unindented ones.
#[test]
fn share_guard_paired_prefix_is_the_only_divergence() {
    // The sample subject is needs_driven, so its baseline run is the
    // identical simulation — pairing the run against itself is
    // byte-equivalent to running the baseline and costs zero extra ticks.
    let run = std::slice::from_ref(share_guard_sample_run());
    let paired = cloudkitty_rl::harness::pair_runs(run, run);
    assert!(!paired.is_empty());

    let mut plain = Vec::new();
    cloudkitty_rl::cli_support::print_paired(&mut plain, &paired, "baseline", "", None).unwrap();
    let mut indented = Vec::new();
    cloudkitty_rl::cli_support::print_paired(&mut indented, &paired, "baseline", "  ", None)
        .unwrap();
    let plain = String::from_utf8(plain).unwrap();
    let indented = String::from_utf8(indented).unwrap();
    for (p, i) in plain.lines().zip(indented.lines()) {
        assert_eq!(format!("  {p}"), i);
        assert!(p.starts_with("seed "));
    }
}
