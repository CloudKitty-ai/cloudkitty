# Implementation Plan: Key Settings (the effective-values block)

**Branch**: `052-key-settings` | **Date**: 2026-09-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/052-key-settings/spec.md` (3 user stories, 17 FRs, 6 SCs; owner's go 2026-09-08; three clarifications the same day, no markers).

## Summary

One server-owned list, the **key settings**: for each listed dial its effective value, its engine default (where one exists) and its source (`toml` or `default`), plus the `engine_defaults_sha256` stamp as the block's header. Built once at boot from the validated engine config, the server's own `[watchdog]` table and a generic parse of the loaded config text (for presence), held in `AppState`, and read three ways: logged as one block before the first tick, served at `GET /settings` (JSON by default, the same text block under `Accept: text/plain`), and printed by `docs/deploy/update.sh` as its closing `key settings` section, which exits non-zero with one of three named causes when it cannot. `/config` is untouched: no engine change, no serialization change, stamp unmoved, nothing deploys from this arc.

Technical approach: a new module `crates/cloudkitty-server/src/settings.rs` holds the list, the builder, the JSON shape and the one text renderer. `main.rs` builds it after `validate_behavior_names` and logs `render_text()` beside the existing per-spec boot lines (which stay), before `sim_task::spawn`. `api.rs` gains `get_settings` with content negotiation; `lib.rs` gains the route. The script gains `print_key_settings`, called inside the healthy branch after the backup prune. Guards: an in-code golden of the key names, the one-key-toml source test, the no-file test, an integration test that the wire (JSON and text) carries the built value unchanged, and a bash test that drives the script's function against a stub server in its four outcomes.

## Technical Context

**Language/Version**: Rust (toolchain pinned by `rust-toolchain.toml`, no change) for the server; bash + python3 stub for the deploy-tail test. No Python binding change.

**Primary Dependencies**: `cloudkitty-server` only: `axum` (route + `Accept` header read), `serde_json` (the value type), `toml` (already a dependency; one `toml::Value` parse for presence), `cloudkitty_rl::suite::engine_defaults_sha256` (already reachable, the server depends on `cloudkitty-rl`). `cloudkitty-core`, `cloudkitty-rl`, `cloudkitty-py`: no change.

**Storage**: none. No snapshot, wire-schema, artifact or fingerprint change.

**Testing**: `cargo test -p cloudkitty-server` (unit tests in `settings.rs`, integration tests in `tests/server_integration.rs`), `cargo test --workspace --no-fail-fast` once before the PR (baseline re-read at cycle 0), fmt + clippy CI-exact, `docs/deploy/test-update-tail.sh` for the script. Red-first per CLAUDE.md rule 5 via `scripts/mutate.sh --expect`, predictions in `redden-list.md`.

**Target Platform**: unchanged. Nothing deploys in this arc; the endpoint reaches the box at its next deploy, and *that* deploy is the first to print the section.

**Project Type**: Rust workspace, server crate + deploy script + docs.

**Performance Goals**: none that matter — one struct built at boot, one `Arc` clone per request.

**Constraints**: `/config` byte-identical and `engine_defaults_sha256` unmoved (SC-003); the block built before the listener binds (FR-006a); existing boot lines untouched (FR-007); `update.sh` stays one installable file (the provisioning script installs it by path); the client-only path untouched (FR-010); owner-authored prose in README, `docs/deployment.md` and the served toml untouched.

**Scale/Scope**: 1 new module, 3 touched server files (`main.rs`, `api.rs`, `lib.rs`), 1 integration-test file (3 `AppState` constructions gain a field + 2 new tests), 1 script, 1 new bash test, 1 CI step (four shell tests), README + `docs/deployment.md` + CHANGELOG, 1 contract.

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Articles I–III**: no need, population or roster mechanic is touched; the feature reads config and reports it. PASS.
- **Article IV**: no behavior path is touched; the endpoint is not a control surface. PASS.
- **Article V (server-authoritative, deterministic)**: all logic stays on the server; the client is not involved; no RNG, no tick-order change. A read-only endpoint over boot-time state. PASS.
- **Article VI (spec-first, test-guarded)**: this spec precedes the code; every FR has a named guard in `quickstart.md`; no constant is introduced (the defaults it reports are the engine's own). PASS.

**Complexity Tracking**: no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/052-key-settings/
├── spec.md              # 3 US / 17 FRs / 6 SCs; §Clarifications 2026-09-08
├── plan.md              # This file
├── research.md          # Phase 0: R1–R11 design decisions
├── data-model.md        # Phase 1: the list, the entry, the sources, the block
├── quickstart.md        # Phase 1: validation guide (guards, reds, the /config diff, the tail test)
├── contracts/
│   └── key-settings.md  # GET /settings (JSON + text), the boot block, the script's tail
├── checklists/requirements.md
├── redden-list.md       # implementation-time red-first record (house standard)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-server/
├── src/
│   ├── settings.rs          # NEW: KeySettings, Entry, Source; build(); render_text(); the key-name golden
│   ├── main.rs              # load_config also returns Option<toml::Value>; build + log the block; AppState.settings
│   ├── api.rs               # AppState gains `settings`; get_settings (JSON | text/plain)
│   └── lib.rs               # `pub mod settings;` + `.route("/settings", get(api::get_settings))`
└── tests/
    └── server_integration.rs  # 3 AppState constructions gain `settings`; +2 tests (wire == built, JSON and text; every entry present on a minimal config)

docs/deploy/
├── update.sh                # print_key_settings(); called in the healthy branch after the prune
└── test-update-tail.sh      # NEW: drives print_key_settings against a python3 stub in 4 modes

.github/workflows/ci.yml     # one step: the four shell tests (deploy tail, two hook self-tests, mutate runner) — R12

README.md                    # endpoint table: one row
docs/deployment.md           # "Updating": the closing section; "What is public": one bullet
CHANGELOG.md                 # ## Unreleased: one line, no markers
```

**Structure Decision**: everything lands in the server crate because it is the only place that sees all three inputs (engine config, the server-owned watchdog table, and the raw config text). The engine crate does not change, which is what keeps `/config` and the stamp provably still.
