//! Spec 059 (ruling eb9e860b): the target-side, engine-validated consent
//! gate. The spec-047 predicate — strictly over the line AND strictly
//! over the target's own play need — moved here whole; what changed is
//! WHO it binds (every proposer type) and WHERE it reads (the engine, at
//! the apply slot, about the TARGET's own state — rule 12). The four
//! predicate pins that lived beside the proposer-side gate in
//! selection.rs are re-homed here, plus the per-kitty-line and
//! stamp-reason guards (tasks T009) and the FR-015 fire-counter recorder.

use std::sync::Arc;

use cloudkitty_core::action::{refusal_reason, Action, TargetRef};
use cloudkitty_core::events::RefusalReason;
use cloudkitty_core::{BehaviorRegistry, Config, World};

/// A default world whose kitty 2 has `eat`/`play` pinned exactly and
/// whose consent comes from the CONFIG the gate reads (`consent_line_for`:
/// per-kitty override, else the world line). Kitty 1 stands adjacent so a
/// play proposal is validate-legal and only consent can refuse it.
fn staged(
    world_line: f32,
    kitty2_line: Option<f32>,
    eat: f32,
    play: f32,
) -> (World, Arc<Config>) {
    let mut config = Config::default();
    config.behavior.consent_line = world_line;
    if let Some(line) = kitty2_line {
        let k2 = config.kitties.iter_mut().find(|k| k.id == 2).unwrap();
        k2.consent_line = Some(line);
    }
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let a = world.kitty_index(1).unwrap();
    world.kitties[a].pos = cloudkitty_core::Position::new(5, 5);
    let b = world.kitty_index(2).unwrap();
    world.kitties[b].pos = cloudkitty_core::Position::new(5, 6);
    world.kitties[b].needs = Default::default();
    world.kitties[b].needs.add(cloudkitty_core::NeedKind::Eat, eat);
    world.kitties[b].needs.add(cloudkitty_core::NeedKind::Play, play);
    (world, config)
}

fn play_at_2() -> Action {
    Action::Play {
        target: Some(TargetRef::Kitty { id: 2 }),
    }
}

/// The owner's rule verbatim, at the gate's new home: over the line AND
/// over play refuses — and the stamp names consent, not a busy partner.
#[test]
fn the_gate_refuses_strictly_over_the_line_and_names_itself() {
    let (mut world, config) = staged(30.0, None, 40.0, 10.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        Action::Idle,
        "eat 40 > line 30 and > play 10: the target declines"
    );
    assert_eq!(
        refusal_reason(&world, 1, play_at_2(), &config),
        RefusalReason::ConsentDeclined,
        "an adjacent idle target refused by consent must not read as busy"
    );
}

/// "Over" is strict: a top non-play need exactly AT the line spares.
#[test]
fn the_gate_spares_a_target_exactly_at_the_line() {
    let (mut world, config) = staged(30.0, None, 30.0, 10.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        play_at_2(),
        "eat 30 is AT the line, not over it"
    );
}

/// Play tying the top non-play need keeps the target conscriptable —
/// refusing needs the non-play need strictly on top.
#[test]
fn the_gate_spares_a_target_whose_play_ties_its_top_need() {
    let (mut world, config) = staged(30.0, None, 40.0, 40.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        play_at_2(),
        "play 40 co-tops eat 40: conscriptable"
    );
}

/// A line at or below zero is structurally open: `Config::default()` and
/// every pre-047 world pass the gate untouched (the evolution golden's
/// silent witness).
#[test]
fn a_line_at_or_below_zero_is_structurally_open() {
    let (mut world, config) = staged(0.0, None, 90.0, 0.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        play_at_2(),
        "line 0.0 gates nothing, ever"
    );
}

/// FR-005: the gate reads the TARGET's per-kitty line, not the world
/// line — in both directions.
#[test]
fn the_gate_reads_the_targets_own_line_not_the_worlds() {
    // World open, the target's own line set: ITS line refuses.
    let (mut world, config) = staged(0.0, Some(30.0), 40.0, 10.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        Action::Idle,
        "the per-kitty line refuses where the world line would not"
    );
    // World strict, the target's own line relaxed: ITS line allows.
    let (mut world, config) = staged(30.0, Some(90.0), 40.0, 10.0);
    assert_eq!(
        world.apply_slot_verdict(1, play_at_2(), &config),
        play_at_2(),
        "the per-kitty line allows where the world line would refuse"
    );
}

