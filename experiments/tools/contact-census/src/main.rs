//! The scripted contact census (exp-004 cosleep-pricing baseline).
//!
//! Measures what "presence" is actually worth on a behavior-driven world:
//! how often cats co-sleep, how long the named companion actually stays in
//! contact, what that companion is doing while the credit flows, and where
//! the cuddle need sits between contacts. This is the "before" picture for
//! the cosleep dial-pricing pilot (exp-004 design inputs §1) — the pilot's
//! control arm re-runs this instrument after the routing change and the
//! dedicated dials exist.
//!
//! Geometry is the F-016 instrument's (`scripted_water_baseline.py` /
//! `water_band.py`): served world, 10 seeds × 20k ticks. The census also
//! tallies on-water occupancy by activity so the run cross-checks against
//! the committed scripted baseline (`rebaseline-2026-08-06/optE-B`) — a
//! disagreement there means this tool is broken, not the world.
//!
//! Why Rust and not the pyo3 env: the measurement's subject is the *named*
//! sleep companion (`Activity::Sleeping { with_friend }`), which the state
//! vector's activity one-hot does not carry. The engine snapshot does.
//!
//! Measurement conventions, stated once:
//! - The census reads the snapshot *after* each driven tick. The engine's
//!   grant check (`is_available_friend`) runs intra-tick, so a run edge can
//!   differ from the paid sequence by one tick. A census of durations does
//!   not care; a ledger of paid relief would.
//! - "Serviced" = the named companion is adjacent (Manhattan ≤ 1, the same
//!   `Position::is_adjacent` the engine uses).
//! - "Mutual" = on a serviced tick the companion is itself Sleeping or
//!   Resting — option C's tier, measured before it exists.
//! - An episode is a maximal run of ticks in the same activity with the same
//!   partner; episodes still open at the horizon are flushed and flagged
//!   `truncated` (they are length-biased low, not discarded).

use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::meow::{freshest_audible, MessageKind};
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::{
    Activity, BehaviorRegistry, Config, ElementType, KittyId, Position, World, WorldSnapshot,
};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::reward::team_reward;
use serde::Serialize;

const ACTIVITIES: [&str; 7] = [
    "Idle", "Resting", "Sleeping", "Eating", "Drinking", "Playing", "Grooming",
];

fn activity_index(a: &Activity) -> usize {
    match a {
        Activity::Idle => 0,
        Activity::Resting { .. } => 1,
        Activity::Sleeping { .. } => 2,
        Activity::Eating => 3,
        Activity::Drinking => 4,
        Activity::Playing { .. } => 5,
        Activity::Grooming { .. } => 6,
    }
}

/// The cuddle thresholds worth counting time above: the scripted ladder's
/// attention line (`worth_a_detour` 30), the meow urgency line (75), and
/// the distress line (90). Read from config where a dial exists; the fixed
/// list is the *reporting* choice, not an engine claim.
const CUDDLE_MARKS: [f32; 3] = [30.0, 75.0, 90.0];

#[derive(Serialize, Clone)]
struct CosleepEpisode {
    partner: KittyId,
    len: u64,
    serviced: u64,
    /// Maximal runs of consecutive serviced ticks — the pilot's
    /// "contact duration" is the mean over these.
    contact_runs: Vec<u64>,
    /// The companion walked away and the sleeper slept on: the episode had
    /// contact and its final tick did not.
    partner_left: bool,
    truncated: bool,
}

#[derive(Serialize, Default, Clone)]
struct KittyCensus {
    activity_ticks: [u64; 7],
    on_water_by_activity: [u64; 7],
    sleep_solo_sunbeam: u64,
    sleep_solo_plain: u64,
    sleep_with_friend: u64,
    cosleep_serviced: u64,
    cosleep_unserviced: u64,
    /// The named companion's activity on serviced ticks.
    partner_activity_on_serviced: [u64; 7],
    rest_duet_ticks: u64,
    groom_actor_ticks: u64,
    /// Co-sleep ticks by named partner (partner-selection symmetry check).
    cosleep_ticks_by_partner: BTreeMap<KittyId, u64>,
    cuddle_sum: f64,
    cuddle_above: [u64; CUDDLE_MARKS.len()],
    cuddle_at_floor: u64,
    happiness_sum: f64,
    cosleep_episodes: Vec<CosleepEpisode>,
    solo_sleep_lens: Vec<u64>,
    rest_duet_lens: Vec<u64>,
    /// Meow emissions by wire name (spec 028; the §2 rate anchors).
    meow_emits: BTreeMap<String, u64>,
    /// Ticks with any need at or above the distress line (the re-baseline's
    /// distress-tick anchor, same definition as the landed counter).
    distress_ticks: u64,
}

/// FR-019 herding, the three REPORTED metrics registered in PR #160, plus
/// the raw counts they derive from. One WantBath "episode" per emitter =
/// the maximal window in which that emitter's ask stays audible, plus one
/// recent-window of grace for late arrivals.
#[derive(Serialize, Clone, Default)]
struct HerdingAgg {
    episodes: u64,
    /// Distinct groomers of the emitter, one entry per closed episode.
    responders_per_episode: Vec<u64>,
    groom_ticks_on_emitter: u64,
    /// Groom ticks landing after the emitter's bath fell below the
    /// announce floor (threshold - hysteresis). NOTE: groom_relief cleans
    /// a just-legal emitter below the floor in one tick, so most ticks of
    /// any groom run land "clean" — this is a relief-overpay diagnostic,
    /// not the herding metric. The registered redundant-groom share is
    /// START-conditioned, below.
    redundant_groom_ticks: u64,
    /// Groom runs begun on this episode's emitter (initiation-conditioned:
    /// a run starts when an actor transitions into grooming the emitter).
    groom_starts: u64,
    /// Groom runs begun when the emitter was ALREADY below the announce
    /// floor — the registered "late arrival grooms a clean cat" share.
    redundant_groom_starts: u64,
    /// A pursuit = a gate-eligible cat closing distance on its freshest
    /// audible WantBath emitter for >= 2 consecutive ticks (the engine's
    /// own `freshest_audible` selection rule picks the target).
    pursuits: u64,
    /// Pursuits that never landed a groom before the episode closed.
    abandoned_pursuits: u64,
}

