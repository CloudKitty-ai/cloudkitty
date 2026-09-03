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
use cloudkitty_core::world::{FogView, World};
use cloudkitty_core::Config;

use crate::codec::ActionCodec;
use crate::observe::{TargetTable, HEAD_KINDS};

/// Versioned with the codec. Schema 2 (spec 028, encodings-v2.md): the
/// serialized wire is one vector, `[activity mask (menu_len) | message
/// mask]` -- both halves pure oracles over engine law; neither is ever
/// all-zero (activity: FR-018 structural; message: Silent always legal).
/// Schema 3 (spec 033): the message half widened 9 → 16 with the
/// say-surface (50 total at default slots); the activity half is
/// unchanged.
pub const MASK_SCHEMA_VERSION: u32 = 3;

/// Computes the legal-action mask for `kitty_id` against its frozen fog
/// view (spec 049 research R2: the mask encodes no knowledge the
/// observation lacks; every menu action is local, so the verdicts equal
/// the full snapshot's -- `mask_oracle` proves it). One bool per menu
/// entry, in menu order.
pub fn legal_action_mask(
    view: &FogView,
    kitty_id: KittyId,
    table: &TargetTable,
    codec: &ActionCodec,
    config: &Config,
) -> Vec<bool> {
    let mut probe = World::from_snapshot(&view.snapshot);
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
pub fn legal_message_mask(view: &FogView, kitty_id: KittyId, config: &Config) -> Vec<bool> {
    let mut mask = vec![false; 1 + HEAD_KINDS.len()];
    mask[0] = true; // Silence is always legal -- structural, never all-zero.
    if let Some(kitty) = view.kitty(kitty_id) {
        for (k, &kind) in HEAD_KINDS.iter().enumerate() {
            mask[k + 1] = message_legal(kitty, kind, view.tick, config, view);
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
        let snapshot = world.snapshot().fog_for(1, config.vision.radius);
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        let table = TargetTable::build(&snapshot, 1, &cfg);

        let mask = legal_action_mask(&snapshot, 1, &table, &codec, &config);
        assert_eq!(mask.len(), 39, "menu v2 at kitty_slots 4 (spec 049)");
        assert!(
            mask[38],
            "idle (last row; 33 at kitty_slots 3) is genuinely legal"
        );
        assert!(mask[4], "solo rest is always legal");
        assert!(mask[14], "self-groom is always legal");
        assert!(mask[29], "solo play is always legal");
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

        let snapshot = world.snapshot().fog_for(1, config.vision.radius);
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        let table = TargetTable::build(&snapshot, 1, &cfg);
        let mask = legal_action_mask(&snapshot, 1, &table, &codec, &config);

        let set: Vec<usize> = (0..mask.len()).filter(|&i| mask[i]).collect();
        assert_eq!(set, vec![9], "exactly the solo-sleep continuation");
        assert_eq!(
            codec.decode(9, &table).unwrap(),
            Action::Sleep { with: None }
        );
    }

    /// Spec 045 FR-007 (armed case): the membership dial moves PRICES,
    /// never legality. A cat charged by the bidirectional rule holds the
    /// exact legal-action and legal-message masks of its uncharged twin
    /// in the option_a world at the same tick — the divergence guard
    /// first proves the twins really did diverge on bath (the charge
    /// landed), so mask equality is measured across a real charge, not
    /// two identical worlds.
    #[tokio::test(flavor = "current_thread")]
    async fn contagion_membership_and_its_charge_never_move_the_mask() {
        use cloudkitty_core::behavior::test_behaviors::AlwaysInvalid;
        use cloudkitty_core::config::ContagionMembership;
        use cloudkitty_core::element::{Element, ElementKind};
        use cloudkitty_core::grid::Position;
        use cloudkitty_core::test_support::test_config;
        use cloudkitty_core::{BehaviorRegistry, ElementType, NeedKind, World};
        use std::sync::Arc;

        async fn charged_world(
            membership: ContagionMembership,
        ) -> (World, Arc<cloudkitty_core::Config>) {
            let mut config = test_config();
            config.kitties[0].behavior = "always_invalid".into();
            config.kitties[1].behavior = "always_invalid".into();
            config.water.contagion_factor = 1.0;
            config.water.contagion_membership = membership;
            config.validate().expect("test config must be legal");
            let config = Arc::new(config);
            let mut world = World::generate(&config);
            world
                .elements
                .retain(|el| el.element_type() != ElementType::Water);
            world.elements.push(Element {
                id: 9_900,
                kind: ElementKind::Water,
                pos: Position::new(8, 8),
                ttl: None,
            });
            // The wet cat rests naming the dry adjacent cat — the 045
            // referenced-role scene: charged under bidirectional only.
            let b = world.kitty_index(2).unwrap();
            world.kitties[b].pos = Position::new(8, 8);
            let cuddle = world.kitties[b].needs.get(NeedKind::Cuddle);
            world.kitties[b].needs.add(NeedKind::Cuddle, 50.0 - cuddle);
            world.kitties[b].activity = Activity::Resting {
                with_friend: Some(1),
            };
            world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].pos = Position::new(8, 9);
            let mut registry = BehaviorRegistry::with_builtins();
            registry.register("always_invalid", Arc::new(AlwaysInvalid));
            world.tick(&registry, &config).await;
            (world, config)
        }

        let (bidi, bidi_cfg) = charged_world(ContagionMembership::Bidirectional).await;
        let (opta, opta_cfg) = charged_world(ContagionMembership::OptionA).await;
        let charged = bidi.kitty(1).unwrap().needs.get(NeedKind::Bath);
        let uncharged = opta.kitty(1).unwrap().needs.get(NeedKind::Bath);
        assert!(
            charged > uncharged + 1.0,
            "the twins must diverge on bath before mask equality means \
             anything: bidirectional {charged} vs option_a {uncharged}"
        );

        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        for id in [1, 2] {
            let sb = bidi.snapshot().fog_for(id, bidi_cfg.vision.radius);
            let sa = opta.snapshot().fog_for(id, opta_cfg.vision.radius);
            let mb = legal_action_mask(
                &sb,
                id,
                &TargetTable::build(&sb, id, &cfg),
                &codec,
                &bidi_cfg,
            );
            let ma = legal_action_mask(
                &sa,
                id,
                &TargetTable::build(&sa, id, &cfg),
                &codec,
                &opta_cfg,
            );
            assert_eq!(
                mb, ma,
                "kitty {id}: the membership dial moved the legal-action \
                 mask (FR-007)"
            );
            assert_eq!(
                legal_message_mask(&sb, id, &bidi_cfg),
                legal_message_mask(&sa, id, &opta_cfg),
                "kitty {id}: the membership dial moved the message mask \
                 (FR-007)"
            );
        }
    }

    /// Spec 045 FR-007 armed case (T025, Article IV): the charge-aware
    /// ladder changes only PROPOSALS. The masks are computed against ONE
    /// exposed world's snapshot under the gate-on and gate-off CONFIGS —
    /// the sharp form of "the bool never leaks into legality"
    /// (medium-review test hygiene: the earlier twin-worlds form was
    /// vacuous under `always_invalid` cats, whose worlds cannot diverge
    /// on the gate; the config is the only input that varies here, so
    /// any legality read of the gate reds this directly — proven by the
    /// recorded fake-hook injection).
    #[tokio::test(flavor = "current_thread")]
    async fn the_ladder_gate_never_moves_the_mask() {
        use cloudkitty_core::behavior::test_behaviors::AlwaysInvalid;
        use cloudkitty_core::config::ContagionMembership;
        use cloudkitty_core::element::{Element, ElementKind};
        use cloudkitty_core::grid::Position;
        use cloudkitty_core::test_support::test_config;
        use cloudkitty_core::{BehaviorRegistry, ElementType, World};
        use std::sync::Arc;

        async fn exposed_world(ladder: bool) -> (World, Arc<cloudkitty_core::Config>) {
            let mut config = test_config();
            config.kitties[0].behavior = "always_invalid".into();
            config.kitties[1].behavior = "always_invalid".into();
            config.water.contagion_factor = 1.0;
            config.water.contagion_membership = ContagionMembership::Bidirectional;
            config.behavior.contagion_aware_ladder = ladder;
            config.validate().expect("test config must be legal");
            let config = Arc::new(config);
            let mut world = World::generate(&config);
            world
                .elements
                .retain(|el| el.element_type() != ElementType::Water);
            world.elements.push(Element {
                id: 9_900,
                kind: ElementKind::Water,
                pos: Position::new(8, 8),
                ttl: None,
            });
            let b = world.kitty_index(2).unwrap();
            world.kitties[b].pos = Position::new(8, 8); // the wet friend
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].pos = Position::new(8, 9); // dry, facing exposure
            let mut registry = BehaviorRegistry::with_builtins();
            registry.register("always_invalid", Arc::new(AlwaysInvalid));
            world.tick(&registry, &config).await;
            (world, config)
        }

        let (on, on_cfg) = exposed_world(true).await;
        // The gate-off config: identical world inputs, only the bool
        // differs — masks are pure functions of (snapshot, config), so
        // one snapshot under both configs isolates the bool exactly.
        let mut off = (*on_cfg).clone();
        off.behavior.contagion_aware_ladder = false;
        let off_cfg = Arc::new(off);
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        for id in [1, 2] {
            let snapshot = on.snapshot().fog_for(id, on_cfg.vision.radius);
            let table = TargetTable::build(&snapshot, id, &cfg);
            assert_eq!(
                legal_action_mask(&snapshot, id, &table, &codec, &on_cfg),
                legal_action_mask(&snapshot, id, &table, &codec, &off_cfg),
                "kitty {id}: the ladder gate moved the legal-action mask \
                 (FR-007 armed case)"
            );
            assert_eq!(
                legal_message_mask(&snapshot, id, &on_cfg),
                legal_message_mask(&snapshot, id, &off_cfg),
                "kitty {id}: the ladder gate moved the message mask"
            );
        }
    }

    #[test]
    fn the_mask_is_never_all_zero_for_a_fresh_world() {
        let (world, config) = test_world();
        let full = world.snapshot();
        let cfg = ObservationConfig::default();
        let codec = ActionCodec::v2(&cfg);
        for kitty in &full.kitties {
            let snapshot = full.fog_for(kitty.id, config.vision.radius);
            let table = TargetTable::build(&snapshot, kitty.id, &cfg);
            let mask = legal_action_mask(&snapshot, kitty.id, &table, &codec, &config);
            assert!(mask.iter().any(|&b| b), "kitty {} all-zero", kitty.id);
        }
    }
}
