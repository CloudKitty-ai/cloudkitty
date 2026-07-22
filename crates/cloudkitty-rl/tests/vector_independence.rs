//! Vectorized independence (spec 014 FR-012, T026): world i in a batch is
//! bit-identical to the same world stepped alone — parallel scheduling can
//! never reorder or alter outputs.

use std::collections::BTreeMap;

use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::episode::{Episode, EpisodeStep};
use cloudkitty_rl::vector::VectorizedEnvironment;

fn fresh_episode() -> Episode {
    Episode::new(Config::default(), RlConfig::default(), BTreeMap::new()).unwrap()
}

fn action_for(step_index: usize, agent_index: usize) -> usize {
    // A deterministic per-agent script over the menu.
    [39usize, 0, 1, 2, 3, 25, 12, 4][(step_index + agent_index) % 8]
}

fn fingerprint(step: &EpisodeStep) -> String {
    let obs: Vec<_> = step
        .observations
        .iter()
        .map(|(id, o)| (id, &o.values))
        .collect();
    format!("{:?}|{}|{:?}", obs, step.reward, step.global_state)
}

#[test]
fn each_world_in_a_batch_matches_the_same_world_stepped_alone() {
    const WORLDS: usize = 3;
    const STEPS: usize = 60;
    let seeds: Vec<u64> = vec![70, 80, 90];

    // The batch, fanned out across threads.
    let mut batch =
        VectorizedEnvironment::new((0..WORLDS).map(|_| fresh_episode()).collect(), Some(WORLDS));
    for result in batch.reset(&seeds) {
        result.expect("reset succeeds");
    }
    let agents: Vec<KittyId> = batch.external_agents();

    let mut batch_traces: Vec<Vec<String>> = vec![Vec::new(); WORLDS];
    for step_index in 0..STEPS {
        let actions: Vec<BTreeMap<KittyId, usize>> = (0..WORLDS)
            .map(|_| {
                agents
                    .iter()
                    .enumerate()
                    .map(|(ai, &id)| (id, action_for(step_index, ai)))
                    .collect()
            })
            .collect();
        for (world, result) in batch.step(&actions).into_iter().enumerate() {
            batch_traces[world].push(fingerprint(&result.unwrap()));
        }
    }

    // Each world alone, sequentially.
    for (world, &seed) in seeds.iter().enumerate() {
        let mut solo = fresh_episode();
        solo.reset(seed);
        for (step_index, expected) in batch_traces[world].iter().enumerate() {
            let actions: BTreeMap<KittyId, usize> = agents
                .iter()
                .enumerate()
                .map(|(ai, &id)| (id, action_for(step_index, ai)))
                .collect();
            let step = solo.step(&actions).unwrap();
            assert_eq!(
                &fingerprint(&step),
                expected,
                "world {world} diverged from its solo run at step {step_index}"
            );
        }
    }
}

#[test]
fn worker_count_never_changes_outputs() {
    const WORLDS: usize = 4;
    let seeds: Vec<u64> = vec![1, 2, 3, 4];

    let run = |workers: usize| {
        let mut batch = VectorizedEnvironment::new(
            (0..WORLDS).map(|_| fresh_episode()).collect(),
            Some(workers),
        );
        for result in batch.reset(&seeds) {
            result.expect("reset succeeds");
        }
        let agents = batch.external_agents();
        let mut traces = Vec::new();
        for step_index in 0..30 {
            let actions: Vec<BTreeMap<KittyId, usize>> = (0..WORLDS)
                .map(|_| {
                    agents
                        .iter()
                        .enumerate()
                        .map(|(ai, &id)| (id, action_for(step_index, ai)))
                        .collect()
                })
                .collect();
            traces.push(
                batch
                    .step(&actions)
                    .into_iter()
                    .map(|r| fingerprint(&r.unwrap()))
                    .collect::<Vec<_>>(),
            );
        }
        traces
    };

    assert_eq!(run(1), run(4), "1 worker vs 4 workers: identical outputs");
}
