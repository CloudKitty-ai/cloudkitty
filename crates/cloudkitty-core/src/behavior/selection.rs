//! Shared need selection for the built-in behaviors.
//!
//! One scored pass over all six needs, every tick, replacing the old two-mode
//! rule (a hard lock above the safeguard threshold, a convenience band below
//! it). The lock is what let one unattainable need starve five satisfiable
//! ones -- the 2026-07-18 root-cause analysis found kitties pinned at the
//! happiness floor because play could not land while bath and sleep, free for
//! the taking, were never chosen. Here urgency is a weight, not a veto:
//!
//! ```text
//! score = pressure + urgency_weight * max(0, pressure - safeguard)
//!         - tile_cost * travel_distance
//! ```
//!
//! Urgent needs still dominate anything similarly far away; they just cannot
//! outrank relief that is already underfoot. Ties go to the need that has
//! waited longest for relief, so nothing can be permanently shadowed at the
//! 100-cap by a fixed ordering.
//!
//! Both built-in profiles select through this module (and external behaviors
//! are welcome to copy it) -- one tested rule, no drift between personalities.

use super::relief::ReliefSource;
use super::DecisionContext;
use crate::action::{Action, TargetRef};
use crate::element::ElementType;
use crate::grid::Position;
use crate::kitty::KittyId;
use crate::meow::MessageKind;
use crate::needs::NeedKind;

/// The outcome of one scored pass: the need most worth acting on, plus the
/// playmate scan that pass already paid for, so pursuing play never scans the
/// world a second time in the same decision.
pub struct Choice {
    pub need: NeedKind,
    /// The nearest viable playmate at decision time. Meaningful to pursuit
    /// only when `need` is play; carried whole so the caller need not guess.
    pub playmate: Option<(TargetRef, Position)>,
}

/// Picks the need most worth acting on: highest score, ties to the need
/// longest without relief, then `NeedKind::ALL` order as the final
/// deterministic word. Needs with no relief path at all are skipped outright
/// (see [`travel_distance`]).
pub fn choose(ctx: &DecisionContext) -> Choice {
    let playmate = nearest_viable_playmate(ctx);
    let mut best: Option<(NeedKind, f32)> = None;

    for kind in NeedKind::ALL {
        let Some(s) = scored(ctx, kind, playmate) else {
            continue;
        };
        let wins = match best {
            None => true,
            Some((held, held_score)) => {
                s > held_score
                    || (s == held_score
                        && ctx.me.last_relief_tick(kind) < ctx.me.last_relief_tick(held))
            }
        };
        if wins {
            best = Some((kind, s));
        }
    }

    // Bath and play are relievable wherever the cat stands, so a best always
    // exists; the fallback is belt and braces, not a reachable path.
    let need = best.map(|(kind, _)| kind).unwrap_or(NeedKind::ALL[0]);
    Choice { need, playmate }
}

/// [`choose`], for callers (and tests) that only want the winning need.
pub fn choose_need(ctx: &DecisionContext) -> NeedKind {
    choose(ctx).need
}

/// The selection score for one need, or `None` when the need has no relief
/// path (see [`travel_distance`]). Public so tests (and curious plugin
/// authors) can check the arithmetic directly.
pub fn score(ctx: &DecisionContext, kind: NeedKind) -> Option<f32> {
    scored(ctx, kind, nearest_viable_playmate(ctx))
}

fn scored(
    ctx: &DecisionContext,
    kind: NeedKind,
    playmate: Option<(TargetRef, Position)>,
) -> Option<f32> {
    let behavior = &ctx.config.behavior;
    let distance = distance_given(ctx, kind, playmate)?;
    let pressure = ctx.me.needs.get(kind);
    let urgency = (pressure - ctx.config.thresholds.safeguard).max(0.0);
    Some(
        pressure + behavior.urgency_weight * urgency
            - behavior.tile_cost * distance
            - scene_exposure_for(ctx, kind, playmate),
    )
}

/// Spec 045 seam 1: the expected exposure of the concrete candidate this
/// score already priced — the playmate the shared scan found for play,
/// the `nearest_friend` for cuddle (the same candidate `distance_given`
/// walked to, so score and walk keep the 004 agreement rule). Zero for
/// every non-partnered relief shape, and zero before any arithmetic when
/// the ladder gate is off (the helper's own short-circuit).
fn scene_exposure_for(
    ctx: &DecisionContext,
    kind: NeedKind,
    playmate: Option<(TargetRef, Position)>,
) -> f32 {
    if !ctx.config.behavior.contagion_aware_ladder {
        return 0.0;
    }
    match kind.relief() {
        ReliefSource::Playmate => match playmate {
            Some((TargetRef::Kitty { id }, _)) => expected_scene_exposure(
                ctx,
                crate::kitty::Activity::Playing {
                    target: Some(TargetRef::Kitty { id }),
                },
                id,
            ),
            _ => 0.0,
        },
        ReliefSource::Friend => ctx
            .world
            .nearest_friend(ctx.me.id, ctx.me.pos)
            .map(|k| {
                expected_scene_exposure(
                    ctx,
                    crate::kitty::Activity::Resting {
                        with_friend: Some(k.id),
                    },
                    k.id,
                )
            })
            .unwrap_or(0.0),
        _ => 0.0,
    }
}

/// How far this cat would have to walk to do something about `need` -- in
/// priced tiles, water surcharge included (spec 010) -- or `None` when the
/// world currently offers no way to relieve it at all.
///
/// "No way" is deliberately not encoded as a huge distance: a sentinel is
/// only as strong as the weight multiplying it, so a legal `tile_cost = 0`
/// would cancel it and let an unrelievable need win selection -- the exact
/// shape of the lock-in spec 004 removed. A skipped need is skipped under
/// every configuration.
pub fn travel_distance(ctx: &DecisionContext, need: NeedKind) -> Option<f32> {
    distance_given(ctx, need, nearest_viable_playmate(ctx))
}

fn distance_given(
    ctx: &DecisionContext,
    need: NeedKind,
    playmate: Option<(TargetRef, Position)>,
) -> Option<f32> {
    let me = &ctx.me;

    // The need→relief pairing comes from the one authoritative definition
    // (`relief.rs`, spec 019); this function owns only the pricing of each
    // relief shape.
    match need.relief() {
        // Relieved-in-place needs cost no travel.
        ReliefSource::InPlace { .. } => Some(0.0),
        ReliefSource::Sunbeam => Some(sleep_travel_distance(ctx)),
        ReliefSource::Element { kind, .. } => {
            priced_nearest_element(ctx, kind).map(|(_, cost)| cost)
        }
        // Playmates are deliberately unpriced (spec 010 scope decision): they
        // move every tick, chases re-aim continuously, and pricing a fleeing
        // target's momentary path would add noise, not honesty.
        ReliefSource::Playmate => Some(play_travel_distance(ctx, playmate) as f32),
        ReliefSource::Friend => ctx
            .world
            .nearest_friend(me.id, me.pos)
            .map(|k| priced_travel(ctx, me.pos, k.pos)),
    }
}

/// The walking distance from `from` to `to` plus the `water_step_cost`
/// surcharge for each wet tile on the deterministic dominant-axis staircase
/// between them (the same path [`crate::grid::Direction::toward`] walks),
/// endpoint excluded -- a kitty finishes *beside* its target, never on it
/// (spec 009). This is spec 010's one pricing rule, shared by scores and
/// walks: an approximation of the greedy walk, deterministic and finite --
/// it can reorder choices but never remove one.
pub fn priced_travel(ctx: &DecisionContext, from: Position, to: Position) -> f32 {
    let mut cost = from.manhattan_distance(&to) as f32;
    let surcharge = ctx.config.behavior.water_step_cost * bath_ratio(ctx);
    if surcharge > 0.0 {
        let mut pos = from;
        while let Some(dir) = crate::grid::Direction::toward(pos, to) {
            let Some(next) = pos.step(dir, ctx.world.width, ctx.world.height) else {
                break;
            };
            pos = next;
            if pos == to {
                break;
            }
            if ctx
                .world
                .elements_of(ElementType::Water)
                .any(|e| e.pos == pos)
            {
                cost += surcharge;
            }
        }
    }
    cost
}

/// The deciding cat's water aversion, as a multiple of the shipped
/// surcharge: [`Config::bath_ratio`] for the cat deciding -- the SAME
/// ratio the engine's wet-fur charge uses, so the scripted ladder and
/// the felt need-pressure express one coherent per-cat preference. A
/// low-bath cat is legibly "the swimmer" to both. Shared by both PRICING
/// sites (score and walk must never disagree -- the 004 agreement rule);
/// the blocked-walk sidestep pool is not a pricing site and keeps its
/// flat dry-first preference (spec 010). Note the scale applies whether
/// or not `[water] bath_gain` is on: for the shipped rosters every ratio
/// is 1.0, so `bath_gain = 0` restores pre-024 routing exactly, but a
/// bath-trait override still tilts routes with the charge disabled.
pub fn bath_ratio(ctx: &DecisionContext) -> f32 {
    ctx.config.bath_ratio(ctx.me.id)
}

