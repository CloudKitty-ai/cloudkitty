//! The key settings (spec 052): one list of the dials anyone has needed to
//! verify after a deploy, each as its EFFECTIVE value (after defaults and
//! validation), its engine default where one exists, and its SOURCE —
//! `toml` when the key is written in the loaded config file, `default`
//! when it is not.
//!
//! One list, three readers (FR-001): [`KeySettings::announce`] logs the
//! block once at boot, `GET /settings` serves it (JSON, or the same text
//! block under `Accept: text/plain`), and `docs/deploy/update.sh` prints
//! that text as its closing section. [`KeySettings::render_text`] is the
//! ONE renderer, so the journal, the wire and the terminal are the same
//! bytes by construction.
//!
//! The list lives here, in the server, because only the server sees all
//! three inputs together: the engine's [`Config`], its own `[watchdog]`
//! table (spec 040: a foreign table the engine never serializes) and the
//! raw config text (for presence). `GET /config` is untouched — it skips
//! every engine-defaulted field (spec 039's stamp discipline), which is
//! exactly why it cannot answer "is it on?" from outside.
//!
//! The source is decided by PRESENCE in the loaded file, never by comparing
//! the value to the default (FR-003a): a key written at its default reads
//! `[toml]` — the tag says the edit landed, the parenthesis says it changed
//! nothing. With no config file loaded, every source is `default`.

use std::fmt::Write as _;

use cloudkitty_core::config::ContagionMembership;
use cloudkitty_core::Config;
use serde::Serialize;
use serde_json::{json, Value};

use crate::watchdog::WatchdogConfig;

/// Where an effective value came from. Two values today: the server's
/// command line takes only paths and `--fresh`, and the only environment
/// variable it reads is the log filter, so nothing else can set a dial. An
/// override layer, if one is ever added, adds a variant here rather than a
/// rewrite.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Source {
    /// The key is written in the loaded config file.
    Toml,
    /// The key is absent from the file (or no file was loaded); the engine
    /// (or server) default is in force.
    Default,
}

impl Source {
    fn as_str(self) -> &'static str {
        match self {
            Source::Toml => "toml",
            Source::Default => "default",
        }
    }
}

/// One key setting: a dial, its effective value, its default (absent for
/// the world shape and the seats, which have none) and its source.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct Entry {
    /// The config section as the TOML spells it (`world`, `kitty`, …).
    pub group: &'static str,
    /// The key within the group; for seats, the kitty id.
    pub key: String,
    /// The effective value. Option keys carry a sentinel string when
    /// absent (`"unbounded"`, `"none"`), never `null`.
    pub value: Value,
    /// The engine (or server) default, where one exists.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub default: Option<Value>,
    pub source: Source,
}

/// The block: the stamp as its identity line, then the entries in display
/// order. Built once at boot, before the listener binds (FR-006a), and held
/// for the life of the process.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct KeySettings {
    /// `engine_defaults_sha256` (spec 039): the hash of the compiled
    /// defaults. A computed identity, not a dial, so it carries no source.
    pub engine_defaults_sha256: String,
    pub entries: Vec<Entry>,
}

/// `Toml` iff `[group] key` is written in the raw tree; `Default` when it
/// is not, or when there is no tree (no file was loaded). The path is the
/// entry's own group and key — never spelled a second time — so an entry
/// cannot report another dial's source.
fn present(raw: Option<&toml::Value>, group: &str, key: &str) -> Source {
    match raw.and_then(|r| r.get(group)).and_then(|g| g.get(key)) {
        Some(_) => Source::Toml,
        None => Source::Default,
    }
}

/// `Toml` iff the `i`-th `[[kitty]]` table is written in the raw tree.
fn present_seat(raw: Option<&toml::Value>, i: usize) -> Source {
    match raw
        .and_then(|r| r.get("kitty"))
        .and_then(|k| k.as_array())
        .and_then(|a| a.get(i))
    {
        Some(_) => Source::Toml,
        None => Source::Default,
    }
}

/// An Option dial as a JSON value: the number when set, the sentinel word
/// when not — so the reader sees the rule, never `null` (FR-003).
fn opt(v: Option<Value>, absent: &'static str) -> Value {
    v.unwrap_or_else(|| Value::String(absent.to_string()))
}

/// An f32 dial as the number it was WRITTEN as: the shortest decimal that
/// round-trips the f32 (`0.2`), not the f64 expansion a plain `f as f64`
/// prints (`0.20000000298023224`) — the block exists to be compared with the
/// toml by eye. A non-finite value (unreachable through validation) renders
/// as its name, never `null` (FR-003).
fn num(f: f32) -> Value {
    if !f.is_finite() {
        return Value::String(f.to_string());
    }
    let shortest: f64 = f.to_string().parse().unwrap_or(f64::from(f));
    json!(shortest)
}

