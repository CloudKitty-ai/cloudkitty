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
#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize)]
pub struct RlConfig {
    #[serde(default)]
    pub observation: ObservationConfig,
    #[serde(default)]
    pub global_state: GlobalStateConfig,
    #[serde(default)]
    pub reward: RewardConfig,
    #[serde(default)]
    pub episode: EpisodeConfig,
    #[serde(default)]
    pub eval: EvalConfig,
    /// `[rl.policy.<name>] artifact = "path"` — the policies configuration
    /// may name in a kitty's `behavior = "policy:<name>"`.
    #[serde(default)]
    pub policy: BTreeMap<String, PolicyConfig>,
}

/// `[rl.observation]`: slot counts and normalization constants (FR-005).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ObservationConfig {
    /// Kitty slots in the observation (default 3 — the default roster's
    /// "everyone else"; larger rosters are partially observable by design).
    #[serde(default = "default_kitty_slots")]
    pub kitty_slots: usize,
    /// Critter slots (default 4).
    #[serde(default = "default_critter_slots")]
    pub critter_slots: usize,
    /// Chow slots (default 2).
    #[serde(default = "default_chow_slots")]
    pub chow_slots: usize,
    /// Water slots (default 2).
    #[serde(default = "default_water_slots")]
    pub water_slots: usize,
    /// Sunbeam slots (default 2).
    #[serde(default = "default_sunbeam_slots")]
    pub sunbeam_slots: usize,
    /// The need-rise rate one trait unit corresponds to: a kitty's encoded
    /// trait is `rate / reference_need_rate`, clamped to [0, 4] (documented
    /// bound). Default 1.0.
    #[serde(default = "default_reference_need_rate")]
    pub reference_need_rate: f32,
    /// Chow servings are encoded as `servings / max_chow_servings`, clamped
    /// to [0, 1]. Default 5 — the default `[elements.chow] servings`.
    #[serde(default = "default_max_chow_servings")]
    pub max_chow_servings: u32,
}

fn default_kitty_slots() -> usize {
    3
}
fn default_critter_slots() -> usize {
    4
}
fn default_chow_slots() -> usize {
    2
}
fn default_water_slots() -> usize {
    2
}
fn default_sunbeam_slots() -> usize {
    2
}
fn default_reference_need_rate() -> f32 {
    1.0
}
fn default_max_chow_servings() -> u32 {
    5
}

impl Default for ObservationConfig {
    fn default() -> Self {
        Self {
            kitty_slots: default_kitty_slots(),
            critter_slots: default_critter_slots(),
            chow_slots: default_chow_slots(),
            water_slots: default_water_slots(),
            sunbeam_slots: default_sunbeam_slots(),
            reference_need_rate: default_reference_need_rate(),
            max_chow_servings: default_max_chow_servings(),
        }
    }
}

/// `[rl.global_state]`: the privileged critic view's bounded element summary
/// (FR-019).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct GlobalStateConfig {
    /// Positions of the K nearest elements per type to the world center
    /// included in the summary. Default 2.
    #[serde(default = "default_elements_per_type")]
    pub elements_per_type: usize,
}

fn default_elements_per_type() -> usize {
    2
}

impl Default for GlobalStateConfig {
    fn default() -> Self {
        Self {
            elements_per_type: default_elements_per_type(),
        }
    }
}

/// `[rl.reward]` (FR-008/FR-009).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RewardConfig {
    /// Power-mean exponent. 1 = plain average, 0 = Nash welfare (geometric
    /// mean, the default), large negative → the least-happy kitty's score.
    /// Must be ≤ 1 (inequality-averse: concave).
    #[serde(default = "default_p")]
    pub p: f64,
    /// Offset keeping the aggregate and its gradient finite at zero
    /// happiness. Default 0.01; must be > 0.
    #[serde(default = "default_epsilon")]
    pub epsilon: f64,
    /// `level` (default): the welfare aggregate each step. `delta`: its
    /// change since the previous step.
    #[serde(default)]
    pub mode: RewardMode,
    /// Potential-based shaping (FR-009). Off by default.
    #[serde(default)]
    pub shaping: ShapingConfig,
}

fn default_p() -> f64 {
    0.0
}
fn default_epsilon() -> f64 {
    0.01
}

impl Default for RewardConfig {
    fn default() -> Self {
        Self {
            p: default_p(),
            epsilon: default_epsilon(),
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
pub struct ShapingConfig {
    #[serde(default)]
    pub enabled: bool,
    #[serde(default = "default_gamma")]
    pub gamma: f64,
    #[serde(default)]
    pub distress_coefficient: f64,
}

fn default_gamma() -> f64 {
    1.0
}

impl Default for ShapingConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            gamma: default_gamma(),
            distress_coefficient: 0.0,
        }
    }
}

/// `[rl.episode]` (FR-010).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct EpisodeConfig {
    /// Truncation horizon in ticks. Default 2000; must be ≥ 1.
    #[serde(default = "default_horizon")]
    pub horizon: u64,
}

fn default_horizon() -> u64 {
    2_000
}

impl Default for EpisodeConfig {
    fn default() -> Self {
        Self {
            horizon: default_horizon(),
        }
    }
}

/// `[rl.eval]` (FR-013): the harness defaults.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EvalConfig {
    /// Run length per seed. Default 20,000 — the long-run welfare horizon.
    #[serde(default = "default_eval_ticks")]
    pub ticks: u64,
    /// The fixed seed set. Default: the 10 fixed CI seeds 1..=10.
    #[serde(default = "default_eval_seeds")]
    pub seeds: Vec<u64>,
}

fn default_eval_ticks() -> u64 {
    20_000
}

fn default_eval_seeds() -> Vec<u64> {
    (1..=10).collect()
}

impl Default for EvalConfig {
    fn default() -> Self {
        Self {
            ticks: default_eval_ticks(),
            seeds: default_eval_seeds(),
        }
    }
}

/// One `[rl.policy.<name>]` block (FR-016).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PolicyConfig {
    /// Path to the policy artifact file.
    pub artifact: String,
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
        if self.reward.p > 1.0 || !self.reward.p.is_finite() {
            return Err(RlConfigError::invalid(
                "[rl.reward] p",
                self.reward.p.to_string(),
                "must be a finite exponent at most 1 (inequality-averse aggregation)",
            ));
        }
        if self.reward.epsilon <= 0.0 || !self.reward.epsilon.is_finite() {
            return Err(RlConfigError::invalid(
                "[rl.reward] epsilon",
                self.reward.epsilon.to_string(),
                "must be a finite number greater than 0",
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

        let err = RlConfig::from_toml_str("[rl.episode]\nhorizon = 0\n").unwrap_err();
        assert!(err.to_string().contains("[rl.episode] horizon"), "{err}");

        let err = RlConfig::from_toml_str("[rl.observation]\nkitty_slots = 0\n").unwrap_err();
        assert!(err.to_string().contains("kitty_slots"), "{err}");

        let err = RlConfig::from_toml_str("[rl.policy.broken]\nartifact = \"\"\n").unwrap_err();
        assert!(err.to_string().contains("[rl.policy.broken]"), "{err}");
    }
}
