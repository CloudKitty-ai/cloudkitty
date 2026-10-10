//! The one parameterized teacher (spec 059).
//!
//! One ladder, four dial groups, three registrations. The dials — need
//! rates, comfort slack, consent line, favourite weights — are read per
//! decision through the SAME config accessors the observation encoder
//! uses, so teacher behavior and the observed identity cells can never
//! diverge (FR-001). What the dials cannot express — the structural
//! differences between the two historical brains — rides preset RUNG
//! TOGGLES, frozen at registration (research R1): compatibility shims,
//! never identity. The `needs_driven` and `playful` registrations are
//! byte-equal to the old brains outside consent sites (SC-001); the
//! `teacher` registration (every rung on) is the Gen 2 collection seat.
//!
//! Consent is NOT here: the gate moved target-side into the engine's
//! apply slot (ruling 2026-10-10, eb9e860b). This file never reads
//! another cat's hidden needs; the response rungs key to the audible
//! digest alone (doctrine rule 5).

use async_trait::async_trait;

use super::needs_driven::{
    finish_what_you_started, groom_response, pursue, take_what_is_here, wander,
};
use super::{selection, Behavior, DecisionContext};
use crate::action::Action;
use crate::config::COMFORT_SLACK_NORMALISER;
use crate::grid::Position;
use crate::kitty::KittyId;
use crate::meow::MessageKind;
use crate::needs::NeedKind;
use crate::seam::Decision;

/// Ticks a call's answer spends on overheads the walk cannot cover: the
/// 1-tick hearing lag (a call is audible from the NEXT tick) plus one
/// propose tick at arrival. Feeds the feasibility filter and `D_w`
/// (contracts/cue-answer.md).
pub(crate) const HANDSHAKE_TICKS: u64 = 2;

/// The scripted teacher. Toggles are per-registration structure
/// (research R1); every quantity that is identity comes from the config
/// accessors at decide time, never from this struct.
#[derive(Debug, Clone, Copy)]
pub struct Teacher {
    /// The low-pressure pottering rung (RNG-drawing). Historical
    /// needs_driven character.
    wander: bool,
    /// The WantBath answer rung. Historical needs_driven character.
    groom_response: bool,
    /// The luxury mode below the comfort line. Historical playful
    /// character; entry is slack-gated (FR-003).
    luxury: bool,
    /// The cue-answer rungs (US3). On only for the Gen 2 teacher: the
    /// compat presets never answered, and byte-equality holds them to
    /// that (research R1 addendum).
    responses: bool,
}

impl Teacher {
    /// The `needs_driven` preset: today's default brain, exactly.
    pub const NEEDS_DRIVEN: Teacher = Teacher {
        wander: true,
        groom_response: true,
        luxury: false,
        responses: false,
    };
    /// The `playful` preset: today's playful brain, exactly.
    pub const PLAYFUL: Teacher = Teacher {
        wander: false,
        groom_response: false,
        luxury: true,
        responses: false,
    };
    /// The `teacher` registration: every rung on — the Gen 2 corpus
    /// demonstrator. Biscuit gains the groom response by construction
    /// (S§4: no suppression).
    pub const GEN2: Teacher = Teacher {
        wander: true,
        groom_response: true,
        luxury: true,
        responses: true,
    };

    pub(crate) fn decide_action(&self, ctx: &DecisionContext) -> Action {
        // A scene in progress that is still doing its job gets finished first.
        if let Some(action) = finish_what_you_started(ctx) {
            return action;
        }

        // Never walk away from something you were going to want anyway.
        // (Consent left this rung with the 2026-10-10 re-key: the engine's
        // target-side gate hears every proposal; adjacency is unchanged.)
        if let Some(action) = take_what_is_here(ctx) {
            return action;
        }

        // Answer an audible ask before pottering off (spec 028): kindness
        // sits above idle wandering, below the cat's own urgent errands.
        if self.groom_response {
            if let Some(action) = groom_response(ctx) {
                return action;
            }
        }

        // The cue-answer terms (spec 059 US3): digest-keyed, valuation
        // only — they raise the matching need's score in the serious
        // selection below and name the answered caller for pursuit.
        // Recomputed from the digest every decide; expiry IS digest
        // visibility.
        let terms = if self.responses {
            response_terms(ctx)
        } else {
            ResponseTerms::NONE
        };

        // Luxury (historical playful character): below the weighted
        // comfort line AND past the slack gate, every spare moment is
        // play. The slack gate (FR-003) delays RE-ENTRY after a relief:
        // it reads the slack CELL's value — the exact number the
        // observation encodes, clamp included — times the normalizer,
        // against ticks since the most recent relief. Slack 0 (both
        // compat presets, the world default) is structurally inert.
        if self.luxury {
            let weights = &ctx.config.behavior.comfort_weight;
            let weighted_pressure = NeedKind::ALL
                .iter()
                .map(|kind| weights.get(*kind) * ctx.me.needs.get(*kind))
                .fold(0.0f32, f32::max);
            if weighted_pressure < ctx.config.behavior.playful_comfort && slack_gate_open(ctx) {
                return selection::scored_play_action(ctx);
            }
        }

        // Nothing pressing: potter about (historical needs_driven
        // character). A live answer term suppresses the potter — kindness
        // sits above idle wandering, the groom_response shelf — so the
        // RNG draw is skipped exactly when there is a call to answer.
        if self.wander && !terms.any_live() {
            let (_, pressure) = ctx.me.needs.highest_pressure();
            if pressure < 20.0 && ctx.rng.gen_bool(0.4) {
                return wander(ctx);
            }
        }

        // One scored pass over every need: urgency weighs in, travel
        // counts against, favourites and answer terms tip the values
        // (spec 059), and nothing gets locked out (see `selection`).
        pursue(ctx, selection::choose_with_terms(ctx, &terms))
    }
}

