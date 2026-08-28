//! Kitties.
//!
//! Article II is structural: this type has no health, no damage, no despawn, and no
//! removal API. There is deliberately no `Kitty::die`, no `World::remove_kitty`, and
//! no lifecycle state that could stand in for one. A kitty that enters the world
//! stays in it.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::action::{Action, TargetRef};
use crate::config::{DurationBounds, DurationsConfig};
use crate::grid::Position;
use crate::meow::MessageKind;
use crate::needs::{NeedKind, Needs};

pub type KittyId = u32;

/// Reserved: no live kitty may ever carry this id (config validation
/// rejects it, spec 014). Downstream encodings use it to mean "no kitty";
/// a proposal naming it lawfully resolves to idle. See
/// [`crate::element::RESERVED_ELEMENT_ID`].
pub const RESERVED_KITTY_ID: KittyId = KittyId::MAX;

/// Engine bookkeeping of the current chase: which target, since when, the best
/// distance achieved, and when that best was last bettered. Written only by the
/// engine from *applied* actions, so no behavior can forge a chase it never ran.
///
/// Patience is measured against `last_progress()` -- ticks since the chase last
/// gained ground -- not against `started`. A one-tick detour does not reset the
/// clock, and a chase that is still closing is never called hopeless, however
/// long it has been running.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Pursuit {
    pub target: TargetRef,
    pub started: u64,
    pub closest: u32,
    /// Tick at which `closest` last improved. Defaulted for snapshots written
    /// before this field existed; `last_progress` treats 0 as "unknown" and
    /// falls back to `started`.
    #[serde(default)]
    pub improved_at: u64,
}

impl Pursuit {
    /// The last tick this chase gained ground -- the clock patience runs
    /// against. Comparing *current* distance to the best-ever distance would
    /// call a chase hopeless at the very moment it arrives (best-ever equals
    /// current exactly when the cat is doing as well as it ever has), so
    /// progress is a timestamp, never a distance comparison.
    pub fn last_progress(&self) -> u64 {
        self.improved_at.max(self.started)
    }
}

/// A chase target given up on: excluded from re-selection until `until`.
/// The exclusion is what makes give-up real with several hopeless targets --
/// without it, abandoning one greeble for another makes the first instantly
/// tempting again (FR-006).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct AbandonedChase {
    pub target: TargetRef,
    pub until: u64,
}

/// What a kitty is currently doing. Multi-tick activities carry their context so
/// the engine can keep applying their effects (and drop the partner bonus if the
/// friend wanders off). Since spec 006 every need-relieving action is an
/// activity, paced by an [`ActivityClock`] and the configured duration bounds.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum Activity {
    #[default]
    Idle,
    Resting {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        with_friend: Option<KittyId>,
    },
    Sleeping {
        in_sunbeam: bool,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        with_friend: Option<KittyId>,
    },
    Eating,
    Drinking,
    Playing {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        target: Option<TargetRef>,
    },
    Grooming {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        target: Option<KittyId>,
    },
}

impl Activity {
    pub fn is_sleeping(&self) -> bool {
        matches!(self, Activity::Sleeping { .. })
    }

    pub fn is_in_progress(&self) -> bool {
        !matches!(self, Activity::Idle)
    }

    pub fn partner(&self) -> Option<KittyId> {
        match self {
            Activity::Idle | Activity::Eating | Activity::Drinking => None,
            Activity::Resting { with_friend } => *with_friend,
            Activity::Sleeping { with_friend, .. } => *with_friend,
            Activity::Playing { target } => match target {
                Some(TargetRef::Kitty { id }) => Some(*id),
                _ => None,
            },
            Activity::Grooming { target } => *target,
        }
    }

