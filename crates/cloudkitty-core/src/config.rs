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
    pub purr: PurrConfig,
    #[serde(default)]
    pub events: EventsConfig,
    #[serde(default)]
    pub viewer: ViewerConfig,
}

/// The rhythm of a sustained purr (spec 011). Purring is engine-owned kitty
/// state -- earned by happiness, never proposed, never a spent turn -- and
/// these three numbers give the rumble its wave shape: a seeded draw between
/// `min_ticks` and `max_ticks`, then `cooldown_ticks` of rest.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PurrConfig {
    /// Shortest purr, in ticks. Must be at least 1 and at most `max_ticks`.
    #[serde(default = "default_purr_min_ticks")]
    pub min_ticks: u64,
    /// Longest purr, in ticks.
    #[serde(default = "default_purr_max_ticks")]
    pub max_ticks: u64,
    /// Rest between purrs, in ticks. 0 is legal: back-to-back rumbles.
    #[serde(default = "default_purr_cooldown_ticks")]
    pub cooldown_ticks: u64,
}

fn default_purr_min_ticks() -> u64 {
    6
}

fn default_purr_max_ticks() -> u64 {
    15
}

fn default_purr_cooldown_ticks() -> u64 {
    30
}

impl Default for PurrConfig {
    fn default() -> Self {
        Self {
            min_ticks: default_purr_min_ticks(),
            max_ticks: default_purr_max_ticks(),
            cooldown_ticks: default_purr_cooldown_ticks(),
        }
    }
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
            // Long, unhurried lifetimes (owner call 2026-07-23): a calmer
            // world is kinder to watch and to learn in (RL agents see fewer
            // targets vanish mid-plan). Staggered respawns come from the
            // spawn-time TTL jitter (spawn.rs), not from fast churn.
            bug: ElementRule {
                min: 3,
                max: 8,
                ttl: Some(300),
                servings: None,
            },
            greeble: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(300),
                servings: None,
            },
            sunbeam: ElementRule {
                min: 3,
                max: 6,
                ttl: Some(300),
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
    /// Play relief for pouncing at nothing. Smaller than `play_relief` so a
    /// kitty with company always prefers the real thing.
    #[serde(default = "default_solo_play_relief")]
    pub solo_play_relief: f32,
    /// How long each activity runs, in ticks (spec 006): the engine holds an
    /// activity at least `min` ticks and never lets it pass `max`.
    #[serde(default)]
    pub durations: DurationsConfig,
}

fn default_solo_play_relief() -> f32 {
    10.0
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
            solo_play_relief: default_solo_play_relief(),
            durations: DurationsConfig::default(),
        }
    }
}

/// Bounds on how long one activity may run, in ticks, inclusive of the tick
/// it starts on. Relief applies on every tick, so `min` also sets the least
/// relief an undertaking delivers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct DurationBounds {
    pub min: u64,
    pub max: u64,
}

impl DurationBounds {
    pub const fn new(min: u64, max: u64) -> Self {
        Self { min, max }
    }
}

/// Per-activity duration bounds (`[actions.durations]`). Keys are named for
/// the need-facing activity: `bath` governs grooming and `cuddle` governs
/// resting, solo or duet.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct DurationsConfig {
    #[serde(default = "default_short_activity")]
    pub eat: DurationBounds,
    #[serde(default = "default_short_activity")]
    pub drink: DurationBounds,
    #[serde(default = "default_short_activity")]
    pub play: DurationBounds,
    #[serde(default = "default_short_activity")]
    pub bath: DurationBounds,
    #[serde(default = "default_long_activity")]
    pub sleep: DurationBounds,
    #[serde(default = "default_long_activity")]
    pub cuddle: DurationBounds,
}

fn default_short_activity() -> DurationBounds {
    DurationBounds::new(2, 5)
}

