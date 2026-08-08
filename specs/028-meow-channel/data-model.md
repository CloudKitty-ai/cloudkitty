# Data Model: spec 028

Phase 1 output. Types and state, keyed to the decisions in
[research.md](research.md). File references are current-tree anchors, not
prescriptions of final line numbers.

## New and changed core types (cloudkitty-core)

### `MessageKind` (meow.rs) — extended enum
- Variants (declaration order): `WantEat, WantDrink, FollowMe, WantPlay,
  WantCuddle, Purr, WaitForMe, WantBath, WantSleep` — the two new kinds
  **appended** (wire = snake_case strings; enum order not wire-visible).
- `for_need` / `related_need` become **total** over the six `NeedKind`s:
  Eat↔WantEat, Drink↔WantDrink, Play↔WantPlay, Cuddle↔WantCuddle,
  Bath↔WantBath, Sleep↔WantSleep; `FollowMe | Purr | WaitForMe → None`
  (related_need side).
- `cooldown_for` **deleted** (courtesy retirement, R5).
- New: `pub fn message_legal(kitty: &Kitty, kind: MessageKind, tick: u64,
  config: &Config) -> bool` (R3). Truth table:

  | kind | legal iff |
  |---|---|
  | (Silent — represented as `None` at the Decision level) | always |
  | want-kinds (6) | `announce_armed` contains the grounding need AND `can_meow(kind, tick)` |
  | `Purr` | `purr_earned(thresholds.purr)` AND `tick >= purr_cooldown_until` |
  | `FollowMe` | `can_meow(FollowMe, tick)` |
  | `WaitForMe` | never (head-excluded; yield rule emits engine-side) |

### `Meow` (meow.rs) — extended struct
```rust
pub struct Meow {
    pub kitty_id: KittyId,
    pub kind: MessageKind,
    pub tick: u64,
    #[serde(default)]           // pre-028 snapshots read 0.0
    pub intensity: f32,         // want-kinds: need/100 at emission; else 0.0
}
```

### `Decision` (seam.rs) — the new pair
```rust
pub struct Decision {
    pub activity: Action,
    pub message: Option<MessageKind>,   // None = Silent
}
```
`Copy + Debug + Clone + PartialEq + Serialize + Deserialize`. Carried by:
- `Behavior::decide(ctx) -> Decision` (behavior/mod.rs trait)
- `ProposalEntry::Action(Decision)` (variant renamed `Proposal` if clearer at
  implementation; wire compat is seam-internal, not snapshot state)
- `JointProposal::propose(id, Decision)` / `from_actions` successor
- `ResolvedDecision { kitty_id, decision: Decision, seed, provenance }`
- `KittyTickRecord` grows: `proposed_message`, `applied_message`
  (`Option<MessageKind>`; `validated` analogue: an illegal message downgrades
  to Silent between proposed and applied — activity provenance is unchanged
  and there is **no** message provenance field; the downgrade is visible as
  proposed≠applied).

### `Action` (action.rs) — one retirement
- `Action::Meow { message }`: still parsed (`"meow"` tag), `validate` → `false`
  (Purr-retirement precedent). All other variants untouched.
- Apply path: message application happens once per kitty per tick after
  activity application: `Some(Purr)` → `start_deliberate_purr`; `Some(kind)` →
  `emit_message` (stamps `intensity`, sets per-kind cooldown to
  `tick + recent_window_ticks`, pushes `recent_meows`); `None` → nothing.

### `Kitty` (kitty.rs) — one new field, one reinterpreted
- **New**: `pub announce_armed: BTreeSet<NeedKind>` —
  `#[serde(default, skip_serializing_if = "BTreeSet::is_empty")]`. Hysteresis
  state (R4). Updated in the needs phase: `need >= announce_threshold` →
  insert; `need < announce_threshold - announce_hysteresis` → remove.
- **Reinterpreted**: `meow_cooldowns: BTreeMap<MessageKind, u64>` — same shape,
  now consulted by `message_legal` (enforced) instead of voluntary courtesy.
- `purr_earned`, `purr_cooldown_until`, `happiness_rose`: unchanged.

### `World` / `WorldSnapshot` (world.rs)
- Shapes unchanged except transitively (Kitty + Meow fields above, all
  serde-defaulted) — **pre-028 snapshots deserialize** (FR-022, fixture R16).
- New needs-phase step `update_announce_arming(config)` beside
  `record_distress` (same edge-rule style, no RNG).

### Config (config/mod.rs, defaults.rs, validate.rs)

| struct | change | defaults |
|---|---|---|
| `MeowConfig` | → `recent_window_ticks: u64`, `announce_threshold: f32`, `announce_hysteresis: f32` + 5 retired sentinels (`Option`, `skip_serializing`): spec-023 pair + `courtesy_ticks`, `urgent_courtesy_ticks`, `urgent_need_threshold` | 10 / 30.0 / 5.0 |
| `ActionEffects` | + `cosleep_drip_relief: f32`, `cosleep_mutual_relief: f32` (serde-defaulted) | 15.0 / 15.0 |
| `BehaviorConfig` | + `cuddle_real_threshold: f32` (serde-defaulted) | 15.0 |

