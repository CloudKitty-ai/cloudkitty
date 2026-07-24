# Data Model: Proposal Boundary Hardening & External Behavior Plugins

**Feature**: 016-behavior-plugins | **Date**: 2026-07-23

No persistent state changes: snapshots, the world model, and the public API
are untouched. Everything below is wire shapes, in-memory plugin state, and
configuration.

## Proposal (wire form of `Action`)

The existing `Action` enum is the internal type; the **proposal** is its JSON
wire form, parsed strictly by the new `parse_proposal` via per-variant mirror
structs with `deny_unknown_fields` (research.md R1). The table below is the
normative statement of what each mirror accepts (exact key match — extra keys
reject, `action` consumed as the tag):

| `action` value | Allowed keys (exact set) | Required | Field rules |
|---|---|---|---|
| `move` | `action`, `direction` | `direction` | `north` \| `east` \| `south` \| `west` |
| `rest` | `action`, `with` | — | `with`: kitty id (u32) or `null` or absent |
| `sleep` | `action`, `with` | — | same as `rest` |
| `groom` | `action`, `target` | — | `target`: kitty id (u32) or `null` or absent |
| `eat` | `action` | — | — |
| `drink` | `action` | — | — |
| `chase` | `action`, `target`, `id` | `target`, `id` | `target`: `element` \| `kitty`; `id`: u32 |
| `play` | `action` [, `target`, `id`] | — | absent target = solo play; if either of `target`/`id` present, **both** must be (existing `strict_play_target`) |
| `purr` | `action` | — | parses; engine validation resolves it to idle (spec 011) |
| `meow` | `action`, `message` | `message` | `want_eat` \| `want_drink` \| `follow_me` \| `want_play` \| `want_cuddle` \| `purr` \| `wait_for_me` |
| `idle` | `action` | — | — |

## ProposalError

Returned by `parse_proposal`; carried in the rejection log event (FR-013).
Kinds (exact naming free to implementation):

- `NotJson` — bytes are not valid JSON
- `NotAnObject` — valid JSON, but not a JSON object
- `MissingKind` / `UnknownKind` — no `action` key / unrecognized value
- `InvalidFields` — the mirror's serde error, which already names the
  problem: unknown extra field ("unknown field \`speed\`, expected …"),
  missing required field, wrong type, unrecognized enum value, incomplete
  play target
- `TooLarge` — reply exceeded `reply_max_bytes` (transport layer)

Note: duplicate JSON keys collapse to the last occurrence at `Value` parse
time (standard JSON semantics) *before* any strict check — documented in the
wire contract and pinned by one rejection-suite case.

Every kind resolves identically downstream: failed proposal → fallback
decision (FR-003 default). The kinds exist for diagnosability, not for
divergent handling.

## DecisionRequest (engine → plugin, one line)

| Field | Type | Notes |
|---|---|---|
| `v` | u32 | wire version, constant `1`; bump on breaking change |
| `tick` | u64 | the deciding tick |
| `kitty_id` | u32 | who is being asked (one shared process may serve several kitties) |
| `me` | `Kitty` | the deciding kitty's full state (existing serialization) |
| `world` | `WorldSnapshot` | start-of-tick snapshot (existing serialization; greebles included) |
| `seed` | u64 | one draw from the kitty's private decision stream (research.md R5) |
| `config` | `Config` | the simulation config (the served core config, not plugin definitions) |

**DecisionResponse** (plugin → engine, one line): a correlated envelope,
strict (unknown keys reject):

| Field | Type | Notes |
|---|---|---|
| `tick` | u64 | must echo the request's `tick` |
| `kitty_id` | u32 | must echo the request's `kitty_id` |
| `proposal` | object | one proposal on the hardened wire (table above) |

One request, one reply, in order. A correlation mismatch means the stream is
desynced (a stale or misattributed reply): failed proposal **and** the child
is killed for resync (research.md R3 / analysis finding I1). An unparseable
reply line is a failed proposal without a kill — line framing is intact.

## ScriptBehavior (in-memory state, `behavior/script.rs`)

| Field | Type | Notes |
|---|---|---|
| `command` | `PathBuf` | validated at startup: exists, is a file (FR-011) |
| `args` | `Vec<String>` | passed verbatim |
| `child` | `Mutex<ChildState>` | lock held for the whole write/read exchange |

`ChildState` transitions:

```text
NotSpawned ──first decision──▶ Running ──I/O error / oversized reply / correlation mismatch──▶ Dead { since_tick }
    ▲                                                                        │
    └────────── relaunch (≥ relaunch_cooldown_ticks later) ──────────────────┘
```

- `is_builtin()` = `false` (budget + breaker apply — inherited protections,
  research.md R4).
- A dead child inside its cooldown window returns failed proposals without
  spawning (fallback decides). Spawn failure re-enters `Dead` with a fresh
  `since_tick`.

## PluginsConfig (server-side, never in served `Config` — FR-014)

```toml
[plugins.professor_whiskers]
command = "./plugins/professor.py"   # must exist at startup
args = ["--temperament", "curious"]  # optional
```

Parsed alongside `RlConfig` in `load_config` (same file, separate struct,
same non-exposure). Registered as `ScriptBehavior` under the table key via
`register_plugin_behaviors(...)`, after policy behaviors, before
`validate_behavior_names`. Kitties opt in with the existing
`behavior = "professor_whiskers"` field.

## New `[behavior]` config knobs (documented defaults, Article VI)

| Key | Default | Meaning |
|---|---|---|
| `reply_max_bytes` | `65536` | cap on one reply line; beyond it the exchange fails and the child is killed (research.md R7) |
| `relaunch_cooldown_ticks` | `20` | minimum ticks between spawn attempts for a dead plugin process (research.md R4) |

Both validated non-zero in `Config::validate()` like `budget_strikes` /
`bench_ticks`.

## Provenance (unchanged shape)

`seam::Provenance` (`PolicyMade` / `FallbackTaken`) already captures the
outcome in the budgetless path; a parse failure is `FallbackTaken`. The
served path's observability is the structured log events (research.md R8):
`proposal rejected` (with `ProposalError` + truncated sample), `plugin
exchange failed`, `plugin relaunched`, plus the existing bench warning.
