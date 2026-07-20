//! The world and its tick loop.
//!
//! Article V fixes the order of a tick, and [`World::tick`] is the only place that
//! order is expressed:
//!
//! 1. snapshot the world; every behavior decides against that same snapshot
//! 2. apply actions in stable kitty-id order ("cats act first")
//! 3. environment phase: critters move, things expire, the world restocks
//! 4. needs rise, happiness is recomputed, distress is recorded, invariants assert
//! 5. publish the new state
//!
//! Note what this type does *not* have: any way to remove a kitty. `kitties` is a
//! plain `Vec` that only ever grows at world creation (Article II).

use std::sync::Arc;

use serde::{Deserialize, Serialize};

use crate::action;
use crate::action::TargetRef;
use crate::behavior::{gather_decisions, BehaviorRegistry};
use crate::config::Config;
use crate::element::{Element, ElementId, ElementKind, ElementType};
use crate::events::{ActivityEnd, ActivityLog, DistressEvent, DistressLog};
use crate::grid::{Direction, Position};
use crate::invariants;
use crate::kitty::{Activity, Kitty, KittyId};
use crate::meow::Meow;
use crate::needs::{happiness, NeedKind};
use crate::rng::SimRng;
use crate::spawn;

/// The complete simulation state. Serialized whole for persistence (RNG included,
/// so a restart continues the same future).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct World {
    pub width: u32,
    pub height: u32,
    pub tick: u64,
    /// Ordered by id. Never shrinks.
    pub kitties: Vec<Kitty>,
    pub elements: Vec<Element>,
    pub recent_meows: Vec<Meow>,
    pub distress: DistressLog,
    /// Finished activities with the true spans they ran (spec 006). Serde
    /// defaulted so snapshots written before the log existed still load.
    #[serde(default)]
    pub activity_log: ActivityLog,
    pub rng: SimRng,
    pub config_fingerprint: String,
    next_element_id: ElementId,
}

/// The read-only view handed to behaviors and pushed to viewers.
///
/// Greebles are present here like any other element: their invisibility is a
/// rendering rule in the client, never a filter in the engine or the API.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldSnapshot {
    pub width: u32,
    pub height: u32,
    pub tick: u64,
    pub kitties: Vec<Kitty>,
    pub elements: Vec<Element>,
    pub recent_meows: Vec<Meow>,
}

impl World {
    /// Builds a fresh world from configuration. Assumes `config.validate()` has
    /// already passed.
    pub fn generate(config: &Config) -> Self {
        let mut world = World {
            width: config.world.width,
            height: config.world.height,
            tick: 0,
            kitties: Vec::new(),
            elements: Vec::new(),
            recent_meows: Vec::new(),
            distress: DistressLog::new(config.events.distress_retention),
            activity_log: ActivityLog::new(config.events.activity_retention),
            rng: SimRng::from_seed(config.world.seed),
            config_fingerprint: config.fingerprint(),
            next_element_id: 1,
        };

        for kc in &config.kitties {
            world.kitties.push(Kitty::new(
                kc.id,
                kc.name.clone(),
                kc.position(),
                kc.behavior.clone(),
            ));
        }
        world.kitties.sort_by_key(|k| k.id);

        // Stock the world to each type's minimum before the first tick.
        spawn::ensure_minimums(&mut world, config);

        for kitty in &mut world.kitties {
            kitty.happiness = happiness(
                &kitty.needs,
                &config.happiness.weights,
                config.happiness.floor,
            );
        }

        world
    }

    pub fn snapshot(&self) -> WorldSnapshot {
        WorldSnapshot {
            width: self.width,
            height: self.height,
            tick: self.tick,
            kitties: self.kitties.clone(),
            elements: self.elements.clone(),
            recent_meows: self.recent_meows.clone(),
        }
    }

    /// Advances the world one tick and returns the newly published state.
    pub async fn tick(
        &mut self,
        registry: &BehaviorRegistry,
        config: &Arc<Config>,
    ) -> Arc<WorldSnapshot> {
        // Phase 1: everyone decides against the same start-of-tick snapshot.
        let decisions = gather_decisions(self, registry, config).await;

        // Phase 2: apply in stable kitty-id order. Validation happens here, against
        // the world as it stands when the action lands -- so the first cat to reach
        // the last serving gets it and the second one simply idles.
        for (kitty_id, proposal) in decisions {
            // An activity whose counterpart is gone ends before anything else
            // happens (spec 006 FR-010): the world moved on, and the kitty's
            // proposal gets its normal hearing.
            self.prune_dead_activity(kitty_id);
            let validated = action::validate(self, kitty_id, proposal, config);
            // Duration enforcement (spec 006): inside an activity's minimum the
            // engine continues the scene whatever was proposed; past it, a
            // different action lawfully interrupts (ending a duet for both).
            let enforced = self.enforce_durations(kitty_id, validated, config);
            // Record what actually happened, not what was proposed: the viewer's
            // "doing" line must never claim an action the engine refused --
            // and on continuation ticks it truthfully repeats the activity.
            if let Some(idx) = self.kitty_index(kitty_id) {
                self.kitties[idx].last_action = Some(enforced);
            }
            action::apply(self, kitty_id, enforced, config);
            self.update_pursuit(kitty_id, enforced, config);
        }

        // Phase 2, closing step: activities that finished their job this tick
        // end here, once relief has landed for everyone (spec 006).
        self.resolve_activity_ends(config);

        // Phase 3: the environment resolves.
        self.environment_phase(config);

        // Phase 4: needs rise, happiness follows, distress is noted, invariants hold.
        self.advance_needs(config);
        self.record_distress(config);
        self.tick += 1;
        self.prune_transient(config);

        invariants::assert_or_report(self, config);

        // Phase 5: publish.
        Arc::new(self.snapshot())
    }

    /// Ends the kitty's activity, and its duet partner's with it -- a duet
    /// never survives one-sided, whichever way it ends (spec 006 FR-009).
    ///
    /// Every engine-side activity end flows through here, which is what makes
    /// the activity log complete: each cleared scene records one event with
    /// the true span its clock witnessed, readable long after served
    /// snapshots have forgotten the final tick.
    fn end_activity(&mut self, kitty_id: KittyId) {
        let partner = self.kitty(kitty_id).and_then(|k| k.activity.duet_partner());
        for id in std::iter::once(kitty_id).chain(partner) {
            if let Some(idx) = self.kitty_index(id) {
                if let Some(clock) = self.kitties[idx].activity_clock {
                    self.activity_log.record(ActivityEnd {
                        kitty_id: id,
                        activity: self.kitties[idx].activity,
                        started: clock.started,
                        ended: clock.applied,
                    });
                }
                self.kitties[idx].clear_activity();
            }
        }
    }

    /// Whether `other` is bound in a duet back to `me`.
    fn reciprocal_duet(&self, me: KittyId, other: KittyId) -> bool {
        self.kitty(other)
            .map(|k| k.activity.duet_partner() == Some(me))
            .unwrap_or(false)
    }

