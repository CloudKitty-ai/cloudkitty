# Data Model: Randomized Starts (Phase 1)

## Config entities

### `StartsConfig` (new, `config/mod.rs`)

TOML `[starts]`; `deny_unknown_fields`. Held as
`Config.starts: Option<StartsConfig>` with
`#[serde(default, skip_serializing_if = "Option::is_none")]` — absent table =
knob off = today's behavior, and `Config::default()` serialization (hence the
`engine_defaults_sha256` stamp) is unchanged.

| Field | Type | Meaning | Validation (load, position 19) |
|---|---|---|---|
| `edge_ring_share` | `f64` | P(a drawn kitty starts on the edge ring, corners included) | in [0, 1] |
| `corner_share` | `f64` | P(a drawn kitty starts on one of the 4 corners) | in [0, 1] and ≤ `edge_ring_share` |

Table present additionally requires `world.width ≥ 3 && world.height ≥ 3`
(rejected loudly otherwise; explicit-starts tiny worlds stay legal).

Derived, not stored: P(non-corner edge) = `edge_ring_share − corner_share`;
P(interior) = `1 − edge_ring_share`.

### `KittyConfig` (changed)

`x: Option<u32>`, `y: Option<u32>` (`default`, `skip_serializing_if =
Option::is_none`). `KittyConfig::new` keeps its `u32` parameters and wraps in
`Some`.

Validation (roster slot, position 2 — new checks fire only on input that
could not previously parse):

- exactly one of x/y set → error naming the kitty (always, knob on or off);
- knob off → both must be set (error naming the kitty);
- both set → today's in-bounds and no-shared-tile checks, unchanged.

State rule: a kitty with both coordinates is **explicit** (never drawn, tile
pre-marked occupied); a kitty with neither is **drawn** (knob on required —
knob off already rejected it above).

## Draw entities (new module `cloudkitty-core/src/starts.rs`)

### `StartCategory`

`Corner | EdgeRing | Interior` — the coverage instrument's disjoint geometry
(contracts/draw-law-v1.md §Geometry). Serialized in the meta echo as
`"corner" | "edge_ring" | "interior"`.

### `DrawnStart`

| Field | Type | Meaning |
|---|---|---|
| `kitty` | `KittyId` | roster id |
| `position` | `Position` | the resolved tile |
| `category` | `StartCategory` | the category the engine drew (for explicit kitties: classified from the pinned tile) |
| `drawn` | `bool` | false for explicit-coordinate kitties |

Produced in kitty-id ascending order by:

```rust
pub fn draw(config: &Config) -> Result<Vec<DrawnStart>, StartsError>
```

the ONE sampler (FR-007). Pure: output depends only on
(world.seed, width, height, shares, roster ids + explicit coords). Called by
`World::try_generate` and by bc-collect's meta echo; SC-006's test pins the
two against tick-0 state.

### `StartsError`

Only world-build failure: category exhaustion. Message names the category,
how many kitties drew it, and its free-tile capacity (spec Edge Cases,
verbatim shape). Surfaced by `World::try_generate(config) -> Result<World,
StartsError>`; `World::generate` delegates and `expect`s (signature and all
68 call sites unchanged).

### `STARTS_LAW_VERSION`

`pub const STARTS_LAW_VERSION: u32 = 1`. Any change to the draw law
(contracts/draw-law-v1.md) bumps this const AND the sub-stream domain tag
(`ck-starts-v1` → `-v2`) in the same change — FR-012's versioned break. The
const is stamped into collection metadata (contracts/provenance.md).

## Relationships

```text
Config.starts (Option) ──knob on──▶ starts::draw(config) ─▶ Vec<DrawnStart>
Config.kitties[].x/y (Option)            │                        │
   explicit kitties: occupied set ───────┘                        │
World::try_generate ◀── positions ────────────────────────────────┤
bc-collect meta.json "starts" echo ◀── same call, same values ────┘
```

## State transitions

None at runtime: the draw happens once, inside world generation, before
tick 0. Snapshots carry positions as kitty state exactly as today; resume
(`from_snapshot`, persistence) never re-draws. `Config::fingerprint()`
(w/h/seed/ids) is untouched.
