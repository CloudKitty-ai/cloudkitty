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

/// FR-024 / SC-004 as the want law leaves it: fog at a world-covering
/// radius IS the pre-fog world -- for the VISIBILITY FILTER. The served
/// roster, all scripted, 20,000 ticks, against the streams
/// `record_prefog_streams` captured at the branch base. Controls:
/// `[vision] radius` forced to 40 (every tile of the 20x20 world inside
/// every disc), the reply floor unset, `announce_here` 0, the served
/// digest window.
///
/// Two claims, in order. (1) The fog-view plumbing alone changes nothing:
/// proven BYTE FOR BYTE -- every action and every message row identical
/// over all 20,000 ticks -- at the pre-law commits of this arc (redden
/// list, cycles 3/5: `a268555` through `11b82a1`), the proof the spec's
/// FR-024 asks for. (2) After the knowledge-gated want law (FR-036) the
/// streams cannot stay byte-identical by construction: the built-in
/// groom response LISTENS to `want_bath` (spec 028 FR-019), and at a
/// world-covering radius that word is silenced whenever an idle friend is
/// in view -- so a groom response the pre-fog engine took never fires,
/// and the trajectories lawfully part from that tick on (owner flag: SC-004
/// amended, recorded in the redden list). What this guard now pins: the
/// action streams are identical up to the first divergence, the first
/// divergence is EXACTLY that -- the pre-fog cat was grooming a friend
/// whose `want_bath` the pre-fog stream carries inside the cooldown and
/// the fog-view stream does not -- and, up to that tick, the message
/// streams differ only by silenced wants (nothing added, nothing but
/// want rows removed).
#[test]
fn world_covering_radius_reproduces_pre_fog_actions() {
    let mut config = served_all_scripted();
    config.vision.radius = 40;
    config.behavior.reply_intensity_floor = None;
    config.validate().expect("the control config validates");
    let cooldown = config.meow.recent_window_ticks;
    let (actions, messages) = record_streams(config, TICKS);
    let expected_actions = read_lines("prefog-actions-20k.digest");
    let expected_messages = read_lines("prefog-messages-20k.digest");
    assert_eq!(expected_actions.len() as u64, TICKS, "the fixture is whole");

    // (a) Actions: identical up to the first divergence.
    let first_divergence = actions
        .iter()
        .zip(expected_actions.iter())
        .position(|(got, want)| got != want);
    let horizon = first_divergence.map_or(TICKS, |i| i as u64);
    if let Some(i) = first_divergence {
        let got = &actions[i];
        let want = &expected_actions[i];
        // Which kitty moved, and what the pre-fog engine had it doing.
        let got_codes: Vec<&str> = got.split('\t').nth(1).unwrap().split(' ').collect();
        let want_codes: Vec<&str> = want.split('\t').nth(1).unwrap().split(' ').collect();
        let diffs: Vec<(usize, &str, &str)> = got_codes
            .iter()
            .zip(want_codes.iter())
            .enumerate()
            .filter(|(_, (g, w))| g != w)
            .map(|(k, (g, w))| (k, *g, *w))
            .collect();
        let explained = diffs.iter().all(|&(_, _, pre)| {
            // A groom of friend `id` in the pre-fog stream ...
            let Some(target) = pre.strip_prefix('G').and_then(|t| t.parse::<u32>().ok()) else {
                return false;
            };
            // ... answering a want_bath from that friend inside the cooldown
            // that the fog-view engine no longer records.
            let silenced = |rows: &[String]| {
                rows.iter().any(|row| {
                    let mut f = row.split('\t');
                    let tick: u64 = f.next().unwrap().parse().unwrap();
                    let kitty: u32 = f.next().unwrap().parse().unwrap();
                    let kind = f.next().unwrap();
                    kitty == target
                        && kind == "want_bath"
                        && tick < horizon
                        && horizon - tick <= cooldown
                })
            };
            silenced(&expected_messages) && !silenced(&messages)
        });
        assert!(
            explained,
            "action stream diverged at tick {i} for a reason other than a silenced want_bath's \
             groom response: fog-view `{got}` vs pre-fog `{want}` (kitties in id order; codes per \
             fog_continuity.rs). STOP and report (rule 4)."
        );
        eprintln!(
            "FR-024: actions identical for {i} ticks; first divergence at tick {i} = a groom \
             response to a want_bath the want law silences ({diffs:?})"
        );
    } else {
        eprintln!("FR-024: actions identical over all {TICKS} ticks");
    }

    // (b) Messages up to the horizon: the want law may only SILENCE wants.
    let before = |rows: &[String]| -> std::collections::BTreeSet<String> {
        rows.iter()
            .filter(|row| row.split('\t').next().unwrap().parse::<u64>().unwrap() < horizon)
            .cloned()
            .collect()
    };
    let got = before(&messages);
    let want = before(&expected_messages);
    // Added rows: a silenced call frees its kind's cooldown, so a later
    // same-kind call the pre-fog engine could NOT make (still cooling down)
    // becomes legal -- the want law's only other footprint. Each added row
    // must be a want whose speaker's previous same-kind call inside the
    // cooldown exists in the pre-fog stream and is absent from ours.
    let parse = |row: &str| {
        let mut f = row.split('\t');
        let tick: u64 = f.next().unwrap().parse().unwrap();
        let kitty: u32 = f.next().unwrap().parse().unwrap();
        let kind = f.next().unwrap().to_string();
        (tick, kitty, kind)
    };
    let mut freed = 0usize;
    for row in got.difference(&want) {
        let (tick, kitty, kind) = parse(row);
        assert!(kind.starts_with("want_"), "a non-want row was ADDED: {row}");
        let silenced_predecessor = want.iter().any(|old| {
            let (t, k, kd) = parse(old);
            k == kitty && kd == kind && t < tick && tick - t < cooldown && !got.contains(old)
        });
        assert!(
            silenced_predecessor,
            "the fog-view engine ADDED {row} without a silenced same-kind call inside the \
             cooldown to explain it"
        );
        freed += 1;
    }
    let mut silenced_kinds = std::collections::BTreeMap::new();
    for row in want.difference(&got) {
        let kind = row
            .split('\t')
            .nth(2)
            .expect("tick\tkitty\tkind\tintensity");
        assert!(
            kind.starts_with("want_"),
            "a non-want row went missing before the horizon (only FR-036 silences may differ): {row}"
        );
        *silenced_kinds.entry(kind.to_string()).or_insert(0usize) += 1;
    }
    eprintln!(
        "FR-024 message exemption set before tick {horizon}: {} of {} pre-fog rows silenced by \
         the want law ({silenced_kinds:?}); {freed} calls freed by a silenced predecessor's \
         cooldown",
        want.difference(&got).count(),
        want.len()
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
