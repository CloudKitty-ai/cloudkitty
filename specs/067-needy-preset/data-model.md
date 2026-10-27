# Data Model: Needy Behaviour Preset

## Config entities

### NeedyConfig (the `[needy]` table; `Config.needy: Option<NeedyConfig>`, skip-if-none)

| Field | Type | TOML spelling | Rules (validated at load, position 22) |
|-------|------|---------------|-----------------------------------------|
| `mix` | `Vec<f32>` | `mix = [0.5, 0.2, 0.15, 0.15, 0.0, 0.0]` | exactly N entries (N = the engine's need count; error names N); each ≥ 0 and finite; not all zero; entry k is the weight of m = k+1 |
| `release_level` | `f32` | `release_level = 90.0` | in [0, 100]; > every reachable floor; `needy_hold` ignores it |
| `hold_ticks` | `u64` | `hold_ticks = 1500` | ≥ 1 |
| `gap` | `{ min, max }` | `gap = { min = 300, max = 1200 }` | 1 ≤ min ≤ max |
| `onset_levels` | `Vec<u64>` | `onset_levels = [0, 10, 100, 500, 2000, 8000]` | strictly increasing; ≥ 6 edges (≥ 5 levels); edges are tick bounds, the last the latest first onset |
| `onset_weights` | `Vec<f32>` | `onset_weights = [0.2, 0.2, 0.2, 0.2, 0.2]` | len = levels; each ≥ 0 finite; not all zero |
| `onset_draw` | enum | `onset_draw = "flat"` \| `"log_uniform"` | default flat |
| `floors` | `BTreeMap<String, f32>` | `[needy.floors] sleep = 20.0` | keys are need names (`NeedKind::as_str`); unknown key refused by name; each in [0, 100] |

- `deny_unknown_fields`; `NeedyConfig::default()` is the coverage design
  (research D7). Absent section + a needy seat → defaults.
- Validation also requires, when sleep is reachable (weight on any m
  and sleep not floored out): `release_level > actions.sleep_floor_off_beam`.
- Not read by `Config::fingerprint()`; not part of any observation.

### Hazard registry rows (spec 066 `HazardMode`, extended)

| Variant | `name()` | Active when | Site text |
|---------|----------|-------------|-----------|
| `Needy` | `needy` | any `[[kitty]]` has `behavior = "needy"` | `[[kitty]] '<name>' (id <id>) behavior = "needy"` (first in config order) |
| `NeedyHold` | `needy_hold` | any `[[kitty]]` has `behavior = "needy_hold"` | same shape |

Registry order: `initial_needs`, `needy`, `needy_hold`. `ALL` is pinned
to the enum by an exhaustive-match test.

## World entities

### NeedyState (`Kitty.needy: Option<NeedyState>`, skip-if-none)

| Field | Type | Meaning |
|-------|------|---------|
| `hold` | `bool` | the preset variant (true = `needy_hold`) |
| `rng` | `ChaCha8Rng` (serialized) | the private sub-stream, seeded from (world seed, kitty id, `ck-needy-v1`) |
| `ordinal` | `u32` | episodes opened so far; 0 before the first onset |
| `phase` | `Phase` | `Resting { next_onset }` \| `Held { onset, masked, release_by_limit_at }` \| `Releasing { onset, masked, released_at, by: Level \| Limit }` (one tick, the release tick's record) |
| `next` | `Option<Pending>` | the next episode's `(m, masked set)` drawn at the previous release (or at generation), so the mask is fixed before it applies |

- `masked: NeedSet` — a bitset over `NeedKind::ALL` (N bits); rendered
  as need names.
- `mask(&self) -> NeedSet`: empty in `Resting`/`Releasing`, the set in
  `Held`.
- Created at `World::try_generate` for every kitty whose `behavior` is
  a needy preset name; absent otherwise; a snapshot's state is
  authoritative on resume (config parameters re-read live).

### Episode (derived, for the contract and the recorder)

| Field | From |
|-------|------|
| ordinal | `NeedyState.ordinal` at onset |
| onset tick | the tick the phase became `Held` |
| masked set | `Held.masked` |
| release tick, by | `Releasing` |
| rest gap | drawn at release |

### Phase transitions (one step per tick, Phase 4 after needs rise)

```
Resting{next_onset}  --tick+1 == next_onset-->  Held{onset, masked=next.set}     (ordinal += 1; end own activity if its governing need ∈ masked)
Held                 --release rule--------->  Releasing{by}                      (level: all masked ≥ release_level, needy only; limit: tick+1-onset ≥ hold_ticks)
Releasing            --next tick------------>  Resting{next_onset = released_at + gap}   (draw gap; draw next m + set)
```

## Engine law entities

### Needy verdict (apply slot, after the consent gate, both sites)

Input: proposer id, the validated action. Output: the action, or `Idle`
when (a) `governing_need(action) ∈ proposer.mask`, or (b) the action
names a partner/target `p` and `partner_relief(action) ∈ p.mask`.

### Partner relief table (`action::partner_relief`)

| Action | Partner / target gets relief on |
|--------|--------------------------------|
| `Groom { target: Some(p) }` | Bath |
| `Play { target: Kitty p }` | Play |
| `Rest { with: Some(p) }` | Cuddle |
| `Sleep { with: Some(p) }` | Cuddle |
| anything else | none |

Cross-checked by a test against `apply_activity_effects`.

### Partner availability

`available_friend_in(kitties, me, friend)` is false when
`friend.needy.mask()` contains the duet's partner-relief need for the
activity `me` is in (Resting/Sleeping with → Cuddle; Grooming target →
Bath).

## Behaviour entities

| Item | Value |
|------|-------|
| `Needy { hold }` | builtin; `is_builtin() = true`; `teaches() = false` |
| names | `needy::NAME = "needy"`, `needy::HOLD_NAME = "needy_hold"` |
| decide | masked view of `me.needs` (masked → 0) through `Teacher::GEN2.decide_action`; post-filter governing need ∈ mask → wander/Idle; message = `announce(ctx)` on the unmasked context |
| `Behavior::teaches()` | default `true`; `BehaviorRegistry::teaches(name) -> Option<bool>` |

## Binding entity

`ParallelEnv.needy() -> list[tuple[int, list[str], int, str]]`: one
tuple per needy seat `(kitty_id, masked need names in NeedKind order,
ordinal, phase)` where phase ∈ `"resting" | "held" | "released_level" |
"released_limit"`; empty list when no seat is needy.
