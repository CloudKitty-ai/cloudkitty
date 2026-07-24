# Writing a CloudKitty Behavior Plugin

A plugin is an external program that decides what a kitty does. You write it
in any language; CloudKitty launches it, keeps it running, and asks it one
question per tick: *"here is the world — what does your kitty do?"* Your
answer is a proposal, and the engine is the law (Article IV): everything you
propose is validated, nothing you do can hurt a kitty, crash the world, or
stall a tick. The worst any plugin can achieve is a moment of lost
cleverness — its kitty falls back to the built-in needs-driven behavior for
that tick.

This document is the complete contract. Every `json accepted` /
`json rejected` example in it is enforced by a test
(`crates/cloudkitty-core/tests/docs_examples.rs`), so if you can read this
file, you are reading the truth.

## Quick start

1. Copy `docs/examples/demo_plugin.py` somewhere and make it executable.
2. Declare it in `cloudkitty.toml` and point a kitty at it:

```toml
[plugins.professor_whiskers]
command = "docs/examples/demo_plugin.py"   # a path to an existing executable
args = []

# ...and in the roster:
# [[kitty]]
# id = 2
# name = "Biscuit"
# behavior = "professor_whiskers"
```

3. Start the server. You'll see `plugin behavior registered` in the log, and
   Biscuit's turns now come from your program.

The `command` must be a path to an existing executable file — a shebang
script, or an absolute interpreter path with the script in `args`. That is
validated at startup; a missing program stops the server with a clear error
instead of surprising you mid-run. Program paths and args are never exposed
on the public `GET /config`.

## The exchange

Your program is **long-running**: launched once, it may keep state between
decisions (a conversation with an LLM, loaded model weights, a grudge
against a particular greeble). The protocol is newline-delimited JSON over
stdio:

- CloudKitty writes **one request line** to your stdin.
- You write **one reply line** to your stdout.
- One request, one reply, in order. stdout is only for replies —
  diagnostics go to stderr, which lands in the server log.

### The request

One JSON object per line, with exactly these fields:

| Field | What it is |
|---|---|
| `v` | Wire version, currently `1`. Refuse versions you don't understand — your failed reply just falls back, which is safe. |
| `tick` | The deciding tick. Echo it back. |
| `kitty_id` | Whose turn this is — one process may advise several kitties. Echo it back. |
| `me` | Your kitty's full state (position, needs, activity, and so on). |
| `world` | The start-of-tick world snapshot every behavior decides against: every kitty, every element (greebles included), recent meows. |
| `seed` | A number from your kitty's own private randomness stream: deterministic to the world, never synchronized between kitties. Use it whenever you need a tie-break (see the livelock warning below). |
| `config` | The simulation config, so your thresholds can match the world's. |

### The reply

A strict envelope around one proposal:

```json
{"tick": 41, "kitty_id": 2, "proposal": {"action": "move", "direction": "north"}}
```

The echoed `tick` and `kitty_id` protect you from your own bugs: without
them, one accidental extra line would silently become the answer to the
*next* decision — possibly for a *different* kitty. If your echo doesn't
match the request, the engine discards the reply and **restarts your
process** to resynchronize the stream. Unknown fields in the envelope are
rejected. One reply line may be at most `reply_max_bytes` (default 64 KiB);
beyond that the reply fails and the process is restarted.

## The proposal wire

A proposal is one JSON object with an `action` field and exactly the fields
that action allows. Parsing is strict: unknown action kinds, missing or
wrong-typed fields, unrecognized values, incomplete targets, and unknown
extra fields are all rejected — a rejected proposal is never quietly
reshaped into something legal; your kitty simply takes its fallback turn,
and the server log tells you exactly what was wrong with the bytes you sent.

Every accepted shape:

```json accepted
{"action": "move", "direction": "north"}
{"action": "move", "direction": "east"}
{"action": "move", "direction": "south"}
{"action": "move", "direction": "west"}
{"action": "rest"}
{"action": "rest", "with": 2}
{"action": "sleep"}
{"action": "sleep", "with": 3}
{"action": "groom"}
{"action": "groom", "target": 1}
{"action": "eat"}
{"action": "drink"}
{"action": "chase", "target": "element", "id": 17}
{"action": "chase", "target": "kitty", "id": 3}
{"action": "play"}
{"action": "play", "target": "element", "id": 8}
{"action": "play", "target": "kitty", "id": 2}
{"action": "meow", "message": "want_eat"}
{"action": "meow", "message": "want_drink"}
{"action": "meow", "message": "follow_me"}
{"action": "meow", "message": "want_play"}
{"action": "meow", "message": "want_cuddle"}
{"action": "meow", "message": "purr"}
{"action": "meow", "message": "wait_for_me"}
{"action": "purr"}
{"action": "idle"}
```

Field notes: `with` / `target` on rest, sleep, and groom name a kitty id and
may be omitted (or `null`) for the solo version. `play` with no target is
solo play; a play target must be complete — both `target` and `id` — or
absent entirely. `purr` still parses (it was retired as an action in
spec 011) but always validates down to an idle turn: a stale advisor is not
a parse error. Duplicate JSON keys collapse to the last occurrence before
any strict check — standard JSON semantics.

