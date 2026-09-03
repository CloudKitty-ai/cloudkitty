//! The held-out evaluation suite (spec 017): scores one subject across a
//! manifest of committed, frozen exam configs, in addition to — never
//! instead of — default-world certification. Standard exams reuse the
//! harness flow per config; the mixed-roster exam runs composition cells
//! against a derived all-scripted baseline and renders the suite's only
//! verdict, anchored to that baseline (FR-010), never to the bar's bounds.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::Config;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::config::{load_configs_from_str, RlConfig};
use crate::harness::{
    pair_runs, run_many, run_one, run_one_with, EvalRequest, PairedDelta, RosterMode, RunOutcome,
};
use crate::welfare;

/// The seat placeholder a frozen exam config uses for policy seats
/// (FR-011). The harness binds it at invocation; no frozen file ever
/// names an artifact.
pub const CANDIDATE_BEHAVIOR: &str = "policy:candidate";

/// The scripted behavior a candidate seat becomes in the derived
/// all-scripted baseline (research.md R4). Scripted seats — `playful`
/// included — are never rewritten.
const BASELINE_BEHAVIOR: &str = "needs_driven";

// ---------------------------------------------------------------------------
// Manifest loading (FR-004, FR-012; data-model.md)
// ---------------------------------------------------------------------------

/// A suite load/validation failure. The message always names the file (and
/// field, where the config loader provides one) — a suite never silently
/// skips an exam (FR-004).
#[derive(Debug)]
pub struct SuiteError(pub String);

impl std::fmt::Display for SuiteError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

#[derive(Deserialize)]
struct RawManifest {
    version: String,
    verdict: RawVerdict,
    #[serde(rename = "exam", default)]
    exams: Vec<RawExam>,
}

#[derive(Deserialize)]
struct RawVerdict {
    differential_tolerance: f64,
    tail_probability: f64,
    least_happy_threshold: BTreeMap<String, u32>,
    sign_test: SignTestMode,
    sign_test_tail: f64,
    sign_test_k: u32,
}

/// Whether a tripped per-kitty sign test fails the exam or only warns
/// (FR-015). The manifest pins the default; the CLI may tighten warn →
/// gate for a run, never the reverse.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum SignTestMode {
    Warn,
    Gate,
}

impl SignTestMode {
    /// The effective mode for a run: the manifest's, tightened by the CLI
    /// when asked. Loosening is impossible by construction.
    pub fn tightened(self, enforce: bool) -> SignTestMode {
        if enforce {
            SignTestMode::Gate
        } else {
            self
        }
    }
}

#[derive(Deserialize)]
struct RawExam {
    name: String,
    kind: String,
    #[serde(default)]
    config: Option<String>,
    #[serde(default)]
    sha256: Option<String>,
    #[serde(rename = "cell", default)]
    cells: Vec<RawCell>,
}

#[derive(Deserialize)]
struct RawCell {
    name: String,
    config: String,
    sha256: String,
}

/// The mixed-roster verdict constants (manifest `[verdict]`; research.md
/// R7, R12).
#[derive(Debug, Clone, Serialize)]
pub struct VerdictConstants {
    pub differential_tolerance: f64,
    pub tail_probability: f64,
    pub least_happy_threshold: BTreeMap<String, u32>,
    /// FR-015: the manifest's default mode for the per-kitty sign test.
    pub sign_test: SignTestMode,
    /// The sign test's own fair-coin tail bound (distinct from
    /// `tail_probability`; they coincide at n = 10 seeds, diverge beyond).
    pub sign_test_tail: f64,
    /// Smallest k with P(Binomial(n_seeds, ½) ≥ k) ≤ `sign_test_tail` —
    /// derived from the exam's seed count, guarded by a recomputation test.
    pub sign_test_k: u32,
}

/// One loaded, hash-verified, validated composition cell.
pub struct LoadedCell {
    pub name: String,
    pub sha256: String,
    pub core: Config,
    pub rl: RlConfig,
}

/// One loaded, hash-verified, validated standard exam.
pub struct LoadedStandard {
    pub name: String,
    pub sha256: String,
    pub core: Config,
    pub rl: RlConfig,
}

pub enum LoadedExam {
    Standard(Box<LoadedStandard>),
    MixedRoster {
        name: String,
        cells: Vec<LoadedCell>,
    },
}