    /// Spec 006 FR-010: an activity whose counterpart is gone -- a critter
    /// expired or scurried out of reach, a groomed friend who walked away, a
    /// water source that dried up -- ends immediately, minimum notwithstanding.
    /// Run at the top of the kitty's apply slot so its proposal, made against
    /// the start-of-tick snapshot, still gets a normal hearing.
    fn prune_dead_activity(&mut self, kitty_id: KittyId) {
        let Some(kitty) = self.kitty(kitty_id) else {
            return;
        };
        if kitty.activity_clock.is_none() {
            return;
        }
        let pos = kitty.pos;
        let counterpart_gone = match kitty.activity {
            Activity::Idle
            | Activity::Eating
            | Activity::Sleeping { .. }
            | Activity::Playing { target: None }
            | Activity::Grooming { target: None }
            | Activity::Resting { with_friend: None } => false,
            // (An emptied or expired bowl is the meal's own end rule, not a
            // vanished counterpart -- see resolve_activity_ends.)
            Activity::Drinking => self.adjacent_element(pos, ElementType::Water).is_none(),
            Activity::Playing {
                target: Some(TargetRef::Element { id }),
            } => self
                .element(id)
                .map(|e| !pos.is_adjacent(&e.pos))
                .unwrap_or(true),
            Activity::Playing {
                target: Some(TargetRef::Kitty { id }),
            } => !self.reciprocal_duet(kitty_id, id),
            Activity::Resting {
                with_friend: Some(id),
            } => !self.reciprocal_duet(kitty_id, id),
            Activity::Grooming { target: Some(id) } => !self.is_available_friend(kitty_id, id),
        };
        if counterpart_gone {
            self.end_activity(kitty_id);
        }
    }

    /// Spec 006 FR-003/004: inside an activity's minimum the engine continues
    /// the scene whatever the behavior proposed; between minimum and maximum a
    /// different validated action lawfully interrupts (ending a duet for both
    /// sides in this very slot); a proposal that continues the activity is
    /// normalized to the continuation action so `last_action` reads true.
    fn enforce_durations(
        &mut self,
        kitty_id: KittyId,
        validated: crate::action::Action,
        config: &Config,
    ) -> crate::action::Action {
        let Some(kitty) = self.kitty(kitty_id) else {
            return validated;
        };
        let Some(clock) = kitty.activity_clock else {
            return validated;
        };
        let activity = kitty.activity;
        // Both are `None` exactly for Idle, and an Idle kitty carries no
        // clock (strict invariant) -- destructured together so a future
        // unbounded activity fails to compile here instead of silently
        // borrowing a phantom minimum.
        let (Some(continuation), Some(bounds)) = (
            activity.continuation(),
            activity.bounds(&config.actions.durations),
        ) else {
            return validated;
        };
        if activity.is_continued_by(&validated) {
            return continuation;
        }
        if clock.serviced_before(self.tick) < bounds.min {
            return continuation;
        }
        self.end_activity(kitty_id);
        validated
    }

    /// Spec 006 FR-005/006/008: the closing step of the apply phase. Every
    /// ongoing activity is examined -- by clock presence, never by whether
    /// effects landed this tick, so a paused meal stays reachable -- and ends
    /// when it has run its maximum, or has met its minimum with its governing
    /// need at 0 (either partner's, for a duet) or its bowl empty.
    fn resolve_activity_ends(&mut self, config: &Config) {
        let tick = self.tick;

        // Index iteration is safe and sufficient: kitties never leave the vec
        // (Article II), and ending a duet clears the partner's clock, so the
        // clock guard below already skips a resolved partner on its own turn.
        for i in 0..self.kitties.len() {
            let kitty = &self.kitties[i];
            let id = kitty.id;
            let Some(clock) = kitty.activity_clock else {
                continue;
            };
            let activity = kitty.activity;
            let Some(bounds) = activity.bounds(&config.actions.durations) else {
                continue;
            };
            let elapsed = clock.elapsed(tick);

            let need_zero = |kind: NeedKind, of: &Kitty| of.needs.get(kind) <= 0.0;
            // The governing need (one mapping, on Activity) ends the scene at
            // 0 -- read off the friend being groomed (a missing friend also
            // ends it), and off *either* side of a duet. An eating kitty's
            // emptied or vanished bowl is the meal's own extra way out.
            let governed_done = match activity.governing_need() {
                None => false,
                Some(need) => {
                    let subject_done = match activity {
                        Activity::Grooming { target: Some(f) } => self
                            .kitty(f)
                            .map(|friend| need_zero(need, friend))
                            .unwrap_or(true),
                        _ => need_zero(need, kitty),
                    };
                    subject_done
                        || activity
                            .duet_partner()
                            .and_then(|p| self.kitty(p))
                            .map(|partner| need_zero(need, partner))
                            .unwrap_or(false)
                }
            };
            let out_of_chow = matches!(activity, Activity::Eating)
                && self.adjacent_stocked_chow(kitty.pos).is_none();
            let done_naturally = elapsed >= bounds.min && (governed_done || out_of_chow);

            if elapsed >= bounds.max || done_naturally {
                self.end_activity(id);
            }
        }
    }

