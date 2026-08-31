# Data Model: The `announce_here` Knob

The feature adds one configuration field and one code constant. It adds
**no world state, no snapshot fields, no wire shapes** (FR-009): the
speaking phase and the selection index derive from `(tick, kitty_id)`,
both already persisted, so a resumed run speaks identically to an unbroken
one by construction.

## Configuration

### `behavior.announce_here` (new)

| Property | Value |
|---|---|
| Location | `BehaviorConfig` (`crates/cloudkitty-core/src/config/mod.rs`), `[behavior]` in TOML |
| Type | `u64` |
| Default | `0` (off) |
| Serde | `#[serde(default, skip_serializing_if = "u64_is_zero")]` — absent at default, so `engine_defaults_sha256` is unmoved |
| Validation | None beyond type (non-negative whole number by construction, FR-011); unknown-field rejection already applies via the struct's `deny_unknown_fields` |
| Semantics | `0`/absent: scripted cats never announce Here\* (today's behavior, byte-identical). `N ≥ 1`: each scripted cat *considers* here-speech on its speaking-phase ticks, `(tick + kitty_id) % N == 0` |
| Guard | Key `"announce_here"` added to `roam_cell_stays_out_of_the_default_serialization` |

Relationships: read only by `behavior::announce()`. Never read by policy
seats, the engine's application phase, validation of proposals, or
observation building. Independent of `meow.vocabulary.*` (legality —
untouched) and `meow.recent_window_ticks` (cooldown stamping — untouched).

## Code constant

### `MessageKind::HERE_KINDS` (new)

```text
[HereFood, HereWater, HereCritter, HereSunbeam]   // MessageKind::ALL order
```

The stable ordering FR-006 indexes into. Lives beside `MessageKind::ALL`
in `meow.rs` so a future fifth here-word forces the author past this
const. The legal subset preserves this order; the spoken word is
`legal[((tick + kitty_id) / period) % legal.len()]`.

## Existing entities touched (read-only)

- **`DecisionContext`**: `announce()` already receives `me` (id, pos,
  needs, cooldowns), `world` (tick, elements), `config`. No new fields.
- **`Decision.message`**: the here-word rides the existing
  `Option<MessageKind>` slot, filled only when it was `None` after the
  want loop — precedence ladder WaitForMe > want > here > Silent
  (needs_driven.rs:33 / playful.rs:33 fill the slot in that order today).
- **Legality funnel** (`meow::message_legal`, meow.rs:190): the Here\*
  arms (adjacency + vocabulary flag + per-kind cooldown) are used as-is,
  both at proposal (inside the here path's filter) and at the engine's
  enforcement seam (world.rs:346). No changes.
- **Emission** (`action::emit_message`, action.rs:887): unchanged —
  arithmetic cooldown stamp, `recent_meows` push, intensity 0.0 for
  non-want kinds (spec 033 verdict).

## State transitions

None. No new state exists to transition.
