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
    ///
    /// The alias is DESERIALIZE-ONLY (033 review Finding 3, Experiments
    /// blessed 2026-08-15): pre-wall saves carrying live `follow_me`
    /// cooldowns now parse, so the fingerprint/schema gates refuse them
    /// with the guided `Incompatible` error instead of a
    /// corruption-flavored parse failure. Emission never writes the old
    /// name -- the round-trip test below keeps the alias from ever
    /// becoming a serialization path.
    #[serde(alias = "follow_me")]
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

    /// Spec 043: the stable ordering the `announce_here` selection
    /// indexes into — the Here family in `ALL` order. A future fifth
    /// here-word must be appended here (and its position is contract:
    /// Experiments' density screen reads per-kind shares against this
    /// order).
    pub const HERE_KINDS: [MessageKind; 4] = [
        MessageKind::HereFood,
        MessageKind::HereWater,
        MessageKind::HereCritter,
        MessageKind::HereSunbeam,
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
/// `validate` (the no-carve-outs doctrine): one rule, no parallel
/// definition. Probing shares the RULE, not the MOMENT (033 review
/// Finding 5): the mask probes the frozen start-of-tick snapshot while
/// enforcement reads live elements after earlier turns apply, so a
/// Here-kind -- the one tier whose law reads element state -- can be
/// mask-legal yet downgrade to Silent within the tick (an earlier turn
/// ate the last serving). Spec-deliberate and rot-safe: emission-time
/// truth, and the divergence only ever silences, never falsely speaks.
/// Want*/Purr state mutates in phase 4 only, so no other tier diverges.
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
    view: &crate::world::FogView,
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
    let elements = &view.elements;
    match kind {
        MessageKind::Purr => kitty.purr_earned(config.thresholds.purr),
        // The free register: sound-named, cooldown-only -- mew's law is
        // byte-identical to its follow_me days.
        MessageKind::Mew | MessageKind::Chirp | MessageKind::Trill | MessageKind::Ekekek => {
            kitty.can_meow(kind, tick)
        }
        // The Here family (spec 049 FR-037, widened): the referent is
        // ADJACENT -- the corresponding action's own predicate (spec 033
        // FR-002), unchanged -- OR the reply condition holds: a matching
        // want from another cat is audible and the referent is visible
        // from the speaker. Cooldown and flag as ever.
        MessageKind::HereFood => {
            (adjacent_stocked_chow_in(elements, kitty.pos).is_some()
                || reply_condition(kind, view, config))
                && kitty.can_meow(kind, tick)
        }
        MessageKind::HereWater => {
            (adjacent_element_in(elements, kitty.pos, ElementType::Water).is_some()
                || reply_condition(kind, view, config))
                && kitty.can_meow(kind, tick)
        }
        MessageKind::HereCritter => {
            (adjacent_critter_in(elements, kitty.pos) || reply_condition(kind, view, config))
                && kitty.can_meow(kind, tick)
        }
        MessageKind::HereSunbeam => {
            (adjacent_element_in(elements, kitty.pos, ElementType::Sunbeam).is_some()
                || reply_condition(kind, view, config))
                && kitty.can_meow(kind, tick)
        }
        // The six law-named requests (spec 049 FR-036, the knowledge-gated
        // want law), in two classes (owner ruled 2026-09-03, T087):
        // ANNOUNCEMENTS (eat, drink, sleep, play, cuddle) -- grounding need
        // armed, that need the cat's TOP need, and no KNOWN relief for it,
        // so under fog the word says "I cannot see it", which no row
        // carries; and the one ASK, `want_bath` -- armed-only: its relief
        // source is in-place self-grooming, the partnered groom only a
        // GROOMER can start, and the groom response starts it on hearing
        // the word, so the word IS the mechanism and an idle friend in view
        // is a groomer to be asked, not relief the caller can execute.
        // Cooldown clear for every kind. Enumerated -- never a catch-all --
        // so a future kind added without a legality tier is a
        // non-exhaustive-match COMPILE error here, not a silently
        // never-legal word (033 review Finding 4). ONE predicate: the RL
        // mask and the built-in announce both call this. `LawEra::PreFog`
        // (SC-004a's test-side switch) replays the 2.x armed-only law.
        MessageKind::WantEat
        | MessageKind::WantDrink
        | MessageKind::WantPlay
        | MessageKind::WantCuddle
        | MessageKind::WantBath
        | MessageKind::WantSleep => {
            let need = kind
                .related_need()
                .expect("every Want kind names its grounding need");
            let armed = kitty.announce_armed.contains(&need) && kitty.can_meow(kind, tick);
            match (config.meow.law_era, kind) {
                (crate::config::LawEra::PreFog, _) => armed,
                (crate::config::LawEra::Fog, MessageKind::WantBath) => armed,
                (crate::config::LawEra::Fog, _) => {
                    armed
                        && kitty.needs.highest_pressure().0 == need
                        && !known_relief(kind, kitty, view)
                }
            }
        }
        MessageKind::WaitForMe => unreachable!("handled before the flag gate above"),
    }
}

