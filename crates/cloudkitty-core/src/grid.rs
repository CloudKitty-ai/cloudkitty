//! Tiles, positions and directions.
//!
//! The grid uses screen coordinates: `x` grows east, `y` grows south, so North is
//! `y - 1`. Adjacency is Manhattan distance <= 1 (the four compass neighbours plus
//! the tile itself — spec 009): interaction range matches the strictly 4-way
//! movement, so what a kitty can *do* is exactly what it can *walk*. Manhattan is
//! likewise the metric for every decision distance; Chebyshev remains only for
//! spawn spreading, where king-move spacing is an aesthetic, not a walk.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Position {
    pub x: u32,
    pub y: u32,
}

impl Position {
    pub fn new(x: u32, y: u32) -> Self {
        Self { x, y }
    }

    /// Chebyshev distance: the number of king-moves between two tiles. Kitties
    /// cannot king-move, so this is *not* a walk cost — its one remaining
    /// consumer is spawn spreading (`spawn.rs`), where it spaces same-type
    /// elements apart for looks. Decisions use [`Self::manhattan_distance`].
    pub fn chebyshev_distance(&self, other: &Position) -> u32 {
        let dx = self.x.abs_diff(other.x);
        let dy = self.y.abs_diff(other.y);
        dx.max(dy)
    }

    /// Manhattan distance: the number of 4-way steps between two tiles — the
    /// true walking distance, since `Direction` is strictly N/E/S/W.
    pub fn manhattan_distance(&self, other: &Position) -> u32 {
        self.x.abs_diff(other.x) + self.y.abs_diff(other.y)
    }

    /// Adjacent means "close enough to interact with": the same tile or one of
    /// the four compass neighbours (spec 009). Diagonal tiles are out of range —
    /// a kitty cannot step diagonally, so it cannot reach diagonally either.
    pub fn is_adjacent(&self, other: &Position) -> bool {
        self.manhattan_distance(other) <= 1
    }

    /// The neighbouring tile in `dir`, or `None` when that would leave the grid.
    pub fn step(&self, dir: Direction, width: u32, height: u32) -> Option<Position> {
        let (x, y) = match dir {
            Direction::North => (self.x, self.y.checked_sub(1)?),
            Direction::South => (self.x, self.y + 1),
            Direction::West => (self.x.checked_sub(1)?, self.y),
            Direction::East => (self.x + 1, self.y),
        };
        if x < width && y < height {
            Some(Position { x, y })
        } else {
            None
        }
    }

    pub fn in_bounds(&self, width: u32, height: u32) -> bool {
        self.x < width && self.y < height
    }

    /// Squared Euclidean distance, `dx² + dy²`, in integers (spec 049
    /// FR-001). Never rooted: the vision disc compares it to `r²`, so no
    /// float ever enters a visibility verdict.
    pub fn euclid_sq(&self, other: &Position) -> u64 {
        let dx = u64::from(self.x.abs_diff(other.x));
        let dy = u64::from(self.y.abs_diff(other.y));
        // Saturating: a sum past u64 is past every r² that fits one, so
        // the verdict is right without widening the type.
        (dx * dx).saturating_add(dy * dy)
    }

    /// The vision rule (spec 049 FR-001): `other` is visible from `self`
    /// exactly when `dx² + dy² ≤ r²` — on the disc's edge counts as seen,
    /// integer arithmetic only. One rule for policies and built-ins alike;
    /// the fog view is its only caller in the engine.
    pub fn visible_from(&self, other: &Position, radius: u32) -> bool {
        let r = u64::from(radius);
        self.euclid_sq(other) <= r.saturating_mul(r)
    }
}

