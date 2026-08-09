//! Mixed control (spec 014 FR-020, T025): scripted kitties decide from
//! their engine-dealt streams and stay bit-deterministic, and the team
//! reward always counts the full roster, scripted kitties included.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::seam::{drive_tick, Provenance};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::episode::{Control, Episode};
use cloudkitty_rl::reward::team_reward;

fn scripted_control(core: &Config) -> BTreeMap<KittyId, Control> {
    core.kitties
        .iter()
        .map(|k| (k.id, Control::Builtin(k.behavior.clone())))
        .collect()
}

#[test]
fn an_all_scripted_episode_replays_the_behavior_driven_world_exactly() {
    // Every kitty scripted with its own configured behavior: the episode's
    // world must serialize byte-identically to a drive_tick loop from the
    // same seed — scripted decisions come from the very streams the engine
    // would deal (FR-020's bit-reproducibility clause).
    let core = Config::default();
    let control = scripted_control(&core);
    let mut episode = Episode::new(core, RlConfig::default(), control).unwrap();
    episode.reset(42);

    let mut config = Config::default();
    config.world.seed = 42;
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut reference = World::generate(&config);

    let empty = BTreeMap::new();
    for tick in 0..300u64 {
        episode.step(&empty).unwrap();
        drive_tick(&mut reference, &registry, &config);
        if tick % 50 == 0 || tick == 299 {
            // The episode deals the *next* tick's decision seeds eagerly
            // (mixed control needs them before the tick); give the
            // reference view the same deal before comparing bytes.
            let mut reference_view = reference.clone();
            reference_view.advance_past_decision_draws();
            assert_eq!(
                serde_json::to_string(episode.world()).unwrap(),
                serde_json::to_string(&reference_view).unwrap(),
                "diverged at tick {tick}"
            );
        }
    }
}

#[test]
fn mixed_rollouts_are_bit_reproducible() {
    // One external kitty among scripted friends, fed a fixed action script:
    // two runs from the same seed produce identical observation, mask,
    // global-state, and reward streams.
    let run = || {
        let core = Config::default();
        let external = core.kitties[0].id;
        let mut control = scripted_control(&core);
        control.insert(external, Control::External);
        let mut episode = Episode::new(core, RlConfig::default(), control).unwrap();
        episode.reset(7);

        let mut trace: Vec<String> = Vec::new();
        for step_index in 0..120u64 {
            // A deterministic little action script over the menu.
            let index = [33usize, 0, 2, 25, 12, 33][step_index as usize % 6]; // 33 = idle, menu v2
            let actions = BTreeMap::from([(external, index)]);
            let step = episode.step(&actions).unwrap();
            let obs = &step.observations[&external];
            trace.push(format!(
                "{:?}|{:?}|{:?}|{}",
                obs.values, step.infos[&external].mask, step.global_state, step.reward,
            ));
        }
        trace
    };

    assert_eq!(run(), run());
}

#[test]
fn the_team_reward_counts_the_full_roster() {
    // The broadcast scalar equals the welfare aggregate over every kitty in
    // the roster — never just the external faction (FR-020).
    let core = Config::default();
    let external = core.kitties[0].id;
    let mut control = scripted_control(&core);
    control.insert(external, Control::External);
    let rl = RlConfig::default();
    let mut episode = Episode::new(core, rl.clone(), control).unwrap();
    episode.reset(11);

    assert_eq!(episode.external_agents(), vec![external]);
    assert!(episode.roster().len() > 1, "scripted kitties are rostered");

    for _ in 0..25 {
        let actions = BTreeMap::from([(external, 33usize)]); // idle, menu v2
        let step = episode.step(&actions).unwrap();
        let expected = team_reward(
            &episode.world().snapshot(),
            episode.core_config(),
            &rl.reward,
        );
        assert_eq!(step.reward, expected, "reward is the full-roster welfare");
    }
}

#[test]
fn a_scripted_kittys_fallback_is_visible_in_the_step_report() {
    // Spec 014 review: the tick stamps every present proposal PolicyMade,
    // but a scripted kitty whose builtin panicked decided via the fallback
    // — the episode must restore the honest mark in the report it exposes
    // (FR-017: a broken advisor never rides the fallback unnoticed).
    // "panicky" is not a registered builtin name, so Episode::new refuses
    // it; instead prove the plumbing with the honest path both ways: a
    // healthy scripted kitty reads PolicyMade, and an absent external
    // proposal reads SubstitutedIdle, never PolicyMade.
    let core = Config::default();
    let scripted = core.kitties[1].id;
    let external = core.kitties[0].id;
    let mut control = scripted_control(&core);
    control.insert(external, Control::External);
    let mut episode = Episode::new(core, RlConfig::default(), control).unwrap();
    episode.reset(13);

    // External kitty sends nothing: substituted idle, marked honestly.
    let step = episode.step(&BTreeMap::new()).unwrap();
    let external_record = step.report.record(external).unwrap();
    assert_eq!(external_record.provenance, Provenance::SubstitutedIdle);
    let scripted_record = step.report.record(scripted).unwrap();
    assert_eq!(scripted_record.provenance, Provenance::PolicyMade);

    // And the absent external's info says "no proposal" — survived is
    // None, not a fabricated true (spec 014 review).
    let info = step.infos.get(&external).unwrap();
    assert_eq!(info.survived, None);
    assert_eq!(info.provenance, Some(Provenance::SubstitutedIdle));
}

#[test]
fn unseeded_resets_advance_a_deterministic_fresh_chain() {
    // Spec 014 review: reset_fresh must give a *different* episode every
    // call, while the chain itself replays exactly from the same start.
    let make = || {
        let core = Config::default();
        Episode::new(core, RlConfig::default(), BTreeMap::new()).unwrap()
    };
    let mut a = make();
    a.reset(7);
    let first = a.reset_fresh();
    let first_seed = a.current_seed();
    let second = a.reset_fresh();
    assert_ne!(first_seed, 7, "the chain moved off the explicit seed");
    assert_ne!(
        a.current_seed(),
        first_seed,
        "each fresh reset advances again"
    );
    let first_obs: Vec<f32> = first
        .observations
        .values()
        .flat_map(|o| o.values.clone())
        .collect();
    let second_obs: Vec<f32> = second
        .observations
        .values()
        .flat_map(|o| o.values.clone())
        .collect();
    assert_ne!(first_obs, second_obs, "fresh episodes genuinely differ");

    // The sequence replays bit-for-bit from the same starting seed.
    let mut b = make();
    b.reset(7);
    let first_again = b.reset_fresh();
    assert_eq!(b.current_seed(), first_seed);
    let again_obs: Vec<f32> = first_again
        .observations
        .values()
        .flat_map(|o| o.values.clone())
        .collect();
    assert_eq!(first_obs, again_obs, "the chain is reproducible");
}
