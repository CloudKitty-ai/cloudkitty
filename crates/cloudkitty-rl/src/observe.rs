//! Observation schema 5 (spec 049 — the fog wall; generation 2 since
//! spec 026, schema 4 since spec 033) and the target table.
//!
//! A fixed-size per-kitty vector, a deterministic pure function of the
//! deciding cat's frozen start-of-tick [`FogView`] — the same information
//! its behavior's decision context exposes, nothing more (FR-021). The
//! normative layout, offsets and masks live in
//! specs/049-fog-gen1/contracts/observation-v5.md; `schema_five_pins.rs`
//! asserts every derived number literally. In order:
//!
//! 1. **Self block (85)**: the schema-4 block unchanged (needs /100,
//!    happiness /100, position, activity one-hot (7) + social flag +
//!    in-sunbeam + in-water + progress, distress flags (6), pursuit (2),
//!    traits (6)), then own scene age, then the own message block (per
//!    `HEAD_KINDS` kind: recency, rate), then the element memory (per
//!    `ElementType::ALL` kind: present, dx, dy, staleness). Never fogged
//!    (FR-005).
//! 2. **Kitty rows × K (62 each)**: one PERMANENT row per friend, in kitty
//!    id order, never re-sorted (FR-011). A row's contents follow the
//!    friend's state for the observer this tick (FR-012): **seen** (inside
//!    the disc) → every field; **heard** (outside the disc, a call inside
//!    the digest window) → present 0, dx/dy/distance to the friend's
//!    position at its last audible meow, the message block live,
//!    knowledge fields 0; **silent** → all zero. A vacant row (roster
//!    smaller than K + 1) is always zero.
//! 3. **Element slots**: chow (5), water (4), sunbeam (6), critter (10)
//!    exactly as schema 4, filled nearest-K over VISIBLE elements only
//!    (FR-004); critters keep the target-priority fill.
//! 4. **Episode clock**: tick/horizon (0 at deploy, where no episode runs).
//!
//! The schema-4 global meow digest is gone: repetition and insistence are
//! per-speaker fields on the rows (FR-016).
//!
//! **Slot fill**: kitty rows are by id (FR-011); the target-priority fill
//! (research R1 of spec 014) stays for critters — the played-with critter
//! is always granted a slot and carries the `is-activity-target` bit — and
//! the kitty half of that rule stays present but inert (FR-015: unreachable
//! once every friend has a row; owner ruling: keep, do not delete). Chow,
//! water, and sunbeam slots are pure nearest-K.

use cloudkitty_core::action::TargetRef;
use cloudkitty_core::element::{ElementId, ElementKind, ElementType};
use cloudkitty_core::grid::{Direction, Position};
use cloudkitty_core::kitty::{Activity, Kitty, KittyId};
use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::world::{FogView, WorldSnapshot};
use cloudkitty_core::Config;

use crate::config::ObservationConfig;

/// Version pinned into policy artifacts (FR-007/FR-016). Schema 3
/// (spec 028): the meow digest became coherent, 183 → 197. Schema 4
/// (spec 033): the say-surface finalized, 197 → 225. Schema 5 (spec 049,
/// the fog wall): permanent by-id kitty rows (4), per-speaker message
/// blocks in place of the global digest, scene age, the water bit, the
/// element memory, 225 → 404.
pub const OBSERVATION_SCHEMA_VERSION: u32 = 5;