#[derive(Default)]
struct Pursuit {
    closing: u8,
    pursuing: bool,
    groomed: bool,
    grooming_now: bool,
    prev_dist: Option<u32>,
}

#[derive(Default)]
struct BathEpisode {
    last_audible: u64,
    responders: std::collections::BTreeSet<KittyId>,
    groom_ticks: u64,
    redundant_groom_ticks: u64,
    groom_starts: u64,
    redundant_groom_starts: u64,
    pursuits: BTreeMap<KittyId, Pursuit>,
}

/// The in-progress episode for one kitty; closed when the (class, partner)
/// signature changes.
enum OpenEpisode {
    None,
    SoloSleep {
        len: u64,
    },
    Cosleep {
        partner: KittyId,
        len: u64,
        serviced: u64,
        run: u64,
        runs: Vec<u64>,
        last_serviced: bool,
    },
    RestDuet {
        partner: KittyId,
        len: u64,
    },
    Other,
}

/// Deliberate-purr probe (owner's question, 2026-08-10): is the message-head
/// Purr socially conditioned or a fires-whenever-legal reflex? Emission is
/// judged against DECISION-TIME state — the previous observed tick — per the
/// house prev-state rule (observe() sees the post-tick world).
#[derive(Default)]
struct PurrProbe {
    /// Post-previous-tick (pos, purr_earned, cooldown ready_at) per kitty.
    prev: BTreeMap<KittyId, (Position, bool, u64)>,
    tick_hist: Vec<u64>,
    pos_hist: Vec<BTreeMap<KittyId, Position>>,
    purr_hist: Vec<std::collections::BTreeSet<KittyId>>,
    legal_company: u64,
    legal_alone: u64,
    emit_company: u64,
    emit_alone: u64,
    /// Emissions our legality reconstruction calls illegal — stays 0 unless
    /// the reconstruction drifts from engine law.
    emit_offwindow: u64,
    emit_by_activity: BTreeMap<String, u64>,
    emit_while_cosleep: u64,
}

#[derive(Default)]
struct PairAgg {
    n: u64,
    adj: u64,
    step: i64,
    speaker_step: i64,
    dist: u64,
}

impl PairAgg {
    fn report(&self) -> serde_json::Value {
        serde_json::json!({
            "n": self.n,
            "p_adjacent_within_window": self.adj as f64 / self.n.max(1) as f64,
            "mean_hearer_step_toward_speaker": -(self.step as f64) / self.n.max(1) as f64,
            "mean_speaker_step_toward_hearer":
                -(self.speaker_step as f64) / self.n.max(1) as f64,
            "mean_distance": self.dist as f64 / self.n.max(1) as f64,
        })
    }
}

struct SeedCensus {
    ids: Vec<KittyId>,
    names: BTreeMap<KittyId, String>,
    kitties: BTreeMap<KittyId, KittyCensus>,
    open: BTreeMap<KittyId, OpenEpisode>,
    team_reward_sum: f64,
    water_tiles_sum: u64,
    ticks_seen: u64,
    seen_meows: std::collections::BTreeSet<(KittyId, &'static str, u64)>,
    /// Bath values from the PREVIOUS observed tick: observe() sees the
    /// post-tick world, so this tick's groom relief is already applied —
    /// redundancy must be judged against the bath the groom actually found.
    prev_bath: BTreeMap<KittyId, f32>,
    bath_eps: BTreeMap<KittyId, BathEpisode>,
    herding: HerdingAgg,
    responder_gate: f32,
    announce_floor: f32,
    meow_window: u64,
    distress_line: f32,
    purr_threshold: f32,
    purr: PurrProbe,
    /// When set, every observed tick appends one JSONL row of kitty state +
    /// purr flags (see `--purr-log`).
    purr_log: Option<std::io::BufWriter<fs::File>>,
}

impl SeedCensus {
    fn new(snap: &WorldSnapshot, config: &Config) -> Self {
        let ids: Vec<KittyId> = snap.kitties.iter().map(|k| k.id).collect();
        SeedCensus {
            names: snap
                .kitties
                .iter()
                .map(|k| (k.id, k.name.clone()))
                .collect(),
            kitties: ids.iter().map(|id| (*id, KittyCensus::default())).collect(),
            open: ids.iter().map(|id| (*id, OpenEpisode::None)).collect(),
            ids,
            team_reward_sum: 0.0,
            water_tiles_sum: 0,
            ticks_seen: 0,
            seen_meows: Default::default(),
            prev_bath: BTreeMap::new(),
            bath_eps: BTreeMap::new(),
            herding: HerdingAgg::default(),
            responder_gate: config.behavior.cuddle_real_threshold,
            announce_floor: config.meow.announce_threshold - config.meow.announce_hysteresis,
            meow_window: config.meow.recent_window_ticks,
            distress_line: config.thresholds.distress,
            purr_threshold: config.thresholds.purr,
            purr: PurrProbe::default(),
            purr_log: None,
        }
    }