/// Whether two tiles lie in the same roam cell (spec 039): the world tiles
/// into `n`-sized cells anchored at the origin, so a tile's cell is its
/// quotient pair `(x / n, y / n)`. Worlds whose dimensions are not multiples
/// of `n` get smaller remainder cells along the far edges, and a world
/// smaller than `n` in a dimension is a single cell across it — all from
/// this one division, no edge cases. `n` is validated ≥ 2 at config load;
/// this predicate does not re-check.
pub fn same_roam_cell(a: Position, b: Position, n: u32) -> bool {
    (a.x / n, a.y / n) == (b.x / n, b.y / n)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Direction {
    North,
    East,
    South,
    West,
}

impl Direction {
    pub const ALL: [Direction; 4] = [
        Direction::North,
        Direction::East,
        Direction::South,
        Direction::West,
    ];

    /// The reverse of this direction (spec 024: the one step a chase
    /// sidestep must never take -- arcing around a blocker is routing,
    /// walking backwards is retreat).
    pub fn opposite(self) -> Direction {
        match self {
            Direction::North => Direction::South,
            Direction::South => Direction::North,
            Direction::East => Direction::West,
            Direction::West => Direction::East,
        }
    }

    /// The direction that moves `from` closest to `to`, or `None` when already there.
    /// Ties resolve to the larger axis gap, then to horizontal movement, so the
    /// choice is deterministic without consulting the RNG.
    pub fn toward(from: Position, to: Position) -> Option<Direction> {
        let dx = to.x as i64 - from.x as i64;
        let dy = to.y as i64 - from.y as i64;
        if dx == 0 && dy == 0 {
            return None;
        }
        if dx.abs() >= dy.abs() {
            Some(if dx > 0 {
                Direction::East
            } else {
                Direction::West
            })
        } else {
            Some(if dy > 0 {
                Direction::South
            } else {
                Direction::North
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chebyshev_treats_diagonals_as_one_step() {
        // Still shipped: spawn spreading spaces elements by king-moves.
        let a = Position::new(5, 5);
        assert_eq!(a.chebyshev_distance(&Position::new(6, 6)), 1);
        assert_eq!(a.chebyshev_distance(&Position::new(5, 5)), 0);
        assert_eq!(a.chebyshev_distance(&Position::new(8, 6)), 3);
    }

    #[test]
    fn manhattan_counts_the_actual_walk() {
        let a = Position::new(5, 5);
        assert_eq!(a.manhattan_distance(&Position::new(5, 5)), 0);
        assert_eq!(a.manhattan_distance(&Position::new(6, 5)), 1);
        assert_eq!(a.manhattan_distance(&Position::new(6, 6)), 2); // the diagonal is two steps
        assert_eq!(a.manhattan_distance(&Position::new(8, 6)), 4);
        assert_eq!(a.manhattan_distance(&Position::new(2, 1)), 7); // symmetric under order
        assert_eq!(Position::new(2, 1).manhattan_distance(&a), 7);
    }

    #[test]
    fn adjacency_is_the_own_tile_plus_the_four_compass_neighbours() {
        // The spec 009 truth table, verbatim.
        let a = Position::new(2, 2);
        assert!(a.is_adjacent(&Position::new(2, 2)), "own tile is in range");
        assert!(a.is_adjacent(&Position::new(1, 2)), "west");
        assert!(a.is_adjacent(&Position::new(3, 2)), "east");
        assert!(a.is_adjacent(&Position::new(2, 1)), "north");
        assert!(a.is_adjacent(&Position::new(2, 3)), "south");
        assert!(
            !a.is_adjacent(&Position::new(3, 3)),
            "diagonal is out of range (was in range before 009)"
        );
        assert!(!a.is_adjacent(&Position::new(1, 1)));
        assert!(!a.is_adjacent(&Position::new(4, 2)), "two steps away");
    }

    #[test]
    fn stepping_off_the_grid_yields_none() {
        let corner = Position::new(0, 0);
        assert_eq!(corner.step(Direction::North, 10, 10), None);
        assert_eq!(corner.step(Direction::West, 10, 10), None);
        assert_eq!(
            corner.step(Direction::South, 10, 10),
            Some(Position::new(0, 1))
        );

        let far = Position::new(9, 9);
        assert_eq!(far.step(Direction::East, 10, 10), None);
        assert_eq!(far.step(Direction::South, 10, 10), None);
    }

    #[test]
    fn the_vision_disc_is_euclidean_and_closed_on_its_edge() {
        // Spec 049 US1 scenarios 1-2 at r = 5: (3, 4) is ON the edge
        // (9 + 16 = 25 ≤ 25) and seen although seven steps away; (5, 1)
        // is six steps away and unseen (26 > 25). The Manhattan diamond
        // would rule the opposite on both.
        let me = Position::new(10, 10);
        let edge = Position::new(13, 14);
        let outside = Position::new(15, 11);
        assert_eq!(me.euclid_sq(&edge), 25);
        assert_eq!(me.euclid_sq(&outside), 26);
        assert!(me.visible_from(&edge, 5), "the disc's edge is seen");
        assert!(!me.visible_from(&outside, 5), "26 > 25 is unseen");
        assert_eq!(me.manhattan_distance(&edge), 7);
        assert_eq!(me.manhattan_distance(&outside), 6);
        // Symmetric, and the own tile is inside every disc.
        assert!(edge.visible_from(&me, 5));
        assert!(me.visible_from(&me, 0));
        // Integer arithmetic survives large offsets without overflow.
        let far = Position::new(u32::MAX, u32::MAX);
        assert!(!Position::new(0, 0).visible_from(&far, u32::MAX - 1));
    }

    #[test]
    fn toward_picks_the_dominant_axis() {
        let from = Position::new(5, 5);
        assert_eq!(
            Direction::toward(from, Position::new(9, 6)),
            Some(Direction::East)
        );
        assert_eq!(
            Direction::toward(from, Position::new(5, 1)),
            Some(Direction::North)
        );
        assert_eq!(Direction::toward(from, from), None);
    }

    /// Spec 039 FR-002: the roam partition assigns every tile exactly one
    /// cell. "Exactly one" is arithmetic (a quotient pair is a function of
    /// the tile), so the real content here is the cell CENSUS: the counts
    /// and shapes that fall out of integer division match what the spec
    /// promises for each geometry.
    #[test]
    fn roam_partition_covers_every_tile_exactly_once() {
        // 20x20 / n=4: the served geometry — exactly 25 cells of 16 tiles.
        let census = |w: u32, h: u32, n: u32| {
            let mut cells = std::collections::BTreeMap::new();
            for x in 0..w {
                for y in 0..h {
                    *cells.entry((x / n, y / n)).or_insert(0u32) += 1;
                }
            }
            cells
        };

        let served = census(20, 20, 4);
        assert_eq!(served.len(), 25);
        assert!(served.values().all(|&c| c == 16));

        // 26x26 / n=4: 4x4 interior, 4x2 + 2x4 edge strips, one 2x2 corner
        // (spec US2 scenario 1). 49 cells, tile counts partition 26*26.
        let ragged = census(26, 26, 4);
        assert_eq!(ragged.len(), 49);
        assert_eq!(ragged.values().sum::<u32>(), 26 * 26);
        assert_eq!(ragged.values().filter(|&&c| c == 16).count(), 36);
        assert_eq!(ragged.values().filter(|&&c| c == 8).count(), 12);
        assert_eq!(ragged.values().filter(|&&c| c == 4).count(), 1);

        // 5x5 / n=8: the whole world is one cell (spec US2 scenario 3).
        let tiny = census(5, 5, 8);
        assert_eq!(tiny.len(), 1);
        assert_eq!(tiny[&(0, 0)], 25);
    }

    #[test]
    fn roam_same_cell_matches_the_quotient_partition() {
        // The predicate agrees with the census definition on every pair of
        // a 26x26 world — including remainder-strip pairs and cross-boundary
        // neighbours (x=23 and x=24 are adjacent tiles in different cells).
        let n = 4;
        assert!(same_roam_cell(
            Position::new(24, 25),
            Position::new(25, 24),
            n
        ));
        assert!(!same_roam_cell(
            Position::new(23, 0),
            Position::new(24, 0),
            n
        ));
        for &(ax, ay, bx, by) in &[(0, 0, 3, 3), (0, 0, 4, 0), (19, 19, 16, 16), (12, 3, 12, 4)] {
            let a = Position::new(ax, ay);
            let b = Position::new(bx, by);
            assert_eq!(
                same_roam_cell(a, b, n),
                (ax / n, ay / n) == (bx / n, by / n),
                "predicate disagrees with quotient partition at {a:?} {b:?}"
            );
        }
    }
}