fn membership(m: ContagionMembership) -> Value {
    serde_json::to_value(m).expect("ContagionMembership serializes to its snake_case name")
}

/// One entry, its source read from its OWN group and key.
fn entry(
    raw: Option<&toml::Value>,
    group: &'static str,
    key: &str,
    value: Value,
    default: Option<Value>,
) -> Entry {
    Entry {
        group,
        key: key.to_string(),
        value,
        default,
        source: present(raw, group, key),
    }
}

/// Builds the block from the validated engine config, the server's
/// `[watchdog]` table and the raw config tree (`None` when the server booted
/// on built-in defaults). Adding a dial is one `push` here plus one name in
/// the golden test below (FR-011).
pub fn build(config: &Config, watchdog: &WatchdogConfig, raw: Option<&toml::Value>) -> KeySettings {
    let d = Config::default();
    let wd = WatchdogConfig::default();
    let mut entries: Vec<Entry> = Vec::new();

    // The world shape and the seats have no defaults: a config without them
    // does not load (and Article III wants at least two seats).
    let w = &config.world;
    entries.push(entry(raw, "world", "width", json!(w.width), None));
    entries.push(entry(raw, "world", "height", json!(w.height), None));
    entries.push(entry(raw, "world", "seed", json!(w.seed), None));
    let seats: Vec<Entry> = config
        .kitties
        .iter()
        .enumerate()
        .map(|(i, k)| Entry {
            group: "kitty",
            key: k.id.to_string(),
            value: json!({ "name": k.name, "behavior": k.behavior }),
            default: None,
            source: present_seat(raw, i),
        })
        .collect();
    entries.extend(seats);

    // Fog Gen 1 (spec 049). A REQUIRED section under the 3.0 rule: a config
    // that omits it fails to load, so there is no default to fall back on and
    // no default column — the source can only ever read `toml`.
    entries.push(entry(
        raw,
        "vision",
        "radius",
        json!(config.vision.radius),
        None,
    ));
    entries.push(entry(
        raw,
        "vision",
        "memory_timeout_ticks",
        json!(config.vision.memory_timeout_ticks),
        None,
    ));

    // The fog want law's memory reach (spec 050); absent = today's unbounded rule.
    entries.push(entry(
        raw,
        "meow",
        "relief_memory_margin",
        opt(
            config.meow.relief_memory_margin.map(Value::from),
            "unbounded",
        ),
        Some(opt(
            d.meow.relief_memory_margin.map(Value::from),
            "unbounded",
        )),
    ));

    // The groom-other pricing curve (spec 054): pay per groomed tick is
    // min(ceiling, floor + slope · delivered/groom_relief). The retired
    // flat groom_cuddle_relief is an inert legacy key — never listed.
    entries.push(entry(
        raw,
        "actions",
        "groom_cuddle_floor",
        num(config.actions.groom_cuddle_floor),
        Some(num(d.actions.groom_cuddle_floor)),
    ));
    entries.push(entry(
        raw,
        "actions",
        "groom_cuddle_slope",
        num(config.actions.groom_cuddle_slope),
        Some(num(d.actions.groom_cuddle_slope)),
    ));
    entries.push(entry(
        raw,
        "actions",
        "groom_cuddle_ceiling",
        num(config.actions.groom_cuddle_ceiling),
        Some(num(d.actions.groom_cuddle_ceiling)),
    ));

    // Launch dials on the built-in chooser (specs 043, 045, 049).
    let b = &config.behavior;
    entries.push(entry(
        raw,
        "behavior",
        "announce_here",
        json!(b.announce_here),
        Some(json!(d.behavior.announce_here)),
    ));
    entries.push(entry(
        raw,
        "behavior",
        "contagion_aware_ladder",
        json!(b.contagion_aware_ladder),
        Some(json!(d.behavior.contagion_aware_ladder)),
    ));
    entries.push(entry(
        raw,
        "behavior",
        "reply_intensity_floor",
        opt(b.reply_intensity_floor.map(num), "none"),
        Some(opt(d.behavior.reply_intensity_floor.map(num), "none")),
    ));

    // Wet fur and the waterline (specs 024, 044, 045).
    let wa = &config.water;
    entries.push(entry(
        raw,
        "water",
        "bath_gain",
        num(wa.bath_gain),
        Some(num(d.water.bath_gain)),
    ));
    entries.push(entry(
        raw,
        "water",
        "bath_gain_ceiling",
        num(wa.bath_gain_ceiling),
        Some(num(d.water.bath_gain_ceiling)),
    ));
    entries.push(entry(
        raw,
        "water",
        "contagion_factor",
        num(wa.contagion_factor),
        Some(num(d.water.contagion_factor)),
    ));
    entries.push(entry(
        raw,
        "water",
        "contagion_membership",
        membership(wa.contagion_membership),
        Some(membership(d.water.contagion_membership)),
    ));

    // The welfare watchdog (spec 040): server-owned, so the engine's
    // `/config` never shows it — this block does.
    entries.push(entry(
        raw,
        "watchdog",
        "threshold",
        json!(watchdog.threshold),
        Some(json!(wd.threshold)),
    ));
    entries.push(entry(
        raw,
        "watchdog",
        "remind_every",
        json!(watchdog.remind_every),
        Some(json!(wd.remind_every)),
    ));

    KeySettings {
        engine_defaults_sha256: cloudkitty_rl::suite::engine_defaults_sha256(),
        entries,
    }
}

