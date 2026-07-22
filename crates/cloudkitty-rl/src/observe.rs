//! Observation schema v1 (spec 014 FR-005) and the target table.
//!
//! A fixed-size per-kitty vector, a deterministic pure function of the frozen
//! start-of-tick [`WorldSnapshot`] — the same information a behavior's
//! decision context exposes, nothing more. Layout, in order:
//!
//! 1. **Self block**: needs (/100), happiness (/100), position (x/width,
//!    y/height), activity one-hot (7) + social flag + in-sunbeam flag +
//!    progress (elapsed/min, clamped), distress flags (6), pursuit (active
//!    flag + staleness), static traits (6 per-need rise rates / reference).
//! 2. **Kitty slots × K**: present, relative position, distance, needs,
//!    happiness, activity one-hot + social, `is-activity-target` bit.
//! 3. **Element slots**: chow (present, rel pos, distance, servings), water
//!    (present, rel pos, distance), sunbeam (present, rel pos, distance,
//!    remaining-ttl fraction, occupied), critter (present, rel pos,
//!    distance, kind bit, greeble heading one-hot, `is-activity-target`).
//! 4. **Meow digest**: per learned kind — recency-weighted presence and the
//!    nearest other emitter's direction (a kitty's own meows tell it
//!    nothing and are excluded).
//! 5. **Episode clock**: tick/horizon (0 at deploy, where no episode runs).
//!
//! **Slot fill (normative, target-priority — research.md R1)**: slots fill
//! nearest-first, distance-ordered, ties by id — except the entity the
//! observing kitty's ongoing activity references is always granted a slot in
//! its table: the referenced kitty of a cuddle, co-sleep, groom, or social
//! play in a kitty slot; a played-with critter in a critter slot. It
//! displaces the farthest otherwise-eligible occupant and carries the
//! `is-activity-target` bit. The engine-side key is [`Activity::partner`]
//! plus the `Playing` element target — deliberately **not** `duet_partner()`,
//! which omits co-sleep and groom. Chow, water, and sunbeam slots are pure
//! nearest-K: no activity references them by identity.

use cloudkitty_core::action::TargetRef;
use cloudkitty_core::element::{ElementId, ElementKind, ElementType};
use cloudkitty_core::grid::Direction;
use cloudkitty_core::kitty::{Activity, Kitty, KittyId};
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::world::WorldSnapshot;
use cloudkitty_core::Config;

use crate::config::ObservationConfig;

/// Version pinned into policy artifacts (FR-007/FR-016).
pub const OBSERVATION_SCHEMA_VERSION: u32 = 1;

/// The meow kinds a policy can hear and speak: every kind except the
/// engine-reserved `wait_for_me` (spec 012). Order is normative — the meow
/// digest and the action menu both use it.
pub const LEARNED_MEOWS: [MessageKind; 6] = [
    MessageKind::WantEat,
    MessageKind::WantDrink,
    MessageKind::FollowMe,
    MessageKind::WantPlay,
    MessageKind::WantCuddle,
    MessageKind::Purr,
];

const SELF_BLOCK: usize = 6 + 1 + 2 + 7 + 1 + 1 + 1 + 6 + 2 + 6;
const KITTY_SLOT: usize = 1 + 2 + 1 + 6 + 1 + 7 + 1 + 1;
const CHOW_SLOT: usize = 1 + 2 + 1 + 1;
const WATER_SLOT: usize = 1 + 2 + 1;
const SUNBEAM_SLOT: usize = 1 + 2 + 1 + 1 + 1;
const CRITTER_SLOT: usize = 1 + 2 + 1 + 1 + 4 + 1;
const MEOW_DIGEST: usize = LEARNED_MEOWS.len() * 3;
const CLOCK: usize = 1;

/// The exact observation length for a slot configuration. With the default
/// slots (3 kitty, 4 critter, 2 chow, 2 water, 2 sunbeam) this is 182.
pub fn observation_len(cfg: &ObservationConfig) -> usize {
    SELF_BLOCK
        + cfg.kitty_slots * KITTY_SLOT
        + cfg.chow_slots * CHOW_SLOT
        + cfg.water_slots * WATER_SLOT
        + cfg.sunbeam_slots * SUNBEAM_SLOT
        + cfg.critter_slots * CRITTER_SLOT
        + MEOW_DIGEST
        + CLOCK
}

