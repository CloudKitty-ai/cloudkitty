# Data Model: World Branch API (spec 068)

Phase 1 of `/speckit-plan`. Types are described by field and rule; exact
Rust spellings are the implementation's, guided by research.md.

## EpisodeSnapshot (rl crate, `episode.rs`)

The serialized form of one environment between steps. Opaque to Python
(bytes); JSON inside (R1).

| Field | Type | Rule |
|-------|------|------|
| `identity` | `Identity` | Checked by `restore`, never assigned into the episode (FR-006). |
| `seed` | `u64` | The config's current world seed; `restore` writes it into the config so `current_seed()` and the `reset_fresh` chain continue as the original's would (R2). |
| `world` | `World` | Serialized whole, RNG included — the same serde the server persists (FR-002). |
| `tick_in_episode` | `u64` | Episode position; truncation is re-derived from it only through `truncated` below, never recomputed. |
| `truncated` | `bool` | Restored as saved (FR-007: a truncated snapshot restores truncated). |
| `prev_level` | `f64` | Reward delta baseline. |
| `prev_potential` | `f64` | Shaping baseline. |
| `pending_seeds` | `DealtSeeds` | The NEXT tick's seeds, already drawn; restored, never re-dealt (R2). `DealtSeeds` gains `Serialize, Deserialize` in core. |

Not carried: `poisoned` (snapshot refused while poisoned; restore
heals), `last_tables` (re-derived), configs/codec/registry/control
(identity), `pending_overrides` (dropped by restore, FR-012).

Validation at restore, in order: parse (malformed → refused, environment
untouched) → identity (R3; first differing component named with both
values) → assign all fields → clear poison and pending overrides →
`collect_step` with an empty report (R4).

## Identity (rl crate)

| Field | Type | Rule |
|-------|------|------|
| `engine_commit` | `String` | The binding's `CLOUDKITTY_ENGINE_COMMIT`, passed in by the py crate; mismatch refuses by default (FR-006). |
| `config_fingerprint` | `String` | hex sha256 of `serde_json(core with world.seed = 0)` ‖ `serde_json(rl)`; covers observation, reward, horizon, roster, behaviours, needy settings; excludes the seed (R3). |
| `control` | `BTreeMap<KittyId, String>` | `"external"` or the builtin/preset name per seat — the `parse_control` vocabulary. |

Equality on every component is required; a mismatch anywhere refuses
(SC-003). The identity is computed by the environment, never trusted
from the caller.

## PendingOverride (rl crate)

| Field | Type | Rule |
|-------|------|------|
| `activity` | `Option<Action>` | Decoded at the call from the seat's start-of-tick table via `codec.decode` (R5); `None` = the seat's own act. |
| `message` | `Option<Option<MessageKind>>` | Decoded at the call via `MessageCodec::decode`; outer `None` = the seat's own message; `Some(None)` = Silent named explicitly. |

Keyed by `KittyId` in `Episode.pending_overrides`. Lifecycle: created by
`override_next` (refused if a key exists, if the seat is `External`, if
the kitty is unknown, or if both halves are `None`); consumed wholesale
by the first `step_inner` that reaches the tick (taken after every
external action has decoded, so a refused step leaves it standing);
cleared by `reset` and `restore`. At most one per seat.

Provenance mark derived at the tick: `activity.is_some() &&
message.is_some()` → `OverriddenBoth`; activity only → `OverriddenAct`;
message only → `OverriddenMessage`.

## Provenance (core crate, `seam.rs`) — extended

| Variant | Wire / Python string | Meaning |
|---------|----------------------|---------|
| `PolicyMade` (existing) | `policy_made` / `"policy"` | The seat's own advisor decided. |
| `FallbackTaken` (existing) | `fallback_taken` / `"fallback"` | Dispatch fell back to the default behaviour. |
| `SubstitutedIdle` (existing) | `substituted_idle` / `"substituted_idle"` | No well-formed proposal; the engine substituted idle. |
| `OverriddenAct` (new) | `overridden_act` / `"overridden_act"` | The harness substituted the act; the message is the seat's own. |
| `OverriddenMessage` (new) | `overridden_message` / `"overridden_message"` | The harness substituted the message; the act is the seat's own. |
| `OverriddenBoth` (new) | `overridden_both` / `"overridden_both"` | The harness substituted both halves. |

Unit variants, `Copy`, `snake_case` serde — the serialized shape of
every existing mark is unchanged (FR-015). The engine's tick marks every
present proposal `PolicyMade`; the episode overwrites scripted and
overridden seats' marks afterwards, as it already does for scripted
fallbacks.

## Tick record (Python reader, `tick_records()`)

One dict per roster kitty, keyed by agent name, built from the last
`TickReport` the wrapper retained (R7):

| Key | Type | Source |
|-----|------|--------|
| `proposed_action_name` | `str \| None` | `record.proposed` via `action_wire_name`; `None` at reset/restore. |
| `validated_action_name` | `str \| None` | `record.validated`. |
| `applied_action_name` | `str \| None` | `record.applied`. |
| `proposed_message` | `str \| None` | wire name; `None` for Silent or a substituted idle (AgentInfo's rule). |
| `applied_message` | `str \| None` | wire name; `None` for Silent. |
| `provenance` | `str \| None` | the table above; `None` at reset/restore. |
| `decision_seed` | `int \| None` | the seed the tick dealt that seat. |
| `survived` | `bool \| None` | `validated == proposed`; `None` for a substituted idle. |

The reader is a world-state reader (sibling to `needy()`), never an
observation; its keys are a documented contract (SC-008 reads
`provenance`).

## State transitions (environment)

```text
fresh ──reset──▶ live ──step──▶ live ──step──▶ … ──step at horizon──▶ truncated
  │                │  ▲            │                                     │
  │ restore        │  │ restore    │ panic                               │ reset / restore
  ▼                ▼  │            ▼                                     ▼
 live (at tick t) ◀───┘         poisoned ──restore──▶ live (healed)    live
```

- `snapshot()` is legal in `live` and `truncated`; refused in `fresh`
  ("reset first") and `poisoned` (RuntimeError).
- `restore(bytes)` is legal in every state; it always lands in the
  snapshot's state (`live` or `truncated`), healing poison.
- `override(...)` is legal in `live` only (refused in `fresh`,
  `truncated`, `poisoned`); it does not change state; the next successful
  `step` consumes it.
- `VectorEnv`: per-world transitions as above; the batch's `needs_reset`
  is unaffected by all three calls (R8).