/// Spec 045: the expected contagion exposure of committing to `scene`
/// with `partner`, in bath need-points — the score's existing currency.
///
/// Scene-total under the ACTIVE membership rule (FR-006, owner-clarified
/// 2026-08-31): every member who would PAY the 044 charge contributes
/// `min(charge(payer) × E_ticks, cap(payer))`, with the per-tick charge
/// read from [`crate::Config::contagion_charge`] — the ONE formula the
/// engine's charge arm shares, so predictor and collector cannot drift.
/// The cap is engine-faithful (Experiments ruling 2026-09-01): the
/// engine's ceiling is an all-or-nothing PRE-charge gate that
/// deliberately overshoots by one scaled charge, so below the ceiling
/// the cap is `headroom + one full charge`, and at or past the ceiling
/// the exposure is 0 — no charge can land there. Payers: under
/// `option_a` the dry NAMER — the decider iff dry beside a wet partner,
/// PLUS the dry partner of a wet decider proposing PLAY (play is
/// reciprocal by construction, so the partner names back and pays under
/// option_a too; Experiments ruling 2026-09-01 — with this, play's
/// payer set is identical under both memberships, a banked smoke
/// prediction). Under `bidirectional` each dry member whose counterpart
/// is wet, either role, any kind. `E_ticks` is the scene's configured
/// MINIMUM duration read from
/// [`crate::kitty::Activity::bounds`], the one activity→duration
/// authority (grooming reads `durations.bath` there — verified at
/// implementation, research D5): the same basis as [`expected_wait`]
/// and needflow's relief horizon, a conservative weight that never
/// manufactures avoidance. `bath_ratio(payer)` is the PAYER's own trait
/// ratio — the exact per-cat scale the engine's charge draws — so the
/// ladder and the felt price stay one coherent preference.
///
/// Prices only partners wet AT DECISION TIME (the wet-now scope,
/// research D4: mid-scene waterline crossings are neither charged nor
/// discounted). Gated: returns 0 BEFORE any arithmetic when
/// `[behavior] contagion_aware_ladder` is off or the charge itself is
/// off (`contagion_factor × bath_gain` = 0), so off is structurally
/// byte-identical. A preference in the behaviors, never a rule in the
/// engine (Article IV): exposure moves what the advisor proposes, never
/// what is legal.
pub fn expected_scene_exposure(
    ctx: &DecisionContext,
    scene: crate::kitty::Activity,
    partner: KittyId,
) -> f32 {
    let b = &ctx.config.behavior;
    let w = &ctx.config.water;
    if !b.contagion_aware_ladder || w.contagion_factor <= 0.0 || w.bath_gain <= 0.0 {
        return 0.0;
    }
    let Some(other) = ctx.world.kitty(partner) else {
        return 0.0;
    };
    let wet = |pos: Position| {
        ctx.world
            .elements_of(ElementType::Water)
            .any(|e| e.pos == pos)
    };
    let me_wet = wet(ctx.me.pos);
    let partner_wet = wet(other.pos);
    let e_ticks = scene
        .bounds(&ctx.config.actions.durations)
        .map(|bounds| bounds.min)
        .unwrap_or(0) as f32;
    let bidirectional = w.contagion_membership == crate::config::ContagionMembership::Bidirectional;
    // Play is reciprocal: the partner names back, so its dry member is a
    // NAMER whatever the membership rule says about referenced cats.
    let reciprocal = matches!(scene, crate::kitty::Activity::Playing { .. });
    let mut exposure = 0.0;
    let mut pay = |id: KittyId, bath_now: f32| {
        if bath_now >= w.bath_gain_ceiling {
            // The engine's pre-charge gate refuses outright — faithful 0.
            return;
        }
        let charge = ctx.config.contagion_charge(id);
        // The gate reads PRE-charge, so the last collectable tick lands a
        // full charge past the headroom — the engine's documented
        // overshoot, bounded by one scaled charge.
        exposure += (charge * e_ticks).min(w.bath_gain_ceiling - bath_now + charge);
    };
    if !me_wet && partner_wet {
        pay(ctx.me.id, ctx.me.needs.get(NeedKind::Bath));
    }
    if (bidirectional || reciprocal) && me_wet && !partner_wet {
        pay(other.id, other.needs.get(NeedKind::Bath));
    }
    exposure
}

/// The element of `kind` cheapest to actually walk to, by
/// `(priced_travel, id)` -- the choice both the score and the pursuit use,
/// so the bowl a kitty picks and the bowl it walks to can never differ
/// (the 004 agreement rule, extended to pricing).
pub fn priced_nearest_element(ctx: &DecisionContext, kind: ElementType) -> Option<(Position, f32)> {
    ctx.world
        .elements_of(kind)
        .map(|e| (e.id, e.pos, priced_travel(ctx, ctx.me.pos, e.pos)))
        .min_by(|a, b| a.2.total_cmp(&b.2).then(a.0.cmp(&b.0)))
        .map(|(_, pos, cost)| (pos, cost))
}

/// The sunbeam worth walking to for a nap, if any: the priced-cheapest one,
/// provided its priced cost fits within `sunbeam_reach`. One helper for both
/// the sleep score and `pursue`'s sleep arm -- the shared carrier of
/// within-shape agreement the `relief` module's invariant names (spec 019;
/// originally the mirror the 004 review demanded, now priced).
pub fn sunbeam_worth_walking(ctx: &DecisionContext) -> Option<(Position, f32)> {
    let (pos, cost) = priced_nearest_element(ctx, ElementType::Sunbeam)?;
    (cost <= ctx.config.behavior.sunbeam_reach as f32).then_some((pos, cost))
}

/// The distance sleep pursuit would actually cover: a sunbeam within
/// `sunbeam_reach` (priced) is worth walking to, anything farther (or no
/// sunbeam at all) means a nap on the spot. Agrees with `pursue`'s sleep
/// arm through [`sunbeam_worth_walking`] (the `relief` module documents
/// this invariant) -- the score must never call sleep free and then commit
/// the cat to a trek.
fn sleep_travel_distance(ctx: &DecisionContext) -> f32 {
    match sunbeam_worth_walking(ctx) {
        Some((_, cost)) => cost,
        None => 0.0,
    }
}

/// The distance the play [`play_action`] would actually cover -- a viable
/// playmate's distance when one is worth walking to, zero when solo play is
/// what would happen.
fn play_travel_distance(ctx: &DecisionContext, playmate: Option<(TargetRef, Position)>) -> u32 {
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = ctx.me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;
    match playmate {
        Some((_, pos)) => {
            let d = ctx.me.pos.manhattan_distance(&pos);
            if d > reach && urgent {
                0 // solo play right here beats the trek
            } else {
                d
            }
        }
        // Nobody viable at all: the kitty entertains itself on the spot.
        None => 0,
    }
}

/// The nearest playmate still worth pursuing -- critter or fellow kitty --
/// ordered by (distance, critters-before-kitties, id) so the choice is
/// stable. THE CLASSIC PICK: this is what NeedsDriven's play scoring, the
/// serious path's `choose`, and `play_travel_distance` consume, and it
/// ignores every spec-042 dial by design (medium review #1: the score is
/// scoped to the playful behavior's own play path -- `scored_playmate` --
/// so the sweep's dials can never move a non-playful cat).
///
/// A candidate stops being viable while it sits in `abandoned_chases`, or
/// while it is the current pursuit target that has gained no ground in
/// `chase_patience_ticks` (a chase that is not working -- as opposed to
/// one that is merely long).
pub fn nearest_viable_playmate(ctx: &DecisionContext) -> Option<(TargetRef, Position)> {
    let me = &ctx.me;

    let critters = ctx.world.critters().map(|e| {
        (
            TargetRef::Element { id: e.id },
            e.pos,
            0u8, // critters win distance ties: bugs are more fun than bothering a friend
            e.id,
        )
    });
    let friends = ctx
        .world
        .others(me.id)
        .map(|k| (TargetRef::Kitty { id: k.id }, k.pos, 1u8, k.id));

    critters
        .chain(friends)
        .filter(|(target, _, _, _)| is_viable(ctx, *target))
        .min_by_key(|(_, pos, tag, id)| (me.pos.manhattan_distance(pos), *tag, *id))
        .map(|(target, pos, _, _)| (target, pos))
}

/// The playful behavior's playmate, by the spec-042 partner-value ranking.
/// At the all-identity dial defaults this is bit-for-bit the classic pick:
/// everyone scores `-distance`, and the tie order (distance,
/// critters-before-kitties, id) decides, so critters still win distance
/// ties.
///
/// The pipeline (data-model.md §2): admission -> eligibility -> ranking.
/// Chase bookkeeping applies unchanged -- the score never resurrects a
/// written-off target (FR-008). Selection is a stateless re-scan every
/// decision tick (FR-010): a candidate whose value collapsed mid-journey
/// is simply re-ranked next tick.
pub fn scored_playmate(ctx: &DecisionContext) -> Option<(TargetRef, Position)> {
    let me = &ctx.me;
    let b = &ctx.config.behavior;
    let my_play = me.needs.get(NeedKind::Play);

    // Each candidate carries its score's value term, computed ONCE from
    // the &Kitty it already is (review 2026-08-29: no by-id re-lookup, no
    // sentinel float -- a kitty absent from the snapshot simply never
    // becomes a candidate). Critters carry no value; their score is the
    // standalone appeal.
    let critters = ctx.world.critters().map(|e| {
        (
            TargetRef::Element { id: e.id },
            e.pos,
            0u8, // critters win distance ties: bugs are more fun than bothering a friend
            e.id,
            None,
        )
    });
    let friends = ctx.world.others(me.id).map(|k| {
        (
            TargetRef::Kitty { id: k.id },
            k.pos,
            1u8,
            k.id,
            // Value AND exposure computed ONCE per candidate, here at
            // construction (the module's recorded 2026-08-29 rule: no
            // re-derivation inside the comparator). Exposure is 0.0 the
            // moment the ladder gate is off — the helper's short-circuit.
            Some((
                partner_value(ctx, k),
                expected_scene_exposure(
                    ctx,
                    crate::kitty::Activity::Playing {
                        target: Some(TargetRef::Kitty { id: k.id }),
                    },
                    k.id,
                ),
            )),
        )
    });

    critters
        .chain(friends)
        // Admission: chase bookkeeping always applies; a mid-scene friend
        // is admitted for anticipatory approach only while the value dial
        // is live (research D2 -- at identity defaults the value term is
        // dead, there is no anticipatory signal to act on, and the classic
        // hard busy-filter stands: the byte-identity witness).
        .filter(|(target, _, _, _, _)| {
            chase_bookkeeping_allows(ctx, *target)
                && match target {
                    TargetRef::Kitty { id } => !kitty_is_mid_scene(ctx, *id) || b.w_value > 0.0,
                    TargetRef::Element { .. } => true,
                }
        })
        // The eligibility filter (spec 042, owner-clarified): the
        // thresholds decide who is worth bothering, so a failing friend
        // drops out of the ranking entirely -- a nearby indifferent
        // friend can never veto partner play by out-scoring on distance.
        // Critters are never filtered: critter and solo play stay
        // unconditional (the character). t_partner at its identity 0.0 is
        // NO BAR at all (medium review #2): value can go negative once
        // w_busy/w_serious are live, and an un-raised threshold must not
        // convert those ranking costs into a hard veto.
        .filter(|(_, _, _, _, value)| match value {
            Some((v, _)) => my_play >= b.t_self && (b.t_partner <= 0.0 || *v >= b.t_partner),
            None => true,
        })
        .max_by(|(_, p1, tag1, id1, v1), (_, p2, tag2, id2, v2)| {
            let s1 = play_score(ctx, *v1, *p1);
            let s2 = play_score(ctx, *v2, *p2);
            // Higher score wins; equal scores fall back to today's exact
            // ascending (distance, tag, id) order -- reversed here because
            // max_by keeps the Greater side. No NaN can reach total_cmp:
            // every dial is validated finite (FR-007) and the value term
            // is bounded need arithmetic.
            s1.total_cmp(&s2).then_with(|| {
                (me.pos.manhattan_distance(p2), *tag2, *id2).cmp(&(
                    me.pos.manhattan_distance(p1),
                    *tag1,
                    *id1,
                ))
            })
        })
        .map(|(target, pos, _, _, _)| (target, pos))
}

