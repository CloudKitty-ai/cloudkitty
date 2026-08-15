//! Kitty communication.
//!
//! Fifteen speakable kinds plus the engine's patience word, visible to every
//! other kitty and to viewers. Spec 028 ended the courtesy era: emission
//! stamps a per-kind cooldown of one audibility window, and legality is
//! engine law. Spec 033 closed the vocabulary as a two-tier language:
//! LAW-NAMED kinds (Want*, Here*, Purr) have their meaning enforced by
//! their grounding predicate; SOUND-NAMED kinds (mew, chirp, trill, ekekek
//! -- the free register) carry cooldown-only law, and what they mean is the
//! cats' to decide. A kind whose name asserts a meaning its predicate does
//! not enforce is a naming-law violation (spec 033 FR-002b).

use serde::{Deserialize, Serialize};

use crate::kitty::KittyId;
use crate::needs::NeedKind;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MessageKind {
    WantEat,
    WantDrink,
    /// The free register's first word (spec 033) -- renamed from FollowMe,
    /// whose designed meaning ("come along") the cats overwrote ("I'm
    /// coming, stay put"). Same position, same cooldown-only law; only the
    /// name moved, because a sound-name cannot lie.
    Mew,
    WantPlay,
    WantCuddle,
    Purr,
    /// Approach etiquette (spec 012): the yielding kitty of a mutual
    /// approach holds its corner and asks its partner to close the gap.
    /// Emitted by the yield rule only -- nothing else may spend it. NOT
    /// renamed at the 033 wall: it is the engine's word, and the engine
    /// means what it says.
    WaitForMe,
    /// Spec 028: the two silent needs get their words. Appended so the
    /// existing six keep their normative positions.
    WantBath,
    WantSleep,
    /// Spec 033, the Here family: law-named altruistic reference. Legal
    /// exactly when the referent is ADJACENT to the speaker (the
    /// corresponding action's own predicate; visibility never suffices --
    /// the owner's adjacency invariant, binding through every vision
    /// regime). Emission-time truth only: the engine never enforces that
    /// the speaker preserve what it announced.
    HereFood,
    HereWater,
    /// Grounded by Play-critter's terms (adjacent live critter),
    /// deliberately NOT Chase's -- Chase is legal at any distance, which
    /// would make this word mean "exists somewhere" instead of "here".
    HereCritter,
    /// The family's one stated exception: no sunbeam action exists to
    /// share a predicate with, so the grounding is explicit adjacency to a
    /// live beam (Drink's shape, stated plainly).
    HereSunbeam,
    /// Spec 033, the free register's second word: active at phase 1.
    Chirp,
    /// Reserve (spec 033): in every layout, config-flag off by default,
    /// zero training presence -- the post-fog language-capacity experiment
    /// arms it by flag, never by codec move.
    Trill,
    /// Reserve, as Trill.
    Ekekek,
}

impl MessageKind {
    pub const ALL: [MessageKind; 16] = [
        MessageKind::WantEat,
        MessageKind::WantDrink,
        MessageKind::Mew,
        MessageKind::WantPlay,
        MessageKind::WantCuddle,
        MessageKind::Purr,
        MessageKind::WaitForMe,
        MessageKind::WantBath,
        MessageKind::WantSleep,
        MessageKind::HereFood,
        MessageKind::HereWater,
        MessageKind::HereCritter,
        MessageKind::HereSunbeam,
        MessageKind::Chirp,
        MessageKind::Trill,
        MessageKind::Ekekek,
    ];

