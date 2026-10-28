# Data Model: Needy Behaviour Preset

Rewritten 2026-10-27 after the analyze pass (`analysis-2026-10-26.md`):
relief tables (H1), onset sweep in place of a partner-availability rule
(H2), the state ⇔ behaviour invariant (H3), the fog blank (H4), the
two-phase state machine with a last-release record (H7), no floor table,
knee-straddling default edges (M16), the refusal reason (M8).

## Config entities

### NeedyConfig (the `[needy]` table; `Config.needy: Option<NeedyConfig>`, skip-if-none)

| Field | Type | TOML spelling | Rules (validated at load, position 22) |
|-------|------|---------------|-----------------------------------------|
| `mix` | `Vec<f32>` | `mix = [0.5, 0.2, 0.15, 0.15, 0.0, 0.0]` | exactly N entries (N = `NeedKind::ALL.len()`; the error names N); each finite and ≥ 0; not all zero; entry k is the weight of m = k+1 |
| `release_level` | `f32` | `release_level = 90.0` | finite, in [0, 100]; strictly above `actions.sleep_floor_off_beam`; `needy_hold` ignores it |
| `hold_ticks` | `u64` | `hold_ticks = 1500` | ≥ 1 |
| `gap` | `{ min, max }` | `gap = { min = 300, max = 1200 }` | 1 ≤ min ≤ max |
| `onset_levels` | `Vec<u64>` | `onset_levels = [0, 2, 10, 50, 200, 20000]` | strictly increasing; ≥ 6 edges (≥ 5 levels); level i is `[edge_i, edge_i+1)`; the last edge is the exclusive bound of the last level |
| `onset_weights` | `Vec<f32>` | `onset_weights = [0.2, 0.2, 0.2, 0.2, 0.2]` | len = levels; each finite and ≥ 0; not all zero |
| `onset_draw` | enum | `onset_draw = "flat"` \| `"log_uniform"` | default flat |

- `deny_unknown_fields`; `NeedyConfig::default()` is the coverage design
  (research D7; `mix` sized by `NeedKind::ALL.len()` at runtime, never a
  literal). Absent section + a needy seat → defaults.
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
| `phase` | `Phase` | `Resting { next_onset }` \| `Held { onset, masked }` |
| `next` | `NeedSet` | the next episode's masked set, drawn at generation and at each release, so the mask is fixed before it applies |
| `last_release` | `Option<Release>` | `{ tick, by: Level \| Limit }` of the most recent release; `None` before the first |

- `NeedSet`: a bitset over `NeedKind::ALL` (N bits), serialized as the
  sorted list of need names (keyed by name, FR-016).
- `mask(&self) -> NeedSet`: the set in `Held`, empty in `Resting`.
- `phase_name(tick) -> &str`: `released_level` / `released_limit` when
  `last_release.tick == tick`, else `held` / `resting`.
- Created at `World::try_generate` for every kitty whose configured
  `behavior` is a needy preset name; absent otherwise; the saved state
  is authoritative on resume (config parameters re-read live).
- INVARIANT (checked every tick, `invariants::check`): `needy.is_some()
  == needy::is_needy_name(&kitty.behavior)`. The binding's `Episode::new`
  and the server's resume refuse a roster that would break it.
- Hidden from friends: `fog_for` writes `None` over `needy` for every
  kitty but the observer.

### Episode (derived, for the contract and the recorder)

| Field | From |
|-------|------|
| ordinal | `NeedyState.ordinal` at onset |
| onset tick | `Held.onset` |
| masked set | `Held.masked` |
| release tick, by | `last_release` |
| rest gap | drawn at release (`next_onset − release tick`) |

### Phase transitions (one step per tick in Phase 4 after needs rise; `t` = the tick about to be published = `world.tick + 1`)

```
Resting{next_onset}  --t >= next_onset-->  Held{onset: t, masked: next}
                                            ordinal += 1; ONSET SWEEP (below)
Held{onset, masked}  --release rule----->  Resting{next_onset: t + gap}
                                            last_release = {t, by}; draw gap; draw next (m, set)
   release rule: Level when !hold and every masked need >= release_level (post-rise), checked first;
                 Limit when t - onset >= hold_ticks (both presets)
```