    /// The deliberate-purr verdict data: the emission 2×2 plus the listener
    /// scan — for every ordered (speaker, hearer) pair and every non-adjacent
    /// tick, did a fresh audible purr from the speaker precede the hearer
    /// stepping toward them / the pair meeting within one audibility window?
    /// Windows overlap tick-to-tick, so n inflates ~window-fold — rates are
    /// comparable between the exposed and control rows, not absolute counts.
    fn purr_report(&self) -> serde_json::Value {
        let p = &self.purr;
        let window = self.meow_window.max(1);
        let t = p.tick_hist.len();
        // Distance-stratified: exposure correlates with pair distance, and
        // approach-step size scales with it — compare like with like.
        let bin = |d: i64| -> &'static str {
            match d {
                ..=3 => "d2-3",
                4..=6 => "d4-6",
                7..=10 => "d7-10",
                _ => "d11+",
            }
        };
        let mut exposed: BTreeMap<&'static str, PairAgg> = BTreeMap::new();
        let mut control: BTreeMap<&'static str, PairAgg> = BTreeMap::new();
        for a in &self.ids {
            for b in &self.ids {
                if a == b {
                    continue;
                }
                for i in 0..t.saturating_sub(1) {
                    let pa = p.pos_hist[i][a];
                    let pb = p.pos_hist[i][b];
                    if pa.is_adjacent(&pb) {
                        continue;
                    }
                    let tick_i = p.tick_hist[i];
                    let heard = (0..=i)
                        .rev()
                        .take_while(|&j| p.tick_hist[j] + window > tick_i)
                        .any(|j| p.purr_hist[j].contains(a));
                    let mut adj = false;
                    let mut k = i + 1;
                    while k < t && p.tick_hist[k] <= tick_i + window {
                        if p.pos_hist[k][a].is_adjacent(&p.pos_hist[k][b]) {
                            adj = true;
                            break;
                        }
                        k += 1;
                    }
                    let d0 = pb.manhattan_distance(&pa) as i64;
                    let d1 = p.pos_hist[i + 1][b].manhattan_distance(&pa) as i64;
                    let sd1 = p.pos_hist[i + 1][a].manhattan_distance(&pb) as i64;
                    let side = if heard { &mut exposed } else { &mut control };
                    let agg = side.entry(bin(d0)).or_default();
                    agg.n += 1;
                    agg.adj += adj as u64;
                    agg.step += d1 - d0;
                    agg.speaker_step += sd1 - d0;
                    agg.dist += d0 as u64;
                }
            }
        }
        serde_json::json!({
            "emission": {
                "legal_company": p.legal_company,
                "legal_alone": p.legal_alone,
                "emit_company": p.emit_company,
                "emit_alone": p.emit_alone,
                "emit_offwindow": p.emit_offwindow,
                "p_emit_given_legal_company":
                    p.emit_company as f64 / p.legal_company.max(1) as f64,
                "p_emit_given_legal_alone":
                    p.emit_alone as f64 / p.legal_alone.max(1) as f64,
                "by_activity": p.emit_by_activity,
                "while_cosleep": p.emit_while_cosleep,
            },
            "listener": {
                "window": window,
                "purr_heard": exposed.iter()
                    .map(|(k, v)| (k.to_string(), v.report()))
                    .collect::<BTreeMap<String, serde_json::Value>>(),
                "control": control.iter()
                    .map(|(k, v)| (k.to_string(), v.report()))
                    .collect::<BTreeMap<String, serde_json::Value>>(),
            },
        })
    }

    fn close_bath_episode(&mut self, emitter: KittyId) {
        let ep = self.bath_eps.remove(&emitter).unwrap();
        self.herding
            .responders_per_episode
            .push(ep.responders.len() as u64);
        self.herding.groom_ticks_on_emitter += ep.groom_ticks;
        self.herding.redundant_groom_ticks += ep.redundant_groom_ticks;
        self.herding.groom_starts += ep.groom_starts;
        self.herding.redundant_groom_starts += ep.redundant_groom_starts;
        let live = ep.pursuits.values().filter(|p| p.pursuing);
        self.herding.pursuits += live.clone().count() as u64;
        self.herding.abandoned_pursuits += live.filter(|p| !p.groomed).count() as u64;
    }

    fn close(&mut self, id: KittyId, truncated: bool) {
        let ep = std::mem::replace(self.open.get_mut(&id).unwrap(), OpenEpisode::None);
        let c = self.kitties.get_mut(&id).unwrap();
        match ep {
            OpenEpisode::None | OpenEpisode::Other => {}
            OpenEpisode::SoloSleep { len } => c.solo_sleep_lens.push(len),
            OpenEpisode::RestDuet { len, .. } => c.rest_duet_lens.push(len),
            OpenEpisode::Cosleep {
                partner,
                len,
                serviced,
                run,
                mut runs,
                last_serviced,
            } => {
                if run > 0 {
                    runs.push(run);
                }
                c.cosleep_episodes.push(CosleepEpisode {
                    partner,
                    len,
                    serviced,
                    contact_runs: runs,
                    partner_left: serviced > 0 && !last_serviced,
                    truncated,
                });
            }
        }
    }

    fn observe(&mut self, snap: &WorldSnapshot) {
        self.ticks_seen += 1;
        let water: Vec<_> = snap
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Water)
            .map(|e| e.pos)
            .collect();
        self.water_tiles_sum += water.len() as u64;

