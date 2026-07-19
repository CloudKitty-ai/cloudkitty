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
| `distress` | DistressLog | ring of DistressEvent, bounded (default 1,000), edge-triggered |
| `rng` | SimRng (wraps ChaCha8Rng) | serialized state; single source of randomness |
| `config_fingerprint` | String | identifies the config a save may resume under |
| `next_element_id` | ElementId | private; monotonic id allocator for spawned elements |

**Invariants (asserted every tick, `invariants::check`)**: `kitties.len() >= 2`;
every need in `0..=100`; happiness ≥ floor; every kitty position in bounds; no two
kitties share a tile; no two elements share a tile; safeguard obligations fulfilled
(need > safeguard threshold ⇒ a satisfying resource exists). The safeguard check is
skipped when every tile already holds an element, since the spec allows a spawn to be
deferred in a full world.

Enforcement: `invariants::assert_or_report` panics in debug/test builds (so the
property suite reports the failing seed) and logs at error level in release, because
crashing a running world would punish the kitties for an engine bug.

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
| `meow_cooldowns` | BTreeMap\<MessageKind, u64\> | tick at which each kind is next allowed; elapsed entries pruned each tick |
| `in_distress` | BTreeSet\<NeedKind\> | needs currently ≥ distress threshold; drives edge-triggering |
| `happiness_rose` | bool | whether happiness went up last tick; one of the two ways to earn a purr |

**Lifecycle**: none. Kitties are created at world generation and exist forever
(Article II — the type exposes no despawn/health/damage concept).

## Needs

`Need` newtype: f32 clamped to `[0, 100]` on every mutation — the constructor and
`add` both clamp, and a NaN delta is ignored rather than allowed to poison the value.
Six kinds: `eat`, `drink`, `sleep`, `play`, `cuddle`, `bath`. `highest_pressure()`
breaks ties in `NeedKind::ALL` order so behavior is never at the mercy of iteration
order.

- Rise: per-need global per-tick rate (config; defaults 0.5/0.7/0.3/0.4/0.25/0.2).
- Fall: only via validated action effects (config; defaults eat −40, drink −40,
  sleep −5/tick (−8 in sunbeam), groom −30 bath, play −25, rest/co-activities lower
  cuddle by their configured amounts).
- Happiness weights (config; defaults 0.25/0.25/0.15/0.15/0.10/0.10, must sum to 1).

## Activity (state machine)

```
Idle ──rest──▶ Resting ──any action other than Idle──▶ Idle
Idle ──sleep─▶ Sleeping ──any action other than Idle──▶ Idle
(all other actions are instantaneous and leave the kitty Idle)
```

`Sleeping { in_sunbeam: bool, with_friend: Option<KittyId> }` and
`Resting { with_friend: Option<KittyId> }` carry their context.

`Idle` means "no override", not "stop": a kitty already resting or sleeping stays
that way and keeps receiving the effect (sleep relief, and cuddle relief if a partner
is still adjacent). This is what makes sleep a multi-tick activity without the
behavior having to re-propose it. Two details re-evaluate every tick: `in_sunbeam`,
because the sunbeam may drift or expire mid-nap, and `with_friend`, which drops to
`None` if the partner wandered off — the activity continues, just alone.

## Element

`Element { id: ElementId, kind: ElementKind, pos: Position, ttl: Option<u64> }`,
where `kind` is serde-flattened with a `kind` tag so the wire shape is
`{"id":9,"kind":"chow","pos":{…},"servings":3}`. A greeble carries its `heading`,
which is what lets it keep a direction between ticks and still look erratic.
Bug movement is stateless: it steps when `(tick + id)` is even, which staggers the
population without storing a timer.

| Kind | Payload | Movement | Expiry |
|------|---------|----------|--------|
| `water` | — | static | permanent (default) |
| `chow` | `servings: u32` | static | despawns at 0 servings; optional TTL |
| `bug` | — | 1 tile / 2 ticks, random direction | TTL (default 120 ticks) |
| `greeble` | `heading: Direction` | 1–2 tiles / tick, direction change ~60%/tick | TTL (default 90 ticks) |
| `sunbeam` | — | static | TTL (default 150 ticks), respawns elsewhere |

Greebles are serialized in every payload like any element — invisibility is a client
rendering rule (FR-033, FR-037).

