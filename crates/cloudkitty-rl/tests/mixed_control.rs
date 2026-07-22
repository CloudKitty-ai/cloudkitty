//! Mixed control (spec 014 FR-020, T025): scripted kitties decide from
//! their engine-dealt streams and stay bit-deterministic, and the team
//! reward always counts the full roster, scripted kitties included.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::seam::drive_tick;
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
            reference_view.deal_decision_seeds();
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
            let index = [39usize, 0, 2, 25, 12, 39][step_index as usize % 6];
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
        let actions = BTreeMap::from([(external, 39usize)]);
        let step = episode.step(&actions).unwrap();
        let expected = team_reward(
            &episode.world().snapshot(),
            episode.core_config(),
            &rl.reward,
        );
        assert_eq!(step.reward, expected, "reward is the full-roster welfare");
    }
}
