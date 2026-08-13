# Contract: Policy Artifact v3 — Container, Header, Validation, Versioning

This contract extends the v2 policy-artifact format
(`specs/014-multi-agent-rl/contracts/policy-artifact.md`,
`specs/028-meow-channel/contracts/encodings-v2.md`). The container is unchanged;
v3 changes the header schema, the version gate, and (see `forward-v3.md`) the
weight blob's internal layout.

## Container (unchanged from v2)

```
magic:        8 bytes  "CKPOLICY"
header_len:   u32 little-endian
header:       header_len bytes of UTF-8 JSON
blob:         f32 little-endian weights, to end of file
```

The SHA-256 of the whole file is computed at load and logged.

## Header schema (v3)

A JSON object, parsed with `deny_unknown_fields`. Unknown or misspelled keys
fail loading and name the field (FR-004). This is new for the artifact header —
the PR #114 strict-loading posture, previously on the TOML config structs, now
covers the artifact JSON. The v2 header is untouched.

```json
{
  "artifact_version": 3,
  "observation_schema": 3,
  "action_schema": 2,
  "mask_schema": 2,
  "architecture": "entity_attention",
  "d_model": 64,
  "heads": 4,
  "encoder_layers": 2,
  "ffn": 128
}
```

The v2 header's `layers` and `activation` fields are absent. Feed-forward
activation is pinned to ReLU by `forward-v3.md`, not declared per-artifact —
matching how the v2 loader fixes `activation == "relu"`.

The header carries no dimension derivable from the compiled slot config or from
these hyperparameters (FR-003): token widths, the type-embedding row count, and
every tensor shape are derived at load.

### Header authority (FR-007, clarify 2026-08-13)

The header is the sole authority for the transformer architecture. The loader
accepts any hyperparameters that pass the constraints below and derives every
tensor shape from them. It does **not** pin the hyperparameters against compiled
constants, so a re-tuned model loads without a rebuild. The forward is generic
over `d_model`, `heads`, `encoder_layers`, `ffn`.

## Version gate (FR-009, FR-010, FR-011)

The binary supports a **set** of artifact versions, `{2, 3}`. After the version
field is read:

- `2` → the v2 header parse, validation, and MLP forward (unchanged; byte-
  identical output — FR-010).
- `3` → the v3 path in this contract.
- anything else → rejected by version, with a message listing the supported set.

A v3 artifact on a binary whose supported set is `{2}` is therefore rejected by
version, not by a downstream shape accident (FR-011).

`PolicyArtifact` becomes a version-keyed enum; `forward` dispatches on the
variant. The behavior seam is unchanged: `decide_sync` splits the returned logit
vector at `menu_len` into activity and message heads exactly as today (FR-016).

## Validation order (FR-006)

The loader validates in this order and fails at the first problem, naming
`[rl.policy.<name>].artifact` and the reason, before any tick:

1. magic `CKPOLICY`
2. header length, header bytes sliced
3. header JSON parses under `deny_unknown_fields`
4. `artifact_version` in `{2, 3}` (else rejected by version)
5. `observation_schema`, `action_schema`, `mask_schema` each match the compiled
   version
6. `architecture == "entity_attention"`
7. hyperparameters positive; `d_model % heads == 0`
8. derived token widths sum to `observation_len`
9. derived output width equals `menu_len + message_head_len`
10. blob byte length equals `4 × Σ(derived tensor sizes)`

On success the loader logs the SHA-256 and the three schema versions (FR-008).

## Error taxonomy

Reuses the v2 `ArtifactError` variants, with two additions and one change:

| Condition | Error |
|-----------|-------|
| bad magic | `BadMagic` (existing) |
| header won't parse / unknown field | `Header(msg)` (existing; now also fires on an unknown key) |
| version not in `{2,3}` | `UnsupportedVersion { found, supported }` — `supported` becomes the set, not a single value (change) |
| schema pin mismatch | `SchemaMismatch { schema, found, expected }` (existing) |
| `architecture` unrecognized | `Architecture(found)` (new) |
| hyperparameter non-positive or `d_model % heads != 0` | `Hyperparameter(msg)` (new) |
| token widths ≠ `observation_len`, or output width ≠ `menu_len + message_head_len` | `Shape(msg)` (existing) |
| blob length mismatch | `BlobSize { found, expected }` (existing) |

## Non-goals

No engine, world, config-schema, or behavior-semantics change (FR-020). Schema 4
and variable rosters are out of scope (FR-021). The mask, `ActionCodec`,
`MessageCodec`, legality, and certification harness are reused unchanged.