        let by_id: BTreeMap<KittyId, &cloudkitty_core::Kitty> =
            snap.kitties.iter().map(|k| (k.id, k)).collect();

        for id in &self.ids.clone() {
            let me = by_id[id];
            let act = activity_index(&me.activity);
            let c = self.kitties.get_mut(id).unwrap();
            c.activity_ticks[act] += 1;
            if water.contains(&me.pos) {
                c.on_water_by_activity[act] += 1;
            }
            let (_, top_need) = me.needs.highest_pressure();
            if top_need >= self.distress_line {
                c.distress_ticks += 1;
            }
            let cuddle = me.needs.cuddle.value();
            c.cuddle_sum += f64::from(cuddle);
            for (i, mark) in CUDDLE_MARKS.iter().enumerate() {
                if cuddle >= *mark {
                    c.cuddle_above[i] += 1;
                }
            }
            if cuddle <= 0.0 {
                c.cuddle_at_floor += 1;
            }
            c.happiness_sum += f64::from(me.happiness);

            // Tick tallies + episode advance, by activity shape.
            match &me.activity {
                Activity::Sleeping {
                    in_sunbeam,
                    with_friend: None,
                } => {
                    if *in_sunbeam {
                        c.sleep_solo_sunbeam += 1;
                    } else {
                        c.sleep_solo_plain += 1;
                    }
                    match self.open.get_mut(id).unwrap() {
                        OpenEpisode::SoloSleep { len } => *len += 1,
                        _ => {
                            self.close(*id, false);
                            *self.open.get_mut(id).unwrap() = OpenEpisode::SoloSleep { len: 1 };
                        }
                    }
                }
                Activity::Sleeping {
                    with_friend: Some(p),
                    ..
                } => {
                    let partner = *p;
                    let serviced = by_id
                        .get(&partner)
                        .is_some_and(|k| me.pos.is_adjacent(&k.pos));
                    let c = self.kitties.get_mut(id).unwrap();
                    c.sleep_with_friend += 1;
                    *c.cosleep_ticks_by_partner.entry(partner).or_default() += 1;
                    if serviced {
                        c.cosleep_serviced += 1;
                        c.partner_activity_on_serviced
                            [activity_index(&by_id[&partner].activity)] += 1;
                    } else {
                        c.cosleep_unserviced += 1;
                    }
                    match self.open.get_mut(id).unwrap() {
                        OpenEpisode::Cosleep {
                            partner: cur,
                            len,
                            serviced: s,
                            run,
                            runs,
                            last_serviced,
                        } if *cur == partner => {
                            *len += 1;
                            if serviced {
                                *s += 1;
                                *run += 1;
                            } else if *run > 0 {
                                runs.push(*run);
                                *run = 0;
                            }
                            *last_serviced = serviced;
                        }
                        _ => {
                            self.close(*id, false);
                            *self.open.get_mut(id).unwrap() = OpenEpisode::Cosleep {
                                partner,
                                len: 1,
                                serviced: u64::from(serviced),
                                run: u64::from(serviced),
                                runs: Vec::new(),
                                last_serviced: serviced,
                            };
                        }
                    }
                }
                Activity::Resting {
                    with_friend: Some(p),
                } => {
                    let partner = *p;
                    self.kitties.get_mut(id).unwrap().rest_duet_ticks += 1;
                    match self.open.get_mut(id).unwrap() {
                        OpenEpisode::RestDuet { partner: cur, len } if *cur == partner => *len += 1,
                        _ => {
                            self.close(*id, false);
                            *self.open.get_mut(id).unwrap() =
                                OpenEpisode::RestDuet { partner, len: 1 };
                        }
                    }
                }
                other => {
                    if let Activity::Grooming { target: Some(_) } = other {
                        self.kitties.get_mut(id).unwrap().groom_actor_ticks += 1;
                    }
                    let open = self.open.get_mut(id).unwrap();
                    if !matches!(open, OpenEpisode::None | OpenEpisode::Other) {
                        self.close(*id, false);
                    }
                    *self.open.get_mut(id).unwrap() = OpenEpisode::Other;
                }
            }
        }

        // -- Meow emissions by kind (each meow counted once, on first sight).
        for m in &snap.recent_meows {
            if self.seen_meows.insert((m.kitty_id, m.kind.wire_name(), m.tick)) {
                if let Some(c) = self.kitties.get_mut(&m.kitty_id) {
                    *c.meow_emits.entry(m.kind.wire_name().to_string()).or_default() += 1;
                }
            }
        }
        let horizon = snap.tick.saturating_sub(4 * self.meow_window.max(1));
        self.seen_meows.retain(|&(_, _, t)| t >= horizon);