#[async_trait]
impl Behavior for Teacher {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        // Two channels (spec 028): the ladder picks the activity; the
        // announce rule rides along, never displacing it.
        let mut decision = Decision::from_legacy(self.decide_action(ctx));
        if decision.message.is_none() {
            decision.message = super::announce(ctx);
        }
        decision
    }

    fn is_builtin(&self) -> bool {
        true
    }
}

/// The slack gate (FR-003): luxury re-entry waits until
/// `ticks since the most recent relief ≥ slack_cell × 40`. The cell value
/// is `Config::slack_cell_for` — the observation's own number, clamp
/// included (slack past 40 saturates at 40 ticks; shared semantics with
/// the student). Slack 0 compares `elapsed ≥ 0`, which is always true:
/// structurally inert for both compat presets.
fn slack_gate_open(ctx: &DecisionContext) -> bool {
    let slack_ticks = ctx.config.slack_cell_for(ctx.me.id) * COMFORT_SLACK_NORMALISER;
    if slack_ticks <= 0.0 {
        return true;
    }
    let last_relief = NeedKind::ALL
        .iter()
        .map(|kind| ctx.me.last_relief_tick(*kind))
        .max()
        .unwrap_or(0);
    ctx.world.tick.saturating_sub(last_relief) as f32 >= slack_ticks
}

/// One live answer term: the winning caller of one want kind, its
/// position (the call's stamp — a heard-unseen caller is walked to where
/// it called from, the groom_response precedent), and the valuation
/// boost in pressure units.
#[derive(Debug, Clone, Copy, PartialEq)]
pub(crate) struct ResponseTerm {
    pub caller: KittyId,
    pub pos: Position,
    pub boost: f32,
}

/// The per-kind answer terms a decide carries into selection. Empty for
/// every registration but `teacher` — and `NONE` adds exactly 0.0, so
/// the scored pass is byte-identical without them.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub(crate) struct ResponseTerms {
    pub cuddle: Option<ResponseTerm>,
    pub play: Option<ResponseTerm>,
}

impl ResponseTerms {
    pub(crate) const NONE: ResponseTerms = ResponseTerms {
        cuddle: None,
        play: None,
    };

    pub(crate) fn for_need(&self, kind: NeedKind) -> Option<&ResponseTerm> {
        match kind {
            NeedKind::Cuddle => self.cuddle.as_ref(),
            NeedKind::Play => self.play.as_ref(),
            _ => None,
        }
    }

    fn any_live(&self) -> bool {
        self.cuddle.is_some() || self.play.is_some()
    }
}

/// The linear net-surplus constant `k = (I_max − I_min) / D_w`
/// (contracts/cue-answer.md, owner-confirmed 2026-10-10): I_max is the
/// emission clamp (1.0), I_min the true armed-emission floor —
/// `(announce_threshold − announce_hysteresis) / 100`, because an armed
/// kind stays emittable down to the bottom of the hysteresis band
/// (review 2026-10-10 finding 6) — and D_w the longest Manhattan walk
/// the digest window can still cover after the handshake, at the
/// implicit 1 tile/tick. A degenerate window yields k = 0: distance
/// stops discounting but feasibility still filters.
fn k_constant(ctx: &DecisionContext) -> f32 {
    let i_min = ((ctx.config.meow.announce_threshold - ctx.config.meow.announce_hysteresis)
        / 100.0)
        .clamp(0.0, 1.0);
    let d_w = ctx
        .config
        .meow
        .digest_window_ticks
        .saturating_sub(HANDSHAKE_TICKS) as f32;
    if d_w <= 0.0 {
        return 0.0;
    }
    (1.0 - i_min) / d_w
}

/// FR-011's window bar, scoped to the config being served (clarify
/// 2026-10-10): on a world whose digest window cannot cover a typical
/// approach — D_w below ≈(width+height)/3 tiles, the mean Manhattan
/// separation of uniform points, at the implicit 1 tile/tick — most cue
/// answers are infeasible. That is lawful (the feasibility filter holds
/// everywhere) but collection-hostile, so startup WARNS rather than
/// refuses. Pure and unit-tested here; the server logs it.
pub fn response_window_shortfall(config: &crate::config::Config) -> Option<String> {
    let d_w = config
        .meow
        .digest_window_ticks
        .saturating_sub(HANDSHAKE_TICKS);
    let typical = ((config.world.width + config.world.height) / 3) as u64;
    (d_w < typical).then(|| {
        format!(
            "[meow] digest_window_ticks {} leaves D_w {} ticks below the typical \
             approach distance {} tiles (≈(width+height)/3 at 1 tile/tick): most \
             cue answers will be infeasible on this world (spec 059 FR-011; the \
             feasibility filter keeps behavior lawful, but a collection config \
             should not look like this)",
            config.meow.digest_window_ticks, d_w, typical
        )
    })
}

fn response_terms(ctx: &DecisionContext) -> ResponseTerms {
    let k = k_constant(ctx);
    ResponseTerms {
        cuddle: response_term(ctx, MessageKind::WantCuddle, k),
        play: response_term(ctx, MessageKind::WantPlay, k),
    }
}