    /// The kitty bound into this activity with a shared clock -- social
    /// play only, since spec 041 made rest co-sleep's sibling. Resting,
    /// co-sleeping and grooming reference a friend without binding them:
    /// those partners keep their own clocks, or none.
    pub fn duet_partner(&self) -> Option<KittyId> {
        match self {
            Activity::Playing {
                target: Some(TargetRef::Kitty { id }),
            } => Some(*id),
            _ => None,
        }
    }

    /// Which configured duration bounds govern this activity.
    pub fn bounds(&self, durations: &DurationsConfig) -> Option<DurationBounds> {
        match self {
            Activity::Idle => None,
            Activity::Eating => Some(durations.eat),
            Activity::Drinking => Some(durations.drink),
            Activity::Playing { .. } => Some(durations.play),
            Activity::Grooming { .. } => Some(durations.bath),
            Activity::Sleeping { .. } => Some(durations.sleep),
            Activity::Resting { .. } => Some(durations.cuddle),
        }
    }

    /// The need whose reaching 0 ends this activity (spec 006 FR-006), or
    /// `None` for an activity with no governing need (solo rest is posture,
    /// not relief -- it ends by interrupt or by running its cap).
    ///
    /// This is the one place the activity-to-need mapping lives; the engine's
    /// end rules and any test asserting them must both derive from it.
    /// *Whose* need is checked stays the engine's business: the groomed
    /// friend's bath, either partner's play or cuddle in a duet.
    pub fn governing_need(&self) -> Option<NeedKind> {
        match self {
            Activity::Idle | Activity::Resting { with_friend: None } => None,
            Activity::Eating => Some(NeedKind::Eat),
            Activity::Drinking => Some(NeedKind::Drink),
            Activity::Playing { .. } => Some(NeedKind::Play),
            Activity::Grooming { .. } => Some(NeedKind::Bath),
            Activity::Sleeping { .. } => Some(NeedKind::Sleep),
            Activity::Resting {
                with_friend: Some(_),
            } => Some(NeedKind::Cuddle),
        }
    }

    /// The action that carries this activity for another tick. `None` only
    /// for `Idle`, which has nothing to continue.
    pub fn continuation(&self) -> Option<Action> {
        match *self {
            Activity::Idle => None,
            Activity::Eating => Some(Action::Eat),
            Activity::Drinking => Some(Action::Drink),
            Activity::Playing { target } => Some(Action::Play { target }),
            Activity::Grooming { target } => Some(Action::Groom { target }),
            Activity::Sleeping { with_friend, .. } => Some(Action::Sleep { with: with_friend }),
            Activity::Resting { with_friend } => Some(Action::Rest { with: with_friend }),
        }
    }

    /// Whether `action` continues this activity rather than switching away.
    /// `Idle` always continues (the built-ins' way of saying "carry on");
    /// targeted activities only continue under the *same* target -- playing
    /// with a different friend is a switch, not a continuation.
    pub fn is_continued_by(&self, action: &Action) -> bool {
        match (self, action) {
            (Activity::Idle, _) => false,
            (_, Action::Idle) => true,
            (Activity::Eating, Action::Eat) => true,
            (Activity::Drinking, Action::Drink) => true,
            (Activity::Playing { target }, Action::Play { target: proposed }) => target == proposed,
            (Activity::Grooming { target }, Action::Groom { target: proposed }) => {
                target == proposed
            }
            (Activity::Sleeping { .. }, Action::Sleep { .. }) => true,
            (Activity::Resting { .. }, Action::Rest { .. }) => true,
            _ => false,
        }
    }
}

