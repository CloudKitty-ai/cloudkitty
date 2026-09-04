//! Spec 049 FR-023 as ruled 2026-09-03 (T088): the blind scripted cat's
//! search is a LATTICE SERPENTINE TOUR. Waypoints sit on a square lattice
//! inset `floor(r / √2)` from each wall with neighbouring waypoints at most
//! `floor(r · √2)` apart -- the two constraints for Euclidean-disc coverage
//! of a rectangle: a corner tile is within `r` of the corner waypoint iff
//! the inset `a` has `a · √2 ≤ r`, and every interior tile is within `r` of
//! the nearest waypoint iff the cell's half-diagonal is, i.e. spacing
//! `≤ r · √2`. Visited in boustrophedon order and back (the cycle is the
//! row-snake forward then reversed, so no long return crossing), so every
//! tile of ANY rectangle at ANY radius is inside the disc at some waypoint
//! by construction -- `coverage_is_complete_by_construction` proves it
//! exhaustively over the sizes and radii that matter. The heading rule it
//! replaces covered a function of r versus world size (the 20×20 core left
//! unseen was 100/36/4/0 tiles at r = 2/3/4/5), which would have made the
//! step-5 radius screen measure the sweep instead of vision.
//!
//! State: one index per cat into the cycle (`Kitty::explore_waypoint`),
//! set at generation to `id mod cycle length` (cats spread over the tour;
//! no RNG draw -- the ruling allows at most one) and advanced by the
//! engine in the environment phase when the cat stands on its waypoint or
//! beside it while another cat occupies it. The exploring turn takes one
//! step toward the current waypoint with the existing step rule.

use crate::grid::Position;

/// A world's tour lattice: the waypoint coordinates per axis.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Lattice {
    xs: Vec<u32>,
    ys: Vec<u32>,
}

/// The waypoint coordinates along one axis of length `len` at radius `r`:
/// inset `a = floor(r / √2)`, then `n = ceil(span / s) + 1` evenly spaced
/// points over `span = len − 1 − 2a` with `s = floor(r · √2)`, rounded
/// half up. A span that does not fit two waypoints collapses to the
/// axis's middle tile (a narrow world).
fn axis(len: u32, radius: u32) -> Vec<u32> {
    let inset = ((radius as f64) / std::f64::consts::SQRT_2).floor() as u32;
    let spacing = ((radius as f64) * std::f64::consts::SQRT_2)
        .floor()
        .max(1.0) as u32;
    let last = len.saturating_sub(1);
    if last < 2 * inset + 1 {
        return vec![last / 2];
    }
    let span = last - 2 * inset;
    let n = span.div_ceil(spacing) + 1;
    (0..n)
        .map(|k| inset + ((k as f64) * (span as f64) / ((n - 1) as f64) + 0.5).floor() as u32)
        .collect()
}

impl Lattice {
    pub fn for_world(width: u32, height: u32, radius: u32) -> Lattice {
        Lattice {
            xs: axis(width, radius),
            ys: axis(height, radius),
        }
    }

    pub fn xs(&self) -> &[u32] {
        &self.xs
    }

    pub fn ys(&self) -> &[u32] {
        &self.ys
    }

    /// The boustrophedon sequence: rows by ascending y, even rows left to
    /// right, odd rows right to left.
    fn snake_len(&self) -> u32 {
        (self.xs.len() * self.ys.len()) as u32
    }

    fn snake(&self, i: u32) -> Position {
        let nx = self.xs.len() as u32;
        let row = i / nx;
        let col = i % nx;
        let x = if row.is_multiple_of(2) {
            self.xs[col as usize]
        } else {
            self.xs[(nx - 1 - col) as usize]
        };
        Position::new(x, self.ys[row as usize])
    }

    /// The tour cycle: the snake forward, then back through its interior
    /// (`2N − 2` positions for `N ≥ 2` waypoints; 1 for a single one).
    pub fn cycle_len(&self) -> u32 {
        let n = self.snake_len();
        if n >= 2 {
            2 * n - 2
        } else {
            1
        }
    }

