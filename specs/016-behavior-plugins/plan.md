# Implementation Plan: Proposal Boundary Hardening & External Behavior Plugins

**Branch**: `016-behavior-plugins` | **Date**: 2026-07-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/016-behavior-plugins/spec.md`

## Summary

Two halves, one sitting. First, harden the action-proposal wire: a new strict
proposal parser makes every action shape reject unknown kinds, missing or
wrong-typed fields, unrecognized values, incomplete targets, and unknown/extra
keys — with a per-shape round-trip + rejection suite (the Play tests are the
template) and Article IV amended (v1.2.0) to name both safe resolutions
(needs-based fallback — the default — and the idle no-op). Second, open the
door that wire was hardened for: `ScriptBehavior`, a long-running external
process attached to a kitty by configuration, speaking one request/response
JSON exchange per decision under every existing Article IV protection (budget,
panic isolation, circuit breaker, fallback). The HTTP transport (FR-007) is
specced but deferred; everything built now must stay transport-agnostic.

## Technical Context

**Language/Version**: Rust, workspace MSRV 1.83 (set by spec 015; no change)

**Primary Dependencies**: existing only — `serde`/`serde_json` (wire),
`tokio` (dispatch, already in place), `async-trait` (Behavior trait),
`std::process` (plugin child process). **No new external crates.**

**Storage**: N/A (no snapshot schema change; plugin state is the plugin's own
problem)

**Testing**: `cargo test` (unit + integration in `cloudkitty-core`, end-to-end
plugin tests with a fixture script); existing property/welfare/determinism
suites as regression gates

**Target Platform**: the server binary's existing targets (macOS/Linux);
plugin child processes are OS processes, so the script transport is
unix-flavored but uses only portable `std::process` APIs

**Project Type**: multi-crate Rust workspace — changes land in
`cloudkitty-core` (wire + ScriptBehavior + tests) and `cloudkitty-server`
(config loading + registration); `cloudkitty-rl` and `cloudkitty-py` untouched

**Performance Goals**: decision exchange comfortably inside the standing
budget (default half a tick, e.g. ~300 ms at 600 ms ticks) for a local
process; zero overhead when no plugin is configured

**Constraints**: plugin-free worlds byte-identical to today (SC-006); reply
size bounded (default 64 KiB); relaunch attempts bounded in frequency; plugin
config never served on `GET /config`

**Scale/Scope**: worlds of ~2–8 kitties, at most a few plugins per world; the
wire matrix is 11 action shapes × ~6 malformed-variant classes

## Constitution Check

*GATE: evaluated against constitution v1.1.0; this feature amends Article IV
to v1.2.0 (FR-017) with spec + guarding tests in the same change, per
Governance.*

- **Article I (no suffering)** — PASS. No needs/welfare mechanics touched. A
  hostile plugin can only cause fallback/idle turns; welfare property tests
  are an explicit acceptance gate (SC-001, SC-003).
- **Article II (no death)** — PASS. No kitty-removal paths introduced; plugin
  failure affects decisions only.
- **Article III (never alone)** — PASS. Roster untouched.
- **Article IV (engine is the law)** — this feature IS Article IV's
  enforcement surface, and it amends the article's wording (v1.2.0): an
  invalid, malformed, late, or absent proposal resolves safely to either the
  default built-in fallback behavior (the default resolution) or the idle
  no-op — never an error state, never a reshaped legal action. The amendment
  reconciles clause 1 ("safe no-op") with clause 2 (which already promised
  "automatic fallback to the default built-in behavior") and with the shipped
  engine. Constitution edit + this spec + the rejection suite land together.
- **Article V (deterministic, server-authoritative)** — PASS with the
  article's own scoping: determinism is promised *for built-in behaviors*;
  external advisors are outside the seed by nature. Plugin-free worlds must
  remain byte-identical (SC-006, determinism suite). The plugin's only
  randomness input is derived from the kitty's dealt decision stream. Clients
  remain pure views; plugins propose, never mutate.
- **Article VI (spec-first, test-guarded)** — PASS. This flow; all new
  constants (reply size bound, relaunch spacing) are documented config
  defaults, not magic numbers.

**Post-Phase-1 re-check**: PASS — no design element below weakens any gate;
the wire parser adds strictness without touching engine validation, and
`ScriptBehavior` slots into the existing dispatch untouched.

## Project Structure

### Documentation (this feature)

```text
specs/016-behavior-plugins/
├── spec.md              # Feature specification (clarified 2026-07-23)
├── plan.md              # This file
├── research.md          # Phase 0: design decisions + rationale
├── data-model.md        # Phase 1: wire types, plugin config, provenance
├── quickstart.md        # Phase 1: end-to-end validation runbook
├── contracts/
│   └── wire-protocol.md # Phase 1: THE wire contract (proposals + exchange)
├── checklists/
│   └── requirements.md  # Spec quality checklist (16/16)
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── action.rs                    # + strict proposal parsing (parse_proposal),
│                                #   per-shape round-trip/rejection suite
├── behavior/
│   ├── mod.rs                   # registry/dispatch — UNCHANGED mechanics;
│   │                            #   doc comment updated for the amendment
│   └── script.rs                # NEW: ScriptBehavior (long-running child,
│                                #   NDJSON exchange, relaunch, size bound)
└── config.rs                    # + [behavior] plugin knobs' documented
                                 #   defaults (reply size, relaunch spacing)

crates/cloudkitty-core/tests/
└── plugin_e2e.rs                # NEW: fixture-script end-to-end tests
                                 #   (hostile + well-behaved advisors)

crates/cloudkitty-server/src/
├── main.rs                      # parse plugin config; register before
│                                #   validate_behavior_names (014 pattern)
└── lib.rs                       # register_plugin_behaviors()

.specify/memory/constitution.md  # Article IV amendment → v1.2.0
docs/plugins.md                  # NEW: plugin author guide (FR-015/FR-016)
cloudkitty.toml                  # commented example plugin block
```

**Structure Decision**: all engine work stays in `cloudkitty-core` where the
`Behavior` trait and dispatch already live; the server crate only parses the
plugin config file section and registers instances at startup, mirroring how
spec 014's policy behaviors register (`register_policy_behaviors` →
`register_plugin_behaviors`, both before `validate_behavior_names`).
`cloudkitty-rl` and `cloudkitty-py` are untouched (spec 015's frozen Python
surface stays frozen).

## Complexity Tracking

No constitution violations; table not needed. One deliberate scope note: the
strict parser is a *second* consumer-facing entry point (`parse_proposal`,
built on per-variant strict mirror structs) rather than a rewrite of
`Action`'s derived `Deserialize`, because serde's `deny_unknown_fields` is
incompatible with internally-tagged enums and `flatten` (research.md R1).
The round-trip suite plus the mirrors' compile-time conversion coupling pin
the two surfaces together so they cannot drift in either direction.