One transition per step at most (`gap >= 1`).

### Onset sweep (engine, on the Onset transition)

| scene | condition | action |
|-------|-----------|--------|
| the needy kitty's own activity | `proposer_relief(continuation) ∩ masked ≠ ∅` | `end_activity(needy)` (a social-play duet ends for both) |
| another kitty Grooming { target: needy } | Bath ∈ masked | `end_activity(other)` |
| another kitty Playing { Kitty needy } | Play ∈ masked | `end_activity(other)` (duet) |
| another kitty Resting / Sleeping { with: needy } | Cuddle ∈ masked | `with_friend = None` (solo posture, clock untouched) |

## Engine law entities

### Relief tables (`needy::proposer_relief`, `needy::partner_relief`; cross-checked against `apply_activity_effects`)

| Action | Proposer relieves (own needs) | Partner / target relieves |
|--------|-------------------------------|---------------------------|
| `Eat` | eat | — |
| `Drink` | drink | — |
| `Sleep { with: None }` | sleep | — |
| `Sleep { with: Some(p) }` | sleep, cuddle | cuddle |
| `Rest { with: None }` | — | — |
| `Rest { with: Some(p) }` | cuddle | cuddle |
| `Groom { target: None }` | bath | — |
| `Groom { target: Some(p) }` | cuddle | bath |
| `Play { target: None \| Element }` | play | — |
| `Play { target: Kitty p }` | play | play |
| `Chase`, `Move`, `Idle`, `Meow`, `Purr` | — | — |

### Needy verdict (apply slot, after the consent gate, both sites)

Input: proposer id, the validated action. Output: the action, or `Idle`
when (a) `proposer_relief(action) ∩ proposer.mask ≠ ∅`, or (b) the
action names a partner/target `p` and `partner_relief(action) ∩ p.mask
≠ ∅`. First line: neither party has state → return the input.

### Refusal reason (`RefusalReason::NeedyMasked`, wire `needy_masked`)

`refusal_reason` order, mirroring the slot: validate's own reasons when
validate refused; otherwise consent (`ConsentDeclined`), then the needy
verdict (`NeedyMasked`); `Other` for a legal proposal.

## Behaviour entities

| Item | Value |
|------|-------|
| `Needy` (unit struct; the release rule is `NeedyState::hold`) | builtin; `is_builtin() = true`; `teaches() = false` |
| names | `needy::NAME = "needy"`, `needy::HOLD_NAME = "needy_hold"`, `needy::is_needy_name(&str)` |
| decide, mask empty | `Teacher::GEN2.decide(ctx)` verbatim |
| decide, mask non-empty | masked `me` (masked needs read 0) + `rng.fork()` through `Teacher::GEN2.decide_action`; post-filter: relief meets mask or Chase under a Play mask → `Sleep{Some}` while sleep is unmasked becomes `Sleep{None}`, else `Idle` (a co-rest never becomes a solo rest); message = the masked ladder's own `WaitForMe` yield if it yields, else `announce(ctx)` on the unmasked context |
| `Behavior::teaches()` | default `true`; `BehaviorRegistry::teaches(name) -> Option<bool>` |
| `DecisionRng::fork()` | a new `DecisionRng` carrying a clone of the current ChaCha8 state |

Registry `names()` (BTreeMap order): `["needs_driven", "needy",
"needy_hold", "playful", "teacher"]`.

## Binding entity

`ParallelEnv.needy() -> list[tuple[int, list[str], int, str]]`: one
tuple per needy seat `(kitty_id, masked need names in NeedKind order,
ordinal, phase)` where phase ∈ `"resting" | "held" | "released_level" |
"released_limit"`; empty list when no seat is needy.

## Collector entity (Experiments' lane, cross-lane by consent)

`teachers_refused(registry, config) -> Vec<KittyId>`: seats with
`registry.teaches(&k.behavior) == Some(false)`; `None` keeps today's
`needs_driven` fallback. Provenance meta gains `"teachers_refused":
[ids]` (empty array when none).
