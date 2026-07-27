//! Validation: every rule the constitution and spec impose on
//! configuration, one validator per section (spec 020 FR-002). Rules
//! and messages are byte-unchanged from the pre-split file; the
//! section call sequence lives on `Config::validate` in `mod.rs`.

use super::{Config, ConfigError, ElementsConfig, TILES_PER_ELEMENT};
use crate::element::ElementType;

impl Config {
    /// Spec 006: every activity's duration bounds must satisfy 1 <= min <= max.
    pub(super) fn validate_durations(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_world(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_roster(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_thresholds(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_happiness(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_needs(&self) -> Result<(), ConfigError> {
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

    pub(super) fn validate_elements(&self) -> Result<(), ConfigError> {
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

    /// `[behavior]` only since spec 020: the purr, actions, viewer, events,
    /// and persistence rules this validator once accumulated live in their
    /// own section validators below.
    pub(super) fn validate_behavior(&self) -> Result<(), ConfigError> {
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
        // One row per nonzero-bounded field: `(field, value, expected)`,
        // message bytes verbatim per row (spec 020 D2 — the loop owns only
        // the if/return shape; a new bounded field is a new row).
        for (field, value, expected) in [
            (
                "[behavior] chase_patience_ticks",
                self.behavior.chase_patience_ticks,
                "must be at least 1 tick",
            ),
            (
                "[behavior] chase_exclusion_ticks",
                self.behavior.chase_exclusion_ticks,
                "must be at least 1 tick",
            ),
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
        Ok(())
    }

    pub(super) fn validate_purr(&self) -> Result<(), ConfigError> {
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
        Ok(())
    }

    /// `[actions]` relief rules; the duration bounds have their own
    /// validator (`validate_durations`), unchanged since spec 006.
    pub(super) fn validate_actions(&self) -> Result<(), ConfigError> {
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
        Ok(())
    }

    pub(super) fn validate_viewer(&self) -> Result<(), ConfigError> {
        if self.viewer.distress_patience_ticks == 0 {
            return Err(ConfigError::invalid(
                "[viewer] distress_patience_ticks",
                "0".to_string(),
                "must be at least 1 tick",
            ));
        }
        Ok(())
    }

    pub(super) fn validate_events(&self) -> Result<(), ConfigError> {
        // Row shape per spec 020 D2.
        for (field, value) in [
            (
                "[events] distress_retention",
                self.events.distress_retention,
            ),
            (
                "[events] activity_retention",
                self.events.activity_retention,
            ),
        ] {
            if value == 0 {
                return Err(ConfigError::invalid(
                    field,
                    "0".to_string(),
                    "must be at least 1",
                ));
            }
        }
        Ok(())
    }

    pub(super) fn validate_persistence(&self) -> Result<(), ConfigError> {
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
    ///
    /// Both branches are currently unreachable through `validate()`: roster
    /// uniqueness (unique in-bounds positions) pigeonholes the kitty count at
    /// ≤ area, and per-kind element maxima (≤ area/32, five kinds) cap the
    /// combined minimums below area. Retained deliberately as defense in
    /// depth — these are the direct statements of the capacity invariant, and
    /// they become load-bearing the moment the earlier validators' rules
    /// loosen. Do not delete as dead code.
    pub(super) fn validate_capacity(&self) -> Result<(), ConfigError> {
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
}
