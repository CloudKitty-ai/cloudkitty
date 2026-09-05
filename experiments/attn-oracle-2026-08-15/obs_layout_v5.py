"""Observation schema 5 layout (spec 049, contracts/observation-v5.md):
self 85 | kitty 4 x 63 | chow 2 x 5 | water 2 x 4 | sunbeam 2 x 6 |
critter 4 x 10 | clock 1 = 408 (404 before the kitty-row sunbeam bit,
owner ruled 2026-09-04). The message-kind token group of schema 4
is gone (repetition rides the kitty rows); seven token types remain.
Pure layout constants, shared by the numpy forward and the generator.
"""
WIDTHS = [("self", 85), ("kitty", 63), ("chow", 5), ("water", 4),
          ("sunbeam", 6), ("critter", 10), ("clock", 1)]
COUNTS = {"self": 1, "kitty": 4, "chow": 2, "water": 2, "sunbeam": 2,
          "critter": 4, "clock": 1}
TYPE_ROW = {"self": [0], "kitty": [1] * 4, "chow": [2], "water": [3],
            "sunbeam": [4], "critter": [5] * 4, "clock": [6]}
N_TYPE_ROWS = 7
OBS_DIM = sum(w * COUNTS[n] for n, w in WIDTHS)
assert OBS_DIM == 408
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
# Block offsets derived from WIDTHS x COUNTS (one row per slot, self and
# clock excluded): kitty 85.., chow 337.., water 347.., sunbeam 355..,
# critter 367..; the last block ends at 407.
BLOCKS = []
_off = 85
for _name, _w in WIDTHS[1:-1]:
    for _j in range(COUNTS[_name]):
        BLOCKS.append((_off, _w))
        _off += _w
assert BLOCKS[-1][0] + BLOCKS[-1][1] == 407 == OBS_DIM - 1
# Named spans the generator's stress rows zero out.
KITTY_SPAN = (85, 85 + 4 * 63)          # 85..337
ELEMENT_SPAN = (337, 367)               # chow, water, sunbeam
CRITTER_SPAN = (367, 407)
KITTY_W = 63

# Intra-block offsets, the engine's `observe.rs::offsets` in Python. Built
# by the same sums the engine uses (never restated as literals) so a
# reader like schema_check.py names a cell instead of counting to it. Kind
# orders are serde snake_case, the spelling a snapshot / meow carries.
HEAD_KINDS = ["want_eat", "want_drink", "mew", "want_play", "want_cuddle",
              "purr", "want_bath", "want_sleep", "here_food", "here_water",
              "here_critter", "here_sunbeam", "chirp", "trill", "ekekek"]
WANT_KINDS = ["want_eat", "want_drink", "want_play", "want_cuddle",
              "want_bath", "want_sleep"]
HERE_KINDS = ["here_food", "here_water", "here_critter", "here_sunbeam"]
WANT_FOR_HERE = {"here_food": "want_eat", "here_water": "want_drink",
                 "here_sunbeam": "want_sleep", "here_critter": "want_play"}
NEED_KINDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
ELEMENT_KINDS = ["water", "chow", "bug", "greeble", "sunbeam"]  # ElementType::ALL
MSG_BLOCK = 2 * len(HEAD_KINDS)                                  # recency, rate
# Self block: schema 4 (needs 6, happiness, pos 2, activity 7, partner,
# in-sunbeam, in-water, progress, distress 6, pursuit 2, traits 6) then
# scene age, own message block, element memory (present, dx, dy, staleness).
SELF_NEEDS, SELF_HAPPINESS, SELF_POS, SELF_ACTIVITY = 0, 6, 7, 9
SELF_PARTNERED, SELF_IN_SUNBEAM, SELF_IN_WATER = 16, 17, 18
SELF_SCHEMA_4 = 6 + 1 + 2 + 7 + 1 + 1 + 1 + 1 + 6 + 2 + 6
SELF_SCENE_AGE = SELF_SCHEMA_4
SELF_MSG_BLOCK = SELF_SCENE_AGE + 1
SELF_MEMORY = SELF_MSG_BLOCK + MSG_BLOCK
MEMORY_SLOT = 4
assert SELF_MEMORY + len(ELEMENT_KINDS) * MEMORY_SLOT == dict(WIDTHS)["self"]
# Kitty row: schema 4 (present, dx, dy, distance, needs 6, happiness,
# activity 7, partnered, is-my-target) then the 049 cells.
ROW_PRESENT, ROW_DX, ROW_DY, ROW_DIST, ROW_NEEDS, ROW_HAPPINESS = 0, 1, 2, 3, 4, 10
ROW_ACTIVITY, ROW_PARTNERED, ROW_IS_TARGET = 11, 18, 19
KITTY_SCHEMA_4 = 1 + 2 + 1 + 6 + 1 + 7 + 1 + 1
ROW_WATER_BIT = KITTY_SCHEMA_4
ROW_SUNBEAM_BIT = ROW_WATER_BIT + 1
ROW_SCENE_AGE = ROW_SUNBEAM_BIT + 1
ROW_MSG_BLOCK = ROW_SCENE_AGE + 1
ROW_INTENSITY = ROW_MSG_BLOCK + MSG_BLOCK
ROW_ANSWERS_ME = ROW_INTENSITY + len(WANT_KINDS)
assert ROW_ANSWERS_ME + len(HERE_KINDS) == KITTY_W
# Element slots: present, dx, dy, distance first in every kind.
SLOT_PRESENT, SLOT_DX, SLOT_DY, SLOT_DIST = 0, 1, 2, 3
# Normalisers (observe.rs): scene age / 24, memory staleness / 40.
SCENE_AGE_NORMALISER, STALENESS_NORMALISER = 24.0, 40.0
