#!/usr/bin/env python3
"""Guards for split_read.py (PREREG.md buckets).

Event rows are real payloads copied verbatim from the refusal-baseline
raws (results-raw/refusal-baseline-close-203824.json); the position
snapshots are constructed, because the geometry boundaries under test
need exact placement and no collected raw existed when these guards
were written.
"""

import unittest

from split_read import bucket, score, target_id

# Real rows, verbatim (ticks rebased into the fixture window below).
SLEEP_WITH = {"kitty_id": 2, "proposed": {"action": "sleep", "with": 5},
              "tick": 100, "absorbed": True, "reason": "partner_absent"}
PLAY_KITTY = {"kitty_id": 4,
              "proposed": {"action": "play", "target": "kitty", "id": 5},
              "tick": 101, "absorbed": False, "reason": "partner_absent"}
GROOM = {"kitty_id": 5, "proposed": {"action": "groom", "target": 3},
         "tick": 102, "absorbed": False, "reason": "partner_absent"}


def raw(events, positions):
    return {"window": {"start_tick": 100, "end_tick": 110},
            "names": {"2": "Biscuit", "4": "Kittybear", "5": "Clementine"},
            "events": events,
            "positions": positions,
            "config": {"vision": {"radius": 4}}}


class TargetId(unittest.TestCase):
    def test_three_real_shapes(self):
        self.assertEqual(target_id(SLEEP_WITH["proposed"]), 5)
        self.assertEqual(target_id(PLAY_KITTY["proposed"]), 5)
        self.assertEqual(target_id(GROOM["proposed"]), 3)


class Bucket(unittest.TestCase):
    def test_orthogonal_neighbour_is_race(self):
        self.assertEqual(bucket([5, 5], [5, 6], 4), "race")

    def test_same_tile_is_race(self):
        self.assertEqual(bucket([5, 5], [5, 5], 4), "race")

    def test_diagonal_neighbour_is_seen_not_race(self):
        # Manhattan 2, d^2 = 2: inside the disc, outside adjacency.
        self.assertEqual(bucket([5, 5], [6, 6], 4), "seen")

    def test_disc_edge_counts_as_seen(self):
        # (4,0): d^2 = 16 = r^2 -- on the edge is seen (grid.rs:80).
        self.assertEqual(bucket([0, 0], [4, 0], 4), "seen")

    def test_just_past_the_disc_is_fog(self):
        # (4,1): d^2 = 17 > 16.
        self.assertEqual(bucket([0, 0], [4, 1], 4), "fog")


class Score(unittest.TestCase):
    def test_joins_on_equal_tick_and_buckets(self):
        positions = {
            "100": {"2": [5, 5], "5": [5, 6]},          # race
            "101": {"4": [0, 0], "5": [3, 3]},          # d^2=18 -> fog
            "102": {"5": [10, 10], "3": [12, 10]},      # d^2=4 -> seen
        }
        sc = score(raw([SLEEP_WITH, PLAY_KITTY, GROOM], positions))
        self.assertEqual(sc["joined"], 3)
        self.assertEqual(sc["buckets"]["race"]["rows"], 1)
        self.assertEqual(sc["buckets"]["fog"]["rows"], 1)
        self.assertEqual(sc["buckets"]["seen"]["rows"], 1)
        self.assertEqual(sc["buckets"]["race"]["absorbed"], 1)
        self.assertEqual(sc["buckets"]["seen"]["absorbed"], 0)

    def test_missing_snapshot_is_dropped_never_guessed(self):
        positions = {"100": {"2": [5, 5], "5": [5, 6]}}
        sc = score(raw([SLEEP_WITH, PLAY_KITTY], positions))
        self.assertEqual(sc["joined"], 1)
        self.assertEqual(sc["dropped_no_snapshot"], 1)

    def test_rows_outside_window_excluded(self):
        late = dict(SLEEP_WITH, tick=111)
        sc = score(raw([late], {"111": {"2": [5, 5], "5": [5, 6]}}))
        self.assertEqual(sc["partner_absent_rows"], 0)

    def test_radius_read_from_stored_config(self):
        # Same geometry, radius 2: (0,0)->(3,3) stays fog, and a d^2=4
        # pair sits on the smaller disc's edge.
        positions = {"100": {"2": [0, 0], "5": [2, 0]}}
        r = raw([SLEEP_WITH], positions)
        r["config"]["vision"]["radius"] = 2
        sc = score(r)
        self.assertEqual(sc["buckets"]["seen"]["rows"], 1)


if __name__ == "__main__":
    unittest.main()
