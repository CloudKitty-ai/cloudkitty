//! Spec 068 (World Branch API): a restored episode continues byte-
//! identically with the dealt seeds carried (US1), a one-tick proposal
//! override is ruled on by the engine's law and honestly marked (US2), one
//! world of a batch branches alone (US4), and a snapshot is refused where it
//! cannot be honoured (US5). Every guard here was seen red through
//! `scripts/mutate.sh` before it was cited green (tasks.md, rule 5).

use std::collections::BTreeMap;

use cloudkitty_core::action::Action;
use cloudkitty_core::config::WelfareHazardConfig;
use cloudkitty_core::kitty::{Activity, KittyId};
use cloudkitty_core::needy;
use cloudkitty_core::seam::Provenance;
use cloudkitty_core::Config;
use cloudkitty_rl::config::{RewardMode, RlConfig};
use cloudkitty_rl::episode::{Control, Episode, EpisodeError, EpisodeStep};
use cloudkitty_rl::mask::legal_action_mask;
use cloudkitty_rl::observe::encode_observation;
use cloudkitty_rl::vector::VectorizedEnvironment;

const ENGINE: &str = "test-engine-068";

/// The default roster with kitty 0 on the needy preset (spec 067: seated by
/// construction, acknowledged as the hazard it is) and kitty 1 external.
fn needy_config() -> Config {
    let mut c = Config::default();
    c.kitties[0].behavior = "needy".into();
    c.welfare_hazard = Some(WelfareHazardConfig {
        acknowledged: vec!["needy".into()],
    });
    c
}

fn mixed_control(core: &Config) -> BTreeMap<KittyId, Control> {
    core.kitties
        .iter()
        .enumerate()
        .map(|(i, k)| {
            let who = if i == 1 {
                Control::External
            } else {
                Control::Builtin(k.behavior.clone())
            };
            (k.id, who)
        })
        .collect()
}

fn new_episode(core: Config, rl: RlConfig) -> Episode {
    let control = mixed_control(&core);
    Episode::new(core, rl, control).expect("the fixture builds")
}

/// A deterministic action for every external agent: a legal menu index
/// chosen by rotation over the agent's own mask, Silent on the message head.
/// Equal states give equal actions, so a divergence shows up as a state
/// difference first, never as a scripted difference.
fn scripted_actions(
    step: &EpisodeStep,
    turn: u64,
    menu_len: usize,
) -> BTreeMap<KittyId, (usize, usize)> {
    step.infos
        .iter()
        .map(|(id, info)| {
            let legal: Vec<usize> = info.mask[..menu_len]
                .iter()
                .enumerate()
                .filter(|(_, &bit)| bit == 1)
                .map(|(i, _)| i)
                .collect();
            let pick = legal[(turn as usize * 7 + *id as usize) % legal.len()];
            (*id, (pick, 0))
        })
        .collect()
}

fn world_json(episode: &Episode) -> String {
    serde_json::to_string(episode.world()).unwrap()
}

fn infos_debug(step: &EpisodeStep) -> String {
    format!("{:?}", step.infos)
}

fn observations(step: &EpisodeStep) -> Vec<(KittyId, Vec<f32>)> {
    step.observations
        .iter()
        .map(|(id, o)| (*id, o.values.clone()))
        .collect()
}

fn seeds_of(step: &EpisodeStep) -> BTreeMap<KittyId, u64> {
    step.infos
        .iter()
        .map(|(id, i)| (*id, i.decision_seed))
        .collect()
}

fn idle_index(episode: &Episode) -> usize {
    episode.codec().len() - 1
}

fn record_of(step: &EpisodeStep, kitty: KittyId) -> &cloudkitty_core::seam::KittyTickRecord {
    step.report
        .record(kitty)
        .expect("every roster kitty has a record")
}

/// A branch of `original` at its current tick: a fresh episode of the same
/// identity restored from `original`'s snapshot.
fn fork(original: &Episode) -> Episode {
    let bytes = original.snapshot(ENGINE).unwrap();
    let mut branch = new_episode(needy_config(), original.rl_config().clone());
    branch.restore(ENGINE, &bytes).expect("a fork restores");
    branch
}

// ---------------------------------------------------------------------------
// US1 — hold a tick, branch it, continue byte-identically
// ---------------------------------------------------------------------------