/// Per-observation mapping from slot indices to concrete identities — the
/// bridge that lets the flat action menu name a specific neighbor (FR-006).
/// Built from the same snapshot by the same fill rule as the observation.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TargetTable {
    /// `kitties[k]` is the kitty in kitty slot k, or None for a vacant slot.
    pub kitties: Vec<Option<KittyId>>,
    /// `critters[j]` is the element in critter slot j, or None.
    pub critters: Vec<Option<ElementId>>,
}

impl TargetTable {
    /// Builds the table for `kitty_id`'s observation of `snapshot`.
    pub fn build(snapshot: &WorldSnapshot, kitty_id: KittyId, cfg: &ObservationConfig) -> Self {
        let me = snapshot
            .kitty(kitty_id)
            .expect("the observing kitty exists in its own snapshot");
        let (kitty_target, critter_target) = activity_targets(me, snapshot);

        let kitty_candidates: Vec<(u32, KittyId)> = snapshot
            .others(kitty_id)
            .map(|k| (me.pos.manhattan_distance(&k.pos), k.id))
            .collect();
        let kitties = fill_slots(kitty_candidates, cfg.kitty_slots, kitty_target);

        let critter_candidates: Vec<(u32, ElementId)> = snapshot
            .critters()
            .map(|e| (me.pos.manhattan_distance(&e.pos), e.id))
            .collect();
        let critters = fill_slots(critter_candidates, cfg.critter_slots, critter_target);

        TargetTable { kitties, critters }
    }
}

/// The entities the kitty's ongoing activity references, per table: the
/// `Activity::partner()` kitty (cuddle, co-sleep, groom, social play) and
/// the played-with critter (research.md R1's engine key). A critter target
/// that no longer exists gets no priority — the activity itself is about to
/// be pruned.
fn activity_targets(me: &Kitty, snapshot: &WorldSnapshot) -> (Option<KittyId>, Option<ElementId>) {
    let kitty_target = me.activity.partner();
    let critter_target = match me.activity {
        Activity::Playing {
            target: Some(TargetRef::Element { id }),
        } => snapshot
            .elements
            .iter()
            .find(|e| e.id == id && e.element_type().is_critter())
            .map(|e| e.id),
        _ => None,
    };
    (kitty_target, critter_target)
}

/// Target-priority slot fill (research.md R1): nearest first, ties by id;
/// the priority entity, if eligible and not already among the nearest K,
/// displaces the farthest occupant; the chosen K are then slot-ordered by
/// (distance, id). Vacant slots pad with None.
fn fill_slots<Id: Copy + Ord>(
    mut candidates: Vec<(u32, Id)>,
    slots: usize,
    priority: Option<Id>,
) -> Vec<Option<Id>> {
    candidates.sort_unstable_by_key(|&(d, id)| (d, id));
    let mut chosen: Vec<(u32, Id)> = candidates.iter().take(slots).copied().collect();
    if let Some(p) = priority {
        let eligible = candidates.iter().find(|&&(_, id)| id == p).copied();
        if let Some(entry) = eligible {
            if !chosen.iter().any(|&(_, id)| id == p) {
                chosen.pop();
                chosen.push(entry);
                chosen.sort_unstable_by_key(|&(d, id)| (d, id));
            }
        }
    }
    let mut out: Vec<Option<Id>> = chosen.into_iter().map(|(_, id)| Some(id)).collect();
    out.resize(slots, None);
    out
}

/// One kitty's encoded view: the vector and the table that names its slots.
#[derive(Debug, Clone)]
pub struct Observation {
    pub values: Vec<f32>,
    pub table: TargetTable,
}

