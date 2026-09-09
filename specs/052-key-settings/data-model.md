# Data Model: Key Settings (spec 052)

## Entities

### KeySettings — the block

| field | type | meaning |
|---|---|---|
| `engine_defaults_sha256` | string (64 hex) | the stamp (spec 039), computed from the compiled defaults; the block's identity line |
| `entries` | ordered list of Entry | the key settings, in display order |

Built once at boot (`settings::build(&config, &watchdog, raw: Option<&toml::Value>)`), immutable for the life of the process, held as `Arc<KeySettings>` in `AppState`.

### Entry — one key setting

| field | type | meaning |
|---|---|---|
| `group` | string | the config section, as the toml spells it: `world`, `kitty`, `vision`, `meow`, `actions`, `behavior`, `water`, `watchdog` |
| `key` | string | the key within the group; for seats, the kitty id |
| `value` | JSON value | the effective value (number / bool / string / seat object); Option keys carry their sentinel string |
| `default` | JSON value or absent | the engine (or server) default; absent for `world.*` and seats |
| `source` | `"toml"` \| `"default"` | `toml` iff the key's path is present in the loaded config text; `default` otherwise, and always when no file was loaded |

### Source

Two values today. Decided by presence in the raw config tree, never by value comparison (FR-003a). Defined as an enum so an override layer, if one is ever added, adds a variant.

## The list (FR-011's golden)

Display order = this table. Paths are what the presence check resolves.

| # | group.key | path in the toml | value type | default | absent renders as |
|---|---|---|---|---|---|
| — | `engine_defaults_sha256` | computed | string | — | — |
| 1 | `world.width` | `world.width` | u32 | none | (required) |
| 2 | `world.height` | `world.height` | u32 | none | (required) |
| 3 | `world.seed` | `world.seed` | u64 | none | (required) |
| 4… | `kitty.<id>` | `kitty[i]` | `{ "name": …, "behavior": … }` | none | (required, ≥ 2) |
| | `vision.radius` | `vision.radius` | u32 | 5 | default |
| | `vision.memory_timeout_ticks` | `vision.memory_timeout_ticks` | u64 | 0 | default |
| | `meow.relief_memory_margin` | `meow.relief_memory_margin` | u32 or `"unbounded"` | `"unbounded"` | `"unbounded"` |
| | `actions.groom_cuddle_relief` | `actions.groom_cuddle_relief` | f32 | 15.0 | default |
| | `behavior.announce_here` | `behavior.announce_here` | u64 | 0 | default |
| | `behavior.contagion_aware_ladder` | `behavior.contagion_aware_ladder` | bool | false | default |
| | `behavior.reply_intensity_floor` | `behavior.reply_intensity_floor` | f32 or `"none"` | `"none"` | `"none"` |
| | `water.bath_gain` | `water.bath_gain` | f32 | 3.5 | default |
| | `water.bath_gain_ceiling` | `water.bath_gain_ceiling` | f32 | 60.0 | default |
| | `water.contagion_factor` | `water.contagion_factor` | f32 | 0.0 | default |
| | `water.contagion_membership` | `water.contagion_membership` | `"option_a"` \| `"bidirectional"` | `"option_a"` | default |
| | `watchdog.threshold` | `watchdog.threshold` | u64 | 150 | server default |
| | `watchdog.remind_every` | `watchdog.remind_every` | u64 | 150 | server default |

The seat count is the roster's; the golden is taken on a two-seat fixture and pins `kitty.1` and `kitty.2` literally. Defaults in the table are the values at a757595 for the reader's orientation; the block reads them live from `Config::default()` / `WatchdogConfig::default()` and no test pins the numbers.

## Validation rules

- Every entry has a `value`; no entry is ever omitted (FR-004).
- `default` is present for every entry except `world.*` and `kitty.*` (and the header).
- An Option key's `value` and `default` are the same sentinel string when absent; a number when set.
- `source` is `default` for every entry when `raw` is `None`.
- The wire (JSON and text) carries the built value unchanged: `serde_json::to_value(&block)` and `block.render_text()` are what `/settings` serves.

## What does not change

`cloudkitty_core::Config` (no field, no attribute, no `Default`), its serialization, `GET /config`, `engine_defaults_sha256`, the snapshot fingerprint, `Published`, the tick loop, the observation layout.
