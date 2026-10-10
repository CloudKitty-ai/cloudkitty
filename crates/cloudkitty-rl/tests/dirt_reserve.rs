//! Spec 058 SC-004 / FR-013: the dirt-reserve inertness proof, the
//! constructible form of the e_col bar (F-058 check-1: prove
//! non-contribution, not mere zeroness in sampled states). Two legs:
//! (a) both cells read exactly 0.0 over a randomized world/config
//! battery; (b) no encoder write path reaches the reserve range — the
//! reserve push is the block's final write, so the cells before it
//! (waypoint) landing at their pinned offsets plus the block width
//! assertion mean nothing upstream can spill into 107-108. A constant
//! zero with no writer contributes nothing to any forward pass; the
//! pre-freeze record of this proof lives in the spec 058 contract.

use std::sync::Arc;

use cloudkitty_core::grid::Position;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::{encode_observation, offsets};

#[test]
fn the_reserve_reads_exactly_zero_over_a_randomized_battery() {
    // Deterministic pseudo-random sweep: the world's own seeded RNG via
    // varied seeds, sizes, positions, needs and ticks — every state we
    // can reach through public mutation.
    for seed in 0..32u64 {
        let mut c = test_config();
        c.world.seed = seed;
        let size = 16 + (seed as u32 % 3) * 42; // 16, 58, 100
        c.world.width = size;
        c.world.height = size;
        for (i, k) in c.kitties.iter_mut().enumerate() {
            k.x = (seed as u32 * 3 + i as u32 * 5) % size;
            k.y = (seed as u32 * 7 + i as u32 * 11) % size;
        }
        c.validate().unwrap();
        let c = Arc::new(c);
        let mut w = World::generate(&c);
        w.tick = seed * 97;
        let i = w.kitty_index(1).unwrap();
        w.kitties[i].needs.add(NeedKind::Bath, (seed % 90) as f32);
        w.kitties[i].pos = Position::new(seed as u32 % size, (seed as u32 * 13) % size);
        for id in [1u32, 2] {
            let view = w.snapshot().fog_for(id, c.vision.radius);
            let obs = encode_observation(&view, id, &c, &ObservationConfig::default());
            assert_eq!(
                &obs.values[offsets::SELF_DIRT_RESERVE..offsets::SELF_DIRT_RESERVE + 2],
                &[0.0, 0.0],
                "seed {seed}, observer {id}: the reserve is exactly zero in every state"
            );
        }
    }
}

#[test]
fn the_reserve_is_the_self_blocks_final_write_with_nothing_after_it() {
    // Leg (b): the write-path pin. The waypoint pair sits immediately
    // before the reserve and the reserve closes the self block — so the
    // only encoder statement that can touch 107-108 is the reserve push
    // itself (observe.rs documents it as the ONLY write path; this
    // asserts the geometry that makes that true).
    assert_eq!(offsets::SELF_DIRT_RESERVE, offsets::SELF_WAYPOINT + 2);
    assert_eq!(offsets::SELF_DIRT_RESERVE + 2, offsets::SELF_BLOCK);
}