/// A friend's value as a playmate (spec 042 FR-001): its own play need,
/// less what waiting for it would cost, less how close it is to getting
/// serious about something that is not play (owner-clarified: wanting to
/// play is the opposite of seriousness and never counts against a
/// candidate).
fn partner_value(ctx: &DecisionContext, k: &crate::kitty::Kitty) -> f32 {
    let b = &ctx.config.behavior;
    let play_need = k.needs.get(NeedKind::Play);
    play_need - b.w_busy * expected_wait(ctx, k) - b.w_serious * top_non_play(k)
}

/// The highest of a kitty's NON-play needs at decision time. One home for
/// the fold on purpose (spec 047 FR-009): the 042 score's seriousness term
/// and the consent gate must read the same number, from the same snapshot.
fn top_non_play(k: &crate::kitty::Kitty) -> f32 {
    NeedKind::ALL
        .iter()
        .filter(|kind| **kind != NeedKind::Play)
        .map(|kind| k.needs.get(*kind))
        .fold(0.0f32, f32::max)
}

/// The spec-047 consent gate: proposing play to the friend `k` is off the
/// table when its top non-play need is strictly over `consent_line` AND
/// strictly over its own play need (the owner's rule — "over", so any tie
/// keeps the friend eligible; play on top is always proposable). At the
/// default `consent_line` 0.0 the gate short-circuits false before reading
/// a single need: identity is structural, not numerical. Consulted only by
/// the playful behavior's friend-play paths — never by needs_driven, never
/// for critters, elements or solo play.
pub(crate) fn consent_blocks(ctx: &DecisionContext, k: &crate::kitty::Kitty) -> bool {
    let line = ctx.config.behavior.consent_line;
    if line <= 0.0 {
        return false;
    }
    let top = top_non_play(k);
    top > line && top > k.needs.get(NeedKind::Play)
}

/// Ticks until a mid-scene kitty could be free -- a HEURISTIC, exact only
/// for scenes that actually hold their minimum: the configured minimum
/// less the ticks already served (inclusive, F-031's +1 convention),
/// never negative -- a scene past its minimum could end any tick, a
/// prunable scene may end sooner, and a boundless activity (or a free
/// kitty) waits zero. w_busy prices this estimate; the sweep prices
/// w_busy.
fn expected_wait(ctx: &DecisionContext, k: &crate::kitty::Kitty) -> f32 {
    let Some(clock) = k.activity_clock else {
        return 0.0;
    };
    let Some(bounds) = k.activity.bounds(&ctx.config.actions.durations) else {
        return 0.0;
    };
    bounds.min.saturating_sub(clock.elapsed(ctx.world.tick)) as f32
}

/// The ranking score (spec 042 FR-001/FR-002): a friend's weighted value
/// against distance; a critter (no value) at the standalone appeal
/// constant (owner-clarified: NOT scaled by w_value -- each dial moves
/// one thing).
/// A friend candidate carries `(value, exposure)` (spec 045): the play
/// scene's expected exposure — precomputed once at candidate
/// construction — is subtracted, so a dry playmate outranks an
/// otherwise-equal wet one: the seam where positional avoidance becomes
/// learnable. Critters carry neither and price no exposure. Currency
/// note (Experiments ruling 2026-09-01, deliberate): exposure is bath
/// need-points subtracted from a base that at identity dials is
/// −distance in TILES — 1:1, no conversion dial. Strong (one Gen 1
/// charge ≡ 3.5–10.5 tiles of walking), disclosed rather than tuned:
/// this ranking is unreachable in the smoke's needs-driven arms and the
/// gate never serves; any future arm that runs the scored ranking must
/// revisit before trusting play-channel readouts.
fn play_score(ctx: &DecisionContext, value: Option<(f32, f32)>, pos: Position) -> f32 {
    let b = &ctx.config.behavior;
    let distance = ctx.me.pos.manhattan_distance(&pos) as f32;
    match value {
        Some((v, exposure)) => b.w_value * v - distance - exposure,
        None => b.critter_appeal - distance,
    }
}

fn is_viable(ctx: &DecisionContext, target: TargetRef) -> bool {
    if !chase_bookkeeping_allows(ctx, target) {
        return false;
    }
    // A kitty mid-activity cannot be conscripted into play (spec 006):
    // proposing it would only validate to Idle, and counting it viable at
    // distance 0 would suppress the solo-play backstop for as long as its
    // scene runs. Busy friends become playmates again when their scene
    // ends. (The playful behavior's scored pick has its own, dial-gated
    // admission rule -- see `scored_playmate`.)
    if let TargetRef::Kitty { id } = target {
        if kitty_is_mid_scene(ctx, id) {
            return false;
        }
    }
    true
}

/// The chase bookkeeping every candidate set honors (FR-008): exclusion
/// after a give-up, and a stalled current pursuit. Shared by the classic
/// and scored picks so neither can resurrect a written-off target.
fn chase_bookkeeping_allows(ctx: &DecisionContext, target: TargetRef) -> bool {
    let tick = ctx.world.tick;
    if ctx.me.is_chase_excluded(target, tick) {
        return false;
    }
    if let Some(pursuit) = &ctx.me.pursuit {
        let patience = ctx.config.behavior.chase_patience_ticks;
        let stalled = tick.saturating_sub(pursuit.last_progress()) >= patience;
        if pursuit.target == target && stalled {
            return false;
        }
    }
    true
}

/// The one mid-scene gate (spec 042 review): both the admission rule in
/// `is_viable` and the never-propose-while-busy rule in
/// `play_action_with` read this, so the two can't drift apart. A kitty
/// missing from the snapshot counts as busy -- the safe reading either
/// way (not admitted at defaults; never proposed to).
fn kitty_is_mid_scene(ctx: &DecisionContext, id: KittyId) -> bool {
    ctx.world
        .kitty(id)
        .map(|k| k.activity.is_in_progress())
        .unwrap_or(true)
}

/// Approach etiquette (spec 012): when two kitties walk at each other, each
/// steps toward where the other just was, and under 009's orthogonal range a
/// pair can orbit a corner forever (verified 2026-07-20: 145 ticks with the
/// urgent-meow lottery silenced). At exactly two walking steps, the
/// higher-id kitty of the pair yields on even world ticks -- holding its
/// corner behind a "Wait for me!" -- and the lower id closes. Tick parity is
/// the progress guarantee: a yield never repeats two ticks running, so a
/// partner who is *not* approaching costs the walker at most one tick.
/// Consulted by both kitty-approach paths (the cuddle walk and kitty-target
/// chases); nothing else may emit the word.
pub fn should_wait_for(ctx: &DecisionContext, friend: KittyId, friend_pos: Position) -> bool {
    ctx.me.pos.manhattan_distance(&friend_pos) == 2
        && ctx.me.id > friend
        && ctx.world.tick.is_multiple_of(2)
}

/// The yield itself: the held turn is spent asking -- or, when the word was
/// said recently, just standing. Either way the turn is spent not pacing,
/// and the stand is what breaks the dance (spec 012 FR-003, amended by spec
/// 023): with the engine's swallow retired, the yield consults courtesy
/// like every scripted emitter, so a long dance asks at most once per
/// courtesy interval instead of every yielding turn.
pub fn wait_for_them(ctx: &DecisionContext) -> Action {
    if ctx.me.can_meow(MessageKind::WaitForMe, ctx.world.tick) {
        Action::Meow {
            message: MessageKind::WaitForMe,
        }
    } else {
        Action::Idle
    }
}

/// One step toward relieving play: pounce on an adjacent playmate, walk after a
/// viable one worth reaching, and otherwise pounce at nothing -- solo play, the
/// backstop that makes play (like bath and sleep) satisfiable anywhere.
pub fn play_action(ctx: &DecisionContext) -> Action {
    play_action_with(ctx, nearest_viable_playmate(ctx))
}

/// The playful behavior's play step (spec 042): [`play_action`] over the
/// partner-value ranking instead of the classic nearest pick. Only the
/// playful behavior calls this -- the dials never move anyone else.
pub fn scored_play_action(ctx: &DecisionContext) -> Action {
    play_action_with(ctx, scored_playmate(ctx))
}

