# Contract: The Proposal Wire & Plugin Decision Exchange

**Feature**: 016-behavior-plugins | **Wire version**: `1` | **Date**: 2026-07-23

This is the contract external advisors write against. It has two layers:
the **proposal wire** (what a proposed action looks like — transport-agnostic,
shared by every current and future transport) and the **script exchange**
(how bytes travel to and from a local plugin process). `docs/plugins.md` is
the reader-friendly rendering of this contract; its examples are verified by
tests (SC-007).

## Layer 1 — The proposal wire

A proposal is **one JSON object** with an `action` key naming the kind, plus
exactly the fields that kind allows (see the table in
[data-model.md](../data-model.md)). Parsing is strict; there is no coercion.

### Accepted (examples)

```json
{"action": "move", "direction": "north"}
{"action": "rest"}
{"action": "rest", "with": 2}
{"action": "sleep", "with": null}
{"action": "groom", "target": 1}
{"action": "eat"}
{"action": "drink"}
{"action": "chase", "target": "element", "id": 17}
{"action": "chase", "target": "kitty", "id": 3}
{"action": "play"}
{"action": "play", "target": "kitty", "id": 2}
{"action": "meow", "message": "want_play"}
{"action": "purr"}
{"action": "idle"}
```

(`purr` parses but always resolves to idle at validation — retired as an
action in spec 011; a stale advisor is not a parse error.)

### Rejected (examples, with the rule that rejects each)

```json
{"action": "levitate"}                                  // unknown action kind
{"action": "move"}                                      // missing required field
{"action": "move", "direction": "up"}                   // unrecognized value
{"action": "move", "direction": "north", "speed": 9}    // unknown extra field
{"action": "chase", "target": "element"}                // incomplete target (no id)
{"action": "play", "id": 2}                             // partial play target
{"action": "groom", "target": "Miso"}                   // wrong type (name, not id)
{"action": "rest", "with": -1}                          // wrong type (ids are unsigned)
"idle"                                                  // not an object
```

Duplicate JSON keys are not a distinct rejection: they collapse to the last
occurrence when the JSON is parsed (standard JSON semantics), *then* the
strict checks apply — `{"action": "move", "direction": "north", "direction":
"south"}` is simply a move south.

### Resolution semantics (FR-003/FR-004, amended Article IV)

| Outcome of parsing | Resolution | Observable as |
|---|---|---|
| Parses to an action, legal in the current world | applied | advisor's decision |
| Parses to an action, illegal in the current world | **idle no-op** (engine `validate`) | idle turn |
| Fails to parse (any rejection above) | **fallback decision** — the default built-in needs-based behavior decides from the kitty's dealt seed | `FallbackTaken` provenance / rejection log with the parse error |

Both resolutions are constitutionally safe (Article IV v1.2.0); the fallback
is the default for failed proposals. A malformed proposal is **never**
reshaped into a different legal action.

## Layer 2 — The script exchange (`ScriptBehavior`)

- The plugin is a **long-running process**, launched once and relaunched (with
  a cooldown) if it exits. It may keep state between decisions.
- Protocol: newline-delimited JSON over stdio. Per decision the engine writes
  **one request line** to the plugin's stdin; the plugin writes **one reply
  line** to stdout. One request, one reply, in order. stdout is only for
  replies; diagnostics belong on stderr, which is passed through to the
  server log.
- Request schema: see `DecisionRequest` in
  [data-model.md](../data-model.md) — `v`, `tick`, `kitty_id`, `me`, `world`,
  `seed`, `config`.
- Reply schema: a **correlated envelope** —
  `{"tick": <request tick>, "kitty_id": <request kitty_id>, "proposal": {…}}`
  — strict (unknown envelope keys reject), with `proposal` a single Layer 1
  proposal object. The echoed `tick`/`kitty_id` are what protect you from
  your own bugs: if your program ever writes an extra line, the stream
  desyncs, and without correlation a stale reply would be silently applied
  to a later decision — or, when one process advises several kitties, to the
  wrong kitty. On a correlation mismatch the engine treats the reply as a
  failed proposal **and restarts your process** to resynchronize the stream.
  An unparseable reply line is just a failed proposal (no restart).
- `v` is `1`. Plugins should reject versions they do not understand (their
  failed reply simply falls back — safe by construction).
- Deadline: each exchange must answer within `exchange_timeout_ms`
  (default 1000). A miss fails the proposal and kills the process (the
  stream is unaccounted for); relaunch follows the cooldown. This deadline
  is the transport's own and applies on every dispatch path, including
  budgetless headless drivers (review 2026-07-23).
- Budget: on the served path the whole exchange additionally runs under the
  standing wall-clock decision budget (default: half a tick), including any
  wait behind other kitties sharing the process. A late reply is discarded;
  repeated timeouts bench the kitty's dispatch (existing circuit breaker,
  expiring bench).
- Reply bound: one line, at most `reply_max_bytes` (default 64 KiB). An
  oversized reply fails the proposal and kills the process (the stream is
  mid-line and unrecoverable); relaunch follows the cooldown.
- Failure of any kind — unparseable reply, correlation mismatch, crash,
  hang, oversized reply, dead process — costs the advised kitty that tick's
  cleverness (fallback decides) and nothing more. The tick loop never waits
  beyond the budget and never stalls. Failures that leave the byte stream
  unrecoverable (oversized reply, correlation mismatch) also restart the
  process, under the relaunch cooldown.
- One shared process may advise several kitties: exchanges are serialized,
  and `kitty_id` says who is asking.

### Multi-agent livelock warning (required in plugin docs, FR-016)

All kitties decide against the same start-of-tick snapshot. Two deterministic
brains reacting to each other can mirror one another indefinitely — each
stepping toward where the other *was*, forever. Break symmetry: use the
request's `seed` (private per kitty per tick, deterministic to the world,
never synchronized between kitties) for tie-breaking randomness, or an
asymmetric rule such as kitty-id right-of-way. A fixed fallback rule that two
kitties compute identically will eventually dance.

## Compatibility promises

- The proposal wire is `Action`'s serialization: everything the engine
  serializes round-trips through `parse_proposal` unchanged (pinned by the
  round-trip suite).
- Spec 014's integer action codec and spec 015's frozen Python surface are
  untouched by this contract.
- The deferred HTTP transport (FR-007) will reuse Layer 1 verbatim and carry
  the same `DecisionRequest`/reply JSON bodies over HTTP; nothing in Layer 2
  may leak local-process assumptions into Layer 1.