        // -- Deliberate-purr probe: this tick's emissions judged against the
        //    decision-time (previous observed tick) legality and company.
        //    Meows are stamped with the PRE-increment tick, one behind the
        //    post-tick snapshot's counter.
        let purred: std::collections::BTreeSet<KittyId> = snap
            .recent_meows
            .iter()
            .filter(|m| m.kind == MessageKind::Purr && m.tick + 1 == snap.tick)
            .map(|m| m.kitty_id)
            .collect();
        if !self.purr.prev.is_empty() {
            let decision_tick = *self.purr.tick_hist.last().unwrap();
            let mut log_rows: Vec<serde_json::Value> = Vec::new();
            for id in &self.ids {
                let (pos, earned, ready_at) = self.purr.prev[id];
                let legal = earned && ready_at <= decision_tick;
                let company = self
                    .purr
                    .prev
                    .iter()
                    .any(|(o, (op, _, _))| o != id && pos.is_adjacent(op));
                let spoke = purred.contains(id);
                if legal {
                    if company {
                        self.purr.legal_company += 1;
                    } else {
                        self.purr.legal_alone += 1;
                    }
                    if spoke {
                        if company {
                            self.purr.emit_company += 1;
                        } else {
                            self.purr.emit_alone += 1;
                        }
                    }
                } else if spoke {
                    self.purr.emit_offwindow += 1;
                }
                if spoke {
                    let act = ACTIVITIES[activity_index(&by_id[id].activity)];
                    *self.purr.emit_by_activity.entry(act.to_string()).or_default() += 1;
                    if matches!(
                        by_id[id].activity,
                        Activity::Sleeping { with_friend: Some(_), .. }
                    ) {
                        self.purr.emit_while_cosleep += 1;
                    }
                }
                if self.purr_log.is_some() {
                    let k = by_id[id];
                    let cosleep = matches!(
                        k.activity,
                        Activity::Sleeping { with_friend: Some(_), .. }
                    );
                    log_rows.push(serde_json::json!([
                        id, k.pos.x, k.pos.y, k.happiness,
                        cloudkitty_core::NeedKind::ALL
                            .map(|n| k.needs.get(n)),
                        activity_index(&k.activity),
                        cosleep as u8, spoke as u8, legal as u8,
                    ]));
                }
            }
            if let Some(w) = &mut self.purr_log {
                use std::io::Write;
                writeln!(
                    w,
                    "{}",
                    serde_json::json!({"t": snap.tick, "k": log_rows})
                )
                .expect("purr-log write");
            }
        }
        self.purr.tick_hist.push(snap.tick);
        self.purr
            .pos_hist
            .push(by_id.iter().map(|(id, k)| (*id, k.pos)).collect());
        self.purr.purr_hist.push(purred);
        self.purr.prev = by_id
            .iter()
            .map(|(id, k)| {
                (
                    *id,
                    (
                        k.pos,
                        k.happiness > self.purr_threshold || k.happiness_rose,
                        k.meow_cooldowns
                            .get(&MessageKind::Purr)
                            .copied()
                            .unwrap_or(0),
                    ),
                )
            })
            .collect();

        // -- FR-019 herding (PR #160): open/refresh WantBath episodes.
        for m in &snap.recent_meows {
            if m.kind != MessageKind::WantBath {
                continue;
            }
            if !self.bath_eps.contains_key(&m.kitty_id) {
                self.herding.episodes += 1;
                self.bath_eps.insert(m.kitty_id, BathEpisode::default());
            }
            let ep = self.bath_eps.get_mut(&m.kitty_id).unwrap();
            ep.last_audible = ep.last_audible.max(m.tick);
        }

        let mut grooming_pairs: std::collections::BTreeSet<(KittyId, KittyId)> = Default::default();
        for k in &snap.kitties {
            // Grooms landing on an emitter, attributed by actual target.
            if let Activity::Grooming { target: Some(t) } = k.activity {
                let clean = self
                    .prev_bath
                    .get(&t)
                    .is_some_and(|&b| b < self.announce_floor);
                if let Some(ep) = self.bath_eps.get_mut(&t) {
                    grooming_pairs.insert((t, k.id));
                    ep.groom_ticks += 1;
                    ep.responders.insert(k.id);
                    if clean {
                        ep.redundant_groom_ticks += 1;
                    }
                    let p = ep.pursuits.entry(k.id).or_default();
                    if !p.grooming_now {
                        ep.groom_starts += 1;
                        if clean {
                            ep.redundant_groom_starts += 1;
                        }
                    }
                    p.grooming_now = true;
                    p.pursuing = true;
                    p.groomed = true;
                }
            }
            // Pursuit: a gate-eligible cat closing on ITS freshest audible
            // emitter -- the engine's own selection rule picks the target.
            if k.needs.cuddle.value() >= self.responder_gate {
                if let Some(m) = freshest_audible(&snap.recent_meows, MessageKind::WantBath, k.id)
                {
                    let emitter_pos = by_id.get(&m.kitty_id).map(|e| e.pos);
                    if let (Some(ep), Some(pos)) = (self.bath_eps.get_mut(&m.kitty_id), emitter_pos)
                    {
                        let d = k.pos.manhattan_distance(&pos);
                        let p = ep.pursuits.entry(k.id).or_default();
                        if let Some(pd) = p.prev_dist {
                            if d < pd {
                                p.closing += 1;
                                if p.closing >= 2 {
                                    p.pursuing = true;
                                }
                            } else {
                                p.closing = 0;
                            }
                        }
                        p.prev_dist = Some(d);
                    }
                }
            }
        }

        for k in &snap.kitties {
            self.prev_bath.insert(k.id, k.needs.bath.value());
        }

        // A groom run ends the tick its actor stops grooming that emitter.
        for (&e, ep) in self.bath_eps.iter_mut() {
            for (&a, p) in ep.pursuits.iter_mut() {
                if p.grooming_now && !grooming_pairs.contains(&(e, a)) {
                    p.grooming_now = false;
                }
            }
        }

        // Close episodes one recent-window after the last audible ask.
        let stale: Vec<KittyId> = self
            .bath_eps
            .iter()
            .filter(|(_, ep)| snap.tick > ep.last_audible + self.meow_window)
            .map(|(&e, _)| e)
            .collect();
        for e in stale {
            self.close_bath_episode(e);
        }
    }

    fn finish(&mut self) {
        for id in self.ids.clone() {
            self.close(id, true);
        }
        let open: Vec<KittyId> = self.bath_eps.keys().copied().collect();
        for e in open {
            self.close_bath_episode(e);
        }
    }
}