/// The message-head kinds (spec 028, finalized by spec 033): every kind a
/// policy can hear and speak — all but the engine-reserved `wait_for_me`
/// (spec 012). Order is normative for the message blocks AND the message
/// head (head index k+1 = HEAD_KINDS[k]; index 0 = Silent): existing kinds
/// keep their positions forever (mew inherits follow_me's, name only), new
/// kinds append. This array is FROZEN through the fog era (ROADMAP
/// principle 5): the reserves (trill, ekekek) exist so future vocabulary
/// experiments are flag flips, never layout moves.
pub const HEAD_KINDS: [MessageKind; 15] = [
    MessageKind::WantEat,
    MessageKind::WantDrink,
    MessageKind::Mew,
    MessageKind::WantPlay,
    MessageKind::WantCuddle,
    MessageKind::Purr,
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

/// The six want-kinds, in `HEAD_KINDS` order: the intensity cells on a
/// friend row (FR-016) follow this order.
pub const WANT_KINDS: [MessageKind; 6] = [
    MessageKind::WantEat,
    MessageKind::WantDrink,
    MessageKind::WantPlay,
    MessageKind::WantCuddle,
    MessageKind::WantBath,
    MessageKind::WantSleep,
];

/// The schema-4 self block, unchanged (FR-026): needs 6, happiness, pos 2,
/// activity 7, partner flag, in-sunbeam, in-water, progress, distress 6,
/// pursuit 2, traits 6.
const SELF_SCHEMA_4: usize = 6 + 1 + 2 + 7 + 1 + 1 + 1 + 1 + 6 + 2 + 6;
/// Per-speaker message block: (recency, rate) per `HEAD_KINDS` kind.
const MSG_BLOCK: usize = HEAD_KINDS.len() * 2;
/// The element memory: (present, dx, dy, staleness) per `ElementType::ALL`
/// kind.
const MEMORY_BLOCK: usize = ElementType::ALL.len() * 4;
/// Self block = schema 4 + own scene age + own message block + memory = 85.
const SELF_BLOCK: usize = SELF_SCHEMA_4 + 1 + MSG_BLOCK + MEMORY_BLOCK;
/// The schema-4 kitty slot, unchanged: present, dx, dy, distance, needs 6,
/// happiness, activity 7, partner flag, is-my-target bit.
const KITTY_SCHEMA_4: usize = 1 + 2 + 1 + 6 + 1 + 7 + 1 + 1;
/// Kitty row = schema 4 + water bit + scene age + message block + want
/// intensities (6) + answers-me bits (4) = 62.
const KITTY_SLOT: usize = KITTY_SCHEMA_4 + 1 + 1 + MSG_BLOCK + WANT_KINDS.len() + HERE_KINDS_LEN;
const HERE_KINDS_LEN: usize = 4;
const CHOW_SLOT: usize = 1 + 2 + 1 + 1;
const WATER_SLOT: usize = 1 + 2 + 1;
const SUNBEAM_SLOT: usize = 1 + 2 + 1 + 1 + 1;
const CRITTER_SLOT: usize = 1 + 2 + 1 + 1 + 4 + 1;
const CLOCK: usize = 1;

/// Frozen normalisers (spec 049 FR-009 / FR-019): scene age is
/// `elapsed / 24`; memory staleness is `(tick − last_seen) / 40`. Literals
/// by ruling — never derived from config at observation time (a repriced
/// durations table must not move the observation's meaning).
pub const SCENE_AGE_NORMALISER: f32 = 24.0;
pub const STALENESS_NORMALISER: f32 = 40.0;

/// Offsets inside the self block and a kitty row
/// (contracts/observation-v5.md), public so the pin and row tests read
/// cells by name rather than by hand-summed literals.
pub mod offsets {
    use super::*;
    /// Self block: own scene age; the own message block; the memory.
    pub const SELF_SCENE_AGE: usize = SELF_SCHEMA_4;
    pub const SELF_MSG_BLOCK: usize = SELF_SCHEMA_4 + 1;
    pub const SELF_MEMORY: usize = SELF_MSG_BLOCK + MSG_BLOCK;
    /// Kitty row: the water bit; scene age; message block; the six want
    /// intensities; the four answers-me bits.
    pub const ROW_WATER_BIT: usize = KITTY_SCHEMA_4;
    pub const ROW_SCENE_AGE: usize = KITTY_SCHEMA_4 + 1;
    pub const ROW_MSG_BLOCK: usize = KITTY_SCHEMA_4 + 2;
    pub const ROW_INTENSITY: usize = ROW_MSG_BLOCK + MSG_BLOCK;
    pub const ROW_ANSWERS_ME: usize = ROW_INTENSITY + WANT_KINDS.len();
    /// Block widths, by name.
    pub const SELF_BLOCK: usize = super::SELF_BLOCK;
    pub const KITTY_SLOT: usize = super::KITTY_SLOT;
    pub const MEMORY_BLOCK: usize = super::MEMORY_BLOCK;
    pub const MSG_BLOCK: usize = super::MSG_BLOCK;
}

/// Per-type token feature widths — the block sizes, exposed for the v3
/// entity tokenizer (spec 030 FR-003) so it derives token widths from this
/// single source rather than restating them. Schema 5 (spec 049): the
/// message-kind token group is gone with the global digest; `memory`,
/// `msg_self` and `msg_kitty` are the sub-block widths the documentation
/// and the tools read.
pub struct BlockWidths {
    pub self_: usize,
    pub kitty: usize,
    pub chow: usize,
    pub water: usize,
    pub sunbeam: usize,
    pub critter: usize,
    pub memory: usize,
    pub msg_self: usize,
    pub msg_kitty: usize,
    pub clock: usize,
}

pub const fn block_widths() -> BlockWidths {
    BlockWidths {
        self_: SELF_BLOCK,
        kitty: KITTY_SLOT,
        chow: CHOW_SLOT,
        water: WATER_SLOT,
        sunbeam: SUNBEAM_SLOT,
        critter: CRITTER_SLOT,
        memory: MEMORY_BLOCK,
        msg_self: MSG_BLOCK,
        msg_kitty: MSG_BLOCK + WANT_KINDS.len() + HERE_KINDS_LEN,
        clock: CLOCK,
    }
}

/// The exact observation length for a slot configuration -- a function of
/// the slot config, never a constant to quote (the served config's slot
/// defaults currently work out to 404; read it from here, don't hardcode).
pub fn observation_len(cfg: &ObservationConfig) -> usize {
    SELF_BLOCK
        + cfg.kitty_slots * KITTY_SLOT
        + cfg.chow_slots * CHOW_SLOT
        + cfg.water_slots * WATER_SLOT
        + cfg.sunbeam_slots * SUNBEAM_SLOT
        + cfg.critter_slots * CRITTER_SLOT
        + CLOCK
}

/// Per-observation mapping from slot indices to concrete identities — the
/// bridge that lets the flat action menu name a specific neighbor (FR-006).
/// Built from the same fog view by the same fill rules as the observation.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TargetTable {
    /// `kitties[k]` is the kitty in row k -- the roster minus the observer,
    /// ascending by id (spec 049 FR-011), whether or not it is seen -- or
    /// None for a vacant row.
    pub kitties: Vec<Option<KittyId>>,
    /// `critters[j]` is the element in critter slot j, or None.
    pub critters: Vec<Option<ElementId>>,
}

