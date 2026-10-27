//! The needy law (spec 067, `specs/067-needy-preset/contracts/needy-law.md`):
//! the schedule a needy seat runs, the mask it carries, and the two
//! relief tables the engine's verdict reads.
//!
//! A needy seat is a SCRIPTED kitty that, on a seeded schedule, stops
//! servicing a drawn set of its needs so they climb mid-world — the
//! instrument for reading a hidden-need probe on a state with a long
//! clean history (F-069, F-070). Every draw comes from a private
//! ChaCha8 sub-stream keyed off (world seed, kitty id, fixed tag) and
//! NEVER the master world stream or another kitty's stream (FR-003); the
//! episode's STATE persists on the kitty because a level release depends
//! on the path the needs took. The mask governs only the kitty's own
//! choices — the world's supply of relief and its safeguards are
//! untouched (FR-013; design doctrine rule 12).
//!
//! Nothing here hard-codes the engine's need count (FR-016): the bitset,
//! the draws and the names all run over `NeedKind::ALL`. Any change to a
//! numbered rule of the law bumps [`NEEDY_LAW_VERSION`] and the domain tag
//! in the same commit.

use rand::{RngCore, SeedableRng};
use rand_chacha::ChaCha8Rng;
use serde::{Deserialize, Serialize};

use crate::action::{Action, TargetRef};
use crate::config::{NeedyConfig, OnsetDraw};
use crate::kitty::KittyId;
use crate::needs::{NeedKind, Needs};

/// Version of the law (needy-law.md). Bumped together with the domain
/// tag on any law change.
pub const NEEDY_LAW_VERSION: u32 = 1;

/// The sub-stream's domain separator (needy-law §2), versioned with the
/// law. Distinct from `ck-starts-v1` and `ck-initnd-v1`.
const DOMAIN_TAG: &[u8; 11] = b"ck-needy-v1";

/// The level-releasing preset's name — also its hazard-mode name (one home).
pub const NAME: &str = "needy";
/// The hold-to-the-limit preset's name — also its hazard-mode name.
pub const HOLD_NAME: &str = "needy_hold";

/// Whether a configured behaviour name seats a needy preset.
pub fn is_needy_name(name: &str) -> bool {
    name == NAME || name == HOLD_NAME
}

/// A set of needs as a bitset over `NeedKind::ALL`, serialized as the
/// sorted list of need names (keyed by name, FR-016).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Hash, Serialize, Deserialize)]
#[serde(try_from = "Vec<String>", into = "Vec<String>")]
pub struct NeedSet(u32);

impl NeedSet {
    pub const EMPTY: NeedSet = NeedSet(0);

    fn bit(kind: NeedKind) -> u32 {
        let index = NeedKind::ALL
            .iter()
            .position(|k| *k == kind)
            .expect("every NeedKind is in NeedKind::ALL");
        1 << index
    }

    pub fn from_kinds(kinds: &[NeedKind]) -> Self {
        let mut set = NeedSet::EMPTY;
        for kind in kinds {
            set.insert(*kind);
        }
        set
    }

    pub fn insert(&mut self, kind: NeedKind) {
        self.0 |= Self::bit(kind);
    }

    pub fn contains(&self, kind: NeedKind) -> bool {
        self.0 & Self::bit(kind) != 0
    }

    pub fn is_empty(&self) -> bool {
        self.0 == 0
    }

    pub fn len(&self) -> usize {
        self.0.count_ones() as usize
    }

    /// Whether the two sets share a need.
    pub fn meets(&self, other: NeedSet) -> bool {
        self.0 & other.0 != 0
    }

    /// The members in `NeedKind::ALL` order.
    pub fn iter(&self) -> impl Iterator<Item = NeedKind> + '_ {
        NeedKind::ALL.into_iter().filter(|k| self.contains(*k))
    }

    /// The members' names in `NeedKind::ALL` order.
    pub fn names(&self) -> Vec<&'static str> {
        self.iter().map(|k| k.as_str()).collect()
    }
}

impl From<NeedSet> for Vec<String> {
    fn from(set: NeedSet) -> Self {
        set.names().into_iter().map(str::to_string).collect()
    }
}

impl TryFrom<Vec<String>> for NeedSet {
    type Error = String;