pub struct LoadedSuite {
    pub version: String,
    pub verdict: VerdictConstants,
    pub exams: Vec<LoadedExam>,
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

/// The engine-defaults stamp (experiments-session request, 2026-07-27).
///
/// Frozen exam files inherit every config section they omit from the
/// compiled defaults, so the manifest's file hashes freeze the exam *text*
/// but not the world it simulates — a change to `Config::default()` or
/// `RlConfig::default()` moves every exam's meaning while every sha256
/// still validates (as the 2026-07-27 relief/weights retune did). This
/// stamp closes that gap: it hashes the canonical JSON of both default
/// surfaces, so two suite reports are comparable only if their stamps
/// match, whatever their `suite_version` says.
pub fn engine_defaults_sha256() -> String {
    defaults_stamp(&Config::default(), &RlConfig::default())
}

/// [`engine_defaults_sha256`]'s body, parameterized so the sensitivity
/// property (any default moving moves the stamp) is testable.
fn defaults_stamp(core: &Config, rl: &RlConfig) -> String {
    let core = serde_json::to_string(core).expect("compiled core defaults always serialize");
    let rl = serde_json::to_string(rl).expect("compiled rl defaults always serialize");
    sha256_hex(format!("{core}\n{rl}").as_bytes())
}

fn load_member(
    dir: &Path,
    rel: &str,
    expected_sha: &str,
) -> Result<(Config, RlConfig), SuiteError> {
    let path: PathBuf = dir.join(rel);
    let bytes = std::fs::read(&path)
        .map_err(|e| SuiteError(format!("cannot read exam config {}: {e}", path.display())))?;
    let actual = sha256_hex(&bytes);
    if actual != expected_sha {
        return Err(SuiteError(format!(
            "{rel}: content hash {actual} does not match the manifest's {expected_sha} — \
             a landed suite version is frozen (FR-012); score modified worlds via --config instead"
        )));
    }
    let text =
        String::from_utf8(bytes).map_err(|e| SuiteError(format!("{rel}: not valid UTF-8: {e}")))?;
    load_configs_from_str(&text).map_err(|e| SuiteError(format!("{rel}: {e}")))
}

/// Loads and fully validates `DIR/manifest.toml` and every member config —
/// hash verification, engine validation, and the structural rules from
/// data-model.md. Any failure names the offending file.
pub fn load_suite(dir: &Path) -> Result<LoadedSuite, SuiteError> {
    let manifest_path = dir.join("manifest.toml");
    let text = std::fs::read_to_string(&manifest_path).map_err(|e| {
        SuiteError(format!(
            "cannot read suite manifest {}: {e}",
            manifest_path.display()
        ))
    })?;
    let raw: RawManifest = toml::from_str(&text)
        .map_err(|e| SuiteError(format!("{}: {e}", manifest_path.display())))?;

    if raw.version.trim().is_empty() {
        return Err(SuiteError("manifest version must be non-empty".into()));
    }
    if raw.exams.is_empty() {
        return Err(SuiteError(format!(
            "suite {} lists no exams — an empty suite is a usage error, not an empty success",
            raw.version
        )));
    }
    let v = &raw.verdict;
    if !(v.differential_tolerance >= 0.0 && v.differential_tolerance.is_finite()) {
        return Err(SuiteError(format!(
            "[verdict] differential_tolerance {} must be finite and >= 0",
            v.differential_tolerance
        )));
    }
    if !(v.tail_probability > 0.0 && v.tail_probability < 1.0) {
        return Err(SuiteError(format!(
            "[verdict] tail_probability {} must be in (0, 1)",
            v.tail_probability
        )));
    }
    if !(v.sign_test_tail > 0.0 && v.sign_test_tail < 1.0) {
        return Err(SuiteError(format!(
            "[verdict] sign_test_tail {} must be in (0, 1)",
            v.sign_test_tail
        )));
    }
    if v.sign_test_k == 0 {
        return Err(SuiteError(
            "[verdict] sign_test_k must be at least 1 (a zero threshold trips on every run)".into(),
        ));
    }

    let mut names = std::collections::BTreeSet::new();
    let mut mixed_count = 0usize;
    let mut exams = Vec::with_capacity(raw.exams.len());
    for exam in &raw.exams {
        if !names.insert(exam.name.clone()) {
            return Err(SuiteError(format!("duplicate exam name '{}'", exam.name)));
        }
        match exam.kind.as_str() {
            "standard" => {
                let (Some(config), Some(sha)) = (&exam.config, &exam.sha256) else {
                    return Err(SuiteError(format!(
                        "standard exam '{}' needs both config and sha256",
                        exam.name
                    )));
                };
                let (core, rl) = load_member(dir, config, sha)?;
                exams.push(LoadedExam::Standard(Box::new(LoadedStandard {
                    name: exam.name.clone(),
                    sha256: sha.clone(),
                    core,
                    rl,
                })));
            }
            "mixed-roster" => {
                mixed_count += 1;
                if exam.cells.len() < 2 {
                    return Err(SuiteError(format!(
                        "mixed-roster exam '{}' needs at least 2 cells",
                        exam.name
                    )));
                }
                let mut cells = Vec::with_capacity(exam.cells.len());
                for cell in &exam.cells {
                    let (core, rl) = load_member(dir, &cell.config, &cell.sha256)?;
                    let candidates = core
                        .kitties
                        .iter()
                        .filter(|k| k.behavior == CANDIDATE_BEHAVIOR)
                        .count();
                    let scripted = core.kitties.len() - candidates;
                    if candidates == 0 {
                        return Err(SuiteError(format!(
                            "{}: cell '{}' has no {CANDIDATE_BEHAVIOR} seat — it would measure nothing",
                            cell.config, cell.name
                        )));
                    }
                    if scripted == 0 {
                        return Err(SuiteError(format!(
                            "{}: cell '{}' has no scripted seat — no guests to differentiate",
                            cell.config, cell.name
                        )));
                    }
                    if !raw.verdict.least_happy_threshold.contains_key(&cell.name) {
                        return Err(SuiteError(format!(
                            "[verdict.least_happy_threshold] has no entry for cell '{}'",
                            cell.name
                        )));
                    }
                    cells.push(LoadedCell {
                        name: cell.name.clone(),
                        sha256: cell.sha256.clone(),
                        core,
                        rl,
                    });
                }
                exams.push(LoadedExam::MixedRoster {
                    name: exam.name.clone(),
                    cells,
                });
            }
            other => {
                return Err(SuiteError(format!(
                    "exam '{}' has unknown kind '{other}' (standard | mixed-roster)",
                    exam.name
                )));
            }
        }
    }
    if mixed_count != 1 {
        return Err(SuiteError(format!(
            "a suite version carries exactly one mixed-roster exam (found {mixed_count}) — \
             the [verdict] constants bind to it"
        )));
    }

    Ok(LoadedSuite {
        version: raw.version,
        verdict: VerdictConstants {
            differential_tolerance: raw.verdict.differential_tolerance,
            tail_probability: raw.verdict.tail_probability,
            least_happy_threshold: raw.verdict.least_happy_threshold,
            sign_test: raw.verdict.sign_test,
            sign_test_tail: raw.verdict.sign_test_tail,
            sign_test_k: raw.verdict.sign_test_k,
        },
        exams,
    })
}

// ---------------------------------------------------------------------------
// Report types (FR-003, FR-013; data-model.md)
// ---------------------------------------------------------------------------

/// The default world's welfare bounds, shown in exam JSON as reference
/// context only — never a verdict on exam worlds (FR-003, research.md R11).
#[derive(Debug, Clone, Serialize)]
pub struct ReferenceBounds {
    pub calibrated_to: &'static str,
    pub min_mean_happiness: f32,
    pub low_happiness: f32,
    pub max_low_streak: u64,
    pub max_low_share: f64,
    pub max_pinned_streak: u64,
    pub max_distress_age: u64,
}

impl ReferenceBounds {
    pub fn current() -> Self {
        ReferenceBounds {
            calibrated_to: "default world",
            min_mean_happiness: welfare::MIN_MEAN_HAPPINESS,
            low_happiness: welfare::LOW_HAPPINESS,
            max_low_streak: welfare::MAX_LOW_STREAK,
            max_low_share: welfare::MAX_LOW_SHARE,
            max_pinned_streak: welfare::MAX_PINNED_STREAK,
            max_distress_age: welfare::MAX_DISTRESS_AGE,
        }
    }
}

#[derive(Serialize)]
pub struct StandardOutcome {
    pub name: String,
    pub config_sha256: String,
    pub runs: Vec<RunOutcome>,
    pub baseline_runs: Vec<RunOutcome>,
    pub paired: Vec<PairedDelta>,
    pub reference_bounds: ReferenceBounds,
}

/// A scripted kitty's guest-welfare differential in one cell (US3).
#[derive(Debug, Clone, Serialize)]
pub struct KittyDifferential {
    pub kitty_id: KittyId,
    pub name: String,
    pub cell_mean: f64,
    pub baseline_mean: f64,
    pub differential: f64,
    /// FR-015: paired seeds where this kitty's differential was strictly
    /// negative (zeros count as non-negative — a bit-identical
    /// `needs_driven`-candidate run scores 0 here, trivially). The sign
    /// test trips at ≥ `sign_test_k`.
    pub negative_seeds: u32,
}

#[derive(Debug, Clone, Serialize)]
pub struct DuetShare {
    pub kitty_id: KittyId,
    pub name: String,
    pub share: f64,
}

#[derive(Serialize)]
pub struct CellOutcome {
    pub name: String,
    pub config_sha256: String,
    pub runs: Vec<RunOutcome>,
    pub baseline_runs: Vec<RunOutcome>,
    pub paired: Vec<PairedDelta>,
    pub differentials: Vec<KittyDifferential>,
    pub least_happy_out_group_seeds: u32,
    /// The same count in the all-scripted baseline: the identity check's
    /// anchor. A `playful` out-group cat may be its meadow's least happy by
    /// temperament in both worlds — only an *increase* over the baseline is
    /// a signal (FR-010: the verdict is anchored to the baseline).
    pub baseline_least_happy_out_group_seeds: u32,
    pub duet_shares: Vec<DuetShare>,
}

#[derive(Debug, Clone, Serialize)]
pub struct VerdictCheck {
    pub cell: String,
    pub check: &'static str,
    pub passed: bool,
    /// The measured value the check judged.
    pub value: f64,
    /// The bound it was judged against.
    pub bound: f64,
    /// The baseline anchor, for checks judged against one (the identity
    /// check's baseline least-happy count) — so `passed` is always
    /// reconstructible from the serialized fields alone, never contradicted
    /// by a value-vs-bound reading (post-implementation review, finding 4).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub baseline: Option<f64>,
}

/// FR-015: emitted when a scripted kitty's sign test trips — its
/// differential was negative in `negative_seeds` ≥ `sign_test_k` of the
/// paired seeds. Rare by construction (fair-coin tail ≤ `sign_test_tail`),
/// so a signature always means something.
#[derive(Debug, Clone, Serialize)]
pub struct ExploitationSignature {
    pub cell: String,
    pub kitty: String,
    pub differential: f64,
    pub negative_seeds: u32,
    /// Whether this cell's aggregate check passed. True is the *masking
    /// case* — a healthy team score hiding a per-kitty victim, the story
    /// FR-010 exists to catch ("exploitation"). False means the cell is
    /// failing anyway: the trip is general harm from an underperforming
    /// candidate, not masked exploitation — a true detection wearing a
    /// different story (2026-07-25 owner review).
    pub cell_aggregate_healthy: bool,
}

#[derive(Serialize)]
pub struct MixedRosterVerdict {
    pub passed: bool,
    /// The effective sign-test mode this verdict was judged under
    /// (manifest default, possibly CLI-tightened) — every report is
    /// self-describing about its regime (FR-015).
    pub sign_test_mode: SignTestMode,
    pub checks: Vec<VerdictCheck>,
    pub exploitation_signatures: Vec<ExploitationSignature>,
}

#[derive(Serialize)]
pub struct MixedRosterOutcome {
    pub name: String,
    pub cells: Vec<CellOutcome>,
    pub verdict: MixedRosterVerdict,
}

#[derive(Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum ExamOutcome {
    Standard(StandardOutcome),
    MixedRoster(MixedRosterOutcome),
}

