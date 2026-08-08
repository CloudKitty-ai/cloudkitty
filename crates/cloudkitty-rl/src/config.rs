//! The `[rl.*]` configuration blocks (spec 014, Article VI: every new
//! constant lives in configuration with documented defaults).
//!
//! These blocks live in the same TOML file as the engine's configuration
//! (`cloudkitty.toml`); the engine ignores them, and this crate ignores the
//! engine's blocks — [`RlConfig::from_toml_str`] extracts `[rl]` alone.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq)]
pub enum RlConfigError {
    #[error("rl config error: {field} is {value}; {expected}")]
    Invalid {
        field: String,
        value: String,
        expected: String,
    },
    #[error("rl config error: {0}")]
    Message(String),
}

impl RlConfigError {
    fn invalid(
        field: impl Into<String>,
        value: impl Into<String>,
        expected: impl Into<String>,
    ) -> Self {
        RlConfigError::Invalid {
            field: field.into(),
            value: value.into(),
            expected: expected.into(),
        }
    }
}

/// Everything under `[rl]`.
///
/// Missing fields and tables fall back to the `Default` impls (the
/// container-level `serde(default)`, which composes with the strictness:
/// an *absent* key defaults, an *unknown* key still refuses to load).
#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct RlConfig {
    pub observation: ObservationConfig,
    pub global_state: GlobalStateConfig,
    pub reward: RewardConfig,
    pub episode: EpisodeConfig,
    pub eval: EvalConfig,
    /// `[rl.policy.<name>] artifact = "path"` — the policies configuration
    /// may name in a kitty's `behavior = "policy:<name>"`.
    pub policy: BTreeMap<String, PolicyConfig>,
}

/// `[rl.observation]`: slot counts and normalization constants (FR-005).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct ObservationConfig {
    /// Kitty slots in the observation (default 3 — the default roster's
    /// "everyone else"; larger rosters are partially observable by design).
    pub kitty_slots: usize,
    /// Critter slots (default 4).
    pub critter_slots: usize,
    /// Chow slots (default 2).
    pub chow_slots: usize,
    /// Water slots (default 2).
    pub water_slots: usize,
    /// Sunbeam slots (default 2).
    pub sunbeam_slots: usize,
    /// The need-rise rate one trait unit corresponds to: a kitty's encoded
    /// trait is `rate / reference_need_rate`, clamped to [0, 4] (documented
    /// bound). Default 1.0.
    pub reference_need_rate: f32,
    /// Chow servings are encoded as `servings / max_chow_servings`, clamped
    /// to [0, 1]. Default 5 — the default `[elements.chow] servings`.
    pub max_chow_servings: u32,
}

impl Default for ObservationConfig {
    fn default() -> Self {
        Self {
            kitty_slots: 3,
            critter_slots: 4,
            chow_slots: 2,
            water_slots: 2,
            sunbeam_slots: 2,
            reference_need_rate: 1.0,
            max_chow_servings: 5,
        }
    }
}

/// `[rl.global_state]`: the privileged critic view's bounded element summary
/// (FR-019).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct GlobalStateConfig {
    /// Positions of the K nearest elements per type to the world center
    /// included in the summary. Default 2.
    pub elements_per_type: usize,
}

impl Default for GlobalStateConfig {
    fn default() -> Self {
        Self {
            elements_per_type: 2,
        }
    }
}

/// `[rl.reward]` (FR-008/FR-009).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct RewardConfig {
    /// Power-mean exponent. 1 = plain average, 0 = Nash welfare (geometric
    /// mean, the default), large negative → the least-happy kitty's score.
    /// Must lie in [[`MIN_P`], 1] (inequality-averse: concave), and be
    /// exactly 0 or at least [`MIN_P_MAGNITUDE`] in size — a tinier
    /// nonzero exponent is numerically Nash with worse rounding.
    pub p: f64,
    /// Offset keeping the aggregate and its gradient finite at zero
    /// happiness. Default 0.01; must exceed [`MIN_EPSILON`] so the shifted
    /// welfare terms stay strictly positive for every lawful core config.
    pub epsilon: f64,
    /// `level` (default): the welfare aggregate each step. `delta`: its
    /// change since the previous step.
    pub mode: RewardMode,
    /// Potential-based shaping (FR-009). Off by default.
    pub shaping: ShapingConfig,
}

