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

mod defaults;
mod validate;

// Load-bearing glob: the `#[serde(default = "default_x")]` string attributes
// below and the `Default` impls resolve these names bare. Narrowing or
// removing this import breaks every one of them.
use defaults::*;

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
#[serde(deny_unknown_fields)]
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
    pub water: WaterConfig,
    #[serde(default)]
    pub events: EventsConfig,
    #[serde(default)]
    pub viewer: ViewerConfig,
    /// The `[rl]`, `[plugins]`, and `[watchdog]` tables are parsed from
    /// the same file text by cloudkitty-rl and the server respectively --
    /// everything under them is someone else's business. They are
    /// recognised here only so `deny_unknown_fields` can hold on
    /// everything that is actually ours, and they never serialize:
    /// `GET /config` must not grow keys, and `engine_defaults_sha256`
    /// hashes this struct's serialized defaults.
    #[serde(default, skip_serializing)]
    pub rl: ForeignTable,
    #[serde(default, skip_serializing)]
    pub plugins: ForeignTable,
    #[serde(default, skip_serializing)]
    pub watchdog: ForeignTable,
}

/// A table this struct accepts and discards because another parser owns
/// it. Deserializes from any value; carries nothing.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct ForeignTable;

impl<'de> serde::Deserialize<'de> for ForeignTable {
    fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        serde::de::IgnoredAny::deserialize(d).map(|_| ForeignTable)
    }
}

/// Wet fur (spec 024): occupying a water tile charges the bath need, so
/// water is priced the same way to every decider -- scripted ladders feel
/// it through need pressure, learned policies through reward. The charge
/// is per occupied tick (one knob prices both crossing and lounging),
/// scaled per cat by its own bath rise relative to the world's baseline,
/// and stops at the ceiling: pond-lounging is priced, never punished.
/// Validation proves the safeguard threshold unreachable by water alone
/// (certification hygiene by construction -- see `validate_water`).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WaterConfig {
    /// Bath need added per tick spent on a water tile, before trait
    /// scaling. The legible framing: 1.0 is 5x the default ambient bath
    /// rise (0.2/tick); the shipped 3.5 (spec 026, owner-set 2026-08-05,
    /// raised from 1.5) makes every wet tick unmistakably pricier than
    /// ambient drift -- exp-002's dial resolution showed 1.5 and 2.5 both
    /// too faint for a learner to price lounging by. Cats still swim when
    /// the detour is long enough. 0 disables the mechanic.
    #[serde(default = "default_water_bath_gain")]
    pub bath_gain: f32,
    /// Pre-charge bath value at or above which the charge stops. The gate
    /// reads the value before that tick's charge, so overshoot is bounded
    /// by one scaled charge -- headroom the validator budgets against the
    /// safeguard threshold. Raised 50 -> 60 with the gain (spec 026): the
    /// ceiling caps the *accumulated* cost of staying wet, and a higher
    /// cap gives a learner a larger, longer-lived signal against
    /// pond-lounging. 60 is the exact roofline the frozen eval suite
    /// permits -- heterogeneity.toml's 4x bath cat draws a 14-point
    /// charge, and 60 + 14 stays under the safeguard where the owner's
    /// first choice (65) did not. Note the tighter trait budget: at
    /// 3.5/60 a cat's bath rise may reach ~4.2x the world baseline
    /// before validation refuses the config (it was ~16x at 1.5/50) --
    /// a config that validated under the old defaults can legitimately
    /// fail now, and the error names the cat and the remedies.
    #[serde(default = "default_water_bath_gain_ceiling")]
    pub bath_gain_ceiling: f32,
    /// Waterline contagion (spec 044): a DRY cat whose own activity names
    /// an ADJACENT partner standing in water accrues `contagion_factor *
    /// bath_gain * bath_ratio(self)` per tick -- wet fur is social, and
    /// the price travels with the scene (a named partner who already
    /// wandered out of adjacency draws no trailing charge; owner ruling
    /// 2026-08-31). Own-activity rule: only the cat whose
    /// activity carries the partner pays (a merely-referenced cat, like an
    /// idle groomee, pays nothing); play is reciprocal by construction so
    /// both members NAME each other, but at most the dry one pays -- a
    /// scene has at most one dry-beside-wet member, so "both pay
    /// contagion" is unreachable (review amendment 2026-08-31). Dry
    /// member only -- a cat on water pays occupancy, never both -- and
    /// the same pre-charge ceiling gates it.
    /// A price, not a prohibition: legality and refusal are untouched.
    /// 0.0 (the default) disables the mechanic entirely; 1.0 is the Gen 1
    /// ruling (owner, 2026-08-30), flipped in its own deploy. Skipped from
    /// serialization at 0.0 so the launch is byte-identical (the 039-D5
    /// stamp discipline).
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub contagion_factor: f32,
    /// Who pays the contagion charge (spec 045, lab dial for the
    /// water's-edge avoidance smoke — owner-directed 2026-08-31).
    /// `option_a` (the default) is the shipped 044 rule verbatim: only
    /// the dry cat whose OWN activity names a wet adjacent partner pays.
    /// `bidirectional` admits the other role too: a dry cat that a wet
    /// adjacent cat's activity names (a referenced groomee, say) also
    /// pays — any dry member of a wet/dry pair, either role. Everything
    /// else is unchanged: same formula, same pre-charge ceiling gate,
    /// same wet-member exemption, same current-adjacency requirement,
    /// and at most ONE charge per cat per tick whatever admits it.
    /// Membership moves who pays, never the per-cat per-tick maximum,
    /// so the 044 budget law stands verbatim. Skipped from
    /// serialization at `option_a` (the 039-D5 stamp discipline).
    #[serde(default, skip_serializing_if = "ContagionMembership::is_option_a")]
    pub contagion_membership: ContagionMembership,
}

/// The waterline-contagion membership rule (spec 045): who pays the 044
/// charge. An enum, not a bool — the owner's vocabulary ("Option A" /
/// "bidirectional", ruling 2026-08-31) and room for future variants.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ContagionMembership {
    /// Shipped 044: only the dry NAMER pays.
    #[default]
    OptionA,
    /// Any dry member of a wet/dry pair pays, either role.
    Bidirectional,
}

impl ContagionMembership {
    /// Serde skip helper: the default variant stays out of the stamp.
    pub fn is_option_a(&self) -> bool {
        matches!(self, ContagionMembership::OptionA)
    }
}

/// The rhythm of a sustained purr (spec 011, retuned by spec 022). Purring
/// is engine-owned kitty state -- earned by happiness -- that a kitty may
/// now also *choose* to start (the deliberate purr, a spent turn). The
/// duration draw sets episode texture; the factor bounds set the rhythm:
/// each finished purr rests the motor for a freshly drawn multiple of its
/// own length, so a happy kitty rumbles a constant 1/(1 + midpoint) of the
/// time -- ~30.8% at the defaults -- while no two rests repeat mechanically.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PurrConfig {
    /// Shortest purr, in ticks. Must be at least 1 and at most `max_ticks`.
    #[serde(default = "default_purr_min_ticks")]
    pub min_ticks: u64,
    /// Longest purr, in ticks.
    #[serde(default = "default_purr_max_ticks")]
    pub max_ticks: u64,
    /// Lower bound of the per-end cooldown-factor draw (spec 022): the
    /// motor's rest is ⌈factor × the finished purr's duration⌉. Must be
    /// positive and at most `cooldown_factor_max`; equal bounds fix the
    /// factor.
    #[serde(default = "default_purr_cooldown_factor_min")]
    pub cooldown_factor_min: f32,
    /// Upper bound of the per-end cooldown-factor draw.
    #[serde(default = "default_purr_cooldown_factor_max")]
    pub cooldown_factor_max: f32,
    /// Chance a *spontaneous* purr start announces itself with a Purr meow
    /// (spec 022). Drawn once per start regardless of value (the
    /// fixed-shape rule); deliberate purrs always announce. 0 -- the
    /// default -- keeps the motor silent: the broadcast channel carries
    /// only chosen purrs.
    #[serde(default = "default_purr_announce_probability")]
    pub announce_probability: f32,
    /// RETIRED (spec 022): the flat rest was replaced by the proportional
    /// factor pair above. Deserialize-only sentinel -- a config that still
    /// names this key fails validation loudly, never silently ignored.
    #[serde(default, skip_serializing)]
    pub cooldown_ticks: Option<u64>,
}

