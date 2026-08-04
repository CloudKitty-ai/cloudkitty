# Data Model: Per-Target Play Relief

No new world state, no schema change, no snapshot change. The entire
data surface is two config fields and one routing table.

## Config: `ActionEffects` (`[actions]`, `config/mod.rs:429-446`)

| Field | Type | Default | Status | Meaning |
|-------|------|---------|--------|---------|
| `solo_play_relief` | f32 | 10.0 | unchanged | play relief for pouncing at nothing — and the fallback for a vanished/non-critter element target |
| `play_relief` | f32 | 20.0 | doc re-scoped | the **kitty/duet** value: each duet partner's per-tick relief (name kept for back-compat and wire stability, R1) |
| `play_relief_bug` | f32 | 25.0 | **new**, serde-defaulted | per-tick relief while playing with a bug |
| `play_relief_greeble` | f32 | 35.0 | **new**, serde-defaulted | per-tick relief while playing with a greeble |

Defaults live in `config/defaults.rs` beside `default_solo_play_relief`.
Both new fields carry `#[serde(default = ...)]` so every existing config
parses; `Config` has no `deny_unknown_fields`, so frozen exam configs
stay valid and byte-identical.

## Validation rules (`validate_actions`, `config/validate.rs:542-562`)

1. **Finite/non-negative** — all four keys must be finite and ≥ 0
   (extends the existing solo-only check).
2. **Strict ordering** — `solo_play_relief < play_relief <
   play_relief_bug < play_relief_greeble`. Supersedes the solo-vs-play
   guard at `validate.rs:551`; its doctrine phrase ("playing together
   must stay the better deal") survives in the new error text.
3. **Duet ceiling** — `play_relief_greeble < 2 × play_relief`. Error
   message states the economics: a duet relieves both cats, so team
   welfare pays 2×kitty per duet tick; at or above the ceiling solo
   greeble-hunting dominates social play and meow recruitment loses
   its value.

Validation order within `validate_actions`: finiteness first, then the
chain, then the ceiling — so an error always names the most upstream
problem.

## Routing table (`Activity::Playing` effect arm, `action.rs:709-723`)

| `target` | Element lookup (`world.element(id)`) | Relief paid | Also |
|----------|--------------------------------------|-------------|------|
| `None` | — | `solo_play_relief` to self | unchanged |
| `Some(Kitty { id })` | — | `play_relief` to **both** parties | partner serviced stamp; unchanged |
| `Some(Element { id })` | `Some` with `ElementType::Bug` | `play_relief_bug` to self | new |
| `Some(Element { id })` | `Some` with `ElementType::Greeble` | `play_relief_greeble` to self | new |
| `Some(Element { id })` | `None` (expired) or any non-critter type | `solo_play_relief` to self | the pinned despawn edge (R2) |

The lookup happens every serviced tick (the effect body is the single
path for tick 1 and ticks 2..n, `action.rs:661-664`), so a mid-scene
despawn changes the very next tick's price. No state transitions are
added; the scene's clock and ending rules are untouched.

## What deliberately does not change

- `Activity` enum shape, `TargetRef`, proposal validation
  (`action.rs:382-392`).
- Observation layout (dim 182), action codec (40), snapshot format,
  config fingerprint (relief values are not fingerprinted —
  `fingerprint_ignores_the_new_behavior_tunables`, `config/mod.rs:1483`).
- Served `cloudkitty.toml` (defaults carry the new keys).
