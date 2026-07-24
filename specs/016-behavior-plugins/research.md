# Research: Proposal Boundary Hardening & External Behavior Plugins

**Feature**: 016-behavior-plugins | **Date**: 2026-07-23

Every decision below was made against the actual code (verified 2026-07-23):
`action.rs`'s serde surface, `behavior/mod.rs`'s dispatch/breaker, spec 014's
policy-registration seam in `cloudkitty-server`, and the constitution v1.1.0.

## R1 — How to reject unknown fields (the serde limitation)

**Decision** *(upgraded per /speckit-analyze finding R1a, 2026-07-23)*:
strict parsing is a dedicated entry point,
`parse_proposal(&str) -> Result<Action, ProposalError>` in `action.rs`,
implemented Value-first with **per-variant strict mirrors**: parse to
`serde_json::Value`, require a JSON object, take the `action` tag, then
deserialize the remaining fields into a small per-variant mirror struct
marked `#[serde(deny_unknown_fields)]`, and convert into the real `Action`
variant via a conversion impl (`Play`'s conversion carries the existing
strict-target logic; no `flatten` is needed anywhere in the mirrors).

**Rationale**: serde's `deny_unknown_fields` is documented as incompatible
with internally-tagged enums (`#[serde(tag = "action")]`) and with
`#[serde(flatten)]` — both of which `Action` uses — and the derived
deserializer buffers content and silently ignores unknown keys, so no
attribute combination on `Action` itself can reject extra fields. The
mirrors get unknown-field rejection from serde itself, with serde-quality
error messages ("unknown field \`speed\`, expected ..."), and — decisively —
**compile-time coupling**: a field whose type or presence drifts between
`Action` and its mirror breaks the conversion impl at compile time.

**Drift guard** (both directions): a field added to `Action` but not its
mirror fails the round-trip property immediately
(`parse_proposal(serde_json::to_string(a)) == a` for every constructible
shape rejects the now-unknown key); a field removed from `Action` breaks the
mirror's conversion impl at compile time. A new variant without a mirror arm
fails round-trip as an unknown `action` kind.

**Alternatives considered**: rewriting `Action`'s `Deserialize` by hand
(rejected: large, drift-prone, and would touch snapshot loading); externally
tagged wire format (rejected: breaks the existing wire shape the play tests
already pin); a hand-maintained exact allowed-key table checked before the
existing derive (the original R1 decision — rejected by analysis finding
R1a: a key removed from `Action` but left in the table would pass the table
check and be silently ignored by the derive, quietly reopening unknown-field
acceptance for that key; the table guards only one drift direction);
`deny_unknown_fields` directly on `Action` (impossible, per the limitation
above).

## R2 — Where strictness applies

**Decision**: `parse_proposal` is the mandatory entry for **external bytes**
(plugin transports). `Action`'s derived `Deserialize` stays as-is for internal
trusted data (snapshots we wrote ourselves, test fixtures). The engine's
`validate()` (well-formed-but-illegal → idle) is unchanged.

**Rationale**: FR-002's rejection matrix only matters where untrusted bytes
arrive; snapshot loading parses our own output, which round-trips by
construction. Keeping the derive untouched means zero risk to snapshot resume
and zero change to spec 014's integer codec (which never touches serde).

## R3 — Script transport protocol

**Decision**: newline-delimited JSON (NDJSON) over stdin/stdout of a
long-running child process. Per decision: the engine writes exactly one
request line to the child's stdin, then reads exactly one reply line from its
stdout. The request carries `v` (wire version, constant `1`), `tick`,
`kitty_id`, `me` (the kitty's full state), `world` (the start-of-tick
`WorldSnapshot`, which already derives `Serialize`), `seed` (see R5), and
`config`. The reply is a **correlated envelope** —
`{"tick": N, "kitty_id": K, "proposal": {…}}`, strict (unknown envelope keys
reject), with the proposal on the hardened wire — added per /speckit-analyze
finding I1: replies are otherwise matched to requests *positionally*, so a
plugin that ever emitted two lines would desync the stream and a stale but
*valid* proposal could be applied to a later tick, or (shared process) a
different kitty. An envelope whose `tick`/`kitty_id` do not match the request
is a failed proposal **and kills the child** (the stream is desynced;
relaunch resynchronizes it). An unparseable reply line is a failed proposal
only — line framing is intact, no kill. The child's stderr is inherited/piped
to the server log.

**Rationale**: NDJSON needs no framing library, is trivially speakable from
any language (`readline` + `print`), matches the one-request-one-reply spec
rule, and keeps the transport-agnostic core (request payload + proposal
parsing) cleanly separated from byte transport — the deferred HTTP transport
reuses the same request/response JSON bodies verbatim over POST.

