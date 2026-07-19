//! Tiles, positions and directions.
//!
//! The grid uses screen coordinates: `x` grows east, `y` grows south, so North is
//! `y - 1`. Adjacency is Chebyshev distance <= 1 (the eight surrounding tiles plus
//! the tile itself), matching the spec's definition of "friend nearby".

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

    /// Chebyshev distance: the number of king-moves between two tiles.
    pub fn chebyshev_distance(&self, other: &Position) -> u32 {
        let dx = self.x.abs_diff(other.x);
        let dy = self.y.abs_diff(other.y);
        dx.max(dy)
    }

    /// Adjacent means "close enough to interact with", which includes sharing a tile.
    pub fn is_adjacent(&self, other: &Position) -> bool {
        self.chebyshev_distance(other) <= 1
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
        let a = Position::new(5, 5);
        assert_eq!(a.chebyshev_distance(&Position::new(6, 6)), 1);
        assert_eq!(a.chebyshev_distance(&Position::new(5, 5)), 0);
        assert_eq!(a.chebyshev_distance(&Position::new(8, 6)), 3);
    }

    #[test]
    fn adjacency_includes_same_tile_and_diagonals() {
        let a = Position::new(2, 2);
        assert!(a.is_adjacent(&Position::new(2, 2)));
        assert!(a.is_adjacent(&Position::new(3, 3)));
        assert!(a.is_adjacent(&Position::new(1, 2)));
        assert!(!a.is_adjacent(&Position::new(4, 2)));
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
