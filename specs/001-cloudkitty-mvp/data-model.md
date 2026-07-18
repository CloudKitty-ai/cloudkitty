# Data Model: CloudKitty MVP

**Date**: 2026-07-18 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

All types live in `cloudkitty-core` with serde derives. Field names below are the
canonical wire names (snake_case JSON). All tunable values come from `Config`;
defaults are listed in [research.md §R11](./research.md) and the shipped
`cloudkitty.toml`.

## World

The root aggregate. Owned exclusively by the sim task; serialized whole as both the
wire snapshot and the persistence snapshot.

| Field | Type | Notes |
|-------|------|-------|
| `width`, `height` | u32 | from config; immutable after creation |
| `tick` | u64 | monotonically increasing |
| `kitties` | Vec\<Kitty\> | **no removal API exists** (Article II); ordered by id |
| `elements` | Vec\<Element\> | elements are added/removed by spawn/expiry/consumption |
| `recent_meows` | Vec\<Meow\> | bounded window (default: last 10 ticks) |
| `distress_events` | VecDeque\<DistressEvent\> | bounded (default 1,000), edge-triggered |
| `rng` | ChaCha8Rng | serialized state; single source of randomness |
| `config_fingerprint` | String | hash of validated config; snapshot-compatibility check |

**Invariants (asserted every tick, `invariants.rs`)**: `kitties.len() >= 2`; every
need in `0..=100`; happiness ≥ floor; every kitty position in bounds; no two kitties
share a tile; safeguard obligations fulfilled (need > safeguard threshold ⇒ satisfying
resource exists, or a spawn occurs this environment phase).

## Position

`{ x: u32, y: u32 }`. Adjacency = Chebyshev distance ≤ 1. One kitty max per tile; one
element max per tile; a kitty and an element may share a tile.

## Kitty

| Field | Type | Notes |
|-------|------|-------|
| `id` | KittyId (u32) | from config; stable ordering key for action application |
| `name` | String | from config |
| `pos` | Position | |
| `needs` | Needs | six clamped values, see below |
| `happiness` | f32 | derived each tick: `100 − weighted_avg(needs)`, clamped to ≥ floor (default 5) |
| `activity` | Activity | see state transitions |
| `behavior` | String | behavior name from config (e.g. `needs_driven`, `playful`) |
| `meow_cooldowns` | Map\<MessageKind, u64\> | tick at which each message kind is next allowed |
| `in_distress` | Set\<NeedKind\> | needs currently ≥ distress threshold; drives edge-triggering |

**Lifecycle**: none. Kitties are created at world generation and exist forever
(Article II — the type exposes no despawn/health/damage concept).

## Needs

`Need` newtype: f32 clamped to `[0, 100]` on every mutation (constructor + all
arithmetic go through `saturating` ops). Six kinds: `eat`, `drink`, `sleep`, `play`,
`cuddle`, `bath`.

- Rise: per-need global per-tick rate (config; defaults 0.5/0.7/0.3/0.4/0.25/0.2).
- Fall: only via validated action effects (config; defaults eat −40, drink −40,
  sleep −5/tick (−8 in sunbeam), groom −30 bath, play −25, rest/co-activities lower
  cuddle by their configured amounts).
- Happiness weights (config; defaults 0.25/0.25/0.15/0.15/0.10/0.10, must sum to 1).

## Activity (state machine)

```
Idle ──rest──▶ Resting ──any other action/behavior──▶ Idle
Idle ──sleep─▶ Sleeping ──behavior interrupts or Sleep=0──▶ Idle
(all other actions are instantaneous and leave the kitty Idle)
```

`Sleeping { in_sunbeam: bool, with_friend: Option<KittyId> }` and
`Resting { with_friend: Option<KittyId> }` carry their context. Engine default while
`Sleeping`: continue sleeping unless the behavior proposes otherwise or Sleep hits 0
(spec assumption). Partner departure degrades the activity to solo (edge case list).

## Element

`Element { id: ElementId, kind: ElementKind, pos: Position, ttl: Option<u64> }`

