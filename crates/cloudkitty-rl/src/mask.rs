//! Legal-action mask v1 (spec 014 FR-018, versioned with the codec).
//!
//! One bit per menu entry: set iff that entry, proposed as the world stood
//! at the frozen start-of-tick snapshot, **would be applied as proposed** at
//! the kitty's apply slot. The verdict is computed by replaying the apply
//! slot's exact engine sequence on a probe world reconstructed from the
//! snapshot: counterpart pruning, then validation, then the duration
//! enforcement verdict — the engine's own code, never a reimplementation
//! (FR-007), guarded by the pure-oracle property test.
//!
//! "Applied as proposed" is an *outcome* claim: inside an activity's
//! minimum, every entry rewrites to the exact continuation, so the mask
//! reduces to that continuation's own entry — including the corner where
//! the continuation itself fails validation (a co-sleep friend who has
//! wandered off) but enforcement still applies it verbatim.
//!
//! **Never all-zero — structural** (amended FR-018): target-priority slot
//! ordering keeps every activity's referenced entity in its table, so the
//! continuation is always expressible; untargeted continuations are
//! untargeted entries; outside activities the idle bit is genuinely legal.
//!
//! **Advisory**: legality speaks to the frozen snapshot; within-tick
//! contention stays the engine's to resolve. Necessary, never sufficient.

use cloudkitty_core::action;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::meow::message_legal;
use cloudkitty_core::world::{World, WorldSnapshot};
use cloudkitty_core::Config;

use crate::codec::ActionCodec;
use crate::observe::{TargetTable, HEAD_KINDS};

/// Versioned with the codec. Schema 2 (spec 028, encodings-v2.md): the
/// serialized wire is one vector, `[activity mask (menu_len) | message
/// mask (9)]` -- 43 at default slots. Both halves are pure oracles over
/// engine law; neither is ever all-zero (activity: FR-018 structural;
/// message: Silent always legal).
pub const MASK_SCHEMA_VERSION: u32 = 2;

/// Computes the legal-action mask for `kitty_id` against the frozen
/// snapshot. One bool per menu entry, in menu order.
pub fn legal_action_mask(
    snapshot: &WorldSnapshot,
    kitty_id: KittyId,
    table: &TargetTable,
    codec: &ActionCodec,
    config: &Config,
) -> Vec<bool> {
    let mut probe = World::from_snapshot(snapshot);
    // The apply slot's first act: an activity whose counterpart is gone ends
    // before the proposal gets its hearing (spec 006 FR-010).
    probe.prune_dead_activity(kitty_id);
    (0..codec.len())
        .map(|index| {
            let proposal = codec
                .decode(index, table)
                .expect("in-range menu indices always decode");
            let validated = action::validate(&probe, kitty_id, proposal, config);
            let applied = probe.enforcement_verdict(kitty_id, &validated, config);
            applied == proposal
        })
        .collect()
}

/// The legal-message mask for `kitty_id` (spec 028): one bool per head
/// index -- 0 (Silent) always true, k+1 probes the engine's own
/// `message_legal` for `HEAD_KINDS[k]`. The same no-reimplementation
/// doctrine as the activity mask: the ruling is the engine's function,
/// called, never copied.
pub fn legal_message_mask(
    snapshot: &WorldSnapshot,
    kitty_id: KittyId,
    config: &Config,
) -> Vec<bool> {
    let mut mask = vec![false; 1 + HEAD_KINDS.len()];
    mask[0] = true; // Silence is always legal -- structural, never all-zero.
    if let Some(kitty) = snapshot.kitty(kitty_id) {
        for (k, &kind) in HEAD_KINDS.iter().enumerate() {
            mask[k + 1] = message_legal(kitty, kind, snapshot.tick, config);
        }
    }
    mask
}

/// The mask as bytes (0/1), the shape the Python surface exposes.
pub fn mask_bytes(mask: &[bool]) -> Vec<u8> {
    mask.iter().map(|&b| u8::from(b)).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::ObservationConfig;
    use crate::observe::TargetTable;
    use cloudkitty_core::action::Action;
    use cloudkitty_core::kitty::{Activity, ActivityClock};
    use cloudkitty_core::test_support::test_world;

    #[test]
    fn an_idle_kitty_has_idle_and_solo_entries_legal() {
        let (world, config) = test_world();
        let snapshot = world.snapshot();
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        let table = TargetTable::build(&snapshot, 1, &cfg);

        let mask = legal_action_mask(&snapshot, 1, &table, &codec, &config);
        assert_eq!(mask.len(), 34, "menu v2: the meow rows are gone");
        assert!(mask[33], "idle (renumbered, spec 028) is genuinely legal");
        assert!(mask[4], "solo rest is always legal");
        assert!(mask[12], "self-groom is always legal");
        assert!(mask[25], "solo play is always legal");
        assert!(mask.iter().filter(|&&b| b).count() >= 4);
    }

    #[test]
    fn inside_the_minimum_the_mask_reduces_to_the_exact_continuation() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].activity = Activity::Sleeping {
            in_sunbeam: false,
            with_friend: None,
        };
        // Clock started this tick: zero ticks serviced, minimum not met.
        world.kitties[idx].activity_clock = Some(ActivityClock::start(world.tick));

        let snapshot = world.snapshot();
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        let table = TargetTable::build(&snapshot, 1, &cfg);
        let mask = legal_action_mask(&snapshot, 1, &table, &codec, &config);

        let set: Vec<usize> = (0..mask.len()).filter(|&i| mask[i]).collect();
        assert_eq!(set, vec![8], "exactly the solo-sleep continuation");
        assert_eq!(
            codec.decode(8, &table).unwrap(),
            Action::Sleep { with: None }
        );
    }

    #[test]
    fn the_mask_is_never_all_zero_for_a_fresh_world() {
        let (world, config) = test_world();
        let snapshot = world.snapshot();
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        for kitty in &snapshot.kitties {
            let table = TargetTable::build(&snapshot, kitty.id, &cfg);
            let mask = legal_action_mask(&snapshot, kitty.id, &table, &codec, &config);
            assert!(mask.iter().any(|&b| b), "kitty {} all-zero", kitty.id);
        }
    }
}
