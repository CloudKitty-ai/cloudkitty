//! Spec 049 FR-024 / SC-004: the pre-fog reference streams, and (once the
//! fog view lands) the proof that a world-covering radius reproduces them.
//!
//! `record_prefog_streams` is the recorder: run ONCE at the branch base,
//! before any engine edit, it writes the served roster's all-scripted
//! 20,000-tick action stream and message stream to the fixtures beside
//! this file. Nothing here asserts yet — the comparison
//! (`world_covering_radius_reproduces_pre_fog_actions`) lands with the
//! fog view and reads what this recorded. The message tuple is
//! (kitty, kind, tick, intensity) ONLY: `pos` and `reply` do not exist at
//! the branch base, and the comparison is on what both engines record.

use std::path::{Path, PathBuf};
use std::sync::Arc;

use cloudkitty_core::{Action, BehaviorRegistry, Config, Direction, TargetRef, World};

const TICKS: u64 = 20_000;

fn fixtures_dir() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures")
}

/// The served config with every seat scripted: `needs_driven` on all five,
/// made explicit rather than left to the policy-seat fallback so the
/// fixture depends on no dispatch path. The served seed, `announce_here`
/// 0 (asserted — the reference world is the ambient-here-off world).
fn served_all_scripted() -> Config {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml"))
        .expect("the served config is readable");
    let mut config: Config = toml::from_str(&text).expect("the served config parses");
    for kitty in &mut config.kitties {
        kitty.behavior = "needs_driven".into();
    }
    assert_eq!(
        config.behavior.announce_here, 0,
        "the reference stream is recorded with the ambient here off"
    );
    config.validate().expect("the served config validates");
    config
}

fn dir_code(d: Direction) -> char {
    match d {
        Direction::North => 'n',
        Direction::East => 'e',
        Direction::South => 's',
        Direction::West => 'w',
    }
}

fn with_code(with: Option<u32>) -> String {
    with.map_or_else(|| "-".to_string(), |id| id.to_string())
}

fn target_code(target: TargetRef) -> String {
    match target {
        TargetRef::Element { id } => format!("e{id}"),
        TargetRef::Kitty { id } => format!("k{id}"),
    }
}

fn kind_name(kind: cloudkitty_core::MessageKind) -> String {
    serde_json::to_string(&kind)
        .expect("a message kind serializes")
        .trim_matches('"')
        .to_string()
}

/// One short token per applied action — readable in a diff, so a
/// divergence names the tick AND the action on both sides.
fn action_code(action: Option<Action>) -> String {
    match action {
        None => "_".into(),
        Some(Action::Move { direction }) => format!("M{}", dir_code(direction)),
        Some(Action::Rest { with }) => format!("R{}", with_code(with)),
        Some(Action::Sleep { with }) => format!("S{}", with_code(with)),
        Some(Action::Groom { target }) => format!("G{}", with_code(target)),
        Some(Action::Eat) => "E".into(),
        Some(Action::Drink) => "D".into(),
        Some(Action::Chase(target)) => format!("C{}", target_code(target)),
        Some(Action::Play { target }) => {
            format!("P{}", target.map_or_else(|| "-".to_string(), target_code))
        }
        Some(Action::Purr) => "U".into(),
        Some(Action::Meow { message }) => format!("W{}", kind_name(message)),
        Some(Action::Idle) => "I".into(),
    }
}

/// Runs `ticks` ticks of `config` under the built-in registry and returns
/// the two streams: one action line per tick (`tick<TAB>code per kitty in
/// id order`) and one message line per recorded meow
/// (`tick<TAB>kitty<TAB>kind<TAB>intensity`), the meows of a tick sorted
/// by (kitty, kind) so the per-tick turn order plays no part.
fn record_streams(config: Config, ticks: u64) -> (Vec<String>, Vec<String>) {
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    let mut actions = Vec::with_capacity(ticks as usize);
    let mut messages = Vec::new();
    for _ in 0..ticks {
        let tick = world.tick;
        runtime.block_on(world.tick(&registry, &config));
        let codes: Vec<String> = world
            .kitties
            .iter()
            .map(|k| action_code(k.last_action))
            .collect();
        actions.push(format!("{tick}\t{}", codes.join(" ")));
        let mut rows: Vec<(u32, String, f32)> = world
            .recent_meows
            .iter()
            .filter(|m| m.tick == tick)
            .map(|m| (m.kitty_id, kind_name(m.kind), m.intensity))
            .collect();
        rows.sort_by(|a, b| a.0.cmp(&b.0).then_with(|| a.1.cmp(&b.1)));
        for (kitty, kind, intensity) in rows {
            messages.push(format!("{tick}\t{kitty}\t{kind}\t{intensity}"));
        }
    }
    (actions, messages)
}

fn write_lines(path: &Path, lines: &[String]) {
    let mut text = lines.join("\n");
    text.push('\n');
    std::fs::write(path, text).expect("the fixture is writable");
}

fn read_lines(name: &str) -> Vec<String> {
    let text = std::fs::read_to_string(fixtures_dir().join(name))
        .unwrap_or_else(|e| panic!("fixture {name} is readable: {e}"));
    text.lines().map(str::to_string).collect()
}

/// FR-024 / SC-004: fog at a world-covering radius IS the pre-fog world.
/// The served roster, all scripted, 20,000 ticks, against the streams
/// `record_prefog_streams` captured at the branch base. Controls:
/// `[vision] radius` forced to 40 (every tile of the 20x20 world is inside
/// every disc), the reply floor unset, `announce_here` 0. The served
/// `digest_window_ticks` (30) is NOT overridden: the buffer outliving the
/// cooldown must leave every built-in's action untouched, and this run is
/// the witness that it does (the built-ins hear at the cooldown until the
/// fog-era targeting lands deliberately at T054). Actions must match tick
/// for tick; messages must match row for row until the want law lands
/// (which may only SILENCE wants -- that exemption is added with it).
#[test]
fn world_covering_radius_reproduces_pre_fog_actions() {
    let mut config = served_all_scripted();
    config.vision.radius = 40;
    config.behavior.reply_intensity_floor = None;
    config.validate().expect("the control config validates");
    let (actions, messages) = record_streams(config, TICKS);
    let expected_actions = read_lines("prefog-actions-20k.digest");
    let expected_messages = read_lines("prefog-messages-20k.digest");
    assert_eq!(expected_actions.len() as u64, TICKS, "the fixture is whole");
    for (i, (got, want)) in actions.iter().zip(expected_actions.iter()).enumerate() {
        assert_eq!(
            got, want,
            "action stream diverged at line {i}: fog-view engine `{got}` vs pre-fog `{want}` \
             (kitties in id order; codes per fog_continuity.rs). STOP and report (rule 4)."
        );
    }
    assert_eq!(actions.len(), expected_actions.len());
    assert_eq!(
        messages, expected_messages,
        "message stream diverged from the pre-fog recording"
    );
}

/// The recorder. Ignored: it WRITES the reference fixtures and is run by
/// hand exactly once, at the branch base, before any engine edit.
#[test]
#[ignore = "writes the pre-fog reference fixtures; run once at the branch base"]
fn record_prefog_streams() {
    let (actions, messages) = record_streams(served_all_scripted(), TICKS);
    assert_eq!(actions.len() as u64, TICKS);
    write_lines(&fixtures_dir().join("prefog-actions-20k.digest"), &actions);
    write_lines(
        &fixtures_dir().join("prefog-messages-20k.digest"),
        &messages,
    );
}