impl Default for PurrConfig {
    fn default() -> Self {
        Self {
            min_ticks: default_purr_min_ticks(),
            max_ticks: default_purr_max_ticks(),
            cooldown_factor_min: default_purr_cooldown_factor_min(),
            cooldown_factor_max: default_purr_cooldown_factor_max(),
            announce_probability: default_purr_announce_probability(),
            cooldown_ticks: None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WorldConfig {
    pub width: u32,
    pub height: u32,
    pub tick_ms: u64,
    pub seed: u64,
    #[serde(default = "default_bind")]
    pub bind: String,
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
pub struct ElementRule {
    pub min: u32,
    pub max: u32,
    /// Lifetime in ticks; `None` (absent) means permanent.
    ///
    /// Note on `max` below: it is read only by config validation. The
    /// simulation tops each type up to `min` and no further, so the
    /// standing population IS the minimums -- `min` is the real knob,
    /// and lowering `max` alone changes nothing at runtime.
    #[serde(default)]
    pub ttl: Option<u64>,
    /// Chow only: servings per element.
    #[serde(default)]
    pub servings: Option<u32>,
    /// Bugs only (spec 039): tether each bug to the `n`-sized world-aligned
    /// cell it stands in — it never leaves. Absent means unbounded roaming
    /// (pre-039 behavior, byte-identical). Validation refuses values below 2
    /// and refuses the key on any other element type: the engine refuses
    /// what it will not honor. `skip_serializing_if` keeps the default
    /// config's JSON — and so `engine_defaults_sha256` — unmoved.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub roam_cell: Option<u32>,
    /// Greebles only (spec 039 third amendment): the greeble joins the
    /// critter rest-tick schedule — moving only when `(tick + id) % 2`
    /// says so, like a bug — and on a moving tick darts 1–3 tiles
    /// instead of the old 1–2. False (absent) is today's every-tick
    /// skitter, byte-identical; the pinned golden digest guards that.
    /// Validation refuses the key on any other element type.
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub dart: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ElementsConfig {
    pub water: ElementRule,
    pub chow: ElementRule,
    pub bug: ElementRule,
    pub greeble: ElementRule,
    pub sunbeam: ElementRule,
    /// Best-of-N width for every spawn placement draw: how many candidate
    /// tiles a spawn considers before choosing (spec 027; was a code
    /// constant). Higher spreads harder; 1 is a plain uniform pick.
    #[serde(default = "default_spread_candidates")]
    pub spread_candidates: usize,
    /// Every timed spawn draws its lifetime as base ± this many ticks, so
    /// a cohort born together never expires together (owner call
    /// 2026-07-23; spec 027 moved the number here). Floored so a short
    /// base can never spawn an already-expired element.
    #[serde(default = "default_ttl_jitter")]
    pub ttl_jitter: u64,
    /// Interior preference (spec 027): subtracted from a perimeter
    /// candidate's spread score, in tiles. A preference, never a
    /// prohibition -- a spawn still lands on the edge when the edge is
    /// all that's free. 0 disables it exactly.
    #[serde(default = "default_edge_penalty")]
    pub edge_penalty: f32,
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
                roam_cell: None,
                dart: false,
            },
            chow: ElementRule {
                min: 5,
                max: 10,
                ttl: None,
                servings: Some(5),
                roam_cell: None,
                dart: false,
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
                roam_cell: None,
                dart: false,
            },
            greeble: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(300),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            sunbeam: ElementRule {
                min: 3,
                max: 6,
                ttl: Some(300),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            spread_candidates: default_spread_candidates(),
            ttl_jitter: default_ttl_jitter(),
            edge_penalty: default_edge_penalty(),
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
#[serde(deny_unknown_fields)]
pub struct ActionEffects {
    pub eat_relief: f32,
    pub drink_relief: f32,
    pub sleep_relief: f32,
    pub sleep_relief_sunbeam: f32,
    pub groom_relief: f32,
    /// The kitty/duet play value: what each partner gains per tick of
    /// social play. The name predates the per-target split (spec 025)
    /// and is kept deliberately -- every config in the wild carries it
    /// with exactly this meaning, and renaming would move the `/config`
    /// wire key for zero behavioral gain.
    pub play_relief: f32,
    /// RETIRED LOUDLY (spec 041, owner's full-compatibility-break ruling
    /// 2026-08-28): the classic shared dial, split into
    /// `rest_mutual_relief` and `groom_cuddle_relief`. Parsed only so its
    /// presence can be rejected with the migration map (the spec-025
    /// pattern); every committed config was migrated in the same change.
    /// The field itself is deleted at the 3.0 config-hygiene wall.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cuddle_relief: Option<f32>,
    /// Cuddle relief per serviced cosleep tick when the adjacent partner is
    /// merely present (spec 028's passive tier). Both parties receive it.
    /// Defaults equal to the classic `cuddle_relief` -- behavior-preserving
    /// until the dial-pricing pilot moves it.
    #[serde(default = "default_cosleep_relief")]
    pub cosleep_drip_relief: f32,
    /// Cuddle relief per serviced cosleep tick when the partner is itself
    /// sleeping or resting (the mutual tier). Both parties receive it.
    #[serde(default = "default_cosleep_relief")]
    pub cosleep_mutual_relief: f32,
    /// Cuddle relief per serviced tick of a partnered rest scene when the
    /// partner is itself resting or sleeping (spec 041's mutual tier -- the
    /// need's saturating specialist). Both parties receive it. Split from
    /// the classic `cuddle_relief` at its engine-default value (a config
    /// that overrode the old key must pin this one explicitly -- the
    /// served toml does; spec 028's cosleep launch pattern). Convention:
    /// `rest_drip_relief` stays below it.
    #[serde(default = "default_cuddle_split_relief")]
    pub rest_mutual_relief: f32,
    /// Cuddle relief per serviced tick of a partnered rest scene when the
    /// partner is merely present (spec 041's drip tier). Both parties
    /// receive it. Launches at 0.0: the engine-sibling change is
    /// legality-and-binding only, and every price movement lives in the
    /// reprice diff.
    #[serde(default = "default_rest_drip_relief")]
    pub rest_drip_relief: f32,
    /// The groomer's own cuddle relief while grooming a friend (spec 041).
    /// Split from the classic `cuddle_relief` at its engine-default value
    /// (same explicit-pin note as `rest_mutual_relief`).
    #[serde(default = "default_cuddle_split_relief")]
    pub groom_cuddle_relief: f32,
    /// Play relief for pouncing at nothing. Smaller than `play_relief` so a
    /// kitty with company always prefers the real thing. Also the price a
    /// vanished play target drops to (spec 025): the critter is gone, the
    /// kitty is pouncing at nothing.
    #[serde(default = "default_solo_play_relief")]
    pub solo_play_relief: f32,
    /// Play relief per tick while playing with a bug (spec 025). Sits
    /// between the duet value and the greeble in the validated gradient.
    #[serde(default = "default_play_relief_bug")]
    pub play_relief_bug: f32,
    /// Play relief per tick while playing with a greeble (spec 025). The
    /// top of the gradient, capped below 2 x `play_relief` so a duet's
    /// team total always beats it.
    #[serde(default = "default_play_relief_greeble")]
    pub play_relief_greeble: f32,
    /// How long each activity runs, in ticks (spec 006): the engine holds an
    /// activity at least `min` ticks and never lets it pass `max`.
    #[serde(default)]
    pub durations: DurationsConfig,
}

impl Default for ActionEffects {
    fn default() -> Self {
        Self {
            eat_relief: 40.0,
            drink_relief: 40.0,
            sleep_relief: 5.0,
            sleep_relief_sunbeam: 7.0,
            // Groom/play/cuddle lowered (owner tuning, 2026-07-27): scenes
            // clear less per tick, so the cats spend more of their lives
            // being playful and cuddly -- the point of the retune.
            groom_relief: 20.0,
            play_relief: 20.0,
            cuddle_relief: None,
            cosleep_drip_relief: default_cosleep_relief(),
            cosleep_mutual_relief: default_cosleep_relief(),
            rest_mutual_relief: default_cuddle_split_relief(),
            rest_drip_relief: default_rest_drip_relief(),
            groom_cuddle_relief: default_cuddle_split_relief(),
            solo_play_relief: default_solo_play_relief(),
            play_relief_bug: default_play_relief_bug(),
            play_relief_greeble: default_play_relief_greeble(),
            durations: DurationsConfig::default(),
        }
    }
}

/// Bounds on how long one activity may run, in ticks, inclusive of the tick
/// it starts on. Relief applies on every tick, so `min` also sets the least
/// relief an undertaking delivers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
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
#[serde(deny_unknown_fields)]
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

/// The meow channel's law (spec 028). The courtesy era (spec 023) is over:
/// message legality is engine law -- a want-kind may be spoken only while
/// its need is armed (threshold + hysteresis) and that kind's per-cat
/// cooldown has cleared. Silence is always legal.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MeowConfig {
    /// How long a meow stays visible to kitties and viewers -- and, since
    /// spec 028, the per-kind emission cooldown: one live digest entry per
    /// kind per emitter, so a persistent signal refreshes exactly as the
    /// old one fades.
    #[serde(default = "default_meow_recent_window_ticks")]
    pub recent_window_ticks: u64,
    /// A want-kind arms when its need reaches this level; only an armed
    /// kind may be announced (grounded legality, enforced in the mask).
    #[serde(default = "default_meow_announce_threshold")]
    pub announce_threshold: f32,
    /// An armed kind disarms when its need falls below
    /// `announce_threshold - announce_hysteresis` -- the band keeps the
    /// mask from flickering while an errand is in progress.
    #[serde(default = "default_meow_announce_hysteresis")]
    pub announce_hysteresis: f32,
    /// RETIRED (spec 023): renamed to `courtesy_ticks` when engine
    /// enforcement ended. Deserialize-only sentinel -- a config naming it
    /// fails validation loudly, never silently shifting semantics.
    #[serde(default, skip_serializing)]
    pub cooldown_ticks: Option<u64>,
    /// RETIRED (spec 023): renamed to `urgent_courtesy_ticks`.
    #[serde(default, skip_serializing)]
    pub urgent_cooldown_ticks: Option<u64>,
    /// RETIRED (spec 028): the courtesy era ended when legality became
    /// engine law; the cooldown is `recent_window_ticks`.
    #[serde(default, skip_serializing)]
    pub courtesy_ticks: Option<u64>,
    /// RETIRED (spec 028): urgency no longer shortens the interval --
    /// grounding (announce_threshold) is the urgency story now.
    #[serde(default, skip_serializing)]
    pub urgent_courtesy_ticks: Option<u64>,
    /// RETIRED (spec 028): replaced by `announce_threshold`, which gates
    /// legality instead of shortening courtesy.
    #[serde(default, skip_serializing)]
    pub urgent_need_threshold: Option<f32>,
    /// Per-kind enable flags (spec 033): vocabulary is armed by config,
    /// never by engine fork. Flags gate LEGALITY ONLY -- every layout
    /// (digest, head, mask, observation) is identical whatever they say.
    #[serde(default)]
    pub vocabulary: VocabularyConfig,
}

impl Default for MeowConfig {
    fn default() -> Self {
        Self {
            recent_window_ticks: default_meow_recent_window_ticks(),
            announce_threshold: default_meow_announce_threshold(),
            announce_hysteresis: default_meow_announce_hysteresis(),
            cooldown_ticks: None,
            urgent_cooldown_ticks: None,
            courtesy_ticks: None,
            urgent_courtesy_ticks: None,
            urgent_need_threshold: None,
            vocabulary: VocabularyConfig::default(),
        }
    }
}

/// `[meow.vocabulary]` (spec 033 FR-006): one named flag per speakable
/// kind, so a misspelled kind refuses to boot (the PR-114 posture) and an
/// omitted table means the documented defaults. Active-vs-reserve is
/// nothing but the default value: `trill` and `ekekek` ship off (in every
/// layout, in no training run) until an experiment arms them -- the
/// post-fog language-capacity arms are pure config. WaitForMe is absent by
/// design: the engine's word is not speakable and not gateable.
// The container-level `#[serde(default)]` fills every omitted field from
// the ONE `Default` impl below (it composes with `deny_unknown_fields`),
// so a flag's default lives in exactly one place. It used to live in two —
// per-field attributes serving the partial-table parse path, the impl
// serving the omitted-table path — which is a drift trap armed exactly
// when a default flips (arming trill/ekekek post-fog): flip one list and
// the two config shapes silently disagree (033 review Finding 6).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct VocabularyConfig {
    pub want_eat: bool,
    pub want_drink: bool,
    pub mew: bool,
    pub want_play: bool,
    pub want_cuddle: bool,
    pub purr: bool,
    pub want_bath: bool,
    pub want_sleep: bool,
    pub here_food: bool,
    pub here_water: bool,
    pub here_critter: bool,
    pub here_sunbeam: bool,
    pub chirp: bool,
    /// Reserve: default off.
    pub trill: bool,
    /// Reserve: default off.
    pub ekekek: bool,
}

/// The single source of every vocabulary default (spec 033 FR-006):
/// active kinds true, reserves false.
impl Default for VocabularyConfig {
    fn default() -> Self {
        Self {
            want_eat: true,
            want_drink: true,
            mew: true,
            want_play: true,
            want_cuddle: true,
            purr: true,
            want_bath: true,
            want_sleep: true,
            here_food: true,
            here_water: true,
            here_critter: true,
            here_sunbeam: true,
            chirp: true,
            trill: false,
            ekekek: false,
        }
    }
}

impl VocabularyConfig {
    /// The flag for a speakable kind. WaitForMe reaches here only from a
    /// trusted in-process caller (see `message_legal`'s doc) and is always
    /// enabled -- it is the engine's word, outside the vocabulary system.
    pub fn enabled(&self, kind: crate::meow::MessageKind) -> bool {
        use crate::meow::MessageKind::*;
        match kind {
            WantEat => self.want_eat,
            WantDrink => self.want_drink,
            Mew => self.mew,
            WantPlay => self.want_play,
            WantCuddle => self.want_cuddle,
            Purr => self.purr,
            WaitForMe => true,
            WantBath => self.want_bath,
            WantSleep => self.want_sleep,
            HereFood => self.here_food,
            HereWater => self.here_water,
            HereCritter => self.here_critter,
            HereSunbeam => self.here_sunbeam,
            Chirp => self.chirp,
            Trill => self.trill,
            Ekekek => self.ekekek,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
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
    /// The final pounce (spec 039 FR-011, the fallback the owner
    /// pre-authorized): when a chase's applied step leaves an ELEMENT
    /// target at Manhattan distance exactly 2, the cat lunges one more
    /// plain step toward it in the same tick — blocked = lost, no routing,
    /// no RNG, never on kitty targets. Default off; `skip_serializing_if`
    /// keeps the defaults stamp unmoved (the 039 D5 discipline).
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub pounce: bool,
    /// Spec 042 (Playful 2.0): the partner-value score's dials, all at
    /// identity 0.0 and skip-serialized there (the pounce field's 039-D5
    /// discipline — the defaults stamp must not move for an inert launch).
    /// Pricing belongs to Experiments' joint sweep; the owner pins served
    /// values. `w_value` scales a friend's value in the score AND switches
    /// busy-friend admission on when > 0 (research D2 — both effects
    /// documented, byte-identity at defaults demands the coupling).
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub w_value: f32,
    /// Expected-wait penalty per tick for a mid-scene candidate (spec 042).
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub w_busy: f32,
    /// Penalty per point of a candidate's top NON-play pressure (spec 042
    /// clarify: wanting to play never counts against a candidate).
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub w_serious: f32,
    /// Own play-need floor for bothering any friend (spec 042 eligibility
    /// filter). 0 = every friend eligible on this axis.
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub t_self: f32,
    /// Per-friend value floor for eligibility (spec 042). 0 = no bar.
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub t_partner: f32,
    /// Standalone critter score offset (spec 042 clarify: NOT scaled by
    /// w_value — each dial moves exactly one thing). Either sign is lawful.
    #[serde(default, skip_serializing_if = "f32_is_zero")]
    pub critter_appeal: f32,
    /// Per-need multipliers inside the playful get-serious trigger ONLY
    /// (spec 042): pressure × weight compared to `playful_comfort`. All 1.0
    /// = exactly the classic unweighted check; skip-serialized at identity.
    #[serde(default, skip_serializing_if = "ComfortWeights::is_identity")]
    pub comfort_weight: ComfortWeights,
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
    /// What "real cuddle need" means to the scripted responders (spec 028):
    /// at or above this, a cat answers an audible `WantBath` with grooming
    /// and prefers a friend's side to a sunbeam for its nap. One shared
    /// gate on purpose -- the responder economy is priced as a unit.
    #[serde(default = "default_cuddle_real_threshold")]
    pub cuddle_real_threshold: f32,
    /// Spec 043: the here-word announce period. 0 (the default, absent
    /// from serialized defaults — the 039-D5 stamp discipline) means
    /// scripted cats never announce Here\*; N ≥ 1 means each scripted
    /// cat considers here-speech on its phase ticks,
    /// `(tick + kitty_id) % N == 0`. Existing speech always wins
    /// (owner ruling 2026-08-23): WaitForMe > want-word > here-word >
    /// Silent — the here path only fills a slot that would be Silent.
    /// Selection among the legal here-kinds indexes `HERE_KINDS` by the
    /// speaking-tick counter `((tick + kitty_id) / N) % n_legal` — NOT
    /// the handoff's literal `(tick + kitty_id) % n_legal`, which
    /// aliases against the phase gate (on speaking ticks the sum is a
    /// multiple of N, so only multiples of gcd(N, n_legal) are ever
    /// reached; research D3, amendment accepted by Experiments
    /// 2026-08-30). Legality is unchanged law: every proposal still
    /// passes `message_legal` and the engine's enforcement seam.
    #[serde(default, skip_serializing_if = "u64_is_zero")]
    pub announce_here: u64,
    /// Spec 045: the charge-aware ladder gate (lab dial for the
    /// water's-edge avoidance smoke). When true, the built-in chooser
    /// prices a candidate partnered scene's expected contagion exposure
    /// — scene-total under the active `[water] contagion_membership`
    /// rule — into its existing scores; when false (the default), every
    /// 045 seam short-circuits BEFORE any exposure arithmetic, so off is
    /// structurally byte-identical to pre-045. Deliberately NOT auto-on
    /// with the contagion factor: smoke arm B needs the factor armed
    /// under a charge-BLIND ladder. A preference in the behaviors, never
    /// a rule in the engine (Article IV) — exposure moves what the
    /// advisor proposes, never what is legal. Skip-serialized at false
    /// (the pounce field's 039-D5 discipline).
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub contagion_aware_ladder: bool,
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
            pounce: false,
            solo_play_reach: default_solo_play_reach(),
            sunbeam_reach: default_sunbeam_reach(),
            budget_strikes: default_budget_strikes(),
            bench_ticks: default_bench_ticks(),
            reply_max_bytes: default_reply_max_bytes(),
            relaunch_cooldown_ticks: default_relaunch_cooldown_ticks(),
            exchange_timeout_ms: default_exchange_timeout_ms(),
            cuddle_real_threshold: default_cuddle_real_threshold(),
            w_value: 0.0,
            w_busy: 0.0,
            w_serious: 0.0,
            t_self: 0.0,
            t_partner: 0.0,
            critter_appeal: 0.0,
            comfort_weight: ComfortWeights::default(),
            announce_here: 0,
            contagion_aware_ladder: false,
        }
    }
}

fn f32_is_zero(v: &f32) -> bool {
    *v == 0.0
}

fn u64_is_zero(v: &u64) -> bool {
    *v == 0
}

/// Spec 042: per-need multipliers for the playful get-serious trigger.
/// All 1.0 is the identity — exactly the classic unweighted check — and
/// the whole table is skip-serialized there so the defaults stamp does
/// not move. Trigger-only: nothing outside `playful`'s comfort check
/// reads these.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct ComfortWeights {
    pub eat: f32,
    pub drink: f32,
    pub sleep: f32,
    pub play: f32,
    pub cuddle: f32,
    pub bath: f32,
}

impl Default for ComfortWeights {
    fn default() -> Self {
        Self {
            eat: 1.0,
            drink: 1.0,
            sleep: 1.0,
            play: 1.0,
            cuddle: 1.0,
            bath: 1.0,
        }
    }
}

impl ComfortWeights {
    pub fn is_identity(&self) -> bool {
        *self == Self::default()
    }

    /// The one read path (spec 042 FR-005): the weight for a need.
    pub fn get(&self, kind: crate::needs::NeedKind) -> f32 {
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

impl BehaviorConfig {
    pub fn budget_ms(&self, tick_ms: u64) -> u64 {
        let ms = (tick_ms as f64 * self.budget_fraction_of_tick as f64).floor() as u64;
        ms.max(1)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EventsConfig {
    pub distress_retention: usize,
    /// How many finished-activity events the world remembers (spec 006):
    /// each carries the true tick span a scene ran, which served snapshots
    /// alone cannot show (the final tick clears the clock it stamped).
    #[serde(default = "default_activity_retention")]
    pub activity_retention: usize,
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
#[serde(deny_unknown_fields)]
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
            water: WaterConfig::default(),
            events: EventsConfig::default(),
            viewer: ViewerConfig::default(),
            rl: ForeignTable,
            plugins: ForeignTable,
            watchdog: ForeignTable,
        }
    }
}

impl Default for WaterConfig {
    fn default() -> Self {
        Self {
            bath_gain: default_water_bath_gain(),
            bath_gain_ceiling: default_water_bath_gain_ceiling(),
            contagion_factor: 0.0,
            contagion_membership: ContagionMembership::default(),
        }
    }
}

impl Config {
    /// Checks every rule the constitution and spec impose on configuration.
    ///
    /// Errors name the field, its value, and the allowed range so an operator can
    /// fix the file without reading the source.
    pub fn validate(&self) -> Result<(), ConfigError> {
        // Section order is spec-contract (spec 020, amended FR-004): the
        // first-failing message a multiply-invalid config reports follows
        // this sequence; reordering it is a spec change, not a refactor.
        // Positions 1-7 and 13-14 are the pre-020 entry order; 7-12 expand
        // the old catch-all in its slot, in its own first-occurrence order.
        self.validate_world()?;
        self.validate_roster()?;
        self.validate_thresholds()?;
        self.validate_happiness()?;
        self.validate_needs()?;
        self.validate_elements()?;
        self.validate_behavior()?;
        self.validate_purr()?;
        self.validate_meow()?;
        self.validate_actions()?;
        self.validate_viewer()?;
        self.validate_events()?;
        self.validate_persistence()?;
        self.validate_durations()?;
        self.validate_capacity()?;
        // Position 16: appended by spec 024 (a spec-contract extension,
        // documented in that spec -- new sections append, never reorder).
        self.validate_water()?;
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

    /// The wet-fur trait scale for one kitty (spec 024): its own bath rise
    /// over the world baseline. One definition shared by the engine's
    /// occupancy charge, the behavior ladder's route pricing, and load-time
    /// validation, so the three can never disagree. A non-positive baseline
    /// (legal only while wet fur is disabled) degrades to 1 rather than
    /// divide.
    pub fn bath_ratio(&self, kitty_id: KittyId) -> f32 {
        if self.needs.bath > 0.0 {
            self.need_rate_for(kitty_id, crate::needs::NeedKind::Bath) / self.needs.bath
        } else {
            1.0
        }
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
    fn the_playful2_dials_reject_negative_and_non_finite_values() {
        // Spec 042 FR-007: no NaN may enter the score's total order, and
        // negatives are rejected where they have no meaning. critter_appeal
        // alone allows either sign ("less appealing than baseline" is a
        // meaningful sweep direction) but never non-finite.
        for poison in [f32::NAN, f32::INFINITY, -1.0] {
            for (name, setter) in [
                (
                    "w_value",
                    (|c: &mut Config, v: f32| c.behavior.w_value = v) as fn(&mut Config, f32),
                ),
                ("w_busy", |c, v| c.behavior.w_busy = v),
                ("w_serious", |c, v| c.behavior.w_serious = v),
                ("t_self", |c, v| c.behavior.t_self = v),
                ("t_partner", |c, v| c.behavior.t_partner = v),
                ("comfort_weight] eat", |c, v| {
                    c.behavior.comfort_weight.eat = v
                }),
                ("comfort_weight] drink", |c, v| {
                    c.behavior.comfort_weight.drink = v
                }),
                ("comfort_weight] sleep", |c, v| {
                    c.behavior.comfort_weight.sleep = v
                }),
                ("comfort_weight] play", |c, v| {
                    c.behavior.comfort_weight.play = v
                }),
                ("comfort_weight] cuddle", |c, v| {
                    c.behavior.comfort_weight.cuddle = v
                }),
                ("comfort_weight] bath", |c, v| {
                    c.behavior.comfort_weight.bath = v
                }),
            ] {
                let mut c = cfg();
                setter(&mut c, poison);
                let msg = c
                    .validate()
                    .expect_err("poison must be rejected")
                    .to_string();
                assert!(msg.contains(name), "{poison} in {name}: {msg}");
            }
        }
        // Comfort weights are strictly positive: zero would disable the
        // get-serious trigger for that need (medium review #5).
        let mut c = cfg();
        c.behavior.comfort_weight.eat = 0.0;
        let msg = c
            .validate()
            .expect_err("a zero weight is rejected")
            .to_string();
        assert!(msg.contains("comfort_weight] eat"), "{msg}");
        // critter_appeal: non-finite rejected, negative accepted.
        for poison in [f32::NAN, f32::INFINITY] {
            let mut c = cfg();
            c.behavior.critter_appeal = poison;
            let msg = c.validate().expect_err("non-finite rejected").to_string();
            assert!(msg.contains("critter_appeal"), "{msg}");
        }
        let mut c = cfg();
        c.behavior.critter_appeal = -3.0;
        c.validate()
            .expect("a negative appeal is a lawful preference");
    }

    #[test]
    fn a_misspelled_comfort_weight_key_fails_loudly() {
        // Spec 042 / contract §5 (convergence T029): the weight table is
        // strict -- a typo'd need key must never silently feed nothing.
        let err = toml::from_str::<ComfortWeights>("eats = 1.5")
            .expect_err("unknown weight keys are rejected");
        assert!(err.to_string().contains("eats"), "{err}");
        let ok: ComfortWeights = toml::from_str("eat = 1.5").expect("real keys parse");
        assert_eq!(ok.eat, 1.5);
        assert_eq!(ok.bath, 1.0, "unset needs keep the identity weight");
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
        // default must land (spec 011 SC-005; defaults retuned by spec 022).
        let parsed: PurrConfig = toml::from_str("").expect("an empty purr table parses");
        assert_eq!((parsed.min_ticks, parsed.max_ticks), (8, 13));
        assert_eq!(
            (parsed.cooldown_factor_min, parsed.cooldown_factor_max),
            (1.75, 2.75)
        );

        let mut c = cfg();
        c.purr.min_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] min_ticks"), "{msg}");
        c.purr.min_ticks = 20; // > max_ticks 13
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] min_ticks"), "{msg}");
        assert!(msg.contains("max_ticks"), "{msg}");
        c.purr.min_ticks = c.purr.max_ticks; // fixed-length purrs are legal
        assert!(c.validate().is_ok());
    }

    #[test]
    fn purr_factor_bounds_validate_and_equal_bounds_fix_the_factor() {
        // Spec 022 FR-010 validation rows for the cooldown-factor pair.
        let mut c = cfg();
        c.purr.cooldown_factor_min = 0.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] cooldown_factor_min"), "{msg}");
        c.purr.cooldown_factor_min = -1.0;
        assert!(c.validate().is_err());
        c.purr.cooldown_factor_min = f32::NAN;
        assert!(c.validate().is_err());
        c.purr.cooldown_factor_min = 3.0; // > max 2.75
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("cooldown_factor_max"), "{msg}");
        c.purr.cooldown_factor_min = 2.25;
        c.purr.cooldown_factor_max = 2.25; // equal bounds: fixed factor
        assert!(c.validate().is_ok());
        // A bad max blames max (review fix: the error names the field the
        // user must change, not its innocent partner).
        c.purr.cooldown_factor_max = f32::INFINITY;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] cooldown_factor_max"), "{msg}");
        c.purr.cooldown_factor_max = f32::NAN;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] cooldown_factor_max"), "{msg}");
        c.purr.cooldown_factor_max = 1_001.0; // over the exactness bound
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] cooldown_factor_max"), "{msg}");
    }