#[derive(Serialize)]
struct SeedRecord {
    seed: u64,
    ticks: u64,
    config: String,
    seat_overrides: BTreeMap<String, String>,
    mean_water_tiles: f64,
    mean_team_reward: f64,
    kitties: BTreeMap<String, KittyCensus>,
    herding: HerdingAgg,
    purr_context: serde_json::Value,
}

struct Args {
    config: PathBuf,
    seeds: Vec<u64>,
    ticks: u64,
    out: PathBuf,
    /// `kitty_<id>=<behavior>` overrides applied to the config roster before
    /// generation — how the policy seats are handed back to a scripted
    /// ladder for a B-geometry run.
    seats: BTreeMap<u32, String>,
    /// Optional .ckpolicy path; registered as "policy:subject".
    artifact: Option<String>,
    /// Optional dir for a per-tick JSONL of kitty state + purr events
    /// (`seed-<n>.jsonl`), for offline purr-semantics analysis.
    purr_log: Option<PathBuf>,
}

fn parse_args() -> Args {
    let mut args = Args {
        config: PathBuf::from("cloudkitty.toml"),
        seeds: (1..=10).collect(),
        ticks: 20_000,
        out: PathBuf::from("contact-census-out"),
        seats: BTreeMap::new(),
        artifact: None,
        purr_log: None,
    };
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--config" => args.config = PathBuf::from(value("--config")),
            "--seeds" => {
                args.seeds = value("--seeds")
                    .split(',')
                    .map(|s| s.trim().parse().expect("--seeds: u64 list"))
                    .collect()
            }
            "--ticks" => args.ticks = value("--ticks").parse().expect("--ticks: u64"),
            "--out" => args.out = PathBuf::from(value("--out")),
            "--artifact" => args.artifact = Some(value("--artifact")),
            "--purr-log" => args.purr_log = Some(PathBuf::from(value("--purr-log"))),
            "--seat" => {
                for pair in value("--seat").split(',') {
                    let (seat, behavior) = pair
                        .split_once('=')
                        .expect("--seat: kitty_<id>=<behavior> pairs");
                    let id: u32 = seat
                        .trim()
                        .strip_prefix("kitty_")
                        .expect("--seat keys look like kitty_<id>")
                        .parse()
                        .expect("--seat: numeric kitty id");
                    args.seats.insert(id, behavior.trim().to_string());
                }
            }
            other => panic!("unknown flag {other}"),
        }
    }
    assert!(!args.seeds.is_empty(), "--seeds must name at least one seed");
    args
}

fn quantiles(mut v: Vec<u64>) -> serde_json::Value {
    if v.is_empty() {
        return serde_json::json!({ "n": 0 });
    }
    v.sort_unstable();
    let n = v.len();
    let mean = v.iter().sum::<u64>() as f64 / n as f64;
    let at = |q: f64| v[((n - 1) as f64 * q).round() as usize];
    serde_json::json!({
        "n": n,
        "mean": mean,
        "median": at(0.5),
        "p90": at(0.9),
        "max": v[n - 1],
    })
}

