//! The world and its tick loop.
//!
//! Article V fixes the order of a tick, and [`World::tick`] is the only place that
//! order is expressed:
//!
//! 1. snapshot the world; every behavior decides against that same snapshot
//! 2. apply actions in a fair per-tick order ("cats act first"): a fresh
//!    permutation drawn from the world RNG each tick, so no kitty is ever
//!    systematically first (Article V as amended, spec 013)
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
use crate::events::{
    ActivityEnd, ActivityLog, DistressEvent, DistressLog, RefusalEvent, RefusalLog,
};
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
    /// Refusals: non-Idle proposals validation resolved to Idle (spec 046).
    /// Serde defaulted so pre-046 saves still load — to capacity 0, which the
    /// server load path immediately re-stamps from config (retention is
    /// configuration, not world state).
    #[serde(default)]
    pub refusal_log: RefusalLog,
    pub rng: SimRng,
    pub config_fingerprint: String,
    next_element_id: ElementId,
    /// The activities that ended during the tick in progress — drained by
    /// the phase pipeline into the tick report (spec 014 FR-003). Captured
    /// directly at `end_activity` rather than read back through the bounded
    /// ring, so the report stays honest at any configured retention.
    /// Transient: never serialized.
    #[serde(skip)]
    pending_endings: Vec<ActivityEnd>,
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

/// Who initiated a purr start (spec 022): the same phenomenon either way,
/// differing only in audibility -- see `World::start_purr`.
#[derive(Clone, Copy)]
pub(crate) enum PurrOrigin {
    /// Chosen via the purr-meow action: always announces.
    Deliberate,
    /// The engine's background motor: announces per `announce_probability`.
    Motor,
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
            refusal_log: RefusalLog::new(config.events.refusal_retention),
            rng: SimRng::from_seed(config.world.seed),
            config_fingerprint: config.fingerprint(),
            next_element_id: 1,
            pending_endings: Vec::new(),
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