/// Engine bookkeeping pacing the ongoing activity (spec 006).
///
/// `started` is the first tick the activity was applied. `applied` is the last
/// tick it was *serviced* -- stamped on every tick the activity survives,
/// whether or not effects landed that tick. The stamp is load-bearing: the end
/// rules key off the clock, so a tick that skipped it (a paused meal, a duet's
/// second slot) would leave the activity unreachable by every way out.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ActivityClock {
    pub started: u64,
    pub applied: u64,
    /// Per-scene tier counters (spec 041 FR-011): serviced ticks of a
    /// partnered rest or co-sleep scene whose partner was itself settled
    /// (`mutual_ticks`) or merely present (`drip_ticks`). Reset with the
    /// clock at scene start, copied onto the `ActivityEnd` event at scene
    /// end, zero on every other activity. Absent in pre-041 snapshots:
    /// a resumed scene honestly counts from its resume.
    #[serde(default, skip_serializing_if = "tier_count_is_zero")]
    pub mutual_ticks: u32,
    #[serde(default, skip_serializing_if = "tier_count_is_zero")]
    pub drip_ticks: u32,
}

fn tier_count_is_zero(n: &u32) -> bool {
    *n == 0
}

impl ActivityClock {
    pub fn start(tick: u64) -> Self {
        Self {
            started: tick,
            applied: tick,
            mutual_ticks: 0,
            drip_ticks: 0,
        }
    }

    /// Inclusive tick count, counting `tick` itself as serviced.
    pub fn elapsed(&self, tick: u64) -> u64 {
        tick.saturating_sub(self.started) + 1
    }