fn main() {
    let args = parse_args();
    let text = fs::read_to_string(&args.config)
        .unwrap_or_else(|e| panic!("reading {}: {e}", args.config.display()));
    let mut base_cfg: Config = toml::from_str(&text).expect("config parses as engine TOML");
    let rl = RlConfig::from_toml_str(&text).expect("[rl] blocks parse and validate");

    for (id, behavior) in &args.seats {
        let kitty = base_cfg
            .kitties
            .iter_mut()
            .find(|k| k.id == *id)
            .unwrap_or_else(|| panic!("--seat kitty_{id}: no such kitty in the config"));
        kitty.behavior = behavior.clone();
    }
    // Behavior-driven worlds run built-in ladders — or, since exp-004's
    // certification battery, a policy artifact registered explicitly
    // (--artifact PATH registers it as "policy:subject"; seat it with
    // --seat kitty_N=policy:subject). Any other unresolvable behavior
    // still fails loudly, not per-tick.
    let mut registry = BehaviorRegistry::with_builtins();
    if let Some(artifact) = &args.artifact {
        let rl_full = cloudkitty_rl::config::RlConfig::from_toml_str(&text)
            .expect("[rl] blocks parse");
        let behavior = cloudkitty_rl::behavior::PolicyBehavior::from_artifact_path(
            artifact, &rl_full, false)
            .unwrap_or_else(|e| panic!("loading {artifact}: {e:?}"));
        registry.register("policy:subject", std::sync::Arc::new(behavior));
    }
    for k in &base_cfg.kitties {
        assert!(
            k.behavior == "needs_driven"
                || k.behavior == "playful"
                || (args.artifact.is_some() && k.behavior == "policy:subject"),
            "kitty_{} runs {:?}; hand policy seats to a scripted ladder or \
             register an artifact and seat --seat kitty_{}=policy:subject",
            k.id,
            k.behavior,
            k.id
        );
    }
    base_cfg
        .validate()
        .expect("config passes engine validation");
    let seat_overrides: BTreeMap<String, String> = args
        .seats
        .iter()
        .map(|(id, b)| (format!("kitty_{id}"), b.clone()))
        .collect();

    fs::create_dir_all(&args.out).expect("creating output directory");

    let mut records: Vec<SeedRecord> = Vec::new();
    for &seed in &args.seeds {
        let mut cfg = base_cfg.clone();
        cfg.world.seed = seed;
        let config = Arc::new(cfg);
        let mut world = World::generate(&config);
        let mut census = SeedCensus::new(&world.snapshot(), &config);
        if let Some(dir) = &args.purr_log {
            fs::create_dir_all(dir).expect("creating purr-log directory");
            census.purr_log = Some(std::io::BufWriter::new(
                fs::File::create(dir.join(format!("seed-{seed}.jsonl")))
                    .expect("creating purr-log file"),
            ));
        }
        for _ in 0..args.ticks {
            let _ = drive_tick(&mut world, &registry, &config);
            let snap = world.snapshot();
            census.team_reward_sum += team_reward(&snap, &config, &rl.reward);
            census.observe(&snap);
        }
        census.finish();

        let record = SeedRecord {
            seed,
            ticks: args.ticks,
            config: args.config.display().to_string(),
            seat_overrides: seat_overrides.clone(),
            mean_water_tiles: census.water_tiles_sum as f64 / args.ticks as f64,
            mean_team_reward: census.team_reward_sum / args.ticks as f64,
            kitties: census
                .kitties
                .iter()
                .map(|(id, c)| (census.names[id].clone(), c.clone()))
                .collect(),
            herding: census.herding.clone(),
            purr_context: census.purr_report(),
        };
        fs::write(
            args.out.join(format!("seed-{seed}.json")),
            serde_json::to_string_pretty(&record).expect("seed record serializes") + "\n",
        )
        .expect("writing seed record");
        let slept: u64 = record
            .kitties
            .values()
            .map(|c| c.activity_ticks[2])
            .sum();
        let with: u64 = record.kitties.values().map(|c| c.sleep_with_friend).sum();
        println!(
            "seed {seed}: {slept} sleep ticks, {with} co-sleep ({:.1}%)",
            100.0 * with as f64 / slept.max(1) as f64
        );
        records.push(record);
    }

    // ---- verdict: aggregate over seeds, per kitty and overall ----
    let names: Vec<String> = records[0].kitties.keys().cloned().collect();
    let id_names: BTreeMap<String, String> = {
        // Partner ids in episode records → names, via the config roster.
        base_cfg
            .kitties
            .iter()
            .map(|k| (k.id.to_string(), k.name.clone()))
            .collect()
    };

    let mut verdict = serde_json::Map::new();
    verdict.insert("config".into(), args.config.display().to_string().into());
    verdict.insert(
        "seat_overrides".into(),
        serde_json::to_value(&seat_overrides).unwrap(),
    );
    verdict.insert(
        "seeds".into(),
        serde_json::to_value(&args.seeds).unwrap(),
    );
    verdict.insert("ticks".into(), args.ticks.into());
    verdict.insert(
        "mean_team_reward".into(),
        (records.iter().map(|r| r.mean_team_reward).sum::<f64>() / records.len() as f64).into(),
    );
    verdict.insert(
        "mean_water_tiles".into(),
        (records.iter().map(|r| r.mean_water_tiles).sum::<f64>() / records.len() as f64).into(),
    );

    let total_ticks = args.ticks * records.len() as u64;
    let mut per_kitty = serde_json::Map::new();
    let mut all = KittyCensus::default();
    for name in &names {
        let mut agg = KittyCensus::default();
        for r in &records {
            let c = &r.kitties[name];
            for i in 0..7 {
                agg.activity_ticks[i] += c.activity_ticks[i];
                agg.on_water_by_activity[i] += c.on_water_by_activity[i];
                agg.partner_activity_on_serviced[i] += c.partner_activity_on_serviced[i];
            }
            agg.sleep_solo_sunbeam += c.sleep_solo_sunbeam;
            agg.sleep_solo_plain += c.sleep_solo_plain;
            agg.sleep_with_friend += c.sleep_with_friend;
            agg.cosleep_serviced += c.cosleep_serviced;
            agg.cosleep_unserviced += c.cosleep_unserviced;
            agg.rest_duet_ticks += c.rest_duet_ticks;
            agg.groom_actor_ticks += c.groom_actor_ticks;
            for (p, n) in &c.cosleep_ticks_by_partner {
                *agg.cosleep_ticks_by_partner.entry(*p).or_default() += n;
            }
            agg.cuddle_sum += c.cuddle_sum;
            for i in 0..CUDDLE_MARKS.len() {
                agg.cuddle_above[i] += c.cuddle_above[i];
            }
            agg.cuddle_at_floor += c.cuddle_at_floor;
            agg.happiness_sum += c.happiness_sum;
            agg.cosleep_episodes.extend(c.cosleep_episodes.iter().cloned());
            agg.solo_sleep_lens.extend(&c.solo_sleep_lens);
            agg.rest_duet_lens.extend(&c.rest_duet_lens);
        }
        let summary = summarize(&agg, total_ticks, &id_names);
        // Roll into the all-kitties aggregate before moving on.
        for i in 0..7 {
            all.activity_ticks[i] += agg.activity_ticks[i];
            all.on_water_by_activity[i] += agg.on_water_by_activity[i];
            all.partner_activity_on_serviced[i] += agg.partner_activity_on_serviced[i];
        }
        all.sleep_solo_sunbeam += agg.sleep_solo_sunbeam;
        all.sleep_solo_plain += agg.sleep_solo_plain;
        all.sleep_with_friend += agg.sleep_with_friend;
        all.cosleep_serviced += agg.cosleep_serviced;
        all.cosleep_unserviced += agg.cosleep_unserviced;
        all.rest_duet_ticks += agg.rest_duet_ticks;
        all.groom_actor_ticks += agg.groom_actor_ticks;
        for (p, n) in &agg.cosleep_ticks_by_partner {
            *all.cosleep_ticks_by_partner.entry(*p).or_default() += n;
        }
        all.cuddle_sum += agg.cuddle_sum;
        for i in 0..CUDDLE_MARKS.len() {
            all.cuddle_above[i] += agg.cuddle_above[i];
        }
        all.cuddle_at_floor += agg.cuddle_at_floor;
        all.happiness_sum += agg.happiness_sum;
        all.cosleep_episodes.extend(agg.cosleep_episodes.iter().cloned());
        all.solo_sleep_lens.extend(&agg.solo_sleep_lens);
        all.rest_duet_lens.extend(&agg.rest_duet_lens);
        per_kitty.insert(name.clone(), summary);
    }
    verdict.insert("per_kitty".into(), per_kitty.into());
    verdict.insert(
        "all_kitties".into(),
        summarize(&all, total_ticks * names.len() as u64, &id_names),
    );

    fs::write(
        args.out.join("verdict.json"),
        serde_json::to_string_pretty(&serde_json::Value::Object(verdict.clone())).unwrap() + "\n",
    )
    .expect("writing verdict");
    println!(
        "\n{}",
        serde_json::to_string_pretty(&verdict["all_kitties"]).unwrap()
    );
    println!("\nwrote {}", args.out.display());
}