/// [`play_action`] against a playmate scan the caller already ran -- how
/// [`choose`]'s result is pursued without scanning the world twice.
pub fn play_action_with(ctx: &DecisionContext, playmate: Option<(TargetRef, Position)>) -> Action {
    let me = &ctx.me;
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;

    match playmate {
        Some((target, pos)) => {
            if me.pos.is_adjacent(&pos) {
                // Spec 042: an adjacent pick that is mid-scene cannot be
                // proposed to (the engine would downgrade it to Idle -- a
                // wasted turn). Waiting is spent playing: solo for the
                // tick, and the per-tick re-scan proposes the moment the
                // friend is free. Never a proposal until free, never an
                // idle stall.
                if let TargetRef::Kitty { id } = target {
                    if kitty_is_mid_scene(ctx, id) {
                        return Action::play_solo();
                    }
                }
                Action::play_with(target)
            } else if me.pos.manhattan_distance(&pos) > reach && urgent {
                // Everyone worth playing with is far away and the need is real:
                // a kitty does not sulk, it pounces at nothing.
                Action::play_solo()
            } else {
                // Approach etiquette applies only to fellow kitties -- a bug
                // does not take turns.
                if let TargetRef::Kitty { id } = target {
                    if should_wait_for(ctx, id, pos) {
                        return wait_for_them(ctx);
                    }
                }
                Action::Chase(target)
            }
        }
        None => Action::play_solo(),
    }
}

