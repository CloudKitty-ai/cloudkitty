//! Configuration and its validation.
//!
//! Every tunable number in CloudKitty lives here (Article VI: no magic numbers in
//! code). Validation is where the constitution meets the operator: a config that
//! would break Articles I-III is rejected at startup with an error naming the
//! field, the offending value, and the allowed range -- the world is never started
//! in a state where a kitty could come to harm.

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::element::ElementType;
use crate::grid::Position;
use crate::kitty::KittyId;
use crate::needs::NeedWeights;

/// Elements may occupy at most one tile in every `TILES_PER_ELEMENT`, which sets
/// the hard upper bound on each element type's population.
pub const TILES_PER_ELEMENT: u32 = 32;

#[derive(Debug, Error, Clone, PartialEq)]
pub enum ConfigError {
    #[error("config error: {field} is {value}; {expected}")]
    Invalid {
        field: String,
        value: String,
        expected: String,
    },
    #[error("config error: {0}")]
    Message(String),
}

impl ConfigError {
    fn invalid(
        field: impl Into<String>,
        value: impl Into<String>,
        expected: impl Into<String>,
    ) -> Self {
        ConfigError::Invalid {
            field: field.into(),
            value: value.into(),
            expected: expected.into(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Config {
    pub world: WorldConfig,
    #[serde(default)]
    pub persistence: PersistenceConfig,
    /// The kitty roster. TOML spells this `[[kitty]]`.
    #[serde(default, rename = "kitty")]
    pub kitties: Vec<KittyConfig>,
    #[serde(default)]
    pub needs: NeedsConfig,
    #[serde(default)]
    pub happiness: HappinessConfig,
    #[serde(default)]
    pub thresholds: ThresholdConfig,
    #[serde(default)]
    pub elements: ElementsConfig,
    #[serde(default)]
    pub actions: ActionEffects,
    #[serde(default)]
    pub meow: MeowConfig,
    #[serde(default)]
    pub behavior: BehaviorConfig,
    #[serde(default)]
    pub events: EventsConfig,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WorldConfig {
    pub width: u32,
    pub height: u32,
    pub tick_ms: u64,
    pub seed: u64,
    #[serde(default = "default_bind")]
    pub bind: String,
}

fn default_bind() -> String {
    "127.0.0.1:8090".to_string()
}

impl Default for WorldConfig {
    fn default() -> Self {
        Self {
            width: 32,
            height: 32,
            tick_ms: 800,
            seed: 20260718,
            bind: default_bind(),
        }
    }
}

impl WorldConfig {
    pub fn area(&self) -> u32 {
        self.width.saturating_mul(self.height)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistenceConfig {
    pub snapshot_path: String,
    pub save_every_ticks: u64,
}

impl Default for PersistenceConfig {
    fn default() -> Self {
        Self {
            snapshot_path: "snapshot.json".to_string(),
            save_every_ticks: 100,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KittyConfig {
    pub id: KittyId,
    pub name: String,
    pub x: u32,
    pub y: u32,
    pub behavior: String,
    /// Optional per-kitty overrides for need rise rates. Unset needs fall back
    /// to the global `[needs]` rates, so a config can say "Pumpkin is always
    /// hungry" without restating the other five.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub needs: Option<NeedRateOverrides>,
}

impl KittyConfig {
    pub fn position(&self) -> Position {
        Position::new(self.x, self.y)
    }
}

/// Per-kitty need-rate overrides; every field optional.
#[derive(Debug, Clone, Copy, PartialEq, Default, Serialize, Deserialize)]
pub struct NeedRateOverrides {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub eat: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drink: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sleep: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub play: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cuddle: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bath: Option<f32>,
}

impl NeedRateOverrides {
    pub fn get(&self, kind: crate::needs::NeedKind) -> Option<f32> {
        use crate::needs::NeedKind::*;
        match kind {
            Eat => self.eat,
            Drink => self.drink,
            Sleep => self.sleep,
            Play => self.play,
            Cuddle => self.cuddle,
            Bath => self.bath,
        }
    }
}

/// Per-tick rise rates for each need.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct NeedsConfig {
    pub eat: f32,
    pub drink: f32,
    pub sleep: f32,
    pub play: f32,
    pub cuddle: f32,
    pub bath: f32,
}

impl Default for NeedsConfig {
    fn default() -> Self {
        Self {
            eat: 0.5,
            drink: 0.7,
            sleep: 0.3,
            play: 0.4,
            cuddle: 0.25,
            bath: 0.2,
        }
    }
}

impl NeedsConfig {
    pub fn rate(&self, kind: crate::needs::NeedKind) -> f32 {
        use crate::needs::NeedKind::*;
        match kind {
            Eat => self.eat,
            Drink => self.drink,
            Sleep => self.sleep,
            Play => self.play,
            Cuddle => self.cuddle,
            Bath => self.bath,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct HappinessConfig {
    #[serde(default)]
    pub weights: NeedWeights,
    pub floor: f32,
}

impl Default for HappinessConfig {
    fn default() -> Self {
        Self {
            weights: NeedWeights::default(),
            floor: 5.0,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ThresholdConfig {
    /// A need at or above this records a distress event (Article I).
    pub distress: f32,
    /// A need above this obliges the world to provide relief (Article I).
    pub safeguard: f32,
    /// Happiness above this permits purring.
    pub purr: f32,
}

impl Default for ThresholdConfig {
    fn default() -> Self {
        Self {
            distress: 90.0,
            safeguard: 75.0,
            purr: 70.0,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ElementRule {
    pub min: u32,
    pub max: u32,
    /// Lifetime in ticks; `None` (absent) means permanent.
    #[serde(default)]
    pub ttl: Option<u64>,
    /// Chow only: servings per element.
    #[serde(default)]
    pub servings: Option<u32>,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ElementsConfig {
    pub water: ElementRule,
    pub chow: ElementRule,
    pub bug: ElementRule,
    pub greeble: ElementRule,
    pub sunbeam: ElementRule,
}

impl Default for ElementsConfig {
    fn default() -> Self {
        Self {
            // Generous by design: a kitty should never have to cross the whole
            // world for a drink. Sparser worlds are legal, just less kind.
            water: ElementRule {
                min: 5,
                max: 10,
                ttl: None,
                servings: None,
            },
            chow: ElementRule {
                min: 5,
                max: 10,
                ttl: None,
                servings: Some(5),
            },
            bug: ElementRule {
                min: 3,
                max: 8,
                ttl: Some(120),
                servings: None,
            },
            greeble: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(90),
                servings: None,
            },
            sunbeam: ElementRule {
                min: 3,
                max: 6,
                ttl: Some(150),
                servings: None,
            },
        }
    }
}

impl ElementsConfig {
    pub fn rule(&self, kind: ElementType) -> ElementRule {
        match kind {
            ElementType::Water => self.water,
            ElementType::Chow => self.chow,
            ElementType::Bug => self.bug,
            ElementType::Greeble => self.greeble,
            ElementType::Sunbeam => self.sunbeam,
        }
    }

    /// Greebles may be absent entirely; every other type must always have at least
    /// one instance so the world is never barren.
    pub fn hard_min(kind: ElementType) -> u32 {
        match kind {
            ElementType::Greeble => 0,
            _ => 1,
        }
    }

    pub fn hard_max(area: u32) -> u32 {
        area / TILES_PER_ELEMENT
    }

    pub fn total_min(&self) -> u32 {
        ElementType::ALL
            .iter()
            .map(|k| self.rule(*k).min)
            .fold(0u32, |a, b| a.saturating_add(b))
    }
}

/// How much each action relieves the need it addresses.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ActionEffects {
    pub eat_relief: f32,
    pub drink_relief: f32,
    pub sleep_relief: f32,
    pub sleep_relief_sunbeam: f32,
    pub groom_relief: f32,
    pub play_relief: f32,
    /// Cuddle relief from resting/sleeping/grooming alongside a friend.
    pub cuddle_relief: f32,
}

impl Default for ActionEffects {
    fn default() -> Self {
        Self {
            eat_relief: 40.0,
            drink_relief: 40.0,
            sleep_relief: 5.0,
            sleep_relief_sunbeam: 8.0,
            groom_relief: 30.0,
            play_relief: 25.0,
            cuddle_relief: 20.0,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct MeowConfig {
    pub cooldown_ticks: u64,
    pub urgent_cooldown_ticks: u64,
    pub urgent_need_threshold: f32,
    /// How long a meow stays visible to kitties and viewers.
    pub recent_window_ticks: u64,
}

impl Default for MeowConfig {
    fn default() -> Self {
        Self {
            cooldown_ticks: 15,
            urgent_cooldown_ticks: 5,
            urgent_need_threshold: 75.0,
            recent_window_ticks: 10,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BehaviorConfig {
    /// Share of a tick an *external* behavior may spend deciding. Built-in
    /// behaviors are exempt (see `behavior::gather_decisions`).
    pub budget_fraction_of_tick: f32,
    /// The pressure at which a `playful` kitty stops playing and attends to a
    /// need. Lower means a better-kept cat; higher means more single-minded fun.
    #[serde(default = "default_playful_comfort")]
    pub playful_comfort: f32,
}

fn default_playful_comfort() -> f32 {
    55.0
}

impl Default for BehaviorConfig {
    fn default() -> Self {
        Self {
            budget_fraction_of_tick: 0.5,
            playful_comfort: default_playful_comfort(),
        }
    }
}

impl BehaviorConfig {
    pub fn budget_ms(&self, tick_ms: u64) -> u64 {
        let ms = (tick_ms as f64 * self.budget_fraction_of_tick as f64).floor() as u64;
        ms.max(1)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct EventsConfig {
    pub distress_retention: usize,
}

impl Default for EventsConfig {
    fn default() -> Self {
        Self {
            distress_retention: 1000,
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            world: WorldConfig::default(),
            persistence: PersistenceConfig::default(),
            kitties: vec![
                KittyConfig {
                    id: 1,
                    name: "Miso".into(),
                    x: 10,
                    y: 12,
                    behavior: "needs_driven".into(),
                    needs: None,
                },
                KittyConfig {
                    id: 2,
                    name: "Biscuit".into(),
                    x: 20,
                    y: 18,
                    behavior: "playful".into(),
                    needs: None,
                },
                KittyConfig {
                    id: 3,
                    name: "Pumpkin".into(),
                    x: 16,
                    y: 8,
                    behavior: "needs_driven".into(),
                    needs: None,
                },
            ],
            needs: NeedsConfig::default(),
            happiness: HappinessConfig::default(),
            thresholds: ThresholdConfig::default(),
            elements: ElementsConfig::default(),
            actions: ActionEffects::default(),
            meow: MeowConfig::default(),
            behavior: BehaviorConfig::default(),
            events: EventsConfig::default(),
        }
    }
}

impl Config {
    /// Checks every rule the constitution and spec impose on configuration.
    ///
    /// Errors name the field, its value, and the allowed range so an operator can
    /// fix the file without reading the source.
    pub fn validate(&self) -> Result<(), ConfigError> {
        self.validate_world()?;
        self.validate_roster()?;
        self.validate_thresholds()?;
        self.validate_happiness()?;
        self.validate_needs()?;
        self.validate_elements()?;
        self.validate_behavior()?;
        self.validate_capacity()?;
        Ok(())
    }

    fn validate_world(&self) -> Result<(), ConfigError> {
        let w = &self.world;
        if w.width == 0 || w.height == 0 {
            return Err(ConfigError::invalid(
                "[world] width/height",
                format!("{}x{}", w.width, w.height),
                "both must be at least 1",
            ));
        }
        if w.tick_ms == 0 {
            return Err(ConfigError::invalid(
                "[world] tick_ms",
                w.tick_ms.to_string(),
                "must be greater than 0",
            ));
        }
        // Below this, `floor(area / 32)` is zero and no element type could reach its
        // hard minimum of one.
        if w.area() < TILES_PER_ELEMENT {
            return Err(ConfigError::invalid(
                "[world] width x height",
                format!("{} tiles", w.area()),
                format!(
                    "must be at least {TILES_PER_ELEMENT} tiles so each element type can exist"
                ),
            ));
        }
        Ok(())
    }

    fn validate_roster(&self) -> Result<(), ConfigError> {
        // Article III: kitties cannot be alone.
        if self.kitties.len() < 2 {
            return Err(ConfigError::invalid(
                "[[kitty]] roster",
                format!("{} kitties", self.kitties.len()),
                "the constitution requires at least 2 kitties (Article III: kitties cannot be alone)",
            ));
        }

        let mut seen_ids = std::collections::BTreeSet::new();
        let mut seen_positions = std::collections::BTreeSet::new();
        for k in &self.kitties {
            if !seen_ids.insert(k.id) {
                return Err(ConfigError::invalid(
                    "[[kitty]] id",
                    k.id.to_string(),
                    "kitty ids must be unique",
                ));
            }
            if !k.position().in_bounds(self.world.width, self.world.height) {
                return Err(ConfigError::invalid(
                    format!("[[kitty]] '{}' position", k.name),
                    format!("({}, {})", k.x, k.y),
                    format!(
                        "must be within the world: x in 0..{}, y in 0..{}",
                        self.world.width, self.world.height
                    ),
                ));
            }
            if !seen_positions.insert((k.x, k.y)) {
                return Err(ConfigError::invalid(
                    format!("[[kitty]] '{}' position", k.name),
                    format!("({}, {})", k.x, k.y),
                    "two kitties may not start on the same tile",
                ));
            }
            if k.behavior.trim().is_empty() {
                return Err(ConfigError::invalid(
                    format!("[[kitty]] '{}' behavior", k.name),
                    "empty".to_string(),
                    "must name a registered behavior, e.g. \"needs_driven\"",
                ));
            }
        }
        Ok(())
    }

    fn validate_thresholds(&self) -> Result<(), ConfigError> {
        let t = &self.thresholds;
        for (field, value) in [
            ("[thresholds] distress", t.distress),
            ("[thresholds] safeguard", t.safeguard),
            ("[thresholds] purr", t.purr),
        ] {
            if !(0.0..=100.0).contains(&value) || value.is_nan() {
                return Err(ConfigError::invalid(
                    field,
                    value.to_string(),
                    "must be between 0 and 100",
                ));
            }
        }
        // Relief must arrive before distress is even recorded, or the safeguard
        // would be pointless.
        if t.safeguard >= t.distress {
            return Err(ConfigError::invalid(
                "[thresholds] safeguard",
                t.safeguard.to_string(),
                format!(
                    "must be below [thresholds] distress ({}) so relief arrives before distress",
                    t.distress
                ),
            ));
        }
        Ok(())
    }

    fn validate_happiness(&self) -> Result<(), ConfigError> {
        let h = &self.happiness;
        // Article I: happiness can never reach zero, so the floor must be above it.
        if !(h.floor > 0.0 && h.floor < 100.0) {
            return Err(ConfigError::invalid(
                "[happiness] floor",
                h.floor.to_string(),
                "must be greater than 0 and less than 100 (Article I: happiness can never reach zero)",
            ));
        }
        let sum = h.weights.sum();
        if (sum - 1.0).abs() > 1e-3 {
            return Err(ConfigError::invalid(
                "[happiness.weights]",
                format!("sum {sum}"),
                "the six weights must sum to 1.0",
            ));
        }
        for kind in crate::needs::NeedKind::ALL {
            let w = h.weights.get(kind);
            if w < 0.0 || w.is_nan() {
                return Err(ConfigError::invalid(
                    format!("[happiness.weights] {}", kind.as_str()),
                    w.to_string(),
                    "must not be negative",
                ));
            }
        }
        Ok(())
    }

    fn validate_needs(&self) -> Result<(), ConfigError> {
        for kind in crate::needs::NeedKind::ALL {
            let rate = self.needs.rate(kind);
            if rate < 0.0 || rate.is_nan() {
                return Err(ConfigError::invalid(
                    format!("[needs] {}", kind.as_str()),
                    rate.to_string(),
                    "must not be negative (needs rise, they do not fall on their own)",
                ));
            }
        }
        // Per-kitty overrides obey the same rule as the globals they replace.
        for kitty in &self.kitties {
            let Some(overrides) = &kitty.needs else {
                continue;
            };
            for kind in crate::needs::NeedKind::ALL {
                if let Some(rate) = overrides.get(kind) {
                    if rate < 0.0 || rate.is_nan() {
                        return Err(ConfigError::invalid(
                            format!("[kitty.needs] {} for '{}'", kind.as_str(), kitty.name),
                            rate.to_string(),
                            "must not be negative (needs rise, they do not fall on their own)",
                        ));
                    }
                }
            }
        }
        Ok(())
    }

    /// The effective rise rate for one kitty's need: its own override when set,
    /// the global `[needs]` rate otherwise. Unknown ids get the global rate, so
    /// this can never make a kitty's needs behave differently than configured.
    pub fn need_rate_for(&self, kitty_id: KittyId, kind: crate::needs::NeedKind) -> f32 {
        self.kitties
            .iter()
            .find(|k| k.id == kitty_id)
            .and_then(|k| k.needs.as_ref())
            .and_then(|o| o.get(kind))
            .unwrap_or_else(|| self.needs.rate(kind))
    }

    fn validate_elements(&self) -> Result<(), ConfigError> {
        let area = self.world.area();
        let hard_max = ElementsConfig::hard_max(area);
        for kind in ElementType::ALL {
            let rule = self.elements.rule(kind);
            let hard_min = ElementsConfig::hard_min(kind);
            let field = format!("[elements.{}]", kind.as_str());

            if rule.min < hard_min {
                return Err(ConfigError::invalid(
                    format!("{field} min"),
                    rule.min.to_string(),
                    format!("must be at least {hard_min} for this element type"),
                ));
            }
            if rule.max > hard_max {
                return Err(ConfigError::invalid(
                    format!("{field} max"),
                    rule.max.to_string(),
                    format!(
                        "must be at most {hard_max} (floor(area / {TILES_PER_ELEMENT}) for a {}x{} world)",
                        self.world.width, self.world.height
                    ),
                ));
            }
            if rule.min > rule.max {
                return Err(ConfigError::invalid(
                    format!("{field} min"),
                    rule.min.to_string(),
                    format!("must not exceed max ({})", rule.max),
                ));
            }
            if matches!(kind, ElementType::Chow) {
                let servings = rule.servings.unwrap_or(0);
                if servings == 0 {
                    return Err(ConfigError::invalid(
                        "[elements.chow] servings",
                        servings.to_string(),
                        "must be at least 1",
                    ));
                }
            }
            if let Some(0) = rule.ttl {
                return Err(ConfigError::invalid(
                    format!("{field} ttl"),
                    "0".to_string(),
                    "must be at least 1 tick, or omitted for a permanent element",
                ));
            }
        }
        Ok(())
    }

    fn validate_behavior(&self) -> Result<(), ConfigError> {
        let f = self.behavior.budget_fraction_of_tick;
        // The budget must leave room for the rest of the tick's work.
        if !(f > 0.0 && f < 1.0) {
            return Err(ConfigError::invalid(
                "[behavior] budget_fraction_of_tick",
                f.to_string(),
                "must be greater than 0 and less than 1 (the decision budget must be shorter than a tick)",
            ));
        }
        let comfort = self.behavior.playful_comfort;
        if !(comfort > 0.0 && comfort <= 100.0) || comfort.is_nan() {
            return Err(ConfigError::invalid(
                "[behavior] playful_comfort",
                comfort.to_string(),
                "must be greater than 0 and at most 100",
            ));
        }
        if self.events.distress_retention == 0 {
            return Err(ConfigError::invalid(
                "[events] distress_retention",
                "0".to_string(),
                "must be at least 1",
            ));
        }
        if self.persistence.save_every_ticks == 0 {
            return Err(ConfigError::invalid(
                "[persistence] save_every_ticks",
                "0".to_string(),
                "must be at least 1",
            ));
        }
        Ok(())
    }

    /// The world must physically fit its inhabitants: one tile per kitty, and one
    /// tile per element at minimum population.
    fn validate_capacity(&self) -> Result<(), ConfigError> {
        let area = self.world.area();
        let kitty_count = self.kitties.len() as u32;
        if kitty_count > area {
            return Err(ConfigError::invalid(
                "[[kitty]] roster",
                format!("{kitty_count} kitties"),
                format!("must not exceed the {area} tiles in the world"),
            ));
        }
        let element_min = self.elements.total_min();
        if element_min > area {
            return Err(ConfigError::invalid(
                "[elements] combined minimums",
                element_min.to_string(),
                format!("must not exceed the {area} tiles in the world"),
            ));
        }
        Ok(())
    }

    /// Confirms every configured behavior name is registered. Called once the
    /// behavior registry is known.
    pub fn validate_behavior_names(&self, known: &[String]) -> Result<(), ConfigError> {
        for k in &self.kitties {
            if !known.iter().any(|n| n == &k.behavior) {
                let mut names = known.to_vec();
                names.sort();
                return Err(ConfigError::invalid(
                    format!("[[kitty]] '{}' behavior", k.name),
                    k.behavior.clone(),
                    format!("must be one of: {}", names.join(", ")),
                ));
            }
        }
        Ok(())
    }

    /// Identifies the settings a saved world must agree with to be resumable.
    pub fn fingerprint(&self) -> String {
        let mut ids: Vec<String> = self.kitties.iter().map(|k| k.id.to_string()).collect();
        ids.sort();
        format!(
            "w{}h{}s{}k{}",
            self.world.width,
            self.world.height,
            self.world.seed,
            ids.join(".")
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cfg() -> Config {
        Config::default()
    }

    #[test]
    fn the_shipped_default_config_is_valid() {
        cfg().validate().expect("default config must be valid");
    }

    #[test]
    fn fewer_than_two_kitties_is_rejected() {
        let mut c = cfg();
        c.kitties.truncate(1);
        let err = c.validate().unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("1 kitties"), "names the value: {msg}");
        assert!(msg.contains("at least 2"), "names the range: {msg}");
        assert!(msg.contains("Article III"), "cites the constitution: {msg}");
    }

    #[test]
    fn zero_kitties_is_rejected() {
        let mut c = cfg();
        c.kitties.clear();
        assert!(c.validate().is_err());
    }

    #[test]
    fn duplicate_kitty_ids_are_rejected() {
        let mut c = cfg();
        c.kitties[1].id = c.kitties[0].id;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("unique"), "{msg}");
    }

    #[test]
    fn duplicate_starting_positions_are_rejected() {
        let mut c = cfg();
        c.kitties[1].x = c.kitties[0].x;
        c.kitties[1].y = c.kitties[0].y;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("same tile"), "{msg}");
    }

    #[test]
    fn off_grid_positions_are_rejected() {
        let mut c = cfg();
        c.kitties[0].x = c.world.width;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("within the world"), "{msg}");
    }

    #[test]
    fn element_max_above_the_hard_bound_is_rejected() {
        let mut c = cfg();
        // 32x32 = 1024 tiles => hard max 32.
        c.elements.bug.max = ElementsConfig::hard_max(c.world.area()) + 1;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("at most 32"), "names the allowed range: {msg}");
    }

    #[test]
    fn element_min_below_the_hard_bound_is_rejected() {
        let mut c = cfg();
        c.elements.water.min = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("at least 1"), "{msg}");
    }

    #[test]
    fn greebles_may_be_absent_entirely() {
        let mut c = cfg();
        c.elements.greeble.min = 0;
        c.validate().expect("greebles are allowed to have min 0");
    }

    #[test]
    fn min_above_max_is_rejected() {
        let mut c = cfg();
        c.elements.sunbeam.min = 3;
        c.elements.sunbeam.max = 2;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("not exceed max"), "{msg}");
    }

    #[test]
    fn safeguard_at_or_above_distress_is_rejected() {
        let mut c = cfg();
        c.thresholds.safeguard = c.thresholds.distress;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("below"), "{msg}");
    }

    #[test]
    fn a_budget_at_or_over_one_tick_is_rejected() {
        let mut c = cfg();
        c.behavior.budget_fraction_of_tick = 1.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("less than 1"), "{msg}");

        c.behavior.budget_fraction_of_tick = 0.0;
        assert!(c.validate().is_err());
    }

    #[test]
    fn weights_that_do_not_sum_to_one_are_rejected() {
        let mut c = cfg();
        c.happiness.weights.eat = 0.9;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("sum to 1.0"), "{msg}");
    }

    #[test]
    fn a_zero_happiness_floor_is_rejected() {
        let mut c = cfg();
        c.happiness.floor = 0.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("Article I"), "cites the constitution: {msg}");
    }

    #[test]
    fn worlds_too_small_for_their_elements_are_rejected() {
        let mut c = cfg();
        c.world.width = 4;
        c.world.height = 4; // 16 tiles: floor(16/32) == 0
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("at least 32 tiles"), "{msg}");
    }

    #[test]
    fn zero_tick_rate_is_rejected() {
        let mut c = cfg();
        c.world.tick_ms = 0;
        assert!(c.validate().is_err());
    }

    #[test]
    fn unknown_behavior_names_are_rejected() {
        let mut c = cfg();
        c.kitties[0].behavior = "telepathic".into();
        let known = vec!["needs_driven".to_string(), "playful".to_string()];
        let msg = c.validate_behavior_names(&known).unwrap_err().to_string();
        assert!(msg.contains("telepathic"), "{msg}");
        assert!(msg.contains("needs_driven"), "lists valid names: {msg}");
    }

    #[test]
    fn per_kitty_overrides_take_precedence_over_globals() {
        let mut c = cfg();
        c.kitties[0].needs = Some(NeedRateOverrides {
            eat: Some(2.0),
            ..Default::default()
        });
        c.validate().expect("overrides are valid config");

        use crate::needs::NeedKind;
        let overridden = c.kitties[0].id;
        let plain = c.kitties[1].id;
        assert_eq!(c.need_rate_for(overridden, NeedKind::Eat), 2.0);
        // Unset needs on the same kitty fall back to the global rate.
        assert_eq!(c.need_rate_for(overridden, NeedKind::Drink), c.needs.drink);
        // Other kitties are untouched.
        assert_eq!(c.need_rate_for(plain, NeedKind::Eat), c.needs.eat);
        // Unknown ids get globals, never a panic.
        assert_eq!(c.need_rate_for(9_999, NeedKind::Eat), c.needs.eat);
    }

    #[test]
    fn negative_per_kitty_overrides_are_rejected() {
        let mut c = cfg();
        c.kitties[1].needs = Some(NeedRateOverrides {
            sleep: Some(-0.1),
            ..Default::default()
        });
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[kitty.needs] sleep"), "{msg}");
        assert!(msg.contains(&c.kitties[1].name), "names the kitty: {msg}");
    }

    #[test]
    fn per_kitty_overrides_parse_from_toml() {
        let toml_src = r#"
            [world]
            width = 16
            height = 16
            tick_ms = 800
            seed = 1

            [[kitty]]
            id = 1
            name = "Hungry"
            x = 1
            y = 1
            behavior = "needs_driven"
            [kitty.needs]
            eat = 1.5

            [[kitty]]
            id = 2
            name = "Plain"
            x = 2
            y = 2
            behavior = "playful"
        "#;
        let c: Config = toml::from_str(toml_src).expect("parses");
        assert_eq!(c.kitties[0].needs.unwrap().eat, Some(1.5));
        assert_eq!(c.kitties[0].needs.unwrap().drink, None);
        assert!(c.kitties[1].needs.is_none());
    }

    #[test]
    fn budget_ms_scales_with_the_tick() {
        let b = BehaviorConfig {
            budget_fraction_of_tick: 0.5,
            ..BehaviorConfig::default()
        };
        assert_eq!(b.budget_ms(800), 400);
        assert_eq!(b.budget_ms(100), 50);
        // Never zero, even for very fast ticks.
        assert_eq!(b.budget_ms(1), 1);
    }

    #[test]
    fn fingerprint_changes_with_world_shape() {
        let a = cfg();
        let mut b = cfg();
        b.world.width = 40;
        assert_ne!(a.fingerprint(), b.fingerprint());
    }
}
