# Research: HttpBehavior — the remote plugin transport

Every Technical Context unknown resolved. Grounding read directly from the
tree at the plan sitting (post-merge of origin/main through d52d386).

## R1. Execution model: blocking I/O thread, not an async client

**Decision**: `HttpBehavior` copies `ScriptBehavior`'s skeleton exactly —
a dedicated blocking I/O thread owns the transport, `try_decide` hands it
one request over an mpsc channel and waits with
`recv_timeout(exchange_timeout_ms)`; the lifecycle enum
(`NotSpawned / Running / Dead{since_tick}`) and `relaunch_cooldown_ticks`
govern thread teardown/rebuild as they govern process relaunch.

**Rationale**: dispatch runs behaviors on blocking threads —
`tokio::task::spawn_blocking(|| futures::executor::block_on(run_catching(...)))`
on the served path (`behavior/mod.rs:407-408`) and plain
`futures::executor::block_on` on the headless paths (`mod.rs:347,351`). An
async HTTP client would need a live tokio reactor handle inside contexts
that deliberately don't provide one; blocking I/O behind a channel deadline
is the shape the review already hardened (deadline carried inside the
transport, bounding every dispatch path — script.rs module doc). Same
failure taxonomy, same logging shape, same cooldown clock semantics fall
out for free.

**Alternatives considered**: async `reqwest` + `tokio::time::timeout`
(breaks on the headless/budgetless drivers, which have no reactor);
blocking call directly inside `try_decide` with only reqwest's own timeout
(loses the engine-side authoritative deadline — a wedged TLS handshake
inside a buggy client would strand the deciding thread, exactly what the
2026-07-23 review removed).

## R2. HTTP client: reqwest 0.12 blocking, promoted from dev-dep

**Decision**: promote `reqwest = "0.12"` from `[dev-dependencies]` to
`[dependencies]` of `cloudkitty-server`, default TLS, `blocking` feature;
one `reqwest::blocking::Client` per plugin, built in/for the I/O thread,
with `redirect(Policy::none())` and a per-request timeout equal to the
exchange deadline.

**Rationale**: CLAUDE.md rule 2 ordering — reqwest is already in the tree
(dev-dep of this very crate, version pinned in `Cargo.lock`, compiled in
every CI run); `hyper` alone would mean hand-rolling connection pooling,
TLS wiring, and body handling. `reqwest::blocking` spins its internal
runtime on the client's own thread — legal on our dedicated I/O thread
(a plain `std::thread`, never a tokio worker). Redirects disabled matches
the spec edge case (a redirect answer is a failed proposal — the
configured address is the trust boundary). The per-request timeout is the
I/O thread's self-unblock; the channel `recv_timeout` remains the
authoritative engine-side deadline (R1).

**Alternatives considered**: `ureq` (a new dependency when an installed
one suffices); raw `TcpStream` HTTP/1.1 (no TLS, hand-rolled framing —
fails "simplest correct"); async reqwest (R1).

## R3. Reply size bound without buffering an unbounded body

**Decision**: read the response body through `std::io::Read` (blocking
`Response` implements it) with `.take(reply_max_bytes + 1)`; a body that
fills the extra byte is the oversized failure. Ignore/refuse
Content-Length as a promise — the read cap is the enforcement.

**Rationale**: byte-for-byte the same one-byte-over-cap proof
`io_loop` uses today (script.rs:122-127); a lying Content-Length or a
chunked trickle can't exhaust memory. The exchange deadline (R1/R2) bounds
a slow trickle in time.

## R4. Status and correlation semantics

