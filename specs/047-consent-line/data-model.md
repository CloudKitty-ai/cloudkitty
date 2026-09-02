# Data Model: Partner Consent Line (spec 047)

No new entities, no persisted state, no wire types. The feature is one
config field and derived per-decision booleans that are never stored.

## Config

**`BehaviorConfig.consent_line: f32`** (`[behavior] consent_line` in TOML)

| Property | Value |
|---|---|
| Default | `0.0` = gate OFF (byte identity) |
| Serialization | `#[serde(default, skip_serializing_if = "f32_is_zero")]` — absent from the serialized defaults (039-D5 stamp discipline, same as the six 042 dials) |
| Validation | finite AND ≥ 0 (the shared 042 loop in `validate.rs`); NaN, ±inf, and negatives rejected at load with an error naming `[behavior] consent_line` |
| Scope | global behavior config, read only by the playful behavior's play paths |
| Persistence | none — server config, not world state; snapshots and resume untouched |

## Derived (per decision, never stored)

**`top_non_play(k)`** — max of the friend `k`'s eat/drink/sleep/cuddle/bath
needs, read from the decision-time world snapshot; one fold shared by the
042 `partner_value` score and the gate (FR-009's single definition).

**`consent_blocks(ctx, k)`** — `line > 0.0 && top_non_play(k) > line &&
top_non_play(k) > k.play` (strict; short-circuits false at the default
before any arithmetic). Consulted at the three playful sites listed in
[contracts/consent-gate.md](contracts/consent-gate.md).

## State transitions

None. The gate is a pure predicate over (config, snapshot); no cooldowns, no
memory, no per-kitty state.