And a gallery of rejections — each of these fails parsing and costs the
proposing kitty its tick (fallback decides):

```json rejected
{"action": "levitate"}
{"action": "move"}
{"action": "move", "direction": "up"}
{"action": "move", "direction": "north", "speed": 9}
{"action": "rest", "with": -1}
{"action": "groom", "target": "Miso"}
{"action": "chase", "target": "element"}
{"action": "chase", "target": "bogus", "id": 1}
{"action": "play", "id": 2}
{"action": "play", "target": "kitty"}
{"action": "meow", "message": "want_snacks"}
{"action": "idle", "why": "sleepy"}
"idle"
```

(In order: unknown action kind; missing required field; unrecognized
direction; unknown extra field; ids are unsigned; ids are numbers, not
names; incomplete chase target; unknown target kind; partial play target,
twice; unknown meow kind; extra field on a bare action; not an object.)

## What happens to your proposal

| Your reply | Resolution | You'll see |
|---|---|---|
| Parses, and is legal right now | Applied — your kitty does it | The action, attributed to your plugin |
| Parses, but is illegal right now (chasing a vanished bug, eating with no chow near) | Idle turn, via engine validation | An idle turn — not a punishment, just the law |
| Fails to parse | Fallback: the built-in needs-driven behavior takes the turn | `proposal rejected` in the log, with the parse error |
| Wrong `tick`/`kitty_id` echo, oversized, or no reply within `exchange_timeout_ms` | Fallback, **and your process is restarted** | `plugin reply desynced` / size / `exchange timed out` warning in the log |
| Your process crashed or its stream broke | Fallback (repeated budget timeouts also bench your kitty's dispatch for a while — it recovers on its own) | `plugin exchange failed`, budget/bench warnings |

Two constitutional safety rails you can rely on (Article IV, v1.2.0): a
malformed proposal resolves to the **fallback**, a well-formed-but-illegal
one to an **idle turn** — never an error state, never a reshaped action you
didn't send, never a stalled world.

## Lifecycle

- **Launch** is lazy (first decision) after startup validation: the
  `command` must exist, be a file, and be executable (`chmod +x`), or the
  server refuses to start.
- **Death** is survived: every affected decision falls back, and the engine
  relaunches your program — at most once per `relaunch_cooldown_ticks`
  (default 20), so a crash-looping program never becomes a spawn storm.
- **Deadline**: each exchange must answer within `exchange_timeout_ms`
  (default 1000). Miss it and the proposal fails, your process is killed,
  and the relaunch cooldown starts — a silently hung program can never
  stall the world. This deadline is the transport's own and applies
  everywhere, including headless drivers with no decision budget.
- **Budget**: on the served path the whole exchange (including waiting for
  siblings sharing your process — see below) also runs inside the standing
  decision budget (default: half a tick — `budget_fraction_of_tick`).
  Answer promptly; precompute between ticks if you must think slowly.
- **Shared processes**: several kitties may name the same plugin. Exchanges
  are serialized and `kitty_id` says who is asking; keep per-kitty state
  keyed by it. Because a kitty's budget clock also covers its wait in the
  queue, keep (kitties sharing the process) × (your reply time) comfortably
  inside the budget — a slow shared plugin can cost its last-served kitties
  budget strikes even when every individual reply is prompt.

## The multi-agent livelock warning

Read this twice if your plugin reacts to other kitties.

All kitties decide against the **same start-of-tick snapshot**. Two
deterministic brains reacting to each other can mirror one another
indefinitely: each steps toward where the other *was*, forever — a dance
with no progress. Three such dances were found in the built-ins in a single
day (a head-on corridor mirror, a mutual-approach corner orbit, a lockstep
convoy sidestep — specs 010/012).

When your behavior has no clearly progressing move, **break symmetry**:

- use the request's `seed` — it is private to your kitty and different every
  tick, so two kitties flipping the same coin get different answers; or
- use an asymmetric rule such as kitty-id right-of-way (lower id yields, or
  proceeds — pick one and commit).

A fixed fallback rule that two kitties can compute identically will
eventually dance.

## Config reference

| Key | Default | Meaning |
|---|---|---|
| `[plugins.<name>] command` | — | Path to your executable (existence and the exec bit validated at startup) |
| `[plugins.<name>] args` | `[]` | Arguments, passed verbatim |
| `[behavior] reply_max_bytes` | `65536` | Cap on one reply line |
| `[behavior] relaunch_cooldown_ticks` | `20` | Minimum ticks between relaunch attempts |
| `[behavior] exchange_timeout_ms` | `1000` | Hard wall-clock deadline on one exchange; missing it kills your process |
| `[behavior] budget_fraction_of_tick` | `0.5` | Your decision budget, as a share of a tick |
| `[behavior] budget_strikes` / `bench_ticks` | `5` / `300` | Consecutive timeouts before your kitty's dispatch is benched, and for how long |