/// A value as it reads on a terminal: strings bare, a seat as
/// `<name> <behavior>`, everything else as JSON prints it.
fn plain(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Object(o) => {
            let name = o.get("name").map(plain).unwrap_or_default();
            let behavior = o.get("behavior").map(plain).unwrap_or_default();
            format!("{name} {behavior}")
        }
        other => other.to_string(),
    }
}

impl KeySettings {
    /// The block as text: the stamp line, then one line per entry —
    /// `group.key = value (default: d) [source]`, the parenthesis omitted
    /// where the key has no default. This is what the boot log says, what
    /// `Accept: text/plain` returns, and what the deploy script prints.
    pub fn render_text(&self) -> String {
        let mut out = String::new();
        let _ = writeln!(
            out,
            "engine_defaults_sha256 = {}",
            self.engine_defaults_sha256
        );
        for e in &self.entries {
            let _ = write!(out, "{}.{} = {}", e.group, e.key, plain(&e.value));
            if let Some(d) = &e.default {
                let _ = write!(out, " (default: {})", plain(d));
            }
            let _ = writeln!(out, " [{}]", e.source.as_str());
        }
        out
    }

    /// Every `group.key` name in display order, the stamp line first — the
    /// shape the golden test pins.
    pub fn names(&self) -> Vec<String> {
        std::iter::once("engine_defaults_sha256".to_string())
            .chain(
                self.entries
                    .iter()
                    .map(|e| format!("{}.{}", e.group, e.key)),
            )
            .collect()
    }

