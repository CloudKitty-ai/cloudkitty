# Data Model: Relief Memory Margin (spec 050)

No new state. One config field, one predicate input. Layout unchanged (schema 5, 408 floats). The normative wording is in [contracts/relief-memory-margin.md](contracts/relief-memory-margin.md).

## Config (`cloudkitty-core::config::MeowConfig`) — additive field

| Field | Type | Default | Serialization | Meaning |
|---|---|---|---|---|
| `relief_memory_margin` | `Option<u32>` | `None` (absent) | `#[serde(default, skip_serializing_if = "Option::is_none")]` — absent from the defaults stamp (039-D5) | `Some(m)`: a remembered tile is known relief iff Manhattan(cat, tile) ≤ `[vision] radius + m` (saturating). `None`: any remembered tile is known relief (the pre-050 rule). Negative refused at parse; no upper bound (≥ width + height ≡ `None`). Served: `Some(0)`. |

## The predicate (`cloudkitty-core::meow::known_relief`)

| Input | Source | Note |
|---|---|---|
| `want: MessageKind` | caller | eat / drink / play read memory; cuddle / bath / sleep do not |
| `kitty: &Kitty` | the deciding cat (`kitty.pos`, `kitty.memory`) | position at the probe: start-of-tick for the mask and the announce ladder; post-move at the enforcement seam (the spec's mid-tick edge case) |
| `view: &FogView` | the cat's fog view (`view.radius`, visible elements, critters, idle friends) | `radius` is the configured `[vision] radius` |
| `margin: Option<u32>` | `config.meow.relief_memory_margin` | NEW |

Relief per want, after 050:

| want | known relief |
|---|---|
| eat | stocked chow in view ∨ `memory[Chow]` within reach |
| drink | water in view ∨ `memory[Water]` within reach |
| play | idle friend in view ∨ critter in view ∨ `memory[Bug]` within reach ∨ `memory[Greeble]` within reach |
| cuddle | idle friend in view (unchanged) |
| bath, sleep | never (unchanged) |

"within reach" = slot is `Some` ∧ (`margin` is `None` ∨ `kitty.pos.manhattan_distance(&slot.pos) <= view.radius.saturating_add(m)`).

## Invariants

- **Margin 0 ⇒ visible relief only**: Manhattan ≤ r implies dx² + dy² ≤ r² (inside the Euclidean disc), and a remembered tile inside the disc either holds the element (then it is visible) or has been refuted (slot cleared in the environment phase). So at margin 0 the memory arm never decides. Guarded by the unit fixture and the property.
- **Monotone in the margin**: for a fixed world, the set of silenced wants grows with the margin; `None` is the supremum.
- **`LawEra::PreFog`** never calls `known_relief` (FR-008) — unchanged.
- **Navigation reads the full memory** (FR-005) — `known_relief` is called only from `message_legal`.

## What moves at the served key (`cloudkitty.toml`, `relief_memory_margin = 0`)

| Artifact | Moves? | Why |
|---|---|---|
| `fog_continuity` preladder r = 5 stream fixtures (actions, messages) | YES, once | served TOML at r = 5; `want_drink` rows appear |
| `fog_continuity` SC-004b (served TOML at r = 40) | no (predicted) | every tile within Manhattan 38 ≤ 40 on 20×20 |
| served welfare readings (r = 5, r = 64; ignored) | re-taken, recorded | readings, not gates |
| evolution golden, strip witness, run_json golden, joint parity, compiled welfare gate, `binding_continuity` | no | `Config::default()` / own fixture → key absent |
| defaults stamp | no | skip-serialized when `None` |
| observation, wire, artifact, exam widths | no | no layout change |
