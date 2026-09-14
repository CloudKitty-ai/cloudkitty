# Quickstart: validating the remote plugin transport

Runnable proof scenarios for the finished feature. Contract detail lives in
[contracts/http-transport.md](contracts/http-transport.md); shapes in
[data-model.md](data-model.md).

## Prerequisites

- Workspace toolchain (rust-toolchain.toml pin), `cargo test` green on the
  branch base.
- No deployment, no tag (house rule); everything below is local.

## 1. The suite (US1–US4 acceptance, SC-001)

```bash
cargo test --workspace
```

Expect: existing suite untouched and green (SC-001); new
`crates/cloudkitty-server/tests/http_plugin.rs` green, covering: applied
proposals with `PolicyMade` provenance against a healthy stub; startup
errors (both/neither transport, bad URL, missing class, args-with-url,
name collision); hostile-endpoint fallbacks per the failure table
(non-200, refused, garbage, desync, oversized, timeout, late-reply
discard); no-plugin byte-identity; the script transport's process-group
kill (US4).

## 2. A remote brain drives a kitty (US1 / SC-002, by hand)

Terminal 1 — a trivial well-behaved endpoint (test stub binary or any
~20-line HTTP responder that echoes `tick`/`kitty_id` around a legal
proposal):

```bash
# the integration suite's stub, runnable standalone, prints each decision
cargo run -p cloudkitty-server --example stub_brain -- 127.0.0.1:9090
```

Terminal 2 — a server config declaring it (server-owned TOML, never
served):

```toml
[plugins.brainy]
url = "http://127.0.0.1:9090/decide"
class = "mind"

[behavior.assignments]   # existing selection surface, unchanged
# <kitty> = "brainy"
```

```bash
cargo run -p cloudkitty-server -- --config /path/to/that.toml
```

Expect: registration log line with `plugin = brainy`, `seat_class = mind`;
the assigned kitty follows stub proposals (provenance `policy_made`);
`GET /config` and `GET /settings` byte-identical to a plugin-free server
(SC-005 — no `url`, no `class`, no plugin key anywhere served).

## 3. Failure containment (US2 / SC-003, by hand)

With scenario 2 running: kill the stub mid-run.

Expect: the affected kitty falls back within the standing budget on the
same tick (log: exchange failure with reason + `seat_class`); tick loop
uninterrupted; other kitties untouched; repeated failures bench the kitty
per the existing breaker. Restart the stub: cleverness returns
automatically after `relaunch_cooldown_ticks` + any bench expiry — no
server restart.

The 1,000-hostile-ticks bar (SC-003) runs in CI as a test, not by hand.

## 4. Determinism / no-op guarantees (SC-004)

```bash
# byte-identity: no plugins configured, fixed seed, N ticks — the existing
# determinism guard extended over the feature branch
cargo test -p cloudkitty-server no_plugins_byte_identical
cargo test -p cloudkitty-core   # script-transport suite unchanged
```

## 5. Docs verified (US3 / SC-006)

```bash
# every documented example parses/behaves as documented — the 016 pattern
cargo test -p cloudkitty-server docs_examples
```

`docs/plugins.md` must cover: `url`/`class` declaration + config-reference
rows, request/reply over HTTP, the failure table, budget/bench
interaction, mutex-burst note with `exchange_timeout_ms` mitigation
(FR-014), exec-bit meaning (FR-013), fallback-rows-are-scripted-rows note
(FR-016), livelock warning pointer.

## 6. Rule-5 discipline

Every new assertion goes through `scripts/mutate.sh --expect <prediction>`
(commit first; `--no-fail-fast` under it). Sort changed-behavior checks
before running (rule 6): must-go-red — the residual-1 grandchild test
against the pre-fix kill path; must-stay-green — the whole script
transport suite across the R5 extraction and the spawn change.