**Alternatives considered**: length-prefixed framing (rejected: needless
ceremony for line-oriented tools); one process per decision (rejected by
clarification Q3); JSON-RPC (rejected: envelope adds nothing over NDJSON
here).

## R4 — Process lifecycle & relaunch policy

**Decision**: `ScriptBehavior` owns `Mutex<Option<Child>>`. Launch happens at
first decision (after startup validation of the command path, FR-011);
`decide()` locks the child for the whole write-request/read-reply exchange.
Any I/O failure (EOF, broken pipe, read error) kills and clears the child and
returns a failed proposal (→ fallback). Relaunch is attempted lazily on a
later decision, at most once per `relaunch_cooldown_ticks` (config default:
20 ticks), measured against `ctx.world.tick` — a crash-looping program costs
its kitty cleverness at a bounded spawn rate, never a spawn storm.

**Rationale (interplay with existing protections — no new mechanisms)**: the
budget already runs non-builtins on the blocking pool under
`tokio::time::timeout`, so a *hung* exchange is preempted and repeated hangs
are benched by the existing circuit breaker; panic isolation already converts
a poisoned exchange into a fallback. The only genuinely new failure mode a
child process adds is *fast* failure (dead process → instant I/O error),
which the cooldown bounds. Sharing one `ScriptBehavior` instance between
kitties is safe: the mutex serializes exchanges, and `kitty_id` in the
request tells the program who is asking.

## R5 — The randomness a plugin receives

**Decision**: the request's `seed` is one `u64` drawn from `ctx.rng` at the
start of the exchange.

**Rationale**: FR-008 grants a plugin the kitty's private per-tick
randomness. `DecisionContext` exposes the `DecisionRng` stream but not the
seed it was built from, and the dealt seed lives in dispatch, not the
context. Drawing one value from the kitty's own stream *is* the sanctioned
randomness — deterministic to the world, never synchronized between kitties —
and needs zero plumbing changes. The fallback-restarts-from-dealt-seed rule
is unaffected (dispatch already reseeds on failure).

## R6 — Configuration surface & FR-014

**Decision**: plugins are declared in the same TOML file under a section the
served `Config` never contains — mirroring the RL precedent exactly
(`load_config` already returns `(Config, RlConfig)` with `RlConfig` parsed
separately and never serialized to `GET /config`). A `PluginsConfig`
(`[plugins.<name>] command = "...", args = [...]`) is parsed in
`cloudkitty-server`, validated at startup (command exists and is a file →
otherwise startup fails with a clear error), and registered via
`register_plugin_behaviors(&mut registry, &plugins_config)` immediately after
`register_policy_behaviors` and before `config.validate_behavior_names()`.
Kitties opt in exactly as they do for any behavior: `behavior = "<name>"`.

**Rationale**: the seam already exists and is proven; behavior *names* remain
public (harmless), paths/args never leave the process. Tunables that belong
to the engine (`reply_max_bytes`, `relaunch_cooldown_ticks`) go in the
existing `[behavior]` block with documented defaults (Article VI).

## R7 — Reply size bound

**Decision**: the reply line is read through a capped reader;
`reply_max_bytes` default **64 KiB** (documented in `[behavior]`). Exceeding
it is a failed proposal (→ fallback) and kills the exchange's child (the
stream is now mid-line and unrecoverable).

**Rationale**: a valid proposal is under 200 bytes; 64 KiB is three orders of
magnitude of headroom while making "plugin cannot exhaust engine memory by
talking" (FR-010) literal.

## R8 — Observability (FR-013)

**Decision**: structured `tracing` events with distinct, greppable shapes per
layer: parse rejection (`warn`, includes the `ProposalError` and a truncated
sample of the offending bytes), exchange failure/relaunch (`warn`), budget
bench (exists today), and validation-idle (unchanged engine behavior). No new
public API surface; the budgetless path's `Provenance` marking is already
correct (a parse failure surfaces as `FallbackTaken`).

**Rationale**: the operator debugging a plugin is at the server console; logs
with the actual parse error are strictly more useful than a counter endpoint,
and adding public API surface would enlarge exactly the boundary this feature
exists to tighten. (If a future viewer feature wants fallback counts, that is
its own spec.)

## R9 — Docs examples verified by tests (SC-007)

**Decision**: `docs/plugins.md` marks its wire examples with fenced blocks
annotated `json accepted` / `json rejected`; a test in `cloudkitty-core`
reads the doc file (`include_str!` via a relative path), extracts the fenced
blocks, and asserts each accepted example parses via `parse_proposal` and
each rejected one fails.

**Rationale**: SC-007 says "every example in it is verified by a test" — the
extraction test makes the docs *incapable* of drifting from the parser, with
no duplicated example corpus to keep in sync.