/// G1 (FR-003/FR-004, SC-001/SC-002): over ten seeds, a never-reset twin
/// restored from a 300-tick snapshot reports the same next decision seeds
/// and then matches the original on every surface for 200 ticks.
#[test]
fn a_restored_episode_continues_byte_identically() {
    for seed in 0..10u64 {
        let mut original = new_episode(needy_config(), RlConfig::default());
        let menu_len = original.codec().len();
        let mut last = original.reset(seed);
        for turn in 0..300u64 {
            let actions = scripted_actions(&last, turn, menu_len);
            last = original.step(&actions).unwrap();
        }
        let bytes = original.snapshot(ENGINE).unwrap();

        let mut twin = new_episode(needy_config(), RlConfig::default());
        let restored = twin
            .restore(ENGINE, &bytes)
            .expect("same identity restores");
        assert_eq!(
            seeds_of(&restored),
            seeds_of(&last),
            "seed {seed}: the restored infos report the original's next decision_seed per agent"
        );
        assert_eq!(
            observations(&restored),
            observations(&last),
            "seed {seed}: restore returns the snapshot tick's observations"
        );
        assert_eq!(
            twin.current_seed(),
            original.current_seed(),
            "seed {seed}: the current seed (the fresh-seed chain's root) travelled"
        );
        assert_eq!(
            restored.global_state, last.global_state,
            "seed {seed}: the global state (the only surface carrying the episode clock) matches"
        );

        let mut a = last;
        for turn in 300..500u64 {
            let actions = scripted_actions(&a, turn, menu_len);
            a = original.step(&actions).unwrap();
            let b = twin.step(&actions).unwrap();
            assert_eq!(
                world_json(&original),
                world_json(&twin),
                "seed {seed} turn {turn}: world diverged"
            );
            assert_eq!(
                a.global_state, b.global_state,
                "seed {seed} turn {turn}: global state (episode clock) diverged"
            );
            assert_eq!(
                observations(&a),
                observations(&b),
                "seed {seed} turn {turn}: observations diverged"
            );
            assert_eq!(
                a.reward, b.reward,
                "seed {seed} turn {turn}: reward diverged"
            );
            assert_eq!(
                infos_debug(&a),
                infos_debug(&b),
                "seed {seed} turn {turn}: infos diverged"
            );
        }
    }
}