/// An adjacent playmate for the opportunism pass: any critter or fellow kitty
/// within paw's reach. Exclusion does not apply here -- a target that wandered
/// into range costs nothing to bat at, however hopeless it was to chase.
pub fn adjacent_playmate(ctx: &DecisionContext) -> Option<TargetRef> {
    let me = &ctx.me;
    let critter = ctx
        .world
        .critters()
        .filter(|e| me.pos.is_adjacent(&e.pos))
        .min_by_key(|e| (me.pos.manhattan_distance(&e.pos), e.id))
        .map(|e| TargetRef::Element { id: e.id });
    critter.or_else(|| {
        ctx.world
            .others(me.id)
            // A friend mid-meal or asleep cannot be batted into a game
            // (spec 006 conscription); only an idle neighbour counts.
            .filter(|k| me.pos.is_adjacent(&k.pos) && !k.activity.is_in_progress())
            .min_by_key(|k| (me.pos.manhattan_distance(&k.pos), k.id))
            .map(|k| TargetRef::Kitty { id: k.id })
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::element::{Element, ElementKind};
    use crate::kitty::{AbandonedChase, Pursuit};
    use crate::test_support::decision_context;

    // ---- Spec 045: the exposure helper (T018) -------------------------

    use crate::config::ContagionMembership;
    use crate::kitty::Activity;

    const WET_POS: Position = Position { x: 8, y: 8 };
    const DRY_POS: Position = Position { x: 8, y: 9 };

    /// A staged pair: kitty 1 (the decider) and kitty 2 adjacent, one
    /// water tile at `WET_POS`, ladder armed at factor 1.0 under the
    /// given membership. `me_wet`/`partner_wet` choose who stands in it.
    fn exposure_ctx(
        membership: ContagionMembership,
        me_wet: bool,
        partner_wet: bool,
    ) -> crate::behavior::DecisionContext {
        let mut ctx = decision_context(move |world| {
            world.elements.clear();
            world.push_element(Element {
                id: 900,
                kind: ElementKind::Water,
                pos: WET_POS,
                ttl: None,
            });
            let me = world.kitty_index(1).unwrap();
            world.kitties[me].pos = if me_wet { WET_POS } else { DRY_POS };
            let other = world.kitty_index(2).unwrap();
            // Both-wet shares the single tile's wetness by position only
            // in the me_wet case; give the partner its own wet tile then.
            world.kitties[other].pos = if partner_wet {
                if me_wet {
                    world.push_element(Element {
                        id: 901,
                        kind: ElementKind::Water,
                        pos: DRY_POS,
                        ttl: None,
                    });
                    DRY_POS
                } else {
                    WET_POS
                }
            } else if me_wet {
                DRY_POS
            } else {
                Position { x: 7, y: 9 }
            };
        });
        let cfg = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
        cfg.behavior.contagion_aware_ladder = true;
        cfg.water.contagion_factor = 1.0;
        cfg.water.contagion_membership = membership;
        ctx
    }

    fn rest_scene() -> Activity {
        Activity::Resting {
            with_friend: Some(2),
        }
    }

    #[test]
    fn exposure_payer_sets_follow_the_membership_rule() {
        // option_a: the decider pays iff it is dry beside a wet partner.
        let rate = |ctx: &crate::behavior::DecisionContext, id| {
            ctx.config.water.contagion_factor
                * ctx.config.water.bath_gain
                * ctx.config.bath_ratio(id)
        };
        let e_cuddle = 3.0; // durations.cuddle.min at the defaults

        let ctx = exposure_ctx(ContagionMembership::OptionA, false, true);
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        assert!(
            (x - rate(&ctx, 1) * e_cuddle).abs() < 1e-4,
            "namer pays: {x}"
        );

        // option_a: a wet decider's dry REST partner is NOT priced (rest
        // references without naming back — the namer is the decider).
        let ctx = exposure_ctx(ContagionMembership::OptionA, true, false);
        assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);

        // But PLAY is reciprocal by construction: the dry partner names
        // the wet decider back, so it is a NAMER and pays under option_a
        // too — the engine's own charge (pinned by the reciprocity
        // integration test) and the needflow model both price it
        // (Experiments ruling 2026-09-01, medium-review finding 1). The
        // ladder must predict that charge from the wet decider's side.
        let play_scene = Activity::Playing {
            target: Some(TargetRef::Kitty { id: 2 }),
        };
        let ctx = exposure_ctx(ContagionMembership::OptionA, true, false);
        let x = expected_scene_exposure(&ctx, play_scene, 2);
        assert!(
            (x - rate(&ctx, 2) * 2.0).abs() < 1e-4,
            "reciprocal play: the dry partner is a namer under option_a \
             and its charge is the scene's cost: {x}"
        );
        // Consequence (banked smoke prediction): play's payer set is
        // IDENTICAL under both membership rules.
        let bidi = exposure_ctx(ContagionMembership::Bidirectional, true, false);
        assert!(
            (expected_scene_exposure(&bidi, play_scene, 2) - x).abs() < 1e-4,
            "play prices identically under both memberships"
        );

        // bidirectional: the dry counterpart pays from either role.
        let ctx = exposure_ctx(ContagionMembership::Bidirectional, true, false);
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        assert!(
            (x - rate(&ctx, 2) * e_cuddle).abs() < 1e-4,
            "the partner's charge is the scene's cost: {x}"
        );
        let ctx = exposure_ctx(ContagionMembership::Bidirectional, false, true);
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        assert!((x - rate(&ctx, 1) * e_cuddle).abs() < 1e-4);

        // Both-dry and both-wet price zero under either rule.
        for membership in [
            ContagionMembership::OptionA,
            ContagionMembership::Bidirectional,
        ] {
            let ctx = exposure_ctx(membership, false, false);
            assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);
            let ctx = exposure_ctx(membership, true, true);
            assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);
        }
    }

    #[test]
    fn exposure_cap_is_engine_faithful_step_with_overshoot() {
        // Experiments ruling 2026-09-01 (medium-review finding 6): the
        // engine's ceiling is an all-or-nothing PRE-charge gate that
        // deliberately overshoots — a cat at bath 59.9 is charged one
        // FULL scaled charge, and only then does the gate close. The
        // ladder's cap must match: below the ceiling, price
        // min(rate × E, headroom + ONE full charge); at or past it,
        // price 0 (faithful — no charge can land there).
        let mut ctx = exposure_ctx(ContagionMembership::OptionA, false, true);
        ctx.me.needs.add(NeedKind::Bath, 58.0); // headroom 2, charge 3.5
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        assert!(
            (x - 5.5).abs() < 1e-4,
            "near the ceiling the engine still collects the overshoot \
             charge: expected headroom 2 + one charge 3.5 = 5.5, got {x}"
        );
        // Mid-range: the horizon term wins, cap inert.
        let mut ctx = exposure_ctx(ContagionMembership::OptionA, false, true);
        ctx.me.needs.add(NeedKind::Bath, 10.0);
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        assert!((x - 10.5).abs() < 1e-4, "mid-range prices rate × E: {x}");
        // At or past the ceiling: the gate refuses everything — 0.
        let mut ctx = exposure_ctx(ContagionMembership::OptionA, false, true);
        ctx.me.needs.add(NeedKind::Bath, 62.0);
        assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);
    }

    #[test]
    fn exposure_horizon_is_the_scenes_minimum_duration() {
        // E_ticks = bounds.min per Activity::bounds (research D5, amended
        // per Experiments review): play 2, cuddle/rest 3, sleep 3, and
        // grooming reads durations.bath (min 2) — the mapping verified
        // against the activity code, recorded in the config doc comment.
        let ctx = exposure_ctx(ContagionMembership::OptionA, false, true);
        let per_tick = ctx.config.water.bath_gain; // factor 1.0, ratio 1.0
        let cases: [(Activity, f32); 4] = [
            (
                Activity::Playing {
                    target: Some(TargetRef::Kitty { id: 2 }),
                },
                2.0,
            ),
            (rest_scene(), 3.0),
            (
                Activity::Sleeping {
                    in_sunbeam: false,
                    with_friend: Some(2),
                },
                3.0,
            ),
            (Activity::Grooming { target: Some(2) }, 2.0),
        ];
        for (scene, e_min) in cases {
            let x = expected_scene_exposure(&ctx, scene, 2);
            assert!(
                (x - per_tick * e_min).abs() < 1e-4,
                "{scene:?}: expected {} got {x}",
                per_tick * e_min
            );
        }
    }

    #[test]
    fn exposure_scales_by_the_payers_own_bath_ratio_not_the_deciders() {
        // bidirectional, wet decider, dry partner with a 2x bath trait:
        // the partner is the payer, so ITS ratio scales the charge.
        let mut ctx = exposure_ctx(ContagionMembership::Bidirectional, true, false);
        let cfg = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
        cfg.kitties[1].needs = Some(crate::config::NeedRateOverrides {
            bath: Some(0.4), // ratio 2.0 against the 0.2 baseline
            ..Default::default()
        });
        let x = expected_scene_exposure(&ctx, rest_scene(), 2);
        let expected = 1.0 * ctx.config.water.bath_gain * 2.0 * 3.0;
        assert!(
            (x - expected).abs() < 1e-4,
            "the payer's ratio scales: expected {expected}, got {x}"
        );
    }

    #[test]
    fn an_exposed_partnered_need_scores_below_its_unexposed_twin() {
        // T020 (SC-004, seam 1): the same cuddle errand, the same
        // adjacent friend — the only difference is the friend standing in
        // water. With the ladder armed at the Gen 1 factor the exposed
        // score drops by exactly the scene's expected exposure; with the
        // gate off the two worlds score identically (pre-045 arithmetic,
        // computed by hand here so the gate-off arm is pinned to the
        // formula, not to itself).
        fn cuddle_ctx(friend_wet: bool, ladder: bool) -> crate::behavior::DecisionContext {
            let mut ctx = decision_context(move |world| {
                world.elements.clear();
                if friend_wet {
                    world.push_element(Element {
                        id: 900,
                        kind: ElementKind::Water,
                        pos: WET_POS,
                        ttl: None,
                    });
                }
                let me = world.kitty_index(1).unwrap();
                world.kitties[me].pos = DRY_POS;
                world.kitties[me].needs.add(NeedKind::Cuddle, 40.0);
                let other = world.kitty_index(2).unwrap();
                world.kitties[other].pos = WET_POS;
            });
            let cfg = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
            cfg.behavior.contagion_aware_ladder = ladder;
            cfg.water.contagion_factor = 1.0;
            ctx
        }
        // Gate ON: the wet-friend world scores strictly below the dry.
        let wet = score(&cuddle_ctx(true, true), NeedKind::Cuddle).unwrap();
        let dry = score(&cuddle_ctx(false, true), NeedKind::Cuddle).unwrap();
        let expected_exposure = 1.0 * 3.5 * 1.0 * 3.0; // factor×gain×ratio×E_cuddle
        assert!(
            (dry - wet - expected_exposure).abs() < 1e-3,
            "exposed cuddle must score exactly one scene-exposure below \
             its twin: dry {dry}, wet {wet}"
        );
        // Gate OFF: identical scores, equal to the pre-045 arithmetic.
        let wet_off = score(&cuddle_ctx(true, false), NeedKind::Cuddle).unwrap();
        let dry_off = score(&cuddle_ctx(false, false), NeedKind::Cuddle).unwrap();
        assert_eq!(wet_off, dry_off, "gate off: exposure must not price");
        let pre045 = 40.0 - 1.0; // pressure − tile_cost × distance(1), no urgency
        assert!(
            (wet_off - pre045).abs() < 1e-3,
            "gate off must be the pre-045 formula: {wet_off} vs {pre045}"
        );
    }

    #[test]
    fn a_dry_playmate_outranks_an_otherwise_equal_wet_one() {
        // T021 (SC-004, seam 2): two idle friends, equal distance, equal
        // value (identity dials), one standing in water. At the Gen 1
        // factor with the ladder armed the dry one wins the ranking; at
        // factor 0.0 with the gate still on, nothing is priced and the
        // classic (distance, tag, id) tie-break stands — the wet, lower
        // id wins. The contrast pins the seam to the CHARGE, not the gate.
        fn pick(factor: f32) -> Option<(TargetRef, Position)> {
            let mut ctx = decision_context(move |world| {
                world.elements.clear();
                world.push_element(Element {
                    id: 900,
                    kind: ElementKind::Water,
                    pos: Position::new(8, 8),
                    ttl: None,
                });
                let me = world.kitty_index(1).unwrap();
                world.kitties[me].pos = Position::new(8, 10);
                let wet = world.kitty_index(2).unwrap();
                world.kitties[wet].pos = Position::new(8, 8);
                let dry =
                    crate::kitty::Kitty::new(3, "Pumpkin", Position::new(8, 12), "needs_driven");
                world.kitties.push(dry);
            });
            let cfg = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
            cfg.behavior.contagion_aware_ladder = true;
            cfg.water.contagion_factor = factor;
            scored_playmate(&ctx)
        }
        assert_eq!(
            pick(1.0),
            Some((TargetRef::Kitty { id: 3 }, Position::new(8, 12))),
            "armed: the dry twin must outrank the wet one"
        );
        assert_eq!(
            pick(0.0),
            Some((TargetRef::Kitty { id: 2 }, Position::new(8, 8))),
            "factor 0.0 with the gate on: the classic tie-break must stand"
        );
    }

    #[test]
    fn exposure_is_zero_before_any_arithmetic_when_gated_off() {
        // Gate off: zero, whatever the factor.
        let mut ctx = exposure_ctx(ContagionMembership::Bidirectional, false, true);
        std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .behavior
            .contagion_aware_ladder = false;
        assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);
        // Gate on, factor 0: the charge does not exist — zero.
        let mut ctx = exposure_ctx(ContagionMembership::Bidirectional, false, true);
        std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .water
            .contagion_factor = 0.0;
        assert_eq!(expected_scene_exposure(&ctx, rest_scene(), 2), 0.0);
    }

    /// The stuck world of tick 1465, reconstructed: Miso at (21,30), bath and
    /// play both pinned at 100, sleep 98.9, a bug 3 tiles away, water 6 and
    /// chow 8 tiles off, friends ~16 away. The old selection locked onto play
    /// forever; the score must pick bath -- relief on the spot.
    fn miso_ctx() -> crate::behavior::DecisionContext {
        decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(21, 30);
            let needs = &mut world.kitties[idx].needs;
            needs.add(NeedKind::Eat, 34.5);
            needs.add(NeedKind::Drink, 30.5);
            needs.add(NeedKind::Sleep, 98.9);
            needs.add(NeedKind::Play, 100.0);
            needs.add(NeedKind::Cuddle, 45.75);
            needs.add(NeedKind::Bath, 100.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 20);
            world.push_element(Element {
                id: 102,
                kind: ElementKind::Bug,
                pos: Position::new(22, 27),
                ttl: Some(95),
            });
            world.push_element(Element {
                id: 5,
                kind: ElementKind::Water,
                pos: Position::new(27, 29),
                ttl: None,
            });
            world.push_element(Element {
                id: 10,
                kind: ElementKind::Chow { servings: 1 },
                pos: Position::new(29, 31),
                ttl: None,
            });
        })
    }

    #[test]
    fn the_stuck_kitty_grooms_instead_of_fixating_on_play() {
        let ctx = miso_ctx();
        // The 004 R1 worked example, re-derived for spec 009's Manhattan
        // distances: the bug at (22,27) is now honestly 4 walking steps (was
        // Chebyshev 3), so play = 100 + 50 - 4 = 146 and the runner-up order
        // flips (sleep 146.7 above play 146) -- but bath, relief on the spot,
        // still wins at 150, which is the property this test guards.
        assert_eq!(score(&ctx, NeedKind::Bath), Some(150.0));
        assert_eq!(score(&ctx, NeedKind::Play), Some(146.0));
        assert!((score(&ctx, NeedKind::Sleep).unwrap() - 146.7).abs() < 0.1);
        assert_eq!(choose_need(&ctx), NeedKind::Bath);
    }

    #[test]
    fn an_unrelievable_need_is_skipped_not_priced() {
        // The 004-review P1 hole: with a legal `tile_cost = 0`, a sentinel
        // distance is multiplied away and a need with no relief path anywhere
        // wins on pressure alone -- the cat idles at high pressure while bath
        // and sleep sit free. Unreachability must survive every config.
        let mut ctx = decision_context(|world| {
            world.elements.clear(); // no chow anywhere
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Eat, 100.0);
            world.kitties[idx].needs.add(NeedKind::Bath, 50.0);
        });
        std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .behavior
            .tile_cost = 0.0;

        assert_eq!(
            score(&ctx, NeedKind::Eat),
            None,
            "no chow in the world means no eat score at all"
        );
        assert_eq!(
            choose_need(&ctx),
            NeedKind::Bath,
            "a need nothing can relieve must not outrank relief underfoot"
        );
    }

    #[test]
    fn sleep_is_priced_at_the_walk_its_pursuit_would_take() {
        // The 004-review scoring hole: sleep scored as distance 0 while its
        // pursuit walks up to `sunbeam_reach` tiles to a sunbeam, letting
        // "free" sleep beat food one step away and then trek right past it.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Sleep, 60.0);
            world.kitties[idx].needs.add(NeedKind::Eat, 58.0);
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 6), // one step away
                ttl: None,
            });
            world.push_element(Element {
                id: 701,
                kind: ElementKind::Sunbeam,
                pos: Position::new(13, 5), // 8 tiles: within reach, and priced
                ttl: Some(100),
            });
        });

        assert_eq!(
            travel_distance(&ctx, NeedKind::Sleep),
            Some(8.0),
            "the sunbeam walk is a real cost"
        );
        assert_eq!(
            choose_need(&ctx),
            NeedKind::Eat,
            "eat 58 - 1 beats sleep 60 - 8; the score and the walk agree"
        );
    }

    #[test]
    fn a_sunbeam_past_reach_means_a_nap_on_the_spot_priced_at_zero() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.push_element(Element {
                id: 702,
                kind: ElementKind::Sunbeam,
                pos: Position::new(13, 13), // 11 tiles, past reach 8
                ttl: Some(100),
            });
        });
        assert_eq!(
            travel_distance(&ctx, NeedKind::Sleep),
            Some(0.0),
            "pursuit would nap right here, so the score says so too"
        );
    }

    #[test]
    fn a_busy_friend_is_not_a_viable_playmate_and_solo_play_steps_in() {
        use crate::kitty::{Activity, ActivityClock};

        // An urgent player beside a friend who is mid-meal: proposing at the
        // friend would only bounce off validation (spec 006 conscription), so
        // the friend must not count as viable -- the solo backstop fires.
        let ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 10;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 6);
            world.kitties[friend].activity = Activity::Eating;
            world.kitties[friend].activity_clock = Some(ActivityClock::start(9));
        });

        assert_eq!(
            nearest_viable_playmate(&ctx),
            None,
            "a cat mid-meal is not on the menu"
        );
        assert_eq!(adjacent_playmate(&ctx), None);
        assert_eq!(
            play_action(&ctx),
            Action::play_solo(),
            "the solo backstop fires instead of a doomed proposal"
        );
    }

    #[test]
    fn urgent_play_with_no_playmate_near_resolves_on_the_spot_not_by_trekking() {
        let mut ctx = miso_ctx();
        // Bath freshly relieved, the bug gone: the nearest playmate is a friend
        // 16 tiles off. Urgent play is still satisfiable right here (solo), so
        // play may win selection -- but it must resolve as a pounce at nothing,
        // never a cross-map trek. One solo helping later, sleep takes over.
        let world = std::sync::Arc::get_mut(&mut ctx.world).unwrap();
        world.elements.retain(|e| e.id != 102);
        ctx.me.needs.add(NeedKind::Bath, -80.0);

        assert_eq!(choose_need(&ctx), NeedKind::Play);
        assert_eq!(play_action(&ctx), Action::play_solo());

        // After the solo relief lands, the scored pass moves on to sleep.
        ctx.me
            .needs
            .add(NeedKind::Play, -ctx.config.actions.solo_play_relief);
        assert_eq!(choose_need(&ctx), NeedKind::Sleep);
    }

    #[test]
    fn genuine_urgency_still_beats_a_mild_zero_distance_need() {
        // Eat at 80 with chow five tiles away must outrank bath at 50 underfoot:
        // eat = 80 + 2*5 - 5 = 85 vs bath = 50.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
            world.kitties[idx].needs.add(NeedKind::Bath, 50.0);
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(10, 5),
                ttl: None,
            });
        });
        assert_eq!(choose_need(&ctx), NeedKind::Eat);
    }

    #[test]
    fn ties_go_to_the_need_longest_without_relief() {
        // Bath and sleep both pinned at 100, both zero distance, identical
        // scores -- the old enum order would say sleep, forever. Relief
        // recency must decide instead.
        let make = |bath_relieved: u64, sleep_relieved: u64| {
            decision_context(move |world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].needs.add(NeedKind::Bath, 100.0);
                world.kitties[idx].needs.add(NeedKind::Sleep, 100.0);
                world.kitties[idx]
                    .last_relief
                    .insert(NeedKind::Bath, bath_relieved);
                world.kitties[idx]
                    .last_relief
                    .insert(NeedKind::Sleep, sleep_relieved);
            })
        };

        let ctx = make(10, 500);
        assert_eq!(choose_need(&ctx), NeedKind::Bath, "bath waited longer");
        let ctx = make(500, 10);
        assert_eq!(choose_need(&ctx), NeedKind::Sleep, "now sleep has");
        // Never-relieved beats any stamp at all.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Bath, 100.0);
            world.kitties[idx].needs.add(NeedKind::Sleep, 100.0);
            world.kitties[idx].last_relief.insert(NeedKind::Sleep, 1);
        });
        assert_eq!(choose_need(&ctx), NeedKind::Bath);
    }

    #[test]
    fn identical_contexts_choose_identically() {
        let a = choose_need(&miso_ctx());
        let b = choose_need(&miso_ctx());
        assert_eq!(a, b);
    }

    #[test]
    fn priced_travel_charges_wet_tiles_on_the_staircase_and_never_the_endpoint() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.push_element(Element {
                id: 850,
                kind: ElementKind::Water,
                pos: Position::new(5, 2), // squarely on the straight east path
                ttl: None,
            });
        });
        // Straight line east through the puddle: 6 steps + one surcharge.
        assert_eq!(
            priced_travel(&ctx, Position::new(2, 2), Position::new(8, 2)),
            10.0
        );
        // The puddle as *destination* costs nothing extra: a kitty drinks
        // from beside its water, never from on top of it (endpoint excluded).
        assert_eq!(
            priced_travel(&ctx, Position::new(2, 2), Position::new(5, 2)),
            3.0
        );
        // No water in play: pricing is plain Manhattan.
        assert_eq!(
            priced_travel(&ctx, Position::new(2, 2), Position::new(2, 8)),
            6.0
        );
    }

    #[test]
    fn priced_travel_follows_the_dominant_axis_staircase_through_a_dogleg() {
        // From (2,2) to (6,5) the staircase runs E,E,S,E,S,E,S -- water at
        // (4,3), its third tile, is crossed; water off the staircase is not.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.push_element(Element {
                id: 851,
                kind: ElementKind::Water,
                pos: Position::new(4, 3), // on the staircase
                ttl: None,
            });
            world.push_element(Element {
                id: 852,
                kind: ElementKind::Water,
                pos: Position::new(2, 5), // well off it
                ttl: None,
            });
        });
        assert_eq!(
            priced_travel(&ctx, Position::new(2, 2), Position::new(6, 5)),
            11.0,
            "7 steps + one wet tile at the default 4.0"
        );
    }

    #[test]
    fn a_bowl_across_a_pond_loses_to_a_farther_dry_bowl_but_wins_alone() {
        // Spec 010 US2 acceptance: 4 raw steps across two water tiles prices
        // at 12; 6 dry steps price at 6. The dry bowl is chosen -- and when it
        // is gone, the wet bowl is still selected and still pursued (pricing
        // reorders, never removes).
        let with_both = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            for (id, pos, kind) in [
                (
                    860u32,
                    Position::new(5, 9),
                    ElementKind::Chow { servings: 3 },
                ),
                (861, Position::new(11, 5), ElementKind::Chow { servings: 3 }),
                (862, Position::new(5, 7), ElementKind::Water),
                (863, Position::new(5, 8), ElementKind::Water),
            ] {
                world.push_element(Element {
                    id,
                    kind,
                    pos,
                    ttl: None,
                });
            }
        });
        assert_eq!(
            priced_nearest_element(&with_both, ElementType::Chow),
            Some((Position::new(11, 5), 6.0)),
            "the dry bowl is the cheaper walk"
        );
        assert_eq!(travel_distance(&with_both, NeedKind::Eat), Some(6.0));

        let only_wet = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            for (id, pos, kind) in [
                (
                    864u32,
                    Position::new(5, 9),
                    ElementKind::Chow { servings: 3 },
                ),
                (865, Position::new(5, 7), ElementKind::Water),
                (866, Position::new(5, 8), ElementKind::Water),
            ] {
                world.push_element(Element {
                    id,
                    kind,
                    pos,
                    ttl: None,
                });
            }
        });
        assert_eq!(
            priced_nearest_element(&only_wet, ElementType::Chow),
            Some((Position::new(5, 9), 12.0)),
            "an only option is priced, never removed"
        );
        assert_eq!(
            choose_need(&only_wet),
            NeedKind::Eat,
            "a hungry cat still goes to dinner across the pond"
        );
    }

    #[test]
    fn the_higher_id_kitty_waits_at_the_corner_on_even_ticks_only() {
        // Spec 012: kitty 2 pursuing kitty 1, one corner apart. Even tick:
        // yield ("Wait for me!"); odd tick: walk. The lower id never yields.
        use crate::test_support::decision_context_for;
        let make = |me: crate::kitty::KittyId, tick: u64| {
            decision_context_for(me, move |world| {
                world.elements.clear();
                world.tick = tick;
                let a = world.kitty_index(1).unwrap();
                world.kitties[a].pos = Position::new(5, 5);
                world.kitties[a].needs.add(NeedKind::Play, 50.0);
                let b = world.kitty_index(2).unwrap();
                world.kitties[b].pos = Position::new(6, 6); // Manhattan 2
                world.kitties[b].needs.add(NeedKind::Play, 50.0);
            })
        };

        assert_eq!(
            play_action(&make(2, 100)),
            Action::Meow {
                message: MessageKind::WaitForMe,
            },
            "higher id, even tick: hold the corner and ask"
        );
        assert_eq!(
            play_action(&make(2, 101)),
            Action::Chase(TargetRef::Kitty { id: 1 }),
            "higher id, odd tick: walk -- parity guarantees progress"
        );
        assert_eq!(
            play_action(&make(1, 100)),
            Action::Chase(TargetRef::Kitty { id: 2 }),
            "the lower id always closes"
        );

        // Spec 023: with the engine swallow retired, the yield itself keeps
        // the courtesy -- inside the interval it stands silently. The turn
        // is still spent not pacing, so the dance's progress guarantee (the
        // stand, tick parity) is untouched.
        let mut on_courtesy = make(2, 100);
        on_courtesy
            .me
            .set_meow_cooldown(MessageKind::WaitForMe, 100 + 4);
        assert_eq!(
            play_action(&on_courtesy),
            Action::Idle,
            "on courtesy, the yield is a silent stand"
        );
        let mut courtesy_over = make(2, 100);
        courtesy_over
            .me
            .set_meow_cooldown(MessageKind::WaitForMe, 100);
        assert_eq!(
            play_action(&courtesy_over),
            Action::Meow {
                message: MessageKind::WaitForMe,
            },
            "courtesy elapsed: the ask returns"
        );

        // Out of the corner zone, nobody stands on ceremony.
        let far = decision_context_for(2, |world| {
            world.elements.clear();
            world.tick = 100;
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].pos = Position::new(5, 5);
            let b = world.kitty_index(2).unwrap();
            world.kitties[b].pos = Position::new(5, 9); // Manhattan 4
            world.kitties[b].needs.add(NeedKind::Play, 50.0);
        });
        assert_eq!(play_action(&far), Action::Chase(TargetRef::Kitty { id: 1 }));
    }

    #[test]
    fn bugs_do_not_take_turns() {
        // Etiquette is for fellow kitties: a critter at Manhattan 2 is
        // chased regardless of parity or id.
        let ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 100; // even
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 50.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(15, 15);
            world.push_element(Element {
                id: 870,
                kind: ElementKind::Bug,
                pos: Position::new(6, 6),
                ttl: Some(50),
            });
        });
        assert_eq!(
            play_action(&ctx),
            Action::Chase(TargetRef::Element { id: 870 })
        );
    }

    #[test]
    fn a_nearer_friend_beats_a_farther_critter() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 8); // 3 away
            world.push_element(Element {
                id: 800,
                kind: ElementKind::Bug,
                pos: Position::new(12, 5), // 7 away
                ttl: Some(50),
            });
        });
        assert_eq!(
            nearest_viable_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 })
        );
    }

    #[test]
    fn an_excluded_target_is_skipped_for_its_whole_window() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].abandoned_chases.push(AbandonedChase {
                target: TargetRef::Element { id: 801 },
                until: world.tick + 60,
            });
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 15); // 10 away
            world.push_element(Element {
                id: 801,
                kind: ElementKind::Greeble {
                    heading: crate::grid::Direction::North,
                },
                pos: Position::new(5, 7), // 2 away, but written off
                ttl: Some(50),
            });
        });
        assert_eq!(
            nearest_viable_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "the excluded greeble does not count, however close"
        );
    }

    /// A pursuit of bug 802 that began at tick 80 and last gained ground at
    /// `improved_at`, seen at tick 100 with the bug `distance` tiles away.
    fn pursuing_ctx(improved_at: u64, distance: u32) -> crate::behavior::DecisionContext {
        decision_context(move |world| {
            world.elements.clear();
            world.tick = 100;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 80.0);
            world.kitties[idx].pursuit = Some(Pursuit {
                target: TargetRef::Element { id: 802 },
                started: 80,
                closest: distance,
                improved_at,
            });
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(20, 20);
            world.push_element(Element {
                id: 802,
                kind: ElementKind::Bug,
                pos: Position::new(5, 5 + distance),
                ttl: Some(50),
            });
        })
    }

    #[test]
    fn a_pursuit_that_has_gained_no_ground_for_a_whole_patience_window_is_dropped() {
        // Last improvement 20 ticks ago, patience 12: this chase is not working.
        let stalled = pursuing_ctx(80, 4);
        assert_ne!(
            nearest_viable_playmate(&stalled).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
    }

    #[test]
    fn a_chase_that_is_still_closing_survives_however_long_it_has_run() {
        // Started 20 ticks ago but gained ground 2 ticks ago: keep going.
        let improving = pursuing_ctx(98, 4);
        assert_eq!(
            nearest_viable_playmate(&improving).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
    }

    #[test]
    fn a_long_chase_is_not_abandoned_at_the_moment_it_arrives() {
        // Regression: viability used to compare current distance against the
        // best-ever distance, which are equal exactly when the cat is doing as
        // well as it ever has -- so a 20-tick chase was condemned at the very
        // tick it caught up. Arriving adjacent (distance 1, just improved) must
        // leave the target viable and get pounced on.
        let arrived = pursuing_ctx(100, 1);
        assert_eq!(
            nearest_viable_playmate(&arrived).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 }),
            "the bug it just spent 20 ticks reaching is still worth playing with"
        );
        assert_eq!(
            play_action(&arrived),
            Action::play_with(TargetRef::Element { id: 802 }),
            "and the cat pounces rather than wandering off"
        );
    }

    #[test]
    fn urgent_play_with_everyone_out_of_reach_goes_solo() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(31, 31); // far past reach 8
        });
        assert_eq!(play_action(&ctx), Action::play_solo());
        assert_eq!(
            travel_distance(&ctx, NeedKind::Play),
            Some(0.0),
            "the score must agree that relief is on the spot"
        );
    }

    #[test]
    fn an_adjacent_partner_is_preferred_over_solo_play() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(2, 3);
        });
        assert_eq!(
            play_action(&ctx),
            Action::play_with(TargetRef::Kitty { id: 2 })
        );
    }

    #[test]
    fn moderate_play_with_a_reachable_playmate_chases() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 50.0);
            world.push_element(Element {
                id: 803,
                kind: ElementKind::Bug,
                pos: Position::new(6, 2), // 4 away, within reach
                ttl: Some(50),
            });
        });
        assert_eq!(
            play_action(&ctx),
            Action::Chase(TargetRef::Element { id: 803 })
        );
    }
}

