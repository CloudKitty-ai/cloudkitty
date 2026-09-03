//! Encoder determinism and bounds (spec 014 FR-005/FR-019, T021): the same
//! snapshot produces identical observation and global-state vectors, with
//! every value inside the documented bounds.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::config::{GlobalStateConfig, ObservationConfig};
use cloudkitty_rl::global_state::{encode_global_state, global_state_len};
use cloudkitty_rl::observe::{encode_observation, observation_len};

#[test]
fn observations_and_global_state_are_deterministic_and_bounded_across_a_run() {
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let obs_cfg = ObservationConfig::default();
    let gs_cfg = GlobalStateConfig::default();

    for tick in 0..200u64 {
        let snapshot = world.snapshot();
        let clock = tick as f32 / 200.0;

        for kitty in &snapshot.kitties {
            let view = snapshot.fog_for(kitty.id, config.vision.radius);
            let a = encode_observation(&view, kitty.id, &config, &obs_cfg, clock);
            let b = encode_observation(&view, kitty.id, &config, &obs_cfg, clock);
            assert_eq!(a.values, b.values, "tick {tick}, kitty {}", kitty.id);
            assert_eq!(a.table, b.table);
            assert_eq!(a.values.len(), observation_len(&obs_cfg));
            for (i, v) in a.values.iter().enumerate() {
                assert!(
                    v.is_finite() && (-1.0..=4.0).contains(v),
                    "tick {tick} kitty {} index {i}: {v}",
                    kitty.id
                );
            }
        }

        let g1 = encode_global_state(&snapshot, &config, &gs_cfg, &obs_cfg, clock);
        let g2 = encode_global_state(&snapshot, &config, &gs_cfg, &obs_cfg, clock);
        assert_eq!(g1, g2);
        assert_eq!(g1.len(), global_state_len(snapshot.kitties.len(), &gs_cfg));
        for (i, v) in g1.iter().enumerate() {
            assert!(v.is_finite() && (0.0..=4.0).contains(v), "global {i}: {v}");
        }

        drive_tick(&mut world, &registry, &config);
    }
}

#[test]
fn same_seed_worlds_encode_identically() {
    // Two worlds from the same seed, stepped identically, encode
    // identically — the SC-002 property at the Rust layer.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    let mut a = World::generate(&config);
    let mut b = World::generate(&config);
    let obs_cfg = ObservationConfig::default();

    for _ in 0..50 {
        drive_tick(&mut a, &registry, &config);
        drive_tick(&mut b, &registry, &config);
    }
    let sa = a.snapshot();
    let sb = b.snapshot();
    for kitty in &sa.kitties {
        let va = sa.fog_for(kitty.id, config.vision.radius);
        let vb = sb.fog_for(kitty.id, config.vision.radius);
        let oa = encode_observation(&va, kitty.id, &config, &obs_cfg, 0.0);
        let ob = encode_observation(&vb, kitty.id, &config, &obs_cfg, 0.0);
        assert_eq!(oa.values, ob.values);
    }
}