/// The want ↔ here pairs (spec 049 FR-037/FR-040/FR-041, contracts/
/// meow-law-v5.md): legality, the reply stamp, the answers-me encoder and
/// the scripted ladder all read this one table. Cuddle and bath have no
/// here-word.
pub const WANT_HERE_PAIRS: [(MessageKind, MessageKind); 4] = [
    (MessageKind::WantEat, MessageKind::HereFood),
    (MessageKind::WantDrink, MessageKind::HereWater),
    (MessageKind::WantSleep, MessageKind::HereSunbeam),
    (MessageKind::WantPlay, MessageKind::HereCritter),
];

/// The want a here-kind answers, if any.
pub fn want_for_here(here: MessageKind) -> Option<MessageKind> {
    WANT_HERE_PAIRS
        .iter()
        .find(|(_, h)| *h == here)
        .map(|(w, _)| *w)
}

/// The here-word that answers a want-kind, if any.
pub fn here_for_want(want: MessageKind) -> Option<MessageKind> {
    WANT_HERE_PAIRS
        .iter()
        .find(|(w, _)| *w == want)
        .map(|(_, h)| *h)
}

/// Is the referent of a here-kind visible from the speaker (anywhere in
/// its disc)? The referent visibility half of the reply condition. Food
/// means a STOCKED bowl, as in the adjacency arm
/// (`adjacent_stocked_chow_in`): no snapshot holds an empty bowl, but the
/// mid-tick enforcement view can (an earlier cat emptied it this tick; it
/// expires in the environment phase), and a `here_food` stamped `reply`
/// must not point at nothing (`/code-review high 049` finding 4).
pub fn referent_visible(here: MessageKind, view: &crate::world::FogView) -> bool {
    use crate::element::{ElementKind, ElementType};
    match here {
        MessageKind::HereFood => view
            .elements_of(ElementType::Chow)
            .any(|e| matches!(e.kind, ElementKind::Chow { servings } if servings > 0)),
        MessageKind::HereWater => view.elements_of(ElementType::Water).next().is_some(),
        MessageKind::HereSunbeam => view.elements_of(ElementType::Sunbeam).next().is_some(),
        MessageKind::HereCritter => view.critters().next().is_some(),
        // Not a here-kind: no referent. Exhaustive on purpose (the no
        // catch-all doctrine above): a new here-kind lands here or fails
        // to compile.
        MessageKind::WantEat
        | MessageKind::WantDrink
        | MessageKind::Mew
        | MessageKind::WantPlay
        | MessageKind::WantCuddle
        | MessageKind::Purr
        | MessageKind::WaitForMe
        | MessageKind::WantBath
        | MessageKind::WantSleep
        | MessageKind::Chirp
        | MessageKind::Trill
        | MessageKind::Ekekek => false,
    }
}