/// Shares and episode statistics for one aggregated census. `ticks` is the
/// kitty-tick denominator the shares are over.
fn summarize(
    c: &KittyCensus,
    ticks: u64,
    id_names: &BTreeMap<String, String>,
) -> serde_json::Value {
    let sleep_ticks = c.activity_ticks[2].max(1);
    let contact_runs: Vec<u64> = c
        .cosleep_episodes
        .iter()
        .flat_map(|e| e.contact_runs.iter().copied())
        .collect();
    let cosleep_lens: Vec<u64> = c.cosleep_episodes.iter().map(|e| e.len).collect();
    let fully_serviced = c
        .cosleep_episodes
        .iter()
        .filter(|e| e.serviced == e.len)
        .count();
    let partner_left = c.cosleep_episodes.iter().filter(|e| e.partner_left).count();
    let never_serviced = c
        .cosleep_episodes
        .iter()
        .filter(|e| e.serviced == 0)
        .count();
    let serviced_ticks = c.cosleep_serviced.max(1);
    let t = ticks.max(1) as f64;
    serde_json::json!({
        "activity_share": ACTIVITIES.iter().zip(c.activity_ticks)
            .map(|(a, n)| (a.to_string(), n as f64 / t))
            .collect::<BTreeMap<_, _>>(),
        "sleep": {
            "ticks": c.activity_ticks[2],
            "solo_sunbeam_share": c.sleep_solo_sunbeam as f64 / sleep_ticks as f64,
            "solo_plain_share": c.sleep_solo_plain as f64 / sleep_ticks as f64,
            "cosleep_share": c.sleep_with_friend as f64 / sleep_ticks as f64,
        },
        "cosleep": {
            "ticks": c.sleep_with_friend,
            "serviced_share": c.cosleep_serviced as f64
                / c.sleep_with_friend.max(1) as f64,
            "episodes": quantiles(cosleep_lens),
            "contact_runs": quantiles(contact_runs),
            "episodes_fully_serviced": fully_serviced,
            "episodes_partner_left": partner_left,
            "episodes_never_serviced": never_serviced,
            "partner_on_serviced_tick": ACTIVITIES.iter()
                .zip(c.partner_activity_on_serviced)
                .map(|(a, n)| (a.to_string(), n as f64 / serviced_ticks as f64))
                .collect::<BTreeMap<_, _>>(),
            // Option C's tier, measured before it exists: companion is
            // itself Sleeping or Resting on a serviced tick.
            "mutual_share_of_serviced": (c.partner_activity_on_serviced[1]
                + c.partner_activity_on_serviced[2]) as f64
                / serviced_ticks as f64,
            "ticks_by_partner": c.cosleep_ticks_by_partner.iter()
                .map(|(p, n)| (id_names.get(&p.to_string())
                                    .cloned()
                                    .unwrap_or_else(|| p.to_string()), *n))
                .collect::<BTreeMap<_, _>>(),
        },
        "solo_sleep_episodes": quantiles(c.solo_sleep_lens.clone()),
        "rest_duet": {
            "ticks": c.rest_duet_ticks,
            "episodes": quantiles(c.rest_duet_lens.clone()),
        },
        "groom_actor_ticks": c.groom_actor_ticks,
        "cuddle_need": {
            "mean": c.cuddle_sum / t,
            "share_above": CUDDLE_MARKS.iter().zip(c.cuddle_above)
                .map(|(m, n)| (format!("{m}"), n as f64 / t))
                .collect::<BTreeMap<_, _>>(),
            "share_at_floor": c.cuddle_at_floor as f64 / t,
        },
        "mean_happiness": c.happiness_sum / t,
        "water": {
            "inwater_share": c.on_water_by_activity.iter().sum::<u64>() as f64 / t,
            "lounge_share": (c.on_water_by_activity[1] + c.on_water_by_activity[2]
                + c.on_water_by_activity[6]) as f64 / t,
            "by_activity": ACTIVITIES.iter().zip(c.on_water_by_activity)
                .map(|(a, n)| (a.to_string(), n))
                .collect::<BTreeMap<_, _>>(),
        },
    })
}
