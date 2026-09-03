# Data Model: Fog Gen 1 (spec 049)

Entities as the engine will hold them. Layout offsets are in [contracts/observation-v5.md](contracts/observation-v5.md); legality and stamps in [contracts/meow-law-v5.md](contracts/meow-law-v5.md); config deltas in [contracts/config-3.0-migration.md](contracts/config-3.0-migration.md).

## Kitty state (`cloudkitty-core::kitty::Kitty`) — additive fields, shims deleted

| Field | Type | Written by | Notes |
|---|---|---|---|
| `memory` | `ElementMemory` = `[Option<MemorySlot>; 5]` in `ElementType::ALL` order (water, chow, bug, greeble, sunbeam) | engine, environment phase (`update_memories`) | `MemorySlot { pos: Position, last_seen: u64 }`. Rules: nearest visible of the kind overwrites (ties lower id); remembered tile inside the disc holding none of the kind → cleared; `memory_timeout_ticks > 0` and `tick − last_seen > timeout` → cleared; else unchanged. Chow = presence only. Serialised; no restore shim. |
| `explore_heading` | `Option<Direction>` | engine, on every applied `Move { direction }` | read by built-in exploration only; persists across non-move turns; a friend's copy is blanked in the fog view. |
| *deleted* | seven `#[serde(default)]` restore shims (mutual/drip ticks, behavior_description, last_action, purring_until, purr_cooldown_until, purring_duration, announce_armed) + `Pursuit.improved_at` default | — | pre-3.0 saves do not load. |

## Meow record (`cloudkitty-core::meow::Meow`) — additive fields

| Field | Type | Stamped | Meaning |
|---|---|---|---|
| `pos` | `Position` | at emission | speaker's position when it spoke; the heard-row position for unseen friends. |
| `reply` | `bool` | at emission, here-kinds only | `reply_condition` held: matching want from another cat audible (start-of-tick, inside `digest_window_ticks`) ∧ referent visible from the speaker. `false` for every non-here kind. |

Retention: `recent_meows` keeps meows with `tick − m.tick < digest_window_ticks`.

## Fog view (`cloudkitty-core::world::FogView`) — new, per kitty per tick

| Field | Type | Contents |
|---|---|---|
| `snapshot` | `WorldSnapshot` (Deref target) | `kitties`: observer (full) + friends inside the disc, with `memory`/`explore_heading` blanked; `elements`: inside the disc; `recent_meows`: whole buffer; `width`, `height`, `tick` unchanged. |
| `observer` | `KittyId` | the deciding cat. |
| `roster` | `Vec<KittyId>` | every kitty id in the world, ascending — ids are not knowledge. |
| `radius` | `u32` | the configured `[vision] radius`. |

Derived (methods): `visible(pos) -> bool` (`dx² + dy² ≤ r²`, integer), `heard_unseen() -> Vec<(KittyId, Position, u64)>` (freshest audible meow inside the window per roster friend not in `snapshot.kitties`, own meows excluded, `m.tick < tick`), `friend_rows() -> [Option<KittyId>; kitty_slots]` (roster minus observer, ascending, padded).

Consumers: `DecisionContext.world: Arc<FogView>` (built-ins), `DecisionRequest.world = &view.snapshot` (plugins), `encode_observation(&view, …)`, `TargetTable::build(&view, …)`, `legal_action_mask(&view, …)`, `legal_message_mask(&view, …)`.

## Law view (`cloudkitty-core::meow::LawView`) — what `message_legal` reads

Constructed from a `FogView` (mask) or from the live world filtered for the emitter (enforcement): visible elements, visible kitties, roster, start-of-tick meows, the emitter's memory. Both constructions go through the same filter function so the mask and enforcement cannot disagree except by the documented mid-tick element divergence (spec 033 review Finding 5: silences only).

## Configuration (`cloudkitty-core::config`)