**Decision**: only HTTP 200 with a body that parses as the strict reply
envelope is a candidate proposal; every other status (including other
2xx/3xx — redirects are disabled so 3xx surfaces as a status) is a failed
proposal. Correlation (`tick`, `kitty_id` echo) is verified by the shared
validation function even though HTTP pairs request/response, because
proxies, caches, and confused load balancers are exactly the middleboxes
the envelope rule exists for (spec assumption "one decision, one
exchange").

**Rationale**: strictest documentable contract; "200 or it didn't happen"
is one sentence in the docs and one branch in code. Desync semantics
(wrong tick/kitty) keep their script-transport meaning: the reply channel
is unaccounted for → taint the I/O thread (R6).

## R5. One contract, one parser: extract shared reply validation into core

**Decision**: extract the validation stage of `ScriptBehavior::exchange`
(strict envelope decode with `deny_unknown_fields`, correlation check,
`parse_proposal_value` hardened gate) into a public function in
`cloudkitty-core::behavior` (new small module `behavior/exchange.rs`,
re-exported), returning the existing failure taxonomy; `ScriptBehavior`
rewires to it (behavior-preserving — guarded by the existing script tests
and the 016 round-trip suite), `HttpBehavior` calls the same function.
`DecisionRequest` (already `pub` with pub fields) is serialized by both
transports unchanged.

**Rationale**: FR-003 demands the identical contract with no dialect; two
hand-kept copies of a 30-line parser is how dialects are born. The
extraction moves code, changes no behavior, and is the only way SC-004's
"script transport unchanged" and FR-003 can both be checked by
construction rather than by prose.

**Alternatives considered**: duplicate the parser in the server crate
(dialect risk, two homes for one contract); make the server depend on
script.rs internals via `pub(crate)` re-export tricks (not possible across
crates).

## R6. HTTP lifecycle: a tainted thread is a dead child

**Decision**: map the script transport's kill-classes onto thread
teardown. Timeout, oversized, and desync taint the exchange channel (a
late in-flight reply could sit in it and answer the next decision) → drop
the channel + client + thread, mark `Dead{since_tick}`, rebuild after
`relaunch_cooldown_ticks`. Envelope/proposal rejections with clean framing
(garbage body on a completed 200, error status, connection refused/reset)
keep the thread alive — the next exchange is independent. The dropped
thread is detached and self-bounds: its in-flight request dies at
reqwest's own timeout (R2), the bounded worst case exactly as the
script transport's detached I/O thread.

**Rationale**: preserves the documented failure semantics table's shape
(unrecoverable-or-unaccounted-for stream → kill + cooldown; clean
rejection → stream lives) and closes the stale-reply hole (US2/AS3: a late
answer is never applied to a later tick — teardown plus the correlation
check make it structural).

## R7. Process-group kill (FR-012, core, unix)

**Decision**: spawn plugin children with
`std::os::unix::process::CommandExt::process_group(0)` (own process group)
and kill with `libc::killpg(pid, SIGKILL)` before the reap; add
`libc = "0.2"` to `cloudkitty-core` under `[target.'cfg(unix)'.dependencies]`
(already in `Cargo.lock` transitively). Non-unix keeps today's
`child.kill()`. The `Drop for PluginChild` comment and `docs/plugins.md`
stop claiming the I/O thread frees "the moment the stream closes" — the
truth becomes: the group dies, so the pipes close, so the thread frees.

**Rationale**: `Child::kill` signals only the direct child; a grandchild
inheriting the stdout pipe keeps it open and strands the detached I/O
thread indefinitely (the residual). `process_group(0)` is std and stable
(1.64; pin is 1.97.1); `killpg` is the one libc call. Lifecycle only — no
decision semantics move; guarded by a new test where the plugin forks a
pipe-holding grandchild (`sh -c 'sleep 600 & read line'` shape, matching
the existing wedge-test style).

**Alternatives considered**: `nix` crate (heavier dep for one call);
double-fork detection or `/proc` walks (non-portable, complex); leaving it
(the spec folds residual 1 by owner ruling A).

## R8. Config surface: `url` + `class` on the existing entry

**Decision**: `PluginEntry` gains optional `url: Option<String>` and
`class: Option<SeatClass>` (`SeatClass` = `scripted | mind`, serde
lowercase), `deny_unknown_fields` retained. Startup validation in
`register_plugin_behaviors` (FR-002/FR-005/FR-015): exactly one of
`command`/`url` (both or neither → error naming the entry); `args`
nonempty with `url` → error; `url` must parse with scheme `http` or
`https` (parsed via `reqwest::Url`); `class` required for `url` entries
(no default — remote code can't show it), defaulted to `scripted` for
`command` entries (today's presumption; existing configs parse unchanged).
DNS resolution and reachability are runtime conditions — never checked at
startup (spec 016 FR-011).

**Rationale**: one declaration surface, one collision rule, one secrecy
rule (spec assumption); `deny_unknown_fields` keeps typo'd keys loud. The
class default asymmetry is the spec's own (FR-015).

## R9. Seat-class observability and fallback lineage (FR-015/FR-016)

**Decision (owner ruled 2026-09-14, option A)**: the class is attached by
a small server-crate wrapper behavior applied to BOTH transports at
registration: it enters a tracing span carrying `seat_class` around the
inner advisor's `try_decide` (via `.instrument()`), so every
plugin-attributed log line the transports already emit (exchange
failures, relaunches — attributed by `plugin = name`) inherits the field;
the registration log line states it too. The wrapper MUST forward
`try_decide` to the inner behavior (and the budget-exemption flag) — the
documented wrapper-author contract in `behavior/mod.rs`; a wrapper that
forwards only `decide` silently turns every plugin decision into a
fallback. No class field enters core (`ScriptBehavior` and `HttpBehavior`
are untouched by this concern); no provenance-enum change, no served
surface, no artifact schema change: `FallbackTaken` provenance (seam.rs,
spec 014 FR-017) is already the per-decision marker FR-016 keys on; the
docs state the doctrine consequence (fallback rows are scripted rows,
excluded from a mind seat's lineage) where corpus/lineage tooling authors
will read it.

**Rationale**: FR-015 asks for observability where decisions are
attributed without reading the server config — logs are that surface
today; a class field in core would be a third core touch carrying a
config-domain concept, and extending `Provenance` or artifact schemas
would be engine/schema change the spec forbids (FR-010, scope fence).
The wrapper is also structurally a preview of the three-tier chain
combinator the LLM-seat sitting will build (a chain is a wrapping
behavior that picks an inner advisor and labels the turn), so the
pattern — including the forward-`try_decide` discipline — is established
where that sitting will reuse it.

**Primary use-case (owner, 2026-09-14)**: a remote LLM as a kitty's
advisor is the most likely consumer of this transport. Two IOUs are
recorded for the LLM-seat sitting, deliberately NOT built here (scope
fence): (1) a machine-readable name→class accessor on the server's
registration map, for stamping class tables into corpus/lineage
artifacts; (2) a possible move of `HttpBehavior` from the server crate to
core or a transport crate IF training rollouts ever want remote teacher
seats — headless lab drivers don't link the server crate. Both are
contained moves (the contract parser is already core via R5; the
behavior is one file).

**Alternatives considered**: class as a field on the behavior values
(option B — a third core touch, and a per-seat field is likely the wrong
shape once the chain needs per-turn tier attribution); registration-line
only (weakest reading of FR-015's "wherever"); per-transport asymmetry
(FR-015 doesn't distinguish transports); amending FR-015 (narrowing a
MUST to fit the implementation).

## R10. LLM-harness direction (owner rulings 2026-09-14; recorded, not built)

The remote-LLM use-case shapes were reviewed before implementation; all
three land as conscious deferrals, with the harness — a service running
local to the LLM, operator-owned — as the designated home:

- **Wire v2 (send-once config handshake): DEFERRED at this sitting.**
  script.rs's DecisionRequest comment marked it "a v2 candidate, noted
  for the HttpBehavior sitting"; the sitting's ruling is to keep the
  stateless resend wire. Token/size cost is mitigated harness-side
  (cache the config, prune/diff the snapshot before prompting); a v2
  bump would touch both transports and is not needed for correctness.
  (T005 updates the script.rs note to point here.)
- **Train of thought: harness-side, engine envelope stays strict.** The
  strict `deny_unknown_fields` envelope is load-bearing (desync and
  middlebox detection); the harness logs the model's reasoning to an
  external file indexed by tick and strips it before replying.
  Engine-side thought carriage is a possible much-later design (an
  "all-LLM" future), entangled with rules 5/6 (students must never see
  it; whether it enters lineage records) — LLM-seat sitting territory
  at the earliest. IOU #3 for that sitting.
- **Harness responsibilities (future build, LLM-seat sitting)**: config
  caching, prompt assembly, thought logging, and UNTRUSTED
  pre-validation of model output — malformed or illegal-looking
  proposals may be retried against the model within the exchange
  deadline, so one bad sample costs a retry, not the tick. The engine's
  side is unchanged and remains authoritative: one request, one reply;
  internal harness retries are invisible to the wire, and every reply
  still passes the hardened gate and world validation (Article IV — the
  harness's validation is a convenience, never trusted).
- **Latency shape**: no new knobs. Slow advisors tune
  `exchange_timeout_ms` and the budget stack; a shared entry serializes
  exchanges (FR-014 burst), so the LLM-shaped deployment is one
  `[plugins]` entry per kitty pointing at the same harness URL — the
  harness parallelizes behind it. Documented in T020.
