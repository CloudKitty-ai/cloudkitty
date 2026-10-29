//! Spec 066 US4: the server's welfare-hazard intent gate
//! (`specs/066-welfare-hazard-guard/contracts/guard-law.md` §6, §7).
//!
//! Validation has already proven the `[welfare_hazard] acknowledged` list
//! equals the set of modes the config activates (guard-law §3), so this
//! module reads the LIST and never re-runs a predicate: a non-empty list
//! IS a hazardous world. Serving one takes the bare switch; serving one
//! says so in one boot line. Both are silent and inert on every other
//! config, so the served `cloudkitty.toml` boot stays byte-identical.

use cloudkitty_core::Config;

/// The bare start-up switch (owner ruling, clarify Q3). One home: the
/// argument parser matches on it and the refusal names it.
pub const SWITCH: &str = "--allow-welfare-hazard";

/// The acknowledged mode names, empty when the section is absent.
pub fn acknowledged(config: &Config) -> &[String] {
    config
        .welfare_hazard
        .as_ref()
        .map(|w| w.acknowledged.as_slice())
        .unwrap_or(&[])
}

/// Guard-law §6: `Err` iff the config acknowledges one or more modes and
/// the switch is absent. Called right after `Config::validate`, before
/// the registry, any snapshot move or any world.
pub fn gate(config: &Config, allowed: bool) -> anyhow::Result<()> {
    let modes = acknowledged(config);
    if modes.is_empty() || allowed {
        return Ok(());
    }
    anyhow::bail!(
        "this config acknowledges welfare-hazardous mode(s) {}; pass {SWITCH} to serve it on purpose",
        modes.join(", ")
    )
}

/// Guard-law §7: the one `info` line, only when a mode is acknowledged.
pub fn log_boot(config: &Config) {
    let modes = acknowledged(config);
    if modes.is_empty() {
        return; // silence keeps the served boot log byte-identical
    }
    tracing::info!(
        "welfare-hazardous world served on purpose ({SWITCH}): acknowledged modes {}",
        modes.join(", ")
    );
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::config::{InitialNeedsSpec, NeedInit, WelfareHazardConfig};

    fn hazardous() -> Config {
        let config = Config {
            initial_needs: Some(InitialNeedsSpec {
                cuddle: Some(NeedInit::Value(92.0)),
                ..Default::default()
            }),
            welfare_hazard: Some(WelfareHazardConfig {
                acknowledged: vec!["initial_needs".into()],
            }),
            ..Config::default()
        };
        config
            .validate()
            .expect("the acknowledged config validates");
        config
    }

    #[test]
    fn the_gate_refuses_an_acknowledged_config_without_the_switch() {
        let err = gate(&hazardous(), false)
            .expect_err("an acknowledged config without the switch is refused")
            .to_string();
        assert!(
            err.contains("initial_needs") && err.contains(SWITCH),
            "the refusal names the mode and the switch: {err}"
        );
    }

    #[test]
    fn the_switch_serves_an_acknowledged_config() {
        gate(&hazardous(), true).expect("the switch serves it");
    }

    #[test]
    fn a_config_with_no_acknowledged_mode_passes_with_or_without_the_switch() {
        gate(&Config::default(), false).expect("no mode, no switch: Ok");
        gate(&Config::default(), true).expect("no mode, switch: Ok and inert");
        let empty = Config {
            welfare_hazard: Some(WelfareHazardConfig {
                acknowledged: vec![],
            }),
            ..Config::default()
        };
        gate(&empty, false).expect("a written empty list acknowledges nothing");
    }

    fn captured_boot_log(config: &Config) -> String {
        crate::test_log::capture(|| log_boot(config))
    }

    #[test]
    fn the_boot_line_names_the_modes_once_and_only_when_acknowledged() {
        let logged = captured_boot_log(&hazardous());
        assert_eq!(logged.lines().count(), 1, "one line:\n{logged}");
        assert!(
            logged.contains("welfare-hazardous world served on purpose")
                && logged.contains(SWITCH)
                && logged.contains("acknowledged modes initial_needs"),
            "{logged}"
        );
        assert!(
            logged.contains(" INFO "),
            "guard-law §7: an info line, not a warning: {logged}"
        );
        let silent = captured_boot_log(&Config::default());
        assert!(
            silent.is_empty(),
            "zero lines on a config with no acknowledged mode:\n{silent}"
        );
    }
}
