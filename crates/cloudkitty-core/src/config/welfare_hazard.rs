//! The welfare-hazard registry (spec 066,
//! `specs/066-welfare-hazard-guard/contracts/guard-law.md` §2): the
//! closed list of config modes that manufacture a welfare hazard, each
//! with its activity predicate and the text of its first activating
//! site. The validator (`validate_welfare_hazard`), both shipped-config
//! sweeps and the server gate iterate `HazardMode::ALL`; adding a mode is
//! a new variant, a new `ALL` entry and a new guard-law row in the same
//! commit — a mode absent here is not guarded.
//!
//! Nothing here is read at decision time: the registry answers "what
//! does this config activate?" at load, and the answer never reaches a
//! world, a draw or an observation (FR-008).

use super::{Config, NeedInit};
use crate::needs::NeedKind;

/// A registered welfare-hazardous mode. The enum is the registry: a
/// `match` over it is exhaustive, so a new variant cannot be left out of
/// `name` or `activation`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HazardMode {
    /// Spec 065's manufactured distressed start: any governing
    /// initial-need setting raised above zero (guard-law §2 row 1).
    InitialNeeds,
    /// Spec 067's level-releasing needy preset seated on any kitty
    /// (guard-law §2 row 2). Mode name = preset name, one home.
    Needy,
    /// Spec 067's hold-to-the-limit needy preset seated on any kitty
    /// (guard-law §2 row 3): a sustained-grave world is its own statement.
    NeedyHold,
}

impl HazardMode {
    /// Registry order — the order the validator's "line to add", the
    /// sweeps' messages and the server's boot line list modes in.
    pub const ALL: &'static [HazardMode] = &[
        HazardMode::InitialNeeds,
        HazardMode::Needy,
        HazardMode::NeedyHold,
    ];

    /// The name an operator writes in `[welfare_hazard] acknowledged`.
    pub fn name(&self) -> &'static str {
        match self {
            HazardMode::InitialNeeds => "initial_needs",
            HazardMode::Needy => crate::needy::NAME,
            HazardMode::NeedyHold => crate::needy::HOLD_NAME,
        }
    }

    /// `Some(site)` when `config` activates this mode, naming the FIRST
    /// activating setting in the validator's order (`validate_initial_needs`:
    /// the roster-wide table, then kitties in config order, needs in
    /// `NeedKind::ALL` order; the needy modes: kitties in config order);
    /// `None` when the mode is inactive.
    pub fn activation(&self, config: &Config) -> Option<String> {
        match self {
            HazardMode::InitialNeeds => initial_needs_site(config),
            HazardMode::Needy => seat_site(config, crate::needy::NAME),
            HazardMode::NeedyHold => seat_site(config, crate::needy::HOLD_NAME),
        }
    }
}

/// The first kitty in config order seated on `preset` (spec 067 FR-009):
/// the seat is the hazard, the `[needy]` table is only its parameters.
fn seat_site(config: &Config, preset: &str) -> Option<String> {
    config
        .kitties
        .iter()
        .find(|k| k.behavior == preset)
        .map(|k| {
            format!(
                "[[kitty]] '{}' (id {}) behavior = \"{preset}\"",
                k.name, k.id
            )
        })
}

/// The widest predicate (owner ruling, spec 066 clarify Q2): a bare value
/// `> 0` or a range whose `max > 0`, at either level, for any need. Runs
/// after `validate_initial_needs`, so every number read is finite and in
/// bounds. The setting is rendered exactly as that validator renders its
/// error value (`92`, `min = 0, max = 90`).
fn initial_needs_site(config: &Config) -> Option<String> {
    let mut specs: Vec<(String, &super::InitialNeedsSpec)> = Vec::new();
    if let Some(s) = &config.initial_needs {
        specs.push(("[initial_needs]".to_string(), s));
    }
    for k in &config.kitties {
        if let Some(s) = &k.initial_needs {
            specs.push((
                format!("[[kitty]] '{}' (id {}) initial_needs", k.name, k.id),
                s,
            ));
        }
    }
    for (home, spec) in specs {
        for kind in NeedKind::ALL {
            let Some(init) = spec.get(kind) else {
                continue;
            };
            let setting = match init {
                NeedInit::Value(v) if v > 0.0 => v.to_string(),
                NeedInit::Range(r) if r.max > 0.0 => format!("min = {}, max = {}", r.min, r.max),
                _ => continue,
            };
            return Some(format!("{home}.{} = {setting}", kind.as_str()));
        }
    }
    None
}