/// Encodes `kitty_id`'s observation of the frozen snapshot. `episode_clock`
/// is tick/horizon in [0, 1] (0 at deploy, where no episode runs).
pub fn encode_observation(
    snapshot: &WorldSnapshot,
    kitty_id: KittyId,
    core: &Config,
    cfg: &ObservationConfig,
    episode_clock: f32,
) -> Observation {
    let me = snapshot
        .kitty(kitty_id)
        .expect("the observing kitty exists in its own snapshot");
    let table = TargetTable::build(snapshot, kitty_id, cfg);
    let (kitty_target, critter_target) = activity_targets(me, snapshot);
    let width = snapshot.width as f32;
    let height = snapshot.height as f32;
    let max_distance = (snapshot.width + snapshot.height) as f32;

    let mut v = Vec::with_capacity(observation_len(cfg));

    // 1. Self block.
    push_needs_and_happiness(&mut v, me);
    v.push(me.pos.x as f32 / width);
    v.push(me.pos.y as f32 / height);
    push_activity(&mut v, &me.activity);
    v.push(if me.activity.partner().is_some() {
        1.0
    } else {
        0.0
    });
    v.push(match me.activity {
        Activity::Sleeping { in_sunbeam, .. } if in_sunbeam => 1.0,
        _ => 0.0,
    });
    v.push(activity_progress(me, snapshot.tick, core));
    push_distress_flags(&mut v, me);
    match me.pursuit {
        Some(p) => {
            v.push(1.0);
            let stale = snapshot.tick.saturating_sub(p.last_progress()) as f32
                / core.behavior.chase_patience_ticks.max(1) as f32;
            v.push(stale.clamp(0.0, 1.0));
        }
        None => {
            v.push(0.0);
            v.push(0.0);
        }
    }
    push_traits(&mut v, kitty_id, core, cfg);

    // 2. Kitty slots.
    for slot in &table.kitties {
        match slot.and_then(|id| snapshot.kitty(id)) {
            Some(other) => {
                v.push(1.0);
                v.push((other.pos.x as f32 - me.pos.x as f32) / width);
                v.push((other.pos.y as f32 - me.pos.y as f32) / height);
                v.push(me.pos.manhattan_distance(&other.pos) as f32 / max_distance);
                push_needs_and_happiness(&mut v, other);
                push_activity(&mut v, &other.activity);
                v.push(if other.activity.partner().is_some() {
                    1.0
                } else {
                    0.0
                });
                v.push(if kitty_target == Some(other.id) {
                    1.0
                } else {
                    0.0
                });
            }
            None => v.extend(std::iter::repeat_n(0.0, KITTY_SLOT)),
        }
    }

    // 3. Element slots. Chow, water, sunbeam: pure nearest-K.
    let chow = nearest_elements(snapshot, me, ElementType::Chow, cfg.chow_slots);
    for slot in &chow {
        match slot {
            Some(e) => {
                push_element_common(&mut v, me, e, width, height, max_distance);
                let servings = match e.kind {
                    ElementKind::Chow { servings } => servings,
                    _ => 0,
                };
                v.push((servings as f32 / cfg.max_chow_servings as f32).clamp(0.0, 1.0));
            }
            None => v.extend(std::iter::repeat_n(0.0, CHOW_SLOT)),
        }
    }
    let water = nearest_elements(snapshot, me, ElementType::Water, cfg.water_slots);
    for slot in &water {
        match slot {
            Some(e) => push_element_common(&mut v, me, e, width, height, max_distance),
            None => v.extend(std::iter::repeat_n(0.0, WATER_SLOT)),
        }
    }
    let sunbeams = nearest_elements(snapshot, me, ElementType::Sunbeam, cfg.sunbeam_slots);
    for slot in &sunbeams {
        match slot {
            Some(e) => {
                push_element_common(&mut v, me, e, width, height, max_distance);
                let ttl_fraction = match (e.ttl, core.elements.sunbeam.ttl) {
                    (Some(left), Some(total)) if total > 0 => {
                        (left as f32 / total as f32).clamp(0.0, 1.0)
                    }
                    _ => 1.0,
                };
                v.push(ttl_fraction);
                let occupied = snapshot.kitties.iter().any(|k| k.pos == e.pos);
                v.push(if occupied { 1.0 } else { 0.0 });
            }
            None => v.extend(std::iter::repeat_n(0.0, SUNBEAM_SLOT)),
        }
    }
    for slot in &table.critters {
        match slot.and_then(|id| snapshot.elements.iter().find(|e| e.id == id)) {
            Some(e) => {
                push_element_common(&mut v, me, e, width, height, max_distance);
                match e.kind {
                    ElementKind::Greeble { heading } => {
                        v.push(1.0);
                        for dir in Direction::ALL {
                            v.push(if dir == heading { 1.0 } else { 0.0 });
                        }
                    }
                    _ => {
                        v.push(0.0);
                        v.extend(std::iter::repeat_n(0.0, 4));
                    }
                }
                v.push(if critter_target == Some(e.id) {
                    1.0
                } else {
                    0.0
                });
            }
            None => v.extend(std::iter::repeat_n(0.0, CRITTER_SLOT)),
        }
    }

    // 4. Meow digest: others' recent meows, recency-weighted, with the
    // nearest emitter's direction.
    let window = core.meow.recent_window_ticks.max(1) as f32;
    for kind in LEARNED_MEOWS {
        let heard: Vec<_> = snapshot
            .recent_meows
            .iter()
            .filter(|m| m.kind == kind && m.kitty_id != kitty_id)
            .collect();
        let presence = heard
            .iter()
            .map(|m| 1.0 - (snapshot.tick.saturating_sub(m.tick) as f32 / window))
            .fold(0.0f32, |a, b| a.max(b.clamp(0.0, 1.0)));
        let nearest = heard
            .iter()
            .filter_map(|m| snapshot.kitty(m.kitty_id))
            .min_by_key(|k| (me.pos.manhattan_distance(&k.pos), k.id));
        v.push(presence);
        match nearest {
            Some(k) => {
                v.push((k.pos.x as f32 - me.pos.x as f32) / width);
                v.push((k.pos.y as f32 - me.pos.y as f32) / height);
            }
            None => {
                v.push(0.0);
                v.push(0.0);
            }
        }
    }

    // 5. Episode clock.
    v.push(episode_clock.clamp(0.0, 1.0));

    debug_assert_eq!(v.len(), observation_len(cfg));
    Observation { values: v, table }
}