| Table | Key | Type / default | Validation |
|---|---|---|---|
| `[vision]` (new, required) | `radius` | `u32`, served 5 (placeholder; step-5 prereg screens it) | ≥ 2 |
| `[vision]` | `memory_timeout_ticks` | `u64`, 0 = never | — |
| `[meow]` | `digest_window_ticks` (new, required) | `u64`, served 30 | positive integer multiple of `recent_window_ticks` |
| `[meow]` | `recent_window_ticks` | unchanged, 10 | doc rewritten: the per-kind emission cooldown |
| `[behavior]` | `reply_intensity_floor` | `Option<f32>`, absent = replies off | in [0, 1] when set; placeholder 0.30 for corpus-collection configs, provisional |
| `[rl.observation]` | `kitty_slots` | default 3 → 4 | ≥ 1 (existing); roster ≤ kitty_slots + 1 (new, in the dual-surface loader and at boot) |
| *deleted* | 13 top-level + 4 nested `#[serde(default)]` section shims; `[purr] cooldown_ticks`; `[meow] cooldown_ticks`, `urgent_cooldown_ticks`, `courtesy_ticks`, `urgent_courtesy_ticks`, `urgent_need_threshold`; `[actions] cuddle_relief` | — | missing section → error naming it; retired key → `deny_unknown_fields` error |
| kept | `[elements.<kind>] max` | unchanged | doc comment corrected (density ceiling + critic chow scale) |

Frozen literals (not config, guarded by pins): scene-age normaliser H = 24; memory staleness normaliser 40.

## Observation schema 5 (`cloudkitty-rl::observe`)

Widths: `SELF_BLOCK` 85, `KITTY_SLOT` 62, `CHOW_SLOT` 5, `WATER_SLOT` 4, `SUNBEAM_SLOT` 6, `CRITTER_SLOT` 10, `CLOCK` 1, global digest deleted. `observation_len(cfg)` = 85 + 4·62 + 2·5 + 2·4 + 2·6 + 4·10 + 1 = **404** at the served config. `OBSERVATION_SCHEMA_VERSION` = 5. `block_widths()` gains `memory` (20) and `msg_self` (30) / `msg_kitty` (40) and drops `msg`/`msg_count`.

Row state (per friend row): `Seen | Heard | Silent` → field-level mask in the contract.

## Action menu / mask / logits (derived, no rule change)

Menu 39 (kitty_slots 4), mask 39 ∥ 16 = 55, v3 logits dense 11 + kitty-ptr 20 + critter-ptr 8 + head 16 = 55. `ACTION_SCHEMA_VERSION` 3, `MASK_SCHEMA_VERSION` 3, `GLOBAL_STATE_SCHEMA_VERSION` 1 unchanged.

## Tokenizer (`cloudkitty-rl::attn::token_layout`)

Groups: self (1 × 85), kitty (4 × 62), chow (2 × 5), water (2 × 4), sunbeam (2 × 6), critter (4 × 10), clock (1 × 1). Type rows 7 (was 22). Artifact format v3 unchanged; blob length derives.

## Eval suite

`evals/v2/`: `heterogeneity`, `mixed-roster-guest`, `mixed-roster-half`, `mixed-roster-host`, `scale`, `scarcity` as complete 3.0 configs + `manifest.toml` with new content hashes. `evals/v1/` listed in `config-sweep-exclusions.txt`.

## State transitions

**Memory slot (per kitty, per kind)**: `Empty --sighting--> Remembered(pos, tick)`; `Remembered --nearer/any sighting--> Remembered(pos', tick')`; `Remembered --tile in disc ∧ none of kind there--> Empty`; `Remembered --timeout (if set)--> Empty`.

**Friend row state (per observer, per friend, per tick)**: `Seen` if inside the disc; else `Heard` if an audible meow inside the window exists; else `Silent`.

**Explore heading**: `None --first applied Move--> Some(d)`; `Some(d) --applied Move(d')--> Some(d')`; never cleared.

**Meow reply**: stamped once at emission; immutable.
