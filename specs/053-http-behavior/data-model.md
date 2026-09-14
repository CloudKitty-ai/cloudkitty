# Data Model: HttpBehavior — the remote plugin transport

No persistent storage; every entity is config-parsed or in-memory. Wire
shapes are spec 016's, unchanged — see
[contracts/http-transport.md](contracts/http-transport.md).

## PluginEntry (extended) — `crates/cloudkitty-server/src/lib.rs`

One `[plugins.<name>]` block. `deny_unknown_fields` retained.

| Field     | Type                 | Rules |
|-----------|----------------------|-------|
| `command` | `Option<String>`     | Script transport. Existing semantics: path to an existing executable file (exec-bit checked at startup; docs now say "executable by anyone" — FR-013). |
| `args`    | `Vec<String>` (default empty) | Script transport only; nonempty with `url` → startup error. |
| `url`     | `Option<String>`     | Remote transport. Must parse as an absolute `http`/`https` URL at startup; reachability/DNS never checked at startup (FR-005). Never served (FR-009). |
| `class`   | `Option<SeatClass>`  | REQUIRED when `url` is set (startup error naming the entry if absent — FR-015); defaults to `scripted` when `command` is set. |

**Invariant (FR-002)**: exactly one of `command` / `url` per entry —
validated in `register_plugin_behaviors`, error names the entry.

## SeatClass (new) — server crate

`enum SeatClass { Scripted, Mind }`, serde lowercase (`"scripted"` /
`"mind"`). Attached by a server-crate wrapper behavior (owner ruled
option A, 2026-09-14 — research R9): the wrapper enters a tracing span
carrying `seat_class` around the inner advisor's `try_decide`
(`.instrument()`), applied to both transports at registration, so every
plugin-attributed log line inherits the field; the registration log line
states it too. The wrapper forwards `try_decide` and the
budget-exemption flag per the `behavior/mod.rs` wrapper-author contract.
No class field in core, never served, never in provenance, never in an
artifact schema (scope fence).

## HttpBehavior (new) — `crates/cloudkitty-server/src/http_behavior.rs`

Mirror of `ScriptBehavior` with the pipe transport swapped for HTTP:

| Field   | Type                  | Notes |
|---------|-----------------------|-------|
| `name`  | `String`              | Registry/behavior name; log context. |
| `url`   | `reqwest::Url`        | Parsed at startup; the configured trust boundary. |
| `state` | `Mutex<ExchangeState>`| Lifecycle below. One shared behavior may advise several kitties; the mutex serializes exchanges (same shared-plugin semantics and mutex-burst caveat as script — FR-014). |

(No `class` field — the seat class rides the registration wrapper's
tracing span, not the transport value; research R9.)

### ExchangeState (lifecycle)

Same three-state machine as `ChildState`, thread-for-process:

```text
NotSpawned ──(first decision)──> Running(IoThread)
Running ──(taint: timeout | dead thread)──> Dead{since_tick}
Dead ──(now - since_tick >= relaunch_cooldown_ticks)──> Running(fresh thread + client)
```

- **Running** holds the request `Sender`, reply `Receiver`, and the
  detached I/O thread owning one `reqwest::blocking::Client`
  (redirects off, request timeout = 2x `exchange_timeout_ms` — the
  engine-side channel deadline is authoritative; the client timer only
  self-unblocks a detached thread).
- **Taint teardown (research R6, narrowed at review)**: only a missed
  deadline (a late in-flight reply may still land in the channel) or a
  dead thread tears down; the fresh thread gets fresh channels, so a
  stale answer is structurally unreadable (US2/AS3).
- **Clean failures** (error status, refused/reset connection, garbage,
  oversized, or mis-correlated body on a consumed reply,
  envelope/proposal rejection) leave `Running` — the next exchange is
  independent.

### Decision flow (`try_decide`) — same order as script.rs

1. Build `DecisionRequest` **unconditionally** (the `ctx.rng.gen_u64()`
   seed draw MUST advance identically whether the endpoint is alive, dead,
   or cooling down — Article V constraint, same as script.rs:360-372).