/// G2 (FR-002): the reward baselines travel — under delta reward with
/// shaping on, the restored twin's first-step reward equals the original's.
#[test]
fn restore_carries_the_reward_baselines() {
    let mut rl = RlConfig::default();
    rl.reward.mode = RewardMode::Delta;
    rl.reward.shaping.enabled = true;
    let mut original = new_episode(needy_config(), rl.clone());
    let menu_len = original.codec().len();
    let mut last = original.reset(3);
    for turn in 0..50u64 {
        last = original
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let bytes = original.snapshot(ENGINE).unwrap();
    let mut twin = new_episode(needy_config(), rl);
    let restored = twin.restore(ENGINE, &bytes).unwrap();
    let actions = scripted_actions(&last, 50, menu_len);
    let a = original.step(&actions).unwrap();
    let b = twin
        .step(&scripted_actions(&restored, 50, menu_len))
        .unwrap();
    assert_eq!(
        a.reward, b.reward,
        "the first reward after restore equals the original's (baselines carried)"
    );
}

/// G4 (FR-007): a snapshot taken at the horizon restores truncated; the
/// twin refuses to step until reset, exactly as the original would.
#[test]
fn a_truncated_snapshot_restores_truncated() {
    let mut rl = RlConfig::default();
    rl.episode.horizon = 5;
    let mut original = new_episode(needy_config(), rl.clone());
    let menu_len = original.codec().len();
    let mut last = original.reset(1);
    for turn in 0..5u64 {
        last = original
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    assert!(
        last.truncated,
        "staged: the original truncated at the horizon"
    );
    let bytes = original.snapshot(ENGINE).unwrap();
    let mut twin = new_episode(needy_config(), rl);
    let restored = twin.restore(ENGINE, &bytes).unwrap();
    assert!(restored.truncated, "the restored step reports truncated");
    assert!(
        matches!(
            twin.step(&BTreeMap::new()),
            Err(EpisodeError::SteppedAfterTruncation)
        ),
        "a truncated restore refuses to step (SteppedAfterTruncation) until reset"
    );
    twin.reset(9);
    twin.step(&BTreeMap::new())
        .expect("reset heals truncation as today");
}

/// G5 (US1 scenario 5): restore replaces state wholesale — stepping past
/// the snapshot and restoring brings the episode back to the snapshot tick.
#[test]
fn restore_replaces_state_wholesale() {
    let mut episode = new_episode(needy_config(), RlConfig::default());
    let menu_len = episode.codec().len();
    let mut last = episode.reset(5);
    for turn in 0..40u64 {
        last = episode
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let at_snapshot = world_json(&episode);
    let seeds_at_snapshot = seeds_of(&last);
    let bytes = episode.snapshot(ENGINE).unwrap();
    episode
        .step(&scripted_actions(&last, 40, menu_len))
        .unwrap();
    assert_ne!(
        world_json(&episode),
        at_snapshot,
        "staged: the world moved on"
    );
    let restored = episode.restore(ENGINE, &bytes).unwrap();
    assert_eq!(
        world_json(&episode),
        at_snapshot,
        "the world is back at the snapshot tick"
    );
    assert_eq!(
        seeds_of(&restored),
        seeds_at_snapshot,
        "the dealt seeds are the snapshot's, not re-dealt"
    );
}

// ---------------------------------------------------------------------------
// US2 — one-tick proposal override under the law, honestly marked
// ---------------------------------------------------------------------------

/// A scripted (builtin, non-needy) seat of the fixture.
fn scripted_seat(episode: &Episode) -> KittyId {
    episode
        .control()
        .iter()
        .find(|(id, c)| {
            matches!(c, Control::Builtin(name) if !needy::is_needy_name(name)) && **id != 0
        })
        .map(|(id, _)| *id)
        .expect("the fixture seats a builtin")
}

/// G7 (FR-009/FR-011, SC-004): an act-only override applies for exactly
/// one tick with the `OverriddenAct` mark; the next tick is the seat's own.
/// Staged against a fork at a tick where the seat's own act is NOT the
/// override's, so a mutant that sets the mark but drops the act cannot pass
/// by coincidence (review 2026-11-06). Runs over every builtin preset and
/// both needy presets (SC-004 "every builtin and needy preset").
#[test]
fn an_act_override_applies_for_exactly_one_tick() {
    for preset in ["needs_driven", "playful", "teacher", "needy", "needy_hold"] {
        let mut core = needy_config();
        core.kitties[0].behavior = preset.into();
        if needy::is_needy_name(preset) {
            core.welfare_hazard = Some(WelfareHazardConfig {
                acknowledged: vec![preset.into()],
            });
        } else {
            core.welfare_hazard = None;
        }
        let seat = core.kitties[0].id;
        let mut rl = RlConfig::default();
        rl.episode.horizon = 10_000;
        let mut original = Episode::new(core.clone(), rl.clone(), mixed_control(&core)).unwrap();
        let menu_len = original.codec().len();
        let mut last = original.reset(11);
        let idle = idle_index(&original);
        let mut done = false;
        for turn in 0..3000u64 {
            let bytes = original.snapshot(ENGINE).unwrap();
            let mut branch = Episode::new(core.clone(), rl.clone(), mixed_control(&core)).unwrap();
            branch.restore(ENGINE, &bytes).unwrap();
            let actions = scripted_actions(&last, turn, menu_len);
            let a = original.step(&actions).unwrap();
            if record_of(&a, seat).proposed == Action::Idle {
                last = a;
                continue; // the seat's own act is the override's; try the next tick
            }
            branch.override_next(seat, Some(idle), None).unwrap();
            let b = branch.step(&actions).unwrap();
            let rb = record_of(&b, seat);
            assert_eq!(
                rb.provenance,
                Provenance::OverriddenAct,
                "{preset}: the overridden tick carries the act mark"
            );
            assert_eq!(
                rb.proposed,
                Action::Idle,
                "{preset}: the proposal is the override's act (the seat's own was {:?})",
                record_of(&a, seat).proposed
            );
            let next = branch
                .step(&scripted_actions(&b, turn + 1, menu_len))
                .unwrap();
            assert_eq!(
                record_of(&next, seat).provenance,
                Provenance::PolicyMade,
                "{preset}: one tick only: the seat decides for itself again"
            );
            done = true;
            break;
        }
        assert!(
            done,
            "staged: {preset} proposed a non-idle act within 3000 ticks"
        );
    }
}

/// G19 (FR-014, SC-004, doctrine rule 6): an act-only override leaves the
/// MESSAGE the seat's own — the branch says exactly what the original said
/// on a tick where the seat's own call is not Silent. The mutant this
/// catches is the harness scripting the free register as a side effect of
/// branching (review 2026-11-06, blocking finding).
#[test]
fn an_act_override_leaves_the_message_the_seats_own() {
    let mut rl = RlConfig::default();
    rl.episode.horizon = 10_000;
    let mut original = new_episode(needy_config(), rl);
    let menu_len = original.codec().len();
    let seat = scripted_seat(&original);
    let mut last = original.reset(19);
    let idle = idle_index(&original);
    let mut checked = false;
    for turn in 0..6000u64 {
        let mut branch = fork(&original);
        let actions = scripted_actions(&last, turn, menu_len);
        let a = original.step(&actions).unwrap();
        let ra = record_of(&a, seat);
        if ra.proposed_message.is_none() {
            last = a;
            continue; // Silent would be indistinguishable from a scripted Silent
        }
        branch.override_next(seat, Some(idle), None).unwrap();
        let b = branch.step(&actions).unwrap();
        let rb = record_of(&b, seat);
        assert_eq!(
            rb.proposed_message, ra.proposed_message,
            "the branch's message is the seat's own ({:?}), not the harness's",
            ra.proposed_message
        );
        assert_eq!(rb.proposed, Action::Idle, "the act half is the override's");
        assert_eq!(rb.provenance, Provenance::OverriddenAct);
        checked = true;
        break;
    }
    assert!(
        checked,
        "staged: the seat called something non-Silent within 6000 ticks"
    );
}

/// G8 (FR-014): a message-only override leaves the act the seat's own —
/// the branch (a fork of the same tick) proposes the same act as the
/// original and the named message, marked `OverriddenMessage`.
#[test]
fn a_message_override_leaves_the_act_the_seats_own() {
    let mut original = new_episode(needy_config(), RlConfig::default());
    let menu_len = original.codec().len();
    let seat = scripted_seat(&original);
    let mut last = original.reset(13);
    for turn in 0..30u64 {
        last = original
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let bytes = original.snapshot(ENGINE).unwrap();
    let mut branch = new_episode(needy_config(), RlConfig::default());
    branch.restore(ENGINE, &bytes).unwrap();
    let want_eat = 1; // head index 1 = the first message kind after Silent
    branch.override_next(seat, None, Some(want_eat)).unwrap();
    let actions = scripted_actions(&last, 30, menu_len);
    let a = original.step(&actions).unwrap();
    let b = branch.step(&actions).unwrap();
    let ra = record_of(&a, seat);
    let rb = record_of(&b, seat);
    assert_eq!(
        rb.provenance,
        Provenance::OverriddenMessage,
        "the branch tick carries the message mark"
    );
    assert_eq!(rb.proposed, ra.proposed, "the act stays the seat's own");
    assert_eq!(
        rb.proposed_message,
        cloudkitty_rl::codec::MessageCodec::decode(want_eat).unwrap(),
        "the proposed message is the named one"
    );
    assert_eq!(
        ra.provenance,
        Provenance::PolicyMade,
        "the original tick is the seat's own"
    );
}

/// G9 (FR-011/FR-014): both halves named → `OverriddenBoth`, and both halves
/// are the override's — staged on a fork at a tick where the seat's own act
/// differs from the override's, so neither half can match by coincidence.
#[test]
fn both_halves_override_marks_overridden_both() {
    let mut rl = RlConfig::default();
    rl.episode.horizon = 10_000;
    let mut original = new_episode(needy_config(), rl);
    let menu_len = original.codec().len();
    let seat = scripted_seat(&original);
    let mut last = original.reset(17);
    let idle = idle_index(&original);
    let want_eat = 1; // head index 1 = the first message kind after Silent
    let mut checked = false;
    for turn in 0..3000u64 {
        let mut branch = fork(&original);
        let actions = scripted_actions(&last, turn, menu_len);
        let a = original.step(&actions).unwrap();
        let ra = record_of(&a, seat);
        if ra.proposed == Action::Idle || ra.proposed_message.is_some() {
            last = a;
            continue;
        }
        branch
            .override_next(seat, Some(idle), Some(want_eat))
            .unwrap();
        let b = branch.step(&actions).unwrap();
        let rb = record_of(&b, seat);
        assert_eq!(rb.provenance, Provenance::OverriddenBoth);
        assert_eq!(rb.proposed, Action::Idle, "the act is the override's");
        assert_eq!(
            rb.proposed_message,
            cloudkitty_rl::codec::MessageCodec::decode(want_eat).unwrap(),
            "the message is the override's"
        );
        checked = true;
        break;
    }
    assert!(
        checked,
        "staged: a tick where the seat's own act was non-idle and its call Silent"
    );
}

/// G10 (FR-010, SC-005): an override proposing relief of the needy seat's
/// own masked need resolves to idle at the apply slot and is stamped a
/// refusal — the law rules, the mark stays honest.
#[test]
fn an_override_cannot_relieve_a_masked_need() {
    let core = needy_config();
    let needy_seat = core.kitties[0].id;
    let mut rl = RlConfig::default();
    rl.episode.horizon = 10_000;
    let mut episode = new_episode(core, rl);
    let menu_len = episode.codec().len();
    let mut last = episode.reset(23);
    let mut found: Option<(usize, Action)> = None;
    for turn in 0..6000u64 {
        let world = episode.world();
        let kitty = world.kitty(needy_seat).unwrap();
        let schedule = kitty
            .needy
            .as_ref()
            .expect("a needy seat carries its schedule");
        if schedule.phase_name(world.tick) == "held" {
            let mask = schedule.mask();
            let snapshot = world.snapshot();
            let view = snapshot.fog_for(needy_seat, episode.core_config().vision.radius);
            let observation = encode_observation(
                &view,
                needy_seat,
                episode.core_config(),
                &episode.rl_config().observation,
            );
            let legal = legal_action_mask(
                &view,
                needy_seat,
                &observation.table,
                episode.codec(),
                episode.core_config(),
            );
            for (index, &legal_here) in legal.iter().enumerate() {
                if !legal_here {
                    continue;
                }
                let action = episode.codec().decode(index, &observation.table).unwrap();
                // A relief that names no kitty: the refusal stamp labels that
                // path NeedyMasked, which is what the assertion below pins
                // (a partnered relief could also be refused for the
                // partner's reasons, and a validation refusal would stamp
                // another reason entirely).
                if needy::proposer_relief(&action).meets(mask)
                    && needy::partner_relief(&action).is_none()
                {
                    found = Some((index, action));
                    break;
                }
            }
            if found.is_some() {
                break;
            }
        }
        last = episode
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let (index, relief) =
        found.expect("staged: a validation-legal act that relieves a masked need");
    let refusals_before = episode.world().refusal_log.len();
    let tick = episode.world().tick;
    episode
        .override_next(needy_seat, Some(index), None)
        .unwrap();
    let step = episode
        .step(&scripted_actions(&last, 9999, menu_len))
        .unwrap();
    let record = record_of(&step, needy_seat);
    assert_eq!(
        record.applied,
        Action::Idle,
        "the masked relief {relief:?} resolves to Idle at the apply slot"
    );
    assert_eq!(record.proposed, relief, "the proposal was the override's");
    let newest = episode
        .world()
        .refusal_log
        .newest()
        .expect("a refusal was stamped");
    assert!(
        episode.world().refusal_log.len() > refusals_before
            && newest.kitty_id == needy_seat
            && newest.tick == tick,
        "the refusal is on the record for the needy seat at tick {tick}"
    );
    assert_eq!(
        newest.reason,
        cloudkitty_core::events::RefusalReason::NeedyMasked,
        "the NEEDY verdict refused it, not validation"
    );
    assert_eq!(
        record.provenance,
        Provenance::OverriddenAct,
        "the mark still says the harness proposed it"
    );
}

/// G11 (FR-010, SC-005): inside a scene's minimum, an override of a
/// different act is continued by duration enforcement like any proposal.
#[test]
fn an_override_inside_a_scene_minimum_continues_the_scene() {
    let mut rl = RlConfig::default();
    rl.episode.horizon = 10_000;
    let mut episode = new_episode(needy_config(), rl);
    let menu_len = episode.codec().len();
    let mut last = episode.reset(29);
    let durations = episode.core_config().actions.durations;
    // (seat, the scene's continuation, a validation-legal act that would
    // INTERRUPT it). Idle continues every scene (`Activity::is_continued_by`),
    // so the override must name a genuinely different act — a move onto a
    // free tile — for the minimum clause of duration enforcement to be what
    // holds the scene (a vacuous first cut of this guard used Idle;
    // mutate.sh caught it). The move is chosen by validation's own rule
    // (in bounds, no kitty there), NOT from the legal mask: the mask already
    // replays duration enforcement and masks every interrupting act out.
    let mut staged: Option<(KittyId, Action, usize, Action)> = None;
    for turn in 0..9000u64 {
        let world = episode.world();
        for (id, control) in episode.control() {
            if !matches!(control, Control::Builtin(_)) {
                continue;
            }
            let kitty = world.kitty(*id).unwrap();
            let (Some(clock), Some(bounds), Some(continuation)) = (
                kitty.activity_clock,
                kitty.activity.bounds(&durations),
                kitty.activity.continuation(),
            ) else {
                continue;
            };
            // A SOLO sleep or rest: its counterpart cannot vanish (a critter
            // play's bug may die, a duet's partner may leave, a meal's bowl
            // may empty — each ends the scene before duration enforcement
            // is heard), so the minimum clause alone decides the outcome.
            let solo_long = matches!(
                kitty.activity,
                Activity::Sleeping {
                    with_friend: None,
                    ..
                } | Activity::Resting { with_friend: None }
            );
            if !(solo_long
                && bounds.min >= 2
                && clock.serviced_before(world.tick) < bounds.min
                && continuation != Action::Idle)
            {
                continue;
            }
            let snapshot = world.snapshot();
            let view = snapshot.fog_for(*id, episode.core_config().vision.radius);
            let observation = encode_observation(
                &view,
                *id,
                episode.core_config(),
                &episode.rl_config().observation,
            );
            let interrupt = (0..menu_len).find_map(|index| {
                let action = episode.codec().decode(index, &observation.table).ok()?;
                let Action::Move { direction } = action else {
                    return None;
                };
                let dest = kitty.pos.step(direction, world.width, world.height)?;
                (world.kitty_at(dest).is_none() && !kitty.activity.is_continued_by(&action))
                    .then_some((index, action))
            });
            if let Some((index, action)) = interrupt {
                staged = Some((*id, continuation, index, action));
                break;
            }
        }
        if staged.is_some() {
            break;
        }
        last = episode
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let (seat, continuation, index, interrupting) = staged
        .expect("staged: a scripted seat inside a scene minimum with a legal move to propose");
    episode.override_next(seat, Some(index), None).unwrap();
    let step = episode
        .step(&scripted_actions(&last, 9999, menu_len))
        .unwrap();
    let record = record_of(&step, seat);
    assert_eq!(
        record.proposed, interrupting,
        "the override proposed the interrupting move"
    );
    assert_eq!(
        record.validated, interrupting,
        "the move survived validation, so enforcement alone can hold the scene"
    );
    assert_eq!(
        record.applied, continuation,
        "duration enforcement continues the scene"
    );
    assert_eq!(record.provenance, Provenance::OverriddenAct);
}

/// G12 (FR-012): every refusal names its cause and leaves the episode as
/// it was.
#[test]
fn override_refusals_name_their_cause_and_leave_the_episode_untouched() {
    let core = needy_config();
    let external = core.kitties[1].id;
    let mut episode = new_episode(core, RlConfig::default());
    let seat = scripted_seat(&episode);
    let _ = episode.reset(31);
    // The snapshot bytes hold the world AND the pending seeds: equal bytes
    // after the refusals = nothing moved (the first cut compared a value
    // with itself — review 2026-11-06).
    let before = episode.snapshot(ENGINE).unwrap();
    let idle = idle_index(&episode);
    let menu_len = episode.codec().len();

    assert!(
        matches!(episode.override_next(external, Some(idle), None), Err(EpisodeError::OverrideRefused { kitty, ref reason }) if kitty == external && reason.contains("externally controlled")),
        "an external seat is refused"
    );
    assert!(
        matches!(episode.override_next(999, Some(idle), None), Err(EpisodeError::OverrideRefused { kitty: 999, ref reason }) if reason.contains("roster")),
        "an unknown kitty is refused"
    );
    assert!(
        matches!(episode.override_next(seat, None, None), Err(EpisodeError::OverrideRefused { ref reason, .. }) if reason.contains("name an action, a message, or both")),
        "an empty override is refused"
    );
    assert!(
        matches!(episode.override_next(seat, Some(menu_len), None), Err(EpisodeError::ActionOutOfRange { index, .. }) if index == menu_len),
        "an out-of-range act is refused as step would"
    );
    assert!(
        matches!(
            episode.override_next(seat, None, Some(16)),
            Err(EpisodeError::MessageOutOfRange { index: 16, .. })
        ),
        "an out-of-range message is refused as step would"
    );
    episode.override_next(seat, Some(idle), None).unwrap();
    assert!(
        matches!(episode.override_next(seat, Some(idle), None), Err(EpisodeError::OverrideRefused { ref reason, .. }) if reason.contains("already")),
        "a second override before a step is refused"
    );
    // The pending (accepted) override is not in the snapshot — by design it
    // belongs to this state and is dropped by restore — so the bytes still
    // compare equal; what they prove is that no REFUSAL moved world or seeds.
    assert_eq!(
        episode.snapshot(ENGINE).unwrap(),
        before,
        "no refusal touched the episode (world and pending seeds unchanged)"
    );
}

/// G13 (FR-012): reset and restore drop a pending override.
#[test]
fn reset_and_restore_drop_a_pending_override() {
    let mut episode = new_episode(needy_config(), RlConfig::default());
    let menu_len = episode.codec().len();
    let seat = scripted_seat(&episode);
    let last = episode.reset(37);
    let bytes = episode.snapshot(ENGINE).unwrap();
    let idle = idle_index(&episode);

    episode.override_next(seat, Some(idle), None).unwrap();
    let restored = episode.restore(ENGINE, &bytes).unwrap();
    let step = episode
        .step(&scripted_actions(&restored, 0, menu_len))
        .unwrap();
    assert_eq!(
        record_of(&step, seat).provenance,
        Provenance::PolicyMade,
        "restore dropped the override"
    );

    episode.override_next(seat, Some(idle), None).unwrap();
    let reset = episode.reset(37);
    let step = episode
        .step(&scripted_actions(&reset, 0, menu_len))
        .unwrap();
    assert_eq!(
        record_of(&step, seat).provenance,
        Provenance::PolicyMade,
        "reset dropped the override"
    );
    let _ = last;
}

/// G14 (FR-012): a step refused for a bad external action leaves the
/// override standing for the next, legal step.
#[test]
fn a_refused_step_leaves_the_override_standing() {
    let core = needy_config();
    let external = core.kitties[1].id;
    let mut episode = new_episode(core, RlConfig::default());
    let menu_len = episode.codec().len();
    let seat = scripted_seat(&episode);
    let last = episode.reset(41);
    let idle = idle_index(&episode);
    episode.override_next(seat, Some(idle), None).unwrap();
    let bad = BTreeMap::from([(external, (menu_len, 0usize))]);
    assert!(
        matches!(
            episode.step(&bad),
            Err(EpisodeError::ActionOutOfRange { .. })
        ),
        "staged: the step is refused"
    );
    let step = episode.step(&scripted_actions(&last, 0, menu_len)).unwrap();
    assert_eq!(
        record_of(&step, seat).provenance,
        Provenance::OverriddenAct,
        "the override survived the refused step"
    );
}

// ---------------------------------------------------------------------------
// US4 — one world of a batch branches alone
// ---------------------------------------------------------------------------

/// G15 (FR-008): in a two-world batch with one worker PER WORLD (so the
/// per-index routing in `VectorizedEnvironment::one` is exercised, not just
/// local-index arithmetic), world 0 restored from its own snapshot matches a
/// single episode restored from the same bytes (seeds, observations and the
/// serialized world), world 1 matches an un-branched twin batch, and world 1
/// can then be branched too.
#[test]
fn a_batched_world_branches_alone() {
    let build = || {
        let episodes: Vec<Episode> = (0..2)
            .map(|_| new_episode(needy_config(), RlConfig::default()))
            .collect();
        VectorizedEnvironment::new(episodes, None)
    };
    let mut batch = build();
    let mut twin_batch = build();
    let seeds = [100u64, 200];
    let mut steps: Vec<EpisodeStep> = batch
        .reset(&seeds)
        .into_iter()
        .map(|r| r.unwrap())
        .collect();
    let mut twin_steps: Vec<EpisodeStep> = twin_batch
        .reset(&seeds)
        .into_iter()
        .map(|r| r.unwrap())
        .collect();
    let menu_len = steps[0].infos.values().next().unwrap().mask.len()
        - cloudkitty_rl::codec::MessageCodec::LEN;
    let act = |steps: &[EpisodeStep], turn: u64| -> Vec<BTreeMap<KittyId, (usize, usize)>> {
        steps
            .iter()
            .map(|s| scripted_actions(s, turn, menu_len))
            .collect()
    };
    for turn in 0..30u64 {
        steps = batch
            .step(&act(&steps, turn))
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
        twin_steps = twin_batch
            .step(&act(&twin_steps, turn))
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
    }
    let bytes = batch.snapshot(0, ENGINE).unwrap();
    let bytes1 = batch.snapshot(1, ENGINE).unwrap();
    let seeds1_at_30 = seeds_of(&twin_steps[1]);
    for turn in 30..40u64 {
        steps = batch
            .step(&act(&steps, turn))
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
        twin_steps = twin_batch
            .step(&act(&twin_steps, turn))
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
    }
    let restored0 = batch.restore(0, ENGINE, &bytes).unwrap();
    let mut single = new_episode(needy_config(), RlConfig::default());
    let single_restored = single.restore(ENGINE, &bytes).unwrap();
    assert_eq!(
        seeds_of(&restored0),
        seeds_of(&single_restored),
        "world 0 restored like a single episode would"
    );
    steps[0] = restored0;
    for turn in 40..60u64 {
        let actions = act(&steps, turn);
        let single_step = single.step(&actions[0]).unwrap();
        steps = batch
            .step(&actions)
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
        twin_steps = twin_batch
            .step(&act(&twin_steps, turn))
            .into_iter()
            .map(|r| r.unwrap())
            .collect();
        assert_eq!(
            observations(&steps[0]),
            observations(&single_step),
            "turn {turn}: world 0 tracks the single restore"
        );
        assert_eq!(
            observations(&steps[1]),
            observations(&twin_steps[1]),
            "turn {turn}: world 1 is untouched by the branch"
        );
    }
    assert_eq!(
        batch.snapshot(0, ENGINE).unwrap(),
        single.snapshot(ENGINE).unwrap(),
        "world 0's serialized state (world + seeds) equals the single restore's"
    );
    let restored1 = batch.restore(1, ENGINE, &bytes1).unwrap();
    assert_eq!(
        seeds_of(&restored1),
        seeds1_at_30,
        "world 1 restores to its own tick-30 deal: the second worker is addressed too"
    );
}

// ---------------------------------------------------------------------------
// US5 — a snapshot is refused where it cannot be honoured
// ---------------------------------------------------------------------------

/// G16 (FR-006, SC-003): every identity mismatch class is refused, naming
/// its component, with the episode untouched.
#[test]
fn restore_refuses_every_identity_mismatch() {
    let mut original = new_episode(needy_config(), RlConfig::default());
    let menu_len = original.codec().len();
    let mut last = original.reset(43);
    for turn in 0..10u64 {
        last = original
            .step(&scripted_actions(&last, turn, menu_len))
            .unwrap();
    }
    let bytes = original.snapshot(ENGINE).unwrap();

    // Each refused episode is reset first so its own snapshot bytes (world +
    // pending seeds) can be compared before and after: "untouched" means the
    // bytes are equal, not merely that it still steps.
    let refuse = |episode: &mut Episode, label: &str, engine: &str, component: &str| {
        episode.reset(5);
        let before = episode.snapshot(ENGINE).unwrap();
        match episode.restore(engine, &bytes) {
            Err(EpisodeError::SnapshotIdentity {
                component: got,
                found,
                expected,
            }) => {
                assert_eq!(got, component, "{label}: the differing component is named");
                assert_ne!(
                    found, expected,
                    "{label}: both values are reported and differ"
                );
                if component == "control" {
                    assert!(
                        found.starts_with("kitty_") && expected.starts_with("kitty_"),
                        "{label}: the control refusal names the seat ({found} / {expected})"
                    );
                }
            }
            other => panic!("{label}: expected an identity refusal on {component}, got {other:?}"),
        }
        assert_eq!(
            episode.snapshot(ENGINE).unwrap(),
            before,
            "{label}: the refused episode is exactly as it was"
        );
        episode
            .step(&BTreeMap::new())
            .expect("the refused episode still steps");
    };

    let mut same = new_episode(needy_config(), RlConfig::default());
    refuse(
        &mut same,
        "engine commit",
        "another-engine",
        "engine_commit",
    );

    let mut rl = RlConfig::default();
    rl.episode.horizon = 7;
    let mut horizon = new_episode(needy_config(), rl);
    refuse(&mut horizon, "rl horizon", ENGINE, "config_digest");

    let mut core = needy_config();
    core.kitties[2].behavior = "playful".into();
    let mut behaviour = new_episode(core, RlConfig::default());
    refuse(
        &mut behaviour,
        "core behaviour name",
        ENGINE,
        "config_digest",
    );

    let core = needy_config();
    let mut control = mixed_control(&core);
    control.insert(core.kitties[2].id, Control::External);
    let mut seats = Episode::new(core, RlConfig::default(), control).unwrap();
    refuse(&mut seats, "control map", ENGINE, "control");

    let mut same_seed_differs = new_episode(needy_config(), RlConfig::default());
    same_seed_differs.reset(999);
    same_seed_differs
        .restore(ENGINE, &bytes)
        .expect("the seed is state, not identity: a differently seeded twin accepts the snapshot");

    // Control is normalized over the roster: a seat left unnamed (implicitly
    // external) and one named "external" are the same environment.
    let core = needy_config();
    let mut unnamed = mixed_control(&core);
    unnamed.remove(&core.kitties[1].id);
    let mut spelled_differently = Episode::new(core, RlConfig::default(), unnamed).unwrap();
    spelled_differently
        .restore(ENGINE, &bytes)
        .expect("an unnamed external seat and an explicit one are one identity");
}

/// G20 (FR-006, Articles I–V): a snapshot that parses but holds a world this
/// environment cannot lawfully run — a trimmed roster, a foreign world
/// fingerprint — is refused as malformed, exactly as the server's load path
/// would refuse it, and the episode is untouched.
#[test]
fn restore_refuses_a_tampered_world() {
    let mut episode = new_episode(needy_config(), RlConfig::default());
    episode.reset(53);
    let bytes = episode.snapshot(ENGINE).unwrap();
    let mut value: serde_json::Value = serde_json::from_slice(&bytes).unwrap();

    let mut trimmed = value.clone();
    trimmed["world"]["kitties"].as_array_mut().unwrap().pop();
    let before = episode.snapshot(ENGINE).unwrap();
    assert!(
        matches!(
            episode.restore(ENGINE, &serde_json::to_vec(&trimmed).unwrap()),
            Err(EpisodeError::SnapshotMalformed(ref why)) if why.contains("roster")
        ),
        "a world missing a roster kitty is refused as malformed"
    );
    assert_eq!(episode.snapshot(ENGINE).unwrap(), before, "untouched");

    value["world"]["config_fingerprint"] = serde_json::Value::String("w1h1s1k1".into());
    assert!(
        matches!(
            episode.restore(ENGINE, &serde_json::to_vec(&value).unwrap()),
            Err(EpisodeError::SnapshotMalformed(ref why)) if why.contains("fingerprint")
        ),
        "a world stamped for another config is refused as malformed"
    );
    assert_eq!(episode.snapshot(ENGINE).unwrap(), before, "untouched");
    episode.step(&BTreeMap::new()).expect("and still steps");
}

/// G17 (FR-006): bytes that are not a snapshot are refused as malformed and
/// the episode is untouched.
#[test]
fn restore_refuses_bytes_that_are_not_a_snapshot() {
    let mut episode = new_episode(needy_config(), RlConfig::default());
    episode.reset(47);
    let before = world_json(&episode);
    assert!(
        matches!(
            episode.restore(ENGINE, b"not a snapshot"),
            Err(EpisodeError::SnapshotMalformed(_))
        ),
        "garbage is refused as malformed"
    );
    assert_eq!(world_json(&episode), before, "the episode is untouched");
    episode.step(&BTreeMap::new()).expect("and still steps");
}