fn default_long_activity() -> DurationBounds {
    // Min raised 2 -> 3 once the 005 animations made durations visible:
    // a nap or cuddle worth watching holds for at least three ticks
    // (owner tuning, 2026-07-20; spec 006 defaults amended in step).
    DurationBounds::new(3, 8)
}

impl Default for DurationsConfig {
    fn default() -> Self {
        Self {
            eat: default_short_activity(),
            drink: default_short_activity(),
            play: default_short_activity(),
            bath: default_short_activity(),
            sleep: default_long_activity(),
            cuddle: default_long_activity(),
        }
    }
}

impl DurationsConfig {
    pub fn all(&self) -> [(&'static str, DurationBounds); 6] {
        [
            ("eat", self.eat),
            ("drink", self.drink),
            ("play", self.play),
            ("bath", self.bath),
            ("sleep", self.sleep),
            ("cuddle", self.cuddle),
        ]
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
    /// Extra selection weight per point of pressure above the safeguard
    /// threshold. Urgent needs dominate similarly-distant alternatives without
    /// ever locking out zero-distance relief.
    #[serde(default = "default_urgency_weight")]
    pub urgency_weight: f32,
    /// How many need-points one tile of travel is worth when choosing what to
    /// attend to.
    #[serde(default = "default_tile_cost")]
    pub tile_cost: f32,
    /// Extra tiles of effort a kitty ascribes to stepping onto a water tile
    /// (spec 010). Dry routes win when they cost less than the splash; a kitty
    /// still wades when water is the only way forward -- this is preference in
    /// the behaviors, never a rule in the engine (Article IV). 0 disables it.
    #[serde(default = "default_water_step_cost")]
    pub water_step_cost: f32,
    /// A need at or above this is worth topping up when the means are already
    /// underfoot, whatever else the kitty was doing.
    #[serde(default = "default_worth_a_detour")]
    pub worth_a_detour: f32,
    /// Elapsed ticks a chase may run without closing distance before its target
    /// stops counting as catchable.
    #[serde(default = "default_chase_patience_ticks")]
    pub chase_patience_ticks: u64,
    /// How long an abandoned chase target stays excluded from re-selection.
    #[serde(default = "default_chase_exclusion_ticks")]
    pub chase_exclusion_ticks: u64,
    /// A viable playmate within this distance suppresses solo play; beyond it,
    /// a kitty entertains itself.
    #[serde(default = "default_solo_play_reach")]
    pub solo_play_reach: u32,
    /// A sunbeam within this distance is worth walking to for a nap; farther
    /// than this (or with no sunbeam at all), a kitty sleeps where it is.
    /// Prices the sleep score and bounds the sleep walk in the same breath.
    #[serde(default = "default_sunbeam_reach")]
    pub sunbeam_reach: u32,
    /// Consecutive budget timeouts (counted per kitty) after which that
    /// kitty's external advisor dispatch is benched — the kitty uses the
    /// fallback and no further work is spawned for it until the bench
    /// expires (spec 014 review: bounds the threads a wedged advisor can
    /// strand at `budget_strikes` per bench window, instead of one per
    /// tick forever).
    #[serde(default = "default_budget_strikes")]
    pub budget_strikes: u32,
    /// How many ticks a bench lasts. On expiry the streak resets and
    /// dispatch is tried again — an advisor that recovered comes back on
    /// its own, one that is still wedged re-benches after another
    /// `budget_strikes` timeouts.
    #[serde(default = "default_bench_ticks")]
    pub bench_ticks: u64,
    /// Cap on one plugin reply line, in bytes (spec 016). A reply beyond it
    /// is a failed proposal and kills the plugin process — the stream is
    /// mid-line and unrecoverable. A real proposal envelope is under 200
    /// bytes; the default (64 KiB) is three orders of magnitude of headroom
    /// while keeping "a plugin cannot exhaust engine memory by talking"
    /// literal. Default: 65536.
    #[serde(default = "default_reply_max_bytes")]
    pub reply_max_bytes: usize,
    /// Minimum ticks between spawn attempts for a dead plugin process
    /// (spec 016). A crash-looping program costs its kitty cleverness at a
    /// bounded spawn rate, never a spawn storm. Default: 20.
    #[serde(default = "default_relaunch_cooldown_ticks")]
    pub relaunch_cooldown_ticks: u64,
    /// Hard wall-clock deadline on one plugin exchange, in milliseconds
    /// (spec 016, review remediation). This is the plugin transport's own
    /// containment — carried inside `ScriptBehavior`, so it bounds the
    /// exchange on *every* dispatch path, including the budgetless one the
    /// served budget never covers. A reply that misses the deadline is a
    /// failed proposal and kills the process (a silently wedged program
    /// must never strand a thread or stall a headless driver). Wall clock
    /// here cannot touch Article V: determinism is scoped to built-in
    /// behaviors, and this deadline exists only inside the external
    /// transport. Default: 1000.
    #[serde(default = "default_exchange_timeout_ms")]
    pub exchange_timeout_ms: u64,
}

fn default_playful_comfort() -> f32 {
    55.0
}

fn default_urgency_weight() -> f32 {
    2.0
}

fn default_tile_cost() -> f32 {
    1.0
}

fn default_water_step_cost() -> f32 {
    4.0
}

fn default_worth_a_detour() -> f32 {
    30.0
}

fn default_chase_patience_ticks() -> u64 {
    12
}

fn default_chase_exclusion_ticks() -> u64 {
    60
}

fn default_solo_play_reach() -> u32 {
    8
}

fn default_sunbeam_reach() -> u32 {
    8
}

fn default_budget_strikes() -> u32 {
    5
}

fn default_bench_ticks() -> u64 {
    300
}

fn default_reply_max_bytes() -> usize {
    65536
}

fn default_relaunch_cooldown_ticks() -> u64 {
    20
}

fn default_exchange_timeout_ms() -> u64 {
    1000
}

impl Default for BehaviorConfig {
    fn default() -> Self {
        Self {
            budget_fraction_of_tick: 0.5,
            playful_comfort: default_playful_comfort(),
            urgency_weight: default_urgency_weight(),
            tile_cost: default_tile_cost(),
            water_step_cost: default_water_step_cost(),
            worth_a_detour: default_worth_a_detour(),
            chase_patience_ticks: default_chase_patience_ticks(),
            chase_exclusion_ticks: default_chase_exclusion_ticks(),
            solo_play_reach: default_solo_play_reach(),
            sunbeam_reach: default_sunbeam_reach(),
            budget_strikes: default_budget_strikes(),
            bench_ticks: default_bench_ticks(),
            reply_max_bytes: default_reply_max_bytes(),
            relaunch_cooldown_ticks: default_relaunch_cooldown_ticks(),
            exchange_timeout_ms: default_exchange_timeout_ms(),
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
    /// How many finished-activity events the world remembers (spec 006):
    /// each carries the true tick span a scene ran, which served snapshots
    /// alone cannot show (the final tick clears the clock it stamped).
    #[serde(default = "default_activity_retention")]
    pub activity_retention: usize,
}

fn default_activity_retention() -> usize {
    1000
}

impl Default for EventsConfig {
    fn default() -> Self {
        Self {
            distress_retention: 1000,
            activity_retention: default_activity_retention(),
        }
    }
}

/// Constants the *viewer* reads via `/config`. The simulation never consults
/// this section — it exists so client tunables are still real configuration
/// (Article VI) without the client computing anything (Article V).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ViewerConfig {
    /// Unresolved-distress age, in ticks, before a kitty's card shows its
    /// gentle "has wanted this for a while" cue.
    pub distress_patience_ticks: u64,
}

impl Default for ViewerConfig {
    fn default() -> Self {
        Self {
            distress_patience_ticks: 60,
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
            purr: PurrConfig::default(),
            events: EventsConfig::default(),
            viewer: ViewerConfig::default(),
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
        self.validate_durations()?;
        self.validate_capacity()?;
        Ok(())
    }

    /// Spec 006: every activity's duration bounds must satisfy 1 <= min <= max.
    fn validate_durations(&self) -> Result<(), ConfigError> {
        for (name, bounds) in self.actions.durations.all() {
            if bounds.min < 1 {
                return Err(ConfigError::invalid(
                    format!("[actions.durations] {name}.min"),
                    bounds.min.to_string(),
                    "an activity runs at least 1 tick (1 <= min <= max)",
                ));
            }
            if bounds.max < bounds.min {
                return Err(ConfigError::invalid(
                    format!("[actions.durations] {name}.max"),
                    bounds.max.to_string(),
                    format!("must be at least {name}.min ({})", bounds.min),
                ));
            }
        }
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
            if k.id == crate::kitty::RESERVED_KITTY_ID {
                return Err(ConfigError::invalid(
                    "[[kitty]] id",
                    k.id.to_string(),
                    "this id is reserved (spec 014: downstream encodings use it to \
                     mean \"no kitty\", so no live kitty may ever carry it)",
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
        if self.purr.min_ticks < 1 {
            return Err(ConfigError::invalid(
                "[purr] min_ticks",
                self.purr.min_ticks.to_string(),
                "must be at least 1",
            ));
        }
        if self.purr.min_ticks > self.purr.max_ticks {
            return Err(ConfigError::invalid(
                "[purr] min_ticks",
                format!(
                    "{} (max_ticks is {})",
                    self.purr.min_ticks, self.purr.max_ticks
                ),
                "must be at most max_ticks",
            ));
        }
        for (field, value) in [
            ("[behavior] urgency_weight", self.behavior.urgency_weight),
            ("[behavior] tile_cost", self.behavior.tile_cost),
            ("[behavior] water_step_cost", self.behavior.water_step_cost),
        ] {
            if !value.is_finite() || value < 0.0 {
                return Err(ConfigError::invalid(
                    field,
                    value.to_string(),
                    "must be a finite number of at least 0",
                ));
            }
        }
        let detour = self.behavior.worth_a_detour;
        if !(0.0..=100.0).contains(&detour) || detour.is_nan() {
            return Err(ConfigError::invalid(
                "[behavior] worth_a_detour",
                detour.to_string(),
                "must be between 0 and 100",
            ));
        }
        for (field, value) in [
            (
                "[behavior] chase_patience_ticks",
                self.behavior.chase_patience_ticks,
            ),
            (
                "[behavior] chase_exclusion_ticks",
                self.behavior.chase_exclusion_ticks,
            ),
        ] {
            if value == 0 {
                return Err(ConfigError::invalid(
                    field,
                    "0".to_string(),
                    "must be at least 1 tick",
                ));
            }
        }
        // One row per nonzero-bounded field: `(field, value, expected)`,
        // message bytes verbatim per row (spec 020 D2 — the loop owns only
        // the if/return shape; a new bounded field is a new row).
        for (field, value, expected) in [
            (
                "[behavior] solo_play_reach",
                self.behavior.solo_play_reach as u64,
                "must be at least 1 tile",
            ),
            (
                "[behavior] sunbeam_reach",
                self.behavior.sunbeam_reach as u64,
                "must be at least 1 tile",
            ),
            (
                "[behavior] budget_strikes",
                self.behavior.budget_strikes as u64,
                "must be at least 1 (an advisor gets at least one timed slot)",
            ),
            (
                "[behavior] bench_ticks",
                self.behavior.bench_ticks,
                "must be at least 1 tick (a bench must last long enough to exist)",
            ),
            (
                "[behavior] reply_max_bytes",
                self.behavior.reply_max_bytes as u64,
                "must be at least 1 byte (a plugin must be allowed to answer)",
            ),
            (
                "[behavior] relaunch_cooldown_ticks",
                self.behavior.relaunch_cooldown_ticks,
                "must be at least 1 tick (unbounded respawn would be a spawn storm)",
            ),
            (
                "[behavior] exchange_timeout_ms",
                self.behavior.exchange_timeout_ms,
                "must be at least 1 ms (a plugin must have a moment to answer)",
            ),
        ] {
            if value == 0 {
                return Err(ConfigError::invalid(field, "0".to_string(), expected));
            }
        }
        let solo = self.actions.solo_play_relief;
        if !solo.is_finite() || solo < 0.0 {
            return Err(ConfigError::invalid(
                "[actions] solo_play_relief",
                solo.to_string(),
                "must be a finite number of at least 0",
            ));
        }
        if solo > self.actions.play_relief {
            return Err(ConfigError::invalid(
                "[actions] solo_play_relief",
                solo.to_string(),
                format!(
                    "must not exceed play_relief ({}) -- playing together must stay the better deal",
                    self.actions.play_relief
                ),
            ));
        }
        // Same row shape as the behavior table above (spec 020 D2).
        for (field, value, expected) in [
            (
                "[viewer] distress_patience_ticks",
                self.viewer.distress_patience_ticks,
                "must be at least 1 tick",
            ),
            (
                "[events] distress_retention",
                self.events.distress_retention as u64,
                "must be at least 1",
            ),
            (
                "[events] activity_retention",
                self.events.activity_retention as u64,
                "must be at least 1",
            ),
            (
                "[persistence] save_every_ticks",
                self.persistence.save_every_ticks,
                "must be at least 1",
            ),
        ] {
            if value == 0 {
                return Err(ConfigError::invalid(field, "0".to_string(), expected));
            }
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
    fn the_reserved_kitty_id_is_rejected() {
        // Spec 014 review: u32::MAX is the action codec's vacant-slot
        // sentinel; a live kitty carrying it would turn every vacant menu
        // entry into a real proposal against that kitty.
        let mut c = cfg();
        c.kitties[0].id = u32::MAX;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("reserved"), "{msg}");
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
    fn negative_urgency_weight_is_rejected() {
        let mut c = cfg();
        c.behavior.urgency_weight = -0.5;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[behavior] urgency_weight"), "{msg}");
        assert!(msg.contains("-0.5"), "names the value: {msg}");
    }

    #[test]
    fn negative_tile_cost_is_rejected() {
        let mut c = cfg();
        c.behavior.tile_cost = f32::NAN;
        assert!(c.validate().is_err());
        c.behavior.tile_cost = -1.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[behavior] tile_cost"), "{msg}");
    }

    #[test]
    fn purr_table_defaults_when_absent_and_rejects_bad_bounds() {
        // A pre-011 config has no [purr] section at all: the whole-table
        // default must land (spec 011 SC-005).
        let parsed: PurrConfig = toml::from_str("").expect("an empty purr table parses");
        assert_eq!(
            (parsed.min_ticks, parsed.max_ticks, parsed.cooldown_ticks),
            (6, 15, 30)
        );

        let mut c = cfg();
        c.purr.min_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] min_ticks"), "{msg}");
        c.purr.min_ticks = 20; // > max_ticks 15
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] min_ticks"), "{msg}");
        assert!(msg.contains("max_ticks"), "{msg}");
        c.purr.min_ticks = c.purr.max_ticks; // fixed-length purrs are legal
        c.purr.cooldown_ticks = 0; // as are back-to-back rumbles
        assert!(c.validate().is_ok());
    }

    #[test]
    fn water_step_cost_defaults_when_absent_and_rejects_nonsense() {
        // A pre-010 [behavior] table has no water_step_cost: the serde
        // default must land, so every existing config file keeps working
        // unedited (spec 010 SC-005).
        let parsed: BehaviorConfig =
            toml::from_str("budget_fraction_of_tick = 0.5").expect("pre-010 table parses");
        assert_eq!(parsed.water_step_cost, 4.0);

        let mut c = cfg();
        c.behavior.water_step_cost = f32::NAN;
        assert!(c.validate().is_err());
        c.behavior.water_step_cost = -1.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[behavior] water_step_cost"), "{msg}");
        c.behavior.water_step_cost = 0.0; // legal: disables the preference
        assert!(c.validate().is_ok());
    }

    #[test]
    fn worth_a_detour_outside_need_range_is_rejected() {
        let mut c = cfg();
        c.behavior.worth_a_detour = 101.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("worth_a_detour"), "{msg}");
        assert!(msg.contains("between 0 and 100"), "{msg}");
    }

    #[test]
    fn zero_chase_windows_are_rejected() {
        let mut c = cfg();
        c.behavior.chase_patience_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("chase_patience_ticks"), "{msg}");

        let mut c = cfg();
        c.behavior.chase_exclusion_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("chase_exclusion_ticks"), "{msg}");
    }

    #[test]
    fn zero_solo_play_reach_is_rejected() {
        let mut c = cfg();
        c.behavior.solo_play_reach = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("solo_play_reach"), "{msg}");
    }

    #[test]
    fn zero_sunbeam_reach_is_rejected_and_the_default_stands_in() {
        let mut c = cfg();
        c.behavior.sunbeam_reach = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("sunbeam_reach"), "{msg}");

        // A config written before the field existed gets the default.
        let old: BehaviorConfig =
            toml::from_str("budget_fraction_of_tick = 0.5").expect("old shape parses");
        assert_eq!(old.sunbeam_reach, default_sunbeam_reach());
    }

    #[test]
    fn zero_plugin_knobs_are_rejected_and_defaults_stand_in() {
        // Spec 016: both plugin knobs must be non-zero, and a config written
        // before they existed gets the documented defaults.
        let mut c = cfg();
        c.behavior.reply_max_bytes = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("reply_max_bytes"), "{msg}");

        let mut c = cfg();
        c.behavior.relaunch_cooldown_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("relaunch_cooldown_ticks"), "{msg}");

        let mut c = cfg();
        c.behavior.exchange_timeout_ms = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("exchange_timeout_ms"), "{msg}");