    /// Chase bookkeeping, run after each kitty's action is applied. The engine
    /// records only facts -- which target, since when, how close it got -- and
    /// moves a pursuit that ran out its patience without closing into the
    /// abandoned list, where it stays excluded from re-selection until its
    /// window expires. Behaviors read these facts; none of them can write them.
    fn update_pursuit(
        &mut self,
        kitty_id: KittyId,
        applied: crate::action::Action,
        config: &Config,
    ) {
        use crate::action::Action;
        use crate::kitty::{AbandonedChase, Pursuit};

        let tick = self.tick;
        let Some(idx) = self.kitty_index(kitty_id) else {
            return;
        };

        // Expired exclusions leave the books here, so the list stays tiny.
        self.kitties[idx]
            .abandoned_chases
            .retain(|a| a.until > tick);

        // A pursuit whose target no longer exists is over, not abandoned --
        // there is nothing left to avoid.
        if let Some(p) = self.kitties[idx].pursuit {
            if self.target_pos(p.target).is_none() {
                self.kitties[idx].pursuit = None;
            }
        }

        let kitty_pos = self.kitties[idx].pos;
        let pursuit = self.kitties[idx].pursuit;

        // Whether the standing pursuit has gone `chase_patience_ticks` without
        // gaining ground -- the definition of a chase not working. Measured
        // from the last improvement, never by comparing current distance to the
        // best-ever: those are equal exactly when the cat is doing as well as it
        // ever has, which would condemn a chase at the moment it arrives.
        let pursuit_is_stale = pursuit
            .map(|p| tick.saturating_sub(p.last_progress()) >= config.behavior.chase_patience_ticks)
            .unwrap_or(false);

        match applied {
            Action::Chase(target) => {
                // Switching away from a stale chase is an abandonment too --
                // without this, hopping between two uncatchable greebles would
                // launder each one's staleness away (analyze finding I1).
                if let Some(p) = pursuit {
                    if p.target != target && pursuit_is_stale {
                        self.kitties[idx].abandoned_chases.push(AbandonedChase {
                            target: p.target,
                            until: tick + config.behavior.chase_exclusion_ticks,
                        });
                    }
                }
                let Some(target_pos) = self.target_pos(target) else {
                    self.kitties[idx].pursuit = None;
                    return;
                };
                let distance = kitty_pos.chebyshev_distance(&target_pos);
                self.kitties[idx].pursuit = Some(match pursuit {
                    Some(p) if p.target == target => Pursuit {
                        target,
                        started: p.started,
                        closest: p.closest.min(distance),
                        // Gaining ground resets the patience clock: a long
                        // chase that is still working is not a hopeless one.
                        improved_at: if distance < p.closest {
                            tick
                        } else {
                            p.improved_at
                        },
                    },
                    _ => Pursuit {
                        target,
                        started: tick,
                        closest: distance,
                        improved_at: tick,
                    },
                });
            }

            // Catching the thing you were chasing ends the pursuit happily.
            Action::Play {
                target: Some(target),
            } if pursuit.map(|p| p.target == target).unwrap_or(false) => {
                self.kitties[idx].pursuit = None;
            }

            // Any other action: the pursuit survives a mere detour (an
            // opportunistic drink must not reset the patience clock), but one
            // that has run out its patience without ever closing is written
            // off, and its target excluded for a while.
            _ => {
                if let Some(p) = pursuit {
                    if pursuit_is_stale {
                        self.kitties[idx].abandoned_chases.push(AbandonedChase {
                            target: p.target,
                            until: tick + config.behavior.chase_exclusion_ticks,
                        });
                        self.kitties[idx].pursuit = None;
                    }
                }
            }
        }
    }

    fn target_pos(&self, target: crate::action::TargetRef) -> Option<Position> {
        match target {
            crate::action::TargetRef::Element { id } => self.element(id).map(|e| e.pos),
            crate::action::TargetRef::Kitty { id } => self.kitty(id).map(|k| k.pos),
        }
    }

    fn environment_phase(&mut self, config: &Config) {
        self.move_critters();
        self.expire_elements();
        spawn::ensure_minimums(self, config);
        spawn::safeguard(self, config);
    }

    /// Bugs plod one tile every other tick; greebles skitter one or two tiles every
    /// tick and change their minds constantly.
    fn move_critters(&mut self) {
        let tick = self.tick;
        let (width, height) = (self.width, self.height);

        for idx in 0..self.elements.len() {
            match self.elements[idx].kind {
                ElementKind::Bug => {
                    if !self.elements[idx].bug_moves_this_tick(tick) {
                        continue;
                    }
                    let dir = *self
                        .rng
                        .choose(&Direction::ALL)
                        .expect("Direction::ALL is never empty");
                    self.try_step_element(idx, dir, width, height);
                }
                ElementKind::Greeble { heading } => {
                    // ~60% of the time a greeble picks a new direction, which is
                    // what makes it look erratic rather than merely fast.
                    let heading = if self.rng.gen_bool(0.6) {
                        *self
                            .rng
                            .choose(&Direction::ALL)
                            .expect("Direction::ALL is never empty")
                    } else {
                        heading
                    };
                    if let Some(el) = self.elements.get_mut(idx) {
                        el.kind = ElementKind::Greeble { heading };
                    }
                    let steps = if self.rng.gen_bool(0.5) { 2 } else { 1 };
                    for _ in 0..steps {
                        self.try_step_element(idx, heading, width, height);
                    }
                }
                _ => {}
            }
        }
    }

    /// Moves an element one tile if the destination is on the grid and no other
    /// element already sits there.
    fn try_step_element(&mut self, idx: usize, dir: Direction, width: u32, height: u32) {
        let Some(el) = self.elements.get(idx) else {
            return;
        };
        let Some(dest) = el.pos.step(dir, width, height) else {
            return;
        };
        let occupied = self
            .elements
            .iter()
            .enumerate()
            .any(|(i, other)| i != idx && other.pos == dest);
        if !occupied {
            if let Some(el) = self.elements.get_mut(idx) {
                el.pos = dest;
            }
        }
    }

    fn expire_elements(&mut self) {
        for el in &mut self.elements {
            el.tick_ttl();
        }
        // Article II in negative space: this is the only retain() over a population
        // in the engine, and it operates on elements.
        self.elements.retain(|el| !el.is_expired());
    }

    fn advance_needs(&mut self, config: &Config) {
        for kitty in &mut self.kitties {
            for kind in NeedKind::ALL {
                // Per-kitty override when configured, global rate otherwise.
                kitty.needs.add(kind, config.need_rate_for(kitty.id, kind));
            }
            let previous = kitty.happiness;
            let current = happiness(
                &kitty.needs,
                &config.happiness.weights,
                config.happiness.floor,
            );
            kitty.happiness_rose = current > previous;
            kitty.happiness = current;
        }
    }

    /// Edge-triggered: a need records one event when it crosses the threshold and
    /// stays quiet until it drops back below and crosses again.
    fn record_distress(&mut self, config: &Config) {
        let threshold = config.thresholds.distress;
        let tick = self.tick;
        let mut new_events = Vec::new();

        for kitty in &mut self.kitties {
            for kind in NeedKind::ALL {
                let value = kitty.needs.get(kind);
                if value >= threshold {
                    if kitty.in_distress.insert(kind) {
                        kitty.distress_since.insert(kind, tick);
                        new_events.push(DistressEvent {
                            kitty_id: kitty.id,
                            need: kind,
                            tick,
                        });
                    } else {
                        // Self-heal: a world resumed from a pre-004 snapshot
                        // arrives with distress but no start ticks; ages count
                        // from the resume rather than being invented.
                        kitty.distress_since.entry(kind).or_insert(tick);
                    }
                } else {
                    kitty.in_distress.remove(&kind);
                    kitty.distress_since.remove(&kind);
                }
            }
        }

        for event in new_events {
            self.distress.record(event);
        }
    }

    /// Keeps the transient parts of the world bounded so a long-running sandbox
    /// does not grow without limit.
    fn prune_transient(&mut self, config: &Config) {
        let window = config.meow.recent_window_ticks;
        let cutoff = self.tick.saturating_sub(window);
        self.recent_meows.retain(|m| m.tick >= cutoff);
        for kitty in &mut self.kitties {
            kitty.prune_meow_cooldowns(self.tick);
        }
    }

    // ---- accessors -------------------------------------------------------

    pub fn kitty_index(&self, id: KittyId) -> Option<usize> {
        self.kitties.iter().position(|k| k.id == id)
    }

    pub fn kitty(&self, id: KittyId) -> Option<&Kitty> {
        self.kitties.iter().find(|k| k.id == id)
    }

