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
use crate::behavior::{gather_decisions, BehaviorRegistry};
use crate::config::Config;
use crate::element::{Element, ElementId, ElementKind, ElementType};
use crate::events::{DistressEvent, DistressLog};
use crate::grid::{Direction, Position};
use crate::invariants;
use crate::kitty::{Kitty, KittyId};
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
            let validated = action::validate(self, kitty_id, proposal, config);
            action::apply(self, kitty_id, validated, config);
        }

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
                kitty.needs.add(kind, config.needs.rate(kind));
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
                        new_events.push(DistressEvent {
                            kitty_id: kitty.id,
                            need: kind,
                            tick,
                        });
                    }
                } else {
                    kitty.in_distress.remove(&kind);
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

    /// A friend is any other kitty; "available" adds the adjacency an interaction
    /// needs.
    pub fn is_available_friend(&self, me: KittyId, friend: KittyId) -> bool {
        if me == friend {
            return false;
        }
        match (self.kitty(me), self.kitty(friend)) {
            (Some(a), Some(b)) => a.pos.is_adjacent(&b.pos),
            _ => false,
        }
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
}