    fn try_from(names: Vec<String>) -> Result<Self, Self::Error> {
        let mut set = NeedSet::EMPTY;
        for name in names {
            let kind = NeedKind::ALL
                .iter()
                .find(|k| k.as_str() == name)
                .ok_or_else(|| format!("unknown need name {name:?}"))?;
            set.insert(*kind);
        }
        Ok(set)
    }
}

/// Why an episode released (needy-law §4).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ReleaseBy {
    /// Every masked need reached the release level (`needy` only).
    Level,
    /// The hold limit passed since onset (both presets).
    Limit,
}

/// The most recent release, kept so the recorder can name the release
/// tick and its kind.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Release {
    pub tick: u64,
    pub by: ReleaseBy,
}

/// Where the seat is in its schedule.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum Phase {
    /// Between episodes; the next opens on the first published tick at
    /// or past `next_onset`.
    Resting { next_onset: u64 },
    /// An episode is open: `masked` is the mask.
    Held { onset: u64, masked: NeedSet },
}

/// What one advance step did.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Transition {
    Onset { masked: NeedSet },
    Release { by: ReleaseBy },
}

/// A needy seat's schedule state, carried on the kitty (`Kitty.needy`)
/// and saved with the world.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NeedyState {
    /// `true` for `needy_hold`: no level release.
    pub hold: bool,
    /// The private sub-stream (§2); every draw of the schedule.
    pub rng: ChaCha8Rng,
    /// Episodes opened so far; 0 before the first onset.
    pub ordinal: u32,
    pub phase: Phase,
    /// The next episode's masked set, drawn ahead (at generation and at
    /// each release) so the mask is fixed before it applies.
    pub next: NeedSet,
    pub last_release: Option<Release>,
}

/// The sub-stream seed (§2): world seed LE, kitty id LE, the domain tag,
/// zeros. The kitty id is what gives two needy seats independent streams.
pub fn sub_stream_seed(world_seed: u64, kitty_id: KittyId) -> [u8; 32] {
    let mut seed = [0u8; 32];
    seed[0..8].copy_from_slice(&world_seed.to_le_bytes());
    seed[8..12].copy_from_slice(&kitty_id.to_le_bytes());
    seed[12..12 + DOMAIN_TAG.len()].copy_from_slice(DOMAIN_TAG);
    seed
}

/// The one conversion from the stream to a uniform in [0, 1) (§3; the
/// init-law §5 recipe): a `u64` to the 53-bit mantissa.
pub fn uniform(rng: &mut ChaCha8Rng) -> f64 {
    (rng.next_u64() >> 11) as f64 * (1.0 / (1u64 << 53) as f64)
}

/// A weighted index from one uniform: the first `i` whose cumulative
/// weight exceeds `u · total`. Assumes validation (finite, non-negative,
/// not all zero); a zero weight is never chosen.
fn weighted_index(rng: &mut ChaCha8Rng, weights: &[f32]) -> usize {
    let total: f64 = weights.iter().map(|w| f64::from(*w)).sum();
    let target = uniform(rng) * total;
    let mut cumulative = 0.0f64;
    for (i, w) in weights.iter().enumerate() {
        cumulative += f64::from(*w);
        if *w > 0.0 && cumulative > target {
            return i;
        }
    }
    // Rounding at the very top of the range: the last positive weight.
    weights
        .iter()
        .rposition(|w| *w > 0.0)
        .expect("validated: at least one weight above zero")
}

/// A tick within `[lo, hi)` from one uniform (§3.1).
fn tick_within(rng: &mut ChaCha8Rng, lo: u64, hi: u64, draw: OnsetDraw) -> u64 {
    let u = uniform(rng);
    let span = hi.saturating_sub(lo).max(1);
    let tick = match draw {
        OnsetDraw::Flat => lo + (u * span as f64).floor() as u64,
        OnsetDraw::LogUniform => {
            let lo_prime = lo.max(1) as f64;
            let hi_f = hi.max(lo + 1) as f64;
            (lo_prime.ln() + u * (hi_f.ln() - lo_prime.ln()))
                .exp()
                .floor() as u64
        }
    };
    tick.clamp(lo, hi.saturating_sub(1).max(lo))
}

/// An episode's masked set (§3.2): `m` by `mix`, then `m` distinct needs
/// by a partial Fisher–Yates over `NeedKind::ALL`.
fn draw_set(rng: &mut ChaCha8Rng, cfg: &NeedyConfig) -> NeedSet {
    let count = NeedKind::ALL.len();
    let m = (weighted_index(rng, &cfg.mix) + 1).min(count);
    let mut order: Vec<NeedKind> = NeedKind::ALL.to_vec();
    for i in 0..m {
        let remaining = (count - i) as f64;
        let j = i + ((uniform(rng) * remaining).floor() as usize).min(count - i - 1);
        order.swap(i, j);
    }
    NeedSet::from_kinds(&order[..m])
}