    /// The waypoint at cycle position `index` (taken modulo the cycle, so
    /// an index saved under another radius still names a tile).
    pub fn waypoint(&self, index: u32) -> Position {
        let n = self.snake_len();
        let i = index % self.cycle_len();
        if i < n {
            self.snake(i)
        } else {
            self.snake(2 * n - 2 - i)
        }
    }

    /// Where a cat starts the tour: spread by id, no draw.
    pub fn start_index(&self, kitty_id: u32) -> u32 {
        kitty_id % self.cycle_len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_served_and_compiled_worlds_lattices_are_the_ruled_ones() {
        assert_eq!(Lattice::for_world(20, 20, 5).xs(), &[3, 10, 16]);
        assert_eq!(Lattice::for_world(32, 32, 5).xs(), &[3, 9, 16, 22, 28]);
        assert_eq!(Lattice::for_world(20, 20, 4).xs(), &[2, 7, 12, 17]);
        assert_eq!(Lattice::for_world(20, 20, 3).xs(), &[2, 6, 10, 13, 17]);
        assert_eq!(
            Lattice::for_world(20, 20, 2).xs(),
            &[1, 3, 5, 7, 9, 10, 12, 14, 16, 18]
        );
    }

    /// The two constraints are the whole argument; this checks the
    /// conclusion tile by tile for every size and radius the prereg can
    /// screen, on rectangles too.
    #[test]
    fn coverage_is_complete_by_construction() {
        for (w, h) in [
            (20, 20),
            (32, 32),
            (24, 24),
            (8, 8),
            (5, 5),
            (3, 9),
            (40, 12),
            (13, 31),
        ] {
            for r in 2..=8u32 {
                let lattice = Lattice::for_world(w, h, r);
                let points: Vec<Position> = (0..lattice.cycle_len())
                    .map(|i| lattice.waypoint(i))
                    .collect();
                for x in 0..w {
                    for y in 0..h {
                        let t = Position::new(x, y);
                        assert!(
                            points.iter().any(|p| p.visible_from(&t, r)),
                            "{w}x{h} r={r}: tile {t:?} is outside every waypoint's disc ({:?} x {:?})",
                            lattice.xs(),
                            lattice.ys()
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn the_cycle_is_the_snake_forward_then_back_with_no_repeats_at_the_turns() {
        let l = Lattice::for_world(20, 20, 5);
        assert_eq!(l.cycle_len(), 16);
        let snake: Vec<(u32, u32)> = (0..9).map(|i| (l.waypoint(i).x, l.waypoint(i).y)).collect();
        assert_eq!(
            snake,
            [
                (3, 3),
                (10, 3),
                (16, 3),
                (16, 10),
                (10, 10),
                (3, 10),
                (3, 16),
                (10, 16),
                (16, 16)
            ]
        );
        let back: Vec<(u32, u32)> = (9..16)
            .map(|i| (l.waypoint(i).x, l.waypoint(i).y))
            .collect();
        assert_eq!(
            back,
            [
                (10, 16),
                (3, 16),
                (3, 10),
                (10, 10),
                (16, 10),
                (16, 3),
                (10, 3)
            ]
        );
        assert_eq!(l.waypoint(16), l.waypoint(0), "the cycle wraps");
        // Every step of the cycle is a lattice neighbour: no crossing.
        for i in 0..l.cycle_len() {
            let a = l.waypoint(i);
            let b = l.waypoint(i + 1);
            assert!(
                (a.x == b.x) ^ (a.y == b.y),
                "consecutive waypoints share exactly one axis: {a:?} -> {b:?}"
            );
        }
        assert_eq!(l.start_index(1), 1);
        assert_eq!(l.start_index(17), 1, "spread by id modulo the cycle");
        let single = Lattice::for_world(3, 3, 5);
        assert_eq!(single.cycle_len(), 1);
        assert_eq!(single.waypoint(7), Position::new(1, 1));
    }
}
