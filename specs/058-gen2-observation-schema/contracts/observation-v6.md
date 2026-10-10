# Contract: Observation schema v6 (and global state v2)

Normative layout for `OBSERVATION_SCHEMA_VERSION = 6`. The implement
phase's `schema_six_pins.rs` asserts every number here literally;
`contracts/observation-v5.md` (spec 049) remains the v5 record.

## Conventions

- **Spatial cell group** (4 cells, every entity reference):

  | cell | formula | notes |
  |---|---|---|
  | bearing-x | dx / d | d = \|dx\| + \|dy\| (Manhattan); 0.0 when d = 0 |
  | bearing-y | dy / d | 0.0 when d = 0; \|bx\| + \|by\| = 1 when d > 0 |
  | linear | min(d / 40, 1) | walk-cost near field; frozen literal 40 |
  | log | log1p(d) / log1p(400) | far-field order; frozen literal 400 |

  dx = target.x − me.x, dy = target.y − me.y, in tiles. NEVER clamped
  or validated against the vision radius: a visible entity's Manhattan
  distance exceeds a Euclidean radius routinely (dx=2, dy=3 inside
  r=4), and heard positions reach radius + digest window (FR-001a).
- Time normalizers unchanged: scene age /24, staleness /40,
  progress = elapsed/min bound (spec 049 values).
- All cells f32; one-hots and bits are 0.0/1.0.

## Self block — width 109, offsets 0-108

| offset | cells | content |
|---|---|---|
| 0–5 | 6 | own needs /100, `NeedKind::ALL` order (Eat, Drink, Sleep, Play, Cuddle, Bath) |
| 6 | 1 | happiness /100 |
| 7–10 | 4 | distance-to-wall N, E, S, W: tiles to each wall, linear /40 clamped at 1 — REPLACES fractional position; corner cats carry two zeros (zero is a real distance, no sentinel) |
| 11–17 | 7 | activity one-hot |
| 18 | 1 | social (partnered) flag |
| 19 | 1 | in-sunbeam bit |
| 20 | 1 | in-water bit |
| 21 | 1 | activity progress |
| 22–27 | 6 | distress flags |
| 28–29 | 2 | pursuit |
| 30–43 | 14 | **identity block**: 30–35 need-rate multipliers (`need_rate_for / reference_need_rate`, clamp [0,4]); 36 comfort slack (ticks /40, clamp [0,1]); 37 consent line (/100); 38–43 favourite weights (`NeedKind::ALL` order, raw [0,1], all-zero = none) |
| 44 | 1 | own scene age /24 |
| 45–74 | 30 | own message block: per `HEAD_KINDS` kind (recency, rate) |
| 75–104 | 30 | element memory: per `ElementType::ALL` kind — present, spatial group (4), staleness /40 |
| 105–106 | 2 | waypoint bearing pair: L1 unit direction from own position to `Lattice::waypoint(own explore index)`; (0, 0) on the waypoint |
| 107–108 | 2 | dirt reserve: always 0.0 until armed (future dirt-package arm); no engine write path exists. PROVEN INERT 2026-10-09 pre-freeze (`tests/dirt_reserve.rs`): exactly 0.0 over the randomized battery (32 seeds × sizes 16/58/100 × 2 observers) and the reserve push is the block's final write — the F-058 check-1 bar |

## Kitty row — width 58, K rows, by id, permanent (FR-011 of 049)

| offset | cells | content |
|---|---|---|
| 0 | 1 | present (1 = seen) |
| 1–4 | 4 | spatial group to friend (seen) or last audible meow position (heard) |
| 5 | 1 | friend's BATH /100 — the one visible need (S§1 amendment) |
| 6–12 | 7 | activity one-hot |
| 13 | 1 | partner flag |
| 14 | 1 | is-my-target bit |
| 15 | 1 | friend-in-water bit (tile-derived) |
| 16 | 1 | friend-on-sunbeam bit (tile-derived) |
| 17 | 1 | friend scene age /24 |
| 18–47 | 30 | friend message block (per `HEAD_KINDS`: recency, rate) |
| 48–53 | 6 | want intensities (`WANT_KINDS` order) |
| 54–57 | 4 | answers-me bits (`HERE_KINDS`) |

