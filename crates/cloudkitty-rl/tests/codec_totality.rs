//! Codec-totality proptest (spec 014 FR-006, T019): every in-range index
//! decodes to a proposal — vacant and stale slots included, never an error —
//! and encode inverts decode for every expressible action.

use cloudkitty_rl::codec::{ActionCodec, CodecError, VACANT_ELEMENT, VACANT_KITTY};
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::TargetTable;
use proptest::prelude::*;

fn arb_table() -> impl Strategy<Value = TargetTable> {
    let kitty_slot = prop_oneof![Just(None), (2u32..40).prop_map(Some)];
    let critter_slot = prop_oneof![Just(None), (100u32..200).prop_map(Some)];
    (
        prop::collection::vec(kitty_slot, 3),
        prop::collection::vec(critter_slot, 4),
    )
        .prop_map(|(mut kitties, mut critters)| {
            // Slot identities are unique by construction in real tables.
            dedup_in_place(&mut kitties);
            dedup_in_place(&mut critters);
            TargetTable { kitties, critters }
        })
}

fn dedup_in_place<T: PartialEq + Copy>(slots: &mut [Option<T>]) {
    for i in 0..slots.len() {
        if let Some(v) = slots[i] {
            for later in slots.iter_mut().skip(i + 1) {
                if *later == Some(v) {
                    *later = None;
                }
            }
        }
    }
}

proptest! {
    #[test]
    fn every_index_decodes_and_expressible_actions_round_trip(table in arb_table()) {
        let codec = ActionCodec::v1(&ObservationConfig::default());
        prop_assert_eq!(codec.len(), 40);

        for index in 0..codec.len() {
            let action = codec.decode(index, &table).expect("in-range decodes are total");
            match codec.encode(&action, &table) {
                // Round trip: the same index comes back.
                Some(encoded) => prop_assert_eq!(encoded, index),
                // Only vacant-slot decodes are inexpressible back.
                None => {
                    let json = serde_json::to_string(&action).unwrap();
                    prop_assert!(
                        json.contains(&VACANT_KITTY.to_string())
                            || json.contains(&VACANT_ELEMENT.to_string()),
                        "{} decoded to {:?} which failed to re-encode",
                        index,
                        action
                    );
                }
            }
        }

        // Out of range is an error, never a panic.
        let over = matches!(codec.decode(40, &table), Err(CodecError::OutOfRange { .. }));
        prop_assert!(over);
        let way_over = matches!(
            codec.decode(usize::MAX, &table),
            Err(CodecError::OutOfRange { .. })
        );
        prop_assert!(way_over);
    }
}