    /// The one boot event (FR-006): the whole block in a single `info`
    /// message, so a journal excerpt is evidence on its own. Lives here, not
    /// in `main.rs`, so a test can capture it (FR-012).
    pub fn announce(&self) {
        tracing::info!("key settings\n{}", self.render_text());
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::sync::{Arc, Mutex};

    /// The eleven optional listed keys: every dial on the list that carries
    /// a per-key default (the 3.0 rule: sections are required, only inert
    /// launch dials default). Removing them from a serialized
    /// `Config::default()` leaves a file that still loads.
    const OPTIONAL: &[(&str, &str)] = &[
        ("meow", "relief_memory_margin"),
        ("actions", "groom_cuddle_floor"),
        ("actions", "groom_cuddle_slope"),
        ("actions", "groom_cuddle_ceiling"),
        ("behavior", "announce_here"),
        ("behavior", "contagion_aware_ladder"),
        ("behavior", "reply_intensity_floor"),
        ("water", "bath_gain"),
        ("water", "bath_gain_ceiling"),
        ("water", "contagion_factor"),
        ("water", "contagion_membership"),
    ];

    /// A two-seat config with every optional listed key ABSENT, as a raw
    /// tree, proven to still load as a `Config`.
    fn minimal_raw() -> toml::Value {
        let mut config = Config::default();
        config.kitties.truncate(2);
        let text = toml::to_string(&config).expect("defaults serialize to TOML");
        let mut raw: toml::Value = text.parse().expect("and parse back");
        for (group, key) in OPTIONAL {
            if let Some(table) = raw.get_mut(group).and_then(|g| g.as_table_mut()) {
                table.remove(*key);
            }
        }
        assert!(
            raw.get("watchdog").is_none(),
            "the engine never serializes [watchdog]"
        );
        let text = toml::to_string(&raw).expect("the trimmed tree serializes");
        let reparsed: Config =
            toml::from_str(&text).expect("a config missing only optional keys still loads");
        reparsed.validate().expect("and validates");
        raw
    }

    fn minimal_config() -> Config {
        let mut config = Config::default();
        config.kitties.truncate(2);
        config
    }

    fn source_of(block: &KeySettings, name: &str) -> Source {
        block
            .entries
            .iter()
            .find(|e| format!("{}.{}", e.group, e.key) == name)
            .unwrap_or_else(|| panic!("no entry {name}"))
            .source
    }

    /// FR-011: the list is the contract. Adding or dropping a dial is a
    /// deliberate diff HERE, never a silent change to what a deploy prints.
    #[test]
    fn the_key_names_are_pinned() {
        let block = build(
            &minimal_config(),
            &WatchdogConfig::default(),
            Some(&minimal_raw()),
        );
        let expected: Vec<&str> = vec![
            "engine_defaults_sha256",
            "world.width",
            "world.height",
            "world.seed",
            "kitty.1",
            "kitty.2",
            "vision.radius",
            "vision.memory_timeout_ticks",
            "meow.relief_memory_margin",
            "actions.groom_cuddle_floor",
            "actions.groom_cuddle_slope",
            "actions.groom_cuddle_ceiling",
            "behavior.announce_here",
            "behavior.contagion_aware_ladder",
            "behavior.reply_intensity_floor",
            "water.bath_gain",
            "water.bath_gain_ceiling",
            "water.contagion_factor",
            "water.contagion_membership",
            "watchdog.threshold",
            "watchdog.remind_every",
        ];
        assert_eq!(
            block.names(),
            expected,
            "the key settings list moved — update the golden on purpose"
        );
    }

    /// FR-011a / FR-003a: source is PRESENCE in the file, not value == default.
    /// The one optional key is written AT its default, so a mutant that
    /// compares values reads `default` here and goes red.
    #[test]
    fn a_minimal_config_plus_one_written_key_sources_exactly_that_key() {
        let mut raw = minimal_raw();
        let default_floor = Config::default().actions.groom_cuddle_floor;
        raw["actions"].as_table_mut().unwrap().insert(
            "groom_cuddle_floor".into(),
            toml::Value::Float(default_floor.into()),
        );
        let block = build(&minimal_config(), &WatchdogConfig::default(), Some(&raw));

        for name in [
            "world.width",
            "world.height",
            "world.seed",
            "kitty.1",
            "kitty.2",
            "vision.radius",
            "vision.memory_timeout_ticks",
        ] {
            assert_eq!(
                source_of(&block, name),
                Source::Toml,
                "{name} is a required key"
            );
        }
        assert_eq!(
            source_of(&block, "actions.groom_cuddle_floor"),
            Source::Toml,
            "written at its default still reads toml"
        );
        for (group, key) in OPTIONAL {
            if *key == "groom_cuddle_floor" {
                continue;
            }
            let name = format!("{group}.{key}");
            assert_eq!(
                source_of(&block, &name),
                Source::Default,
                "{name} is absent from the file"
            );
        }
        assert_eq!(source_of(&block, "watchdog.threshold"), Source::Default);
        assert_eq!(source_of(&block, "watchdog.remind_every"), Source::Default);
    }

    /// FR-011a: no file loaded → every source is `default`, the block still complete.
    #[test]
    fn no_config_file_means_every_source_is_default() {
        let block = build(&minimal_config(), &WatchdogConfig::default(), None);
        assert_eq!(block.entries.len(), 20);
        for e in &block.entries {
            assert_eq!(e.source, Source::Default, "{}.{}", e.group, e.key);
        }
    }

    /// FR-003: an Option dial renders the rule its absence selects, in both
    /// value and default, never `null`; set, it renders the number.
    #[test]
    fn option_dials_render_their_rule_never_null() {
        let mut config = minimal_config();
        let block = build(&config, &WatchdogConfig::default(), None);
        let margin = block
            .entries
            .iter()
            .find(|e| e.key == "relief_memory_margin")
            .unwrap();
        assert_eq!(margin.value, json!("unbounded"));
        assert_eq!(margin.default, Some(json!("unbounded")));
        let floor = block
            .entries
            .iter()
            .find(|e| e.key == "reply_intensity_floor")
            .unwrap();
        assert_eq!(floor.value, json!("none"));
        assert_eq!(floor.default, Some(json!("none")));
        for e in &block.entries {
            assert!(!e.value.is_null(), "{}.{} is null", e.group, e.key);
        }

        config.meow.relief_memory_margin = Some(0);
        let block = build(&config, &WatchdogConfig::default(), None);
        let margin = block
            .entries
            .iter()
            .find(|e| e.key == "relief_memory_margin")
            .unwrap();
        assert_eq!(margin.value, json!(0));
        assert_eq!(margin.default, Some(json!("unbounded")));
    }

    /// Contracts §2: the line grammar.
    #[test]
    fn render_text_follows_the_line_grammar() {
        let block = build(
            &minimal_config(),
            &WatchdogConfig::default(),
            Some(&minimal_raw()),
        );
        let text = block.render_text();
        let lines: Vec<&str> = text.lines().collect();
        assert_eq!(lines.len(), 1 + block.entries.len());
        assert!(text.ends_with('\n'));

        let stamp = lines[0]
            .strip_prefix("engine_defaults_sha256 = ")
            .expect("stamp header first");
        assert_eq!(stamp.len(), 64);
        assert!(stamp.chars().all(|c| c.is_ascii_hexdigit()));

        assert_eq!(
            lines[1],
            format!("world.width = {} [toml]", block.entries[0].value),
            "no parenthesis without a default"
        );
        assert_eq!(
            lines[4],
            "kitty.1 = Miso needs_driven [toml]"
                .replace("Miso needs_driven", &plain(&block.entries[3].value))
        );
        let radius = lines
            .iter()
            .find(|l| l.starts_with("vision.radius = "))
            .unwrap();
        assert!(radius.ends_with(" [toml]"), "{radius}");
        assert!(
            !radius.contains(" (default: "),
            "[vision] is a required section: no default to advertise — {radius}"
        );
        let relief = lines
            .iter()
            .find(|l| l.starts_with("actions.groom_cuddle_floor = "))
            .unwrap();
        assert!(relief.contains(" (default: "), "{relief}");
        let margin = lines
            .iter()
            .find(|l| l.starts_with("meow.relief_memory_margin = "))
            .unwrap();
        assert_eq!(
            *margin,
            "meow.relief_memory_margin = unbounded (default: unbounded) [default]"
        );
        for l in &lines[1..] {
            assert!(l.ends_with(" [toml]") || l.ends_with(" [default]"), "{l}");
        }
    }

    /// Review finding (2026-09-09): an f32 widened to f64 prints its full
    /// expansion (`0.20000000298023224`), and the block exists to be compared
    /// with the toml by eye. Dials print as written; non-finite never `null`.
    #[test]
    fn f32_dials_print_as_written() {
        let mut config = minimal_config();
        config.behavior.reply_intensity_floor = Some(0.2);
        config.water.contagion_factor = 0.1;
        config.actions.groom_cuddle_floor = 0.5;
        let block = build(&config, &WatchdogConfig::default(), None);
        let text = block.render_text();
        assert!(
            text.contains("behavior.reply_intensity_floor = 0.2 (default: none) [default]"),
            "{text}"
        );
        assert!(
            text.contains("water.contagion_factor = 0.1 (default: 0.0) [default]"),
            "{text}"
        );
        assert!(
            text.contains("actions.groom_cuddle_floor = 0.5 (default: 0.25) [default]"),
            "{text}"
        );
        let floor = block
            .entries
            .iter()
            .find(|e| e.key == "reply_intensity_floor")
            .unwrap();
        assert_eq!(floor.value, json!(0.2));
        assert_eq!(num(f32::NAN), json!("NaN"), "never null");
    }

    /// A writer that keeps what `tracing` formats, so the boot event can be
    /// read back.
    #[derive(Clone, Default)]
    struct Captured(Arc<Mutex<Vec<u8>>>);

    impl Write for Captured {
        fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
            self.0.lock().unwrap().extend_from_slice(buf);
            Ok(buf.len())
        }
        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }

    impl<'a> tracing_subscriber::fmt::MakeWriter<'a> for Captured {
        type Writer = Captured;
        fn make_writer(&'a self) -> Self::Writer {
            self.clone()
        }
    }

    /// FR-012: the boot log IS the renderer's output. A log line that says
    /// anything else (structured fields, JSON, a summary) goes red here.
    #[test]
    fn announce_logs_the_rendered_block_verbatim() {
        let block = build(&minimal_config(), &WatchdogConfig::default(), None);
        let sink = Captured::default();
        let subscriber = tracing_subscriber::fmt()
            .with_writer(sink.clone())
            .with_ansi(false)
            .finish();
        tracing::subscriber::with_default(subscriber, || block.announce());
        let logged = String::from_utf8(sink.0.lock().unwrap().clone()).unwrap();
        assert!(logged.contains("key settings\n"), "{logged}");
        assert!(
            logged.contains(&block.render_text()),
            "the log must carry the block verbatim:\n{logged}"
        );
        assert_eq!(
            logged.matches("engine_defaults_sha256 = ").count(),
            1,
            "one block, once"
        );
    }
}
