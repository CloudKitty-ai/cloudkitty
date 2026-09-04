//! The schema-5 pin (spec 049 SC-001 / FR-026 / FR-027): every derived
//! number asserted against the literals in
//! specs/049-fog-gen1/contracts/observation-v5.md.
//!
//! These are deliberately literal: the engine derives every one of these
//! numbers from the block constants, `HEAD_KINDS` and the slot config, so
//! a drive-by width move would shift them all silently. This file makes
//! any such move loud, and makes the contract's table executable. (The
//! schema-4 pins -- 225 / 34 / 50 / 3 slots -- were observed red at the
//! wall before this file replaced them: redden list, cycle 15.)

use cloudkitty_core::meow::MessageKind;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::global_state::GLOBAL_STATE_SCHEMA_VERSION;
use cloudkitty_rl::mask::MASK_SCHEMA_VERSION;
use cloudkitty_rl::observe::{
    observation_len, HEAD_KINDS, OBSERVATION_SCHEMA_VERSION, SCENE_AGE_NORMALISER,
    STALENESS_NORMALISER,
};

/// The whole derived chain, one assertion per contract row.
#[test]
fn the_schema_five_numbers_match_the_contract() {
    let cfg = ObservationConfig::default();

    assert_eq!(HEAD_KINDS.len(), 15, "fifteen speakable kinds, frozen");
    assert_eq!(
        MessageCodec::LEN,
        16,
        "message head: Silent + 15, unchanged"
    );
    assert_eq!(
        cfg.kitty_slots, 4,
        "FR-011: roster - 1, one permanent row per friend"
    );
    assert_eq!(
        observation_len(&cfg),
        408,
        "self 85 | kitty 4 x 63 | chow 2 x 5 | water 2 x 4 | sunbeam 2 x 6 | critter 4 x 10 | clock 1"
    );
    assert_eq!(
        ActionCodec::v2(&cfg).len(),
        39,
        "FR-027: 34 + one kitty-verb group for the fourth row"
    );

    assert_eq!(OBSERVATION_SCHEMA_VERSION, 5, "FR-025");
    assert_eq!(
        ACTION_SCHEMA_VERSION, 3,
        "unchanged: the menu is config-derived"
    );
    assert_eq!(MASK_SCHEMA_VERSION, 3, "unchanged");
    assert_eq!(
        GLOBAL_STATE_SCHEMA_VERSION, 1,
        "the critic's view is unfogged and unmoved"
    );

    assert_eq!(SCENE_AGE_NORMALISER, 24.0, "FR-019: H frozen");
    assert_eq!(STALENESS_NORMALISER, 40.0, "FR-009: 20 + 20 frozen");
}

/// The offset table (contract §Self block / §Kitty row) as LITERALS,
/// independent of the derivation (review 3 finding 3, 2026-09-04): the
/// row tests in `observe.rs` read their cells THROUGH these constants,
/// so a reordered block tail that keeps the width left the suite green and
/// silently reinterpreted every trained artifact's input. Seen red on an
/// induced self-tail swap (memory before the message block): redden
/// list, cycle r3b.
#[test]
fn the_offset_table_matches_the_contract() {
    use cloudkitty_rl::observe::{block_widths, offsets};
    assert_eq!(offsets::SELF_SCENE_AGE, 34, "own scene age");
    assert_eq!(offsets::SELF_MSG_BLOCK, 35, "own message block 35-64");
    assert_eq!(offsets::SELF_MEMORY, 65, "element memory 65-84");
    assert_eq!(offsets::SELF_BLOCK, 85, "self block");
    assert_eq!(offsets::ROW_WATER_BIT, 20, "neighbour in water");
    assert_eq!(
        offsets::ROW_SUNBEAM_BIT,
        21,
        "neighbour on a sunbeam (owner ruled 2026-09-04)"
    );
    assert_eq!(offsets::ROW_SCENE_AGE, 22, "their scene age");
    assert_eq!(offsets::ROW_MSG_BLOCK, 23, "their message block 23-52");
    assert_eq!(offsets::ROW_INTENSITY, 53, "want intensities 53-58");
    assert_eq!(offsets::ROW_ANSWERS_ME, 59, "answers-me 59-62");
    assert_eq!(offsets::KITTY_SLOT, 63, "kitty row");
    assert_eq!(offsets::MEMORY_BLOCK, 20, "5 kinds x 4");
    assert_eq!(offsets::MSG_BLOCK, 30, "15 kinds x 2");
    let w = block_widths();
    assert_eq!(
        (w.self_, w.kitty, w.chow, w.water, w.sunbeam, w.critter, w.clock),
        (85, 63, 5, 4, 6, 10, 1),
        "token widths"
    );
    assert_eq!(
        (w.memory, w.msg_self, w.msg_kitty),
        (20, 30, 40),
        "sub-block widths"
    );
}

/// The v3 forward's logit budget: dense 11, kitty-ptr 20 (5 verbs x 4),
/// critter-ptr 8 (2 x 4), message head 16 -- 55 in all. Asserted via the
/// codec (menu 39) and head rather than a hand sum, so the test derives
/// exactly as the forward does.
#[test]
fn the_logit_budget_is_fifty_five() {
    let cfg = ObservationConfig::default();
    let menu = ActionCodec::v2(&cfg).len();
    assert_eq!(
        menu + MessageCodec::LEN,
        55,
        "activity logits + message head"
    );
    assert_eq!(5 * cfg.kitty_slots, 20, "kitty-pointer logits");
    assert_eq!(2 * cfg.critter_slots, 8, "critter-pointer logits");
    assert_eq!(menu, 11 + 20 + 8, "dense + kitty-pointer + critter-pointer");
}

/// The mask is the two-head concat: menu 39 | message 16 = 55.
#[test]
fn the_mask_is_fifty_five_wide() {
    let cfg = ObservationConfig::default();
    assert_eq!(ActionCodec::v2(&cfg).len() + MessageCodec::LEN, 55);
}

/// T003 of spec 033, the rename pin: Mew answers for follow_me's position
/// with only the name changed. Head index 3 = HEAD_KINDS[2].
#[test]
fn mew_holds_follow_mes_exact_position() {
    assert_eq!(
        HEAD_KINDS[2],
        MessageKind::Mew,
        "head index 3 / message-block column 2, inherited byte-for-byte"
    );
    assert_eq!(MessageKind::Mew.wire_name(), "mew");
    assert_eq!(
        serde_json::to_string(&MessageKind::Mew).unwrap(),
        "\"mew\"",
        "the wire spelling is the serde spelling"
    );
}

/// The full contract order of the spec-033 tail, indices 9..=15 of the
/// head (array positions 8..=14) -- frozen through the fog era.
#[test]
fn the_new_kinds_sit_in_contract_order() {
    use MessageKind::*;
    assert_eq!(
        &HEAD_KINDS[8..],
        &[
            HereFood,
            HereWater,
            HereCritter,
            HereSunbeam,
            Chirp,
            Trill,
            Ekekek
        ],
        "append order is normative-forever (contract table)"
    );
    for (kind, wire) in [
        (HereFood, "here_food"),
        (HereWater, "here_water"),
        (HereCritter, "here_critter"),
        (HereSunbeam, "here_sunbeam"),
        (Chirp, "chirp"),
        (Trill, "trill"),
        (Ekekek, "ekekek"),
    ] {
        assert_eq!(kind.wire_name(), wire);
    }
}