/// Spec 042 (Playful 2.0): the partner-value ranking's guard battery.
/// Every dial's effect shown red-first against the distance-only pick;
/// the identity pins are the byte-identity witnesses (SC-001 at unit
/// scale). Staging idiom: `decision_context` + a cloned third kitty
/// where a scenario needs two friends.
#[cfg(test)]
mod playful2_tests {
    use super::*;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::kitty::ActivityClock;
    use crate::needs::NeedKind;
    use crate::test_support::decision_context;

    /// A third cat cloned from the first two -- the test world ships two.
    fn push_friend(world: &mut crate::world::World, id: u32, pos: Position) {
        let mut k = world.kitties[0].clone();
        k.id = id;
        k.name = format!("Extra{id}");
        k.pos = pos;
        k.needs = crate::needs::Needs::default();
        k.activity = crate::kitty::Activity::Idle;
        k.activity_clock = None;
        world.kitties.push(k);
    }

    fn set_dials(
        ctx: &mut crate::behavior::DecisionContext,
        f: impl FnOnce(&mut crate::config::BehaviorConfig),
    ) {
        f(&mut std::sync::Arc::get_mut(&mut ctx.config).unwrap().behavior);
    }

    fn busy(world: &mut crate::world::World, id: u32) {
        let idx = world.kitty_index(id).unwrap();
        world.kitties[idx].activity = crate::kitty::Activity::Eating;
        world.kitties[idx].activity_clock = Some(ActivityClock::start(world.tick));
    }

