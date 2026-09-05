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

use cloudkitty_core::config::LawEra;
use cloudkitty_core::{Action, BehaviorRegistry, Config, Direction, NeedKind, TargetRef, World};

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
/// What one run yields: the two fixture streams, and two per-tick facts
/// read at the START of each tick (the state the deciders read) that are
/// not fixtures but what SC-004b's classifier needs to NAME a divergence:
/// the kitties whose bath need was below `announce_threshold` (the on-sight
/// rule), and the kitties with a sunbeam inside `sunbeam_reach` that
/// another cat stood on (the T092 cosleep/nap rule: an occupied beam is
/// not worth walking to, so the fog cat naps or cosleeps where the
/// pre-fog cat priced the walk -- beside it, or anywhere in reach since
/// review 3 finding 1 made the rule hold for the remembered tile too).
/// `roster` maps an action column to a kitty id.
struct Streams {
    actions: Vec<String>,
    messages: Vec<String>,
    clean: Vec<Vec<u32>>,
    beam_blocked: Vec<Vec<u32>>,
    roster: Vec<u32>,
}

fn record_streams(config: Config, ticks: u64) -> Streams {
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    let mut actions = Vec::with_capacity(ticks as usize);
    let mut messages = Vec::new();
    let mut clean = Vec::with_capacity(ticks as usize);
    let mut beam_blocked = Vec::with_capacity(ticks as usize);
    let roster: Vec<u32> = world.kitties.iter().map(|k| k.id).collect();
    for _ in 0..ticks {
        let tick = world.tick;
        clean.push(
            world
                .kitties
                .iter()
                .filter(|k| k.needs.get(NeedKind::Bath) < config.meow.announce_threshold)
                .map(|k| k.id)
                .collect::<Vec<u32>>(),
        );
        beam_blocked.push(
            world
                .kitties
                .iter()
                .filter(|k| {
                    world.kitties.iter().any(|o| {
                        o.id != k.id
                            && k.pos.manhattan_distance(&o.pos) <= config.behavior.sunbeam_reach
                            && world.element_at(o.pos).map(|e| e.element_type())
                                == Some(cloudkitty_core::ElementType::Sunbeam)
                    })
                })
                .map(|k| k.id)
                .collect::<Vec<u32>>(),
        );
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
    Streams {
        actions,
        messages,
        clean,
        beam_blocked,
        roster,
    }
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

/// SC-004a (owner ruled 2026-09-03, T087): the visibility plumbing alone
/// changes nothing. The current engine under `LawEra::PreFog` -- the 2.x
/// armed-only word law and the 2.x groom response (no on-sight drop) -- at
/// a world-covering radius reproduces the pre-fog reference streams byte
/// for byte, actions AND messages, over all 20,000 ticks. The switch is
/// test-side (`#[serde(skip)]`), so the proof stays reproducible after
/// merge without a pinned commit. Controls: `[vision] radius` forced to 40
/// (every tile of the 20x20 world inside every disc), the reply floor
/// unset, `announce_here` 0, the served digest window.
#[test]
fn world_covering_radius_under_the_pre_fog_law_is_byte_identical() {
    let mut config = served_all_scripted();
    config.vision.radius = 40;
    config.behavior.reply_intensity_floor = None;
    config.meow.law_era = LawEra::PreFog;
    config.validate().expect("the control config validates");
    let Streams {
        actions, messages, ..
    } = record_streams(config, TICKS);
    let expected_actions = read_lines("prefog-actions-20k.digest");
    let expected_messages = read_lines("prefog-messages-20k.digest");
    if let Some((tick, (got, want))) = actions
        .iter()
        .zip(&expected_actions)
        .enumerate()
        .find(|(_, (a, b))| a != b)
    {
        panic!("SC-004a: actions diverge at tick {tick}:\n  pre-fog {want}\n  now     {got}");
    }
    assert_eq!(
        actions.len(),
        expected_actions.len(),
        "action stream length"
    );
    if let Some((i, (got, want))) = messages
        .iter()
        .zip(&expected_messages)
        .enumerate()
        .find(|(_, (a, b))| a != b)
    {
        panic!("SC-004a: messages diverge at row {i}:\n  pre-fog {want}\n  now     {got}");
    }
    assert_eq!(
        messages.len(),
        expected_messages.len(),
        "message stream length"
    );
}

/// SC-004b (owner ruled 2026-09-03, T087): the law. Under the ruled law the
/// same run parts from the pre-fog streams, and every action-stream
/// divergence must trace to a NAMED cause -- nothing else. With `want_bath`
/// armed-only no want with an action listener is ever silenced, and the
/// groom response's freshness rule is 2.x-matching, so the one named cause
/// left is the on-sight rule: the pre-fog cat groomed a caller whose bath
/// need was already below the announce threshold, which the ruled rung
/// declines. Pinned: actions identical up to the first divergence; the
/// first divergence is exactly that (every differing kitty is a pre-fog
/// `G{id}` whose target was clean at that tick's start -- the worlds are
/// identical up to there, so our run's clean set IS the pre-fog world's);
/// and up to that tick the message streams differ only by wants silenced
/// by top-need / known-relief (nothing added but calls freed by a silenced
/// predecessor's cooldown, nothing removed but want rows).
#[test]
fn world_covering_radius_diverges_only_by_the_named_causes() {
    let mut config = served_all_scripted();
    config.vision.radius = 40;
    config.behavior.reply_intensity_floor = None;
    config.validate().expect("the control config validates");
    let cooldown = config.meow.recent_window_ticks;
    let Streams {
        actions,
        messages,
        clean: clean_sets,
        beam_blocked,
        roster,
    } = record_streams(config, TICKS);
    let expected_actions = read_lines("prefog-actions-20k.digest");
    let expected_messages = read_lines("prefog-messages-20k.digest");
    assert_eq!(expected_actions.len() as u64, TICKS, "the fixture is whole");

    // (a) Actions: identical up to the first divergence, which is named.
    let first_divergence = actions
        .iter()
        .zip(expected_actions.iter())
        .position(|(got, want)| got != want);
    let horizon = first_divergence.map_or(TICKS, |i| i as u64);
    if let Some(i) = first_divergence {
        let got = &actions[i];
        let want = &expected_actions[i];
        let got_codes: Vec<&str> = got.split('\t').nth(1).unwrap().split(' ').collect();
        let want_codes: Vec<&str> = want.split('\t').nth(1).unwrap().split(' ').collect();
        let diffs: Vec<(usize, &str, &str)> = got_codes
            .iter()
            .zip(want_codes.iter())
            .enumerate()
            .filter(|(_, (g, w))| g != w)
            .map(|(k, (g, w))| (k, *g, *w))
            .collect();
        // The on-sight rule declines the whole errand, walk included: a
        // fresh ask (age <= cooldown at this tick's start) from a caller
        // already clean at this tick's start, which the pre-fog cats still
        // answered -- each differing pre-fog action is that walk (a Move)
        // or that groom (`G{caller}`).
        let clean = &clean_sets[i];
        let asked_fresh = |target: u32| {
            expected_messages.iter().any(|row| {
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
        let clean_callers: Vec<u32> = clean.iter().copied().filter(|&c| asked_fresh(c)).collect();
        // (i) the on-sight rule: every differing pre-fog action is the walk
        // or the groom toward a fresh ask from an already-clean caller;
        // (ii) T092: the differing cat had another cat on a sunbeam inside
        // its reach and naps/cosleeps (`S…`) where the pre-fog cat priced
        // the walk to that beam -- and waited (`I`), stepped (`M…`), or,
        // the nap now costing nothing, served another need first (the
        // score side of the same helper). Each diff must be one of them.
        let blocked = &beam_blocked[i];
        let explained = diffs.iter().all(|&(k, now, pre)| {
            let on_sight = !clean_callers.is_empty()
                && (pre.starts_with('M')
                    || pre
                        .strip_prefix('G')
                        .and_then(|t| t.parse::<u32>().ok())
                        .is_some_and(|target| clean_callers.contains(&target)));
            let warm_beam = now.starts_with('S') && blocked.contains(&roster[k]);
            on_sight || warm_beam
        });
        assert!(
            explained,
            "action stream diverged at tick {i} for a reason other than the named causes \
             (the on-sight rule: pre-fog cats answering a fresh ask from an already-clean \
             caller; T092: a nap or cosleep where an occupied beam was in reach): fog-view `{got}` \
             vs pre-fog `{want}` (kitties in id order; codes per fog_continuity.rs; clean at \
             start {clean:?}, of whom asked inside the cooldown {clean_callers:?}; beam-blocked \
             {blocked:?}). STOP and report (rule 4)."
        );
        eprintln!(
            "SC-004b: actions identical for {i} ticks; first divergence at tick {i} named \
             (clean callers asked fresh {clean_callers:?}, beam-blocked {blocked:?}): {diffs:?}"
        );
    } else {
        eprintln!("SC-004b: actions identical over all {TICKS} ticks");
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
    let Streams {
        actions, messages, ..
    } = record_streams(served_all_scripted(), TICKS);
    assert_eq!(actions.len() as u64, TICKS);
    write_lines(&fixtures_dir().join("prefog-actions-20k.digest"), &actions);
    write_lines(
        &fixtures_dir().join("prefog-messages-20k.digest"),
        &messages,
    );
}

// ---- spec 049 T065 / SC-011: the reply ladder is inert with the floor unset ----

/// The served roster all scripted at the Gen 1 radius, `announce_here` 0,
/// `reply_intensity_floor` unset -- the exact configuration SC-011 names.
fn served_all_scripted_r5_floor_unset() -> Config {
    let mut config = served_all_scripted();
    config.vision.radius = 5;
    config.behavior.reply_intensity_floor = None;
    config.validate().expect("the r = 5 served config is valid");
    config
}

/// SC-011: with `reply_intensity_floor` unset the engine WITH the reply
/// ladder (T063) produces byte-identical action and message streams to
/// the engine immediately before it -- PROVEN at the ladder's landing
/// (a90f2fe) against streams `record_preladder_r5_streams` captured at
/// the commit before it; no feature gate, no cfg switch, the comparator
/// was the pre-ladder engine itself, frozen as data. The fixtures were
/// re-recorded at T087 (the ruled bath clause and groom-response rules
/// move every r = 5 stream), so what they pin NOW is that the floor-unset
/// streams of the ruled engine do not drift -- any later scripted-dynamics
/// move re-records them with its justification. Fog is on (r = 5), so the
/// blind cats explore and call; only replies are absent.
///
/// Re-recorded for spec 050 (2026-09-05): the served `[meow]
/// relief_memory_margin = 0` bounds remembered relief to the disc, so
/// want calls the unbounded memory silenced return -- first kitty 3's
/// `want_eat` at tick 118 (its remembered bowl lay beyond reach); kitty 4,
/// cuddle top, then targets the HEARD friend (research R10) and walks west
/// at tick 128 where it idled before -- the first action divergence; the
/// first `want_drink` is at tick 1,610 (23 per 20,000 on this seed, 0 under
/// the old rule at every horizon). The r = 40 control above is untouched:
/// on 20x20 every tile is within Manhattan 38 <= 40 + 0.
#[test]
fn reply_floor_unset_is_byte_identical() {
    let expected_actions = read_lines("preladder-r5-20k.actions.digest");
    let expected_messages = read_lines("preladder-r5-20k.messages.digest");
    let Streams {
        actions, messages, ..
    } = record_streams(served_all_scripted_r5_floor_unset(), TICKS);
    if let Some((tick, (got, want))) = actions
        .iter()
        .zip(&expected_actions)
        .enumerate()
        .find(|(_, (a, b))| a != b)
    {
        panic!("actions diverge at tick {tick}:\n  pre-ladder {want}\n  now        {got}");
    }
    assert_eq!(
        actions.len(),
        expected_actions.len(),
        "action stream length"
    );
    if let Some((i, (got, want))) = messages
        .iter()
        .zip(&expected_messages)
        .enumerate()
        .find(|(_, (a, b))| a != b)
    {
        panic!("messages diverge at row {i}:\n  pre-ladder {want}\n  now        {got}");
    }
    assert_eq!(
        messages.len(),
        expected_messages.len(),
        "message stream length"
    );
}

/// The T065 recorder: run once at the commit immediately before T063 to
/// capture the pre-ladder r = 5 streams. `cargo test -p cloudkitty-core
/// --test fog_continuity -- --ignored record_preladder`.
#[test]
#[ignore]
fn record_preladder_r5_streams() {
    let Streams {
        actions, messages, ..
    } = record_streams(served_all_scripted_r5_floor_unset(), TICKS);
    write_lines(
        &fixtures_dir().join("preladder-r5-20k.actions.digest"),
        &actions,
    );
    write_lines(
        &fixtures_dir().join("preladder-r5-20k.messages.digest"),
        &messages,
    );
}
