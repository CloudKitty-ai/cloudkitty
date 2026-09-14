# Implementation Plan: HttpBehavior — the remote plugin transport

**Branch**: `053-http-behavior` | **Date**: 2026-09-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/053-http-behavior/spec.md`

## Summary

Add a second speaker of the spec-016 plugin contract: a `[plugins.<name>]`
entry may declare `url` instead of `command`, and every decision travels as
one HTTP POST carrying the identical `DecisionRequest` JSON, answered by the
identical strict reply envelope. The transport is implemented in the SERVER
crate as `HttpBehavior`, reusing ScriptBehavior's proven skeleton (dedicated
blocking I/O thread, channel wait with a hard deadline, lifecycle enum with
relaunch cooldown) with the pipe I/O swapped for a blocking HTTP exchange.
The reply-validation path (envelope decode → correlation check → hardened
proposal gate) is extracted from `script.rs` into one shared public function
in core so both transports parse replies through literally the same code —
FR-003's "no dialect" by construction. Article IV machinery (budget,
breaker, bench, fallback) is not touched: it already wraps any `Behavior`.
The three script-transport residuals land here too: process-group kill
(core `script.rs`, lifecycle only), exec-bit doc note, and the documented
re-acceptance of the shared-plugin mutex burst. Doctrine fold: every plugin
entry can carry `class = "scripted" | "mind"` (required for `url` entries,
default `scripted` for `command` entries), logged wherever the plugin's
decisions are logged; fallback rows stay `FallbackTaken` provenance — the
existing marker — and the docs state they are scripted rows excluded from a
mind seat's lineage.

## Technical Context

**Language/Version**: Rust, workspace toolchain pin 1.97.1 (rust-toolchain.toml)

**Primary Dependencies**: `reqwest` 0.12 promoted from dev-dependency to
dependency of `cloudkitty-server` (blocking client, redirects disabled);
`libc` 0.2 added to `cloudkitty-core` under `cfg(unix)` for the
process-group kill (both already in `Cargo.lock` transitively). No other
new dependencies.

**Storage**: N/A (no persistent state; plugin declarations stay in the
server's TOML, never served — spec 016 FR-014 / this spec FR-009)

**Testing**: `cargo test` workspace suite; new integration tests in
`crates/cloudkitty-server/tests/` driving `HttpBehavior` against a raw
`std::net::TcpListener` stub (full control of hostile responses: garbage
bytes, error statuses, oversized bodies, slow trickle, redirects, silence);
existing core tests guard the script transport through the extraction
refactor. Red-first via `scripts/mutate.sh --expect` per house rule 5.

**Target Platform**: macOS + Linux server (unix; the process-group kill is
`cfg(unix)`, matching the existing exec-bit check's cfg)

**Project Type**: Rust workspace — engine crate (`cloudkitty-core`) +
server crate (`cloudkitty-server`); this feature is server-crate-first with
two bounded core touches (shared reply validation, process-group kill)

**Performance Goals**: none new — the standing wall-clock decision budget
and `exchange_timeout_ms` bound every exchange; fallback latency within the
standing budget from the first affected tick (SC-003)

**Constraints**: zero engine-semantics change (no RNG draw moved, no reward
term, no served-config byte — SC-004/SC-005); the seed draw advances the
kitty's decision stream identically whether the endpoint is alive or dead
(mirrors `script.rs`'s unconditional request build); no new `[behavior]`
tunables — `exchange_timeout_ms`, `reply_max_bytes`,
`relaunch_cooldown_ticks`, budget, strikes, bench govern the remote
transport as-is (spec Assumptions)

**Scale/Scope**: one new server module (`http_behavior.rs`, ~350 lines with
tests), one core extraction (~60 lines moved, behavior-preserving), config
validation additions in `register_plugin_behaviors`, `docs/plugins.md`
remote-transport section, one new contracts doc

## Constitution Check

*GATE: evaluated pre-Phase-0; re-evaluated post-Phase-1 (below).*

- **Article I–III (suffering/death/aloneness)**: untouched — the transport
  proposes; the engine validates exactly as today. PASS.
- **Article IV (engine is the law)**: the point of the feature. Remote
  proposals enter through the same hardened gate
  (`parse_proposal_value`) via the shared validation function; failed
  exchanges are `try_decide -> None`, resolving to the default fallback or
  idle exactly as the amended Article IV names. Budget, breaker, bench:
  unchanged code, verified by the hostile-endpoint suite. The three-tier
  fallback chain is explicitly OUT (spec scope fence). PASS.
- **Article V (server-authoritative, deterministic)**: remote-plugin worlds
  sit outside the determinism guarantee exactly as script-plugin worlds
  already do (constitution scopes determinism to built-in behaviors);
  everything around the advisor stays deterministic — guarded by the
  unconditional-seed-draw requirement and SC-004's byte-identity checks.
  Client remains a pure view. PASS.
- **Article VI (spec-first, test-guarded)**: this plan follows the banked
  spec; no new constants — existing documented `[behavior]` keys govern;
  the one new config field family (`url`, `class`) is documented in the
  config reference with defaults (`class` default `scripted` for `command`
  entries; `url` has no default — its absence selects the script
  transport). PASS.

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/053-http-behavior/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── http-transport.md  # Phase 1 output — the remote leg of the 016 wire
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/behavior/
├── script.rs            # EDIT: extract reply validation; process-group
│                        #   spawn + group kill (FR-012); doc-comment fix
│                        #   (stop claiming the thread frees on close)
└── mod.rs               # EDIT: re-export the shared validation fn

crates/cloudkitty-server/
├── Cargo.toml           # EDIT: reqwest 0.12 dev-dep -> dep (blocking,
│                        #   no default json feature needed)
├── src/
│   ├── lib.rs           # EDIT: PluginEntry gains url/class; exactly-one-
│   │                    #   transport + URL + class validation in
│   │                    #   register_plugin_behaviors; registration logs class
│   └── http_behavior.rs # NEW: HttpBehavior (ScriptBehavior skeleton,
│                        #   HTTP exchange in the I/O thread)
└── tests/
    └── http_plugin.rs   # NEW: stub-endpoint integration suite (US1/US2,
                         #   SC-002/SC-003), startup-validation cases

docs/plugins.md          # EDIT: remote transport section (US3), exec-bit
                         #   meaning (FR-013), mutex-burst re-acceptance
                         #   (FR-014), seat class + fallback-lineage note
                         #   (FR-015/FR-016)
```

**Structure Decision**: `HttpBehavior` lives in `cloudkitty-server`
(plugins config, registration, and the HTTP stack already live there;
precedent: `PolicyBehavior` implements the core `Behavior` trait from
outside core). Core is touched only where the spec demands shared contract
code (reply validation) and the residual-1 lifecycle fix — both bounded,
neither changes a decision semantic.

## Phase 0 / Phase 1 outputs

See [research.md](research.md) (nine decisions, no open NEEDS
CLARIFICATION), [data-model.md](data-model.md),
[contracts/http-transport.md](contracts/http-transport.md),
[quickstart.md](quickstart.md).

## Post-design Constitution re-check

Re-evaluated after Phase 1: the design introduces no new resolution
outcome, no new tunable, no served-surface change, and no code path that
removes, harms, or isolates a kitty. The Article IV/V/VI readings above
hold against the concrete design. PASS.