/// The rest gap (§3.3): flat in `[min, max]`, inclusive.
fn draw_gap(rng: &mut ChaCha8Rng, cfg: &NeedyConfig) -> u64 {
    let span = cfg.gap.max.saturating_sub(cfg.gap.min) + 1;
    (cfg.gap.min + (uniform(rng) * span as f64).floor() as u64).min(cfg.gap.max)
}

impl NeedyState {
    /// A fresh seat at generation: the first onset (level, then tick
    /// within it), then the first episode's set — in that order (§3).
    pub fn new(world_seed: u64, kitty_id: KittyId, hold: bool, cfg: &NeedyConfig) -> Self {
        let mut rng = ChaCha8Rng::from_seed(sub_stream_seed(world_seed, kitty_id));
        let level = weighted_index(&mut rng, &cfg.onset_weights);
        let (lo, hi) = (cfg.onset_levels[level], cfg.onset_levels[level + 1]);
        let next_onset = tick_within(&mut rng, lo, hi, cfg.onset_draw);
        let next = draw_set(&mut rng, cfg);
        NeedyState {
            hold,
            rng,
            ordinal: 0,
            phase: Phase::Resting { next_onset },
            next,
            last_release: None,
        }
    }

    /// One advance step (§4) for the tick `t` about to be published, on
    /// the post-rise `needs`. At most one transition per step.
    pub fn step(&mut self, needs: &Needs, t: u64, cfg: &NeedyConfig) -> Option<Transition> {
        match self.phase {
            Phase::Resting { next_onset } => {
                if t < next_onset {
                    return None;
                }
                self.ordinal += 1;
                let masked = self.next;
                self.phase = Phase::Held { onset: t, masked };
                Some(Transition::Onset { masked })
            }
            Phase::Held { onset, masked } => {
                let at_level =
                    !self.hold && masked.iter().all(|k| needs.get(k) >= cfg.release_level);
                let by = if at_level {
                    ReleaseBy::Level
                } else if t.saturating_sub(onset) >= cfg.hold_ticks {
                    ReleaseBy::Limit
                } else {
                    return None;
                };
                self.last_release = Some(Release { tick: t, by });
                let gap = draw_gap(&mut self.rng, cfg);
                self.next = draw_set(&mut self.rng, cfg);
                self.phase = Phase::Resting {
                    next_onset: t + gap,
                };
                Some(Transition::Release { by })
            }
        }
    }

    /// The current mask: the held set, or empty.
    pub fn mask(&self) -> NeedSet {
        match self.phase {
            Phase::Held { masked, .. } => masked,
            Phase::Resting { .. } => NeedSet::EMPTY,
        }
    }

    /// The recorder's phase name for the published tick `t` (needy-law
    /// §7): the release kind on the release tick, else `held` / `resting`.
    pub fn phase_name(&self, t: u64) -> &'static str {
        match (self.last_release, self.phase) {
            (Some(Release { tick, by }), _) if tick == t => match by {
                ReleaseBy::Level => "released_level",
                ReleaseBy::Limit => "released_limit",
            },
            (_, Phase::Held { .. }) => "held",
            (_, Phase::Resting { .. }) => "resting",
        }
    }
}

/// The needs an action relieves on the ACTOR (needy-law §5a), read off
/// `apply_activity_effects` / `apply_sleep_relief` and cross-checked
/// against them by test: co-sleep relieves sleep AND cuddle; grooming a
/// friend pays the groomer's own cuddle; solo rest is posture.
pub fn proposer_relief(action: &Action) -> NeedSet {
    use NeedKind::*;
    match action {
        Action::Eat => NeedSet::from_kinds(&[Eat]),
        Action::Drink => NeedSet::from_kinds(&[Drink]),
        Action::Sleep { with: None } => NeedSet::from_kinds(&[Sleep]),
        Action::Sleep { with: Some(_) } => NeedSet::from_kinds(&[Sleep, Cuddle]),
        Action::Rest { with: None } => NeedSet::EMPTY,
        Action::Rest { with: Some(_) } => NeedSet::from_kinds(&[Cuddle]),
        Action::Groom { target: None } => NeedSet::from_kinds(&[Bath]),
        Action::Groom { target: Some(_) } => NeedSet::from_kinds(&[Cuddle]),
        Action::Play { .. } => NeedSet::from_kinds(&[Play]),
        Action::Chase(_)
        | Action::Move { .. }
        | Action::Idle
        | Action::Meow { .. }
        | Action::Purr => NeedSet::EMPTY,
    }
}

