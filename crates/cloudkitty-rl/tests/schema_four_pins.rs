//! The schema-4 pin (spec 033, T002/T003): every derived width asserted
//! against the literals in specs/033-say-surface/contracts/say-surface-v3.md.
//!
//! These are deliberately literal: the engine derives every one of these
//! numbers from `HEAD_KINDS` and the slot config, so a drive-by kind
//! addition would move them all silently. This file makes any such move
//! loud, and makes the contract's table executable.

use cloudkitty_core::meow::MessageKind;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::mask::MASK_SCHEMA_VERSION;
use cloudkitty_rl::observe::{observation_len, HEAD_KINDS, OBSERVATION_SCHEMA_VERSION};

/// The whole derived chain, one assertion per contract row.
#[test]
fn the_schema_four_numbers_match_the_contract() {
    let cfg = ObservationConfig::default();

    assert_eq!(HEAD_KINDS.len(), 15, "fifteen speakable kinds");
    assert_eq!(MessageCodec::LEN, 16, "message head: Silent + 15");
    assert_eq!(
        observation_len(&cfg),
        225,
        "served observation: 197 + 7 new digest kinds x 4"
    );
    assert_eq!(cfg.kitty_slots, 3, "FR-011: slots are a schema constant");
    assert_eq!(
        ActionCodec::v2(&cfg).len(),
        34,
        "FR-009: the activity menu does not move at this wall"
    );

    assert_eq!(OBSERVATION_SCHEMA_VERSION, 4);
    assert_eq!(ACTION_SCHEMA_VERSION, 3);
    assert_eq!(MASK_SCHEMA_VERSION, 3);
}

/// The v3 forward's logit budget: dense 11 + kitty-ptr 15 + critter-ptr 8
/// plus message head 16 = 50. Asserted via the codec (menu 34) and head
/// rather than a hand sum, so the test derives exactly as the forward does.
#[test]
fn the_logit_budget_is_fifty() {
    let cfg = ObservationConfig::default();
    let menu = ActionCodec::v2(&cfg).len();
    assert_eq!(
        menu + MessageCodec::LEN,
        50,
        "activity logits + message head"
    );
}

/// T003, the rename pin: Mew answers for follow_me's position with only
/// the name changed. Head index 3 = HEAD_KINDS[2]; digest column 2 is the
/// same array position (digest columns ARE head-kind order).
#[test]
fn mew_holds_follow_mes_exact_position() {
    assert_eq!(
        HEAD_KINDS[2],
        MessageKind::Mew,
        "head index 3 / digest column 2, inherited byte-for-byte"
    );
    assert_eq!(MessageKind::Mew.wire_name(), "mew");
    assert_eq!(
        serde_json::to_string(&MessageKind::Mew).unwrap(),
        "\"mew\"",
        "the wire spelling is the serde spelling"
    );
}

/// The full contract order of the new tail, indices 9..=15 of the head
/// (array positions 8..=14).
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