    #[test]
    fn purr_tick_bounds_reject_arithmetic_hazards() {
        // Review fix alongside spec 022: without an upper bound, an absurd
        // max_ticks silently truncated the duration draw and could undercut
        // the "rest is never shortened" ceiling (f32 mantissa) or overflow
        // `tick + duration`. The bound makes those configs fail loudly.
        let mut c = cfg();
        c.purr.max_ticks = 1_000_000; // at the bound: legal
        assert!(c.validate().is_ok());
        c.purr.max_ticks = 1_000_001;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] max_ticks"), "{msg}");
        c.purr.max_ticks = u64::MAX;
        assert!(c.validate().is_err());
    }

    #[test]
    fn meow_dial_defaults_land_and_the_rows_hold() {
        // Spec 028 (keeping 023's posture): an absent [meow] table (or a
        // partial one) fills from defaults, so an old-key config reaches
        // validation where the retirement error can explain itself.
        let parsed: MeowConfig = toml::from_str("").expect("an empty meow table parses");
        assert_eq!(
            (
                parsed.recent_window_ticks,
                parsed.announce_threshold,
                parsed.announce_hysteresis
            ),
            (10, 30.0, 5.0)
        );
        let partial: MeowConfig =
            toml::from_str("announce_threshold = 40.0").expect("a partial meow table parses");
        assert_eq!(partial.announce_hysteresis, 5.0);

        // The band rows: hysteresis strictly below threshold, threshold on
        // the need scale, the window alive.
        let mut c = cfg();
        c.meow.announce_hysteresis = c.meow.announce_threshold;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[meow] announce_hysteresis"), "{msg}");
        c.meow.announce_hysteresis = 0.0; // no band is legal
        assert!(c.validate().is_ok());
        c.meow.announce_threshold = 0.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[meow] announce_threshold"), "{msg}");
        c.meow.announce_threshold = 101.0;
        assert!(c.validate().is_err());
        c.meow.announce_threshold = 100.0; // the top of the scale is legal
        assert!(c.validate().is_ok());
        c.meow.recent_window_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[meow] recent_window_ticks"), "{msg}");
    }

    #[test]
    fn the_retired_courtesy_trio_is_rejected_loudly() {
        // Spec 028 (FR-024, US6 scenario 2): the courtesy-era names fail at
        // load with migration text naming their successors -- the intended
        // signal for any config carried across the generation wall.
        for (toml_line, key, successor) in [
            (
                "courtesy_ticks = 10",
                "[meow] courtesy_ticks",
                "recent_window_ticks",
            ),
            (
                "urgent_courtesy_ticks = 5",
                "[meow] urgent_courtesy_ticks",
                "announce_threshold",
            ),
            (
                "urgent_need_threshold = 75.0",
                "[meow] urgent_need_threshold",
                "announce_threshold",
            ),
        ] {
            let parsed: MeowConfig =
                toml::from_str(toml_line).expect("the retired key still parses");
            let mut c = cfg();
            c.meow = parsed;
            let msg = c.validate().unwrap_err().to_string();
            assert!(msg.contains(key), "{msg}");
            assert!(msg.contains("retired by spec 028"), "{msg}");
            assert!(msg.contains(successor), "{msg}");
        }
    }

    #[test]
    fn the_retired_meow_cooldown_knobs_are_rejected_loudly() {
        // Spec 023 FR-006 / US3 scenario 2: the enforcement-era names fail
        // at load naming their replacements -- never silently accepted with
        // shifted semantics.
        let parsed: MeowConfig =
            toml::from_str("cooldown_ticks = 15").expect("the retired key still parses");
        let mut c = cfg();
        c.meow = parsed;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[meow] cooldown_ticks"), "{msg}");
        assert!(msg.contains("retired"), "{msg}");
        assert!(msg.contains("courtesy_ticks"), "{msg}");

        let parsed: MeowConfig = toml::from_str("urgent_cooldown_ticks = 5").expect("parses");
        let mut c = cfg();
        c.meow = parsed;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[meow] urgent_cooldown_ticks"), "{msg}");
        assert!(msg.contains("urgent_courtesy_ticks"), "{msg}");
    }

    #[test]
    fn the_retired_purr_cooldown_knob_is_rejected_loudly() {
        // Spec 022 FR-010 / US3 scenario 3: a config still naming the flat
        // rest fails at load with an error naming the replacements -- never
        // a silent ignore (the config module accepts unknown keys, so the
        // sentinel is what makes this loud).
        let parsed: PurrConfig =
            toml::from_str("cooldown_ticks = 30").expect("the retired key still parses");
        let mut c = cfg();
        c.purr = parsed;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] cooldown_ticks"), "{msg}");
        assert!(msg.contains("retired"), "{msg}");
        assert!(msg.contains("cooldown_factor_min"), "{msg}");
    }

    #[test]
    fn purr_announce_probability_defaults_silent_and_rejects_nonsense() {
        // Spec 022 FR-007/FR-010: an absent key means a silent motor.
        let parsed: PurrConfig = toml::from_str("").expect("empty purr table parses");
        assert_eq!(parsed.announce_probability, 0.0);

        let mut c = cfg();
        c.purr.announce_probability = -0.1;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[purr] announce_probability"), "{msg}");
        c.purr.announce_probability = 1.1;
        assert!(c.validate().is_err());
        c.purr.announce_probability = f32::NAN;
        assert!(c.validate().is_err());
        c.purr.announce_probability = 1.0; // legal: every start announces
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
    fn water_section_defaults_when_absent_and_old_configs_keep_parsing() {
        // A pre-024 config has no [water] table: the section default must
        // land whole, so every existing config file keeps working unedited
        // (spec 024 FR-010) -- including the hash-frozen exam configs,
        // which can never be edited at all.
        let parsed: Config = toml::from_str(
            "[world]\nwidth = 32\nheight = 32\nseed = 7\ntick_ms = 1000\n\
             [[kitty]]\nid = 1\nname = \"A\"\nx = 1\ny = 1\nbehavior = \"needs_driven\"\n\
             [[kitty]]\nid = 2\nname = \"B\"\nx = 2\ny = 2\nbehavior = \"needs_driven\"\n",
        )
        .expect("pre-024 config parses");
        assert_eq!(parsed.water.bath_gain, 3.5);
        assert_eq!(parsed.water.bath_gain_ceiling, 60.0);
        parsed.validate().expect("defaults validate");
    }

    #[test]
    fn water_rejections_name_the_field_the_user_must_change() {
        for bad in [f32::NAN, f32::INFINITY, -1.0, 101.0] {
            let mut c = cfg();
            c.water.bath_gain = bad;
            let msg = c.validate().unwrap_err().to_string();
            assert!(msg.contains("[water] bath_gain"), "{bad}: {msg}");
        }
        for bad in [f32::NAN, f32::NEG_INFINITY, -0.5, 100.5] {
            let mut c = cfg();
            c.water.bath_gain_ceiling = bad;
            let msg = c.validate().unwrap_err().to_string();
            assert!(msg.contains("[water] bath_gain_ceiling"), "{bad}: {msg}");
        }
    }

    #[test]
    fn water_safeguard_headroom_is_unrepresentable_to_break() {
        // The flat case: ceiling + gain crowds the safeguard (75).
        let mut c = cfg();
        c.water.bath_gain = 30.0;
        c.water.bath_gain_ceiling = 50.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[water] bath_gain_ceiling"), "{msg}");
        assert!(msg.contains("75"), "shows the safeguard: {msg}");

        // The trait-scaled case: a high bath-rise cat doubles the charge,
        // and the error names that cat -- the field the operator must
        // reconsider is on the roster, not in [water].
        let mut c = cfg();
        c.water.bath_gain = 8.0; // fine alone: 60 + 8 < 75
        c.kitties[1].needs = Some(NeedRateOverrides {
            bath: Some(0.4), // ratio 2.0 against the 0.2 baseline
            ..Default::default()
        });
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[water] bath_gain_ceiling"), "{msg}");
        assert!(msg.contains("Biscuit"), "blames the swimmer: {msg}");

        // A zero ambient baseline has nothing to scale against.
        let mut c = cfg();
        c.needs.bath = 0.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[needs] bath"), "{msg}");

        // ...unless wet fur is off entirely: 0 disables the mechanic and
        // every budget with it.
        let mut c = cfg();
        c.needs.bath = 0.0;
        c.water.bath_gain = 0.0;
        assert!(c.validate().is_ok());
    }

    #[test]
    fn contagion_widens_the_headroom_budget_only_above_factor_one() {
        // Spec 044 FR-009/FR-011: the budget is ceiling + max(1, factor) x
        // gain x max_ratio < safeguard. Dry-member-only keeps the per-tick
        // worst case unchanged at factor <= 1.0, so every config valid
        // under the occupancy-only budget stays valid at the Gen 1 ruling
        // -- bit-identical check, no re-baseline debt.
        let mut c = cfg();
        c.water.contagion_factor = 1.0;
        c.validate()
            .expect("factor 1.0 must not change what validates (FR-011)");

        // Above 1.0 the contagion charge IS the worst case: the default
        // world (ceiling 60, gain 3.5, ratio 1.0, safeguard 75) has 15 of
        // headroom, so factor 5.0 (charge 17.5) crowds the safeguard.
        let mut c = cfg();
        c.water.contagion_factor = 5.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[water] bath_gain_ceiling"), "{msg}");
        assert!(
            msg.contains("contagion_factor"),
            "the remedy names the new dial: {msg}"
        );

        // The same factor with enough headroom is accepted -- the budget
        // is a line, not a ban on the dial.
        let mut c = cfg();
        c.water.contagion_factor = 5.0;
        c.water.bath_gain_ceiling = 50.0; // 50 + 17.5 < 75
        c.validate()
            .expect("factor 5.0 with real headroom must validate");

        // And the trait-scaled case still blames the right cat: Biscuit
        // at 2x bath rise doubles the contagion charge exactly as it
        // doubles occupancy (same bath_ratio scale).
        let mut c = cfg();
        c.water.contagion_factor = 3.0; // 3.5 x 2.0 x 3.0 = 21; 60 + 21 >= 75
        c.kitties[1].needs = Some(NeedRateOverrides {
            bath: Some(0.4), // ratio 2.0 against the 0.2 baseline
            ..Default::default()
        });
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("Biscuit"), "blames the swimmer: {msg}");

        // Review amendment 2026-08-31: the contagion remedy sentence
        // appears only when the factor actually multiplies the charge.
        // An operator whose config never mentions the key must not be
        // told to lower it.
        let mut c = cfg();
        c.water.bath_gain = 15.0; // 60 + 15 = 75, not < 75
        let msg = c.validate().unwrap_err().to_string();
        assert!(
            !msg.contains("contagion_factor"),
            "a factor-absent budget failure must not name the factor: {msg}"
        );
    }

    #[test]
    fn membership_never_moves_the_budget() {
        // Spec 045 FR-008/D8: `bidirectional` moves who pays, never the
        // per-cat per-tick maximum (one charge, same magnitude, same
        // ceiling gate — FR-003), so the 044 headroom law stands
        // verbatim: the sibling test's accept and reject configs must
        // accept/reject IDENTICALLY with the membership flipped. A
        // divergence here is exactly the bug this arm exists to catch —
        // someone teaching `validate_water` to price membership.
        for membership in [
            ContagionMembership::OptionA,
            ContagionMembership::Bidirectional,
        ] {
            // The Gen 1 factor accepts (FR-011's bit-identical check).
            let mut c = cfg();
            c.water.contagion_factor = 1.0;
            c.water.contagion_membership = membership;
            c.validate()
                .unwrap_or_else(|e| panic!("factor 1.0 must validate under {membership:?}: {e}"));

            // The crowded default world rejects, naming the same dials.
            let mut c = cfg();
            c.water.contagion_factor = 5.0;
            c.water.contagion_membership = membership;
            let msg = c.validate().unwrap_err().to_string();
            assert!(
                msg.contains("[water] bath_gain_ceiling") && msg.contains("contagion_factor"),
                "the reject and its remedies must be membership-blind \
                 ({membership:?}): {msg}"
            );

            // The same factor with real headroom accepts.
            let mut c = cfg();
            c.water.contagion_factor = 5.0;
            c.water.bath_gain_ceiling = 50.0; // 50 + 17.5 < 75
            c.water.contagion_membership = membership;
            c.validate().unwrap_or_else(|e| {
                panic!("factor 5.0 with headroom must validate under {membership:?}: {e}")
            });
        }
    }

    #[test]
    fn contagion_factor_bounds_are_checked_even_when_wet_fur_is_off() {
        // Spec 044 FR-010: nonsense is nonsense whether or not the charge
        // could ever fire — the bounds check precedes the gain == 0.0
        // early return, so a config carrying a NaN factor beside a
        // disabled mechanic is still refused loudly.
        for bad in [f32::NAN, f32::INFINITY, f32::NEG_INFINITY, -1.0] {
            let mut c = cfg();
            c.water.contagion_factor = bad;
            let msg = c.validate().unwrap_err().to_string();
            assert!(msg.contains("[water] contagion_factor"), "{bad}: {msg}");

            let mut c = cfg();
            c.water.bath_gain = 0.0;
            c.water.contagion_factor = bad;
            let msg = c.validate().unwrap_err().to_string();
            assert!(
                msg.contains("[water] contagion_factor"),
                "{bad} with wet fur off: {msg}"
            );
        }
        // The legal states: absent (the default), the explicit off state,
        // and the Gen 1 ruling.
        cfg().validate().expect("default (absent) validates");
        for good in [0.0, 1.0] {
            let mut c = cfg();
            c.water.contagion_factor = good;
            c.validate()
                .unwrap_or_else(|e| panic!("factor {good} must validate: {e}"));
        }
        // Sibling parity (review amendment 2026-08-31): every other
        // [water] key is bounded 0..=100; the factor is too. The top of
        // the range is legal (beside a disabled gain, so the headroom
        // budget stays out of the way), one step past it is not.
        let mut c = cfg();
        c.water.bath_gain = 0.0;
        c.water.contagion_factor = 100.0;
        c.validate().expect("factor 100.0 is the top of the range");
        let mut c = cfg();
        c.water.bath_gain = 0.0;
        c.water.contagion_factor = 100.5;
        let msg = c.validate().unwrap_err().to_string();
        assert!(
            msg.contains("[water] contagion_factor"),
            "over-range: {msg}"
        );
    }

    #[test]
    fn fingerprint_ignores_water_tunables() {
        let a = cfg();
        let mut b = cfg();
        b.water.bath_gain = 0.0;
        b.water.bath_gain_ceiling = 10.0;
        assert_eq!(
            a.fingerprint(),
            b.fingerprint(),
            "pricing water must never orphan a saved world (spec 024)"
        );
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
    fn the_play_gradient_rejects_equality_at_every_link() {
        // Spec 025 FR-005: the chain is strict -- equality anywhere makes
        // two play forms indistinguishable, which is the team-neutrality
        // the split exists to remove.
        for key in ["solo_play_relief", "play_relief", "play_relief_bug"] {
            let mut c = cfg();
            match key {
                "solo_play_relief" => c.actions.solo_play_relief = c.actions.play_relief,
                "play_relief" => c.actions.play_relief = c.actions.play_relief_bug,
                _ => c.actions.play_relief_bug = c.actions.play_relief_greeble,
            }
            let msg = c.validate().unwrap_err().to_string();
            // The full "[actions] {key} is" prefix, not a bare contains(key):
            // "play_relief" is a substring of every play key, so a bare
            // contains could never catch the error blaming the wrong link.
            assert!(
                msg.contains(&format!("[actions] {key} is")),
                "{key} equality must be rejected under its own key: {msg}"
            );
            assert!(
                msg.contains("strictly less than"),
                "the rule is named: {msg}"
            );
        }
    }

    #[test]
    fn the_duet_ceiling_holds_at_exactly_twice_the_kitty_value() {
        // Spec 025 FR-006: at greeble == 2 x kitty a myopic defection is
        // exactly team-neutral -- the dilemma's edge goes flat -- so the
        // boundary itself is rejected, and the message teaches why.
        let mut c = cfg();
        c.actions.play_relief_greeble = 2.0 * c.actions.play_relief;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("play_relief_greeble"), "{msg}");
        assert!(
            msg.contains("both cats"),
            "the error explains the duet economics: {msg}"
        );

        // Just under the ceiling (and above the bug value) passes.
        let mut c = cfg();
        c.actions.play_relief_greeble = 2.0 * c.actions.play_relief - 0.5;
        c.validate()
            .expect("a greeble just under the ceiling is lawful");
    }

    #[test]
    fn the_new_play_keys_reject_negative_and_non_finite_values() {
        // Spec 025 FR-007, including the tightening the contract names:
        // a NaN play_relief previously slipped past the old guard by
        // accident of comparison semantics (solo > NaN is false).
        for poison in [f32::NAN, f32::INFINITY, -1.0] {
            for setter in [
                (|c: &mut Config, v: f32| c.actions.solo_play_relief = v) as fn(&mut Config, f32),
                |c, v| c.actions.play_relief = v,
                |c, v| c.actions.play_relief_bug = v,
                |c, v| c.actions.play_relief_greeble = v,
            ] {
                let mut c = cfg();
                setter(&mut c, poison);
                assert!(
                    c.validate().is_err(),
                    "{poison} must be rejected wherever it lands"
                );
            }
        }
    }

    #[test]
    fn the_remaining_relief_dials_reject_negative_and_non_finite_values() {
        // The finiteness sweep (2026-08-06, spec 025 review finding 7):
        // the six non-play relief dials joined the play keys' table.
        // Before this, `cuddle_relief = nan` validated cleanly and the
        // first duet rest tick poisoned the need and every downstream
        // happiness metric for the rest of the run.
        for poison in [f32::NAN, f32::INFINITY, -1.0] {
            for (name, setter) in [
                (
                    "eat_relief",
                    (|c: &mut Config, v: f32| c.actions.eat_relief = v) as fn(&mut Config, f32),
                ),
                ("drink_relief", |c, v| c.actions.drink_relief = v),
                ("sleep_relief", |c, v| c.actions.sleep_relief = v),
                ("sleep_relief_sunbeam", |c, v| {
                    c.actions.sleep_relief_sunbeam = v
                }),
                ("groom_relief", |c, v| c.actions.groom_relief = v),
                ("rest_mutual_relief", |c, v| {
                    c.actions.rest_mutual_relief = v
                }),
                ("rest_drip_relief", |c, v| c.actions.rest_drip_relief = v),
                ("groom_cuddle_relief", |c, v| {
                    c.actions.groom_cuddle_relief = v
                }),
            ] {
                let mut c = cfg();
                setter(&mut c, poison);
                let err = c.validate().expect_err("poison must be rejected");
                assert!(
                    err.to_string().contains(name),
                    "{poison} in {name} must be rejected by name, got: {err}"
                );
            }
        }
    }

    #[test]
    fn a_config_carrying_the_retired_cuddle_relief_fails_with_a_map() {
        // Spec 041 FR-005 (owner's noisy-failure ruling, 2026-08-28): the
        // retired key is a loud error carrying the migration map -- the
        // spec-025 pattern. Silently accepting it would either run a
        // doubled economy (engine defaults) or pretend the old economy
        // still exists; the owner chose the full compatibility break.
        let cfg_with = |extra: &str| -> Result<(), ConfigError> {
            let c: Config = toml::from_str(&format!(
                r#"
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

                [actions]
                eat_relief = 40.0
                drink_relief = 40.0
                sleep_relief = 5.0
                sleep_relief_sunbeam = 8.0
                groom_relief = 30.0
                play_relief = 20.0
                {extra}
            "#
            ))
            .expect("shape parses");
            c.validate()
        };

        let msg = cfg_with("cuddle_relief = 8.0")
            .expect_err("the retired key must fail loudly")
            .to_string();
        assert!(msg.contains("cuddle_relief"), "{msg}");
        assert!(
            msg.contains("rest_mutual_relief") && msg.contains("groom_cuddle_relief"),
            "the error carries the migration map: {msg}"
        );

        // Without the key, the same config is fine.
        cfg_with("").expect("a migrated config loads");
    }

    #[test]
    fn a_pre_025_config_outside_the_survivable_band_fails_with_a_map() {
        // The contract's two documented break classes: a legacy config
        // carrying play_relief >= 25 collides with the defaulted bug value
        // in the chain; one at or below 17.5 collides with the defaulted
        // greeble via the duet ceiling. Both must fail loudly, blaming the
        // defaulted key and pointing at the migration (pin the 025 keys).
        // In between, the band upgrades untouched.
        let legacy = |play_relief: f32| -> Config {
            toml::from_str(&format!(
                r#"
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

                [actions]
                eat_relief = 40.0
                drink_relief = 40.0
                sleep_relief = 5.0
                sleep_relief_sunbeam = 8.0
                groom_relief = 30.0
                play_relief = {play_relief}
            "#
            ))
            .expect("legacy shape parses")
        };

        let msg = legacy(25.0).validate().unwrap_err().to_string();
        assert!(msg.contains("play_relief_bug"), "{msg}");
        assert!(msg.contains("explicitly"), "points at the migration: {msg}");

        let msg = legacy(15.0).validate().unwrap_err().to_string();
        assert!(msg.contains("play_relief_greeble"), "{msg}");
        assert!(msg.contains("explicitly"), "points at the migration: {msg}");

        legacy(20.0)
            .validate()
            .expect("the in-band legacy config upgrades untouched");
    }

    #[test]
    fn the_shipped_play_gradient_is_lawful() {
        // 10 < 20 < 25 < 35 and 35 < 40: the defaults pass their own guards,
        // ceiling margin included.
        let c = cfg();
        c.validate().expect("shipped defaults validate");
        assert_eq!(c.actions.play_relief_bug, 25.0);
        assert_eq!(c.actions.play_relief_greeble, 35.0);
        assert!(c.actions.play_relief_greeble < 2.0 * c.actions.play_relief);
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
            play_relief = 20.0
        "#;
        let c: Config = toml::from_str(toml_src).expect("old-shape config parses");
        assert_eq!(c.behavior.urgency_weight, default_urgency_weight());
        assert_eq!(
            c.behavior.chase_exclusion_ticks,
            default_chase_exclusion_ticks()
        );
        assert_eq!(c.actions.solo_play_relief, default_solo_play_relief());
        // Spec 025: a today's-keys-only config gets the per-target play
        // values by default -- and the whole gradient still validates.
        assert_eq!(c.actions.play_relief_bug, default_play_relief_bug());
        assert_eq!(c.actions.play_relief_greeble, default_play_relief_greeble());
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

    /// Spec 020 review guard: the section sequence in `validate` is a
    /// message-order contract (amended FR-004) — the first-reported error
    /// for a multiply-invalid config follows the documented call order.
    /// These fixtures make a reorder of the call list fail here instead of
    /// silently changing operator-facing messages.
    #[test]
    fn multi_fault_first_error_follows_the_section_sequence() {
        // behavior (position 7) reports before purr (8).
        let mut c = Config::default();
        c.purr.min_ticks = 0;
        c.behavior.sunbeam_reach = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[behavior] sunbeam_reach"), "{msg}");

        // actions (9) reports before viewer (10).
        let mut c = Config::default();
        c.viewer.distress_patience_ticks = 0;
        c.actions.solo_play_relief = -1.0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[actions] solo_play_relief"), "{msg}");

        // world (1) reports before the dissolved sections entirely.
        let mut c = Config::default();
        c.persistence.save_every_ticks = 0;
        c.world.tick_ms = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("[world] tick_ms"), "{msg}");

        // persistence (13) reports before water (16, appended by spec 024).
        let mut c = Config::default();
        c.water.bath_gain = -1.0;
        c.persistence.save_every_ticks = 0;
        let msg = c.validate().unwrap_err().to_string();
        assert!(msg.contains("save_every_ticks"), "{msg}");
    }

    #[test]
    fn a_misspelt_dial_is_rejected_at_load_not_silently_ignored() {
        // The 2026-08-06 handoff's incident class: one typo'd letter used
        // to disable a safety validator without a word -- the file
        // validated and the world ran on the default.
        let err = toml::from_str::<Config>("[water]\nbath_gain_ceilling = 9999.0\n")
            .expect_err("an unknown key in a known table is refused");
        assert!(err.to_string().contains("bath_gain_ceilling"), "{err}");
    }

    #[test]
    fn a_key_in_the_wrong_table_is_rejected_at_load() {
        // The exact measurement that went wrong: a real dial, real value,
        // wrong table -- accepted silently, engine ran the default.
        let err = toml::from_str::<Config>("[thresholds]\nedge_penalty = 0.0\n")
            .expect_err("a known key under the wrong table is refused");
        assert!(err.to_string().contains("edge_penalty"), "{err}");
    }

    #[test]
    fn an_invented_section_is_rejected_at_load() {
        let err = toml::from_str::<Config>("[not_a_section]\nknob = 1\n")
            .expect_err("an unknown top-level table is refused");
        assert!(err.to_string().contains("not_a_section"), "{err}");
    }

    #[test]
    fn the_rl_and_plugins_tables_belong_to_other_parsers_and_still_load() {
        let text = "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
                    [rl.observation]\nkitty_slots = 4\n\n\
                    [plugins.greeter]\ncommand = \"/bin/true\"\n";
        let c: Config = toml::from_str(text).expect("foreign tables are recognised, not rejected");
        let plain: Config =
            toml::from_str("[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n").unwrap();
        assert_eq!(c, plain, "and they carry nothing into Config");
    }

    #[test]
    fn the_foreign_tables_never_serialize() {
        // GET /config serves this struct's JSON and engine_defaults_sha256
        // hashes its serialized defaults -- neither may grow keys.
        let json: serde_json::Value =
            serde_json::from_str(&serde_json::to_string(&Config::default()).unwrap()).unwrap();
        let obj = json.as_object().unwrap();
        assert!(!obj.contains_key("rl"), "rl leaked into serialization");
        assert!(
            !obj.contains_key("plugins"),
            "plugins leaked into serialization"
        );
        assert!(
            !obj.contains_key("watchdog"),
            "watchdog leaked into serialization (spec 040: server-owned, stamp must not move)"
        );
    }

    #[test]
    fn roam_cell_validation_refuses_zero_and_one() {
        // Spec 039 FR-005: a 1-tile cell silently immobilizes every bug —
        // a different world than anyone asked for. Refused, value named.
        for bad in [0u32, 1] {
            let mut c = cfg();
            c.elements.bug.roam_cell = Some(bad);
            let err = c.validate().unwrap_err().to_string();
            assert!(err.contains("[elements.bug] roam_cell"), "{err}");
            assert!(err.contains(&bad.to_string()), "{err}");
        }
    }

    #[test]
    fn roam_cell_validation_refuses_non_bug_tables() {
        // Research D3's deliberate divergence from the silent `servings`
        // precedent: the engine refuses what it will not honor.
        let mut c = cfg();
        c.elements.greeble.roam_cell = Some(4);
        let err = c.validate().unwrap_err().to_string();
        assert!(err.contains("[elements.greeble] roam_cell"), "{err}");

        let mut c = cfg();
        c.elements.sunbeam.roam_cell = Some(4);
        let err = c.validate().unwrap_err().to_string();
        assert!(err.contains("[elements.sunbeam] roam_cell"), "{err}");
    }

    #[test]
    fn roam_cell_validation_accepts_legal_values() {
        // 2 is the floor, 4 is the served package, 64 exceeds the world
        // (legal: the whole world becomes one cell).
        for good in [2u32, 4, 64] {
            let mut c = cfg();
            c.elements.bug.roam_cell = Some(good);
            c.validate()
                .unwrap_or_else(|e| panic!("roam_cell {good} must load: {e}"));
        }
    }

    #[test]
    fn roam_cell_stays_out_of_the_default_serialization() {
        // Spec 039 research D5: `engine_defaults_sha256` hashes the default
        // Config's serialized JSON, so an unset roam_cell must not appear as
        // a key — otherwise adding the field moves the stamp for a value
        // nobody set. Delete the field's `skip_serializing_if` and this test
        // goes red; it is the assertion aimed at exactly that attribute.
        let json = serde_json::to_string(&Config::default()).unwrap();
        assert!(!json.contains("roam_cell"), "{json}");
        // Same discipline for the pounce flag (FR-012): default-off must
        // not appear as a key. Delete its skip attribute and this reddens.
        assert!(!json.contains("pounce"), "{json}");
        // And for the greeble schedule flag (FR-015).
        assert!(!json.contains("dart"), "{json}");
        // Spec 042 (medium review #4): all twelve Playful 2.0 dials ride
        // the same discipline -- a dropped or mistyped skip attribute on
        // any of them moves the stamp silently and mints the re-baseline
        // debt the inert launch exists to avoid. Delete one skip and its
        // line here reddens.
        for key in [
            "w_value",
            "w_busy",
            "w_serious",
            "t_self",
            "t_partner",
            "critter_appeal",
            "comfort_weight",
        ] {
            assert!(!json.contains(key), "{key} leaked into the stamp: {json}");
        }
        // Spec 043: the here-word announce period rides the same
        // discipline — 0/absent is the launch state and the stamp must
        // not move for a value nobody set.
        assert!(
            !json.contains("announce_here"),
            "announce_here leaked into the stamp: {json}"
        );
        // Spec 044: the waterline contagion factor rides the same
        // discipline — 0.0/absent is the launch state.
        assert!(
            !json.contains("contagion_factor"),
            "contagion_factor leaked into the stamp: {json}"
        );
        // Spec 045: both lab dials ride the same discipline —
        // option_a/absent and false/absent are the launch states and the
        // stamp must not move for values nobody set. Delete either
        // field's skip attribute and its line here reddens.
        assert!(
            !json.contains("contagion_membership"),
            "contagion_membership leaked into the stamp: {json}"
        );
        assert!(
            !json.contains("contagion_aware_ladder"),
            "contagion_aware_ladder leaked into the stamp: {json}"
        );
    }

    #[test]
    fn contagion_factor_stays_out_of_the_stamp_at_explicit_zero() {
        // Spec 044 US1: the identity-skip half — an EXPLICIT 0.0 must
        // serialize the same as absent (skip_serializing_if reads the
        // value, not whether anyone wrote it), so a world that spells
        // out the off state cannot move the defaults stamp.
        let mut c = Config::default();
        c.water.contagion_factor = 0.0;
        let json = serde_json::to_string(&c).unwrap();
        assert!(
            !json.contains("contagion_factor"),
            "explicit 0.0 leaked into the stamp: {json}"
        );
    }

    #[test]
    fn contagion_factor_zero_parses_equal_to_absent() {
        // Spec 044 US1 scenario 2: `contagion_factor = 0.0` and an absent
        // key are the same world. The `absent` arm carries a [water] table
        // WITHOUT the key — the shape every existing world config has — so
        // a dropped `default` attribute reds here instead of hiding behind
        // the section-level default.
        let absent: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\n",
        )
        .unwrap();
        let zero: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\ncontagion_factor = 0.0\n",
        )
        .unwrap();
        assert_eq!(absent, zero);
        assert_eq!(absent.water.contagion_factor, 0.0);
    }

    #[test]
    fn contagion_membership_option_a_parses_equal_to_absent() {
        // Spec 045 FR-001/SC-001: `contagion_membership = "option_a"` and
        // an absent key are the same world — the shipped 044 rule. The
        // `absent` arm carries a [water] table WITHOUT the key, so a
        // dropped `default` attribute reds here instead of hiding behind
        // the section-level default.
        let absent: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\n",
        )
        .unwrap();
        let explicit: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\ncontagion_membership = \"option_a\"\n",
        )
        .unwrap();
        assert_eq!(absent, explicit);
        assert_eq!(
            absent.water.contagion_membership,
            ContagionMembership::OptionA
        );
        // The other variant actually parses — the dial is reachable.
        let bidi: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\ncontagion_membership = \"bidirectional\"\n",
        )
        .unwrap();
        assert_eq!(
            bidi.water.contagion_membership,
            ContagionMembership::Bidirectional
        );
    }

    #[test]
    fn contagion_membership_unknown_value_is_rejected_naming_both() {
        // Spec 045 FR-008: an unknown membership value must refuse the
        // config at load, and the error must name both legal values so
        // the lab config author sees the menu, not a shrug.
        let err = toml::from_str::<Config>(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [water]\nbath_gain = 3.5\ncontagion_membership = \"both\"\n",
        )
        .unwrap_err()
        .to_string();
        assert!(err.contains("option_a"), "error must name option_a: {err}");
        assert!(
            err.contains("bidirectional"),
            "error must name bidirectional: {err}"
        );
    }

    #[test]
    fn contagion_aware_ladder_false_parses_equal_to_absent() {
        // Spec 045 FR-005/SC-001: `contagion_aware_ladder = false` and an
        // absent key are the same world — the gate off, the stamp
        // unmoved. Same discipline as the sibling arms above.
        let absent: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [behavior]\nbudget_fraction_of_tick = 0.5\n",
        )
        .unwrap();
        let explicit: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [behavior]\nbudget_fraction_of_tick = 0.5\ncontagion_aware_ladder = false\n",
        )
        .unwrap();
        assert_eq!(absent, explicit);
        assert!(!absent.behavior.contagion_aware_ladder);
        let on: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [behavior]\nbudget_fraction_of_tick = 0.5\ncontagion_aware_ladder = true\n",
        )
        .unwrap();
        assert!(on.behavior.contagion_aware_ladder);
    }

    #[test]
    fn announce_here_zero_parses_equal_to_absent() {
        // Spec 043 US2: `announce_here = 0` and an absent key are the
        // same world — both the off state, both the defaults stamp.
        // The `absent` arm carries a [behavior] table WITHOUT the key —
        // the shape every existing world config has — so a dropped
        // `default` attribute reds here instead of hiding behind the
        // struct-level default.
        let absent: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [behavior]\nbudget_fraction_of_tick = 0.5\n",
        )
        .unwrap();
        let zero: Config = toml::from_str(
            "[world]\nwidth = 24\nheight = 24\ntick_ms = 800\nseed = 7\n\n\
             [behavior]\nbudget_fraction_of_tick = 0.5\nannounce_here = 0\n",
        )
        .unwrap();
        assert_eq!(absent, zero);
        assert_eq!(absent.behavior.announce_here, 0);
    }

    #[test]
    fn announce_here_round_trips_when_set() {
        // Spec 043 FR-001: a world that sets the knob keeps it through
        // serialize/deserialize — only the DEFAULT hides the key.
        let mut c = Config::default();
        c.behavior.announce_here = 4;
        let json = serde_json::to_string(&c).unwrap();
        assert!(json.contains("\"announce_here\":4"), "{json}");
        let back: Config = serde_json::from_str(&json).unwrap();
        assert_eq!(back.behavior.announce_here, 4);
    }

    #[test]
    fn dart_validation_refuses_non_greeble_tables() {
        // FR-015, same refusal discipline as roam_cell: the engine refuses
        // what it will not honor. Bugs are already on the schedule.
        let mut c = cfg();
        c.elements.bug.dart = true;
        let err = c.validate().unwrap_err().to_string();
        assert!(err.contains("[elements.bug] dart"), "{err}");

        let mut c = cfg();
        c.elements.sunbeam.dart = true;
        let err = c.validate().unwrap_err().to_string();
        assert!(err.contains("[elements.sunbeam] dart"), "{err}");
    }

    #[test]
    fn dart_validation_accepts_the_greeble_flag() {
        let mut c = cfg();
        c.elements.greeble.dart = true;
        c.validate()
            .expect("dart on the greeble table is the whole point");
    }

    // ---- spec 033 (T017): the vocabulary table's config law ----

    #[test]
    fn an_omitted_vocabulary_table_means_the_documented_defaults() {
        // US3/AC3: thirteen active kinds on, the two reserves off.
        let config = crate::test_support::test_config();
        let v = config.meow.vocabulary;
        assert!(v.want_eat && v.mew && v.purr && v.here_food && v.chirp);
        assert!(!v.trill && !v.ekekek, "reserves ship off");
        // And a bare [meow] table parses to the same defaults.
        let meow: MeowConfig = toml::from_str("").unwrap();
        assert_eq!(meow.vocabulary, VocabularyConfig::default());
    }

    #[test]
    fn a_misspelled_vocabulary_key_refuses_to_boot_naming_the_field() {
        // US3/AC4 (the PR-114 posture): strictness catches the typo.
        let err = toml::from_str::<VocabularyConfig>("here_fud = true").unwrap_err();
        assert!(
            err.to_string().contains("here_fud"),
            "the error names the offending field: {err}"
        );
    }

    #[test]
    fn a_partial_vocabulary_table_fills_the_rest_with_defaults() {
        let v: VocabularyConfig = toml::from_str(
            "chirp = false
trill = true",
        )
        .unwrap();
        assert!(!v.chirp, "the stated flag holds");
        assert!(v.trill, "a reserve can be armed by config alone");
        assert!(v.want_eat && v.here_sunbeam, "unstated kinds keep defaults");
        assert!(!v.ekekek, "unstated reserves keep their off default");
    }

    #[test]
    fn every_vocabulary_default_has_exactly_one_source() {
        // 033 review Finding 6: the defaults used to be encoded twice
        // (per-field serde attributes for partial tables, the Default impl
        // for omitted ones) with no cross-check — flipping one list, which
        // is exactly what arming a reserve will do, made the two parse
        // paths silently disagree. Now the container-level
        // #[serde(default)] routes BOTH paths through the one impl; this
        // pins that, exhaustively, by comparing a stated-flag parse
        // against the impl for every kind.
        let default = VocabularyConfig::default();
        for kind in crate::meow::MessageKind::ALL {
            if kind == crate::meow::MessageKind::WaitForMe {
                continue; // not a vocabulary flag
            }
            let flipped: VocabularyConfig = toml::from_str(&format!(
                "{} = {}",
                kind.wire_name(),
                !default.enabled(kind)
            ))
            .unwrap();
            for other in crate::meow::MessageKind::ALL {
                if other == crate::meow::MessageKind::WaitForMe {
                    continue;
                }
                let expected = if other == kind {
                    !default.enabled(kind)
                } else {
                    default.enabled(other)
                };
                assert_eq!(
                    flipped.enabled(other),
                    expected,
                    "stating {} must change {} alone; every other flag \
                     fills from the single Default impl",
                    kind.wire_name(),
                    kind.wire_name()
                );
            }
        }
    }
}