    pub fn kitty_at(&self, pos: Position) -> Option<&Kitty> {
        self.kitties.iter().find(|k| k.pos == pos)
    }

    pub fn element(&self, id: ElementId) -> Option<&Element> {
        self.elements.iter().find(|e| e.id == id)
    }

    pub fn element_mut(&mut self, id: ElementId) -> Option<&mut Element> {
        self.elements.iter_mut().find(|e| e.id == id)
    }

    pub fn element_at(&self, pos: Position) -> Option<&Element> {
        self.elements.iter().find(|e| e.pos == pos)
    }

    /// The nearest element of `kind` on or beside `pos`, preferring the closest.
    pub fn adjacent_element(&self, pos: Position, kind: ElementType) -> Option<&Element> {
        self.elements
            .iter()
            .filter(|e| e.element_type() == kind && pos.is_adjacent(&e.pos))
            .min_by_key(|e| (pos.chebyshev_distance(&e.pos), e.id))
    }

    /// The bowl a kitty at `pos` would eat from, if it still holds a serving.
    ///
    /// One predicate, three consumers -- validation of an `Eat` proposal, the
    /// per-tick meal continuation, and the end-of-meal rule -- so "which bowl,
    /// and is it usable" can never quietly mean three different things.
    /// Deliberately the *nearest* adjacent bowl filtered for servings, not
    /// the nearest stocked one: a cat at an empty bowl beside a fuller one
    /// pauses (and then ends) rather than stretching across.
    pub fn adjacent_stocked_chow(&self, pos: Position) -> Option<&Element> {
        self.adjacent_element(pos, ElementType::Chow)
            .filter(|e| matches!(e.kind, ElementKind::Chow { servings } if servings > 0))
    }

    pub fn nearest_element(&self, pos: Position, kind: ElementType) -> Option<&Element> {
        self.elements
            .iter()
            .filter(|e| e.element_type() == kind)
            .min_by_key(|e| (pos.chebyshev_distance(&e.pos), e.id))
    }

    pub fn count_of(&self, kind: ElementType) -> u32 {
        self.elements
            .iter()
            .filter(|e| e.element_type() == kind)
            .count() as u32
    }

    /// Both sides of a prospective interaction, resolved once. `None` when
    /// either kitty is missing or the "friend" is the kitty itself.
    fn friend_pair(&self, me: KittyId, friend: KittyId) -> Option<(&Kitty, &Kitty)> {
        if me == friend {
            return None;
        }
        Some((self.kitty(me)?, self.kitty(friend)?))
    }

    /// A friend is any other kitty; "available" adds the adjacency an interaction
    /// needs.
    pub fn is_available_friend(&self, me: KittyId, friend: KittyId) -> bool {
        self.friend_pair(me, friend)
            .map(|(a, b)| a.pos.is_adjacent(&b.pos))
            .unwrap_or(false)
    }

    /// A friend who can be drawn into a duet right now: available *and* doing
    /// nothing. A kitty mid-activity cannot be conscripted out of it (its own
    /// minimum would be broken), and a sleeping cat is never yanked awake to
    /// cuddle. Governs cuddle and social play; co-sleeping and grooming keep
    /// the plain availability rule because they bind nobody.
    pub fn is_conscriptable_friend(&self, me: KittyId, friend: KittyId) -> bool {
        // "Doing nothing" is one check, not two: the strict pairing invariant
        // (clock present exactly when an activity is in progress) makes the
        // clock alone authoritative.
        self.friend_pair(me, friend)
            .map(|(a, b)| a.pos.is_adjacent(&b.pos) && b.activity_clock.is_none())
            .unwrap_or(false)
    }

    pub fn push_element(&mut self, element: Element) {
        self.next_element_id = self.next_element_id.max(element.id + 1);
        self.elements.push(element);
    }

    pub(crate) fn allocate_element_id(&mut self) -> ElementId {
        let id = self.next_element_id;
        self.next_element_id = self.next_element_id.wrapping_add(1).max(1);
        id
    }

    /// Tiles with no element on them. Kitties do not block element spawning --
    /// sharing a tile is how eating, drinking and sunbathing work.
    pub(crate) fn free_element_tiles(&self) -> Vec<Position> {
        let occupied: std::collections::BTreeSet<Position> =
            self.elements.iter().map(|e| e.pos).collect();
        let mut free = Vec::new();
        for y in 0..self.height {
            for x in 0..self.width {
                let pos = Position::new(x, y);
                if !occupied.contains(&pos) {
                    free.push(pos);
                }
            }
        }
        free
    }
}

impl WorldSnapshot {
    pub fn kitty(&self, id: KittyId) -> Option<&Kitty> {
        self.kitties.iter().find(|k| k.id == id)
    }