/// Activity one-hot in normative order: idle, resting, sleeping, eating,
/// drinking, playing, grooming. Shared with the global-state encoder
/// (spec 014 review): actor and critic must agree on what an activity
/// looks like, so the mapping exists exactly once.
pub(crate) fn push_activity(v: &mut Vec<f32>, activity: &Activity) {
    let index = match activity {
        Activity::Idle => 0,
        Activity::Resting { .. } => 1,
        Activity::Sleeping { .. } => 2,
        Activity::Eating => 3,
        Activity::Drinking => 4,
        Activity::Playing { .. } => 5,
        Activity::Grooming { .. } => 6,
    };
    for i in 0..7 {
        v.push(if i == index { 1.0 } else { 0.0 });
    }
}

/// Needs (each /100) then happiness (/100), in normative order. Shared by
/// the self block, the kitty slots, and the global-state encoder: actor
/// and critic must scale a kitty's condition identically, so the scaling
/// exists exactly once (spec 014 third review).
pub(crate) fn push_needs_and_happiness(v: &mut Vec<f32>, kitty: &Kitty) {
    for kind in NeedKind::ALL {
        v.push(kitty.needs.get(kind) / 100.0);
    }
    v.push(kitty.happiness / 100.0);
}

/// One flag per need kind, 1.0 while that need is in distress. Shared with
/// the global-state encoder.
pub(crate) fn push_distress_flags(v: &mut Vec<f32>, kitty: &Kitty) {
    for kind in NeedKind::ALL {
        v.push(if kitty.in_distress.contains(&kind) {
            1.0
        } else {
            0.0
        });
    }
}

/// Trait features: each configured need rate over the reference rate,
/// clamped to [0, 4] (the schema's documented bound). Shared with the
/// global-state encoder — the critic's view of a trait must scale exactly
/// as the actors' do.
pub(crate) fn push_traits(
    v: &mut Vec<f32>,
    kitty_id: cloudkitty_core::kitty::KittyId,
    core: &Config,
    cfg: &ObservationConfig,
) {
    for kind in NeedKind::ALL {
        let trait_value = core.need_rate_for(kitty_id, kind) / cfg.reference_need_rate;
        v.push(trait_value.clamp(0.0, 4.0));
    }
}

/// Elapsed / configured minimum, clamped to [0, 1]; 0 outside an activity.
/// Shared with the global-state encoder — one formula, two consumers.
pub(crate) fn activity_progress(me: &Kitty, tick: u64, core: &Config) -> f32 {
    let Some(clock) = me.activity_clock else {
        return 0.0;
    };
    let Some(bounds) = me.activity.bounds(&core.actions.durations) else {
        return 0.0;
    };
    (clock.elapsed(tick) as f32 / bounds.min.max(1) as f32).clamp(0.0, 1.0)
}

fn push_element_common(
    v: &mut Vec<f32>,
    me: &Kitty,
    e: &cloudkitty_core::element::Element,
    width: f32,
    height: f32,
    max_distance: f32,
) {
    v.push(1.0);
    v.push((e.pos.x as f32 - me.pos.x as f32) / width);
    v.push((e.pos.y as f32 - me.pos.y as f32) / height);
    v.push(me.pos.manhattan_distance(&e.pos) as f32 / max_distance);
}

/// The one proximity ordering (spec 014 review): Manhattan distance from
/// `anchor`, ties by id — the normative slot-fill key (FR-005), shared by
/// the observation's element slots and the global state's center summary
/// so the convention can never fork.
pub(crate) fn sort_by_proximity(
    elements: &mut [&cloudkitty_core::element::Element],
    anchor: cloudkitty_core::grid::Position,
) {
    elements.sort_unstable_by_key(|e| (anchor.manhattan_distance(&e.pos), e.id));
}