    /// Ticks already serviced before `tick` -- the "minimum met?" measure at
    /// enforcement time, before the current tick is counted.
    pub fn serviced_before(&self, tick: u64) -> u64 {
        tick.saturating_sub(self.started)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Kitty {
    pub id: KittyId,
    pub name: String,
    pub pos: Position,
    pub needs: Needs,
    pub happiness: f32,
    pub activity: Activity,
    /// Name of the behavior strategy deciding for this kitty.
    ///
    /// Configuration owns this on resume (spec 014): the value persisted in
    /// a snapshot is informational as of save time, and the loader
    /// re-stamps it from the config's roster — never trust a snapshot's
    /// behavior string over the config.
    pub behavior: String,
    /// Human-readable summary of what drives this kitty (spec 034), served
    /// verbatim beside `behavior`: the model registry's display line for a
    /// policy seat, `"Scripted"` for a builtin, absent for a plugin.
    ///
    /// Server-stamped presentation, never read by the engine. The registry
    /// (like the config for `behavior`) is authoritative on resume: the
    /// server re-stamps every kitty after load, so a snapshot's value —
    /// including its absence in pre-034 saves — is informational only.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub behavior_description: Option<String>,
    /// Earliest tick at which each message kind may be used again.
    #[serde(default)]
    pub meow_cooldowns: BTreeMap<MessageKind, u64>,
    /// Needs currently at or above the distress threshold. Drives edge-triggered
    /// event recording: a need already in this set does not re-record.
    #[serde(default)]
    pub in_distress: BTreeSet<NeedKind>,
    /// Whether happiness went up on the previous tick; one of the two ways a kitty
    /// earns the right to purr.
    #[serde(default)]
    pub happiness_rose: bool,
    /// The action the engine actually applied for this kitty last tick -- the
    /// post-validation one, so an illegal proposal honestly reads as `Idle`.
    /// `None` only before the world's first tick. Feeds the viewer's "doing"
    /// line; defaulted so pre-existing saves still load.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub last_action: Option<Action>,
    /// The chase in progress, if any. Engine-maintained (see `World::tick`);
    /// behaviors read it to judge when a chase has become hopeless.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pursuit: Option<Pursuit>,
    /// Targets recently given up on, each excluded until its `until` tick.
    /// Engine-maintained and engine-pruned, so it stays tiny.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub abandoned_chases: Vec<AbandonedChase>,
    /// The tick each need last received relief, whatever delivered it. Missing
    /// means never -- which deliberately wins selection ties, so a
    /// long-neglected need gets its turn first.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub last_relief: BTreeMap<NeedKind, u64>,
    /// The tick each currently-active distress began. Keys match `in_distress`
    /// after every needs phase; viewers derive "how long has this been going
    /// on" as `world.tick - distress_since[need]`.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub distress_since: BTreeMap<NeedKind, u64>,
    /// Duration bookkeeping for the ongoing activity (spec 006). Present
    /// exactly when `activity` is in progress -- a strict pairing enforced by
    /// the invariants, with no legacy tolerance.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub activity_clock: Option<ActivityClock>,
    /// `Some(t)` while the kitty is purring; the purr ends at tick `t`
    /// (spec 011). Purring is background state -- it never occupies the
    /// action slot -- and its presence in the payload is the viewer's
    /// "rumbling now" signal. Absent in pre-011 snapshots: quiet.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub purring_until: Option<u64>,
    /// The drawn length of the current purr (spec 022): set at purr start
    /// (either origin), consumed at purr end to stamp the proportional motor
    /// cooldown, then cleared -- paired with `purring_until`. Absent in
    /// pre-022 snapshots: an in-flight purr restores without it, and its end
    /// treats the duration as `[purr] min_ticks` (the fixed convention).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub purring_duration: Option<u64>,
    /// No new purr may begin before this tick (spec 011). 0 in pre-011
    /// snapshots: immediately eligible.
    #[serde(default)]
    pub purr_cooldown_until: u64,
    /// Needs currently armed for announcement (spec 028): a want-kind is
    /// speakable only while its need is armed. Armed at `>= [meow]
    /// announce_threshold`, disarmed below `threshold - hysteresis`, held
    /// in the band -- updated in the needs phase beside distress, same
    /// edge-rule style, no RNG. Absent in pre-028 snapshots: disarmed,
    /// and re-armed honestly on the first needs phase.
    #[serde(default, skip_serializing_if = "BTreeSet::is_empty")]
    pub announce_armed: BTreeSet<NeedKind>,
}

impl Kitty {
    pub fn new(
        id: KittyId,
        name: impl Into<String>,
        pos: Position,
        behavior: impl Into<String>,
    ) -> Self {
        Self {
            id,
            name: name.into(),
            pos,
            needs: Needs::default(),
            happiness: 100.0,
            activity: Activity::Idle,
            behavior: behavior.into(),
            behavior_description: None,
            meow_cooldowns: BTreeMap::new(),
            in_distress: BTreeSet::new(),
            happiness_rose: false,
            last_action: None,
            pursuit: None,
            abandoned_chases: Vec::new(),
            last_relief: BTreeMap::new(),
            distress_since: BTreeMap::new(),
            activity_clock: None,
            purring_until: None,
            purring_duration: None,
            purr_cooldown_until: 0,
            announce_armed: BTreeSet::new(),
        }
    }

    /// Ends whatever this kitty is doing: activity and clock are cleared
    /// together, the strict pairing the invariants demand. Every site that
    /// ends an activity must come through here, so a future field joining
    /// the pairing has exactly one place to join it.
    pub(crate) fn clear_activity(&mut self) {
        self.activity = Activity::Idle;
        self.activity_clock = None;
    }

    /// The earned-purr rule (specs 011/022), the one definition both
    /// enforcement sites share: the motor's start check (`World::purr_phase`)
    /// and the deliberate purr's validate gate -- which the RL mask derives
    /// from -- must never disagree, so neither may inline its own copy.
    /// `purr_threshold` is `config.thresholds.purr`.
    pub fn purr_earned(&self, purr_threshold: f32) -> bool {
        self.happiness > purr_threshold || self.happiness_rose
    }

    /// Whether repeating `kind` at `tick` would be courteous (spec 023):
    /// consulted voluntarily by the scripted behaviors before they propose
    /// a repeat. The engine enforces nothing with this -- every validated
    /// meow emits.
    pub fn can_meow(&self, kind: MessageKind, tick: u64) -> bool {
        match self.meow_cooldowns.get(&kind) {
            Some(&ready_at) => tick >= ready_at,
            None => true,
        }
    }

    /// When `kind` last got relief; 0 ("the dawn of time") when it never has,
    /// so an untouched need wins selection ties.
    pub fn last_relief_tick(&self, kind: NeedKind) -> u64 {
        self.last_relief.get(&kind).copied().unwrap_or(0)
    }

    /// Whether `target` is currently excluded after an abandoned chase.
    pub fn is_chase_excluded(&self, target: TargetRef, tick: u64) -> bool {
        self.abandoned_chases
            .iter()
            .any(|a| a.target == target && a.until > tick)
    }

    pub fn set_meow_cooldown(&mut self, kind: MessageKind, ready_at_tick: u64) {
        self.meow_cooldowns.insert(kind, ready_at_tick);
    }

    /// Drops cooldown entries that have already elapsed, so the map cannot grow
    /// without bound over a long-lived world.
    pub fn prune_meow_cooldowns(&mut self, tick: u64) {
        self.meow_cooldowns.retain(|_, ready_at| *ready_at > tick);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn kitty() -> Kitty {
        Kitty::new(1, "Miso", Position::new(3, 3), "needs_driven")
    }

    #[test]
    fn new_kitties_start_content() {
        let k = kitty();
        assert_eq!(k.happiness, 100.0);
        assert_eq!(k.activity, Activity::Idle);
        assert!(k.in_distress.is_empty());
    }

    #[test]
    fn meow_cooldown_gates_repeats() {
        let mut k = kitty();
        assert!(k.can_meow(MessageKind::WantPlay, 0));

        k.set_meow_cooldown(MessageKind::WantPlay, 15);
        assert!(!k.can_meow(MessageKind::WantPlay, 14));
        assert!(k.can_meow(MessageKind::WantPlay, 15));
        // Other message kinds are unaffected.
        assert!(k.can_meow(MessageKind::WantEat, 0));
    }

    #[test]
    fn elapsed_cooldowns_are_pruned() {
        let mut k = kitty();
        k.set_meow_cooldown(MessageKind::WantEat, 5);
        k.set_meow_cooldown(MessageKind::WantPlay, 20);
        k.prune_meow_cooldowns(10);
        assert!(!k.meow_cooldowns.contains_key(&MessageKind::WantEat));
        assert!(k.meow_cooldowns.contains_key(&MessageKind::WantPlay));
    }

    #[test]
    fn pursuit_and_bookkeeping_fields_round_trip() {
        let mut k = kitty();
        k.pursuit = Some(Pursuit {
            target: TargetRef::Element { id: 102 },
            started: 1461,
            closest: 3,
            improved_at: 1464,
        });
        k.abandoned_chases.push(AbandonedChase {
            target: TargetRef::Element { id: 105 },
            until: 1520,
        });
        k.last_relief.insert(NeedKind::Eat, 1396);
        k.distress_since.insert(NeedKind::Play, 1249);
        k.purring_until = Some(1500);
        k.purring_duration = Some(9);

        let json = serde_json::to_string(&k).unwrap();
        let back: Kitty = serde_json::from_str(&json).unwrap();
        assert_eq!(back, k);
    }

    #[test]
    fn a_pre_004_kitty_json_deserializes_with_empty_bookkeeping() {
        // The exact field set a 003-era snapshot carries -- none of the new ones.
        let json = r#"{
            "id": 1, "name": "Miso", "pos": {"x": 21, "y": 30},
            "needs": {"eat": 34.5, "drink": 30.5, "sleep": 98.9,
                      "play": 100.0, "cuddle": 45.75, "bath": 100.0},
            "happiness": 39.3,
            "activity": {"state": "idle"},
            "behavior": "needs_driven",
            "meow_cooldowns": {},
            "in_distress": ["sleep", "play", "bath"],
            "happiness_rose": false
        }"#;
        let k: Kitty = serde_json::from_str(json).unwrap();
        assert!(k.pursuit.is_none());
        assert!(k.abandoned_chases.is_empty());
        assert!(k.last_relief.is_empty());
        assert!(k.distress_since.is_empty());
        assert!(
            k.purring_duration.is_none(),
            "pre-022 snapshots have no stored duration (min_ticks convention)"
        );
        assert_eq!(
            k.last_relief_tick(NeedKind::Bath),
            0,
            "never = dawn of time"
        );
    }

    #[test]
    fn a_pre_028_kitty_json_deserializes_disarmed() {
        // Spec 028 (FR-022): a pre-028 kitty carries no announce_armed key
        // and loads disarmed; the first needs phase re-arms honestly from
        // the loaded need values. Wire hygiene both ways: empty sets are
        // absent when serialized, armed sets round-trip.
        let json = r#"{
            "id": 1, "name": "Miso", "pos": {"x": 3, "y": 3},
            "needs": {"eat": 80.0, "drink": 30.0, "sleep": 30.0,
                      "play": 30.0, "cuddle": 30.0, "bath": 30.0},
            "happiness": 80.0,
            "activity": {"state": "idle"},
            "behavior": "needs_driven",
            "meow_cooldowns": {"want_eat": 120},
            "in_distress": [],
            "happiness_rose": false
        }"#;
        let k: Kitty = serde_json::from_str(json).unwrap();
        assert!(
            k.announce_armed.is_empty(),
            "pre-028 kitties load disarmed, whatever their needs say"
        );
        let out = serde_json::to_string(&k).unwrap();
        assert!(
            !out.contains("announce_armed"),
            "an empty set stays off the wire"
        );

        let mut armed = k.clone();
        armed.announce_armed.insert(NeedKind::Eat);
        let out = serde_json::to_string(&armed).unwrap();
        assert!(out.contains("announce_armed"), "armed state rides the wire");
        let back: Kitty = serde_json::from_str(&out).unwrap();
        assert_eq!(back.announce_armed, armed.announce_armed);
    }

    #[test]
    fn restored_meow_bookkeeping_is_a_harmless_courtesy_record() {
        // Spec 023 US3 scenario 4: a pre-023 snapshot's stamped cooldowns
        // load fine; the courtesy consult respects them (a delayed next
        // scripted meow) and nothing enforces them -- the engine reads
        // this map nowhere.
        let json = r#"{
            "id": 1, "name": "Miso", "pos": {"x": 3, "y": 3},
            "needs": {"eat": 30.0, "drink": 30.0, "sleep": 30.0,
                      "play": 30.0, "cuddle": 30.0, "bath": 30.0},
            "happiness": 80.0,
            "activity": {"state": "idle"},
            "behavior": "needs_driven",
            "meow_cooldowns": {"want_eat": 500},
            "in_distress": [],
            "happiness_rose": false
        }"#;
        let k: Kitty = serde_json::from_str(json).unwrap();
        assert!(
            !k.can_meow(MessageKind::WantEat, 499),
            "the restored record delays the courtesy consult"
        );
        assert!(k.can_meow(MessageKind::WantEat, 500));
    }