2. `ensure_running` honoring `relaunch_cooldown_ticks`; not running →
   `None` (fallback decides from the dealt seed).
3. Serialize the request only after liveness is settled (a dead endpoint
   must not cost a world serialization per decision).
4. Exchange: send over channel; `recv_timeout(exchange_timeout_ms)` is the
   authoritative deadline. I/O thread: one POST, read body via
   `Read::take(reply_max_bytes + 1)`.
5. Validate via the shared core function (below). `Ok(action)` →
   `Some(Decision::silent(action))` (bare-action wire, Meow-stays-activity
   — identical to script). Any failure → log (with `seat_class`), maybe
   taint (R6 table), return `None`.

## ExchangeFailure (extended taxonomy, HTTP leg)

Script kinds map onto HTTP as:

| Script kind          | HTTP analog | Taints thread? |
|----------------------|-------------|----------------|
| `Io` (pipes broke)   | connect refused/reset/DNS failure, client error before a status | no (stateless exchange; retry next decision) |
| `BadEnvelope`        | 200 body not a valid envelope | no |
| `Desynced`           | envelope echoes wrong tick/kitty | no (consumed reply, connection dropped — review 2026-09-14 finding 5) |
| `Rejected`           | proposal fails the hardened gate | no |
| `TooLarge`           | body exceeds `reply_max_bytes` | no (read stopped at the cap — review finding 5) |
| `TimedOut`           | no reply within `exchange_timeout_ms` | **yes** |
| *(new)* `BadStatus`  | any non-200 status (includes surfaced redirects) | no |

The deliberate difference from script grew at review: NOTHING that
consumed its one reply taints — there is no shared stream to desync, so
`Io`, `Desynced`, and `TooLarge` all leave the channel accounted and the
next exchange independent. Only `TimedOut` (a reply may still be in
flight toward the channel) and `ChannelGone` (the thread is dead) tear
down, with `relaunch_cooldown_ticks` before rebuild. The io thread's
client timer sits at 2x the exchange deadline so the engine-side
`recv_timeout` always classifies a deadline miss as `TimedOut`, never as
a racing client-side error (review finding 6); a client build failure
drops the channel silently so the first exchange reads `ChannelGone`
(review finding 7).

## Shared reply validation (extracted) — `cloudkitty-core::behavior::exchange`

```text
pub fn parse_reply_line(bytes: &[u8], expect_tick: u64, expect_kitty: KittyId)
    -> Result<Action, ReplyRejection>
```

Strict envelope decode (`deny_unknown_fields`) → correlation check →
`parse_proposal_value`. Moved from `ScriptBehavior::exchange`
(script.rs:325-338), behavior-preserving; both transports call it —
FR-003 by construction. `ReplyRejection` carries the
BadEnvelope/Desynced/Rejected distinctions the callers' logging needs.

## ScriptBehavior (residual 1 touch only)

- Children spawn with `process_group(0)`; kill path becomes
  `killpg(child_pid, SIGKILL)` + reap (unix; non-unix unchanged).
- `Drop for PluginChild` comment + `docs/plugins.md` reworded: the thread
  frees because the whole group dies and the pipes close — no longer "a
  grandchild could hold it open indefinitely".
- No other change; decision semantics untouched.

## Unchanged, load-bearing

- `DecisionRequest` (script.rs, already `pub`): serialized identically by
  both transports; fog view via `ctx.world.snapshot` (spec 049 FR-048).
- `Provenance` (seam.rs): `PolicyMade` / `FallbackTaken` /
  `SubstitutedIdle` — FR-016's marker, no variant added.
- `[behavior]` knobs: `exchange_timeout_ms`, `reply_max_bytes`,
  `relaunch_cooldown_ticks`, budget, strikes, bench — govern both
  transports, no new tunables (Article VI).
- Budget/breaker/bench (`behavior/mod.rs`): zero edits — FR-006's "no new
  code paths per transport" is literal.