        let old: BehaviorConfig =
            toml::from_str("budget_fraction_of_tick = 0.5").expect("old shape parses");
        assert_eq!(old.reply_max_bytes, default_reply_max_bytes());
        assert_eq!(
            old.relaunch_cooldown_ticks,
            default_relaunch_cooldown_ticks()
        );
        assert_eq!(old.exchange_timeout_ms, default_exchange_timeout_ms());
    }

    #[test]
    fn solo_play_relief_may_not_beat_social_play() {
        let mut c = cfg();
        c.actions.solo_play_relief = c.actions.play_relief + 1.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("solo_play_relief"), "{msg}");
        assert!(msg.contains("play_relief"), "names the bound: {msg}");

        let mut c = cfg();
        c.actions.solo_play_relief = -1.0;
        assert!(c.validate().is_err());
    }

    #[test]
    fn zero_viewer_patience_is_rejected() {
        let mut c = cfg();
        c.viewer.distress_patience_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[viewer] distress_patience_ticks"), "{msg}");
    }

    #[test]
    fn a_pre_004_toml_without_the_new_keys_parses_with_defaults() {
        let toml_src = r#"
            [world]
            width = 32
            height = 32
            tick_ms = 800
            seed = 1

            [[kitty]]
            id = 1
            name = "A"
            x = 1
            y = 1
            behavior = "needs_driven"

            [[kitty]]
            id = 2
            name = "B"
            x = 2
            y = 2
            behavior = "playful"

            [behavior]
            budget_fraction_of_tick = 0.5

            [actions]
            eat_relief = 40.0
            drink_relief = 40.0
            sleep_relief = 5.0
            sleep_relief_sunbeam = 8.0
            groom_relief = 30.0
            play_relief = 25.0
            cuddle_relief = 20.0
        "#;
        let c: Config = toml::from_str(toml_src).expect("old-shape config parses");
        assert_eq!(c.behavior.urgency_weight, default_urgency_weight());
        assert_eq!(
            c.behavior.chase_exclusion_ticks,
            default_chase_exclusion_ticks()
        );
        assert_eq!(c.actions.solo_play_relief, default_solo_play_relief());
        assert_eq!(c.viewer.distress_patience_ticks, 60);
        c.validate().expect("defaults are valid");
    }

    #[test]
    fn fingerprint_ignores_the_new_behavior_tunables() {
        let a = cfg();
        let mut b = cfg();
        b.behavior.urgency_weight = 9.0;
        b.behavior.sunbeam_reach = 3;
        b.actions.solo_play_relief = 1.0;
        b.viewer.distress_patience_ticks = 999;
        assert_eq!(
            a.fingerprint(),
            b.fingerprint(),
            "tuning selection must never orphan a saved world"
        );
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

    // ---- action durations (spec 006) ----------------------------------

    #[test]
    fn a_toml_without_durations_gets_the_documented_defaults() {
        let toml_src = r#"
            [world]
            width = 32
            height = 32
            tick_ms = 800
            seed = 1

            [actions]
            eat_relief = 40.0
            drink_relief = 40.0
            sleep_relief = 5.0
            sleep_relief_sunbeam = 8.0
            groom_relief = 30.0
            play_relief = 25.0
            cuddle_relief = 20.0
        "#;
        let c: Config = toml::from_str(toml_src).expect("durationless [actions] parses");
        assert_eq!(c.actions.durations.eat, DurationBounds::new(2, 5));
        assert_eq!(c.actions.durations.drink, DurationBounds::new(2, 5));
        assert_eq!(c.actions.durations.play, DurationBounds::new(2, 5));
        assert_eq!(c.actions.durations.bath, DurationBounds::new(2, 5));
        // Sleep and cuddle minimums raised 2 -> 3 by owner tuning
        // (2026-07-20), once the 005 animations made durations visible.
        assert_eq!(c.actions.durations.sleep, DurationBounds::new(3, 8));
        assert_eq!(c.actions.durations.cuddle, DurationBounds::new(3, 8));
    }

    #[test]
    fn a_zero_minimum_duration_is_rejected_by_name() {
        let mut c = cfg();
        c.actions.durations.eat = DurationBounds::new(0, 5);
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[actions.durations] eat.min"), "{msg}");
        assert!(msg.contains('0'), "{msg}");
    }

    #[test]
    fn a_maximum_below_the_minimum_is_rejected_by_name() {
        let mut c = cfg();
        c.actions.durations.sleep = DurationBounds::new(4, 3);
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[actions.durations] sleep.max"), "{msg}");
        assert!(msg.contains("sleep.min (4)"), "{msg}");
    }

    #[test]
    fn instant_actions_are_a_lawful_configuration() {
        // min = max = 1 everywhere reproduces the pre-006 pacing.
        let mut c = cfg();
        for bounds in [
            &mut c.actions.durations.eat,
            &mut c.actions.durations.drink,
            &mut c.actions.durations.play,
            &mut c.actions.durations.bath,
            &mut c.actions.durations.sleep,
            &mut c.actions.durations.cuddle,
        ] {
            *bounds = DurationBounds::new(1, 1);
        }
        c.validate().expect("instant actions are legal");
    }

    #[test]
    fn fingerprint_ignores_duration_tunables() {
        let a = cfg();
        let mut b = cfg();
        b.actions.durations.eat = DurationBounds::new(1, 9);
        b.actions.durations.sleep = DurationBounds::new(3, 20);
        assert_eq!(
            a.fingerprint(),
            b.fingerprint(),
            "duration tuning must never orphan a saved world"
        );
    }
}