/// The exclusive lower bound on `[rl.reward] epsilon` (spec 014 third
/// review). Core accepts happiness weights whose sum is within 1e-3 of
/// 1.0, so unclamped normalized happiness can lawfully reach −0.001; an
/// ε at or below that would let `h + ε` hit zero or go negative, and
/// `ln`/`powf` would turn the team reward into a silent NaN.
pub const MIN_EPSILON: f64 = 1e-3;

/// The inclusive floor on `[rl.reward] p` (round-one review, 2026-07-24).
/// By −64 the power mean is numerically indistinguishable from the
/// least-happy-kitty limit, and more negative exponents only push `powf`
/// toward overflow; the reward's term floor is sized so this exponent
/// stays finite (`reward::TERM_FLOOR`).
pub const MIN_P: f64 = -64.0;

/// The smallest nonzero magnitude `[rl.reward] p` may take (round-one
/// review, 2026-07-24). A nonzero exponent tinier than this computes the
/// same aggregate as Nash welfare through `powf` rounding, only less
/// precisely — an operator who means the geometric mean should say
/// `p = 0` and get the dedicated `ln`-based path.
pub const MIN_P_MAGNITUDE: f64 = 1e-3;

impl Default for RewardConfig {
    fn default() -> Self {
        Self {
            p: 0.0,
            epsilon: 0.01,
            mode: RewardMode::default(),
            shaping: ShapingConfig::default(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RewardMode {
    #[default]
    Level,
    Delta,
}

/// Potential-based reward shaping (FR-009): `F = gamma * Φ(s') − Φ(s)`, with
/// the potential `Φ(s) = −distress_coefficient × (active distress entries /
/// roster)`. Provably policy-invariant; off by default; every coefficient
/// configured.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct ShapingConfig {
    pub enabled: bool,
    pub gamma: f64,
    pub distress_coefficient: f64,
}

impl Default for ShapingConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            gamma: 1.0,
            distress_coefficient: 0.0,
        }
    }
}

/// `[rl.episode]` (FR-010).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct EpisodeConfig {
    /// Truncation horizon in ticks. Default 2000; must be ≥ 1.
    pub horizon: u64,
}

impl Default for EpisodeConfig {
    fn default() -> Self {
        Self { horizon: 2_000 }
    }
}

/// `[rl.eval]` (FR-013): the harness defaults.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct EvalConfig {
    /// Run length per seed. Default 20,000 — the long-run welfare horizon.
    pub ticks: u64,
    /// The fixed seed set. Default: the 10 fixed CI seeds 1..=10.
    pub seeds: Vec<u64>,
}

impl Default for EvalConfig {
    fn default() -> Self {
        Self {
            ticks: 20_000,
            seeds: (1..=10).collect(),
        }
    }
}

/// One `[rl.policy.<name>]` block (FR-016).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolicyConfig {
    /// Path to the policy artifact file.
    pub artifact: String,
    /// Sample from the masked softmax using the kitty's own decision
    /// stream instead of greedy argmax (FR-015). Default false.
    #[serde(default)]
    pub sample: bool,
}

/// The wrapper shape of a full config file: everything except `[rl]` is
/// someone else's business.
#[derive(Debug, Default, Deserialize)]
struct FileWithRl {
    #[serde(default)]
    rl: RlConfig,
}

impl RlConfig {
    /// Extracts and validates the `[rl]` blocks from a full config file's
    /// TOML text. A file with no `[rl]` section yields the documented
    /// defaults.
    pub fn from_toml_str(text: &str) -> Result<Self, RlConfigError> {
        let file: FileWithRl =
            toml::from_str(text).map_err(|e| RlConfigError::Message(e.to_string()))?;
        file.rl.validate()?;
        Ok(file.rl)
    }