    /// The need this message asks about -- want-kinds only. Everything
    /// else (the free register, Purr, WaitForMe, the Here family) has
    /// none: they are not requests, and their intensity stamps 0.0.
    pub fn related_need(&self) -> Option<NeedKind> {
        match self {
            MessageKind::WantEat => Some(NeedKind::Eat),
            MessageKind::WantDrink => Some(NeedKind::Drink),
            MessageKind::WantPlay => Some(NeedKind::Play),
            MessageKind::WantCuddle => Some(NeedKind::Cuddle),
            MessageKind::WantBath => Some(NeedKind::Bath),
            MessageKind::WantSleep => Some(NeedKind::Sleep),
            MessageKind::Mew
            | MessageKind::Purr
            | MessageKind::WaitForMe
            | MessageKind::HereFood
            | MessageKind::HereWater
            | MessageKind::HereCritter
            | MessageKind::HereSunbeam
            | MessageKind::Chirp
            | MessageKind::Trill
            | MessageKind::Ekekek => None,
        }
    }

    /// The wire spelling (serde's snake_case tag) as a static string --
    /// the one spelling every surface reports (spec 028 R17: the py
    /// binding's Debug-spelling wart died with this).
    pub fn wire_name(&self) -> &'static str {
        match self {
            MessageKind::WantEat => "want_eat",
            MessageKind::WantDrink => "want_drink",
            MessageKind::Mew => "mew",
            MessageKind::WantPlay => "want_play",
            MessageKind::WantCuddle => "want_cuddle",
            MessageKind::Purr => "purr",
            MessageKind::WaitForMe => "wait_for_me",
            MessageKind::WantBath => "want_bath",
            MessageKind::WantSleep => "want_sleep",
            MessageKind::HereFood => "here_food",
            MessageKind::HereWater => "here_water",
            MessageKind::HereCritter => "here_critter",
            MessageKind::HereSunbeam => "here_sunbeam",
            MessageKind::Chirp => "chirp",
            MessageKind::Trill => "trill",
            MessageKind::Ekekek => "ekekek",
        }
    }

    /// The message a kitty uses to ask for help with `need`. Total since
    /// spec 028: every need is announceable.
    pub fn for_need(need: NeedKind) -> MessageKind {
        match need {
            NeedKind::Eat => MessageKind::WantEat,
            NeedKind::Drink => MessageKind::WantDrink,
            NeedKind::Play => MessageKind::WantPlay,
            NeedKind::Cuddle => MessageKind::WantCuddle,
            NeedKind::Bath => MessageKind::WantBath,
            NeedKind::Sleep => MessageKind::WantSleep,
        }
    }
}