    pub fn others<'a>(&'a self, me: KittyId) -> impl Iterator<Item = &'a Kitty> + 'a {
        self.kitties.iter().filter(move |k| k.id != me)
    }

    pub fn elements_of(&self, kind: ElementType) -> impl Iterator<Item = &Element> {
        self.elements
            .iter()
            .filter(move |e| e.element_type() == kind)
    }

    pub fn critters(&self) -> impl Iterator<Item = &Element> {
        self.elements
            .iter()
            .filter(|e| e.element_type().is_critter())
    }

    pub fn element_at(&self, pos: Position) -> Option<&Element> {
        self.elements.iter().find(|e| e.pos == pos)
    }

    pub fn nearest_element(&self, pos: Position, kind: ElementType) -> Option<&Element> {
        self.elements
            .iter()
            .filter(|e| e.element_type() == kind)
            .min_by_key(|e| (pos.chebyshev_distance(&e.pos), e.id))
    }

    /// Nearest bug or greeble. Kitties perceive greebles perfectly well, even
    /// though nobody watching can see them.
    pub fn nearest_critter(&self, pos: Position) -> Option<&Element> {
        self.critters()
            .min_by_key(|e| (pos.chebyshev_distance(&e.pos), e.id))
    }

    pub fn nearest_friend(&self, me: KittyId, pos: Position) -> Option<&Kitty> {
        self.others(me)
            .min_by_key(|k| (pos.chebyshev_distance(&k.pos), k.id))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::behavior::BehaviorRegistry;
    use crate::test_support::{test_config, test_world};

    #[tokio::test]
    async fn a_tick_advances_the_clock_and_publishes() {
        let config = Arc::new(test_config());
        let mut world = World::generate(&config);
        let registry = BehaviorRegistry::with_builtins();

        assert_eq!(world.tick, 0);
        let snapshot = world.tick(&registry, &config).await;
        assert_eq!(world.tick, 1);
        assert_eq!(snapshot.tick, 1);
        assert_eq!(snapshot.kitties.len(), world.kitties.len());
    }

    #[tokio::test]
    async fn needs_rise_over_time() {
        let config = Arc::new(test_config());
        let mut world = World::generate(&config);
        let registry = BehaviorRegistry::with_builtins();

        // Cuddle has no automatic relief unless cats choose to socialise, but the
        // sum of all needs must clearly climb from a fresh world.
        let before: f32 = world.kitties[0].needs.all().iter().map(|(_, v)| v).sum();
        for _ in 0..5 {
            world.tick(&registry, &config).await;
        }
        let after: f32 = world.kitties[0].needs.all().iter().map(|(_, v)| v).sum();
        assert!(after > before, "{after} should exceed {before}");
    }

    #[tokio::test]
    async fn per_kitty_need_rates_change_how_fast_a_need_rises() {
        use crate::config::NeedRateOverrides;

        let mut config = test_config();
        // Kitty 1 gets triple the global eat rate; kitty 2 stays on defaults.
        config.kitties[0].needs = Some(NeedRateOverrides {
            eat: Some(config.needs.eat * 3.0),
            ..Default::default()
        });
        config.validate().expect("valid");
        let config = Arc::new(config);

        let mut world = World::generate(&config);
        // Park both cats' behaviors out of the picture by measuring pure rise:
        // apply the needs phase directly a few times.
        for _ in 0..10 {
            world.advance_needs(&config);
        }

        let hungry = world.kitty(1).unwrap().needs.get(NeedKind::Eat);
        let plain = world.kitty(2).unwrap().needs.get(NeedKind::Eat);
        assert!(
            (hungry - plain * 3.0).abs() < 0.01,
            "override kitty at {hungry}, plain at {plain}"
        );
        // And their other needs rise identically.
        assert_eq!(
            world.kitty(1).unwrap().needs.get(NeedKind::Drink),
            world.kitty(2).unwrap().needs.get(NeedKind::Drink)
        );
    }

    #[test]
    fn generated_worlds_meet_element_minimums() {
        let config = test_config();
        let world = World::generate(&config);
        for kind in ElementType::ALL {
            let rule = config.elements.rule(kind);
            assert!(
                world.count_of(kind) >= rule.min,
                "{:?}: {} < min {}",
                kind,
                world.count_of(kind),
                rule.min
            );
        }
    }

    #[tokio::test]
    async fn last_action_records_what_actually_happened() {
        use crate::behavior::test_behaviors::AlwaysInvalid;

        let mut config = test_config();
        config.kitties[0].behavior = "always_invalid".into();
        let config = Arc::new(config);

        let mut registry = BehaviorRegistry::with_builtins();
        registry.register("always_invalid", Arc::new(AlwaysInvalid));

        let mut world = World::generate(&config);
        assert!(
            world.kitties.iter().all(|k| k.last_action.is_none()),
            "no actions before the first tick"
        );

        world.tick(&registry, &config).await;

        // The liar's proposals are always illegal, so the record must honestly
        // say it idled -- never the fiction it proposed.
        assert_eq!(
            world.kitty(1).unwrap().last_action,
            Some(crate::action::Action::Idle)
        );
        // And every kitty has a recorded action after a tick.
        assert!(world.kitties.iter().all(|k| k.last_action.is_some()));
    }

    #[test]
    fn distress_is_edge_triggered() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();

        // Push a need over the threshold and record.
        world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
        world.record_distress(&config);
        assert_eq!(world.distress.len(), 1);

        // Still over the threshold on later ticks: no new events.
        for _ in 0..10 {
            world.record_distress(&config);
        }
        assert_eq!(world.distress.len(), 1, "one event per crossing");

        // Drop below, then cross again: a second event.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, -50.0);
        world.record_distress(&config);
        assert_eq!(world.distress.len(), 1);

        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 60.0);
        world.record_distress(&config);
        assert_eq!(world.distress.len(), 2, "re-armed after dropping below");
    }

    #[tokio::test]
    async fn recent_meows_stay_bounded() {
        let config = Arc::new(test_config());
        let mut world = World::generate(&config);
        let registry = BehaviorRegistry::with_builtins();

        for _ in 0..60 {
            world.tick(&registry, &config).await;
        }
        let window = config.meow.recent_window_ticks;
        for meow in &world.recent_meows {
            assert!(
                meow.tick + window >= world.tick,
                "meow from tick {} lingered past the {window}-tick window at tick {}",
                meow.tick,
                world.tick
            );
        }
    }

    #[test]
    fn elements_never_stack_on_one_tile() {
        let config = test_config();
        let world = World::generate(&config);
        let mut seen = std::collections::BTreeSet::new();
        for el in &world.elements {
            assert!(seen.insert(el.pos), "two elements share {:?}", el.pos);
        }
    }

    // ---- pursuit bookkeeping (US2) ---------------------------------------

    use crate::action::{Action, TargetRef};
    use crate::element::ElementKind;

    /// A world with one kitty at (2,2) and one greeble parked far away at
    /// (14,14): a chase that can be made to never close.
    fn chase_world() -> (World, Config) {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(2, 2);
        let other = world.kitty_index(2).unwrap();
        world.kitties[other].pos = Position::new(0, 15);
        world.push_element(Element {
            id: 900,
            kind: ElementKind::Greeble {
                heading: Direction::North,
            },
            pos: Position::new(14, 14),
            ttl: Some(500),
        });
        (world, config)
    }

    #[test]
    fn an_applied_chase_starts_a_pursuit_and_a_detour_does_not_reset_it() {
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        let p = world.kitty(1).unwrap().pursuit.expect("pursuit recorded");
        assert_eq!(p.started, 10);
        assert_eq!(p.closest, 12);

        // Two ticks later, an opportunistic drink: the pursuit must survive
        // with its original start tick (patience is elapsed, not consecutive).
        world.tick = 12;
        world.update_pursuit(1, Action::Drink, &config);
        let p = world
            .kitty(1)
            .unwrap()
            .pursuit
            .expect("survives the detour");
        assert_eq!(p.started, 10, "the clock did not reset");
    }

    #[test]
    fn closing_in_updates_closest_and_keeps_the_chase_alive_past_patience() {
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        // The cat gains ground; closest improves.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(6, 6);
        world.tick = 11;
        world.update_pursuit(1, Action::Chase(target), &config);
        let p = world.kitty(1).unwrap().pursuit.unwrap();
        assert_eq!(p.closest, 8);
        assert_eq!(
            p.improved_at, 11,
            "gaining ground resets the patience clock"
        );
    }

    #[test]
    fn a_chase_that_keeps_closing_is_never_called_hopeless() {
        // Regression: patience used to be measured from `started` with a
        // "current >= best-ever" distance test, so a chase running longer than
        // the patience window was condemned the moment it stopped improving --
        // including on arrival, when current *equals* best-ever. A cat that
        // closes one tile per tick for far longer than the window must keep
        // its target, and must not be left blacklisting it.
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };
        let steps = config.behavior.chase_patience_ticks * 2;

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);

        // Walk in diagonally, one tile closer every tick.
        for step in 1..=steps {
            let idx = world.kitty_index(1).unwrap();
            let pos = world.kitties[idx].pos;
            world.kitties[idx].pos = Position::new(pos.x + 1, pos.y + 1);
            world.tick = 10 + step;
            world.update_pursuit(1, Action::Chase(target), &config);

            let kitty = world.kitty(1).unwrap();
            assert!(
                kitty.pursuit.is_some(),
                "the chase was dropped at step {step} while still gaining ground"
            );
            assert!(
                kitty.abandoned_chases.is_empty(),
                "a productive chase must not blacklist its target (step {step})"
            );
        }

        // And having arrived, the catch clears the pursuit with no grudge.
        world.update_pursuit(
            1,
            Action::Play {
                target: Some(target),
            },
            &config,
        );
        let kitty = world.kitty(1).unwrap();
        assert!(kitty.pursuit.is_none());
        assert!(kitty.abandoned_chases.is_empty());
    }

    #[test]
    fn a_chase_stuck_at_a_fixed_distance_is_still_given_up_on() {
        // The other half of the fix: a chase that never worsens but never
        // improves (a greeble matching the cat's speed) must still expire --
        // a plain `>` on distance would have made it immortal.
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        let start_distance = world.kitty(1).unwrap().pursuit.unwrap().closest;

        // Keep chasing without ever closing: the target keeps its distance.
        for step in 1..=config.behavior.chase_patience_ticks {
            world.tick = 10 + step;
            world.update_pursuit(1, Action::Chase(target), &config);
            assert_eq!(
                world.kitty(1).unwrap().pursuit.unwrap().closest,
                start_distance,
                "no ground gained"
            );
        }

        // The next non-chase action writes it off.
        world.update_pursuit(1, Action::Idle, &config);
        let kitty = world.kitty(1).unwrap();
        assert!(kitty.pursuit.is_none());
        assert!(
            kitty.is_chase_excluded(target, world.tick),
            "a chase that never gains ground is still hopeless"
        );
    }

    #[test]
    fn a_futile_chase_is_abandoned_and_its_target_excluded() {
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);

        // Patience runs out with no ground gained; the next non-chase action
        // converts the pursuit into an exclusion.
        world.tick = 10 + config.behavior.chase_patience_ticks;
        world.update_pursuit(1, Action::Idle, &config);

        let kitty = world.kitty(1).unwrap();
        assert!(kitty.pursuit.is_none(), "the chase is over");
        assert!(
            kitty.is_chase_excluded(target, world.tick),
            "the target is written off"
        );
        assert!(
            !kitty.is_chase_excluded(target, world.tick + config.behavior.chase_exclusion_ticks),
            "the exclusion expires on schedule"
        );
    }

    #[test]
    fn catching_the_target_ends_the_pursuit_without_an_exclusion() {
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        // Even well past patience: a catch is a catch.
        world.tick = 40;
        world.update_pursuit(
            1,
            Action::Play {
                target: Some(target),
            },
            &config,
        );

        let kitty = world.kitty(1).unwrap();
        assert!(kitty.pursuit.is_none());
        assert!(kitty.abandoned_chases.is_empty(), "no grudge held");
    }

    #[test]
    fn a_dead_target_clears_the_pursuit_without_an_exclusion() {
        let (mut world, config) = chase_world();
        let target = TargetRef::Element { id: 900 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        world.elements.retain(|e| e.id != 900);
        world.tick = 30; // patience long gone -- but the target died first
        world.update_pursuit(1, Action::Idle, &config);

        let kitty = world.kitty(1).unwrap();
        assert!(kitty.pursuit.is_none());
        assert!(kitty.abandoned_chases.is_empty());
    }

    #[test]
    fn expired_exclusions_are_pruned_on_the_next_update() {
        let (mut world, config) = chase_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx]
            .abandoned_chases
            .push(crate::kitty::AbandonedChase {
                target: TargetRef::Element { id: 900 },
                until: 20,
            });

        world.tick = 25;
        world.update_pursuit(1, Action::Idle, &config);
        assert!(world.kitty(1).unwrap().abandoned_chases.is_empty());
    }

    #[test]
    fn two_uncatchable_targets_both_end_up_excluded_so_solo_play_unlocks() {
        // The I1 regression: give up on A, switch to B, give up on B -- both
        // must be excluded at once, so the reach test finds nobody viable and
        // solo play fires. Hopping between them must not launder staleness.
        let (mut world, config) = chase_world();
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Greeble {
                heading: Direction::South,
            },
            pos: Position::new(15, 2),
            ttl: Some(500),
        });
        let a = TargetRef::Element { id: 900 };
        let b = TargetRef::Element { id: 901 };
        let patience = config.behavior.chase_patience_ticks;

        // Chase A until patience runs out, gaining nothing...
        world.tick = 10;
        world.update_pursuit(1, Action::Chase(a), &config);
        // ...then switch to B: the stale A-chase is abandoned in the same move.
        world.tick = 10 + patience;
        world.update_pursuit(1, Action::Chase(b), &config);
        assert!(
            world.kitty(1).unwrap().is_chase_excluded(a, world.tick),
            "switching away from a stale chase writes the old target off"
        );

        // B fares no better; the next non-chase action writes it off too.
        world.tick = 10 + 2 * patience;
        world.update_pursuit(1, Action::play_solo(), &config);

        let kitty = world.kitty(1).unwrap();
        assert!(kitty.is_chase_excluded(a, world.tick), "A still excluded");
        assert!(kitty.is_chase_excluded(b, world.tick), "B excluded too");
        assert!(kitty.pursuit.is_none());
    }

    // ---- distress ages (US5) ---------------------------------------------

    #[test]
    fn distress_since_is_stamped_on_crossing_and_cleared_on_recovery() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Play, 95.0);
        world.tick = 100;
        world.record_distress(&config);
        assert_eq!(
            world.kitty(1).unwrap().distress_since.get(&NeedKind::Play),
            Some(&100)
        );

        // Still distressed later: the original stamp is preserved.
        world.tick = 150;
        world.record_distress(&config);
        assert_eq!(
            world.kitty(1).unwrap().distress_since.get(&NeedKind::Play),
            Some(&100),
            "the age keeps counting from the crossing"
        );

        // Recovery clears both the distress and its age.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Play, -60.0);
        world.record_distress(&config);
        let kitty = world.kitty(1).unwrap();
        assert!(!kitty.in_distress.contains(&NeedKind::Play));
        assert!(!kitty.distress_since.contains_key(&NeedKind::Play));
    }

    #[test]
    fn a_pre_004_resume_self_heals_its_distress_ages() {
        let (mut world, config) = test_world();
        // Simulate the pre-004 shape: in distress, but no start tick recorded.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Bath, 95.0);
        world.kitties[idx].in_distress.insert(NeedKind::Bath);
        world.kitties[idx].distress_since.clear();

        world.tick = 500;
        world.record_distress(&config);
        assert_eq!(
            world.kitty(1).unwrap().distress_since.get(&NeedKind::Bath),
            Some(&500),
            "the age starts counting from the resume, not from a guess"
        );
    }

    // ---- action durations (spec 006) ----------------------------------

    /// One kitty's engine slot of the apply phase, exactly as `tick` runs it
    /// (minus pursuit bookkeeping, which these tests don't exercise).
    fn run_slot(world: &mut World, config: &Config, kitty_id: KittyId, proposal: Action) -> Action {
        world.prune_dead_activity(kitty_id);
        let validated = action::validate(world, kitty_id, proposal, config);
        let enforced = world.enforce_durations(kitty_id, validated, config);
        if let Some(idx) = world.kitty_index(kitty_id) {
            world.kitties[idx].last_action = Some(enforced);
        }
        action::apply(world, kitty_id, enforced, config);
        enforced
    }

    /// Closes the apply phase and moves to the next tick.
    fn close_tick(world: &mut World, config: &Config) {
        world.resolve_activity_ends(config);
        world.tick += 1;
    }

    /// A world reduced to one deterministic scene: kitty 1 at (5,5) beside a
    /// bowl, everything else cleared out of the way.
    fn dinner_table(servings: u32) -> (World, Config) {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        let far = world.kitty_index(2).unwrap();
        world.kitties[far].pos = Position::new(15, 15);
        world.push_element(Element {
            id: 900,
            kind: ElementKind::Chow { servings },
            pos: Position::new(5, 6),
            ttl: None,
        });
        world.tick = 100;
        (world, config)
    }

    #[test]
    fn an_ended_scene_records_its_true_span_in_the_activity_log() {
        // The final tick of a scene clears the clock it just stamped, so
        // snapshots alone cannot show how long a scene ran -- the log is the
        // honest record (spec 006 review remediation). A meal eaten at
        // pressure 100 relieves 40/tick: ticks 100, 101, 102 -> need zero,
        // ended at the first lawful moment with an exact 3-tick span.
        let (mut world, config) = dinner_table(5);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 100.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        close_tick(&mut world, &config);
        for _ in 0..2 {
            run_slot(&mut world, &config, 1, Action::Idle);
            close_tick(&mut world, &config);
        }

        assert_eq!(
            world.kitty(1).unwrap().activity_clock,
            None,
            "the meal is over"
        );
        let ends: Vec<_> = world.activity_log.to_vec();
        assert_eq!(ends.len(), 1, "one scene, one event: {ends:?}");
        assert_eq!(ends[0].kitty_id, 1);
        assert_eq!(ends[0].activity, Activity::Eating);
        assert_eq!(ends[0].started, 100);
        assert_eq!(
            ends[0].ended, 102,
            "the invisible final tick is on the books"
        );
        assert_eq!(ends[0].span(), 3);
    }

    #[test]
    fn a_meal_runs_its_minimum_with_relief_every_tick() {
        let (mut world, config) = dinner_table(5);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 100.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 60.0);
        assert_eq!(
            world.kitty(1).unwrap().last_relief.get(&NeedKind::Eat),
            Some(&100)
        );
        close_tick(&mut world, &config);

        // Mid-minimum, a lawful Move proposal is superseded by the meal.
        let enforced = run_slot(&mut world, &config, 1, Action::move_to(Direction::North));
        assert_eq!(enforced, Action::Eat, "the engine keeps the scene going");
        assert_eq!(
            world.kitty(1).unwrap().needs.get(NeedKind::Eat),
            20.0,
            "relief lands on every tick of the meal"
        );
        assert_eq!(
            world.kitty(1).unwrap().last_action,
            Some(Action::Eat),
            "the record shows what actually happened"
        );
        assert_eq!(
            world.kitty(1).unwrap().last_relief.get(&NeedKind::Eat),
            Some(&101),
            "last_relief is stamped per tick"
        );
        close_tick(&mut world, &config);

        // Minimum met: the same proposal now lawfully interrupts.
        let enforced = run_slot(&mut world, &config, 1, Action::move_to(Direction::North));
        assert_eq!(enforced, Action::move_to(Direction::North));
        assert_eq!(world.kitty(1).unwrap().activity, Activity::Idle);
        assert!(world.kitty(1).unwrap().activity_clock.is_none());
    }

    #[test]
    fn re_proposing_sleep_never_resets_the_clock_and_the_cap_holds() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Sleep, 100.0);
        world.tick = 50;

        run_slot(&mut world, &config, 1, Action::Sleep { with: None });
        close_tick(&mut world, &config);

        // An endlessly re-proposed sleep continues -- with the original clock.
        for _ in 0..6 {
            let enforced = run_slot(&mut world, &config, 1, Action::Sleep { with: None });
            assert_eq!(enforced, Action::Sleep { with: None });
            assert_eq!(
                world.kitty(1).unwrap().activity_clock.unwrap().started,
                50,
                "continuation never launders the clock"
            );
            close_tick(&mut world, &config);
        }

        // Tick 57 is the 8th serviced tick: the cap ends the sleep.
        assert!(world.kitty(1).unwrap().activity.is_sleeping());
        run_slot(&mut world, &config, 1, Action::Sleep { with: None });
        close_tick(&mut world, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Idle,
            "no activity outlives its maximum"
        );

        // Re-entry is lawful and gets a fresh clock.
        run_slot(&mut world, &config, 1, Action::Sleep { with: None });
        assert_eq!(world.kitty(1).unwrap().activity_clock.unwrap().started, 58);
    }

    #[test]
    fn a_finished_need_ends_the_meal_at_the_first_lawful_tick() {
        let (mut world, config) = dinner_table(5);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 50.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        close_tick(&mut world, &config); // eat: 10, min not yet met
        assert!(world.kitty(1).unwrap().activity_clock.is_some());

        run_slot(&mut world, &config, 1, Action::Idle);
        assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 0.0);
        close_tick(&mut world, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Idle,
            "minimum met and need at 0: the meal is over"
        );
    }

    #[test]
    fn need_zero_before_the_minimum_waits_for_the_minimum() {
        let (mut world, config) = dinner_table(5);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 30.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 0.0);
        close_tick(&mut world, &config);
        assert!(
            world.kitty(1).unwrap().activity_clock.is_some(),
            "content, but the scene holds until its minimum"
        );

        run_slot(&mut world, &config, 1, Action::Idle);
        close_tick(&mut world, &config);
        assert_eq!(world.kitty(1).unwrap().activity, Activity::Idle);
    }

    #[test]
    fn an_emptied_bowl_pauses_below_the_minimum_and_ends_at_it() {
        let (mut world, config) = dinner_table(1);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 100.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 60.0);
        close_tick(&mut world, &config);

        // The bowl is empty and the minimum unmet: the cat licks the bowl --
        // no relief, no consumption -- but the clock still stamps, so the end
        // rules can reach the paused meal (analyze C1).
        run_slot(&mut world, &config, 1, Action::Idle);
        let kitty = world.kitty(1).unwrap();
        assert_eq!(
            kitty.needs.get(NeedKind::Eat),
            60.0,
            "no relief from an empty bowl"
        );
        assert_eq!(
            kitty.activity_clock.unwrap().applied,
            world.tick,
            "the pause still services the clock"
        );
        close_tick(&mut world, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Idle,
            "minimum met over an empty bowl: the meal ends"
        );
    }

    #[test]
    fn instant_bounds_reproduce_pre_006_pacing() {
        let (mut world, mut config) = dinner_table(5);
        config.actions.durations.eat = crate::config::DurationBounds::new(1, 1);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 100.0);

        run_slot(&mut world, &config, 1, Action::Eat);
        close_tick(&mut world, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Idle,
            "min = max = 1 is an instant action"
        );
        assert_eq!(world.kitty(1).unwrap().needs.get(NeedKind::Eat), 60.0);
    }

    /// Two kitties side by side, everything else out of the way.
    fn duet_stage() -> (World, Config) {
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(5, 6);
        world.tick = 100;
        (world, config)
    }

    #[test]
    fn a_busy_or_sleeping_partner_cannot_be_conscripted() {
        let (mut world, config) = duet_stage();
        world.push_element(Element {
            id: 900,
            kind: ElementKind::Chow { servings: 5 },
            pos: Position::new(5, 4),
            ttl: None,
        });
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 100.0);

        // Kitty 1 starts eating; kitty 2 tries to cuddle it mid-meal.
        run_slot(&mut world, &config, 1, Action::Eat);
        let enforced = run_slot(&mut world, &config, 2, Action::Rest { with: Some(1) });
        assert_eq!(enforced, Action::Idle, "a cat mid-meal is not draftable");
        close_tick(&mut world, &config);

        // A sleeping cat is not yanked awake to play either.
        let (mut world, config) = duet_stage();
        run_slot(&mut world, &config, 1, Action::Sleep { with: None });
        let enforced = run_slot(
            &mut world,
            &config,
            2,
            Action::play_with(TargetRef::Kitty { id: 1 }),
        );
        assert_eq!(enforced, Action::Idle);
    }

    #[test]
    fn duet_relief_lands_once_per_tick_for_both_partners() {
        let (mut world, config) = duet_stage();
        for id in [1, 2] {
            let idx = world.kitty_index(id).unwrap();
            world.kitties[idx].needs.add(NeedKind::Play, 100.0);
        }

        run_slot(
            &mut world,
            &config,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
        );
        // Kitty 2's own slot the same tick: already in the duet, no seconds.
        run_slot(
            &mut world,
            &config,
            2,
            Action::play_with(TargetRef::Kitty { id: 1 }),
        );
        for id in [1, 2] {
            assert_eq!(
                world.kitty(id).unwrap().needs.get(NeedKind::Play),
                75.0,
                "exactly one helping of relief per tick"
            );
        }
        assert_eq!(
            world.kitty(1).unwrap().activity_clock,
            world.kitty(2).unwrap().activity_clock,
            "one shared clock"
        );
        close_tick(&mut world, &config);

        // Next tick: whichever slot runs first feeds both, once.
        run_slot(&mut world, &config, 1, Action::Idle);
        run_slot(&mut world, &config, 2, Action::Idle);
        for id in [1, 2] {
            assert_eq!(world.kitty(id).unwrap().needs.get(NeedKind::Play), 50.0);
        }
    }

    #[test]
    fn a_duet_ends_for_both_when_either_is_content() {
        let (mut world, config) = duet_stage();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].needs.add(NeedKind::Play, 100.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].needs.add(NeedKind::Play, 30.0);

        run_slot(
            &mut world,
            &config,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
        );
        run_slot(&mut world, &config, 2, Action::Idle);
        close_tick(&mut world, &config);

        run_slot(&mut world, &config, 1, Action::Idle);
        run_slot(&mut world, &config, 2, Action::Idle);
        assert_eq!(world.kitty(2).unwrap().needs.get(NeedKind::Play), 0.0);
        close_tick(&mut world, &config);

        for id in [1, 2] {
            assert_eq!(
                world.kitty(id).unwrap().activity,
                Activity::Idle,
                "the duet ends together on the same tick"
            );
        }
        assert!(
            world.kitty(1).unwrap().needs.get(NeedKind::Play) > 0.0,
            "the hungrier player is freed by the content one"
        );
    }

    #[test]
    fn a_post_min_interrupt_frees_both_duet_partners_the_same_tick() {
        let (mut world, config) = duet_stage();
        for id in [1, 2] {
            let idx = world.kitty_index(id).unwrap();
            world.kitties[idx].needs.add(NeedKind::Play, 100.0);
        }

        run_slot(
            &mut world,
            &config,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
        );
        run_slot(&mut world, &config, 2, Action::Idle);
        close_tick(&mut world, &config);
        run_slot(&mut world, &config, 1, Action::Idle);
        run_slot(&mut world, &config, 2, Action::Idle);
        close_tick(&mut world, &config);

        // Minimum met. Kitty 2 (the conscripted partner!) walks away; both
        // sides of the duet clear in that very slot -- no one-sided state.
        run_slot(&mut world, &config, 1, Action::Idle);
        let enforced = run_slot(&mut world, &config, 2, Action::move_to(Direction::South));
        assert_eq!(enforced, Action::move_to(Direction::South));
        for id in [1, 2] {
            assert_eq!(world.kitty(id).unwrap().activity, Activity::Idle);
            assert!(world.kitty(id).unwrap().activity_clock.is_none());
        }
        close_tick(&mut world, &config);
        invariants::check(&world, &config).expect("no one-sided duet survives");
    }

    #[test]
    fn a_vanished_critter_ends_play_where_it_stands() {
        let (mut world, config) = duet_stage();
        world.push_element(Element {
            id: 800,
            kind: ElementKind::Bug,
            pos: Position::new(4, 5),
            ttl: Some(50),
        });
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Play, 100.0);

        run_slot(
            &mut world,
            &config,
            1,
            Action::play_with(TargetRef::Element { id: 800 }),
        );
        close_tick(&mut world, &config);

        // The bug expires mid-game -- inside the minimum.
        world.elements.retain(|e| e.id != 800);
        run_slot(&mut world, &config, 1, Action::Idle);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Idle,
            "minimum notwithstanding, there is nothing left to play with"
        );
        assert_eq!(
            world.kitty(1).unwrap().needs.get(NeedKind::Play),
            75.0,
            "relief already granted is kept; none is invented"
        );
    }

    #[test]
    fn a_groomed_friend_walking_away_ends_the_grooming() {
        let (mut world, config) = duet_stage();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Cuddle, 50.0);

        run_slot(&mut world, &config, 1, Action::Groom { target: Some(2) });
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Grooming { target: Some(2) }
        );
        assert!(
            world.kitty(2).unwrap().activity_clock.is_none(),
            "being groomed binds nobody"
        );
        close_tick(&mut world, &config);

        // The friend wanders off; the groomer's next slot finds it gone.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(12, 12);
        run_slot(&mut world, &config, 1, Action::Idle);
        assert_eq!(world.kitty(1).unwrap().activity, Activity::Idle);
    }
}