/// The reply condition (spec 049 FR-037/FR-040, research R7): a meow of
/// the paired want from ANOTHER cat is audible in the speaker's
/// start-of-tick buffer (the view's one audibility rule: earlier tick,
/// inside the digest window) AND the referent is visible from the
/// speaker. Shared by the widened here law, the engine's reply stamp and
/// the scripted ladder -- the condition is one thing; the triggers differ.
pub fn reply_condition(
    here: MessageKind,
    view: &crate::world::FogView,
    config: &crate::config::Config,
) -> bool {
    let Some(want) = want_for_here(here) else {
        return false;
    };
    let window = config.meow.digest_window_ticks;
    let audible_want = view
        .recent_meows
        .iter()
        .any(|m| m.kind == want && m.kitty_id != view.observer && view.audible(m, window));
    audible_want && referent_visible(here, view)
}

/// Known relief (spec 049 FR-036 clause c): what silences a want-word --
/// relief the CALLER can execute itself. Eat/drink: the element visible or
/// remembered; cuddle: an idle friend IN VIEW (walk over and rest; heard
/// friends never gate -- owner ruled 2026-09-03); play: that friend clause
/// OR a critter visible or remembered; sleep: never (need-only-when-top);
/// bath: never -- an idle friend in view is a groomer who has to be asked,
/// not relief the caller can execute (owner ruled 2026-09-03, T087; the
/// law does not consult this arm, it is here so the table stays whole).
/// Reads the cat's OWN memory (the view's observer record is whole).
pub fn known_relief(
    want: MessageKind,
    kitty: &crate::kitty::Kitty,
    view: &crate::world::FogView,
) -> bool {
    use crate::element::ElementType;
    use crate::kitty::memory_index;
    let remembered = |kind: ElementType| kitty.memory[memory_index(kind)].is_some();
    let visible = |kind: ElementType| view.elements_of(kind).next().is_some();
    match want {
        MessageKind::WantEat => visible(ElementType::Chow) || remembered(ElementType::Chow),
        MessageKind::WantDrink => visible(ElementType::Water) || remembered(ElementType::Water),
        MessageKind::WantCuddle => crate::world::idle_friend_in_view(view),
        MessageKind::WantBath => false,
        MessageKind::WantPlay => {
            crate::world::idle_friend_in_view(view)
                || view.critters().next().is_some()
                || ElementType::ALL
                    .iter()
                    .any(|kind| kind.is_critter() && remembered(*kind))
        }
        MessageKind::WantSleep => false,
        // Not a want-kind: nothing to silence. Exhaustive on purpose.
        MessageKind::Mew
        | MessageKind::Purr
        | MessageKind::WaitForMe
        | MessageKind::HereFood
        | MessageKind::HereWater
        | MessageKind::HereCritter
        | MessageKind::HereSunbeam
        | MessageKind::Chirp
        | MessageKind::Trill
        | MessageKind::Ekekek => false,
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Meow {
    pub kitty_id: KittyId,
    pub kind: MessageKind,
    pub tick: u64,
    /// Spec 028: the grounding need's value at emission, /100 (want-kinds);
    /// 0.0 for the social words. REQUIRED since the 3.0 wall (spec 049
    /// FR-032, the eighth shim deleted): under fog intensity is an observed
    /// digest feature and the reply ladder's tie-breaker, so a silent 0.0
    /// on a missing field would corrupt the digest instead of failing at
    /// load.
    pub intensity: f32,
    /// Spec 049 FR-040: the speaker's position at emission, engine-stamped.
    /// Under fog this is what a listener that cannot see the speaker
    /// learns from the call -- the heard row points here, the scripted
    /// groom response walks here; the position is the MEOW's, never the
    /// cat's current one (owner ruling, coverage pass 2026-09-02).
    pub pos: crate::grid::Position,
    /// Spec 049 FR-040: engine-stamped at emission, never policy-chosen.
    /// For a here-kind, true iff a matching want from another cat was
    /// audible in the speaker's start-of-tick snapshot AND the referent
    /// was visible from the speaker; false for every other kind. The
    /// stamp is separate from any trigger (an ambient here landing while
    /// a want is audible is stamped too). Immutable once recorded.
    pub reply: bool,
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
    fn here_kinds_pins_the_all_order() {
        // Spec 043 FR-006: the selection index is only stable if this
        // ordering is — pinned to the Here family's positions in ALL.
        assert_eq!(
            MessageKind::HERE_KINDS,
            [
                MessageKind::HereFood,
                MessageKind::HereWater,
                MessageKind::HereCritter,
                MessageKind::HereSunbeam,
            ]
        );
        let in_all: Vec<MessageKind> = MessageKind::ALL
            .iter()
            .copied()
            .filter(|k| MessageKind::HERE_KINDS.contains(k))
            .collect();
        assert_eq!(
            in_all,
            MessageKind::HERE_KINDS.to_vec(),
            "HERE_KINDS must preserve MessageKind::ALL order"
        );
    }

    #[test]
    fn freshest_audible_takes_max_tick_ties_to_the_lower_id_and_never_self() {
        let m = |kitty_id: KittyId, tick: u64| Meow {
            kitty_id,
            kind: MessageKind::WantBath,
            tick,
            intensity: 0.0,
            pos: crate::grid::Position::new(0, 0),
            reply: false,
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
    fn the_follow_me_alias_reads_old_saves_and_never_writes() {
        // 033 review Finding 3 (Experiments blessed 2026-08-15): a pre-wall
        // save's live follow_me cooldown parses as Mew, so the
        // fingerprint/schema gates get to refuse the save with the guided
        // Incompatible error instead of a corruption-flavored parse failure.
        let old: MessageKind = serde_json::from_str("\"follow_me\"").unwrap();
        assert_eq!(old, MessageKind::Mew);
        // Deserialize-only, per the blessing's condition: emission writes
        // the new name, always — the alias must never become a
        // serialization path.
        assert_eq!(serde_json::to_string(&MessageKind::Mew).unwrap(), "\"mew\"");
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
        let view = world.snapshot().fog_for(1, config.vision.radius);
        message_legal(world.kitty(1).unwrap(), kind, world.tick, config, &view)
    }

    /// `/code-review high 049` finding 4 (2026-09-04): `here_food`'s
    /// referent is FOOD, not a bowl object. At the mid-tick enforcement
    /// seam a bowl an earlier cat emptied this tick still sits in the
    /// element list (it expires in the environment phase), so the reply
    /// arm must read stocked, as the adjacency arm always has -- else a
    /// here stamped `reply` points at nothing. Staged: kitty 2's
    /// `want_eat` audible, a bowl in view but not adjacent (the reply arm
    /// is the only way in), empty then stocked.
    #[test]
    fn here_food_needs_a_stocked_bowl_in_view() {
        let (mut world, config) = bare_meadow();
        world.recent_meows.push(Meow {
            kitty_id: 2,
            kind: MessageKind::WantEat,
            tick: 45,
            intensity: 0.5,
            pos: Position::new(2, 2),
            reply: false,
        });
        world.push_element(crate::element::Element {
            id: 900,
            kind: ElementKind::Chow { servings: 0 },
            pos: Position::new(11, 8),
            ttl: None,
        });
        let view = world.snapshot().fog_for(1, config.vision.radius);
        assert!(
            !referent_visible(MessageKind::HereFood, &view),
            "an emptied bowl is not food in view"
        );
        assert!(
            !legal(&world, MessageKind::HereFood, &config),
            "no here_food for an empty bowl, however loud the want"
        );
        let bowl = world.elements.iter_mut().find(|e| e.id == 900).unwrap();
        bowl.kind = ElementKind::Chow { servings: 1 };
        let view = world.snapshot().fog_for(1, config.vision.radius);
        assert!(referent_visible(MessageKind::HereFood, &view));
        assert!(
            legal(&world, MessageKind::HereFood, &config),
            "stocked and a want audible: the reply arm opens"
        );
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
