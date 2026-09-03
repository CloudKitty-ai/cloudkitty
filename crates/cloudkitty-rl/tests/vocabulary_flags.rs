//! Spec 033 US3 / FR-007 (T017): vocabulary flags gate LEGALITY, never
//! LAYOUT. Two configs differing only in flags produce byte-identical
//! observation and mask shapes; a disabled kind is masked off and never
//! emits; the schema pin means one shape per schema, whatever the flags say.

use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::Position;
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::test_support::test_world;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::mask::{legal_action_mask, legal_message_mask};
use cloudkitty_rl::observe::{encode_observation, observation_len, TargetTable, HEAD_KINDS};

#[test]
fn flags_never_move_a_single_layout_number() {
    let (mut world, mut config) = test_world();
    world.tick = 50;
    world.elements.clear();
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].pos = Position::new(8, 8);
    world.push_element(Element {
        id: 900,
        kind: ElementKind::Chow { servings: 3 },
        pos: Position::new(8, 9),
        ttl: None,
    });
    let cfg = ObservationConfig::default();
    let snapshot = world.snapshot().fog_for(1, config.vision.radius);
    let table = TargetTable::build(&snapshot, 1, &cfg);
    let codec = ActionCodec::v2(&cfg);

    let all_on_obs = encode_observation(&snapshot, 1, &config, &cfg, 0.0);
    let all_on_msg = legal_message_mask(&snapshot, 1, &config);
    let all_on_act = legal_action_mask(&snapshot, 1, &table, &codec, &config);
    assert!(
        all_on_msg[1 + HEAD_KINDS
            .iter()
            .position(|&k| k == MessageKind::HereFood)
            .unwrap()],
        "grounded and enabled: legal"
    );

    // Flip EVERY flag off (Silent needs no flag; the engine's word has none).
    config.meow.vocabulary = toml::from_str::<cloudkitty_core::config::VocabularyConfig>(
        "want_eat=false\nwant_drink=false\nmew=false\nwant_play=false\nwant_cuddle=false\n\
         purr=false\nwant_bath=false\nwant_sleep=false\nhere_food=false\nhere_water=false\n\
         here_critter=false\nhere_sunbeam=false\nchirp=false\ntrill=false\nekekek=false",
    )
    .unwrap();
    let all_off_obs = encode_observation(&snapshot, 1, &config, &cfg, 0.0);
    let all_off_msg = legal_message_mask(&snapshot, 1, &config);
    let all_off_act = legal_action_mask(&snapshot, 1, &table, &codec, &config);

    // LAYOUT: identical in every dimension.
    assert_eq!(all_on_obs.values.len(), all_off_obs.values.len());
    assert_eq!(all_on_obs.values.len(), observation_len(&cfg));
    assert_eq!(all_on_msg.len(), all_off_msg.len());
    assert_eq!(all_on_msg.len(), MessageCodec::LEN);
    assert_eq!(all_on_act.len(), all_off_act.len());

    // LEGALITY: every spoken word is off; Silent stands alone, structural.
    assert!(all_off_msg[0], "Silent is never flag-gated");
    assert!(
        all_off_msg[1..].iter().all(|&b| !b),
        "an all-off vocabulary silences every kind"
    );
    // The activity mask is not the vocabulary's business.
    assert_eq!(all_on_act, all_off_act, "flags never touch the menu");
    // And the OBSERVATION is identical too: flags are invisible to hearers'
    // shapes (a disabled kind's column simply stays zero because nothing
    // can ever emit it).
    assert_eq!(all_on_obs.values, all_off_obs.values);
}

#[test]
fn a_disabled_kind_never_emits_over_any_horizon() {
    // SC-001's flags-off half at the enforcement seam: the mask is false on
    // every tick, so the two-head policy can never select it and a direct
    // proposal downgrades (enforcement filters on the same function).
    let (mut world, mut config) = test_world();
    config.meow.vocabulary.here_food = false;
    world.tick = 10;
    world.elements.clear();
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].pos = Position::new(8, 8);
    world.push_element(Element {
        id: 901,
        kind: ElementKind::Chow { servings: 5 },
        pos: Position::new(8, 9),
        ttl: None,
    });
    for t in 10..60 {
        world.tick = t;
        let snapshot = world.snapshot().fog_for(1, config.vision.radius);
        let mask = legal_message_mask(&snapshot, 1, &config);
        let col = 1 + HEAD_KINDS
            .iter()
            .position(|&k| k == MessageKind::HereFood)
            .unwrap();
        assert!(!mask[col], "tick {t}: disabled means never-legal");
    }
}