## R10 — Article IV amendment text (v1.2.0)

**Decision**: amend Article IV's first clause to (final wording to be placed
in the constitution with a sync-impact comment, per its own conventions):

> Kitty behaviors (including external scripts, APIs, or local services) only
> *propose* actions. The engine validates every proposed action against the
> rules and current world state. Invalid, malformed, late, or absent
> proposals resolve safely to one of two constitutionally safe outcomes: the
> **default built-in (needs-based) fallback behavior** — the default
> resolution — or the **idle no-op**. Never an error state, never a rule
> violation, never a reshaped legal action.

Clause 2 (time budget + automatic fallback) is untouched. Version bump
1.1.0 → **1.2.0** (material expansion of a principle's stated outcomes);
ratified alongside this spec and the rejection suite in the same change
(Governance).

**Rationale**: clarification Q2. The amendment legitimizes both outcomes the
engine has always produced (fallback for failed advisors, idle for illegal
proposals) and names the default, ending the clause-1/clause-2 contradiction.

## R11 — How a failed exchange reaches the fallback path (surfaced during task generation)

**Problem**: `Behavior::decide(&self, ctx) -> Action` cannot express "I have
no proposal" — today the only routes to the fallback are a panic, a timeout,
or an unregistered name. A `ScriptBehavior` whose exchange fails (dead
process, unparseable reply, oversized reply) must NOT return `Action::Idle`
(that would reshape failure into a chosen action, violating FR-003's default)
and should not panic as control flow (noisy per-failure stderr from the
blocking pool; panic-as-API is fragile).

**Decision**: extend the trait with a **provided method**
`async fn try_decide(&self, ctx) -> Option<Action>` that defaults to
`Some(self.decide(ctx).await)`. Dispatch (`run_catching` on both the served
and budgetless paths) calls `try_decide`; `None` — from an override or from
panic containment — takes the existing crashed-advisor path: fallback decides
from the dealt seed, provenance `FallbackTaken`. `ScriptBehavior` overrides
`try_decide` and never implements a meaningful `decide`. Built-ins and every
existing test behavior are untouched (they inherit the default).

**Alternatives considered**: changing `decide` to return
`Option<Action>`/`Result` (rejected: churns every built-in and test behavior
for a case only externals have); deliberate `panic_any` on failure (rejected:
uses the containment path as control flow and spams stderr once per hostile
decision); returning `Idle` (rejected outright: FR-003 violation — failure
must resolve to the fallback by default, not to a legal action the advisor
never earned).

A new hostile test behavior (`Unintelligible`: `try_decide` → `None`) proves
the path independently of any transport, which keeps User Story 1 testable
without User Story 2.

## R12 — The exchange deadline (review remediation, 2026-07-23)

**Decision**: `ScriptBehavior` carries its own hard wall-clock deadline per
exchange (`[behavior] exchange_timeout_ms`, default 1000, non-zero
validated). Each child's pipes belong to a dedicated I/O thread; an exchange
hands it one request over a channel and waits for the reply with
`recv_timeout`. A miss fails the proposal and kills the process (which
closes the pipes and unblocks the I/O thread); the thread is detached, never
joined, so a plugin grandchild holding the pipe open can strand at most one
self-freeing OS thread per killed process.

**Rationale**: the post-implementation review confirmed four consequences of
relying on the *served* budget alone for wedge containment: (1) a silently
wedged plugin stranded one tokio blocking-pool thread per timed-out decision
— unbounded across bench windows, eventually saturating the shared pool and
degrading every external advisor; (2) the budgetless dispatch path
(`resolve_one` / `seam::drive_tick`, spec 014's mixed-control API) had no
wall clock at all, so a wedge hung headless drivers forever; (3) a
budget-stray thread could hold the instance mutex indefinitely; (4) its
eventual `Dead { since_tick }` write could carry an unboundedly stale tick,
pre-expiring the relaunch cooldown. A transport-carried deadline collapses
all four: strays finish within one deadline, every path is bounded, and the
`since_tick` skew is capped at one deadline's worth of ticks.

**Alternatives considered**: pipe-level `poll(2)` with a timeout (needs a
libc dependency and per-platform code for what a std thread + channel does);
relying on the breaker alone (leaves the budgetless path unbounded — the
review's finding, not a fix); joining the I/O thread on drop (deadlocks on a
plugin grandchild that inherits the stdout pipe).

**Residual, documented**: on the served path a kitty's budget clock also
covers its wait behind siblings sharing the process, so an overloaded shared
plugin can cost tail kitties budget strikes even when each reply is prompt —
documented in docs/plugins.md ("keep kitties × reply time inside the
budget") rather than re-architected, since per-kitty processes are one
config line away.