Validation (`validate_meow` rewritten; frozen message style, section order
unchanged): threshold ∈ (0, 100]; 0 ≤ hysteresis < threshold; window ≥ 1;
three retirement errors `"retired by spec 028: …"`. `validate_actions` tier-1
finiteness loop grows to 12 dials. `cuddle_real_threshold`: finite, ∈ [0, 100].

## RL-side (cloudkitty-rl)

### Constants and layouts
| constant | old | new |
|---|---|---|
| `OBSERVATION_SCHEMA_VERSION` | 2 | **3** |
| `ACTION_SCHEMA_VERSION` | 1 | **2** |
| `MASK_SCHEMA_VERSION` | 1 | **2** |
| `ARTIFACT_VERSION` | 1 | **2** |
| `GLOBAL_STATE_SCHEMA_VERSION` | 1 | 1 (verify; bump only if it encodes messages/menu) |
| `LEARNED_MEOWS: [MessageKind; 6]` | — | **renamed/replaced** `HEAD_KINDS: [MessageKind; 8]` |
| `MEOW_DIGEST` | 18 (6×3) | **32** (8×4) |
| `observation_len` (default slots) | 183 | **197** |
| menu length (default slots) | 40 | **34** |
| message head length | — | **9** (Silent + 8) |
| serialized mask width | 40 | **43** (34 ∥ 9) |

### `HEAD_KINDS` (normative order)
`[WantEat, WantDrink, FollowMe, WantPlay, WantCuddle, Purr, WantBath, WantSleep]`
— existing six in their current normative order, two appended. Digest iterates
this; message head index `k+1` = `HEAD_KINDS[k]`; index 0 = Silent.

### Digest v3 (observe.rs §4) — per kind, 4 values, one emitter
For each kind in `HEAD_KINDS`: select freshest audible meow (max `tick`,
tie-break min `kitty_id`; self-excluded); emit `[recency, dx, dy, intensity]`
where recency = `(1 − age/window).clamp(0,1)`, dx/dy normalized as today,
intensity = the stamped `Meow.intensity`. No emitter → `[0,0,0,0]`.

### `MessageCodec` (codec.rs)
Total decode over 0..9; encode inverts decode; `WaitForMe` inexpressible (as
today's codec treats it). `ActionCodec::v2`: the `LEARNED_MEOWS` extend removed
→ 34 rows; stale `+7` capacity hint fixed.

### `legal_message_mask` (mask.rs)
Pure oracle probing `message_legal` per head index; Silent (index 0) always
true — the never-all-zero analogue is structural. Wire form: concatenated
`[activity(34) | message(9)]`, `mask_schema = 2`.

### Artifact v2 (policy.rs)
Header field semantics unchanged; validation chain adds: `artifact_version == 2`,
final layer out-width == `menu_len + message_head_len` (43). Logit split is an
index convention: `[0..34)` activity, `[34..43)` message.
`SchemaExpectations` grows `message_head_len: usize`.

### Selection (behavior.rs) & episode (episode.rs)
- Sampling: one `gen_u64` split hi/lo u32 → per-head uniforms (R10); greedy
  draws nothing.
- `Episode::step(&BTreeMap<KittyId, (usize, usize)>)`; `AgentInfo` grows
  `applied_message: Option<String>` (wire name) beside `applied_action`; mask
  bytes 43-wide.

### Eval reporting (welfare.rs / harness.rs / cli_support.rs / suite.rs)
`WelfareAccumulator` grows census state; `WelfareReport` grows:
```rust
pub distress_census: Vec<KittyDistressCounts>
// per kitty: kitty_id, name, by_need: BTreeMap<&'static str, NeedCount { ticks, episodes }>
```
Semantics: post-tick, `>= thresholds.distress`, episode edge below→at/above —
verbatim the distress-census instrument's convention (R15). Reported in JSON
and one human-panel line; **no verdict consumes it**.

## Python binding (cloudkitty-py)
- `action_space` → `MultiDiscrete([34, 9])` (fallback dict analogue); step
  accepts the pair; `VectorEnv` gains `head_len` getter beside `menu_len`;
  info-dict mask `[43]` / stacked `[n, 43]`; `applied_message` in info.
- `recent_meows` returns wire names (snake_case) — Debug-spelling wart fixed
  (R17). Returns 4-tuple growing `intensity`? **No** — keep 3-tuple
  (tick, kitty_id, kind); intensity is observation content, not a py-API need.
  (Additive change deferred until a consumer asks.)

## State transitions

**Arming (per kitty × need, needs phase)**:
`Disarmed --need ≥ T--> Armed --need < T−h--> Disarmed` (T = announce_threshold,
h = hysteresis; in the band [T−h, T) the state holds).

**Message resolution (per kitty × tick)**:
`proposed --message_legal?--> applied` where illegal → `Silent`; applied
`Some(kind ≠ Purr)` → cooldown stamped + `recent_meows` push (with intensity);
applied `Some(Purr)` → deliberate-purr start (existing no-op-if-purring
semantics).

**Cosleep tier (per serviced sleep tick)**:
partner adjacent? no → solo (Sleep relief only). yes → partner activity
∈ {Sleeping, Resting} → **mutual** rate to both; else **drip** rate to both.
Departure ends credit the same tick (existing guarantee, test-pinned).