    // ---- Spec 047: the consent gate (T005 predicate pins) -------------

    /// Pins a kitty's needs exactly: everything zeroed, then only eat and
    /// play set — so `top_non_play` is the eat value by construction.
    fn pin_needs(world: &mut crate::world::World, id: u32, eat: f32, play: f32) {
        let idx = world.kitty_index(id).unwrap();
        world.kitties[idx].needs = crate::needs::Needs::default();
        world.kitties[idx].needs.eat = crate::needs::Need::new(eat);
        world.kitties[idx].needs.play = crate::needs::Need::new(play);
    }

    /// The owner's rule verbatim: over the line AND over play blocks.
    #[test]
    fn the_consent_gate_blocks_a_friend_strictly_over_the_line() {
        let mut ctx = decision_context(|world| pin_needs(world, 2, 40.0, 10.0));
        set_dials(&mut ctx, |b| b.consent_line = 30.0);
        let k = ctx.world.kitties.iter().find(|k| k.id == 2).unwrap();
        assert!(consent_blocks(&ctx, k), "eat 40 > line 30 and > play 10");
    }

    /// "Over" is strict: a top non-play need exactly AT the line spares.
    #[test]
    fn the_consent_gate_spares_a_friend_exactly_at_the_line() {
        let mut ctx = decision_context(|world| pin_needs(world, 2, 30.0, 10.0));
        set_dials(&mut ctx, |b| b.consent_line = 30.0);
        let k = ctx.world.kitties.iter().find(|k| k.id == 2).unwrap();
        assert!(!consent_blocks(&ctx, k), "eat 30 is AT the line, not over it");
    }

    /// Play tying the top non-play need keeps the friend proposable —
    /// blocking needs the non-play need strictly on top.
    #[test]
    fn the_consent_gate_spares_a_friend_whose_play_ties_its_top_need() {
        let mut ctx = decision_context(|world| pin_needs(world, 2, 40.0, 40.0));
        set_dials(&mut ctx, |b| b.consent_line = 30.0);
        let k = ctx.world.kitties.iter().find(|k| k.id == 2).unwrap();
        assert!(!consent_blocks(&ctx, k), "play 40 co-tops eat 40: proposable");
    }

    /// The default 0.0 is OFF: no need is even read (the short-circuit).
    #[test]
    fn the_consent_gate_is_off_at_the_default_line() {
        let ctx = decision_context(|world| pin_needs(world, 2, 90.0, 0.0));
        let k = ctx.world.kitties.iter().find(|k| k.id == 2).unwrap();
        assert!(!consent_blocks(&ctx, k), "line 0.0 gates nothing, ever");
    }