    #[test]
    fn empty_bookkeeping_stays_off_the_wire() {
        let json = serde_json::to_value(kitty()).unwrap();
        assert!(json.get("pursuit").is_none());
        assert!(json.get("abandoned_chases").is_none());
        assert!(json.get("last_relief").is_none());
        assert!(json.get("distress_since").is_none());
        assert!(json.get("purring_duration").is_none());
    }

    #[test]
    fn a_pursuit_saved_before_improved_at_existed_falls_back_to_started() {
        // The field is serde-defaulted, so a snapshot written between the 004
        // merge and this fix arrives with improved_at = 0. Treating that as
        // "improved at the dawn of time" would condemn the chase instantly;
        // last_progress falls back to `started` instead.
        let json = r#"{"target":{"target":"element","id":9},"started":500,"closest":4}"#;
        let p: Pursuit = serde_json::from_str(json).unwrap();
        assert_eq!(p.improved_at, 0);
        assert_eq!(p.last_progress(), 500, "falls back to the start tick");

        // And a normal pursuit reports its actual last improvement.
        let fresh = Pursuit {
            target: TargetRef::Element { id: 9 },
            started: 500,
            closest: 4,
            improved_at: 512,
        };
        assert_eq!(fresh.last_progress(), 512);
    }

    #[test]
    fn chase_exclusion_expires() {
        let mut k = kitty();
        let target = TargetRef::Element { id: 7 };
        k.abandoned_chases
            .push(AbandonedChase { target, until: 100 });
        assert!(k.is_chase_excluded(target, 99));
        assert!(!k.is_chase_excluded(target, 100), "until is exclusive");
        assert!(!k.is_chase_excluded(TargetRef::Kitty { id: 2 }, 50));
    }

