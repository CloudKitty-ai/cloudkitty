//! Spec 058 SC-003 / FR-015: the column map's two version arms, each
//! against its own oracle — v5 against the contract literals that
//! schema_five_pins also pins (so map and oracle can never drift apart
//! silently), v6 against the live pins and the default slot config —
//! plus the loud failure modes (unknown version, unknown cell, slot out
//! of range). Mutation-verified: a swapped v5 entry reds the pins file;
//! a v6 lookup moved off its offset reds the cross-derivation here.

use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::{observation_len, offsets, OBSERVATION_SCHEMA_VERSION};
use cloudkitty_rl::schema_map::{column_map, SchemaMapError};

#[test]
fn the_v6_map_is_the_live_encoder_by_name() {
    let m = column_map(6).expect("the current version has a map");
    assert_eq!(m.observation_version, OBSERVATION_SCHEMA_VERSION);
    let cfg = ObservationConfig::default();
    assert_eq!(m.observation_len, observation_len(&cfg), "derived, not restated");
    assert_eq!(
        m.slot_config,
        (cfg.kitty_slots, cfg.chow_slots, cfg.water_slots, cfg.sunbeam_slots, cfg.critter_slots),
        "the map describes the default slot config"
    );
    // Spot the derived cells against the offsets module (one source).
    assert_eq!(m.cell("self.identity_block").unwrap(), offsets::SELF_IDENTITY);
    assert_eq!(m.cell("self.waypoint_block").unwrap(), offsets::SELF_WAYPOINT);
    assert_eq!(m.cell("self.dirt_reserve_block").unwrap(), offsets::SELF_DIRT_RESERVE);
    assert_eq!(m.cell("kitty_row.bath").unwrap(), offsets::ROW_BATH);
    assert_eq!(m.cell("kitty_row.want_block").unwrap(), offsets::ROW_INTENSITY);
    assert_eq!(m.block("kitty_row").unwrap().base, offsets::SELF_BLOCK);
    assert_eq!(m.block("kitty_row").unwrap().stride, offsets::KITTY_SLOT);
    // Every block's cells stay inside the stride; blocks tile the vector.
    for b in m.blocks {
        for (name, rel) in m.cells.iter().filter(|(n, _)| n.starts_with(b.name)) {
            assert!(*rel < b.stride, "{name} inside {}", b.name);
        }
    }
    let last = m.blocks.last().unwrap();
    assert_eq!(last.base + last.count * last.stride, m.observation_len, "no clock cell after the blocks");
    // A v5-only name is not a v6 cell.
    assert!(m.cell("clock").is_err(), "v6 has no clock");
    assert!(m.cell("kitty_row.happiness").is_err(), "hidden fields have no cells");
}

#[test]
fn v5_lookups_reproduce_the_retired_layout_and_failures_are_loud() {
    let m = column_map(5).expect("the retired v5 map stays forever");
    // The reader-facing trio the Experiments flips start from.
    assert_eq!(m.cell("self.needs.eat").unwrap(), 0);
    assert_eq!(m.index("kitty_row", 0, "kitty_row.happiness").unwrap(), 85 + 10);
    assert_eq!(m.cell("clock").unwrap(), 407);
    // Loud failures, never defaults (FR-015).
    assert!(matches!(column_map(7), Err(SchemaMapError::UnknownSchemaVersion(7))));
    assert!(matches!(column_map(4), Err(SchemaMapError::UnknownSchemaVersion(4))));
    assert!(matches!(m.cell("self.wall.n"), Err(SchemaMapError::UnknownCell(_))), "a v6 name is not a v5 cell");
    assert!(matches!(
        column_map(6).unwrap().index("kitty_row", 9, "kitty_row.present"),
        Err(SchemaMapError::SlotOutOfRange { .. })
    ));
    assert!(matches!(m.block("nothing"), Err(SchemaMapError::UnknownBlock(_))));
}