/// The one winner for one want kind (FR-016): feasibility filter first
/// (a caller the hearer cannot reach and complete with inside the
/// remaining window is dropped — hard, not scored), then the linear
/// net-surplus score `intensity − k·d`, Manhattan. The fire threshold is
/// deterministic (clarify Q3): the call must outrank the hearer's own
/// loudest need (`intensity ≥ max(reply_intensity_floor, top/100)`) —
/// graded across states, never a draw. Tie chain: score → higher
/// intensity → nearer → lower id. Free-register kinds never reach here:
/// the rung keys on the two want kinds alone (FR-012).
///
/// The commitment margin (owner ruled B, 2026-10-10, on Experiments'
/// measured read a3abffb7): the margin exists exactly where commitment
/// is OBSERVABLE, and nowhere else. A play answer walks as a Chase, so
/// the engine's pursuit record — surfaced to the student as the pursuit
/// cells and the activity-target bits — names the incumbent; a
/// challenger displaces it only past `h = k × response_commitment_ticks`.
/// A cuddle answer walks as bare Moves with no observable commitment,
/// so it stays a pure function of the observation and switches freely
/// to any new net-surplus winner — an unobservable commitment would be
/// the exact rule-5 violation this spec removes elsewhere.
fn response_term(ctx: &DecisionContext, kind: MessageKind, k: f32) -> Option<ResponseTerm> {
    let me = &ctx.me;
    let floor = ctx.config.behavior.reply_intensity_floor.unwrap_or(0.0);
    let (_, top) = me.needs.highest_pressure();
    // The groom_response precedent (review 2026-10-10 finding 4): a cat
    // whose own top need is at or past the safeguard has its own errand
    // first — no answer term, ever, at safeguard pressure. Below it, the
    // deterministic threshold: the call must outrank the hearer's own
    // loudest need.
    if top >= ctx.config.thresholds.safeguard {
        return None;
    }
    let threshold = (top / 100.0).max(floor);
    let window = ctx.config.meow.digest_window_ticks;
    let now = ctx.world.tick;

    // Each caller is represented by its FRESHEST audible call of this
    // kind, and nothing else (review 2026-10-10 finding 1): the
    // observation's digest cell and heard row carry only the freshest,
    // so a superseded call is state the student cannot see — scoring it
    // would be the rule-5 violation this spec removes elsewhere.
    let audible: Vec<&crate::meow::Meow> = ctx
        .world
        .recent_meows
        .iter()
        .filter(|m| m.kind == kind && m.kitty_id != me.id && ctx.world.audible(m, window))
        .collect();
    let candidates: Vec<&crate::meow::Meow> = audible
        .iter()
        .filter(|m| {
            !audible
                .iter()
                .any(|m2| m2.kitty_id == m.kitty_id && m2.tick > m.tick)
        })
        .copied()
        .filter(|m| m.intensity >= threshold)
        .filter(|m| {
            // Feasible: d + handshake fits in the window still open.
            let remaining = window.saturating_sub(now.saturating_sub(m.tick));
            let d = me.pos.manhattan_distance(&m.pos) as u64;
            d + HANDSHAKE_TICKS <= remaining
        })
        // A written-off or stalled chase target is not resurrected by its
        // own calling (review 2026-10-10 finding 2): the same chase
        // bookkeeping every playmate scan honors gates the answer too.
        .filter(|m| {
            kind != MessageKind::WantPlay
                || selection::chase_bookkeeping_allows(
                    ctx,
                    crate::action::TargetRef::Kitty { id: m.kitty_id },
                )
        })
        .collect();
    let score = |m: &crate::meow::Meow| m.intensity - k * me.pos.manhattan_distance(&m.pos) as f32;
    let best = candidates
        .iter()
        .max_by(|a, b| {
            let (sa, sb) = (score(a), score(b));
            sa.total_cmp(&sb)
                .then(a.intensity.total_cmp(&b.intensity))
                .then(
                    (me.pos.manhattan_distance(&b.pos)).cmp(&me.pos.manhattan_distance(&a.pos)), // nearer wins
                )
                .then(b.kitty_id.cmp(&a.kitty_id)) // lower id wins
        })
        .copied()?;
    // The play-side incumbent: the caller this cat's recorded pursuit
    // already chases. Holds unless the best challenger clears the margin.
    let incumbent = (kind == MessageKind::WantPlay)
        .then_some(me.pursuit)
        .flatten()
        .and_then(|p| match p.target {
            crate::action::TargetRef::Kitty { id } => {
                candidates.iter().find(|m| m.kitty_id == id).copied()
            }
            crate::action::TargetRef::Element { .. } => None,
        });
    let h = k * ctx.config.behavior.response_commitment_ticks;
    let winner = match incumbent {
        Some(inc) if inc.kitty_id != best.kitty_id && score(best) <= score(inc) + h => inc,
        _ => best,
    };
    // A non-positive net surplus is no answer at all (review 2026-10-10
    // finding 6): a quiet-and-far call must never LOWER the pull toward
    // its own need, and a zero-value term must not retarget pursuit.
    if score(winner) <= 0.0 {
        return None;
    }
    let d = me.pos.manhattan_distance(&winner.pos) as f32;
    Some(ResponseTerm {
        caller: winner.kitty_id,
        pos: winner.pos,
        // Net surplus, re-inflated to pressure units: the same currency
        // the selection score speaks (derived, not a tunable —
        // contracts/cue-answer.md).
        boost: (winner.intensity - k * d) * 100.0,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::action::Action;
    use crate::test_support::decision_context;

    /// A cat with nothing pressing (weighted pressure under comfort) whose
    /// most recent relief was `ticks_since` ticks ago, with a per-kitty
    /// slack override — the luxury gate's own staging. No playmates in
    /// reach, so luxury is the solo pounce and the gated path is the
    /// scored selection's in-place choice: two distinguishable actions.
    fn luxury_ctx(slack: f32, ticks_since: u64) -> super::super::DecisionContext {
        let mut ctx = decision_context(move |world| {
            world.tick = 200;
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = crate::grid::Position::new(5, 5);
            world.kitties[idx].needs = crate::needs::Needs::default();
            world.kitties[idx]
                .needs
                .add(crate::needs::NeedKind::Bath, 10.0);
            world.kitties[idx]
                .last_relief
                .insert(crate::needs::NeedKind::Eat, 200 - ticks_since);
            // Park the other seats out of reach AND mid-scene: at default
            // dials a busy friend is not a luxury candidate, so luxury is
            // the solo pounce — distinguishable from the serious path.
            for k in &mut world.kitties {
                if k.id != 1 {
                    k.pos = crate::grid::Position::new(15, 15);
                    k.activity = crate::kitty::Activity::Grooming { target: None };
                    k.activity_clock = Some(crate::kitty::ActivityClock::start(200));
                }
            }
        });
        let config = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
        let k1 = config.kitties.iter_mut().find(|k| k.id == 1).unwrap();
        k1.comfort_slack = Some(slack);
        ctx
    }

    /// FR-003: slack gates luxury ENTRY by exactly its tick count, read
    /// off the per-kitty accessor — inside the slack window the cat runs
    /// the serious selection; at the boundary it returns to luxury.
    #[test]
    fn slack_delays_the_return_to_luxury_by_its_tick_count() {
        let gated = Teacher::PLAYFUL.decide_action(&luxury_ctx(12.0, 11));
        assert!(
            !matches!(gated, Action::Play { target: None }),
            "11 < 12 ticks since relief: still inside the slack window, got {gated:?}"
        );
        let open = Teacher::PLAYFUL.decide_action(&luxury_ctx(12.0, 12));
        assert_eq!(
            open,
            Action::play_solo(),
            "12 >= 12: the gate opens exactly at the slack count"
        );
    }

    /// FR-003: the gate reads the CELL's value, clamp included — slack 80
    /// saturates at 40 effective ticks (slack_cell 1.0 × normalizer),
    /// exactly what the observation shows the student.
    #[test]
    fn the_slack_gate_reads_the_clamped_cell_not_raw_slack() {
        let open = Teacher::PLAYFUL.decide_action(&luxury_ctx(80.0, 45));
        assert_eq!(
            open,
            Action::play_solo(),
            "45 >= the clamped 40: a raw-slack read (45 < 80) would still gate"
        );
    }

    /// Slack 0 — both compat presets and the world default — is inert:
    /// luxury entry is today's stateless comparison.
    #[test]
    fn slack_zero_is_structurally_inert() {
        assert_eq!(
            Teacher::PLAYFUL.decide_action(&luxury_ctx(0.0, 0)),
            Action::play_solo(),
            "relief THIS tick, slack 0: luxury immediately, as today"
        );
    }

    /// FR-004: a favourite tips selection between equal-value options —
    /// equal pressures, both reliefs underfoot, where the deterministic
    /// tie falls to Eat by ALL-order; a Cuddle favourite flips it, an Eat
    /// favourite keeps it (each dial moves exactly its own thing), and
    /// all-zero is the unweighted pass by construction.
    #[test]
    fn a_favourite_tips_an_equal_value_choice() {
        let stage = |favourite: Option<(crate::needs::NeedKind, f32)>| {
            let mut ctx = decision_context(|world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = crate::grid::Position::new(5, 5);
                world.kitties[idx].needs = crate::needs::Needs::default();
                world.kitties[idx]
                    .needs
                    .add(crate::needs::NeedKind::Eat, 40.0);
                world.kitties[idx]
                    .needs
                    .add(crate::needs::NeedKind::Cuddle, 40.0);
                // Both reliefs underfoot: chow adjacent, an idle friend adjacent.
                world.push_element(crate::element::Element {
                    id: 800,
                    kind: crate::element::ElementKind::Chow { servings: 5 },
                    pos: crate::grid::Position::new(5, 6),
                    ttl: None,
                });
                let f = world.kitty_index(2).unwrap();
                world.kitties[f].pos = crate::grid::Position::new(4, 5);
                for k in &mut world.kitties {
                    if k.id > 2 {
                        k.pos = crate::grid::Position::new(15, 15);
                    }
                }
            });
            if let Some((kind, w)) = favourite {
                let config = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
                let k1 = config.kitties.iter_mut().find(|k| k.id == 1).unwrap();
                let mut fav = crate::config::FavouriteWeights::default();
                match kind {
                    NeedKind::Eat => fav.eat = Some(w),
                    NeedKind::Cuddle => fav.cuddle = Some(w),
                    _ => unreachable!("only eat/cuddle staged here"),
                }
                k1.favourite = Some(fav);
            }
            crate::behavior::selection::choose(&ctx).need
        };
        assert_eq!(
            stage(None),
            crate::needs::NeedKind::Eat,
            "equal values: the deterministic tie falls to Eat"
        );
        assert_eq!(
            stage(Some((crate::needs::NeedKind::Cuddle, 0.5))),
            crate::needs::NeedKind::Cuddle,
            "a cuddle favourite tips the equal-value choice"
        );
        assert_eq!(
            stage(Some((crate::needs::NeedKind::Eat, 0.5))),
            crate::needs::NeedKind::Eat,
            "an eat favourite moves only its own kind"
        );
    }

    /// SC-003, the behavior-layer twin of spec 058's row-visibility
    /// property: a friend's HIDDEN state (the five non-bath needs;
    /// happiness) cannot move any teacher decision. Paired decides over
    /// a sweep of hidden extremes — same world, same seed, same digest,
    /// live 042 dials so every re-keyed path is exercised — must be
    /// identical. Bath is deliberately NOT varied (the ruled visible
    /// need, lawfully read); the engine's consent gate is out of frame
    /// (it is target-side and runs at the apply slot, not here).
    #[test]
    fn hidden_friend_extremes_cannot_move_any_teacher_decision() {
        let decide = |preset: Teacher, hidden: [f32; 5]| {
            let mut ctx = decision_context(move |world| {
                world.tick = 100;
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = crate::grid::Position::new(5, 5);
                world.kitties[idx].needs = crate::needs::Needs::default();
                // Play 40: under the comfort line, so the playful/teacher
                // presets take the LUXURY path (scored_playmate — the one
                // place a reintroduced partner read could hide), and well
                // over the wander line so no RNG draw complicates the pair.
                world.kitties[idx]
                    .needs
                    .add(crate::needs::NeedKind::Play, 40.0);
                // A competing critter at the friend's exact distance: a
                // score moved by hidden state FLIPS the pick instead of
                // vanishing into a one-candidate scan.
                world.push_element(crate::element::Element {
                    id: 900,
                    kind: crate::element::ElementKind::Bug,
                    pos: crate::grid::Position::new(8, 5),
                    ttl: Some(1000),
                });
                let f = world.kitty_index(2).unwrap();
                world.kitties[f].pos = crate::grid::Position::new(5, 8);
                world.kitties[f].needs = crate::needs::Needs::default();
                for (kind, v) in [
                    crate::needs::NeedKind::Eat,
                    crate::needs::NeedKind::Drink,
                    crate::needs::NeedKind::Sleep,
                    crate::needs::NeedKind::Play,
                    crate::needs::NeedKind::Cuddle,
                ]
                .into_iter()
                .zip(hidden)
                {
                    world.kitties[f].needs.add(kind, v);
                }
                for k in &mut world.kitties {
                    if k.id > 2 {
                        k.pos = crate::grid::Position::new(15, 15);
                    }
                }
            });
            let config = std::sync::Arc::get_mut(&mut ctx.config).unwrap();
            config.behavior.w_value = 1.0;
            config.behavior.w_busy = 1.0;
            config.behavior.w_serious = 1.0;
            config.behavior.consent_line = 30.0;
            preset.decide_action(&ctx)
        };
        let sweeps: [[f32; 5]; 4] = [
            [0.0; 5],
            [95.0; 5],
            [95.0, 0.0, 95.0, 0.0, 95.0],
            [0.0, 95.0, 0.0, 95.0, 0.0],
        ];
        for preset in [Teacher::NEEDS_DRIVEN, Teacher::PLAYFUL, Teacher::GEN2] {
            let reference = decide(preset, sweeps[0]);
            for hidden in &sweeps[1..] {
                assert_eq!(
                    decide(preset, *hidden),
                    reference,
                    "a hidden extreme moved the decision (preset {preset:?}, hidden {hidden:?})"
                );
            }
        }
    }

    /// Adds an extra idle friend (the test roster has only kitties 1-2).
    fn push_friend(world: &mut crate::world::World, id: u32, pos: crate::grid::Position) {
        let mut k = world.kitties[0].clone();
        k.id = id;
        k.name = format!("Extra{id}");
        k.pos = pos;
        k.needs = crate::needs::Needs::default();
        k.activity = crate::kitty::Activity::Idle;
        k.activity_clock = None;
        world.kitties.push(k);
    }

    /// Stages an audible want-call from `id`, stamped `age` ticks before
    /// the staged now (tick 100), at the caller's position.
    fn call(world: &mut crate::world::World, id: u32, kind: MessageKind, intensity: f32, age: u64) {
        let pos = world.kitties.iter().find(|k| k.id == id).unwrap().pos;
        world.recent_meows.push(crate::meow::Meow {
            kitty_id: id,
            kind,
            tick: 100 - age,
            intensity,
            pos,
            reply: false,
        });
    }

    /// A GEN2 hearer at (5,5) with its own top pressure pinned, friends
    /// parked busy out of reach (no luxury candidates, no groomable asks)
    /// — the cue-answer rungs' clean room. Callers are staged by `call`.
    fn hearer_ctx(
        own_top: f32,
        stage_calls: impl Fn(&mut crate::world::World) + Send + Sync + 'static,
    ) -> super::super::DecisionContext {
        decision_context(move |world| {
            world.tick = 100;
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = crate::grid::Position::new(5, 5);
            world.kitties[idx].needs = crate::needs::Needs::default();
            world.kitties[idx]
                .needs
                .add(crate::needs::NeedKind::Sleep, own_top);
            for k in &mut world.kitties {
                if k.id != 1 {
                    k.pos = crate::grid::Position::new(18, 18);
                    k.activity = crate::kitty::Activity::Grooming { target: None };
                    k.activity_clock = Some(crate::kitty::ActivityClock::start(100));
                }
            }
            stage_calls(world);
        })
    }

    /// FR-010: the term exists while the call's remaining window still
    /// covers the answer and is gone one tick later — expiry IS the
    /// digest window, met through the feasibility margin (an adjacent
    /// caller, d 1, needs 1 + HANDSHAKE ticks of window left), with no
    /// stored state. A call past the window itself is simply inaudible.
    #[test]
    fn the_term_expires_with_the_digest_window() {
        let window = crate::config::Config::default().meow.digest_window_ticks;
        let edge = window - 1 - HANDSHAKE_TICKS; // remaining = d + handshake exactly
        let inside = hearer_ctx(20.0, move |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6); // adjacent
            call(w, 2, MessageKind::WantCuddle, 0.60, edge);
        });
        assert!(
            response_terms(&inside).cuddle.is_some(),
            "remaining window exactly covers d + handshake: live"
        );
        let past = hearer_ctx(20.0, move |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6);
            call(w, 2, MessageKind::WantCuddle, 0.60, edge + 1);
        });
        assert!(
            response_terms(&past).cuddle.is_none(),
            "one tick later the answer cannot complete: expired"
        );
        let inaudible = hearer_ctx(20.0, move |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6);
            call(w, 2, MessageKind::WantCuddle, 0.60, window);
        });
        assert!(
            response_terms(&inaudible).cuddle.is_none(),
            "at the window the call is not even audible"
        );
    }

    /// FR-011 (clarify Q3): deterministic threshold — the call must
    /// outrank the hearer's own loudest need, in both directions.
    #[test]
    fn the_threshold_compares_the_call_to_the_hearers_own_loudest_need() {
        let quiet_call_busy_hearer = hearer_ctx(70.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 9);
            call(w, 2, MessageKind::WantCuddle, 0.60, 1);
        });
        assert!(
            response_terms(&quiet_call_busy_hearer).cuddle.is_none(),
            "intensity 0.60 under own top 70/100: no term"
        );
        let same_call_idle_hearer = hearer_ctx(40.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 9);
            call(w, 2, MessageKind::WantCuddle, 0.60, 1);
        });
        assert!(
            response_terms(&same_call_idle_hearer).cuddle.is_some(),
            "intensity 0.60 over own top 40/100: the term fires"
        );
    }

    /// FR-016: the feasibility filter is hard — a louder caller the
    /// hearer cannot reach inside the remaining window never enters the
    /// score; the quieter, reachable one wins outright.
    #[test]
    fn feasibility_drops_a_louder_unreachable_caller() {
        let ctx = hearer_ctx(20.0, |w| {
            // Loud but stale-and-far: 25 ticks already spent, d = 13 — the
            // remaining 5-tick window cannot cover 13 + handshake.
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(18, 5);
            call(w, 2, MessageKind::WantPlay, 0.95, 25);
            // Quiet and near and fresh: d = 3, feasible.
            push_friend(w, 3, crate::grid::Position::new(5, 8));
            call(w, 3, MessageKind::WantPlay, 0.40, 1);
        });
        let term = response_terms(&ctx).play.expect("the near call is live");
        assert_eq!(
            term.caller, 3,
            "the infeasible loud call never enters the score"
        );
    }

    /// Spec US3 scenario 5: the iso-line. Two feasible same-kind calls —
    /// louder wins while intensity_diff > k·distance_diff; nearer wins
    /// when the inequality reverses. k at the default config is
    /// (1 − 0.20) / 28 ≈ 0.0286.
    #[test]
    fn the_choice_flips_from_louder_to_nearer_across_the_iso_line() {
        // intensity_diff 0.25 > k·(d 3 − d 2 = 1) ≈ 0.029: louder wins.
        let louder = hearer_ctx(20.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 8); // d 3
            call(w, 2, MessageKind::WantPlay, 0.95, 1);
            push_friend(w, 3, crate::grid::Position::new(5, 7)); // d 2
            call(w, 3, MessageKind::WantPlay, 0.70, 1);
        });
        assert_eq!(response_terms(&louder).play.unwrap().caller, 2);
        // intensity_diff 0.1 < k·(d 10 − d 2 = 8) ≈ 0.229: nearer wins.
        let nearer = hearer_ctx(20.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 15); // d 10
            call(w, 2, MessageKind::WantPlay, 0.80, 1);
            push_friend(w, 3, crate::grid::Position::new(5, 7)); // d 2
            call(w, 3, MessageKind::WantPlay, 0.70, 1);
        });
        assert_eq!(response_terms(&nearer).play.unwrap().caller, 3);
    }

    /// FR-012: the free register moves nothing — an armed trill/ekekek in
    /// the digest produces no term and leaves the whole decision
    /// untouched; and the scripted emitter can never answer in it (a
    /// world where only free-register words would be legal gets Silence).
    #[tokio::test]
    async fn free_register_kinds_move_nothing_and_are_never_spoken() {
        let silent = hearer_ctx(20.0, |_| {});
        let noisy = hearer_ctx(20.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 9);
            call(w, 2, MessageKind::Trill, 0.90, 1);
            call(w, 2, MessageKind::Ekekek, 0.90, 1);
            call(w, 2, MessageKind::Mew, 0.90, 1);
        });
        assert_eq!(response_terms(&noisy), ResponseTerms::NONE);
        assert_eq!(
            Teacher::GEN2.decide_action(&noisy),
            Teacher::GEN2.decide_action(&silent),
            "free-register noise is invisible to the ladder"
        );
        // Emission half: the hearer's own needs are all below arming, so
        // no want is legal; the decision's message channel must be empty,
        // never a free-register word.
        let decision = Teacher::GEN2.decide(&silent).await;
        assert!(
            !matches!(
                decision.message,
                Some(
                    MessageKind::Mew
                        | MessageKind::Chirp
                        | MessageKind::Trill
                        | MessageKind::Ekekek
                )
            ),
            "the scripted teacher never speaks the free register: {:?}",
            decision.message
        );
    }

    /// FR-010 scenarios 1-2 end to end: an answered play call walks to
    /// the CALLER and the resulting proposal still passes the engine's
    /// unchanged gates — a burdened caller's own line refuses the answer
    /// at the apply slot (valuation is never a consent bypass).
    #[test]
    fn an_answer_never_bypasses_the_consent_gate() {
        // Own top 60: OVER the comfort line, so the luxury rung is shut
        // and only the answer term can put play on top — the boost itself
        // is what moves this decision (its own mutate witness).
        let ctx = hearer_ctx(60.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6); // adjacent
            w.kitties[f].activity = crate::kitty::Activity::Idle;
            w.kitties[f].activity_clock = None;
            w.kitties[f].needs = crate::needs::Needs::default();
            w.kitties[f].needs.add(crate::needs::NeedKind::Play, 35.0);
            w.kitties[f].needs.add(crate::needs::NeedKind::Eat, 60.0); // past line 30
            call(w, 2, MessageKind::WantPlay, 0.95, 1);
        });
        // The term is live and the decide proposes play at the caller.
        assert_eq!(response_terms(&ctx).play.unwrap().caller, 2);
        let action = Teacher::GEN2.decide_action(&ctx);
        assert_eq!(
            action,
            Action::play_with(crate::action::TargetRef::Kitty { id: 2 }),
            "the answer proposes at the caller"
        );
        // The engine's gate refuses it: the term raised a valuation, not
        // a permission (staged on a fresh world with the same shape).
        let mut config = crate::config::Config::default();
        config.behavior.consent_line = 30.0;
        let config = std::sync::Arc::new(config);
        let mut world = crate::world::World::generate(&config);
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = crate::grid::Position::new(5, 5);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = crate::grid::Position::new(5, 6);
        world.kitties[b].needs = crate::needs::Needs::default();
        world.kitties[b]
            .needs
            .add(crate::needs::NeedKind::Play, 35.0);
        world.kitties[b]
            .needs
            .add(crate::needs::NeedKind::Eat, 60.0);
        assert_eq!(
            world.apply_slot_verdict(1, action, &config),
            Action::Idle,
            "consent and adjacency gates run unchanged after the term"
        );
    }

    /// Review 2026-10-10 finding 1: only a caller's FRESHEST call of a
    /// kind speaks for it — the observation carries nothing older, so a
    /// superseded call is invisible state. A loud old call must neither
    /// clear the threshold nor aim the answer at its stale stamp.
    #[test]
    fn only_a_callers_freshest_call_speaks_for_it() {
        let ctx = hearer_ctx(50.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6);
            call(w, 2, MessageKind::WantPlay, 0.90, 20); // loud, superseded
            w.kitties[f].pos = crate::grid::Position::new(5, 12);
            call(w, 2, MessageKind::WantPlay, 0.30, 5); // the freshest: quiet
        });
        assert!(
            response_terms(&ctx).play.is_none(),
            "the freshest call (0.30) is under the hearer's 0.50 threshold; \
             the superseded 0.90 must not fire"
        );
    }

    /// Review 2026-10-10 finding 2: a written-off chase target cannot
    /// call itself back — the same chase bookkeeping every playmate scan
    /// honors gates the answer.
    #[test]
    fn a_written_off_chase_target_cannot_call_itself_back() {
        let ctx = hearer_ctx(20.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 9);
            call(w, 2, MessageKind::WantPlay, 0.80, 1);
            let me = w.kitty_index(1).unwrap();
            w.kitties[me]
                .abandoned_chases
                .push(crate::kitty::AbandonedChase {
                    target: crate::action::TargetRef::Kitty { id: 2 },
                    until: 1000,
                });
        });
        assert!(
            response_terms(&ctx).play.is_none(),
            "an excluded target's call raises no term"
        );
    }

    /// Review 2026-10-10 finding 3: a reached stamp with no caller in
    /// view releases the PLAY answer to the ordinary playmate pick (the
    /// cuddle arm's rule) instead of pinning solo pounces at the stamp.
    #[test]
    fn a_reached_empty_stamp_releases_the_play_answer() {
        let ctx = hearer_ctx(20.0, |w| {
            // A real critter the ordinary pick would chase.
            w.push_element(crate::element::Element {
                id: 910,
                kind: crate::element::ElementKind::Bug,
                pos: crate::grid::Position::new(5, 9),
                ttl: Some(1000),
            });
        });
        let choice = crate::behavior::selection::Choice {
            need: NeedKind::Play,
            playmate: Some((
                crate::action::TargetRef::Element { id: 910 },
                crate::grid::Position::new(5, 9),
            )),
            // Caller 99 does not exist; the stamp is adjacent: reached.
            answered: Some((99, crate::grid::Position::new(5, 6))),
        };
        let action = super::super::needs_driven::pursue(&ctx, choice);
        assert_eq!(
            action,
            Action::Chase(crate::action::TargetRef::Element { id: 910 }),
            "the dropped answer falls through to the ordinary pick"
        );
    }

    /// Review 2026-10-10 finding 4 (the groom_response precedent): a
    /// hearer at safeguard pressure has its own errand first — no answer
    /// term, however loud the call.
    #[test]
    fn safeguard_pressure_silences_every_answer() {
        let ctx = hearer_ctx(80.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 6);
            call(w, 2, MessageKind::WantCuddle, 0.95, 1);
            call(w, 2, MessageKind::WantPlay, 0.95, 1);
        });
        assert_eq!(
            response_terms(&ctx),
            ResponseTerms::NONE,
            "safeguard first: eat at 80 is not outranked by any call"
        );
    }

    /// Review 2026-10-10 finding 6: a non-positive net surplus is no
    /// answer — a quiet far call must never lower the pull toward its
    /// own need or retarget pursuit for nothing.
    #[test]
    fn a_non_positive_surplus_is_no_answer() {
        let ctx = hearer_ctx(15.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 15); // d 10
            call(w, 2, MessageKind::WantPlay, 0.20, 1); // k·10 ≈ 0.30 > 0.20
        });
        assert!(
            response_terms(&ctx).play.is_none(),
            "intensity 0.20 minus k·10 is negative: no term"
        );
    }

    /// FR-016 margin (owner ruled B, 2026-10-10): a recorded play
    /// pursuit of a live caller is the incumbent; a challenger within
    /// `h = k × response_commitment_ticks` never displaces it, one past
    /// the margin does. At default config h ≈ 0.0857 score units.
    #[test]
    fn the_margin_holds_a_play_incumbent_against_an_in_margin_challenger() {
        let stage = |challenger_intensity: f32| {
            hearer_ctx(20.0, move |w| {
                // The incumbent: caller 2 at d 4, already pursued.
                let f = w.kitty_index(2).unwrap();
                w.kitties[f].pos = crate::grid::Position::new(5, 9);
                call(w, 2, MessageKind::WantPlay, 0.70, 2);
                // The challenger: caller 3 at the same distance.
                push_friend(w, 3, crate::grid::Position::new(9, 5));
                call(w, 3, MessageKind::WantPlay, challenger_intensity, 1);
                let me = w.kitty_index(1).unwrap();
                w.kitties[me].pursuit = Some(crate::kitty::Pursuit {
                    target: crate::action::TargetRef::Kitty { id: 2 },
                    started: 95,
                    closest: 4,
                    improved_at: 99,
                });
            })
        };
        // Equal distances: the score gap is the intensity gap.
        assert_eq!(
            response_terms(&stage(0.75)).play.unwrap().caller,
            2,
            "0.05 over the incumbent is inside h ≈ 0.0857: the incumbent holds"
        );
        assert_eq!(
            response_terms(&stage(0.80)).play.unwrap().caller,
            3,
            "0.10 over the incumbent clears h: the challenger takes it"
        );
    }

    /// The cuddle side has no observable commitment, so it has no margin
    /// (ruled B): the same in-margin challenger that a play incumbent
    /// resists takes a cuddle answer immediately.
    #[test]
    fn a_cuddle_answer_switches_freely_no_margin() {
        let ctx = hearer_ctx(20.0, |w| {
            let f = w.kitty_index(2).unwrap();
            w.kitties[f].pos = crate::grid::Position::new(5, 9);
            call(w, 2, MessageKind::WantCuddle, 0.70, 2);
            push_friend(w, 3, crate::grid::Position::new(9, 5));
            call(w, 3, MessageKind::WantCuddle, 0.75, 1);
            // Even a recorded pursuit of caller 2 confers no cuddle hold.
            let me = w.kitty_index(1).unwrap();
            w.kitties[me].pursuit = Some(crate::kitty::Pursuit {
                target: crate::action::TargetRef::Kitty { id: 2 },
                started: 95,
                closest: 4,
                improved_at: 99,
            });
        });
        assert_eq!(
            response_terms(&ctx).cuddle.unwrap().caller,
            3,
            "cuddle answers are a pure function of the observation"
        );
    }

    /// FR-011's config bar: the served shape clears it; a world the
    /// digest cannot cover does not, and the shortfall names the numbers.
    #[test]
    fn the_window_shortfall_warns_exactly_when_the_digest_cannot_cover_approach() {
        let config = crate::config::Config::default();
        assert_eq!(
            response_window_shortfall(&config),
            None,
            "20x20 with window 30: D_w 28 covers the typical 13"
        );
        let mut big = crate::config::Config::default();
        big.world.width = 58;
        big.world.height = 100;
        let s = response_window_shortfall(&big).expect("58x100 cannot be covered by 30");
        assert!(s.contains("digest_window_ticks 30"), "{s}");
        assert!(s.contains("52"), "names the typical distance: {s}");
    }

    #[test]
    fn the_preset_toggle_table_is_the_contract_table() {
        // contracts/presets-and-dials.md, pinned: a toggle edit must be a
        // deliberate contract change, not a drive-by.
        let nd = Teacher::NEEDS_DRIVEN;
        assert!(
            (nd.wander, nd.groom_response, nd.luxury, nd.responses) == (true, true, false, false)
        );
        let p = Teacher::PLAYFUL;
        assert!((p.wander, p.groom_response, p.luxury, p.responses) == (false, false, true, false));
        let g = Teacher::GEN2;
        assert!((g.wander, g.groom_response, g.luxury, g.responses) == (true, true, true, true));
    }
}