**Spawn rules** (`spawn.rs`): per-type configured `min`/`max` within hard bounds
(hard min 1, greebles 0; hard max `floor(area/32)`); below-min types respawn during
the environment phase at a random element-unoccupied tile, chosen by best-of-N
sampling (N=8) preferring the candidate farthest from the nearest same-type element
— a spread *preference* that never blocks a spawn; safeguard spawning (need >
safeguard threshold, no satisfying resource) ignores `max`.
Need→resource mapping: eat→chow, drink→water, sleep→(sunbeam counts as enhancer,
not required), play→bug/greeble/other kitty (always present ⇒ safeguard never
triggers for play/cuddle/bath — satisfied by other kitties/self-grooming).
Safeguard-relevant needs are therefore **eat** and **drink** (spec: "resource
capable of satisfying that need").

## Action

Enum (proposal from behavior; engine validates then applies):

```
Move { direction: Direction }      Rest { with: Option<KittyId> }
Sleep { with: Option<KittyId> }    Groom { target: Option<KittyId> }
Eat                                Drink
Chase(TargetRef)                   Play(TargetRef)
Purr                               Meow { message: MessageKind }
Idle
```

`TargetRef = Element { id: ElementId } | Kitty { id: KittyId }`. `action::validate`
implements FR-020/FR-021: illegal-for-state proposals resolve to `Idle`, never an
error. Notable rules:

- **Move**: blocked by the grid edge or a kitty-occupied destination → `Idle`.
- **Chase**: legal only against things that flee — a bug, a greeble, or another
  kitty. Approaching chow, water or a sunbeam is a `Move` (FR-019/FR-020).
- **Play**: requires adjacency, and an element target must be a critter.
- **Rest / Sleep / Groom with a partner**: the partner must exist and be adjacent.
- **Eat**: requires adjacent chow with `servings > 0`; **Drink**: adjacent water.
- **Purr**: happiness > threshold (default 70) *or* happiness rose last tick.
- **Meow**: always legal; the cooldown decides whether it is audible.

Application never errors either. Effects are applied through the clamped `Need`
type, so Article I holds whatever magnitudes the config carries.

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
| `rng` | `DecisionRng` — per-kitty stream derived from the master RNG in stable id order, *before* any decision runs (R4) |
| `config` | `Arc<Config>` — the full validated config, so behaviors read thresholds and effects rather than hard-coding them |

## Config (cloudkitty.toml → validated structs)

Sections: `[world]` (width, height, tick_ms, seed, bind), `[persistence]`
(snapshot_path, save_every_ticks), `[[kitty]]` roster (id, name, x, y, behavior),
`[elements.<kind>]` (min, max, ttl, servings), `[needs]` (rise rates),
`[happiness]` (floor + `[happiness.weights]`), `[thresholds]` (distress=90,
safeguard=75, purr=70), `[actions]` (effect magnitudes), `[meow]` (cooldowns +
recent_window_ticks), `[behavior]` (budget_fraction_of_tick=0.5,
playful_comfort=55), `[events]` (distress_retention=1000).

**Validation rules** (FR-007, every error naming field, value and allowed range):

- ≥ 2 kitties; unique ids; positions on-grid and non-duplicate; behavior name
  non-empty and registered
- element `min` ≥ hard min (1, or 0 for greebles), `max` ≤ `floor(area / 32)`,
  `min` ≤ `max`; chow `servings` ≥ 1; any `ttl` ≥ 1
- `safeguard` < `distress`; all three thresholds within 0–100
- happiness `floor` strictly between 0 and 100 (Article I: never zero); weights
  non-negative and summing to 1 (±1e-3)
- need rise rates non-negative
- `budget_fraction_of_tick` strictly between 0 and 1 (the budget must be shorter
  than a tick)
- `tick_ms` > 0; area ≥ 32 tiles; enough tiles for the roster and element minimums
- `distress_retention` ≥ 1; `save_every_ticks` ≥ 1

Behavior names are validated separately (`validate_behavior_names`) once the
registry is known, so the error can list the names that *are* available.

## World vs WorldSnapshot

Two shapes, one source of truth:

- **`World`** is the persistence format. It serializes whole — including `rng` and
  `config_fingerprint` — which is what lets a restart continue the same future
  rather than merely the same positions.
- **`WorldSnapshot`** is the wire and decision format: `width`, `height`, `tick`,
  `kitties`, `elements`, `recent_meows`. It omits `rng` and `config_fingerprint`
  (viewers have no use for either) and `distress`, which is served separately at
  `/events/distress`. The same struct is handed to behaviors as the start-of-tick
  view, so what a kitty can perceive and what a viewer receives are the same thing.

Both include greebles. See contracts/http-api.md for the exact wire shape.
