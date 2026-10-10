//! The schema-6 pin (spec 058 FR-016 / SC-007, the 049 discipline):
//! every derived number asserted against the literals in
//! specs/058-gen2-observation-schema/contracts/observation-v6.md. The
//! engine derives every one of these from the block constants and the
//! slot config, so a drive-by width move would shift them all silently;
//! this file makes any such move loud and makes the contract's table
//! executable. (The schema-5 pins were observed red at this wall before
//! their conversion to the map oracle — spec 058 pre-bump red probe.)

use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::global_state::GLOBAL_STATE_SCHEMA_VERSION;
use cloudkitty_rl::observe::{
    block_widths, observation_len, offsets, FAR_DISTANCE_NORMALISER, NEAR_DISTANCE_NORMALISER,
    OBSERVATION_SCHEMA_VERSION, SCENE_AGE_NORMALISER, STALENESS_NORMALISER,
};

/// The top-line v6 numbers, one assertion per contract row.
#[test]
fn the_schema_six_numbers_match_the_contract() {
    let cfg = ObservationConfig::default();
    assert_eq!(OBSERVATION_SCHEMA_VERSION, 6, "FR-014");
    assert_eq!(GLOBAL_STATE_SCHEMA_VERSION, 2, "FR-009: the critic sees the dials");
    let w = block_widths();
    assert_eq!(
        (w.self_, w.kitty, w.chow, w.water, w.sunbeam, w.critter, w.clock),
        (109, 58, 6, 5, 7, 11, 0),
        "token widths: identity +8, walls +4 -2 pos, memory 5x6, waypoint 2, reserve 2 | row -6 hidden +1 spatial | slots +1 | no clock"
    );
    assert_eq!(
        observation_len(&cfg),
        421,
        "self 109 | kitty 4 x 58 | chow 2 x 6 | water 2 x 5 | sunbeam 2 x 7 | critter 4 x 11 | no clock"
    );
    assert_eq!((w.memory, w.msg_self, w.msg_kitty), (30, 30, 40), "sub-block widths");
    // The frozen normalizers ARE the schema (FR-002; the 049 pattern).
    assert_eq!(NEAR_DISTANCE_NORMALISER, 40.0, "walk-cost near field");
    assert_eq!(FAR_DISTANCE_NORMALISER, 400.0, "log far field");
    assert_eq!(SCENE_AGE_NORMALISER, 24.0, "FR-004: untouched");
    assert_eq!(STALENESS_NORMALISER, 40.0, "FR-004: untouched");
}

/// The offset table (contract §Self block / §Kitty row) as LITERALS: the
/// row tests read cells through these constants, so a reordered block
/// tail that keeps the width must fail HERE by number (the schema-5
/// review-3 lesson carried forward).
#[test]
fn the_offset_table_matches_the_contract() {
    assert_eq!(offsets::SELF_WALLS, 7, "walls N/E/S/W 7-10");
    assert_eq!(offsets::SELF_IDENTITY, 30, "identity block 30-43");
    assert_eq!(offsets::SELF_SCENE_AGE, 44, "own scene age");
    assert_eq!(offsets::SELF_MSG_BLOCK, 45, "own message block 45-74");
    assert_eq!(offsets::SELF_MEMORY, 75, "element memory 75-104");
    assert_eq!(offsets::SELF_WAYPOINT, 105, "waypoint bearing 105-106");
    assert_eq!(offsets::SELF_DIRT_RESERVE, 107, "dirt reserve 107-108");
    assert_eq!(offsets::SELF_BLOCK, 109, "self block");
    assert_eq!(offsets::ROW_BATH, 5, "bath: the one visible need");
    assert_eq!(offsets::ROW_WATER_BIT, 15, "neighbour in water");
    assert_eq!(offsets::ROW_SUNBEAM_BIT, 16, "neighbour on a sunbeam");
    assert_eq!(offsets::ROW_SCENE_AGE, 17, "their scene age");
    assert_eq!(offsets::ROW_MSG_BLOCK, 18, "their message block 18-47");
    assert_eq!(offsets::ROW_INTENSITY, 48, "want intensities 48-53");
    assert_eq!(offsets::ROW_ANSWERS_ME, 54, "answers-me 54-57");
    assert_eq!(offsets::KITTY_SLOT, 58, "kitty row");
    assert_eq!(offsets::MEMORY_BLOCK, 30, "5 kinds x 6");
    assert_eq!(offsets::MSG_BLOCK, 30, "15 kinds x 2");
}
