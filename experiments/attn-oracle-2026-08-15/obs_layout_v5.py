"""Observation schema 5 layout (spec 049, contracts/observation-v5.md):
self 85 | kitty 4 x 62 | chow 2 x 5 | water 2 x 4 | sunbeam 2 x 6 |
critter 4 x 10 | clock 1 = 404. The message-kind token group of schema 4
is gone (repetition rides the kitty rows); seven token types remain.
Pure layout constants, shared by the numpy forward and the generator.
"""
WIDTHS = [("self", 85), ("kitty", 62), ("chow", 5), ("water", 4),
          ("sunbeam", 6), ("critter", 10), ("clock", 1)]
COUNTS = {"self": 1, "kitty": 4, "chow": 2, "water": 2, "sunbeam": 2,
          "critter": 4, "clock": 1}
TYPE_ROW = {"self": [0], "kitty": [1] * 4, "chow": [2], "water": [3],
            "sunbeam": [4], "critter": [5] * 4, "clock": [6]}
N_TYPE_ROWS = 7
OBS_DIM = sum(w * COUNTS[n] for n, w in WIDTHS)
assert OBS_DIM == 404
# Menu 39 at kitty_slots 4 (ActionCodec::v2): Move 0-3, RestSolo 4,
# RestWith 5-8, SleepSolo 9, SleepWith 10-13, GroomSelf 14, GroomKitty
# 15-18, Eat 19, Drink 20, ChaseCritter 21-24, ChaseKitty 25-28, PlaySolo
# 29, PlayCritter 30-33, PlayKitty 34-37, Idle 38.
N_ACT = 39
DENSE_ACT = [0, 1, 2, 3, 4, 9, 14, 19, 20, 29, 38]
KITTY_MENU = [[5 + k, 10 + k, 15 + k, 25 + k, 34 + k] for k in range(4)]
CRIT_MENU = [[21 + j, 30 + j] for j in range(4)]
N_HEAD = 16
N_LOGITS = N_ACT + N_HEAD
assert N_LOGITS == 55
# token positions: self 0, kitty 1..5, chow 5..7, water 7..9, sunbeam
# 9..11, critter 11..15, clock 15
KITTY_TOK = slice(1, 5)
CRIT_TOK = slice(11, 15)
BLOCKS = ([(85 + 62 * k, 62) for k in range(4)] + [(333 + 5 * j, 5) for j in range(2)]
          + [(343 + 4 * j, 4) for j in range(2)] + [(351 + 6 * j, 6) for j in range(2)]
          + [(363 + 10 * j, 10) for j in range(4)])
assert BLOCKS[-1][0] + BLOCKS[-1][1] == 403
