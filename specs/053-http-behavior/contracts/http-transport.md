# Contract: the HTTP leg of the plugin wire

One contract, two transports. The request/reply/proposal shapes are spec
016's (`specs/016-behavior-plugins/contracts/wire-protocol.md`); this
document defines only how those bytes ride HTTP. Anything not stated here
is inherited unchanged.

## Declaration

```toml
[plugins.brainy]
url = "http://127.0.0.1:9090/decide"   # http or https; the exact
                                        # configured address is the contract
class = "mind"                          # REQUIRED for url entries:
                                        # "scripted" | "mind"
```

- Exactly one of `url` / `command` per entry; `args` is script-only.
- Startup errors (each naming the entry): both/neither transport, relative
  or non-http(s) URL, unparseable URL, missing `class` on a `url` entry,
  `args` with `url`, name collision with a builtin or policy behavior.
- Runtime-only conditions (never startup errors): DNS failure,
  unreachable/refusing endpoint.
- `url` and `class` are server-owned: never in `GET /config`, the stamp,
  or `/settings` (spec 016 FR-014 / 053 FR-009).

## Exchange

One decision = one `POST <url>`:

- **Request**: `Content-Type: application/json`; body = the one
  `DecisionRequest` JSON document (the exact bytes the script transport
  writes as a stdin line, no trailing newline required on the wire).
- **Response**: status `200` with body = the strict reply envelope JSON
  (`{"tick": ..., "kitty_id": ..., "proposal": {...}}`, unknown fields
  refused), matching what a script plugin writes as one stdout line. A
  trailing newline in the body is tolerated; nothing else extra is.
- The engine follows **no redirects**: the configured address is the trust
  boundary. 3xx is a failed proposal like any other non-200.

## Failure semantics (all → failed proposal → Article IV fallback)

| Endpoint behavior | Engine reading | Connection state after |
|---|---|---|
| non-200 status (incl. 3xx) | `BadStatus` | next exchange proceeds |
| refused / reset / DNS failure | I/O failure | next exchange proceeds |
| 200, body not a valid envelope | `BadEnvelope` | next exchange proceeds |
| 200, envelope echoes wrong tick/kitty | `Desynced` | exchange channel torn down; rebuilt after `relaunch_cooldown_ticks` |
| body exceeds `reply_max_bytes` | `TooLarge` | torn down + cooldown |
| no complete reply within `exchange_timeout_ms` | `TimedOut` | torn down + cooldown; a late answer is discarded, never applied to a later tick |
| well-formed but illegal proposal | engine validation idles it | unchanged (parse vs validation stay distinct) |

Correlation is verified even though HTTP pairs request and response:
proxies, caches, and load balancers are middleboxes the envelope echo
exists to catch.

## Bounds and knobs

No new tunables. The transport is governed by the existing documented
`[behavior]` keys: `exchange_timeout_ms` (end-to-end exchange deadline,
engine-side), `reply_max_bytes` (body cap, enforced by capped read — a
Content-Length is not trusted), `relaunch_cooldown_ticks` (teardown
cooldown), and the budget/strikes/bench stack, all transport-agnostic.

## Doctrine (rules 6/10)

- `class` states whether the advisor is a rule a person wrote
  (`scripted`) or a trained policy / LLM (`mind`); remote code cannot show
  it, so the declaration has no default for `url` entries.
- Article IV fallback turns are scripted turns regardless of `class`:
  `FallbackTaken` provenance is the marker, and such rows are excluded
  from a mind seat's lineage. No new marking surface.

## Compatibility

- Wire version: unchanged (`v` = current `PROPOSAL_WIRE_VERSION`); this is
  a transport addition, not a wire bump. The send-once config handshake
  stays a v2 candidate (script.rs note), untaken here.
- A config with only `command` entries, or no `[plugins]` at all, parses
  and behaves byte-identically to today.
