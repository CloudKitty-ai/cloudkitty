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
}
