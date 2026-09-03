//! The 3.0 generation wall, engine side (spec 049 FR-032 / SC-006): a
//! pre-3.0 world snapshot does NOT load on this engine, and a 3.0 save
//! round-trips. Until spec 049 this file was the 028/041 wall's witness
//! the other way round -- two committed fixtures (`pre-028-world.json`,
//! `pre-041-bound-duet.json`) that loaded and ran through restore shims.
//! The owner ruled the shims and both fixture tests deleted with the wall
//! (timeline @ cefe5ba, item 5); what remains asserts the refusal, field
//! by field, so a silent default can never read a missing field into
//! state again.

use cloudkitty_core::Meow;

/// Spec 049 FR-032 (owner ruled 2026-09-03, item 6 -- the eighth shim):
/// a recorded meow needs every field; a missing `pos` or `reply` -- and,
/// once the pre-028 tolerance is deleted at T071, `intensity` -- fails to
/// deserialize NAMING the field. Intensity is an observed digest feature
/// and the reply ladder's tie-breaker under fog: reading 0.0 into it
/// would corrupt the digest instead of failing at load.
#[test]
fn a_pre_3_0_meow_entry_is_refused() {
    let complete = r#"{"kitty_id": 3, "kind": "want_play", "tick": 42, "intensity": 0.5,
                       "pos": {"x": 4, "y": 5}, "reply": false}"#;
    let meow: Meow = serde_json::from_str(complete).expect("a 3.0 entry loads");
    assert_eq!(meow.pos, cloudkitty_core::Position::new(4, 5));
    assert!(!meow.reply);

    for (missing, json) in [
        (
            "pos",
            r#"{"kitty_id": 3, "kind": "want_play", "tick": 42, "intensity": 0.5, "reply": false}"#,
        ),
        (
            "reply",
            r#"{"kitty_id": 3, "kind": "want_play", "tick": 42, "intensity": 0.5, "pos": {"x": 4, "y": 5}}"#,
        ),
    ] {
        let err = serde_json::from_str::<Meow>(json).unwrap_err().to_string();
        assert!(
            err.contains(missing),
            "an entry without `{missing}` is refused naming it: {err}"
        );
    }
}

/// Spec 049 FR-032: a pre-3.0 world save does not load. The concrete
/// witness is the shape the deleted `pre-028-world.json` fixture had -- a
/// kitty without the 3.0 fields -- refused naming the first missing one.
#[test]
fn a_pre_3_0_kitty_record_is_refused_naming_the_missing_field() {
    // A complete 3.0 kitty, serialized by this engine, loads back.
    let kitty = cloudkitty_core::Kitty::new(
        1,
        "Miso",
        cloudkitty_core::Position::new(2, 3),
        "needs_driven",
    );
    let text = serde_json::to_string(&kitty).unwrap();
    let back: cloudkitty_core::Kitty =
        serde_json::from_str(&text).expect("a 3.0 kitty round-trips");
    assert_eq!(back, kitty);

    // Strip one 3.0 field at a time: each absence is refused by name.
    let value: serde_json::Value = serde_json::from_str(&text).unwrap();
    for field in [
        "memory",
        "explore_heading",
        "announce_armed",
        "last_action",
        "purr_cooldown_until",
        "behavior_description",
        "purring_until",
        "purring_duration",
    ] {
        let mut stripped = value.clone();
        stripped
            .as_object_mut()
            .unwrap()
            .remove(field)
            .unwrap_or_else(|| panic!("{field} is serialized"));
        let err = serde_json::from_value::<cloudkitty_core::Kitty>(stripped)
            .unwrap_err()
            .to_string();
        assert!(
            err.contains(field),
            "a save without `{field}` is refused naming it: {err}"
        );
    }
}