/// Engine law (spec 028, tiered by spec 033): may `kitty` speak `kind` at
/// `tick`, standing among `elements`? Silence is the absence of a message
/// and needs no ruling -- this covers the spoken kinds. The RL message
/// mask derives from here by probing, exactly as the activity mask probes
/// `validate` (the no-carve-outs doctrine), which is what keeps mask and
/// enforcement agreeing by construction.
///
/// The tiers (spec 033 FR-002/FR-002b): a WANT-kind needs its grounding
/// need armed (threshold + hysteresis) and its cooldown clear. PURR is
/// earned-only (the retired purr-meow's validate gate, byte-faithful). A
/// HERE-kind needs its referent ADJACENT -- the corresponding action's own
/// predicate, never a parallel definition; visibility never suffices. The
/// FREE REGISTER (mew, chirp, trill, ekekek) is cooldown-gated only: the
/// engine enforces no meaning for a sound-named word. Every speakable kind
/// is additionally gated by its `[meow.vocabulary]` flag -- legality only,
/// never layout.
///
/// WaitForMe is cooldown-gated, head-excluded, and NOT flag-gated (the
/// engine's yield rule proposes it; policies cannot). Its yield-rule-only
/// vocabulary rule (spec 012) is convention, not law -- guarded at the
/// head, not the seam. A trusted in-process caller CAN pass legality with
/// it on a clear cooldown, deliberately: replay instruments re-propose
/// recorded decisions through the typed seam, and a provenance guard here
/// would downgrade a recorded yield-rule WaitForMe and break bit-exact
/// replay. Python and plugins cannot reach it either way.
pub fn message_legal(
    kitty: &crate::kitty::Kitty,
    kind: MessageKind,
    tick: u64,
    config: &crate::config::Config,
    elements: &[crate::element::Element],
) -> bool {
    use crate::element::ElementType;
    use crate::world::{adjacent_critter_in, adjacent_element_in, adjacent_stocked_chow_in};

    // WaitForMe first: the engine's own word, outside the flag system.
    if kind == MessageKind::WaitForMe {
        return kitty.can_meow(kind, tick);
    }
    if !config.meow.vocabulary.enabled(kind) {
        return false;
    }
    match kind {
        MessageKind::Purr => kitty.purr_earned(config.thresholds.purr),
        // The free register: sound-named, cooldown-only -- mew's law is
        // byte-identical to its follow_me days.
        MessageKind::Mew | MessageKind::Chirp | MessageKind::Trill | MessageKind::Ekekek => {
            kitty.can_meow(kind, tick)
        }
        // The Here family: the referent is adjacent, or the word is not
        // spoken. Each arm is the corresponding action's own predicate
        // (spec 033 FR-002); HereSunbeam is the one stated exception.
        MessageKind::HereFood => {
            adjacent_stocked_chow_in(elements, kitty.pos).is_some() && kitty.can_meow(kind, tick)
        }
        MessageKind::HereWater => {
            adjacent_element_in(elements, kitty.pos, ElementType::Water).is_some()
                && kitty.can_meow(kind, tick)
        }
        MessageKind::HereCritter => {
            adjacent_critter_in(elements, kitty.pos) && kitty.can_meow(kind, tick)
        }
        MessageKind::HereSunbeam => {
            adjacent_element_in(elements, kitty.pos, ElementType::Sunbeam).is_some()
                && kitty.can_meow(kind, tick)
        }
        want => match want.related_need() {
            Some(need) => kitty.announce_armed.contains(&need) && kitty.can_meow(want, tick),
            // Every kind without a need is matched above; the compiler
            // keeps this arm unreachable by construction, and a new kind
            // added without a tier fails HERE at review, not at runtime.
            None => false,
        },
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Meow {
    pub kitty_id: KittyId,
    pub kind: MessageKind,
    pub tick: u64,
    /// Spec 028: the grounding need's value at emission, /100 (want-kinds);
    /// 0.0 for the social words. Pre-028 snapshots read 0.0.
    #[serde(default)]
    pub intensity: f32,
}

/// The audible-emitter selection rule (spec 028), shared by the
/// observation digest and the scripted groom responder: among meows of
/// `kind`, the freshest wins (max tick), a tie falls to the LOWER kitty
/// id -- hence the deliberately reversed id comparison inside the
/// `max_by` -- and the listener's own emissions are never audible to
/// itself. FR-019's imitability guarantee (the responder keys on exactly
/// what the digest shows) holds only while both sides call this one
/// function; do not re-derive it in place.
pub fn freshest_audible(meows: &[Meow], kind: MessageKind, listener: KittyId) -> Option<&Meow> {
    meows
        .iter()
        .filter(|m| m.kind == kind && m.kitty_id != listener)
        .max_by(|a, b| a.tick.cmp(&b.tick).then(b.kitty_id.cmp(&a.kitty_id)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn freshest_audible_takes_max_tick_ties_to_the_lower_id_and_never_self() {
        let m = |kitty_id: KittyId, tick: u64| Meow {
            kitty_id,
            kind: MessageKind::WantBath,
            tick,
            intensity: 0.0,
        };
        let meows = vec![
            m(5, 10),
            m(2, 12),
            m(7, 12), // same tick as id 2: the LOWER id must win
            m(3, 8),
        ];
        let picked = freshest_audible(&meows, MessageKind::WantBath, 9).unwrap();
        assert_eq!(
            (picked.kitty_id, picked.tick),
            (2, 12),
            "tie to the lower id"
        );

        // The listener's own freshest emission is inaudible to itself.
        let picked = freshest_audible(&meows, MessageKind::WantBath, 2).unwrap();
        assert_eq!(picked.kitty_id, 7, "self excluded, next claimant wins");

        // Kind filter is exact; a different kind hears nothing.
        assert!(freshest_audible(&meows, MessageKind::WantPlay, 9).is_none());
    }

    #[test]
    fn wait_for_me_is_a_patience_word() {
        // Spec 012: in the vocabulary, no related need (urgency never
        // touches a word whose meaning is patience), wire name stable.
        assert!(MessageKind::ALL.contains(&MessageKind::WaitForMe));
        assert_eq!(MessageKind::WaitForMe.related_need(), None);
        assert_eq!(
            serde_json::to_string(&MessageKind::WaitForMe).unwrap(),
            "\"wait_for_me\""
        );
    }

    #[test]
    fn wire_names_match_the_serde_tags_for_every_kind() {
        for kind in MessageKind::ALL {
            let tag = serde_json::to_value(kind).unwrap();
            assert_eq!(tag.as_str().unwrap(), kind.wire_name(), "{kind:?}");
        }
    }

    #[test]
    fn need_to_message_mapping_round_trips() {
        // Spec 028: total both ways -- every need has its word, and every
        // want-kind points back at its need.
        for need in NeedKind::ALL {
            let msg = MessageKind::for_need(need);
            assert_eq!(msg.related_need(), Some(need));
        }
        assert_eq!(
            serde_json::to_string(&MessageKind::WantBath).unwrap(),
            "\"want_bath\""
        );
        assert_eq!(
            serde_json::to_string(&MessageKind::WantSleep).unwrap(),
            "\"want_sleep\""
        );
    }

    // ---- spec 033: the Here family's law (T011) ----

    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::test_support::test_world;
    use crate::world::World;

    /// A clean stage: no elements, kitty 1 parked mid-meadow, tick 50.
    fn bare_meadow() -> (World, crate::config::Config) {
        let (mut world, config) = test_world();
        world.tick = 50;
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(8, 8);
        (world, config)
    }

    fn legal(world: &World, kind: MessageKind, config: &crate::config::Config) -> bool {
        message_legal(
            world.kitty(1).unwrap(),
            kind,
            world.tick,
            config,
            &world.elements,
        )
    }

    #[test]
    fn a_here_word_is_legal_exactly_at_its_referent() {
        use MessageKind::*;
        let referents: [(MessageKind, ElementKind); 4] = [
            (HereFood, ElementKind::Chow { servings: 2 }),
            (HereWater, ElementKind::Water),
            (HereCritter, ElementKind::Bug),
            (HereSunbeam, ElementKind::Sunbeam),
        ];
        for (kind, element_kind) in referents {
            let (mut world, config) = bare_meadow();
            assert!(
                !legal(&world, kind, &config),
                "{kind:?} on bare grass is not a here"
            );
            world.push_element(Element {
                id: 900,
                kind: element_kind,
                pos: Position::new(8, 9), // adjacent
                ttl: Some(50),
            });
            assert!(
                legal(&world, kind, &config),
                "{kind:?} beside its referent is legal"
            );
        }
    }

    #[test]
    fn the_speakers_own_tile_grounds_a_here_word_too() {
        // is_adjacent is manhattan <= 1: a cat ON the beam announces it.
        let (mut world, config) = bare_meadow();
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Sunbeam,
            pos: Position::new(8, 8),
            ttl: Some(50),
        });
        assert!(legal(&world, MessageKind::HereSunbeam, &config));
    }

    #[test]
    fn an_empty_bowl_is_not_food_here() {
        // US1/AC3: HereFood shares Eat's predicate exactly, servings and all.
        let (mut world, config) = bare_meadow();
        world.push_element(Element {
            id: 902,
            kind: ElementKind::Chow { servings: 0 },
            pos: Position::new(8, 9),
            ttl: None,
        });
        assert!(!legal(&world, MessageKind::HereFood, &config));
    }

    #[test]
    fn a_far_critter_is_chaseable_but_not_here() {
        // US1/AC4: Chase is legal at any distance -- which is exactly why
        // HereCritter does NOT share its predicate. The word means "here,
        // with me", never "exists somewhere".
        let (mut world, config) = bare_meadow();
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Bug,
            pos: Position::new(1, 1), // far across the meadow
            ttl: Some(200),
        });
        let chase = crate::action::validate(
            &world,
            1,
            crate::action::Action::Chase(crate::action::TargetRef::Element { id: 903 }),
            &config,
        );
        assert_ne!(
            chase,
            crate::action::Action::Idle,
            "the far bug IS a lawful chase target"
        );
        assert!(
            !legal(&world, MessageKind::HereCritter, &config),
            "...and still not a here"
        );
    }

    #[test]
    fn the_cooldown_binds_the_here_family_like_every_kind() {
        let (mut world, config) = bare_meadow();
        world.push_element(Element {
            id: 904,
            kind: ElementKind::Chow { servings: 2 },
            pos: Position::new(8, 9),
            ttl: None,
        });
        assert!(legal(&world, MessageKind::HereFood, &config));
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].set_meow_cooldown(MessageKind::HereFood, world.tick + 5);
        assert!(
            !legal(&world, MessageKind::HereFood, &config),
            "one live digest entry per kind per emitter (spec 028), Here included"
        );
    }

    // ---- spec 033: the free register (T015) ----

    #[test]
    fn the_free_register_needs_no_grounding() {
        // US2/AC1: mew and chirp are legal on bare grass off cooldown --
        // sound-named words carry no predicate, exactly follow_me's old law.
        let (world, config) = bare_meadow();
        assert!(legal(&world, MessageKind::Mew, &config));
        assert!(legal(&world, MessageKind::Chirp, &config));
    }

    #[test]
    fn the_reserves_are_never_legal_until_armed_and_then_chirp_equivalent() {
        // US2/AC2: active-vs-reserve is nothing but the flag default.
        let (world, mut config) = bare_meadow();
        assert!(!legal(&world, MessageKind::Trill, &config));
        assert!(!legal(&world, MessageKind::Ekekek, &config));
        config.meow.vocabulary.trill = true;
        config.meow.vocabulary.ekekek = true;
        assert!(legal(&world, MessageKind::Trill, &config));
        assert!(legal(&world, MessageKind::Ekekek, &config));
    }

    #[test]
    fn a_disabled_kind_is_never_legal_whatever_the_world_says() {
        // US3/AC1: the flag out-ranks a true predicate.
        let (mut world, mut config) = bare_meadow();
        world.push_element(Element {
            id: 905,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(8, 9),
            ttl: None,
        });
        assert!(legal(&world, MessageKind::HereFood, &config));
        config.meow.vocabulary.here_food = false;
        assert!(!legal(&world, MessageKind::HereFood, &config));
        config.meow.vocabulary.mew = false;
        assert!(!legal(&world, MessageKind::Mew, &config));
    }

    #[test]
    fn wait_for_me_stays_outside_the_flag_system() {
        // The engine's word: cooldown-gated, never vocabulary-gated, and
        // deliberately unaffected by any flag (it is not speakable anyway).
        let (world, config) = bare_meadow();
        assert!(legal(&world, MessageKind::WaitForMe, &config));
    }

    #[test]
    fn mews_law_is_byte_identical_to_follow_mes() {
        // T003's legality half: cooldown-only, no grounding, no arming.
        let (mut world, config) = bare_meadow();
        assert!(
            legal(&world, MessageKind::Mew, &config),
            "clear cooldown: legal"
        );
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].set_meow_cooldown(MessageKind::Mew, world.tick + 3);
        assert!(
            !legal(&world, MessageKind::Mew, &config),
            "on cooldown: not"
        );
    }
}