#[derive(Serialize)]
pub struct SuiteReport {
    pub suite_version: String,
    /// See [`engine_defaults_sha256`]: reports whose stamps differ ran
    /// different engines and must not be compared, same version or not.
    pub engine_defaults_sha256: String,
    pub subject: String,
    /// `greedy`/`sampled` for a policy subject; absent for built-ins. A
    /// certification record must never be ambiguous about which policy
    /// distribution was evaluated (issue #70).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub selection: Option<&'static str>,
    pub exams: Vec<ExamOutcome>,
}

// ---------------------------------------------------------------------------
// Scoring (FR-001, FR-002, FR-008, FR-009; research.md R5, R6, R9)
// ---------------------------------------------------------------------------

/// The subject under evaluation, already bound in the registry — including
/// under [`CANDIDATE_BEHAVIOR`] for cell seats (research.md R4).
pub struct SuiteSubject<'a> {
    pub registry: &'a BehaviorRegistry,
    pub name: &'a str,
    pub is_policy: bool,
    /// `greedy`/`sampled` for a policy subject; `None` for built-ins.
    /// Stamped into the report — see [`SuiteReport::selection`].
    pub selection: Option<&'static str>,
}

/// A mid-suite mechanical failure. Fallback accounting is not here — it is
/// summed over the whole report and judged at the end, exactly as the
/// single-config path does.
#[derive(Debug)]
pub enum SuiteRunError {
    /// A repeated seed disagreed with itself (exit 3). `location` names the
    /// exam (and cell/mode) that produced it.
    Determinism { location: String, seed: u64 },
}

pub(crate) fn self_check(
    request: &EvalRequest<'_>,
    first_outcome: &RunOutcome,
    location: String,
) -> Result<(), SuiteRunError> {
    let again = run_one(request);
    if &again != first_outcome {
        return Err(SuiteRunError::Determinism {
            location,
            seed: request.seed,
        });
    }
    Ok(())
}

fn score_standard(
    name: &str,
    sha256: &str,
    core: &Config,
    rl: &RlConfig,
    subject: &SuiteSubject<'_>,
) -> Result<StandardOutcome, SuiteRunError> {
    let seeds = &rl.eval.seeds;
    let base = EvalRequest {
        core,
        rl,
        registry: subject.registry,
        subject: Some(subject.name),
        roster: RosterMode::AllSubject,
        seed: 0,
        ticks: rl.eval.ticks,
    };
    let modes: &[RosterMode] = if subject.is_policy {
        &[RosterMode::AllSubject, RosterMode::Mixed]
    } else {
        &[RosterMode::AllSubject]
    };
    let sweep = crate::cli_support::run_subject_over_modes(&base, modes, seeds, |mode| {
        format!("exam {name} ({mode:?})")
    })?;
    Ok(StandardOutcome {
        name: name.to_string(),
        config_sha256: sha256.to_string(),
        runs: sweep.runs,
        baseline_runs: sweep.baseline_runs,
        paired: sweep.paired,
        reference_bounds: ReferenceBounds::current(),
    })
}

