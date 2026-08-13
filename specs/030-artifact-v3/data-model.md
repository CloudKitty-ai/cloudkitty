# Phase 1 Data Model: Policy Artifact v3

All widths below are the current schema-3 values for reference. The loader
**derives** them from `observe.rs` block constants and the slot config; it never
hardcodes them. Token widths: self 34, kitty 20, chow 5, water 4, sunbeam 6,
critter 10, message-kind 4, clock 1 — summing to `observation_len` (197 at the
served slot config), 23 tokens (1 + 3 + 2 + 2 + 2 + 4 + 8 + 1).

## On-disk entities

### V3 Header (JSON, strict)

Parsed with `deny_unknown_fields` (FR-004). Fields, all required:

| Field | Type | Constraint |
|-------|------|-----------|
| `artifact_version` | u32 | must equal 3 for this path |
| `observation_schema` | u32 | must equal the compiled `OBSERVATION_SCHEMA_VERSION` (3) |
| `action_schema` | u32 | must equal the compiled `ACTION_SCHEMA_VERSION` (2) |
| `mask_schema` | u32 | must equal the compiled `MASK_SCHEMA_VERSION` (2) |
| `architecture` | String | must equal `"entity_attention"` |
| `d_model` | usize | > 0, `d_model % heads == 0` |
| `heads` | usize | > 0 |
| `encoder_layers` | usize | > 0 |
| `ffn` | usize | > 0 |

No `layers`, no `activation`, no per-tensor shapes — the v2 header's `layers`
and `activation` fields do not appear in v3 (FFN activation is pinned to ReLU by
the forward contract). The header carries no dimension derivable from the slot
config or these hyperparameters (FR-003).

### Weight Blob

`f32` little-endian, row-major, in the fixed module order defined in
`contracts/forward-v3.md`. Total byte length is `4 × Σ(derived tensor sizes)`;
the loader asserts it exactly (FR-007). Weight matrices are `[out][in]`; biases
and LayerNorm gains/biases are `[len]`.

### Parity Fixture File (test-only, Experiments-written)

`[u32 n_rows][u32 obs_len][u32 logit_len]` then `n_rows × (obs_len + logit_len)`
`f32`, each row being the observation followed by the expected logits. Read
dependency-free by the Rust parity test (FR-017). Format owned here; see D7.

## Runtime entities (Rust)

### `PolicyArtifact` (version-keyed enum) — `policy.rs`

Replaces the current struct. Variants: `V2(MlpArtifact)` (the existing struct,
moved behind the enum, unchanged) and `V3(AttnArtifact)`. `load` reads the
container, hashes the file, reads the version, and dispatches to the matching
variant's parse-and-validate. `forward(&self, input, scratch) -> &[f32]`
dispatches on the variant. `sha256` and the schema-version accessors are common.

### `AttnArtifact` — `attn.rs` (new)

Holds the validated header hyperparameters and the parsed weight tensors, grouped
by module (embeddings, type-embedding table, per-layer encoder blocks, summary
norm, four heads). Derives and stores the token layout (per-type offset, width,
count, type-embedding row) from the slot config once at load. No per-forward
allocation beyond `Scratch`.

### `Scratch` — `attn.rs`

Preallocated buffers reused across decisions: the token matrix (`23 × d`), the
attention scores (`heads × 23 × 23`), per-layer temporaries, the pooled summary
(`2d`), and the `menu_len + message_head_len` output vector. Sized from the
hyperparameters at construction; no heap traffic during a decision (FR-012).

### Token layout (derived, not stored on disk)

For each token type: byte offset into the flat observation, feature width, slot
count, and its type-embedding row index. Kitty tokens all map to one embedding
linear and one type-embedding row; critter tokens likewise; each message kind
gets its own type-embedding row (kind identity is its position in `HEAD_KINDS`).
A slot is padding-masked when its first feature is `≤ 0` (the engine's vacant
encoding); self and clock are never masked.

## Validation rules (load order — FR-006)

1. Magic `CKPOLICY` present.
2. `u32` header length read; header bytes sliced.
3. Header JSON parses under `deny_unknown_fields`.
4. `artifact_version` in the supported set `{2, 3}`; else rejected by version
   listing the set. (Version 2 leaves this path for the v2 loader.)
5. `observation_schema`/`action_schema`/`mask_schema` each equal the compiled
   version; else `SchemaMismatch { schema, found, expected }`.
6. `architecture == "entity_attention"`; else rejected naming the field.
7. Hyperparameters positive and `d_model % heads == 0`; else rejected naming the
   offending field.
8. Derived token widths sum to `observation_len`; else `Shape` naming found vs
   expected (the v3 analog of the v2 input-width check).
9. Derived output width equals `menu_len + message_head_len`; else `Shape`.
10. Blob byte length equals `4 × Σ(derived tensor sizes)`; else `BlobSize {
    found, expected }`.

Any failure fails startup naming `[rl.policy.<name>].artifact` and the reason,
before any tick (FR-006). SHA-256 and the three schema versions are logged on
success (FR-008).

## State transitions

None. An artifact is immutable once loaded; there is no lifecycle beyond
load-or-reject at startup.