    pub fn validate(&self) -> Result<(), RlConfigError> {
        for (field, value) in [
            ("[rl.observation] kitty_slots", self.observation.kitty_slots),
            (
                "[rl.observation] critter_slots",
                self.observation.critter_slots,
            ),
            ("[rl.observation] chow_slots", self.observation.chow_slots),
            ("[rl.observation] water_slots", self.observation.water_slots),
            (
                "[rl.observation] sunbeam_slots",
                self.observation.sunbeam_slots,
            ),
        ] {
            if value == 0 {
                return Err(RlConfigError::invalid(
                    field,
                    "0".to_string(),
                    "must be at least 1 slot",
                ));
            }
        }
        if self.observation.reference_need_rate <= 0.0
            || !self.observation.reference_need_rate.is_finite()
        {
            return Err(RlConfigError::invalid(
                "[rl.observation] reference_need_rate",
                self.observation.reference_need_rate.to_string(),
                "must be a finite number greater than 0",
            ));
        }
        if self.observation.max_chow_servings == 0 {
            return Err(RlConfigError::invalid(
                "[rl.observation] max_chow_servings",
                "0".to_string(),
                "must be at least 1",
            ));
        }
        if self.global_state.elements_per_type == 0 {
            return Err(RlConfigError::invalid(
                "[rl.global_state] elements_per_type",
                "0".to_string(),
                "must be at least 1",
            ));
        }
        if !self.reward.p.is_finite() || self.reward.p > 1.0 || self.reward.p < MIN_P {
            return Err(RlConfigError::invalid(
                "[rl.reward] p",
                self.reward.p.to_string(),
                "must be a finite exponent in [-64, 1]: at most 1 keeps the \
                 aggregation inequality-averse, and below -64 the power mean is \
                 numerically the least-happy-kitty limit while powf courts overflow",
            ));
        }
        if self.reward.p != 0.0 && self.reward.p.abs() < MIN_P_MAGNITUDE {
            return Err(RlConfigError::invalid(
                "[rl.reward] p",
                self.reward.p.to_string(),
                "a nonzero exponent must be at least 0.001 in magnitude: anything \
                 tinier is Nash welfare with worse rounding — say p = 0 to mean \
                 the geometric mean",
            ));
        }
        if self.reward.epsilon <= MIN_EPSILON || !self.reward.epsilon.is_finite() {
            return Err(RlConfigError::invalid(
                "[rl.reward] epsilon",
                self.reward.epsilon.to_string(),
                "must be a finite number greater than 0.001: core tolerates happiness \
                 weights summing to 1 ± 0.001, so normalized happiness can lawfully \
                 reach −0.001, and ε must dominate it to keep the welfare terms positive",
            ));
        }
        if self.reward.shaping.enabled {
            if !(self.reward.shaping.gamma > 0.0 && self.reward.shaping.gamma <= 1.0) {
                return Err(RlConfigError::invalid(
                    "[rl.reward.shaping] gamma",
                    self.reward.shaping.gamma.to_string(),
                    "must be in (0, 1]",
                ));
            }
            if !self.reward.shaping.distress_coefficient.is_finite()
                || self.reward.shaping.distress_coefficient < 0.0
            {
                return Err(RlConfigError::invalid(
                    "[rl.reward.shaping] distress_coefficient",
                    self.reward.shaping.distress_coefficient.to_string(),
                    "must be a finite number of at least 0",
                ));
            }
        }
        if self.episode.horizon == 0 {
            return Err(RlConfigError::invalid(
                "[rl.episode] horizon",
                "0".to_string(),
                "an episode runs at least 1 tick before truncation",
            ));
        }
        if self.eval.ticks == 0 {
            return Err(RlConfigError::invalid(
                "[rl.eval] ticks",
                "0".to_string(),
                "must be at least 1 tick",
            ));
        }
        if self.eval.seeds.is_empty() {
            return Err(RlConfigError::invalid(
                "[rl.eval] seeds",
                "empty".to_string(),
                "must list at least one seed",
            ));
        }
        for (name, policy) in &self.policy {
            if policy.artifact.trim().is_empty() {
                return Err(RlConfigError::invalid(
                    format!("[rl.policy.{name}] artifact"),
                    "empty".to_string(),
                    "must be a path to a policy artifact file",
                ));
            }
        }
        Ok(())
    }
}