/// The derived all-scripted baseline config: every candidate seat becomes
/// `needs_driven`; scripted seats (`playful` included) are untouched.
/// Mechanical, never a committed file — baseline drift is impossible (R4).
pub fn all_scripted_config(cell: &Config) -> Config {
    let mut config = cell.clone();
    for kitty in &mut config.kitties {
        if kitty.behavior == CANDIDATE_BEHAVIOR {
            kitty.behavior = BASELINE_BEHAVIOR.to_string();
        }
    }
    config
}

fn mean(values: impl Iterator<Item = f64>) -> f64 {
    let (sum, n) = values.fold((0.0, 0u32), |(s, n), v| (s + v, n + 1));
    if n == 0 {
        0.0
    } else {
        sum / n as f64
    }
}

/// One kitty's mean happiness in one run's welfare report. The single
/// lookup both the seed-mean aggregation and the sign test's per-seed
/// counting go through — they must never disagree about what a kitty's
/// per-seed value is.
fn per_seed_kitty_mean(run: &RunOutcome, id: KittyId) -> Option<f64> {
    run.report
        .kitties
        .iter()
        .find(|k| k.kitty_id == id)
        .map(|k| k.mean_happiness)
}

fn kitty_mean(runs: &[RunOutcome], id: KittyId) -> f64 {
    mean(runs.iter().filter_map(|run| per_seed_kitty_mean(run, id)))
}

fn score_cell(
    exam: &str,
    cell: &LoadedCell,
    subject: &SuiteSubject<'_>,
) -> Result<CellOutcome, SuiteRunError> {
    let seeds = &cell.rl.eval.seeds;
    let ticks = cell.rl.eval.ticks;
    // The cell config runs verbatim: subject None honors the config's own
    // roster, candidate seats resolved through the registry binding (R5).
    // FromConfig is the honest label — no seat was rewritten (review
    // finding 6: these runs were previously mislabeled [AllSubject]).
    let cell_request = EvalRequest {
        core: &cell.core,
        rl: &cell.rl,
        registry: subject.registry,
        subject: None,
        roster: RosterMode::FromConfig,
        seed: 0,
        ticks,
    };
    let mut runs = Vec::with_capacity(seeds.len());
    let mut duet_counts: Vec<BTreeMap<KittyId, u64>> = Vec::with_capacity(seeds.len());
    for &seed in seeds {
        let request = EvalRequest {
            seed,
            ..cell_request.clone()
        };
        let mut counts: BTreeMap<KittyId, u64> = BTreeMap::new();
        let outcome = run_one_with(&request, |world| {
            for kitty in &world.kitties {
                if kitty.activity.partner().is_some() {
                    *counts.entry(kitty.id).or_insert(0) += 1;
                }
            }
        });
        runs.push(outcome);
        duet_counts.push(counts);
    }
    if let Some(first) = seeds.first() {
        self_check(
            &EvalRequest {
                seed: *first,
                ..cell_request.clone()
            },
            &runs[0],
            format!("exam {exam}, cell {}", cell.name),
        )?;
    }

    let baseline_core = all_scripted_config(&cell.core);
    let baseline_request = EvalRequest {
        core: &baseline_core,
        ..cell_request.clone()
    };
    let baseline_runs = run_many(&baseline_request, seeds);
    if let Some(first) = seeds.first() {
        self_check(
            &EvalRequest {
                seed: *first,
                ..baseline_request.clone()
            },
            &baseline_runs[0],
            format!("exam {exam}, cell {} (all-scripted baseline)", cell.name),
        )?;
    }

    let paired = pair_runs(&runs, &baseline_runs);

    // Scripted seats are the out-group: every kitty the cell does not hand
    // to the candidate.
    let scripted: Vec<(KittyId, String)> = cell
        .core
        .kitties
        .iter()
        .filter(|k| k.behavior != CANDIDATE_BEHAVIOR)
        .map(|k| (k.id, k.name.clone()))
        .collect();
    let differentials: Vec<KittyDifferential> = scripted
        .iter()
        .map(|(id, name)| {
            let cell_mean = kitty_mean(&runs, *id);
            let baseline_mean = kitty_mean(&baseline_runs, *id);
            // FR-015: per paired seed, strictly negative counts; zeros are
            // non-negative, so bit-identical cell/baseline runs score 0.
            let negative_seeds = runs
                .iter()
                .zip(&baseline_runs)
                .filter(|(cell_run, base_run)| {
                    per_seed_kitty_mean(cell_run, *id)
                        .zip(per_seed_kitty_mean(base_run, *id))
                        .is_some_and(|(c, b)| c < b)
                })
                .count() as u32;
            KittyDifferential {
                kitty_id: *id,
                name: name.clone(),
                cell_mean,
                baseline_mean,
                differential: cell_mean - baseline_mean,
                negative_seeds,
            }
        })
        .collect();

    let scripted_ids: std::collections::BTreeSet<KittyId> =
        scripted.iter().map(|(id, _)| *id).collect();
    let out_group_least_count = |outcomes: &[RunOutcome]| {
        outcomes
            .iter()
            .filter(|run| {
                let mut least: Option<&crate::welfare::KittyWelfare> = None;
                for k in &run.report.kitties {
                    if least.is_none_or(|l| k.mean_happiness < l.mean_happiness) {
                        least = Some(k);
                    }
                }
                least.is_some_and(|k| scripted_ids.contains(&k.kitty_id))
            })
            .count() as u32
    };
    let least_happy_out_group_seeds = out_group_least_count(&runs);
    let baseline_least_happy_out_group_seeds = out_group_least_count(&baseline_runs);

    let duet_shares: Vec<DuetShare> = cell
        .core
        .kitties
        .iter()
        .map(|k| DuetShare {
            kitty_id: k.id,
            name: k.name.clone(),
            share: mean(
                duet_counts
                    .iter()
                    .map(|counts| *counts.get(&k.id).unwrap_or(&0) as f64 / ticks.max(1) as f64),
            ),
        })
        .collect();

    Ok(CellOutcome {
        name: cell.name.clone(),
        config_sha256: cell.sha256.clone(),
        runs,
        baseline_runs,
        paired,
        differentials,
        least_happy_out_group_seeds,
        baseline_least_happy_out_group_seeds,
        duet_shares,
    })
}

