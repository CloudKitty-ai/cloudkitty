//! Validation: every rule the constitution and spec impose on
//! configuration, one validator per section (spec 020 FR-002). Rules
//! and messages are byte-unchanged from the pre-split file; the
//! section call sequence lives on `Config::validate` in `mod.rs`.

use super::{Config, ConfigError, ElementsConfig, TILES_PER_ELEMENT};
use crate::element::ElementType;

/// Upper bounds on the purr knobs (spec 022 review): generous beyond any
/// real world (durations default 8-13 ticks; a million ticks is days of
/// sim time), but they keep the cooldown arithmetic provably exact --
/// duration and factor x duration both fit f64's integer range with room
/// to spare, so the "rest is never shortened" ceiling can never be
/// undercut by rounding, and `tick + cooldown` can never overflow.
const MAX_PURR_TICKS: u64 = 1_000_000;
const MAX_PURR_COOLDOWN_FACTOR: f32 = 1_000.0;

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
            // The roam tether (spec 039) is a bug-only mechanic; the engine
            // refuses the key where it would not honor it, rather than
            // letting a config line lie (deliberate divergence from the
            // silently-ignored non-chow `servings`).
            if let Some(cell) = rule.roam_cell {
                if !matches!(kind, ElementType::Bug) {
                    return Err(ConfigError::invalid(
                        format!("{field} roam_cell"),
                        cell.to_string(),
                        "only bugs are tethered (spec 039); remove this key",
                    ));
                }
                if cell < 2 {
                    return Err(ConfigError::invalid(
                        format!("{field} roam_cell"),
                        cell.to_string(),
                        "must be at least 2 tiles; a 1-tile cell would immobilize every bug",
                    ));
                }
            }
            // Same refusal discipline for the greeble schedule flag
            // (spec 039 third amendment, FR-015).
            if rule.dart && !matches!(kind, ElementType::Greeble) {
                return Err(ConfigError::invalid(
                    format!("{field} dart"),
                    "true".to_string(),
                    "only greebles take the dart schedule (spec 039); remove this key",
                ));
            }
        }
        // The spawn dials (spec 027). The jitter's floor-at-1 math is
        // total, but its draw is 32-bit: 2*jitter+1 must fit.
        if self.elements.ttl_jitter > (u32::MAX / 2 - 1) as u64 {
            return Err(ConfigError::invalid(
                "[elements] ttl_jitter",
                self.elements.ttl_jitter.to_string(),
                format!(
                    "must fit the RNG's 32-bit draw (at most {})",
                    u32::MAX / 2 - 1
                ),
            ));
        }
        if self.elements.spread_candidates < 1 {
            return Err(ConfigError::invalid(
                "[elements] spread_candidates",
                self.elements.spread_candidates.to_string(),
                "must be at least 1 (a spawn needs at least one candidate tile)",
            ));
        }
        if self.elements.spread_candidates > 10_000 {
            return Err(ConfigError::invalid(
                "[elements] spread_candidates",
                self.elements.spread_candidates.to_string(),
                "must be at most 10000 -- candidates are drawn per spawn, and \
                 more than any plausible world has tiles is a config error, \
                 refused here rather than discovered as a hang at spawn time",
            ));
        }
        let penalty = self.elements.edge_penalty;
        if !penalty.is_finite() || penalty < 0.0 {
            return Err(ConfigError::invalid(
                "[elements] edge_penalty",
                penalty.to_string(),
                "must be a finite number of tiles >= 0 (0 disables the interior preference)",
            ));
        }
        // Lake feasibility (spec 027): the guarantee needs a 2x2 to fit.
        // Today's world-size floors already imply this; the check is
        // explicit so the invariant survives a future floor change.
        if self.elements.water.min >= 4 && (self.world.width < 2 || self.world.height < 2) {
            return Err(ConfigError::invalid(
                "[world] width/height",
                format!("{}x{}", self.world.width, self.world.height),
                "a water minimum of 4+ guarantees a 2x2 lake, which needs a 2x2 world",
            ));
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
        // Spec 042 (Playful 2.0): the score/gate dials and comfort weights
        // share the house finite-and-non-negative rule -- a NaN anywhere
        // would poison the score's total order (FR-007). critter_appeal is
        // checked separately below: either sign is a lawful preference.
        let b = &self.behavior;
        let cw = &b.comfort_weight;
        for (field, value) in [
            ("[behavior] urgency_weight", self.behavior.urgency_weight),
            ("[behavior] tile_cost", self.behavior.tile_cost),
            ("[behavior] water_step_cost", self.behavior.water_step_cost),
            ("[behavior] w_value", b.w_value),
            ("[behavior] w_busy", b.w_busy),
            ("[behavior] w_serious", b.w_serious),
            ("[behavior] t_self", b.t_self),
            ("[behavior] t_partner", b.t_partner),
            // Spec 047: the consent line shares the rule — a NaN would
            // poison the gate's comparisons, a negative has no meaning.
            ("[behavior] consent_line", b.consent_line),
        ] {
            if !value.is_finite() || value < 0.0 {
                return Err(ConfigError::invalid(
                    field,
                    value.to_string(),
                    "must be a finite number of at least 0",
                ));
            }
        }
        // Spec 047 (medium review #4): needs cap at 100, so a consent line
        // above 100 can never block -- it would load clean, serialize as
        // "set", and silently do nothing. Bounded like the sibling
        // percentage dials (playful_comfort, worth_a_detour); 100 itself
        // is legal and documented as never-blocking.
        if b.consent_line > 100.0 {
            return Err(ConfigError::invalid(
                "[behavior] consent_line",
                b.consent_line.to_string(),
                "must be at most 100 (needs cap at 100, so a higher line can never block)",
            ));
        }
        // The comfort weights are strictly positive (medium review #5):
        // a zero weight would switch the get-serious trigger OFF for that
        // need entirely -- beyond what any lawful playful_comfort (which
        // must itself be > 0) could do. Down-weighting is the tool;
        // disabling is not on the dial.
        for (field, value) in [
            ("[behavior.comfort_weight] eat", cw.eat),
            ("[behavior.comfort_weight] drink", cw.drink),
            ("[behavior.comfort_weight] sleep", cw.sleep),
            ("[behavior.comfort_weight] play", cw.play),
            ("[behavior.comfort_weight] cuddle", cw.cuddle),
            ("[behavior.comfort_weight] bath", cw.bath),
        ] {
            if !value.is_finite() || value <= 0.0 {
                return Err(ConfigError::invalid(
                    field,
                    value.to_string(),
                    "must be a finite number greater than 0 (1.0 is the \
                     classic unweighted check; small weights defer a need, \
                     zero would disable its get-serious trigger outright)",
                ));
            }
        }
        if !b.critter_appeal.is_finite() {
            return Err(ConfigError::invalid(
                "[behavior] critter_appeal",
                b.critter_appeal.to_string(),
                "must be a finite number (either sign: negative means \
                 critters are less appealing than the baseline)",
            ));
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
        // Spec 028: the scripted responders' shared cuddle gate lives on the
        // need scale.
        let gate = self.behavior.cuddle_real_threshold;
        if !gate.is_finite() || !(0.0..=100.0).contains(&gate) {
            return Err(ConfigError::invalid(
                "[behavior] cuddle_real_threshold",
                gate.to_string(),
                "must be a finite number in [0, 100] -- the need scale",
            ));
        }
        // Spec 049 FR-043: the reply listener floor is a stamped intensity
        // (need/100), so it lives on [0, 1] when set; NaN is never a floor.
        if let Some(floor) = self.behavior.reply_intensity_floor {
            if !floor.is_finite() || !(0.0..=1.0).contains(&floor) {
                return Err(ConfigError::invalid(
                    "[behavior] reply_intensity_floor",
                    floor.to_string(),
                    "must be a finite number in [0, 1] -- a caller's stamped \
                     intensity (need/100); unset means replies are off",
                ));
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
        if self.purr.max_ticks > MAX_PURR_TICKS {
            return Err(ConfigError::invalid(
                "[purr] max_ticks",
                self.purr.max_ticks.to_string(),
                "must be at most 1000000 (keeps the cooldown arithmetic exact)",
            ));
        }
        let p = self.purr.announce_probability;
        if !(0.0..=1.0).contains(&p) || p.is_nan() {
            return Err(ConfigError::invalid(
                "[purr] announce_probability",
                p.to_string(),
                "must be between 0 and 1",
            ));
        }
        let (f_min, f_max) = (self.purr.cooldown_factor_min, self.purr.cooldown_factor_max);
        if !f_min.is_finite() || f_min <= 0.0 {
            return Err(ConfigError::invalid(
                "[purr] cooldown_factor_min",
                f_min.to_string(),
                "must be a positive number",
            ));
        }
        if !f_max.is_finite() || f_max > MAX_PURR_COOLDOWN_FACTOR {
            return Err(ConfigError::invalid(
                "[purr] cooldown_factor_max",
                f_max.to_string(),
                "must be a finite number of at most 1000",
            ));
        }
        if f_min > f_max {
            return Err(ConfigError::invalid(
                "[purr] cooldown_factor_min",
                format!("{f_min} (cooldown_factor_max is {f_max})"),
                "must be at most cooldown_factor_max",
            ));
        }
        Ok(())
    }

    /// `[water]` wet fur (spec 024). The load-bearing rule is the last one:
    /// the ceiling plus the largest single trait-scaled charge must stay
    /// strictly below the safeguard threshold, so no amount of voluntary
    /// swimming can ever cause a safeguard or distress event -- the
    /// certification-hygiene guarantee is unrepresentable to break, not
    /// merely tested (spec 024 FR-004).
    pub(super) fn validate_water(&self) -> Result<(), ConfigError> {
        let gain = self.water.bath_gain;
        if !gain.is_finite() || !(0.0..=100.0).contains(&gain) {
            return Err(ConfigError::invalid(
                "[water] bath_gain",
                gain.to_string(),
                "must be a finite number between 0 and 100 (0 disables wet fur)",
            ));
        }
        let ceiling = self.water.bath_gain_ceiling;
        if !ceiling.is_finite() || !(0.0..=100.0).contains(&ceiling) {
            return Err(ConfigError::invalid(
                "[water] bath_gain_ceiling",
                ceiling.to_string(),
                "must be a finite number between 0 and 100",
            ));
        }
        // Contagion bounds sit BEFORE the gain == 0.0 early return (spec
        // 044 FR-010): nonsense is nonsense even beside a disabled
        // mechanic, and a config must not start passing validation just
        // because wet fur was switched off.
        let factor = self.water.contagion_factor;
        if !factor.is_finite() || !(0.0..=100.0).contains(&factor) {
            return Err(ConfigError::invalid(
                "[water] contagion_factor",
                factor.to_string(),
                "must be a finite number between 0 and 100 (0 disables \
                 waterline contagion)",
            ));
        }
        if gain == 0.0 {
            // Wet fur disabled: no charge exists, nothing to budget.
            return Ok(());
        }
        let baseline = self.needs.bath;
        if baseline <= 0.0 {
            return Err(ConfigError::invalid(
                "[needs] bath",
                baseline.to_string(),
                "must be positive while [water] bath_gain is nonzero -- the \
                 wet-fur charge scales each cat by its bath rise relative to \
                 this baseline",
            ));
        }
        // The largest single charge any rostered cat can receive, and who
        // (Config::bath_ratio, the same scale the engine charges by).
        let (max_ratio, swimmer) = self
            .kitties
            .iter()
            .map(|k| (self.bath_ratio(k.id), k))
            .fold((1.0_f32, None), |(best, who), (ratio, k)| {
                if ratio > best {
                    (ratio, Some(k))
                } else {
                    (best, who)
                }
            });
        // Spec 044: contagion scales the same per-tick charge by the
        // factor, so above 1.0 the contagion charge IS the worst case; at
        // or below 1.0 occupancy still is (dry-member-only, no cat pays
        // both) and the budget is bit-identical to the occupancy-only one.
        let max_charge = gain * max_ratio * factor.max(1.0);
        let safeguard = self.thresholds.safeguard;
        if ceiling + max_charge >= safeguard {
            let blame = swimmer.map_or_else(
                || "the baseline cat".to_string(),
                |k| format!("'{}'", k.name),
            );
            return Err(ConfigError::invalid(
                "[water] bath_gain_ceiling",
                format!("{ceiling} (largest single charge is {max_charge} for {blame})"),
                format!(
                    "ceiling plus the largest trait-scaled charge must stay \
                     below the safeguard threshold ({safeguard}); lower the \
                     ceiling, the gain, or that cat's [kitty.needs] bath \
                     rise -- or set [water] bath_gain = 0 to disable wet \
                     fur (both [water] keys have engine defaults, so this \
                     can fire for a config that never wrote them){}",
                    if factor > 1.0 {
                        "; when [water] contagion_factor is above 1 it \
                         multiplies the charge, so lowering the factor is \
                         a remedy too"
                    } else {
                        ""
                    }
                ),
            ));
        }
        Ok(())
    }

    /// `[meow]` law rows (spec 028): the announce band well-formed, the
    /// window alive, and both retirement eras' key names rejected loudly.
    pub(super) fn validate_meow(&self) -> Result<(), ConfigError> {
        let m = &self.meow;
        if m.recent_window_ticks < 1 {
            return Err(ConfigError::invalid(
                "[meow] recent_window_ticks",
                m.recent_window_ticks.to_string(),
                "must be at least 1 -- the per-kind emission cooldown",
            ));
        }
        // Spec 049 FR-017: the digest window is a positive integer multiple
        // of the cooldown, so the rate cell's maximum (window / cooldown
        // calls) is exact. Both keys named: the fix is to move either.
        if m.digest_window_ticks == 0
            || !m.digest_window_ticks.is_multiple_of(m.recent_window_ticks)
        {
            return Err(ConfigError::invalid(
                "[meow] digest_window_ticks",
                m.digest_window_ticks.to_string(),
                format!(
                    "must be a positive integer multiple of [meow] recent_window_ticks ({}) \
                     -- the rate cell counts calls per window / cooldown",
                    m.recent_window_ticks
                ),
            ));
        }
        if !m.announce_threshold.is_finite()
            || m.announce_threshold <= 0.0
            || m.announce_threshold > 100.0
        {
            return Err(ConfigError::invalid(
                "[meow] announce_threshold",
                m.announce_threshold.to_string(),
                "must be a finite number in (0, 100] -- the need scale",
            ));
        }
        if !m.announce_hysteresis.is_finite()
            || m.announce_hysteresis < 0.0
            || m.announce_hysteresis >= m.announce_threshold
        {
            return Err(ConfigError::invalid(
                "[meow] announce_hysteresis",
                m.announce_hysteresis.to_string(),
                "must be a finite number of at least 0 and below \
                 announce_threshold -- disarm happens at threshold - hysteresis",
            ));
        }
        Ok(())
    }

    /// `[actions]` relief rules; the duration bounds have their own
    /// validator (`validate_durations`), unchanged since spec 006.
    ///
    /// Spec 025: the play economy is a validated gradient, not four loose
    /// dials. Order of checks: finiteness first, then the strict chain,
    /// then the duet ceiling -- an error always names the most upstream
    /// problem.
    pub(super) fn validate_actions(&self) -> Result<(), ConfigError> {
        let a = &self.actions;
        // Every relief dial shares one finiteness/negativity rule. Spec 025
        // built the table for the four play keys; the remaining six joined
        // 2026-08-06 (the 025 review's finding 7): before that,
        // `cuddle_relief = nan` passed validation and the first duet rest
        // tick propagated NaN into the need and every downstream happiness
        // metric. Zero stays legal -- "this action relieves nothing" is a
        // strange world, not an invalid one.
        for (key, value) in [
            ("[actions] solo_play_relief", a.solo_play_relief),
            ("[actions] play_relief", a.play_relief),
            ("[actions] play_relief_bug", a.play_relief_bug),
            ("[actions] play_relief_greeble", a.play_relief_greeble),
            ("[actions] eat_relief", a.eat_relief),
            ("[actions] drink_relief", a.drink_relief),
            ("[actions] sleep_relief", a.sleep_relief),
            ("[actions] sleep_relief_sunbeam", a.sleep_relief_sunbeam),
            ("[actions] groom_relief", a.groom_relief),
            ("[actions] cosleep_drip_relief", a.cosleep_drip_relief),
            ("[actions] cosleep_mutual_relief", a.cosleep_mutual_relief),
            ("[actions] rest_mutual_relief", a.rest_mutual_relief),
            ("[actions] rest_drip_relief", a.rest_drip_relief),
            ("[actions] groom_cuddle_relief", a.groom_cuddle_relief),
        ] {
            if !value.is_finite() || value < 0.0 {
                return Err(ConfigError::invalid(
                    key,
                    value.to_string(),
                    "must be a finite number of at least 0",
                ));
            }
        }
        // The strict chain: solo < kitty < bug < greeble. Equality anywhere
        // makes two play forms indistinguishable -- exactly the
        // team-neutrality the split exists to remove. Each link carries its
        // own why: the doctrine phrase belongs to the solo/kitty link alone
        // (FR-005), and the kitty/bug link is where a pre-025 config
        // collides with the compiled default, so that error carries the
        // migration map.
        for (key, value, bound_name, bound, why) in [
            (
                "[actions] solo_play_relief",
                a.solo_play_relief,
                "play_relief",
                a.play_relief,
                "playing together must stay the better deal",
            ),
            (
                "[actions] play_relief",
                a.play_relief,
                "play_relief_bug",
                a.play_relief_bug,
                "a config written before spec 025 hits this through the compiled \
                 default (25): set play_relief_bug and play_relief_greeble explicitly",
            ),
            (
                "[actions] play_relief_bug",
                a.play_relief_bug,
                "play_relief_greeble",
                a.play_relief_greeble,
                "critter play ranks bugs below greebles",
            ),
        ] {
            if value >= bound {
                return Err(ConfigError::invalid(
                    key,
                    value.to_string(),
                    format!(
                        "must be strictly less than {bound_name} ({bound}) -- the play \
                         gradient is solo < kitty < bug < greeble, and {why}"
                    ),
                ));
            }
        }
        // The duet ceiling, the load-bearing bound: a duet relieves BOTH
        // cats, so team welfare earns 2 x play_relief per duet tick. Below
        // the ceiling social play stays team-optimal and WantPlay
        // recruitment keeps its value; at or above it, cats should ignore
        // each other and the meow economy dies.
        if a.play_relief_greeble >= 2.0 * a.play_relief {
            return Err(ConfigError::invalid(
                "[actions] play_relief_greeble",
                a.play_relief_greeble.to_string(),
                format!(
                    "must be strictly less than 2 x play_relief ({}) -- a duet relieves \
                     both cats, so the team earns 2 x play_relief per duet tick; at or \
                     above this ceiling solo greeble-hunting beats social play and meow \
                     recruitment loses its value (a config written before spec 025 with \
                     play_relief at or below 17.5 hits this through the compiled default \
                     greeble (35): set play_relief_bug and play_relief_greeble explicitly)",
                    2.0 * a.play_relief
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
            ("[events] refusal_retention", self.events.refusal_retention),
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
    /// `[vision]` (spec 049): the disc must contain adjacency and the
    /// spec-012 yield rule's Manhattan-2 friend, which any r >= 2 gives
    /// (edge case "Radius validation"). No upper bound: a world-covering
    /// radius is the no-fog control.
    pub(super) fn validate_vision(&self) -> Result<(), ConfigError> {
        let v = &self.vision;
        if v.radius < 2 {
            return Err(ConfigError::invalid(
                "[vision] radius",
                v.radius.to_string(),
                "must be at least 2 -- adjacency (r >= 1) and the yield rule's \
                 Manhattan-2 friend must be inside the disc",
            ));
        }
        Ok(())
    }

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