**Removed vs v5 (the leak audit, FR-007a)**: eat, drink, sleep, play,
cuddle need cells (hidden — five of six), happiness (hidden AND a
view hole: zero behavior-rule reads). No cell for distress flags or
traits existed in v5 and none exists in v6. Remaining fields each
justified: bath (ruled visible control), activity/partner/target
(visible acts), water/sunbeam/scene-age (world facts about a visible
cat), message block + wants + answers-me (the audible digest), purr
(a `HEAD_KINDS` row in the message block — audible).

**Row states**: Seen → all fields live. Heard → present 0, spatial
group to last-meow position, bath 0 (hearing carries no coat state),
offsets 6–17 zero, message block + wants + answers-me live. Silent /
vacant → all 58 cells zero.

## Element slots

Served slot defaults: kitty 4, chow 2, water 2, sunbeam 2, **critter 2**
(4 → 2 by the owner's word 2026-10-09, the banked Gen 2 trim — two
slots cover a radius-5 disc's maximum ever observed). Default
observation length 399; menu 35; logits 51.

Each slot: present, spatial group (4), then its v5 extras unchanged —
chow + servings fraction (width 6); water (5); sunbeam + ttl fraction
+ occupied bit (7); critter + kind one-hot (4) + is-activity-target
(11). Nearest-K fill unchanged (Manhattan, ties by id); critter
target-priority fill unchanged.

## Clock

None. v5 offset −1 (the final cell) is gone; `encode()` takes no
clock argument; `behavior::served_clock` is deleted.

## Global state v2

v1 layout with each kitty block's traits (6) extended to the identity
block's 14 (same order and normalizers as observation offsets 30–43).
Everything else unchanged, including the episode clock (critic-only,
finite-horizon value — R7) and width-normalized positions (single-size
training by ruled staging). `GLOBAL_STATE_SCHEMA_VERSION = 2`.

## Column map

`cloudkitty_rl::schema_map::column_map(version)`:

- `column_map(6)`: every named cell above, derived from the encoder's
  offset constants.
- `column_map(5)`: the spec-049 layout as a literal table, tested
  against `schema_five_pins.rs` numbers.
- any other version: `Err(UnknownSchemaVersion)`; unknown cell name
  lookups: `Err(UnknownCell)`.
- Action menu v2 names ride along (`ACTION_SCHEMA_VERSION = 2`
  unchanged): index → proposal name per the spec-028 table.

Python (`cloudkitty` module): `COLUMN_MAPS: dict[int, dict[str, int]]`
(block-qualified names, e.g. `"kitty_row.bath"` with per-row stride
and base), `ACTION_MENU: dict[str, int]`, beside the four
`*_SCHEMA_VERSION` constants.

## Version gates

A policy artifact pinned to v5 refuses to load against v6 and vice
versa (existing mechanism, SC-006). Gen 1 serving is untouched: the
served world stays schema 5 end to end.

## T024 re-verify (executed at spec 059's close, 2026-10-10)

The deferred obligation (tasks.md T024; 059 FR-014): the friend-field
read sweep re-ran over the post-059 behavior layer, and the FR-011
strip list re-verified against it.

- Sweep result: the only friend `needs.get` reads left in
  `crates/cloudkitty-core/src/behavior/` are the three retained BATH
  sites (finish_what_you_started's groomee read; groom_response's
  announce-threshold decline and exposure-vs-value comparison;
  expected_scene_exposure's partner bath) — bath is the ruled visible
  need. Zero reads of friends' other needs or happiness. The spec-047
  proposer-side consent reads (partner play, top_non_play) are GONE:
  consent moved target-side into the engine (ruling eb9e860b), where
  the target reads its OWN state.
- The strip list stands: every field FR-011 removed from the friend
  row remains unread by deciders as well as unencoded;
  `row_visibility.rs` (hidden-extremes encode identically) stays green,
  and spec 059 added its behavior-layer twin
  (`hidden_friend_extremes_cannot_move_any_teacher_decision`).
- Per-site record: specs/059-teacher-rework/contracts/audit-record.md.
