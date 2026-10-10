"""Observation schema 6 layout (spec 058,
contracts/observation-v6.md): self 109 | kitty 4 x 58 | chow 2 x 6 |
water 2 x 5 | sunbeam 2 x 7 | critter 4 x 11 = 421. No clock cell and
no clock token (spec 058 FR-010); six token types. Every spatial
feature is the Manhattan spatial group (bearing pair, d/40 clamped,
log1p(d)/log1p(400)); walls replace fractional self-position; the
identity block replaces the traits; kitty rows carry bath only
(five-of-six). Pure layout constants, shared by the numpy forward and
the generator.
"""
WIDTHS = [("self", 109), ("kitty", 58), ("chow", 6), ("water", 5),
          ("sunbeam", 7), ("critter", 11)]
COUNTS = {"self": 1, "kitty": 4, "chow": 2, "water": 2, "sunbeam": 2,
          "critter": 4}
TYPE_ROW = {"self": [0], "kitty": [1] * 4, "chow": [2], "water": [3],
            "sunbeam": [4], "critter": [5] * 4}
N_TYPE_ROWS = 6
OBS_DIM = sum(w * COUNTS[n] for n, w in WIDTHS)
assert OBS_DIM == 421
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
# Block offsets derived from WIDTHS x COUNTS (one row per slot, self
# excluded): kitty 109.., chow 341.., water 353.., sunbeam 363..,
# critter 377..; the last block ends at 421 (no clock cell).
BLOCKS = []
_off = 109
for _name, _w in WIDTHS[1:]:
    for _j in range(COUNTS[_name]):
        BLOCKS.append((_off, _w))
        _off += _w
assert BLOCKS[-1][0] + BLOCKS[-1][1] == 421 == OBS_DIM
# Named spans the generator's stress rows zero out.
KITTY_SPAN = (109, 109 + 4 * 58)        # 109..341
ELEMENT_SPAN = (341, 377)               # chow, water, sunbeam
CRITTER_SPAN = (377, 421)
KITTY_W = 58

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
# Self block v6: needs 6, happiness, walls 4, activity 7, partner,
# in-sunbeam, in-water, progress, distress 6, pursuit 2, identity 14;
# then scene age, own message block, element memory (present, spatial
# group, staleness), waypoint bearing 2, dirt reserve 2.
SELF_NEEDS, SELF_HAPPINESS, SELF_WALLS, SELF_ACTIVITY = 0, 6, 7, 11
SELF_PARTNERED, SELF_IN_SUNBEAM, SELF_IN_WATER = 18, 19, 20
IDENTITY_BLOCK = 6 + 1 + 1 + 6
SELF_IDENTITY = 6 + 1 + 4 + 7 + 1 + 1 + 1 + 1 + 6 + 2
SELF_CORE = SELF_IDENTITY + IDENTITY_BLOCK
SELF_SCENE_AGE = SELF_CORE
SELF_MSG_BLOCK = SELF_SCENE_AGE + 1
SELF_MEMORY = SELF_MSG_BLOCK + MSG_BLOCK
MEMORY_SLOT = 6  # present, bearing 2, linear, log, staleness
SELF_WAYPOINT = SELF_MEMORY + len(ELEMENT_KINDS) * MEMORY_SLOT
SELF_DIRT_RESERVE = SELF_WAYPOINT + 2
assert SELF_DIRT_RESERVE + 2 == dict(WIDTHS)["self"]
# Kitty row v6: present, spatial group 4, bath, activity 7, partnered,
# is-my-target, then the 049 tail cells (five-of-six: no needs other
# than bath, no happiness).
ROW_PRESENT, ROW_BEARING, ROW_LINEAR, ROW_LOG, ROW_BATH = 0, 1, 3, 4, 5
ROW_ACTIVITY, ROW_PARTNERED, ROW_IS_TARGET = 6, 13, 14
KITTY_CORE = 1 + 4 + 1 + 7 + 1 + 1
ROW_WATER_BIT = KITTY_CORE
ROW_SUNBEAM_BIT = ROW_WATER_BIT + 1
ROW_SCENE_AGE = ROW_SUNBEAM_BIT + 1
ROW_MSG_BLOCK = ROW_SCENE_AGE + 1
ROW_INTENSITY = ROW_MSG_BLOCK + MSG_BLOCK
ROW_ANSWERS_ME = ROW_INTENSITY + len(WANT_KINDS)
assert ROW_ANSWERS_ME + len(HERE_KINDS) == KITTY_W
# Element slots: present, then the spatial group, in every kind.
SLOT_PRESENT, SLOT_BEARING, SLOT_LINEAR, SLOT_LOG = 0, 1, 3, 4
# Normalisers (observe.rs): scene age / 24, memory staleness / 40,
# spatial near / 40, spatial far log1p / log1p(400).
SCENE_AGE_NORMALISER, STALENESS_NORMALISER = 24.0, 40.0
NEAR_DISTANCE_NORMALISER, FAR_DISTANCE_NORMALISER = 40.0, 400.0
