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
fn staged(world_line: f32, kitty2_line: Option<f32>, eat: f32, play: f32) -> (World, Arc<Config>) {
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
    world.kitties[b]
        .needs
        .add(cloudkitty_core::NeedKind::Eat, eat);
    world.kitties[b]
        .needs
        .add(cloudkitty_core::NeedKind::Play, play);
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
    world.kitties[a]
        .needs
        .add(cloudkitty_core::NeedKind::Play, 45.0); // real play urge
    let b = world.kitty_index(2).unwrap();
    world.kitties[b].pos = cloudkitty_core::Position::new(5, 6); // adjacent
    world.kitties[b].needs = Default::default();
    world.kitties[b]
        .needs
        .add(cloudkitty_core::NeedKind::Eat, 40.0);
    world.kitties[b]
        .needs
        .add(cloudkitty_core::NeedKind::Play, 10.0); // burdened: blocked at 30
                                                     // Park every other seat far away so the staging is the pair's.
    for k in &mut world.kitties {
        if k.id > 2 {
            k.pos = cloudkitty_core::Position::new(15, 15);
        }
    }
    world.tick(&registry, &config).await;
    let kitty2 = world.kitty(2).unwrap();
    assert!(
        !matches!(kitty2.activity, cloudkitty_core::Activity::Playing { .. }),
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

/// SC-005's seeded sample (ignored; tasks T024): the served world, 20k
/// ticks, TWO arms — every seat on `teacher`, and a `needs_driven`
/// control (review 2026-10-10 finding 5: the first cut's "answered"
/// count passed without the feature; coincidental partnered starts
/// beside a caller are the base rate, so the claim is now DIFFERENTIAL:
/// the teacher's PROPOSER-side answered rate must beat the control's).
/// Zero-bypass stays absolute on both arms.
///
///   cargo test -p cloudkitty-core --test consent_gate -- --ignored record_spec059_answer
#[tokio::test]
#[ignore]
async fn record_spec059_answer_sample() {
    let teacher = answer_sample_arm("teacher").await;
    let control = answer_sample_arm("needs_driven").await;
    let json = serde_json::json!({ "teacher": teacher, "needs_driven_control": control });
    println!("{json:#}");
    let (t_ans, t_bypass) = (
        teacher["proposer_answered_starts"].as_u64().unwrap(),
        teacher["consent_bypass_scenes"].as_u64().unwrap(),
    );
    let (c_ans, c_bypass) = (
        control["proposer_answered_starts"].as_u64().unwrap(),
        control["consent_bypass_scenes"].as_u64().unwrap(),
    );
    assert!(t_ans > 0, "SC-005: a nonzero answered-call rate");
    assert!(
        t_ans > c_ans,
        "SC-005: the teacher's proposer-side answered rate ({t_ans}) must beat the \
         no-rung control's coincidence rate ({c_ans})"
    );
    assert_eq!(t_bypass + c_bypass, 0, "SC-005: no consent bypass ever");
}

async fn answer_sample_arm(brain: &str) -> serde_json::Value {
    use cloudkitty_core::meow::MessageKind;
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml")).expect("served config");
    let mut config: Config = toml::from_str(&text).expect("config parses");
    for k in &mut config.kitties {
        k.behavior = brain.into();
    }
    config.validate().expect("validates");
    let window = config.meow.digest_window_ticks;
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let mut prev: std::collections::BTreeMap<u32, cloudkitty_core::Activity> =
        world.kitties.iter().map(|k| (k.id, k.activity)).collect();
    let (mut answered, mut partnered_starts, mut consent_bypass) = (0u64, 0u64, 0u64);
    for _ in 0..20_000u64 {
        // The gate judges DECISION-time state; snapshots are post-apply
        // (the house trap: scene-start reads need t−1), so the bypass
        // check reads each kitty's needs BEFORE the tick.
        let pre: std::collections::BTreeMap<u32, (f32, f32)> = world
            .kitties
            .iter()
            .map(|k| {
                (
                    k.id,
                    (
                        k.top_non_play_pressure(),
                        k.needs.get(cloudkitty_core::NeedKind::Play),
                    ),
                )
            })
            .collect();
        world.tick(&registry, &config).await;
        let now = world.tick;
        for k in &world.kitties {
            let started = prev.get(&k.id) != Some(&k.activity);
            if !started {
                continue;
            }
            let (partner, want) = match k.activity {
                cloudkitty_core::Activity::Resting {
                    with_friend: Some(p),
                } => (Some(p), MessageKind::WantCuddle),
                cloudkitty_core::Activity::Playing {
                    target: Some(TargetRef::Kitty { id: p }),
                } => (Some(p), MessageKind::WantPlay),
                _ => (None, MessageKind::WantCuddle),
            };
            let Some(partner) = partner else { continue };
            partnered_starts += 1;
            // PROPOSER-side only (finding 5): this cat's own applied
            // action made the partnered proposal; a cat merely
            // conscripted by the caller is the caller being relieved,
            // not an answer demonstrated.
            let proposed = match want {
                MessageKind::WantCuddle => {
                    k.last_action
                        == Some(cloudkitty_core::Action::Rest {
                            with: Some(partner),
                        })
                }
                _ => {
                    k.last_action
                        == Some(cloudkitty_core::Action::Play {
                            target: Some(TargetRef::Kitty { id: partner }),
                        })
                }
            };
            let asked = world.recent_meows.iter().any(|m| {
                m.kitty_id == partner && m.kind == want && now.saturating_sub(m.tick) <= window
            });
            if proposed && asked {
                answered += 1;
            }
            // Zero-bypass: the partner's own line must not refuse this
            // scene at its start (Play only — rest binds nobody).
            // Only the PROPOSER's side carries the guarantee: the gate
            // protects the conscripted TARGET, never the proposer from
            // its own proposal (a past-line cat may lawfully propose).
            // The proposer is the side whose own applied action was the
            // play proposal; the conscripted side's activity was set by
            // the engine, not by its action.
            // A conscripted cat's absorbed continuation ALSO records as
            // Play{proposer} in last_action, so when both sides show
            // play-at-each-other the proposer is unattributable from the
            // post-tick state alone (the burdened cat may have been the
            // lawful proposer — its line gates only conscription OF it).
            // Count only the unambiguous proposer side.
            let x_proposed = k.last_action
                == Some(cloudkitty_core::Action::Play {
                    target: Some(TargetRef::Kitty { id: partner }),
                })
                && world.kitty(partner).is_some_and(|p| {
                    p.last_action
                        != Some(cloudkitty_core::Action::Play {
                            target: Some(TargetRef::Kitty { id: k.id }),
                        })
                });
            if want == MessageKind::WantPlay && x_proposed {
                let line = config.consent_line_for(partner);
                if line > 0.0 {
                    // The gate reads the LIVE mid-tick world; this replay
                    // reads only tick boundaries. A target relieved
                    // mid-tick (pre-refusing, post-clean) was lawfully
                    // clean when the gate looked, so a genuine bypass
                    // must refuse on BOTH sides of the tick.
                    let pre_refuses = pre
                        .get(&partner)
                        .is_some_and(|&(top, play)| top > line && top > play);
                    let post_refuses = world.kitty(partner).is_some_and(|p| {
                        let top = p.top_non_play_pressure();
                        top > line && top > p.needs.get(cloudkitty_core::NeedKind::Play)
                    });
                    if pre_refuses && post_refuses {
                        consent_bypass += 1;
                    }
                }
            }
        }
        prev = world.kitties.iter().map(|k| (k.id, k.activity)).collect();
    }
    serde_json::json!({
        "ticks": 20000,
        "partnered_scene_starts": partnered_starts,
        "proposer_answered_starts": answered,
        "consent_bypass_scenes": consent_bypass,
    })
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
        ("cert_anchor_b3", "experiments/fog-gen1-cert/anchor-b3.toml"),
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
