//! The schema-5 oracle (spec 049 SC-001 / FR-026 / FR-027, converted by
//! spec 058 T004): every v5 number asserted as a LITERAL against
//! `schema_map::column_map(5)`, decoupled from the live encoder so the
//! Gen 2 bump (observation v6) can move the encoder without silently
//! dragging this oracle along. The literals are the contract's table
//! (specs/049-fog-gen1/contracts/observation-v5.md); the map is the
//! shipped copy readers flip onto; this file is what keeps the two
//! identical. (History: the schema-4 pins were observed red at the
//! schema-5 wall; the live-offset form of THIS file was retired at the
//! v6 wall for the same reason — a live read follows the encoder and
//! pins nothing.)
//!
//! Evergreen pins (message-kind order, codec sizes, action/mask
//! versions) stay live: they are frozen-through-the-fog-era claims that
//! v6 must also satisfy, so a red here at the bump is a REAL violation.

use cloudkitty_core::meow::MessageKind;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::mask::MASK_SCHEMA_VERSION;
use cloudkitty_rl::observe::HEAD_KINDS;
use cloudkitty_rl::schema_map::column_map;

/// The v5 top-line numbers, as map literals vs contract literals.
#[test]
fn the_schema_five_numbers_match_the_contract() {
    let m = column_map(5).expect("v5 map exists forever");
    assert_eq!(m.observation_version, 5, "FR-025");
    assert_eq!(
        m.observation_len,
        408,
        "self 85 | kitty 4 x 63 | chow 2 x 5 | water 2 x 4 | sunbeam 2 x 6 | critter 4 x 10 | clock 1"
    );
    assert_eq!(m.slot_config, (4, 2, 2, 2, 4), "the served slot defaults");
    assert_eq!(HEAD_KINDS.len(), 15, "fifteen speakable kinds, frozen");
    assert_eq!(
        MessageCodec::LEN,
        16,
        "message head: Silent + 15, unchanged"
    );
}

/// The v5 offset table (contract §Self block / §Kitty row / §Element
/// slots) as literals, every named map entry pinned. A reordered table
/// or a transposed base reds exactly one named line.
#[test]
fn the_offset_table_matches_the_contract() {
    let m = column_map(5).expect("v5 map exists forever");

    // Self block, absolute.
    for (name, at) in [
        ("self.needs.eat", 0),
        ("self.needs.bath", 5),
        ("self.happiness", 6),
        ("self.pos.x", 7),
        ("self.pos.y", 8),
        ("self.activity_block", 9),
        ("self.social", 16),
        ("self.in_sunbeam", 17),
        ("self.in_water", 18),
        ("self.progress", 19),
        ("self.distress_block", 20),
        ("self.pursuit_block", 26),
        ("self.traits_block", 28),
        ("self.scene_age", 34),
        ("self.msg_block", 35),
        ("self.memory_block", 65),
        ("clock", 407),
    ] {
        assert_eq!(m.cell(name).unwrap(), at, "{name}");
    }

    // Kitty row, stride-relative (spec 049 row order).
    for (name, at) in [
        ("kitty_row.present", 0),
        ("kitty_row.dx", 1),
        ("kitty_row.dy", 2),
        ("kitty_row.distance", 3),
        ("kitty_row.needs.eat", 4),
        ("kitty_row.needs.bath", 9),
        ("kitty_row.happiness", 10),
        ("kitty_row.activity_block", 11),
        ("kitty_row.partner", 18),
        ("kitty_row.is_my_target", 19),
        ("kitty_row.in_water", 20),
        ("kitty_row.on_sunbeam", 21),
        ("kitty_row.scene_age", 22),
        ("kitty_row.msg_block", 23),
        ("kitty_row.want_block", 53),
        ("kitty_row.answers_me_block", 59),
    ] {
        assert_eq!(m.cell(name).unwrap(), at, "{name}");
    }

    // Blocks: base / stride / count.
    for (name, base, stride, count) in [
        ("kitty_row", 85, 63, 4),
        ("chow", 337, 5, 2),
        ("water", 347, 4, 2),
        ("sunbeam", 355, 6, 2),
        ("critter", 367, 10, 4),
    ] {
        let b = m.block(name).unwrap();
        assert_eq!((b.base, b.stride, b.count), (base, stride, count), "{name}");
    }

    // Element extras.
    assert_eq!(m.cell("chow.servings").unwrap(), 4);
    assert_eq!(m.cell("sunbeam.ttl").unwrap(), 4);
    assert_eq!(m.cell("sunbeam.occupied").unwrap(), 5);
    assert_eq!(m.cell("critter.is_greeble").unwrap(), 4);
    assert_eq!(m.cell("critter.heading_block").unwrap(), 5);
    assert_eq!(m.cell("critter.is_activity_target").unwrap(), 9);

    // Resolution: base + slot*stride + rel, and the loud failure modes.
    assert_eq!(
        m.index("kitty_row", 2, "kitty_row.happiness").unwrap(),
        85 + 2 * 63 + 10
    );
    assert!(
        m.cell("self.waypoint_block").is_err(),
        "a v6 name is not a v5 cell"
    );
    assert!(
        m.index("kitty_row", 4, "kitty_row.present").is_err(),
        "slot past count"
    );
    assert!(column_map(4).is_err(), "retired pre-5 versions have no map");
}

/// The v5-ERA slot config, pinned explicitly: the live default moved
/// to critter_slots 2 (owner ruled 2026-10-09), but every schema-5
/// artifact was built at 4 — this historical cfg is what the v5 map's
/// numbers describe.
fn v5_era_cfg() -> ObservationConfig {
    ObservationConfig {
        critter_slots: 4,
        ..ObservationConfig::default()
    }
}

/// The v5-era v3 forward's logit budget: dense 11, kitty-ptr 20
/// (5 verbs x 4), critter-ptr 8 (2 x 4), message head 16 -- 55 in all,
/// at the v5-era slot config.
#[test]
fn the_v5_era_logit_budget_was_fifty_five() {
    let cfg = v5_era_cfg();
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

/// Action and mask schemas hold at 3 across the v6 bump AND the
/// critter-slot cut (spec 058 FR-014: only moved layouts bump; the menu
/// is config-derived, so a slot-count change is config, never a schema
/// version).
#[test]
fn action_and_mask_versions_hold() {
    assert_eq!(
        ACTION_SCHEMA_VERSION, 3,
        "unchanged: the menu is config-derived"
    );
    assert_eq!(MASK_SCHEMA_VERSION, 3, "unchanged");
    assert_eq!(
        ActionCodec::v2(&v5_era_cfg()).len(),
        39,
        "the v5-era menu (FR-027 of 049)"
    );
    assert_eq!(
        ActionCodec::v2(&ObservationConfig::default()).len(),
        35,
        "the live menu at critter_slots 2 (owner ruled 2026-10-09)"
    );
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
