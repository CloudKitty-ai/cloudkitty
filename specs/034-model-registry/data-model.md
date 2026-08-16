# Data Model: Model Registry & Served Behavior Descriptions (spec 034)

## Registry row

One TOML table per certified artifact, keyed by the artifact's sha256 — the
same identity `policies/README.md` ledgers and the server logs at startup.

| Field | Type | Rules |
|-------|------|-------|
| *key* | 64-char lowercase hex sha256 | Identity; never edited, never removed (rows outlive artifacts and renames) |
| `architecture` | non-empty string | Spelled out ("Transformer", "MLP") — never internal shorthand (owner style ruling) |
| `recipe` | non-empty string | Training recipe as certified ("BC+PPO", future "BC+PPO+leash") |
| `display` | non-empty string | The line served to clients, authoritative as written (not derived from the other two) |

Parsing is strict (`deny_unknown_fields`); TOML itself refuses duplicate
keys. Unknown fields, empty required fields, or an unparseable file are
errors wherever the registry is read (server startup when any policy seats;
the repo test always).

**Lifecycle**: a row is born in the PR that lands its artifact (Experiments'
certification-time step, FR-003); it never changes and never leaves.
Renaming or retiring the artifact does not touch the registry — sha is
identity, filename is a label.

## Resolution map (server, in-memory, per boot)

Built during `register_policy_behaviors` (D4): full behavior name
(`policy:<name>`) → display line, from the registry file beside each seated
artifact. Construction fails startup if any seated artifact's directory lacks
`registry.toml` or its sha lacks a row (FR-007 refuse; error names path +
sha). Exists only at startup; consumed by the stamp.

## `Kitty.behavior_description` (served field)

| Property | Value |
|----------|-------|
| Type | `Option<String>`, serde `default` + `skip_serializing_if = Option::is_none` |
| Written by | Server only: once after fresh world generation, and in the resume re-stamp loop beside `behavior` |
| Read by | Nobody in the engine — serialization only |
| Value | `policy:*` seat → registry display line; builtin behavior → `"Scripted"`; plugin behavior → `None` (field absent on the wire) |
| Persistence | Snapshots may carry it, but the registry (like the config) is authoritative on resume — the re-stamp overwrites whatever was frozen, and pre-034 snapshots (no field) load as `None` then get stamped |

## Relationships

```text
policies/registry.toml ──(sha256 lookup at startup)──▶ resolution map
[rl.policy.*] artifact ──(PolicyArtifact::load → sha256)─┘      │
                                                                ▼ stamp
config kitty behavior ──("policy:*" | builtin | plugin)──▶ Kitty.behavior_description
                                                                │
                            REST /world, /kitties, /kitties/:id, WS snapshot_json
                                                                ▼
                                              client (render verbatim; fallback to
                                               model id when absent — Client's side)
```