| Kind | Payload | Movement | Expiry |
|------|---------|----------|--------|
| `water` | — | static | permanent (default) |
| `chow` | `servings: u32` | static | despawns at 0 servings; optional TTL |
| `bug` | — | 1 tile / 2 ticks, random direction | TTL (default 120 ticks) |
| `greeble` | — | 1–2 tiles / tick, direction change ~60%/tick | TTL (default 90 ticks) |
| `sunbeam` | — | static | TTL (default 150 ticks), respawns elsewhere |

Greebles are serialized in every payload like any element — invisibility is a client
rendering rule (FR-033, FR-037).

**Spawn rules** (`spawn.rs`): per-type configured `min`/`max` within hard bounds
(hard min 1, greebles 0; hard max `floor(area/32)`); below-min types respawn during
the environment phase at a random unoccupied tile (element-unoccupied); safeguard
spawning (need > safeguard threshold, no satisfying resource) ignores `max`.
Need→resource mapping: eat→chow, drink→water, sleep→(sunbeam counts as enhancer,
not required), play→bug/greeble/other kitty (always present ⇒ safeguard never
triggers for play/cuddle/bath — satisfied by other kitties/self-grooming).
Safeguard-relevant needs are therefore **eat** and **drink** (spec: "resource
capable of satisfying that need").

## Action

Enum (proposal from behavior; engine validates then applies):

```
Move(Direction)                    Rest { with: Option<KittyId> }
Sleep { with: Option<KittyId> }    Groom { target: Option<KittyId> }
Eat                                Drink
Chase(TargetRef)                   Play(TargetRef)
Purr                               Meow(MessageKind)
Idle
```

`TargetRef = Element(ElementId) | Kitty(KittyId)`. Validation table implements
FR-020/FR-021: illegal-for-state proposals resolve to `Idle` (never an error).
Blocked moves (edge / kitty-occupied destination) → `Idle`. Purr requires
happiness > threshold (default 70) or happiness rose this tick.

## Meow / MessageKind

`MessageKind = WantEat | WantDrink | FollowMe | WantPlay | WantCuddle | Purr`

`Meow { kitty_id, kind, tick }`. Cooldown per kitty per kind: default 15 ticks,
5 ticks while the related need ≥ 75 (`WantEat`→eat, `WantDrink`→drink,
`WantPlay`→play, `WantCuddle`→cuddle; `FollowMe` and `Purr` have no related need —
flat 15). Meow during cooldown: silently dropped, still consumes the turn (FR-023).

## DistressEvent

`{ kitty_id, need: NeedKind, tick }` — recorded **only** when a need crosses from
below to ≥ threshold (default 90); re-armed when it drops below (clarification
2026-07-18). Bounded retention (default 1,000). Exposed via API and persisted in
snapshots.

## DecisionContext (behavior input, read-only)

| Field | Notes |
|-------|-------|
| `me` | full own Kitty state |
| `world` | start-of-tick WorldSnapshot (positions, elements incl. greebles, recent meows) |
| `rng` | per-kitty RNG stream derived from master RNG in stable id order (R4) |
| `constants` | relevant config constants (thresholds, effects) |

## Config (cloudkitty.toml → validated structs)

Sections: `[world]` (width, height, tick_ms, seed), `[persistence]` (snapshot_path,
save_every_ticks), `[[kitty]]` roster (id, name, x, y, behavior), `[elements.<kind>]`
(min, max, ttl, servings…), `[needs]` (rates), `[happiness]` (weights, floor),
`[thresholds]` (distress=90, safeguard=75, purr=70), `[actions]` (effect magnitudes),
`[meow]` (cooldowns), `[behavior]` (budget_fraction_of_tick=0.5).

**Validation rules** (FR-007, clear error naming field/value/allowed range): ≥2
kitties; unique kitty ids; positions on-grid, non-duplicate; element min/max within
hard bounds; min ≤ max; safeguard < distress; behavior budget < tick; happiness
weights sum to 1 (±ε); world large enough for kitties + element minimums; tick_ms > 0.

## WorldSnapshot (wire form)

Serialization of `World` minus `rng` and `config_fingerprint` is **not** separate in
the MVP: the full `World` (including RNG state) is the persistence format, while the
wire snapshot omits `rng` (clients have no use for it) — a `#[serde(skip)]`-marked
projection or a thin `WorldSnapshot` view struct; contracts/http-api.md defines the
wire shape. Both forms include greebles.