/// Nearest-K elements of one type, distance-ordered, ties by id, padded
/// with None.
fn nearest_elements<'a>(
    snapshot: &'a WorldSnapshot,
    me: &Kitty,
    kind: ElementType,
    slots: usize,
) -> Vec<Option<&'a cloudkitty_core::element::Element>> {
    let mut candidates: Vec<&cloudkitty_core::element::Element> =
        snapshot.elements_of(kind).collect();
    sort_by_proximity(&mut candidates, me.pos);
    let mut out: Vec<Option<&cloudkitty_core::element::Element>> =
        candidates.into_iter().take(slots).map(Some).collect();
    out.resize(slots, None);
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::grid::Position;
    use cloudkitty_core::kitty::ActivityClock;
    use cloudkitty_core::test_support::test_world;

    #[test]
    fn the_default_layout_is_182_values() {
        assert_eq!(observation_len(&ObservationConfig::default()), 182);
    }

    #[test]
    fn a_distant_groom_target_is_granted_a_slot_with_the_bit_set() {
        // Force a roster larger than the slots: the groom target sits far
        // away, three other kitties crowd close. Target-priority must
        // displace the farthest nearby kitty. (Grooming is exactly one of
        // the activities duet_partner() omits — the regression this module
        // exists to prevent.)
        let (mut world, config) = test_world();
        // Grow the roster to 5 by hand (test worlds allow it: kitties are
        // only ever added).
        for (id, x, y) in [(3u32, 3u32, 4u32), (4, 4, 3), (5, 2, 3)] {
            world.kitties.push(cloudkitty_core::kitty::Kitty::new(
                id,
                format!("K{id}"),
                Position::new(x, y),
                "needs_driven",
            ));
        }
        world.kitties.sort_by_key(|k| k.id);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(3, 3);
        world.kitties[idx].activity = Activity::Grooming { target: Some(2) };
        world.kitties[idx].activity_clock = Some(ActivityClock::start(0));
        let far = world.kitty_index(2).unwrap();
        world.kitties[far].pos = Position::new(15, 15);

        let snapshot = world.snapshot();
        let cfg = ObservationConfig::default();
        let table = TargetTable::build(&snapshot, 1, &cfg);

        assert!(
            table.kitties.contains(&Some(2)),
            "the groom target holds a slot despite being farthest: {:?}",
            table.kitties
        );
        // And the observation's is-activity-target bit marks that slot.
        let obs = encode_observation(&snapshot, 1, &config, &cfg, 0.0);
        let slot = table.kitties.iter().position(|s| *s == Some(2)).unwrap();
        let bit_index = SELF_BLOCK + slot * KITTY_SLOT + (KITTY_SLOT - 1);
        assert_eq!(obs.values[bit_index], 1.0);
    }

    #[test]
    fn without_an_activity_slots_are_pure_nearest_k_ties_by_id() {
        let (mut world, _config) = test_world();
        for (id, x, y) in [(3u32, 5u32, 3u32), (4, 3, 5), (5, 9, 9)] {
            world.kitties.push(cloudkitty_core::kitty::Kitty::new(
                id,
                format!("K{id}"),
                Position::new(x, y),
                "needs_driven",
            ));
        }
        world.kitties.sort_by_key(|k| k.id);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(3, 3);
        // Kitty 2 at distance 2; kitties 3 and 4 both at distance 2; kitty 5 far.
        let k2 = world.kitty_index(2).unwrap();
        world.kitties[k2].pos = Position::new(3, 1);

        let snapshot = world.snapshot();
        let table = TargetTable::build(&snapshot, 1, &ObservationConfig::default());
        assert_eq!(
            table.kitties,
            vec![Some(2), Some(3), Some(4)],
            "distance 2 for all three, ties broken by id; 5 is crowded out"
        );
    }

    #[test]
    fn encoding_is_deterministic_and_in_bounds() {
        let (world, config) = test_world();
        let snapshot = world.snapshot();
        let cfg = ObservationConfig::default();

        let a = encode_observation(&snapshot, 1, &config, &cfg, 0.25);
        let b = encode_observation(&snapshot, 1, &config, &cfg, 0.25);
        assert_eq!(a.values, b.values, "same snapshot, identical vector");
        assert_eq!(a.table, b.table);
        assert_eq!(a.values.len(), observation_len(&cfg));
        for (i, value) in a.values.iter().enumerate() {
            assert!(
                (-1.0..=4.0).contains(value),
                "value {value} at index {i} outside documented bounds"
            );
        }
    }
}