impl TargetTable {
    /// Builds the table for `kitty_id`'s observation of its `view`.
    pub fn build(view: &FogView, kitty_id: KittyId, cfg: &ObservationConfig) -> Self {
        debug_assert_eq!(view.observer, kitty_id, "a view is built for its observer");
        let me = view
            .kitty(kitty_id)
            .expect("the observing kitty exists in its own view");
        let (_kitty_target, critter_target) = activity_targets(me, view);

        // Kitty rows: permanent, by id (FR-011). The target-priority fill
        // is not consulted for kitties any more -- every friend has a row
        // -- but `fill_slots` stays whole for critters (FR-015).
        let kitties = view.friend_rows(cfg.kitty_slots);

        let critter_candidates: Vec<(u32, ElementId)> = view
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
/// that no longer exists (or is out of sight) gets no priority — the
/// activity itself is about to be pruned.
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
/// (distance, id). Vacant slots pad with None. Critters only since spec
/// 049 (kitty rows are by id); kept whole by ruling (FR-015).
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

/// A friend row's state for the observer this tick (FR-012).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RowState {
    /// Inside the disc: every field.
    Seen,
    /// Outside the disc, a call inside the digest window: the position of
    /// that call, the message block, nothing else.
    Heard { pos: Position },
    /// Outside the disc and quiet: all zero.
    Silent,
}

/// The row state of `friend` for the view's observer (FR-012), read off
/// the view: seen iff present in it; else heard iff `heard_unseen` lists
/// it; else silent.
pub fn row_state(view: &FogView, friend: KittyId, window: u64) -> RowState {
    if view.kitty(friend).is_some() {
        return RowState::Seen;
    }
    view.heard_unseen(window)
        .into_iter()
        .find(|&(id, _, _)| id == friend)
        .map_or(RowState::Silent, |(_, pos, _)| RowState::Heard { pos })
}

/// Encodes `kitty_id`'s observation of its frozen fog `view`. `episode_clock`
/// is tick/horizon in [0, 1] (0 at deploy, where no episode runs).
pub fn encode_observation(
    view: &FogView,
    kitty_id: KittyId,
    core: &Config,
    cfg: &ObservationConfig,
    episode_clock: f32,
) -> Observation {
    debug_assert_eq!(
        view.observer, kitty_id,
        "a view is encoded for its observer"
    );
    let me = view
        .kitty(kitty_id)
        .expect("the observing kitty exists in its own view");
    let table = TargetTable::build(view, kitty_id, cfg);
    let (kitty_target, critter_target) = activity_targets(me, view);
    let width = view.width as f32;
    let height = view.height as f32;
    let max_distance = (view.width + view.height) as f32;
    let window = core.meow.digest_window_ticks;

    let mut v = Vec::with_capacity(observation_len(cfg));

    // 1. Self block: the schema-4 block, verbatim.
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
    // Tile-derived, unlike its sunbeam neighbor (see the module doc): wet
    // is a fact about the tile, not the activity, and not the pricing. The
    // own tile is inside every disc (FR-005).
    v.push(if water_at(view, me.pos) { 1.0 } else { 0.0 });
    v.push(activity_progress(me, view.tick, core));
    push_distress_flags(&mut v, me);
    match me.pursuit {
        Some(p) => {
            v.push(1.0);
            let stale = view.tick.saturating_sub(p.last_progress()) as f32
                / core.behavior.chase_patience_ticks.max(1) as f32;
            v.push(stale.clamp(0.0, 1.0));
        }
        None => {
            v.push(0.0);
            v.push(0.0);
        }
    }
    push_traits(&mut v, kitty_id, core, cfg);
    debug_assert_eq!(v.len(), SELF_SCHEMA_4);
    // Own scene age (FR-019): elapsed / 24, clamped; 0 with no scene.
    v.push(scene_age(me, view.tick));
    // Own message block (FR-016): recency + rate of my own calls; no
    // intensity cells on the self row (my needs are already here).
    push_message_block(&mut v, view, kitty_id, core, false);
    // Element memory (FR-009): per kind, present, dx, dy relative to the
    // CURRENT position, staleness = (tick − last_seen) / 40, clamped.
    for kind in ElementType::ALL {
        match me.memory[cloudkitty_core::kitty::memory_index(kind)] {
            Some(slot) => {
                v.push(1.0);
                v.push((slot.pos.x as f32 - me.pos.x as f32) / width);
                v.push((slot.pos.y as f32 - me.pos.y as f32) / height);
                let staleness =
                    view.tick.saturating_sub(slot.last_seen) as f32 / STALENESS_NORMALISER;
                v.push(staleness.clamp(0.0, 1.0));
            }
            None => v.extend(std::iter::repeat_n(0.0, 4)),
        }
    }
    debug_assert_eq!(v.len(), SELF_BLOCK);
    let _ = window;

    // 2. Kitty rows: permanent, by id; contents by row state (FR-012).
    for row in &table.kitties {
        let Some(friend) = *row else {
            v.extend(std::iter::repeat_n(0.0, KITTY_SLOT));
            continue;
        };
        match row_state(view, friend, window) {
            RowState::Seen => {
                let other = view.kitty(friend).expect("seen means in the view");
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
                // Knowledge fields (FR-020): the neighbour-in-water bit
                // (tile-derived, as the own-tile bit) and their scene age.
                v.push(if water_at(view, other.pos) { 1.0 } else { 0.0 });
                v.push(scene_age(other, view.tick));
                // Their message block + want intensities (FR-016) and the
                // answers-me bits (FR-041; land with US7 -- 0 until then).
                push_message_block(&mut v, view, friend, core, true);
                v.extend(std::iter::repeat_n(0.0, HERE_KINDS_LEN));
            }
            RowState::Heard { pos } => {
                v.push(0.0);
                v.push((pos.x as f32 - me.pos.x as f32) / width);
                v.push((pos.y as f32 - me.pos.y as f32) / height);
                v.push(me.pos.manhattan_distance(&pos) as f32 / max_distance);
                // Knowledge fields masked: needs, happiness, activity,
                // partner flag, target bit, water bit, scene age.
                v.extend(std::iter::repeat_n(0.0, 6 + 1 + 7 + 1 + 1 + 1 + 1));
                // The message block is live on a heard row (FR-012).
                push_message_block(&mut v, view, friend, core, true);
                v.extend(std::iter::repeat_n(0.0, HERE_KINDS_LEN));
            }
            RowState::Silent => v.extend(std::iter::repeat_n(0.0, KITTY_SLOT)),
        }
    }

    // 3. Element slots over VISIBLE elements (the view holds nothing else).
    // Chow, water, sunbeam: pure nearest-K.
    let chow = nearest_elements(view, me, ElementType::Chow, cfg.chow_slots);
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
    let water = nearest_elements(view, me, ElementType::Water, cfg.water_slots);
    for slot in &water {
        match slot {
            Some(e) => push_element_common(&mut v, me, e, width, height, max_distance),
            None => v.extend(std::iter::repeat_n(0.0, WATER_SLOT)),
        }
    }
    let sunbeams = nearest_elements(view, me, ElementType::Sunbeam, cfg.sunbeam_slots);
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
                let occupied = view.kitties.iter().any(|k| k.pos == e.pos);
                v.push(if occupied { 1.0 } else { 0.0 });
            }
            None => v.extend(std::iter::repeat_n(0.0, SUNBEAM_SLOT)),
        }
    }
    for slot in &table.critters {
        match slot.and_then(|id| view.elements.iter().find(|e| e.id == id)) {
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

    // 4. Episode clock.
    v.push(episode_clock.clamp(0.0, 1.0));

    debug_assert_eq!(v.len(), observation_len(cfg));
    Observation { values: v, table }
}

/// Scene age (spec 049 FR-019/FR-020): the activity clock's elapsed
/// ticks over the frozen 24, clamped to 1; 0 outside a scene. Never read
/// from `[actions] durations` -- a repriced table must not move the
/// observation's meaning.
fn scene_age(kitty: &Kitty, tick: u64) -> f32 {
    kitty
        .activity_clock
        .map(|clock| (clock.elapsed(tick) as f32 / SCENE_AGE_NORMALISER).clamp(0.0, 1.0))
        .unwrap_or(0.0)
}

/// A speaker's message block (spec 049 FR-016): per `HEAD_KINDS` kind,
/// recency = `1 − age / digest_window` of its freshest call of that kind
/// and rate = its calls of that kind inside the window over the most it
/// could have made (`window / cooldown`), both clamped to [0, 1]; then,
/// on friend rows only, the last stamped intensity of its freshest call
/// of each `WANT_KINDS` kind. A call is inside the window iff its age is
/// strictly less than the window, and only START-OF-TICK calls count
/// (`m.tick < tick`, research R5). Reserve kinds read 0 wherever unarmed
/// because nobody speaks them.
fn push_message_block(
    v: &mut Vec<f32>,
    view: &FogView,
    speaker: KittyId,
    core: &Config,
    with_intensity: bool,
) {
    let now = view.tick;
    let window = core.meow.digest_window_ticks.max(1);
    let cooldown = core.meow.recent_window_ticks.max(1);
    let max_calls = (window / cooldown).max(1) as f32;
    // One audibility rule, the view's (FR-016/R5): never re-derived here.
    let audible =
        |m: &&cloudkitty_core::meow::Meow| m.kitty_id == speaker && view.audible(m, window);
    for kind in HEAD_KINDS {
        let mut count = 0u32;
        let mut freshest: Option<u64> = None;
        for m in view
            .recent_meows
            .iter()
            .filter(audible)
            .filter(|m| m.kind == kind)
        {
            count += 1;
            freshest = Some(freshest.map_or(m.tick, |t| t.max(m.tick)));
        }
        let recency = freshest
            .map(|t| (1.0 - (now - t) as f32 / window as f32).clamp(0.0, 1.0))
            .unwrap_or(0.0);
        v.push(recency);
        v.push((count as f32 / max_calls).clamp(0.0, 1.0));
    }
    if with_intensity {
        for kind in WANT_KINDS {
            let freshest = view
                .recent_meows
                .iter()
                .filter(audible)
                .filter(|m| m.kind == kind)
                .max_by(|a, b| a.tick.cmp(&b.tick));
            v.push(freshest.map_or(0.0, |m| m.intensity.clamp(0.0, 1.0)));
        }
    }
}

/// A water element on `pos` in the view (tile-derived, as the own-tile
/// flag has always been).
fn water_at(snapshot: &WorldSnapshot, pos: Position) -> bool {
    snapshot
        .elements
        .iter()
        .any(|e| e.element_type() == ElementType::Water && e.pos == pos)
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
    fn the_default_layout_is_404_values() {
        // Schema 5 (spec 049): self 85 | 4 x 62 | 2 x 5 | 2 x 4 | 2 x 6 |
        // 4 x 10 | clock 1. (History: 197 at schema 3, 225 at schema 4.)
        assert_eq!(observation_len(&ObservationConfig::default()), 404);
    }

    #[test]
    fn the_self_block_is_carried_exactly_once_at_any_slot_config() {
        // Growing a slot count adds slot-sized steps on top of the same
        // single self block (spec 026 US1 scenario 4, re-pinned at 85).
        assert_eq!(SELF_BLOCK, 85, "34 (schema 4) + scene age + 30 + 20");
        assert_eq!(
            KITTY_SLOT, 62,
            "20 (schema 4) + water + scene age + 30 + 6 + 4"
        );
        let cfg = ObservationConfig {
            kitty_slots: ObservationConfig::default().kitty_slots + 2,
            ..ObservationConfig::default()
        };
        assert_eq!(observation_len(&cfg), 404 + 2 * KITTY_SLOT);
    }

    /// The in-water flag's fixed self-block index: needs (6) + happiness +
    /// position (2) + activity one-hot (7) + social flag + in-sunbeam flag.
    /// A layout drift moves the flag and fails these tests loudly.
    const IN_WATER_INDEX: usize = 6 + 1 + 2 + 7 + 1 + 1;

    #[test]
    fn the_in_water_flag_is_tile_occupancy_not_proximity() {
        use cloudkitty_core::element::Element;
        let (mut world, config) = test_world();
        let cfg = ObservationConfig::default();
        let idx = world.kitty_index(1).unwrap();
        let me = world.kitties[idx].pos;

        // Dry: no water anywhere.
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Water);
        let dry = encode_observation(
            &world.snapshot().fog_for(1, config.vision.radius),
            1,
            &config,
            &cfg,
            0.0,
        );
        assert_eq!(dry.values[IN_WATER_INDEX], 0.0, "no water: dry");

        // Water on the neighboring tile must not leak into the flag —
        // schema 1's distance-0 inference is exactly what this replaces.
        world.elements.push(Element {
            id: 9001,
            kind: ElementKind::Water,
            pos: Position::new(me.x + 1, me.y),
            ttl: None,
        });
        let beside = encode_observation(
            &world.snapshot().fog_for(1, config.vision.radius),
            1,
            &config,
            &cfg,
            0.0,
        );
        assert_eq!(
            beside.values[IN_WATER_INDEX], 0.0,
            "water beside is not water underfoot"
        );

        // Underfoot: the tile itself holds water. A configured TTL changes
        // nothing — present in the snapshot is present to the flag.
        world.elements.push(Element {
            id: 9002,
            kind: ElementKind::Water,
            pos: me,
            ttl: Some(300),
        });
        let wet = encode_observation(
            &world.snapshot().fog_for(1, config.vision.radius),
            1,
            &config,
            &cfg,
            0.0,
        );
        assert_eq!(wet.values[IN_WATER_INDEX], 1.0, "water underfoot: wet");
    }

    #[test]
    fn the_in_water_flag_ignores_the_activity() {
        // Tile-derived, unlike the in-sunbeam flag beside it: a kitty
        // grooming on a puddle is wet, whatever it is busy doing.
        use cloudkitty_core::element::Element;
        let (mut world, config) = test_world();
        let cfg = ObservationConfig::default();
        let idx = world.kitty_index(1).unwrap();
        let me = world.kitties[idx].pos;
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Water);
        world.elements.push(Element {
            id: 9003,
            kind: ElementKind::Water,
            pos: me,
            ttl: None,
        });
        world.kitties[idx].activity = Activity::Grooming { target: None };
        world.kitties[idx].activity_clock = Some(ActivityClock::start(0));
        let obs = encode_observation(
            &world.snapshot().fog_for(1, config.vision.radius),
            1,
            &config,
            &cfg,
            0.0,
        );
        assert_eq!(obs.values[IN_WATER_INDEX], 1.0);
        // And the neighboring sunbeam flag stayed activity-derived: not
        // sleeping in a sunbeam, so 0 — the deliberate asymmetry.
        assert_eq!(obs.values[IN_WATER_INDEX - 1], 0.0);
    }

    #[test]
    fn a_distant_groom_target_keeps_its_permanent_row_with_the_bit_set() {
        // Under permanent by-id rows (spec 049 FR-011) the groom target
        // never needs displacing: it owns row (id - 1) whatever the crowd
        // and however far it stands, and the observation's
        // is-activity-target bit marks that row. (Grooming is exactly one
        // of the activities duet_partner() omits — the regression this
        // module exists to prevent.)
        let (mut world, config) = test_world();
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

        let view = world.snapshot().fog_for(1, config.vision.radius);
        let cfg = ObservationConfig::default();
        let table = TargetTable::build(&view, 1, &cfg);
        assert_eq!(
            table.kitties,
            vec![Some(2), Some(3), Some(4), Some(5)],
            "rows by id"
        );
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        let bit_index = SELF_BLOCK + KITTY_SCHEMA_4 - 1;
        assert_eq!(
            obs.values[bit_index], 1.0,
            "row 0 (kitty 2) carries the target bit"
        );
        assert_eq!(
            obs.values[SELF_BLOCK + KITTY_SLOT + KITTY_SCHEMA_4 - 1],
            0.0
        );
    }

    #[test]
    fn kitty_rows_are_by_id_whatever_the_distances() {
        // Spec 049 US2 scenario 1: row k holds friend k + 1's fields --
        // distance plays no part (the schema-4 nearest-K fill is gone).
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
        let k2 = world.kitty_index(2).unwrap();
        world.kitties[k2].pos = Position::new(15, 15); // the farthest, still row 0

        let view = world.snapshot().fog_for(1, 40);
        let table = TargetTable::build(&view, 1, &ObservationConfig::default());
        assert_eq!(table.kitties, vec![Some(2), Some(3), Some(4), Some(5)]);
        // And from kitty 3's seat the same roster minus itself, ascending.
        let view3 = world.snapshot().fog_for(3, 40);
        let table3 = TargetTable::build(&view3, 3, &ObservationConfig::default());
        assert_eq!(table3.kitties, vec![Some(1), Some(2), Some(4), Some(5)]);
    }

    #[test]
    fn encoding_is_deterministic_and_in_bounds() {
        let (world, config) = test_world();
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let cfg = ObservationConfig::default();

        let a = encode_observation(&view, 1, &config, &cfg, 0.25);
        let b = encode_observation(&view, 1, &config, &cfg, 0.25);
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
    // ---- spec 049 T027: permanent by-id rows, row states, memory cells ----

    /// A 20x20 world, five cats (ids 1..5), observer 1 at (10, 10), r = 5.
    fn five_cat_world() -> (cloudkitty_core::World, Config) {
        let mut config = cloudkitty_core::test_support::test_config();
        config.world.width = 20;
        config.world.height = 20;
        config.vision.radius = 5;
        config.kitties = [
            (1u32, 10u32, 10u32),
            (2, 11, 10),
            (3, 0, 0),
            (4, 19, 19),
            (5, 0, 19),
        ]
        .iter()
        .map(|&(id, x, y)| cloudkitty_core::config::KittyConfig {
            id,
            name: format!("K{id}"),
            x,
            y,
            behavior: "needs_driven".into(),
            needs: None,
        })
        .collect();
        config.validate().unwrap();
        let mut world = cloudkitty_core::World::generate(&config);
        world.elements.clear();
        world.tick = 100;
        (world, config)
    }

    fn row(obs: &Observation, k: usize) -> &[f32] {
        &obs.values[SELF_BLOCK + k * KITTY_SLOT..SELF_BLOCK + (k + 1) * KITTY_SLOT]
    }

    #[test]
    fn rows_are_permanent_and_present_toggles_exactly_with_the_disc() {
        // US2 scenarios 1-2: row k = friend k + 1 whatever the distances;
        // friend 4 walks out of the disc and back, its row index unchanged,
        // `present` 1 exactly on the ticks it is inside.
        let (mut world, config) = five_cat_world();
        let cfg = ObservationConfig::default();
        for (x, y, inside) in [
            (13u32, 14u32, true),
            (15, 11, false),
            (14, 10, true),
            (16, 10, false),
        ] {
            let idx = world.kitty_index(4).unwrap();
            world.kitties[idx].pos = Position::new(x, y);
            let view = world.snapshot().fog_for(1, config.vision.radius);
            let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
            assert_eq!(
                obs.table.kitties,
                vec![Some(2), Some(3), Some(4), Some(5)],
                "rows by id"
            );
            let r4 = row(&obs, 2);
            assert_eq!(
                r4[0],
                if inside { 1.0 } else { 0.0 },
                "friend 4 at ({x}, {y}): present"
            );
            if inside {
                assert!(
                    (r4[1] - (x as f32 - 10.0) / 20.0).abs() < 1e-6,
                    "dx to the live position"
                );
                assert!(
                    (r4[3] - ((x as f32 - 10.0).abs() + (y as f32 - 10.0).abs()) / 40.0).abs()
                        < 1e-6
                );
                assert_eq!(
                    r4[10],
                    world.kitty(4).unwrap().happiness / 100.0,
                    "knowledge shown"
                );
            } else {
                assert!(r4.iter().all(|&v| v == 0.0), "silent: all zero");
            }
            // Friend 2, adjacent, is seen on every tick in row 0.
            assert_eq!(row(&obs, 0)[0], 1.0);
        }
    }

    #[test]
    fn a_heard_row_points_at_the_stamped_meow_position_with_knowledge_masked() {
        // US2 scenario 3: friend 3 outside the disc called 12 ticks ago
        // from tile T; its row reads present 0, dx/dy/distance to T
        // (wherever it has walked since), knowledge fields 0.
        use cloudkitty_core::meow::{Meow, MessageKind};
        let (mut world, config) = five_cat_world();
        let cfg = ObservationConfig::default();
        world.recent_meows.push(Meow {
            kitty_id: 3,
            kind: MessageKind::HereWater,
            tick: 88,
            intensity: 0.0,
            pos: Position::new(2, 5),
            reply: false,
        });
        let idx = world.kitty_index(3).unwrap();
        world.kitties[idx].pos = Position::new(0, 0); // walked on since
        world.kitties[idx].happiness = 42.0;
        let view = world.snapshot().fog_for(1, config.vision.radius);
        assert!(view.kitty(3).is_none(), "outside the disc");
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        let r3 = row(&obs, 1);
        assert_eq!(r3[0], 0.0, "present means seen");
        assert!(
            (r3[1] - (2.0 - 10.0) / 20.0).abs() < 1e-6,
            "dx to T, not to the cat"
        );
        assert!((r3[2] - (5.0 - 10.0) / 20.0).abs() < 1e-6, "dy to T");
        assert!((r3[3] - (8.0 + 5.0) / 40.0).abs() < 1e-6, "distance to T");
        assert!(
            r3[4..KITTY_SCHEMA_4].iter().all(|&v| v == 0.0),
            "needs, happiness, activity, flags masked"
        );
        assert_eq!(r3[offsets::ROW_WATER_BIT], 0.0);
        assert_eq!(r3[offsets::ROW_SCENE_AGE], 0.0);
        // Silent friend 5 (no call) and vacant rows are all zero; a lab
        // roster of three leaves row 4 permanently vacant (scenario 5).
        assert!(row(&obs, 3).iter().all(|&v| v == 0.0), "friend 5: silent");
        let mut three = config.clone();
        three.kitties.truncate(3);
        three.validate().unwrap();
        let mut w3 = cloudkitty_core::World::generate(&three);
        w3.elements.clear();
        let view3 = w3.snapshot().fog_for(1, 40);
        let obs3 = encode_observation(&view3, 1, &three, &cfg, 0.0);
        assert_eq!(obs3.table.kitties, vec![Some(2), Some(3), None, None]);
        assert!(row(&obs3, 2).iter().all(|&v| v == 0.0) && row(&obs3, 3).iter().all(|&v| v == 0.0));
        assert_eq!(
            obs3.values.len(),
            404,
            "the slot config does not change per lab"
        );
    }

    #[test]
    fn the_memory_cells_read_the_remembered_tile_with_staleness_over_forty() {
        // FR-009: present, dx/dy to the remembered tile from the CURRENT
        // position, staleness (tick - last_seen)/40 clamped, 40 frozen.
        use cloudkitty_core::kitty::{memory_index, MemorySlot};
        // A 24x24 world (width + height = 48 != 40), so a normaliser
        // derived from the world would read wrong here.
        let (mut world, mut config) = five_cat_world();
        config.world.width = 24;
        config.world.height = 24;
        world.width = 24;
        world.height = 24;
        let cfg = ObservationConfig::default();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].memory[memory_index(ElementType::Chow)] = Some(MemorySlot {
            pos: Position::new(14, 7),
            last_seen: 90,
        });
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        let chow = offsets::SELF_MEMORY + 4 * memory_index(ElementType::Chow);
        assert_eq!(obs.values[chow], 1.0, "present");
        assert!((obs.values[chow + 1] - 4.0 / 24.0).abs() < 1e-6, "dx");
        assert!((obs.values[chow + 2] - (-3.0) / 24.0).abs() < 1e-6, "dy");
        assert!(
            (obs.values[chow + 3] - 10.0 / 40.0).abs() < 1e-6,
            "staleness 10/40"
        );
        let water = offsets::SELF_MEMORY + 4 * memory_index(ElementType::Water);
        assert!(
            obs.values[water..water + 4].iter().all(|&v| v == 0.0),
            "never seen: zero"
        );
        // Clamped at a full traverse and beyond; the normaliser is the
        // frozen literal, never the world's width + height.
        world.kitties[idx].memory[memory_index(ElementType::Chow)] = Some(MemorySlot {
            pos: Position::new(14, 7),
            last_seen: 10,
        });
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(obs.values[chow + 3], 1.0, "90/40 clamps to 1");
        assert_eq!(STALENESS_NORMALISER, 40.0);
    }
    // ---- spec 049 T037: repetition and insistence are fields (US3) ----

    fn meow_at(
        kitty_id: u32,
        kind: MessageKind,
        tick: u64,
        intensity: f32,
    ) -> cloudkitty_core::meow::Meow {
        cloudkitty_core::meow::Meow {
            kitty_id,
            kind,
            tick,
            intensity,
            pos: Position::new(0, 0),
            reply: false,
        }
    }

    fn head_col(kind: MessageKind) -> usize {
        HEAD_KINDS.iter().position(|&k| k == kind).unwrap()
    }

    #[test]
    fn per_speaker_recency_and_rate_cells_tell_three_calls_from_one() {
        // US3 scenarios 1-2, 4, 5: A (id 2, seen) called want_play at
        // t-25, t-15, t-5 (cooldown 10, window 30) -> recency 1 - 5/30,
        // rate 3/3; B (id 3, heard) once at t-5 -> rate 1/3; a call at age
        // exactly 30 contributes nothing; reserve kinds zero everywhere.
        let (mut world, config) = five_cat_world();
        assert_eq!(
            (
                config.meow.recent_window_ticks,
                config.meow.digest_window_ticks
            ),
            (10, 30)
        );
        let t = world.tick; // 100
        for age in [25u64, 15, 5] {
            world
                .recent_meows
                .push(meow_at(2, MessageKind::WantPlay, t - age, 0.5));
        }
        world
            .recent_meows
            .push(meow_at(2, MessageKind::WantPlay, t - 30, 0.9)); // age == window
        world
            .recent_meows
            .push(meow_at(3, MessageKind::WantPlay, t - 5, 0.5));
        // Friend 4 (unseen) spoke exactly one window ago: NOT audible, so
        // its row is silent -- the strict `<` at the window's edge.
        world
            .recent_meows
            .push(meow_at(4, MessageKind::WantEat, t - 30, 0.7));
        let cfg = ObservationConfig::default();
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        let col = offsets::ROW_MSG_BLOCK + 2 * head_col(MessageKind::WantPlay);
        let a = row(&obs, 0);
        assert!((a[col] - (1.0 - 5.0 / 30.0)).abs() < 1e-6, "A recency");
        assert!(
            (a[col + 1] - 1.0).abs() < 1e-6,
            "A rate 3/3 -- the age-30 call is outside"
        );
        let b = row(&obs, 1);
        assert_eq!(b[0], 0.0, "B is heard, not seen");
        assert!((b[col] - (1.0 - 5.0 / 30.0)).abs() < 1e-6, "B recency");
        assert!(
            (b[col + 1] - 1.0 / 3.0).abs() < 1e-6,
            "B rate 1/3: distinguishable from A"
        );
        assert!(
            row(&obs, 2).iter().all(|&x| x == 0.0),
            "friend 4: a call at age == window is silence"
        );
        for kind in [MessageKind::Trill, MessageKind::Ekekek] {
            let c = offsets::ROW_MSG_BLOCK + 2 * head_col(kind);
            for k in 0..4 {
                assert_eq!(row(&obs, k)[c], 0.0);
                assert_eq!(row(&obs, k)[c + 1], 0.0);
            }
            assert_eq!(
                obs.values[offsets::SELF_MSG_BLOCK + 2 * head_col(kind)],
                0.0
            );
        }
        // Nobody's own block reflects another speaker's calls.
        assert_eq!(
            obs.values[offsets::SELF_MSG_BLOCK + 2 * head_col(MessageKind::WantPlay)],
            0.0
        );
    }

    #[test]
    fn the_observers_own_block_carries_only_its_own_calls() {
        // US3 scenario 3: my here_food at t-2 reads recency 1 - 2/30, rate
        // 1/3 in the SELF block and in no kitty row.
        let (mut world, config) = five_cat_world();
        let t = world.tick;
        world
            .recent_meows
            .push(meow_at(1, MessageKind::HereFood, t - 2, 0.0));
        let cfg = ObservationConfig::default();
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        let sc = offsets::SELF_MSG_BLOCK + 2 * head_col(MessageKind::HereFood);
        assert!((obs.values[sc] - (1.0 - 2.0 / 30.0)).abs() < 1e-6);
        assert!((obs.values[sc + 1] - 1.0 / 3.0).abs() < 1e-6);
        let rc = offsets::ROW_MSG_BLOCK + 2 * head_col(MessageKind::HereFood);
        for k in 0..4 {
            assert_eq!(row(&obs, k)[rc], 0.0, "row {k} does not carry my call");
        }
        // And a same-tick call is not yet audible (start-of-tick buffer).
        world
            .recent_meows
            .push(meow_at(1, MessageKind::HereWater, t, 0.0));
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(
            obs.values[offsets::SELF_MSG_BLOCK + 2 * head_col(MessageKind::HereWater)],
            0.0
        );
    }

    #[test]
    fn want_intensity_cells_carry_the_last_stamp_seen_or_heard_and_expire_with_the_window() {
        // US3 scenario 6: A's last want_eat stamped 0.62 reads 0.62 in A's
        // row whether A is seen or heard; outside the window 0; here-kinds
        // have no intensity cell.
        let (mut world, config) = five_cat_world();
        let t = world.tick;
        world
            .recent_meows
            .push(meow_at(2, MessageKind::WantEat, t - 20, 0.40));
        world
            .recent_meows
            .push(meow_at(2, MessageKind::WantEat, t - 8, 0.62));
        let cfg = ObservationConfig::default();
        let cell = offsets::ROW_INTENSITY
            + WANT_KINDS
                .iter()
                .position(|&k| k == MessageKind::WantEat)
                .unwrap();
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(row(&obs, 0)[0], 1.0, "A is seen");
        assert!(
            (row(&obs, 0)[cell] - 0.62).abs() < 1e-6,
            "the freshest stamp, seen"
        );
        let idx = world.kitty_index(2).unwrap();
        world.kitties[idx].pos = Position::new(19, 0); // out of sight, heard
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(row(&obs, 0)[0], 0.0, "A is heard");
        assert!(
            (row(&obs, 0)[cell] - 0.62).abs() < 1e-6,
            "the freshest stamp, heard"
        );
        world.tick = t + 40; // both calls outside the window
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert!(
            row(&obs, 0).iter().all(|&x| x == 0.0),
            "silent: nothing in the window"
        );
        assert_eq!(
            offsets::ROW_INTENSITY - offsets::ROW_MSG_BLOCK,
            2 * HEAD_KINDS.len(),
            "here-kinds carry recency + rate only; the six intensity cells follow"
        );
    }

    // ---- spec 049 T041: scene age and the wet neighbour (US4) ----

    #[test]
    fn scene_age_reads_elapsed_over_a_frozen_twenty_four() {
        // US4 scenarios 1-2, 4: 12 ticks in -> 0.5, 30 -> 1.0, no scene ->
        // 0; a seen friend 6 ticks in -> 0.25; and 24 stays 24 under a
        // repriced durations table.
        let (mut world, mut config) = five_cat_world();
        let t = world.tick;
        let me = world.kitty_index(1).unwrap();
        let friend = world.kitty_index(2).unwrap();
        let cfg = ObservationConfig::default();
        for (elapsed, expect) in [(12u64, 0.5f32), (30, 1.0), (60, 1.0)] {
            world.kitties[me].activity = Activity::Grooming { target: None };
            world.kitties[me].activity_clock = Some(ActivityClock::start(t + 1 - elapsed));
            let view = world.snapshot().fog_for(1, config.vision.radius);
            let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
            assert!(
                (obs.values[offsets::SELF_SCENE_AGE] - expect).abs() < 1e-6,
                "{elapsed} ticks in"
            );
        }
        world.kitties[me].activity = Activity::Idle;
        world.kitties[me].activity_clock = None;
        world.kitties[friend].activity = Activity::Grooming { target: None };
        world.kitties[friend].activity_clock = Some(ActivityClock::start(t + 1 - 6));
        config.actions.durations.sleep.max = 200; // a repriced table changes nothing
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(obs.values[offsets::SELF_SCENE_AGE], 0.0, "no scene: 0");
        assert!(
            (row(&obs, 0)[offsets::ROW_SCENE_AGE] - 0.25).abs() < 1e-6,
            "a seen friend 6 ticks in"
        );
        assert_eq!(SCENE_AGE_NORMALISER, 24.0);
    }

    #[test]
    fn the_neighbour_in_water_bit_and_scene_age_are_seen_only() {
        // US4 scenario 3 + FR-012: a seen friend on a water tile reads 1;
        // the same friend outside the disc reads 0 there whatever its tile.
        use cloudkitty_core::element::Element;
        let (mut world, config) = five_cat_world();
        let friend = world.kitty_index(2).unwrap();
        world.kitties[friend].activity = Activity::Grooming { target: None };
        world.kitties[friend].activity_clock = Some(ActivityClock::start(world.tick - 5));
        world.push_element(Element {
            id: 700,
            kind: ElementKind::Water,
            pos: Position::new(11, 10),
            ttl: None,
        });
        let cfg = ObservationConfig::default();
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(row(&obs, 0)[offsets::ROW_WATER_BIT], 1.0, "seen and wet");
        assert!(row(&obs, 0)[offsets::ROW_SCENE_AGE] > 0.0);
        // Walk the friend (and its pond) out of the disc but keep it heard.
        world.kitties[friend].pos = Position::new(19, 0);
        world.elements[0].pos = Position::new(19, 0);
        world
            .recent_meows
            .push(meow_at(2, MessageKind::Mew, world.tick - 1, 0.0));
        let view = world.snapshot().fog_for(1, config.vision.radius);
        let obs = encode_observation(&view, 1, &config, &cfg, 0.0);
        assert_eq!(row(&obs, 0)[0], 0.0, "heard");
        assert_eq!(
            row(&obs, 0)[offsets::ROW_WATER_BIT],
            0.0,
            "knowledge masked"
        );
        assert_eq!(
            row(&obs, 0)[offsets::ROW_SCENE_AGE],
            0.0,
            "knowledge masked"
        );
        assert!(
            row(&obs, 0)[offsets::ROW_MSG_BLOCK + 2 * head_col(MessageKind::Mew)] > 0.0,
            "the block is live"
        );
    }
}