/// Loads the engine `Config` and the `[rl]` blocks from one TOML text —
/// the shape of `cloudkitty.toml`. The engine config is validated; behavior
/// names are the caller's business (the registry decides what exists).
pub fn load_configs_from_str(
    text: &str,
) -> Result<(cloudkitty_core::Config, RlConfig), RlConfigError> {
    let core: cloudkitty_core::Config =
        toml::from_str(text).map_err(|e| RlConfigError::Message(e.to_string()))?;
    core.validate()
        .map_err(|e| RlConfigError::Message(e.to_string()))?;
    let rl = RlConfig::from_toml_str(text)?;
    Ok((core, rl))
}

/// [`load_configs_from_str`] for a file path.
pub fn load_configs_from_path(
    path: &str,
) -> Result<(cloudkitty_core::Config, RlConfig), RlConfigError> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| RlConfigError::Message(format!("cannot read {path}: {e}")))?;
    load_configs_from_str(&text)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn an_empty_file_yields_the_documented_defaults() {
        let rl = RlConfig::from_toml_str("").expect("defaults are valid");
        assert_eq!(rl.observation.kitty_slots, 3);
        assert_eq!(rl.observation.critter_slots, 4);
        assert_eq!(rl.observation.chow_slots, 2);
        assert_eq!(rl.observation.water_slots, 2);
        assert_eq!(rl.observation.sunbeam_slots, 2);
        assert_eq!(rl.reward.p, 0.0, "Nash welfare by default");
        assert_eq!(rl.reward.epsilon, 0.01);
        assert_eq!(rl.reward.mode, RewardMode::Level);
        assert!(!rl.reward.shaping.enabled, "shaping defaults off");
        assert_eq!(rl.episode.horizon, 2_000);
        assert_eq!(rl.eval.ticks, 20_000);
        assert_eq!(rl.eval.seeds.len(), 10);
    }

    #[test]
    fn a_full_config_file_parses_only_its_rl_blocks() {
        let text = r#"
            [world]
            width = 32
            height = 32
            tick_ms = 800
            seed = 1

            [rl.reward]
            p = 1.0
            epsilon = 0.05

            [rl.episode]
            horizon = 512

            [rl.policy.sunchaser]
            artifact = "policies/sunchaser-v1.ckpolicy"
        "#;
        let rl = RlConfig::from_toml_str(text).expect("parses");
        assert_eq!(rl.reward.p, 1.0);
        assert_eq!(rl.reward.epsilon, 0.05);
        assert_eq!(rl.episode.horizon, 512);
        assert_eq!(
            rl.policy.get("sunchaser").unwrap().artifact,
            "policies/sunchaser-v1.ckpolicy"
        );
    }

    #[test]
    fn invalid_values_are_rejected_by_field_name() {
        let err = RlConfig::from_toml_str("[rl.reward]\np = 2.0\n").unwrap_err();
        assert!(err.to_string().contains("[rl.reward] p"), "{err}");

        let err = RlConfig::from_toml_str("[rl.reward]\nepsilon = 0.0\n").unwrap_err();
        assert!(err.to_string().contains("epsilon"), "{err}");

        // Third review: an ε at or below core's happiness-weights sum
        // tolerance (1e-3) would let a lawful config drive the welfare
        // terms non-positive and NaN the team reward.
        let err = RlConfig::from_toml_str("[rl.reward]\nepsilon = 0.0005\n").unwrap_err();
        assert!(err.to_string().contains("epsilon"), "{err}");
        RlConfig::from_toml_str("[rl.reward]\nepsilon = 0.002\n")
            .expect("an epsilon above the tolerance is lawful");

        let err = RlConfig::from_toml_str("[rl.episode]\nhorizon = 0\n").unwrap_err();
        assert!(err.to_string().contains("[rl.episode] horizon"), "{err}");

        let err = RlConfig::from_toml_str("[rl.observation]\nkitty_slots = 0\n").unwrap_err();
        assert!(err.to_string().contains("kitty_slots"), "{err}");

        let err = RlConfig::from_toml_str("[rl.policy.broken]\nartifact = \"\"\n").unwrap_err();
        assert!(err.to_string().contains("[rl.policy.broken]"), "{err}");
    }

    #[test]
    fn the_p_exponent_is_bounded_on_both_sides() {
        // Round-one review finding 2: any finite p ≤ 1 used to pass. A
        // tiny nonzero |p| collapses the aggregate into a badly-rounded
        // Nash; a hugely negative p drives powf toward overflow.
        let err = RlConfig::from_toml_str("[rl.reward]\np = 0.0001\n").unwrap_err();
        assert!(err.to_string().contains("p = 0"), "{err}");
        let err = RlConfig::from_toml_str("[rl.reward]\np = -0.0005\n").unwrap_err();
        assert!(err.to_string().contains("p = 0"), "{err}");
        let err = RlConfig::from_toml_str("[rl.reward]\np = -65.0\n").unwrap_err();
        assert!(err.to_string().contains("[rl.reward] p"), "{err}");

        // The documented extremes stay lawful: the floor itself, the
        // smallest honest nonzero magnitude, Nash, and the plain average.
        for lawful in ["-64.0", "-0.001", "0.001", "0.0", "1.0"] {
            RlConfig::from_toml_str(&format!("[rl.reward]\np = {lawful}\n"))
                .unwrap_or_else(|e| panic!("p = {lawful} must be lawful: {e}"));
        }
    }

    #[test]
    fn the_documented_deploy_snippet_wires_a_policy_kitty() {
        // Round-one review finding 1: the docs showed `[kitties.pumpkin]`,
        // a table core's lenient config silently ignores -- the US4 deploy
        // step no-oped with no error. This pins the corrected `[[kitty]]`
        // form end to end: the behavior lands on the kitty, and the policy
        // block is found.
        let (core, rl) = load_configs_from_str(
            r#"
            [world]
            width = 32
            height = 32
            tick_ms = 800
            seed = 1

            [[kitty]]
            id = 1
            name = "Miso"
            x = 1
            y = 1
            behavior = "needs_driven"

            [[kitty]]
            id = 3
            name = "Pumpkin"
            x = 2
            y = 2
            behavior = "policy:trained"

            [rl.policy.trained]
            artifact = "policies/trained.ckpolicy"
            "#,
        )
        .expect("the documented deploy config must load");
        let pumpkin = core
            .kitties
            .iter()
            .find(|k| k.name == "Pumpkin")
            .expect("Pumpkin is in the roster");
        assert_eq!(pumpkin.behavior, "policy:trained");
        assert_eq!(
            rl.policy.get("trained").unwrap().artifact,
            "policies/trained.ckpolicy"
        );
    }

    #[test]
    fn a_misspelt_rl_key_is_rejected_at_load_not_silently_ignored() {
        // Same strictness as the core config (2026-08-06 handoff): a
        // typo'd dial under [rl.*] must refuse to load, not run defaults.
        let err = RlConfig::from_toml_str("[rl.observation]\nkitty_slotz = 4\n")
            .expect_err("an unknown key in an rl table is refused");
        assert!(err.to_string().contains("kitty_slotz"), "{err}");
    }

    #[test]
    fn parked_policy_seats_stay_legal_under_strictness() {
        // Spec 026 parks seats by leaving [rl.policy.<name>] blocks
        // present but unreferenced -- known fields, never unknown ones.
        let rl = RlConfig::from_toml_str(
            "[rl.policy.parked]\nartifact = \"policies/parked.ckpolicy\"\nsample = true\n",
        )
        .expect("a parked seat block still loads");
        assert!(rl.policy.contains_key("parked"));
    }
}