    /// (a) The identity pin: at all-default dials the pick is today's --
    /// nearest first, critter beating friend on a distance tie.
    #[test]
    fn at_default_dials_the_pick_is_todays_nearest_with_critter_tie() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 9); // distance 4
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Bug,
                pos: Position::new(9, 5), // distance 4: the tie
                ttl: Some(100),
            });
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 700 }),
            "critters win distance ties, exactly as today"
        );
    }

    /// (b) Value outranks distance once w_value is real.
    #[test]
    fn a_distant_eager_friend_beats_an_adjacent_indifferent_one() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent, no play need
            push_friend(world, 7, Position::new(5, 11)); // distance 6
            let g = world.kitty_index(7).unwrap();
            world.kitties[g].needs.add(NeedKind::Play, 60.0);
        });
        set_dials(&mut ctx, |b| b.w_value = 5.0);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 7 }),
            "worth beats distance"
        );
    }

    /// (c) t_partner leaves an indifferent friend in peace.
    #[test]
    fn a_low_value_friend_below_t_partner_is_left_in_peace() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent, need 0
            world.push_element(Element {
                id: 701,
                kind: ElementKind::Bug,
                pos: Position::new(5, 12), // distance 7
                ttl: Some(100),
            });
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.t_partner = 20.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 701 }),
            "the friend is ineligible; the game goes to the critter"
        );
    }

    /// (d) t_self: a cat with no real play urge bothers nobody.
    #[test]
    fn below_t_self_no_friend_is_bothered() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 80.0);
            world.push_element(Element {
                id: 702,
                kind: ElementKind::Bug,
                pos: Position::new(5, 13),
                ttl: Some(100),
            });
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.t_self = 50.0; // my own play need is far below this
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 702 }),
            "no friend is eligible when my own urge is not real"
        );
    }

    /// (e) Clarify ruling 1: eligibility is a FILTER -- a passing
    /// lower-scoring friend wins when the best-scoring one fails the bar.
    #[test]
    fn a_passing_lower_scoring_friend_beats_a_failing_best_scorer() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 5.0); // value 5: fails bar
            push_friend(world, 7, Position::new(5, 13)); // distance 8
            let g = world.kitty_index(7).unwrap();
            world.kitties[g].needs.add(NeedKind::Play, 60.0); // value 60: passes
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 0.1; // small: adjacency out-SCORES the eager friend
            b.t_partner = 20.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 7 }),
            "the bar filters candidates; it is not a veto held by the best scorer"
        );
    }

    /// (f) The wait cost: a mid-scene friend loses to an equal free one.
    #[test]
    fn a_mid_scene_friend_is_outranked_by_an_equal_free_one() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 8); // distance 3
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 50.0);
            busy(world, 2);
            push_friend(world, 7, Position::new(8, 5)); // distance 3 too
            let g = world.kitty_index(7).unwrap();
            world.kitties[g].needs.add(NeedKind::Play, 50.0);
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.w_busy = 30.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 7 }),
            "waiting costs; the free friend wins"
        );
    }

    /// (g) The admission pin (research D2): at ALL-default dials a busy
    /// adjacent friend is invisible -- today's pick stands. At w_value > 0
    /// a busy friend becomes rankable.
    #[test]
    fn busy_friends_are_admitted_only_when_the_value_dial_is_live() {
        let stage = |world: &mut crate::world::World| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent...
            busy(world, 2); // ...but mid-scene
            world.push_element(Element {
                id: 703,
                kind: ElementKind::Bug,
                pos: Position::new(5, 10), // distance 5
                ttl: Some(100),
            });
        };
        let ctx = decision_context(stage);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 703 }),
            "defaults: the busy friend is not a candidate (today's behavior)"
        );

        let mut ctx = decision_context(|world| {
            stage(world);
            world.elements.clear(); // only the busy friend remains
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 60.0);
        });
        set_dials(&mut ctx, |b| b.w_value = 1.0);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "a live value dial admits the soon-free friend for approach"
        );
    }

    /// (h) Clarify ruling 2: seriousness reads NON-play pressure only.
    #[test]
    fn seriousness_penalizes_hunger_but_never_play_hunger() {
        // A pressing eat need costs a candidate the game...
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 8);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 50.0);
            world.kitties[fk].needs.add(NeedKind::Eat, 80.0);
            push_friend(world, 7, Position::new(8, 5));
            let g = world.kitty_index(7).unwrap();
            world.kitties[g].needs.add(NeedKind::Play, 50.0);
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.w_serious = 1.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 7 }),
            "the hungry friend is about to get serious -- leave it be"
        );

        // ...but a high PLAY pressure is the opposite of seriousness.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 8);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 80.0); // eager, not serious
            push_friend(world, 7, Position::new(8, 5));
            let g = world.kitty_index(7).unwrap();
            world.kitties[g].needs.add(NeedKind::Play, 50.0);
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.w_serious = 1.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "play pressure is value, never a penalty"
        );
    }

    /// (i) Clarify ruling 3: critter appeal is a standalone axis.
    #[test]
    fn critter_appeal_is_standalone_and_untouched_by_w_value() {
        let stage = |world: &mut crate::world::World| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.push_element(Element {
                id: 704,
                kind: ElementKind::Bug,
                pos: Position::new(5, 8), // distance 3
                ttl: Some(100),
            });
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 10); // distance 5
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 100.0);
        };
        // w_value alone: the friend's score rises, the critter's does not.
        let mut ctx = decision_context(stage);
        set_dials(&mut ctx, |b| b.w_value = 0.1);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "friend 10-5=5 beats critter 0-3=-3: w_value moved only the friend"
        );
        // critter_appeal alone lifts the critter back over.
        let mut ctx = decision_context(stage);
        set_dials(&mut ctx, |b| {
            b.w_value = 0.1;
            b.critter_appeal = 9.0;
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 704 }),
            "critter 9-3=6 beats friend 5: appeal is its own unscaled axis"
        );
    }

    /// (j) The busy-adjacent fallback: waiting is spent playing.
    #[test]
    fn an_adjacent_mid_scene_pick_resolves_to_solo_play_never_idle() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent
            busy(world, 2);
        });
        set_dials(&mut ctx, |b| b.w_value = 1.0);
        let action = play_action_with(
            &ctx,
            Some((TargetRef::Kitty { id: 2 }, Position::new(5, 6))),
        );
        assert_eq!(
            action,
            Action::play_solo(),
            "no proposal until free, and never an idle stall"
        );
    }

    /// (k) FR-010: no target lock-in -- a collapsed value redirects the
    /// very next decision. Green-on-arrival pin: selection is stateless
    /// re-scan by construction; this guard keeps it that way.
    #[test]
    fn a_collapsed_value_redirects_the_next_decision() {
        let stage = |need: f32| {
            let mut ctx = decision_context(move |world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = Position::new(5, 5);
                let f = world.kitty_index(2).unwrap();
                world.kitties[f].pos = Position::new(5, 11); // distance 6
                let fk = world.kitty_index(2).unwrap();
                world.kitties[fk].needs.add(NeedKind::Play, need);
                world.push_element(Element {
                    id: 705,
                    kind: ElementKind::Bug,
                    pos: Position::new(5, 9), // distance 4
                    ttl: Some(100),
                });
            });
            set_dials(&mut ctx, |b| {
                b.w_value = 1.0;
                b.t_partner = 20.0;
            });
            scored_playmate(&ctx).map(|(t, _)| t)
        };
        assert_eq!(
            stage(60.0),
            Some(TargetRef::Kitty { id: 2 }),
            "tick n: the eager distant friend is the pick"
        );
        assert_eq!(
            stage(0.0),
            Some(TargetRef::Element { id: 705 }),
            "tick n+1, need serviced by someone else: the pick moves on"
        );
    }

    /// (n, medium-review #2) t_partner's identity is NO BAR: a friend
    /// whose value goes negative under live w_serious/w_busy is a ranking
    /// cost, never a hard veto, until t_partner is actually raised.
    #[test]
    fn an_unraised_t_partner_never_vetoes_a_negative_value_friend() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 8);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 40.0);
            world.kitties[fk].needs.add(NeedKind::Eat, 80.0); // value 40-80 = -40
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 1.0;
            b.w_serious = 1.0; // t_partner stays 0.0
        });
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "penalized in the ranking, not dropped from it"
        );
    }

    /// (m, medium-review #1) Scope: the spec-042 score belongs to the
    /// PLAYFUL behavior's play path alone. The shared classic pick --
    /// which NeedsDriven's play scoring and the serious path consume --
    /// must ignore every dial, or the sweep's dials silently move
    /// non-playful cats.
    #[test]
    fn the_shared_classic_pick_ignores_every_dial() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 6); // adjacent, need 0
            world.push_element(Element {
                id: 708,
                kind: ElementKind::Bug,
                pos: Position::new(5, 12),
                ttl: Some(100),
            });
        });
        set_dials(&mut ctx, |b| {
            b.w_value = 5.0;
            b.t_partner = 20.0;
            b.t_self = 50.0;
        });
        assert_eq!(
            nearest_viable_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "the classic pick is nearest-first whatever the dials say"
        );
    }

    /// (l2, convergence T028) FR-008's other arm: a stalled pursuit is
    /// not re-picked however well it scores.
    #[test]
    fn a_stalled_pursuit_target_is_not_repicked_however_well_it_scores() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 200;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 9);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 100.0);
            world.push_element(Element {
                id: 707,
                kind: ElementKind::Bug,
                pos: Position::new(5, 12),
                ttl: Some(300),
            });
        });
        // A pursuit of that friend that has gained no ground for far
        // longer than the patience window (default 12).
        ctx.me.pursuit = Some(crate::kitty::Pursuit {
            target: TargetRef::Kitty { id: 2 },
            started: 100,
            closest: 4,
            improved_at: 100,
        });
        set_dials(&mut ctx, |b| b.w_value = 5.0);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 707 }),
            "a hopeless chase stays hopeless, whatever the value says"
        );
    }

    /// (l) FR-008: the score never resurrects a written-off target.
    #[test]
    fn an_excluded_friend_is_not_ranked_however_well_it_scores() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let f = world.kitty_index(2).unwrap();
            world.kitties[f].pos = Position::new(5, 8);
            let fk = world.kitty_index(2).unwrap();
            world.kitties[fk].needs.add(NeedKind::Play, 100.0);
            world.push_element(Element {
                id: 706,
                kind: ElementKind::Bug,
                pos: Position::new(5, 12),
                ttl: Some(100),
            });
        });
        ctx.me.abandoned_chases.push(crate::kitty::AbandonedChase {
            target: TargetRef::Kitty { id: 2 },
            until: ctx.world.tick + 100,
        });
        set_dials(&mut ctx, |b| b.w_value = 5.0);
        assert_eq!(
            scored_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Element { id: 706 }),
            "exclusion outranks any score"
        );
    }
}
