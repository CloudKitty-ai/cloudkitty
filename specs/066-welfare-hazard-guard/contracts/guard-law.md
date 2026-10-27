# The Welfare-Hazard Acknowledgement Law, v1

Spec 066. The one place the guard's semantics are pinned;
`config/welfare_hazard.rs`, `validate_welfare_hazard`, the two sweeps
and the server gate implement it. Adding a hazardous mode is a new
registry entry here and in the enum, in the same commit.

## §1 The section

```toml
[welfare_hazard]
acknowledged = ["initial_needs"]
```

Optional, top-level, `deny_unknown_fields`. Absent: every readable
surface is byte-identical to the pre-066 engine (serialization, stamp,
`GET /config`, decisions, draws). Present: serializes as written (an
empty list serializes as `acknowledged = []`) on EVERY serialization
of `Config` — `GET /config`, the stamp's input, and the plugin
decision request (`behavior/script.rs` `DecisionRequest.config`, from
which the spec 055 lab prompt is rendered). On the decision wire it is
information to the advisor, never a decision input: the engine reads
it at load and boot only (owner ruling 2026-10-26, "A"). Never part of
`Config::fingerprint()`.

## §2 The registry

| name | active iff | site text (first match, validator order) |
|------|-----------|-------------------------------------------|
| `initial_needs` | any governing initial-need setting, roster-wide table or any `[[kitty]]` override, any of the six needs, is a value > 0 or a range whose `max` > 0 | `[initial_needs].<need> = <setting>` / `[[kitty]] '<name>' (id <id>) initial_needs.<need> = <setting>` |

Order of evaluation for the site: the roster-wide table first, then
kitties in config order; within each, needs in `NeedKind::ALL` order
(eat, drink, sleep, play, cuddle, bath). Numbers are rendered as
`validate_initial_needs` renders them (`92`, `min = 0, max = 90`).

A mode absent from this table is not guarded. The registry records no
teacher-eligibility (deferred to the needy-preset spec).

## §3 Exactness

Let A = the acknowledged names, M = the active modes. Validation
passes iff A, as a set with no duplicates, equals M, and every name in
A is registered. A absent is the empty set. Checked in order: unknown →
duplicate → missing → stale; the first failing check is the error.

## §4 Error text

Every failure is `ConfigError::Invalid` with
`field = "[welfare_hazard] acknowledged"`, rendered by the existing
`Display` as `config error: {field} is {value}; {expected}`.

| shape | value | expected |
|-------|-------|----------|
| unknown | the list as written | `'<name>' is not a registered welfare-hazardous mode (known: initial_needs)` |
| duplicate | the list as written | `'<name>' is listed more than once; one name per mode` |
| missing | the list as written, or `absent` | `the config activates welfare-hazardous mode '<name>' at <site>[, and '<name>' at <site>]; add to the config:\n[welfare_hazard]\nacknowledged = ["<every active name, registry order>"]` |
| stale | the list as written | `'<name>' is acknowledged but not active in this config; an acknowledgement is exact, remove it`; two or more: `'<a>', '<b>' are acknowledged but not active in this config; an acknowledgement is exact, remove them` |

The "line to add" always lists the FULL active set in registry order,
so pasting it makes the config exact in one edit.

## §5 Sweep rule

For every tracked `*.toml` the sweep loads: if the file is not under
`<repo>/experiments/`, `active_hazards()` must be empty, else the
sweep fails with `<path>: welfare-hazardous mode(s) <names> active
outside experiments/ (spec 066 FR-005)`. Files under `experiments/`
are governed by §3 through the load itself. Both sweeps (core and RL)
apply the rule identically.

## §6 Server gate

`--allow-welfare-hazard` is a bare switch. After `Config::validate`
and before any registry, snapshot or world: if `[welfare_hazard]
acknowledged` is non-empty and the switch is absent, start-up fails
with `this config acknowledges welfare-hazardous mode(s) <names>;
pass --allow-welfare-hazard to serve it on purpose`. Non-zero exit,
no world created or resumed, no backup moved. The switch on a config
with no acknowledged mode is accepted and changes nothing.

## §7 Surfaces when served

- Boot log, one `info` line, only when non-empty:
  `welfare-hazardous world served on purpose (--allow-welfare-hazard):
  acknowledged modes <names>`.
- `GET /config`: the section as written (§1).
- The plugin decision request: the section inside its `config` field,
  as written (§1); absent, the key is absent and the wire is
  byte-identical to pre-066.
- Key-settings block (spec 052), last row, only when non-empty:
  `welfare_hazard.acknowledged = [<names as JSON>] [toml]`; no default
  column.

With no acknowledged mode: no line, no row; the config surface carries
the section only when the config wrote it (§1: absent stays absent, a
written empty list serializes) — the served `cloudkitty.toml` boot is
byte-identical to today.