    /// Reconstructs a rule-evaluation view of a frozen snapshot: a `World`
    /// whose kitties, elements, clock, and dimensions are the snapshot's,
    /// with fresh bookkeeping (empty logs, zero-seeded RNG). Exists so a
    /// snapshot consumer can ask the law questions -- validation, duration
    /// enforcement -- through the engine's own code (spec 014 FR-018's mask
    /// derives from this). Not for resuming a simulation: the RNG is not the
    /// live world's.
    pub fn from_snapshot(snapshot: &WorldSnapshot) -> Self {
        let next_element_id = snapshot
            .elements
            .iter()
            .map(|e| e.id)
            .max()
            .map(|id| id.wrapping_add(1).max(1))
            .unwrap_or(1);
        World {
            width: snapshot.width,
            height: snapshot.height,
            tick: snapshot.tick,
            kitties: snapshot.kitties.clone(),
            elements: snapshot.elements.clone(),
            recent_meows: snapshot.recent_meows.clone(),
            distress: DistressLog::default(),
            activity_log: ActivityLog::default(),
            refusal_log: RefusalLog::default(),
            rng: SimRng::from_seed(0),
            config_fingerprint: String::new(),
            next_element_id,
            pending_endings: Vec::new(),
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

        // Phases 2-4: one shared pipeline (spec 014 FR-002) -- the seam is a
        // different *source* of proposals, never a different law.
        self.run_applied_phases_from_decisions(&decisions, config);

        // Phase 5: publish.
        Arc::new(self.snapshot())
    }

    /// Deals this tick's per-kitty decision seeds from the master RNG, in
    /// stable id order (Article V discipline; spec 014 FR-003 exposes them).
    /// Exactly one `u64` draw per kitty -- the same shape every dispatch path
    /// consumes, which is what keeps same-seed futures coincident.
    pub fn deal_decision_seeds(&mut self) -> crate::seam::DealtSeeds {
        let ids: Vec<KittyId> = self.kitties.iter().map(|k| k.id).collect();
        crate::seam::DealtSeeds {
            tick: self.tick,
            seeds: ids
                .into_iter()
                .map(|id| (id, self.rng.next_u64()))
                .collect(),
        }
    }

    /// Advances the world exactly one tick from externally supplied proposals
    /// (spec 014 FR-001): the same constitutional tick order as
    /// [`World::tick`], with behavior dispatch as the only step bypassed.
    /// Absent or malformed entries resolve to idle (Article IV), marked
    /// `SubstitutedIdle`; entries for unknown ids are reported unconsumed.
    pub fn tick_with_proposals(
        &mut self,
        proposals: &crate::seam::JointProposal,
        config: &Config,
    ) -> crate::seam::TickReport {
        let seeds = self.deal_decision_seeds();
        self.tick_with_proposals_seeded(proposals, seeds, config)
    }

    /// Advances the master RNG past this tick's per-kitty decision-seed
    /// draws without keeping the seeds — for reference-stream comparisons
    /// that must match a driver which dealt eagerly (the honest name for
    /// what was previously spelled as a deal nobody applied).
    pub fn advance_past_decision_draws(&mut self) {
        let _ = self.deal_decision_seeds();
    }

    /// The seeded form of [`World::tick_with_proposals`], for drivers that
    /// dealt this tick's decision seeds themselves (mixed control needs the
    /// seeds *before* the tick, to run scripted behaviors and to surface
    /// them to trainers -- spec 014 FR-015/FR-020). Dealing early and
    /// applying here draws the identical master-RNG stream a
    /// behavior-driven tick would; the deal's tick stamp is asserted, and
    /// the value is consumed, so it cannot be reused.
    ///
    /// # Panics
    ///
    /// If `seeds` was dealt for a different tick -- a driver bug that would
    /// otherwise silently break same-seed reproducibility (Article V).
    pub fn tick_with_proposals_seeded(
        &mut self,
        proposals: &crate::seam::JointProposal,
        seeds: crate::seam::DealtSeeds,
        config: &Config,
    ) -> crate::seam::TickReport {
        use crate::seam::{ProposalEntry, Provenance, TickReport};

        assert_eq!(
            seeds.tick, self.tick,
            "decision seeds were dealt for tick {} but applied at tick {}; \
             deal_decision_seeds must be called exactly once per tick, on the \
             tick it is applied to",
            seeds.tick, self.tick
        );
        let roster: Vec<KittyId> = self.kitties.iter().map(|k| k.id).collect();
        let mut decisions = Vec::with_capacity(roster.len());
        // Index-aligned with `roster` and `decisions` (one entry per roster
        // kitty, same loop).
        let mut marks: Vec<Provenance> = Vec::with_capacity(roster.len());
        for &id in &roster {
            match proposals.get(id) {
                Some(ProposalEntry::Decision(decision)) => {
                    decisions.push((id, *decision));
                    marks.push(Provenance::PolicyMade);
                }
                Some(ProposalEntry::Malformed) | None => {
                    decisions.push((
                        id,
                        crate::seam::Decision::silent(crate::action::Action::Idle),
                    ));
                    marks.push(Provenance::SubstitutedIdle);
                }
            }
        }
        let unconsumed: Vec<KittyId> = proposals.ids().filter(|id| !roster.contains(id)).collect();

        let outcome = self.run_applied_phases_from_decisions(&decisions, config);
        let records = outcome.records(roster.iter().enumerate().map(|(index, &id)| {
            let (_, proposed) = decisions[index];
            let decision_seed = seeds.seed_for(id).expect(
                "the deal covers every roster kitty: both come from this world at this tick",
            );
            (id, proposed, marks[index], decision_seed)
        }));

        TickReport {
            records,
            distress_events: outcome.distress_events,
            activity_endings: outcome.activity_endings,
            unconsumed,
        }
    }

    /// Phases 2-4 of the constitutional tick, shared verbatim by the
    /// behavior-driven tick and the joint-action seam (spec 014 FR-002).
    ///
    /// Phase 2 applies in this tick's fair turn order (Article V as amended,
    /// spec 013). Validation happens here, against the world as it stands
    /// when the action lands -- so the first cat to reach the last serving
    /// gets it and the second one simply idles; *which* cat is first is a
    /// fresh draw every tick, never a standing privilege of a low id.
    ///
    /// Spec 028: each kitty's turn applies its decision's **activity** first
    /// (the pipeline above, unchanged) and then its **message** -- ruled by
    /// `meow::message_legal`; an illegal message downgrades to Silent with
    /// the paired activity untouched. Message application rides the same
    /// fair turn order, so digest freshness ties resolve identically on
    /// every replay of a seed.
    pub(crate) fn run_applied_phases_from_decisions(
        &mut self,
        decisions: &[(KittyId, crate::seam::Decision)],
        config: &Config,
    ) -> PhaseOutcome {
        self.pending_endings.clear();
        let mut per_kitty = Vec::with_capacity(self.kitties.len());

        let order = self.draw_turn_order();
        for kitty_id in order {
            let Some(decision) = decisions
                .iter()
                .find(|(id, _)| *id == kitty_id)
                .map(|&(_, decision)| decision)
            else {
                continue;
            };
            let proposal = decision.activity;
            // An activity whose counterpart is gone ends before anything else
            // happens (spec 006 FR-010): the world moved on, and the kitty's
            // proposal gets its normal hearing.
            self.prune_dead_activity(kitty_id);
            let validated = action::validate(self, kitty_id, proposal, config);
            // Duration enforcement (spec 006): inside an activity's minimum the
            // engine continues the scene whatever was proposed; past it, a
            // different action lawfully interrupts (ending a duet for both).
            let enforced = self.enforce_durations(kitty_id, validated, config);
            // The refusal stamp (spec 046): a non-Idle proposal validation
            // resolved to Idle, recorded on the tick it was heard, in turn
            // order. `absorbed` reads the enforcement outcome -- a MID-SCENE
            // kitty's continuing activity is the only way a refused turn
            // ends non-Idle, minimum met or not: for a refusal (validated ==
            // Idle) `is_continued_by` answers before the minimum check, so
            // the flag means "the kitty was mid-scene", ruled the census
            // meaning (Experiments (a), 2026-09-01). A legal proposal never
            // enters (validated == proposal != Idle), so duration overrides
            // of legal actions are not refusals.
            if proposal != action::Action::Idle && validated == action::Action::Idle {
                self.refusal_log.record(RefusalEvent {
                    kitty_id,
                    proposed: proposal,
                    tick: self.tick,
                    absorbed: enforced != action::Action::Idle,
                });
            }
            // Record what actually happened, not what was proposed: the viewer's
            // "doing" line must never claim an action the engine refused --
            // and on continuation ticks it truthfully repeats the activity.
            if let Some(idx) = self.kitty_index(kitty_id) {
                self.kitties[idx].last_action = Some(enforced);
            }
            action::apply(self, kitty_id, enforced, config);
            self.update_pursuit(kitty_id, enforced, config);
            // The message half: legality read after the activity landed
            // (defined order -- activity, then message), enforcement as
            // downgrade-to-Silent, never an error.
            let tick = self.tick;
            let applied_message = decision.message.filter(|&kind| {
                self.kitty(kitty_id).is_some_and(|k| {
                    crate::meow::message_legal(k, kind, tick, config, &self.elements)
                })
            });
            if let Some(kind) = applied_message {
                action::apply_message(self, kitty_id, kind, config, tick);
            }
            per_kitty.push((kitty_id, validated, enforced, applied_message));
        }

        // Phase 2, closing step: activities that finished their job this tick
        // end here, once relief has landed for everyone (spec 006).
        self.resolve_activity_ends(config);

        // Phase 3: the environment resolves.
        self.environment_phase(config);

        // Phase 4: needs rise, happiness follows, arming and distress are
        // noted, invariants hold.
        self.advance_needs(config);
        self.update_announce_arming(config);
        // The honest per-tick capture (spec 014 FR-003): both event kinds are
        // taken at their source, so the report cannot under-report however
        // small the configured retention rings are.
        let distress_events = self.record_distress(config);
        // Spec 011: purrs start and stop here, with happiness at its freshest.
        self.purr_phase(config);
        self.tick += 1;
        self.prune_transient(config);

        invariants::assert_or_report(self, config);

        let activity_endings = std::mem::take(&mut self.pending_endings);

        PhaseOutcome {
            per_kitty,
            distress_events,
            activity_endings,
        }
    }

    /// This tick's turn order (Article V as amended, spec 013): a uniform
    /// permutation of the roster, Fisher-Yates-drawn from the world RNG --
    /// fair over time, identical on every replay of the same seed. Exactly
    /// `kitties.len() - 1` draws, a count that depends only on the roster
    /// size -- itself deterministic in a seeded world -- so the RNG stream
    /// keeps its reproducible shape even in a future where kittens grow the
    /// roster (a newcomer joins the draw, fairly, from its first full tick).
    /// Public so the Article VI guarding test exercises the very permutation
    /// the tick applies.
    pub fn draw_turn_order(&mut self) -> Vec<KittyId> {
        let mut order: Vec<KittyId> = self.kitties.iter().map(|k| k.id).collect();
        for i in (1..order.len()).rev() {
            let j = self.rng.gen_range_u32(0, i as u32 + 1) as usize;
            order.swap(i, j);
        }
        order
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
                    let end = ActivityEnd {
                        kitty_id: id,
                        activity: self.kitties[idx].activity,
                        started: clock.started,
                        ended: clock.applied,
                        mutual_ticks: clock.mutual_ticks,
                        drip_ticks: clock.drip_ticks,
                    };
                    self.activity_log.record(end);
                    self.pending_endings.push(end);
                }
                self.kitties[idx].clear_activity();
            }
        }
    }

    /// Spec 006 FR-010: an activity whose counterpart is gone -- a critter
    /// expired or scurried out of reach, a groomed friend who walked away, a
    /// water source that dried up -- ends immediately, minimum notwithstanding.
    /// Run at the top of the kitty's apply slot so its proposal, made against
    /// the start-of-tick snapshot, still gets a normal hearing. Public since
    /// spec 014: the legal-action mask replays the apply slot's exact
    /// sequence (prune, validate, enforcement verdict) on a probe world.
    pub fn prune_dead_activity(&mut self, kitty_id: KittyId) {
        if self.counterpart_gone(kitty_id) {
            self.end_activity(kitty_id);
        }
    }

    /// Whether `kitty_id`'s ongoing activity has a counterpart the world no
    /// longer supplies (spec 048 FR-002): THE one definition of a dead
    /// scene. `prune_dead_activity` ends scenes by it; the behavior-side
    /// commitment (`finish_what_you_started`) declines to continue by it,
    /// through the snapshot twin below -- one body in
    /// `counterpart_gone_in`, so the two rules can never drift.
    pub(crate) fn counterpart_gone(&self, kitty_id: KittyId) -> bool {
        self.kitty(kitty_id)
            .is_some_and(|k| counterpart_gone_in(k, &self.kitties, &self.elements))
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
        match self.duration_ruling(kitty_id, &validated, config) {
            DurationRuling::NotGoverned => validated,
            DurationRuling::Continue(continuation) => continuation,
            DurationRuling::Interrupt => {
                // A different action applying past the minimum lawfully
                // interrupts: the activity ends in this very slot (for both
                // duet partners).
                self.end_activity(kitty_id);
                validated
            }
        }
    }

    /// The one implementation of the duration-enforcement law, read-only:
    /// what this tick's enforcement rules for `validated`. Both
    /// [`World::enforce_durations`] (the tick's mutating arm) and
    /// [`World::enforcement_verdict`] (the mask's read-only probe) are thin
    /// matches over this ruling, so the law cannot drift between them.
    fn duration_ruling(
        &self,
        kitty_id: KittyId,
        validated: &crate::action::Action,
        config: &Config,
    ) -> DurationRuling {
        let Some(kitty) = self.kitty(kitty_id) else {
            return DurationRuling::NotGoverned;
        };
        let Some(clock) = kitty.activity_clock else {
            return DurationRuling::NotGoverned;
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
            return DurationRuling::NotGoverned;
        };
        if activity.is_continued_by(validated) {
            return DurationRuling::Continue(continuation);
        }
        if clock.serviced_before(self.tick) < bounds.min {
            return DurationRuling::Continue(continuation);
        }
        DurationRuling::Interrupt
    }

    /// The apply slot's gauntlet, run for real (spec 014): counterpart
    /// pruning, validation, then duration enforcement — mutations included.
    /// Returns the action that would be applied. Exists for the mask's
    /// pure-oracle property test, which checks the read-only
    /// [`World::enforcement_verdict`] path against this genuine one on a
    /// probe world; the served tick never calls it.
    pub fn apply_slot_verdict(
        &mut self,
        kitty_id: KittyId,
        proposal: crate::action::Action,
        config: &Config,
    ) -> crate::action::Action {
        self.prune_dead_activity(kitty_id);
        let validated = action::validate(self, kitty_id, proposal, config);
        self.enforce_durations(kitty_id, validated, config)
    }

    /// The read-only twin of `enforce_durations` (spec 014): what duration
    /// enforcement *would* return for `validated` this tick, without ending
    /// anything. Both arms share [`World::duration_ruling`] -- one law, two
    /// consumers -- and the mask's pure-oracle property test (amended
    /// FR-018) still checks them against each other end to end.
    pub fn enforcement_verdict(
        &self,
        kitty_id: KittyId,
        validated: &crate::action::Action,
        config: &Config,
    ) -> crate::action::Action {
        match self.duration_ruling(kitty_id, validated, config) {
            DurationRuling::NotGoverned | DurationRuling::Interrupt => *validated,
            DurationRuling::Continue(continuation) => continuation,
        }
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
                // Manhattan, like every decision distance (spec 009): with a
                // 4-way walk and an orthogonal catch, converting a diagonal
                // offset into a straight one is real, catch-enabling progress
                // -- measured in Chebyshev it looked like a stall, and the
                // patience clock condemned chases at the moment they became
                // winnable.
                let distance = kitty_pos.manhattan_distance(&target_pos);
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
        self.move_critters(config);
        self.expire_elements();
        spawn::ensure_minimums(self, config);
        spawn::safeguard(self, config);
    }

    /// Bugs plod one tile every other tick; greebles skitter one or two tiles every
    /// tick and change their minds constantly. A configured roam cell (spec 039)
    /// tethers each bug to the world-aligned cell it stands in — for life, since
    /// it can never leave. Under `dart` (039 third amendment) greebles join the
    /// bugs' rest-tick schedule and dart 1-3 tiles on their moving ticks.
    fn move_critters(&mut self, config: &Config) {
        let tick = self.tick;
        let (width, height) = (self.width, self.height);
        let bug_roam = config.elements.bug.roam_cell;

        for idx in 0..self.elements.len() {
            match self.elements[idx].kind {
                ElementKind::Bug => {
                    if !self.elements[idx].critter_moves_this_tick(tick) {
                        continue;
                    }
                    let dir = *self
                        .rng
                        .choose(&Direction::ALL)
                        .expect("Direction::ALL is never empty");
                    // Spec 039: the tether check rides AFTER the draw, so the
                    // stream shape is identical with or without it, and an
                    // outward draw costs the step exactly like a blocked one —
                    // no redraw, no compensation (FR-003).
                    if let Some(cell) = bug_roam {
                        let pos = self.elements[idx].pos;
                        match pos.step(dir, width, height) {
                            Some(dest) if crate::grid::same_roam_cell(pos, dest, cell) => {}
                            _ => continue,
                        }
                    }
                    self.try_step_element(idx, dir, width, height);
                }
                ElementKind::Greeble { heading } => {
                    // The dart schedule (spec 039 third amendment): a flagged
                    // greeble rests on its off-parity tick and draws nothing —
                    // the rest check sits before every draw so the flag-off
                    // stream is byte-identical (FR-015, the golden digest's
                    // guard).
                    let dart = config.elements.greeble.dart;
                    if dart && !self.elements[idx].critter_moves_this_tick(tick) {
                        continue;
                    }
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
                    // Moving ticks pay for the rest with a wider dart: 1-3
                    // tiles instead of the every-tick 1-or-2 coin.
                    let steps = if dart {
                        self.rng.gen_range_u32(1, 4)
                    } else if self.rng.gen_bool(0.5) {
                        2
                    } else {
                        1
                    };
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
        // Wet fur (spec 024): occupancy of a water tile is priced in bath
        // need, per tick, so crossing and lounging share one knob. Water
        // positions are collected before the kitty loop (the loop holds
        // &mut self.kitties, and elements is a disjoint field), and only
        // when the charge exists at all. No RNG is drawn anywhere in this
        // phase -- reads never shape the stream.
        let water: Vec<Position> = if config.water.bath_gain > 0.0 {
            self.elements
                .iter()
                .filter(|el| el.element_type() == ElementType::Water)
                .map(|el| el.pos)
                .collect()
        } else {
            Vec::new()
        };
        // Waterline contagion (spec 044): wet fur travels with the scene.
        // Membership is ruled by `[water] contagion_membership` (spec
        // 045). Under `option_a` -- the shipped 044 rule and the default
        // -- it is the cat's OWN activity naming a partner (the clarified
        // own-activity rule -- a merely-referenced cat, like an idle
        // groomee, pays nothing; play is reciprocal by construction so
        // both members name each other). Under `bidirectional` the other
        // role is admitted too: a dry cat that a WET cat's activity names
        // also pays. Either way the partner must be CURRENTLY adjacent
        // (`is_available_friend`, the one adjacency predicate;
        // owner-ruled 2026-08-31: a scene the tick has already dissolved
        // -- a free partner who wandered after the namer's slot, before
        // the namer's next prune -- never draws a trailing charge). Dry
        // members only: a cat on water pays occupancy below, never both
        // -- the arms are mutually exclusive, so the per-tick worst case
        // is unchanged at factor <= 1; the BTreeSet makes a cat admitted
        // by both roles, or referenced by several wet cats, ONE member
        // and so one charge (FR-003, structural). Both sets are
        // snapshots of current positions and activities taken before the
        // loop, so the needs loop itself is order-free (Article V), and
        // nothing is collected while the dial is off.
        let contagious: std::collections::BTreeSet<crate::kitty::KittyId> =
            if config.water.contagion_factor > 0.0 && config.water.bath_gain > 0.0 {
                let wet_ids: std::collections::BTreeSet<crate::kitty::KittyId> = self
                    .kitties
                    .iter()
                    .filter(|k| water.contains(&k.pos))
                    .map(|k| k.id)
                    .collect();
                // Spec 045 bidirectional arm: admit a dry cat when ANY
                // wet cat's activity names it AND that namer is still
                // adjacent. A scan, not the research-note's BTreeMap
                // keyed by named cat: the map would keep one namer per
                // named cat, and if the kept one had wandered while
                // another adjacent wet namer remained, it would wrongly
                // deny -- adjacency is per NAMER, so every namer must be
                // consulted. Order-free (any() over a snapshot).
                let bidirectional = config.water.contagion_membership
                    == crate::config::ContagionMembership::Bidirectional;
                // Wet namers pre-collected as (namer, named) pairs -- the
                // scan is O(wet-namers x dry) instead of O(roster^2), and
                // wet namers are few (medium review, since this arm is a
                // candidate for a served pre-fog flip).
                let wet_namer_pairs: Vec<(crate::kitty::KittyId, crate::kitty::KittyId)> =
                    if bidirectional {
                        self.kitties
                            .iter()
                            .filter(|w| wet_ids.contains(&w.id))
                            .filter_map(|w| w.activity.partner().map(|named| (w.id, named)))
                            .collect()
                    } else {
                        Vec::new()
                    };
                self.kitties
                    .iter()
                    .filter(|k| !water.contains(&k.pos))
                    .filter(|k| {
                        k.activity.partner().is_some_and(|p| {
                            wet_ids.contains(&p) && self.is_available_friend(k.id, p)
                        }) || wet_namer_pairs
                            .iter()
                            .any(|(w, named)| *named == k.id && self.is_available_friend(*w, k.id))
                    })
                    .map(|k| k.id)
                    .collect()
            } else {
                std::collections::BTreeSet::new()
            };
        for kitty in &mut self.kitties {
            for kind in NeedKind::ALL {
                // Per-kitty override when configured, global rate otherwise.
                kitty.needs.add(kind, config.need_rate_for(kitty.id, kind));
            }
            // The charge gates on the PRE-charge value (after this tick's
            // ambient rise): overshoot is bounded by one scaled charge,
            // headroom validate_water already budgeted against the
            // safeguard. Scaling is `Config::bath_ratio` -- the cat's own
            // bath rise over the world baseline (validate_water keeps the
            // baseline positive whenever the gain is; the helper degrades
            // to 1 rather than divide if a config skipped validation).
            if config.water.bath_gain > 0.0
                && kitty.needs.get(NeedKind::Bath) < config.water.bath_gain_ceiling
                && water.contains(&kitty.pos)
            {
                let ratio = config.bath_ratio(kitty.id);
                kitty
                    .needs
                    .add(NeedKind::Bath, config.water.bath_gain * ratio);
            } else if contagious.contains(&kitty.id)
                && kitty.needs.get(NeedKind::Bath) < config.water.bath_gain_ceiling
            {
                // The contagion arm (spec 044): same pre-charge ceiling
                // gate, same bath_ratio scale, one extra dial. No cat
                // pays both arms in a tick, twice over: when occupancy
                // fires, the `else` skips this arm; when occupancy is
                // ceiling-refused, the shared gate here refuses too; and
                // the `contagious` filter never admits a wet cat at all.
                // (Review finding 2 read the `else` alone as the guard --
                // it is one of three, none load-bearing by itself.)
                // The formula lives in `Config::contagion_charge` -- the
                // ONE copy the 045 ladder also reads (predictor and
                // collector must never drift).
                kitty
                    .needs
                    .add(NeedKind::Bath, config.contagion_charge(kitty.id));
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

    /// The announce-arming edge rule (spec 028), distress's sibling: a
    /// want-kind arms at `>= announce_threshold`, disarms below
    /// `threshold - hysteresis`, and holds anywhere in the band -- so the
    /// message mask cannot flicker across one errand. No RNG, no events;
    /// pure state the mask reads.
    fn update_announce_arming(&mut self, config: &Config) {
        let arm_at = config.meow.announce_threshold;
        let disarm_below = arm_at - config.meow.announce_hysteresis;
        for kitty in &mut self.kitties {
            for kind in NeedKind::ALL {
                let value = kitty.needs.get(kind);
                if value >= arm_at {
                    kitty.announce_armed.insert(kind);
                } else if value < disarm_below {
                    kitty.announce_armed.remove(&kind);
                }
                // In the band [disarm_below, arm_at): hold whatever it was.
            }
        }
    }

    /// Edge-triggered: a need records one event when it crosses the threshold and
    /// stays quiet until it drops back below and crosses again. Returns the
    /// events this call produced — the tick report's capture (spec 014
    /// FR-003), taken at the source rather than read back through the ring.
    fn record_distress(&mut self, config: &Config) -> Vec<DistressEvent> {
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

        for event in &new_events {
            self.distress.record(event.clone());
        }
        new_events
    }

    /// One purr-duration draw from the master RNG -- shared by the motor and
    /// the deliberate purr (spec 022) so the draw has a single
    /// implementation. One draw even when min == max: config can never
    /// change the draw *count* (the fixed-shape rule). The span always fits
    /// u32: `validate_purr` bounds `max_ticks`.
    pub(crate) fn draw_purr_duration(&mut self, config: &Config) -> u64 {
        let span = (config.purr.max_ticks - config.purr.min_ticks + 1) as u32;
        config.purr.min_ticks + self.rng.gen_range_u32(0, span) as u64
    }

    /// The purr-start transition (spec 022): one implementation for both
    /// origins, so the paired fields (`purring_until` + `purring_duration`)
    /// can never drift apart. Draws the duration -- always exactly one draw
    /// -- then records the start announcement per the origin's audibility:
    /// a deliberate purr always announces; the motor announces per
    /// `announce_probability`, drawing its decision even at 0 and 1 --
    /// config changes outcomes, never the draw shape. (`gen_f32 < p` rather
    /// than `gen_bool(p)`: Bernoulli short-circuits p = 1.0 without
    /// consuming the stream, which would break the shape rule.) Purr starts
    /// stamp no message cooldown (the stamp lost its last reader -- spec
    /// 023 retires the enforcement it once fed).
    pub(crate) fn start_purr(
        &mut self,
        idx: usize,
        config: &Config,
        tick: u64,
        origin: PurrOrigin,
    ) {
        let duration = self.draw_purr_duration(config);
        self.kitties[idx].purring_until = Some(tick + duration);
        self.kitties[idx].purring_duration = Some(duration);
        let announce = match origin {
            PurrOrigin::Deliberate => true,
            PurrOrigin::Motor => self.rng.gen_f32() < config.purr.announce_probability,
        };
        if announce {
            let id = self.kitties[idx].id;
            self.recent_meows.push(Meow {
                kitty_id: id,
                kind: crate::meow::MessageKind::Purr,
                tick,
                intensity: 0.0,
            });
        }
    }

    /// Spec 011's engine-owned background purr, amended by spec 022: a purr
    /// may now also be *initiated* by choice (the deliberate purr, applied
    /// in the action phase), but running and ending are origin-less and live
    /// here. Runs right after needs and happiness settle, so a purr can
    /// begin the very tick contentment crosses the line; stable kitty-id
    /// order keeps the RNG draws deterministic (Article V). A purr that ends
    /// this tick starts the motor's cooldown and the motor cannot restart it
    /// until the cooldown passes -- a deliberate purr may, at any time
    /// (choice beats reflex).
    fn purr_phase(&mut self, config: &Config) {
        let tick = self.tick;
        for idx in 0..self.kitties.len() {
            let (purring_until, cooldown_until, earned) = {
                let k = &self.kitties[idx];
                (
                    k.purring_until,
                    k.purr_cooldown_until,
                    k.purr_earned(config.thresholds.purr),
                )
            };
            match purring_until {
                Some(until) if tick >= until => {
                    // Spec 022: the motor's rest is proportional to the
                    // finished purr -- one fresh factor draw per end (even
                    // when the bounds are equal), ceiling-rounded so rest
                    // is never shortened. The product is taken in f64,
                    // where it is exact for every validated config (factor
                    // has 24 mantissa bits, duration is bounded by
                    // `validate_purr`), so the ceiling truly never
                    // undercuts. A pre-022 snapshot's in-flight purr
                    // carries no duration; the fixed convention reads it
                    // as min_ticks (FR-012).
                    let duration = self.kitties[idx]
                        .purring_duration
                        .unwrap_or(config.purr.min_ticks);
                    let factor = config.purr.cooldown_factor_min
                        + (config.purr.cooldown_factor_max - config.purr.cooldown_factor_min)
                            * self.rng.gen_f32();
                    let cooldown = (f64::from(factor) * duration as f64).ceil() as u64;
                    self.kitties[idx].purring_until = None;
                    self.kitties[idx].purring_duration = None;
                    self.kitties[idx].purr_cooldown_until = tick + cooldown;
                }
                Some(_) => {}
                None => {
                    if earned && tick >= cooldown_until {
                        self.start_purr(idx, config, tick, PurrOrigin::Motor);
                    }
                }
            }
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
        adjacent_element_in(&self.elements, pos, kind)
    }

    /// The bowl a kitty at `pos` would eat from, if it still holds a serving.
    ///
    /// One predicate, FOUR consumers -- validation of an `Eat` proposal, the
    /// per-tick meal continuation, the end-of-meal rule, and (spec 033)
    /// HereFood's grounding -- so "which bowl, and is it usable" can never
    /// quietly mean different things, and a cat can never announce food it
    /// could not itself eat. Deliberately the *nearest* adjacent bowl
    /// filtered for servings, not the nearest stocked one: a cat at an empty
    /// bowl beside a fuller one pauses (and then ends) rather than
    /// stretching across.
    pub fn adjacent_stocked_chow(&self, pos: Position) -> Option<&Element> {
        adjacent_stocked_chow_in(&self.elements, pos)
    }

    /// Whether any live critter stands on or beside `pos` -- the
    /// existential lift of Play-critter's validate arm (`is_critter() &&
    /// is_adjacent`, spec 033 FR-002): HereCritter is legal exactly when
    /// SOME target would make `Play(critter)` legal. Deliberately not
    /// Chase's predicate, which is distance-unbounded.
    pub fn adjacent_critter(&self, pos: Position) -> bool {
        adjacent_critter_in(&self.elements, pos)
    }

    pub fn count_of(&self, kind: ElementType) -> u32 {
        self.elements
            .iter()
            .filter(|e| e.element_type() == kind)
            .count() as u32
    }

    /// A friend is any other kitty; "available" adds the adjacency an interaction
    /// needs. One body in `available_friend_in` (the free twin), shared with
    /// the dead-scene rule's grooming arm so the two can't drift (spec 048
    /// review).
    pub fn is_available_friend(&self, me: KittyId, friend: KittyId) -> bool {
        self.kitty(me)
            .is_some_and(|k| available_friend_in(&self.kitties, k, friend))
    }

    /// A friend who can be drawn into a duet right now: available *and* doing
    /// nothing. A kitty mid-activity cannot be conscripted out of it (its own
    /// minimum would be broken), and a sleeping cat is never yanked awake to
    /// cuddle. Governs cuddle and social play; co-sleeping and grooming keep
    /// the plain availability rule because they bind nobody.
    pub fn is_conscriptable_friend(&self, me: KittyId, friend: KittyId) -> bool {
        // Availability is the ONE shared body (`available_friend_in`);
        // conscriptability adds "doing nothing" — one check, not two: the
        // strict pairing invariant (clock present exactly when an activity
        // is in progress) makes the clock alone authoritative.
        self.is_available_friend(me, friend)
            && self
                .kitty(friend)
                .is_some_and(|k| k.activity_clock.is_none())
    }

    /// The shared mutual predicate (spec 041 FR-002): the kitty is itself
    /// settled in a pile -- sleeping or resting, the contact-census
    /// definition. The ONE definition of "mutual": co-sleep tier pricing,
    /// warmth conduction (spec 031), and rest tier resolution all call it,
    /// so the three can never disagree about whether a pile is mutual.
    /// (A 2026-08-27 note anticipated waterline contagion hooking in here
    /// too; the shipped spec 044 covers all four paired kinds, not just
    /// the settled two, so its membership is `Activity::partner()` plus
    /// `is_available_friend` in `advance_needs` -- changing this function
    /// does NOT move the contagion charge.)
    pub fn is_settled(&self, id: KittyId) -> bool {
        self.kitty(id).is_some_and(|k| {
            matches!(
                k.activity,
                Activity::Sleeping { .. } | Activity::Resting { .. }
            )
        })
    }

    pub fn push_element(&mut self, element: Element) {
        self.next_element_id = self.next_element_id.max(element.id + 1);
        self.elements.push(element);
    }

    pub(crate) fn allocate_element_id(&mut self) -> ElementId {
        // 0 is skipped by long precedent; the reserved id is never issued
        // (spec 014: downstream encodings use it to mean "no element").
        if self.next_element_id == 0 || self.next_element_id == crate::element::RESERVED_ELEMENT_ID
        {
            self.next_element_id = 1;
        }
        let id = self.next_element_id;
        self.next_element_id = self.next_element_id.wrapping_add(1);
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

/// The duration-enforcement law's ruling for one validated action
/// (spec 006 FR-003/004, one implementation since the spec 014 review).
enum DurationRuling {
    /// No activity in progress (or an unbounded one): the action stands.
    NotGoverned,
    /// The scene continues: the action is rewritten to the continuation.
    Continue(crate::action::Action),
    /// Past the minimum, not a continuation: the activity ends and the
    /// action applies as validated.
    Interrupt,
}

/// What the shared phase pipeline hands back to whichever tick drove it:
/// the per-kitty (validated, applied) pairs in this tick's turn order, and
/// the events the tick produced (spec 014 FR-003).
pub(crate) struct PhaseOutcome {
    pub per_kitty: Vec<(
        KittyId,
        crate::action::Action,
        crate::action::Action,
        Option<crate::meow::MessageKind>,
    )>,
    pub distress_events: Vec<DistressEvent>,
    pub activity_endings: Vec<ActivityEnd>,
}

impl PhaseOutcome {
    /// The (validated, applied, applied_message) triple per kitty, keyed
    /// for record building.
    #[allow(clippy::type_complexity)]
    fn applied_by_id(
        &self,
    ) -> std::collections::BTreeMap<
        KittyId,
        (
            crate::action::Action,
            crate::action::Action,
            Option<crate::meow::MessageKind>,
        ),
    > {
        self.per_kitty
            .iter()
            .map(|&(id, validated, applied, message)| (id, (validated, applied, message)))
            .collect()
    }

    /// Builds the per-kitty tick records for the decisions this outcome
    /// applied — the one record assembler shared by both tick drivers
    /// (spec 014 third review), so the behavior-driven report and the
    /// joint-action report can never drift. `decisions` supplies each
    /// kitty's (id, proposed, provenance, decision seed) in report order.
    pub fn records(
        &self,
        decisions: impl IntoIterator<
            Item = (KittyId, crate::seam::Decision, crate::seam::Provenance, u64),
        >,
    ) -> Vec<crate::seam::KittyTickRecord> {
        let applied_by_id = self.applied_by_id();
        decisions
            .into_iter()
            .map(|(kitty_id, decision, provenance, decision_seed)| {
                let (validated, applied, applied_message) = applied_by_id
                    .get(&kitty_id)
                    .copied()
                    .expect("the phase pipeline hears every kitty that has a decision");
                crate::seam::KittyTickRecord {
                    kitty_id,
                    proposed: decision.activity,
                    validated,
                    applied,
                    proposed_message: decision.message,
                    applied_message,
                    provenance,
                    decision_seed,
                }
            })
            .collect()
    }
}

impl WorldSnapshot {
    pub fn kitty(&self, id: KittyId) -> Option<&Kitty> {
        self.kitties.iter().find(|k| k.id == id)
    }

    /// The dead-scene rule over the decision snapshot -- same body as
    /// `World::counterpart_gone` (spec 048 FR-002, one definition).
    pub(crate) fn counterpart_gone(&self, kitty_id: KittyId) -> bool {
        self.kitty(kitty_id)
            .is_some_and(|k| counterpart_gone_in(k, &self.kitties, &self.elements))
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

    pub fn nearest_friend(&self, me: KittyId, pos: Position) -> Option<&Kitty> {
        self.others(me)
            .min_by_key(|k| (pos.manhattan_distance(&k.pos), k.id))
    }
}

// The adjacency predicates as free functions over an element slice (spec
// 033): `message_legal` rules on the same predicates the actions use, but
// its callers hold a `World` in one place and a `WorldSnapshot` in another
// -- one body here, thin delegating methods above, so the predicate can
// never fork. `is_adjacent` is manhattan <= 1: the speaker's own tile
// counts, uniformly, for every predicate below.

/// The one body of the dead-scene rule (spec 048 FR-002): whether
/// `kitty`'s ongoing activity names a counterpart that `kitties`/`elements`
/// no longer supply. Serves both worlds -- the live one (prune, at the
/// apply slot) and the decision snapshot (`finish_what_you_started`) --
/// via the thin delegating methods, so the ending rule and the
/// don't-continue rule can never fork. A kitty with no activity clock has
/// no scene. Table: specs/048-no-stale-reproposal/data-model.md.
pub(crate) fn counterpart_gone_in(kitty: &Kitty, kitties: &[Kitty], elements: &[Element]) -> bool {
    if kitty.activity_clock.is_none() {
        return false;
    }
    let pos = kitty.pos;
    match kitty.activity {
        // A rest companion, like a co-sleep companion, is re-filtered
        // every serviced tick by the effects arm (spec 041) -- a
        // wandered partner drops the scene to solo posture there, so
        // rest has no prune entry in either shape.
        Activity::Idle
        | Activity::Eating
        | Activity::Sleeping { .. }
        | Activity::Playing { target: None }
        | Activity::Grooming { target: None }
        | Activity::Resting { .. } => false,
        // (An emptied or expired bowl is the meal's own end rule, not a
        // vanished counterpart -- see resolve_activity_ends.)
        Activity::Drinking => adjacent_element_in(elements, pos, ElementType::Water).is_none(),
        Activity::Playing {
            target: Some(TargetRef::Element { id }),
        } => elements
            .iter()
            .find(|e| e.id == id)
            .map(|e| !pos.is_adjacent(&e.pos))
            .unwrap_or(true),
        // A duet whose other side is not bound back to this kitty.
        Activity::Playing {
            target: Some(TargetRef::Kitty { id }),
        } => !kitties
            .iter()
            .find(|k| k.id == id)
            .map(|k| k.activity.duet_partner() == Some(kitty.id))
            .unwrap_or(false),
        // The groomed friend must still be available -- the SAME body
        // `is_available_friend` delegates to, not a replica.
        Activity::Grooming { target: Some(id) } => !available_friend_in(kitties, kitty, id),
    }
}

/// The one body of "available friend" (a distinct, present, adjacent
/// kitty): `World::is_available_friend` and the dead-scene rule's grooming
/// arm both delegate here.
pub(crate) fn available_friend_in(kitties: &[Kitty], me: &Kitty, friend: KittyId) -> bool {
    friend != me.id
        && kitties
            .iter()
            .find(|k| k.id == friend)
            .map(|k| me.pos.is_adjacent(&k.pos))
            .unwrap_or(false)
}

/// The nearest element of `kind` on or beside `pos` (ties broken by id).
pub fn adjacent_element_in(
    elements: &[Element],
    pos: Position,
    kind: ElementType,
) -> Option<&Element> {
    elements
        .iter()
        .filter(|e| e.element_type() == kind && pos.is_adjacent(&e.pos))
        .min_by_key(|e| (pos.manhattan_distance(&e.pos), e.id))
}

/// Eat's predicate (and HereFood's): the nearest adjacent bowl, if it
/// still holds a serving. See `World::adjacent_stocked_chow` for the
/// nearest-not-nearest-stocked reasoning.
pub fn adjacent_stocked_chow_in(elements: &[Element], pos: Position) -> Option<&Element> {
    adjacent_element_in(elements, pos, ElementType::Chow)
        .filter(|e| matches!(e.kind, ElementKind::Chow { servings } if servings > 0))
}

/// HereCritter's predicate: some live critter on or beside `pos` -- the
/// existential lift of Play-critter's validate arm. See
/// `World::adjacent_critter`.
pub fn adjacent_critter_in(elements: &[Element], pos: Position) -> bool {
    elements
        .iter()
        .any(|e| e.element_type().is_critter() && pos.is_adjacent(&e.pos))
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

    /// Drops a permanent water tile at `pos` (spec 024 test rigging).
    fn add_water(world: &mut World, pos: Position) {
        world.elements.push(Element {
            id: 9_000 + world.elements.len() as ElementId,
            kind: ElementKind::Water,
            pos,
            ttl: None,
        });
    }

    /// Moves the needle to an exact value regardless of the world's start.
    fn set_need(world: &mut World, id: KittyId, kind: NeedKind, target: f32) {
        let current = world.kitty(id).unwrap().needs.get(kind);
        world
            .kitties
            .iter_mut()
            .find(|k| k.id == id)
            .unwrap()
            .needs
            .add(kind, target - current);
    }

    #[test]
    fn water_occupancy_charges_bath_on_top_of_ambient() {
        let config = test_config();
        let mut world = World::generate(&config);
        let dry_pos = world.kitties[1].pos;
        let wet_pos = world.kitties[0].pos;
        add_water(&mut world, wet_pos);
        // Same starting point for a clean read.
        set_need(&mut world, 1, NeedKind::Bath, 10.0);
        set_need(&mut world, 2, NeedKind::Bath, 10.0);
        assert_ne!(dry_pos, wet_pos);

        world.advance_needs(&config);

        let wet = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        let dry = world.kitty(2).unwrap().needs.get(NeedKind::Bath);
        // Ambient rise is identical; the difference is exactly the charge.
        assert!(
            (wet - dry - config.water.bath_gain).abs() < 1e-4,
            "wet {wet}, dry {dry}, gain {}",
            config.water.bath_gain
        );
        // FR-002: charge and ambient are additive, not either-or.
        assert!((dry - 10.0 - config.needs.bath).abs() < 1e-4);
        // The same tick's happiness already reflects the charge.
        assert!(
            world.kitty(1).unwrap().happiness < world.kitty(2).unwrap().happiness,
            "the swimmer's happiness must feel the charge this tick"
        );
    }

    #[test]
    fn the_charge_gates_on_the_pre_charge_value() {
        let config = test_config();
        let mut world = World::generate(&config);
        let pos = world.kitties[0].pos;
        add_water(&mut world, pos);
        let ceiling = config.water.bath_gain_ceiling;

        // At the ceiling before the check: ambient pushes past it, no charge.
        set_need(&mut world, 1, NeedKind::Bath, ceiling);
        world.advance_needs(&config);
        let bath = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        assert!(
            (bath - (ceiling + config.needs.bath)).abs() < 1e-4,
            "at {bath}: above the ceiling only ambient applies"
        );

        // Just under after ambient: the charge lands whole -- bounded
        // overshoot of at most one scaled charge (the validated headroom).
        set_need(
            &mut world,
            1,
            NeedKind::Bath,
            ceiling - config.needs.bath - 0.1,
        );
        world.advance_needs(&config);
        let bath = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        let expected = ceiling - 0.1 + config.water.bath_gain;
        assert!(
            (bath - expected).abs() < 1e-3,
            "at {bath}, expected {expected}: one whole charge, then done"
        );
        assert!(bath > ceiling, "the overshoot case is real");

        // And the tick after the overshoot: ambient only, forever.
        world.advance_needs(&config);
        let after = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        assert!((after - (bath + config.needs.bath)).abs() < 1e-4);
    }

    #[test]
    fn the_charge_scales_with_the_bath_trait() {
        use crate::config::NeedRateOverrides;

        let mut config = test_config();
        config.kitties[0].needs = Some(NeedRateOverrides {
            bath: Some(config.needs.bath * 2.0), // ratio 2: a fussy cat
            ..Default::default()
        });
        config.validate().expect("valid");
        let mut world = World::generate(&config);
        let (p1, p2) = (world.kitties[0].pos, world.kitties[1].pos);
        add_water(&mut world, p1);
        add_water(&mut world, p2);
        set_need(&mut world, 1, NeedKind::Bath, 0.0);
        set_need(&mut world, 2, NeedKind::Bath, 0.0);

        world.advance_needs(&config);

        let fussy = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        let plain = world.kitty(2).unwrap().needs.get(NeedKind::Bath);
        let expected_fussy = config.needs.bath * 2.0 + config.water.bath_gain * 2.0;
        let expected_plain = config.needs.bath + config.water.bath_gain;
        assert!((fussy - expected_fussy).abs() < 1e-4, "fussy at {fussy}");
        assert!((plain - expected_plain).abs() < 1e-4, "plain at {plain}");
    }

    #[test]
    fn gain_zero_disables_wet_fur_entirely() {
        let mut config = test_config();
        config.water.bath_gain = 0.0;
        config
            .validate()
            .expect("0 is legal: disables the mechanic");
        let mut world = World::generate(&config);
        let pos = world.kitties[0].pos;
        add_water(&mut world, pos);
        set_need(&mut world, 1, NeedKind::Bath, 10.0);

        world.advance_needs(&config);

        let bath = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        assert!((bath - 10.0 - config.needs.bath).abs() < 1e-4);
    }

    #[test]
    fn adjacency_is_free_only_occupancy_pays() {
        // FR-003: water as a drinking DESTINATION costs nothing -- the
        // charge attaches to standing on the tile, never to being beside
        // it (where drinking happens).
        let config = test_config();
        let mut world = World::generate(&config);
        let pos = world.kitties[0].pos;
        let beside = Position::new(pos.x + 1, pos.y);
        add_water(&mut world, beside);
        set_need(&mut world, 1, NeedKind::Bath, 10.0);

        world.advance_needs(&config);

        let bath = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        assert!(
            (bath - 10.0 - config.needs.bath).abs() < 1e-4,
            "adjacent cat pays ambient only, at {bath}"
        );
        // And Drink validates from adjacency exactly as before.
        let verdict = action::validate(&world, 1, Action::Drink, &config);
        assert_eq!(verdict, Action::Drink, "drinking stays free and legal");
    }

    #[test]
    fn moving_onto_water_is_one_ordinary_step() {
        // FR-003: movement is untouched -- one tile per tick, wet or dry.
        let config = test_config();
        let mut world = World::generate(&config);
        let start = world.kitties[0].pos;
        let dest = Position::new(start.x + 1, start.y);
        // Clear the destination of kitties, then flood it.
        if let Some(other) = world.kitty_at(dest).map(|k| k.id) {
            let far = Position::new(0, 0);
            world
                .kitties
                .iter_mut()
                .find(|k| k.id == other)
                .unwrap()
                .pos = far;
        }
        add_water(&mut world, dest);

        action::apply(
            &mut world,
            1,
            Action::Move {
                direction: Direction::East,
            },
            &config,
        );
        assert_eq!(
            world.kitty(1).unwrap().pos,
            dest,
            "a wet destination is entered exactly like a dry one"
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

    // ---- sustained purring (spec 011, amended by spec 022) ---------------

    #[test]
    fn announce_arming_rises_holds_and_falls_on_the_hysteresis_edges() {
        // Spec 028 US2: armed at >= threshold, held anywhere in the band
        // [threshold - hysteresis, threshold), disarmed only below it. The
        // three edges of the band, walked explicitly (defaults 30/5).
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        let set = |world: &mut World, value: f32| {
            let current = world.kitties[idx].needs.get(crate::needs::NeedKind::Eat);
            world.kitties[idx]
                .needs
                .add(crate::needs::NeedKind::Eat, value - current);
        };
        let armed = |world: &World| {
            world.kitties[idx]
                .announce_armed
                .contains(&crate::needs::NeedKind::Eat)
        };

        // Rising: just below the threshold stays disarmed...
        set(&mut world, 29.9);
        world.update_announce_arming(&config);
        assert!(!armed(&world), "below threshold never arms");
        // ...at the threshold arms.
        set(&mut world, 30.0);
        world.update_announce_arming(&config);
        assert!(armed(&world), "the threshold is inclusive");

        // Held: relief into the band keeps the word speakable mid-errand.
        set(&mut world, 26.0);
        world.update_announce_arming(&config);
        assert!(armed(&world), "the band holds an armed kind");

        // Falling: below threshold - hysteresis disarms.
        set(&mut world, 24.9);
        world.update_announce_arming(&config);
        assert!(!armed(&world), "below the band disarms");

        // And a disarmed kind in the band stays disarmed (no re-arm from
        // below): the band holds state, it never creates it.
        set(&mut world, 27.0);
        world.update_announce_arming(&config);
        assert!(!armed(&world), "the band holds a disarmed kind too");
    }

    #[test]
    fn no_purr_start_of_either_origin_stamps_meow_bookkeeping() {
        // Spec 023 US3 scenario 3 -- the 022 FR-008 handoff, guarded from
        // this side: motor starts (silent or announcing) and deliberate
        // starts write nothing into `meow_cooldowns`.
        for p in [0.0f32, 1.0] {
            let (mut world, mut config) = test_world();
            config.purr.announce_probability = p;
            world.tick = 10;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].happiness = 90.0;
            world.purr_phase(&config); // motor start
            let kitty = world.kitty(1).unwrap();
            assert!(kitty.purring_until.is_some());
            assert!(
                !kitty
                    .meow_cooldowns
                    .contains_key(&crate::meow::MessageKind::Purr),
                "motor start (p = {p}) stamped bookkeeping"
            );
        }

        let (mut world, config) = test_world();
        world.tick = 10;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0;
        // The deliberate purr rides the message channel since spec 028.
        crate::action::apply_message(&mut world, 1, crate::meow::MessageKind::Purr, &config, 10);
        let kitty = world.kitty(1).unwrap();
        assert!(kitty.purring_until.is_some(), "the deliberate purr started");
        assert!(
            !kitty
                .meow_cooldowns
                .contains_key(&crate::meow::MessageKind::Purr),
            "a deliberate start stamped bookkeeping"
        );
    }

    #[test]
    fn per_tick_meowing_stays_bounded_by_the_pruning_window() {
        // Spec 023 (US1 scenario 2): no engine cap on emission, but the
        // record cannot grow without limit -- pruning holds it to the
        // retention window.
        let (mut world, config) = test_world();
        for _ in 0..200 {
            world.tick += 1;
            let tick = world.tick;
            world.recent_meows.push(crate::meow::Meow {
                kitty_id: 1,
                kind: crate::meow::MessageKind::WantPlay,
                tick,
                intensity: 0.0,
            });
            world.prune_transient(&config);
        }
        assert!(
            world.recent_meows.len() as u64 <= config.meow.recent_window_ticks + 1,
            "bounded: {} entries for window {}",
            world.recent_meows.len(),
            config.meow.recent_window_ticks
        );
    }

    /// One scripted "tick" of the purr surfaces: randomized moods, one
    /// kitty attempting the deliberate purr through validation, then the
    /// purr phase. Shared by the determinism tests so both runs replay the
    /// identical script.
    fn purr_script_tick(world: &mut World, config: &Config, scratch: &mut SimRng) {
        world.tick += 1;
        for idx in 0..world.kitties.len() {
            world.kitties[idx].happiness = scratch.gen_range_u32(0, 101) as f32;
            world.kitties[idx].happiness_rose = scratch.gen_bool(0.3);
        }
        let choose = scratch.gen_range_u32(0, world.kitties.len() as u32) as usize;
        let id = world.kitties[choose].id;
        let validated = crate::action::validate(
            world,
            id,
            crate::action::Action::Meow {
                message: crate::meow::MessageKind::Purr,
            },
            config,
        );
        crate::action::apply(world, id, validated, config);
        world.purr_phase(config);
    }

    #[test]
    fn same_seed_purr_trajectories_replay_exactly_with_both_origins() {
        // Spec 022 SC-006: same seed + config + ticks -> identical world,
        // with motor and deliberate purrs interleaving.
        let run = || {
            let (mut world, config) = test_world();
            world.rng = SimRng::from_seed(9);
            let mut scratch = SimRng::from_seed(13);
            for _ in 0..300 {
                purr_script_tick(&mut world, &config, &mut scratch);
            }
            serde_json::to_string(&world).unwrap()
        };
        assert_eq!(run(), run());
    }

    #[test]
    fn purr_determinism_survives_a_mid_purr_save_and_restore() {
        // Spec 022 FR-012/SC-006: a world saved mid-purr and restored
        // replays exactly what the uninterrupted run does -- including the
        // proportional cooldown stamped from the restored duration.
        let (mut a, config) = test_world();
        a.rng = SimRng::from_seed(31);
        let mut scratch = SimRng::from_seed(77);
        for _ in 0..40 {
            purr_script_tick(&mut a, &config, &mut scratch);
        }
        assert!(
            a.kitties.iter().any(|k| k.purring_until.is_some()),
            "the save point should catch someone mid-purr"
        );

        // Save/restore the whole world (RNG state included) and continue
        // both copies with identically-seeded scratch streams.
        let saved = serde_json::to_string(&a).unwrap();
        let mut b: World = serde_json::from_str(&saved).unwrap();
        let mut scratch_b = scratch.clone();
        for _ in 0..120 {
            purr_script_tick(&mut a, &config, &mut scratch);
            purr_script_tick(&mut b, &config, &mut scratch_b);
        }
        assert_eq!(
            serde_json::to_string(&a).unwrap(),
            serde_json::to_string(&b).unwrap(),
            "the restored world replays the uninterrupted one exactly"
        );
    }

    #[test]
    fn every_purr_of_either_origin_certifies_an_earned_cat() {
        // Spec 022 SC-003 property: across randomized seeds, moods, and
        // purr configs, a purr never starts -- by motor or by choice --
        // unless the earned rule held at that moment.
        for seed in 0..20u64 {
            let (mut world, mut config) = test_world();
            world.rng = SimRng::from_seed(seed);
            config.thresholds.purr = 50.0 + (seed % 5) as f32 * 10.0;
            config.purr.min_ticks = 2 + seed % 4;
            config.purr.max_ticks = config.purr.min_ticks + seed % 7;
            let mut scratch = SimRng::from_seed(seed ^ 0x00C0_FFEE);

            for _ in 0..2_000 {
                world.tick += 1;
                let tick = world.tick;
                let mut was_purring = Vec::new();
                for idx in 0..world.kitties.len() {
                    world.kitties[idx].happiness = scratch.gen_range_u32(0, 101) as f32;
                    world.kitties[idx].happiness_rose = scratch.gen_bool(0.3);
                    was_purring.push(world.kitties[idx].purring_until.is_some());
                }
                // A random kitty tries the deliberate path each tick; the
                // validate gate decides whether the choice is lawful.
                let choose = scratch.gen_range_u32(0, world.kitties.len() as u32) as usize;
                let id = world.kitties[choose].id;
                let validated = crate::action::validate(
                    &world,
                    id,
                    crate::action::Action::Meow {
                        message: crate::meow::MessageKind::Purr,
                    },
                    &config,
                );
                crate::action::apply(&mut world, id, validated, &config);
                world.purr_phase(&config);

                for (idx, was) in was_purring.iter().enumerate() {
                    let k = &world.kitties[idx];
                    if !was && k.purring_until.is_some() {
                        assert!(
                            k.happiness > config.thresholds.purr || k.happiness_rose,
                            "seed {seed} tick {tick}: a purr started unearned"
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn an_earned_kitty_starts_purring_with_a_bounded_draw_and_one_meow() {
        // Re-baselined by spec 022 (FR-015): the motor announces per
        // `announce_probability`; the spec-011 one-meow-per-purr guarantee
        // is asserted against an always-announcing world (p = 1), exactly
        // the pre-022 behavior.
        let (mut world, mut config) = test_world();
        config.purr.announce_probability = 1.0;
        world.tick = 50;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0; // past the purr threshold
        world.kitties[idx].happiness_rose = false;

        world.purr_phase(&config);

        let kitty = world.kitty(1).unwrap();
        let until = kitty.purring_until.expect("an earned kitty rumbles");
        let duration = until - 50;
        assert!(
            (config.purr.min_ticks..=config.purr.max_ticks).contains(&duration),
            "duration {duration} outside [{}, {}]",
            config.purr.min_ticks,
            config.purr.max_ticks
        );
        let purr_meows = |world: &World| {
            world
                .recent_meows
                .iter()
                .filter(|m| m.kitty_id == 1 && m.kind == crate::meow::MessageKind::Purr)
                .count()
        };
        assert_eq!(purr_meows(&world), 1, "exactly one meow, at purr start");
        assert!(
            !world
                .kitty(1)
                .unwrap()
                .meow_cooldowns
                .contains_key(&crate::meow::MessageKind::Purr),
            "purr starts stamp no message cooldown (spec 022 FR-008; 023 re-verifies)"
        );

        // Further purring ticks announce nothing.
        world.tick = 51;
        world.purr_phase(&config);
        assert_eq!(world.kitty(1).unwrap().purring_until, Some(until));
        assert_eq!(purr_meows(&world), 1);
    }

    #[test]
    fn the_default_motor_is_silent_at_an_unchanged_cadence() {
        // Spec 022 US2: at the default announce probability (0) the motor
        // purrs exactly as it would at p = 1 -- same starts, same
        // durations -- but records no announcement and stamps nothing.
        let (mut world, config) = test_world();
        assert_eq!(config.purr.announce_probability, 0.0, "default is silent");
        world.tick = 50;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0;

        world.purr_phase(&config);

        let kitty = world.kitty(1).unwrap();
        assert!(kitty.purring_until.is_some(), "the rumble is unchanged");
        assert!(
            world.recent_meows.is_empty(),
            "a silent start records no announcement"
        );
        assert!(
            !kitty
                .meow_cooldowns
                .contains_key(&crate::meow::MessageKind::Purr),
            "a silent start stamps nothing"
        );
    }

    #[test]
    fn purr_timings_are_identical_across_announce_probabilities() {
        // Spec 022 FR-011 shape rule (research D10): the announce decision
        // is drawn even at 0 and 1, so flipping the probability changes
        // what is heard, never when purrs start or end.
        let run = |p: f32| -> Vec<(u64, Option<u64>)> {
            let (mut world, mut config) = test_world();
            config.purr.announce_probability = p;
            world.rng = SimRng::from_seed(7);
            let mut scratch = SimRng::from_seed(99);
            let mut timeline = Vec::new();
            for _ in 0..400 {
                world.tick += 1;
                for idx in 0..world.kitties.len() {
                    // Same mood script on both runs (independent stream).
                    world.kitties[idx].happiness = scratch.gen_range_u32(0, 101) as f32;
                    world.kitties[idx].happiness_rose = scratch.gen_bool(0.3);
                }
                world.purr_phase(&config);
                timeline.push((world.tick, world.kitty(1).unwrap().purring_until));
            }
            timeline
        };

        assert_eq!(run(0.0), run(1.0), "announcements differ; timings must not");
    }

    #[test]
    fn a_finished_purr_rests_by_a_drawn_factor_of_its_own_length() {
        // Spec 022 FR-009 / US3 scenario 1: the stamp is ⌈factor × the
        // finished purr's actual duration⌉ with the factor drawn per end;
        // equal bounds make the expectation exact, unequal bounds bound it.
        let (mut world, mut config) = test_world();
        config.purr.cooldown_factor_min = 2.25;
        config.purr.cooldown_factor_max = 2.25;
        world.tick = 100;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].purring_until = Some(100); // ends this tick
        world.kitties[idx].purring_duration = Some(9);
        for k in world.kitties.iter_mut() {
            k.happiness = 10.0; // nobody else starts or ends anything
            k.happiness_rose = false;
        }

        world.purr_phase(&config);

        let kitty = world.kitty(1).unwrap();
        assert_eq!(kitty.purring_until, None);
        assert_eq!(kitty.purring_duration, None, "cleared together");
        // 2.25 × 9 = 20.25 → 21: the ceiling never shortens rest.
        assert_eq!(kitty.purr_cooldown_until, 100 + 21);

        // Unequal bounds: same seed reproduces the same stamp exactly, and
        // it always lies within the ceil(min×d)..=ceil(max×d) envelope.
        let stamp = |seed: u64| -> u64 {
            let (mut world, mut config) = test_world();
            config.purr.cooldown_factor_min = 1.75;
            config.purr.cooldown_factor_max = 2.75;
            world.rng = SimRng::from_seed(seed);
            world.tick = 100;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].purring_until = Some(100);
            world.kitties[idx].purring_duration = Some(9);
            for k in world.kitties.iter_mut() {
                k.happiness = 10.0;
                k.happiness_rose = false;
            }
            world.purr_phase(&config);
            world.kitty(1).unwrap().purr_cooldown_until - 100
        };
        for seed in 0..10 {
            let s = stamp(seed);
            assert_eq!(s, stamp(seed), "seed-reproducible");
            let lo = (1.75f32 * 9.0).ceil() as u64; // 16
            let hi = (2.75f32 * 9.0).ceil() as u64; // 25
            assert!((lo..=hi).contains(&s), "stamp {s} outside [{lo}, {hi}]");
        }
    }

    #[test]
    fn a_pre_022_snapshot_mid_purr_rests_by_the_min_ticks_convention() {
        // FR-012 (clarified 2026-07-31): a restored pre-022 purr carries no
        // stored duration; the cooldown treats it as min_ticks -- a fixed
        // convention, biased to the shortest lawful rest.
        let (mut world, mut config) = test_world();
        config.purr.cooldown_factor_min = 2.25;
        config.purr.cooldown_factor_max = 2.25;
        world.tick = 100;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].purring_until = Some(100);
        world.kitties[idx].purring_duration = None; // the pre-022 shape
        for k in world.kitties.iter_mut() {
            k.happiness = 10.0;
            k.happiness_rose = false;
        }

        world.purr_phase(&config);

        let expected = (2.25f32 * config.purr.min_ticks as f32).ceil() as u64;
        assert_eq!(
            world.kitty(1).unwrap().purr_cooldown_until,
            100 + expected,
            "unknown duration reads as min_ticks"
        );
    }

    #[test]
    fn happy_kitty_occupancy_holds_the_factor_midpoint_duty_cycle() {
        // Spec 022 SC-004: occupancy within 2pp of 1/(1 + mean factor
        // bounds) over ≥20k ticks, independent of the duration bounds and
        // of the factor spread (configs share the 2.25 midpoint).
        let configs: [(u64, u64, f32, f32); 2] = [
            (8, 13, 1.75, 2.75), // the defaults
            (3, 20, 2.25, 2.25), // wild durations, fixed factor
        ];
        for (min_t, max_t, f_min, f_max) in configs {
            let (mut world, mut config) = test_world();
            config.purr.min_ticks = min_t;
            config.purr.max_ticks = max_t;
            config.purr.cooldown_factor_min = f_min;
            config.purr.cooldown_factor_max = f_max;
            world.rng = SimRng::from_seed(4242);
            let idx = world.kitty_index(1).unwrap();
            let mut purring_ticks = 0u64;
            const TICKS: u64 = 20_000;
            for _ in 0..TICKS {
                world.tick += 1;
                for k in world.kitties.iter_mut() {
                    k.happiness = 95.0; // a healthy meadow, pinned
                }
                world.purr_phase(&config);
                if world.kitties[idx].purring_until.is_some() {
                    purring_ticks += 1;
                }
            }
            let occupancy = purring_ticks as f64 / TICKS as f64;
            let target = 1.0 / (1.0 + (f_min + f_max) as f64 / 2.0);
            assert!(
                (occupancy - target).abs() < 0.02,
                "occupancy {occupancy:.4} vs target {target:.4} \
                 for ({min_t}, {max_t}, {f_min}, {f_max})"
            );
        }
    }

    #[test]
    fn the_cooldown_holds_an_earned_purr_back() {
        let (mut world, config) = test_world();
        world.tick = 60;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0;
        world.kitties[idx].purr_cooldown_until = 100;

        world.purr_phase(&config);
        assert_eq!(
            world.kitty(1).unwrap().purring_until,
            None,
            "still resting its motor"
        );

        world.tick = 100;
        world.purr_phase(&config);
        assert!(
            world.kitty(1).unwrap().purring_until.is_some(),
            "the cooldown expiring reopens the rumble"
        );
    }

    #[test]
    fn a_purr_ends_on_schedule_and_stamps_the_cooldown() {
        // Re-baselined by spec 022: the stamp is proportional now. Equal
        // factor bounds make the expected rest exact.
        let (mut world, mut config) = test_world();
        config.purr.cooldown_factor_min = 2.25;
        config.purr.cooldown_factor_max = 2.25;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0; // earned throughout -- gates nothing mid-purr
        world.kitties[idx].purring_until = Some(80);
        world.kitties[idx].purring_duration = Some(9);

        world.tick = 79;
        world.purr_phase(&config);
        assert_eq!(world.kitty(1).unwrap().purring_until, Some(80));

        world.tick = 80;
        world.purr_phase(&config);
        let kitty = world.kitty(1).unwrap();
        assert_eq!(kitty.purring_until, None, "the rumble winds down on time");
        assert_eq!(
            kitty.purr_cooldown_until,
            80 + 21, // ⌈2.25 × 9⌉
            "and the motor rests in proportion to the finished purr"
        );
    }

    #[tokio::test]
    async fn a_purring_kitty_still_takes_its_turn() {
        // Spec 011 SC-001: the action slot is provably free -- a rumbling
        // kitty beside its bowl begins eating while the purr carries on.
        let config = Arc::new(test_config());
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
        world.kitties[idx].purring_until = Some(1_000);
        world.kitties[idx].set_meow_cooldown(crate::meow::MessageKind::WantEat, u64::MAX);
        world.push_element(Element {
            id: 970,
            kind: ElementKind::Chow { servings: 5 },
            pos: Position::new(5, 6),
            ttl: None,
        });

        world.tick(&registry, &config).await;

        let kitty = world.kitty(1).unwrap();
        assert!(
            matches!(kitty.activity, Activity::Eating),
            "dinner proceeds, purr or no purr (got {:?})",
            kitty.activity
        );
        assert_eq!(
            kitty.purring_until,
            Some(1_000),
            "and the rumble never paused"
        );
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
        assert_eq!(
            p.closest, 24,
            "(2,2) to (14,14) is 24 walking steps (spec 009: Manhattan)"
        );

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
        assert_eq!(p.closest, 16, "(6,6) to (14,14) is 16 walking steps");
        assert_eq!(
            p.improved_at, 11,
            "gaining ground resets the patience clock"
        );
    }

    #[test]
    fn converting_a_diagonal_offset_into_a_straight_one_counts_as_progress() {
        // Spec 009 US2: a kitty one diagonal step from its quarry cannot catch
        // it (orthogonal-only interactions) -- stepping to a compass neighbour
        // is the move that makes the catch possible. In Chebyshev both
        // positions measured 1 and the patience clock saw a stall; Manhattan
        // sees 2 become 1 and resets it.
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        let other = world.kitty_index(2).unwrap();
        world.kitties[other].pos = Position::new(0, 15);
        world.push_element(Element {
            id: 910,
            kind: ElementKind::Greeble {
                heading: Direction::North,
            },
            pos: Position::new(6, 6), // one diagonal step away
            ttl: Some(500),
        });
        let target = TargetRef::Element { id: 910 };

        world.tick = 10;
        world.update_pursuit(1, Action::Chase(target), &config);
        assert_eq!(world.kitty(1).unwrap().pursuit.unwrap().closest, 2);

        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(6, 5); // now beside it
        world.tick = 11;
        world.update_pursuit(1, Action::Chase(target), &config);
        let p = world.kitty(1).unwrap().pursuit.unwrap();
        assert_eq!(p.closest, 1);
        assert_eq!(
            p.improved_at, 11,
            "closing the corner is real, catch-enabling progress"
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

        // Reposition +1/+1 each iteration: two walking steps closer per tick.
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
    fn a_refused_proposal_is_stamped_with_kitty_proposal_and_tick() {
        // Spec 046 US1-1/US1-2 + the legacy edge case: a non-Idle proposal
        // resolved to Idle by validation records exactly one event carrying
        // the kitty, the proposal VERBATIM, and the tick it was heard --
        // `absorbed == false` when no scene was there to continue (a taxed
        // tick). A chosen Idle is not a refusal. A stray legacy proposal
        // (Purr, retired spec 011) IS one: the stamp reports the enforcement
        // surface faithfully.
        let config = test_config();
        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0); // kitty 1
        world.kitties[1].pos = Position::new(1, 0); // kitty 2, blocking east

        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::move_to(Direction::East)); // occupied cell
        proposals.propose(2, Action::Purr); // retired action, always refused
        world.tick_with_proposals(&proposals, &config);

        let events = world.refusal_log.to_vec();
        assert_eq!(events.len(), 2, "two refusals, two events: {events:?}");
        let moved = events.iter().find(|e| e.kitty_id == 1).unwrap();
        assert_eq!(
            moved.proposed,
            Action::move_to(Direction::East),
            "the proposal rides verbatim, not the applied Idle"
        );
        assert_eq!(moved.tick, 0, "stamped on the tick it was heard");
        assert!(!moved.absorbed, "no scene absorbed it: a taxed tick");
        let purred = events.iter().find(|e| e.kitty_id == 2).unwrap();
        assert_eq!(purred.proposed, Action::Purr);
        assert!(!purred.absorbed);

        // A chosen Idle records nothing (US1-2): the ring does not grow.
        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::Idle);
        world.tick_with_proposals(&proposals, &config);
        assert_eq!(
            world.refusal_log.len(),
            2,
            "a chosen Idle is not a refusal; nor is a substituted one"
        );
    }

    #[test]
    fn duration_enforcement_decides_the_absorbed_flag_never_the_refusal() {
        // Spec 046 US1-3 (Experiments ruling b, 2026-09-01): duration
        // enforcement never creates or suppresses a refusal event -- it only
        // decides the flag. (a) A LEGAL different action proposed inside a
        // scene minimum is continuation-overridden, not refused: NO event.
        // (b) An ILLEGAL proposal inside the minimum is refused AND the
        // scene continues: one event, `absorbed == true` (nothing lost).
        let config = test_config();
        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0); // kitty 1
        world.kitties[1].pos = Position::new(5, 5); // kitty 2, far away

        // Tick 0: both start a solo sleep (always legal; min 3 governs).
        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::Sleep { with: None });
        proposals.propose(2, Action::Sleep { with: None });
        world.tick_with_proposals(&proposals, &config);
        assert!(world.refusal_log.is_empty(), "legal starts refuse nothing");
        for id in [1, 2] {
            assert!(
                world.kitty(id).unwrap().activity_clock.is_some(),
                "kitty {id} is mid-scene"
            );
        }

        // Tick 1, inside the minimum: kitty 1 proposes a LEGAL move (east is
        // empty), kitty 2 an ILLEGAL Purr.
        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::move_to(Direction::East));
        proposals.propose(2, Action::Purr);
        world.tick_with_proposals(&proposals, &config);

        let events = world.refusal_log.to_vec();
        assert_eq!(
            events.len(),
            1,
            "the legal override is not a refusal; the illegal one is: {events:?}"
        );
        assert_eq!(events[0].kitty_id, 2);
        assert_eq!(events[0].proposed, Action::Purr);
        assert_eq!(events[0].tick, 1);
        assert!(
            events[0].absorbed,
            "the scene continued: refusal heard, nothing lost"
        );
        // Both scenes really did continue (the flag told the truth).
        for id in [1, 2] {
            assert!(
                matches!(world.kitty(id).unwrap().activity, Activity::Sleeping { .. }),
                "kitty {id} kept sleeping through the minimum"
            );
        }
    }

    #[test]
    fn a_refusal_past_the_scene_minimum_is_still_absorbed() {
        // Experiments ruling (a) on review-medium finding 1 (2026-09-01):
        // `absorbed` means "the kitty was MID-SCENE and the scene
        // continued", NOT "a scene minimum was still binding". Past the
        // minimum a legal proposal could lawfully have ended the scene --
        // but that difference is proposal quality (the absorbed rows'
        // step-4/H6 evidence), not welfare cost: the taxed count stays
        // F-033-comparable (idle ticks) only if this event stays
        // absorbed == true. Pinned so nobody later "corrects" it toward
        // minimum-only semantics.
        let config = test_config();
        let min = config.actions.durations.sleep.min;
        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0);
        world.kitties[1].pos = Position::new(5, 5);
        // A deep sleep debt so the scene outlives its minimum (a scene ends
        // past min once its governing need hits 0 -- resolve_activity_ends).
        world.kitties[0].needs.sleep = crate::needs::Need::new(100.0);

        // Tick 0: a solo sleep. Then idle through the minimum.
        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::Sleep { with: None });
        world.tick_with_proposals(&proposals, &config);
        while world
            .kitty(1)
            .unwrap()
            .activity_clock
            .expect("the sleep outlives the minimum on this seed")
            .serviced_before(world.tick)
            < min
        {
            world.tick_with_proposals(&crate::seam::JointProposal::new(), &config);
        }
        assert!(
            matches!(world.kitty(1).unwrap().activity, Activity::Sleeping { .. }),
            "still mid-scene, minimum already met -- else this test is vacuous"
        );

        // Past the minimum: an ILLEGAL proposal (Purr is retired).
        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::Purr);
        world.tick_with_proposals(&proposals, &config);

        let events = world.refusal_log.to_vec();
        assert_eq!(events.len(), 1, "one refusal: {events:?}");
        assert!(
            events[0].absorbed,
            "past-minimum refusal inside a continuing scene is ABSORBED \
             (ruling (a)): the kitty kept a need-relieving scene; what it \
             lost is proposal quality, not the tick"
        );
        assert!(
            matches!(world.kitty(1).unwrap().activity, Activity::Sleeping { .. }),
            "and the scene really did continue"
        );
    }

    #[test]
    fn the_refusal_ring_honors_configured_retention() {
        // Spec 046 US2-2: the generic EventLog trim is covered in events.rs;
        // this pins the CONFIG WIRING -- `[events] refusal_retention` is the
        // capacity `World::generate` actually hands the ring.
        let mut config = test_config();
        config.events.refusal_retention = 3;
        config.validate().expect("retention 3 is legal");
        let mut world = World::generate(&config);

        // Five refusals: a stray Purr each tick (always refused, no scene).
        for _ in 0..5 {
            let mut proposals = crate::seam::JointProposal::new();
            proposals.propose(1, Action::Purr);
            world.tick_with_proposals(&proposals, &config);
        }

        let ticks: Vec<u64> = world.refusal_log.to_vec().iter().map(|e| e.tick).collect();
        assert_eq!(
            ticks,
            vec![2, 3, 4],
            "the ring holds the newest 3 of 5, oldest dropped first"
        );
    }

    #[test]
    fn a_refused_partnered_proposal_carries_the_asked_partner() {
        // Spec 046 US1-4 / SC-002: the census can name WHO was asked. A
        // refused social play (partner out of reach) records the proposal
        // verbatim, target included -- never the enforced Idle.
        let config = test_config();
        let mut world = World::generate(&config);
        world.kitties[0].pos = Position::new(0, 0); // kitty 1
        world.kitties[1].pos = Position::new(9, 9); // kitty 2: not adjacent

        let mut proposals = crate::seam::JointProposal::new();
        proposals.propose(1, Action::play_with(TargetRef::Kitty { id: 2 }));
        world.tick_with_proposals(&proposals, &config);

        let events = world.refusal_log.to_vec();
        assert_eq!(events.len(), 1, "one refused play: {events:?}");
        assert_eq!(
            events[0].proposed,
            Action::play_with(TargetRef::Kitty { id: 2 }),
            "the event names the asked partner"
        );
        assert!(!events[0].absorbed);
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

    /// Spec 048 SC-005 must-stay-green: the SAME-TICK race stays a genuine,
    /// stamped refusal. The partner lawfully interrupts the duet in its own
    /// earlier slot; this cat's continuation — decided when the duet was
    /// still live — is then refused and recorded `absorbed = false`. The
    /// spec-048 rule reads the DECISION snapshot and must never see (or
    /// suppress) this.
    #[test]
    fn a_same_tick_duet_race_is_still_a_stamped_refusal() {
        // Both role assignments run (interrupter/proposer swapped); the fair
        // turn-order draw decides which one realizes the race (interrupter
        // first). Exactly the realized one must stamp the un-absorbed
        // refusal. Each interrupter steps AWAY from its partner (a step
        // into the partner's tile would be illegal and interrupt nothing).
        let race_row = |interrupter: KittyId, proposer: KittyId, away: Direction| {
            let (mut world, config) = duet_stage();
            for id in [1, 2] {
                let idx = world.kitty_index(id).unwrap();
                world.kitties[idx].needs.add(NeedKind::Play, 100.0);
                world.kitties[idx].activity = Activity::Playing {
                    target: Some(TargetRef::Kitty { id: 3 - id }),
                };
                // Past the play minimum: interruptible.
                world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock {
                    started: 97,
                    applied: 99,
                    mutual_ticks: 0,
                    drip_ticks: 0,
                });
            }
            let tick = world.tick;
            let config = std::sync::Arc::new(config);
            world.tick_with_proposals(
                &crate::seam::JointProposal::from_actions([
                    (interrupter, Action::move_to(away)),
                    (
                        proposer,
                        Action::play_with(TargetRef::Kitty { id: interrupter }),
                    ),
                ]),
                &config,
            );
            // absorbed = false is the race signature: the duet ended both
            // sides in the interrupter's earlier slot, so nothing continued.
            // (Proposer-first instead yields an absorbed = true row: the
            // still-live scene absorbs the refused re-proposal — 046's
            // mid-scene meaning, filtered out of the R8 tax by construction.)
            let row = world
                .refusal_log
                .events()
                .find(|r| r.kitty_id == proposer && r.tick == tick && !r.absorbed)
                .cloned();
            row
        };

        // Kitty 1 sits at (5,5), kitty 2 at (5,6): 1 escapes North, 2 South.
        let realized: Vec<_> = [
            race_row(2, 1, Direction::South),
            race_row(1, 2, Direction::North),
        ]
        .into_iter()
        .flatten()
        .collect();
        assert_eq!(
            realized.len(),
            1,
            "exactly one role assignment realizes the race (interrupter drew the earlier slot)"
        );
        assert!(
            matches!(realized[0].proposed, Action::Play { .. }),
            "the stale continuation is what was refused"
        );
    }

    /// Spec 048 US1 e2e (FR-007/SC-002): a cat mid-play with a critter that
    /// expired last tick — dead in the decision snapshot — takes a REAL
    /// action this tick and stamps no refusal row. Staged so the fresh
    /// decision is unambiguous: ravenous beside a stocked bowl.
    #[tokio::test]
    async fn a_dead_critter_scene_yields_a_real_action_and_no_refusal_row() {
        let (mut world, config) = duet_stage();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Play, 60.0);
        world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
        world.kitties[idx].activity = Activity::Playing {
            target: Some(TargetRef::Element { id: 800 }),
        };
        world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(95));
        // The critter is GONE (expired); only relief remains in reach.
        world.push_element(Element {
            id: 900,
            kind: ElementKind::Chow { servings: 5 },
            pos: Position::new(4, 5),
            ttl: None,
        });
        // Keep the neighbour out of the story.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(15, 15);

        let registry = crate::behavior::BehaviorRegistry::with_builtins();
        let config = std::sync::Arc::new(config);
        let tick = world.tick;
        world.tick(&registry, &config).await;

        assert!(
            !world
                .refusal_log
                .events()
                .any(|r| r.kitty_id == 1 && r.tick == tick),
            "no proposal was refused: the dead scene was never re-proposed"
        );
        assert_eq!(
            world.kitty(1).unwrap().last_action,
            Some(Action::Eat),
            "the freed tick buys a real action, not an idle"
        );
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

        // Kitty 1 starts eating; kitty 2 settles beside it mid-meal.
        // Repointed at spec 041: rest binds nobody now, so a busy cat is
        // lawfully restable-beside -- the eater's meal is untouched.
        run_slot(&mut world, &config, 1, Action::Eat);
        let enforced = run_slot(&mut world, &config, 2, Action::Rest { with: Some(1) });
        assert_eq!(
            enforced,
            Action::Rest { with: Some(1) },
            "a cat mid-meal is restable-beside (nobody is drafted)"
        );
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Eating,
            "and its meal goes on"
        );
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
                80.0,
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
            assert_eq!(world.kitty(id).unwrap().needs.get(NeedKind::Play), 60.0);
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
            "relief already granted is kept (one bug-priced tick, spec 025); none is invented"
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

    /// Spec 044, owner-ruled 2026-08-31: the contagion charge requires the
    /// named partner to be CURRENTLY adjacent — a trailing tick is not a
    /// price. The stale state is real mid-tick (a free rest companion or
    /// groomee moves onto water after the namer's slot, before the namer's
    /// next prune), so the pin lives at the needs phase itself, the layer
    /// the charge reads from.
    #[tokio::test]
    async fn contagion_charges_only_a_currently_adjacent_wet_partner() {
        use crate::kitty::ActivityClock;

        let mut config = test_config();
        config.water.contagion_factor = 1.0;
        config.validate().expect("test config must be legal");
        let config = Arc::new(config);
        let mut world = World::generate(&config);

        // One permanent water tile, nothing else wet on the map.
        world
            .elements
            .retain(|el| el.element_type() != ElementType::Water);
        let wet_tile = Position::new(8, 8);
        world.elements.push(Element {
            id: 9_900,
            kind: ElementKind::Water,
            pos: wet_tile,
            ttl: None,
        });

        // The wandered-partner state as Phase 4 sees it mid-tick: kitty 1
        // still holds the scene naming kitty 2, but 2 has stepped onto
        // water two tiles away (one step past adjacency).
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = wet_tile;
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(8, 10);
        world.kitties[a].activity = Activity::Resting {
            with_friend: Some(2),
        };
        world.kitties[a].activity_clock = Some(ActivityClock::start(world.tick));

        let ambient = config.need_rate_for(1, NeedKind::Bath);
        let charge = config.water.contagion_factor * config.water.bath_gain * config.bath_ratio(1);

        let before = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        world.advance_needs(&config);
        let moved = world.kitty(1).unwrap().needs.get(NeedKind::Bath) - before;
        assert!(
            (moved - ambient).abs() < 1e-4,
            "a partner no longer adjacent must not charge: bath moved {moved}, ambient is {ambient}"
        );

        // Positive control on the same world: step the namer back into
        // adjacency and the identical scene pays the full charge.
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(8, 9);
        let before = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        world.advance_needs(&config);
        let moved = world.kitty(1).unwrap().needs.get(NeedKind::Bath) - before;
        assert!(
            (moved - (ambient + charge)).abs() < 1e-4,
            "the adjacent case must still pay: bath moved {moved}, expected {}",
            ambient + charge
        );
    }

    /// Spec 045: the adjacency ruling holds for the REFERENCED role too.
    /// Under `bidirectional` a wet cat's activity naming a dry cat admits
    /// that cat only while the NAMER is currently adjacent — a groomee
    /// who wandered two tiles from its wet groomer draws no trailing
    /// charge. Same mid-tick layer as the 044 pin above: the stale
    /// reference is real between the namer's slot and its next prune.
    #[tokio::test]
    async fn bidirectional_charges_only_while_the_wet_namer_is_adjacent() {
        use crate::kitty::ActivityClock;

        let mut config = test_config();
        config.water.contagion_factor = 1.0;
        config.water.contagion_membership = crate::config::ContagionMembership::Bidirectional;
        config.validate().expect("test config must be legal");
        let config = Arc::new(config);
        let mut world = World::generate(&config);

        // One permanent water tile, nothing else wet on the map.
        world
            .elements
            .retain(|el| el.element_type() != ElementType::Water);
        let wet_tile = Position::new(8, 8);
        world.elements.push(Element {
            id: 9_900,
            kind: ElementKind::Water,
            pos: wet_tile,
            ttl: None,
        });

        // The wet cat holds the scene naming the dry cat, which has
        // wandered two tiles off (one step past adjacency), idle.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = wet_tile;
        world.kitties[b].activity = Activity::Resting {
            with_friend: Some(1),
        };
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(8, 10);

        let ambient = config.need_rate_for(1, NeedKind::Bath);
        let charge = config.water.contagion_factor * config.water.bath_gain * config.bath_ratio(1);

        let before = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        world.advance_needs(&config);
        let moved = world.kitty(1).unwrap().needs.get(NeedKind::Bath) - before;
        assert!(
            (moved - ambient).abs() < 1e-4,
            "a referenced cat no longer adjacent to its wet namer must not \
             charge: bath moved {moved}, ambient is {ambient}"
        );

        // Positive control on the same world: step the referenced cat
        // back into adjacency and the identical scene pays the charge.
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(8, 9);
        let before = world.kitty(1).unwrap().needs.get(NeedKind::Bath);
        world.advance_needs(&config);
        let moved = world.kitty(1).unwrap().needs.get(NeedKind::Bath) - before;
        assert!(
            (moved - (ambient + charge)).abs() < 1e-4,
            "the adjacent referenced case must pay: bath moved {moved}, expected {}",
            ambient + charge
        );
    }
}
