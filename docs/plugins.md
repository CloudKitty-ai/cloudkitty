# Writing a CloudKitty Behavior Plugin

A plugin is an external brain that decides what a kitty does. You write it
in any language, and it speaks to CloudKitty over one of two transports:
a **local program** (launched and kept running, spoken to over stdio) or a
**remote HTTP endpoint** (one POST per decision — spec 053). Either way
the engine asks one question per tick: *"here is the world — what does
your kitty do?"* Your answer is a proposal, and the engine is the law
(Article IV): everything you propose is validated, nothing you do can hurt
a kitty, crash the world, or stall a tick. The worst any plugin can
achieve is a moment of lost cleverness — its kitty falls back to the
built-in needs-driven behavior for that tick.

**One contract, two transports.** The request, the reply envelope, the
proposal wire, the failure semantics, and the budget/bench machinery in
this document apply to both transports identically — the engine parses
both through literally the same code. Sections below say so where the
carrier differs.

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
instead of surprising you mid-run. One precision worth knowing: the exec
check is "executable by **anyone**" (`mode & 0o111`), not "executable by
the server's user" — a program executable only by another owner or group
passes startup and then fails at every spawn, which surfaces as per-tick
fallbacks, not a startup error. `chmod +x` covers the common case. Program
paths and args are never exposed on the public `GET /config`.

### Remote quick start (spec 053)

The same brain can live behind an HTTP endpoint instead — any service you
can reach, no file on the server's disk:

```toml
[plugins.professor_whiskers]
url = "http://127.0.0.1:9090/decide"   # absolute http(s); the exact
                                        # address is the trust boundary
class = "scripted"                      # REQUIRED for url entries:
                                        # "scripted" (a rule a person
                                        # wrote) or "mind" (a trained
                                        # policy, an LLM)
```

`docs/examples/demo_http_brain.py` is the runnable twin of
`demo_plugin.py`: start it, declare it as above, point a kitty at it. One
entry declares exactly one transport — `command` or `url`, never both,
never neither, and `args` is script-only. The URL must parse at startup
(scheme http or https); whether it *answers* is a runtime question with a
per-tick fallback, exactly like a crashing program. `url` and `class` are
server-owned like the rest of the entry: never served, never in the
engine-defaults stamp, not a key setting.

**Why `class` exists**: for a local program someone can read the file; for
remote code nobody can, so the entry itself must say whether the advisor
is scripted or a mind (design doctrine rule 6). The declared class rides
the registration line and every log line the transports emit as
`seat_class` (the dispatch layer's own bench warning names the advisor
but not the class — it lives below the wrapper). Script entries
may declare it too (a local LLM harness is a mind); undeclared, they
default to `scripted`. One doctrine consequence to know: an Article IV
**fallback turn is a scripted turn** no matter what the seat declares —
fallback rows are excluded from a mind seat's lineage, keyed on the same
provenance mark you see in logs.

## The exchange

Your program is **long-running**: launched once, it may keep state between
decisions (a conversation with an LLM, loaded model weights, a grudge
against a particular greeble). The protocol is newline-delimited JSON over
stdio:

- CloudKitty writes **one request line** to your stdin.
- You write **one reply line** to your stdout.
- One request, one reply, in order. stdout is only for replies —
  diagnostics go to stderr, which lands in the server log.

Over the **remote transport** the same exchange is one HTTP round trip:
the engine POSTs the request line as a JSON body
(`Content-Type: application/json`) to your configured URL, and your
response is status **200** with the reply envelope as its body (a
trailing newline is tolerated; nothing else extra is). Everything else is
identical — same fields, same envelope, same proposal wire. Three
HTTP-specific rules:

- **200 or it didn't happen.** Any other status — errors, and redirects,
  which are never followed (the configured address is the trust
  boundary) — is a failed proposal, whatever the body says.
- **One request, one exchange, no pipelining.** Internal retries are your
  business: a harness may re-ask its model within `exchange_timeout_ms`
  and send its one reply late-but-in-time; the engine never sees the
  attempts. The engine's validation stays authoritative regardless of any
  checking you do on your side.
- **The envelope echo is still checked**, even though HTTP pairs request
  and response — proxies, caches, and confused load balancers are exactly
  the middleboxes it exists to catch.

### The request

One JSON object per line, with exactly these fields:

