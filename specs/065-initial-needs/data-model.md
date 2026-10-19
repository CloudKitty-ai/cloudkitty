# Data Model: Initial-Needs Distribution

## Config entities

### NeedInit (one need's initial setting)

| Form | TOML spelling | Semantics |
|------|---------------|-----------|
| Fixed | `cuddle = 80.0` | Exact value for every kitty it governs; zero draws |
| Range | `cuddle = { min = 60.0, max = 95.0 }` | One independent draw per governed (kitty, need); inclusive range |

Validation (startup, clear errors naming need + kitty where
applicable): finite numbers; value/min/max ∈ [0, 100]; min ≤ max.
Range struct is `deny_unknown_fields`.

### InitialNeedsSpec (six optional per-need entries)

Fields: `eat`, `drink`, `sleep`, `play`, `cuddle`, `bath` — each
`Option<NeedInit>`, skip-if-none, `deny_unknown_fields`. Used at BOTH
levels:

- `Config.initial_needs: Option<InitialNeedsSpec>` — the roster-wide
  `[initial_needs]` table; `#[serde(default, skip_serializing_if =
  "Option::is_none")]` (the starts attrs — stamp/`GET /config` do not
  grow).
- `KittyConfig.initial_needs: Option<InitialNeedsSpec>` — per-kitty
  override, same attrs; need-by-need precedence over the roster-wide
  table. Un-rostered overrides are inexpressible by construction
  (field lives ON the kitty entry).

**Feature-active predicate**: top-level table present OR any kitty
carries the field. Inactive = today's engine byte-for-byte.

### Resolution (per kitty, per need)

```
governing(kitty, need) = kitty.initial_needs[need]   if set
                       | config.initial_needs[need]  if set
                       | none                        (need starts 0)
```

## Engine state touched (no new fields)

| State | Where | How it moves |
|-------|-------|--------------|
| `Kitty.needs` | kitty.rs | Set at generation from resolved values/draws (bounded by `Need` clamp semantics as belt-and-braces over validation) |
| `Kitty.happiness` | kitty.rs | Existing generate-time recompute derives it (world.rs ~178); never configured directly |
| `Kitty.announce_armed` | kitty.rs | `update_announce_arming` run at generation when feature active |
| `Kitty.in_distress`, `Kitty.distress_since` | kitty.rs | `record_distress` run at generation when feature active; `distress_since` anchored at tick 0 |
| `World.distress` (DistressLog) | world.rs | Same `record_distress` call records tick-0 events |

## Draw-state lifecycle

Sub-stream `ChaCha8Rng::from_seed(seed-recipe with tag ck-initnd-v1)`
created at generation when the feature is active, consumed in the law
order (contracts/init-law.md), dropped after application. Never stored;
never touches `World.rng` (the master stream) or any other sub-stream.

## State transitions

None beyond generation: initial needs are world state from tick 0
onward; save/load carries them as-is (no re-seed at resume — the
062/064 generation-time-knob precedent); every later transition is the
existing engine's.