/// The needs an action relieves on the kitty it NAMES (needy-law §5a),
/// with that kitty's id; `None` for an action naming no kitty.
pub fn partner_relief(action: &Action) -> Option<(KittyId, NeedSet)> {
    use NeedKind::*;
    match action {
        Action::Groom { target: Some(p) } => Some((*p, NeedSet::from_kinds(&[Bath]))),
        Action::Play {
            target: Some(TargetRef::Kitty { id }),
        } => Some((*id, NeedSet::from_kinds(&[Play]))),
        Action::Rest { with: Some(p) } | Action::Sleep { with: Some(p) } => {
            Some((*p, NeedSet::from_kinds(&[Cuddle])))
        }
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cfg() -> NeedyConfig {
        NeedyConfig::default()
    }

    fn short() -> NeedyConfig {
        NeedyConfig {
            onset_levels: vec![0, 5, 20, 50, 100, 200],
            hold_ticks: 50,
            gap: crate::config::GapRange { min: 10, max: 30 },
            release_level: 60.0,
            ..cfg()
        }
    }

    /// Runs the law on a flat need trajectory (every need climbs 0.5 a
    /// tick from 0, nothing serviced) for `ticks`, returning the
    /// transitions with their ticks.
    fn run(state: &mut NeedyState, cfg: &NeedyConfig, ticks: u64) -> Vec<(u64, Transition)> {
        let mut needs = Needs::default();
        let mut out = Vec::new();
        for t in 1..=ticks {
            for k in NeedKind::ALL {
                needs.add(k, 0.5);
            }
            if let Some(tr) = state.step(&needs, t, cfg) {
                out.push((t, tr));
            }
        }
        out
    }

    #[test]
    fn same_seed_and_id_replay_identically_and_either_difference_diverges() {
        let c = short();
        let base = run(&mut NeedyState::new(7, 2, false, &c), &c, 2000);
        assert_eq!(base, run(&mut NeedyState::new(7, 2, false, &c), &c, 2000));
        assert!(base.len() >= 20, "ten episodes at least: {}", base.len());

        let mut other_id = NeedyState::new(7, 3, false, &c);
        let mut other_seed = NeedyState::new(8, 2, false, &c);
        assert_ne!(
            base,
            run(&mut other_id, &c, 2000),
            "the kitty id reaches the stream"
        );
        assert_ne!(
            base,
            run(&mut other_seed, &c, 2000),
            "the world seed reaches the stream"
        );
    }

    #[test]
    fn level_release_fires_at_exactly_the_level_and_never_for_hold() {
        let c = short();
        let masked = NeedSet::from_kinds(&[NeedKind::Eat]);
        let mut state = NeedyState::new(1, 1, false, &c);
        state.phase = Phase::Held { onset: 10, masked };
        let mut needs = Needs::default();
        needs.add(NeedKind::Eat, 59.9);
        assert_eq!(state.step(&needs, 11, &c), None, "below the level: held");
        needs.add(NeedKind::Eat, 0.1);
        assert_eq!(
            state.step(&needs, 12, &c),
            Some(Transition::Release {
                by: ReleaseBy::Level
            }),
            "a need exactly at the release level releases (>=)"
        );
        assert_eq!(state.phase_name(12), "released_level");
        assert_eq!(state.phase_name(13), "resting");

        let mut hold = NeedyState::new(1, 1, true, &c);
        hold.phase = Phase::Held { onset: 10, masked };
        let mut full = Needs::default();
        full.add(NeedKind::Eat, 100.0);
        assert_eq!(
            hold.step(&full, 11, &c),
            None,
            "needy_hold never releases by level"
        );
        assert_eq!(
            hold.step(&full, 10 + c.hold_ticks, &c),
            Some(Transition::Release {
                by: ReleaseBy::Limit
            }),
            "the limit releases at t - onset >= hold_ticks"
        );
        assert_eq!(hold.phase_name(10 + c.hold_ticks), "released_limit");
    }

    #[test]
    fn the_ordinal_counts_onsets_from_one_and_an_onset_of_zero_opens_on_tick_one() {
        let c = short();
        let mut state = NeedyState::new(3, 1, false, &c);
        assert_eq!(state.ordinal, 0);
        state.phase = Phase::Resting { next_onset: 0 };
        let needs = Needs::default();
        let tr = state.step(&needs, 1, &c);
        assert!(
            matches!(tr, Some(Transition::Onset { .. })),
            "an onset of 0 opens on the first published tick (>=, never ==): {tr:?}"
        );
        assert_eq!(state.ordinal, 1);
        assert_eq!(state.phase_name(1), "held");
        assert!(!state.mask().is_empty());

        // Release by limit, then a gap of exactly 1 opens the next on t + 1.
        let mut c1 = c.clone();
        c1.gap = crate::config::GapRange { min: 1, max: 1 };
        let t_release = 1 + c1.hold_ticks;
        assert_eq!(
            state.step(&needs, t_release, &c1),
            Some(Transition::Release {
                by: ReleaseBy::Limit
            })
        );
        assert_eq!(state.mask(), NeedSet::EMPTY, "released: the mask lifts");
        assert!(
            matches!(
                state.step(&needs, t_release + 1, &c1),
                Some(Transition::Onset { .. })
            ),
            "gap 1 reopens on the tick after the release"
        );
        assert_eq!(state.ordinal, 2, "the ordinal counts onsets, not releases");
    }

    #[test]
    fn drawn_sets_have_m_distinct_needs_and_every_stratum_is_reachable_in_proportion() {
        // SC-004 reachability under the DEFAULT parameters, over 10,000
        // draws; plus a mix with every count open so m = N is seen.
        let c = cfg();
        let n = NeedKind::ALL.len();
        let mut rng = ChaCha8Rng::from_seed(sub_stream_seed(99, 1));
        let mut by_m = vec![0usize; n];
        let mut by_need = vec![0usize; n];
        for _ in 0..10_000 {
            let set = draw_set(&mut rng, &c);
            assert!(!set.is_empty());
            by_m[set.len() - 1] += 1;
            for (i, k) in NeedKind::ALL.iter().enumerate() {
                if set.contains(*k) {
                    by_need[i] += 1;
                }
            }
        }
        let total: f32 = c.mix.iter().sum();
        for (k, w) in c.mix.iter().enumerate() {
            let share = by_m[k] as f32 / 10_000.0;
            if *w == 0.0 {
                assert_eq!(by_m[k], 0, "a zero weight is never drawn (m = {})", k + 1);
            } else {
                assert!(
                    (share - w / total).abs() < 0.02,
                    "m = {}: share {share} vs weight {}",
                    k + 1,
                    w / total
                );
            }
        }
        for (i, k) in NeedKind::ALL.iter().enumerate() {
            assert!(
                by_need[i] > 0,
                "{} never appears in a drawn set",
                k.as_str()
            );
        }

        let mut all_open = cfg();
        all_open.mix = vec![1.0; n];
        let mut seen_full = false;
        for _ in 0..2_000 {
            let set = draw_set(&mut rng, &all_open);
            seen_full |= set.len() == n;
        }
        assert!(seen_full, "m = N is reachable when the mix opens it");

        // First-onset levels over 10,000 seeds: every positive-weight
        // level hit in proportion, a zero-weight level never, and the
        // tick inside the level for both draw shapes.
        for draw in [OnsetDraw::Flat, OnsetDraw::LogUniform] {
            let mut c2 = cfg();
            c2.onset_draw = draw;
            c2.onset_weights = vec![0.4, 0.0, 0.3, 0.2, 0.1];
            let levels = c2.level_count();
            let mut by_level = vec![0usize; levels];
            for seed in 0..10_000u64 {
                let s = NeedyState::new(seed, 1, false, &c2);
                let Phase::Resting { next_onset } = s.phase else {
                    panic!("fresh state rests");
                };
                let level = (0..levels)
                    .find(|&i| {
                        next_onset >= c2.onset_levels[i] && next_onset < c2.onset_levels[i + 1]
                    })
                    .unwrap_or_else(|| panic!("onset {next_onset} outside every level"));
                by_level[level] += 1;
            }
            let total: f32 = c2.onset_weights.iter().sum();
            for (i, w) in c2.onset_weights.iter().enumerate() {
                let share = by_level[i] as f32 / 10_000.0;
                if *w == 0.0 {
                    assert_eq!(by_level[i], 0, "{draw:?}: zero-weight level {i} drawn");
                } else {
                    assert!(
                        (share - w / total).abs() < 0.02,
                        "{draw:?}: level {i} share {share} vs {}",
                        w / total
                    );
                }
            }
        }
    }

    /// The porting-grade pin (needy-law §3): the first 20 uniforms of the
    /// documented sub-stream and the first three episodes' (onset, set,
    /// release tick) for seed 1 / kitty 1 under the short config on the
    /// flat 0.5-a-tick trajectory. Recorded from the law's own output at
    /// v1; a legitimate law change bumps the version, the tag and this pin
    /// together.
    #[test]
    fn the_v1_draw_order_and_conversion_are_pinned_for_porting() {
        let mut rng = ChaCha8Rng::from_seed(sub_stream_seed(1, 1));
        let uniforms: Vec<f64> = (0..20).map(|_| uniform(&mut rng)).collect();
        assert_eq!(
            uniforms[..3],
            [0.10574643388000982, 0.49688750037087237, 0.2650333939694427],
            "the first three uniforms of (seed 1, kitty 1)"
        );
        let c = short();
        let mut state = NeedyState::new(1, 1, false, &c);
        let Phase::Resting { next_onset } = state.phase else {
            panic!()
        };
        let first_set: Vec<&str> = state.next.names();
        let transitions = run(&mut state, &c, 400);
        let summary: Vec<String> = transitions
            .iter()
            .take(6)
            .map(|(t, tr)| match tr {
                Transition::Onset { masked } => format!("{t}:onset:{}", masked.names().join("+")),
                Transition::Release { by } => format!("{t}:release:{by:?}"),
            })
            .collect();
        assert_eq!(
            (next_onset, first_set, summary),
            (
                2,
                vec!["cuddle"],
                vec![
                    "2:onset:cuddle".to_string(),
                    "52:release:Limit".to_string(),
                    "75:onset:eat+cuddle+bath".to_string(),
                    "120:release:Level".to_string(),
                    "138:onset:eat+play".to_string(),
                    "139:release:Level".to_string(),
                ]
            ),
            "seed 1 / kitty 1 under the short config"
        );
    }

    #[test]
    fn the_relief_tables_match_the_law_row_by_row() {
        use NeedKind::*;
        type Row = (Action, &'static [NeedKind], Option<&'static [NeedKind]>);
        let rows: Vec<Row> = vec![
            (Action::Eat, &[Eat], None),
            (Action::Drink, &[Drink], None),
            (Action::Sleep { with: None }, &[Sleep], None),
            (
                Action::Sleep { with: Some(2) },
                &[Sleep, Cuddle],
                Some(&[Cuddle]),
            ),
            (Action::Rest { with: None }, &[], None),
            (Action::Rest { with: Some(2) }, &[Cuddle], Some(&[Cuddle])),
            (Action::Groom { target: None }, &[Bath], None),
            (Action::Groom { target: Some(2) }, &[Cuddle], Some(&[Bath])),
            (Action::Play { target: None }, &[Play], None),
            (
                Action::Play {
                    target: Some(TargetRef::Element { id: 9 }),
                },
                &[Play],
                None,
            ),
            (
                Action::Play {
                    target: Some(TargetRef::Kitty { id: 2 }),
                },
                &[Play],
                Some(&[Play]),
            ),
            (Action::Chase(TargetRef::Kitty { id: 2 }), &[], None),
            (Action::Idle, &[], None),
            (Action::Purr, &[], None),
        ];
        for (action, own, partner) in rows {
            assert_eq!(
                proposer_relief(&action),
                NeedSet::from_kinds(own),
                "{action:?}"
            );
            assert_eq!(
                partner_relief(&action),
                partner.map(|p| (2, NeedSet::from_kinds(p))),
                "{action:?}"
            );
        }
    }

    #[test]
    fn need_sets_serialize_as_names_and_refuse_unknown_ones() {
        let set = NeedSet::from_kinds(&[NeedKind::Bath, NeedKind::Eat]);
        let json = serde_json::to_string(&set).unwrap();
        assert_eq!(json, "[\"eat\",\"bath\"]", "NeedKind::ALL order");
        let back: NeedSet = serde_json::from_str(&json).unwrap();
        assert_eq!(back, set);
        assert!(serde_json::from_str::<NeedSet>("[\"hunger\"]").is_err());
    }
}
