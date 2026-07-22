//! Global state v1 (spec 014 FR-019): the privileged critic view.
//!
//! A fixed-size vector (for a given configuration) derived from the same
//! frozen snapshot as the observations: every kitty's full state **without
//! slot truncation**, a bounded configured element summary, and the episode
//! clock. It exists for critics, not actors — the deployed behavior API
//! never receives it (decentralized execution enforced by API shape).
//!
//! Layout: per kitty in stable id order — needs (/100), happiness (/100),
//! position, activity one-hot (7), social flag, partner (present flag +
//! roster index / (n−1)), progress, distress flags (6), traits (6) — then
//! per element type (water, chow, bug, greeble, sunbeam): count / hard max,
//! plus (chow only) total servings / (max elements × servings each), plus
//! the K nearest elements to the world center (present, x/width, y/height);
//! then the episode clock.

use cloudkitty_core::element::ElementType;
use cloudkitty_core::grid::Position;
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::world::WorldSnapshot;
use cloudkitty_core::Config;

use crate::config::GlobalStateConfig;

/// Versioned like the observation schema (FR-019).
pub const GLOBAL_STATE_SCHEMA_VERSION: u32 = 1;

const PER_KITTY: usize = 6 + 1 + 2 + 7 + 1 + 2 + 1 + 6 + 6;
const PER_TYPE_BASE: usize = 1;
const PER_CENTER_ELEMENT: usize = 3;

/// The exact global-state length for a roster size and configuration.
pub fn global_state_len(roster: usize, cfg: &GlobalStateConfig) -> usize {
    roster * PER_KITTY
        + ElementType::ALL.len() * (PER_TYPE_BASE + cfg.elements_per_type * PER_CENTER_ELEMENT)
        + 1  // total chow servings
        + 1 // episode clock
}

/// Encodes the privileged global state. `episode_clock` is tick/horizon.
pub fn encode_global_state(
    snapshot: &WorldSnapshot,
    core: &Config,
    cfg: &GlobalStateConfig,
    episode_clock: f32,
) -> Vec<f32> {
    let width = snapshot.width as f32;
    let height = snapshot.height as f32;
    let roster = snapshot.kitties.len();
    let mut v = Vec::with_capacity(global_state_len(roster, cfg));

    // Kitties, stable id order (the snapshot's order).
    for kitty in &snapshot.kitties {
        for kind in NeedKind::ALL {
            v.push(kitty.needs.get(kind) / 100.0);
        }
        v.push(kitty.happiness / 100.0);
        v.push(kitty.pos.x as f32 / width);
        v.push(kitty.pos.y as f32 / height);
        let index = match kitty.activity {
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
        let partner = kitty.activity.partner();
        v.push(if partner.is_some() { 1.0 } else { 0.0 });
        match partner.and_then(|p| snapshot.kitties.iter().position(|k| k.id == p)) {
            Some(pos) if roster > 1 => {
                v.push(1.0);
                v.push(pos as f32 / (roster - 1) as f32);
            }
            _ => {
                v.push(0.0);
                v.push(0.0);
            }
        }
        let progress = match (
            kitty.activity_clock,
            kitty.activity.bounds(&core.actions.durations),
        ) {
            (Some(clock), Some(bounds)) => {
                (clock.elapsed(snapshot.tick) as f32 / bounds.min.max(1) as f32).clamp(0.0, 1.0)
            }
            _ => 0.0,
        };
        v.push(progress);
        for kind in NeedKind::ALL {
            v.push(if kitty.in_distress.contains(&kind) {
                1.0
            } else {
                0.0
            });
        }
        for kind in NeedKind::ALL {
            v.push((core.need_rate_for(kitty.id, kind) / 1.0).clamp(0.0, 4.0));
        }
    }

    // Element summary, bounded by configuration.
    let center = Position::new(snapshot.width / 2, snapshot.height / 2);
    let hard_max = (snapshot.width * snapshot.height / cloudkitty_core::config::TILES_PER_ELEMENT)
        .max(1) as f32;
    for kind in ElementType::ALL {
        let mut of_kind: Vec<_> = snapshot.elements_of(kind).collect();
        v.push(of_kind.len() as f32 / hard_max);
        of_kind.sort_unstable_by_key(|e| (center.manhattan_distance(&e.pos), e.id));
        for slot in 0..cfg.elements_per_type {
            match of_kind.get(slot) {
                Some(e) => {
                    v.push(1.0);
                    v.push(e.pos.x as f32 / width);
                    v.push(e.pos.y as f32 / height);
                }
                None => {
                    v.push(0.0);
                    v.push(0.0);
                    v.push(0.0);
                }
            }
        }
    }
    let total_servings: u32 = snapshot
        .elements_of(ElementType::Chow)
        .map(|e| match e.kind {
            cloudkitty_core::element::ElementKind::Chow { servings } => servings,
            _ => 0,
        })
        .sum();
    let servings_cap =
        (core.elements.chow.max.max(1) * core.elements.chow.servings.unwrap_or(1).max(1)) as f32;
    v.push((total_servings as f32 / servings_cap).clamp(0.0, 1.0));

    v.push(episode_clock.clamp(0.0, 1.0));

    debug_assert_eq!(v.len(), global_state_len(roster, cfg));
    v
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::test_support::test_world;

    #[test]
    fn the_global_state_has_its_documented_fixed_size_and_bounds() {
        let (world, config) = test_world();
        let snapshot = world.snapshot();
        let cfg = GlobalStateConfig::default();

        let v = encode_global_state(&snapshot, &config, &cfg, 0.5);
        assert_eq!(v.len(), global_state_len(snapshot.kitties.len(), &cfg));
        for (i, value) in v.iter().enumerate() {
            assert!(
                (0.0..=4.0).contains(value),
                "value {value} at {i} out of bounds"
            );
        }

        let again = encode_global_state(&snapshot, &config, &cfg, 0.5);
        assert_eq!(v, again, "deterministic");
    }
}
