//! Spec 040: the serving welfare watchdog.
//!
//! A standing, read-only watch over the engine's own `distress_since`
//! records. The engine computes distress ages; nothing was watching them
//! continuously on the served world — F-027's co-sleep deadlock ran a
//! 2331-tick streak against an alarm line of 150 with nobody looking.
//! This module looks: crossing/reminder/recovery events for the log, a
//! status snapshot for `GET /welfare`. Detection only — it proposes
//! nothing, mutates nothing, draws no RNG (spec 040 FR-001/FR-006).
//!
//! Configuration rides the server-owned `[watchdog]` toml table (the
//! `[rl]`/`[plugins]` foreign-table pattern), so the engine `Config` and
//! `engine_defaults_sha256` are untouched by construction.

use std::collections::BTreeMap;

use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{KittyId, World};
use serde::{Deserialize, Serialize};

#[derive(Debug, thiserror::Error)]
pub enum WatchdogConfigError {
    #[error("{0}")]
    Message(String),
    #[error("{field} = {value}: {expected}")]
    Invalid {
        field: String,
        value: String,
        expected: String,
    },
}

/// The `[watchdog]` table. Absent = these defaults — the watch is on by
/// default; there is no off switch to forget (spec 040 FR-005).
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct WatchdogConfig {
    /// Alarm line in ticks of sustained distress — the certification
    /// bound (`max_distress_age` vs 150 in every battery since exp-004).
    pub threshold: u64,
    /// A streak past the line re-announces itself every this many ticks,
    /// so a long incident cannot scroll out of the log's attention.
    pub remind_every: u64,
}

impl Default for WatchdogConfig {
    fn default() -> Self {
        Self {
            threshold: 150,
            remind_every: 150,
        }
    }
}

#[derive(Debug, Default, Deserialize)]
struct FileWithWatchdog {
    #[serde(default)]
    watchdog: Option<WatchdogConfig>,
}

impl WatchdogConfig {
    /// Extracts and validates the `[watchdog]` table from a full config
    /// file's TOML text; everything else in the file is someone else's
    /// business. A file with no table yields the documented defaults.
    pub fn from_toml_str(text: &str) -> Result<Self, WatchdogConfigError> {
        let file: FileWithWatchdog =
            toml::from_str(text).map_err(|e| WatchdogConfigError::Message(e.to_string()))?;
        let config = file.watchdog.unwrap_or_default();
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<(), WatchdogConfigError> {
        for (field, value) in [
            ("[watchdog] threshold", self.threshold),
            ("[watchdog] remind_every", self.remind_every),
        ] {
            if value == 0 {
                return Err(WatchdogConfigError::Invalid {
                    field: field.to_string(),
                    value: "0".to_string(),
                    expected: "must be at least 1 tick".to_string(),
                });
            }
        }
        Ok(())
    }
}

/// One in-distress (kitty, need) with its current age — the endpoint's
/// row shape (spec 040 FR-003).
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct WelfareEntry {
    pub kitty_id: KittyId,
    pub kitty_name: String,
    pub need: NeedKind,
    pub age: u64,
}

/// What `GET /welfare` serves: every live distress age (not only the
/// alarming ones — the surface answers "how are the cats", the threshold
/// answers "should I worry").
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct WelfareStatus {
    pub threshold: u64,
    pub alarm_live: bool,
    pub entries: Vec<WelfareEntry>,
}

impl WelfareStatus {
    pub fn healthy(threshold: u64) -> Self {
        Self {
            threshold,
            alarm_live: false,
            entries: Vec::new(),
        }
    }
}

/// The events the log renders. Tests assert these; the tracing lines in
/// `sim_task` are a thin rendering of the same data (plan D2).
#[derive(Debug, Clone, PartialEq)]
pub enum AlarmEvent {
    Crossing {
        kitty_id: KittyId,
        kitty_name: String,
        need: NeedKind,
        age: u64,
    },
    Reminder {
        kitty_id: KittyId,
        kitty_name: String,
        need: NeedKind,
        age: u64,
    },
    Recovery {
        kitty_id: KittyId,
        kitty_name: String,
        need: NeedKind,
        final_age: u64,
    },
}

#[derive(Debug, Clone, Copy)]
struct Streak {
    last_alarm_age: u64,
    last_age: u64,
}

/// The watchdog's whole memory is this map — rebuilt from the world's own
/// `distress_since` after a restart (a live streak re-fires its crossing
/// once: re-announced beats forgotten, spec edge case / plan D5).
pub struct Watchdog {
    config: WatchdogConfig,
    streaks: BTreeMap<(KittyId, NeedKind), Streak>,
}

impl Watchdog {
    pub fn new(config: WatchdogConfig) -> Self {
        Self {
            config,
            streaks: BTreeMap::new(),
        }
    }

