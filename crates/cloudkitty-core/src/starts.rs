//! Randomized starts (spec 062): the versioned draw law.
//!
//! One pure function, `draw`, resolves every kitty's start tile from the
//! config alone. It consumes a domain-separated ChaCha8 sub-stream keyed
//! off (world seed, fixed tag) — NEVER the master world stream — so a
//! knob-on world and an explicit-starts world with the same positions are
//! byte-identical over a full run (FR-004 / SC-003). The law is documented
//! porting-grade in `specs/062-randomized-starts/contracts/draw-law-v1.md`;
//! any change to it bumps [`STARTS_LAW_VERSION`] and the domain tag in the
//! same commit (FR-012).

use std::collections::BTreeSet;

use rand::{RngCore, SeedableRng};
use rand_chacha::ChaCha8Rng;

use crate::config::Config;
use crate::grid::Position;
use crate::kitty::KittyId;

/// Version of the draw law (contracts/draw-law-v1.md). Stamped into
/// collection metadata; bumped together with [`DOMAIN_TAG`] on any law
/// change — the law never changes silently under a stable version.
pub const STARTS_LAW_VERSION: u32 = 1;

/// The sub-stream's domain separator: 12 ASCII bytes, versioned with the law.
const DOMAIN_TAG: &[u8; 12] = b"ck-starts-v1";

/// Start-tile category — the coverage instrument's disjoint geometry
/// (coverage_read.py): corners are the 4 tiles on both edges, the edge
/// ring is the non-corner remainder of the outer ring, interior is the
/// rest.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StartCategory {
    Corner,
    EdgeRing,
    Interior,
}

impl StartCategory {
    /// The wire spelling used by collection metadata (contracts/provenance.md).
    pub fn as_str(self) -> &'static str {
        match self {
            StartCategory::Corner => "corner",
            StartCategory::EdgeRing => "edge_ring",
            StartCategory::Interior => "interior",
        }
    }

    /// Classifies a tile by the coverage instrument's geometry.
    pub fn classify(pos: Position, width: u32, height: u32) -> Self {
        let on_x_edge = pos.x == 0 || pos.x == width - 1;
        let on_y_edge = pos.y == 0 || pos.y == height - 1;
        match (on_x_edge, on_y_edge) {
            (true, true) => StartCategory::Corner,
            (false, false) => StartCategory::Interior,
            _ => StartCategory::EdgeRing,
        }
    }
}

/// One kitty's resolved start: the engine's own draw record.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DrawnStart {
    pub kitty: KittyId,
    pub position: Position,
    /// For explicit kitties, the geometric classification of the pinned tile.
    pub category: StartCategory,
    /// False for explicit-coordinate kitties (they consume no draws).
    pub drawn: bool,
}

/// The only draw failure: a kitty drew a category with no free tile left.
/// Never silent, never spilling into another category.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
#[error(
    "[starts] category '{}' exhausted: {drawn_into} kitties drew it but it has \
     only {capacity} tiles ({occupied_in_category} already occupied) -- shrink \
     the roster, adjust the shares, or grow the world",
    category.as_str()
)]
pub struct StartsError {
    pub category: StartCategory,
    /// How many kitties have drawn this category, including the failing one.
    pub drawn_into: usize,
    /// The category's total tile capacity in this world.
    pub capacity: usize,
    /// How many of those tiles were already occupied at the failing draw.
    pub occupied_in_category: usize,
}

/// The sub-stream seed: world seed little-endian, the domain tag, zeros
/// (contracts/draw-law-v1.md §3).
fn sub_stream_seed(world_seed: u64) -> [u8; 32] {
    let mut seed = [0u8; 32];
    seed[0..8].copy_from_slice(&world_seed.to_le_bytes());
    seed[8..20].copy_from_slice(DOMAIN_TAG);
    seed
}

/// The category's tiles in canonical row-major order (y outer ascending,
/// x inner ascending), the one enumeration order everywhere in the law.
fn category_tiles(category: StartCategory, width: u32, height: u32) -> Vec<Position> {
    let mut tiles = Vec::new();
    for y in 0..height {
        for x in 0..width {
            let pos = Position::new(x, y);
            if StartCategory::classify(pos, width, height) == category {
                tiles.push(pos);
            }
        }
    }
    tiles
}

