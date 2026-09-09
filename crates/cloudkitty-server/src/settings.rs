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

/// One step of a presence path into the raw config tree.
#[derive(Debug, Clone, Copy)]
enum Seg {
    Key(&'static str),
    Index(usize),
}

/// `Toml` iff `path` resolves in the raw tree; `Default` when it does not
/// or when there is no tree (no file was loaded).
fn present(raw: Option<&toml::Value>, path: &[Seg]) -> Source {
    let Some(mut node) = raw else {
        return Source::Default;
    };
    for seg in path {
        node = match seg {
            Seg::Key(k) => match node.get(k) {
                Some(next) => next,
                None => return Source::Default,
            },
            Seg::Index(i) => match node.as_array().and_then(|a| a.get(*i)) {
                Some(next) => next,
                None => return Source::Default,
            },
        };
    }
    Source::Toml
}

/// An Option dial as a JSON value: the number when set, the sentinel word
/// when not — so the reader sees the rule, never `null` (FR-003).
fn opt<T: Into<Value>>(v: Option<T>, absent: &'static str) -> Value {
    match v {
        Some(v) => v.into(),
        None => Value::String(absent.to_string()),
    }
}

fn membership(m: ContagionMembership) -> Value {
    serde_json::to_value(m).expect("ContagionMembership serializes to its snake_case name")
}

/// Builds the block from the validated engine config, the server's
/// `[watchdog]` table and the raw config tree (`None` when the server booted
/// on built-in defaults). Adding a dial is one `push` here plus one name in
/// the golden test below (FR-011).
pub fn build(config: &Config, watchdog: &WatchdogConfig, raw: Option<&toml::Value>) -> KeySettings {
    let d = Config::default();
    let wd = WatchdogConfig::default();
    let mut entries = Vec::new();
    let mut push =
        |group: &'static str, key: &str, value: Value, default: Option<Value>, path: &[Seg]| {
            entries.push(Entry {
                group,
                key: key.to_string(),
                value,
                default,
                source: present(raw, path),
            });
        };

    // The world shape and the seats have no defaults: a config without them
    // does not load (and Article III wants at least two seats).
    let w = &config.world;
    push(
        "world",
        "width",
        json!(w.width),
        None,
        &[Seg::Key("world"), Seg::Key("width")],
    );
    push(
        "world",
        "height",
        json!(w.height),
        None,
        &[Seg::Key("world"), Seg::Key("height")],
    );
    push(
        "world",
        "seed",
        json!(w.seed),
        None,
        &[Seg::Key("world"), Seg::Key("seed")],
    );
    for (i, k) in config.kitties.iter().enumerate() {
        push(
            "kitty",
            &k.id.to_string(),
            json!({ "name": k.name, "behavior": k.behavior }),
            None,
            &[Seg::Key("kitty"), Seg::Index(i)],
        );
    }

    // Fog Gen 1 (spec 049).
    push(
        "vision",
        "radius",
        json!(config.vision.radius),
        Some(json!(d.vision.radius)),
        &[Seg::Key("vision"), Seg::Key("radius")],
    );
    push(
        "vision",
        "memory_timeout_ticks",
        json!(config.vision.memory_timeout_ticks),
        Some(json!(d.vision.memory_timeout_ticks)),
        &[Seg::Key("vision"), Seg::Key("memory_timeout_ticks")],
    );

    // The fog want law's memory reach (spec 050); absent = today's unbounded rule.
    push(
        "meow",
        "relief_memory_margin",
        opt(config.meow.relief_memory_margin, "unbounded"),
        Some(opt(d.meow.relief_memory_margin, "unbounded")),
        &[Seg::Key("meow"), Seg::Key("relief_memory_margin")],
    );

    // The groom bump and its owed revert (spec 041 / cuddle economy).
    push(
        "actions",
        "groom_cuddle_relief",
        json!(config.actions.groom_cuddle_relief),
        Some(json!(d.actions.groom_cuddle_relief)),
        &[Seg::Key("actions"), Seg::Key("groom_cuddle_relief")],
    );

    // Launch dials on the built-in chooser (specs 043, 045, 049).
    let b = &config.behavior;
    push(
        "behavior",
        "announce_here",
        json!(b.announce_here),
        Some(json!(d.behavior.announce_here)),
        &[Seg::Key("behavior"), Seg::Key("announce_here")],
    );
    push(
        "behavior",
        "contagion_aware_ladder",
        json!(b.contagion_aware_ladder),
        Some(json!(d.behavior.contagion_aware_ladder)),
        &[Seg::Key("behavior"), Seg::Key("contagion_aware_ladder")],
    );
    push(
        "behavior",
        "reply_intensity_floor",
        opt(b.reply_intensity_floor, "none"),
        Some(opt(d.behavior.reply_intensity_floor, "none")),
        &[Seg::Key("behavior"), Seg::Key("reply_intensity_floor")],
    );

    // Wet fur and the waterline (specs 024, 044, 045).
    let wa = &config.water;
    push(
        "water",
        "bath_gain",
        json!(wa.bath_gain),
        Some(json!(d.water.bath_gain)),
        &[Seg::Key("water"), Seg::Key("bath_gain")],
    );
    push(
        "water",
        "bath_gain_ceiling",
        json!(wa.bath_gain_ceiling),
        Some(json!(d.water.bath_gain_ceiling)),
        &[Seg::Key("water"), Seg::Key("bath_gain_ceiling")],
    );
    push(
        "water",
        "contagion_factor",
        json!(wa.contagion_factor),
        Some(json!(d.water.contagion_factor)),
        &[Seg::Key("water"), Seg::Key("contagion_factor")],
    );
    push(
        "water",
        "contagion_membership",
        membership(wa.contagion_membership),
        Some(membership(d.water.contagion_membership)),
        &[Seg::Key("water"), Seg::Key("contagion_membership")],
    );

    // The welfare watchdog (spec 040): server-owned, so the engine's
    // `/config` never shows it — this block does.
    push(
        "watchdog",
        "threshold",
        json!(watchdog.threshold),
        Some(json!(wd.threshold)),
        &[Seg::Key("watchdog"), Seg::Key("threshold")],
    );
    push(
        "watchdog",
        "remind_every",
        json!(watchdog.remind_every),
        Some(json!(wd.remind_every)),
        &[Seg::Key("watchdog"), Seg::Key("remind_every")],
    );

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

    /// The nine optional listed keys: every dial on the list that carries a
    /// per-key default (the 3.0 rule: sections are required, only inert
    /// launch dials default). Removing them from a serialized
    /// `Config::default()` leaves a file that still loads.
    const OPTIONAL: &[(&str, &str)] = &[
        ("meow", "relief_memory_margin"),
        ("actions", "groom_cuddle_relief"),
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
            "actions.groom_cuddle_relief",
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
        let default_relief = Config::default().actions.groom_cuddle_relief;
        raw["actions"].as_table_mut().unwrap().insert(
            "groom_cuddle_relief".into(),
            toml::Value::Float(default_relief.into()),
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
            source_of(&block, "actions.groom_cuddle_relief"),
            Source::Toml,
            "written at its default still reads toml"
        );
        for (group, key) in OPTIONAL {
            if *key == "groom_cuddle_relief" {
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
        assert_eq!(block.entries.len(), 18);
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
        assert!(radius.contains(" (default: "), "{radius}");
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