/// The mixed-roster verdict (FR-010, research.md R7): pure over the cell
/// outcomes and the manifest constants — no simulation, fully unit-testable.
/// `sign_test_mode` is the *effective* mode (manifest default, possibly
/// CLI-tightened, FR-015).
pub fn evaluate_verdict(
    cells: &[CellOutcome],
    constants: &VerdictConstants,
    sign_test_mode: SignTestMode,
) -> MixedRosterVerdict {
    let mut checks = Vec::new();
    let mut signatures = Vec::new();
    for cell in cells {
        let aggregate = mean(cell.runs.iter().map(|r| r.aggregates.team_welfare))
            - mean(cell.baseline_runs.iter().map(|r| r.aggregates.team_welfare));
        let aggregate_check = VerdictCheck {
            cell: cell.name.clone(),
            check: "aggregate",
            passed: aggregate >= 0.0,
            value: aggregate,
            bound: 0.0,
            baseline: None,
        };
        // The signatures' health annotation is definitionally this check's
        // verdict — sourced from it, so the two can never diverge if the
        // check's rule ever changes (third review, finding 10).
        let aggregate_healthy = aggregate_check.passed;
        checks.push(aggregate_check);

        let differential = mean(cell.differentials.iter().map(|d| d.differential));
        checks.push(VerdictCheck {
            cell: cell.name.clone(),
            check: "differential",
            passed: differential >= -constants.differential_tolerance,
            value: differential,
            bound: -constants.differential_tolerance,
            baseline: None,
        });

        let threshold = constants
            .least_happy_threshold
            .get(&cell.name)
            .copied()
            .unwrap_or(u32::MAX);
        checks.push(VerdictCheck {
            cell: cell.name.clone(),
            check: "identity",
            // Anchored to the baseline (FR-010): a playful out-group cat is
            // its meadow's least happy by temperament in BOTH worlds, so
            // concentration is a signal only when it clears the seed-noise
            // threshold AND exceeds the baseline's own concentration.
            passed: cell.least_happy_out_group_seeds < threshold
                || cell.least_happy_out_group_seeds <= cell.baseline_least_happy_out_group_seeds,
            value: cell.least_happy_out_group_seeds as f64,
            bound: threshold as f64,
            baseline: Some(cell.baseline_least_happy_out_group_seeds as f64),
        });

        // FR-015: the per-kitty paired sign test. The signature IS the
        // trigger — a scripted kitty whose differential was negative in
        // ≥ sign_test_k paired seeds — so signatures stay rare enough to
        // mean something. `passed` carries the mode-independent measurement
        // verdict (value vs bound stays reconstructible from the check's
        // own fields); whether a tripped check FAILS the exam or only
        // WARNS is the verdict-level mode's decision below.
        let tripped: Vec<&KittyDifferential> = cell
            .differentials
            .iter()
            .filter(|d| d.negative_seeds >= constants.sign_test_k)
            .collect();
        let max_negative = cell
            .differentials
            .iter()
            .map(|d| d.negative_seeds)
            .max()
            .unwrap_or(0);
        checks.push(VerdictCheck {
            cell: cell.name.clone(),
            check: SIGN_TEST_CHECK,
            passed: tripped.is_empty(),
            value: max_negative as f64,
            bound: constants.sign_test_k as f64,
            baseline: None,
        });
        for d in tripped {
            signatures.push(ExploitationSignature {
                cell: cell.name.clone(),
                kitty: d.name.clone(),
                differential: d.differential,
                negative_seeds: d.negative_seeds,
                cell_aggregate_healthy: aggregate_healthy,
            });
        }
    }
    // A failed sign-test check is forgiven under warn mode — the check
    // records the measurement; the mode decides whether it gates. Every
    // other check always gates.
    let passed = checks
        .iter()
        .all(|c| c.passed || sign_test_forgiven(c, sign_test_mode));
    MixedRosterVerdict {
        passed,
        sign_test_mode,
        checks,
        exploitation_signatures: signatures,
    }
}

/// The check name the warn-forgiveness rule keys on — one constant shared
/// by check construction, the verdict's `passed`, and the report label.
const SIGN_TEST_CHECK: &str = "sign-test";

/// The one definition of "this failed check is forgiven": a tripped
/// sign-test check under warn mode. The verdict's `passed` and the human
/// report's `[WARN]` label both read it, so they can never disagree
/// (third review, finding 6).
fn sign_test_forgiven(check: &VerdictCheck, mode: SignTestMode) -> bool {
    !check.passed && check.check == SIGN_TEST_CHECK && mode == SignTestMode::Warn
}

/// Scores every exam in manifest order. On a mechanical failure the error
/// carries the exam/cell that produced it; nothing is ever skipped.
pub fn score_suite(
    suite: &LoadedSuite,
    subject: &SuiteSubject<'_>,
    enforce_sign_test: bool,
) -> Result<SuiteReport, SuiteRunError> {
    let sign_test_mode = suite.verdict.sign_test.tightened(enforce_sign_test);
    let mut exams = Vec::with_capacity(suite.exams.len());
    for exam in &suite.exams {
        match exam {
            LoadedExam::Standard(exam) => {
                exams.push(ExamOutcome::Standard(score_standard(
                    &exam.name,
                    &exam.sha256,
                    &exam.core,
                    &exam.rl,
                    subject,
                )?));
            }
            LoadedExam::MixedRoster { name, cells } => {
                let mut outcomes = Vec::with_capacity(cells.len());
                for cell in cells {
                    outcomes.push(score_cell(name, cell, subject)?);
                }
                let verdict = evaluate_verdict(&outcomes, &suite.verdict, sign_test_mode);
                exams.push(ExamOutcome::MixedRoster(MixedRosterOutcome {
                    name: name.clone(),
                    cells: outcomes,
                    verdict,
                }));
            }
        }
    }
    Ok(SuiteReport {
        suite_version: suite.version.clone(),
        engine_defaults_sha256: engine_defaults_sha256(),
        subject: subject.name.to_string(),
        selection: subject.selection,
        exams,
    })
}

// ---------------------------------------------------------------------------
// Human report (contracts/suite-cli.md; research.md R11)
// ---------------------------------------------------------------------------

/// Prints the whole suite report, exam by exam, in manifest order.
pub fn human_report(report: &SuiteReport) {
    let stdout = std::io::stdout();
    human_report_to(&mut stdout.lock(), report).expect("writing suite report to stdout");
}