impl Config {
    /// Every registered mode this config activates, in registry order,
    /// each with its first activating site. Empty for every pre-066
    /// config and for a distressed-start section with every need at zero.
    pub fn active_hazards(&self) -> Vec<(HazardMode, String)> {
        HazardMode::ALL
            .iter()
            .filter_map(|mode| mode.activation(self).map(|site| (*mode, site)))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{InitialNeedsSpec, NeedInitRange};

    fn cfg() -> Config {
        Config::default()
    }

    fn value(v: f32) -> Option<NeedInit> {
        Some(NeedInit::Value(v))
    }

    fn range(min: f32, max: f32) -> Option<NeedInit> {
        Some(NeedInit::Range(NeedInitRange { min, max }))
    }

    #[test]
    fn a_pre_feature_config_activates_nothing() {
        assert!(cfg().active_hazards().is_empty());
        assert_eq!(HazardMode::InitialNeeds.activation(&cfg()), None);
    }

    #[test]
    fn a_roster_wide_raised_need_activates_with_the_table_site() {
        let mut c = cfg();
        c.initial_needs = Some(InitialNeedsSpec {
            cuddle: value(92.0),
            ..Default::default()
        });
        assert_eq!(
            c.active_hazards(),
            vec![(
                HazardMode::InitialNeeds,
                "[initial_needs].cuddle = 92".to_string()
            )]
        );
    }

    #[test]
    fn a_per_kitty_override_alone_activates_and_names_the_kitty() {
        // The phase-1b P shape: no roster-wide table, one kitty's entry.
        let mut c = cfg();
        assert!(c.initial_needs.is_none());
        let k = &mut c.kitties[1];
        k.initial_needs = Some(InitialNeedsSpec {
            play: value(60.0),
            ..Default::default()
        });
        let expected = format!(
            "[[kitty]] '{}' (id {}) initial_needs.play = 60",
            k.name, k.id
        );
        assert_eq!(
            c.active_hazards(),
            vec![(HazardMode::InitialNeeds, expected)]
        );
    }

    #[test]
    fn every_need_at_zero_is_inert() {
        let mut c = cfg();
        c.initial_needs = Some(InitialNeedsSpec {
            eat: value(0.0),
            drink: range(0.0, 0.0),
            ..Default::default()
        });
        c.kitties[0].initial_needs = Some(InitialNeedsSpec {
            bath: value(0.0),
            ..Default::default()
        });
        assert!(
            c.active_hazards().is_empty(),
            "expected an empty active set for all-zero settings, got {:?}",
            c.active_hazards()
        );
    }

    #[test]
    fn a_range_with_a_raised_max_activates_with_the_validators_rendering() {
        let mut c = cfg();
        c.initial_needs = Some(InitialNeedsSpec {
            sleep: range(0.0, 90.0),
            ..Default::default()
        });
        assert_eq!(
            c.active_hazards(),
            vec![(
                HazardMode::InitialNeeds,
                "[initial_needs].sleep = min = 0, max = 90".to_string()
            )]
        );
    }

    #[test]
    fn the_site_is_the_first_in_validator_order() {
        // Roster table beats a kitty entry; within a spec, eat before
        // cuddle (NeedKind::ALL order), skipping zeros.
        let mut c = cfg();
        c.kitties[0].initial_needs = Some(InitialNeedsSpec {
            eat: value(50.0),
            ..Default::default()
        });
        c.initial_needs = Some(InitialNeedsSpec {
            eat: value(0.0),
            cuddle: value(70.0),
            ..Default::default()
        });
        assert_eq!(
            c.active_hazards()[0].1,
            "[initial_needs].cuddle = 70",
            "the roster table's first raised need wins over the kitty entry"
        );
        c.initial_needs = None;
        assert!(
            c.active_hazards()[0].1.ends_with("initial_needs.eat = 50"),
            "without the table the kitty entry is the site: {:?}",
            c.active_hazards()
        );
    }

    #[test]
    fn the_registry_names_are_unique_and_in_all() {
        let names: Vec<&str> = HazardMode::ALL.iter().map(|m| m.name()).collect();
        assert_eq!(names, vec!["initial_needs", "needy", "needy_hold"]);
    }

    /// PR #469 review N4: `ALL` is tied to the enum. An exhaustive `match`
    /// over every variant builds the list, so a new variant fails to
    /// compile here until it is placed in `ALL` too.
    #[test]
    fn all_lists_every_variant_once() {
        let mut from_match = Vec::new();
        for mode in HazardMode::ALL {
            // Exhaustive by construction: adding a variant breaks the build.
            let placed = match mode {
                HazardMode::InitialNeeds => HazardMode::InitialNeeds,
                HazardMode::Needy => HazardMode::Needy,
                HazardMode::NeedyHold => HazardMode::NeedyHold,
            };
            from_match.push(placed);
        }
        let every_variant = [
            HazardMode::InitialNeeds,
            HazardMode::Needy,
            HazardMode::NeedyHold,
        ];
        assert_eq!(from_match, every_variant);
        assert_eq!(
            HazardMode::ALL,
            &every_variant[..],
            "ALL lists every variant once, in order"
        );
    }

    /// Spec 067 FR-009: a needy seat activates its own mode, naming the
    /// first such kitty in config order; the two presets are two modes.
    #[test]
    fn a_needy_seat_activates_its_mode_naming_the_first_kitty() {
        let mut c = cfg();
        assert_eq!(HazardMode::Needy.activation(&c), None);
        assert_eq!(HazardMode::NeedyHold.activation(&c), None);
        c.kitties[2].behavior = crate::needy::NAME.to_string();
        c.kitties[1].behavior = crate::needy::NAME.to_string();
        let (name, id) = (c.kitties[1].name.clone(), c.kitties[1].id);
        assert_eq!(
            c.active_hazards(),
            vec![(
                HazardMode::Needy,
                format!("[[kitty]] '{name}' (id {id}) behavior = \"needy\"")
            )],
            "the first needy seat in config order is the site"
        );
        c.kitties[0].behavior = crate::needy::HOLD_NAME.to_string();
        c.initial_needs = Some(InitialNeedsSpec {
            cuddle: value(92.0),
            ..Default::default()
        });
        let names: Vec<&str> = c.active_hazards().iter().map(|(m, _)| m.name()).collect();
        assert_eq!(
            names,
            vec!["initial_needs", "needy", "needy_hold"],
            "registry order, every active mode"
        );
        assert!(c.active_hazards()[2]
            .1
            .ends_with("behavior = \"needy_hold\""));
    }
}