    /// Reads the world, returns the current welfare surface and whatever
    /// alarm events this observation produced. `&World` is the whole
    /// FR-006 argument: this cannot mutate the simulation.
    pub fn observe(&mut self, world: &World) -> (WelfareStatus, Vec<AlarmEvent>) {
        let mut events = Vec::new();
        let mut entries = Vec::new();
        let mut live: BTreeMap<(KittyId, NeedKind), u64> = BTreeMap::new();

        for kitty in world.kitties.iter() {
            for (&need, &since) in kitty.distress_since.iter() {
                let age = world.tick.saturating_sub(since);
                entries.push(WelfareEntry {
                    kitty_id: kitty.id,
                    kitty_name: kitty.name.clone(),
                    need,
                    age,
                });
                live.insert((kitty.id, need), age);

                if age >= self.config.threshold {
                    match self.streaks.get_mut(&(kitty.id, need)) {
                        None => {
                            self.streaks.insert(
                                (kitty.id, need),
                                Streak {
                                    last_alarm_age: age,
                                    last_age: age,
                                },
                            );
                            events.push(AlarmEvent::Crossing {
                                kitty_id: kitty.id,
                                kitty_name: kitty.name.clone(),
                                need,
                                age,
                            });
                        }
                        Some(streak) => {
                            if age.saturating_sub(streak.last_alarm_age)
                                >= self.config.remind_every
                            {
                                streak.last_alarm_age = age;
                                events.push(AlarmEvent::Reminder {
                                    kitty_id: kitty.id,
                                    kitty_name: kitty.name.clone(),
                                    need,
                                    age,
                                });
                            }
                            streak.last_age = age;
                        }
                    }
                }
            }
        }

        // Streaks whose distress entry is gone (or whose kitty somehow is,
        // though Article II says never): one recovery line each, with the
        // final length the streak reached.
        let cleared: Vec<((KittyId, NeedKind), Streak)> = self
            .streaks
            .iter()
            .filter(|(key, _)| !live.contains_key(key))
            .map(|(k, s)| (*k, *s))
            .collect();
        for ((kitty_id, need), streak) in cleared {
            self.streaks.remove(&(kitty_id, need));
            let kitty_name = world
                .kitties
                .iter()
                .find(|k| k.id == kitty_id)
                .map(|k| k.name.clone())
                .unwrap_or_else(|| format!("kitty {kitty_id}"));
            events.push(AlarmEvent::Recovery {
                kitty_id,
                kitty_name,
                need,
                final_age: streak.last_age,
            });
        }

        let status = WelfareStatus {
            threshold: self.config.threshold,
            alarm_live: !self.streaks.is_empty(),
            entries,
        };
        (status, events)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;

    use cloudkitty_core::Config;

    // ---- T002: the config table ----

    #[test]
    fn watchdog_config_absent_table_means_defaults() {
        let c = WatchdogConfig::from_toml_str("[world]\nwidth = 20\n").unwrap();
        assert_eq!(c, WatchdogConfig::default());
        assert_eq!(c.threshold, 150);
        assert_eq!(c.remind_every, 150);
    }

    #[test]
    fn watchdog_config_refuses_zero_threshold() {
        let err = WatchdogConfig::from_toml_str("[watchdog]\nthreshold = 0\n").unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[watchdog] threshold"), "{msg}");
        assert!(msg.contains('0'), "{msg}");
    }

    #[test]
    fn watchdog_config_refuses_zero_cadence() {
        let err = WatchdogConfig::from_toml_str("[watchdog]\nremind_every = 0\n").unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[watchdog] remind_every"), "{msg}");
    }

    #[test]
    fn watchdog_config_refuses_unknown_keys() {
        // The PR #114 strictness doctrine, applied to the new table.
        let err = WatchdogConfig::from_toml_str("[watchdog]\nthreshhold = 150\n").unwrap_err();
        assert!(err.to_string().contains("threshhold"), "{err}");
    }

    // ---- T003: the alarm state machine ----

    /// A world whose distress records are set by hand: the engine already
    /// owns the definition (age = tick − since); these tests own the
    /// scenarios. The kitty.rs test precedent constructs distress_since
    /// directly the same way.
    fn world() -> (World, Arc<Config>) {
        let config = Arc::new(Config::default());
        let world = World::generate(&config);
        (world, config)
    }

    fn events_over_streak(
        watchdog: &mut Watchdog,
        world: &mut World,
        kitty_index: usize,
        need: NeedKind,
        start_tick: u64,
        length: u64,
    ) -> Vec<AlarmEvent> {
        let mut all = Vec::new();
        world.kitties[kitty_index]
            .distress_since
            .insert(need, start_tick);
        for t in start_tick..=start_tick + length {
            world.tick = t;
            let (_, mut events) = watchdog.observe(world);
            all.append(&mut events);
        }
        // The streak clears; one more observation sees the recovery.
        world.kitties[kitty_index].distress_since.remove(&need);
        world.tick = start_tick + length + 1;
        let (_, mut events) = watchdog.observe(world);
        all.append(&mut events);
        all
    }

    #[test]
    fn watchdog_alarms_cross_remind_and_recover() {
        // SC-001 (streak length 500 rather than the task's 200, so the
        // reminder cadence is exercised in the same scenario): crossing
        // at exactly 150, reminders at 300 and 450, recovery at 500.
        let (mut world, _config) = world();
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        let id = world.kitties[0].id;
        let name = world.kitties[0].name.clone();
        let events = events_over_streak(&mut watchdog, &mut world, 0, NeedKind::Play, 1000, 500);
        assert_eq!(
            events,
            vec![
                AlarmEvent::Crossing {
                    kitty_id: id,
                    kitty_name: name.clone(),
                    need: NeedKind::Play,
                    age: 150
                },
                AlarmEvent::Reminder {
                    kitty_id: id,
                    kitty_name: name.clone(),
                    need: NeedKind::Play,
                    age: 300
                },
                AlarmEvent::Reminder {
                    kitty_id: id,
                    kitty_name: name.clone(),
                    need: NeedKind::Play,
                    age: 450
                },
                AlarmEvent::Recovery {
                    kitty_id: id,
                    kitty_name: name,
                    need: NeedKind::Play,
                    final_age: 500
                },
            ]
        );
    }

    #[test]
    fn watchdog_is_silent_below_the_line() {
        // Ordinary need pressure: distress that resolves before the
        // threshold logs nothing at all.
        let (mut world, _config) = world();
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        let events = events_over_streak(&mut watchdog, &mut world, 0, NeedKind::Eat, 500, 149);
        assert_eq!(events, Vec::new());
    }

    #[test]
    fn watchdog_f027_shaped_streak_alarms_at_150_of_2331() {
        // SC-002: the incident this exists for. A 2331-tick streak fires
        // its crossing at age exactly 150 and 15 total alarms at the
        // defaults (1 crossing + 14 reminders), then one recovery.
        let (mut world, _config) = world();
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        let events =
            events_over_streak(&mut watchdog, &mut world, 0, NeedKind::Sleep, 40_000, 2331);
        let crossings: Vec<_> = events
            .iter()
            .filter(|e| matches!(e, AlarmEvent::Crossing { .. }))
            .collect();
        let reminders = events
            .iter()
            .filter(|e| matches!(e, AlarmEvent::Reminder { .. }))
            .count();
        let recoveries: Vec<_> = events
            .iter()
            .filter(|e| matches!(e, AlarmEvent::Recovery { .. }))
            .collect();
        assert_eq!(crossings.len(), 1);
        assert!(
            matches!(crossings[0], AlarmEvent::Crossing { age: 150, .. }),
            "first alarm at age 150, got {:?}",
            crossings[0]
        );
        assert_eq!(reminders, 14, "reminders every 150 across 2331 ticks");
        assert_eq!(recoveries.len(), 1);
        assert!(matches!(
            recoveries[0],
            AlarmEvent::Recovery {
                final_age: 2331,
                ..
            }
        ));
    }

    #[test]
    fn watchdog_tracks_simultaneous_streaks_independently() {
        // Two cats (or one cat, two needs) are independent alarms, each
        // named (spec edge case).
        let (mut world, _config) = world();
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        world.kitties[0]
            .distress_since
            .insert(NeedKind::Play, 100);
        world.kitties[1]
            .distress_since
            .insert(NeedKind::Bath, 130);
        world.tick = 250;
        let (status, events) = watchdog.observe(&world);
        // kitty0/Play at age 150 crosses; kitty1/Bath at 120 does not.
        assert_eq!(events.len(), 1);
        assert!(matches!(
            &events[0],
            AlarmEvent::Crossing { kitty_id, need: NeedKind::Play, age: 150, .. }
                if *kitty_id == world.kitties[0].id
        ));
        assert!(status.alarm_live);
        assert_eq!(status.entries.len(), 2, "the surface reports BOTH live ages");
        world.tick = 280;
        let (status, events) = watchdog.observe(&world);
        assert_eq!(events.len(), 1, "kitty1/Bath crosses at its own 150");
        assert!(matches!(
            &events[0],
            AlarmEvent::Crossing { kitty_id, need: NeedKind::Bath, age: 150, .. }
                if *kitty_id == world.kitties[1].id
        ));
        assert!(status.alarm_live);
    }

    #[test]
    fn watchdog_status_healthy_shape() {
        let (mut world, _config) = world();
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        world.tick = 5_000;
        let (status, events) = watchdog.observe(&world);
        assert_eq!(status, WelfareStatus::healthy(150));
        assert!(events.is_empty());
    }
}

#[cfg(test)]
mod non_interference {
    use super::*;
    use std::sync::Arc;

    use cloudkitty_core::{BehaviorRegistry, Config, World};

    /// Spec 040 FR-006 / SC-004: a watched world IS the unwatched world.
    /// `observe(&World)` cannot mutate by type, but this pins the claim
    /// against any future "just one little write" drift.
    #[test]
    fn watchdog_watched_and_unwatched_worlds_are_identical() {
        let mut config = Config::default();
        config.world.seed = 90_210;
        config.validate().unwrap();
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .unwrap();

        let mut watched = World::generate(&config);
        let mut plain = World::generate(&config);
        let mut watchdog = Watchdog::new(WatchdogConfig::default());
        for _ in 0..2_000 {
            runtime.block_on(watched.tick(&registry, &config));
            let _ = watchdog.observe(&watched);
            runtime.block_on(plain.tick(&registry, &config));
        }
        assert_eq!(
            serde_json::to_string(&watched).unwrap(),
            serde_json::to_string(&plain).unwrap(),
            "the watchdog changed the world it was only supposed to watch"
        );
    }
}