/// Writer-based body of [`human_report`], capturable by the share-guard
/// test (spec 018 FR-009). Per-run and paired rendering flow through
/// `cli_support` — the single implementation both CLI modes share.
fn human_report_to(w: &mut dyn std::io::Write, report: &SuiteReport) -> std::io::Result<()> {
    let note = crate::cli_support::selection_note(report.selection);
    writeln!(
        w,
        "== kitty-eval suite {}: subject {}{note} ==",
        report.suite_version, report.subject
    )?;
    writeln!(w, "engine defaults {}", report.engine_defaults_sha256)?;
    for exam in &report.exams {
        match exam {
            ExamOutcome::Standard(exam) => {
                writeln!(
                    w,
                    "\n-- exam {} (sha256 {}) --",
                    exam.name,
                    &exam.config_sha256[..12.min(exam.config_sha256.len())]
                )?;
                for run in &exam.runs {
                    crate::cli_support::print_run_panel(w, run, false)?;
                }
                writeln!(w, "-- paired vs needs_driven baseline --")?;
                crate::cli_support::print_paired(
                    w,
                    &exam.paired,
                    "baseline",
                    "  ",
                    report.selection,
                )?;
            }
            ExamOutcome::MixedRoster(exam) => {
                writeln!(w, "\n-- exam {} --", exam.name)?;
                for cell in &exam.cells {
                    writeln!(
                        w,
                        "\ncell {} (sha256 {}):",
                        cell.name,
                        &cell.config_sha256[..12.min(cell.config_sha256.len())]
                    )?;
                    for run in &cell.runs {
                        crate::cli_support::print_run_panel(w, run, false)?;
                    }
                    crate::cli_support::print_paired(
                        w,
                        &cell.paired,
                        "all-scripted",
                        "  ",
                        report.selection,
                    )?;
                    writeln!(w, "  guest-welfare differentials (scripted kitties):")?;
                    for d in &cell.differentials {
                        writeln!(
                            w,
                            "    {:<10} cell {:>5.1}  all-scripted {:>5.1}  differential {:+.2}",
                            d.name, d.cell_mean, d.baseline_mean, d.differential
                        )?;
                    }
                    writeln!(
                        w,
                        "  least-happy out-group seeds: {}/{} (all-scripted baseline {}/{})",
                        cell.least_happy_out_group_seeds,
                        cell.runs.len(),
                        cell.baseline_least_happy_out_group_seeds,
                        cell.baseline_runs.len()
                    )?;
                    writeln!(w, "  duet-participation shares:")?;
                    for share in &cell.duet_shares {
                        writeln!(w, "    {:<10} {:.3}", share.name, share.share)?;
                    }
                }
                writeln!(w, "\nverdict:")?;
                writeln!(
                    w,
                    "  sign-test mode: {} (FR-015; a signature under warn \
                     prompts a strict rerun with --enforce sign-test)",
                    match exam.verdict.sign_test_mode {
                        SignTestMode::Warn => "warn",
                        SignTestMode::Gate => "gate",
                    }
                )?;
                for check in &exam.verdict.checks {
                    // A tripped sign-test check under warn mode is forgiven
                    // by the verdict but must be unmissable in the report.
                    let label = if check.passed {
                        "PASS"
                    } else if sign_test_forgiven(check, exam.verdict.sign_test_mode) {
                        "WARN"
                    } else {
                        "FAIL"
                    };
                    let baseline = check
                        .baseline
                        .map(|b| format!(", baseline {b:+.4}"))
                        .unwrap_or_default();
                    writeln!(
                        w,
                        "  [{label}] {}[{}]: value {:+.4}, bound {:+.4}{baseline}",
                        check.check, check.cell, check.value, check.bound
                    )?;
                }
                for signature in &exam.verdict.exploitation_signatures {
                    // Same trigger, two stories: a victim under a healthy
                    // team score is masked exploitation (the case this exam
                    // exists to catch); a victim in a failing cell is
                    // general harm from an underperforming candidate.
                    let (label, tail) = if signature.cell_aggregate_healthy {
                        (
                            "EXPLOITATION SIGNATURE",
                            "under a healthy cell aggregate (the masking case)",
                        )
                    } else {
                        (
                            "SIGN-TEST TRIP",
                            "cell aggregate also failing: general harm, not masked exploitation",
                        )
                    };
                    writeln!(
                        w,
                        "  {label} [{}]: {} differential {:+.2}, negative in {} \
                         paired seeds — {tail}",
                        signature.cell,
                        signature.kitty,
                        signature.differential,
                        signature.negative_seeds
                    )?;
                }
                writeln!(
                    w,
                    "  mixed-roster verdict: {}",
                    if exam.verdict.passed { "PASS" } else { "FAIL" }
                )?;
            }
        }
    }
    Ok(())
}

/// Sum of fallback-taken decisions across every run in the report,
/// subject-side and baseline alike (only policy dispatch can produce them).
pub fn total_fallbacks(report: &SuiteReport) -> u64 {
    let runs = |exam: &ExamOutcome| -> u64 {
        match exam {
            ExamOutcome::Standard(e) => e
                .runs
                .iter()
                .chain(&e.baseline_runs)
                .map(|r| r.fallback_count)
                .sum(),
            ExamOutcome::MixedRoster(e) => e
                .cells
                .iter()
                .flat_map(|c| c.runs.iter().chain(&c.baseline_runs))
                .map(|r| r.fallback_count)
                .sum(),
        }
    };
    report.exams.iter().map(runs).sum()
}