/// The end-to-end welfare property the spec-047 battery protected, kept
/// under the re-key: a burdened adjacent friend is never CONSCRIPTED —
/// the playful proposer now proposes (it reads no hidden state) and the
/// engine's gate refuses, stamping `consent_declined` in the refusal
/// log. One full served tick, scripted seats.
#[tokio::test]
async fn a_burdened_friend_is_never_conscripted_end_to_end() {
    let mut config = Config::default();
    config.behavior.consent_line = 30.0;
    for k in &mut config.kitties {
        // Only the proposer is playful: a playful target (eat 40, under
        // comfort) would enter luxury and conscript kitty 1 right back —
        // its own line does not protect a cat whose top non-play is 0.
        k.behavior = if k.id == 1 { "playful" } else { "needs_driven" }.into();
    }
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    world.elements.clear();
    let a = world.kitty_index(1).unwrap();
    world.kitties[a].pos = cloudkitty_core::Position::new(5, 5);
    world.kitties[a].needs = Default::default();
    world.kitties[a].needs.add(cloudkitty_core::NeedKind::Play, 45.0); // real play urge
    let b = world.kitty_index(2).unwrap();
    world.kitties[b].pos = cloudkitty_core::Position::new(5, 6); // adjacent
    world.kitties[b].needs = Default::default();
    world.kitties[b].needs.add(cloudkitty_core::NeedKind::Eat, 40.0);
    world.kitties[b].needs.add(cloudkitty_core::NeedKind::Play, 10.0); // burdened: blocked at 30
    // Park every other seat far away so the staging is the pair's.
    for k in &mut world.kitties {
        if k.id > 2 {
            k.pos = cloudkitty_core::Position::new(15, 15);
        }
    }
    world.tick(&registry, &config).await;
    let kitty2 = world.kitty(2).unwrap();
    assert!(
        !matches!(
            kitty2.activity,
            cloudkitty_core::Activity::Playing { .. }
        ),
        "the burdened friend was conscripted: {:?}",
        kitty2.activity
    );
    let consent_refusals: Vec<_> = world
        .refusal_log
        .events()
        .filter(|e| e.reason == RefusalReason::ConsentDeclined)
        .collect();
    assert!(
        !consent_refusals.is_empty(),
        "the proposal was made and the gate's refusal is stamped"
    );
    assert_eq!(consent_refusals[0].kitty_id, 1, "the proposer is stamped");
}

/// The FR-015 fire-counter recorder (ignored; run once per reference
/// re-cut): drives the two reference configs — the served
/// `cloudkitty.toml` and the c30 certification anchor — for 20k ticks on
/// scripted seats and counts the consent gate's direct fires
/// (`consent_declined` stamps). Output JSON goes beside the fixtures;
/// the committed table lives in
/// specs/059-teacher-rework/contracts/audit-record.md.
///
///   cargo test -p cloudkitty-core --test consent_gate -- --ignored record_spec059
#[tokio::test]
#[ignore]
async fn record_spec059_fire_counter() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let mut out = serde_json::Map::new();
    for (arm, path) in [
        ("served_cloudkitty_toml", "cloudkitty.toml"),
        (
            "cert_anchor_b3",
            "experiments/fog-gen1-cert/anchor-b3.toml",
        ),
    ] {
        let text = std::fs::read_to_string(root.join(path)).expect("config readable");
        let config: Config = toml::from_str(&text).expect("config parses");
        config.validate().expect("config validates");
        let config = Arc::new(config);
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let mut consent_fires = 0u64;
        let mut total_refusals = 0u64;
        for _ in 0..20_000u64 {
            let tick = world.tick;
            world.tick(&registry, &config).await;
            for e in world.refusal_log.events().filter(|e| e.tick == tick) {
                total_refusals += 1;
                if e.reason == RefusalReason::ConsentDeclined {
                    consent_fires += 1;
                }
            }
        }
        out.insert(
            arm.to_string(),
            serde_json::json!({
                "ticks": 20000,
                "consent_declined_fires": consent_fires,
                "total_refusals": total_refusals,
            }),
        );
    }
    let json = serde_json::Value::Object(out);
    let dest = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/spec059-fire-counter.json");
    std::fs::write(&dest, serde_json::to_string_pretty(&json).unwrap()).unwrap();
    println!("{json:#}");
}