/// Resolves every rostered kitty's start (the ONE sampler, FR-007), in
/// kitty-id ascending order. Pure: the output depends only on (world seed,
/// dimensions, shares, roster ids and explicit coordinates). Explicit
/// kitties keep their tiles and consume zero draws; drawn kitties take two
/// `u64` draws each from the sub-stream. Assumes `config.validate()` has
/// already passed (as `World::generate` does): a kitty without coordinates
/// implies `[starts]` is present.
pub fn draw(config: &Config) -> Result<Vec<DrawnStart>, StartsError> {
    let width = config.world.width;
    let height = config.world.height;

    let mut roster: Vec<_> = config.kitties.iter().collect();
    roster.sort_by_key(|k| k.id);

    // Explicit tiles are occupied before any draw (contracts/draw-law-v1.md §4).
    let mut occupied: BTreeSet<Position> = roster.iter().filter_map(|k| k.position()).collect();

    let mut rng = ChaCha8Rng::from_seed(sub_stream_seed(config.world.seed));
    let mut drawn_into = [0usize; 3];
    let mut starts = Vec::with_capacity(roster.len());

    for kitty in roster {
        if let Some(position) = kitty.position() {
            starts.push(DrawnStart {
                kitty: kitty.id,
                position,
                category: StartCategory::classify(position, width, height),
                drawn: false,
            });
            continue;
        }
        let shares = config
            .starts
            .as_ref()
            .expect("config.validate() guarantees [starts] when a kitty has no coordinates");

        let v1 = rng.next_u64();
        // u in [0, 1): the standard 53-bit mantissa construction, exact in f64.
        let u = (v1 >> 11) as f64 * (1.0 / (1u64 << 53) as f64);
        let category = if u < shares.corner_share {
            StartCategory::Corner
        } else if u < shares.edge_ring_share {
            StartCategory::EdgeRing
        } else {
            StartCategory::Interior
        };
        let cat_index = category as usize;
        drawn_into[cat_index] += 1;

        let all = category_tiles(category, width, height);
        let free: Vec<Position> = all
            .iter()
            .copied()
            .filter(|p| !occupied.contains(p))
            .collect();
        if free.is_empty() {
            return Err(StartsError {
                category,
                drawn_into: drawn_into[cat_index],
                capacity: all.len(),
                occupied_in_category: all.len(),
            });
        }
        let v2 = rng.next_u64();
        let position = free[(v2 % free.len() as u64) as usize];
        occupied.insert(position);
        starts.push(DrawnStart {
            kitty: kitty.id,
            position,
            category,
            drawn: true,
        });
    }
    Ok(starts)
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;

    use super::*;
    use crate::config::{KittyConfig, StartsConfig};

    /// A share-enabled config: `n` drawn kitties on a `width` x `height`
    /// world, no explicit coordinates.
    fn share_config(width: u32, height: u32, seed: u64, n: u32, shares: StartsConfig) -> Config {
        let mut config = Config::default();
        config.world.width = width;
        config.world.height = height;
        config.world.seed = seed;
        config.kitties = (1..=n)
            .map(|id| {
                let mut k = KittyConfig::new(id, format!("k{id}"), 0, 0, "needs_driven");
                k.x = None;
                k.y = None;
                k
            })
            .collect();
        config.starts = Some(shares);
        config
    }

    fn default_shares() -> StartsConfig {
        StartsConfig {
            edge_ring_share: 0.25,
            corner_share: 0.05,
        }
    }

    #[test]
    fn same_seed_and_config_draw_identical_positions() {
        let config = share_config(16, 12, 20261016, 6, default_shares());
        let a = draw(&config).unwrap();
        let b = draw(&config).unwrap();
        assert_eq!(a, b, "the draw must be a pure function of the config");
    }

    #[test]
    fn roster_file_order_does_not_move_any_start() {
        let config = share_config(16, 12, 7, 5, default_shares());
        let mut reordered = config.clone();
        reordered.kitties.reverse();
        let a = draw(&config).unwrap();
        let b = draw(&reordered).unwrap();
        assert_eq!(a, b, "the draw keys on kitty-id order, never file order");
    }

    /// SC-001 + SC-002, pinned bounds: 500 seeds x 4 drawn kitties = 2000
    /// category draws. Each category count is Binomial(2000, p); the
    /// assertion band is p +- 4 sigma, so a correct law fails with
    /// probability ~6e-5 per category while a swapped or shifted share
    /// (the bugs this guards) lands far outside.
    #[test]
    fn sweep_every_start_lawful_and_shares_within_binomial_tolerance() {
        let shares = default_shares();
        let (width, height, kitties_per_world) = (16, 12, 4);
        let seeds = 500u64;
        let mut counts = [0usize; 3]; // corner, edge_ring, interior
        for seed in 0..seeds {
            let config = share_config(width, height, seed, kitties_per_world, shares);
            let starts = draw(&config).unwrap();
            assert_eq!(starts.len(), kitties_per_world as usize);
            let mut seen = BTreeSet::new();
            for s in &starts {
                assert!(
                    s.position.x < width && s.position.y < height,
                    "seed {seed}: start out of bounds: {:?}",
                    s.position
                );
                assert!(
                    seen.insert(s.position),
                    "seed {seed}: two kitties share {:?}",
                    s.position
                );
                // Independent classification: re-derive the geometry here
                // rather than trusting the draw's own record.
                let on_x = s.position.x == 0 || s.position.x == width - 1;
                let on_y = s.position.y == 0 || s.position.y == height - 1;
                let independent = match (on_x, on_y) {
                    (true, true) => StartCategory::Corner,
                    (false, false) => StartCategory::Interior,
                    _ => StartCategory::EdgeRing,
                };
                assert_eq!(
                    s.category, independent,
                    "seed {seed}: recorded category disagrees with the geometry at {:?}",
                    s.position
                );
                counts[s.category as usize] += 1;
            }
        }
        let n = (seeds * kitties_per_world as u64) as f64;
        let expected = [
            shares.corner_share,
            shares.edge_ring_share - shares.corner_share,
            1.0 - shares.edge_ring_share,
        ];
        for (category, (&count, p)) in counts.iter().zip(expected).enumerate() {
            let sigma = (n * p * (1.0 - p)).sqrt();
            let diff = (count as f64 - n * p).abs();
            assert!(
                diff <= 4.0 * sigma,
                "category {category}: {count} of {n} draws, expected {} +- {} (4 sigma)",
                n * p,
                4.0 * sigma
            );
        }
    }

    #[test]
    fn exhaustion_fails_naming_the_category_and_counts() {
        // corner_share 1.0: every kitty draws Corner; the 5th finds the 4
        // corner tiles taken.
        let config = share_config(
            8,
            8,
            3,
            5,
            StartsConfig {
                edge_ring_share: 1.0,
                corner_share: 1.0,
            },
        );
        let err = draw(&config).unwrap_err();
        assert_eq!(err.category, StartCategory::Corner);
        assert_eq!(err.drawn_into, 5);
        assert_eq!(err.capacity, 4);
        let msg = err.to_string();
        assert!(
            msg.contains("'corner'") && msg.contains('5') && msg.contains('4'),
            "error must name the category and the counts: {msg}"
        );
    }

    #[test]
    fn explicit_kitties_keep_their_tile_consume_no_draws_and_block_it() {
        let shares = default_shares();
        let mut mixed = share_config(16, 12, 11, 4, shares);
        // Pin kitty 2 explicitly; ids 1, 3, 4 stay drawn.
        mixed.kitties[1].x = Some(7);
        mixed.kitties[1].y = Some(5);

        let drawn_only = {
            let mut c = mixed.clone();
            c.kitties.remove(1); // same seed, kitty 2 absent entirely
            draw(&c).unwrap()
        };
        let with_pin = draw(&mixed).unwrap();

        let pinned = with_pin.iter().find(|s| s.kitty == 2).unwrap();
        assert_eq!(pinned.position, Position::new(7, 5));
        assert!(!pinned.drawn);
        assert_eq!(pinned.category, StartCategory::Interior);

        // An explicit kitty consumes zero draws, so the pin changes the
        // draw only through the occupied set: every drawn kitty keeps its
        // CATEGORY (same v1 sequence), and kitties outside the pinned
        // tile's category (interior here) keep their exact position —
        // their free lists never saw the pin.
        for s in &drawn_only {
            let same = with_pin.iter().find(|w| w.kitty == s.kitty).unwrap();
            assert_eq!(
                s.category, same.category,
                "pinning kitty 2 shifted kitty {}'s category draw",
                s.kitty
            );
            assert_ne!(same.position, Position::new(7, 5), "drawn onto the pin");
            if s.category != StartCategory::Interior {
                assert_eq!(
                    s.position, same.position,
                    "the interior pin reached kitty {}'s {:?} free list",
                    s.kitty, s.category
                );
            }
        }

        // ...and its tile is genuinely blocked: pin a tile a kitty would
        // have drawn and that kitty must land elsewhere, still lawful.
        let victim = drawn_only[0];
        let mut blocking = share_config(16, 12, 11, 4, shares);
        blocking.kitties[1].x = Some(victim.position.x);
        blocking.kitties[1].y = Some(victim.position.y);
        let blocked = draw(&blocking).unwrap();
        let moved = blocked.iter().find(|s| s.kitty == victim.kitty).unwrap();
        assert_ne!(moved.position, victim.position, "occupied tile re-drawn");
        assert_eq!(moved.category, victim.category, "resample stays in category");
    }

    #[test]
    fn knob_off_all_explicit_classifies_without_touching_any_rng() {
        let mut config = Config::default();
        config.world.width = 8;
        config.world.height = 8;
        config.kitties = vec![
            KittyConfig::new(1, "a", 0, 0, "needs_driven"),
            KittyConfig::new(2, "b", 3, 3, "needs_driven"),
        ];
        let starts = draw(&config).unwrap();
        assert_eq!(starts[0].category, StartCategory::Corner);
        assert!(!starts[0].drawn);
        assert_eq!(starts[1].category, StartCategory::Interior);
    }
}
