//! Spec 058 SC-002, the leak-audit property (FR-005/FR-006/FR-007a):
//! two encodes differing ONLY in a friend's hidden fields (the five
//! non-bath needs, happiness, distress) produce IDENTICAL observations;
//! bath differs in exactly its one row cell; the observer's own block
//! keeps its full state. Observed RED under the v5 encoder (hunger and
//! happiness cells leaked) in the spec-058 pre-bump probe.

use std::sync::Arc;

use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::{encode_observation, offsets};

fn set_need(w: &mut World, id: u32, kind: NeedKind, value: f32) {
    let i = w.kitty_index(id).unwrap();
    let cur = w.kitties[i].needs.get(kind);
    w.kitties[i].needs.add(kind, value - cur);
}

/// Encode observer 1's view with friend 2's state set per the closure.
fn encode_with(setup: impl FnOnce(&mut World)) -> Vec<f32> {
    let c = Arc::new(test_config());
    let mut w = World::generate(&c);
    w.elements.clear();
    cloudkitty_core::test_support::forget_everything(&mut w);
    let i = w.kitty_index(2).unwrap();
    w.kitties[i].pos = cloudkitty_core::grid::Position::new(4, 4);
    setup(&mut w);
    let view = w.snapshot().fog_for(1, c.vision.radius);
    assert!(view.kitty(2).is_some(), "friend 2 is seen");
    encode_observation(&view, 1, &c, &ObservationConfig::default()).values
}

#[test]
fn hidden_friend_fields_cannot_reach_any_cell() {
    // A deterministic sweep in place of rand: every hidden need at an
    // extreme, happiness and distress with it. If ANY cell moves, a
    // hidden field leaked (the v5 red: the row's need cells moved).
    let quiet = encode_with(|w| {
        for kind in [
            NeedKind::Eat,
            NeedKind::Drink,
            NeedKind::Sleep,
            NeedKind::Play,
            NeedKind::Cuddle,
        ] {
            set_need(w, 2, kind, 5.0);
        }
        let i = w.kitty_index(2).unwrap();
        w.kitties[i].happiness = 90.0;
        w.kitties[i].in_distress.clear();
    });
    let desperate = encode_with(|w| {
        for kind in [
            NeedKind::Eat,
            NeedKind::Drink,
            NeedKind::Sleep,
            NeedKind::Play,
            NeedKind::Cuddle,
        ] {
            set_need(w, 2, kind, 95.0);
        }
        let i = w.kitty_index(2).unwrap();
        w.kitties[i].happiness = 8.0;
        w.kitties[i].in_distress = [cloudkitty_core::needs::NeedKind::Eat].into_iter().collect();
    });
    assert_eq!(
        quiet, desperate,
        "five-of-six: no cell anywhere carries a friend's hidden needs, happiness or distress"
    );
}

#[test]
fn bath_moves_exactly_one_row_cell() {
    let clean = encode_with(|w| set_need(w, 2, NeedKind::Bath, 10.0));
    let scruffy = encode_with(|w| set_need(w, 2, NeedKind::Bath, 80.0));
    let diff: Vec<usize> = (0..clean.len()).filter(|&i| clean[i] != scruffy[i]).collect();
    let bath_cell = offsets::SELF_BLOCK + offsets::ROW_BATH;
    assert_eq!(
        diff,
        vec![bath_cell],
        "bath (the ruled visible control) reaches its one row cell and nothing else"
    );
    assert_eq!(scruffy[bath_cell], 0.8, "bath /100");
}

#[test]
fn own_state_stays_fully_visible() {
    // FR-007: hiding applies to knowledge of OTHERS only — the
    // observer's own needs and happiness move its own cells.
    let hungry = encode_with(|w| set_need(w, 1, NeedKind::Eat, 95.0));
    let fed = encode_with(|w| set_need(w, 1, NeedKind::Eat, 5.0));
    assert_eq!(hungry[0], 0.95, "own hunger /100, cell 0");
    assert_eq!(fed[0], 0.05);
}