    #[test]
    fn activity_wire_shape_uses_a_state_tag() {
        let sleeping = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(2),
        };
        let json = serde_json::to_value(sleeping).unwrap();
        assert_eq!(json["state"], "sleeping");
        assert_eq!(json["in_sunbeam"], true);
        assert_eq!(json["with_friend"], 2);

        let solo = serde_json::to_value(Activity::Resting { with_friend: None }).unwrap();
        assert_eq!(solo["state"], "resting");
        assert!(solo.get("with_friend").is_none());
    }

    #[test]
    fn the_006_activity_variants_have_tidy_wire_shapes() {
        let eating = serde_json::to_value(Activity::Eating).unwrap();
        assert_eq!(eating["state"], "eating");

        let drinking = serde_json::to_value(Activity::Drinking).unwrap();
        assert_eq!(drinking["state"], "drinking");

        let social = serde_json::to_value(Activity::Playing {
            target: Some(TargetRef::Kitty { id: 2 }),
        })
        .unwrap();
        assert_eq!(social["state"], "playing");
        assert_eq!(social["target"]["target"], "kitty");
        assert_eq!(social["target"]["id"], 2);

        let solo_play = serde_json::to_value(Activity::Playing { target: None }).unwrap();
        assert_eq!(solo_play["state"], "playing");
        assert!(solo_play.get("target").is_none(), "solo play omits target");

        let groom = serde_json::to_value(Activity::Grooming { target: Some(3) }).unwrap();
        assert_eq!(groom["state"], "grooming");
        assert_eq!(groom["target"], 3);

        let self_groom = serde_json::to_value(Activity::Grooming { target: None }).unwrap();
        assert_eq!(self_groom["state"], "grooming");
        assert!(self_groom.get("target").is_none());
    }

    #[test]
    fn the_activity_clock_round_trips_and_is_omitted_when_absent() {
        let mut k = kitty();
        assert!(
            !serde_json::to_string(&k)
                .unwrap()
                .contains("activity_clock"),
            "no clock, no wire noise"
        );

        k.activity = Activity::Eating;
        k.activity_clock = Some(ActivityClock {
            started: 41,
            applied: 43,
            mutual_ticks: 0,
            drip_ticks: 0,
        });
        let json = serde_json::to_value(&k).unwrap();
        assert_eq!(json["activity_clock"]["started"], 41);
        assert_eq!(json["activity_clock"]["applied"], 43);

        let back: Kitty = serde_json::from_value(json).unwrap();
        assert_eq!(back.activity_clock, k.activity_clock);
        assert_eq!(back.activity, Activity::Eating);
    }

    #[test]
    fn a_pre_006_kitty_json_deserializes_with_no_clock() {
        // The field defaults to None; whether such a kitty is *lawful* is the
        // invariants' strict business (an in-progress activity without a
        // clock is refused there), not serde's.
        let json = serde_json::json!({
            "id": 1,
            "name": "Miso",
            "pos": {"x": 1, "y": 1},
            "needs": {"eat": 0.0, "drink": 0.0, "sleep": 0.0, "play": 0.0, "cuddle": 0.0, "bath": 0.0},
            "happiness": 100.0,
            "activity": {"state": "sleeping", "in_sunbeam": false},
            "behavior": "needs_driven",
        });
        let k: Kitty = serde_json::from_value(json).unwrap();
        assert_eq!(k.activity_clock, None);
        assert!(k.activity.is_sleeping());
    }

    #[test]
    fn the_elapsed_convention_is_inclusive() {
        let clock = ActivityClock::start(10);
        assert_eq!(clock.elapsed(10), 1, "the starting tick counts");
        assert_eq!(clock.elapsed(14), 5);
        assert_eq!(clock.serviced_before(10), 0);
        assert_eq!(clock.serviced_before(12), 2, "min 2 is met from tick 12");
    }

    #[test]
    fn continuation_actions_mirror_their_activities() {
        assert_eq!(Activity::Eating.continuation(), Some(Action::Eat));
        assert_eq!(
            Activity::Playing {
                target: Some(TargetRef::Element { id: 7 })
            }
            .continuation(),
            Some(Action::Play {
                target: Some(TargetRef::Element { id: 7 })
            })
        );
        assert_eq!(Activity::Idle.continuation(), None);

        // Idle continues anything in progress; a different play target is a
        // switch, not a continuation.
        let playing = Activity::Playing {
            target: Some(TargetRef::Element { id: 7 }),
        };
        assert!(playing.is_continued_by(&Action::Idle));
        assert!(playing.is_continued_by(&Action::Play {
            target: Some(TargetRef::Element { id: 7 })
        }));
        assert!(!playing.is_continued_by(&Action::Play {
            target: Some(TargetRef::Element { id: 8 })
        }));
        assert!(!playing.is_continued_by(&Action::Eat));
        assert!(!Activity::Idle.is_continued_by(&Action::Idle));
    }

    #[test]
    fn every_activity_names_its_governing_need_or_lawfully_has_none() {
        use crate::needs::NeedKind;
        assert_eq!(Activity::Eating.governing_need(), Some(NeedKind::Eat));
        assert_eq!(Activity::Drinking.governing_need(), Some(NeedKind::Drink));
        assert_eq!(
            Activity::Playing { target: None }.governing_need(),
            Some(NeedKind::Play)
        );
        assert_eq!(
            Activity::Grooming { target: Some(2) }.governing_need(),
            Some(NeedKind::Bath),
            "friend-grooming is governed by bath (the *friend's* -- whose is the engine's business)"
        );
        assert_eq!(
            Activity::Sleeping {
                in_sunbeam: true,
                with_friend: None
            }
            .governing_need(),
            Some(NeedKind::Sleep)
        );
        assert_eq!(
            Activity::Resting {
                with_friend: Some(2)
            }
            .governing_need(),
            Some(NeedKind::Cuddle)
        );
        // Solo rest is posture, not relief: no governing need, ends by
        // interrupt or cap. Idle is not an activity at all.
        assert_eq!(
            Activity::Resting { with_friend: None }.governing_need(),
            None
        );
        assert_eq!(Activity::Idle.governing_need(), None);
    }

    #[test]
    fn duet_partners_are_only_the_bound_kind() {
        assert_eq!(
            Activity::Playing {
                target: Some(TargetRef::Kitty { id: 2 })
            }
            .duet_partner(),
            Some(2)
        );
        // Resting joined the reference-without-binding kind at spec 041;
        // co-sleeping and grooming were always there.
        assert_eq!(
            Activity::Resting {
                with_friend: Some(2)
            }
            .duet_partner(),
            None
        );
        assert_eq!(
            Activity::Sleeping {
                in_sunbeam: false,
                with_friend: Some(2)
            }
            .duet_partner(),
            None
        );
        assert_eq!(Activity::Grooming { target: Some(2) }.duet_partner(), None);
    }
}