/// True when the report's mixed-roster exam failed its verdict (exit 4).
pub fn verdict_failed(report: &SuiteReport) -> bool {
    report.exams.iter().any(|exam| match exam {
        ExamOutcome::MixedRoster(e) => !e.verdict.passed,
        ExamOutcome::Standard(_) => false,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::harness::WelfareAggregates;
    use crate::welfare::{KittyWelfare, WelfareReport};

    fn scratch_dir(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join("ck-suite-unit").join(name);
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    const MINIMAL_EXAM: &str = r#"
[world]
width = 16
height = 16
tick_ms = 800
seed = 1

[[kitty]]
id = 1
name = "A"
x = 2
y = 2
behavior = "policy:candidate"

[[kitty]]
id = 2
name = "B"
x = 12
y = 12
behavior = "needs_driven"

[elements.water]
min = 1
max = 2

[elements.chow]
min = 1
max = 2
servings = 5

[elements.bug]
min = 1
max = 2
ttl = 300

[elements.greeble]
min = 0
max = 1
ttl = 300

[elements.sunbeam]
min = 1
max = 2
ttl = 300

[rl.eval]
seeds = [1, 2]
ticks = 50
[vision]
radius = 40
memory_timeout_ticks = 0
"#;

    fn write_suite(dir: &Path, exam_text: &str, tamper_hash: bool) {
        let exam_path = dir.join("exam.toml");
        std::fs::write(&exam_path, exam_text).unwrap();
        let sha = if tamper_hash {
            "0".repeat(64)
        } else {
            sha256_hex(exam_text.as_bytes())
        };
        let manifest = format!(
            r#"
version = "unit-suite"

[verdict]
differential_tolerance = 0.0
tail_probability = 0.01
sign_test = "warn"
sign_test_tail = 0.001
sign_test_k = 2

[verdict.least_happy_threshold]
guest = 3
host = 3

[[exam]]
name = "mixed"
kind = "mixed-roster"

[[exam.cell]]
name = "guest"
config = "exam.toml"
sha256 = "{sha}"

[[exam.cell]]
name = "host"
config = "exam.toml"
sha256 = "{sha}"
"#
        );
        std::fs::write(dir.join("manifest.toml"), manifest).unwrap();
    }

    #[test]
    fn a_valid_manifest_loads_with_verified_hashes() {
        let dir = scratch_dir("valid");
        write_suite(
            &dir,
            &cloudkitty_core::test_support::complete_toml(MINIMAL_EXAM),
            false,
        );
        let suite = load_suite(&dir).expect("loads");
        assert_eq!(suite.version, "unit-suite");
        assert_eq!(suite.exams.len(), 1);
    }

    #[test]
    fn a_tampered_hash_names_the_file() {
        let dir = scratch_dir("tampered");
        write_suite(
            &dir,
            &cloudkitty_core::test_support::complete_toml(MINIMAL_EXAM),
            true,
        );
        let Err(err) = load_suite(&dir) else {
            panic!("hash mismatch must fail");
        };
        assert!(err.0.contains("exam.toml"), "names the file: {err}");
        assert!(err.0.contains("frozen"), "explains the doctrine: {err}");
    }

    #[test]
    fn an_invalid_config_names_exam_and_field() {
        let dir = scratch_dir("invalid");
        let bad = MINIMAL_EXAM.replace("width = 16", "width = 0");
        write_suite(
            &dir,
            &cloudkitty_core::test_support::complete_toml(&bad),
            false,
        );
        let Err(err) = load_suite(&dir) else {
            panic!("invalid config must fail");
        };
        assert!(err.0.contains("exam.toml"), "names the file: {err}");
        assert!(err.0.contains("width"), "names the field: {err}");
    }

    fn synthetic_cell(
        name: &str,
        team_deltas: &[(f64, f64)],
        differentials: &[(&str, f64, u32)],
        least_happy_out_group_seeds: u32,
        baseline_least_happy_out_group_seeds: u32,
    ) -> CellOutcome {
        let run = |welfare: f64| RunOutcome {
            seed: 1,
            ticks: 10,
            roster: RosterMode::AllSubject,
            report: WelfareReport {
                ticks: 10,
                kitties: vec![KittyWelfare {
                    kitty_id: 1,
                    name: "A".into(),
                    mean_happiness: 90.0,
                    max_low_streak: 0,
                    low_share: 0.0,
                    floor_touches: 0,
                }],
                max_distress_age: 0,
                pinned: Vec::new(),
                distress_census: Vec::new(),
            },
            aggregates: WelfareAggregates {
                team_welfare: welfare,
                plain_mean: welfare,
                least_happy_mean: 90.0,
            },
            fallback_count: 0,
            fallbacks: Vec::new(),
        };
        CellOutcome {
            name: name.into(),
            config_sha256: "0".repeat(64),
            runs: team_deltas.iter().map(|(cell, _)| run(*cell)).collect(),
            baseline_runs: team_deltas.iter().map(|(_, base)| run(*base)).collect(),
            paired: Vec::new(),
            differentials: differentials
                .iter()
                .enumerate()
                .map(|(i, (kitty, d, negative_seeds))| KittyDifferential {
                    kitty_id: (i + 1) as KittyId,
                    name: kitty.to_string(),
                    cell_mean: 80.0 + d,
                    baseline_mean: 80.0,
                    differential: *d,
                    negative_seeds: *negative_seeds,
                })
                .collect(),
            least_happy_out_group_seeds,
            baseline_least_happy_out_group_seeds,
            duet_shares: Vec::new(),
        }
    }

    fn constants() -> VerdictConstants {
        VerdictConstants {
            differential_tolerance: 0.0,
            tail_probability: 0.01,
            least_happy_threshold: [("host".to_string(), 6u32)].into_iter().collect(),
            sign_test: SignTestMode::Warn,
            sign_test_tail: 0.001,
            sign_test_k: 10,
        }
    }

    #[test]
    fn a_healthy_cell_passes_all_checks() {
        let cell = synthetic_cell("host", &[(0.90, 0.89)], &[("Biscuit", 1.5, 3)], 1, 1);
        let verdict = evaluate_verdict(&[cell], &constants(), SignTestMode::Gate);
        assert!(verdict.passed);
        assert!(verdict.exploitation_signatures.is_empty());
    }

    #[test]
    fn a_temperamentally_least_happy_out_group_cat_is_not_an_identity_signal() {
        // The case the first full-suite run caught: playful Biscuit is the
        // meadow's least-happy by temperament in the cell AND the baseline.
        // Concentration matching the baseline is no signal, however high
        // (FR-010: anchored to the baseline, never absolute).
        let cell = synthetic_cell("host", &[(0.90, 0.89)], &[("Biscuit", 0.5, 0)], 10, 10);
        let verdict = evaluate_verdict(&[cell], &constants(), SignTestMode::Warn);
        assert!(verdict.passed, "identity anchored to the baseline");
        let identity = verdict
            .checks
            .iter()
            .find(|c| c.check == "identity")
            .unwrap();
        assert_eq!(
            identity.baseline,
            Some(10.0),
            "the anchor is serialized, so passed is reconstructible (finding 4)"
        );
    }

    #[test]
    fn a_negative_host_differential_fails_the_differential_check() {
        let cell = synthetic_cell("host", &[(0.91, 0.90)], &[("Biscuit", -3.2, 2)], 2, 1);
        let verdict = evaluate_verdict(&[cell], &constants(), SignTestMode::Warn);
        assert!(!verdict.passed, "the differential check fails the exam");
        // Sub-k concentration is not a signature (FR-015 defines the
        // trigger; FR-010 defers to it) — the harm stays visible in the
        // differential table, not in the signature list.
        assert!(
            verdict.exploitation_signatures.is_empty(),
            "negative_seeds 2 < k 10: table-visible, not signature-named"
        );
    }

    #[test]
    fn concentrated_least_happy_identity_fails_the_identity_check() {
        // Above the seed-noise threshold AND above the baseline's own
        // concentration: both conditions met, the check fails.
        let cell = synthetic_cell("host", &[(0.90, 0.89)], &[("Biscuit", 0.5, 0)], 6, 2);
        let verdict = evaluate_verdict(&[cell], &constants(), SignTestMode::Warn);
        assert!(!verdict.passed);
        let identity = verdict
            .checks
            .iter()
            .find(|c| c.check == "identity")
            .unwrap();
        assert!(!identity.passed);
        assert_eq!(identity.value, 6.0);
    }

    // FR-015: the sign test names the tripped kitty in warn mode without
    // failing the exam, and fails it in gate mode — the signature is the
    // trigger either way. The fixture is the masking scenario the test
    // exists for: one targeted victim hidden behind a positive out-group
    // mean, so every other check passes.
    #[test]
    fn a_tripped_sign_test_warns_by_default_and_gates_when_enforced() {
        let cell = || {
            synthetic_cell(
                "host",
                &[(0.91, 0.90)],
                &[("Biscuit", -1.8, 10), ("Miso", 2.5, 0)],
                1,
                1,
            )
        };
        let warned = evaluate_verdict(&[cell()], &constants(), SignTestMode::Warn);
        assert!(warned.passed, "warn mode never fails the exam");
        assert_eq!(warned.sign_test_mode, SignTestMode::Warn);
        let signature = &warned.exploitation_signatures[0];
        assert_eq!(
            (signature.cell.as_str(), signature.kitty.as_str()),
            ("host", "Biscuit")
        );
        assert_eq!(signature.negative_seeds, 10);
        assert!(
            signature.cell_aggregate_healthy,
            "healthy aggregate + victim = the masking case, labeled as such"
        );
        // The check itself records the measurement, mode-independently:
        // value vs bound and passed always agree (second review, finding 1).
        let check = warned
            .checks
            .iter()
            .find(|c| c.check == "sign-test")
            .unwrap();
        assert!(!check.passed, "tripped is tripped, even when forgiven");
        assert_eq!((check.value, check.bound), (10.0, 10.0));

        let gated = evaluate_verdict(&[cell()], &constants(), SignTestMode::Gate);
        assert!(!gated.passed, "gate mode fails the exam (exit 4)");
        assert_eq!(gated.sign_test_mode, SignTestMode::Gate);
        let check = gated
            .checks
            .iter()
            .find(|c| c.check == "sign-test")
            .unwrap();
        assert!(!check.passed);
        assert_eq!((check.value, check.bound), (10.0, 10.0));
    }

    // The same trigger under a FAILING aggregate is annotated as general
    // harm, not masked exploitation — an underperforming candidate makes
    // its neighbors' trips true detections wearing a different story
    // (owner review, 2026-07-25).
    #[test]
    fn a_trip_in_a_failing_cell_is_general_harm_not_masked_exploitation() {
        let cell = synthetic_cell(
            "host",
            &[(0.85, 0.90)],
            &[("Biscuit", -2.3, 10), ("Miso", 2.5, 0)],
            1,
            1,
        );
        let verdict = evaluate_verdict(&[cell], &constants(), SignTestMode::Warn);
        assert!(!verdict.passed, "the failing aggregate gates regardless");
        let signature = &verdict.exploitation_signatures[0];
        assert_eq!(signature.kitty, "Biscuit");
        assert!(
            !signature.cell_aggregate_healthy,
            "failing aggregate: the trip is named, but not as masked exploitation"
        );
    }

    #[test]
    fn the_sign_test_mode_only_ever_tightens() {
        assert_eq!(SignTestMode::Warn.tightened(false), SignTestMode::Warn);
        assert_eq!(SignTestMode::Warn.tightened(true), SignTestMode::Gate);
        assert_eq!(SignTestMode::Gate.tightened(false), SignTestMode::Gate);
        assert_eq!(SignTestMode::Gate.tightened(true), SignTestMode::Gate);
    }

    /// Spec 018 FR-009 share-guard, suite side: the suite report embeds the
    /// shared renderer's suite-variant output verbatim — the report cannot
    /// describe a run differently than `cli_support::print_run_panel` does.
    #[test]
    fn share_guard_suite_report_embeds_the_shared_panel_verbatim() {
        let core = Config::default();
        let rl = crate::config::RlConfig::default();
        let registry = BehaviorRegistry::with_builtins();
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            seed: 7,
            ticks: 120,
        };
        let run = run_one(&request);

        let mut panel = Vec::new();
        crate::cli_support::print_run_panel(&mut panel, &run, false).unwrap();
        let panel = String::from_utf8(panel).unwrap();

        let report = SuiteReport {
            suite_version: "share-guard".to_string(),
            engine_defaults_sha256: engine_defaults_sha256(),
            subject: "needs_driven".to_string(),
            selection: None,
            exams: vec![ExamOutcome::Standard(StandardOutcome {
                name: "fixture".to_string(),
                config_sha256: "0".repeat(64),
                runs: vec![run],
                baseline_runs: Vec::new(),
                paired: Vec::new(),
                reference_bounds: ReferenceBounds::current(),
            })],
        };
        let mut rendered = Vec::new();
        human_report_to(&mut rendered, &report).unwrap();
        let rendered = String::from_utf8(rendered).unwrap();
        assert!(
            rendered.contains(&panel),
            "suite report does not embed the shared panel verbatim"
        );
    }

    #[test]
    fn the_engine_defaults_stamp_is_stable_and_well_formed() {
        let stamp = engine_defaults_sha256();
        assert_eq!(stamp.len(), 64);
        assert!(stamp.chars().all(|c| c.is_ascii_hexdigit()));
        assert_eq!(stamp, engine_defaults_sha256(), "same build, same stamp");
    }

    #[test]
    fn any_default_moving_moves_the_stamp() {
        let baseline = engine_defaults_sha256();

        let mut core = Config::default();
        core.actions.rest_mutual_relief += 1.0;
        assert_ne!(
            defaults_stamp(&core, &crate::config::RlConfig::default()),
            baseline,
            "a core default moved but the stamp did not — silent comparability"
        );

        let mut rl = crate::config::RlConfig::default();
        rl.reward.epsilon += 0.001;
        assert_ne!(
            defaults_stamp(&Config::default(), &rl),
            baseline,
            "an rl default moved but the stamp did not — silent comparability"
        );
    }
}