| Field | What it is |
|---|---|
| `v` | Wire version, currently `3` (spec 049: the fog — see below; version 2 was spec 033's vocabulary). Refuse versions you don't understand — your failed reply just falls back, which is safe. |
| `tick` | The deciding tick. Echo it back. |
| `kitty_id` | Whose turn this is — one process may advise several kitties. Echo it back. |
| `me` | Your kitty's full state (position, needs, activity, and so on) — including, since version 3, its element `memory` (one last-seen tile per kind: water, chow, bug, greeble, sunbeam) and its `explore_waypoint` (its index into the lattice exploration tour). |
| `world` | The start-of-tick world **as your kitty may know it** (version 3, spec 049 — the fog): the kitties and elements inside its vision disc (`dx² + dy² ≤ radius²` from `me`, `[vision] radius` in `config`; greebles included), every recent meow (hearing is global — each carries the speaker's `pos` at emission and an engine-stamped `reply` bit), and nothing beyond. Friends' `memory` / `explore_waypoint` are blanked. The same shape as version 2; a plugin assuming full sight cannot tell the difference, which is why the version moved. |
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
{"action": "meow", "message": "mew"}
{"action": "meow", "message": "want_play"}
{"action": "meow", "message": "want_cuddle"}
{"action": "meow", "message": "purr"}
{"action": "meow", "message": "wait_for_me"}
{"action": "meow", "message": "want_bath"}
{"action": "meow", "message": "want_sleep"}
{"action": "meow", "message": "here_food"}
{"action": "meow", "message": "here_water"}
{"action": "meow", "message": "here_critter"}
{"action": "meow", "message": "here_sunbeam"}
{"action": "meow", "message": "chirp"}
{"action": "meow", "message": "trill"}
{"action": "meow", "message": "ekekek"}
{"action": "purr"}
{"action": "idle"}
```

Field notes: `with` / `target` on rest, sleep, and groom name a kitty id and
may be omitted (or `null`) for the solo version. `play` with no target is
solo play; a play target must be complete — both `target` and `id` — or
absent entirely. Duplicate JSON keys collapse to the last occurrence before
any strict check — standard JSON semantics.

Two purrs, two fates. The purr **meow** is the deliberate purr (spec 022):
proposed by a content cat — happiness above the purr threshold, or rising —
it starts a real purr; proposed unearned, it resolves to an idle turn --
law-named kinds are only legal when their claim is true. The bare `purr` **action** still
parses (it was retired as an action in spec 011) but always validates down
to an idle turn: a stale advisor is not a parse error.

The vocabulary is two-tier since spec 033 (proposal wire v2; the full
language reference is `docs/meows.md`). LAW-NAMED kinds carry enforced
meaning: a want-kind needs its need armed, `purr` needs contentment
earned, and a `here_*` kind needs its referent adjacent — a cat can only
announce food it could itself eat. SOUND-NAMED kinds (`mew`, `chirp`,
`trill`, `ekekek` — the free register) have no grounding at all; what they
mean is the cats' business. Every kind obeys the per-kind cooldown, and
every kind can be disabled by the world's `[meow.vocabulary]` config.
Note `follow_me` no longer parses: it was renamed `mew` when the cats'
usage overwrote its designed meaning — the name now denotes the sound, as
all free-register names do.

**An honest limitation of this wire (since spec 028, stated plainly
here since spec 033): a plugin's meow proposal never sounds.** Decisions
are two-channel inside the engine — an activity plus a riding message —
but this wire carries one action, and a meow arriving as the *activity*
validates to an idle turn (the meow rows left the activity space when
the message channel was born). The accepted shapes above parse, cost
nothing to send, and spend the turn idling. The full vocabulary is
listed because the parse contract is real and because a future wire
version is expected to carry the message channel to plugins; until it
does, plugin cats are mute on the meow channel and the words above are
what the in-process minds (policies and built-ins) speak. This also
retires the older claim that a purr-meow "starts a real purr" via this
wire — it does not; only the in-process message channel can.

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
{"action": "meow", "message": "follow_me"}
{"action": "idle", "why": "sleepy"}
"idle"
```

(In order: unknown action kind; missing required field; unrecognized
direction; unknown extra field; ids are unsigned; ids are numbers, not
names; incomplete chase target; unknown target kind; partial play target,
twice; unknown meow kind; the pre-033 name a rename retired; extra field
on a bare action; not an object.)

## What happens to your proposal

| Your reply | Resolution | You'll see |
|---|---|---|
| Parses, and is legal right now | Applied — your kitty does it | The action, attributed to your plugin |
| Parses, but is illegal right now (chasing a vanished bug, eating with no chow near, purring without contentment) | Idle turn, via engine validation | An idle turn — not a punishment, just the law |
| Fails to parse | Fallback: the built-in needs-driven behavior takes the turn | `proposal rejected` in the log, with the parse error |
| Wrong `tick`/`kitty_id` echo, oversized, or no reply within `exchange_timeout_ms` | Fallback, **and your process is restarted** (remote: only the missed deadline tears the exchange channel down — a late answer is discarded, never applied to a later tick; a consumed wrong-echo or oversized reply costs one tick and the next exchange proceeds) | `plugin reply desynced` / size / `exchange timed out` warning in the log |
| Your process crashed or its stream broke (remote: connection refused/reset, DNS failure, a non-200 status) | Fallback (repeated budget timeouts also bench your kitty's dispatch for a while — it recovers on its own); remote clean failures don't cool down — the next decision asks again | `plugin exchange failed`, budget/bench warnings |

Two constitutional safety rails you can rely on (Article IV, v1.2.0): a
malformed proposal resolves to the **fallback**, a well-formed-but-illegal
one to an **idle turn** — never an error state, never a reshaped action you
didn't send, never a stalled world.

## Lifecycle

- **Launch** is lazy (first decision) after startup validation: the
  `command` must exist, be a file, and be executable — by anyone, see the
  quick-start note — or the server refuses to start. A remote entry's URL
  is validated the same way at startup; reachability never is.
- **Death** is survived: every affected decision falls back, and the engine
  relaunches your program — at most once per `relaunch_cooldown_ticks`
  (default 20), so a crash-looping program never becomes a spawn storm.
  The remote transport reuses the same cooldown for rebuilding its
  exchange channel after a missed deadline (only — a consumed oversized
  or mis-correlated reply costs one tick, no cooldown; see the table
  above). One sizing note: the rebuilt exchange starts COLD — client,
  DNS, TCP, and any TLS handshake all happen inside the same
  `exchange_timeout_ms` a warm request meets easily — so keep the
  deadline comfortably above your endpoint's cold-connection setup,
  especially for https advisors with aggressive timeouts.
- **Deadline**: each exchange must answer within `exchange_timeout_ms`
  (default 1000). Miss it and the proposal fails, your process is killed
  — as its whole process group, so a grandchild holding your stdout dies
  with you and the engine's I/O thread frees because the pipes close —
  and the relaunch cooldown starts; a silently hung program can never
  stall the world. This deadline is the transport's own and applies
  everywhere, including headless drivers with no decision budget.
- **Budget**: on the served path the whole exchange (including waiting for
  siblings sharing your process — see below) also runs inside the standing
  decision budget (default: half a tick — `budget_fraction_of_tick`).
  Answer promptly; precompute between ticks if you must think slowly.
- **Shared processes**: several kitties may name the same plugin (either
  transport). Exchanges are serialized and `kitty_id` says who is asking;
  keep per-kitty state keyed by it. Because a kitty's budget clock also
  covers its wait in the queue, keep (kitties sharing the process) × (your
  reply time) comfortably inside the budget — a slow shared plugin can
  cost its last-served kitties budget strikes even when every individual
  reply is prompt. This burst is a known, accepted bound (016 review
  residual 2, re-accepted at the 053 sitting): when a shared plugin
  wedges, each sibling's dispatch thread can park on the queue for up to
  `exchange_timeout_ms` during the one relaunch+timeout tick per cooldown
  window. The mitigation is tuning `exchange_timeout_ms` down when many
  kitties share one process.
- **Slow advisors — a remote LLM harness, say**: declare **one entry per
  kitty** pointing at the same URL. Each entry is its own exchange queue,
  so your endpoint sees the kitties in parallel and no kitty pays for a
  sibling's wait; the serialization above is per-entry, not per-URL.
  Auxiliary model output (a train of thought, telemetry) never rides the
  reply — the envelope rejects unknown fields by design; log it on your
  own side, keyed by `tick`, and strip it before answering.

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
| `[plugins.<name>] command` | — | Path to your executable (existence and the exec bit — "executable by anyone" — validated at startup); script transport, exclusive with `url` |
| `[plugins.<name>] args` | `[]` | Arguments, passed verbatim (script transport only) |
| `[plugins.<name>] url` | — | Absolute `http(s)` endpoint address (parsed at startup, never probed); remote transport, exclusive with `command` |
| `[plugins.<name>] class` | `"scripted"` for `command` entries; **no default** for `url` entries | Seat class, `"scripted"` or `"mind"` — remote code cannot show which it is, so a url entry must say |
| `[behavior] reply_max_bytes` | `65536` | Cap on one reply line |
| `[behavior] relaunch_cooldown_ticks` | `20` | Minimum ticks between relaunch attempts |
| `[behavior] exchange_timeout_ms` | `1000` | Hard wall-clock deadline on one exchange; missing it kills your process |
| `[behavior] budget_fraction_of_tick` | `0.5` | Your decision budget, as a share of a tick |
| `[behavior] budget_strikes` / `bench_ticks` | `5` / `300` | Consecutive timeouts before your kitty's dispatch is benched, and for how long |
