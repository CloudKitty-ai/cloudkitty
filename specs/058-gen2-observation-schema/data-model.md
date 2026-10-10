# Data Model: Gen 2 Observation Schema Bump (spec 058)

Phase 1 output. The normative cell-level layout lives in
`contracts/observation-v6.md`; this file holds the entities, their
relationships, and the validation rules. Widths below assume the
schema-5 sub-block constants (`HEAD_KINDS` 15, `WANT_KINDS` 6,
`HERE_KINDS` 4, `ElementType::ALL` 5) — all unchanged by this spec.

## Entities

### Observation vector v6

One per cat per tick; a pure function of the cat's frozen `FogView`
plus config. Blocks in order:

| Block | v5 width | v6 width | Delta and why |
|---|---|---|---|
| Self block | 85 | 109 | −2 fractional position, +4 walls, +8 identity extension, +10 memory spatial, +2 waypoint, +2 dirt reserve |
| Kitty row × K | 63 | 58 | +1 spatial (3 → 4 cells), −5 hidden needs (bath stays), −1 happiness (view hole + hidden) |
| Chow slot × c | 5 | 6 | +1 spatial |
| Water slot × w | 4 | 5 | +1 spatial |
| Sunbeam slot × s | 6 | 7 | +1 spatial |
| Critter slot × r | 10 | 11 | +1 spatial |
| Episode clock | 1 | 0 | dropped (K§2) |

Total length stays a function of the slot config
(`observation_len`), never a quoted constant.

**Self block v6, in order**: needs (6, /100) · happiness (/100) ·
distance-to-wall N/E/S/W (4, linear /40 clamped — replaces
fractional position) · activity one-hot (7) · social flag ·
in-sunbeam · in-water · progress · distress flags (6) · pursuit (2) ·
identity block (14, below) · own scene age · own message block (30) ·
element memory (5 kinds × 6: present, bearing pair, linear, log,
staleness — was × 4 with dx/dy) · waypoint bearing pair (2) · dirt
reserve (2, always 0.0).

**Identity block (14)**: need-rate multipliers (6, `need_rate_for /
reference_need_rate`, clamp [0,4] — the existing traits cells,
position preserved in spirit, offsets move) · comfort slack (ticks
/40, clamp [0,1]) · consent line (/100) · favourite weights (6, one
per `NeedKind`, raw [0,1], all-zero = no favourite).

**Kitty row v6, in order**: present · bearing pair (2) · linear
magnitude · log magnitude · bath (/100) · activity one-hot (7) ·
partner flag · is-my-target · water bit · sunbeam bit · scene age ·
message block (30) · want intensities (6) · answers-me (4). Removed
vs v5: eat/drink/sleep/play/cuddle need cells, happiness.

**Spatial cell group (every entity: kitty rows, element slots,
element memory)**: bearing = (dx/d, dy/d) with d = |dx| + |dy|
Manhattan, (0, 0) at d = 0 · linear = d/40 clamped at 1 · log =
log1p(d)/log1p(400). Constants 40, 400 frozen literals. Never
clamped or validated against the vision radius (FR-001a).

### Global state v2

Per kitty in stable id order, the v1 block plus the +8 identity
extension (comfort slack, consent line, favourite 6) appended after
the existing traits 6 — the critic sees every seat's full dials
(FR-009). Element summary, center-K, and the episode clock stay as
v1 (R7: critic keeps its clock; positions stay width-normalized —
training is single-size by ruled staging). `global_state_len` moves
accordingly.

### Identity dial accessors (config)

The `need_rate_for` pattern (per-kitty roster override, else world
default), extended to:

| Accessor | Per-kitty override | World default | Range |
|---|---|---|---|
| `need_rate_for(id, kind)` | existing | existing | validated > 0 |
| `comfort_slack_for(id)` | new `[[kitties]] comfort_slack` | new `[behavior] comfort_slack` (documented default) | ticks ≥ 0 |
| `consent_line_for(id)` | new `[[kitties]] consent_line` | existing `[behavior] consent_line` | 0–100 |
| `favourite_weight_for(id, kind)` | new `[[kitties]] favourite.<kind>` | 0.0 | [0, 1] |

Validation joins the existing config validator (ranges above;
rejects NaN). These accessors are the ONE home for the dials; spec
059's parameterized teacher reads the same functions.

**Config-sweep note**: new toml keys redden the shipped-config sweeps
until defaults land everywhere the sweep loads (rust-toolchain-pin
memory: any new root toml key is a two-sweep event) — tasks must
include the sweep run.

### Column map (`schema_map`)

- `column_map(version: u32) -> Result<&'static SchemaMap, SchemaMapError>`
- v6 map: built from the v6 offset constants (one source).
- v5 map: literal table, oracle-tested against `schema_five_pins.rs`
  numbers.
- Carries action-menu names for action codec v2 (unchanged table).
- Python: exported as a nested dict
  `COLUMN_MAPS = {5: {...}, 6: {...}}` plus `ACTION_MENU = {...}`
  beside the existing `*_SCHEMA_VERSION` constants.
- Unknown version or cell name: error, never a default (FR-015).

### Version pins

| Constant | v5 world | this spec |
|---|---|---|
| `OBSERVATION_SCHEMA_VERSION` | 5 | 6 |
| `GLOBAL_STATE_SCHEMA_VERSION` | 1 | 2 |
| `ACTION_SCHEMA_VERSION` | 2 | 2 (unchanged) |
| `MASK_SCHEMA_VERSION` | (current) | unchanged |

Artifact load-time gates keep refusing mismatches (SC-006) — the
existing mechanism, new values.

## State transitions

None — the observation is stateless per tick. Row states
(Seen/Heard/Silent/Vacant) keep their v5 semantics; the heard-row
mask narrows by the removed cells (R12).

## Validation rules

- Encoder debug-asserts each block width (existing pattern).
- `schema_five_pins.rs` is FROZEN as the v5 oracle (it validates the
  column map's v5 table; it no longer compiles against the live
  encoder — it pins the literal table instead).
- A v6 pins test (`schema_six_pins.rs`) asserts every derived offset
  literally, the 049 discipline.
- Dirt reserve: property test asserts both cells are 0.0 over
  randomized worlds; no encoder write-path to the reserve range
  exists (R10).
- FR-001a pin: a seen friend at dx=2, dy=3 under radius 4 encodes
  Manhattan 5 > r, unclamped.
